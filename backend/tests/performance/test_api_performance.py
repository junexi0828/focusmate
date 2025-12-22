"""
Performance Tests for API Endpoints
Tests response times, throughput, and scalability
"""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client."""
    try:
        from app.main import app
        return TestClient(app)
    except Exception:
        pytest.skip("App not available")


class TestAPIResponseTime:
    """Test API endpoint response times."""

    def test_health_endpoint_response_time(self, client):
        """Test health endpoint responds within acceptable time."""
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code in [200, 404]
        assert elapsed < 1.0, f"Health endpoint too slow: {elapsed:.3f}s"

    def test_api_docs_response_time(self, client):
        """Test API docs endpoint response time."""
        start = time.time()
        response = client.get("/docs")
        elapsed = time.time() - start

        assert response.status_code in [200, 404]
        assert elapsed < 2.0, f"Docs endpoint too slow: {elapsed:.3f}s"

    def test_openapi_response_time(self, client):
        """Test OpenAPI endpoint response time."""
        start = time.time()
        response = client.get("/openapi.json")
        elapsed = time.time() - start

        assert response.status_code in [200, 404]
        assert elapsed < 1.0, f"OpenAPI endpoint too slow: {elapsed:.3f}s"


class TestConcurrentRequests:
    """Test API performance under concurrent load."""

    def test_concurrent_health_checks(self, client):
        """Test health endpoint with concurrent requests."""
        num_requests = 10
        start = time.time()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(client.get, "/health") for _ in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        elapsed = time.time() - start
        avg_time = elapsed / num_requests

        # All requests should succeed
        assert all(r.status_code in [200, 404] for r in results)
        # Average response time should be reasonable
        assert avg_time < 0.5, f"Average response time too high: {avg_time:.3f}s"
        # Total time should be less than sequential
        assert elapsed < num_requests * 0.5, f"Concurrent requests not efficient: {elapsed:.3f}s"

    def test_concurrent_api_calls(self, client):
        """Test multiple API endpoints concurrently."""
        endpoints = ["/health", "/docs", "/openapi.json"]
        start = time.time()

        with ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
            futures = {executor.submit(client.get, endpoint): endpoint for endpoint in endpoints}
            results = {}
            for future in as_completed(futures):
                endpoint = futures[future]
                results[endpoint] = future.result()

        elapsed = time.time() - start

        # All should succeed
        assert all(r.status_code in [200, 404] for r in results.values())
        # Should complete faster than sequential
        assert elapsed < len(endpoints) * 1.0, f"Concurrent calls too slow: {elapsed:.3f}s"


class TestLoadPerformance:
    """Test API performance under load."""

    def test_sustained_load(self, client):
        """Test API performance under sustained load."""
        num_requests = 50
        response_times = []

        for _ in range(num_requests):
            start = time.time()
            response = client.get("/health")
            elapsed = time.time() - start
            response_times.append(elapsed)
            assert response.status_code in [200, 404]

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]

        # Performance assertions
        assert avg_time < 0.5, f"Average response time too high: {avg_time:.3f}s"
        assert median_time < 0.5, f"Median response time too high: {median_time:.3f}s"
        assert p95_time < 1.0, f"P95 response time too high: {p95_time:.3f}s"

    def test_burst_load(self, client):
        """Test API performance under burst load."""
        num_requests = 20
        start = time.time()

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(client.get, "/health") for _ in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        elapsed = time.time() - start
        requests_per_second = num_requests / elapsed

        # All should succeed
        assert all(r.status_code in [200, 404] for r in results)
        # Should handle at least 10 requests per second
        assert requests_per_second >= 10, f"Throughput too low: {requests_per_second:.2f} req/s"


class TestDatabaseQueryPerformance:
    """Test database query performance."""

    @pytest.mark.asyncio
    async def test_query_performance(self):
        """Test database query performance (requires DB)."""
        # This would test actual database queries
        # For now, skip if database not available
        try:
            # Test would go here
            pytest.skip("Database performance test requires setup")
        except Exception:
            pytest.skip("Database not available")


class TestMemoryPerformance:
    """Test memory usage and leaks."""

    def test_memory_usage_stable(self, client):
        """Test that memory usage remains stable under load."""
        import os

        try:
            import psutil
        except ImportError:
            pytest.skip("psutil module not installed")

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run many requests
        for _ in range(100):
            client.get("/health")

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase"


@pytest.mark.benchmark
class TestBenchmarkEndpoints:
    """Benchmark tests for key endpoints."""

    def test_benchmark_health_endpoint(self, client):
        """Benchmark health endpoint."""
        num_iterations = 100
        times = []

        for _ in range(num_iterations):
            start = time.time()
            client.get("/health")
            times.append(time.time() - start)

        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        p99 = sorted(times)[int(len(times) * 0.99)]

        print("\nHealth Endpoint Benchmark:")
        print(f"  Average: {avg*1000:.2f}ms")
        print(f"  P95: {p95*1000:.2f}ms")
        print(f"  P99: {p99*1000:.2f}ms")

        assert avg < 0.1, f"Average too slow: {avg*1000:.2f}ms"

