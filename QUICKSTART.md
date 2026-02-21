# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies

```bash
# Make sure you're in the backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your key from: https://platform.openai.com/api-keys
```

### 3. Start the Server

```bash
# Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or simply:
python -m uvicorn app.main:app --reload
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000/api/v1

## 📋 API Workflow

### Step 1: Upload a Textbook

Using cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/textbooks/upload" \
  -F "file=@your_textbook.pdf" \
  -F "title=Your Textbook Title" \
  -F "author=Author Name"
```

Using Python:
```python
import requests

with open("textbook.pdf", "rb") as f:
    files = {"file": f}
    data = {"title": "Mathematics Grade 10", "author": "John Doe"}
    response = requests.post(
        "http://localhost:8000/api/v1/textbooks/upload",
        files=files,
        data=data
    )
print(response.json())
```

### Step 2: Set Table of Contents Pages

```python
# Assuming textbook_id = 1 and TOC is on pages 3-5
response = requests.post(
    "http://localhost:8000/api/v1/extract/textbook/1/set-toc",
    json={"start_page": 3, "end_page": 5}
)
```

### Step 3: Detect Chapters with AI

```python
response = requests.post(
    "http://localhost:8000/api/v1/chapters/detect",
    json={"textbook_id": 1}
)
detected_chapters = response.json()
```

### Step 4: Create Chapters

```python
chapters_data = {
    "textbook_id": 1,
    "chapters": [
        {"chapter_number": 1, "title": "Introduction", "start_page": 10, "end_page": 25},
        {"chapter_number": 2, "title": "Algebra", "start_page": 26, "end_page": 50}
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/chapters/batch",
    json=chapters_data
)
```

### Step 5: Generate Summary

```python
# Generate summary for chapter 1
response = requests.post(
    "http://localhost:8000/api/v1/chapters/1/generate-summary"
)
summary = response.json()
```

## 🧪 Test the API

Run the test script:
```bash
python test_api.py
```

Run the example workflow:
```bash
python example_workflow.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── database/      # Database models
│   ├── models/        # Request/response schemas
│   ├── services/      # Business logic
│   ├── config.py      # Configuration
│   └── main.py        # Application entry
├── uploads/           # Uploaded PDFs
├── chapters/          # Split chapter PDFs
├── .env              # Environment variables
└── requirements.txt   # Dependencies
```

## 🔧 Troubleshooting

### OpenAI API Key Error
- Make sure your API key is set in `.env`
- Verify the key is valid at https://platform.openai.com/api-keys

### Module Import Errors
- Ensure virtual environment is activated
- Run from the backend directory
- Use `python -m uvicorn app.main:app` instead of direct execution

### Database Issues
- Delete `teaching_assistant.db` to reset the database
- The database is automatically created on first run

### PDF Processing Errors
- Ensure the PDF is not corrupted
- Check file size is under 50MB
- Verify PyMuPDF is installed correctly

## 📚 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Customize AI prompts**: Edit `app/services/ai_service.py`
3. **Add authentication**: Implement JWT tokens for security
4. **Deploy to production**: Use Docker and a cloud provider
5. **Build a frontend**: Create a React/Vue/Angular app

## 🆘 Need Help?

- Check the full README.md for detailed documentation
- Review the API docs at http://localhost:8000/docs
- Examine the example scripts: `test_api.py` and `example_workflow.py`