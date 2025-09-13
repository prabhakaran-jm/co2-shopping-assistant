"""
Performance and load testing for CO2 Shopping Assistant
"""
import asyncio
import pytest
import time
from typing import List, Dict, Any
import httpx
import statistics


class LoadTestConfig:
    """Configuration for load tests"""
    BASE_URL = "http://localhost:8000"
    CONCURRENT_USERS = 10
    REQUESTS_PER_USER = 100
    TIMEOUT = 30.0


@pytest.mark.performance
@pytest.mark.slow
class TestLoadPerformance:
    """Load testing suite"""
    
    async def test_concurrent_chat_requests(self):
        """Test concurrent chat requests"""
        async def make_request(client: httpx.AsyncClient, user_id: int) -> Dict[str, Any]:
            """Make a single chat request"""
            start_time = time.time()
            try:
                response = await client.post(
                    f"{LoadTestConfig.BASE_URL}/api/chat",
                    json={
                        "message": f"Find me eco-friendly laptops under $1500 (User {user_id})",
                        "session_id": f"load_test_user_{user_id}"
                    },
                    timeout=LoadTestConfig.TIMEOUT
                )
                end_time = time.time()
                
                return {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "success": response.status_code == 200,
                    "user_id": user_id
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "status_code": 0,
                    "response_time": end_time - start_time,
                    "success": False,
                    "error": str(e),
                    "user_id": user_id
                }
        
        # Create HTTP client
        async with httpx.AsyncClient() as client:
            # Create tasks for concurrent requests
            tasks = []
            for user_id in range(LoadTestConfig.CONCURRENT_USERS):
                for request_num in range(LoadTestConfig.REQUESTS_PER_USER):
                    task = make_request(client, user_id)
                    tasks.append(task)
            
            # Execute all requests concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze results
            successful_requests = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_requests = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            response_times = [r["response_time"] for r in successful_requests]
            
            # Calculate metrics
            total_requests = len(results)
            success_rate = len(successful_requests) / total_requests * 100
            avg_response_time = statistics.mean(response_times) if response_times else 0
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
            p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
            requests_per_second = total_requests / (end_time - start_time)
            
            # Print results
            print(f"\n=== Load Test Results ===")
            print(f"Total Requests: {total_requests}")
            print(f"Successful Requests: {len(successful_requests)}")
            print(f"Failed Requests: {len(failed_requests)}")
            print(f"Success Rate: {success_rate:.2f}%")
            print(f"Average Response Time: {avg_response_time:.3f}s")
            print(f"P95 Response Time: {p95_response_time:.3f}s")
            print(f"P99 Response Time: {p99_response_time:.3f}s")
            print(f"Requests per Second: {requests_per_second:.2f}")
            print(f"Total Test Duration: {end_time - start_time:.3f}s")
            
            # Assertions
            assert success_rate >= 95.0, f"Success rate {success_rate:.2f}% is below 95%"
            assert avg_response_time <= 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2s"
            assert p95_response_time <= 5.0, f"P95 response time {p95_response_time:.3f}s exceeds 5s"
            assert requests_per_second >= 10.0, f"RPS {requests_per_second:.2f} is below 10"
    
    async def test_health_check_performance(self):
        """Test health check endpoint performance"""
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            
            # Make multiple health check requests
            tasks = []
            for _ in range(100):
                task = client.get(f"{LoadTestConfig.BASE_URL}/health", timeout=5.0)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_responses = [r for r in responses if isinstance(r, httpx.Response) and r.status_code == 200]
            avg_response_time = (end_time - start_time) / len(responses)
            
            print(f"\n=== Health Check Performance ===")
            print(f"Total Health Checks: {len(responses)}")
            print(f"Successful: {len(successful_responses)}")
            print(f"Average Response Time: {avg_response_time:.3f}s")
            
            assert len(successful_responses) >= 95, "Health check success rate below 95%"
            assert avg_response_time <= 0.1, f"Health check response time {avg_response_time:.3f}s exceeds 100ms"
    
    async def test_metrics_endpoint_performance(self):
        """Test metrics endpoint performance"""
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            
            # Make multiple metrics requests
            tasks = []
            for _ in range(50):
                task = client.get(f"{LoadTestConfig.BASE_URL}/metrics", timeout=5.0)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_responses = [r for r in responses if isinstance(r, httpx.Response) and r.status_code == 200]
            avg_response_time = (end_time - start_time) / len(responses)
            
            print(f"\n=== Metrics Endpoint Performance ===")
            print(f"Total Metrics Requests: {len(responses)}")
            print(f"Successful: {len(successful_responses)}")
            print(f"Average Response Time: {avg_response_time:.3f}s")
            
            assert len(successful_responses) >= 95, "Metrics endpoint success rate below 95%"
            assert avg_response_time <= 0.5, f"Metrics response time {avg_response_time:.3f}s exceeds 500ms"


@pytest.mark.performance
class TestMemoryUsage:
    """Memory usage testing"""
    
    async def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async with httpx.AsyncClient() as client:
            # Make many requests to detect memory leaks
            for i in range(1000):
                try:
                    await client.post(
                        f"{LoadTestConfig.BASE_URL}/api/chat",
                        json={
                            "message": f"Test message {i}",
                            "session_id": f"memory_test_{i}"
                        },
                        timeout=5.0
                    )
                except Exception:
                    pass  # Ignore individual request failures
                
                # Check memory every 100 requests
                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    print(f"Request {i}: Memory usage {current_memory:.2f}MB (+{memory_increase:.2f}MB)")
                    
                    # Allow for some memory increase but not excessive
                    assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"\n=== Memory Usage Test ===")
        print(f"Initial Memory: {initial_memory:.2f}MB")
        print(f"Final Memory: {final_memory:.2f}MB")
        print(f"Total Increase: {total_increase:.2f}MB")
        
        assert total_increase < 50, f"Total memory increase {total_increase:.2f}MB exceeds 50MB"
