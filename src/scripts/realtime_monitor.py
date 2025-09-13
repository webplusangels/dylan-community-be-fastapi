# realtime_monitor.py
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List

import aiohttp
import psutil


class RealTimeMonitor:
    """실시간 서버 모니터링 대시보드"""

    def __init__(
        self, server_url: str = "http://localhost:8000", server_pid: int = None
    ):
        self.server_url = server_url.rstrip("/")
        self.server_pid = server_pid or self._find_uvicorn_process()
        self.monitoring = False
        self.data_points: List[Dict] = []

    def _find_uvicorn_process(self) -> int:
        """uvicorn 프로세스 자동 탐지"""
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"] or [])
                if "uvicorn" in cmdline.lower() and "main:app" in cmdline:
                    print(f"🔍 Found uvicorn process: PID {proc.info['pid']}")
                    return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print("⚠️ Warning: Could not find uvicorn process")
        return None

    async def check_server_health(self) -> Dict:
        """서버 상태 체크"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=2)
            ) as session:
                start_time = time.time()
                async with session.get(f"{self.server_url}/docs") as response:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "status_code": response.status,
                        "response_time_ms": response_time,
                        "timestamp": datetime.now().isoformat(),
                    }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time_ms": 0,
                "timestamp": datetime.now().isoformat(),
            }

    def get_process_stats(self) -> Dict:
        """프로세스 리소스 사용량"""
        if not self.server_pid:
            return {}

        try:
            process = psutil.Process(self.server_pid)

            # CPU 사용률
            cpu_percent = process.cpu_percent()

            # 메모리 사용량
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = process.memory_percent()

            # 네트워크 연결
            try:
                connections = len(
                    [c for c in process.connections() if c.status == "ESTABLISHED"]
                )
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                connections = 0

            # 스레드 수
            num_threads = process.num_threads()

            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "active_connections": connections,
                "thread_count": num_threads,
                "status": process.status(),
            }

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {"error": str(e)}

    def get_system_stats(self) -> Dict:
        """시스템 전체 리소스"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # 네트워크 통계
        net_io = psutil.net_io_counters()

        return {
            "system_cpu_percent": round(cpu_percent, 2),
            "system_memory_percent": round(memory.percent, 2),
            "system_memory_available_mb": round(memory.available / 1024 / 1024, 2),
            "disk_usage_percent": round(disk.percent, 2),
            "network_bytes_sent": net_io.bytes_sent,
            "network_bytes_recv": net_io.bytes_recv,
        }

    async def collect_metrics(self) -> Dict:
        """종합 메트릭 수집"""
        timestamp = datetime.now()

        # 병렬로 데이터 수집
        health_check_task = asyncio.create_task(self.check_server_health())

        process_stats = self.get_process_stats()
        system_stats = self.get_system_stats()
        health_stats = await health_check_task

        metrics = {
            "timestamp": timestamp.isoformat(),
            "unix_timestamp": timestamp.timestamp(),
            "health": health_stats,
            "process": process_stats,
            "system": system_stats,
        }

        return metrics

    async def start_monitoring(self, interval: float = 1.0, duration: int = 60):
        """실시간 모니터링 시작"""
        print(
            f"🚀 Starting real-time monitoring for {duration}s (interval: {interval}s)"
        )
        print(f"   Server: {self.server_url}")
        if self.server_pid:
            print(f"   Process PID: {self.server_pid}")
        print("-" * 80)

        self.monitoring = True
        self.data_points.clear()
        start_time = time.time()

        try:
            while self.monitoring and (time.time() - start_time) < duration:
                metrics = await self.collect_metrics()
                self.data_points.append(metrics)

                # 실시간 출력
                self._print_realtime_stats(metrics)

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")

        self.monitoring = False
        print(
            f"\n✅ Monitoring completed. Collected {len(self.data_points)} data points"
        )
        return self.data_points

    def _print_realtime_stats(self, metrics: Dict):
        """실시간 통계 출력"""
        timestamp = datetime.fromisoformat(metrics["timestamp"]).strftime("%H:%M:%S")

        # 서버 상태
        health = metrics["health"]
        health_status = health.get("status", "unknown")
        response_time = health.get("response_time_ms", 0)

        # 프로세스 통계
        process = metrics.get("process", {})
        cpu = process.get("cpu_percent", 0)
        memory = process.get("memory_mb", 0)
        connections = process.get("active_connections", 0)

        # 시스템 통계
        system = metrics.get("system", {})
        sys_cpu = system.get("system_cpu_percent", 0)
        sys_memory = system.get("system_memory_percent", 0)

        # 상태에 따른 색상 이모지
        status_emoji = {"healthy": "🟢", "unhealthy": "🟡", "error": "🔴"}.get(
            health_status, "⚪"
        )

        print(
            f"{timestamp} {status_emoji} "
            f"Health: {health_status:8s} "
            f"Response: {response_time:5.1f}ms "
            f"CPU: {cpu:5.1f}% "
            f"Memory: {memory:6.1f}MB "
            f"Conn: {connections:3d} "
            f"Sys: {sys_cpu:4.1f}%/{sys_memory:4.1f}%"
        )

    def save_data(self, filename: str = None):
        """수집된 데이터 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"monitoring_data_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data_points, f, indent=2, ensure_ascii=False)

        print(f"📊 Monitoring data saved to {filename}")
        return filename

    def analyze_data(self):
        """데이터 분석 및 요약"""
        if not self.data_points:
            print("No data to analyze")
            return

        print("\n" + "=" * 60)
        print("📈 MONITORING ANALYSIS")
        print("=" * 60)

        # 응답시간 분석
        response_times = [
            dp["health"].get("response_time_ms", 0)
            for dp in self.data_points
            if dp["health"].get("response_time_ms") is not None
        ]

        if response_times:
            print("\n🎯 Response Time Analysis:")
            print(f"   Average: {sum(response_times) / len(response_times):.2f}ms")
            print(f"   Min: {min(response_times):.2f}ms")
            print(f"   Max: {max(response_times):.2f}ms")
            print(f"   Samples: {len(response_times)}")

        # CPU 사용률 분석
        cpu_values = [
            dp["process"].get("cpu_percent", 0)
            for dp in self.data_points
            if "process" in dp and dp["process"].get("cpu_percent") is not None
        ]

        if cpu_values:
            print("\n⚡ CPU Usage Analysis:")
            print(f"   Average: {sum(cpu_values) / len(cpu_values):.2f}%")
            print(f"   Peak: {max(cpu_values):.2f}%")
            print(f"   Min: {min(cpu_values):.2f}%")

        # 메모리 사용량 분석
        memory_values = [
            dp["process"].get("memory_mb", 0)
            for dp in self.data_points
            if "process" in dp and dp["process"].get("memory_mb") is not None
        ]

        if memory_values:
            print("\n💾 Memory Usage Analysis:")
            print(f"   Average: {sum(memory_values) / len(memory_values):.2f}MB")
            print(f"   Peak: {max(memory_values):.2f}MB")
            print(f"   Growth: {max(memory_values) - min(memory_values):.2f}MB")

        # 연결 수 분석
        connection_values = [
            dp["process"].get("active_connections", 0)
            for dp in self.data_points
            if "process" in dp and dp["process"].get("active_connections") is not None
        ]

        if connection_values:
            print("\n🔗 Connection Analysis:")
            print(f"   Average: {sum(connection_values) / len(connection_values):.1f}")
            print(f"   Peak: {max(connection_values)}")
            print(f"   Min: {min(connection_values)}")

        # 상태 분석
        health_statuses = [dp["health"].get("status") for dp in self.data_points]
        status_counts = {}
        for status in health_statuses:
            status_counts[status] = status_counts.get(status, 0) + 1

        print("\n🏥 Health Status Summary:")
        for status, count in status_counts.items():
            percentage = (count / len(health_statuses)) * 100
            print(f"   {status}: {count} ({percentage:.1f}%)")


# 실행 함수
async def run_monitoring(duration: int = 60, interval: float = 1.0):
    """모니터링 실행"""
    monitor = RealTimeMonitor()

    # 모니터링 실행
    data = await monitor.start_monitoring(interval=interval, duration=duration)

    # 결과 분석
    monitor.analyze_data()

    # 데이터 저장
    filename = monitor.save_data()

    return data, filename


# 부하 테스트와 함께 모니터링
async def monitor_with_load_test():
    """부하 테스트와 함께 모니터링"""
    from concurrent_benchmark import ConcurrentBenchmark

    print("🔥 Starting load test with real-time monitoring")

    # 모니터 시작
    monitor = RealTimeMonitor()
    monitoring_task = asyncio.create_task(
        monitor.start_monitoring(interval=0.5, duration=120)
    )

    # 잠시 대기 후 부하 테스트 시작
    await asyncio.sleep(5)

    # 부하 테스트 실행
    benchmark = ConcurrentBenchmark("http://localhost:8000")

    print("\n🚀 Starting concurrent load test...")
    await benchmark.run_concurrency_scaling_test(
        endpoint="/api/v1/posts/",
        concurrency_levels=[5, 10, 20, 30],
        requests_per_test=100,
    )

    # 모니터링 종료
    monitor.monitoring = False
    await monitoring_task

    # 결과 분석
    monitor.analyze_data()
    monitor.save_data("load_test_monitoring.json")
    benchmark.save_results("load_test_benchmark.json")


if __name__ == "__main__":
    # 기본 모니터링 (60초)
    # asyncio.run(run_monitoring(duration=60, interval=1.0))

    # 부하 테스트와 함께 모니터링
    asyncio.run(monitor_with_load_test())
