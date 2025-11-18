"""
Configuration settings for the Face Recognition API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Face Recognition API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # File Upload Settings
    upload_dir: str = "uploads"
    known_faces_dir: str = "known_faces"
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: set = {".jpg", ".jpeg", ".png", ".bmp"}

    # Face Recognition Settings
    face_detection_model: str = "hog"  # hog or cnn
    num_jitters: int = 1  # Number of times to re-sample when calculating encoding
    tolerance: float = 0.6  # Face comparison tolerance (lower is more strict)

    # Security (optional)
    secret_key: Optional[str] = None
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
