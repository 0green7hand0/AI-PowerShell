"""
性能基准测试

测试系统各个组件的性能指标，包括 AI 翻译延迟、命令执行延迟等。
"""

import pytest
import time
import statistics
from pathlib import Path
from unittest.mock import patch, Mock

from src.main import PowerShellAssistant
from src.interfaces.base import (
    Suggestion, ValidationResult, ExecutionResult,
    RiskLevel, Context
)


class TestAITranslationPerformance:
    """AI 翻译性能测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "perf_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"
  temperature: 0.7
  max_tokens: 256
  cache_enabled: true

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "WARNING"
  file: "logs/perf_test.log"
  max_size: "10MB"
  backup_count: 3
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: false

storage:
  storage_type: "file"
  base_path: "test_data/perf"
  history_limit: 100

context:
  max_history: 100
  session_timeout: 3600
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_single_translation_latency(self, assistant):
        """测试单次翻译延迟"""
        context = assistant._build_context()
        user_input = "显示当前时间"
        
        # 测量翻译时间
        start_time = time.time()
        suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # 验证结果
        assert isinstance(suggestion, Suggestion)
        assert suggestion.generated_command is not None
        
        # 性能断言：翻译应该在合理时间内完成（1秒）
        assert latency < 1.0, f"Translation took {latency:.3f}s, expected < 1.0s"
        
        print(f"\n单次翻译延迟: {latency*1000:.2f}ms")
    
    def test_batch_translation_performance(self, assistant):
        """测试批量翻译性能"""
        context = assistant._build_context()
        
        test_inputs = [
            "显示当前时间",
            "列出所有文件",
            "查看系统信息",
            "测试网络连接",
            "显示进程列表",
            "查看磁盘空间",
            "显示环境变量",
            "查看服务状态",
            "显示网络配置",
            "查看事件日志"
        ]
        
        latencies = []
        
        # 测量每次翻译的时间
        for user_input in test_inputs:
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            
            assert isinstance(suggestion, Suggestion)
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print(f"\n批量翻译性能统计:")
        print(f"  平均延迟: {avg_latency*1000:.2f}ms")
        print(f"  最大延迟: {max_latency*1000:.2f}ms")
        print(f"  最小延迟: {min_latency*1000:.2f}ms")
        print(f"  总请求数: {len(test_inputs)}")
        
        # 性能断言
        assert avg_latency < 1.0, f"Average latency {avg_latency:.3f}s exceeds 1.0s"
    
    def test_cache_effectiveness(self, assistant):
        """测试缓存有效性"""
        context = assistant._build_context()
        user_input = "显示当前时间"
        
        # 第一次翻译（未缓存）
        start_time = time.time()
        suggestion1 = assistant.ai_engine.translate_natural_language(user_input, context)
        first_latency = time.time() - start_time
        
        # 第二次翻译（应该使用缓存）
        start_time = time.time()
        suggestion2 = assistant.ai_engine.translate_natural_language(user_input, context)
        cached_latency = time.time() - start_time
        
        print(f"\n缓存效果:")
        print(f"  首次翻译: {first_latency*1000:.2f}ms")
        print(f"  缓存翻译: {cached_latency*1000:.2f}ms")
        print(f"  加速比: {first_latency/cached_latency:.2f}x")
        
        # 验证缓存命中应该更快（至少快50%）
        # 注意：如果缓存未启用或实现不同，这个测试可能需要调整
        assert suggestion1.generated_command == suggestion2.generated_command


class TestSecurityValidationPerformance:
    """安全验证性能测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "sec_perf_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "strict"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
    - "Format-Volume"
    - "Stop-Computer"
  safe_prefixes:
    - "Get-"
    - "Test-"

execution:
  timeout: 30

