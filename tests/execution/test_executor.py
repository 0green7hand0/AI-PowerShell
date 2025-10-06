"""
命令执行器测试模块

测试 CommandExecutor 类的功能，包括：
- PowerShell 检测
- 命令执行
- 超时处理
- 错误处理
- 异步执行
"""

import pytest
import asyncio
import platform
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.execution.executor import CommandExecutor
from src.interfaces.base import ExecutionResult, ExecutionStatus


class TestCommandExecutor:
    """命令执行器测试类"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return CommandExecutor(encoding='utf-8', default_timeout=30)
    
    def test_init(self, executor):
        """测试执行器初始化"""
        assert executor.encoding in ['utf-8', 'gbk']
        assert executor.default_timeout == 30
        assert executor.platform_name in ['Windows', 'Linux', 'Darwin']
    
    def test_detect_powershell(self, executor):
        """测试 PowerShell 检测"""
        # PowerShell 应该被检测到（如果系统中安装了）
        if executor.powershell_cmd:
            assert executor.powershell_cmd in ['pwsh', 'powershell']
    
    def test_is_available(self, executor):
        """测试 PowerShell 可用性检查"""
        is_available = executor.is_available()
        assert isinstance(is_available, bool)
        
        # 如果检测到 PowerShell，应该返回 True
        if executor.powershell_cmd:
            assert is_available is True
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_simple_command(self, executor):
        """测试执行简单命令"""
        # 执行一个简单的 echo 命令
        result = executor.execute('echo "Hello, World!"')
        
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.return_code == 0
        assert "Hello, World!" in result.output
        assert result.status == ExecutionStatus.SUCCESS
        assert result.execution_time > 0
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_get_date(self, executor):
        """测试执行 Get-Date 命令"""
        result = executor.execute('Get-Date -Format "yyyy-MM-dd"')
        
        assert result.success is True
        assert result.return_code == 0
        assert len(result.output.strip()) > 0
        assert result.status == ExecutionStatus.SUCCESS
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_error(self, executor):
        """测试执行错误命令"""
        # 执行一个不存在的命令
        result = executor.execute('Get-NonExistentCommand')
        
        assert isinstance(result, ExecutionResult)
        assert result.success is False
        assert result.return_code != 0
        assert result.status == ExecutionStatus.FAILED
        assert len(result.error) > 0
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_timeout(self, executor):
        """测试命令超时"""
        # 执行一个会超时的命令（睡眠 10 秒，但超时设置为 1 秒）
        result = executor.execute('Start-Sleep -Seconds 10', timeout=1)
        
        assert isinstance(result, ExecutionResult)
        assert result.success is False
        assert result.status == ExecutionStatus.TIMEOUT
        assert "超时" in result.error
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    @pytest.mark.asyncio
    async def test_execute_async(self, executor):
        """测试异步执行"""
        result = await executor.execute_async('echo "Async Test"')
        
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert "Async Test" in result.output
        assert result.metadata.get('async') is True
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    @pytest.mark.asyncio
    async def test_execute_async_with_timeout(self, executor):
        """测试异步执行超时"""
        result = await executor.execute_async('Start-Sleep -Seconds 10', timeout=1)
        
        assert isinstance(result, ExecutionResult)
        assert result.success is False
        assert result.status == ExecutionStatus.TIMEOUT
    
    def test_execute_without_powershell(self):
        """测试在没有 PowerShell 的情况下执行"""
        # 模拟 PowerShell 不可用
        with patch.object(CommandExecutor, '_detect_powershell', return_value=None):
            executor = CommandExecutor()
            result = executor.execute('echo "test"')
            
            assert result.success is False
            assert "不可用" in result.error
            assert result.status == ExecutionStatus.FAILED
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_get_powershell_version(self, executor):
        """测试获取 PowerShell 版本"""
        version = executor.get_powershell_version()
        
        if executor.is_available():
            assert version is not None
            assert len(version) > 0
            # 版本号应该包含数字
            assert any(char.isdigit() for char in version)
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_metadata(self, executor):
        """测试执行结果包含元数据"""
        result = executor.execute('echo "test"')
        
        assert 'powershell_version' in result.metadata
        assert 'platform' in result.metadata
        assert 'encoding' in result.metadata
        assert result.metadata['powershell_version'] in ['pwsh', 'powershell']
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_multiline_output(self, executor):
        """测试多行输出"""
        command = 'echo "Line 1"; echo "Line 2"; echo "Line 3"'
        result = executor.execute(command)
        
        assert result.success is True
        assert "Line 1" in result.output
        assert "Line 2" in result.output
        assert "Line 3" in result.output
    
    def test_encoding_windows(self):
        """测试 Windows 平台编码"""
        with patch('platform.system', return_value='Windows'):
            executor = CommandExecutor(encoding='utf-8')
            # Windows 应该自动使用 gbk
            assert executor.encoding == 'gbk'
    
    def test_encoding_unix(self):
        """测试 Unix 平台编码"""
        with patch('platform.system', return_value='Linux'):
            executor = CommandExecutor(encoding='utf-8')
            # Unix 应该使用 utf-8
            assert executor.encoding == 'utf-8'
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_custom_timeout(self, executor):
        """测试自定义超时"""
        # 执行一个快速命令，使用较长的超时
        result = executor.execute('echo "test"', timeout=60)
        
        assert result.success is True
        assert result.execution_time < 60
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execution_result_properties(self, executor):
        """测试执行结果的属性"""
        result = executor.execute('echo "test"')
        
        # 测试 has_output 属性
        assert result.has_output is True
        
        # 测试 has_error 属性（成功的命令不应该有错误）
        if result.success:
            assert result.has_error is False
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_empty_command(self, executor):
        """测试执行空命令"""
        result = executor.execute('')
        
        # 空命令应该成功执行（不做任何事）
        assert isinstance(result, ExecutionResult)
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_timestamp_in_result(self, executor):
        """测试结果中包含时间戳"""
        before = datetime.now()
        result = executor.execute('echo "test"')
        after = datetime.now()
        
        assert before <= result.timestamp <= after


class TestCommandExecutorScriptExecution:
    """脚本执行测试类"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return CommandExecutor()
    
    @pytest.fixture
    def temp_script_file(self, tmp_path):
        """创建临时脚本文件"""
        script_file = tmp_path / "test_script.ps1"
        script_file.write_text('echo "Script Test"', encoding='utf-8')
        return str(script_file)
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_script_file(self, executor, temp_script_file):
        """测试执行脚本文件"""
        result = executor.execute_script_file(temp_script_file)
        
        assert isinstance(result, ExecutionResult)
        
        # 如果执行策略阻止脚本执行，跳过此测试
        if "UnauthorizedAccess" in result.error or "禁止运行脚本" in result.error:
            pytest.skip("PowerShell execution policy blocks script execution")
        
        assert result.success is True
        assert "Script Test" in result.output
        assert 'script_path' in result.metadata
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_nonexistent_script(self, executor):
        """测试执行不存在的脚本"""
        result = executor.execute_script_file('/nonexistent/script.ps1')
        
        assert result.success is False
        assert result.status == ExecutionStatus.FAILED
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_script_with_timeout(self, executor, tmp_path):
        """测试脚本执行超时"""
        # 创建一个会超时的脚本
        script_file = tmp_path / "timeout_script.ps1"
        script_file.write_text('Start-Sleep -Seconds 10', encoding='utf-8')
        
        result = executor.execute_script_file(str(script_file), timeout=1)
        
        # 如果执行策略阻止脚本执行，跳过此测试
        if "UnauthorizedAccess" in result.error or "禁止运行脚本" in result.error:
            pytest.skip("PowerShell execution policy blocks script execution")
        
        assert result.success is False
        assert result.status == ExecutionStatus.TIMEOUT


class TestCommandExecutorEdgeCases:
    """边界情况测试类"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return CommandExecutor()
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_special_characters(self, executor):
        """测试包含特殊字符的命令"""
        # 测试引号
        result = executor.execute('echo "Test with \\"quotes\\""')
        assert result.success is True
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_pipe(self, executor):
        """测试管道命令"""
        result = executor.execute('echo "test" | Select-String "test"')
        assert result.success is True
        assert "test" in result.output
    
    @pytest.mark.skipif(
        not CommandExecutor().is_available(),
        reason="PowerShell not available"
    )
    def test_execute_with_variables(self, executor):
        """测试包含变量的命令"""
        result = executor.execute('$x = 5; echo $x')
        assert result.success is True
        assert "5" in result.output
