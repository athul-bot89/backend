#!/usr/bin/env python3
"""
Test script to verify OCR improvements in PDF processing.
Tests the enhanced OCR detection and extraction logic.
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_service import PDFService

def test_needs_ocr():
    """Test the improved needs_ocr function."""
    print("Testing needs_ocr function...")
    
    # Check if there are any PDF files in the uploads directory
    uploads_dir = Path(__file__).parent / "uploads"
    if not uploads_dir.exists():
        print(f"Uploads directory not found: {uploads_dir}")
        return
    
    pdf_files = list(uploads_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in uploads directory")
        return
    
    # Test with the first PDF found
    pdf_path = str(pdf_files[0])
    print(f"\nTesting with PDF: {pdf_path}")
    
    # Test the needs_ocr function
    pdf_service = PDFService()
    
    # Test with default sampling (multiple pages)
    needs_ocr = pdf_service.needs_ocr(pdf_path)
    print(f"needs_ocr result (multi-page sampling): {needs_ocr}")
    
    # Test with specific pages
    total_pages = pdf_service.get_total_pages(pdf_path)
    print(f"Total pages in PDF: {total_pages}")
    
    if total_pages > 1:
        # Test first page only
        needs_ocr_first = pdf_service.needs_ocr(pdf_path, [1])
        print(f"needs_ocr for page 1 only: {needs_ocr_first}")
        
        # Test last page only
        needs_ocr_last = pdf_service.needs_ocr(pdf_path, [total_pages])
        print(f"needs_ocr for page {total_pages} only: {needs_ocr_last}")
    
    print("\n" + "="*50)

def test_extraction_with_logging():
    """Test text extraction with the new logging."""
    import logging
    
    # Set up logging to see our debug messages
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\nTesting text extraction with enhanced OCR detection...")
    
    # Check for PDF files
    uploads_dir = Path(__file__).parent / "uploads"
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in uploads directory")
        return
    
    pdf_path = str(pdf_files[0])
    pdf_service = PDFService()
    total_pages = pdf_service.get_total_pages(pdf_path)
    
    print(f"\nExtracting text from {pdf_path}")
    print(f"Total pages: {total_pages}")
    
    # Test extraction with OCR enabled
    print("\n--- Extraction WITH OCR enabled ---")
    if total_pages >= 3:
        # Extract first 3 pages
        text_with_ocr = pdf_service.extract_text_from_pages(
            pdf_path,
            start_page=1,
            end_page=min(3, total_pages),
            ocr_fallback=True
        )
        print(f"Extracted {len(text_with_ocr)} characters with OCR enabled")
        
        # Show first 500 characters
        print("\nFirst 500 characters of extracted text:")
        print(text_with_ocr[:500])
    else:
        # Extract all pages
        text_with_ocr = pdf_service.extract_text_from_pages(
            pdf_path,
            start_page=1,
            end_page=total_pages,
            ocr_fallback=True
        )
        print(f"Extracted {len(text_with_ocr)} characters with OCR enabled")
    
    print("\n" + "="*50)
    
    # Test extraction without OCR for comparison
    print("\n--- Extraction WITHOUT OCR ---")
    if total_pages >= 3:
        text_without_ocr = pdf_service.extract_text_from_pages(
            pdf_path,
            start_page=1,
            end_page=min(3, total_pages),
            ocr_fallback=False
        )
        print(f"Extracted {len(text_without_ocr)} characters without OCR")
    else:
        text_without_ocr = pdf_service.extract_text_from_pages(
            pdf_path,
            start_page=1,
            end_page=total_pages,
            ocr_fallback=False
        )
        print(f"Extracted {len(text_without_ocr)} characters without OCR")
    
    # Compare results
    print(f"\nDifference: {len(text_with_ocr) - len(text_without_ocr)} characters")
    if len(text_with_ocr) > len(text_without_ocr):
        print("✓ OCR extracted additional content!")
    elif len(text_with_ocr) == len(text_without_ocr):
        print("○ Same amount of content extracted (PDF might not need OCR)")
    else:
        print("⚠ Unexpected: Less content with OCR enabled")

def main():
    """Run all tests."""
    print("="*60)
    print("Testing OCR Improvements in PDF Processing")
    print("="*60)
    
    test_needs_ocr()
    test_extraction_with_logging()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()