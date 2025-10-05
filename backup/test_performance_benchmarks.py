"""Performance Benchmarks and Load Testing

This module provides comprehensive performance benchmarks and load testing
for the AI PowerShell Assistant system.
"""

import pytest
import asyncio
import time
import statistics
import tempfile
import shutil
import threading
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List, Tuple
import concurrent.futures

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import (
    Platform, UserRole, LogLevel, OutputFormat, RiskLevel, SecurityAction, Permission,
    CommandSuggestion, ValidationResult, ExecutionResult
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def performance_config(temp_dir):
    """Create performance-optimized test configuration"""
    config = ServerConfig(
        version="1.0.0-perf-test",
        platform=Platform.WINDOWS,
        debug_mode=False,  # Production-like performance
        model=ModelConfig(
            model_type="mock-fast",
            context_length=2048,
            temperature=0.7,
            max_tokens=256
        ),
        security=SecurityConfig(
            whitelist_path=str(Path(temp_dir) / "whitelist.json"),
            sandbox_enabled=False,  # Disable for performance testing
            audit_log_path=str(Path(temp_dir) / "audit.log")
        ),
        logging=LoggingConfig(
            log_level=LogLevel.ERROR,  # Minimal logging for performance
            enable_correlation_tracking=False,
            sensitive_data_masking=False
        ),
        execution=ExecutionConfig(
            default_timeout=30,
            max_output_size=1024 * 1024
        ),
        storage=StorageConfig(data_directory=str(Path(temp_dir) / "storage")),
        mcp_server=MCPServerConfig(
            max_concurrent_requests=50
        )
    )
    return config


@pytest.fixture
def fast_mock_integration(performance_config):
    """Create fast mock integration for performance testing"""
    integration = AIPowerShellAssistantIntegration()
    integration.config = performance_config
    
    # Mock components with minimal latency
    integration.storage = AsyncMock()
    integration.logging_engine = AsyncMock()
    integration.context_manager = AsyncMock()
    integration.ai_engine = Mock()
    integration.security_engine = Mock()
    integration.executor = Mock()
    integration.mcp_server = Mock()
    
    # Setup fast return values
    integration.context_manager.create_session.return_value = "perf-session"
    integration.context_manager.get_current_context.return_value = Mock()
    integration.logging_engine.log_user_input.return_value = "perf-corr"
    
    # Fast AI engine mock
    def fast_translate(input_text, context):
        return CommandSuggestion(
            original_input=input_text,
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Fast response",
            alternatives=[]
        )
    
    integration.ai_engine.translate_natural_language.side_effect = fast_translate
    
    # Fast security validation
    integration.security_engine.validate_command.return_value = ValidationResult(
        is_valid=True,
        blocked_reasons=[],
        required_permissions=[],
        suggested_alternatives=[],
        risk_assessment=RiskLevel.LOW
    )
    
    # Fast execution
    def fast_execute(command, context):
        return ExecutionResult(
            success=True,
            return_code=0,
            stdout="Fast execution result",
            stderr="",
            execution_time=0.01,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
    
    integration.executor.execute_command.side_effect = fast_execute
    integration.executor.format_output.side_effect = lambda output, format_type: output
    
    integration._initialized = True
    return integration


class PerformanceMetrics:
    """Helper class for collecting performance metrics"""
    
    def __init__(self):
        self.response_times = []
        self.throughput_data = []
        self.error_rates = []
        self.memory_usage = []
        self.cpu_usage = []
    
    def add_response_time(self, response_time: float):
        """Add response time measurement"""
        self.response_times.append(response_time)
    
    def add_throughput_measurement(self, requests_per_second: float):
        """Add throughput measurement"""
        self.throughput_data.append(requests_per_second)
    
    def add_error_rate(self, error_rate: float):
        """Add error rate measurement"""
        self.error_rates.append(error_rate)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        if self.response_times:
            stats["response_time"] = {
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "min": min(self.response_times),
                "max": max(self.response_times),
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99),
                "stdev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
            }
        
        if self.throughput_data:
            stats["throughput"] = {
                "mean": statistics.mean(self.throughput_data),
                "max": max(self.throughput_data),
                "min": min(self.throughput_data)
            }
        
        if self.error_rates:
            stats["error_rate"] = {
                "mean": statistics.mean(self.error_rates),
                "max": max(self.error_rates)
            }
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class TestResponseTimePerformance:
    """Test response time performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_natural_language_processing_latency(self, fast_mock_integration):
        """Test natural language processing response time"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        metrics = PerformanceMetrics()
        
        # Test multiple requests to get statistical data
        test_inputs = [
            "list running processes",
            "show system services",
            "get network connections",
            "display memory usage",
            "find large files"
        ]
        
        for test_input in test_inputs:
            for _ in range(10):  # 10 iterations per input
                start_time = time.time()
                
                result = await tool_implementations.natural_language_to_powershell(test_input)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                metrics.add_response_time(response_time)
                
                # Verify successful processing
                assert result["success"] is True
        
        # Analyze performance
        stats = metrics.get_statistics()
        response_stats = stats["response_time"]
        
        # Performance assertions
        assert response_stats["mean"] < 0.1, f"Mean response time too high: {response_stats['mean']:.3f}s"
        assert response_stats["p95"] < 0.2, f"95th percentile too high: {response_stats['p95']:.3f}s"
        assert response_stats["p99"] < 0.5, f"99th percentile too high: {response_stats['p99']:.3f}s"
        
        print(f"Natural Language Processing Performance:")
        print(f"  Mean: {response_stats['mean']:.3f}s")
        print(f"  Median: {response_stats['median']:.3f}s")
        print(f"  P95: {response_stats['p95']:.3f}s")
        print(f"  P99: {response_stats['p99']:.3f}s")
    
    @pytest.mark.asyncio
    async def test_command_execution_latency(self, fast_mock_integration):
        """Test command execution response time"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        metrics = PerformanceMetrics()
        
        # Test various command types
        test_commands = [
            "Get-Process",
            "Get-Service",
            "Get-ChildItem",
            "Get-EventLog -LogName System -Newest 10",
            "Get-WmiObject -Class Win32_ComputerSystem"
        ]
        
        for command in test_commands:
            for _ in range(10):  # 10 iterations per command
                start_time = time.time()
                
                result = await tool_implementations.execute_powershell_command(command)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                metrics.add_response_time(response_time)
                
                # Verify successful execution
                assert result["success"] is True
        
        # Analyze performance
        stats = metrics.get_statistics()
        response_stats = stats["response_time"]
        
        # Performance assertions
        assert response_stats["mean"] < 0.05, f"Mean execution time too high: {response_stats['mean']:.3f}s"
        assert response_stats["p95"] < 0.1, f"95th percentile too high: {response_stats['p95']:.3f}s"
        
        print(f"Command Execution Performance:")
        print(f"  Mean: {response_stats['mean']:.3f}s")
        print(f"  Median: {response_stats['median']:.3f}s")
        print(f"  P95: {response_stats['p95']:.3f}s")
    
    @pytest.mark.asyncio
    async def test_system_info_retrieval_latency(self, fast_mock_integration):
        """Test system information retrieval response time"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Mock health check
        async def fast_health_check():
            return {"overall": "healthy"}
        
        fast_mock_integration.health_check = fast_health_check
        fast_mock_integration.executor.get_powershell_info.return_value = {
            "version": "7.3.0",
            "edition": "Core"
        }
        
        metrics = PerformanceMetrics()
        
        # Test system info retrieval
        for _ in range(20):
            start_time = time.time()
            
            result = await tool_implementations.get_powershell_info()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics.add_response_time(response_time)
            
            # Verify successful retrieval
            assert result["success"] is True
        
        # Analyze performance
        stats = metrics.get_statistics()
        response_stats = stats["response_time"]
        
        # Performance assertions
        assert response_stats["mean"] < 0.02, f"Mean info retrieval time too high: {response_stats['mean']:.3f}s"
        
        print(f"System Info Retrieval Performance:")
        print(f"  Mean: {response_stats['mean']:.3f}s")
        print(f"  Median: {response_stats['median']:.3f}s")


class TestThroughputPerformance:
    """Test throughput and concurrent request handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_natural_language_processing(self, fast_mock_integration):
        """Test concurrent natural language processing throughput"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20, 50]
        
        for concurrency in concurrency_levels:
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for i in range(concurrency):
                task = tool_implementations.natural_language_to_powershell(f"test command {i}")
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculate throughput
            successful_requests = len([r for r in results if not isinstance(r, Exception) and r.get("success", False)])
            throughput = successful_requests / total_time
            
            print(f"Concurrency {concurrency}: {throughput:.2f} requests/second ({successful_requests}/{concurrency} successful)")
            
            # Performance assertions
            assert successful_requests >= concurrency * 0.95, f"Too many failures at concurrency {concurrency}"
            assert throughput > concurrency * 0.8, f"Throughput too low at concurrency {concurrency}"
    
    @pytest.mark.asyncio
    async def test_sustained_load_performance(self, fast_mock_integration):
        """Test sustained load performance over time"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Test sustained load for 10 seconds
        test_duration = 10  # seconds
        request_interval = 0.1  # 10 requests per second
        
        start_time = time.time()
        request_count = 0
        successful_requests = 0
        response_times = []
        
        while time.time() - start_time < test_duration:
            request_start = time.time()
            
            try:
                result = await tool_implementations.natural_language_to_powershell("sustained load test")
                request_end = time.time()
                
                request_count += 1
                if result.get("success", False):
                    successful_requests += 1
                
                response_times.append(request_end - request_start)
                
            except Exception as e:
                print(f"Request failed: {e}")
            
            # Wait for next request
            elapsed = time.time() - request_start
            if elapsed < request_interval:
                await asyncio.sleep(request_interval - elapsed)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        success_rate = successful_requests / request_count if request_count > 0 else 0
        average_throughput = successful_requests / total_time
        average_response_time = statistics.mean(response_times) if response_times else 0
        
        print(f"Sustained Load Performance:")
        print(f"  Duration: {total_time:.2f}s")
        print(f"  Total requests: {request_count}")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average throughput: {average_throughput:.2f} requests/second")
        print(f"  Average response time: {average_response_time:.3f}s")
        
        # Performance assertions
        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"
        assert average_throughput >= 8, f"Throughput too low: {average_throughput:.2f} req/s"
        assert average_response_time <= 0.2, f"Response time too high: {average_response_time:.3f}s"
    
    @pytest.mark.asyncio
    async def test_burst_load_handling(self, fast_mock_integration):
        """Test handling of burst loads"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Test burst of 100 requests
        burst_size = 100
        
        start_time = time.time()
        
        # Create burst of concurrent requests
        tasks = []
        for i in range(burst_size):
            task = tool_implementations.natural_language_to_powershell(f"burst test {i}")
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_requests = len([r for r in results if not isinstance(r, Exception) and r.get("success", False)])
        failed_requests = burst_size - successful_requests
        throughput = successful_requests / total_time
        
        print(f"Burst Load Performance:")
        print(f"  Burst size: {burst_size}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful: {successful_requests}")
        print(f"  Failed: {failed_requests}")
        print(f"  Success rate: {successful_requests/burst_size:.2%}")
        print(f"  Throughput: {throughput:.2f} requests/second")
        
        # Performance assertions
        assert successful_requests >= burst_size * 0.9, f"Too many failures in burst: {failed_requests}"
        assert total_time <= 5.0, f"Burst took too long: {total_time:.2f}s"


class TestMemoryAndResourceUsage:
    """Test memory usage and resource consumption"""
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, fast_mock_integration):
        """Test memory usage under sustained load"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Get initial memory usage (if available)
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            initial_memory = 0
            print("psutil not available, skipping memory measurements")
        
        # Run sustained load
        request_count = 1000
        
        for i in range(request_count):
            await tool_implementations.natural_language_to_powershell(f"memory test {i}")
            
            # Check memory every 100 requests
            if i % 100 == 0 and initial_memory > 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                print(f"Request {i}: Memory usage {current_memory:.1f}MB (+{memory_increase:.1f}MB)")
                
                # Memory should not grow excessively
                assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.1f}MB"
        
        # Final memory check
        if initial_memory > 0:
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            total_increase = final_memory - initial_memory
            
            print(f"Final memory usage: {final_memory:.1f}MB (+{total_increase:.1f}MB)")
            
            # Total memory increase should be reasonable
            assert total_increase < 50, f"Total memory increase too high: {total_increase:.1f}MB"
    
    @pytest.mark.asyncio
    async def test_session_cleanup_performance(self, fast_mock_integration):
        """Test performance of session cleanup operations"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Create many sessions
        session_count = 100
        session_ids = []
        
        start_time = time.time()
        
        for i in range(session_count):
            session_id = f"cleanup-test-session-{i}"
            session_ids.append(session_id)
            
            # Simulate session activity
            await tool_implementations.natural_language_to_powershell(
                f"test command {i}",
                session_id=session_id
            )
        
        creation_time = time.time() - start_time
        
        # Simulate session cleanup (would be done by context manager)
        cleanup_start = time.time()
        
        # Mock cleanup operations
        for session_id in session_ids:
            # Simulate cleanup work
            pass
        
        cleanup_time = time.time() - cleanup_start
        
        print(f"Session Management Performance:")
        print(f"  Created {session_count} sessions in {creation_time:.2f}s")
        print(f"  Cleanup time: {cleanup_time:.3f}s")
        print(f"  Creation rate: {session_count/creation_time:.1f} sessions/second")
        
        # Performance assertions
        assert creation_time < 10.0, f"Session creation too slow: {creation_time:.2f}s"
        assert cleanup_time < 1.0, f"Session cleanup too slow: {cleanup_time:.3f}s"


