"""
AI 提供商测试
"""

import pytest
from src.ai_engine.providers import (
    AIProvider, MockProvider, get_provider
)
from src.interfaces.base import Context


class TestMockProvider:
    """模拟提供商测试"""
    
    def test_mock_provider_initialization(self):
        """测试模拟提供商初始化"""
        provider = MockProvider()
        assert provider is not None
    
    def test_mock_provider_is_available(self):
        """测试模拟提供商可用性"""
        provider = MockProvider()
        assert provider.is_available() is True
    
    def test_mock_provider_generate_files(self):
        """测试生成文件相关命令"""
        provider = MockProvider()
        context = Context(session_id="test")
        
        result = provider.generate("显示文件", context)
        assert result is not None
        assert "Get-ChildItem" in result.generated_command
    
    def test_mock_provider_generate_process(self):
        """测试生成进程相关命令"""
        provider = MockProvider()
        context = Context(session_id="test")
        
        result = provider.generate("显示进程", context)
        assert result is not None
        assert "Get-Process" in result.generated_command
    
    def test_mock_provider_generate_date(self):
        """测试生成时间相关命令"""
        provider = MockProvider()
        context = Context(session_id="test")
        
        result = provider.generate("显示时间", context)
        assert result is not None
        assert "Get-Date" in result.generated_command
    
    def test_mock_provider_generate_unknown(self):
        """测试生成未知命令"""
        provider = MockProvider()
        context = Context(session_id="test")
        
        result = provider.generate("完全未知的命令", context)
        assert result is not None
        assert result.generated_command is not None


class TestGetProvider:
    """提供商工厂函数测试"""
    
    def test_get_mock_provider(self):
        """测试获取模拟提供商"""
        provider = get_provider('mock', {})
        assert isinstance(provider, MockProvider)
    
    def test_get_provider_case_insensitive(self):
        """测试提供商名称大小写不敏感"""
        provider1 = get_provider('MOCK', {})
        provider2 = get_provider('Mock', {})
        provider3 = get_provider('mock', {})
        
        assert isinstance(provider1, MockProvider)
        assert isinstance(provider2, MockProvider)
        assert isinstance(provider3, MockProvider)
    
    def test_get_provider_invalid_name(self):
        """测试无效的提供商名称"""
        with pytest.raises(ValueError, match="未知的 AI 提供商"):
            get_provider('invalid_provider', {})
    
    def test_get_llama_provider(self):
        """测试获取 LLaMA 提供商"""
        # 注意：这个测试可能会失败，因为 llama-cpp-python 可能未安装
        try:
            provider = get_provider('llama', {'model_path': ''})
            assert provider is not None
        except ImportError:
            pytest.skip("llama-cpp-python 未安装")
    
    def test_get_ollama_provider(self):
        """测试获取 Ollama 提供商"""
        # 注意：这个测试可能会失败，因为 ollama 可能未安装
        try:
            provider = get_provider('ollama', {'model_name': 'llama2'})
            assert provider is not None
        except ImportError:
            pytest.skip("ollama 包未安装")


class TestAIProviderBase:
    """AI 提供商基类测试"""
    
    def test_build_prompt(self):
        """测试构建提示词"""
        provider = MockProvider()
        context = Context(session_id="test")
        context.add_command("Get-ChildItem")
        context.add_command("Get-Process")
        
        prompt = provider._build_prompt("显示文件", context)
        assert "显示文件" in prompt
        assert "PowerShell" in prompt
    
    def test_parse_result_simple(self):
        """测试解析简单结果"""
        provider = MockProvider()
        
        result = provider._parse_result("Get-ChildItem", "显示文件")
        assert result.generated_command == "Get-ChildItem"
        assert result.original_input == "显示文件"
    
    def test_parse_result_with_code_block(self):
        """测试解析带代码块的结果"""
        provider = MockProvider()
        
        result = provider._parse_result("```\nGet-ChildItem\n```", "显示文件")
        assert "Get-ChildItem" in result.generated_command
    
    def test_parse_result_with_powershell_prefix(self):
        """测试解析带 PowerShell 前缀的结果"""
        provider = MockProvider()
        
        result = provider._parse_result("powershell Get-ChildItem", "显示文件")
        assert "Get-ChildItem" in result.generated_command
        assert "powershell" not in result.generated_command.lower() or result.generated_command == "Get-ChildItem"
