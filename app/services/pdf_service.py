"""
PDF processing service.
Handles PDF text extraction, page splitting, and other PDF operations.
"""

import fitz  # PyMuPDF
from typing import List, Tuple, Optional
import os
from pathlib import Path

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
    def extract_text_from_pages(pdf_path: str, start_page: int, end_page: int) -> str:
        """
        Extract text from specified page range in a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            start_page: Starting page number (1-based)
            end_page: Ending page number (1-based, inclusive)
            
        Returns:
            Extracted text as a string
        """
        try:
            with fitz.open(pdf_path) as pdf_doc:
                # Validate page numbers
                total_pages = len(pdf_doc)
                if start_page < 1 or end_page > total_pages or start_page > end_page:
                    raise ValueError(f"Invalid page range. PDF has {total_pages} pages.")
                
                # Extract text from each page in the range
                extracted_text = []
                for page_num in range(start_page - 1, end_page):  # Convert to 0-based indexing
                    page = pdf_doc[page_num]
                    text = page.get_text()
                    extracted_text.append(f"--- Page {page_num + 1} ---\n{text}")
                
                return "\n\n".join(extracted_text)
        
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