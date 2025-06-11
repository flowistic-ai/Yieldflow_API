"""
API Dependencies for Yieldflow API
Handles authentication, authorization, and feature access control
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
import json
import os
from datetime import datetime

logger = structlog.get_logger()
security = HTTPBearer()


class MockUser:
    """Mock user class for development when database is not available"""
    def __init__(self, id: int, email: str, plan: str, is_active: bool = True):
        self.id = id
        self.email = email
        self.plan = plan
        self.is_active = is_active
        self.is_admin = False


def load_test_api_keys():
    """Load test API keys from generated files"""
    test_keys = {}
    
    # Load from generated API key files
    for plan in ["free", "basic", "pro", "enterprise"]:
        key_file = f"api_key_{plan}.json"
        if os.path.exists(key_file):
            try:
                with open(key_file, 'r') as f:
                    data = json.load(f)
                    api_key = data["api_key"]
                    test_keys[api_key] = {
                        "user_id": data["user_data"]["id"],
                        "email": data["user_data"]["email"],
                        "plan": data["user_data"]["plan"],
                        "is_active": True,
                        "expires_at": data["api_key_data"]["expires_at"]
                    }
            except Exception as e:
                logger.warning(f"Could not load {key_file}", error=str(e))
    
    # Add some hardcoded test keys for convenience
    test_keys.update({
        "test_free_key": {"user_id": 100, "email": "free@test.com", "plan": "free", "is_active": True},
        "test_basic_key": {"user_id": 101, "email": "basic@test.com", "plan": "basic", "is_active": True},
        "test_pro_key": {"user_id": 102, "email": "pro@test.com", "plan": "pro", "is_active": True},
        "test_enterprise_key": {"user_id": 103, "email": "enterprise@test.com", "plan": "enterprise", "is_active": True},
    })
    
    return test_keys


# Load test keys at startup
TEST_API_KEYS = load_test_api_keys()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> MockUser:
    """
    Get current user from API key
    """
    try:
        api_key = credentials.credentials
        
        # First try test API keys (for development)
        if api_key in TEST_API_KEYS:
            key_data = TEST_API_KEYS[api_key]
            logger.info("Using test API key", 
                       user_id=key_data["user_id"], 
                       plan=key_data["plan"],
                       email=key_data["email"])
            
            return MockUser(
                id=key_data["user_id"],
                email=key_data["email"], 
                plan=key_data["plan"],
                is_active=key_data["is_active"]
            )
        
        # Try database lookup (when database is available) - disabled for now
        # try:
        #     from app.models.user import User, APIKey
        #     from app.core.database import get_db
        #     
        #     # Query API key from database
        #     db_api_key = db.query(APIKey).filter(
        #         APIKey.key_hash == api_key,  # In production, store hashed keys
        #         APIKey.is_active == True
        #     ).first()
        #     
        #     if db_api_key:
        #         # Check if API key is expired
        #         if hasattr(db_api_key, 'is_expired') and db_api_key.is_expired():
        #             raise HTTPException(
        #                 status_code=status.HTTP_401_UNAUTHORIZED,
        #                 detail="API key expired"
        #             )
        #         
        #         # Get associated user
        #         user = db.query(User).filter(User.id == db_api_key.user_id).first()
        #         if user and user.is_active:
        #             # Update last used timestamp
        #             if hasattr(db_api_key, 'update_usage'):
        #                 db_api_key.update_usage()
        #                 db.commit()
        #             
        #             logger.info("User authenticated from database", user_id=user.id, plan=user.plan)
        #             return user
        #             
        # except Exception as db_error:
        #     logger.warning("Database authentication failed, trying test keys", error=str(db_error))
        
        # If we get here, the API key is invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
        
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
    async def _check_feature_access(current_user = Depends(get_current_user)):
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


def get_rate_limit_info(user) -> Dict[str, Any]:
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
    current_user = Depends(get_current_user)
):
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
    current_user = Depends(get_current_user)
):
    """
    Require admin access for sensitive endpoints
    """
    is_admin = getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superuser', False)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Feature-specific dependencies
async def require_basic_access(
    current_user = Depends(require_feature_access("basic_financial_data"))
):
    return current_user


async def require_advanced_analytics(
    current_user = Depends(require_feature_access("advanced_analytics"))
):
    return current_user


async def require_pro_features(
    current_user = Depends(require_feature_access("forecasting"))
):
    return current_user 