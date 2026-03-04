#!/usr/bin/env python3
"""
Demo script to show how OpenAI Vision API handles OCR when needed.
This creates a sample image with text to demonstrate Vision API OCR capabilities.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import AIService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image_with_text():
    """Create a test image with text for OCR testing."""
    # Create a white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a better font if available, otherwise use default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    # Add some text to the image
    y_position = 50
    
    # Title
    draw.text((50, y_position), "OpenAI Vision API OCR Test", font=title_font, fill='black')
    y_position += 60
    
    # Sample text in multiple languages
    test_texts = [
        "English: The quick brown fox jumps over the lazy dog.",
        "Numbers: 1234567890",
        "Special Characters: !@#$%^&*()_+-=[]{}|;:',.<>?/",
        "Mathematical: E = mc², π ≈ 3.14159, ∑(n=1 to ∞) 1/n²",
        "Mixed Case: OpenAI GPT-4 Vision API for OCR Processing",
        "",
        "This is a test image to demonstrate how the OpenAI Vision API",
        "can extract text from images. It replaces traditional OCR tools",
        "like Tesseract with a more powerful AI-based approach that can",
        "understand context, handle multiple languages, and even interpret",
        "complex layouts and formatting.",
        "",
        "Key Features:",
        "• Multi-language support",
        "• Better accuracy than traditional OCR",
        "• Context-aware text extraction",
        "• Handles handwriting and difficult fonts",
        "• Can understand tables and structured data",
    ]
    
    for text in test_texts:
        if text.startswith("•"):
            draw.text((70, y_position), text, font=font, fill='darkblue')
        elif text == "":
            y_position += 20  # Add space for empty lines
            continue
        else:
            draw.text((50, y_position), text, font=font, fill='black')
        y_position += 35
    
    return image

def test_vision_api_with_generated_image():
    """Test the Vision API with a generated image."""
    try:
        print("\n=== Creating Test Image ===")
        test_image = create_test_image_with_text()
        
        # Save the test image for reference
        test_image_path = "test_ocr_image.png"
        test_image.save(test_image_path)
        print(f"Test image saved to: {test_image_path}")
        
        print("\n=== Testing OpenAI Vision API ===")
        ai_service = AIService()
        
        # Process the image with Vision API
        extracted_text = ai_service.process_image_with_vision(test_image)
        
        print(f"\n=== Extracted Text ===")
        print(extracted_text)
        
        print(f"\n=== Statistics ===")
        print(f"Total characters extracted: {len(extracted_text)}")
        print(f"Lines extracted: {len(extracted_text.splitlines())}")
        
        print("\n✅ Vision API OCR test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Test failed")
        return False

def main():
    """Main function to run the OCR comparison test."""
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
    success = test_vision_api_with_generated_image()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()