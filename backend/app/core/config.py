"""
Application Configuration
Loads and validates environment variables using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    
    # Redis
    REDIS_URL: str = Field(..., description="Redis URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, description="Max Redis connections")
    
    # Google Cloud Platform
    GCP_PROJECT_ID: str = Field(..., description="GCP Project ID")
    GCP_REGION: str = Field(default="us-central1", description="GCP region")
    GCP_CREDENTIALS_PATH: Optional[str] = Field(default=None, description="Path to GCP credentials JSON")
    VERTEX_AI_MODEL: str = Field(default="gemini-2.0-flash-exp", description="Vertex AI model name")
    VERTEX_AI_LOCATION: str = Field(default="us-central1", description="Vertex AI location")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME: str = Field(..., description="GCS bucket name for media storage")
    GCS_PHOTO_PREFIX: str = Field(default="photos/", description="GCS prefix for photos")
    GCS_VIDEO_PREFIX: str = Field(default="videos/", description="GCS prefix for videos")
    GCS_AUDIO_PREFIX: str = Field(default="audio/", description="GCS prefix for audio")
    
    # ZEP Memory
    ZEP_API_KEY: str = Field(..., description="ZEP API key")
    ZEP_API_URL: str = Field(default="https://api.getzep.com", description="ZEP API URL")
    ZEP_SESSION_ID: str = Field(default="memories-session", description="Default ZEP session ID")
    
    # Neo4j for Graphiti
    NEO4J_URI: str = Field(..., description="Neo4j connection URI")
    NEO4J_USER: str = Field(default="neo4j", description="Neo4j username")
    NEO4J_PASSWORD: str = Field(..., description="Neo4j password")
    NEO4J_DATABASE: str = Field(default="memories", description="Neo4j database name")
    
    # Embedding Model
    EMBEDDING_MODEL_NAME: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Local embedding model name"
    )
    EMBEDDING_DEVICE: str = Field(default="cpu", description="Device for embeddings: cpu or cuda")
    EMBEDDING_BATCH_SIZE: int = Field(default=32, description="Batch size for embeddings")
    
    # LongMatrix Model
    LONGMATRIX_CHECKPOINT_PATH: str = Field(
        default="./finetune/best.pt",
        description="Path to LongMatrix checkpoint"
    )
    LONGMATRIX_CONFIG_PATH: str = Field(
        default="./finetune/config_used.yaml",
        description="Path to LongMatrix config"
    )
    LONGMATRIX_MAX_LENGTH: int = Field(default=512, description="Max sequence length for LongMatrix")
    
    # Security
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="JWT expiration in minutes")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = Field(default=10, description="Max agent iterations")
    AGENT_TEMPERATURE: float = Field(default=0.7, description="Agent temperature")
    AGENT_MAX_TOKENS: int = Field(default=2048, description="Max tokens per agent response")
    AGENT_REASONING_ENABLED: bool = Field(default=True, description="Enable agent reasoning display")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_BURST: int = Field(default=10, description="Rate limit burst")
    
    # Media Processing
    MAX_UPLOAD_SIZE_MB: int = Field(default=100, description="Max upload size in MB")
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".webp"],
        description="Allowed image extensions"
    )
    ALLOWED_VIDEO_EXTENSIONS: List[str] = Field(
        default=[".mp4", ".mov", ".avi", ".mkv"],
        description="Allowed video extensions"
    )
    ALLOWED_AUDIO_EXTENSIONS: List[str] = Field(
        default=[".mp3", ".wav", ".m4a", ".ogg"],
        description="Allowed audio extensions"
    )
    IMAGE_MAX_DIMENSION: int = Field(default=2048, description="Max image dimension")
    VIDEO_THUMBNAIL_TIME: float = Field(default=1.0, description="Video thumbnail time in seconds")
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string if needed"""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @field_validator("ALLOWED_IMAGE_EXTENSIONS", "ALLOWED_VIDEO_EXTENSIONS", "ALLOWED_AUDIO_EXTENSIONS", mode="before")
    @classmethod
    def parse_extensions(cls, v):
        """Parse extensions from JSON string if needed"""
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
