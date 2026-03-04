#!/bin/bash

# Docker Quick Start Script for Teaching Assistant API
# This script builds, runs, and optionally exports the Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="teaching-assistant-api"
CONTAINER_NAME="teaching-app"
PORT=8000

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Teaching Assistant API - Docker Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed!${NC}"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
}

# Function to build the image
build_image() {
    echo -e "\n${YELLOW}Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME}:latest .
    echo -e "${GREEN}✓ Image built successfully${NC}"
}

# Function to stop and remove existing container
cleanup_existing() {
    if docker ps -a | grep -q ${CONTAINER_NAME}; then
        echo -e "\n${YELLOW}Removing existing container...${NC}"
        docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1
        echo -e "${GREEN}✓ Existing container removed${NC}"
    fi
}

# Function to run the container
run_container() {
    echo -e "\n${YELLOW}Starting container...${NC}"
    docker run -d -p ${PORT}:8000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest
    echo -e "${GREEN}✓ Container started successfully${NC}"
    echo -e "${GREEN}API is running at: http://localhost:${PORT}${NC}"
    echo -e "${GREEN}API Documentation: http://localhost:${PORT}/docs${NC}"
}

# Function to export image
export_image() {
    echo -e "\n${YELLOW}Exporting Docker image to tar.gz...${NC}"
    docker save ${IMAGE_NAME}:latest | gzip > ${IMAGE_NAME}.tar.gz
    SIZE=$(du -h ${IMAGE_NAME}.tar.gz | cut -f1)
    echo -e "${GREEN}✓ Image exported to ${IMAGE_NAME}.tar.gz (${SIZE})${NC}"
}

# Function to show status
show_status() {
    echo -e "\n${YELLOW}Container Status:${NC}"
    docker ps | grep ${CONTAINER_NAME} || echo "Container is not running"
}

# Function to show logs
show_logs() {
    echo -e "\n${YELLOW}Recent logs:${NC}"
    docker logs --tail 20 ${CONTAINER_NAME}
}

# Main menu
main_menu() {
    echo -e "\n${YELLOW}What would you like to do?${NC}"
    echo "1) Build and run (recommended for first time)"
    echo "2) Build only"
    echo "3) Run only (use existing image)"
    echo "4) Export image to tar.gz"
    echo "5) Stop container"
    echo "6) Show status"
    echo "7) Show logs"
    echo "8) Complete setup (build, run, and export)"
    echo "9) Exit"
    
    read -p "Enter choice [1-9]: " choice
    
    case $choice in
        1)
            build_image
            cleanup_existing
            run_container
            show_status
            ;;
        2)
            build_image
            ;;
        3)
            cleanup_existing
            run_container
            show_status
            ;;
        4)
            export_image
            ;;
        5)
            docker stop ${CONTAINER_NAME}
            echo -e "${GREEN}✓ Container stopped${NC}"
            ;;
        6)
            show_status
            ;;
        7)
            show_logs
            ;;
        8)
            build_image
            cleanup_existing
            run_container
            export_image
            show_status
            echo -e "\n${GREEN}========================================${NC}"
            echo -e "${GREEN}Complete setup finished!${NC}"
            echo -e "${GREEN}Image saved as: ${IMAGE_NAME}.tar.gz${NC}"
            echo -e "${GREEN}API running at: http://localhost:${PORT}${NC}"
            echo -e "${GREEN}========================================${NC}"
            ;;
        9)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
}

# Check Docker installation
check_docker

# If no arguments, show menu
if [ $# -eq 0 ]; then
    while true; do
        main_menu
    done
fi

# Handle command line arguments
case "$1" in
    build)
        build_image
        ;;
    run)
        cleanup_existing
        run_container
        ;;
    export)
        export_image
        ;;
    all)
        build_image
        cleanup_existing
        run_container
        export_image
        show_status
        ;;
    *)
        echo "Usage: $0 {build|run|export|all}"
        echo "Or run without arguments for interactive menu"
        exit 1
        ;;
esac