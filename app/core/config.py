import os
from typing import Dict, List, Any, ClassVar, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Yieldflow API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Comprehensive FastAPI Financial Analytics API - From Data to Insights in One API Call"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="test-secret-key-for-development", description="Secret key for JWT token generation")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Database settings
    DATABASE_URL: str = Field(default="postgresql+asyncpg://syedzeewaqarhussain:password@localhost/yieldflow_db", description="PostgreSQL database URL")
    PORT: int = Field(default=8000, description="Port to run the application on")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis cache URL")
    
    # External API keys
    ALPHA_VANTAGE_API_KEY: str = Field(default="8U60647QE9JL1KKX", description="Alpha Vantage API key")
    FMP_API_KEY: str = Field(default="SaSKENT5J7T2P8ix8Un7qfJO80GPmh4M", description="Financial Modeling Prep API key")
    POLYGON_API_KEY: str = Field(default="", description="Polygon.io API key")
    TWELVEDATA_API_KEY: str = Field(default="", description="Twelve Data API key")
    IEX_CLOUD_API_KEY: str = Field(default="", description="IEX Cloud API key")
    QUANDL_API_KEY: str = Field(default="", description="Quandl API key")
    EOD_HISTORICAL_API_KEY: str = Field(default="", description="EOD Historical Data API key")
    FRED_API_KEY: str = Field(default="a8e11fe22a153d722a432b582ac47912", description="FRED (Federal Reserve Economic Data) API key")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for AI insights")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic Claude API key for AI insights")
    GOOGLE_GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for AI insights")
    NEWS_API_KEY: str = Field(default="", description="NewsAPI.org API key for news sentiment analysis")
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000", 
            "http://localhost:8000", 
            "https://localhost:3000",
            "https://yieldflow-api.onrender.com"
        ],
        description="List of allowed CORS origins"
    )
    
    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Cache TTL settings (in seconds)
    CACHE_TTL_HOT: int = Field(default=300, description="Hot data cache TTL (5 minutes)")
    CACHE_TTL_ANALYTICS: int = Field(default=3600, description="Analytics cache TTL (1 hour)")
    CACHE_TTL_CHARTS: int = Field(default=7200, description="Charts cache TTL (2 hours)")
    CACHE_TTL_STATIC: int = Field(default=86400, description="Static data cache TTL (24 hours)")
    
    # API Plans configuration - using ClassVar to indicate this is not a field
    API_PLANS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "free": {
            "daily_limit": 100,
            "minute_limit": 10,
            "features": ["basic_financials", "simple_ratios"]
        },
        "basic": {
            "daily_limit": 1000,
            "minute_limit": 60,
            "features": ["basic_financials", "simple_ratios", "basic_analytics", "charts"]
        },
        "professional": {
            "daily_limit": 10000,
            "minute_limit": 300,
            "features": ["all_financials", "advanced_analytics", "ai_insights", "charts", "compliance"]
        },
        "enterprise": {
            "daily_limit": -1,  # Unlimited
            "minute_limit": 1000,
            "features": ["all"]
        }
    }
    
    # Feature flags
    ENABLE_AI_INSIGHTS: bool = Field(default=False, description="Enable AI insights feature")
    ENABLE_COMPLIANCE_FEATURES: bool = Field(default=True, description="Enable European compliance features")
    ENABLE_CACHING: bool = Field(default=True, description="Enable caching")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in environment but ignore them


# Global settings instance
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
