"""
基础接口和数据模型的单元测试
"""

import pytest
from datetime import datetime
from src.interfaces.base import (
    RiskLevel,
    ExecutionStatus,
    Suggestion,
    ValidationResult,
    ExecutionResult,
    Context,
    AIEngineInterface,
    SecurityEngineInterface,
    ExecutorInterface,
    StorageInterface,
    LoggerInterface,
)


# ============================================================================
# 枚举类型测试
# ============================================================================

class TestEnums:
    """测试枚举类型"""
    
    def test_risk_level_enum(self):
        """测试风险等级枚举"""
        assert RiskLevel.SAFE.value == "safe"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"
    
    def test_execution_status_enum(self):
        """测试执行状态枚举"""
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.CANCELLED.value == "cancelled"


# ============================================================================
# Suggestion 数据模型测试
# ============================================================================

class TestSuggestion:
    """测试 Suggestion 数据模型"""
    
    def test_suggestion_creation(self):
        """测试创建 Suggestion 对象"""
        suggestion = Suggestion(
            original_input="显示当前时间",
            generated_command="Get-Date",
            confidence_score=0.95,
            explanation="获取当前日期和时间"
        )
        
        assert suggestion.original_input == "显示当前时间"
        assert suggestion.generated_command == "Get-Date"
        assert suggestion.confidence_score == 0.95
        assert suggestion.explanation == "获取当前日期和时间"
        assert suggestion.alternatives == []
        assert isinstance(suggestion.timestamp, datetime)
    
    def test_suggestion_with_alternatives(self):
        """测试带备选命令的 Suggestion"""
        suggestion = Suggestion(
            original_input="显示文件",
            generated_command="Get-ChildItem",
            confidence_score=0.90,
            explanation="列出当前目录的文件",
            alternatives=["ls", "dir"]
        )
        
        assert len(suggestion.alternatives) == 2
        assert "ls" in suggestion.alternatives
        assert "dir" in suggestion.alternatives
    
    def test_suggestion_invalid_confidence_score(self):
        """测试无效的置信度分数"""
        with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
            Suggestion(
                original_input="test",
                generated_command="Get-Date",
                confidence_score=1.5,
                explanation="test"
            )
        
        with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
            Suggestion(
                original_input="test",
                generated_command="Get-Date",
                confidence_score=-0.1,
                explanation="test"
            )
    
    def test_suggestion_empty_input(self):
        """测试空输入"""
        with pytest.raises(ValueError, match="original_input and generated_command cannot be empty"):
            Suggestion(
                original_input="",
                generated_command="Get-Date",
                confidence_score=0.9,
                explanation="test"
            )
    
    def test_suggestion_empty_command(self):
        """测试空命令"""
        with pytest.raises(ValueError, match="original_input and generated_command cannot be empty"):
            Suggestion(
                original_input="test",
                generated_command="",
                confidence_score=0.9,
                explanation="test"
            )


# ============================================================================
# ValidationResult 数据模型测试
# ============================================================================

class TestValidationResult:
    """测试 ValidationResult 数据模型"""
    
    def test_validation_result_safe(self):
        """测试安全的验证结果"""
        result = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        
        assert result.is_valid is True
        assert result.risk_level == RiskLevel.SAFE
        assert result.blocked_reasons == []
        assert result.requires_confirmation is False
        assert result.requires_elevation is False
        assert result.warnings == []
        assert result.is_dangerous is False
    
    def test_validation_result_dangerous(self):
        """测试危险的验证结果"""
        result = ValidationResult(
            is_valid=False,
            risk_level=RiskLevel.CRITICAL,
            blocked_reasons=["包含危险命令模式"],
            requires_confirmation=True
        )
        
        assert result.is_valid is False
        assert result.risk_level == RiskLevel.CRITICAL
        assert len(result.blocked_reasons) == 1
        assert result.requires_confirmation is True
        assert result.is_dangerous is True
    
    def test_validation_result_with_warnings(self):
        """测试带警告的验证结果"""
        result = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.MEDIUM,
            warnings=["此命令可能需要管理员权限"],
            requires_elevation=True
        )
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.requires_elevation is True
    
    def test_is_dangerous_property(self):
        """测试 is_dangerous 属性"""
        safe_result = ValidationResult(is_valid=True, risk_level=RiskLevel.SAFE)
        low_result = ValidationResult(is_valid=True, risk_level=RiskLevel.LOW)
        medium_result = ValidationResult(is_valid=True, risk_level=RiskLevel.MEDIUM)
        high_result = ValidationResult(is_valid=False, risk_level=RiskLevel.HIGH)
        critical_result = ValidationResult(is_valid=False, risk_level=RiskLevel.CRITICAL)
        
        assert safe_result.is_dangerous is False
        assert low_result.is_dangerous is False
        assert medium_result.is_dangerous is False
        assert high_result.is_dangerous is True
        assert critical_result.is_dangerous is True


