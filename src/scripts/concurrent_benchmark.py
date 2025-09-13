# concurrent_benchmark.py
import asyncio
import json
import time
from dataclasses import asdict, dataclass
from statistics import mean, median, stdev
from typing import Dict, List, Optional

import aiohttp
import psutil


@dataclass
class ConcurrentBenchmarkResult:
    endpoint: str
    concurrency_level: int
    total_requests: int
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    std_dev_response_time: float
    requests_per_second: float
    success_rate: float
    error_count: int
    timeout_count: int
    # Server monitoring
    peak_cpu_percent: float
    avg_cpu_percent: float
    peak_memory_mb: float
    avg_memory_mb: float
    memory_growth_mb: float


@dataclass
class MonitoringSnapshot:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    active_connections: int


class ServerMonitor:
    """서버 프로세스 실시간 모니터링"""

    def __init__(self, server_pid: Optional[int] = None):
        self.server_pid = server_pid or self._find_uvicorn_process()
        self.snapshots: List[MonitoringSnapshot] = []
        self.monitoring = False

    def _find_uvicorn_process(self) -> Optional[int]:
        """uvicorn 프로세스 PID 자동 탐지"""
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])
                if "uvicorn" in cmdline.lower() and "main:app" in cmdline:
                    print(f"📊 Found uvicorn process: PID {proc.info['pid']}")
                    return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print(
            "⚠️ Warning: Could not find uvicorn process. Using current process for monitoring."
        )
        return None

    async def start_monitoring(self, interval: float = 0.1):
        """실시간 모니터링 시작"""
        self.monitoring = True
        self.snapshots.clear()

        if self.server_pid:
            try:
                process = psutil.Process(self.server_pid)
            except psutil.NoSuchProcess:
                print(f"⚠️ Process {self.server_pid} not found. Using current process.")
                process = psutil.Process()
        else:
            process = psutil.Process()

        while self.monitoring:
            try:
                cpu = process.cpu_percent()
                memory = process.memory_info().rss / 1024 / 1024  # MB

                # 네트워크 연결 수 (선택적)
                try:
                    connections = len(process.connections())
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    connections = 0

                snapshot = MonitoringSnapshot(
                    timestamp=time.time(),
                    cpu_percent=cpu,
                    memory_mb=memory,
                    active_connections=connections,
                )
                self.snapshots.append(snapshot)

                await asyncio.sleep(interval)

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"⚠️ Monitoring error: {e}")
                break

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False

    def get_stats(self) -> Dict:
        """모니터링 통계 계산"""
        if not self.snapshots:
            return {}

        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_mb for s in self.snapshots]

        return {
            "peak_cpu_percent": max(cpu_values),
            "avg_cpu_percent": mean(cpu_values),
            "peak_memory_mb": max(memory_values),
            "avg_memory_mb": mean(memory_values),
            "memory_growth_mb": max(memory_values) - min(memory_values),
            "sample_count": len(self.snapshots),
        }


