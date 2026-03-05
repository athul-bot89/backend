# AI Teaching Assistant Backend

A powerful FastAPI-based backend for an AI-powered teaching assistant that processes PDF textbooks, automatically detects chapters, and generates educational content using Azure OpenAI or OpenAI API.

## 🌟 Key Features

- 📚 **PDF Textbook Management**: Upload, store, and manage PDF textbooks
- 🤖 **AI-Powered Chapter Detection**: Automatically detect and extract chapters from table of contents
- ✂️ **Smart PDF Splitting**: Split large textbooks into individual chapter PDFs
- 📝 **Text & Vision Extraction**: Extract text and process images from PDFs
- 🧠 **Dual AI Integration**: Support for both Azure OpenAI and OpenAI APIs
- 💾 **SQLite Database**: Zero-configuration, lightweight data storage
- 🔄 **RESTful API**: Well-documented endpoints with Swagger/OpenAPI support
- ⚡ **Async Processing**: High-performance asynchronous request handling
- 📅 **Study Schedule Generation**: Create personalized study plans from chapters

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher (3.10+ recommended)
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 1GB free space for application and PDFs
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 20.04+, or any modern Linux

### API Requirements
- Either **Azure OpenAI API Key** or **OpenAI API Key**
- Internet connection for AI API calls

## 🖥️ Operating System Specific Installation

### 🪟 Windows Installation

#### Step 1: Install Python (if not already installed)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **CHECK "Add Python to PATH"**
3. Verify installation:
```powershell
python --version
pip --version
```

If commands not found, restart your computer or manually add Python to PATH.

#### Step 2: Download and Extract Project

```powershell
# Option 1: Using Git (if installed)
git clone <repository-url>
cd nithinproject2\backend

# Option 2: Manual download
# Download ZIP from repository
# Extract to desired location using Windows Explorer
# Open PowerShell/Command Prompt in the backend folder
```

#### Step 3: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Command Prompt:
venv\Scripts\activate.bat

# For PowerShell (may require execution policy change):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# For Git Bash:
source venv/Scripts/activate
```

#### Step 4: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# If you encounter SSL errors:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

#### Step 5: Configure Environment

```powershell
# Create .env file from example
copy .env.example .env

# Edit with Notepad
notepad .env

# Or use any text editor (VS Code, Notepad++, etc.)
```

#### Step 6: Run Application

```powershell
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 🍎 macOS Installation

#### Step 1: Install Prerequisites

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

#### Step 2: Download Project

```bash
# Using Git
git clone <repository-url>
cd backend

# Or download and extract ZIP manually
```

#### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install packages
pip install -r requirements.txt

# For M1/M2 Macs, if you encounter issues:
pip install --no-cache-dir -r requirements.txt
```

#### Step 5: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env
# Or use: open -e .env (TextEdit)
# Or use: code .env (VS Code)
```

#### Step 6: Run Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 🐧 Linux Installation (Ubuntu/Debian)

#### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and required system packages
sudo apt install python3.10 python3.10-venv python3-pip git build-essential

# For PDF processing dependencies
sudo apt install libmupdf-dev mupdf-tools

# Verify installation
python3 --version
pip3 --version
```

#### Step 2: Download Project

```bash
# Using Git
git clone <repository-url>
cd nithinproject2/backend

# Or using wget
wget https://github.com/username/repo/archive/main.zip
unzip main.zip
cd nithinproject2/backend
```

#### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install packages
pip install -r requirements.txt
```

#### Step 5: Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit with your preferred editor
nano .env
# Or: vim .env
# Or: code .env (VS Code)
```

#### Step 6: Run Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode with systemd service (recommended)
# See "Production Deployment" section below
```

### 🐧 Linux Installation (RHEL/CentOS/Fedora)

```bash
# Install dependencies
sudo dnf install python3.10 python3-pip git gcc

# Follow same steps as Ubuntu from Step 2 onwards
```

### 🐧 Linux Installation (Arch/Manjaro)

