import asyncio
import time
from typing import AsyncGenerator, List
from app.adapters.base import BaseProviderAdapter
from app.schemas.chat import ChatMessage, StreamChunk, StreamDelta

class MockAdapter(BaseProviderAdapter):
    provider_name: str = "mock"

    def is_configured(self) -> bool:
        return True

    async def stream_chat(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        request_id: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        last_message = messages[-1].content if messages else "Hello"
        
        # Craft a deterministic, clearly labeled mock response
        prefix = f"[MOCK MODE — {model_id}] "
        canned_sentences = [
            prefix,
            f"Received your prompt: \"{last_message[:60]}...\" ",
            "\n\nInferenceOS is operating in zero-cost deterministic mock mode. ",
            "This simulated stream confirms that backend SSE streaming, ",
            "client connection lifecycle, latency measurement, and cancellation ",
            "operate correctly without requiring paid or third-party API credentials.",
            "\n\n- Stream status: Active & Verified",
            "\n- Model ID: " + model_id,
            "\n- Request ID: " + request_id,
            "\n\nFinished streaming simulated response."
        ]

        start_time = time.perf_counter()
        first_token = True

        for i, sentence in enumerate(canned_sentences):
            # Simulate realistic network chunk arrival (20-40ms per chunk)
            await asyncio.sleep(0.03)
            
            ttft = None
            if first_token:
                ttft = (time.perf_counter() - start_time) * 1000
                first_token = False

            yield StreamChunk(
                id=request_id,
                model=model_id,
                provider="mock",
                delta=StreamDelta(content=sentence),
                time_to_first_token_ms=ttft
            )

        # Final chunk with usage stats
        yield StreamChunk(
            id=request_id,
            model=model_id,
            provider="mock",
            delta=StreamDelta(finish_reason="stop"),
            usage={
                "prompt_tokens": len(last_message.split()),
                "completion_tokens": sum(len(s.split()) for s in canned_sentences),
                "total_tokens": len(last_message.split()) + sum(len(s.split()) for s in canned_sentences)
            }
        )
