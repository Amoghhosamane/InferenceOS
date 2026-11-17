# InferenceOS Architecture & Engineering Design

## 1. System Overview
**InferenceOS** is a free-tier-first, unified multi-model AI gateway and developer platform designed for low-latency streaming, resilient error recovery, side-by-side model comparison, and strict billing safety.

```
                    ┌───────────────────────────────────────────┐
                    │     InferenceOS Web Client (Next.js)      │
                    │   - Gemini-inspired Spacious Minimal UI   │
                    │   - Collapsible History Sidebar           │
                    │   - SSE Streaming Client & Stop Control   │
                    │   - Multi-Model Comparison Engine         │
                    └─────────────────────┬─────────────────────┘
                                          │
                                          ▼  SSE / HTTP Requests
                    ┌───────────────────────────────────────────┐
                    │      FastAPI Gateway (Port 8000)          │
                    │   - Strict Free-Tier Model Allowlist      │
                    │   - Intelligent Provider Routing          │
                    │   - Fallback Engine (Zero-Cost Models)    │
                    │   - Per-request Observability & Metrics   │
                    │   - SQLite Persistence for Conversations  │
                    └──────┬──────────────┬──────────────┬──────┘
                           │              │              │
                           ▼              ▼              ▼
                    ┌────────────┐ ┌────────────┐ ┌─────────────┐
                    │    Groq    │ │Google Gemini││  OpenRouter │
                    │ Free Tier  │ │  Free Tier │ │:free Models │
                    └────────────┘ └────────────┘ └─────────────┘
                                          │
                                          ▼ (Optional Local Worker)
                                   ┌────────────┐
                                   │ Local vLLM │
                                   │ OpenAI-API │
                                   └────────────┘
```

## 2. Core Pillars

### 2.1 Billing Safeguards & Free-Tier First Policy
- **Strict Allowlisting:** Every model passed to `/api/v1/chat/stream` or `/api/v1/chat/compare` is validated against `VERIFIED_FREE_MODELS`. Unknown or paid models fail closed immediately (HTTP 400).
- **Backend-Only Secret Keys:** Third-party credentials (`GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`) remain strictly on the FastAPI server and are never delivered to client bundles.
- **Explicit Fallback Notification:** When fallback is triggered (e.g. on provider rate limit 429), it only transfers context to another verified zero-cost model and explicitly notifies the user inline in the stream.

### 2.2 Streaming & Cancellation Architecture
- Uses **Server-Sent Events (SSE)** via `sse-starlette` to stream individual chunks incrementally with microsecond-level telemetry.
- Records observed `time_to_first_token_ms` (TTFT) and total observed end-to-end latency without fabricating internal GPU metrics.
- Client maintains an `AbortController` enabling instant termination of incoming streams upon user request.

### 2.3 Resilient Persistence
- Conversations and message histories are persisted locally in SQLite (`aiosqlite`), with full CRUD support, deletion compliance, and zero heavy external infrastructure requirements.
