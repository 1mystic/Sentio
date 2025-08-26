from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Mindfluence API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://mindfluence.vercel.app",
        "https://mindfluence.netlify.app"
    ]
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = ""  # Will be constructed from Supabase URL
    
    # ML Models
    HUGGINGFACE_API_KEY: str = ""
    SENTIMENT_MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # Email (Optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Redis (Optional)
    REDIS_URL: str = ""
    
    # Encryption
    ENCRYPTION_KEY: str = ""
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Assessment Settings
    ASSESSMENT_CACHE_TTL: int = 3600  # 1 hour
    
    # Journal Settings
    MAX_JOURNAL_ENTRY_LENGTH: int = 10000
    
    # Community Settings
    MAX_POST_LENGTH: int = 5000
    MAX_COMMENT_LENGTH: int = 1000
    
    # ML Settings
    SENTIMENT_CONFIDENCE_THRESHOLD: float = 0.7
    RECOMMENDATION_CACHE_TTL: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Construct database URL from Supabase URL
        if self.SUPABASE_URL and not self.DATABASE_URL:
            self.DATABASE_URL = self.SUPABASE_URL.replace("https://", "postgresql://postgres:").replace(".supabase.co", ".supabase.co:5432/postgres")

# Create settings instance
settings = Settings()

# Environment-specific configurations
if os.getenv("ENVIRONMENT") == "production":
    settings.DEBUG = False
elif os.getenv("ENVIRONMENT") == "development":
    settings.DEBUG = True
