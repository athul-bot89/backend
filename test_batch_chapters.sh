#!/bin/bash

# Curl request to create multiple chapters at once using the /chapters/batch endpoint
# This example assumes textbook_id 7 exists (adjust as needed)

echo "Creating multiple chapters for textbook ID 7..."
echo ""

curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Introduction to Computer Science",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 25
      },
      {
        "title": "Data Structures and Algorithms",
        "chapter_number": 2,
        "start_page": 26,
        "end_page": 60
      },
      {
        "title": "Database Management Systems",
        "chapter_number": 3,
        "start_page": 61,
        "end_page": 95
      },
      {
        "title": "Operating Systems",
        "chapter_number": 4,
        "start_page": 96,
        "end_page": 130
      },
      {
        "title": "Computer Networks",
        "chapter_number": 5,
        "start_page": 131,
        "end_page": 0
      }
    ]
  }' | python3 -m json.tool

echo ""
echo "Note: The last chapter has end_page set to 0, which will be auto-fixed by the API"
echo "It will either use the textbook's total pages or a default value"