"""Simple Integration Tests for MCP Tools

This module provides basic integration tests to verify MCP tool functionality.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import (
    Platform, UserRole, LogLevel, OutputFormat, RiskLevel, SecurityAction, Permission,
    CommandSuggestion, ValidationResult, ExecutionResult
)


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
            powershell_executable="pwsh",
            default_timeout=60,
            max_output_size=1048576
        ),
        storage=StorageConfig(
            data_directory=str(Path(temp_dir) / "storage"),
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
def mock_integration(test_config):
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
def tool_implementations(mock_integration):
    """Create tool implementations with mock integration"""
    return MCPToolImplementations(mock_integration)


@pytest.mark.asyncio
async def test_natural_language_empty_input(tool_implementations):
    """Test validation of empty input"""
    result = await tool_implementations.natural_language_to_powershell("")
    
    assert result["success"] is False
    assert result["error"] == "Input text cannot be empty"
    assert result["error_code"] == "INVALID_INPUT"


@pytest.mark.asyncio
async def test_natural_language_successful_translation(tool_implementations, mock_integration):
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


@pytest.mark.asyncio
async def test_execute_command_empty_input(tool_implementations):
    """Test validation of empty command"""
    result = await tool_implementations.execute_powershell_command("")
    
    assert result["success"] is False
    assert result["error"] == "Command cannot be empty"
    assert result["error_code"] == "INVALID_COMMAND"


@pytest.mark.asyncio
async def test_execute_command_successful(tool_implementations, mock_integration):
    """Test successful command execution"""
    # Setup mocks
    mock_validation = ValidationResult(
        is_valid=True,
        blocked_reasons=[],
        required_permissions=[],
        suggested_alternatives=[],
        risk_assessment=RiskLevel.LOW
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


@pytest.mark.asyncio
async def test_get_system_info_basic(tool_implementations, mock_integration):
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


@pytest.mark.asyncio
async def test_ai_engine_unavailable(tool_implementations, mock_integration):
    """Test handling when AI engine is unavailable"""
    mock_integration.ai_engine = None
    
    result = await tool_implementations.natural_language_to_powershell("test input")
    
    assert result["success"] is False
    assert result["error"] == "AI engine not available"
    assert result["error_code"] == "AI_ENGINE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_security_engine_unavailable(tool_implementations, mock_integration):
    """Test handling when security engine is unavailable"""
    mock_integration.security_engine = None
    
    result = await tool_implementations.execute_powershell_command("Get-Process")
    
    assert result["success"] is False
    assert result["error"] == "Security engine not available"
    assert result["error_code"] == "SECURITY_ENGINE_UNAVAILABLE"


@pytest.mark.asyncio
async def test_executor_unavailable(tool_implementations, mock_integration):
    """Test handling when executor is unavailable"""
    mock_integration.executor = None
    
    result = await tool_implementations.get_powershell_info()
    
    assert result["success"] is False
    assert result["error"] == "Execution engine not available"
    assert result["error_code"] == "EXECUTOR_UNAVAILABLE"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])