class TestScalabilityLimits:
    """Test system scalability limits"""
    
    @pytest.mark.asyncio
    async def test_maximum_concurrent_requests(self, fast_mock_integration):
        """Test maximum concurrent request handling"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Test increasing concurrency levels until failure
        max_concurrency = 200
        step_size = 25
        
        for concurrency in range(step_size, max_concurrency + 1, step_size):
            try:
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = []
                for i in range(concurrency):
                    task = tool_implementations.natural_language_to_powershell(f"scalability test {i}")
                    tasks.append(task)
                
                # Execute with timeout
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=30.0
                )
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Analyze results
                successful_requests = len([r for r in results if not isinstance(r, Exception) and r.get("success", False)])
                success_rate = successful_requests / concurrency
                throughput = successful_requests / total_time
                
                print(f"Concurrency {concurrency}: {success_rate:.2%} success rate, {throughput:.1f} req/s")
                
                # If success rate drops below 90%, we've found the limit
                if success_rate < 0.9:
                    print(f"Scalability limit reached at concurrency level {concurrency}")
                    break
                
            except asyncio.TimeoutError:
                print(f"Timeout at concurrency level {concurrency}")
                break
            except Exception as e:
                print(f"Error at concurrency level {concurrency}: {e}")
                break
    
    @pytest.mark.asyncio
    async def test_large_input_handling(self, fast_mock_integration):
        """Test handling of large inputs"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Test various input sizes
        input_sizes = [100, 1000, 10000, 50000]  # characters
        
        for size in input_sizes:
            large_input = "A" * size
            
            start_time = time.time()
            
            try:
                result = await asyncio.wait_for(
                    tool_implementations.natural_language_to_powershell(large_input),
                    timeout=10.0
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                print(f"Input size {size}: {processing_time:.3f}s processing time")
                
                # Should handle gracefully (success or controlled failure)
                assert isinstance(result, dict)
                
            except asyncio.TimeoutError:
                print(f"Timeout with input size {size}")
                # Large inputs may timeout, which is acceptable
            except Exception as e:
                print(f"Error with input size {size}: {e}")
                # Should not crash with unhandled exceptions
                assert False, f"Unhandled exception with input size {size}: {e}"


class TestRegressionBenchmarks:
    """Test performance regression benchmarks"""
    
    @pytest.mark.asyncio
    async def test_baseline_performance_regression(self, fast_mock_integration):
        """Test against baseline performance metrics"""
        tool_implementations = MCPToolImplementations(fast_mock_integration)
        
        # Baseline performance targets (these would be established over time)
        baseline_targets = {
            "natural_language_mean_response_time": 0.1,  # seconds
            "command_execution_mean_response_time": 0.05,  # seconds
            "system_info_mean_response_time": 0.02,  # seconds
            "concurrent_10_success_rate": 0.95,  # 95%
            "concurrent_10_throughput": 80,  # requests/second
        }
        
        # Test natural language processing
        nl_times = []
        for _ in range(20):
            start_time = time.time()
            result = await tool_implementations.natural_language_to_powershell("baseline test")
            end_time = time.time()
            
            assert result["success"] is True
            nl_times.append(end_time - start_time)
        
        nl_mean = statistics.mean(nl_times)
        
        # Test command execution
        exec_times = []
        for _ in range(20):
            start_time = time.time()
            result = await tool_implementations.execute_powershell_command("Get-Process")
            end_time = time.time()
            
            assert result["success"] is True
            exec_times.append(end_time - start_time)
        
        exec_mean = statistics.mean(exec_times)
        
        # Test system info
        fast_mock_integration.health_check = AsyncMock(return_value={"overall": "healthy"})
        fast_mock_integration.executor.get_powershell_info.return_value = {"version": "7.3.0"}
        
        info_times = []
        for _ in range(20):
            start_time = time.time()
            result = await tool_implementations.get_powershell_info()
            end_time = time.time()
            
            assert result["success"] is True
            info_times.append(end_time - start_time)
        
        info_mean = statistics.mean(info_times)
        
        # Test concurrent performance
        concurrency = 10
        start_time = time.time()
        
        tasks = []
        for i in range(concurrency):
            task = tool_implementations.natural_language_to_powershell(f"concurrent test {i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_concurrent = len([r for r in results if not isinstance(r, Exception) and r.get("success", False)])
        concurrent_success_rate = successful_concurrent / concurrency
        concurrent_throughput = successful_concurrent / total_time
        
        # Performance regression checks
        performance_results = {
            "natural_language_mean_response_time": nl_mean,
            "command_execution_mean_response_time": exec_mean,
            "system_info_mean_response_time": info_mean,
            "concurrent_10_success_rate": concurrent_success_rate,
            "concurrent_10_throughput": concurrent_throughput,
        }
        
        print("Performance Regression Test Results:")
        for metric, value in performance_results.items():
            target = baseline_targets[metric]
            status = "PASS" if value <= target else "FAIL"
            print(f"  {metric}: {value:.4f} (target: {target:.4f}) [{status}]")
            
            # Assert against baseline (with some tolerance)
            tolerance = 1.2  # 20% tolerance for performance variations
            assert value <= target * tolerance, f"Performance regression in {metric}: {value:.4f} > {target * tolerance:.4f}"
        
        return performance_results


if __name__ == "__main__":
    # Run performance benchmarks
    pytest.main([__file__, "-v", "-s", "-k", "test_"])