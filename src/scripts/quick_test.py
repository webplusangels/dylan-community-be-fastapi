# quick_test.py
"""
빠른 동시성 테스트 실행 스크립트
"""

import asyncio
import os
import sys

# 스크립트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from concurrent_benchmark import ConcurrentBenchmark
from realtime_monitor import RealTimeMonitor


async def quick_concurrency_test():
    """빠른 동시성 테스트"""
    print("🚀 Quick Concurrency Test")
    print("=" * 50)

    benchmark = ConcurrentBenchmark("http://localhost:8000")

    # 간단한 동시성 테스트
    result = await benchmark.benchmark_concurrent(
        endpoint="/api/v1/posts/",
        concurrency=10,
        total_requests=50,
        print_progress=True,
    )

    print("\n✅ Test completed!")
    print(f"   Average response time: {result.avg_response_time:.2f}ms")
    print(f"   Requests per second: {result.requests_per_second:.2f}")
    print(f"   Success rate: {result.success_rate:.1f}%")
    print(f"   Peak CPU: {result.peak_cpu_percent:.1f}%")

    return result


async def quick_monitoring_test():
    """빠른 모니터링 테스트"""
    print("📊 Quick Monitoring Test (30 seconds)")
    print("=" * 50)

    monitor = RealTimeMonitor()
    data = await monitor.start_monitoring(interval=1.0, duration=30)

    print("\n📈 Quick Analysis:")
    monitor.analyze_data()

    return data


async def concurrency_scaling_test():
    """동시성 스케일링 테스트"""
    print("📈 Concurrency Scaling Test")
    print("=" * 50)

    benchmark = ConcurrentBenchmark("http://localhost:8000")

    results = await benchmark.run_concurrency_scaling_test(
        endpoint="/api/v1/posts/",
        concurrency_levels=[1, 5, 10, 15],
        requests_per_test=50,
    )

    benchmark.print_summary()
    benchmark.save_results("scaling_test_results.json")

    return results


async def main():
    """메인 실행"""
    if len(sys.argv) < 2:
        print("Usage: python quick_test.py [test_type]")
        print("Test types:")
        print("  concurrent  - Quick concurrency test")
        print("  monitor     - Quick monitoring test")
        print("  scaling     - Concurrency scaling test")
        print("  combined    - Combined test with monitoring")
        return

    test_type = sys.argv[1].lower()

    if test_type == "concurrent":
        await quick_concurrency_test()
    elif test_type == "monitor":
        await quick_monitoring_test()
    elif test_type == "scaling":
        await concurrency_scaling_test()
    elif test_type == "combined":
        print("🔥 Combined Test: Monitoring + Load Testing")
        print("=" * 50)

        # 모니터링 시작
        monitor = RealTimeMonitor()
        monitoring_task = asyncio.create_task(
            monitor.start_monitoring(interval=0.5, duration=60)
        )

        # 약간 대기 후 부하 테스트
        await asyncio.sleep(3)

        benchmark = ConcurrentBenchmark("http://localhost:8000")
        await benchmark.run_concurrency_scaling_test(
            endpoint="/api/v1/posts/",
            concurrency_levels=[5, 10, 20],
            requests_per_test=100,
        )

        # 모니터링 종료
        monitor.monitoring = False
        await monitoring_task

        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 COMBINED TEST RESULTS")
        print("=" * 60)

        monitor.analyze_data()
        benchmark.print_summary()

        # 파일 저장
        monitor.save_data("combined_monitoring.json")
        benchmark.save_results("combined_benchmark.json")

    else:
        print(f"Unknown test type: {test_type}")


if __name__ == "__main__":
    asyncio.run(main())
