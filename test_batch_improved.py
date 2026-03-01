#!/usr/bin/env python3
"""
Test script for the improved batch chapter creation endpoint.
Tests both synchronous and asynchronous processing modes.
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_batch_creation(textbook_id: int, async_mode: bool = True):
    """Test batch chapter creation with different processing modes."""
    
    # Sample chapters data
    chapters_data = {
        "textbook_id": textbook_id,
        "chapters": [
            {
                "title": "Introduction to Science",
                "chapter_number": 1,
                "start_page": 1,
                "end_page": 15
            },
            {
                "title": "Basic Mathematics",
                "chapter_number": 2,
                "start_page": 16,
                "end_page": 30
            },
            {
                "title": "Physics Fundamentals",
                "chapter_number": 3,
                "start_page": 31,
                "end_page": 45
            }
        ]
    }
    
    # Add async_processing parameter
    params = {"async_processing": async_mode}
    
    print(f"\n{'='*50}")
    print(f"Testing Batch Creation - Async Mode: {async_mode}")
    print(f"{'='*50}")
    
    # Send request
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/chapters/batch",
            json=chapters_data,
            params=params,
            timeout=30  # 30 second timeout
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success! Created {result['created_count']} chapters")
            print(f"  Time taken: {elapsed:.2f} seconds")
            if 'message' in result:
                print(f"  Message: {result['message']}")
            
            # Show chapter details
            print("\nCreated chapters:")
            for ch in result['chapters']:
                print(f"  - Chapter {ch['chapter_number']}: {ch['title']}")
                print(f"    Status: {ch.get('processing_status', 'unknown')}")
                print(f"    Pages: {ch['start_page']}-{ch['end_page']}")
            
            return result
        else:
            print(f"✗ Failed with status {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"✗ Request timed out after {elapsed:.2f} seconds")
        return None
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Error: {str(e)}")
        print(f"  Time before error: {elapsed:.2f} seconds")
        return None

def check_processing_status(textbook_id: int):
    """Check the processing status of chapters."""
    
    print(f"\n{'='*50}")
    print("Checking Processing Status")
    print(f"{'='*50}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/chapters/textbook/{textbook_id}/processing-status"
        )
        
        if response.status_code == 200:
            status = response.json()
            summary = status['summary']
            
            print("\nStatus Summary:")
            print(f"  Total chapters: {summary['total']}")
            print(f"  ✓ Completed: {summary['completed']}")
            print(f"  ⚡ PDF Ready: {summary['pdf_ready']}")
            print(f"  ⏳ Processing: {summary['processing']}")
            print(f"  ⏸ Pending: {summary['pending']}")
            print(f"  ✗ Failed: {summary['failed']}")
            
            if summary.get('text_extraction_failed', 0) > 0:
                print(f"  ⚠ Text extraction failed: {summary['text_extraction_failed']}")
            
            print("\nChapter Details:")
            for ch in status['chapters']:
                status_icon = {
                    'completed': '✓',
                    'pdf_ready': '📄',
                    'processing': '⏳',
                    'pending': '⏸',
                    'failed': '✗'
                }.get(ch['status'], '?')
                
                print(f"  {status_icon} Chapter {ch['chapter_number']}: {ch['title']}")
                print(f"     Status: {ch['status']}")
                if ch['error']:
                    print(f"     Error: {ch['error']}")
                print(f"     Has PDF: {ch['has_pdf']}, Has Text: {ch['has_text']}")
            
            return status
        else:
            print(f"✗ Failed to get status: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error checking status: {str(e)}")
        return None

def main():
    """Main test function."""
    
    print("Batch Chapter Creation Test - Improved Version")
    print("=" * 60)
    
    # You'll need to replace this with an actual textbook ID from your database
    textbook_id = 1  # Change this to your actual textbook ID
    
    # Test 1: Asynchronous processing (fast response)
    print("\nTest 1: Asynchronous Processing (Background)")
    result = test_batch_creation(textbook_id, async_mode=True)
    
    if result:
        # Wait a bit and check status
        print("\nWaiting 2 seconds before checking status...")
        time.sleep(2)
        check_processing_status(textbook_id)
    
    # Test 2: Synchronous processing (waits for PDF splitting)
    print("\n" + "="*60)
    print("\nTest 2: Synchronous Processing (Wait for PDFs)")
    result = test_batch_creation(textbook_id + 1, async_mode=False)  # Use different textbook to avoid conflicts
    
    if result:
        check_processing_status(textbook_id + 1)
    
    print("\n" + "="*60)
    print("Testing complete!")

if __name__ == "__main__":
    main()