```bash
# Install dependencies
sudo pacman -S python python-pip git base-devel

# Follow same steps as Ubuntu from Step 2 onwards
```

## ⚙️ Configuration

### Environment Variables (.env file)

Create a `.env` file in the backend directory with the following configuration:

```env
# ============================================
# AI PROVIDER CONFIGURATION
# ============================================

# Choose AI Provider: "azure" or "openai"
USE_AZURE_OPENAI=false

# --------------------------------------------
# Azure OpenAI Configuration (if USE_AZURE_OPENAI=true)
# --------------------------------------------
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# --------------------------------------------
# Standard OpenAI Configuration (if USE_AZURE_OPENAI=false)
# --------------------------------------------
OPENAI_API_KEY=your-openai-api-key
# Optional: Specify model (default: gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# ============================================
# DATABASE CONFIGURATION
# ============================================
DATABASE_URL=sqlite:///./teaching_assistant.db

# ============================================
# FILE STORAGE CONFIGURATION
# ============================================
UPLOAD_DIR=uploads
CHAPTERS_DIR=chapters
MAX_UPLOAD_SIZE=52428800  # 50MB in bytes

# ============================================
# API SERVER CONFIGURATION
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4  # For production only

# ============================================
# SECURITY & CORS (Production)
# ============================================
# CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
# SECRET_KEY=your-secret-key-here
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚀 Running the Application

### Development Mode

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Single worker (simple)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Multiple workers (better performance)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (recommended for production)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment (All Platforms)

```dockerfile
# Create a Dockerfile in the backend directory
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run with Docker
docker build -t teaching-assistant-backend .
docker run -p 8000:8000 --env-file .env teaching-assistant-backend
```

## 🧪 Verification & Testing

### 1. Check API is Running

Open browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 2. Test with cURL

```bash
# Health check
curl http://localhost:8000/health

# List textbooks
curl http://localhost:8000/api/v1/textbooks

# Upload a textbook
curl -X POST "http://localhost:8000/api/v1/textbooks/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/textbook.pdf"
```

### 3. Test with Python

```python
import requests

# Test API
response = requests.get("http://localhost:8000/api/v1/textbooks")
print(response.json())

# Upload file
with open("textbook.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/v1/textbooks/upload", files=files)
    print(response.json())
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

## � Common Troubleshooting

### Platform-Specific Issues

#### Windows Issues

**PowerShell Execution Policy:**
```powershell
# If you get "cannot be loaded because running scripts is disabled"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Long Path Support:**
```powershell
# Enable long path support (run as Administrator)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

**Visual C++ Build Tools:**
If you get "Microsoft Visual C++ 14.0 is required":
- Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

#### macOS Issues

**M1/M2 Silicon Issues:**
```bash
# For ARM64 compatibility issues
pip install --no-binary :all: --no-cache-dir PyMuPDF
```

**SSL Certificate Issues:**
```bash
# Install certificates
pip install --upgrade certifi
```

#### Linux Issues

**Permission Denied Errors:**
```bash
# Fix permissions for directories
sudo chown -R $USER:$USER .
chmod -R 755 uploads chapters
```

**Missing System Libraries:**
```bash
# Ubuntu/Debian
sudo apt-get install libmupdf-dev python3-dev build-essential

# Fedora/RHEL
sudo dnf install mupdf-devel python3-devel gcc

# Arch Linux
sudo pacman -S mupdf python gcc
```

### Connection & API Issues

**OpenAI API Errors:**
- Verify API key is valid and has credits
- Check rate limits aren't exceeded
- Ensure network can reach api.openai.com

**Azure OpenAI Errors:**
- Verify resource exists and is not deleted
- Check deployment name matches exactly
- Ensure API version is supported
- Verify region availability

**CORS Issues (Frontend Connection):**
```python
# Update app/main.py to allow your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "your-frontend-url"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐳 Docker Deployment (Detailed)

### Create Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads chapters

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./chapters:/app/chapters
      - ./teaching_assistant.db:/app/teaching_assistant.db
    env_file:
      - .env
    restart: unless-stopped
```

