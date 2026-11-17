import time
import uuid
from typing import AsyncGenerator, Dict, List
from app.adapters.base import BaseProviderAdapter
from app.adapters.mock import MockAdapter
from app.adapters.groq import GroqAdapter
from app.adapters.gemini import GeminiAdapter
from app.adapters.openrouter import OpenRouterAdapter
from app.adapters.inception import InceptionAdapter
from app.adapters.vllm import VLLMAdapter
from app.schemas.chat import ChatMessage, StreamChunk, StreamDelta
from app.services.models_registry import VERIFIED_FREE_MODELS, is_model_free_eligible
from app.services.metrics import metrics_service
from app.services.security import sanitize_error_message
from app.config import settings

class RouterService:
    def __init__(self):
        self.adapters: Dict[str, BaseProviderAdapter] = {
            "mock": MockAdapter(),
            "groq": GroqAdapter(),
            "gemini": GeminiAdapter(),
            "openrouter": OpenRouterAdapter(),
            "inception": InceptionAdapter(),
            "vllm": VLLMAdapter(),
        }

    def get_adapter_for_model(self, model_id: str) -> BaseProviderAdapter:
        if settings.MOCK_MODE:
            return self.adapters["mock"]

        if model_id.startswith("mock-") or model_id in ["mock-gpt-oss", "mock-fast-chat"]:
            return self.adapters["mock"]
        elif model_id.startswith("groq/"):
            return self.adapters["groq"]
        elif model_id.startswith("gemini/"):
            return self.adapters["gemini"]
        elif model_id.startswith("openrouter/"):
            return self.adapters["openrouter"]
        elif model_id.startswith("inception/"):
            return self.adapters["inception"]
        elif model_id.startswith("vllm/"):
            return self.adapters["vllm"]
        else:
            return self.adapters["mock"]

    def find_free_fallback_model(self, failed_model_id: str) -> str | None:
        """Find an alternative verified free model from an operational provider."""
        failed_meta = VERIFIED_FREE_MODELS.get(failed_model_id)
        failed_provider = failed_meta.provider if failed_meta else ""

        # Candidates must be verified free and from an alternate configured provider
        for cand_id, meta in VERIFIED_FREE_MODELS.items():
            if cand_id == failed_model_id:
                continue
            if meta.provider == failed_provider:
                continue
            # If in mock mode, allow mock models
            if settings.MOCK_MODE and meta.provider == "mock":
                return cand_id
            # In live mode, ensure candidate provider is configured
            if not settings.MOCK_MODE and meta.provider != "mock":
                adapter = self.adapters.get(meta.provider)
                if adapter and adapter.is_configured():
                    return cand_id

        # Fallback to mock model if permitted
        return "mock-gpt-oss"

    async def stream_completion(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        allow_fallback: bool = False,
        request_id: str = None
    ) -> AsyncGenerator[StreamChunk, None]:
        req_id = request_id or str(uuid.uuid4())

        # 1. Strict Free Mode Safeguard
        if settings.FREE_MODE_ONLY and not is_model_free_eligible(model_id):
            yield StreamChunk(
                id=req_id,
                model=model_id,
                provider="router",
                delta=StreamDelta(),
                error=f"Model '{model_id}' is not in the verified free-tier allowlist. Request rejected to prevent billing."
            )
            return

        adapter = self.get_adapter_for_model(model_id)
        start_time = time.perf_counter()
        first_token_time = None
        has_error = False
        chunks_yielded = 0

        try:
            async for chunk in adapter.stream_chat(
                model_id=model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                request_id=req_id,
            ):
                if chunk.error:
                    chunk.error = sanitize_error_message(chunk.error)
                    has_error = True
                    # Check if fallback is enabled and we haven't sent substantive tokens yet
                    if allow_fallback and chunks_yielded == 0:
                        fallback_id = self.find_free_fallback_model(model_id)
                        if fallback_id and fallback_id != model_id:
                            fallback_adapter = self.get_adapter_for_model(fallback_id)
                            # Yield notification chunk indicating fallback
                            yield StreamChunk(
                                id=req_id,
                                model=fallback_id,
                                provider=fallback_adapter.provider_name,
                                delta=StreamDelta(
                                    content=f"\n*[Notice: Fallback activated from {model_id} to verified free model {fallback_id} due to upstream provider error]*\n\n"
                                ),
                                fallback_used=True,
                                original_model=model_id
                            )
                            # Stream from fallback provider
                            async for f_chunk in fallback_adapter.stream_chat(
                                model_id=fallback_id,
                                messages=messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                request_id=req_id,
                            ):
                                yield f_chunk
                            return

                if chunk.time_to_first_token_ms and first_token_time is None:
                    first_token_time = chunk.time_to_first_token_ms

                chunks_yielded += 1
                yield chunk

        except Exception as e:
            has_error = True
            yield StreamChunk(
                id=req_id,
                model=model_id,
                provider=adapter.provider_name,
                delta=StreamDelta(),
                error=f"Internal gateway streaming error: {str(e)}"
            )

        finally:
            total_duration_ms = (time.perf_counter() - start_time) * 1000
            metrics_service.record_request(
                provider=adapter.provider_name,
                latency_ms=total_duration_ms,
                ttft_ms=first_token_time,
                success=not has_error
            )

router_service = RouterService()
