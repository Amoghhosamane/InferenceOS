# InferenceOS

High-Performance Unified Multi-Model AI Gateway & Developer Platform

[![CI - Test & Quality Gates](https://github.com/Amoghhosamane/InferenceOS/actions/workflows/ci.yml/badge.svg)](https://github.com/Amoghhosamane/InferenceOS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Next.js: 15.1](https://img.shields.io/badge/Next.js-15.1-black)](https://nextjs.org/)

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
                                  |  - Security & Header Sanitization     |
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
           |                      |     Local SQLite Store       |
           |                      |  aiosqlite (Async CRUD)      |
           |                      |  Conversations & Messages    |
           |                      +------------------------------+
           v
+----------------------+
| Local vLLM Worker    |
| Port 8001 Isolation  |
| OpenAI API Spec      |
+----------------------+
```

---

## Software Development Life Cycle (SDLC) & Quality Gates

InferenceOS was designed and implemented adhering to production software engineering standards:

1. **Requirements Specification & Architecture Contract:** Governed strictly by root-level architectural and security guidelines defined in `AGENTS.md`.
2. **Defensive Security & Privacy-First Design:**
   - Credentials remain exclusively in server memory; zero API keys are bundled into client assets or repository commits.
   - All client responses and external errors are filtered through an automated redaction engine (`sanitize_error_message`) to eliminate credential leakage.
   - Enforced HTTP security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`).
3. **Automated Verification Gates:**
   - **Backend Unit & Integration Tests:** 18 automated test suites verifying model allowlists, SSE stream chunks, SQLite persistence, and credential redactors.
   - **Frontend Compilation & Strict Typing:** Zero TypeScript compiler warnings and clean ESLint verification (`npm run build`).
   - **Continuous Integration (CI):** GitHub Actions workflow executing full backend test matrix and frontend production builds on every push.
4. **Empirical Benchmarking:** Real performance measurements recorded over synthetic request profiles; no synthetic or fabricated GPU metrics.

---

## Technical Specifications & Stack

| Layer | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js 15.1, React 19, TypeScript | Gemini-inspired minimalist interface, light/dark themes, collapsible history drawer, auto-resizing composer, multi-model comparison view. |
| **Styling** | Tailwind CSS | Mobile-first responsive layout (375px, 768px, 1280px, 1920px), dynamic safe areas (`100dvh`), custom subtle scrollbars. |
| **Backend Gateway** | FastAPI, Python 3.13, Uvicorn | Async provider adapters, SSE streaming via `sse-starlette`, intelligent fallback routing, microsecond telemetry. |
| **Database** | PostgreSQL + SQLAlchemy (Async) | Production asynchronous ORM via `asyncpg` with zero-dependency `sqlite+aiosqlite` local fallback. |
| **Migrations** | Alembic | Version-controlled declarative schema migrations with autogeneration support. |
| **Cache & Rate Limiting** | Redis (`redis.asyncio`) | Distributed sliding-window token bucket rate limiter and response caching with automatic memory fallback. |
| **Model Registry** | Pydantic V2 | Strict allowlisting failing closed on unknown pricing or eligibility. |
| **CI/CD** | GitHub Actions | Automated multi-stage validation pipeline running pytest and Next.js static builds. |

---

## Supported AI Providers & Models

| Provider | Model Identifier | Free-Tier / Credit Status | Context Length | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Groq** | `groq/openai/gpt-oss-20b` | Verified Free | 131,072 | Mixture-of-Experts open model on Groq free tier |
| **Groq** | `groq/openai/gpt-oss-120b` | Verified Free | 131,072 | Large-scale reasoning open model on Groq free tier |
| **Groq** | `groq/qwen/qwen3.8-27b` | Verified Free | 131,072 | Alibaba flagship open-weights model hosted on Groq free tier |
| **Groq** | `groq/llama-3.3-70b-versatile` | Verified Free | 128,000 | Llama 3.3 70B model with high-speed LPU inference |
| **Groq** | `groq/llama-3.1-8b-instant` | Verified Free | 128,000 | Sub-second low latency Llama 3.1 8B endpoint |
| **Google Gemini** | `gemini/gemini-2.0-flash` | Verified Free | 1,048,576 | Google next-gen multimodal model on AI Studio free tier |
| **Google Gemini** | `gemini/gemini-1.5-flash` | Verified Free | 1,048,576 | Versatile high-efficiency Google model on AI Studio free tier |
| **Google Gemini** | `gemini/gemini-1.5-flash-8b` | Verified Free | 1,048,576 | High-throughput compact model on AI Studio free tier |
| **OpenRouter** | `openrouter/...:free` | Verified Free | 16k - 32k | Zero-cost OpenRouter endpoints; non-free models fail closed |
| **Inception Labs** | `inception/mercury-3` | Promotional Trial | 1,048,576 | High-speed diffusion LLM (dLLM) on trial credits |
| **Inception Labs** | `inception/mercury-voice` | Promotional Trial | 32,768 | Conversational low-latency diffusion model |
| **vLLM** | `vllm/local-model` | Self-Hosted | 8,192 | OpenAI-compatible endpoint isolated on port 8001 |

---

## Empirical Performance Benchmarks

Performance was evaluated using the automated latency profiling harness (`services/api/benchmark.py`) under concurrent load against the local streaming endpoint.

### Benchmark Setup
- **Workload:** 20 batch requests
- **Concurrency:** 5 concurrent client streams
- **Protocol:** HTTP/1.1 Server-Sent Events (SSE)
- **Environment:** Windows 11 x64, Python 3.13.7, Local Loopback (127.0.0.1:8000)

### Empirical Results

| Metric | Measured Value | Unit |
| :--- | :--- | :--- |
| **Completed Requests** | 20 / 20 | requests |
| **Success Rate** | 100.0% | % |
| **Request Failures / Errors** | 0 | errors |
| **Time to First Token (TTFT) p50** | 44.48 | milliseconds |
| **End-to-End Latency (p50)** | 341.26 | milliseconds |
| **End-to-End Latency (p95)** | 369.15 | milliseconds |

Complete reproduction commands and methodology are documented in [docs/BENCHMARKS.md](docs/BENCHMARKS.md).

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Amoghhosamane/InferenceOS.git
cd InferenceOS
```

### 2. Configure Environment
```bash
cp .env.example .env
```
By default, `MOCK_MODE=true` is enabled. You can run and test the complete application offline without configuring third-party credentials.

To enable live providers, configure your keys in `.env`:
```env
MOCK_MODE=false
FREE_MODE_ONLY=true

GROQ_API_KEY
GEMINI_API_KEY
OPENROUTER_API_KEY
INCEPTION_API_KEY
VLLM_BASE_URL=http://localhost:8001/v1
```

### 3. Start Backend Gateway (FastAPI)
```powershell
# Install backend dependencies
python -m pip install -r services/api/requirements.txt

# Start FastAPI server on port 8000
$env:PYTHONPATH="services/api"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation is accessible at `http://127.0.0.1:8000/docs`.

### 4. Start Web Application (Next.js)
```powershell
cd apps/web
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Verification & Testing Commands

### Backend Automated Test Suite
```powershell
$env:PYTHONPATH="services/api"
python -m pytest services/api/tests -v
```

### Frontend Production Build & Typecheck
```powershell
cd apps/web
npm run build
```

### Performance Benchmark Profiling
```powershell
$env:PYTHONPATH="services/api"
python services/api/benchmark.py
```

---

## Technical Documentation & Reports

- [AGENTS.md](AGENTS.md) — Engineering priorities, provider safety policies, and design rules.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Architectural diagrams, data flows, and security decisions.
- [docs/BENCHMARKS.md](docs/BENCHMARKS.md) — Benchmark methodology, statistical parameters, and reproduction guide.
- [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md) — Comprehensive engineering report with verified outcome statements.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
