"""MCP Tool Discovery and Registration

This module provides mechanisms for tool discovery, registration,
and management within the MCP server framework.
"""

import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timezone
from pathlib import Path
import json

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.schemas import (
    ToolDefinition, ToolRegistry, ToolCategory, ToolStatus,
    NaturalLanguageToolRequest, ExecuteCommandToolRequest, SystemInfoToolRequest,
    NaturalLanguageToolResponse, ExecuteCommandToolResponse, SystemInfoToolResponse,
    validate_tool_request, format_tool_response
)


class ToolDiscoveryManager:
    """Manages tool discovery, registration, and lifecycle"""
    
    def __init__(self, registry_path: Optional[str] = None):
        """Initialize the tool discovery manager
        
        Args:
            registry_path: Path to store the tool registry file
        """
        self.logger = logging.getLogger(__name__)
        self.registry_path = registry_path or "tool_registry.json"
        self.registry = ToolRegistry(last_updated=datetime.now(timezone.utc).isoformat())
        self.tool_handlers: Dict[str, Callable] = {}
        
        # Load existing registry if available
        self._load_registry()
        
        # Register built-in tools
        self._register_builtin_tools()
        
        self.logger.info("ToolDiscoveryManager initialized")
    
    def _load_registry(self) -> None:
        """Load tool registry from file"""
        try:
            registry_file = Path(self.registry_path)
            if registry_file.exists():
                with open(registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)
                    self.registry = ToolRegistry(**registry_data)
                self.logger.info(f"Loaded tool registry from {self.registry_path}")
            else:
                self.logger.info("No existing registry found, starting with empty registry")
        except Exception as e:
            self.logger.error(f"Failed to load tool registry: {e}")
            # Continue with empty registry
    
    def _save_registry(self) -> None:
        """Save tool registry to file"""
        try:
            self.registry.last_updated = datetime.now(timezone.utc).isoformat()
            registry_file = Path(self.registry_path)
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(registry_file, 'w', encoding='utf-8') as f:
                # Use mode='json' to properly serialize enums
                registry_data = self.registry.model_dump(mode='json')
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved tool registry to {self.registry_path}")
        except Exception as e:
            self.logger.error(f"Failed to save tool registry: {e}")
    
    def _register_builtin_tools(self) -> None:
        """Register built-in MCP tools"""
        
        # Natural Language to PowerShell Tool
        nl_tool = ToolDefinition(
            name="natural_language_to_powershell",
            description="Convert natural language descriptions to PowerShell commands using local AI models",
            category=ToolCategory.NATURAL_LANGUAGE,
            version="1.0.0",
            status=ToolStatus.AVAILABLE,
            request_schema=NaturalLanguageToolRequest.model_json_schema(),
            response_schema=NaturalLanguageToolResponse.model_json_schema(),
            parameters={
                "max_input_length": 10000,
                "min_confidence_threshold": 0.1,
                "max_alternatives": 5
            },
            examples=[
                {
                    "description": "List running processes",
                    "request": {
                        "input_text": "show me all running processes",
                        "include_explanation": True
                    },
                    "expected_response": {
                        "generated_command": "Get-Process",
                        "explanation": "Lists all currently running processes"
                    }
                },
                {
                    "description": "Find files by extension",
                    "request": {
                        "input_text": "find all .txt files in current directory",
                        "include_alternatives": True
                    },
                    "expected_response": {
                        "generated_command": "Get-ChildItem -Filter '*.txt'",
                        "alternatives": ["ls *.txt", "dir *.txt"]
                    }
                }
            ],
            requirements=["AI engine available", "Local AI model loaded"],
            permissions=["read_system_info"],
            rate_limit={
                "requests_per_minute": 60,
                "burst_limit": 10
            }
        )
        
        # PowerShell Command Execution Tool
        exec_tool = ToolDefinition(
            name="execute_powershell_command",
            description="Execute PowerShell commands with security validation and sandbox support",
            category=ToolCategory.COMMAND_EXECUTION,
            version="1.0.0",
            status=ToolStatus.AVAILABLE,
            request_schema=ExecuteCommandToolRequest.model_json_schema(),
            response_schema=ExecuteCommandToolResponse.model_json_schema(),
            parameters={
                "max_execution_time": 3600,
                "max_output_size": 10485760,  # 10MB
                "default_timeout": 60,
                "sandbox_enabled": True
            },
            examples=[
                {
                    "description": "List directory contents",
                    "request": {
                        "command": "Get-ChildItem",
                        "use_sandbox": True,
                        "timeout": 30
                    },
                    "expected_response": {
                        "success": True,
                        "return_code": 0,
                        "stdout": "Directory listing output..."
                    }
                },
                {
                    "description": "Get system information",
                    "request": {
                        "command": "Get-ComputerInfo",
                        "output_format": "JSON",
                        "use_sandbox": False
                    },
                    "expected_response": {
                        "success": True,
                        "return_code": 0,
                        "output_format": "JSON"
                    }
                }
            ],
            requirements=["PowerShell available", "Security engine enabled"],
            permissions=["execute_commands", "access_sandbox"],
            rate_limit={
                "requests_per_minute": 30,
                "burst_limit": 5
            }
        )
        
        # System Information Tool
        info_tool = ToolDefinition(
            name="get_powershell_info",
            description="Get PowerShell environment and system information",
            category=ToolCategory.SYSTEM_INFO,
            version="1.0.0",
            status=ToolStatus.AVAILABLE,
            request_schema=SystemInfoToolRequest.model_json_schema(),
            response_schema=SystemInfoToolResponse.model_json_schema(),
            parameters={
                "include_sensitive_info": False,
                "cache_duration_seconds": 300,
                "max_modules_listed": 1000
            },
            examples=[
                {
                    "description": "Basic system info",
                    "request": {
                        "include_modules": True,
                        "include_environment": False
                    },
                    "expected_response": {
                        "success": True,
                        "powershell": {"version": "7.3.0", "edition": "Core"},
                        "platform": "Windows"
                    }
                },
                {
                    "description": "Detailed system info",
                    "request": {
                        "include_modules": True,
                        "include_environment": True,
                        "include_performance": True,
                        "detailed_info": True
                    },
                    "expected_response": {
                        "success": True,
                        "modules": [],
                        "environment": {},
                        "performance": {}
                    }
                }
            ],
            requirements=["PowerShell available"],
            permissions=["read_system_info"],
            rate_limit={
                "requests_per_minute": 120,
                "burst_limit": 20
            }
        )
        
        # Register all built-in tools
        for tool in [nl_tool, exec_tool, info_tool]:
            self.register_tool(tool)
        
        self.logger.info("Built-in tools registered successfully")
    
    def register_tool(self, tool: ToolDefinition) -> bool:
        """Register a new tool
        
        Args:
            tool: Tool definition to register
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Validate tool definition
            if not tool.name or not tool.description:
                self.logger.error(f"Invalid tool definition: missing name or description")
                return False
            
            # Check for conflicts
            if tool.name in self.registry.tools:
                existing_tool = self.registry.tools[tool.name]
                if existing_tool.version == tool.version:
                    self.logger.warning(f"Tool {tool.name} v{tool.version} already registered")
                    return False
                else:
                    self.logger.info(f"Updating tool {tool.name} from v{existing_tool.version} to v{tool.version}")
            
            # Add to registry
            self.registry.add_tool(tool)
            
            # Save registry
            self._save_registry()
            
            self.logger.info(f"Successfully registered tool: {tool.name} v{tool.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool
        
        Args:
            tool_name: Name of tool to unregister
            
        Returns:
            True if unregistration successful, False otherwise
        """
        try:
            if self.registry.remove_tool(tool_name):
                # Remove handler if exists
                if tool_name in self.tool_handlers:
                    del self.tool_handlers[tool_name]
                
                # Save registry
                self._save_registry()
                
                self.logger.info(f"Successfully unregistered tool: {tool_name}")
                return True
            else:
                self.logger.warning(f"Tool not found for unregistration: {tool_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister tool {tool_name}: {e}")
            return False
    
    def register_tool_handler(self, tool_name: str, handler: Callable) -> bool:
        """Register a handler function for a tool
        
        Args:
            tool_name: Name of the tool
            handler: Handler function for the tool
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            if tool_name not in self.registry.tools:
                self.logger.error(f"Cannot register handler for unknown tool: {tool_name}")
                return False
            
            self.tool_handlers[tool_name] = handler
            self.logger.info(f"Registered handler for tool: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register handler for tool {tool_name}: {e}")
            return False
    
    def get_tool_definition(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool definition if found, None otherwise
        """
        return self.registry.tools.get(tool_name)
    
    def get_available_tools(self) -> List[ToolDefinition]:
        """Get all available tools
        
        Returns:
            List of available tool definitions
        """
        return self.registry.get_available_tools()
    
    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get tools by category
        
        Args:
            category: Tool category
            
        Returns:
            List of tool definitions in the category
        """
        return self.registry.get_tools_by_category(category)
    
    def set_tool_status(self, tool_name: str, status: ToolStatus) -> bool:
        """Set tool status
        
        Args:
            tool_name: Name of the tool
            status: New status
            
        Returns:
            True if status updated successfully, False otherwise
        """
        try:
            if tool_name not in self.registry.tools:
                self.logger.error(f"Cannot set status for unknown tool: {tool_name}")
                return False
            
            old_status = self.registry.tools[tool_name].status
            self.registry.tools[tool_name].status = status
            
            # Save registry
            self._save_registry()
            
            self.logger.info(f"Updated tool {tool_name} status from {old_status.value} to {status.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set status for tool {tool_name}: {e}")
            return False
    
    def validate_tool_request(self, tool_name: str, request_data: Dict[str, Any]) -> Any:
        """Validate a tool request
        
        Args:
            tool_name: Name of the tool
            request_data: Request data to validate
            
        Returns:
            Validated request object or error
        """
        return validate_tool_request(tool_name, request_data)
    
    def format_tool_response(self, tool_name: str, response_data: Dict[str, Any]) -> Any:
        """Format a tool response
        
        Args:
            tool_name: Name of the tool
            response_data: Response data to format
            
        Returns:
            Formatted response object
        """
        return format_tool_response(tool_name, response_data)
    
    def get_tool_handler(self, tool_name: str) -> Optional[Callable]:
        """Get tool handler function
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Handler function if registered, None otherwise
        """
        return self.tool_handlers.get(tool_name)
    
    def discover_tools(self, search_paths: List[str] = None) -> int:
        """Discover tools from specified paths
        
        Args:
            search_paths: Paths to search for tool definitions
            
        Returns:
            Number of tools discovered and registered
        """
        # This is a placeholder for future implementation
        # Could scan directories for tool definition files
        discovered_count = 0
        
        if search_paths:
            for path in search_paths:
                try:
                    search_path = Path(path)
                    if search_path.exists() and search_path.is_dir():
                        # Scan for tool definition files (*.tool.json)
                        for tool_file in search_path.glob("*.tool.json"):
                            try:
                                with open(tool_file, 'r', encoding='utf-8') as f:
                                    tool_data = json.load(f)
                                    tool = ToolDefinition(**tool_data)
                                    if self.register_tool(tool):
                                        discovered_count += 1
                            except Exception as e:
                                self.logger.error(f"Failed to load tool from {tool_file}: {e}")
                except Exception as e:
                    self.logger.error(f"Failed to scan path {path}: {e}")
        
        self.logger.info(f"Discovered and registered {discovered_count} tools")
        return discovered_count
    
    def get_registry_info(self) -> Dict[str, Any]:
        """Get registry information
        
        Returns:
            Registry information dictionary
        """
        return {
            "version": self.registry.version,
            "last_updated": self.registry.last_updated,
            "total_tools": len(self.registry.tools),
            "available_tools": len(self.registry.get_available_tools()),
            "categories": {
                category: len(tools) 
                for category, tools in self.registry.categories.items()
            },
            "tools": {
                name: {
                    "version": tool.version,
                    "status": tool.status.value,
                    "category": tool.category.value
                }
                for name, tool in self.registry.tools.items()
            }
        }