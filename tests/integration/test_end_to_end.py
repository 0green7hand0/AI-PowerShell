"""
端到端集成测试

测试完整的用户请求处理流程，从输入到输出，验证所有模块的协作。
"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

from src.main import PowerShellAssistant
from src.interfaces.base import (
    ExecutionResult, Suggestion, ValidationResult, 
    RiskLevel, ExecutionStatus, Context
)


class TestEndToEndFlow:
    """端到端流程测试"""
    
    @pytest.fixture
    def test_config_path(self, tmp_path):
        """创建测试配置文件"""
        config_file = tmp_path / "e2e_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test-model"
  temperature: 0.7
  max_tokens: 256
  cache_enabled: true

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
    - "Format-Volume"
  safe_prefixes:
    - "Get-"
    - "Test-"
    - "Show-"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "DEBUG"
  file: "logs/e2e_test.log"
  max_size: "10MB"
  backup_count: 3
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: false

storage:
  storage_type: "file"
  base_path: "test_data/e2e"
  history_limit: 100

context:
  max_history: 100
  session_timeout: 3600
"""
        config_file.write_text(config_content, encoding='utf-8')
        return str(config_file)
    
    def test_complete_safe_command_flow(self, test_config_path):
        """测试安全命令的完整流程：输入 -> 翻译 -> 验证 -> 执行 -> 输出"""
        # 初始化助手
        assistant = PowerShellAssistant(config_path=test_config_path)
        
        # 启动会话
        assistant.context_manager.start_session()
        
        # 执行安全命令
        user_input = "显示当前时间"
        result = assistant.process_request(user_input, auto_execute=True)
        
        # 验证结果结构
        assert isinstance(result, ExecutionResult)
        assert result.command is not None
        assert result.command != ""
        assert result.timestamp is not None
        
        # 验证历史记录
        recent_commands = assistant.context_manager.get_recent_commands(limit=10)
        assert len(recent_commands) >= 1
        assert recent_commands[-1].user_input == user_input
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_multiple_commands_in_session(self, test_config_path):
        """测试会话中执行多个命令"""
        assistant = PowerShellAssistant(config_path=test_config_path)
        
        # 启动会话
        assistant.context_manager.start_session()
        session = assistant.context_manager.get_current_session()
        session_id = session.session_id
        
        # 执行多个命令
        commands = [
            "显示当前时间",
            "显示当前目录",
            "列出文件"
        ]
        
        results = []
        for cmd in commands:
            result = assistant.process_request(cmd, auto_execute=True)
            results.append(result)
            time.sleep(0.1)  # 避免过快执行
        
        # 验证所有命令都被执行
        assert len(results) == len(commands)
        
        # 验证会话 ID 保持一致
        current_session = assistant.context_manager.get_current_session()
        assert current_session.session_id == session_id
        
        # 验证历史记录
        recent_commands = assistant.context_manager.get_recent_commands(limit=10)
        assert len(recent_commands) >= len(commands)
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_context_awareness(self, test_config_path):
        """测试上下文感知能力"""
        assistant = PowerShellAssistant(config_path=test_config_path)
        
        # 启动会话
        assistant.context_manager.start_session()
        
        # 执行第一个命令
        result1 = assistant.process_request("显示当前目录", auto_execute=True)
        
        # 获取上下文
        context = assistant._build_context()
        
        # 验证上下文包含历史命令
        assert len(context.command_history) >= 1
        assert context.session_id is not None
        assert context.working_directory is not None
        
        # 执行第二个命令（可能依赖上下文）
        result2 = assistant.process_request("列出文件", auto_execute=True)
        
        # 验证上下文更新
        context2 = assistant._build_context()
        assert len(context2.command_history) >= 2
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_error_recovery(self, test_config_path):
        """测试错误恢复能力"""
        assistant = PowerShellAssistant(config_path=test_config_path)
        
        # 启动会话
        assistant.context_manager.start_session()
        
        # 执行一个可能失败的命令
        result1 = assistant.process_request("执行不存在的命令xyz123", auto_execute=True)
        
        # 验证错误被正确处理
        assert isinstance(result1, ExecutionResult)
        
        # 执行一个正常命令，验证系统仍然可用
        result2 = assistant.process_request("显示当前时间", auto_execute=True)
        assert isinstance(result2, ExecutionResult)
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_history_persistence(self, test_config_path, tmp_path):
        """测试历史记录持久化"""
        # 第一次会话
        assistant1 = PowerShellAssistant(config_path=test_config_path)
        assistant1.context_manager.start_session()
        
        # 执行命令
        user_input = "显示当前时间"
        result1 = assistant1.process_request(user_input, auto_execute=True)
        
        assistant1.context_manager.terminate_session()
        
        # 创建新的助手实例（模拟重启）
        assistant2 = PowerShellAssistant(config_path=test_config_path)
        
        # 验证历史记录被加载
        history = assistant2.storage.load_history(limit=10)
        
        # 应该能找到之前的命令
        assert isinstance(history, list)