class ConcurrentBenchmark:
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.results: List[ConcurrentBenchmarkResult] = []
        self.monitor = ServerMonitor()

    def _get_headers(self) -> Dict[str, str]:
        """인증 헤더 생성"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def _single_request(
        self, session: aiohttp.ClientSession, endpoint: str
    ) -> Dict:
        """단일 요청 실행"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with session.get(
                url,
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                await response.text()
                end_time = time.time()

                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": end_time - start_time,
                    "error": None,
                    "timeout": False,
                }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "status_code": 0,
                "response_time": time.time() - start_time,
                "error": "timeout",
                "timeout": True,
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "response_time": time.time() - start_time,
                "error": str(e),
                "timeout": False,
            }

    async def benchmark_concurrent(
        self,
        endpoint: str,
        concurrency: int = 10,
        total_requests: int = 100,
        print_progress: bool = True,
    ) -> ConcurrentBenchmarkResult:
        """동시성 벤치마크 실행"""

        if print_progress:
            print("\n🚀 Starting concurrent benchmark:")
            print(f"   Endpoint: {endpoint}")
            print(f"   Concurrency: {concurrency}")
            print(f"   Total requests: {total_requests}")
            print(f"   Expected duration: ~{total_requests / concurrency * 0.015:.1f}s")

        # 모니터링 시작
        monitoring_task = asyncio.create_task(
            self.monitor.start_monitoring(interval=0.05)
        )

        # 동시 요청 실행
        connector = aiohttp.TCPConnector(limit=concurrency + 5)
        async with aiohttp.ClientSession(connector=connector) as session:
            # 요청을 배치로 나누어 동시성 제어
            batches = []
            batch_size = concurrency

            for i in range(0, total_requests, batch_size):
                batch_requests = min(batch_size, total_requests - i)
                batch = [
                    self._single_request(session, endpoint)
                    for _ in range(batch_requests)
                ]
                batches.append(batch)

            # 배치별 실행
            all_results = []
            start_time = time.time()

            for i, batch in enumerate(batches):
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                all_results.extend([r for r in batch_results if isinstance(r, dict)])

                if print_progress and i % max(1, len(batches) // 5) == 0:
                    progress = (i + 1) / len(batches) * 100
                    print(
                        f"   Progress: {progress:.1f}% ({len(all_results)}/{total_requests})"
                    )

            end_time = time.time()

        # 모니터링 중지
        self.monitor.stop_monitoring()
        monitoring_task.cancel()

        # 결과 분석
        response_times = [r["response_time"] * 1000 for r in all_results]  # ms 변환
        success_count = sum(1 for r in all_results if r["success"])
        error_count = sum(
            1 for r in all_results if not r["success"] and not r["timeout"]
        )
        timeout_count = sum(1 for r in all_results if r["timeout"])

        # 퍼센타일 계산
        sorted_times = sorted(response_times)

        def percentile(data, p):
            if not data:
                return 0
            index = int(p * len(data) / 100)
            return data[min(index, len(data) - 1)]

        # 모니터링 통계
        monitor_stats = self.monitor.get_stats()

        # 결과 생성
        total_duration = end_time - start_time
        result = ConcurrentBenchmarkResult(
            endpoint=endpoint,
            concurrency_level=concurrency,
            total_requests=len(all_results),
            avg_response_time=mean(response_times) if response_times else 0,
            median_response_time=median(response_times) if response_times else 0,
            p95_response_time=percentile(sorted_times, 95),
            p99_response_time=percentile(sorted_times, 99),
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            std_dev_response_time=stdev(response_times)
            if len(response_times) > 1
            else 0,
            requests_per_second=len(all_results) / total_duration,
            success_rate=(success_count / len(all_results) * 100) if all_results else 0,
            error_count=error_count,
            timeout_count=timeout_count,
            peak_cpu_percent=monitor_stats.get("peak_cpu_percent", 0),
            avg_cpu_percent=monitor_stats.get("avg_cpu_percent", 0),
            peak_memory_mb=monitor_stats.get("peak_memory_mb", 0),
            avg_memory_mb=monitor_stats.get("avg_memory_mb", 0),
            memory_growth_mb=monitor_stats.get("memory_growth_mb", 0),
        )

        self.results.append(result)

        if print_progress:
            print(
                f"✅ Completed: {result.avg_response_time:.2f}ms avg, {result.requests_per_second:.2f} req/s"
            )

        return result

    async def run_concurrency_scaling_test(
        self,
        endpoint: str,
        concurrency_levels: Optional[List[int]] = None,
        requests_per_test: int = 100,
    ):
        """동시성 레벨별 성능 테스트"""
        if concurrency_levels is None:
            concurrency_levels = [1, 5, 10, 25, 50]
        print(f"🔬 Running concurrency scaling test for {endpoint}")
        print(f"   Concurrency levels: {concurrency_levels}")
        print(f"   Requests per test: {requests_per_test}")

        results = []
        for concurrency in concurrency_levels:
            print(f"\n--- Testing concurrency level: {concurrency} ---")
            result = await self.benchmark_concurrent(
                endpoint=endpoint,
                concurrency=concurrency,
                total_requests=requests_per_test,
            )
            results.append(result)

            # 테스트 간 휴식 (서버 안정화)
            print("   Waiting 2s before next test...")
            await asyncio.sleep(2)

        return results

    def save_results(self, filename: str = "./concurrent_benchmark_results.json"):
        """결과를 JSON 파일로 저장"""
        results_dict = []
        for result in self.results:
            result_dict = asdict(result)
            # 반올림 처리
            for key, value in result_dict.items():
                if isinstance(value, float):
                    result_dict[key] = round(value, 2)
            results_dict.append(result_dict)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)

        print(f"📄 Results saved to {filename}")
        return filename

    def print_summary(self):
        """결과 요약 출력"""
        if not self.results:
            print("No results to display")
            return

        print("\n" + "=" * 80)
        print("📊 CONCURRENT BENCHMARK SUMMARY")
        print("=" * 80)

        for result in self.results:
            print(f"\n🎯 {result.endpoint} (Concurrency: {result.concurrency_level})")
            print(
                f"   Response Time: {result.avg_response_time:.2f}ms avg, {result.median_response_time:.2f}ms median"
            )
            print(
                f"   Percentiles: P95={result.p95_response_time:.2f}ms, P99={result.p99_response_time:.2f}ms"
            )
            print(f"   Throughput: {result.requests_per_second:.2f} req/s")
            print(
                f"   Success Rate: {result.success_rate:.1f}% ({result.total_requests - result.error_count - result.timeout_count}/{result.total_requests})"
            )

            if result.error_count > 0 or result.timeout_count > 0:
                print(
                    f"   ⚠️ Errors: {result.error_count}, Timeouts: {result.timeout_count}"
                )

            print(
                f"   Server CPU: {result.peak_cpu_percent:.1f}% peak, {result.avg_cpu_percent:.1f}% avg"
            )
            print(
                f"   Server Memory: {result.peak_memory_mb:.1f}MB peak, +{result.memory_growth_mb:.1f}MB growth"
            )


