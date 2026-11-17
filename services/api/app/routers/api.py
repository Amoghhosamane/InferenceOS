import json
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from app.schemas.chat import (
    ModelListResponse,
    ChatCompletionRequest,
    CompareRequest,
    MetricSummary
)
from app.services.models_registry import VERIFIED_FREE_MODELS, is_model_free_eligible
from app.services.router import router_service
from app.services.metrics import metrics_service
from app.services import history
from app.config import settings

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mock_mode": settings.MOCK_MODE,
        "free_mode_only": settings.FREE_MODE_ONLY,
        "configured_providers": {
            "mock": True,
            "groq": router_service.adapters["groq"].is_configured(),
            "gemini": router_service.adapters["gemini"].is_configured(),
            "openrouter": router_service.adapters["openrouter"].is_configured(),
            "inception": router_service.adapters["inception"].is_configured(),
            "vllm": router_service.adapters["vllm"].is_configured(),
        }
    }

@api_router.get("/ready")
async def readiness_check():
    """Readiness probe checking database connectivity and Redis availability."""
    from app.services.db import engine
    from app.services.cache import cache_service
    from sqlalchemy import text

    db_ready = False
    redis_ready = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ready = True
    except Exception as e:
        db_ready = False

    try:
        redis = await cache_service.get_redis()
        redis_ready = bool(redis is not None)
    except Exception:
        redis_ready = False

    status_code = 200 if db_ready else 503
    return {
        "status": "ready" if db_ready else "not_ready",
        "database": "connected" if db_ready else "disconnected",
        "redis": "connected" if redis_ready else "memory_fallback",
        "mock_mode": settings.MOCK_MODE,
    }

@api_router.get("/models", response_model=ModelListResponse)
async def list_models():
    models_list = list(VERIFIED_FREE_MODELS.values())
    # Update availability flags according to configured adapters
    for m in models_list:
        if settings.MOCK_MODE:
            m.is_available = True
        else:
            adapter = router_service.adapters.get(m.provider)
            m.is_available = adapter.is_configured() if adapter else False

    return ModelListResponse(
        models=models_list,
        mock_mode=settings.MOCK_MODE,
        free_mode_only=settings.FREE_MODE_ONLY,
    )

@api_router.post("/chat/stream")
async def chat_stream(request: ChatCompletionRequest):
    if settings.FREE_MODE_ONLY and not is_model_free_eligible(request.model):
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' is not an approved free-tier model. Free mode is strictly enforced."
        )

    async def event_generator():
        async for chunk in router_service.stream_completion(
            model_id=request.model,
            messages=request.messages,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1024,
            allow_fallback=request.allow_fallback,
        ):
            yield {
                "event": "chunk",
                "data": chunk.model_dump_json()
            }
        yield {
            "event": "done",
            "data": "[DONE]"
        }

    return EventSourceResponse(event_generator())

@api_router.post("/chat/compare")
async def chat_compare(request: CompareRequest):
    if len(request.models) < 2 or len(request.models) > 3:
        raise HTTPException(status_code=400, detail="Compare mode requires 2 or 3 models.")

    for m in request.models:
        if settings.FREE_MODE_ONLY and not is_model_free_eligible(m):
            raise HTTPException(status_code=400, detail=f"Model '{m}' is not an approved free-tier model.")

    async def compare_stream_generator():
        queue: asyncio.Queue = asyncio.Queue()

        async def stream_single(model_id: str):
            try:
                async for chunk in router_service.stream_completion(
                    model_id=model_id,
                    messages=request.messages,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1024,
                ):
                    await queue.put(chunk)
            except Exception as e:
                pass
            finally:
                await queue.put(None)  # Sentinel for this model

        tasks = [asyncio.create_task(stream_single(m)) for m in request.models]
        completed_streams = 0

        while completed_streams < len(request.models):
            chunk = await queue.get()
            if chunk is None:
                completed_streams += 1
                continue
            yield {
                "event": "compare_chunk",
                "data": chunk.model_dump_json()
            }

        yield {
            "event": "done",
            "data": "[DONE]"
        }

    return EventSourceResponse(compare_stream_generator())

@api_router.get("/metrics", response_model=MetricSummary)
async def get_metrics():
    return metrics_service.get_summary(active_mock_mode=settings.MOCK_MODE)

# Conversation History Endpoints
@api_router.get("/conversations")
async def get_conversations():
    return await history.list_conversations()

@api_router.post("/conversations")
async def create_conversation(data: dict):
    title = data.get("title", "New Conversation")
    model = data.get("model", "mock-gpt-oss")
    return await history.create_conversation(title, model)

@api_router.get("/conversations/{conv_id}")
async def get_conversation_detail(conv_id: str):
    conv = await history.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@api_router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    await history.delete_conversation(conv_id)
    return {"status": "deleted", "id": conv_id}

@api_router.post("/conversations/{conv_id}/messages")
async def add_message(conv_id: str, data: dict):
    return await history.add_message(
        conversation_id=conv_id,
        role=data.get("role", "user"),
        content=data.get("content", ""),
        model=data.get("model", ""),
        provider=data.get("provider", ""),
        latency_ms=data.get("latency_ms", 0.0)
    )
