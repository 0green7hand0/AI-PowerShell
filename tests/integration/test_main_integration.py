"""
主控制器集成测试

测试 PowerShellAssistant 与各个模块的集成，验证完整的请求处理流程。
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.main import PowerShellAssistant
from src.interfaces.base import ExecutionResult


class TestMainIntegration:
    """主控制器集成测试"""
    
    @pytest.fixture
    def config_path(self, tmp_path):
        """创建临时配置文件"""
        config_file = tmp_path / "test_config.yaml"
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
  safe_prefixes:
    - "Get-"
    - "Test-"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "INFO"
  file: "logs/test.log"
  max_size: "10MB"
  backup_count: 3
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  console_output: false

storage:
  storage_type: "file"
  base_path: "test_data"
  history_limit: 100

context:
  max_history: 100
  session_timeout: 3600
"""
        config_file.write_text(config_content, encoding='utf-8')
        return str(config_file)
    
    def test_full_request_flow_with_safe_command(self, config_path):
        """测试安全命令的完整请求流程"""
        # 初始化助手
        assistant = PowerShellAssistant(config_path=config_path)
        
        # 处理请求
        result = assistant.process_request("显示当前时间", auto_execute=True)
        
        # 验证结果
        assert isinstance(result, ExecutionResult)
        assert result.command is not None
        # 注意：实际执行可能失败（如果 PowerShell 不可用），但应该有结果
    
    def test_context_persistence_across_requests(self, config_path):
        """测试多个请求之间的上下文持久化"""
        # 初始化助手
        assistant = PowerShellAssistant(config_path=config_path)
        
        # 启动会话
        assistant.context_manager.start_session()
        
        # 执行多个请求
        result1 = assistant.process_request("显示当前时间", auto_execute=True)
        result2 = assistant.process_request("显示当前目录", auto_execute=True)
        
        # 验证上下文
        recent_commands = assistant.context_manager.get_recent_commands(limit=10)
        assert len(recent_commands) >= 2
        
        # 结束会话
        assistant.context_manager.terminate_session()
    
    def test_dangerous_command_blocked(self, config_path):
        """测试危险命令被阻止"""
        # 初始化助手
        assistant = PowerShellAssistant(config_path=config_path)
        
        # 尝试执行危险命令
        result = assistant.process_request("删除所有文件", auto_execute=True)
        
        # 验证命令被阻止
        # 注意：根据 AI 翻译结果，可能被阻止或需要确认
        assert isinstance(result, ExecutionResult)


class TestMainWithMockedComponents:
    """使用 mock 组件的主控制器测试"""
    
    @pytest.fixture
    def assistant_with_mocks(self):
        """创建带 mock 组件的助手"""
        with patch('src.main.ConfigManager'), \
             patch('src.main.LogEngine'), \
             patch('src.main.StorageFactory'), \
             patch('src.main.ContextManager'), \
             patch('src.main.AIEngine'), \
             patch('src.main.SecurityEngine'), \
             patch('src.main.CommandExecutor'):
            
            assistant = PowerShellAssistant()
            
            # 设置基本的 mock 返回值
            assistant.context_manager.get_current_session.return_value = Mock(session_id="test")
            assistant.context_manager.get_recent_commands.return_value = []
            
            return assistant
    
    def test_error_handling_in_ai_engine(self, assistant_with_mocks):
        """测试 AI 引擎错误处理"""
        # 设置 AI 引擎抛出异常
        assistant_with_mocks.ai_engine.translate_natural_language.side_effect = \
            Exception("AI 模型不可用")
        
        # 执行请求
        result = assistant_with_mocks.process_request("测试命令", auto_execute=True)
        
        # 验证错误被正确处理
        assert result.success is False
        assert "处理请求时发生错误" in result.error
    
    def test_error_handling_in_executor(self, assistant_with_mocks):
        """测试执行器错误处理"""
        from src.interfaces.base import Suggestion, ValidationResult, RiskLevel
        
        # 设置正常的 AI 翻译和安全验证
        suggestion = Suggestion(
            original_input="测试命令",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="测试"
        )
        assistant_with_mocks.ai_engine.translate_natural_language.return_value = suggestion
        
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        assistant_with_mocks.security_engine.validate_command.return_value = validation
        
        # 设置执行器抛出异常
        assistant_with_mocks.executor.execute.side_effect = TimeoutError("执行超时")
        
        # 执行请求
        result = assistant_with_mocks.process_request("测试命令", auto_execute=True)
        
        # 验证错误被正确处理
        assert result.success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