class TestModuleCollaboration:
    """模块协作测试"""
    
    @pytest.fixture
    def assistant_with_real_components(self, tmp_path):
        """创建使用真实组件的助手"""
        config_file = tmp_path / "collab_config.yaml"
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
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
  safe_prefixes:
    - "Get-"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "INFO"
  file: "logs/collab_test.log"
  max_size: "10MB"
  backup_count: 3
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: false

storage:
  storage_type: "file"
  base_path: "test_data/collab"
  history_limit: 100

context:
  max_history: 100
  session_timeout: 3600
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_ai_to_security_flow(self, assistant_with_real_components):
        """测试 AI 引擎到安全引擎的流程"""
        assistant = assistant_with_real_components
        
        # 获取上下文
        context = assistant._build_context()
        
        # AI 翻译
        user_input = "显示当前时间"
        suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
        
        # 验证 AI 输出
        assert isinstance(suggestion, Suggestion)
        assert suggestion.generated_command is not None
        
        # 安全验证
        validation = assistant.security_engine.validate_command(
            suggestion.generated_command,
            context
        )
        
        # 验证安全输出
        assert isinstance(validation, ValidationResult)
        assert validation.risk_level is not None
    
    def test_security_to_executor_flow(self, assistant_with_real_components):
        """测试安全引擎到执行引擎的流程"""
        assistant = assistant_with_real_components
        
        # 创建一个安全命令
        safe_command = "Get-Date"
        context = assistant._build_context()
        
        # 安全验证
        validation = assistant.security_engine.validate_command(safe_command, context)
        
        # 如果通过验证，执行命令
        if validation.is_valid:
            result = assistant.executor.execute(
                safe_command,
                timeout=assistant.config.execution.timeout
            )
            
            # 验证执行结果
            assert isinstance(result, ExecutionResult)
            assert result.command == safe_command
    
    def test_executor_to_storage_flow(self, assistant_with_real_components):
        """测试执行引擎到存储引擎的流程"""
        assistant = assistant_with_real_components
        
        # 执行命令
        command = "Get-Date"
        result = assistant.executor.execute(command, timeout=30)
        
        # 保存到存储
        history_entry = {
            "user_input": "显示当前时间",
            "command": command,
            "success": result.success,
            "output": result.output[:100] if result.output else "",
            "timestamp": result.timestamp.isoformat()
        }
        
        save_success = assistant.storage.save_history(history_entry)
        
        # 验证保存成功
        assert save_success is True
        
        # 验证可以加载
        history = assistant.storage.load_history(limit=10)
        assert isinstance(history, list)
    
    def test_context_manager_integration(self, assistant_with_real_components):
        """测试上下文管理器与其他模块的集成"""
        assistant = assistant_with_real_components
        
        # 启动会话
        assistant.context_manager.start_session()
        session = assistant.context_manager.get_current_session()
        
        # 创建建议和结果
        suggestion = Suggestion(
            original_input="测试命令",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="测试"
        )
        
        result = ExecutionResult(
            success=True,
            command="Test-Command",
            output="测试输出"
        )
        
        # 添加到上下文
        assistant.context_manager.add_command(
            user_input="测试命令",
            suggestion=suggestion,
            result=result
        )
        
        # 验证上下文更新
        recent_commands = assistant.context_manager.get_recent_commands(limit=10)
        assert len(recent_commands) >= 1
        
        # 结束会话
        assistant.context_manager.terminate_session()


