AGENTS.md — InferenceOS Engineering & Design Rules
Read this file before inspecting, writing, or refactoring code. Follow the closest AGENTS.md when working in subdirectories. Keep this document updated when project conventions change.

Product
InferenceOS is a free-tier-first, multi-model AI chat and developer API platform. It unifies Groq (GPT-OSS and Qwen free models), Google Gemini, OpenRouter (:free only), Inception Labs Mercury (promotional trial credits), and local vLLM workers (on port 8001) behind a reliable backend. Inception Labs Mercury promotional credits are recognized as temporary trial tokens, not permanent free tiers. Do not misrepresent hosted API aggregation as self-hosted LLM inference infrastructure.
Engineering priorities (in order)
1. Security, correct provider behavior, and zero unintended paid usage.
2. Working end-to-end features, graceful failure, and trustworthy data.
3. Fast, accessible, responsive Gemini-inspired UX.
4. Testability, clear architecture, maintainability, and observability.
5. Measured performance optimization, not speculative claims.
Frontend design system — Gemini-inspired, original implementation
- Build an original visual language inspired by the calm, spacious, minimalist interaction principles of Google Gemini. Do not copy logos, branding, proprietary illustrations, or pixel-identical UI.
- Use Next.js, TypeScript, Tailwind CSS, shadcn/ui primitives, and Lucide icons where appropriate. Reuse existing project tools if already installed.
- Prefer clean white or near-white backgrounds, subtle borders, generous whitespace, restrained accents, and readable typography. Support light and dark themes.
- Suggested light tokens: background #F8FAFC, surface #FFFFFF, foreground #202124, muted #667085, border #E5E7EB, accent #2563EB. These are starting points, not a mandate to create unnecessary gradients.
- Layout: collapsible conversation history sidebar; centered chat content; discreet header/model selector; readable messages; anchored multiline composer; comparison mode with side-by-side panels that stack vertically on mobile.
- Responsive target widths: 375px, 768px, 1280px, 1920px. Use dynamic viewport units (100dvh) and safe areas; avoid horizontal overflow and keyboard-obscured composer.
- Make hover, focus, disabled, loading, empty, streaming, cancellation, error, quota and fallback states clear. Honor prefers-reduced-motion. Use accessible contrast and keyboard navigation; label every interactive control.
- Use subtle transitions only; avoid flashy animations, neon palettes, glassmorphism, excessive shadows, giant gradients, and crowded dashboards.
- No fake buttons, dead links, placeholder charts without labels, or static data presented as live telemetry.
Backend architecture and safety
- Frontend must never call external model providers with secret keys. Make all provider calls through FastAPI.
- Implement per-provider adapters for Groq, Gemini, and OpenRouter with normalized message input, provider model IDs, chunk streaming, cancellation, error mapping, retry rules, and usage accounting. Do not assume providers expose identical metadata.
- Enable only explicitly configured, provider-verified free-tier models. Unknown price/free status means disabled by default. For OpenRouter, require free-model IDs or explicitly verified openrouter/free; never silently route to a paid model.
- Free-tier usage is subject to quota and terms, and no code can guarantee a zero bill if an account has billing enabled. Never promise guaranteed zero charges; provide configuration safeguards, warnings, and clear instructions.
- No API keys in browser bundles, committed files, logs, screenshots, exceptions, or telemetry. Use .env.example with placeholders and gitignore .env* files while permitting .env.example.
- Use per-user/server-side rate limiting, bounded request queues, timeout handling, exponential backoff for safe retries, circuit breakers, and clear 429/5xx messages. Never retry non-idempotent operations blindly.
- Model fallback must select only an allowed free model, preserve context when compatible, inform users when provider/model changed, and be configurable/off by default when transparency is required.
- Store minimal metadata by default. Do not log full chat content, authorization headers, or private data. Provide conversation deletion and documented retention if persistence is implemented.
- Use parameterized database operations, explicit authorization, safe CORS, validated request sizes, and sanitization of rendered Markdown.
Performance and measurement
- For hosted APIs, record observed end-to-end latency, backend time-to-first-streamed-content, per-request duration, responses, errors and usage tokens when supplied. Do not label hosted-provider telemetry as GPU utilization or internal GPU TTFT.
- For self-hosted GPUs in Phase 2, use actual hardware instrumentation (for example NVIDIA exporter, DCGM or validated GPU metrics). Label all simulations and mocks unmistakably.
- Provide provider/model-level p50/p95 latency, error rate, request throughput and quota/fallback status, with sample size and timeframe.
- Use SSE or a well-tested equivalent for incremental streaming and cancellation. Avoid excessive polling and unnecessary rerenders; virtualization only if needed.
- Optimize based on a measured baseline and repeat the same benchmark after each meaningful change. Document hardware, model, prompt lengths, concurrency, configuration, and raw results.
Minimum testing and quality gates
- Backend: pytest for provider adapters, free-model allowlisting, timeout, 429, missing key, fallback, stream cancellation, and usage counting.
- Frontend: component tests, keyboard/accessibility checks, responsive checks, and Playwright E2E for new chat, history, model selection, comparison, and streamed output.
- E2E should run in a visibly labeled MOCK MODE without real API keys; live provider smoke tests are opt-in and must not be claimed as run if keys are absent.
- Run the repository's actual lint, TypeScript typecheck, frontend test, backend test, build, and configured E2E commands. Fix failures or disclose exact blockers.
- Never alter unrelated code, remove tests to make CI pass, invent metrics, or claim a task was completed without evidence.
Required documentation
- README.md: setup, architecture overview, supported features, usage, safety notices, demo mode, and start/test commands.
- .env.example: named configuration placeholders, with no secrets.
- docs/ARCHITECTURE.md: API and provider-routing diagram, data flows, key decisions, and limitations.
- docs/BENCHMARKS.md: methodology, raw/derived measurements, reproduction commands, and mocked vs real labels.
- docs/FINAL_REPORT.md: work performed, test status, metrics, unresolved problems, and next steps.
Reporting contract
At delivery, write docs/FINAL_REPORT.md with these sections:
1. Summary of implemented features (working vs partial vs blocked)
2. Files/modules changed
3. Architecture and security decisions
4. Tests executed: exact commands, passes/failures, environment, and limitations
5. Measurements: baseline and final values, sample size, dates, hardware/provider and methodology
6. Outcome statements in this exact format: Accomplished [X], as measured by [Y], by implementing [Z].
7. Remaining risks, known bugs, unmet requirements, and recommended next actions
Use only measured [X]/[Y]/[Z] statements. If something cannot be verified, say Not measured or Not verified; never invent a percentage, a GPU speedup, production concurrency, or live model access.
Definition of done
Code works end-to-end in mock/demo mode; provider integrations have verified configuration pathways; UI works across desktop/tablet/mobile; security checks are applied; error states and quotas are visible; automated tests and build have been attempted; docs and final report reflect actual evidence. Prioritize a reliable thin vertical slice over unfinished breadth