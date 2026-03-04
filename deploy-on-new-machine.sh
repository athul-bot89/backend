#!/bin/bash

# Simple deployment script for new machines
# Just run: bash deploy-on-new-machine.sh

echo "========================================"
echo "Teaching Assistant API - Quick Deploy"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if image file exists
if [ ! -f "teaching-assistant-api.tar.gz" ]; then
    echo "❌ teaching-assistant-api.tar.gz not found!"
    echo "Please ensure the file is in the current directory"
    exit 1
fi

echo "✅ Found teaching-assistant-api.tar.gz"

# Load the Docker image
echo "📦 Loading Docker image..."
docker load < teaching-assistant-api.tar.gz

# Stop and remove any existing container
if docker ps -a | grep -q teaching-app; then
    echo "🔄 Removing existing container..."
    docker rm -f teaching-app > /dev/null 2>&1
fi

# Run the container
echo "🚀 Starting container..."
docker run -d -p 8000:8000 --name teaching-app teaching-assistant-api:latest

# Wait for startup
echo "⏳ Waiting for API to start..."
sleep 5

# Check if running
if docker ps | grep -q teaching-app; then
    echo "✅ Container is running!"
    echo ""
    echo "========================================"
    echo "🎉 Deployment Successful!"
    echo "========================================"
    echo "API URL: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/health"
    echo ""
    echo "To view logs: docker logs teaching-app"
    echo "To stop: docker stop teaching-app"
else
    echo "❌ Container failed to start"
    echo "Check logs with: docker logs teaching-app"
    exit 1
fi