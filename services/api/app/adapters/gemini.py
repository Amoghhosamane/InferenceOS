import time
import json
import httpx
from typing import AsyncGenerator, List
from app.adapters.base import BaseProviderAdapter
from app.schemas.chat import ChatMessage, StreamChunk, StreamDelta
from app.config import settings

class GeminiAdapter(BaseProviderAdapter):
    provider_name: str = "gemini"
    # Official Google Gemini REST streaming endpoint using x-goog-api-key header for security
    BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse"

    def is_configured(self) -> bool:
        return bool(settings.GEMINI_API_KEY.strip())

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
                error="Google Gemini API key is not configured in backend environment."
            )
            return

        actual_model = model_id.split("/", 1)[-1] if "/" in model_id else model_id
        url = self.BASE_URL.format(model=actual_model)

        # Transform normalized messages to Gemini contents structure
        contents = []
        for m in messages:
            role = "user" if m.role in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": m.content}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.GEMINI_API_KEY,
        }

        start_time = time.perf_counter()
        first_token = True

        try:
            async with httpx.AsyncClient(timeout=settings.DEFAULT_TIMEOUT_SECONDS) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code == 429:
                        yield StreamChunk(
                            id=request_id,
                            model=model_id,
                            provider=self.provider_name,
                            delta=StreamDelta(),
                            error="Gemini Free Tier Quota / Rate Limit reached (HTTP 429)."
                        )
                        return
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield StreamChunk(
                            id=request_id,
                            model=model_id,
                            provider=self.provider_name,
                            delta=StreamDelta(),
                            error=f"Gemini API error ({response.status_code}): {error_body.decode('utf-8', 'ignore')}"
                        )
                        return

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        try:
                            data = json.loads(data_str)
                            candidates = data.get("candidates", [])
                            if not candidates:
                                continue
                            parts = candidates[0].get("content", {}).get("parts", [])
                            delta_text = "".join(p.get("text", "") for p in parts)
                            finish_reason = candidates[0].get("finishReason")

                            ttft = None
                            if first_token and delta_text:
                                ttft = (time.perf_counter() - start_time) * 1000
                                first_token = False

                            usage_meta = data.get("usageMetadata", {})
                            usage = {
                                "prompt_tokens": usage_meta.get("promptTokenCount", 0),
                                "completion_tokens": usage_meta.get("candidatesTokenCount", 0),
                                "total_tokens": usage_meta.get("totalTokenCount", 0)
                            } if usage_meta else None

                            yield StreamChunk(
                                id=request_id,
                                model=model_id,
                                provider=self.provider_name,
                                delta=StreamDelta(content=delta_text, finish_reason=finish_reason),
                                time_to_first_token_ms=ttft,
                                usage=usage
                            )
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException:
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error="Gemini request timed out."
            )
        except Exception as e:
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error=f"Gemini network or adapter exception: {str(e)}"
            )
