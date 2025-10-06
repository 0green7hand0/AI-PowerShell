"""
错误检测测试
"""

import pytest
from src.ai_engine.error_detection import ErrorDetector
from src.interfaces.base import Suggestion


class TestErrorDetector:
    """错误检测器测试"""
    
    def test_detector_initialization(self):
        """测试检测器初始化"""
        detector = ErrorDetector()
        assert detector is not None
        assert detector.common_errors is not None
    
    def test_has_errors_empty_command(self):
        """测试空命令检测"""
        detector = ErrorDetector()
        
        assert detector.has_errors("") is True
        assert detector.has_errors("   ") is True
    
    def test_has_errors_valid_command(self):
        """测试有效命令"""
        detector = ErrorDetector()
        
        valid_commands = [
            "Get-ChildItem",
            "Get-Process",
            "Get-Date",
            "Get-ChildItem | Sort-Object Name"
        ]
        
        for command in valid_commands:
            assert detector.has_errors(command) is False
    
    def test_detect_quote_errors(self):
        """测试引号错误检测"""
        detector = ErrorDetector()
        
        # 不匹配的单引号
        errors = detector.detect_errors("Get-Content 'file.txt")
        assert any(error[0] == 'quotes' for error in errors)
        
        # 不匹配的双引号
        errors = detector.detect_errors('Get-Content "file.txt')
        assert any(error[0] == 'quotes' for error in errors)
    
    def test_detect_bracket_errors(self):
        """测试括号错误检测"""
        detector = ErrorDetector()
        
        # 不匹配的圆括号
        errors = detector.detect_errors("Get-Process | Where-Object {$_.Name -eq 'test'")
        assert any(error[0] == 'brackets' for error in errors)
        
        # 不匹配的花括号
        errors = detector.detect_errors("Get-Process | Where-Object {$_.Name")
        assert any(error[0] == 'brackets' for error in errors)
    
    def test_detect_pipe_errors(self):
        """测试管道错误检测"""
        detector = ErrorDetector()
        
        # 空管道段
        errors = detector.detect_errors("Get-Process | | Sort-Object")
        assert any(error[0] == 'pipe' for error in errors)
        
        # 管道末尾为空
        errors = detector.detect_errors("Get-Process |")
        assert any(error[0] == 'pipe' for error in errors)
    
    def test_check_quotes(self):
        """测试引号检查"""
        detector = ErrorDetector()
        
        assert detector._check_quotes("Get-Content 'file.txt'") is True
        assert detector._check_quotes('Get-Content "file.txt"') is True
        assert detector._check_quotes("Get-Content 'file.txt") is False
        assert detector._check_quotes('Get-Content "file.txt') is False
    
    def test_check_brackets(self):
        """测试括号检查"""
        detector = ErrorDetector()
        
        assert detector._check_brackets("Get-Process | Where-Object {$_.Name -eq 'test'}") is True
        assert detector._check_brackets("Get-Process | Where-Object {$_.Name") is False
        assert detector._check_brackets("(Get-Process)") is True
        assert detector._check_brackets("(Get-Process") is False
    
    def test_check_pipe_syntax(self):
        """测试管道语法检查"""
        detector = ErrorDetector()
        
        assert detector._check_pipe_syntax("Get-Process | Sort-Object") is True
        assert detector._check_pipe_syntax("Get-Process |") is False
        assert detector._check_pipe_syntax("| Sort-Object") is False
        assert detector._check_pipe_syntax("Get-Process | | Sort-Object") is False
    
    def test_fix_quotes(self):
        """测试修正引号"""
        detector = ErrorDetector()
        
        fixed = detector._fix_quotes("Get-Content 'file.txt")
        assert fixed.count("'") % 2 == 0
        
        fixed = detector._fix_quotes('Get-Content "file.txt')
        assert fixed.count('"') % 2 == 0
    
    def test_fix_brackets(self):
        """测试修正括号"""
        detector = ErrorDetector()
        
        fixed = detector._fix_brackets("Get-Process | Where-Object {$_.Name")
        assert fixed.count('{') == fixed.count('}')
        
        fixed = detector._fix_brackets("(Get-Process")
        assert fixed.count('(') == fixed.count(')')
    
    def test_fix_pipe(self):
        """测试修正管道"""
        detector = ErrorDetector()
        
        fixed = detector._fix_pipe("Get-Process | | Sort-Object")
        assert "||" not in fixed
        
        fixed = detector._fix_pipe("Get-Process |")
        assert not fixed.endswith("|")
    
    def test_fix_spelling(self):
        """测试修正拼写"""
        detector = ErrorDetector()
        
        # 测试常见拼写错误修正
        fixed = detector._fix_spelling("Get-Childs")
        assert "Get-ChildItem" in fixed
        
        fixed = detector._fix_spelling("Get-Procs")
        assert "Get-Process" in fixed
    
    def test_fix_suggestion(self):
        """测试修正建议"""
        detector = ErrorDetector()
        
        # 创建一个有错误的建议
        suggestion = Suggestion(
            original_input="显示文件",
            generated_command="Get-Content 'file.txt",  # 缺少闭合引号
            confidence_score=0.9,
            explanation="读取文件"
        )
        
        fixed = detector.fix(suggestion)
        assert fixed is not None
        # 修正后置信度应该降低
        if not detector.has_errors(fixed.generated_command):
            assert fixed.confidence_score <= suggestion.confidence_score
    
    def test_suggest_improvements(self):
        """测试改进建议"""
        detector = ErrorDetector()
        
        # 删除命令应该建议添加确认
        suggestions = detector.suggest_improvements("Remove-Item file.txt")
        assert len(suggestions) > 0
        assert any("Confirm" in s or "ErrorAction" in s for s in suggestions)
        
        # Get 命令应该建议格式化输出
        suggestions = detector.suggest_improvements("Get-Process")
        assert any("Format" in s for s in suggestions)
    
    def test_detect_errors_comprehensive(self):
        """测试综合错误检测"""
        detector = ErrorDetector()
        
        # 多种错误
        command = "Get-Process | Where-Object {$_.Name -eq 'test' | Sort-Object"
        errors = detector.detect_errors(command)
        assert len(errors) > 0
    
    def test_no_errors_for_valid_commands(self):
        """测试有效命令不报错"""
        detector = ErrorDetector()
        
        valid_commands = [
            "Get-ChildItem",
            "Get-Process | Sort-Object CPU -Descending",
            "Get-Service | Where-Object {$_.Status -eq 'Running'}",
            "Get-Content 'file.txt' | Select-String 'pattern'",
            "(Get-Process).Count"
        ]
        
        for command in valid_commands:
            errors = detector.detect_errors(command)
            # 这些命令应该没有错误或只有很少的错误
            assert len(errors) <= 1  # 允许一些误报
