# AI Teaching Assistant Backend

A FastAPI-based backend for an AI-powered teaching assistant that processes textbooks, extracts chapters, and generates educational content using Azure OpenAI or OpenAI API.

## 🚀 Features

- 📚 **Textbook Management**: Upload and manage PDF textbooks
- 📖 **Chapter Detection**: AI-powered automatic detection of chapters from table of contents
- ✂️ **PDF Splitting**: Split textbooks into individual chapter PDFs
- 📝 **Text Extraction**: Extract text from specific page ranges
- 🤖 **AI Integration**: Azure OpenAI/OpenAI API for intelligent content generation
- 💾 **SQLite Database**: Lightweight, zero-configuration data storage
- 🔄 **RESTful API**: Clean, well-documented API endpoints
- ⚡ **Async Support**: High-performance asynchronous request handling

## 📋 Prerequisites

Before setting up this application, ensure you have:

- **Python 3.8 or higher** installed on your machine
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **Azure OpenAI API Key** or **OpenAI API Key**
- Minimum 500MB free disk space for PDFs and database

## 🛠️ Installation Guide

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd nithinproject2/backend

# Or if you have a zip file, extract it and navigate to the backend folder
unzip nithinproject2.zip
cd nithinproject2/backend
```

### Step 2: Set Up Python Virtual Environment

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
# On Windows: use notepad, VS Code, or any text editor
# On macOS/Linux: use nano, vim, or any text editor
nano .env
```

**Required Configuration in .env:**

```env
# Choose your AI provider (true for Azure, false for OpenAI)
USE_AZURE_OPENAI=true

# If using Azure OpenAI:
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# If using standard OpenAI (set USE_AZURE_OPENAI=false):
# OPENAI_API_KEY=your_openai_api_key_here

# Database (default SQLite - no changes needed)
DATABASE_URL=sqlite:///./teaching_assistant.db

# Upload settings (optional - defaults work fine)
MAX_UPLOAD_SIZE=52428800  # 50MB in bytes
UPLOAD_DIR=uploads
CHAPTERS_DIR=chapters

# API settings (optional - defaults work fine)
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 5: Create Required Directories

The application will create these automatically, but you can create them manually:

```bash
# Create directories for uploads and chapters
mkdir -p uploads chapters
```

### Step 6: Run the Application

**Development Mode (with auto-reload):**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

### Step 7: Verify Installation

Open your browser and navigate to:
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)

## 🧪 Testing the API

### Quick Test with curl

```bash
# Check if the API is running
curl http://localhost:8000/api/v1/textbooks

# Upload a textbook (replace textbook.pdf with your file)
curl -X POST "http://localhost:8000/api/v1/textbooks/upload" \
  -F "file=@textbook.pdf"
```

### Using the Test Scripts

```bash
# Test basic API functionality
python test_api.py

# Test Azure OpenAI connection
python test_azure_openai.py
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── textbooks.py  # Textbook CRUD operations
│   │   ├── chapters.py   # Chapter management
│   │   └── extraction.py # Text extraction utilities
│   ├── database/         # Database layer
│   │   ├── database.py   # Database connection setup
│   │   └── models.py     # SQLAlchemy ORM models
│   ├── models/           # Data models
│   │   └── schemas.py    # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── pdf_service.py # PDF processing
│   │   └── ai_service.py  # AI/LLM operations
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application
├── uploads/              # Uploaded PDF storage
├── chapters/             # Generated chapter PDFs
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your configuration (create this)
├── test_api.py          # API test script
├── test_azure_openai.py # Azure OpenAI test script
└── README.md            # This file
```

## 🔧 API Endpoints

### Textbook Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/textbooks/upload` | Upload a new PDF textbook |
| GET | `/api/v1/textbooks` | List all uploaded textbooks |
| GET | `/api/v1/textbooks/{textbook_id}` | Get textbook details |
| DELETE | `/api/v1/textbooks/{textbook_id}` | Delete a textbook |

