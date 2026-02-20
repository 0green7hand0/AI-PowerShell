"""
响应时间测试

测试系统在本地AI模型推理条件下的响应时间性能。
验证平均响应时间 < 2秒的要求。
"""

import pytest
import time
import statistics
from pathlib import Path
from typing import List, Dict

from src.main import PowerShellAssistant
from src.interfaces.base import Suggestion, ExecutionResult, Context


class TestResponseTime:
    """响应时间测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手（本地AI模型配置）"""
        config_file = tmp_path / "response_time_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"
  temperature: 0.7
  max_tokens: 512
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
  file: "logs/response_time_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/response_time"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def get_test_scenarios(self) -> List[Dict[str, str]]:
        """获取测试场景集合"""
        return [
            # 简单命令场景
            {"category": "简单命令", "input": "显示当前时间"},
            {"category": "简单命令", "input": "查看当前目录"},
            {"category": "简单命令", "input": "列出所有文件"},
            {"category": "简单命令", "input": "查看IP地址"},
            {"category": "简单命令", "input": "显示进程列表"},
            
            # 中等复杂度命令场景
            {"category": "中等复杂度", "input": "创建新文件夹并设置权限"},
            {"category": "中等复杂度", "input": "查找包含特定文本的文件"},
            {"category": "中等复杂度", "input": "查看系统服务状态并过滤运行中的服务"},
            {"category": "中等复杂度", "input": "测试网络连接并显示详细信息"},
            {"category": "中等复杂度", "input": "查看磁盘空间使用情况并排序"},
            
            # 复杂命令场景
            {"category": "复杂命令", "input": "批量重命名文件并添加时间戳"},
            {"category": "复杂命令", "input": "监控进程CPU使用情况并生成报告"},
            {"category": "复杂命令", "input": "设置定时任务并配置触发条件"},
            {"category": "复杂命令", "input": "分析系统事件日志并提取错误信息"},
            {"category": "复杂命令", "input": "创建PowerShell函数并添加参数验证"},
        ]
    
    def test_single_command_response_time(self, assistant):
        """测试单个命令的响应时间"""
        test_scenarios = self.get_test_scenarios()
        context = assistant._build_context()
        
        latencies = []
        category_latencies = {}
        
        print(f"\n单个命令响应时间测试")
        print("=" * 80)
        
        for scenario in test_scenarios:
            category = scenario["category"]
            user_input = scenario["input"]
            
            # 测量响应时间
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            latency = time.time() - start_time
            
            latencies.append(latency)
            
            # 按类别统计
            if category not in category_latencies:
                category_latencies[category] = []
            category_latencies[category].append(latency)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            assert suggestion.generated_command is not None
            
            print(f"{category}: '{user_input}' -> {latency*1000:.2f}ms")
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        print("\n" + "=" * 80)
        print(f"单个命令响应时间统计:")
        print(f"  平均响应时间: {avg_latency*1000:.2f}ms")
        print(f"  中位响应时间: {median_latency*1000:.2f}ms")
        print(f"  最大响应时间: {max_latency*1000:.2f}ms")
        print(f"  最小响应时间: {min_latency*1000:.2f}ms")
        
        # 按类别统计
        print(f"\n按类别响应时间统计:")
        for category, category_times in category_latencies.items():
            cat_avg = statistics.mean(category_times)
            print(f"  {category}: {cat_avg*1000:.2f}ms")
        
        # 性能断言：平均响应时间 < 2秒
        assert avg_latency < 2.0, f"平均响应时间 {avg_latency:.3f}s 超过要求的 2秒"
        
        # 性能断言：95%的请求响应时间 < 3秒
        sorted_latencies = sorted(latencies)
        p95_latency = sorted_latencies[int(len(latencies) * 0.95)]
        assert p95_latency < 3.0, f"95%响应时间 {p95_latency:.3f}s 超过 3秒"
        
        print(f"\n95%响应时间: {p95_latency*1000:.2f}ms")
    
    def test_batch_response_time(self, assistant):
        """测试批量命令的响应时间"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件",
            "查看IP地址",
            "显示进程列表",
            "查看服务状态",
            "查看磁盘空间",
            "测试网络连接",
            "查看环境变量",
            "查看系统信息"
        ]
        
        context = assistant._build_context()
        latencies = []
        
        print(f"\n批量命令响应时间测试")
        print("=" * 80)
        
        for i, user_input in enumerate(test_inputs, 1):
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            latency = time.time() - start_time
            
            latencies.append(latency)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            
            print(f"请求 {i}/{len(test_inputs)}: '{user_input}' -> {latency*1000:.2f}ms")
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        total_time = sum(latencies)
        throughput = len(test_inputs) / total_time if total_time > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"批量响应时间统计:")
        print(f"  总请求数: {len(test_inputs)}")
        print(f"  总时间: {total_time:.2f}s")
        print(f"  平均响应时间: {avg_latency*1000:.2f}ms")
        print(f"  吞吐量: {throughput:.2f} 请求/秒")
        
        # 性能断言：平均响应时间 < 2秒
        assert avg_latency < 2.0, f"批量平均响应时间 {avg_latency:.3f}s 超过要求的 2秒"
    
    def test_cache_effect_response_time(self, assistant):
        """测试缓存对响应时间的影响"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件"
        ]
        
        context = assistant._build_context()
        first_latencies = []
        cached_latencies = []
        
        print(f"\n缓存效果响应时间测试")
        print("=" * 80)
        
        for user_input in test_inputs:
            # 第一次请求（无缓存）
            start_time = time.time()
            suggestion1 = assistant.ai_engine.translate_natural_language(user_input, context)
            first_latency = time.time() - start_time
            first_latencies.append(first_latency)
            
            # 第二次请求（应该有缓存）
            start_time = time.time()
            suggestion2 = assistant.ai_engine.translate_natural_language(user_input, context)
            cached_latency = time.time() - start_time
            cached_latencies.append(cached_latency)
            
            # 验证结果
            assert isinstance(suggestion1, Suggestion)
            assert isinstance(suggestion2, Suggestion)
            assert suggestion1.generated_command == suggestion2.generated_command
            
            speedup = first_latency / cached_latency if cached_latency > 0 else 0
            print(f"'{user_input}':")
            print(f"  首次响应: {first_latency*1000:.2f}ms")
            print(f"  缓存响应: {cached_latency*1000:.2f}ms")
            print(f"  加速比: {speedup:.2f}x")
        
        # 计算统计数据
        avg_first_latency = statistics.mean(first_latencies)
        avg_cached_latency = statistics.mean(cached_latencies)
        avg_speedup = avg_first_latency / avg_cached_latency if avg_cached_latency > 0 else 0
        
        print("\n" + "=" * 80)
        print(f"缓存效果统计:")
        print(f"  平均首次响应: {avg_first_latency*1000:.2f}ms")
        print(f"  平均缓存响应: {avg_cached_latency*1000:.2f}ms")
        print(f"  平均加速比: {avg_speedup:.2f}x")
        
        # 验证缓存确实有效果
        assert avg_cached_latency < avg_first_latency, "缓存没有提高性能"
    
    def test_end_to_end_response_time(self, assistant):
        """测试端到端响应时间（包括执行）"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件"
        ]
        
        latencies = []
        
        print(f"\n端到端响应时间测试")
        print("=" * 80)
        
        for user_input in test_inputs:
            start_time = time.time()
            result = assistant.process_request(user_input, auto_execute=True)
            latency = time.time() - start_time
            
            latencies.append(latency)
            
            # 验证结果
            assert isinstance(result, ExecutionResult)
            
            print(f"'{user_input}': {latency*1000:.2f}ms")
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        
        print("\n" + "=" * 80)
        print(f"端到端响应时间统计:")
        print(f"  平均响应时间: {avg_latency*1000:.2f}ms")
        
        # 性能断言：端到端平均响应时间 < 2秒
        assert avg_latency < 2.0, f"端到端平均响应时间 {avg_latency:.3f}s 超过要求的 2秒"
    
    def test_load_response_time(self, assistant):
        """测试负载下的响应时间"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件",
            "查看IP地址",
            "显示进程列表"
        ]
        
        context = assistant._build_context()
        latencies = []
        
        print(f"\n负载下响应时间测试")
        print("=" * 80)
        
        # 执行20个请求模拟负载
        for i in range(20):
            user_input = test_inputs[i % len(test_inputs)]
            
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            latency = time.time() - start_time
            
            latencies.append(latency)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            
            # 每5个请求打印一次进度
            if (i + 1) % 5 == 0:
                avg_so_far = statistics.mean(latencies[:i+1])
                print(f"完成 {i+1}/20 请求, 平均响应时间: {avg_so_far*1000:.2f}ms")
        
        # 计算统计数据
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print("\n" + "=" * 80)
        print(f"负载下响应时间统计:")
        print(f"  平均响应时间: {avg_latency*1000:.2f}ms")
        print(f"  中位响应时间: {median_latency*1000:.2f}ms")
        print(f"  95%响应时间: {p95_latency*1000:.2f}ms")
        
        # 性能断言：负载下平均响应时间 < 2秒
        assert avg_latency < 2.0, f"负载下平均响应时间 {avg_latency:.3f}s 超过要求的 2秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
