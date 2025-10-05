"""Unit tests for MCP tool schemas and validation"""

import pytest
from datetime import datetime
from typing import Dict, Any

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.schemas import (
    NaturalLanguageToolRequest, ExecuteCommandToolRequest, SystemInfoToolRequest,
    NaturalLanguageToolResponse, ExecuteCommandToolResponse, SystemInfoToolResponse,
    ToolDefinition, ToolRegistry, ToolCategory, ToolStatus, ToolError,
    validate_tool_request, format_tool_response
)
from interfaces.base import OutputFormat


class TestRequestSchemas:
    """Test cases for request schemas"""
    
    def test_natural_language_request_valid(self):
        """Test valid natural language request"""
        request = NaturalLanguageToolRequest(
            input_text="list all processes",
            session_id="test_session",
            context={"key": "value"},
            include_explanation=True,
            include_alternatives=False,
            confidence_threshold=0.8
        )
        
        assert request.input_text == "list all processes"
        assert request.session_id == "test_session"
        assert request.context == {"key": "value"}
        assert request.include_explanation is True
        assert request.include_alternatives is False
        assert request.confidence_threshold == 0.8
    
    def test_natural_language_request_minimal(self):
        """Test minimal natural language request"""
        request = NaturalLanguageToolRequest(input_text="test command")
        
        assert request.input_text == "test command"
        assert request.session_id is None
        assert request.context is None
        assert request.include_explanation is True  # default
        assert request.include_alternatives is True  # default
        assert request.confidence_threshold == 0.5  # default
    
    def test_natural_language_request_validation_errors(self):
        """Test natural language request validation errors"""
        from pydantic import ValidationError
        
        # Empty input text (Pydantic min_length validation)
        with pytest.raises(ValidationError):
            NaturalLanguageToolRequest(input_text="")
        
        # Whitespace only input text (custom validator)
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            NaturalLanguageToolRequest(input_text="   ")
        
        # Invalid confidence threshold
        with pytest.raises(ValidationError):
            NaturalLanguageToolRequest(input_text="test", confidence_threshold=1.5)
        
        with pytest.raises(ValidationError):
            NaturalLanguageToolRequest(input_text="test", confidence_threshold=-0.1)
    
    def test_execute_command_request_valid(self):
        """Test valid execute command request"""
        request = ExecuteCommandToolRequest(
            command="Get-Process",
            session_id="test_session",
            timeout=120,
            use_sandbox=False,
            output_format=OutputFormat.JSON,
            max_output_size=2048000,
            working_directory="/tmp",
            environment_variables={"VAR1": "value1", "VAR2": "value2"}
        )
        
        assert request.command == "Get-Process"
        assert request.session_id == "test_session"
        assert request.timeout == 120
        assert request.use_sandbox is False
        assert request.output_format == OutputFormat.JSON
        assert request.max_output_size == 2048000
        assert request.working_directory == "/tmp"
        assert request.environment_variables == {"VAR1": "value1", "VAR2": "value2"}
    
    def test_execute_command_request_defaults(self):
        """Test execute command request with defaults"""
        request = ExecuteCommandToolRequest(command="Get-Process")
        
        assert request.command == "Get-Process"
        assert request.session_id is None
        assert request.timeout == 60
        assert request.use_sandbox is True
        assert request.output_format == OutputFormat.JSON
        assert request.max_output_size == 1048576  # 1MB
        assert request.working_directory is None
        assert request.environment_variables is None
    
    def test_execute_command_request_validation_errors(self):
        """Test execute command request validation errors"""
        from pydantic import ValidationError
        
        # Empty command (Pydantic min_length validation)
        with pytest.raises(ValidationError):
            ExecuteCommandToolRequest(command="")
        
        # Invalid timeout
        with pytest.raises(ValidationError):
            ExecuteCommandToolRequest(command="test", timeout=0)
        
        with pytest.raises(ValidationError):
            ExecuteCommandToolRequest(command="test", timeout=4000)
        
        # Invalid max_output_size
        with pytest.raises(ValidationError):
            ExecuteCommandToolRequest(command="test", max_output_size=500)
        
        # Invalid environment variables (Pydantic type validation)
        with pytest.raises(ValidationError):
            ExecuteCommandToolRequest(
                command="test", 
                environment_variables={"key": 123}
            )
    
    def test_system_info_request_valid(self):
        """Test valid system info request"""
        request = SystemInfoToolRequest(
            session_id="test_session",
            include_modules=False,
            include_environment=True,
            include_performance=True,
            include_security=False,
            module_filter="Microsoft.*",
            detailed_info=True
        )
        
        assert request.session_id == "test_session"
        assert request.include_modules is False
        assert request.include_environment is True
        assert request.include_performance is True
        assert request.include_security is False
        assert request.module_filter == "Microsoft.*"
        assert request.detailed_info is True
    
    def test_system_info_request_defaults(self):
        """Test system info request with defaults"""
        request = SystemInfoToolRequest()
        
        assert request.session_id is None
        assert request.include_modules is True
        assert request.include_environment is False
        assert request.include_performance is False
        assert request.include_security is False
        assert request.module_filter is None
        assert request.detailed_info is False


