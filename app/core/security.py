from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
import time
from collections import defaultdict

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Rate limiting storage (in production, use Redis)
rate_limit_storage = defaultdict(lambda: defaultdict(list))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


class RateLimiter:
    """Rate limiting class"""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limits"""
        now = time.time()
        calls = rate_limit_storage[key]["calls"]
        
        # Remove old calls outside the time window
        rate_limit_storage[key]["calls"] = [
            call_time for call_time in calls 
            if now - call_time < self.period
        ]
        
        # Check if under limit
        if len(rate_limit_storage[key]["calls"]) < self.calls:
            rate_limit_storage[key]["calls"].append(now)
            return True
        
        return False


def get_rate_limiter(plan: str, period_type: str = "minute") -> RateLimiter:
    """Get rate limiter based on plan and period"""
    plan_config = settings.API_PLANS.get(plan, settings.API_PLANS["free"])
    
    if period_type == "minute":
        calls = plan_config["minute_limit"]
        period = 60
    else:  # daily
        calls = plan_config["daily_limit"]
        period = 86400
    
    if calls == -1:  # unlimited
        calls = 999999
    
    return RateLimiter(calls, period)


async def verify_api_key(request: Request) -> Dict[str, Any]:
    """Verify API key from request headers"""
    api_key = request.headers.get("X-API-KEY")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # In production, this would query the database
    # For now, we'll return a mock user for valid API keys
    hashed_key = hash_api_key(api_key)
    
    # Mock validation - replace with database lookup
    # Accept test_ keys or yk_ (Yieldflow) keys
    if api_key.startswith("test_") or api_key.startswith("yk_"):
        return {
            "user_id": "test_user",
            "plan": "professional",
            "api_key_hash": hashed_key,
            "features": settings.API_PLANS["professional"]["features"]
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key"
    )


async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token from Authorization header"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return payload


def check_rate_limit(request: Request, user_data: Dict[str, Any]) -> bool:
    """Check rate limits for user"""
    user_id = user_data.get("user_id")
    plan = user_data.get("plan", "free")
    
    # Check minute limit
    minute_limiter = get_rate_limiter(plan, "minute")
    if not minute_limiter.is_allowed(f"{user_id}_minute"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per minute"
        )
    
    # Check daily limit
    daily_limiter = get_rate_limiter(plan, "daily")
    if not daily_limiter.is_allowed(f"{user_id}_daily"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: daily limit reached"
        )
    
    return True


def check_feature_access(feature: str, user_data: Dict[str, Any]) -> bool:
    """Check if user has access to a specific feature"""
    user_features = user_data.get("features", [])
    
    # Check for global access
    if "all" in user_features:
        return True
    
    # Check for exact feature match
    if feature in user_features:
        return True
    
    # Check for upgraded feature access (e.g., all_financials includes basic_financials)
    feature_hierarchy = {
        "basic_financials": ["all_financials"],
        "simple_ratios": ["advanced_analytics"],
        "basic_analytics": ["advanced_analytics"],
        "charts": ["advanced_analytics"],
    }
    
    # If user has a higher-level feature, they can access the lower-level one
    for higher_feature in feature_hierarchy.get(feature, []):
        if higher_feature in user_features:
            return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Feature '{feature}' not available in your plan"
    )