### Chapter Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/textbooks/{textbook_id}/detect-chapters` | Detect chapters using AI |
| POST | `/api/v1/textbooks/{textbook_id}/split-chapters` | Split PDF into chapters |
| GET | `/api/v1/textbooks/{textbook_id}/chapters` | List all chapters |
| GET | `/api/v1/chapters/{chapter_id}/download` | Download chapter PDF |

### Text Extraction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extraction/extract-text` | Extract text from page range |
| POST | `/api/v1/extraction/extract-chapter` | Extract text from a chapter |

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Python Version Issues
**Problem:** `python: command not found` or wrong Python version
```bash
# Check Python version
python --version  # or python3 --version

# If Python 3.8+ is not installed:
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.8 python3-pip

# On macOS (using Homebrew):
brew install python@3.8

# On Windows:
# Download from https://www.python.org/downloads/
```

#### 2. Virtual Environment Activation Issues
**Problem:** Virtual environment not activating properly
```bash
# Try alternative activation methods:
# On Windows PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1

# On Windows Git Bash:
source venv/Scripts/activate

# On macOS/Linux with fish shell:
source venv/bin/activate.fish
```

#### 3. Package Installation Failures
**Problem:** `pip install` fails with errors
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# If still failing, install packages one by one:
pip install fastapi
pip install uvicorn[standard]
pip install PyMuPDF
# ... continue with other packages

# On Linux, you might need:
sudo apt-get install python3-dev
```

#### 4. Azure OpenAI Connection Issues
**Problem:** API key or endpoint errors
- Verify your API key is correct and active
- Check the endpoint format: `https://your-resource-name.openai.azure.com`
- Ensure your deployment name matches exactly
- Test connection with: `python test_azure_openai.py`

#### 5. Port Already in Use
**Problem:** `Address already in use` error
```bash
# Find process using port 8000
# On Linux/macOS:
lsof -i :8000
kill -9 <PID>

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port:
uvicorn app.main:app --port 8001
```

#### 6. Database Issues
**Problem:** SQLite database errors
```bash
# Remove existing database and let it recreate
rm teaching_assistant.db
# Run the application again - it will create a fresh database
```

#### 7. PDF Upload Issues
**Problem:** File upload fails or size limit errors
- Check file size is under 50MB (default limit)
- Ensure the file is a valid PDF
- Check upload directory permissions:
```bash
# On Linux/macOS:
chmod 755 uploads chapters

# On Windows (run as administrator):
icacls uploads /grant Everyone:F
icacls chapters /grant Everyone:F
```

## 🚢 Deployment Options

### Option 1: Deploy with Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads chapters

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-teaching-assistant .
docker run -p 8000:8000 --env-file .env ai-teaching-assistant
```

### Option 2: Deploy with PM2 (Process Manager)

```bash
# Install PM2 globally
npm install -g pm2

# Create ecosystem file
pm2 start app.main:app --interpreter python3 --name ai-teacher

# Save PM2 configuration
pm2 save
pm2 startup
```

### Option 3: Deploy as a System Service (Linux)

Create `/etc/systemd/system/ai-teacher.service`:
```ini
[Unit]
Description=AI Teaching Assistant API
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ai-teacher
sudo systemctl start ai-teacher
```

## 🧑‍💻 Development Tips

### Running in Debug Mode
```bash
# Set debug environment variable
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Run with debug logging
uvicorn app.main:app --reload --log-level debug
```

### Using Different Databases

While SQLite is the default, you can use PostgreSQL or MySQL:

**PostgreSQL:**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**MySQL:**
```bash
# Install MySQL driver
pip install pymysql

# Update .env
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
```

## 📊 Monitoring and Logs

### View Application Logs
```bash
# Run with custom log file
uvicorn app.main:app --log-config=log_config.yaml > app.log 2>&1

