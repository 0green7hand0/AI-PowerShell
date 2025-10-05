"""Unit tests for PowerShellAssistantMCP server core"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, Any

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.server import PowerShellAssistantMCP, NaturalLanguageRequest, ExecuteCommandRequest, SystemInfoRequest
from config.models import ServerConfig, MCPServerConfig
from interfaces.base import (
    CommandSuggestion, ExecutionResult, ValidationResult, CommandContext,
    Platform, UserRole, RiskLevel, SecurityAction
)


class TestPowerShellAssistantMCP:
    """Test cases for PowerShellAssistantMCP class"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        config = ServerConfig()
        config.mcp_server = MCPServerConfig(
            enable_natural_language_tool=True,
            enable_execute_command_tool=True,
            enable_system_info_tool=True
        )
        return config
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components"""
        return {
            'ai_engine': Mock(),
            'security_engine': Mock(),
            'executor': Mock(),
            'context_manager': Mock(),
            'logging_engine': Mock()
        }
    
    @pytest.fixture
    def server(self, config, mock_components):
        """Create server instance with mocked components"""
        server = PowerShellAssistantMCP(config)
        server.set_components(**mock_components)
        return server
    
    def test_initialization(self, config):
        """Test server initialization"""
        server = PowerShellAssistantMCP(config)
        
        assert server.config == config
        assert server.app is None
        assert not server._running
        assert server.active_sessions == {}
    
    def test_set_components(self, config, mock_components):
        """Test component dependency injection"""
        server = PowerShellAssistantMCP(config)
        server.set_components(**mock_components)
        
        assert server.ai_engine == mock_components['ai_engine']
        assert server.security_engine == mock_components['security_engine']
        assert server.executor == mock_components['executor']
        assert server.context_manager == mock_components['context_manager']
        assert server.logging_engine == mock_components['logging_engine']
    
    def test_register_tools(self, server):
        """Test MCP tool registration"""
        server.register_tools()
        
        assert server.app is not None
        assert server.app.name == "AI PowerShell Assistant"
    
    @pytest.mark.asyncio
    async def test_handle_natural_language_request_success(self, server, mock_components):
        """Test successful natural language processing"""
        # Setup mocks
        mock_components['context_manager'].create_session.return_value = "test_session"
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        mock_components['context_manager'].get_current_context.return_value = CommandContext(
            current_directory="/test",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.WINDOWS
        )
        
        mock_suggestion = CommandSuggestion(
            original_input="list processes",
            generated_command="Get-Process",
            confidence_score=0.95,
            explanation="Lists all running processes",
            alternatives=["ps"]
        )
        mock_components['ai_engine'].translate_natural_language.return_value = mock_suggestion
        
        # Execute
        result = await server._handle_natural_language_request(
            "list processes", None, {}
        )
        
        # Verify
        assert result["success"] is True
        assert result["generated_command"] == "Get-Process"
        assert result["confidence_score"] == 0.95
        assert "session_id" in result
        assert "correlation_id" in result
        
        # Verify mock calls
        mock_components['context_manager'].create_session.assert_called_once()
        mock_components['logging_engine'].log_user_input.assert_called_once()
        mock_components['ai_engine'].translate_natural_language.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_natural_language_request_no_ai_engine(self, server):
        """Test natural language processing without AI engine"""
        server.ai_engine = None
        
        result = await server._handle_natural_language_request(
            "list processes", "test_session", {}
        )
        
        assert result["success"] is False
        assert "AI engine not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_execute_command_success(self, server, mock_components):
        """Test successful command execution"""
        # Setup mocks
        mock_components['context_manager'].create_session.return_value = "test_session"
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        mock_components['security_engine'].validate_command.return_value = mock_validation
        
        mock_context = CommandContext(
            current_directory="/test",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.WINDOWS
        )
        mock_components['context_manager'].get_current_context.return_value = mock_context
        
        mock_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Process output",
            stderr="",
            execution_time=1.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        mock_components['executor'].execute_command.return_value = mock_result
        
        # Execute
        result = await server._handle_execute_command(
            "Get-Process", None, 60, False
        )
        
        # Verify
        assert result["success"] is True
        assert result["return_code"] == 0
        assert result["stdout"] == "Process output"
        assert result["execution_time"] == 1.5
        
        # Verify mock calls
        mock_components['security_engine'].validate_command.assert_called_once_with("Get-Process")
        mock_components['executor'].execute_command.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_execute_command_blocked_by_security(self, server, mock_components):
        """Test command execution blocked by security"""
        # Setup mocks
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        
        mock_validation = ValidationResult(
            is_valid=False,
            blocked_reasons=["Dangerous command detected"],
            required_permissions=[],
            suggested_alternatives=["Get-Process -Name safe"],
            risk_assessment=RiskLevel.HIGH
        )
        mock_components['security_engine'].validate_command.return_value = mock_validation
        
        # Execute
        result = await server._handle_execute_command(
            "Remove-Item -Recurse C:\\", "test_session", 60, True
        )
        
        # Verify
        assert result["success"] is False
        assert "Command blocked by security policy" in result["error"]
        assert result["blocked_reasons"] == ["Dangerous command detected"]
        assert result["suggested_alternatives"] == ["Get-Process -Name safe"]
        
        # Verify executor was not called
        mock_components['executor'].execute_command.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_execute_command_with_sandbox(self, server, mock_components):
        """Test command execution in sandbox"""
        # Setup mocks
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        
        mock_validation = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        mock_components['security_engine'].validate_command.return_value = mock_validation
        
        mock_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Sandbox output",
            stderr="",
            execution_time=2.0,
            platform=Platform.LINUX,
            sandbox_used=True
        )
        mock_components['security_engine'].execute_in_sandbox.return_value = mock_result
        
        # Execute
        result = await server._handle_execute_command(
            "Get-Process", "test_session", 60, True
        )
        
        # Verify
        assert result["success"] is True
        assert result["sandbox_used"] is True
        assert result["stdout"] == "Sandbox output"
        
        # Verify sandbox execution was called
        mock_components['security_engine'].execute_in_sandbox.assert_called_once_with("Get-Process", 60)
    
    @pytest.mark.asyncio
    async def test_handle_get_system_info_success(self, server, mock_components):
        """Test successful system info retrieval"""
        # Setup mocks
        mock_components['context_manager'].create_session.return_value = "test_session"
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        
        mock_ps_info = {
            "version": "7.3.0",
            "edition": "Core",
            "platform": "Windows",
            "modules": ["Microsoft.PowerShell.Management"],
            "environment": {"PSModulePath": "/modules"}
        }
        mock_components['executor'].get_powershell_info.return_value = mock_ps_info
        
        # Execute
        result = await server._handle_get_system_info(
            None, True, True
        )
        
        # Verify
        assert result["success"] is True
        assert result["powershell"] == mock_ps_info
        assert result["platform"] == server.config.platform.value
        assert result["server_version"] == server.config.version
        assert "session_id" in result
        assert "correlation_id" in result
        
        # Verify mock calls
        mock_components['executor'].get_powershell_info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_get_system_info_no_executor(self, server):
        """Test system info retrieval without executor"""
        server.executor = None
        
        result = await server._handle_get_system_info(
            "test_session", True, False
        )
        
        assert result["success"] is False
        assert "Execution engine not available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_error_handling_with_logging(self, server, mock_components):
        """Test error handling and logging"""
        # Setup mocks to raise exception
        mock_components['logging_engine'].log_user_input.return_value = "corr_123"
        mock_components['ai_engine'].translate_natural_language.side_effect = Exception("Test error")
        
        # Execute
        result = await server._handle_natural_language_request(
            "test input", "test_session", {}
        )
        
        # Verify
        assert result["success"] is False
        assert "Test error" in result["error"]
        assert result["correlation_id"] == "corr_123"
        
        # Verify error was logged
        mock_components['logging_engine'].log_error.assert_called_once()
    
    def test_shutdown(self, server, mock_components):
        """Test server shutdown"""
        # Add some active sessions
        server.active_sessions["session1"] = Mock()
        server.active_sessions["session2"] = Mock()
        server._running = True
        
        # Execute shutdown
        server.shutdown()
        
        # Verify
        assert not server._running
        assert len(server.active_sessions) == 0
        
        # Verify sessions were ended
        assert mock_components['context_manager'].end_session.call_count == 2
    
    def test_synchronous_wrappers(self, server, mock_components):
        """Test synchronous wrapper methods"""
        # Mock the async methods
        server._handle_natural_language_request = AsyncMock(return_value={"success": True})
        server._handle_execute_command = AsyncMock(return_value={"success": True})
        server._handle_get_system_info = AsyncMock(return_value={"success": True})
        
        # Test wrappers
        result1 = server.handle_natural_language_request("test", "session")
        result2 = server.handle_execute_command("Get-Process", "session")
        result3 = server.handle_get_system_info("session")
        
        # Verify
        assert result1["success"] is True
        assert result2["success"] is True
        assert result3["success"] is True
    
    def test_properties(self, server):
        """Test server properties"""
        # Test is_running
        assert not server.is_running
        server._running = True
        assert server.is_running
        
        # Test get_active_sessions
        server.active_sessions["session1"] = Mock()
        server.active_sessions["session2"] = Mock()
        
        sessions = server.get_active_sessions()
        assert len(sessions) == 2
        assert "session1" in sessions
        assert "session2" in sessions


class TestRequestModels:
    """Test cases for Pydantic request models"""
    
    def test_natural_language_request(self):
        """Test NaturalLanguageRequest model"""
        request = NaturalLanguageRequest(
            input_text="list processes",
            session_id="test_session",
            context={"key": "value"}
        )
        
        assert request.input_text == "list processes"
        assert request.session_id == "test_session"
        assert request.context == {"key": "value"}
    
    def test_natural_language_request_minimal(self):
        """Test NaturalLanguageRequest with minimal data"""
        request = NaturalLanguageRequest(input_text="test")
        
        assert request.input_text == "test"
        assert request.session_id is None
        assert request.context is None
    
    def test_execute_command_request(self):
        """Test ExecuteCommandRequest model"""
        request = ExecuteCommandRequest(
            command="Get-Process",
            session_id="test_session",
            timeout=120,
            use_sandbox=False
        )
        
        assert request.command == "Get-Process"
        assert request.session_id == "test_session"
        assert request.timeout == 120
        assert request.use_sandbox is False
    
    def test_execute_command_request_defaults(self):
        """Test ExecuteCommandRequest with default values"""
        request = ExecuteCommandRequest(command="Get-Process")
        
        assert request.command == "Get-Process"
        assert request.session_id is None
        assert request.timeout == 60
        assert request.use_sandbox is True
    
    def test_system_info_request(self):
        """Test SystemInfoRequest model"""
        request = SystemInfoRequest(
            session_id="test_session",
            include_modules=False,
            include_environment=True
        )
        
        assert request.session_id == "test_session"
        assert request.include_modules is False
        assert request.include_environment is True
    
    def test_system_info_request_defaults(self):
        """Test SystemInfoRequest with default values"""
        request = SystemInfoRequest()
        
        assert request.session_id is None
        assert request.include_modules is True
        assert request.include_environment is False


if __name__ == "__main__":
    pytest.main([__file__])