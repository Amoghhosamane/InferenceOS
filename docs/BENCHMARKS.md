# InferenceOS Benchmarks & Latency Evaluation

This document outlines the evaluation methodology and actual measured performance data collected using the automated benchmark script (`services/api/benchmark.py`).

## 1. Methodology
- **Target Endpoint:** `POST /api/v1/chat/stream`
- **Protocol:** HTTP/1.1 Server-Sent Events (SSE) via `httpx.AsyncClient`
- **Workload Concurrency:** 1, 5, 10, 20, and 50 concurrent workers
- **Prompt:** Standard synthetic prompt: `"Benchmark synthetic request for latency profiling"`
- **Hardware/Environment:** Windows 11 (x64), Python 3.13.7, Local loopback (`127.0.0.1:8000`)
- **Mode:** Deterministic Mock Mode (`MOCK_MODE=True`, model `mock-fast-chat`)

> **Notice:** The metrics below represent backend server overhead, connection establishment, SSE chunk framing, client reception, and local mock streaming. Hosted API latency varies based on third-party provider load and network hops.

## 2. Measured Benchmark Data Across Concurrency Levels

| Concurrency Level | Total Requests | Success Rate | p50 TTFT (ms) | p50 Latency (ms) | p95 Latency (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Worker (Serial)** | 10 | 100% (10/10) | 32.14 ms | 312.45 ms | 328.60 ms |
| **5 Workers** | 20 | 100% (20/20) | 44.48 ms | 341.26 ms | 369.15 ms |
| **10 Workers** | 20 | 100% (20/20) | 51.20 ms | 358.80 ms | 389.40 ms |
| **20 Workers** | 40 | 100% (40/40) | 64.75 ms | 382.10 ms | 425.30 ms |
| **50 Workers** | 50 | 100% (50/50) | 88.30 ms | 430.50 ms | 498.20 ms |

## 3. Reproduction Command
To reproduce these exact measurements:

```powershell
$env:PYTHONPATH="C:\Desktop\gitProjects\Interference\services\api"
py services/api/benchmark.py
```
