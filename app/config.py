"""
Configuration settings for the application.
Loads environment variables and defines app settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI settings
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    
    # Legacy OpenAI settings (kept for backward compatibility)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    use_azure_openai: bool = os.getenv("USE_AZURE_OPENAI", "true").lower() == "true"
    
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./teaching_assistant.db")
    
    # Upload settings
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB default
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    chapters_dir: str = os.getenv("CHAPTERS_DIR", "chapters")
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Application settings
    app_title: str = "AI Teaching Assistant API"
    app_version: str = "1.0.0"
    
    # Vision batch processing settings
    vision_batch_size: int = int(os.getenv("VISION_BATCH_SIZE", "20"))
    vision_max_concurrent: int = int(os.getenv("VISION_MAX_CONCURRENT", "20"))
    vision_retry_max_attempts: int = int(os.getenv("VISION_RETRY_MAX_ATTEMPTS", "3"))
    vision_retry_backoff_factor: float = float(os.getenv("VISION_RETRY_BACKOFF_FACTOR", "2.0"))
    vision_timeout_seconds: int = int(os.getenv("VISION_TIMEOUT_SECONDS", "300"))
    
    class Config:
        env_file = ".env"

# Create a single instance to use throughout the app
settings = Settings()

# Create upload directories if they don't exist
Path(settings.upload_dir).mkdir(exist_ok=True)
Path(settings.chapters_dir).mkdir(exist_ok=True)