class TestResponseSchemas:
    """Test cases for response schemas"""
    
    def test_natural_language_response_success(self):
        """Test successful natural language response"""
        response = NaturalLanguageToolResponse(
            success=True,
            original_input="list processes",
            generated_command="Get-Process",
            confidence_score=0.95,
            explanation="Lists all running processes",
            alternatives=["ps", "Get-Process | Select-Object Name, Id"],
            session_id="test_session",
            correlation_id="corr_123",
            processing_time_ms=250.5,
            warnings=["High CPU usage detected"]
        )
        
        assert response.success is True
        assert response.original_input == "list processes"
        assert response.generated_command == "Get-Process"
        assert response.confidence_score == 0.95
        assert response.explanation == "Lists all running processes"
        assert len(response.alternatives) == 2
        assert response.session_id == "test_session"
        assert response.correlation_id == "corr_123"
        assert response.processing_time_ms == 250.5
        assert response.error is None
        assert len(response.warnings) == 1
    
    def test_natural_language_response_error(self):
        """Test error natural language response"""
        error = ToolError(
            error_code="AI_ENGINE_ERROR",
            error_message="AI engine not available",
            timestamp="2024-01-01T00:00:00Z",
            recoverable=True,
            suggested_actions=["Check AI engine status", "Restart service"]
        )
        
        response = NaturalLanguageToolResponse(
            success=False,
            error=error,
            correlation_id="corr_123"
        )
        
        assert response.success is False
        assert response.error.error_code == "AI_ENGINE_ERROR"
        assert response.error.recoverable is True
        assert len(response.error.suggested_actions) == 2
    
    def test_execute_command_response_success(self):
        """Test successful execute command response"""
        response = ExecuteCommandToolResponse(
            success=True,
            return_code=0,
            stdout="Process output here",
            stderr="",
            execution_time=1.5,
            platform="Windows",
            sandbox_used=True,
            output_format="JSON",
            output_truncated=False,
            session_id="test_session",
            correlation_id="corr_123",
            security_validation={"passed": True, "risk_level": "low"},
            performance_metrics={"cpu_usage": 15.2, "memory_mb": 128}
        )
        
        assert response.success is True
        assert response.return_code == 0
        assert response.stdout == "Process output here"
        assert response.execution_time == 1.5
        assert response.platform == "Windows"
        assert response.sandbox_used is True
        assert response.output_truncated is False
        assert response.security_validation["passed"] is True
        assert response.performance_metrics["cpu_usage"] == 15.2
    
    def test_system_info_response_success(self):
        """Test successful system info response"""
        response = SystemInfoToolResponse(
            success=True,
            powershell={"version": "7.3.0", "edition": "Core"},
            platform="Windows",
            server_version="1.0.0",
            modules=[{"name": "Microsoft.PowerShell.Management", "version": "7.3.0"}],
            environment={"PSModulePath": "/modules"},
            performance={"cpu_usage": 10.5, "memory_mb": 256},
            security={"sandbox_enabled": True, "whitelist_active": True},
            session_id="test_session",
            correlation_id="corr_123",
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert response.success is True
        assert response.powershell["version"] == "7.3.0"
        assert response.platform == "Windows"
        assert response.server_version == "1.0.0"
        assert len(response.modules) == 1
        assert response.environment["PSModulePath"] == "/modules"
        assert response.performance["cpu_usage"] == 10.5
        assert response.security["sandbox_enabled"] is True


class TestToolDefinition:
    """Test cases for tool definitions"""
    
    def test_tool_definition_valid(self):
        """Test valid tool definition"""
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
            version="1.0.0",
            status=ToolStatus.AVAILABLE,
            request_schema={"type": "object"},
            response_schema={"type": "object"},
            parameters={"param1": "value1"},
            examples=[{"example": "data"}],
            requirements=["requirement1"],
            permissions=["permission1"],
            rate_limit={"requests_per_minute": 60}
        )
        
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.category == ToolCategory.UTILITY
        assert tool.version == "1.0.0"
        assert tool.status == ToolStatus.AVAILABLE
        assert tool.parameters["param1"] == "value1"
        assert len(tool.examples) == 1
        assert len(tool.requirements) == 1
        assert len(tool.permissions) == 1
        assert tool.rate_limit["requests_per_minute"] == 60
    
    def test_tool_definition_validation_errors(self):
        """Test tool definition validation errors"""
        # Empty name
        with pytest.raises(ValueError, match="Tool name cannot be empty"):
            ToolDefinition(
                name="",
                description="Test",
                category=ToolCategory.UTILITY,
                request_schema={},
                response_schema={}
            )
        
        # Invalid name characters
        with pytest.raises(ValueError, match="Tool name must contain only"):
            ToolDefinition(
                name="test@tool",
                description="Test",
                category=ToolCategory.UTILITY,
                request_schema={},
                response_schema={}
            )


