import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "mock_mode" in data

@pytest.mark.asyncio
async def test_models_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert len(data["models"]) > 0
    # Every model exposed must have verified_free or promotional_trial status
    for m in data["models"]:
        assert m["pricing_status"] in ["verified_free", "promotional_trial"]

@pytest.mark.asyncio
async def test_chat_stream_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "model": "mock-gpt-oss",
            "messages": [{"role": "user", "content": "Explain gravity in one sentence"}],
            "stream": True
        }
        response = await ac.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_chat_stream_rejects_paid_or_unknown_model():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "model": "anthropic/claude-3-opus",
            "messages": [{"role": "user", "content": "Test"}],
            "stream": True
        }
        response = await ac.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "p50_latency_ms" in data
    assert "sample_size" in data

@pytest.mark.asyncio
async def test_conversations_crud():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create
        res = await ac.post("/api/v1/conversations", json={"title": "Test Chat", "model": "mock-gpt-oss"})
        assert res.status_code == 200
        conv = res.json()
        conv_id = conv["id"]

        # List
        res_list = await ac.get("/api/v1/conversations")
        assert res_list.status_code == 200
        assert any(c["id"] == conv_id for c in res_list.json())

        # Detail
        res_detail = await ac.get(f"/api/v1/conversations/{conv_id}")
        assert res_detail.status_code == 200
        assert res_detail.json()["id"] == conv_id

        # Delete
        res_del = await ac.delete(f"/api/v1/conversations/{conv_id}")
        assert res_del.status_code == 200