# Monitor logs in real-time
tail -f app.log
```

### Health Check Endpoint

Add this to your `app/main.py` for monitoring:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues, questions, or suggestions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check existing issues in the repository
4. Create a new issue with detailed information

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)

---

**Note:** This application requires an active Azure OpenAI or OpenAI API subscription. Ensure you have the necessary API keys and permissions before deployment.
python app/main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Workflow

### 1. Upload a Textbook

```bash
curl -X POST "http://localhost:8000/api/v1/textbooks/upload" \
  -F "file=@textbook.pdf" \
  -F "title=Mathematics Grade 10" \
  -F "author=John Doe"
```

### 2. Set Table of Contents Pages

```bash
curl -X POST "http://localhost:8000/api/v1/extract/textbook/1/set-toc" \
  -H "Content-Type: application/json" \
  -d '{"start_page": 3, "end_page": 5}'
```

### 3. Detect Chapters using AI

```bash
curl -X POST "http://localhost:8000/api/v1/chapters/detect" \
  -H "Content-Type: application/json" \
  -d '{"textbook_id": 1}'
```

### 4. Create Chapters with Page Ranges

```bash
curl -X POST "http://localhost:8000/api/v1/chapters/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_id": 1,
    "chapters": [
      {"chapter_number": 1, "title": "Introduction", "start_page": 10, "end_page": 25},
      {"chapter_number": 2, "title": "Algebra", "start_page": 26, "end_page": 50}
    ]
  }'
```

### 5. Generate Chapter Summary

```bash
curl -X POST "http://localhost:8000/api/v1/chapters/1/generate-summary"
```

## Key Endpoints

### Textbooks
- `POST /api/v1/textbooks/upload` - Upload a new textbook
- `GET /api/v1/textbooks/` - List all textbooks
- `GET /api/v1/textbooks/{id}` - Get textbook details
- `PATCH /api/v1/textbooks/{id}` - Update textbook info
- `DELETE /api/v1/textbooks/{id}` - Delete a textbook

### Chapters
- `POST /api/v1/chapters/detect` - Detect chapters from TOC
- `POST /api/v1/chapters/batch` - Create multiple chapters
- `GET /api/v1/chapters/textbook/{textbook_id}` - List chapters
- `GET /api/v1/chapters/{id}` - Get chapter details
- `POST /api/v1/chapters/{id}/generate-summary` - Generate AI summary
- `DELETE /api/v1/chapters/{id}` - Delete a chapter

### Text Extraction
- `POST /api/v1/extract/textbook/{id}/pages` - Extract text from pages
- `GET /api/v1/extract/textbook/{id}/toc` - Get TOC text
- `POST /api/v1/extract/textbook/{id}/set-toc` - Set and extract TOC

## Database Schema

The application uses SQLite with the following main tables:

- **textbooks**: Stores textbook metadata and file paths
- **chapters**: Individual chapters with text and PDFs
- **worksheets**: Generated worksheets (future feature)
- **lesson_plans**: Generated lesson plans (future feature)

## Error Handling

The API uses standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

Error responses include detailed messages:
```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 400
}
```

## Development Tips

1. **Check logs**: The application provides detailed logging
2. **Use Swagger UI**: Test endpoints directly from the documentation
3. **Database viewer**: Use SQLite browser to inspect the database
4. **Test PDFs**: Start with small PDFs for faster testing

## Future Enhancements

- [ ] Worksheet generation from chapters
- [ ] Lesson plan creation
- [ ] Quiz generation
- [ ] Multi-user support with authentication
- [ ] Cloud storage integration
- [ ] Batch processing for large textbooks
- [ ] Export to various formats (DOCX, Markdown)
- [ ] Advanced AI prompting customization

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your API key is set correctly in `.env`
2. **PDF Processing Error**: Check if the PDF is not corrupted
3. **Database Lock**: Ensure only one instance is running
4. **Memory Issues**: For large PDFs, consider increasing system memory

## License

This project is for educational purposes.

## Support

For issues or questions, please create an issue in the repository.