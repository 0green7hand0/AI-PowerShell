"""
中文自然语言支持测试

测试系统对中文自然语言输入的支持能力，以及生成中文解释输出的能力。
"""

import pytest
import time
from pathlib import Path
from typing import List, Dict

from src.main import PowerShellAssistant
from src.interfaces.base import Suggestion, ExecutionResult, Context


class TestChineseLanguageSupport:
    """中文自然语言支持测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "chinese_language_config.yaml"
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
  file: "logs/chinese_language_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/chinese_language"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def get_chinese_test_cases(self) -> List[Dict[str, str]]:
        """获取中文测试用例集合"""
        return [
            # 基础命令（中文表达）
            {"category": "基础命令", "input": "显示当前时间", "description": "简单中文指令"},
            {"category": "基础命令", "input": "查看当前目录", "description": "简单中文指令"},
            {"category": "基础命令", "input": "列出所有文件", "description": "简单中文指令"},
            {"category": "基础命令", "input": "查看IP地址", "description": "简单中文指令"},
            {"category": "基础命令", "input": "显示进程列表", "description": "简单中文指令"},
            
            # 复杂命令（中文表达）
            {"category": "复杂命令", "input": "创建新文件夹并设置权限", "description": "复合中文指令"},
            {"category": "复杂命令", "input": "查找包含特定文本的文件", "description": "复合中文指令"},
            {"category": "复杂命令", "input": "查看系统服务状态并过滤运行中的服务", "description": "复合中文指令"},
            {"category": "复杂命令", "input": "测试网络连接并显示详细信息", "description": "复合中文指令"},
            {"category": "复杂命令", "input": "查看磁盘空间使用情况并排序", "description": "复合中文指令"},
            
            # 口语化表达
            {"category": "口语表达", "input": "给我看看现在几点了", "description": "口语化中文指令"},
            {"category": "口语表达", "input": "帮我列一下当前文件夹里的东西", "description": "口语化中文指令"},
            {"category": "口语表达", "input": "我想知道我的IP地址是多少", "description": "口语化中文指令"},
            {"category": "口语表达", "input": "能不能查看一下正在运行的进程", "description": "口语化中文指令"},
            {"category": "口语表达", "input": "帮我检查一下网络通不通", "description": "口语化中文指令"},
            
            # 专业术语
            {"category": "专业术语", "input": "查询Windows服务状态", "description": "包含专业术语的中文指令"},
            {"category": "专业术语", "input": "监控CPU使用率", "description": "包含专业术语的中文指令"},
            {"category": "专业术语", "input": "配置防火墙规则", "description": "包含专业术语的中文指令"},
            {"category": "专业术语", "input": "管理计划任务", "description": "包含专业术语的中文指令"},
            {"category": "专业术语", "input": "分析系统事件日志", "description": "包含专业术语的中文指令"},
            
            # 歧义表达
            {"category": "歧义表达", "input": "查看文件", "description": "歧义中文指令"},
            {"category": "歧义表达", "input": "测试连接", "description": "歧义中文指令"},
            {"category": "歧义表达", "input": "显示信息", "description": "歧义中文指令"},
            {"category": "歧义表达", "input": "检查状态", "description": "歧义中文指令"},
            {"category": "歧义表达", "input": "管理进程", "description": "歧义中文指令"},
            
            # 长句子
            {"category": "长句子", "input": "请帮我显示当前系统的时间和日期，然后列出当前目录下的所有文件和文件夹", "description": "长句子中文指令"},
            {"category": "长句子", "input": "我需要查看当前系统中所有正在运行的进程，特别是那些占用CPU资源较高的进程", "description": "长句子中文指令"},
            {"category": "长句子", "input": "请检查本地网络连接状态，并测试与百度网站的连接是否正常", "description": "长句子中文指令"},
            
            # 特定场景
            {"category": "特定场景", "input": "备份重要文件", "description": "特定场景中文指令"},
            {"category": "特定场景", "input": "清理系统垃圾文件", "description": "特定场景中文指令"},
            {"category": "特定场景", "input": "优化系统性能", "description": "特定场景中文指令"},
            {"category": "特定场景", "input": "排查网络故障", "description": "特定场景中文指令"},
        ]
    
    def test_chinese_input_understanding(self, assistant):
        """测试中文输入理解能力"""
        test_cases = self.get_chinese_test_cases()
        context = assistant._build_context()
        
        successful_count = 0
        total_count = len(test_cases)
        
        print(f"\n中文输入理解测试: {total_count} 个中文场景")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            category = test_case["category"]
            user_input = test_case["input"]
            description = test_case["description"]
            
            # 测试中文输入
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            
            # 检查是否成功生成命令
            if suggestion.generated_command:
                successful_count += 1
                status = "✓ 成功"
            else:
                status = "✗ 失败"
            
            # 每10个测试打印一次进度
            if i % 10 == 0:
                success_rate = (successful_count / i) * 100
                print(f"测试 {i}/{total_count}: {category} - {description}")
                print(f"输入: '{user_input}'")
                print(f"生成命令: '{suggestion.generated_command}'")
                print(f"状态: {status}")
                print(f"当前成功率: {success_rate:.2f}%")
                print("-" * 80)
        
        # 计算最终成功率
        success_rate = (successful_count / total_count) * 100
        
        print("\n" + "=" * 80)
        print(f"测试完成: {successful_count}/{total_count} 成功")
        print(f"中文输入理解成功率: {success_rate:.2f}%")
        
        # 性能断言：中文输入理解成功率应高于90%
        assert success_rate >= 90.0, f"中文输入理解成功率 {success_rate:.2f}% 过低"
    
    def test_chinese_explanation_output(self, assistant):
        """测试中文解释输出能力"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件"
        ]
        
        context = assistant._build_context()
        chinese_explanation_count = 0
        total_count = len(test_inputs)
        
        print(f"\n中文解释输出测试: {total_count} 个场景")
        print("=" * 80)
        
        for user_input in test_inputs:
            # 测试中文输入并获取解释
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            
            # 检查解释是否为中文
            explanation = getattr(suggestion, 'explanation', '') or getattr(suggestion, 'description', '')
            
            # 简单判断是否包含中文字符
            contains_chinese = any('\u4e00' <= char <= '\u9fff' for char in explanation)
            
            if contains_chinese:
                chinese_explanation_count += 1
                status = "✓ 中文解释"
            else:
                status = "✗ 非中文解释"
            
            print(f"输入: '{user_input}'")
            print(f"生成命令: '{suggestion.generated_command}'")
            print(f"解释: '{explanation}'")
            print(f"状态: {status}")
            print()
        
        # 计算最终中文解释率
        chinese_explanation_rate = (chinese_explanation_count / total_count) * 100
        
        print("" + "=" * 80)
        print(f"测试完成: {chinese_explanation_count}/{total_count} 中文解释")
        print(f"中文解释输出率: {chinese_explanation_rate:.2f}%")
        
        # 性能断言：中文解释输出率应高于90%
        assert chinese_explanation_rate >= 90.0, f"中文解释输出率 {chinese_explanation_rate:.2f}% 过低"
    
    def test_chinese_variations(self, assistant):
        """测试中文表达变体"""
        variations = [
            {"base": "显示当前时间", "variations": ["显示现在的时间", "告诉我现在几点了", "查看当前的时间"]},
            {"base": "列出所有文件", "variations": ["列出所有的文件", "显示所有文件", "查看所有文件"]},
            {"base": "查看IP地址", "variations": ["查看我的IP地址", "显示IP地址", "获取IP地址"]},
        ]
        
        context = assistant._build_context()
        successful_variations = 0
        total_variations = 0
        
        print(f"\n中文表达变体测试")
        print("=" * 80)
        
        for item in variations:
            base_input = item["base"]
            base_suggestion = assistant.ai_engine.translate_natural_language(base_input, context)
            base_command = getattr(base_suggestion, 'generated_command', '')
            
            if not base_command:
                print(f"基础输入 '{base_input}' 未能生成命令，跳过变体测试")
                continue
            
            print(f"基础输入: '{base_input}'")
            print(f"基础命令: '{base_command}'")
            print()
            
            for variation in item["variations"]:
                total_variations += 1
                
                variation_suggestion = assistant.ai_engine.translate_natural_language(variation, context)
                variation_command = getattr(variation_suggestion, 'generated_command', '')
                
                # 检查变体是否成功生成命令
                if variation_command:
                    successful_variations += 1
                    status = "✓ 成功"
                else:
                    status = "✗ 失败"
                
                print(f"变体: '{variation}' -> {status}")
                if variation_command:
                    print(f"  生成命令: '{variation_command}'")
            
            print("-" * 80)
        
        if total_variations > 0:
            success_rate = (successful_variations / total_variations) * 100
            print(f"\n变体测试完成: {successful_variations}/{total_variations} 成功")
            print(f"中文变体成功率: {success_rate:.2f}%")
            
            # 性能断言：中文变体成功率应高于85%
            assert success_rate >= 85.0, f"中文变体成功率 {success_rate:.2f}% 过低"
        else:
            print("\n未进行变体测试（基础输入未能生成命令）")
    
    def test_chinese_end_to_end(self, assistant):
        """测试中文端到端流程"""
        test_inputs = [
            "显示当前时间",
            "查看当前目录",
            "列出所有文件"
        ]
        
        successful_count = 0
        total_count = len(test_inputs)
        
        print(f"\n中文端到端流程测试: {total_count} 个场景")
        print("=" * 80)
        
        for user_input in test_inputs:
            # 测试完整流程
            result = assistant.process_request(user_input, auto_execute=True)
            
            # 验证结果
            assert isinstance(result, ExecutionResult)
            
            # 检查是否成功执行
            if result.success:
                successful_count += 1
                status = "✓ 成功"
            else:
                status = "✗ 失败"
            
            print(f"输入: '{user_input}'")
            print(f"执行命令: '{result.command}'")
            print(f"执行状态: {status}")
            if not result.success and result.error:
                print(f"错误信息: '{result.error}'")
            print()
        
        # 计算最终成功率
        success_rate = (successful_count / total_count) * 100
        
        print("" + "=" * 80)
        print(f"端到端测试完成: {successful_count}/{total_count} 成功")
        print(f"中文端到端成功率: {success_rate:.2f}%")
        
        # 性能断言：中文端到端成功率应高于85%
        assert success_rate >= 85.0, f"中文端到端成功率 {success_rate:.2f}% 过低"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
