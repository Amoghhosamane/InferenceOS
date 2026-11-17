import pytest
from app.adapters.mock import MockAdapter
from app.schemas.chat import ChatMessage

@pytest.mark.asyncio
async def test_mock_adapter_stream():
    adapter = MockAdapter()
    assert adapter.is_configured() is True
    
    messages = [ChatMessage(role="user", content="Hello test")]
    chunks = []
    async for chunk in adapter.stream_chat(
        model_id="mock-gpt-oss",
        messages=messages,
        request_id="req-123"
    ):
        chunks.append(chunk)

    assert len(chunks) > 0
    assert chunks[0].id == "req-123"
    assert chunks[0].model == "mock-gpt-oss"
    # Verify final chunk contains usage
    assert chunks[-1].usage is not None
    assert "total_tokens" in chunks[-1].usage
