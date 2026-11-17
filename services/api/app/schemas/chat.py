from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ModelMetadata(BaseModel):
    id: str
    name: str
    provider: Literal["groq", "gemini", "openrouter", "inception", "vllm", "mock"]
    free_tier: bool = True
    context_length: int = 8192
    description: str
    is_available: bool = True
    pricing_status: Literal["verified_free", "promotional_trial", "unknown", "paid"] = "verified_free"

class ModelListResponse(BaseModel):
    models: List[ModelMetadata]
    mock_mode: bool
    free_mode_only: bool

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    stream: bool = True
    allow_fallback: bool = False

class CompareRequest(BaseModel):
    models: List[str]
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

class StreamDelta(BaseModel):
    content: Optional[str] = None
    finish_reason: Optional[str] = None

class StreamChunk(BaseModel):
    id: str
    model: str
    provider: str
    delta: StreamDelta
    usage: Optional[Dict[str, int]] = None
    time_to_first_token_ms: Optional[float] = None
    error: Optional[str] = None
    fallback_used: Optional[bool] = False
    original_model: Optional[str] = None

class MetricSummary(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    p50_latency_ms: float
    p95_latency_ms: float
    p50_ttft_ms: float
    provider_breakdown: Dict[str, Dict[str, Any]]
    active_mock_mode: bool
    sample_size: int
    timeframe: str = "all-time"