### Build and Run with Docker

```bash
# Build Docker image
docker build -t ai-teaching-assistant .

# Run with Docker
docker run -d \
  --name teaching-assistant \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/chapters:/app/chapters \
  ai-teaching-assistant

# Or with Docker Compose
docker-compose up -d

# View logs
docker logs -f teaching-assistant

# Stop container
docker stop teaching-assistant

# Remove container
docker rm teaching-assistant
```

## 🔐 Security Best Practices

### Environment Variables
- **Never commit `.env` file to version control**
- Use strong, unique API keys
- Rotate API keys regularly
- Use environment-specific configurations

### File Uploads
- Validate file types (PDF only)
- Implement virus scanning for production
- Set appropriate file size limits
- Use secure file storage locations

### API Security
- Enable CORS only for trusted domains
- Implement rate limiting for production
- Use HTTPS in production
- Add authentication for sensitive endpoints

### Database Security
- Use PostgreSQL or MySQL for production
- Regular database backups
- Encrypt sensitive data
- Use connection pooling

## 🚀 Production Deployment

### Linux Systemd Service

Create `/etc/systemd/system/teaching-assistant.service`:

```ini
[Unit]
Description=AI Teaching Assistant Backend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/teaching-assistant/backend
Environment="PATH=/opt/teaching-assistant/backend/venv/bin"
ExecStart=/opt/teaching-assistant/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable teaching-assistant
sudo systemctl start teaching-assistant
sudo systemctl status teaching-assistant
```

### Nginx Reverse Proxy

Install and configure Nginx:

```nginx
# /etc/nginx/sites-available/teaching-assistant
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/teaching-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## 📊 Performance Optimization

### Database Optimization
```python
# Add database indexes (in models.py)
class Textbook(Base):
    __tablename__ = "textbooks"
    __table_args__ = (
        Index('idx_textbook_created', 'created_at'),
    )
```

### Caching
```python
# Add Redis caching for frequently accessed data
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@lru_cache(maxsize=128)
def get_cached_chapters(textbook_id: int):
    # Implementation
    pass
```

### Async Processing
```python
# Use background tasks for heavy operations
from fastapi import BackgroundTasks

@router.post("/process-heavy-task")
async def process_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(heavy_processing_function)
    return {"message": "Processing started"}
```

## 📚 API Usage Examples

### JavaScript/TypeScript
```javascript
// Upload textbook
const uploadTextbook = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/v1/textbooks/upload', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};

// Detect chapters
const detectChapters = async (textbookId) => {
  const response = await fetch(`http://localhost:8000/api/v1/textbooks/${textbookId}/detect-chapters`, {
    method: 'POST'
  });
  
  return await response.json();
};
```

### Python Client
```python
import httpx
import asyncio

class TeachingAssistantClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def upload_textbook(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await self.client.post(
                f"{self.base_url}/api/v1/textbooks/upload",
                files=files
            )
        return response.json()
    
    async def get_textbooks(self):
        response = await self.client.get(f"{self.base_url}/api/v1/textbooks")
        return response.json()

# Usage
async def main():
    client = TeachingAssistantClient()
    result = await client.upload_textbook("textbook.pdf")
    print(result)

asyncio.run(main())
```

## 📝 Environment Templates

### .env.example (Create this file)
```env
# AI Configuration
USE_AZURE_OPENAI=false
OPENAI_API_KEY=your-key-here

# Azure OpenAI (if using)
# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_ENDPOINT=
# AZURE_OPENAI_DEPLOYMENT=
# AZURE_OPENAI_API_VERSION=

# Database
DATABASE_URL=sqlite:///./teaching_assistant.db

# File Storage
UPLOAD_DIR=uploads
CHAPTERS_DIR=chapters
MAX_UPLOAD_SIZE=52428800

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation at `/docs`

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

---

**Made with ❤️ by the AI Teaching Assistant Team**
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