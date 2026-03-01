# CURL Examples for /chapters/batch Endpoint

## Endpoint Details
- **URL**: `POST /api/v1/chapters/batch`
- **Purpose**: Create multiple chapters at once for a textbook
- **Features**: 
  - Batch creation of chapters
  - Auto-fixes end_page when set to 0
  - Splits PDFs for each chapter
  - Extracts text with Indian language OCR support

## Basic CURL Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Introduction",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 20
      },
      {
        "title": "Chapter 2: Fundamentals",
        "chapter_number": 2,
        "start_page": 21,
        "end_page": 45
      }
    ]
  }'
```

## Complete Example with Multiple Chapters

```bash
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
        "end_page": 165
      },
      {
        "title": "Software Engineering",
        "chapter_number": 6,
        "start_page": 166,
        "end_page": 200
      }
    ]
  }'
```

## Example with Auto-fixing End Pages

When `end_page` is 0, the API auto-fixes it:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Chapter 1",
        "chapter_number": 1,
        "start_page": 5,
        "end_page": 0
      },
      {
        "title": "Chapter 2",
        "chapter_number": 2,
        "start_page": 30,
        "end_page": 0
      },
      {
        "title": "Chapter 3",
        "chapter_number": 3,
        "start_page": 65,
        "end_page": 0
      }
    ]
  }'
```

## With Pretty JSON Output

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Sample Chapter",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 10
      }
    ]
  }' | python3 -m json.tool
```

## Save Response to File

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Chapter 1",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 25
      }
    ]
  }' -o response.json
```

## Using External JSON File

Create a file `chapters.json`:

```json
{
  "textbook_id": 7,
  "chapters": [
    {
      "title": "Chapter 1: Getting Started",
      "chapter_number": 1,
      "start_page": 1,
      "end_page": 30
    },
    {
      "title": "Chapter 2: Core Concepts",
      "chapter_number": 2,
      "start_page": 31,
      "end_page": 60
    },
    {
      "title": "Chapter 3: Advanced Topics",
      "chapter_number": 3,
      "start_page": 61,
      "end_page": 90
    }
  ]
}
```

Then run:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d @chapters.json
```

## With Verbose Output for Debugging

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -v \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Debug Test",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 5
      }
    ]
  }'
```

## With Timeout (Recommended if endpoint is slow)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  --max-time 60 \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Chapter with Timeout",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 10
      }
    ]
  }'
```

## Expected Response Format

Successful response (200 OK):

```json
{
  "created_count": 2,
  "chapters": [
    {
      "id": 1,
      "textbook_id": 7,
      "title": "Introduction",
      "chapter_number": 1,
      "start_page": 1,
      "end_page": 20,
      "pdf_path": "/path/to/chapters/textbook_7_chapter_1.pdf",
      "extracted_text": "...",
      "summary": null,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00",
      "has_pdf": true,
      "has_text": true,
      "has_summary": false
    },
    {
      "id": 2,
      "textbook_id": 7,
      "title": "Chapter 2: Fundamentals",
      "chapter_number": 2,
      "start_page": 21,
      "end_page": 45,
      "pdf_path": "/path/to/chapters/textbook_7_chapter_2.pdf",
      "extracted_text": "...",
      "summary": null,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00",
      "has_pdf": true,
      "has_text": true,
      "has_summary": false
    }
  ]
}
```

## Error Response Examples

Textbook not found (404):

```json
{
  "detail": "Textbook not found"
}
```

## Notes

1. **Performance**: This endpoint may take time if processing many chapters or large PDFs
2. **Duplicate Handling**: Existing chapters (same textbook_id and chapter_number) are skipped
3. **Error Handling**: If PDF processing fails for a chapter, it still creates the chapter entry
4. **OCR Support**: Automatically uses OCR for Indian languages if text extraction fails

## Troubleshooting

If the request hangs or times out:
1. Check if the textbook PDF exists and is accessible
2. Verify the page ranges are valid
3. Consider processing fewer chapters at once
4. Check server logs for processing errors
5. Use the `--max-time` flag to set a timeout