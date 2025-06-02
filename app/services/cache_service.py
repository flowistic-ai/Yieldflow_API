import json
import hashlib
from typing import Optional, Any, Dict
import redis.asyncio as redis
from datetime import datetime, timedelta
import structlog

from app.core.config import settings
from app.utils.exceptions import CacheError

logger = structlog.get_logger()


class CacheService:
    """Redis-based caching service with multiple TTL levels"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client connection"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error("Failed to connect to Redis", error=str(e))
                raise CacheError(f"Redis connection failed: {str(e)}", "connect")
        
        return self.redis_client
    
    def _generate_key(self, prefix: str, identifier: str, **kwargs) -> str:
        """Generate cache key with optional parameters"""
        key_parts = [prefix, identifier]
        
        # Add additional parameters if provided
        if kwargs:
            sorted_params = sorted(kwargs.items())
            param_string = "_".join([f"{k}:{v}" for k, v in sorted_params])
            key_parts.append(param_string)
        
        return ":".join(key_parts)
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for caching"""
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=str)
            return str(data)
        except Exception as e:
            raise CacheError(f"Failed to serialize data: {str(e)}", "serialize")
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize cached data"""
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
        except Exception as e:
            raise CacheError(f"Failed to deserialize data: {str(e)}", "deserialize")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            client = await self.get_client()
            cached_data = await client.get(key)
            
            if cached_data is None:
                return None
            
            return self._deserialize_data(cached_data)
        
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache with TTL"""
        try:
            client = await self.get_client()
            serialized_data = self._serialize_data(value)
            
            await client.setex(key, ttl, serialized_data)
            logger.debug("Cache set successful", key=key, ttl=ttl)
            return True
        
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            client = await self.get_client()
            deleted_count = await client.delete(key)
            return deleted_count > 0
        
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            client = await self.get_client()
            return await client.exists(key) > 0
        
        except Exception as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False
    
    # Specialized caching methods for different data types
    
    async def cache_hot_data(self, key: str, data: Any) -> bool:
        """Cache hot data (current ratios, recent analysis) - 1 hour TTL"""
        cache_key = self._generate_key("hot", key)
        return await self.set(cache_key, data, settings.CACHE_TTL_HOT_DATA)
    
    async def get_hot_data(self, key: str) -> Optional[Any]:
        """Get hot data from cache"""
        cache_key = self._generate_key("hot", key)
        return await self.get(cache_key)
    
    async def cache_analytics(self, key: str, data: Any) -> bool:
        """Cache analytics data - 24 hour TTL"""
        cache_key = self._generate_key("analytics", key)
        return await self.set(cache_key, data, settings.CACHE_TTL_ANALYTICS)
    
    async def get_analytics(self, key: str) -> Optional[Any]:
        """Get analytics data from cache"""
        cache_key = self._generate_key("analytics", key)
        return await self.get(cache_key)
    
    async def cache_chart(self, key: str, data: Any) -> bool:
        """Cache chart data - 1 week TTL"""
        cache_key = self._generate_key("chart", key)
        return await self.set(cache_key, data, settings.CACHE_TTL_CHARTS)
    
    async def get_chart(self, key: str) -> Optional[Any]:
        """Get chart data from cache"""
        cache_key = self._generate_key("chart", key)
        return await self.get(cache_key)
    
    async def cache_static_data(self, key: str, data: Any) -> bool:
        """Cache static data - 1 month TTL"""
        cache_key = self._generate_key("static", key)
        return await self.set(cache_key, data, settings.CACHE_TTL_STATIC)
    
    async def get_static_data(self, key: str) -> Optional[Any]:
        """Get static data from cache"""
        cache_key = self._generate_key("static", key)
        return await self.get(cache_key)
    
    # Financial data specific caching
    
    async def cache_financial_data(self, ticker: str, period: str, data: Any) -> bool:
        """Cache financial statements data"""
        key = f"financials_{ticker}_{period}"
        return await self.cache_analytics(key, data)
    
    async def get_financial_data(self, ticker: str, period: str) -> Optional[Any]:
        """Get cached financial statements data"""
        key = f"financials_{ticker}_{period}"
        return await self.get_analytics(key)
    
    async def cache_ratio_analysis(self, ticker: str, analysis_type: str, data: Any) -> bool:
        """Cache ratio analysis results"""
        key = f"ratios_{ticker}_{analysis_type}"
        return await self.cache_analytics(key, data)
    
    async def get_ratio_analysis(self, ticker: str, analysis_type: str) -> Optional[Any]:
        """Get cached ratio analysis results"""
        key = f"ratios_{ticker}_{analysis_type}"
        return await self.get_analytics(key)
    
    async def cache_ai_insights(self, ticker: str, data: Any) -> bool:
        """Cache AI insights"""
        key = f"ai_insights_{ticker}"
        return await self.cache_hot_data(key, data)
    
    async def get_ai_insights(self, ticker: str) -> Optional[Any]:
        """Get cached AI insights"""
        key = f"ai_insights_{ticker}"
        return await self.get_hot_data(key)
    
    # Cache invalidation methods
    
    async def invalidate_ticker_cache(self, ticker: str) -> int:
        """Invalidate all cache entries for a ticker"""
        try:
            client = await self.get_client()
            pattern = f"*{ticker}*"
            keys = await client.keys(pattern)
            
            if keys:
                deleted_count = await client.delete(*keys)
                logger.info("Cache invalidated for ticker", ticker=ticker, deleted_keys=deleted_count)
                return deleted_count
            
            return 0
        
        except Exception as e:
            logger.error("Cache invalidation failed", ticker=ticker, error=str(e))
            return 0
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Redis connection closed")
