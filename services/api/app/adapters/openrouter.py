import time
import json
import httpx
from typing import AsyncGenerator, List
from app.adapters.base import BaseProviderAdapter
from app.schemas.chat import ChatMessage, StreamChunk, StreamDelta
from app.config import settings

class OpenRouterAdapter(BaseProviderAdapter):
    provider_name: str = "openrouter"
    BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(settings.OPENROUTER_API_KEY.strip())

    async def stream_chat(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        request_id: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        if not self.is_configured():
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error="OpenRouter API key is not configured in backend environment."
            )
            return

        # Strip prefix e.g. "openrouter/meta-llama/llama-3.3-70b-instruct:free" -> "meta-llama/llama-3.3-70b-instruct:free"
        actual_model = model_id.split("/", 1)[-1] if model_id.startswith("openrouter/") else model_id

        # STRICT FREE SAFEGUARD: OpenRouter free models must contain ':free' or 'openrouter/free'
        if settings.FREE_MODE_ONLY and (":free" not in actual_model and actual_model != "openrouter/free"):
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error=f"Model {actual_model} rejected: Free-mode-only enforcement requires explicit ':free' suffix."
            )
            return

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "InferenceOS Gateway",
            "Content-Type": "application/json",
        }
        payload = {
            "model": actual_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        start_time = time.perf_counter()
        first_token = True

        try:
            async with httpx.AsyncClient(timeout=settings.DEFAULT_TIMEOUT_SECONDS) as client:
                async with client.stream("POST", self.BASE_URL, headers=headers, json=payload) as response:
                    if response.status_code == 429:
                        yield StreamChunk(
                            id=request_id,
                            model=model_id,
                            provider=self.provider_name,
                            delta=StreamDelta(),
                            error="OpenRouter rate limit or upstream provider quota reached (HTTP 429)."
                        )
                        return
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield StreamChunk(
                            id=request_id,
                            model=model_id,
                            provider=self.provider_name,
                            delta=StreamDelta(),
                            error=f"OpenRouter API error ({response.status_code}): {error_body.decode('utf-8', 'ignore')}"
                        )
                        return

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])
                            if not choices:
                                continue
                            delta_content = choices[0].get("delta", {}).get("content", "")
                            finish_reason = choices[0].get("finish_reason")

                            ttft = None
                            if first_token and delta_content:
                                ttft = (time.perf_counter() - start_time) * 1000
                                first_token = False

                            yield StreamChunk(
                                id=request_id,
                                model=model_id,
                                provider=self.provider_name,
                                delta=StreamDelta(content=delta_content, finish_reason=finish_reason),
                                time_to_first_token_ms=ttft,
                                usage=data.get("usage")
                            )
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException:
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error="OpenRouter request timed out."
            )
        except Exception as e:
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error=f"OpenRouter network or adapter exception: {str(e)}"
            )
