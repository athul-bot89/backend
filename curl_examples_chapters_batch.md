# Curl Examples for /chapters/batch Endpoint

## Basic Example - Create Multiple Chapters

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

## Example with Auto-fixing End Pages

When `end_page` is set to 0, the API will auto-fix it:
- For chapters in the middle: Uses next chapter's start_page - 1
- For the last chapter: Uses textbook's total_pages or start_page + 20

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "Chapter 1: Getting Started",
        "chapter_number": 1,
        "start_page": 5,
        "end_page": 0
      },
      {
        "title": "Chapter 2: Core Concepts",
        "chapter_number": 2,
        "start_page": 30,
        "end_page": 0
      },
      {
        "title": "Chapter 3: Advanced Topics",
        "chapter_number": 3,
        "start_page": 65,
        "end_page": 0
      }
    ]
  }'
```

## Large Batch Example - Complete Textbook

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 7,
    "chapters": [
      {
        "title": "प्रस्तावना (Introduction)",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 15
      },
      {
        "title": "गणित के मूल सिद्धांत (Basic Principles)",
        "chapter_number": 2,
        "start_page": 16,
        "end_page": 35
      },
      {
        "title": "அடிப்படை கணிதம் (Basic Mathematics)",
        "chapter_number": 3,
        "start_page": 36,
        "end_page": 55
      },
      {
        "title": "ಬೀಜಗಣಿತ (Algebra)",
        "chapter_number": 4,
        "start_page": 56,
        "end_page": 80
      },
      {
        "title": "ज्यामिति (Geometry)",
        "chapter_number": 5,
        "start_page": 81,
        "end_page": 105
      },
      {
        "title": "त्रिकोणमिति (Trigonometry)",
        "chapter_number": 6,
        "start_page": 106,
        "end_page": 130
      },
      {
        "title": "സ്ഥിതിവിവരക്കണക്ക് (Statistics)",
        "chapter_number": 7,
        "start_page": 131,
        "end_page": 155
      },
      {
        "title": "కాలిక్యులస్ (Calculus)",
        "chapter_number": 8,
        "start_page": 156,
        "end_page": 180
      },
      {
        "title": "সম্ভাব্যতা (Probability)",
        "chapter_number": 9,
        "start_page": 181,
        "end_page": 200
      },
      {
        "title": "Review and Practice Problems",
        "chapter_number": 10,
        "start_page": 201,
        "end_page": 220
      }
    ]
  }'
```

## With Pretty Output (using jq or python)

```bash
# Using Python's json.tool for pretty printing
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
      }
    ]
  }' | python3 -m json.tool

# Using jq for pretty printing (if installed)
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
      }
    ]
  }' | jq '.'
```

## Store Response in a File

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
  }' -o batch_response.json
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
        "title": "Test Chapter",
        "chapter_number": 1,
        "start_page": 1,
        "end_page": 10
      }
    ]
  }'
```

## Using a JSON File as Input

First, create a JSON file with the request data:

```json
// chapters_batch.json
{
  "textbook_id": 7,
  "chapters": [
    {
      "title": "Chapter 1: Introduction",
      "chapter_number": 1,
      "start_page": 1,
      "end_page": 30
    },
    {
      "title": "Chapter 2: Basics",
      "chapter_number": 2,
      "start_page": 31,
      "end_page": 60
    }
  ]
}
```

Then use it with curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d @chapters_batch.json
```

## Notes

1. The endpoint will:
   - Skip chapters that already exist (based on textbook_id and chapter_number)
   - Auto-fix end_page when set to 0
   - Split PDFs for each chapter
   - Extract text with Indian language OCR support
   - Handle errors gracefully (continues processing even if one chapter fails)

2. Response includes:
   - `created_count`: Number of chapters successfully created
   - `chapters`: Array of created chapter objects with their IDs and details

3. The text extraction uses OCR with support for:
   - English (eng)
   - Hindi (hin)
   - Tamil (tam)
   - Telugu (tel)
   - Kannada (kan)
   - Malayalam (mal)
   - Marathi (mar)
   - Gujarati (guj)
   - Bengali (ben)
   - Punjabi (pan)
   - Odia (ori)