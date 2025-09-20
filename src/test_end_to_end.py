"""End-to-End Integration Tests

This module provides end-to-end tests for the complete AI PowerShell Assistant
system integration, testing the full workflow from startup to tool execution.
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

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from startup_system import SystemIntegration
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import Platform, LogLevel, CommandSuggestion, ValidationResult, ExecutionResult, RiskLevel


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


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_natural_language_workflow(self, test_config):
        """Test complete workflow from natural language to PowerShell execution"""
        
        # Create integration with mocked components
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
        
        # Mock AI engine response
        mock_suggestion = CommandSuggestion(
            original_input="list running processes",
            generated_command="Get-Process | Where-Object {$_.Status -eq 'Running'}",
            confidence_score=0.95,
            explanation="Lists all currently running processes",
            alternatives=["Get-Process", "ps"]
        )
        integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Mock security validation
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        integration.security_engine.validate_command.return_value = mock_validation
        
        # Mock command execution
        mock_execution = ExecutionResult(
            success=True,
            return_code=0,
            stdout='[{"Name": "pwsh", "Id": 1234, "Status": "Running"}]',
            stderr="",
            execution_time=0.3,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        integration.executor.execute_command.return_value = mock_execution
        integration.executor.format_output.return_value = mock_execution.stdout
        
        integration._initialized = True
        
        # Create tool implementations
        tool_implementations = MCPToolImplementations(integration)
        
        # Step 1: Natural language to PowerShell
        nl_result = await tool_implementations.natural_language_to_powershell(
            "list running processes",
            session_id="test-session"
        )
        
        assert nl_result["success"] is True
        assert nl_result["confidence_score"] == 0.95
        assert "Get-Process" in nl_result["generated_command"]
        generated_command = nl_result["generated_command"]
        
        # Step 2: Execute the generated command
        exec_result = await tool_implementations.execute_powershell_command(
            generated_command,
            session_id="test-session"
        )
        
        assert exec_result["success"] is True
        assert exec_result["return_code"] == 0
        assert "pwsh" in exec_result["stdout"]
        
        # Step 3: Get system information
        info_result = await tool_implementations.get_powershell_info(
            session_id="test-session"
        )
        
        assert info_result["success"] is True
        assert info_result["session_id"] == "test-session"
        
        # Verify session consistency across all operations
        assert nl_result["session_id"] == exec_result["session_id"] == info_result["session_id"]
        
        # Verify logging correlation
        assert "correlation_id" in nl_result
        assert "correlation_id" in exec_result
        assert "correlation_id" in info_result
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, test_config):
        """Test error handling throughout the complete workflow"""
        
        # Create integration with failing components
        integration = AIPowerShellAssistantIntegration()
        integration.config = test_config
        
        # Mock components with failures
        integration.storage = AsyncMock()
        integration.logging_engine = AsyncMock()
        integration.context_manager = AsyncMock()
        integration.ai_engine = None  # AI engine unavailable
        integration.security_engine = None  # Security engine unavailable
        integration.executor = None  # Executor unavailable
        integration.mcp_server = Mock()
        
        # Setup mock return values
        integration.context_manager.create_session.return_value = "test-session-123"
        integration.logging_engine.log_user_input.return_value = "corr-123"
        
        integration._initialized = True
        
        # Create tool implementations
        tool_implementations = MCPToolImplementations(integration)
        
        # Test 1: Natural language processing with AI engine unavailable
        nl_result = await tool_implementations.natural_language_to_powershell(
            "list processes"
        )
        
        assert nl_result["success"] is False
        assert nl_result["fallback_mode"] is True
        assert "AI engine not available" in nl_result["error"]
        assert "error_handling" in nl_result
        
        # Test 2: Command execution with security engine unavailable
        exec_result = await tool_implementations.execute_powershell_command(
            "Get-Process"
        )
        
        assert exec_result["success"] is False
        assert exec_result["fail_safe_mode"] is True
        assert "Security validation unavailable" in exec_result["blocked_reasons"]
        assert "error_handling" in exec_result
        
        # Test 3: System info with executor unavailable (should still work in degraded mode)
        info_result = await tool_implementations.get_powershell_info()
        
        assert info_result["success"] is True
        assert info_result["degraded_mode"] is True
        assert info_result["powershell"]["status"] == "unavailable"
        assert "error_handling" in info_result
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_config):
        """Test handling of concurrent requests"""
        
        # Create integration with mocked components
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
        
        # Mock AI engine response
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test command",
            alternatives=[]
        )
        integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Mock security validation
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        integration.security_engine.validate_command.return_value = mock_validation
        
        integration._initialized = True
        
        # Create tool implementations
        tool_implementations = MCPToolImplementations(integration)
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = tool_implementations.natural_language_to_powershell(
                f"test command {i}",
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
    
    @pytest.mark.asyncio
    async def test_system_startup_integration(self):
        """Test system startup integration"""
        
        # Mock the integration creation to avoid actual component initialization
        mock_integration = Mock()
        mock_integration.storage = AsyncMock()
        mock_integration.logging_engine = AsyncMock()
        mock_integration.context_manager = AsyncMock()
        mock_integration.ai_engine = AsyncMock()
        mock_integration.security_engine = AsyncMock()
        mock_integration.executor = AsyncMock()
        mock_integration.mcp_server = Mock()
        
        # Mock health checks
        mock_integration.storage.health_check = AsyncMock(return_value={"status": "healthy"})
        mock_integration.logging_engine.health_check = AsyncMock(return_value={"status": "healthy"})
        
        # Mock startup/shutdown functions
        mock_integration.storage.initialize = AsyncMock()
        mock_integration.storage.close = AsyncMock()
        mock_integration.logging_engine.initialize = AsyncMock()
        mock_integration.logging_engine.stop = AsyncMock()
        mock_integration.context_manager.initialize = AsyncMock()
        mock_integration.context_manager.stop = AsyncMock()
        mock_integration.ai_engine.initialize = AsyncMock()
        mock_integration.ai_engine.stop = AsyncMock()
        mock_integration.security_engine.initialize = AsyncMock()
        mock_integration.security_engine.stop = AsyncMock()
        mock_integration.executor.initialize = AsyncMock()
        mock_integration.executor.stop = AsyncMock()
        mock_integration.mcp_server.register_tools = Mock()
        mock_integration.mcp_server.shutdown = Mock()
        mock_integration.shutdown = AsyncMock()
        
        with patch('startup_system.AIPowerShellAssistantIntegration', return_value=mock_integration):
            system = SystemIntegration()
            
            # Mock startup phases to avoid complex initialization
            async def mock_phase():
                pass
            
            for phase in system.startup_phases:
                phase.startup_function = mock_phase
            
            # Test startup
            result = await system.startup()
            
            assert result is True
            assert system.is_running
            
            # Test system status
            status = await system.get_system_status()
            assert "system_state" in status
            assert "startup_time" in status
            assert "components" in status
            
            # Test shutdown
            await system.shutdown()
            assert not system.is_running
            mock_integration.shutdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_performance_characteristics(self, test_config):
        """Test basic performance characteristics"""
        import time
        
        # Create integration with mocked components
        integration = AIPowerShellAssistantIntegration()
        integration.config = test_config
        
        # Mock all components with minimal delay
        integration.storage = AsyncMock()
        integration.logging_engine = AsyncMock()
        integration.context_manager = AsyncMock()
        integration.ai_engine = Mock()
        integration.security_engine = Mock()
        integration.executor = Mock()
        integration.mcp_server = Mock()
        
        # Setup mock return values
        integration.context_manager.create_session.return_value = "test-session"
        integration.context_manager.get_current_context.return_value = Mock()
        integration.logging_engine.log_user_input.return_value = "corr-123"
        
        # Mock fast AI response
        mock_suggestion = CommandSuggestion(
            original_input="test",
            generated_command="Get-Process",
            confidence_score=0.8,
            explanation="Test",
            alternatives=[]
        )
        integration.ai_engine.translate_natural_language.return_value = mock_suggestion
        
        # Mock fast security validation
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        integration.security_engine.validate_command.return_value = mock_validation
        
        integration._initialized = True
        
        # Create tool implementations
        tool_implementations = MCPToolImplementations(integration)
        
        # Measure response time
        start_time = time.time()
        result = await tool_implementations.natural_language_to_powershell("test input")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result["success"] is True
        # Response should be fast with mocked components (under 1 second)
        assert response_time < 1.0
        
        # Test multiple requests for consistency
        response_times = []
        for _ in range(10):
            start_time = time.time()
            await tool_implementations.natural_language_to_powershell("test")
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        # All responses should be consistently fast
        assert all(rt < 1.0 for rt in response_times)
        
        # Average response time should be reasonable
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 0.5  # Average under 500ms


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])