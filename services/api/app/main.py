from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.config import settings
from app.routers.api import api_router
from app.services.db import init_db
from app.services.redis_manager import redis_service

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite/PostgreSQL schema
    await init_db()
    # Initialize shared Redis connection pool
    await redis_service.initialize()
    yield
    # Gracefully disconnect Redis
    await redis_service.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="InferenceOS: Free-Tier Unified Multi-Model Gateway & Developer Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration with dynamic FRONTEND_URL support
allowed_origins = list(settings.CORS_ORIGINS)
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app" if not any("*" in o for o in allowed_origins) else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "platform": "InferenceOS",
        "status": "online",
        "mock_mode": settings.MOCK_MODE,
        "free_mode_only": settings.FREE_MODE_ONLY,
        "docs_url": "/docs"
    }
