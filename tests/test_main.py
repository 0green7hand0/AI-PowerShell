"""
主控制器单元测试

测试 PowerShellAssistant 类的核心功能，包括：
- 初始化和依赖注入
- 请求处理流程
- 交互模式
- 命令行模式
"""

import pytest
import uuid
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
from io import StringIO

from src.main import PowerShellAssistant, main
from src.interfaces.base import (
    Context, Suggestion, ValidationResult, ExecutionResult,
    RiskLevel, ExecutionStatus
)
from src.config import AppConfig


class TestPowerShellAssistantInitialization:
    """测试 PowerShellAssistant 初始化"""
    
    @patch('src.main.ConfigManager')
    @patch('src.main.LogEngine')
    @patch('src.main.StorageFactory')
    @patch('src.main.ContextManager')
    @patch('src.main.AIEngine')
    @patch('src.main.SecurityEngine')
    @patch('src.main.CommandExecutor')
    def test_initialization_with_default_config(
        self,
        mock_executor,
        mock_security,
        mock_ai,
        mock_context,
        mock_storage_factory,
        mock_log,
        mock_config_manager
    ):
        """测试使用默认配置初始化"""
        # 设置 mock
        mock_config = MagicMock()
        mock_config_manager.return_value.load_config.return_value = mock_config
        
        # 初始化
        assistant = PowerShellAssistant()
        
        # 验证
        assert assistant.config == mock_config
        mock_config_manager.assert_called_once_with(None)
        mock_log.assert_called_once()
        mock_storage_factory.create_storage.assert_called_once()
        mock_context.assert_called_once()
        mock_ai.assert_called_once()
        mock_security.assert_called_once()
        mock_executor.assert_called_once()
    
    @patch('src.main.ConfigManager')
    @patch('src.main.LogEngine')
    @patch('src.main.StorageFactory')
    @patch('src.main.ContextManager')
    @patch('src.main.AIEngine')
    @patch('src.main.SecurityEngine')
    @patch('src.main.CommandExecutor')
    def test_initialization_with_custom_config(
        self,
        mock_executor,
        mock_security,
        mock_ai,
        mock_context,
        mock_storage_factory,
        mock_log,
        mock_config_manager
    ):
        """测试使用自定义配置初始化"""
        # 设置 mock
        mock_config = MagicMock()
        mock_config_manager.return_value.load_config.return_value = mock_config
        custom_config_path = "/path/to/config.yaml"
        
        # 初始化
        assistant = PowerShellAssistant(config_path=custom_config_path)
        
        # 验证
        mock_config_manager.assert_called_once_with(custom_config_path)
        assert assistant.config == mock_config


