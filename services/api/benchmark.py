import asyncio
import time
import httpx
import numpy as np

async def run_benchmark(num_requests: int = 20, concurrency: int = 5):
    url = "http://127.0.0.1:8000/api/v1/chat/stream"
    payload = {
        "model": "mock-fast-chat",
        "messages": [{"role": "user", "content": "Benchmark synthetic request for latency profiling"}],
        "stream": True
    }

    latencies = []
    ttfts = []
    errors = 0

    sem = asyncio.Semaphore(concurrency)

    async def single_req(client: httpx.AsyncClient):
        nonlocal errors
        async with sem:
            start = time.perf_counter()
            first_token = None
            try:
                async with client.stream("POST", url, json=payload, timeout=15.0) as resp:
                    if resp.status_code != 200:
                        errors += 1
                        return
                    async for line in resp.aiter_lines():
                        if line and "time_to_first_token_ms" in line and first_token is None:
                            first_token = (time.perf_counter() - start) * 1000
                total_ms = (time.perf_counter() - start) * 1000
                latencies.append(total_ms)
                if first_token:
                    ttfts.append(first_token)
            except Exception as e:
                errors += 1

    async with httpx.AsyncClient() as client:
        tasks = [single_req(client) for _ in range(num_requests)]
        await asyncio.gather(*tasks)

    p50_lat = np.percentile(latencies, 50) if latencies else 0
    p95_lat = np.percentile(latencies, 95) if latencies else 0
    p50_ttft = np.percentile(ttfts, 50) if ttfts else 0

    print("--- BENCHMARK RESULTS ---")
    print(f"Total Requests: {num_requests}")
    print(f"Concurrency: {concurrency}")
    print(f"Successful: {len(latencies)}")
    print(f"Errors: {errors}")
    print(f"p50 Latency: {p50_lat:.2f} ms")
    print(f"p95 Latency: {p95_lat:.2f} ms")
    print(f"p50 TTFT: {p50_ttft:.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
