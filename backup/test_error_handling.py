"""Tests for Error Handling and Recovery Mechanisms

This module tests the comprehensive error handling, graceful degradation,
and recovery mechanisms.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent))

from error_handling import (
    ErrorHandler, ErrorContext, RecoveryStrategy, RecoveryAction, 
    ErrorSeverity, ErrorCategory, ComponentHealthMonitor, error_handler
)
from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import Platform, UserRole, LogLevel, RiskLevel


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration"""
    config = ServerConfig(
        version="1.0.0-test",
        platform=Platform.WINDOWS,
        debug_mode=True,
        model=ModelConfig(),
        security=SecurityConfig(),
        logging=LoggingConfig(),
        execution=ExecutionConfig(),
        storage=StorageConfig(data_directory=str(Path(temp_dir) / "storage")),
        mcp_server=MCPServerConfig()
    )
    return config


@pytest.fixture
def error_handler_instance():
    """Create fresh error handler instance"""
    return ErrorHandler()


@pytest.fixture
def mock_integration(test_config):
    """Create mock integration for testing"""
    integration = AIPowerShellAssistantIntegration()
    integration.config = test_config
    integration._initialized = True
    return integration


class TestErrorHandler:
    """Test error handler functionality"""
    
    @pytest.mark.asyncio
    async def test_error_classification(self, error_handler_instance):
        """Test error classification"""
        # AI engine error
        context = ErrorContext(component="ai_engine", operation="translate")
        error = Exception("AI model not available")
        
        error_type = error_handler_instance._classify_error(error, context)
        assert error_type == "ai_engine_unavailable"
        
        # Timeout error
        timeout_error = TimeoutError("Operation timed out")
        error_type = error_handler_instance._classify_error(timeout_error, context)
        assert error_type == "timeout_error"
        
        # Security engine error
        security_context = ErrorContext(component="security_engine", operation="validate")
        security_error = Exception("Security engine unavailable")
        
        error_type = error_handler_instance._classify_error(security_error, security_context)
        assert error_type == "security_engine_unavailable"
    
    @pytest.mark.asyncio
    async def test_severity_determination(self, error_handler_instance):
        """Test error severity determination"""
        # Critical error in security engine
        critical_context = ErrorContext(component="security_engine", operation="validate")
        critical_error = Exception("Critical security failure")
        
        severity = error_handler_instance._determine_severity(critical_error, critical_context)
        assert severity == ErrorSeverity.CRITICAL
        
        # High severity error
        high_context = ErrorContext(component="ai_engine", operation="process")
        high_error = Exception("AI engine unavailable")
        
        severity = error_handler_instance._determine_severity(high_error, high_context)
        assert severity == ErrorSeverity.HIGH
        
        # Medium severity error
        medium_context = ErrorContext(component="executor", operation="execute")
        medium_error = TimeoutError("Command timed out")
        
        severity = error_handler_instance._determine_severity(medium_error, medium_context)
        assert severity == ErrorSeverity.MEDIUM
    
    @pytest.mark.asyncio
    async def test_ai_engine_fallback(self, error_handler_instance):
        """Test AI engine fallback recovery"""
        context = ErrorContext(
            component="ai_engine",
            operation="translate_natural_language",
            user_input="list processes"
        )
        
        error = Exception("AI engine not available")
        result = await error_handler_instance.handle_error(error, context, "ai_engine_unavailable")
        
        assert result["error_handled"] is True
        assert result["recovery_attempted"] is True
        assert result["recovery_successful"] is True
        assert result["recovery_action"] == "fallback"
        
        fallback_result = result["fallback_result"]
        assert fallback_result["success"] is False
        assert fallback_result["fallback_mode"] is True
        assert "AI engine not available" in fallback_result["error"]
    
    @pytest.mark.asyncio
    async def test_security_fail_safe(self, error_handler_instance):
        """Test security engine fail-safe recovery"""
        context = ErrorContext(
            component="security_engine",
            operation="validate_command",
            user_input="Remove-Item -Recurse"
        )
        
        error = Exception("Security engine unavailable")
        result = await error_handler_instance.handle_error(error, context, "security_engine_unavailable")
        
        assert result["error_handled"] is True
        assert result["recovery_attempted"] is True
        assert result["recovery_successful"] is True
        assert result["recovery_action"] == "fail_safe"
        
        fail_safe_result = result["fail_safe_result"]
        assert fail_safe_result["success"] is False
        assert fail_safe_result["fail_safe_mode"] is True
        assert "Security validation unavailable" in fail_safe_result["blocked_reasons"]
    
    @pytest.mark.asyncio
    async def test_executor_degraded_mode(self, error_handler_instance):
        """Test executor degraded mode recovery"""
        context = ErrorContext(
            component="executor",
            operation="execute_command",
            user_input="Get-Process"
        )
        
        error = Exception("Executor unavailable")
        result = await error_handler_instance.handle_error(error, context, "executor_unavailable")
        
        assert result["error_handled"] is True
        assert result["recovery_attempted"] is True
        assert result["recovery_successful"] is True
        assert result["recovery_action"] == "degrade"
        
        degraded_result = result["degraded_result"]
        assert degraded_result["success"] is False
        assert degraded_result["degraded_mode"] is True
        assert "system_info" in degraded_result["available_operations"]
    
    @pytest.mark.asyncio
    async def test_storage_degraded_mode(self, error_handler_instance):
        """Test storage degraded mode recovery"""
        context = ErrorContext(
            component="storage",
            operation="save_history"
        )
        
        error = Exception("Storage unavailable")
        result = await error_handler_instance.handle_error(error, context, "storage_unavailable")
        
        assert result["error_handled"] is True
        assert result["recovery_attempted"] is True
        assert result["recovery_successful"] is True
        assert result["recovery_action"] == "degrade"
        
        degraded_result = result["degraded_result"]
        assert degraded_result["success"] is True
        assert degraded_result["degraded_mode"] is True
        assert "memory-only mode" in degraded_result["warning"]
    
    @pytest.mark.asyncio
    async def test_retry_recovery_strategy(self, error_handler_instance):
        """Test retry recovery strategy"""
        context = ErrorContext(
            component="ai_engine",
            operation="process"
        )
        
        error = Exception("Temporary processing error")
        result = await error_handler_instance.handle_error(error, context, "ai_processing_error")
        
        assert result["error_handled"] is True
        assert result["recovery_attempted"] is True
        assert result["recovery_action"] == "retry"
        
        # Check retry parameters
        assert "max_retries" in result
        assert "retry_delay" in result
    
    @pytest.mark.asyncio
    async def test_error_statistics(self, error_handler_instance):
        """Test error statistics collection"""
        # Generate some test errors
        contexts = [
            ErrorContext(component="ai_engine", operation="translate"),
            ErrorContext(component="security_engine", operation="validate"),
            ErrorContext(component="executor", operation="execute")
        ]
        
        errors = [
            Exception("AI error"),
            Exception("Security error"),
            TimeoutError("Execution timeout")
        ]
        
        for context, error in zip(contexts, errors):
            await error_handler_instance.handle_error(error, context)
        
        stats = error_handler_instance.get_error_statistics()
        
        assert stats["total_errors"] == 3
        assert stats["recovery_attempts"] >= 0
        assert "severity_breakdown" in stats
        assert "category_breakdown" in stats
        assert "most_common_errors" in stats
    
    @pytest.mark.asyncio
    async def test_custom_recovery_strategy(self, error_handler_instance):
        """Test custom recovery strategy registration"""
        def custom_fallback(context):
            return {"custom": True, "message": "Custom recovery"}
        
        custom_strategy = RecoveryStrategy(
            action=RecoveryAction.FALLBACK,
            fallback_function=custom_fallback
        )
        
        error_handler_instance.register_recovery_strategy("custom_error", custom_strategy)
        
        context = ErrorContext(component="test", operation="test")
        error = Exception("Custom error")
        
        result = await error_handler_instance.handle_error(error, context, "custom_error")
        
        assert result["recovery_attempted"] is True
        assert result["fallback_result"]["custom"] is True