class TestProcessRequest:
    """测试请求处理流程"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建 mock 的 assistant 实例"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            assistant = PowerShellAssistant()
            
            # 设置 mock 返回值
            assistant.context_manager.get_current_session.return_value = Mock(session_id="test-session")
            assistant.context_manager.get_recent_commands.return_value = []
            
            return assistant
    
    def test_successful_request_processing(self, mock_assistant):
        """测试成功的请求处理"""
        # 准备测试数据
        user_input = "显示当前时间"
        
        # 设置 mock 返回值
        suggestion = Suggestion(
            original_input=user_input,
            generated_command="Get-Date",
            confidence_score=0.95,
            explanation="显示当前日期和时间"
        )
        mock_assistant.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE,
            requires_confirmation=False
        )
        mock_assistant.security_engine.validate_command.return_value = validation
        
        execution_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0,
            execution_time=0.123
        )
        mock_assistant.executor.execute.return_value = execution_result
        
        # 执行
        result = mock_assistant.process_request(user_input, auto_execute=True)
        
        # 验证
        assert result.success is True
        assert result.command == "Get-Date"
        mock_assistant.ai_engine.translate_natural_language.assert_called_once()
        mock_assistant.security_engine.validate_command.assert_called_once()
        mock_assistant.executor.execute.assert_called_once()
        mock_assistant.storage.save_history.assert_called_once()
        mock_assistant.context_manager.add_command.assert_called_once()
    
    def test_request_blocked_by_security(self, mock_assistant):
        """测试请求被安全引擎阻止"""
        # 准备测试数据
        user_input = "删除所有文件"
        
        # 设置 mock 返回值
        suggestion = Suggestion(
            original_input=user_input,
            generated_command="Remove-Item * -Recurse -Force",
            confidence_score=0.90,
            explanation="递归删除所有文件"
        )
        mock_assistant.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=False,
            risk_level=RiskLevel.CRITICAL,
            blocked_reasons=["危险的递归删除操作"]
        )
        mock_assistant.security_engine.validate_command.return_value = validation
        
        # 执行
        result = mock_assistant.process_request(user_input, auto_execute=True)
        
        # 验证
        assert result.success is False
        assert "命令被安全引擎阻止" in result.error
        mock_assistant.executor.execute.assert_not_called()
    
    def test_request_with_user_confirmation_accepted(self, mock_assistant):
        """测试需要用户确认且用户同意"""
        # 准备测试数据
        user_input = "重启计算机"
        
        # 设置 mock 返回值
        suggestion = Suggestion(
            original_input=user_input,
            generated_command="Restart-Computer",
            confidence_score=0.85,
            explanation="重启计算机"
        )
        mock_assistant.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
            warnings=["此操作将重启计算机"]
        )
        mock_assistant.security_engine.validate_command.return_value = validation
        
        execution_result = ExecutionResult(
            success=True,
            command="Restart-Computer",
            output="",
            return_code=0
        )
        mock_assistant.executor.execute.return_value = execution_result
        
        # Mock 用户确认
        with patch.object(mock_assistant, '_get_user_confirmation', return_value=True):
            result = mock_assistant.process_request(user_input, auto_execute=False)
        
        # 验证
        assert result.success is True
        mock_assistant.executor.execute.assert_called_once()
    
    def test_request_with_user_confirmation_rejected(self, mock_assistant):
        """测试需要用户确认且用户拒绝"""
        # 准备测试数据
        user_input = "重启计算机"
        
        # 设置 mock 返回值
        suggestion = Suggestion(
            original_input=user_input,
            generated_command="Restart-Computer",
            confidence_score=0.85,
            explanation="重启计算机"
        )
        mock_assistant.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True
        )
        mock_assistant.security_engine.validate_command.return_value = validation
        
        # Mock 用户拒绝
        with patch.object(mock_assistant, '_get_user_confirmation', return_value=False):
            result = mock_assistant.process_request(user_input, auto_execute=False)
        
        # 验证
        assert result.success is True
        assert "用户取消执行" in result.output
        mock_assistant.executor.execute.assert_not_called()
    
    def test_request_with_exception(self, mock_assistant):
        """测试请求处理过程中发生异常"""
        # 准备测试数据
        user_input = "显示当前时间"
        
        # 设置 mock 抛出异常
        mock_assistant.ai_engine.translate_natural_language.side_effect = Exception("AI 引擎错误")
        
        # 执行
        result = mock_assistant.process_request(user_input, auto_execute=True)
        
        # 验证
        assert result.success is False
        assert "处理请求时发生错误" in result.error
        mock_assistant.log_engine.error.assert_called_once()


class TestBuildContext:
    """测试上下文构建"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建 mock 的 assistant 实例"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            return PowerShellAssistant()
    
    def test_build_context(self, mock_assistant):
        """测试构建上下文"""
        # 设置 mock 返回值
        mock_session = Mock(session_id="test-session-123")
        mock_assistant.context_manager.get_current_session.return_value = mock_session
        
        mock_commands = [
            Mock(translated_command="Get-Date"),
            Mock(translated_command="Get-Process")
        ]
        mock_assistant.context_manager.get_recent_commands.return_value = mock_commands
        
        # 执行
        context = mock_assistant._build_context()
        
        # 验证
        assert context.session_id == "test-session-123"
        assert len(context.command_history) == 2
        assert context.command_history[0] == "Get-Date"
        assert context.command_history[1] == "Get-Process"