class TestToolRegistry:
    """Test cases for tool registry"""
    
    def test_tool_registry_operations(self):
        """Test tool registry add/remove operations"""
        registry = ToolRegistry(last_updated="2024-01-01T00:00:00Z")
        
        # Create test tool
        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
            request_schema={},
            response_schema={}
        )
        
        # Add tool
        registry.add_tool(tool)
        assert "test_tool" in registry.tools
        assert ToolCategory.UTILITY.value in registry.categories
        assert "test_tool" in registry.categories[ToolCategory.UTILITY.value]
        
        # Get tools by category
        utility_tools = registry.get_tools_by_category(ToolCategory.UTILITY)
        assert len(utility_tools) == 1
        assert utility_tools[0].name == "test_tool"
        
        # Get available tools
        available_tools = registry.get_available_tools()
        assert len(available_tools) == 1
        
        # Remove tool
        removed = registry.remove_tool("test_tool")
        assert removed is True
        assert "test_tool" not in registry.tools
        assert ToolCategory.UTILITY.value not in registry.categories
        
        # Try to remove non-existent tool
        removed = registry.remove_tool("non_existent")
        assert removed is False


class TestValidationFunctions:
    """Test cases for validation functions"""
    
    def test_validate_tool_request_success(self):
        """Test successful tool request validation"""
        # Natural language tool
        request_data = {
            "input_text": "test command",
            "session_id": "test_session"
        }
        result = validate_tool_request("natural_language_to_powershell", request_data)
        assert isinstance(result, NaturalLanguageToolRequest)
        assert result.input_text == "test command"
        
        # Execute command tool
        request_data = {
            "command": "Get-Process",
            "timeout": 30
        }
        result = validate_tool_request("execute_powershell_command", request_data)
        assert isinstance(result, ExecuteCommandToolRequest)
        assert result.command == "Get-Process"
        assert result.timeout == 30
        
        # System info tool
        request_data = {
            "include_modules": True,
            "include_environment": False
        }
        result = validate_tool_request("get_powershell_info", request_data)
        assert isinstance(result, SystemInfoToolRequest)
        assert result.include_modules is True
        assert result.include_environment is False
    
    def test_validate_tool_request_unknown_tool(self):
        """Test validation with unknown tool"""
        result = validate_tool_request("unknown_tool", {})
        assert isinstance(result, ToolError)
        assert result.error_code == "UNKNOWN_TOOL"
        assert "Unknown tool: unknown_tool" in result.error_message
    
    def test_validate_tool_request_validation_error(self):
        """Test validation with invalid request data"""
        # Invalid natural language request
        request_data = {
            "input_text": "",  # Empty input
            "confidence_threshold": 1.5  # Invalid threshold
        }
        result = validate_tool_request("natural_language_to_powershell", request_data)
        assert isinstance(result, ToolError)
        assert result.error_code == "VALIDATION_ERROR"
        assert result.recoverable is True
    
    def test_format_tool_response_success(self):
        """Test successful tool response formatting"""
        # Natural language response
        response_data = {
            "success": True,
            "generated_command": "Get-Process",
            "confidence_score": 0.95
        }
        result = format_tool_response("natural_language_to_powershell", response_data)
        assert isinstance(result, NaturalLanguageToolResponse)
        assert result.success is True
        assert result.generated_command == "Get-Process"
        
        # Execute command response
        response_data = {
            "success": True,
            "return_code": 0,
            "stdout": "output"
        }
        result = format_tool_response("execute_powershell_command", response_data)
        assert isinstance(result, ExecuteCommandToolResponse)
        assert result.success is True
        assert result.return_code == 0
        
        # System info response
        response_data = {
            "success": True,
            "platform": "Windows"
        }
        result = format_tool_response("get_powershell_info", response_data)
        assert isinstance(result, SystemInfoToolResponse)
        assert result.success is True
        assert result.platform == "Windows"
    
    def test_format_tool_response_unknown_tool(self):
        """Test response formatting with unknown tool"""
        result = format_tool_response("unknown_tool", {})
        assert isinstance(result, ToolError)
        assert result.error_code == "UNKNOWN_TOOL"


if __name__ == "__main__":
    pytest.main([__file__])