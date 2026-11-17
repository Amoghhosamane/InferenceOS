import time
import json
import logging
from typing import Optional, Dict, Any, List
from app.config import settings

try:
    import redis.asyncio as aioredis
    from redis.asyncio.connection import ConnectionPool
except ImportError:
    aioredis = None
    ConnectionPool = None

logger = logging.getLogger("inferenceos.redis")

class RedisService:
    """Enterprise Redis Manager for distributed rate limiting, provider cooldowns, and caching.
    
    Adheres strictly to the free-tier-first policy, atomic token-bucket operations,
    and safe graceful degradation.
    """

    def __init__(self):
        self._pool: Optional[Any] = None
        self._client: Optional[Any] = None
        self._memory_rate_limits: Dict[str, Dict[str, Any]] = {}
        self._memory_cooldowns: Dict[str, float] = {}
        self._memory_cache: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize connection pool on FastAPI startup."""
        if not settings.REDIS_URL or not aioredis:
            logger.info("Redis not configured or client library unavailable. Operating with in-memory fallback.")
            return

        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                decode_responses=True,
                socket_timeout=3.0,
                socket_connect_timeout=3.0,
            )
            self._client = aioredis.Redis(connection_pool=self._pool)
            await self._client.ping()
            logger.info("Successfully connected to Redis instance.")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis ({str(e)}). Using in-memory fallback.")
            self._client = None
            if settings.REDIS_REQUIRED:
                raise RuntimeError(f"REDIS_REQUIRED is true but connection to {settings.REDIS_URL} failed.")

    async def close(self):
        """Gracefully release Redis connections on FastAPI shutdown."""
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connection pool disconnected.")

    async def get_client(self):
        # Only attempt to connect to external Redis if REDIS_URL is provided, not default localhost when redis isn't running
        if self._client is not None:
            return self._client
        return None

    # --------------------------------------------------------------------------
    # Distributed Rate Limiting (Token Bucket / Sliding Window)
    # --------------------------------------------------------------------------
    async def check_rate_limit(
        self,
        identifier: str,
        provider: str = "global",
        max_requests: int = 30,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """Atomic sliding window rate limiter.
        
        Returns:
            (is_allowed: bool, retry_after_seconds: int)
        """
        if not settings.ENABLE_DISTRIBUTED_RATE_LIMIT:
            return True, 0

        client = await self.get_client()
        key = f"rl:{provider}:{identifier}"
        now = time.time()

        if client:
            try:
                # Use Redis pipeline for atomic sliding-window check
                async with client.pipeline(transaction=True) as pipe:
                    clear_before = now - window_seconds
                    pipe.zremrangebyscore(key, 0, clear_before)
                    pipe.zcard(key)
                    pipe.zadd(key, {str(now): now})
                    pipe.expire(key, window_seconds)
                    res = await pipe.execute()
                    request_count = res[1]

                    if request_count >= max_requests:
                        # Exceeded limit
                        return False, window_seconds
                    return True, 0
            except Exception as e:
                logger.warning(f"Redis rate-limit query failed: {str(e)}. Falling back to in-memory check.")
                if settings.REDIS_REQUIRED:
                    return False, 60

        # In-memory sliding window fallback
        record = self._memory_rate_limits.get(key, {"timestamps": []})
        # Prune expired
        record["timestamps"] = [t for t in record["timestamps"] if t > now - window_seconds]
        if len(record["timestamps"]) >= max_requests:
            oldest = record["timestamps"][0]
            retry_after = int(max(1, window_seconds - (now - oldest)))
            return False, retry_after

        record["timestamps"].append(now)
        self._memory_rate_limits[key] = record
        return True, 0

    # --------------------------------------------------------------------------
    # Provider Availability & Temporary Rate-Limit Cooldown
    # --------------------------------------------------------------------------
    async def set_provider_cooldown(self, provider: str, cooldown_seconds: int = 60):
        """Mark a provider in temporary rate-limit cooldown (e.g. after HTTP 429)."""
        client = await self.get_client()
        key = f"cooldown:{provider}"
        if client:
            try:
                await client.setex(key, cooldown_seconds, "1")
                return
            except Exception:
                pass
        self._memory_cooldowns[provider] = time.time() + cooldown_seconds

    async def is_provider_in_cooldown(self, provider: str) -> bool:
        """Check if provider is currently in cooldown to prevent repeated rejected calls."""
        client = await self.get_client()
        key = f"cooldown:{provider}"
        if client:
            try:
                res = await client.get(key)
                return bool(res)
            except Exception:
                pass
        expires_at = self._memory_cooldowns.get(provider, 0)
        return time.time() < expires_at

    # --------------------------------------------------------------------------
    # Model Metadata & Non-sensitive Configuration Cache
    # --------------------------------------------------------------------------
    async def get_cached_metadata(self, key: str) -> Optional[Any]:
        client = await self.get_client()
        if client:
            try:
                val = await client.get(f"meta:{key}")
                if val:
                    return json.loads(val)
            except Exception:
                pass
        return self._memory_cache.get(key)

    async def set_cached_metadata(self, key: str, value: Any, ttl_seconds: int = 3600):
        client = await self.get_client()
        if client:
            try:
                await client.setex(f"meta:{key}", ttl_seconds, json.dumps(value))
                return
            except Exception:
                pass
        self._memory_cache[key] = value

redis_service = RedisService()
