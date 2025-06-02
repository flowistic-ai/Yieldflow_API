from typing import List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Yieldflow API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Comprehensive Financial Analytics API"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_EXPIRE_DAYS: int = 365
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # Redis Configuration
    REDIS_URL: str
    
    # External API Keys
    ALPHA_VANTAGE_API_KEY: str
    FMP_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    FRED_API_KEY: Optional[str] = None
    
    # Rate Limiting Configuration
    RATE_LIMIT_FREE_DAILY: int = 100
    RATE_LIMIT_FREE_MINUTE: int = 10
    RATE_LIMIT_BASIC_DAILY: int = 1000
    RATE_LIMIT_BASIC_MINUTE: int = 60
    RATE_LIMIT_PRO_DAILY: int = 10000
    RATE_LIMIT_PRO_MINUTE: int = 300
    
    # Caching Configuration
    CACHE_TTL_HOT_DATA: int = 3600  # 1 hour
    CACHE_TTL_ANALYTICS: int = 86400  # 24 hours
    CACHE_TTL_CHARTS: int = 604800  # 1 week
    CACHE_TTL_STATIC: int = 2592000  # 1 month
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Chart Generation
    CHART_WIDTH: int = 800
    CHART_HEIGHT: int = 600
    CHART_DPI: int = 100
    
    # European Compliance
    BASE_CURRENCY: str = "EUR"
    SUPPORTED_CURRENCIES: List[str] = ["EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK"]
    
    # AI Model Configuration
    AI_MODEL_VERSION: str = "v2.1"
    AI_CONFIDENCE_THRESHOLD: float = 0.7
    
    # API Plans Configuration
    API_PLANS = {
        "free": {
            "daily_limit": RATE_LIMIT_FREE_DAILY,
            "minute_limit": RATE_LIMIT_FREE_MINUTE,
            "features": ["basic_financials", "simple_ratios"]
        },
        "basic": {
            "daily_limit": RATE_LIMIT_BASIC_DAILY,
            "minute_limit": RATE_LIMIT_BASIC_MINUTE,
            "features": ["basic_financials", "simple_ratios", "basic_analytics", "charts"]
        },
        "pro": {
            "daily_limit": RATE_LIMIT_PRO_DAILY,
            "minute_limit": RATE_LIMIT_PRO_MINUTE,
            "features": ["all_financials", "advanced_analytics", "ai_insights", "charts", "compliance"]
        },
        "enterprise": {
            "daily_limit": -1,  # unlimited
            "minute_limit": 1000,
            "features": ["all"]
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validation functions
def validate_api_keys():
    """Validate that required API keys are present"""
    required_keys = {
        "ALPHA_VANTAGE_API_KEY": settings.ALPHA_VANTAGE_API_KEY,
        "FMP_API_KEY": settings.FMP_API_KEY,
        "SECRET_KEY": settings.SECRET_KEY,
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value or value.startswith("your_")]
    
    if missing_keys and not settings.DEBUG:
        raise ValueError(f"Missing required API keys in production: {', '.join(missing_keys)}")
    
    return True


def get_database_url() -> str:
    """Get the appropriate database URL based on environment"""
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL"""
    return settings.REDIS_URL
