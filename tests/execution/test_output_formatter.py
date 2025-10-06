"""
输出格式化器测试模块

测试 OutputFormatter 类的功能，包括：
- 结果格式化
- 颜色输出
- 输出截断
- 表格格式化
- 错误格式化
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.execution.output_formatter import OutputFormatter
from src.interfaces.base import ExecutionResult, ExecutionStatus


class TestOutputFormatter:
    """输出格式化器测试类"""
    
    @pytest.fixture
    def formatter(self):
        """创建格式化器实例"""
        return OutputFormatter(
            max_output_length=5000,
            enable_colors=True,
            truncate_long_lines=True,
            max_line_length=200
        )
    
    @pytest.fixture
    def success_result(self):
        """创建成功的执行结果"""
        return ExecutionResult(
            success=True,
            command='Get-Date',
            output='2025-01-20 10:30:45',
            error='',
            return_code=0,
            execution_time=0.234,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now(),
            metadata={'powershell_version': 'pwsh', 'platform': 'Windows'}
        )
    
    @pytest.fixture
    def failed_result(self):
        """创建失败的执行结果"""
        return ExecutionResult(
            success=False,
            command='Get-NonExistentCommand',
            output='',
            error='CommandNotFoundException: The term Get-NonExistentCommand is not recognized',
            return_code=1,
            execution_time=0.123,
            status=ExecutionStatus.FAILED,
            timestamp=datetime.now(),
            metadata={'powershell_version': 'pwsh'}
        )
    
    @pytest.fixture
    def timeout_result(self):
        """创建超时的执行结果"""
        return ExecutionResult(
            success=False,
            command='Start-Sleep -Seconds 100',
            output='',
            error='命令执行超时 (30 秒)',
            return_code=-1,
            execution_time=30.0,
            status=ExecutionStatus.TIMEOUT,
            timestamp=datetime.now()
        )
    
    def test_init(self, formatter):
        """测试格式化器初始化"""
        assert formatter.max_output_length == 5000
        assert formatter.enable_colors is True
        assert formatter.truncate_long_lines is True
        assert formatter.max_line_length == 200
    
    def test_format_success_result(self, formatter, success_result):
        """测试格式化成功结果"""
        formatted = formatter.format_result(success_result)
        
        assert isinstance(formatted, str)
        assert '执行成功' in formatted or '✅' in formatted
        assert 'Get-Date' in formatted
        assert '2025-01-20 10:30:45' in formatted
    
    def test_format_failed_result(self, formatter, failed_result):
        """测试格式化失败结果"""
        formatted = formatter.format_result(failed_result)
        
        assert isinstance(formatted, str)
        assert '执行失败' in formatted or '❌' in formatted
        assert 'Get-NonExistentCommand' in formatted
        assert 'CommandNotFoundException' in formatted
    
    def test_format_timeout_result(self, formatter, timeout_result):
        """测试格式化超时结果"""
        formatted = formatter.format_result(timeout_result)
        
        assert isinstance(formatted, str)
        assert '超时' in formatted
        assert 'Start-Sleep' in formatted
    
    def test_format_simple(self, formatter, success_result):
        """测试简单格式化"""
        formatted = formatter.format_simple(success_result)
        
        assert isinstance(formatted, str)
        assert '2025-01-20 10:30:45' in formatted
        # 简单格式不应该包含状态标题
        assert '执行成功' not in formatted
    
    def test_format_json(self, formatter, success_result):
        """测试 JSON 格式化"""
        json_result = formatter.format_json(success_result)
        
        assert isinstance(json_result, dict)
        assert 'success' in json_result
        assert 'command' in json_result
        assert 'output' in json_result
        assert 'error' in json_result
        assert 'return_code' in json_result
        assert 'execution_time' in json_result
        assert 'status' in json_result
        assert json_result['success'] is True
        assert json_result['command'] == 'Get-Date'
    
    def test_clean_output(self, formatter):
        """测试输出清理"""
        # 测试移除多余空白行
        text = "Line 1\n\n\n\nLine 2"
        cleaned = formatter._clean_output(text)
        assert cleaned == "Line 1\n\nLine 2"
        
        # 测试移除行尾空白
        text = "Line 1   \nLine 2  "
        cleaned = formatter._clean_output(text)
        assert cleaned == "Line 1\nLine 2"
    
    def test_truncate_long_output(self, formatter):
        """测试截断长输出"""
        # 创建一个超长输出
        long_output = "x" * 10000
        result = ExecutionResult(
            success=True,
            command='test',
            output=long_output,
            error='',
            return_code=0,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now()
        )
        
        formatted = formatter._format_output(result.output)
        
        # 输出应该被截断
        assert len(formatted) < len(long_output)
        assert '截断' in formatted
    
    def test_truncate_long_lines(self, formatter):
        """测试截断长行"""
        long_line = "x" * 500
        truncated = formatter._truncate_long_lines(long_line)
        
        # 行应该被截断
        assert len(truncated) < len(long_line)
        assert '截断' in truncated
    
    def test_colorize(self, formatter):
        """测试颜色化"""
        text = "Test"
        colored = formatter._colorize(text, 'red')
        
        # 应该包含 ANSI 颜色代码
        assert '\033[' in colored
        assert text in colored
    
    def test_colorize_with_bold(self, formatter):
        """测试加粗颜色化"""
        text = "Test"
        colored = formatter._colorize(text, 'green', bold=True)
        
        # 应该包含加粗代码
        assert '\033[1m' in colored
        assert text in colored
    
    def test_colorize_disabled(self):
        """测试禁用颜色"""
        formatter = OutputFormatter(enable_colors=False)
        text = "Test"
        colored = formatter._colorize(text, 'red')
        
        # 不应该包含颜色代码
        assert colored == text
    
    def test_strip_ansi_codes(self, formatter):
        """测试移除 ANSI 代码"""
        colored_text = '\033[91mRed Text\033[0m'
        stripped = formatter.strip_ansi_codes(colored_text)
        
        assert stripped == 'Red Text'
        assert '\033[' not in stripped
    
    def test_format_table(self, formatter):
        """测试表格格式化"""
        data = [
            {'Name': 'Alice', 'Age': 30, 'City': 'New York'},
            {'Name': 'Bob', 'Age': 25, 'City': 'London'},
            {'Name': 'Charlie', 'Age': 35, 'City': 'Paris'}
        ]
        
        table = formatter.format_table(data)
        
        assert isinstance(table, str)
        assert 'Alice' in table
        assert 'Bob' in table
        assert 'Charlie' in table
        assert '|' in table  # 表格分隔符
        assert '-' in table  # 表格横线
    
    def test_format_table_empty(self, formatter):
        """测试空表格格式化"""
        table = formatter.format_table([])
        assert table == "无数据"
    
    def test_format_table_with_headers(self, formatter):
        """测试带自定义表头的表格"""
        data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        headers = ['name', 'age']
        
        table = formatter.format_table(data, headers=headers)
        
        assert 'name' in table
        assert 'age' in table
        assert 'Alice' in table
    
    def test_format_list(self, formatter):
        """测试列表格式化"""
        items = ['Item 1', 'Item 2', 'Item 3']
        
        formatted = formatter.format_list(items)
        
        assert isinstance(formatted, str)
        assert 'Item 1' in formatted
        assert 'Item 2' in formatted
        assert 'Item 3' in formatted
        assert '•' in formatted  # 列表符号
    
    def test_format_list_numbered(self, formatter):
        """测试编号列表格式化"""
        items = ['Item 1', 'Item 2', 'Item 3']
        
        formatted = formatter.format_list(items, numbered=True)
        
        assert '1.' in formatted
        assert '2.' in formatted
        assert '3.' in formatted
    
    def test_format_list_empty(self, formatter):
        """测试空列表格式化"""
        formatted = formatter.format_list([])
        assert formatted == "无项目"
    
    def test_format_error_message(self, formatter):
        """测试错误消息格式化"""
        error = ValueError("Test error")
        formatted = formatter.format_error_message(error)
        
        assert isinstance(formatted, str)
        assert 'ValueError' in formatted
        assert 'Test error' in formatted
        assert '错误' in formatted
    
    def test_format_error_message_with_context(self, formatter):
        """测试带上下文的错误消息格式化"""
        error = ValueError("Test error")
        formatted = formatter.format_error_message(error, context="During command execution")
        
        assert 'During command execution' in formatted
    
    def test_format_status_header_success(self, formatter, success_result):
        """测试成功状态标题"""
        header = formatter._format_status_header(success_result)
        
        assert '成功' in header or '✅' in header
    
    def test_format_status_header_failed(self, formatter, failed_result):
        """测试失败状态标题"""
        header = formatter._format_status_header(failed_result)
        
        assert '失败' in header or '❌' in header
    
    def test_format_status_header_timeout(self, formatter, timeout_result):
        """测试超时状态标题"""
        header = formatter._format_status_header(timeout_result)
        
        assert '超时' in header or '⏱️' in header
    
    def test_format_command_info(self, formatter, success_result):
        """测试命令信息格式化"""
        info = formatter._format_command_info(success_result)
        
        assert 'Get-Date' in info
        assert '命令' in info or '📝' in info
    
    def test_format_execution_info(self, formatter, success_result):
        """测试执行信息格式化"""
        info = formatter._format_execution_info(success_result)
        
        assert '0.234' in info  # 执行时间
        assert '0' in info  # 返回码
        assert 'pwsh' in info  # PowerShell 版本
        assert 'Windows' in info  # 平台


class TestOutputFormatterEdgeCases:
    """边界情况测试类"""
    
    @pytest.fixture
    def formatter(self):
        """创建格式化器实例"""
        return OutputFormatter()
    
    def test_format_result_with_no_output(self, formatter):
        """测试无输出的结果"""
        result = ExecutionResult(
            success=True,
            command='test',
            output='',
            error='',
            return_code=0,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now()
        )
        
        formatted = formatter.format_result(result)
        assert isinstance(formatted, str)
    
    def test_format_result_with_unicode(self, formatter):
        """测试包含 Unicode 字符的结果"""
        result = ExecutionResult(
            success=True,
            command='test',
            output='测试中文输出 🎉',
            error='',
            return_code=0,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now()
        )
        
        formatted = formatter.format_result(result)
        assert '测试中文输出' in formatted
        assert '🎉' in formatted
    
    def test_format_result_with_multiline_output(self, formatter):
        """测试多行输出"""
        result = ExecutionResult(
            success=True,
            command='test',
            output='Line 1\nLine 2\nLine 3',
            error='',
            return_code=0,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now()
        )
        
        formatted = formatter.format_result(result)
        assert 'Line 1' in formatted
        assert 'Line 2' in formatted
        assert 'Line 3' in formatted
    
    def test_format_table_with_missing_keys(self, formatter):
        """测试包含缺失键的表格"""
        data = [
            {'Name': 'Alice', 'Age': 30},
            {'Name': 'Bob'},  # 缺少 Age
            {'Age': 35}  # 缺少 Name
        ]
        
        table = formatter.format_table(data)
        assert isinstance(table, str)
        assert 'Alice' in table
        assert 'Bob' in table
    
    def test_format_with_very_long_command(self, formatter):
        """测试非常长的命令"""
        long_command = 'Get-Process | ' * 100
        result = ExecutionResult(
            success=True,
            command=long_command,
            output='test',
            error='',
            return_code=0,
            status=ExecutionStatus.SUCCESS,
            timestamp=datetime.now()
        )
        
        formatted = formatter.format_result(result)
        assert isinstance(formatted, str)


class TestOutputFormatterConfiguration:
    """配置测试类"""
    
    def test_custom_max_output_length(self):
        """测试自定义最大输出长度"""
        formatter = OutputFormatter(max_output_length=100)
        assert formatter.max_output_length == 100
    
    def test_custom_max_line_length(self):
        """测试自定义最大行长度"""
        formatter = OutputFormatter(max_line_length=50)
        assert formatter.max_line_length == 50
    
    def test_disable_colors(self):
        """测试禁用颜色"""
        formatter = OutputFormatter(enable_colors=False)
        assert formatter.enable_colors is False
    
    def test_disable_line_truncation(self):
        """测试禁用行截断"""
        formatter = OutputFormatter(truncate_long_lines=False)
        assert formatter.truncate_long_lines is False
        
        # 长行不应该被截断
        long_line = "x" * 500
        truncated = formatter._truncate_long_lines(long_line)
        assert truncated == long_line
