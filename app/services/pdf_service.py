"""
PDF processing service.
Handles PDF text extraction, page splitting, and other PDF operations.
"""

import fitz  # PyMuPDF
from typing import List, Tuple, Optional, Dict
import os
import re
import logging
from pathlib import Path
from PIL import Image
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.config import settings

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

class PDFService:
    """Service for handling PDF operations."""
    
    @staticmethod
    def get_total_pages(pdf_path: str) -> int:
        """
        Get the total number of pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Total number of pages
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                return len(pdf_doc)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def needs_ocr(pdf_path: str, sample_pages: List[int] = None) -> bool:
        """
        Check if a PDF needs OCR by testing text extraction on multiple sample pages.
        Uses a conservative approach - returns True if ANY page needs OCR.
        
        Args:
            pdf_path: Path to the PDF file
            sample_pages: List of page numbers to test (1-based). If None, samples first, middle, and last third
            
        Returns:
            True if OCR is needed, False otherwise
        """
        import re
        
        try:
            with fitz.open(pdf_path) as pdf_doc:
                total_pages = len(pdf_doc)
                
                # Determine which pages to sample
                if sample_pages is None:
                    # Sample from different parts of the document
                    sample_pages = []
                    if total_pages > 0:
                        sample_pages.append(1)  # First page
                    if total_pages > 3:
                        sample_pages.append(total_pages // 3)  # First third
                    if total_pages > 6:
                        sample_pages.append(2 * total_pages // 3)  # Second third
                    if total_pages > 1:
                        sample_pages.append(total_pages)  # Last page
                    
                    # Remove duplicates and ensure valid range
                    sample_pages = list(set(sample_pages))
                
                # Check each sample page
                for page_num in sample_pages:
                    if page_num < 1 or page_num > total_pages:
                        continue
                    
                    page = pdf_doc[page_num - 1]
                    text = page.get_text()
                    
                    # Count images on the page
                    image_count = len(page.get_images())
                    has_significant_images = image_count > 0
                    
                    # Check if text is empty or too short
                    if not text or len(text.strip()) < 50:
                        # If page has images and no/little text, definitely needs OCR
                        if has_significant_images:
                            return True
                        # Even without images, very little text is suspicious
                        if len(text.strip()) < 20:
                            return True
                    
                    # Check if text looks like just page numbers or headers
                    # Common patterns: "Page 1", "1", "Chapter", dates, etc.
                    header_pattern = r'^\s*(Page\s*\d+|\d+|Chapter|CHAPTER|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[IVXivx]+)\s*$'
                    lines = text.strip().split('\n')
                    non_header_lines = [line for line in lines if line.strip() and not re.match(header_pattern, line.strip())]
                    
                    # If most content looks like headers/page numbers, needs OCR
                    if len(non_header_lines) < 3 and has_significant_images:
                        return True
                    
                    # Check for CID encoding (both upper and lowercase)
                    if '(cid:' in text.lower() or 'CID:' in text or '(CID' in text:
                        return True
                    
                    # Enhanced garbled character detection
                    garbled_chars = ['Ú', 'Ë', '˙', 'ﬁ', '˜', 'Æ', '∆', '®', '¥', '∫', '√', '∂', '∑', 
                                   'Ω', '≈', '∞', '≤', '≥', '±', '≠', '×', '÷', '◊', 'Ø']
                    if any(char in text for char in garbled_chars):
                        # Count how many garbled characters
                        garbled_count = sum(1 for char in text if char in garbled_chars)
                        if garbled_count > len(text) * 0.05:  # More than 5% garbled
                            return True
                    
                    # Check for too many non-ASCII characters in non-Unicode range
                    non_ascii = len([c for c in text if ord(c) < 32 or (ord(c) > 126 and ord(c) < 256)])
                    if non_ascii > len(text) * 0.3:
                        return True
                    
                    # Check if extracted text is too short relative to page size
                    # A typical page should have at least 100-200 characters
                    if len(text.strip()) < 100 and has_significant_images:
                        return True
                
                # If all sample pages passed, OCR not needed
                return False
                
        except Exception as e:
            # If we can't determine, err on the side of caution and use OCR
            print(f"Error checking OCR need: {e}")
            return True
    
    @staticmethod
    def extract_text_from_pages(pdf_path: str, start_page: int, end_page: int,
                                ocr_fallback: bool = True, ocr_language: str = "eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori",
                                ocr_dpi: int = 300, ocr_config: str = None) -> str:
        """
        Extract text from specified page range in a PDF with OpenAI Vision API OCR fallback for image-based pages.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, inclusive)
            ocr_fallback: Whether to use OpenAI Vision API OCR for pages with no text (default: True)
            ocr_language: Language(s) for OCR recognition. Can be single language (e.g., "eng") 
                         or multiple languages separated by + (e.g., "eng+hin+tam")
                         Default includes English and major Indian languages:
                         - eng: English
                         - hin: Hindi (हिन्दी)
                         - tam: Tamil (தமிழ்)
                         - tel: Telugu (తెలుగు)
                         - kan: Kannada (ಕನ್ನಡ)
                         - mal: Malayalam (മലയാളം)
                         - mar: Marathi (मराठी)
                         - guj: Gujarati (ગુજરાતી)
                         - ben: Bengali (বাংলা)
                         - pan: Punjabi (ਪੰਜਾਬੀ)
                         - ori: Odia (ଓଡ଼ିଆ)
            ocr_dpi: DPI for image conversion when using OCR (default: 300)
            ocr_config: Custom Tesseract configuration string (e.g., "--psm 6")
            
        Returns:
            Extracted text as a string with page labels indicating extraction method
        """
        # Check if file exists
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
                # Pre-check if PDF needs OCR (optional optimization)
        # This helps us log upfront whether OCR will likely be needed
        if ocr_fallback and PDF2IMAGE_AVAILABLE:
            # Sample a few pages from the range to check
            sample_pages = []
            if end_page - start_page + 1 <= 3:
                # For small ranges, check all pages
                sample_pages = list(range(start_page, end_page + 1))
            else:
                # For larger ranges, sample first, middle, and last
                sample_pages = [start_page, (start_page + end_page) // 2, end_page]
            
            if PDFService.needs_ocr(pdf_path, sample_pages):
                logger.info(f"PDF likely needs OCR based on sample pages {sample_pages}. OCR will be attempted where needed.")
        
        try:
            with fitz.open(pdf_path) as pdf_doc:
                total_pages = len(pdf_doc)
                
                # Validate page numbers with specific error messages
                if start_page < 1:
                    raise ValueError(f"Start page must be >= 1, got {start_page}")
                if end_page > total_pages:
                    raise ValueError(f"End page {end_page} exceeds total pages {total_pages}")
                if start_page > end_page:
                    raise ValueError(f"Start page {start_page} cannot be greater than end page {end_page}")
                
                # Extract text from each page in the range
                extracted_text = []
                
                for page_num in range(start_page - 1, end_page):  # Convert to 0-based indexing
                    page_label = page_num + 1
                    text = ""
                    extraction_method = ""
                    
                    # Try pdfplumber first for better Unicode/Indian language handling
                    if PDFPLUMBER_AVAILABLE and not text.strip():
                        try:
                            with pdfplumber.open(pdf_path) as plumber_pdf:
                                plumber_page = plumber_pdf.pages[page_num]
                                # Try different extraction methods
                                plumber_text = plumber_page.extract_text()
                                
                                # Check if extracted text has CID encoding
                                if plumber_text and '(cid:' not in plumber_text.lower() and plumber_text.strip():
                                    text = plumber_text
                                    extraction_method = "pdfplumber"
                        except Exception as e:
                            # pdfplumber failed, continue to other methods
                            logger.debug(f"pdfplumber extraction failed for page {page_label}: {e}")
                            pass
                    
                    # Try PyMuPDF if pdfplumber didn't work
                    if not text.strip():
                        page = pdf_doc[page_num]
                        mupdf_text = page.get_text()
                        if mupdf_text and mupdf_text.strip():
                            text = mupdf_text
                            extraction_method = "PyMuPDF"
                    
                    # Check if text looks garbled or is CID-encoded
                    # Look for common garbled patterns or CID codes
                    is_garbled = False
                    if text:
                        # Check for CID encoding patterns like (cid:xxx)
                        if '(cid:' in text.lower():
                            is_garbled = True
                        # Check for common garbled character patterns
                        elif any(char in text for char in ['Ú', 'Ë', '˙', 'ﬁ', '˜', 'Æ', '∆', '®', '¥', '∫', '√', '∂', '∑']):
                            is_garbled = True
                        # Check if text has too many special/control characters
                        elif len([c for c in text if ord(c) < 32 or (ord(c) > 126 and ord(c) < 256)]) > len(text) * 0.3:
                            is_garbled = True
                    
                    if is_garbled:
                        # Text appears to be garbled or CID-encoded, force OCR
                        logger.info(f"Page {page_label}: Detected garbled/CID-encoded text, will attempt OCR")
                        text = ""
                        extraction_method = ""
                    
                    # Enhanced check if text extraction was truly successful
                    # Don't just check if text exists, check if it's meaningful
                    text_is_meaningful = False
                    if text.strip():
                        import re
                        # Check if text is more than just page numbers or minimal headers
                        # Common patterns that shouldn't count as successful extraction
                        minimal_patterns = [
                            r'^\s*\d+\s*$',  # Just a number (likely page number)
                            r'^\s*Page\s*\d+\s*$',  # "Page X" format
                            r'^\s*\d+\s*/\s*\d+\s*$',  # "X/Y" page format
                            r'^\s*[IVXivx]+\s*$',  # Roman numerals only
                        ]
                        
                        # Strip and check if it's just minimal text
                        stripped_text = text.strip()
                        is_minimal = any(re.match(pattern, stripped_text) for pattern in minimal_patterns)
                        
                        # Also check if text is suspiciously short (less than 50 chars is likely just headers)
                        # But allow short text if there are no images on the page
                        page = pdf_doc[page_num]
                        has_images = len(page.get_images()) > 0
                        
                        # Text is meaningful if:
                        # 1. It's not matching minimal patterns AND
                        # 2. Either it's reasonably long OR there are no images (might be a genuine short page)
                        text_is_meaningful = (
                            not is_minimal and 
                            (len(stripped_text) > 50 or not has_images)
                        )
                        
                        # If text exists but seems insufficient and page has images, try OCR anyway
                        if not text_is_meaningful and has_images and ocr_fallback and PDF2IMAGE_AVAILABLE:
                            # Mark that we should try OCR
                            logger.info(f"Page {page_label}: Extracted text seems minimal ({len(stripped_text)} chars) with images present, will attempt OCR")
                            text = ""
                            extraction_method = ""
                    
                    # Check if text extraction was truly successful
                    if text.strip() and text_is_meaningful:
                        # Text extraction worked and is meaningful
                        extracted_text.append(f"--- Page {page_label} ({extraction_method}) ---\n{text}")
                    elif ocr_fallback:
                        # Try OpenAI Vision API for OCR
                        logger.info(f"Page {page_label}: No meaningful text extracted, attempting OCR with OpenAI Vision...")
                        ocr_text = PDFService.extract_text_with_vision(
                            pdf_path=pdf_path,
                            page_number=page_label,
                            dpi=ocr_dpi
                        )
                        
                        if ocr_text:
                            logger.info(f"Page {page_label}: Vision API OCR successful, extracted {len(ocr_text)} characters")
                            extracted_text.append(f"--- Page {page_label} (Vision OCR) ---\n{ocr_text}")
                        else:
                            # Vision OCR didn't find any text or failed
                            logger.warning(f"Page {page_label}: Vision API OCR completed but no text found")
                            extracted_text.append(f"--- Page {page_label} (Vision OCR - no text found) ---\n")
                    else:
                        # No text and OCR disabled
                        extracted_text.append(f"--- Page {page_label} (text - empty) ---\n")
                
                return "\n\n".join(extracted_text)
        
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def split_pdf_by_pages(pdf_path: str, output_path: str, start_page: int, end_page: int) -> str:
        """
        Split a PDF file and save specific pages as a new PDF.
        
        Args:
            pdf_path: Path to the source PDF file
            output_path: Path where the split PDF should be saved
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, inclusive)
            
        Returns:
            Path to the created PDF file
        """
        try:
            # Open the source PDF
            with fitz.open(pdf_path) as pdf_doc:
                # Validate page numbers
                total_pages = len(pdf_doc)
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    raise ValueError(f"Invalid page range. PDF has {total_pages} pages.")
                
                # Create a new PDF with only the specified pages
                new_pdf = fitz.open()  # Create new empty PDF
                
                # Add pages from the specified range
                for page_num in range(start_page - 1, end_page):  # Convert to 0-based indexing
                    new_pdf.insert_pdf(pdf_doc, from_page=page_num, to_page=page_num)
                
                # Ensure the output directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Save the new PDF
                new_pdf.save(output_path)
                new_pdf.close()
                
                return output_path
        
        except Exception as e:
            raise Exception(f"Error splitting PDF: {str(e)}")
    
    @staticmethod
    def extract_all_text(pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            All text content as a string
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                all_text = []
                for page_num, page in enumerate(pdf_doc, 1):
                    text = page.get_text()
                    all_text.append(f"--- Page {page_num} ---\n{text}")
                
                return "\n\n".join(all_text)
        
        except Exception as e:
            raise Exception(f"Error extracting all text from PDF: {str(e)}")
    
    @staticmethod
    def extract_indian_language_text(pdf_path: str, start_page: int, end_page: int) -> str:
        """
        Specialized extraction for Indian language PDFs.
        Tries multiple methods to get the best text extraction.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, inclusive)
            
        Returns:
            Extracted text with better Indian language support
        """
        extracted_text = []
        
        # Method 1: Try pdfplumber with better layout preservation
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                        page = pdf.pages[page_num]
                        page_label = page_num + 1
                        
                        # Extract with layout preservation
                        text = page.extract_text(
                            layout=True,  # Preserve layout
                            x_density=7.25,  # Higher density for better character recognition
                            y_density=13
                        )
                        
                        if text and text.strip():
                            extracted_text.append(f"--- Page {page_label} ---\n{text}")
                        else:
                            # Try table extraction if no text found
                            tables = page.extract_tables()
                            if tables:
                                table_text = "\n".join([
                                    "\n".join([" | ".join(row) for row in table if row])
                                    for table in tables
                                ])
                                extracted_text.append(f"--- Page {page_label} (tables) ---\n{table_text}")
                
                if extracted_text:
                    return "\n\n".join(extracted_text)
            except Exception as e:
                print(f"pdfplumber extraction failed: {e}")
        
        # Fall back to the standard method with OCR
        return PDFService.extract_text_from_pages(
            pdf_path, 
            start_page, 
            end_page,
            ocr_language="eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori"
        )
    
    @staticmethod
    def get_page_info(pdf_path: str, page_number: int) -> dict:
        """
        Get information about a specific page in the PDF.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number (1-based)
            
        Returns:
            Dictionary containing page information
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                if page_number < 1 or page_number > len(pdf_doc):
                    raise ValueError(f"Invalid page number. PDF has {len(pdf_doc)} pages.")
                
                page = pdf_doc[page_number - 1]  # Convert to 0-based indexing
                
                return {
                    "page_number": page_number,
                    "width": page.rect.width,
                    "height": page.rect.height,
                    "text_length": len(page.get_text()),
                    "has_images": len(page.get_images()) > 0
                }
        
        except Exception as e:
            raise Exception(f"Error getting page info: {str(e)}")
    
    @staticmethod
    def extract_text_with_vision(pdf_path: str, page_number: int, dpi: int = 300) -> str:
        """
        Extract text from a PDF page using OpenAI Vision API.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number to extract (1-indexed)
            dpi: DPI for image conversion (default 300)
            
        Returns:
            Extracted text from the page, or empty string if failed
        """
        try:
            # First check if pdf2image is available for conversion
            if not PDF2IMAGE_AVAILABLE:
                logger.error("pdf2image library not available for Vision OCR")
                return ""
            
            # Import AI service here to avoid circular dependencies
            from app.services.ai_service import AIService
            
            # Convert the specific page to image
            try:
                images = convert_from_path(
                    pdf_path,
                    first_page=page_number,
                    last_page=page_number,
                    dpi=dpi
                )
                
                if not images:
                    logger.error(f"Failed to convert page {page_number} to image")
                    return ""
                
                # Get the page image
                page_image = images[0]
                
                # Initialize AI service and process with Vision API
                ai_service = AIService()
                extracted_text = ai_service.process_image_with_vision(page_image)
                
                return extracted_text
                
            except Exception as conv_error:
                logger.error(f"Error converting page {page_number} to image: {str(conv_error)}")
                return ""
                
        except Exception as e:
            logger.error(f"Vision API OCR failed for page {page_number}: {str(e)}")
            return ""
    
    @staticmethod
    def convert_pdf_pages_batch(
        pdf_path: str, 
        page_numbers: List[int], 
        dpi: int = 300
    ) -> List[Tuple[int, Image.Image]]:
        """
        Convert multiple PDF pages to images in batch.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to convert (1-indexed)
            dpi: DPI for image conversion
            
        Returns:
            List of tuples (page_number, PIL Image)
        """
        if not PDF2IMAGE_AVAILABLE:
            logger.error("pdf2image library not available for batch conversion")
            return []
        
        try:
            # Sort page numbers to optimize conversion
            page_numbers_sorted = sorted(page_numbers)
            
            # Convert pages in chunks to manage memory
            result_images = []
            
            for page_num in page_numbers_sorted:
                try:
                    # Convert single page to avoid memory issues with large batches
                    images = convert_from_path(
                        pdf_path,
                        first_page=page_num,
                        last_page=page_num,
                        dpi=dpi,
                        thread_count=4  # Use multiple threads for faster conversion
                    )
                    
                    if images:
                        result_images.append((page_num, images[0]))
                        logger.debug(f"Converted page {page_num} to image")
                    
                except Exception as e:
                    logger.error(f"Failed to convert page {page_num}: {str(e)}")
                    # Continue with other pages even if one fails
            
            return result_images
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {str(e)}")
            return []
    
    @staticmethod
    async def extract_text_with_vision_batch(
        pdf_path: str,
        page_numbers: List[int],
        dpi: int = 300,
        progress_callback = None
    ) -> Dict[int, str]:
        """
        Extract text from multiple PDF pages using Vision API with batch processing.
        
        Args:
            pdf_path: Path to the PDF file
            page_numbers: List of page numbers to process (1-indexed)
            dpi: DPI for image conversion
            progress_callback: Optional async callback for progress updates
            
        Returns:
            Dictionary mapping page numbers to extracted text
        """
        # Import here to avoid circular dependencies
        from app.services.ai_service import AsyncVisionBatchProcessor
        
        results = {}
        
        try:
            # Process pages in chunks to manage memory
            chunk_size = settings.vision_batch_size
            page_chunks = [
                page_numbers[i:i + chunk_size] 
                for i in range(0, len(page_numbers), chunk_size)
            ]
            
            async with AsyncVisionBatchProcessor() as processor:
                for chunk_idx, chunk_pages in enumerate(page_chunks):
                    logger.info(f"Processing chunk {chunk_idx + 1}/{len(page_chunks)} with {len(chunk_pages)} pages")
                    
                    # Convert pages to images using ThreadPoolExecutor for CPU-bound task
                    with ThreadPoolExecutor(max_workers=4) as executor:
                        loop = asyncio.get_event_loop()
                        images = await loop.run_in_executor(
                            executor,
                            PDFService.convert_pdf_pages_batch,
                            pdf_path,
                            chunk_pages,
                            dpi
                        )
                    
                    if not images:
                        logger.warning(f"No images converted for chunk {chunk_idx + 1}")
                        continue
                    
                    # Process images with Vision API in parallel
                    chunk_results = await processor.process_image_batch(
                        images,
                        progress_callback=progress_callback
                    )
                    
                    # Merge results
                    results.update(chunk_results)
                    
                    # Clean up images to free memory
                    for _, img in images:
                        img.close()
                    
                    logger.info(f"Completed chunk {chunk_idx + 1}/{len(page_chunks)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch Vision processing failed: {str(e)}")
            return results  # Return partial results if available
    
    @staticmethod
    async def process_pdf_with_vision_parallel(
        pdf_path: str,
        start_page: int = 1,
        end_page: Optional[int] = None,
        ocr_threshold: float = 0.1,
        progress_callback = None
    ) -> str:
        """
        Process PDF with parallel Vision OCR for pages that need it.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page (1-indexed)
            end_page: Ending page (1-indexed), None for all pages
            ocr_threshold: Minimum text density to skip OCR
            progress_callback: Optional async callback for progress
            
        Returns:
            Extracted text from all pages
        """
        try:
            # First, identify which pages need OCR
            pages_needing_ocr = []
            all_text = {}
            
            # Get total pages
            with fitz.open(pdf_path) as pdf_doc:
                total_pages = len(pdf_doc)
                if end_page is None:
                    end_page = total_pages
                
                # Quick scan to identify pages needing OCR
                for page_num in range(start_page - 1, min(end_page, total_pages)):
                    page = pdf_doc[page_num]
                    text = page.get_text()
                    
                    # Check if page needs OCR (low text content)
                    if len(text.strip()) < 50:  # Less than 50 chars indicates image-based page
                        pages_needing_ocr.append(page_num + 1)  # Convert to 1-indexed
                        logger.info(f"Page {page_num + 1} marked for Vision OCR")
                    else:
                        # Store text for pages that don't need OCR
                        all_text[page_num + 1] = text
            
            # Process pages needing OCR in parallel
            if pages_needing_ocr:
                logger.info(f"Processing {len(pages_needing_ocr)} pages with Vision OCR in parallel")
                ocr_results = await PDFService.extract_text_with_vision_batch(
                    pdf_path,
                    pages_needing_ocr,
                    progress_callback=progress_callback
                )
                
                # Merge OCR results
                all_text.update(ocr_results)
            
            # Sort by page number and combine
            sorted_pages = sorted(all_text.keys())
            combined_text = []
            
            for page_num in sorted_pages:
                text = all_text.get(page_num, "")
                if text:
                    combined_text.append(f"--- Page {page_num} ---\n{text}")
            
            return "\n\n".join(combined_text)
            
        except Exception as e:
            logger.error(f"Parallel PDF processing failed: {str(e)}")
            # Fall back to sequential processing
            return PDFService.extract_text_from_pages(
                pdf_path, start_page, end_page, ocr_fallback=True
            )
    
    @staticmethod
    async def extract_text_from_pages_async(
        pdf_path: str,
        start_page: int,
        end_page: int,
        use_batch_vision: bool = True,
        ocr_fallback: bool = True,
        progress_callback = None
    ) -> str:
        """
        Async version of extract_text_from_pages with batch Vision processing.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page (1-indexed)
            end_page: Ending page (1-indexed)
            use_batch_vision: Use batch Vision processing for better performance
            ocr_fallback: Whether to use Vision OCR for image pages
            progress_callback: Optional callback for progress updates
            
        Returns:
            Extracted text from the PDF
        """
        if use_batch_vision and ocr_fallback:
            # Use parallel Vision processing
            return await PDFService.process_pdf_with_vision_parallel(
                pdf_path,
                start_page,
                end_page,
                progress_callback=progress_callback
            )
        else:
            # Use traditional synchronous extraction
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    PDFService.extract_text_from_pages,
                    pdf_path,
                    start_page,
                    end_page,
                    ocr_fallback
                )
            return result
    
    def extract_pages_as_pdf(self, pdf_path: str, start_page: int, end_page: int) -> bytes:
        """
        Extract specific pages from a PDF and return as bytes.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed)
            
        Returns:
            bytes: PDF content as bytes
        """
        import PyPDF2
        from io import BytesIO
        
        # Validate page numbers
        if start_page < 1 or end_page < start_page:
            raise ValueError("Invalid page range")
        
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Validate against total pages
            if start_page > total_pages or end_page > total_pages:
                raise ValueError(f"Page range exceeds document length ({total_pages} pages)")
            
            # Create a new PDF with selected pages
            pdf_writer = PyPDF2.PdfWriter()
            
            # Add pages (convert to 0-indexed)
            for page_num in range(start_page - 1, end_page):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            # Write to bytes
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.read()