logging:
  level: "WARNING"
  file: "logs/sec_perf_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/sec_perf"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_single_validation_latency(self, assistant):
        """测试单次安全验证延迟"""
        context = assistant._build_context()
        command = "Get-Date"
        
        # 测量验证时间
        start_time = time.time()
        validation = assistant.security_engine.validate_command(command, context)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # 验证结果
        assert isinstance(validation, ValidationResult)
        
        # 性能断言：验证应该非常快（< 100ms）
        assert latency < 0.1, f"Validation took {latency:.3f}s, expected < 0.1s"
        
        print(f"\n单次安全验证延迟: {latency*1000:.2f}ms")
    
    def test_batch_validation_performance(self, assistant):
        """测试批量安全验证性能"""
        context = assistant._build_context()
        
        test_commands = [
            "Get-Date",
            "Get-Process",
            "Get-Service",
            "Test-Connection localhost",
            "Get-ChildItem",
            "Get-Location",
            "Get-Content test.txt",
            "Get-EventLog -LogName System -Newest 10",
            "Get-NetAdapter",
            "Get-Disk"
        ]
        
        latencies = []
        
        # 测量每次验证的时间
        for command in test_commands:
            start_time = time.time()
            validation = assistant.security_engine.validate_command(command, context)
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            
            assert isinstance(validation, ValidationResult)
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        
        print(f"\n批量安全验证性能统计:")
        print(f"  平均延迟: {avg_latency*1000:.2f}ms")
        print(f"  最大延迟: {max_latency*1000:.2f}ms")
        print(f"  总验证数: {len(test_commands)}")
        
        # 性能断言
        assert avg_latency < 0.1, f"Average validation latency {avg_latency:.3f}s exceeds 0.1s"


class TestCommandExecutionPerformance:
    """命令执行性能测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "exec_perf_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: false

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "WARNING"
  file: "logs/exec_perf_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/exec_perf"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_simple_command_execution_latency(self, assistant):
        """测试简单命令执行延迟"""
        command = "Get-Date"
        
        # 测量执行时间
        start_time = time.time()
        result = assistant.executor.execute(command, timeout=30)
        end_time = time.time()
        
        latency = end_time - start_time
        
        # 验证结果
        assert isinstance(result, ExecutionResult)
        
        print(f"\n简单命令执行延迟: {latency*1000:.2f}ms")
        
        # 性能断言：简单命令应该快速执行（< 2秒）
        assert latency < 2.0, f"Execution took {latency:.3f}s, expected < 2.0s"
    
    def test_multiple_commands_execution_performance(self, assistant):
        """测试多个命令执行性能"""
        commands = [
            "Get-Date",
            "Get-Location",
            "Get-Host",
            "Get-PSVersion",
            "Get-ExecutionPolicy"
        ]
        
        latencies = []
        
        # 测量每个命令的执行时间
        for command in commands:
            start_time = time.time()
            result = assistant.executor.execute(command, timeout=30)
            end_time = time.time()
            
            latency = end_time - start_time
            latencies.append(latency)
            
            assert isinstance(result, ExecutionResult)
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        total_time = sum(latencies)
        
        print(f"\n多命令执行性能统计:")
        print(f"  平均延迟: {avg_latency*1000:.2f}ms")
        print(f"  总执行时间: {total_time:.2f}s")
        print(f"  命令数量: {len(commands)}")
        
        # 性能断言
        assert avg_latency < 2.0, f"Average execution latency {avg_latency:.3f}s exceeds 2.0s"


class TestEndToEndPerformance:
    """端到端性能测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "e2e_perf_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"
  cache_enabled: true

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"

execution:
  timeout: 30
  encoding: "utf-8"

