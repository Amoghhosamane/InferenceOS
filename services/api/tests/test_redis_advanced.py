import pytest
import asyncio
from app.services.redis_manager import RedisService

@pytest.mark.asyncio
async def test_redis_sliding_window_rate_limiting():
    service = RedisService()
    client_id = "test-client-ip"
    
    # Send 5 allowed requests within limit of 5
    for i in range(5):
        allowed, retry_after = await service.check_rate_limit(
            identifier=client_id,
            provider="test-provider",
            max_requests=5,
            window_seconds=10
        )
        assert allowed is True
        assert retry_after == 0

    # 6th request should be rate-limited
    allowed, retry_after = await service.check_rate_limit(
        identifier=client_id,
        provider="test-provider",
        max_requests=5,
        window_seconds=10
    )
    assert allowed is False
    assert retry_after > 0

@pytest.mark.asyncio
async def test_redis_provider_cooldown():
    service = RedisService()
    provider = "groq-cooldown-test"
    
    assert await service.is_provider_in_cooldown(provider) is False
    
    # Mark cooldown for 2 seconds
    await service.set_provider_cooldown(provider, cooldown_seconds=2)
    assert await service.is_provider_in_cooldown(provider) is True

@pytest.mark.asyncio
async def test_redis_metadata_caching():
    service = RedisService()
    key = "model_config_sample"
    data = {"models": ["mock-gpt-oss", "groq/openai/gpt-oss-20b"], "status": "active"}
    
    await service.set_cached_metadata(key, data, ttl_seconds=60)
    cached = await service.get_cached_metadata(key)
    assert cached == data
