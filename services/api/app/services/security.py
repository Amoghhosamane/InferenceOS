import re

def sanitize_error_message(error_str: str) -> str:
    """Strip any potential API keys, auth headers, or raw URL query parameters from exception/error strings."""
    if not error_str:
        return ""
    # Mask common key formats if present in error strings
    # e.g., AIzaSy..., gsk_..., sk-or-v1-..., etc.
    sanitized = re.sub(r'AIzaSy[A-Za-z0-9_-]{30,}', '[REDACTED_GEMINI_KEY]', error_str)
    sanitized = re.sub(r'gsk_[A-Za-z0-9]{30,}', '[REDACTED_GROQ_KEY]', sanitized)
    sanitized = re.sub(r'sk-or-v1-[A-Za-z0-9]{30,}', '[REDACTED_OPENROUTER_KEY]', sanitized)
    sanitized = re.sub(r'Bearer\s+[A-Za-z0-9_.-]+', 'Bearer [REDACTED_TOKEN]', sanitized)
    sanitized = re.sub(r'key=[A-Za-z0-9_-]+', 'key=[REDACTED_KEY]', sanitized)
    return sanitized
