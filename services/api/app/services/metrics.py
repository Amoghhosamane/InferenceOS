import time
from typing import Dict, List, Any
import numpy as np

class MetricsService:
    def __init__(self):
        self._latencies: List[float] = []
        self._ttfts: List[float] = []
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._failed_requests: int = 0
        self._provider_stats: Dict[str, Dict[str, Any]] = {
            "mock": {"requests": 0, "errors": 0, "total_time": 0.0},
            "groq": {"requests": 0, "errors": 0, "total_time": 0.0},
            "gemini": {"requests": 0, "errors": 0, "total_time": 0.0},
            "openrouter": {"requests": 0, "errors": 0, "total_time": 0.0},
            "inception": {"requests": 0, "errors": 0, "total_time": 0.0},
            "vllm": {"requests": 0, "errors": 0, "total_time": 0.0},
        }

    def record_request(
        self,
        provider: str,
        latency_ms: float,
        ttft_ms: float | None = None,
        success: bool = True
    ):
        self._total_requests += 1
        if success:
            self._successful_requests += 1
        else:
            self._failed_requests += 1

        self._latencies.append(latency_ms)
        if ttft_ms is not None:
            self._ttfts.append(ttft_ms)

        if provider not in self._provider_stats:
            self._provider_stats[provider] = {"requests": 0, "errors": 0, "total_time": 0.0}

        self._provider_stats[provider]["requests"] += 1
        if not success:
            self._provider_stats[provider]["errors"] += 1
        self._provider_stats[provider]["total_time"] += latency_ms

    def get_summary(self, active_mock_mode: bool) -> Dict[str, Any]:
        p50_lat = 0.0
        p95_lat = 0.0
        p50_ttft = 0.0

        if self._latencies:
            p50_lat = float(np.percentile(self._latencies, 50))
            p95_lat = float(np.percentile(self._latencies, 95))
        if self._ttfts:
            p50_ttft = float(np.percentile(self._ttfts, 50))

        provider_summary = {}
        for p, data in self._provider_stats.items():
            reqs = data["requests"]
            avg_lat = (data["total_time"] / reqs) if reqs > 0 else 0.0
            provider_summary[p] = {
                "requests": reqs,
                "errors": data["errors"],
                "avg_latency_ms": round(avg_lat, 2)
            }

        return {
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "p50_latency_ms": round(p50_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "p50_ttft_ms": round(p50_ttft, 2),
            "provider_breakdown": provider_summary,
            "active_mock_mode": active_mock_mode,
            "sample_size": len(self._latencies),
            "timeframe": "all-time"
        }

metrics_service = MetricsService()
