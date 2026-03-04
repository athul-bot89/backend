# Docker Commands Guide for FastAPI Teaching Assistant App

This guide provides simple commands to build, run, save, and deploy your FastAPI application with embedded SQLite database and configuration.

## 🚀 Quick Start

### 1. Build the Docker Image
```bash
docker build -t teaching-assistant-api .
```

### 2. Run the Container
```bash
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api
```

That's it! Your app is now running at http://localhost:8000

## 📦 Complete Command Reference

### Building the Image

**Basic build:**
```bash
docker build -t teaching-assistant-api .
```

**Build with specific tag/version:**
```bash
docker build -t teaching-assistant-api:v1.0 .
```

### Running the Container

**Run in detached mode (background):**
```bash
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api
```

**Run in foreground (see logs):**
```bash
docker run -p 8000:8000 --name teaching-app teaching-assistant-api
```

**Run with custom port mapping (e.g., port 3000):**
```bash
docker run -d -p 3000:8000 --name teaching-app teaching-assistant-api
```

### Container Management

**View running containers:**
```bash
docker ps
```

**View logs:**
```bash
docker logs teaching-app
```

**Follow logs in real-time:**
```bash
docker logs -f teaching-app
```

**Stop the container:**
```bash
docker stop teaching-app
```

**Start a stopped container:**
```bash
docker start teaching-app
```

**Remove the container:**
```bash
docker rm teaching-app
```

**Remove container forcefully:**
```bash
docker rm -f teaching-app
```

## 💾 Save and Export for Distribution

### Save as TAR.GZ File

**Step 1: Save the image to a tar file:**
```bash
docker save teaching-assistant-api:latest -o teaching-assistant-api.tar
```

**Step 2: Compress to tar.gz:**
```bash
gzip teaching-assistant-api.tar
```

**Or do both in one command:**
```bash
docker save teaching-assistant-api:latest | gzip > teaching-assistant-api.tar.gz
```

The resulting `teaching-assistant-api.tar.gz` file can be shared and deployed on any machine with Docker.

## 🖥️ Deploy on Another Machine

### Load and Run on New Machine

**Step 1: Copy the tar.gz file to the new machine**

**Step 2: Load the image:**
```bash
docker load < teaching-assistant-api.tar.gz
```

**Or if you have the uncompressed tar:**
```bash
docker load -i teaching-assistant-api.tar
```

**Step 3: Run the container (no configuration needed!):**
```bash
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api
```

That's all! No environment setup, no configuration files, no dependencies to install.

## 🔍 Verify the Deployment

**Check if container is running:**
```bash
docker ps | grep teaching-app
```

**Test the health endpoint:**
```bash
curl http://localhost:8000/health
```

**Access the API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Image Information

**Check image size:**
```bash
docker images teaching-assistant-api
```

**Inspect image details:**
```bash
docker inspect teaching-assistant-api
```

## 🛠️ Troubleshooting

**If port 8000 is already in use:**
```bash
# Use a different port
docker run -d -p 8080:8000 --name teaching-app teaching-assistant-api
```

**If container name already exists:**
```bash
# Remove old container first
docker rm -f teaching-app
# Then run new one
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api
```

**View detailed logs:**
```bash
docker logs --details teaching-app
```

**Execute commands inside running container:**
```bash
# Open a shell inside the container
docker exec -it teaching-app /bin/bash

# Check Python version
docker exec teaching-app python --version

# List files
docker exec teaching-app ls -la
```

## 🎯 One-Liner Deployment

**Complete deployment on a new machine:**
```bash
# Load image and run in one line (after copying tar.gz file)
docker load < teaching-assistant-api.tar.gz && docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api
```

## 📝 Notes

- The container includes everything: FastAPI app, SQLite database, uploaded PDFs, and all configuration
- No external .env file or volume mounting needed
- The database and uploads are preserved inside the container
- API keys and configuration are embedded in the image
- The app runs with auto-reload enabled for development convenience
- Default access at http://localhost:8000

## 🔐 Security Note

Since this image contains API keys and sensitive configuration, only share it with trusted parties. For production use, consider using Docker secrets or environment variable injection instead of embedding credentials.