import time
from typing import Optional
from app.config import settings

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

class CacheRateLimitService:
    """Enterprise rate limiting and caching backed by Redis with automatic memory fallback."""

    def __init__(self):
        self._redis_client = None
        self._memory_cache = {}
        self._memory_rate_limits = {}

    async def get_redis(self):
        if not settings.REDIS_URL or not aioredis:
            return None
        if self._redis_client is None:
            try:
                self._redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=2.0
                )
                await self._redis_client.ping()
            except Exception:
                self._redis_client = None
        return self._redis_client

    async def check_rate_limit(self, client_ip: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Sliding-window token bucket / counter rate limiter."""
        redis = await self.get_redis()
        key = f"rate_limit:{client_ip}"
        
        if redis:
            try:
                current = await redis.incr(key)
                if current == 1:
                    await redis.expire(key, window_seconds)
                return current <= max_requests
            except Exception:
                pass  # Fall back to in-memory counter if Redis fails

        # In-memory sliding window fallback
        now = time.time()
        record = self._memory_rate_limits.get(client_ip, {"count": 0, "reset": now + window_seconds})
        if now > record["reset"]:
            record = {"count": 1, "reset": now + window_seconds}
        else:
            record["count"] += 1
        self._memory_rate_limits[client_ip] = record
        return record["count"] <= max_requests

    async def get_cached_response(self, cache_key: str) -> Optional[str]:
        """Fetch cached model completion if enabled."""
        if not settings.ENABLE_REDIS_CACHE:
            return None
        redis = await self.get_redis()
        if redis:
            try:
                return await redis.get(f"cache:{cache_key}")
            except Exception:
                pass
        return self._memory_cache.get(cache_key)

    async def set_cached_response(self, cache_key: str, value: str, ttl_seconds: int = 3600):
        """Store model response in cache with TTL."""
        if not settings.ENABLE_REDIS_CACHE:
            return
        redis = await self.get_redis()
        if redis:
            try:
                await redis.setex(f"cache:{cache_key}", ttl_seconds, value)
                return
            except Exception:
                pass
        self._memory_cache[cache_key] = value

cache_service = CacheRateLimitService()
