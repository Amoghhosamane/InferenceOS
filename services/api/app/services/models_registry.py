from typing import Dict
from app.schemas.chat import ModelMetadata

# Strict allowlist of verified free-tier and promotional-trial models.
# Unknown or paid models must NEVER be routed to.
VERIFIED_FREE_MODELS: Dict[str, ModelMetadata] = {
    # Deterministic Mock Provider (for offline development & testing)
    "mock-gpt-oss": ModelMetadata(
        id="mock-gpt-oss",
        name="Mock Deterministic OSS",
        provider="mock",
        free_tier=True,
        context_length=8192,
        description="Deterministic local mock model for zero-cost testing and validation.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "mock-fast-chat": ModelMetadata(
        id="mock-fast-chat",
        name="Mock Ultra-Fast Streamer",
        provider="mock",
        free_tier=True,
        context_length=4096,
        description="Low-latency simulated stream for responsive UI and comparison tests.",
        is_available=True,
        pricing_status="verified_free"
    ),

    # Groq Free Tier Models: GPT-OSS and Qwen models on eligible free tier
    "groq/openai/gpt-oss-20b": ModelMetadata(
        id="groq/openai/gpt-oss-20b",
        name="Groq OpenAI GPT-OSS 20B",
        provider="groq",
        free_tier=True,
        context_length=131072,
        description="High-throughput open-weight Mixture-of-Experts model on Groq free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "groq/openai/gpt-oss-120b": ModelMetadata(
        id="groq/openai/gpt-oss-120b",
        name="Groq OpenAI GPT-OSS 120B",
        provider="groq",
        free_tier=True,
        context_length=131072,
        description="Large-scale reasoning open model on Groq Cloud free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "groq/qwen/qwen3.8-27b": ModelMetadata(
        id="groq/qwen/qwen3.8-27b",
        name="Groq Qwen 3.8 27B",
        provider="groq",
        free_tier=True,
        context_length=131072,
        description="Alibaba flagship open-weights model hosted on Groq free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "groq/llama-3.3-70b-versatile": ModelMetadata(
        id="groq/llama-3.3-70b-versatile",
        name="Llama 3.3 70B Versatile",
        provider="groq",
        free_tier=True,
        context_length=128000,
        description="Groq-accelerated flagship Llama 3.3 model on Groq Cloud free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "groq/llama-3.1-8b-instant": ModelMetadata(
        id="groq/llama-3.1-8b-instant",
        name="Llama 3.1 8B Instant",
        provider="groq",
        free_tier=True,
        context_length=128000,
        description="Sub-second low latency Llama 3.1 8B model on Groq Cloud free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),

    # Google Gemini Free Tier Models (via Google AI Studio)
    "gemini/gemini-2.0-flash": ModelMetadata(
        id="gemini/gemini-2.0-flash",
        name="Gemini 2.0 Flash",
        provider="gemini",
        free_tier=True,
        context_length=1048576,
        description="Google next-gen multimodal model with 1M context on AI Studio free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "gemini/gemini-1.5-flash": ModelMetadata(
        id="gemini/gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        provider="gemini",
        free_tier=True,
        context_length=1048576,
        description="Fast, versatile high-efficiency Google model on AI Studio free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "gemini/gemini-1.5-flash-8b": ModelMetadata(
        id="gemini/gemini-1.5-flash-8b",
        name="Gemini 1.5 Flash 8B",
        provider="gemini",
        free_tier=True,
        context_length=1048576,
        description="High-throughput compact model on Google AI Studio free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),

    # OpenRouter Verified Free Models (:free suffix strictly enforced)
    "openrouter/google/gemini-2.0-flash-exp:free": ModelMetadata(
        id="openrouter/google/gemini-2.0-flash-exp:free",
        name="Gemini 2.0 Flash Exp (Free)",
        provider="openrouter",
        free_tier=True,
        context_length=32768,
        description="Verified zero-cost OpenRouter free endpoint.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "openrouter/meta-llama/llama-3.3-70b-instruct:free": ModelMetadata(
        id="openrouter/meta-llama/llama-3.3-70b-instruct:free",
        name="Llama 3.3 70B Instruct (Free)",
        provider="openrouter",
        free_tier=True,
        context_length=32768,
        description="Verified zero-cost OpenRouter free endpoint for Llama 3.3 70B.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "openrouter/meta-llama/llama-3.1-8b-instruct:free": ModelMetadata(
        id="openrouter/meta-llama/llama-3.1-8b-instruct:free",
        name="Llama 3.1 8B Instruct (Free)",
        provider="openrouter",
        free_tier=True,
        context_length=16384,
        description="Verified zero-cost OpenRouter free endpoint for Llama 3.1 8B.",
        is_available=True,
        pricing_status="verified_free"
    ),
    "openrouter/qwen/qwen-2.5-coder-32b-instruct:free": ModelMetadata(
        id="openrouter/qwen/qwen-2.5-coder-32b-instruct:free",
        name="Qwen 2.5 Coder 32B (Free)",
        provider="openrouter",
        free_tier=True,
        context_length=32768,
        description="Specialized code reasoning open-weights model on OpenRouter free tier.",
        is_available=True,
        pricing_status="verified_free"
    ),

    # Inception Labs Mercury API (Promotional Trial Credits)
    "inception/mercury-3": ModelMetadata(
        id="inception/mercury-3",
        name="Inception Mercury 3",
        provider="inception",
        free_tier=True,
        context_length=1048576,
        description="High-speed diffusion LLM (dLLM) powered by Inception promotional trial credits.",
        is_available=True,
        pricing_status="promotional_trial"
    ),
    "inception/mercury-voice": ModelMetadata(
        id="inception/mercury-voice",
        name="Inception Mercury Voice",
        provider="inception",
        free_tier=True,
        context_length=32768,
        description="Ultra-low latency conversational diffusion model on promotional trial credits.",
        is_available=True,
        pricing_status="promotional_trial"
    ),

    # Optional local vLLM adapter (configured on dedicated port 8001)
    "vllm/local-model": ModelMetadata(
        id="vllm/local-model",
        name="Local vLLM Worker (Port 8001)",
        provider="vllm",
        free_tier=True,
        context_length=8192,
        description="Self-hosted local OpenAI-compatible inference worker (Phase 2).",
        is_available=False,
        pricing_status="verified_free"
    ),
}

def is_model_free_eligible(model_id: str) -> bool:
    """Verifies that model_id exists in our strict allowlist and is verified_free or promotional_trial."""
    if model_id in VERIFIED_FREE_MODELS:
        status = VERIFIED_FREE_MODELS[model_id].pricing_status
        return status in ["verified_free", "promotional_trial"]
    return False
