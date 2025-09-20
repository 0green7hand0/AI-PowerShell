"""MCP Tool Schemas and Validation

This module defines the schemas for MCP tools, parameter validation,
response formatting, and tool discovery mechanisms.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Platform, OutputFormat, LogLevel


class ToolCategory(Enum):
    """Categories for MCP tools"""
    NATURAL_LANGUAGE = "natural_language"
    COMMAND_EXECUTION = "command_execution"
    SYSTEM_INFO = "system_info"
    UTILITY = "utility"


class ToolStatus(Enum):
    """Status of MCP tools"""
    AVAILABLE = "available"
    DISABLED = "disabled"
    ERROR = "error"
    MAINTENANCE = "maintenance"


# Request Schemas
class NaturalLanguageToolRequest(BaseModel):
    """Schema for natural language processing tool requests"""
    input_text: str = Field(
        ..., 
        min_length=1,
        max_length=10000,
        description="Natural language input to convert to PowerShell commands"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Session identifier for context tracking"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context information"
    )
    include_explanation: bool = Field(
        True, 
        description="Whether to include explanation of the generated command"
    )
    include_alternatives: bool = Field(
        True, 
        description="Whether to include alternative command suggestions"
    )
    confidence_threshold: float = Field(
        0.5, 
        ge=0.0, 
        le=1.0,
        description="Minimum confidence score for command suggestions"
    )
    
    @field_validator('input_text')
    @classmethod
    def validate_input_text(cls, v):
        """Validate input text"""
        if not v.strip():
            raise ValueError('Input text cannot be empty or whitespace only')
        return v.strip()


class ExecuteCommandToolRequest(BaseModel):
    """Schema for PowerShell command execution tool requests"""
    command: str = Field(
        ..., 
        min_length=1,
        max_length=50000,
        description="PowerShell command to execute"
    )
    session_id: Optional[str] = Field(
        None, 
        description="Session identifier for context tracking"
    )
    timeout: int = Field(
        60, 
        ge=1, 
        le=3600,
        description="Execution timeout in seconds (1-3600)"
    )
    use_sandbox: bool = Field(
        True, 
        description="Whether to execute in sandbox environment"
    )
    output_format: OutputFormat = Field(
        OutputFormat.JSON, 
        description="Desired output format"
    )
    max_output_size: int = Field(
        1048576,  # 1MB
        ge=1024,
        le=10485760,  # 10MB
        description="Maximum output size in bytes"
    )
    working_directory: Optional[str] = Field(
        None, 
        description="Working directory for command execution"
    )
    environment_variables: Optional[Dict[str, str]] = Field(
        None, 
        description="Additional environment variables"
    )
    
    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        """Validate PowerShell command"""
        if not v.strip():
            raise ValueError('Command cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('environment_variables')
    @classmethod
    def validate_environment_variables(cls, v):
        """Validate environment variables"""
        if v is not None:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError('Environment variables must be string key-value pairs')
                if not key.strip():
                    raise ValueError('Environment variable names cannot be empty')
        return v


class SystemInfoToolRequest(BaseModel):
    """Schema for system information tool requests"""
    session_id: Optional[str] = Field(
        None, 
        description="Session identifier for context tracking"
    )
    include_modules: bool = Field(
        True, 
        description="Include PowerShell module information"
    )
    include_environment: bool = Field(
        False, 
        description="Include environment variables"
    )
    include_performance: bool = Field(
        False, 
        description="Include performance metrics"
    )
    include_security: bool = Field(
        False, 
        description="Include security configuration"
    )
    module_filter: Optional[str] = Field(
        None, 
        description="Filter modules by name pattern"
    )
    detailed_info: bool = Field(
        False, 
        description="Include detailed system information"
    )


# Response Schemas
class ToolError(BaseModel):
    """Schema for tool error responses"""
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: str = Field(..., description="Error timestamp")
    recoverable: bool = Field(False, description="Whether the error is recoverable")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested recovery actions")


class NaturalLanguageToolResponse(BaseModel):
    """Schema for natural language processing tool responses"""
    success: bool = Field(..., description="Whether the request was successful")
    original_input: Optional[str] = Field(None, description="Original natural language input")
    generated_command: Optional[str] = Field(None, description="Generated PowerShell command")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    explanation: Optional[str] = Field(None, description="Explanation of the generated command")
    alternatives: List[str] = Field(default_factory=list, description="Alternative command suggestions")
    session_id: Optional[str] = Field(None, description="Session identifier")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    error: Optional[ToolError] = Field(None, description="Error information if unsuccessful")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")


class ExecuteCommandToolResponse(BaseModel):
    """Schema for command execution tool responses"""
    success: bool = Field(..., description="Whether the command executed successfully")
    return_code: Optional[int] = Field(None, description="Command return code")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    platform: Optional[str] = Field(None, description="Execution platform")
    sandbox_used: Optional[bool] = Field(None, description="Whether sandbox was used")
    output_format: Optional[str] = Field(None, description="Output format used")
    output_truncated: bool = Field(False, description="Whether output was truncated")
    session_id: Optional[str] = Field(None, description="Session identifier")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    security_validation: Optional[Dict[str, Any]] = Field(None, description="Security validation results")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    error: Optional[ToolError] = Field(None, description="Error information if unsuccessful")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")


class SystemInfoToolResponse(BaseModel):
    """Schema for system information tool responses"""
    success: bool = Field(..., description="Whether the request was successful")
    powershell: Optional[Dict[str, Any]] = Field(None, description="PowerShell information")
    platform: Optional[str] = Field(None, description="Platform information")
    server_version: Optional[str] = Field(None, description="Server version")
    modules: Optional[List[Dict[str, Any]]] = Field(None, description="PowerShell modules")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    performance: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    security: Optional[Dict[str, Any]] = Field(None, description="Security configuration")
    session_id: Optional[str] = Field(None, description="Session identifier")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: Optional[str] = Field(None, description="Response timestamp")
    error: Optional[ToolError] = Field(None, description="Error information if unsuccessful")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")


# Tool Definition Schema
class ToolDefinition(BaseModel):
    """Schema for MCP tool definitions"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    version: str = Field("1.0.0", description="Tool version")
    status: ToolStatus = Field(ToolStatus.AVAILABLE, description="Tool status")
    request_schema: Dict[str, Any] = Field(..., description="Request schema definition")
    response_schema: Dict[str, Any] = Field(..., description="Response schema definition")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    requirements: List[str] = Field(default_factory=list, description="Tool requirements")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    rate_limit: Optional[Dict[str, Any]] = Field(None, description="Rate limiting configuration")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate tool name"""
        if not v.strip():
            raise ValueError('Tool name cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Tool name must contain only alphanumeric characters, hyphens, and underscores')
        return v.strip()


# Tool Registry Schema
class ToolRegistry(BaseModel):
    """Schema for tool registry"""
    tools: Dict[str, ToolDefinition] = Field(default_factory=dict, description="Registered tools")
    categories: Dict[str, List[str]] = Field(default_factory=dict, description="Tools by category")
    version: str = Field("1.0.0", description="Registry version")
    last_updated: str = Field(..., description="Last update timestamp")
    
    def add_tool(self, tool: ToolDefinition) -> None:
        """Add a tool to the registry"""
        self.tools[tool.name] = tool
        
        # Update category index
        category_name = tool.category.value
        if category_name not in self.categories:
            self.categories[category_name] = []
        
        if tool.name not in self.categories[category_name]:
            self.categories[category_name].append(tool.name)
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool from the registry"""
        if tool_name not in self.tools:
            return False
        
        tool = self.tools[tool_name]
        category_name = tool.category.value
        
        # Remove from tools
        del self.tools[tool_name]
        
        # Remove from category index
        if category_name in self.categories and tool_name in self.categories[category_name]:
            self.categories[category_name].remove(tool_name)
            
            # Clean up empty categories
            if not self.categories[category_name]:
                del self.categories[category_name]
        
        return True
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a specific category"""
        category_name = category.value
        if category_name not in self.categories:
            return []
        
        return [self.tools[tool_name] for tool_name in self.categories[category_name]]
    
    def get_available_tools(self) -> List[ToolDefinition]:
        """Get all available tools"""
        return [tool for tool in self.tools.values() if tool.status == ToolStatus.AVAILABLE]


# Validation Functions
def validate_tool_request(tool_name: str, request_data: Dict[str, Any]) -> Union[BaseModel, ToolError]:
    """Validate a tool request against its schema"""
    try:
        if tool_name == "natural_language_to_powershell":
            return NaturalLanguageToolRequest(**request_data)
        elif tool_name == "execute_powershell_command":
            return ExecuteCommandToolRequest(**request_data)
        elif tool_name == "get_powershell_info":
            return SystemInfoToolRequest(**request_data)
        else:
            return ToolError(
                error_code="UNKNOWN_TOOL",
                error_message=f"Unknown tool: {tool_name}",
                timestamp=str(datetime.now()),
                recoverable=False
            )
    except Exception as e:
        return ToolError(
            error_code="VALIDATION_ERROR",
            error_message=f"Request validation failed: {str(e)}",
            error_details={"validation_errors": str(e)},
            timestamp=str(datetime.now()),
            recoverable=True,
            suggested_actions=["Check request parameters", "Refer to tool documentation"]
        )


def format_tool_response(tool_name: str, response_data: Dict[str, Any]) -> BaseModel:
    """Format a tool response according to its schema"""
    if tool_name == "natural_language_to_powershell":
        return NaturalLanguageToolResponse(**response_data)
    elif tool_name == "execute_powershell_command":
        return ExecuteCommandToolResponse(**response_data)
    elif tool_name == "get_powershell_info":
        return SystemInfoToolResponse(**response_data)
    else:
        # Return generic error response
        return ToolError(
            error_code="UNKNOWN_TOOL",
            error_message=f"Unknown tool for response formatting: {tool_name}",
            timestamp=str(datetime.now()),
            recoverable=False
        )


# Import datetime for validation functions
from datetime import datetime