class TestComponentHealthMonitor:
    """Test component health monitoring"""
    
    @pytest.fixture
    def health_monitor(self):
        """Create health monitor instance"""
        return ComponentHealthMonitor()
    
    @pytest.mark.asyncio
    async def test_component_registration(self, health_monitor):
        """Test component registration"""
        def mock_health_check():
            return {"status": "healthy"}
        
        def mock_recovery():
            return True
        
        health_monitor.register_component(
            "test_component",
            mock_health_check,
            mock_recovery
        )
        
        assert "test_component" in health_monitor.component_status
        status = health_monitor.component_status["test_component"]
        assert status["health_check"] == mock_health_check
        assert status["recovery_func"] == mock_recovery
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, health_monitor):
        """Test successful health check"""
        def healthy_check():
            return {"status": "healthy"}
        
        health_monitor.register_component("healthy_component", healthy_check)
        
        # Perform health check
        status = health_monitor.component_status["healthy_component"]
        await health_monitor._check_component_health("healthy_component", status)
        
        assert status["status"] == "healthy"
        assert status["consecutive_failures"] == 0
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, health_monitor):
        """Test health check failure"""
        def unhealthy_check():
            return {"status": "unhealthy", "error": "Component failed"}
        
        health_monitor.register_component("unhealthy_component", unhealthy_check)
        
        # Perform health check
        status = health_monitor.component_status["unhealthy_component"]
        await health_monitor._check_component_health("unhealthy_component", status)
        
        assert status["status"] == "unhealthy"
        assert status["failure_count"] > 0
        assert status["consecutive_failures"] > 0
    
    @pytest.mark.asyncio
    async def test_recovery_attempt(self, health_monitor):
        """Test recovery attempt after failures"""
        failure_count = 0
        
        def failing_check():
            return {"status": "unhealthy"}
        
        def mock_recovery():
            return True
        
        health_monitor.register_component("failing_component", failing_check, mock_recovery)
        health_monitor.failure_threshold = 2  # Lower threshold for testing
        
        status = health_monitor.component_status["failing_component"]
        
        # Trigger multiple failures to reach threshold
        for _ in range(3):
            await health_monitor._check_component_health("failing_component", status)
        
        # Recovery should have been attempted
        assert status["last_recovery"] is not None