class TestInteractiveMode:
    """测试交互模式"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建 mock 的 assistant 实例"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            return PowerShellAssistant()
    
    def test_interactive_mode_exit_command(self, mock_assistant, capsys):
        """测试交互模式退出命令"""
        # Mock 用户输入
        with patch('builtins.input', side_effect=['exit']):
            mock_assistant.interactive_mode()
        
        # 验证
        mock_assistant.context_manager.start_session.assert_called_once()
        mock_assistant.context_manager.end_session.assert_called_once()
        
        captured = capsys.readouterr()
        assert "再见" in captured.out
    
    def test_interactive_mode_help_command(self, mock_assistant, capsys):
        """测试交互模式帮助命令"""
        # Mock 用户输入
        with patch('builtins.input', side_effect=['help', 'exit']):
            mock_assistant.interactive_mode()
        
        # 验证
        captured = capsys.readouterr()
        assert "帮助信息" in captured.out
        assert "使用示例" in captured.out
    
    def test_interactive_mode_history_command(self, mock_assistant, capsys):
        """测试交互模式历史命令"""
        # 设置 mock 返回值
        mock_assistant.context_manager.get_recent_commands.return_value = []
        
        # Mock 用户输入
        with patch('builtins.input', side_effect=['history', 'exit']):
            mock_assistant.interactive_mode()
        
        # 验证
        captured = capsys.readouterr()
        assert "命令历史" in captured.out
    
    def test_interactive_mode_normal_request(self, mock_assistant, capsys):
        """测试交互模式正常请求"""
        # 设置 mock 返回值
        execution_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0
        )
        
        mock_process = Mock(return_value=execution_result)
        with patch.object(mock_assistant, 'process_request', mock_process):
            with patch('builtins.input', side_effect=['显示当前时间', 'exit']):
                mock_assistant.interactive_mode()
        
        # 验证
        mock_process.assert_called_once_with('显示当前时间', auto_execute=False)
        captured = capsys.readouterr()
        assert "执行成功" in captured.out
    
    def test_interactive_mode_keyboard_interrupt(self, mock_assistant, capsys):
        """测试交互模式键盘中断"""
        # Mock 用户输入抛出 KeyboardInterrupt
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            mock_assistant.interactive_mode()
        
        # 验证
        mock_assistant.context_manager.end_session.assert_called_once()
        captured = capsys.readouterr()
        assert "Ctrl+C" in captured.out


class TestCommandLineMode:
    """测试命令行模式"""
    
    @patch('src.main.PowerShellAssistant')
    def test_main_with_command_argument(self, mock_assistant_class):
        """测试带命令参数的命令行模式"""
        # 设置 mock
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        
        execution_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0
        )
        mock_assistant.process_request.return_value = execution_result
        
        # 模拟命令行参数
        test_args = ['main.py', '-c', '显示当前时间']
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # 验证
        assert exc_info.value.code == 0
        mock_assistant.process_request.assert_called_once_with('显示当前时间', auto_execute=False)
    
    @patch('src.main.PowerShellAssistant')
    def test_main_with_auto_execute(self, mock_assistant_class):
        """测试自动执行模式"""
        # 设置 mock
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        
        execution_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0
        )
        mock_assistant.process_request.return_value = execution_result
        
        # 模拟命令行参数
        test_args = ['main.py', '-c', '显示当前时间', '-a']
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # 验证
        assert exc_info.value.code == 0
        mock_assistant.process_request.assert_called_once_with('显示当前时间', auto_execute=True)
    
    @patch('src.main.PowerShellAssistant')
    def test_main_interactive_mode(self, mock_assistant_class):
        """测试交互模式"""
        # 设置 mock
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        
        # 模拟命令行参数（无参数）
        test_args = ['main.py']
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # 验证
        assert exc_info.value.code == 0
        mock_assistant.interactive_mode.assert_called_once()
    
    @patch('src.main.PowerShellAssistant')
    def test_main_with_failed_execution(self, mock_assistant_class):
        """测试执行失败的情况"""
        # 设置 mock
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        
        execution_result = ExecutionResult(
            success=False,
            command="Invalid-Command",
            error="命令不存在",
            return_code=1
        )
        mock_assistant.process_request.return_value = execution_result
        
        # 模拟命令行参数
        test_args = ['main.py', '-c', '无效命令']
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # 验证
        assert exc_info.value.code == 1
    
    @patch('src.main.PowerShellAssistant')
    def test_main_with_custom_config(self, mock_assistant_class):
        """测试使用自定义配置"""
        # 设置 mock
        mock_assistant = Mock()
        mock_assistant_class.return_value = mock_assistant
        
        execution_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0
        )
        mock_assistant.process_request.return_value = execution_result
        
        # 模拟命令行参数
        test_args = ['main.py', '-c', '显示当前时间', '--config', '/path/to/config.yaml']
        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # 验证
        mock_assistant_class.assert_called_once_with(config_path='/path/to/config.yaml')


class TestDisplayResult:
    """测试结果显示"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建 mock 的 assistant 实例"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            return PowerShellAssistant()
    
    def test_display_successful_result(self, mock_assistant, capsys):
        """测试显示成功结果"""
        result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20 10:30:45",
            return_code=0,
            execution_time=0.123
        )
        
        mock_assistant._display_result(result)
        
        captured = capsys.readouterr()
        assert "执行成功" in captured.out
        assert "2025-01-20 10:30:45" in captured.out
        assert "0.123" in captured.out
    
    def test_display_failed_result(self, mock_assistant, capsys):
        """测试显示失败结果"""
        result = ExecutionResult(
            success=False,
            command="Invalid-Command",
            error="命令不存在",
            return_code=1
        )
        
        mock_assistant._display_result(result)
        
        captured = capsys.readouterr()
        assert "执行失败" in captured.out
        assert "命令不存在" in captured.out


