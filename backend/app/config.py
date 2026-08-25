"""Configuration module for IBVAP backend"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "IBVAP - Intelligent Border Video Analytics Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    # Server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/ibvap"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ALERT_QUEUE: str = "alerts_queue"
    REDIS_EVENT_CHANNEL: str = "events_channel"
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Stream Configuration
    MAX_STREAM_WORKERS: int = int(os.getenv("MAX_STREAM_WORKERS", "10"))
    FRAME_SKIP_INTERVAL: int = 1  # Process every Nth frame
    
    # Model Configuration
    YOLO_MODEL_PATH: str = "models/yolov8m.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    
    # Detection Thresholds
    HUMAN_DETECTION_THRESHOLD: float = 0.6
    VEHICLE_DETECTION_THRESHOLD: float = 0.5
    FACE_DETECTION_THRESHOLD: float = 0.7
    PLATE_DETECTION_THRESHOLD: float = 0.65
    WEAPON_DETECTION_THRESHOLD: float = 0.85  # Higher threshold for weapons
    
    # Alert Configuration
    ALERT_QUEUE_SIZE: int = 1000
    ALERT_RETENTION_DAYS: int = 30
    CRITICAL_ALERT_WEBHOOK: Optional[str] = os.getenv("CRITICAL_ALERT_WEBHOOK")
    
    # Night-time Detection
    NIGHT_MODE_ENABLED: bool = True
    NIGHT_MODE_START_HOUR: int = 18  # 6 PM
    NIGHT_MODE_END_HOUR: int = 6     # 6 AM
    LOW_LIGHT_THRESHOLD: int = 50
    
    # Tracking
    MAX_TRACKER_AGE: int = 30
    MIN_DETECTIONS_FOR_TRACK: int = 2
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, minio
    SNAPSHOT_RETENTION_DAYS: int = 7
    VIDEO_CLIP_RETENTION_DAYS: int = 14
    
    # S3/MinIO
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "ibvap-storage")
    AWS_S3_REGION: str = os.getenv("AWS_S3_REGION", "us-east-1")
    
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET: str = "ibvap"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "logs/ibvap.log"
    
    # Performance
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    GPU_ENABLED: bool = os.getenv("GPU_ENABLED", "True") == "True"
    BATCH_PROCESSING: bool = True
    BATCH_SIZE: int = 8
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
