import pytest
from app.services.models_registry import VERIFIED_FREE_MODELS, is_model_free_eligible
from app.schemas.chat import ModelMetadata

def test_mock_models_free_eligible():
    assert is_model_free_eligible("mock-gpt-oss") is True
    assert is_model_free_eligible("mock-fast-chat") is True

def test_groq_gpt_oss_and_qwen_free_eligible():
    # Verify GPT-OSS models on Groq
    assert is_model_free_eligible("groq/openai/gpt-oss-20b") is True
    assert is_model_free_eligible("groq/openai/gpt-oss-120b") is True
    # Verify Qwen on Groq
    assert is_model_free_eligible("groq/qwen/qwen3.8-27b") is True
    # Verify existing Groq Llama models
    assert is_model_free_eligible("groq/llama-3.3-70b-versatile") is True
    assert is_model_free_eligible("groq/llama-3.1-8b-instant") is True

def test_gemini_models_free_eligible():
    assert is_model_free_eligible("gemini/gemini-2.0-flash") is True
    assert is_model_free_eligible("gemini/gemini-1.5-flash") is True
    assert is_model_free_eligible("gemini/gemini-1.5-flash-8b") is True

def test_openrouter_free_strict_allowlist():
    # Only :free suffix models should be verified free
    assert is_model_free_eligible("openrouter/meta-llama/llama-3.3-70b-instruct:free") is True
    assert is_model_free_eligible("openrouter/qwen/qwen-2.5-coder-32b-instruct:free") is True
    # Non-free or non-allowlisted models must be rejected
    assert is_model_free_eligible("openrouter/openai/gpt-4o") is False
    assert is_model_free_eligible("anthropic/claude-3-5-sonnet") is False

def test_inception_mercury_promotional_trial():
    # Verify Inception Labs Mercury models are allowlisted under promotional_trial status
    assert is_model_free_eligible("inception/mercury-3") is True
    assert is_model_free_eligible("inception/mercury-voice") is True
    assert VERIFIED_FREE_MODELS["inception/mercury-3"].pricing_status == "promotional_trial"

def test_vllm_local_model_port():
    # Verify vLLM exists and port conflict with FastAPI 8000 is resolved
    assert is_model_free_eligible("vllm/local-model") is True

def test_unknown_models_fail_closed():
    assert is_model_free_eligible("unknown-model-id") is False
    assert is_model_free_eligible("gpt-4-turbo") is False
    assert is_model_free_eligible("claude-instant-1") is False