# ============================================================================
# ExecutionResult 数据模型测试
# ============================================================================

class TestExecutionResult:
    """测试 ExecutionResult 数据模型"""
    
    def test_execution_result_success(self):
        """测试成功的执行结果"""
        result = ExecutionResult(
            success=True,
            command="Get-Date",
            output="2025年1月20日 10:30:45",
            return_code=0,
            execution_time=0.234
        )
        
        assert result.success is True
        assert result.command == "Get-Date"
        assert result.output == "2025年1月20日 10:30:45"
        assert result.error == ""
        assert result.return_code == 0
        assert result.execution_time == 0.234
        assert result.status == ExecutionStatus.SUCCESS
        assert result.has_output is True
        assert result.has_error is False
    
    def test_execution_result_failure(self):
        """测试失败的执行结果"""
        result = ExecutionResult(
            success=False,
            command="Invalid-Command",
            error="命令未找到",
            return_code=1,
            status=ExecutionStatus.FAILED
        )
        
        assert result.success is False
        assert result.error == "命令未找到"
        assert result.return_code == 1
        assert result.status == ExecutionStatus.FAILED
        assert result.has_output is False
        assert result.has_error is True
    
    def test_execution_result_timeout(self):
        """测试超时的执行结果"""
        result = ExecutionResult(
            success=False,
            command="Long-Running-Command",
            status=ExecutionStatus.TIMEOUT,
            execution_time=30.0
        )
        
        assert result.success is False
        assert result.status == ExecutionStatus.TIMEOUT
        assert result.execution_time == 30.0
    
    def test_execution_result_with_metadata(self):
        """测试带元数据的执行结果"""
        result = ExecutionResult(
            success=True,
            command="Get-Process",
            output="process list",
            metadata={"process_count": 42, "platform": "windows"}
        )
        
        assert result.metadata["process_count"] == 42
        assert result.metadata["platform"] == "windows"
    
    def test_has_output_property(self):
        """测试 has_output 属性"""
        result_with_output = ExecutionResult(
            success=True,
            command="test",
            output="some output"
        )
        result_without_output = ExecutionResult(
            success=True,
            command="test",
            output=""
        )
        result_whitespace_only = ExecutionResult(
            success=True,
            command="test",
            output="   \n  "
        )
        
        assert result_with_output.has_output is True
        assert result_without_output.has_output is False
        assert result_whitespace_only.has_output is False
    
    def test_has_error_property(self):
        """测试 has_error 属性"""
        result_with_error = ExecutionResult(
            success=False,
            command="test",
            error="error message"
        )
        result_without_error = ExecutionResult(
            success=True,
            command="test",
            error=""
        )
        
        assert result_with_error.has_error is True
        assert result_without_error.has_error is False


# ============================================================================
# Context 数据模型测试
# ============================================================================

class TestContext:
    """测试 Context 数据模型"""
    
    def test_context_creation(self):
        """测试创建 Context 对象"""
        context = Context(
            session_id="test-session-123",
            user_id="user-456",
            working_directory="/home/user"
        )
        
        assert context.session_id == "test-session-123"
        assert context.user_id == "user-456"
        assert context.working_directory == "/home/user"
        assert context.environment_vars == {}
        assert context.command_history == []
        assert isinstance(context.timestamp, datetime)
    
    def test_context_add_command(self):
        """测试添加命令到历史"""
        context = Context(session_id="test-session")
        
        context.add_command("Get-Date")
        context.add_command("Get-Process")
        context.add_command("Get-Service")
        
        assert len(context.command_history) == 3
        assert context.command_history[0] == "Get-Date"
        assert context.command_history[1] == "Get-Process"
        assert context.command_history[2] == "Get-Service"
    
    def test_context_get_recent_commands(self):
        """测试获取最近的命令"""
        context = Context(session_id="test-session")
        
        for i in range(10):
            context.add_command(f"Command-{i}")
        
        recent = context.get_recent_commands(limit=5)
        
        assert len(recent) == 5
        assert recent[0] == "Command-5"
        assert recent[4] == "Command-9"
    
    def test_context_get_recent_commands_less_than_limit(self):
        """测试获取最近的命令（少于限制数量）"""
        context = Context(session_id="test-session")
        
        context.add_command("Command-1")
        context.add_command("Command-2")
        
        recent = context.get_recent_commands(limit=5)
        
        assert len(recent) == 2
        assert recent[0] == "Command-1"
        assert recent[1] == "Command-2"
    
    def test_context_with_environment_vars(self):
        """测试带环境变量的 Context"""
        context = Context(
            session_id="test-session",
            environment_vars={"PATH": "/usr/bin", "HOME": "/home/user"}
        )
        
        assert context.environment_vars["PATH"] == "/usr/bin"
        assert context.environment_vars["HOME"] == "/home/user"
    
    def test_context_with_metadata(self):
        """测试带元数据的 Context"""
        context = Context(
            session_id="test-session",
            metadata={"platform": "windows", "version": "1.0"}
        )
        
        assert context.metadata["platform"] == "windows"
        assert context.metadata["version"] == "1.0"


