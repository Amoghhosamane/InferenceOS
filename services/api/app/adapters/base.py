from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List
from app.schemas.chat import ChatMessage, StreamChunk

class BaseProviderAdapter(ABC):
    provider_name: str

    @abstractmethod
    async def stream_chat(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        request_id: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        """Yield normalized StreamChunks from the provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if required API keys / base URLs are set."""
        pass
