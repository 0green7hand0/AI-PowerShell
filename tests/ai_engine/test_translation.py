"""
翻译逻辑测试
"""

import pytest
from src.ai_engine.translation import NaturalLanguageTranslator
from src.interfaces.base import Context


class TestNaturalLanguageTranslator:
    """自然语言翻译器测试"""
    
    def test_translator_initialization(self):
        """测试翻译器初始化"""
        translator = NaturalLanguageTranslator()
        assert translator is not None
        assert translator.rules is not None
        assert len(translator.rules) > 0
    
    def test_translate_list_files(self):
        """测试翻译：列出文件"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        test_cases = [
            "显示文件",
            "列出文件",
            "查看目录",
            "ls 文件"
        ]
        
        for text in test_cases:
            result = translator.translate(text, context)
            assert result is not None
            assert "Get-ChildItem" in result.generated_command
            assert result.confidence_score > 0
    
    def test_translate_current_directory(self):
        """测试翻译：显示当前目录"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        test_cases = [
            "显示当前目录",
            "查看当前位置",
            "pwd"
        ]
        
        for text in test_cases:
            result = translator.translate(text, context)
            assert result is not None
            assert "Get-Location" in result.generated_command
    
    def test_translate_get_date(self):
        """测试翻译：获取时间"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        test_cases = [
            "显示时间",
            "查看日期",
            "获取当前时间"
        ]
        
        for text in test_cases:
            result = translator.translate(text, context)
            assert result is not None
            assert "Get-Date" in result.generated_command
    
    def test_translate_list_processes(self):
        """测试翻译：列出进程"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        test_cases = [
            "显示进程",
            "列出任务",
            "查看进程"
        ]
        
        for text in test_cases:
            result = translator.translate(text, context)
            assert result is not None
            assert "Get-Process" in result.generated_command
    
    def test_translate_top_cpu_processes(self):
        """测试翻译：CPU使用率最高的进程"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        result = translator.translate("显示CPU使用率最高的5个进程", context)
        assert result is not None
        assert "Get-Process" in result.generated_command
        assert "Sort-Object" in result.generated_command or "Sort" in result.generated_command
        assert "CPU" in result.generated_command
    
    def test_translate_test_connection(self):
        """测试翻译：测试网络连接"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        result = translator.translate("测试网络连接 google.com", context)
        assert result is not None
        assert "Test-NetConnection" in result.generated_command
    
    def test_translate_unknown_command(self):
        """测试翻译：未知命令"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        result = translator.translate("这是一个完全未知的命令", context)
        assert result is not None
        # 应该返回回退翻译
        assert result.confidence_score < 0.7
    
    def test_explain_command(self):
        """测试命令解释"""
        translator = NaturalLanguageTranslator()
        
        test_cases = {
            "Get-ChildItem": "列出",
            "Get-Location": "显示当前",
            "Get-Date": "获取当前日期",
            "Get-Process": "列出",
        }
        
        for command, expected_keyword in test_cases.items():
            explanation = translator.explain_command(command)
            assert explanation is not None
            assert expected_keyword in explanation
    
    def test_generate_alternatives(self):
        """测试生成备选命令"""
        translator = NaturalLanguageTranslator()
        context = Context(session_id="test")
        
        result = translator.translate("显示文件", context)
        # 某些翻译可能有备选命令
        assert isinstance(result.alternatives, list)
    
    def test_fallback_translation(self):
        """测试回退翻译"""
        translator = NaturalLanguageTranslator()
        
        result = translator._fallback_translation("显示文件")
        assert result is not None
        assert result.generated_command is not None
        assert result.confidence_score < 0.7
    
    def test_extract_path(self):
        """测试路径提取"""
        translator = NaturalLanguageTranslator()
        
        import re
        match = re.search(r'.*', "切换到 C:\\Users\\test")
        path = translator._extract_path("切换到 C:\\Users\\test", match)
        assert "C:\\Users\\test" in path or path == "."
    
    def test_extract_count(self):
        """测试数量提取"""
        translator = NaturalLanguageTranslator()
        
        import re
        match = re.search(r'.*', "显示前10个进程")
        count = translator._extract_count("显示前10个进程", match)
        assert count == "10"
    
    def test_extract_host(self):
        """测试主机名提取"""
        translator = NaturalLanguageTranslator()
        
        import re
        match = re.search(r'.*', "测试连接 192.168.1.1")
        host = translator._extract_host("测试连接 192.168.1.1", match)
        assert host == "192.168.1.1"
        
        match = re.search(r'.*', "测试连接 google.com")
        host = translator._extract_host("测试连接 google.com", match)
        assert host == "google.com"