# ============================================================================
# 接口测试（验证接口定义）
# ============================================================================

class TestInterfaces:
    """测试接口定义"""
    
    def test_ai_engine_interface_methods(self):
        """测试 AIEngineInterface 接口方法"""
        # 验证接口定义了必需的方法
        assert hasattr(AIEngineInterface, 'translate_natural_language')
        assert hasattr(AIEngineInterface, 'validate_command')
        assert hasattr(AIEngineInterface, 'get_command_explanation')
    
    def test_security_engine_interface_methods(self):
        """测试 SecurityEngineInterface 接口方法"""
        assert hasattr(SecurityEngineInterface, 'validate_command')
        assert hasattr(SecurityEngineInterface, 'check_permissions')
        assert hasattr(SecurityEngineInterface, 'is_dangerous_command')
    
    def test_executor_interface_methods(self):
        """测试 ExecutorInterface 接口方法"""
        assert hasattr(ExecutorInterface, 'execute')
        assert hasattr(ExecutorInterface, 'execute_async')
        assert hasattr(ExecutorInterface, 'is_available')
    
    def test_storage_interface_methods(self):
        """测试 StorageInterface 接口方法"""
        assert hasattr(StorageInterface, 'save_history')
        assert hasattr(StorageInterface, 'load_history')
        assert hasattr(StorageInterface, 'save_config')
        assert hasattr(StorageInterface, 'load_config')
    
    def test_logger_interface_methods(self):
        """测试 LoggerInterface 接口方法"""
        assert hasattr(LoggerInterface, 'log_request')
        assert hasattr(LoggerInterface, 'log_translation')
        assert hasattr(LoggerInterface, 'log_execution')
        assert hasattr(LoggerInterface, 'log_error')
    
    def test_interfaces_are_abstract(self):
        """测试接口是抽象的，不能直接实例化"""
        with pytest.raises(TypeError):
            AIEngineInterface()
        
        with pytest.raises(TypeError):
            SecurityEngineInterface()
        
        with pytest.raises(TypeError):
            ExecutorInterface()
        
        with pytest.raises(TypeError):
            StorageInterface()
        
        with pytest.raises(TypeError):
            LoggerInterface()


# ============================================================================
# 集成测试
# ============================================================================

class TestDataModelIntegration:
    """测试数据模型的集成使用"""
    
    def test_complete_workflow_data_flow(self):
        """测试完整工作流的数据流"""
        # 1. 创建上下文
        context = Context(
            session_id="workflow-test",
            working_directory="/test"
        )
        
        # 2. 创建 AI 建议
        suggestion = Suggestion(
            original_input="显示进程",
            generated_command="Get-Process",
            confidence_score=0.95,
            explanation="列出所有运行的进程"
        )
        
        # 3. 创建验证结果
        validation = ValidationResult(
            is_valid=True,
            risk_level=RiskLevel.SAFE
        )
        
        # 4. 创建执行结果
        execution = ExecutionResult(
            success=True,
            command=suggestion.generated_command,
            output="Process list...",
            execution_time=0.5
        )
        
        # 5. 更新上下文
        context.add_command(suggestion.generated_command)
        
        # 验证数据流
        assert context.command_history[-1] == suggestion.generated_command
        assert validation.is_valid is True
        assert execution.success is True
        assert execution.command == suggestion.generated_command
