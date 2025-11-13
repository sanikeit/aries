from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./aries.db"
    
    # JWT Security
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pulsar/Kafka
    PULSAR_URL: str = "pulsar://localhost:6650"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # HLS Streams
    HLS_OUTPUT_DIR: str = "./hls_streams"
    
    # Model Configuration
    MODEL_CONFIG_DIR: str = "./configs"
    MODEL_WEIGHTS_DIR: str = "./models"
    
    # Security
    API_KEY_HEADER_NAME: str = "X-API-Key"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()