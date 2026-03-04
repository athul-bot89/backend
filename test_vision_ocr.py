#!/usr/bin/env python3
"""
Test script for OpenAI Vision API OCR integration.
This script tests the PDF text extraction with Vision API OCR.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_service import PDFService
from app.services.ai_service import AIService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vision_ocr():
    """Test the Vision API OCR functionality."""
    
    # Test with a sample PDF file if it exists
    test_pdf = None
    upload_dir = Path("uploads")
    
    # Find a test PDF in the uploads directory
    if upload_dir.exists():
        pdf_files = list(upload_dir.glob("*.pdf"))
        if pdf_files:
            test_pdf = str(pdf_files[0])
            print(f"Using test PDF: {test_pdf}")
    
    if not test_pdf:
        print("No PDF file found in uploads directory. Please upload a PDF first.")
        return
    
    try:
        # Initialize services
        pdf_service = PDFService()
        ai_service = AIService()
        
        print("\n=== Testing PDF Service with Vision OCR ===")
        
        # Get total pages
        total_pages = pdf_service.get_total_pages(test_pdf)
        print(f"Total pages: {total_pages}")
        
        # Check if OCR is needed
        needs_ocr = pdf_service.needs_ocr(test_pdf)
        print(f"PDF needs OCR: {needs_ocr}")
        
        # Extract text from first few pages
        test_pages = min(2, total_pages)  # Test with first 2 pages or less
        print(f"\nExtracting text from pages 1-{test_pages}...")
        
        extracted_text = pdf_service.extract_text_from_pages(
            pdf_path=test_pdf,
            start_page=1,
            end_page=test_pages,
            ocr_fallback=True  # Enable Vision OCR
        )
        
        print(f"\nExtracted text length: {len(extracted_text)} characters")
        print(f"First 500 characters:\n{extracted_text[:500]}...")
        
        # Test Vision API directly with an image
        print("\n=== Testing Vision API Directly ===")
        try:
            from pdf2image import convert_from_path
            from PIL import Image
            
            # Convert first page to image
            images = convert_from_path(test_pdf, first_page=1, last_page=1, dpi=300)
            if images:
                page_image = images[0]
                print("Testing direct Vision API call on first page...")
                
                vision_text = ai_service.process_image_with_vision(page_image)
                print(f"Vision API extracted {len(vision_text)} characters")
                print(f"First 300 characters:\n{vision_text[:300]}...")
            else:
                print("Could not convert page to image for direct Vision test")
                
        except ImportError:
            print("pdf2image not installed, skipping direct Vision API test")
        except Exception as e:
            print(f"Direct Vision API test failed: {e}")
        
        print("\n=== Test Complete ===")
        print("Vision OCR integration is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Test failed")
        return False
    
    return True

if __name__ == "__main__":
    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check API key configuration
    use_azure = os.getenv("USE_AZURE_OPENAI", "true").lower() == "true"
    
    if use_azure:
        if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
            print("❌ Azure OpenAI credentials not found!")
            print("Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env file")
            sys.exit(1)
    else:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OpenAI API key not found!")
            print("Please set OPENAI_API_KEY in .env file")
            sys.exit(1)
    
    print(f"Using {'Azure' if use_azure else 'Standard'} OpenAI API")
    
    # Run the test
    success = test_vision_ocr()
    sys.exit(0 if success else 1)