class TestIntegrationErrorHandling:
    """Test error handling in integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_ai_engine_unavailable_graceful_degradation(self, mock_integration):
        """Test graceful degradation when AI engine is unavailable"""
        tool_implementations = MCPToolImplementations(mock_integration)
        
        # Set AI engine to None to simulate unavailability
        mock_integration.ai_engine = None
        mock_integration.logging_engine = AsyncMock()
        mock_integration.context_manager = AsyncMock()
        mock_integration.context_manager.create_session.return_value = "test-session"
        mock_integration.logging_engine.log_user_input.return_value = "corr-123"
        
        result = await tool_implementations.natural_language_to_powershell("list processes")
        
        assert result["success"] is False
        assert result["fallback_mode"] is True
        assert "AI engine not available" in result["error"]
        assert "error_handling" in result
        assert result["error_handling"]["recovery_attempted"] is True
    
    @pytest.mark.asyncio
    async def test_security_engine_unavailable_fail_safe(self, mock_integration):
        """Test fail-safe behavior when security engine is unavailable"""
        tool_implementations = MCPToolImplementations(mock_integration)
        
        # Set security engine to None to simulate unavailability
        mock_integration.security_engine = None
        mock_integration.logging_engine = AsyncMock()
        mock_integration.context_manager = AsyncMock()
        mock_integration.context_manager.create_session.return_value = "test-session"
        mock_integration.logging_engine.log_user_input.return_value = "corr-123"
        
        result = await tool_implementations.execute_powershell_command("Get-Process")
        
        assert result["success"] is False
        assert result["fail_safe_mode"] is True
        assert "Security validation unavailable" in result["blocked_reasons"]
        assert "error_handling" in result
        assert result["error_handling"]["recovery_attempted"] is True
    
    @pytest.mark.asyncio
    async def test_executor_unavailable_degraded_mode(self, mock_integration):
        """Test degraded mode when executor is unavailable"""
        tool_implementations = MCPToolImplementations(mock_integration)
        
        # Set executor to None to simulate unavailability
        mock_integration.executor = None
        mock_integration.logging_engine = AsyncMock()
        mock_integration.context_manager = AsyncMock()
        mock_integration.context_manager.create_session.return_value = "test-session"
        mock_integration.logging_engine.log_user_input.return_value = "corr-123"
        
        result = await tool_implementations.get_powershell_info()
        
        assert result["success"] is True  # Still succeeds in degraded mode
        assert result["degraded_mode"] is True
        assert result["powershell"]["status"] == "unavailable"
        assert "error_handling" in result
        assert result["error_handling"]["recovery_attempted"] is True
    
    @pytest.mark.asyncio
    async def test_multiple_component_failures(self, mock_integration):
        """Test handling of multiple component failures"""
        tool_implementations = MCPToolImplementations(mock_integration)
        
        # Simulate multiple component failures
        mock_integration.ai_engine = None
        mock_integration.security_engine = None
        mock_integration.executor = None
        mock_integration.logging_engine = AsyncMock()
        mock_integration.context_manager = AsyncMock()
        mock_integration.context_manager.create_session.return_value = "test-session"
        mock_integration.logging_engine.log_user_input.return_value = "corr-123"
        
        # Test natural language processing
        nl_result = await tool_implementations.natural_language_to_powershell("test")
        assert nl_result["success"] is False
        assert nl_result["fallback_mode"] is True
        
        # Test command execution
        exec_result = await tool_implementations.execute_powershell_command("test")
        assert exec_result["success"] is False
        assert exec_result["fail_safe_mode"] is True
        
        # Test system info
        info_result = await tool_implementations.get_powershell_info()
        assert info_result["success"] is True  # Degraded mode still works
        assert info_result["degraded_mode"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])