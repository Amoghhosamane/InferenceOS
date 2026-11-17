import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "InferenceOS"
    API_V1_STR: str = "/api/v1"
    
    # Operational modes
    MOCK_MODE: bool = True
    FREE_MODE_ONLY: bool = True
    
    # Provider Keys (kept strictly on server)
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    INCEPTION_API_KEY: str = ""
    VLLM_BASE_URL: str = "http://localhost:8001/v1"
    VLLM_API_KEY: str = ""
    
    # Database URL: Supports PostgreSQL (postgresql+asyncpg://...) or SQLite (sqlite+aiosqlite://...)
    DATABASE_URL: str = "sqlite+aiosqlite:///./inferenceos.db"
    
    # Redis configuration for caching and distributed token-bucket rate limiting
    REDIS_URL: str = ""
    ENABLE_REDIS_CACHE: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]
    
    # Rate limits and timeouts
    DEFAULT_TIMEOUT_SECONDS: float = 30.0
    MAX_TOKENS_DEFAULT: int = 1024
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
