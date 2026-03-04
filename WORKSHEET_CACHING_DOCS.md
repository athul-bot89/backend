# Worksheet Caching Documentation

## Overview

The worksheet generation system now includes intelligent caching to improve performance. Generated worksheets are stored in the database and served from cache on subsequent requests, unless explicitly regenerated.

## Features

### 1. **Automatic Caching**
- First worksheet generation for a chapter is automatically stored in the database
- Subsequent requests return the cached version instantly (typically < 0.01s vs 10-20s for generation)
- One worksheet is stored per chapter

### 2. **Force Regeneration**
- Add `?regenerate=true` query parameter to force new generation
- New worksheet replaces the cached version in database

### 3. **Manual Cache Clearing**
- DELETE endpoint available to remove cached worksheet
- Next request will generate and cache a new worksheet

## API Endpoints

### Generate/Retrieve Worksheet

```http
POST /api/v1/chapters/{chapter_id}/generate-worksheet
```

**Query Parameters:**
- `regenerate` (boolean, optional): Force regeneration even if cached version exists
- `num_questions` (integer, optional): Number of questions to generate (1-20, default: 10)

**Behavior:**
1. If `regenerate=false` (default) and worksheet exists in DB → Return cached version
2. If `regenerate=true` or no worksheet in DB → Generate new worksheet and store in DB

**Example - First Generation:**
```bash
curl -X POST http://localhost:8000/api/v1/chapters/41/generate-worksheet
# Takes 10-20 seconds, generates and stores worksheet
```

**Example - Cached Retrieval:**
```bash
curl -X POST http://localhost:8000/api/v1/chapters/41/generate-worksheet
# Returns instantly from cache (<0.01s)
```

**Example - Force Regeneration:**
```bash
curl -X POST http://localhost:8000/api/v1/chapters/41/generate-worksheet?regenerate=true
# Generates new worksheet and updates cache
```

### Delete Cached Worksheet

```http
DELETE /api/v1/chapters/{chapter_id}/worksheet
```

Removes the cached worksheet for a chapter, forcing regeneration on next request.

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/chapters/41/worksheet
# Response: {"message": "Worksheet for chapter 'Chapter Title' has been deleted"}
```

## Database Schema

Worksheets are stored in the `worksheets` table:

```sql
CREATE TABLE worksheets (
    id INTEGER PRIMARY KEY,
    chapter_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    difficulty_level VARCHAR(50),
    content TEXT NOT NULL,  -- JSON string of questions
    answer_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);
```

## Storage Format

The worksheet content is stored as a JSON string in the `content` field. Each question includes:
- `question`: The question text
- `question_type`: Type of question (multiple_choice, true_false, short_answer, essay)
- `options`: Array of options (for multiple choice questions)
- `correct_answer`: The correct answer
- `difficulty`: Difficulty level (easy, medium, hard)

## Performance Benefits

### Without Caching:
- Every request triggers AI generation: ~10-20 seconds
- High computational cost
- Potential rate limiting issues with AI service

### With Caching:
- First request: ~10-20 seconds (generation + storage)
- Subsequent requests: <0.01 seconds (database retrieval)
- Significant reduction in AI API calls
- Better user experience

## Implementation Details

### Cache Logic Flow:
1. Request received at `/chapters/{id}/generate-worksheet`
2. Check `regenerate` query parameter
3. If `regenerate=false`:
   - Query database for existing worksheet
   - If found, parse JSON and return immediately
   - If not found or corrupted, proceed to generation
4. If `regenerate=true` or no cached worksheet:
   - Call AI service to generate questions
   - Store/update in database
   - Return generated worksheet

### Database Operations:
- `get_worksheet_by_chapter_id()`: Retrieve cached worksheet
- `create_worksheet()`: Store new worksheet
- `update_worksheet()`: Update existing worksheet (on regeneration)
- `delete_worksheet_by_chapter_id()`: Remove cached worksheet

## Testing

Run the provided test scripts to verify functionality:

```bash
# Python test with detailed output
python test_worksheet_caching.py

# Bash script for quick testing
./test_worksheet_cache.sh
```

## Notes

- **Storage Policy**: One worksheet per chapter (not per difficulty level)
- **Update Policy**: Chapter content updates do NOT automatically invalidate cached worksheets
- **Regeneration**: Must be explicitly requested via `regenerate=true` parameter
- **Response Format**: No indication whether response came from cache (transparent to client)