# 실행 예시
async def main():
    """메인 실행 함수"""

    # 인증 토큰 획득 (옵션)
    # auth_token = await get_auth_token("http://localhost:8000", "test@example.com", "password")

    benchmark = ConcurrentBenchmark("http://localhost:8000", auth_token=None)

    print("🚀 Starting Concurrent Performance Benchmark")
    print("=" * 50)

    # 1. 단일 엔드포인트 동시성 테스트
    await benchmark.benchmark_concurrent(
        endpoint="/api/v1/posts/", concurrency=10, total_requests=200
    )

    # 2. 동시성 스케일링 테스트
    scaling_results = await benchmark.run_concurrency_scaling_test(
        endpoint="/api/v1/posts/",
        concurrency_levels=[1, 5, 10, 20, 30],
        requests_per_test=100,
    )

    # 3. 여러 엔드포인트 테스트
    endpoints = [
        "/api/v1/users/me",
        "/api/v1/comments/49c914d6-c858-4581-b54e-d562e22bedbe",
    ]

    for endpoint in endpoints:
        await benchmark.benchmark_concurrent(
            endpoint=endpoint, concurrency=15, total_requests=150
        )

    # 결과 출력 및 저장
    benchmark.print_summary()
    benchmark.save_results()

    # 스케일링 분석
    print("\n📈 CONCURRENCY SCALING ANALYSIS")
    print("-" * 50)
    for result in scaling_results:
        efficiency = result.requests_per_second / result.concurrency_level
        print(
            f"Concurrency {result.concurrency_level:2d}: {result.requests_per_second:6.2f} req/s, "
            f"efficiency: {efficiency:5.2f} req/s/thread, "
            f"avg: {result.avg_response_time:6.2f}ms"
        )


if __name__ == "__main__":
    asyncio.run(main())
