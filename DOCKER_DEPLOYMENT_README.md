# 🐳 Docker Deployment Guide - Teaching Assistant API

## 📋 What's Included

This Docker image contains:
- ✅ Complete FastAPI application
- ✅ SQLite database with all data
- ✅ Environment variables and API keys
- ✅ Uploaded PDF files
- ✅ Chapter extractions
- ✅ All Python dependencies

**No external configuration needed!**

## 🚀 Quick Start (3 Commands)

```bash
# 1. Build the image
docker build -t teaching-assistant-api .

# 2. Run the container
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api

# 3. Access the API
curl http://localhost:8000/health
```

Your API is now running at: **http://localhost:8000**

## 📦 Distribution Instructions

### To Package for Distribution:

```bash
# Save as compressed tar.gz file (1.1GB)
docker save teaching-assistant-api:latest | gzip > teaching-assistant-api.tar.gz
```

### To Deploy on ANY Machine:

1. **Copy the tar.gz file to the new machine**

2. **Load and run (2 commands only):**
```bash
# Load the image
docker load < teaching-assistant-api.tar.gz

# Run it
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api:latest
```

That's it! No pip install, no environment setup, no configuration files needed.

## 🔧 Useful Commands

### Container Management
```bash
# View logs
docker logs teaching-app

# Follow logs in real-time
docker logs -f teaching-app

# Stop container
docker stop teaching-app

# Start again
docker start teaching-app

# Remove container
docker rm -f teaching-app

# Check status
docker ps | grep teaching-app
```

### Different Port
```bash
# Run on port 3000 instead of 8000
docker run -d -p 3000:8000 --name teaching-app teaching-assistant-api
```

## 🌐 API Endpoints

Once running, access:
- **API Base**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 File Structure in Container

```
/app/
├── app/             # FastAPI application
├── uploads/         # Uploaded PDFs
├── chapters/        # Extracted chapters
├── teaching_assistant.db  # SQLite database
├── .env            # Environment variables (embedded)
└── requirements.txt # Python dependencies
```

## 🔐 Security Notes

⚠️ **This image contains embedded API keys and credentials**
- Only share with trusted parties
- Not recommended for public distribution
- For production, use environment variable injection

## 🏭 Production Deployment

For production with better performance:
```bash
# Use the production Dockerfile (without --reload)
docker build -f Dockerfile.production -t teaching-assistant-api:prod .
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api:prod
```

## 🛠️ Automated Scripts

### Use the Quick Start Script:
```bash
# Interactive menu
./docker-quickstart.sh

# Or direct commands
./docker-quickstart.sh build    # Build only
./docker-quickstart.sh run      # Run only
./docker-quickstart.sh export   # Export to tar.gz
./docker-quickstart.sh all      # Build, run, and export
```

### Deploy on New Machine:
```bash
# After copying the tar.gz file
bash deploy-on-new-machine.sh
```

## ✅ Verification

Test that everything is working:
```bash
# Check health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "service": "AI Teaching Assistant API",
#   "version": "1.0.0"
# }
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Use a different port
docker run -d -p 8080:8000 --name teaching-app teaching-assistant-api
```

### Container Won't Start
```bash
# Check logs for errors
docker logs teaching-app
```

### Need to Rebuild
```bash
# Remove old container and image
docker rm -f teaching-app
docker rmi teaching-assistant-api

# Rebuild
docker build -t teaching-assistant-api .
```

## 📊 Resource Usage

- **Image Size**: ~1.1GB compressed
- **Memory Usage**: ~200-500MB
- **CPU**: Minimal (spikes during PDF processing)
- **Disk**: Size of database + uploaded files

## 🎯 Summary

1. **Development Machine**: Build → Run → Export to tar.gz
2. **Target Machine**: Load tar.gz → Run → Done!

No Python installation, no pip packages, no environment setup required on the target machine. Just Docker.