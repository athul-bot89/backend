#!/bin/bash

echo "Testing simple chapter batch creation..."
echo "Creating a single chapter for textbook ID 7"
echo ""

# Use timeout command to avoid hanging
timeout 10 curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Test Chapter",
        "chapter_number": 99,
        "start_page": 1,
        "end_page": 5
      }
    ]
  }' -w "\n\nHTTP Status: %{http_code}\nTime Total: %{time_total}s\n"

echo ""
echo "If this hangs for 10 seconds, there might be an issue with the endpoint."