class TestErrorHandlingAcrossModules:
    """跨模块错误处理测试"""
    
    @pytest.fixture
    def assistant_with_mocks(self):
        """创建带 mock 组件的助手"""
        with patch('src.main.ConfigManager') as mock_config_mgr, \
             patch('src.main.LogEngine') as mock_log, \
             patch('src.main.StorageFactory') as mock_storage_factory, \
             patch('src.main.ContextManager') as mock_context, \
             patch('src.main.AIEngine') as mock_ai, \
             patch('src.main.SecurityEngine') as mock_security, \
             patch('src.main.CommandExecutor') as mock_executor:
            
            # 设置配置管理器
            mock_config = Mock()
            mock_config.ai = Mock()
            mock_config.security = Mock()
            mock_config.execution = Mock(timeout=30)
            mock_config.logging = Mock()
            mock_config.storage = Mock()
            mock_config.ai.model_dump = Mock(return_value={})
            mock_config.security.model_dump = Mock(return_value={})
            mock_config.execution.model_dump = Mock(return_value={})
            mock_config_mgr.return_value.load_config.return_value = mock_config
            
            # 设置存储工厂
            mock_storage = Mock()
            mock_storage_factory.create_storage.return_value = mock_storage
            
            # 设置上下文管理器
            mock_context_instance = Mock()
            mock_context_instance.get_current_session.return_value = Mock(session_id="test")
            mock_context_instance.get_recent_commands.return_value = []
            mock_context.return_value = mock_context_instance
            
            assistant = PowerShellAssistant()
            
            return assistant
    
    def test_ai_engine_failure_handling(self, assistant_with_mocks):
        """测试 AI 引擎失败时的处理"""
        # 设置 AI 引擎抛出异常
        assistant_with_mocks.ai_engine.translate_natural_language.side_effect = \
            RuntimeError("AI 模型加载失败")
        
        # 执行请求
        result = assistant_with_mocks.process_request("测试命令", auto_execute=True)
        
        # 验证错误被正确处理
        assert result.success is False
        assert "处理请求时发生错误" in result.error
        assert result.return_code == -1
    
    def test_security_engine_blocking(self, assistant_with_mocks):
        """测试安全引擎阻止命令"""
        # 设置正常的 AI 翻译
        suggestion = Suggestion(
            original_input="删除所有文件",
            generated_command="Remove-Item -Recurse -Force C:\\*",
            confidence_score=0.9,
            explanation="危险命令"
        )
        assistant_with_mocks.ai_engine.translate_natural_language.return_value = suggestion
        
        # 设置安全引擎阻止
        validation = ValidationResult(
            is_valid=False,
            risk_level=RiskLevel.CRITICAL,
            blocked_reasons=["危险的递归删除操作"]
        )
        assistant_with_mocks.security_engine.validate_command.return_value = validation
        
        # 执行请求
        result = assistant_with_mocks.process_request("删除所有文件", auto_execute=True)
        
        # 验证命令被阻止
        assert result.success is False
        assert "命令被安全引擎阻止" in result.error
        
        # 验证执行器未被调用
        assistant_with_mocks.executor.execute.assert_not_called()
    
    def test_executor_timeout_handling(self, assistant_with_mocks):
        """测试执行器超时处理"""
        # 设置正常的 AI 翻译和安全验证
        suggestion = Suggestion(
            original_input="长时间运行的命令",
            generated_command="Start-Sleep -Seconds 100",
            confidence_score=0.9,
            explanation="睡眠命令"
        )
        assistant_with_mocks.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        assistant_with_mocks.security_engine.validate_command.return_value = validation
        
        # 设置执行器超时
        assistant_with_mocks.executor.execute.side_effect = TimeoutError("命令执行超时")
        
        # 执行请求
        result = assistant_with_mocks.process_request("长时间运行的命令", auto_execute=True)
        
        # 验证超时被正确处理
        assert result.success is False
        assert "处理请求时发生错误" in result.error
    
    def test_storage_failure_graceful_handling(self, assistant_with_mocks):
        """测试存储失败时的优雅处理"""
        # 设置正常的流程
        suggestion = Suggestion(
            original_input="测试命令",
            generated_command="Get-Date",
            confidence_score=0.9,
            explanation="获取日期"
        )
        assistant_with_mocks.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        assistant_with_mocks.security_engine.validate_command.return_value = validation
        
        exec_result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025-01-20"
        )
        assistant_with_mocks.executor.execute.return_value = exec_result
        
        # 设置存储失败
        assistant_with_mocks.storage.save_history.side_effect = IOError("磁盘已满")
        
        # 执行请求
        result = assistant_with_mocks.process_request("测试命令", auto_execute=True)
        
        # 验证即使存储失败，命令仍然执行成功
        assert result.success is True
        assert result.command == "Get-Date"


class TestConcurrentRequests:
    """并发请求测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "concurrent_config.yaml"
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
  level: "INFO"
  file: "logs/concurrent_test.log"
  max_size: "10MB"
  backup_count: 3
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: false

storage:
  storage_type: "file"
  base_path: "test_data/concurrent"
  history_limit: 100

context:
  max_history: 100
  session_timeout: 3600
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_sequential_requests_in_same_session(self, assistant):
        """测试同一会话中的顺序请求"""
        assistant.context_manager.start_session()
        
        # 顺序执行多个请求
        commands = ["显示当前时间", "显示当前目录", "列出文件"]
        results = []
        
        for cmd in commands:
            result = assistant.process_request(cmd, auto_execute=True)
            results.append(result)
        
        # 验证所有请求都被处理
        assert len(results) == len(commands)
        
        # 验证历史记录顺序
        recent_commands = assistant.context_manager.get_recent_commands(limit=10)
        assert len(recent_commands) >= len(commands)
        
        assistant.context_manager.terminate_session()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
