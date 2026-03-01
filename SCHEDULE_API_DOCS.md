# Study Schedule API Documentation

The Study Schedule API provides endpoints for creating and managing study schedules for textbook chapters. It helps students organize their learning by creating optimized study plans with target completion dates.

## Endpoints

### 1. Create Custom Study Schedule

**POST** `/api/v1/schedule/create`

Creates a custom study schedule for a list of chapters with specific target completion dates.

#### Request Body

```json
{
  "textbook_id": 1,  // Optional: Link to existing textbook
  "chapters": [
    {
      "chapter_name": "Introduction to Python",
      "chapter_id": null,  // Optional: Link to existing chapter
      "target_completion_date": "2024-12-31T00:00:00",
      "estimated_hours": 10.5,  // Optional: Estimated study hours
      "priority": "high"  // Options: "low", "medium", "high"
    }
  ],
  "start_date": "2024-12-01T00:00:00",  // Optional: Defaults to today
  "study_hours_per_day": 2.5,  // Default: 2.0
  "include_weekends": false,  // Default: true
  "break_days": [  // Optional: List of dates to skip
    "2024-12-25T00:00:00",
    "2024-12-26T00:00:00"
  ]
}
```

#### Response

```json
{
  "textbook_id": 1,
  "total_chapters": 5,
  "start_date": "2024-12-01T00:00:00",
  "end_date": "2024-12-31T00:00:00",
  "total_study_days": 20,
  "schedule": [
    {
      "chapter_name": "Introduction to Python",
      "chapter_id": null,
      "target_completion_date": "2024-12-07T00:00:00",
      "suggested_start_date": "2024-12-01T00:00:00",
      "estimated_study_days": 4,
      "daily_hours": 2.5,
      "priority": "high",
      "study_tips": [
        "Focus on understanding basic syntax",
        "Practice with simple examples",
        "Take notes on key concepts"
      ]
    }
  ],
  "weekly_breakdown": {
    "Week 49 (Dec 01)": ["Introduction to Python", "Data Types"],
    "Week 50 (Dec 08)": ["Control Flow", "Functions"]
  },
  "conflicts": [
    "⚠️ 'Advanced Topics' cannot be completed by target date"
  ],
  "recommendations": [
    "📚 Many high-priority chapters detected. Consider increasing daily study hours.",
    "🗓️ Weekends excluded from schedule. Consider using them for review sessions."
  ],
  "created_at": "2024-11-26T10:00:00"
}
```

### 2. Optimize Schedule for Existing Textbook

**POST** `/api/v1/schedule/optimize/{textbook_id}`

Automatically creates an optimized study schedule for all chapters in an existing textbook.

#### Path Parameters
- `textbook_id` (integer): The ID of the textbook to create a schedule for

#### Query Parameters
- `target_completion_date` (datetime): Target date to complete all chapters
- `study_hours_per_day` (float): Available study hours per day (default: 2.0)
- `include_weekends` (boolean): Whether to include weekends (default: true)

#### Example Request
```
POST /api/v1/schedule/optimize/1?target_completion_date=2024-12-31T00:00:00&study_hours_per_day=3.0&include_weekends=true
```

#### Response
Same structure as the create endpoint response, but automatically includes all chapters from the specified textbook.

## Features

### 1. Smart Scheduling Algorithm
- Sorts chapters by target completion date and priority
- Calculates optimal study days based on estimated hours
- Avoids scheduling on break days and optionally weekends
- Detects and reports scheduling conflicts

### 2. Priority Levels
- **High Priority**: Scheduled first, may include AI-generated study tips
- **Medium Priority**: Standard scheduling
- **Low Priority**: Scheduled with flexibility

### 3. Weekly Breakdown
Provides a week-by-week view of which chapters to study, making it easy to track progress.

### 4. Conflict Detection
Automatically detects and reports:
- Chapters that cannot be completed by target date
- Overlapping high-priority chapters
- Schedule feasibility issues

### 5. AI-Powered Features
- Study tips for high-priority chapters
- Personalized recommendations based on schedule analysis
- Intelligent time estimation based on chapter content

## Use Cases

### 1. Student Planning for Exams
Create a study schedule leading up to an exam date, ensuring all chapters are covered.

```python
import requests
from datetime import datetime, timedelta

# Exam is in 30 days
exam_date = datetime.now() + timedelta(days=30)

schedule_data = {
    "chapters": [
        {"chapter_name": "Chapter 1", "target_completion_date": exam_date - timedelta(days=5)},
        {"chapter_name": "Chapter 2", "target_completion_date": exam_date - timedelta(days=3)},
        {"chapter_name": "Review", "target_completion_date": exam_date - timedelta(days=1)}
    ],
    "study_hours_per_day": 3.0,
    "include_weekends": True
}

response = requests.post("http://localhost:8000/api/v1/schedule/create", json=schedule_data)
```

### 2. Course Planning
Teachers can create recommended study schedules for their courses.

### 3. Self-Paced Learning
Learners can create flexible schedules for self-study, adjusting based on their available time.

## Integration with Other Endpoints

The schedule API integrates with:
- **Textbooks API**: Link schedules to existing textbooks
- **Chapters API**: Reference existing chapters in schedules
- **AI Service**: Generate study tips and recommendations

## Error Handling

Common error responses:

### 404 Not Found
```json
{
  "detail": "Textbook with ID 123 not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to create study schedule: [error details]"
}
```

## Best Practices

1. **Set Realistic Study Hours**: Don't overestimate daily study capacity
2. **Include Buffer Days**: Add break days for review and rest
3. **Prioritize Foundational Chapters**: Mark early chapters as high priority
4. **Use Existing Data**: Link to existing textbook/chapter IDs when available
5. **Review Conflicts**: Check and address any scheduling conflicts
6. **Follow Recommendations**: Consider AI-generated recommendations for better outcomes