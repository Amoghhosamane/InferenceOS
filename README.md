# InferenceOS

High-Performance Unified Multi-Model AI Gateway & Developer Platform

[![CI - Test & Quality Gates](https://github.com/Amoghhosamane/InferenceOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Amoghhosamane/InferenceOS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Next.js: 15.1](https://img.shields.io/badge/Next.js-15.1-black)](https://nextjs.org/)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20SQLAlchemy%202.x-336791)](https://www.postgresql.org/)
[![Cache: Redis](https://img.shields.io/badge/Cache-Redis-DC382D)](https://redis.io/)

---

## Executive Summary

InferenceOS is an enterprise-grade AI model gateway and developer orchestration platform engineered with a strict free-tier-first philosophy. It unifies disparate large language model providers—including Groq (OpenAI GPT-OSS and Qwen open-weights), Google Gemini (AI Studio), OpenRouter (strictly verified `:free` endpoints), Inception Labs Mercury (diffusion LLMs via promotional trial credits), and self-hosted vLLM workers—behind a unified, low-latency Server-Sent Events (SSE) streaming API and a minimalist, Gemini-inspired web interface.

The system incorporates fail-closed billing safeguards, intelligent heuristic routing with zero-cost fallback, client-side stream abort controls, end-to-end request telemetry (p50/p95 latency and Time-to-First-Token tracking without simulated GPU telemetry), and asynchronous local persistence.

---

## System Architecture

```
                                  +---------------------------------------+
                                  |     InferenceOS Web Client            |
                                  |   Next.js 15 (App Router), React,     |
                                  |   TypeScript, Tailwind CSS, Lucide    |
                                  |   Deployed on Vercel                  |
                                  +-------------------+-------------------+
                                                      |
                                                      | SSE / JSON REST
                                                      v
                                  +---------------------------------------+
                                  |       InferenceOS API Gateway         |
                                  |     FastAPI, Python 3.13, Pydantic    |
                                  |  - Strict Model Allowlist Guardrail   |
                                  |  - Fail-Closed Billing Protection     |
                                  |  - Asynchronous SSE Stream Engine     |
                                  |  - Deployed on Render                 |
                                  +----+-----------+-----------+----+-----+
                                       |           |           |    |
           +---------------------------+           |           |    +---------------------------+
           |                                       |           |                                |
           v                                       v           v                                v
+----------------------+              +----------------------+ +--------------------+ +----------------------+
|     Groq Adapter     |              |    Gemini Adapter    | | OpenRouter Adapter | |  Inception Adapter   |
| openai/gpt-oss-20b   |              | gemini-2.0-flash     | | meta-llama/:free   | | mercury-3 (dLLM)     |
| openai/gpt-oss-120b  |              | gemini-1.5-flash     | | qwen-2.5-coder/:free| | mercury-voice         |
| qwen/qwen3.8-27b     |              | gemini-1.5-flash-8b  | | (strictly :free)   | | (trial credits only) |
| llama-3.3-70b        |              +----------------------+ +--------------------+ +----------------------+
+----------------------+                         |
           |                                     v
           |                      +------------------------------+
           |                      |  PostgreSQL / SQLAlchemy     |
           |                      |  Asyncpg + Alembic Migrations|
           |                      |  Conversations & Messages    |
           |                      +------------------------------+
           |                                     |
           |                                     v
           |                      +------------------------------+
           |                      |  Redis (aioredis)            |
           |                      |  Sliding Window Rate Limiter |
           |                      +------------------------------+
           v
+----------------------+
| Local vLLM Worker    |
| Port 8001 Isolation  |
| OpenAI API Spec      |
+----------------------+
```

---

## Production Deployment Guide (Vercel + Render)

InferenceOS is architected for zero-friction cloud deployment separating static frontend assets on Vercel from the containerized FastAPI backend, PostgreSQL database, and Redis cache on Render.

### 1. Render Deployment (Backend API, PostgreSQL & Redis)

You can deploy the complete backend stack on Render using the included Infrastructure-as-Code blueprint [`render.yaml`](render.yaml):

1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Select **New +** -> **Blueprint**.
3. Connect your repository `https://github.com/Amoghhosamane/InferenceOS`.
4. Render will automatically parse `render.yaml` and provision:
   - **`inferenceos-api`** (FastAPI Web Service)
   - **`inferenceos-db`** (Managed PostgreSQL Database)
   - **`inferenceos-redis`** (Managed Redis Cache)
5. **Render Build Command:**
   ```bash
   cd services/api && pip install -r requirements.txt && alembic upgrade head
   ```
6. **Render Start Command:**
   ```bash
   cd services/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
7. Configure the following environment variables in the Render dashboard:
   - `FRONTEND_URL`: `https://<your-vercel-app>.vercel.app`
   - `MOCK_MODE`: `true` (or `false` when using live provider keys)
   - `FREE_MODE_ONLY`: `true`
   - `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `INCEPTION_API_KEY` (Optional)

---

### 2. Vercel Deployment (Frontend Web Client)

1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project** and import `Amoghhosamane/InferenceOS`.
3. In project configuration:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Edit and select `apps/web`
4. In **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: `https://inferenceos-api.onrender.com` (Your Render Web Service URL)
   - `NEXT_PUBLIC_DEFAULT_MOCK_MODE`: `true`
5. Click **Deploy**. Vercel will build the optimized production package.

---

## Environment Variable Reference

| Variable Name | Required Service | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Vercel (Frontend) | `https://inferenceos-api.onrender.com` | Base URL of deployed Render backend gateway |
| `DATABASE_URL` | Render (Backend) | `postgresql+asyncpg://user:pass@host:5432/db` | PostgreSQL async connection string (or local SQLite) |
| `REDIS_URL` | Render (Backend) | `redis://red-xxx:6379` | Redis instance URL for sliding window rate limiting |
| `FRONTEND_URL` | Render (Backend) | `https://inferenceos.vercel.app` | Production domain used to configure CORS origins |
| `MOCK_MODE` | Render (Backend) | `true` | When true, provides deterministic zero-cost responses |
| `FREE_MODE_ONLY` | Render (Backend) | `true` | Strictly blocks unverified or paid models (HTTP 400) |
| `GROQ_API_KEY` | Render (Backend) | `gsk_...` | Groq Cloud free-tier API credential |
| `GEMINI_API_KEY` | Render (Backend) | `AIzaSy...` | Google AI Studio free-tier API credential |
| `OPENROUTER_API_KEY` | Render (Backend) | `sk-or-v1-...` | OpenRouter free model API credential |
| `INCEPTION_API_KEY` | Render (Backend) | `...` | Inception Labs Mercury promotional trial key |
| `VLLM_BASE_URL` | Render (Backend) | `http://localhost:8001/v1` | Optional OpenAI-compatible local vLLM endpoint |

---

## Local Development Instructions

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js 18+ and npm

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Run Backend Gateway
```powershell
python -m pip install -r services/api/requirements.txt
cd services/api
alembic upgrade head
$env:PYTHONPATH="."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation: `http://127.0.0.1:8000/docs`
Health Check: `GET http://127.0.0.1:8000/api/v1/health`
Readiness Probe: `GET http://127.0.0.1:8000/api/v1/ready`

### 4. Run Frontend Client
```powershell
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Testing & Quality Verification

```powershell
# Run backend test suite (21 passing tests)
$env:PYTHONPATH="services/api"
python -m pytest services/api/tests -v

# Run production frontend build
cd apps/web
npm run build

# Run latency benchmark harness
python services/api/benchmark.py
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
