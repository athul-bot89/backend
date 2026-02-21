"""
Main FastAPI application.
This is the entry point for the AI Teaching Assistant backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.database import init_db
from app.api import textbooks, chapters, extraction

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.app_title} v{settings.app_version}")
    init_db()  # Initialize database tables
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application")

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Backend API for AI-powered teaching assistant that processes textbooks and generates educational content.",
    lifespan=lifespan
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(textbooks.router, prefix="/api/v1")
app.include_router(chapters.router, prefix="/api/v1")
app.include_router(extraction.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - provides basic API information.
    """
    return {
        "message": "Welcome to the AI Teaching Assistant API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.app_title,
        "version": settings.app_version
    }

# API information endpoint
@app.get("/api/v1")
async def api_info():
    """
    Provides information about available API endpoints.
    """
    return {
        "version": "v1",
        "endpoints": {
            "textbooks": "/api/v1/textbooks",
            "chapters": "/api/v1/chapters",
            "extraction": "/api/v1/extract",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        },
        "description": "API for managing textbooks, chapters, and educational content generation"
    }

if __name__ == "__main__":
    # This block is for development only
    # In production, use a proper ASGI server like uvicorn or gunicorn
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True  # Enable auto-reload during development
    )