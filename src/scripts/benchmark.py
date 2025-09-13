# comprehensive_benchmark.py
import asyncio
import json
import time
from dataclasses import dataclass
from typing import List

import aiohttp
import psutil


@dataclass
class BenchmarkResult:
    endpoint: str
    avg_response_time: float
    requests_per_second: float
    success_rate: float
    memory_usage: float
    cpu_usage: float


class ComprehensiveBenchmark:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[BenchmarkResult] = []

    async def benchmark_endpoint(
        self, endpoint: str, requests: int = 100, headers: dict | None = None
    ) -> BenchmarkResult:
        """개별 엔드포인트 벤치마크"""
        print(f"Benchmarking {endpoint}...")

        # 메모리 및 CPU 측정 시작
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_cpu = process.cpu_percent()

        response_times = []
        success_count = 0

        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            for _ in range(requests):
                request_start = time.time()
                try:
                    async with session.get(
                        f"{self.base_url}{endpoint}", headers=headers
                    ) as response:
                        await response.text()
                        if response.status == 200:
                            success_count += 1
                except Exception:
                    pass
                request_end = time.time()
                response_times.append(request_end - request_start)

            end_time = time.time()

        # 메모리 및 CPU 측정 종료
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = process.cpu_percent()

        total_duration = end_time - start_time
        avg_response_time = sum(response_times) / len(response_times) * 1000  # ms
        requests_per_second = requests / total_duration
        success_rate = (success_count / requests) * 100
        memory_usage = end_memory - start_memory
        cpu_usage = end_cpu - start_cpu

        result = BenchmarkResult(
            endpoint=endpoint,
            avg_response_time=avg_response_time,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
        )

        self.results.append(result)
        return result

    def save_results(self, filename: str = "src/scripts/benchmark_results.json"):
        """결과를 JSON 파일로 저장"""
        results_dict = []
        for result in self.results:
            results_dict.append(
                {
                    "endpoint": result.endpoint,
                    "avg_response_time_ms": round(result.avg_response_time, 2),
                    "requests_per_second": round(result.requests_per_second, 2),
                    "success_rate_percent": round(result.success_rate, 2),
                    "memory_usage_mb": round(result.memory_usage, 2),
                    "cpu_usage_percent": round(result.cpu_usage, 2),
                }
            )

        with open(filename, "w") as f:
            json.dump(results_dict, f, indent=2)

        print(f"Results saved to {filename}")


async def get_token(base_url: str, username: str, password: str):
    # Use form-encoded data to match the OAuth2 password grant used by the API
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "string",
        "client_secret": "string",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/api/v1/auth/token", data=data, headers=headers
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                print(f"Failed to obtain token: {resp.status} - {text}")
                return None
            data = await resp.json()
            return data.get("access_token")


# 실행 예시
async def main():
    benchmark = ComprehensiveBenchmark("http://localhost:8000")
    token = await get_token("http://localhost:8000", "test@example.com", "password123")
    if token:
        auth_headers = {"Authorization": f"Bearer {token}"}
    else:
        auth_headers = None

    # 주요 엔드포인트 벤치마크
    endpoints = [
        "/api/v1/posts/",
        "/api/v1/users/me",
        "/api/v1/comments/49c914d6-c858-4581-b54e-d562e22bedbe",
        "/api/v1/likes/posts/98e3a82e-d2a9-49d3-88c0-cf8fcc49537f",
    ]

    for endpoint in endpoints:
        headers = auth_headers if endpoint != "/api/v1/auth/token" else None
        result = await benchmark.benchmark_endpoint(
            endpoint, requests=200, headers=headers
        )
        print(
            f"✅ {endpoint}: {result.avg_response_time:.2f}ms, {result.requests_per_second:.2f} req/s"
        )

    benchmark.save_results()


if __name__ == "__main__":
    asyncio.run(main())
