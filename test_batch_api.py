#!/usr/bin/env python3
"""
Test script for the /chapters/batch endpoint
"""

import requests
import json

# API endpoint
url = "http://127.0.0.1:8000/api/v1/chapters/batch"

# Test data - creating multiple chapters for textbook ID 7
payload = {
    "textbook_id": 7,
    "chapters": [
        {
            "title": "Introduction to Programming",
            "chapter_number": 1,
            "start_page": 1,
            "end_page": 25
        },
        {
            "title": "Variables and Data Types",
            "chapter_number": 2,
            "start_page": 26,
            "end_page": 50
        },
        {
            "title": "Control Flow",
            "chapter_number": 3,
            "start_page": 51,
            "end_page": 75
        },
        {
            "title": "Functions and Modules",
            "chapter_number": 4,
            "start_page": 76,
            "end_page": 100
        },
        {
            "title": "Object-Oriented Programming",
            "chapter_number": 5,
            "start_page": 101,
            "end_page": 0  # This will be auto-fixed by the API
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json"
}

print("Sending batch chapter creation request...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    # Send POST request with timeout
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    # Check response status
    if response.status_code == 200:
        print("✅ Success! Chapters created.")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error: Status code {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 30 seconds")
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to the server. Is it running?")
except Exception as e:
    print(f"❌ An error occurred: {e}")

print("\n" + "="*50)
print("Alternative curl command (copy and paste to terminal):")
print("="*50)
print(f"""
curl -X POST "{url}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(payload)}'
""")