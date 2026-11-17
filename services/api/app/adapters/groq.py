import time
import json
import httpx
from typing import AsyncGenerator, List
from app.adapters.base import BaseProviderAdapter
from app.schemas.chat import ChatMessage, StreamChunk, StreamDelta
from app.config import settings

class GroqAdapter(BaseProviderAdapter):
    provider_name: str = "groq"
    BASE_URL: str = "https://api.groq.com/openai/v1/chat/completions"

    def is_configured(self) -> bool:
        return bool(settings.GROQ_API_KEY.strip())

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
                error="Groq API key is not configured in backend environment."
            )
            return

        # Strip provider prefix if present (e.g. "groq/llama-3.3-70b-versatile" -> "llama-3.3-70b-versatile")
        actual_model = model_id.split("/", 1)[-1] if "/" in model_id else model_id

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
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
                            error="Groq Rate limit exceeded (HTTP 429). Please wait before retrying."
                        )
                        return
                    if response.status_code != 200:
                        error_body = await response.aread()
                        yield StreamChunk(
                            id=request_id,
                            model=model_id,
                            provider=self.provider_name,
                            delta=StreamDelta(),
                            error=f"Groq API error (status {response.status_code}): {error_body.decode('utf-8', 'ignore')}"
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
                error="Groq request timed out."
            )
        except Exception as e:
            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider=self.provider_name,
                delta=StreamDelta(),
                error=f"Groq network or adapter exception: {str(e)}"
            )
