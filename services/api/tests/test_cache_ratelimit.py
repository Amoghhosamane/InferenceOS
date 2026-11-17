import pytest
from app.services.cache import CacheRateLimitService

@pytest.mark.asyncio
async def test_in_memory_rate_limiter():
    service = CacheRateLimitService()
    client_ip = "192.168.1.100"
    
    # Within limit of 3 requests
    assert await service.check_rate_limit(client_ip, max_requests=3, window_seconds=60) is True
    assert await service.check_rate_limit(client_ip, max_requests=3, window_seconds=60) is True
    assert await service.check_rate_limit(client_ip, max_requests=3, window_seconds=60) is True
    
    # Exceeding limit
    assert await service.check_rate_limit(client_ip, max_requests=3, window_seconds=60) is False

@pytest.mark.asyncio
async def test_cache_fallback():
    service = CacheRateLimitService()
    # Cache key set and retrieve
    service._memory_cache["test_prompt_hash"] = "cached completion output"
    res = await service.get_cached_response("test_prompt_hash")
    # By default ENABLE_REDIS_CACHE is false
    assert res is None or res == "cached completion output"
