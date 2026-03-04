# Use Python 3.11 slim image for smaller size and better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed for PDF processing
# PyMuPDF doesn't require additional system packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application including .env file
COPY . .

# Ensure the .env file is present and loaded
# The app uses python-dotenv which will automatically load this
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create necessary directories if they don't exist
RUN mkdir -p uploads chapters

# Ensure the database file has proper permissions
RUN if [ -f teaching_assistant.db ]; then chmod 644 teaching_assistant.db; fi

# Expose the port
EXPOSE 8000

# Run the FastAPI application with uvicorn
# Using --reload for development convenience as requested
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]