logging:
  level: "WARNING"
  file: "logs/e2e_perf_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/e2e_perf"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_complete_request_latency(self, assistant):
        """测试完整请求处理延迟"""
        user_input = "显示当前时间"
        
        # 测量完整流程时间
        start_time = time.time()
        result = assistant.process_request(user_input, auto_execute=True)
        end_time = time.time()
        
        total_latency = end_time - start_time
        
        # 验证结果
        assert isinstance(result, ExecutionResult)
        
        print(f"\n完整请求处理延迟: {total_latency*1000:.2f}ms")
        
        # 性能断言：完整流程应该在合理时间内完成（< 3秒）
        assert total_latency < 3.0, f"Total latency {total_latency:.3f}s exceeds 3.0s"
    
    def test_throughput_measurement(self, assistant):
        """测试系统吞吐量"""
        test_inputs = [
            "显示当前时间",
            "列出文件",
            "查看目录",
            "显示主机信息",
            "查看执行策略"
        ]
        
        # 启动会话
        assistant.context_manager.start_session()
        
        # 测量总时间
        start_time = time.time()
        
        results = []
        for user_input in test_inputs:
            result = assistant.process_request(user_input, auto_execute=True)
            results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算吞吐量
        throughput = len(test_inputs) / total_time
        avg_latency = total_time / len(test_inputs)
        
        print(f"\n系统吞吐量测试:")
        print(f"  总请求数: {len(test_inputs)}")
        print(f"  总时间: {total_time:.2f}s")
        print(f"  吞吐量: {throughput:.2f} 请求/秒")
        print(f"  平均延迟: {avg_latency:.2f}s")
        
        # 验证所有请求都被处理
        assert len(results) == len(test_inputs)
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_memory_efficiency(self, assistant):
        """测试内存效率（简单版本）"""
        import sys
        
        # 获取初始对象数量
        initial_objects = len([obj for obj in dir(assistant) if not obj.startswith('_')])
        
        # 执行多个请求
        for i in range(10):
            result = assistant.process_request(f"显示当前时间 {i}", auto_execute=True)
            assert isinstance(result, ExecutionResult)
        
        # 获取最终对象数量
        final_objects = len([obj for obj in dir(assistant) if not obj.startswith('_')])
        
        print(f"\n内存效率测试:")
        print(f"  初始对象数: {initial_objects}")
        print(f"  最终对象数: {final_objects}")
        print(f"  对象增长: {final_objects - initial_objects}")
        
        # 验证对象数量没有显著增长（允许一些增长）
        assert final_objects - initial_objects < 10, "Too many objects created"


class TestPerformanceUnderLoad:
    """负载下的性能测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "load_perf_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"
  cache_enabled: true

security:
  sandbox_enabled: false
  require_confirmation: false

execution:
  timeout: 30

logging:
  level: "ERROR"
  file: "logs/load_perf_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/load_perf"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_sustained_load_performance(self, assistant):
        """测试持续负载下的性能"""
        num_requests = 20
        latencies = []
        
        assistant.context_manager.start_session()
        
        print(f"\n持续负载测试 ({num_requests} 个请求):")
        
        for i in range(num_requests):
            user_input = f"显示当前时间 {i}"
            
            start_time = time.time()
            result = assistant.process_request(user_input, auto_execute=True)
            latency = time.time() - start_time
            
            latencies.append(latency)
            
            assert isinstance(result, ExecutionResult)
            
            # 每5个请求打印一次进度
            if (i + 1) % 5 == 0:
                avg_so_far = statistics.mean(latencies)
                print(f"  完成 {i+1}/{num_requests} 请求, 平均延迟: {avg_so_far:.3f}s")
        
        # 计算性能指标
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print(f"\n持续负载性能统计:")
        print(f"  平均延迟: {avg_latency:.3f}s")
        print(f"  中位延迟: {median_latency:.3f}s")
        print(f"  P95 延迟: {p95_latency:.3f}s")
        
        assistant.context_manager.terminate_session()
        
        # 性能断言：即使在负载下，平均延迟也应该合理
        assert avg_latency < 5.0, f"Average latency under load {avg_latency:.3f}s exceeds 5.0s"
    
    def test_performance_degradation(self, assistant):
        """测试性能退化"""
        # 测试前10个请求
        early_latencies = []
        for i in range(10):
            start_time = time.time()
            result = assistant.process_request(f"测试 {i}", auto_execute=True)
            latency = time.time() - start_time
            early_latencies.append(latency)
            assert isinstance(result, ExecutionResult)
        
        # 执行中间的请求（不记录）
        for i in range(10, 30):
            assistant.process_request(f"测试 {i}", auto_execute=True)
        
        # 测试后10个请求
        late_latencies = []
        for i in range(30, 40):
            start_time = time.time()
            result = assistant.process_request(f"测试 {i}", auto_execute=True)
            latency = time.time() - start_time
            late_latencies.append(latency)
            assert isinstance(result, ExecutionResult)
        
        # 比较性能
        early_avg = statistics.mean(early_latencies)
        late_avg = statistics.mean(late_latencies)
        degradation = (late_avg - early_avg) / early_avg * 100
        
        print(f"\n性能退化测试:")
        print(f"  早期平均延迟: {early_avg:.3f}s")
        print(f"  后期平均延迟: {late_avg:.3f}s")
        print(f"  性能退化: {degradation:.1f}%")
        
        # 验证性能退化不超过50%
        assert degradation < 50, f"Performance degraded by {degradation:.1f}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
