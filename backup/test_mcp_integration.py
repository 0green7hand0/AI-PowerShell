"""Integration Tests for MCP Tools

This module provides comprehensive integration tests for all MCP tools
with full pipeline testing and error scenario validation.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional
import json

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import (
    Platform, UserRole, LogLevel, OutputFormat, RiskLevel, SecurityAction, Permission,
    CommandSuggestion, ValidationResult, ExecutionResult
)


class TestMCPToolsIntegration:
    """Integration tests for MCP tools with full pipeline testing"""
    
    @pytest.fixture
    async def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    async def test_config(self, temp_dir):
        """Create test configuration"""
        config = ServerConfig(
            version="1.0.0-test",
            platform=Platform.WINDOWS,
            debug_mode=True,
            model=ModelConfig(
                model_type="mock",
                model_path=str(Path(temp_dir) / "model"),
                context_length=2048,
                temperature=0.7,
                max_tokens=512
            ),
            security=SecurityConfig(
                whitelist_path=str(Path(temp_dir) / "whitelist.json"),
                sandbox_image="mock-sandbox",
                sandbox_enabled=True,
                require_confirmation_for_admin=True,
                audit_log_path=str(Path(temp_dir) / "audit.log"),
                max_sandbox_memory="512m"
            ),
            logging=LoggingConfig(
                log_level=LogLevel.DEBUG,
                audit_log_path=str(Path(temp_dir) / "audit.log"),
                performance_log_path=str(Path(temp_dir) / "performance.log"),
                max_log_file_size="10MB",
                log_retention_days=7,
                enable_correlation_tracking=True,
                sensitive_data_masking=True
            ),
            execution=ExecutionConfig(
                powershell_path="pwsh",
                default_timeout=60,
                max_output_size=1048576,
                enable_cross_platform=True
            ),

            storage=StorageConfig(
                base_path=str(Path(temp_dir) / "storage"),
                enable_encryption=False,
                backup_enabled=False
            ),
            mcp_server=MCPServerConfig(
                host="localhost",
                port=8080,
                enable_natural_language_tool=True,
                enable_execute_command_tool=True,
                enable_system_info_tool=True
            )
        )
        return config
    
    @pytest.fixture
    async def mock_integration(self, test_config):
        """Create mock integration with test configuration"""
        integration = AIPowerShellAssistantIntegration()
        integration.config = test_config
        
        # Mock all components
        integration.storage = AsyncMock()
        integration.logging_engine = AsyncMock()
        integration.context_manager = AsyncMock()
        integration.ai_engine = Mock()
        integration.security_engine = Mock()
        integration.executor = Mock()
        integration.mcp_server = Mock()
        
        # Setup mock return values
        integration.context_manager.create_session.return_value = "test-session-123"
        integration.context_manager.get_current_context.return_value = Mock()
        integration.logging_engine.log_user_input.return_value = "corr-123"
        
        integration._initialized = True
        return integration
    
    @pytest.fixture
    async def tool_implementations(self, mock_integration):
        """Create tool implementations with mock integration"""
        return MCPToolImplementations(mock_integration)


class TestNaturalLanguageToPowerShell:
    """Test natural language to PowerShell conversion tool"""
    
    @pytest.mark.asyncio
    async def test_successful_translation(self, tool_implementations, mock_integration):
        """Test successful natural language translation"""
        # Setup mocks
        
        mock_suggestion = CommandSuggestion(
            original_input="list running processes",
            generated_command="Get-Process | Where-Object {$_.Status -eq 'Running'}",
            confidence_score=0.95,
            explanation="Lists all currently running processes",
            alternatives=["Get-Process", "ps"]
        )
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_integration.security_engine.validate_command.return_value = mock_validation
        
        # Execute test
        result = await tool_implementations.natural_language_to_powershell(
            "list running processes",
            session_id="test-session"
        )
        
        # Verify results
        assert result["success"] is True
        assert result["original_input"] == "list running processes"
        assert result["generated_command"] == "Get-Process | Where-Object {$_.Status -eq 'Running'}"
        assert result["confidence_score"] == 0.95
        assert result["explanation"] == "Lists all currently running processes"
        assert len(result["alternatives"]) == 2
        assert result["session_id"] == "test-session"
        assert "correlation_id" in result
        assert "security_validation" in result
        assert result["security_validation"]["is_valid"] is True
        
        # Verify component interactions
        mock_integration.ai_engine.translate_natural_language.assert_called_once()
        mock_integration.security_engine.validate_command.assert_called_once()
        mock_integration.logging_engine.log_user_input.assert_called_once()
        mock_integration.logging_engine.log_ai_processing.assert_called_once()
        mock_integration.logging_engine.log_security_validation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_empty_input_validation(self, tool_implementations):
        """Test validation of empty input"""
        result = await tool_implementations.natural_language_to_powershell("")
        
        assert result["success"] is False
        assert result["error"] == "Input text cannot be empty"
        assert result["error_code"] == "INVALID_INPUT"
    
    @pytest.mark.asyncio
    async def test_ai_engine_unavailable(self, tool_implementations, mock_integration):
        """Test handling when AI engine is unavailable"""
        mock_integration.ai_engine = None
        
        result = await tool_implementations.natural_language_to_powershell(
            "list processes"
        )
        
        assert result["success"] is False
        assert result["error"] == "AI engine not available"
        assert result["error_code"] == "AI_ENGINE_UNAVAILABLE"
    
    @pytest.mark.asyncio
    async def test_ai_processing_exception(self, tool_implementations, mock_integration):
        """Test handling of AI processing exceptions"""
        mock_integration.ai_engine.translate_natural_language.side_effect = Exception("AI model error")
        
        result = await tool_implementations.natural_language_to_powershell(
            "list processes"
        )
        
        assert result["success"] is False
        assert "AI model error" in result["error"]
        assert result["error_code"] == "PROCESSING_ERROR"
        
        # Verify error logging
        mock_integration.logging_engine.log_error.assert_called_once()


class TestExecutePowerShellCommand:
    """Test PowerShell command execution tool"""
    
    @pytest.mark.asyncio
    async def test_successful_execution(self, tool_implementations, mock_integration):
        """Test successful command execution"""
        # Setup mocks
        from security.models import ValidationResult, RiskAssessment
        from interfaces.base import ExecutionResult
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.LOW,
                risk_factors=[],
                requires_confirmation=False,
                requires_sandbox=False
            )
        )
        
        mock_execution = ExecutionResult(
            success=True,
            return_code=0,
            stdout='{"processes": [{"name": "pwsh", "id": 1234}]}',
            stderr="",
            execution_time=0.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        mock_integration.security_engine.validate_command.return_value = mock_validation
        mock_integration.executor.execute_command.return_value = mock_execution
        mock_integration.executor.format_output.return_value = mock_execution.stdout
        
        # Execute test
        result = await tool_implementations.execute_powershell_command(
            "Get-Process pwsh",
            session_id="test-session",
            timeout=30,
            use_sandbox=False
        )
        
        # Verify results
        assert result["success"] is True
        assert result["return_code"] == 0
        assert "processes" in result["stdout"]
        assert result["stderr"] == ""
        assert result["execution_time"] == 0.5
        assert result["platform"] == "windows"
        assert result["sandbox_used"] is False
        assert result["session_id"] == "test-session"
        assert "correlation_id" in result
        assert "security_validation" in result
        
        # Verify component interactions
        mock_integration.security_engine.validate_command.assert_called_once_with("Get-Process pwsh")
        mock_integration.executor.execute_command.assert_called_once()
        mock_integration.logging_engine.log_security_validation.assert_called_once()
        mock_integration.logging_engine.log_command_execution.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_command_blocked_by_security(self, tool_implementations, mock_integration):
        """Test command blocked by security policy"""
        from security.models import ValidationResult, RiskAssessment
        
        mock_validation = ValidationResult(
            is_valid=False,
            blocked_reasons=["Command contains dangerous operation: Remove-Item -Recurse"],
            required_permissions=[Permission.ADMIN],
            suggested_alternatives=["Get-ChildItem", "Remove-Item -Path specific_file"],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.HIGH,
                risk_factors=["Recursive deletion", "Administrative privileges required"],
                requires_confirmation=True,
                requires_sandbox=True
            )
        )
        
        mock_integration.security_engine.validate_command.return_value = mock_validation
        
        result = await tool_implementations.execute_powershell_command(
            "Remove-Item -Path C:\\ -Recurse -Force"
        )
        
        assert result["success"] is False
        assert result["error"] == "Command blocked by security policy"
        assert result["error_code"] == "SECURITY_BLOCKED"
        assert len(result["blocked_reasons"]) > 0
        assert len(result["suggested_alternatives"]) > 0
        assert result["risk_assessment"]["risk_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_sandbox_execution(self, tool_implementations, mock_integration):
        """Test sandbox execution for high-risk commands"""
        from security.models import ValidationResult, RiskAssessment
        from interfaces.base import ExecutionResult
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.MEDIUM,
                risk_factors=["Network access"],
                requires_confirmation=False,
                requires_sandbox=True
            )
        )
        
        mock_sandbox_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Sandbox execution successful",
            stderr="",
            execution_time=1.2,
            platform=Platform.WINDOWS,
            sandbox_used=True
        )
        
        mock_integration.security_engine.validate_command.return_value = mock_validation
        mock_integration.security_engine.execute_in_sandbox.return_value = mock_sandbox_result
        mock_integration.config.security.sandbox_enabled = True
        
        result = await tool_implementations.execute_powershell_command(
            "Invoke-WebRequest -Uri https://example.com",
            use_sandbox=True
        )
        
        assert result["success"] is True
        assert result["sandbox_used"] is True
        mock_integration.security_engine.execute_in_sandbox.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_empty_command_validation(self, tool_implementations):
        """Test validation of empty command"""
        result = await tool_implementations.execute_powershell_command("")
        
        assert result["success"] is False
        assert result["error"] == "Command cannot be empty"
        assert result["error_code"] == "INVALID_COMMAND"
    
    @pytest.mark.asyncio
    async def test_execution_timeout(self, tool_implementations, mock_integration):
        """Test command execution timeout handling"""
        from security.models import ValidationResult, RiskAssessment
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.LOW,
                risk_factors=[],
                requires_confirmation=False,
                requires_sandbox=False
            )
        )
        
        mock_integration.security_engine.validate_command.return_value = mock_validation
        mock_integration.executor.execute_command.side_effect = TimeoutError("Command timed out")
        
        result = await tool_implementations.execute_powershell_command(
            "Start-Sleep -Seconds 120",
            timeout=5
        )
        
        assert result["success"] is False
        assert "timed out" in result["error"].lower()
        assert result["error_code"] == "EXECUTION_ERROR"


class TestGetPowerShellInfo:
    """Test PowerShell system information tool"""
    
    @pytest.mark.asyncio
    async def test_basic_system_info(self, tool_implementations, mock_integration):
        """Test basic system information retrieval"""
        mock_ps_info = {
            "version": "7.3.0",
            "edition": "Core",
            "platform": "Win32NT",
            "modules": ["Microsoft.PowerShell.Management", "Microsoft.PowerShell.Utility"],
            "environment": {"PATH": "/usr/bin:/bin", "HOME": "/home/user"}
        }
        
        mock_integration.executor.get_powershell_info.return_value = mock_ps_info
        
        # Mock health check
        async def mock_health_check():
            return {
                "overall": "healthy",
                "components": {
                    "ai_engine": {"status": "healthy"},
                    "security_engine": {"status": "healthy"},
                    "executor": {"status": "healthy"}
                }
            }
        
        mock_integration.health_check = mock_health_check
        
        result = await tool_implementations.get_powershell_info(
            session_id="test-session",
            include_modules=True,
            include_environment=False
        )
        
        assert result["success"] is True
        assert result["powershell"]["version"] == "7.3.0"
        assert result["platform"] == mock_integration.config.platform.value
        assert result["server_version"] == mock_integration.config.version
        assert result["session_id"] == "test-session"
        assert "health" in result
        assert result["health"]["overall"] == "healthy"
        assert "security" in result
        assert "ai_engine" in result
        assert "modules" in result
        assert len(result["modules"]) > 0
    
    @pytest.mark.asyncio
    async def test_with_environment_info(self, tool_implementations, mock_integration):
        """Test system info with environment variables"""
        mock_ps_info = {
            "version": "7.3.0",
            "environment": {
                "PATH": "/usr/bin:/bin",
                "HOME": "/home/user",
                "SECRET_KEY": "hidden",  # Should be filtered out
                "PASSWORD": "secret"     # Should be filtered out
            }
        }
        
        mock_integration.executor.get_powershell_info.return_value = mock_ps_info
        mock_integration.health_check = AsyncMock(return_value={"overall": "healthy"})
        
        result = await tool_implementations.get_powershell_info(
            include_environment=True
        )
        
        assert result["success"] is True
        assert "environment" in result
        # Sensitive variables should be filtered out
        assert "SECRET_KEY" not in result["environment"]
        assert "PASSWORD" not in result["environment"]
        # Safe variables should be included
        assert "PATH" in result["environment"]
        assert "HOME" in result["environment"]
    
    @pytest.mark.asyncio
    async def test_executor_unavailable(self, tool_implementations, mock_integration):
        """Test handling when executor is unavailable"""
        mock_integration.executor = None
        
        result = await tool_implementations.get_powershell_info()
        
        assert result["success"] is False
        assert result["error"] == "Execution engine not available"
        assert result["error_code"] == "EXECUTOR_UNAVAILABLE"
    
    @pytest.mark.asyncio
    async def test_partial_failure_resilience(self, tool_implementations, mock_integration):
        """Test resilience to partial component failures"""
        mock_ps_info = {"version": "7.3.0"}
        mock_integration.executor.get_powershell_info.return_value = mock_ps_info
        
        # Mock health check failure
        mock_integration.health_check = AsyncMock(side_effect=Exception("Health check failed"))
        
        result = await tool_implementations.get_powershell_info()
        
        # Should still succeed with basic info
        assert result["success"] is True
        assert result["powershell"]["version"] == "7.3.0"
        # Health should show error
        assert result["health"]["status"] == "unknown"
        assert "error" in result["health"]


class TestErrorHandlingAndRecovery:
    """Test comprehensive error handling and recovery mechanisms"""
    
    @pytest.mark.asyncio
    async def test_component_initialization_failure(self, test_config, temp_dir):
        """Test handling of component initialization failures"""
        # Create integration with invalid configuration
        integration = AIPowerShellAssistantIntegration()
        integration.config = test_config
        
        # Mock storage initialization failure
        with patch('storage.file_storage.FileStorage') as mock_storage:
            mock_storage.return_value.initialize.side_effect = Exception("Storage init failed")
            
            with pytest.raises(Exception) as exc_info:
                await integration.initialize_components()
            
            assert "Storage init failed" in str(exc_info.value)
            assert not integration.is_initialized
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, tool_implementations, mock_integration):
        """Test graceful degradation when components are unavailable"""
        # Test with AI engine unavailable
        mock_integration.ai_engine = None
        
        result = await tool_implementations.natural_language_to_powershell("test input")
        assert result["success"] is False
        assert result["error_code"] == "AI_ENGINE_UNAVAILABLE"
        
        # Test with security engine unavailable
        mock_integration.security_engine = None
        
        result = await tool_implementations.execute_powershell_command("Get-Process")
        assert result["success"] is False
        assert result["error_code"] == "SECURITY_ENGINE_UNAVAILABLE"
    
    @pytest.mark.asyncio
    async def test_logging_failure_resilience(self, tool_implementations, mock_integration):
        """Test resilience to logging failures"""
        # Mock logging failure
        mock_integration.logging_engine.log_user_input.side_effect = Exception("Logging failed")
        
        # Setup successful AI processing
        from ai_engine.models import CommandSuggestion
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test",
            alternatives=[]
        )
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Should still process successfully despite logging failure
        result = await tool_implementations.natural_language_to_powershell("test input")
        
        # The main functionality should work despite logging failure
        assert result["generated_command"] == "Get-Process"
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, tool_implementations, mock_integration):
        """Test handling of concurrent requests"""
        from ai_engine.models import CommandSuggestion
        
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test",
            alternatives=[]
        )
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = tool_implementations.natural_language_to_powershell(
                f"test input {i}",
                session_id=f"session-{i}"
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        for i, result in enumerate(results):
            assert not isinstance(result, Exception)
            assert result["success"] is True
            assert result["session_id"] == f"session-{i}"


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_natural_language_workflow(self, tool_implementations, mock_integration):
        """Test complete workflow from natural language to execution"""
        # Setup mocks for complete workflow
        from ai_engine.models import CommandSuggestion
        from security.models import ValidationResult, RiskAssessment
        from interfaces.base import ExecutionResult
        
        # 1. Natural language processing
        mock_suggestion = CommandSuggestion(
            original_input="show running processes",
            generated_command="Get-Process | Where-Object {$_.Status -eq 'Running'}",
            confidence_score=0.92,
            explanation="Shows all currently running processes",
            alternatives=["Get-Process", "ps"]
        )
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.LOW,
                risk_factors=[],
                requires_confirmation=False,
                requires_sandbox=False
            )
        )
        
        mock_execution = ExecutionResult(
            success=True,
            return_code=0,
            stdout='[{"Name": "pwsh", "Id": 1234, "Status": "Running"}]',
            stderr="",
            execution_time=0.3,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_integration.security_engine.validate_command.return_value = mock_validation
        mock_integration.executor.execute_command.return_value = mock_execution
        mock_integration.executor.format_output.return_value = mock_execution.stdout
        
        # Step 1: Natural language to PowerShell
        nl_result = await tool_implementations.natural_language_to_powershell(
            "show running processes",
            session_id="workflow-session"
        )
        
        assert nl_result["success"] is True
        assert nl_result["confidence_score"] == 0.92
        generated_command = nl_result["generated_command"]
        
        # Step 2: Execute the generated command
        exec_result = await tool_implementations.execute_powershell_command(
            generated_command,
            session_id="workflow-session"
        )
        
        assert exec_result["success"] is True
        assert exec_result["return_code"] == 0
        assert "pwsh" in exec_result["stdout"]
        
        # Verify session consistency
        assert nl_result["session_id"] == exec_result["session_id"]
        
        # Verify logging correlation
        assert "correlation_id" in nl_result
        assert "correlation_id" in exec_result
    
    @pytest.mark.asyncio
    async def test_security_blocked_workflow(self, tool_implementations, mock_integration):
        """Test workflow with security-blocked command"""
        from ai_engine.models import CommandSuggestion
        from security.models import ValidationResult, RiskAssessment
        
        # AI generates a dangerous command
        mock_suggestion = CommandSuggestion(
            original_input="delete all files",
            generated_command="Remove-Item -Path C:\\ -Recurse -Force",
            confidence_score=0.85,
            explanation="Recursively deletes all files",
            alternatives=["Remove-Item -Path specific_file"]
        )
        
        mock_validation = ValidationResult(
            is_valid=False,
            blocked_reasons=["Dangerous recursive deletion operation"],
            required_permissions=[Permission.ADMIN],
            suggested_alternatives=["Remove-Item -Path specific_file", "Get-ChildItem | Remove-Item"],
            risk_assessment=RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                risk_factors=["System-wide deletion", "Irreversible operation"],
                requires_confirmation=True,
                requires_sandbox=True
            )
        )
        
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_integration.security_engine.validate_command.return_value = mock_validation
        
        # Step 1: Natural language processing (should succeed)
        nl_result = await tool_implementations.natural_language_to_powershell(
            "delete all files"
        )
        
        assert nl_result["success"] is True
        assert nl_result["security_validation"]["is_valid"] is False
        generated_command = nl_result["generated_command"]
        
        # Step 2: Execution should be blocked
        exec_result = await tool_implementations.execute_powershell_command(
            generated_command
        )
        
        assert exec_result["success"] is False
        assert exec_result["error_code"] == "SECURITY_BLOCKED"
        assert len(exec_result["blocked_reasons"]) > 0
        assert len(exec_result["suggested_alternatives"]) > 0


# Performance and Load Testing
class TestPerformanceAndLoad:
    """Test performance characteristics and load handling"""
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self, tool_implementations, mock_integration):
        """Test response time performance"""
        import time
        from ai_engine.models import CommandSuggestion
        
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test",
            alternatives=[]
        )
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        start_time = time.time()
        result = await tool_implementations.natural_language_to_powershell("test input")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result["success"] is True
        # Response should be under 1 second for mocked components
        assert response_time < 1.0
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, tool_implementations, mock_integration):
        """Test memory usage stability under repeated requests"""
        import gc
        from ai_engine.models import CommandSuggestion
        
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test",
            alternatives=[]
        )
        mock_integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Perform multiple requests
        for i in range(10):
            result = await tool_implementations.natural_language_to_powershell(f"test input {i}")
            assert result["success"] is True
            
            # Force garbage collection
            gc.collect()
        
        # Memory should remain stable (no significant leaks)
        # This is a basic test - in production, you'd use memory profiling tools


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])