"""
API Dependencies for Yieldflow API
Handles authentication, authorization, and feature access control
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, APIKey
from app.core.config import settings
import structlog

logger = structlog.get_logger()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from API key
    """
    try:
        api_key = credentials.credentials
        
        # Query API key from database
        db_api_key = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not db_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check if API key is expired
        if db_api_key.is_expired():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key expired"
            )
        
        # Get associated user
        user = db.query(User).filter(User.id == db_api_key.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive"
            )
        
        # Update last used timestamp
        db_api_key.update_usage()
        db.commit()
        
        logger.info("User authenticated", user_id=user.id, plan=user.plan)
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def require_feature_access(feature: str):
    """
    Create a dependency that checks if user has access to specific feature
    """
    async def _check_feature_access(current_user: User = Depends(get_current_user)) -> User:
        plan_features = {
            "free": [
                "basic_company_info",
                "basic_financial_data"
            ],
            "basic": [
                "basic_company_info",
                "basic_financial_data",
                "financial_ratios",
                "trend_analysis"
            ],
            "pro": [
                "basic_company_info",
                "basic_financial_data", 
                "financial_ratios",
                "trend_analysis",
                "advanced_analytics",
                "peer_comparison",
                "forecasting",
                "custom_ratios"
            ],
            "enterprise": [
                "basic_company_info",
                "basic_financial_data",
                "financial_ratios", 
                "trend_analysis",
                "advanced_analytics",
                "peer_comparison",
                "forecasting",
                "custom_ratios",
                "bulk_data",
                "real_time_data",
                "api_webhooks",
                "white_label"
            ]
        }
        
        user_features = plan_features.get(current_user.plan, [])
        
        if feature not in user_features:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' requires upgrade to higher plan. Current plan: {current_user.plan}"
            )
        
        logger.info("Feature access granted", 
                    user_id=current_user.id, 
                    feature=feature, 
                    plan=current_user.plan)
        return current_user
    
    return _check_feature_access


def get_rate_limit_info(user: User) -> Dict[str, Any]:
    """
    Get rate limiting information for user's plan
    """
    rate_limits = {
        "free": {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "requests_per_day": 1000
        },
        "basic": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "requests_per_day": 10000
        },
        "pro": {
            "requests_per_minute": 300,
            "requests_per_hour": 5000,
            "requests_per_day": 50000
        },
        "enterprise": {
            "requests_per_minute": 1000,
            "requests_per_hour": 20000,
            "requests_per_day": 200000
        }
    }
    
    return rate_limits.get(user.plan, rate_limits["free"])


async def check_rate_limit(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if user has exceeded rate limits
    This is a simplified version - in production you'd use Redis for tracking
    """
    # In a real implementation, you would:
    # 1. Check Redis for current usage counts
    # 2. Implement sliding window rate limiting
    # 3. Track per-minute, per-hour, per-day limits
    # 4. Return appropriate 429 errors when limits exceeded
    
    # For now, just return the user (rate limiting would be implemented with Redis)
    return current_user


# Optional: Admin access
async def require_admin_access(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin access for sensitive endpoints
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Feature-specific dependencies
async def require_basic_access(
    current_user: User = Depends(require_feature_access("basic_financial_data"))
) -> User:
    return current_user


async def require_advanced_analytics(
    current_user: User = Depends(require_feature_access("advanced_analytics"))
) -> User:
    return current_user


async def require_pro_features(
    current_user: User = Depends(require_feature_access("forecasting"))
) -> User:
    return current_user 