class TestGetUserConfirmation:
    """测试用户确认"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建 mock 的 assistant 实例"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            return PowerShellAssistant()
    
    def test_user_confirms_with_yes(self, mock_assistant):
        """测试用户输入 yes 确认"""
        suggestion = Suggestion(
            original_input="显示当前时间",
            generated_command="Get-Date",
            confidence_score=0.95,
            explanation="显示当前日期和时间"
        )
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        
        with patch('builtins.input', return_value='y'):
            result = mock_assistant._get_user_confirmation(suggestion, validation)
        
        assert result is True
    
    def test_user_confirms_with_no(self, mock_assistant):
        """测试用户输入 no 拒绝"""
        suggestion = Suggestion(
            original_input="重启计算机",
            generated_command="Restart-Computer",
            confidence_score=0.85,
            explanation="重启计算机"
        )
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.HIGH,
            warnings=["此操作将重启计算机"]
        )
        
        with patch('builtins.input', return_value='n'):
            result = mock_assistant._get_user_confirmation(suggestion, validation)
        
        assert result is False
    
    def test_user_confirmation_with_warnings(self, mock_assistant, capsys):
        """测试带警告的用户确认"""
        suggestion = Suggestion(
            original_input="删除文件",
            generated_command="Remove-Item test.txt",
            confidence_score=0.90,
            explanation="删除文件"
        )
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.MEDIUM,
            warnings=["此操作不可撤销"],
            requires_elevation=True
        )
        
        with patch('builtins.input', return_value='n'):
            mock_assistant._get_user_confirmation(suggestion, validation)
        
        captured = capsys.readouterr()
        assert "警告" in captured.out
        assert "此操作不可撤销" in captured.out
        assert "需要管理员权限" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
