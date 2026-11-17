import pytest
from app.adapters.inception import InceptionAdapter
from app.schemas.chat import ChatMessage
from app.config import settings

@pytest.mark.asyncio
async def test_inception_adapter_missing_key_behavior():
    # Test that missing key returns informative error chunk without crashing
    orig_key = settings.INCEPTION_API_KEY
    settings.INCEPTION_API_KEY = ""
    try:
        adapter = InceptionAdapter()
        assert adapter.is_configured() is False
        
        chunks = []
        async for chunk in adapter.stream_chat(
            model_id="inception/mercury-3",
            messages=[ChatMessage(role="user", content="Hello Mercury")],
            request_id="inc-test-1"
        ):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0].error is not None
        assert "INCEPTION_API_KEY" in chunks[0].error
    finally:
        settings.INCEPTION_API_KEY = orig_key
