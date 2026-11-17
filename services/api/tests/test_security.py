import pytest
from app.services.security import sanitize_error_message

def test_sanitize_gemini_key():
    raw_error = "Error from Gemini: AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q failed"
    sanitized = sanitize_error_message(raw_error)
    assert "AIzaSy" not in sanitized
    assert "[REDACTED_GEMINI_KEY]" in sanitized

def test_sanitize_groq_key():
    raw_error = "Groq exception with key gsk_abcdef1234567890abcdef1234567890"
    sanitized = sanitize_error_message(raw_error)
    assert "gsk_" not in sanitized
    assert "[REDACTED_GROQ_KEY]" in sanitized

def test_sanitize_bearer_token():
    raw_error = "Authentication failed for header Authorization: Bearer secret_token_xyz.123"
    sanitized = sanitize_error_message(raw_error)
    assert "secret_token_xyz" not in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized
