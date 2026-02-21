#!/usr/bin/env python3
"""
Example workflow for using the AI Teaching Assistant API.

This script demonstrates the complete workflow:
1. Upload a PDF textbook
2. Set table of contents pages
3. Detect chapters using AI
4. Create chapters with page ranges
5. Generate summaries

Prerequisites:
- Server running at http://localhost:8000
- OpenAI API key set in .env file
- A PDF file to upload
"""

import requests
import json
import os
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

def upload_textbook(pdf_path: str, title: str, author: Optional[str] = None):
    """
    Upload a PDF textbook to the system.
    
    Args:
        pdf_path: Path to the PDF file
        title: Title of the textbook
        author: Author name (optional)
    
    Returns:
        Textbook ID if successful
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return None
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        data = {'title': title}
        if author:
            data['author'] = author
        
        response = requests.post(f"{BASE_URL}/textbooks/upload", files=files, data=data)
    
    if response.status_code == 200:
        print("✅ Textbook uploaded successfully!")
        # Get the textbook ID from the list
        textbooks = requests.get(f"{BASE_URL}/textbooks/").json()
        if textbooks:
            return textbooks[-1]['id']  # Return the latest textbook ID
    else:
        print(f"❌ Upload failed: {response.json()}")
        return None

def set_toc_pages(textbook_id: int, start_page: int, end_page: int):
    """
    Set and extract table of contents pages.
    
    Args:
        textbook_id: ID of the textbook
        start_page: Starting page of TOC
        end_page: Ending page of TOC
    
    Returns:
        Extracted TOC text
    """
    data = {
        "start_page": start_page,
        "end_page": end_page
    }
    
    response = requests.post(f"{BASE_URL}/extract/textbook/{textbook_id}/set-toc", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ TOC extracted from pages {start_page}-{end_page}")
        print(f"Preview: {result['extracted_text'][:200]}...")
        return result['extracted_text']
    else:
        print(f"❌ TOC extraction failed: {response.json()}")
        return None

def detect_chapters(textbook_id: int):
    """
    Use AI to detect chapters from the table of contents.
    
    Args:
        textbook_id: ID of the textbook
    
    Returns:
        List of detected chapters
    """
    data = {"textbook_id": textbook_id}
    response = requests.post(f"{BASE_URL}/chapters/detect", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Detected {result['total_chapters']} chapters:")
        for chapter in result['detected_chapters']:
            print(f"   Chapter {chapter['chapter_number']}: {chapter['title']}")
        return result['detected_chapters']
    else:
        print(f"❌ Chapter detection failed: {response.json()}")
        return None

def create_chapters(textbook_id: int, chapters_data: list):
    """
    Create chapters with specific page ranges.
    
    Args:
        textbook_id: ID of the textbook
        chapters_data: List of chapter data with page ranges
    
    Returns:
        Created chapters
    """
    # Prepare the batch creation data
    chapters = []
    for i, chapter in enumerate(chapters_data, 1):
        chapters.append({
            "chapter_number": i,
            "title": chapter.get('title', f'Chapter {i}'),
            "start_page": chapter['start_page'],
            "end_page": chapter['end_page']
        })
    
    data = {
        "textbook_id": textbook_id,
        "chapters": chapters
    }
    
    response = requests.post(f"{BASE_URL}/chapters/batch", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Created {result['created_count']} chapters")
        return result['chapters']
    else:
        print(f"❌ Chapter creation failed: {response.json()}")
        return None

def generate_summary(chapter_id: int):
    """
    Generate AI summary for a chapter.
    
    Args:
        chapter_id: ID of the chapter
    
    Returns:
        Generated summary
    """
    response = requests.post(f"{BASE_URL}/chapters/{chapter_id}/generate-summary")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Summary generated for chapter: {result['chapter_title']}")
        print(f"Summary: {result['summary'][:200]}...")
        print(f"Key concepts: {', '.join(result['key_concepts'][:5])}")
        return result
    else:
        print(f"❌ Summary generation failed: {response.json()}")
        return None

def example_workflow():
    """
    Complete example workflow.
    """
    print("=" * 60)
    print("AI Teaching Assistant - Example Workflow")
    print("=" * 60)
    print()
    
    # Example data - replace with your actual values
    print("📝 Example usage (modify these values for your use case):\n")
    
    print("# Step 1: Upload a textbook")
    print('textbook_id = upload_textbook("math_textbook.pdf", "Mathematics Grade 10", "John Doe")')
    print()
    
    print("# Step 2: Set table of contents pages (e.g., pages 3-5)")
    print("toc_text = set_toc_pages(textbook_id, 3, 5)")
    print()
    
    print("# Step 3: Detect chapters using AI")
    print("detected_chapters = detect_chapters(textbook_id)")
    print()
    
    print("# Step 4: Create chapters with page ranges")
    print("chapters_data = [")
    print('    {"title": "Introduction to Algebra", "start_page": 10, "end_page": 25},')
    print('    {"title": "Linear Equations", "start_page": 26, "end_page": 45},')
    print('    {"title": "Quadratic Functions", "start_page": 46, "end_page": 70},')
    print("]")
    print("created_chapters = create_chapters(textbook_id, chapters_data)")
    print()
    
    print("# Step 5: Generate summary for a chapter")
    print("if created_chapters:")
    print("    summary = generate_summary(created_chapters[0]['id'])")
    print()
    
    print("-" * 60)
    print("\n💡 Tips:")
    print("1. Make sure your OpenAI API key is set in the .env file")
    print("2. The server must be running: uvicorn app.main:app --reload")
    print("3. Visit http://localhost:8000/docs for interactive API testing")
    print("4. Check the README.md for more detailed documentation")

if __name__ == "__main__":
    example_workflow()
    
    # Uncomment below to run with actual files:
    # textbook_id = upload_textbook("your_textbook.pdf", "Your Textbook Title", "Author Name")
    # if textbook_id:
    #     toc_text = set_toc_pages(textbook_id, 3, 5)  # Adjust page numbers
    #     if toc_text:
    #         detected_chapters = detect_chapters(textbook_id)
    #         # Create chapters with your page ranges
    #         chapters_data = [
    #             {"title": "Chapter 1", "start_page": 10, "end_page": 25},
    #             # Add more chapters...
    #         ]
    #         created_chapters = create_chapters(textbook_id, chapters_data)
    #         if created_chapters:
    #             generate_summary(created_chapters[0]['id'])