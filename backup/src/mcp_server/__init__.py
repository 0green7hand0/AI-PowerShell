"""MCP Server Core Module

This module provides the FastMCP server implementation for tool registration
and MCP protocol communication.

Interfaces to implement:
- MCPServerInterface: Main MCP server interface
"""

from .server import PowerShellAssistantMCP
from .schemas import (
    NaturalLanguageToolRequest, ExecuteCommandToolRequest, SystemInfoToolRequest,
    NaturalLanguageToolResponse, ExecuteCommandToolResponse, SystemInfoToolResponse,
    ToolDefinition, ToolRegistry, ToolCategory, ToolStatus
)
from .discovery import ToolDiscoveryManager

__all__ = [
    "PowerShellAssistantMCP",
    "NaturalLanguageToolRequest", 
    "ExecuteCommandToolRequest",
    "SystemInfoToolRequest",
    "NaturalLanguageToolResponse",
    "ExecuteCommandToolResponse", 
    "SystemInfoToolResponse",
    "ToolDefinition",
    "ToolRegistry",
    "ToolCategory",
    "ToolStatus",
    "ToolDiscoveryManager"
]