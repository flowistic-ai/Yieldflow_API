from typing import Generator, Dict, Any
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_api_key, check_rate_limit, check_feature_access
from app.services.cache_service import CacheService


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session dependency"""
    async for session in get_async_session():
        yield session


async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from API key"""
    user_data = await verify_api_key(request)
    check_rate_limit(request, user_data)
    return user_data


def require_feature(feature_name: str):
    """Dependency factory to require specific features"""
    async def feature_dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        check_feature_access(feature_name, user)
        return user
    return feature_dependency


async def get_cache_service() -> CacheService:
    """Get cache service dependency"""
    return CacheService()


# Common feature dependencies
require_basic_financials = require_feature("basic_financials")
require_advanced_analytics = require_feature("advanced_analytics")
require_ai_insights = require_feature("ai_insights")
require_charts = require_feature("charts")
require_compliance = require_feature("compliance")
