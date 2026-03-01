"""
PDF processing service.
Handles PDF text extraction, page splitting, and other PDF operations.
"""

import fitz  # PyMuPDF
from typing import List, Tuple, Optional
import os
from pathlib import Path
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

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
    def needs_ocr(pdf_path: str, sample_page: int = 1) -> bool:
        """
        Check if a PDF needs OCR by testing text extraction on a sample page.
        
        Args:
            pdf_path: Path to the PDF file
            sample_page: Page number to test (1-based, default: 1)
            
        Returns:
            True if OCR is needed, False otherwise
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                if sample_page > len(pdf_doc):
                    sample_page = 1
                
                page = pdf_doc[sample_page - 1]
                text = page.get_text()
                
                # Check if text is empty or garbled
                if not text or not text.strip():
                    return True
                
                # Check for CID encoding
                if '(cid:' in text.lower():
                    return True
                
                # Check for garbled characters
                if any(char in text for char in ['Ú', 'Ë', '˙', 'ﬁ', '˜', 'Æ', '∆', '®', '¥', '∫', '√', '∂', '∑']):
                    return True
                
                # Check for too many non-ASCII characters in non-Unicode range
                non_ascii = len([c for c in text if ord(c) < 32 or (ord(c) > 126 and ord(c) < 256)])
                if non_ascii > len(text) * 0.3:
                    return True
                
                return False
        except:
            return True
    
    @staticmethod
    def extract_text_from_pages(pdf_path: str, start_page: int, end_page: int,
                                ocr_fallback: bool = True, ocr_language: str = "eng+hin+tam+tel+kan+mal+mar+guj+ben+pan+ori",
                                ocr_dpi: int = 300, ocr_config: str = None) -> str:
        """
        Extract text from specified page range in a PDF with OCR fallback for image-based pages.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, inclusive)
            ocr_fallback: Whether to use OCR for pages with no text (default: True)
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
                        text = ""
                        extraction_method = ""
                    
                    # Check if text extraction was successful
                    if text.strip():
                        # Text extraction worked
                        extracted_text.append(f"--- Page {page_label} ({extraction_method}) ---\n{text}")
                    elif ocr_fallback and OCR_AVAILABLE:
                        # Try OCR fallback for image-based pages
                        try:
                            # Convert only the specific page to image
                            images = convert_from_path(
                                pdf_path,
                                first_page=page_label,
                                last_page=page_label,
                                dpi=ocr_dpi
                            )
                            
                            if images:
                                # Run OCR on the page image with language support
                                # Use custom config for better Indian language recognition
                                config = ocr_config or "--oem 3 --psm 6"
                                ocr_text = pytesseract.image_to_string(
                                    images[0],
                                    lang=ocr_language,
                                    config=config
                                )
                                
                                if ocr_text.strip():
                                    extracted_text.append(f"--- Page {page_label} (OCR) ---\n{ocr_text}")
                                else:
                                    # OCR didn't find any text
                                    extracted_text.append(f"--- Page {page_label} (OCR - no text found) ---\n")
                            else:
                                extracted_text.append(f"--- Page {page_label} (OCR - conversion failed) ---\n")
                        
                        except Exception as ocr_error:
                            # OCR failed, add error note
                            extracted_text.append(
                                f"--- Page {page_label} (OCR failed: {str(ocr_error)}) ---\n"
                            )
                    elif ocr_fallback and not OCR_AVAILABLE:
                        # OCR requested but libraries not available
                        extracted_text.append(
                            f"--- Page {page_label} (text - empty, OCR unavailable) ---\n"
                            f"Note: Install 'pdf2image' and 'pytesseract' for OCR support\n"
                        )
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