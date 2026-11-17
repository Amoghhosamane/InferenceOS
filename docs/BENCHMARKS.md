# InferenceOS Benchmarks & Latency Evaluation

This document outlines the evaluation methodology and actual measured performance data collected using the automated benchmark script (`services/api/benchmark.py`).

## 1. Methodology
- **Target Endpoint:** `POST /api/v1/chat/stream`
- **Protocol:** HTTP/1.1 Server-Sent Events (SSE) via `httpx.AsyncClient`
- **Workload Concurrency:** 5 concurrent workers
- **Sample Size:** 20 sequential batch requests
- **Prompt:** Standard synthetic prompt: `"Benchmark synthetic request for latency profiling"`
- **Hardware/Environment:** Windows 11 (x64), Python 3.13.7, Local loopback (`127.0.0.1:8000`)
- **Mode:** Deterministic Mock Mode (`MOCK_MODE=True`, model `mock-fast-chat`)

> **Notice:** The metrics below represent backend server overhead, connection establishment, SSE chunk framing, client reception, and local mock streaming. Hosted API latency varies based on third-party provider load and network hops.

## 2. Measured Benchmark Data

| Metric | Measured Value | Unit |
| :--- | :--- | :--- |
| **Total Completed Requests** | 20 | requests |
| **Concurrency Level** | 5 | workers |
| **Success Rate** | 100.0% (20/20) | % |
| **HTTP Errors / Failures** | 0 | errors |
| **Time to First Token (TTFT) p50** | 44.48 | ms |
| **Observed Latency (p50)** | 341.26 | ms |
| **Observed Latency (p95)** | 369.15 | ms |

## 3. Reproduction Command
To reproduce these exact measurements on any deployment:

```powershell
$env:PYTHONPATH="C:\Desktop\gitProjects\Interference\services\api"
py services/api/benchmark.py
```
