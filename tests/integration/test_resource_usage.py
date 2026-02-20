"""
资源占用测试

测试系统在空闲和负载情况下的内存和CPU占用情况。
验证空闲时内存占用 < 100MB，CPU占用 < 5% 的要求。
"""

import pytest
import time
import psutil
import os
import gc
from pathlib import Path
from typing import List, Dict, Tuple

from src.main import PowerShellAssistant
from src.interfaces.base import Suggestion, Context


class TestResourceUsage:
    """资源占用测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "resource_usage_config.yaml"
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
  file: "logs/resource_usage_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/resource_usage"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def get_process_memory_usage(self) -> int:
        """获取当前进程的内存使用情况（MB）"""
        process = psutil.Process(os.getpid())
        return int(process.memory_info().rss / 1024 / 1024)
    
    def get_process_cpu_usage(self, interval: float = 1.0) -> float:
        """获取当前进程的CPU使用情况（%）"""
        process = psutil.Process(os.getpid())
        return process.cpu_percent(interval=interval)
    
    def get_system_cpu_usage(self, interval: float = 1.0) -> float:
        """获取系统的CPU使用情况（%）"""
        return psutil.cpu_percent(interval=interval)
    
    def test_idle_resource_usage(self, assistant):
        """测试空闲时的资源占用"""
        # 等待系统稳定
        time.sleep(2)
        
        # 强制垃圾回收
        gc.collect()
        time.sleep(1)
        
        # 测量空闲时的资源占用
        memory_usages = []
        cpu_usages = []
        
        print(f"\n空闲资源占用测试")
        print("=" * 80)
        
        # 连续测量5次，取平均值
        for i in range(5):
            memory_usage = self.get_process_memory_usage()
            cpu_usage = self.get_process_cpu_usage(interval=0.5)
            
            memory_usages.append(memory_usage)
            cpu_usages.append(cpu_usage)
            
            print(f"测量 {i+1}/5: 内存={memory_usage}MB, CPU={cpu_usage:.1f}%")
            time.sleep(0.5)
        
        # 计算平均值
        avg_memory = sum(memory_usages) / len(memory_usages)
        avg_cpu = sum(cpu_usages) / len(cpu_usages)
        
        print("\n" + "=" * 80)
        print(f"空闲资源占用统计:")
        print(f"  平均内存占用: {avg_memory:.1f}MB")
        print(f"  平均CPU占用: {avg_cpu:.1f}%")
        print(f"  最大内存占用: {max(memory_usages)}MB")
        print(f"  最大CPU占用: {max(cpu_usages):.1f}%")
        
        # 性能断言：空闲时内存占用 < 100MB
        assert avg_memory < 100.0, f"空闲时平均内存占用 {avg_memory:.1f}MB 超过要求的 100MB"
        
        # 性能断言：空闲时CPU占用 < 5%
        assert avg_cpu < 5.0, f"空闲时平均CPU占用 {avg_cpu:.1f}% 超过要求的 5%"
    
    def test_load_resource_usage(self, assistant):
        """测试负载时的资源占用"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件",
            "查看IP地址",
            "显示进程列表"
        ]
        
        context = assistant._build_context()
        
        # 测量负载前的资源占用
        pre_memory = self.get_process_memory_usage()
        pre_cpu = self.get_process_cpu_usage(interval=0.5)
        
        print(f"\n负载资源占用测试")
        print("=" * 80)
        print(f"负载前: 内存={pre_memory}MB, CPU={pre_cpu:.1f}%")
        
        # 执行负载测试
        memory_usages = []
        cpu_usages = []
        
        for i, user_input in enumerate(test_inputs, 1):
            # 执行前测量
            exec_memory = self.get_process_memory_usage()
            
            # 执行命令
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            exec_time = time.time() - start_time
            
            # 执行后测量
            post_memory = self.get_process_memory_usage()
            cpu_usage = self.get_process_cpu_usage(interval=0.5)
            
            memory_usages.append(post_memory)
            cpu_usages.append(cpu_usage)
            
            memory_diff = post_memory - exec_memory
            
            print(f"执行 {i}/{len(test_inputs)}: '{user_input}'")
            print(f"  执行时间: {exec_time*1000:.2f}ms")
            print(f"  内存变化: {memory_diff:+d}MB")
            print(f"  当前内存: {post_memory}MB")
            print(f"  当前CPU: {cpu_usage:.1f}%")
            print()
        
        # 计算负载时的资源占用
        avg_memory = sum(memory_usages) / len(memory_usages)
        avg_cpu = sum(cpu_usages) / len(cpu_usages)
        max_memory = max(memory_usages)
        max_cpu = max(cpu_usages)
        
        print("" + "=" * 80)
        print(f"负载资源占用统计:")
        print(f"  平均内存占用: {avg_memory:.1f}MB")
        print(f"  平均CPU占用: {avg_cpu:.1f}%")
        print(f"  最大内存占用: {max_memory}MB")
        print(f"  最大CPU占用: {max_cpu:.1f}%")
        print(f"  内存增长: {max_memory - pre_memory:+d}MB")
        
        # 性能断言：负载时内存占用不应过高
        assert max_memory < 200.0, f"负载时最大内存占用 {max_memory}MB 过高"
        
        # 性能断言：负载时CPU占用不应过高
        assert max_cpu < 50.0, f"负载时最大CPU占用 {max_cpu:.1f}% 过高"
    
    def test_resource_recovery(self, assistant):
        """测试资源回收能力"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件",
            "查看IP地址",
            "显示进程列表"
        ]
        
        context = assistant._build_context()
        
        # 测量初始资源占用
        initial_memory = self.get_process_memory_usage()
        
        print(f"\n资源回收测试")
        print("=" * 80)
        print(f"初始内存: {initial_memory}MB")
        
        # 执行多个命令
        for user_input in test_inputs:
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            assert isinstance(suggestion, Suggestion)
        
        # 执行后测量资源占用
        post_exec_memory = self.get_process_memory_usage()
        
        print(f"执行后内存: {post_exec_memory}MB")
        print(f"内存增长: {post_exec_memory - initial_memory:+d}MB")
        
        # 强制垃圾回收
        gc.collect()
        time.sleep(2)
        
        # 测量垃圾回收后的资源占用
        recovered_memory = self.get_process_memory_usage()
        
        print(f"垃圾回收后内存: {recovered_memory}MB")
        print(f"内存回收: {post_exec_memory - recovered_memory:+d}MB")
        
        # 计算内存回收率
        if post_exec_memory > initial_memory:
            memory_increase = post_exec_memory - initial_memory
            memory_recovery = post_exec_memory - recovered_memory
            recovery_rate = (memory_recovery / memory_increase) * 100 if memory_increase > 0 else 0
            print(f"内存回收率: {recovery_rate:.1f}%")
        
        # 性能断言：垃圾回收后内存占用应接近初始值
        memory_diff_after_recovery = abs(recovered_memory - initial_memory)
        assert memory_diff_after_recovery < 50, f"垃圾回收后内存差异 {memory_diff_after_recovery}MB 过大"
    
    def test_long_running_resource_usage(self, assistant):
        """测试长时间运行的资源占用"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件"
        ]
        
        context = assistant._build_context()
        
        memory_usages = []
        cpu_usages = []
        
        print(f"\n长时间运行资源占用测试")
        print("=" * 80)
        
        # 运行20个周期
        for cycle in range(20):
            user_input = test_inputs[cycle % len(test_inputs)]
            
            # 执行命令
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            assert isinstance(suggestion, Suggestion)
            
            # 测量资源占用
            memory_usage = self.get_process_memory_usage()
            cpu_usage = self.get_process_cpu_usage(interval=0.2)
            
            memory_usages.append(memory_usage)
            cpu_usages.append(cpu_usage)
            
            # 每5个周期打印一次
            if (cycle + 1) % 5 == 0:
                avg_memory = sum(memory_usages[-5:]) / 5
                avg_cpu = sum(cpu_usages[-5:]) / 5
                print(f"周期 {cycle+1}/20: 平均内存={avg_memory:.1f}MB, 平均CPU={avg_cpu:.1f}%")
            
            # 短暂休息
            time.sleep(0.1)
        
        # 计算统计数据
        avg_memory = sum(memory_usages) / len(memory_usages)
        avg_cpu = sum(cpu_usages) / len(cpu_usages)
        max_memory = max(memory_usages)
        max_cpu = max(cpu_usages)
        
        print("\n" + "=" * 80)
        print(f"长时间运行资源占用统计:")
        print(f"  平均内存占用: {avg_memory:.1f}MB")
        print(f"  平均CPU占用: {avg_cpu:.1f}%")
        print(f"  最大内存占用: {max_memory}MB")
        print(f"  最大CPU占用: {max_cpu:.1f}%")
        
        # 性能断言：长时间运行内存占用不应持续增长
        # 检查内存使用趋势
        if len(memory_usages) >= 10:
            first_half = memory_usages[:10]
            second_half = memory_usages[10:]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            memory_growth = avg_second - avg_first
            
            print(f"\n内存趋势分析:")
            print(f"  前10个周期平均: {avg_first:.1f}MB")
            print(f"  后10个周期平均: {avg_second:.1f}MB")
            print(f"  内存增长: {memory_growth:+f}MB")
            
            # 内存增长不应过大
            assert abs(memory_growth) < 30, f"长时间运行内存增长 {memory_growth:+f}MB 过大"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
