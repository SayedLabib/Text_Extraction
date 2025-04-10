from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Text Extraction API"
    PROJECT_DESCRIPTION: str = "API for extracting text from PDF, Images, and DOCX files"
    PROJECT_VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # File settings
    SUPPORTED_FORMATS: List[str] = ["PDF", "DOCX", "JPG", "JPEG", "PNG", "GIF", "BMP"]
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()