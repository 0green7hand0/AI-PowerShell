"""FastMCP Server Core Implementation

This module implements the PowerShellAssistantMCP class using the FastMCP framework
for tool registration, lifecycle management, and MCP protocol communication.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import traceback

from fastmcp import FastMCP
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    MCPServerInterface, CommandContext, ExecutionResult, 
    Platform, UserRole, AuditEventType
)
from config.models import ServerConfig
from mcp_server.discovery import ToolDiscoveryManager
from mcp_server.schemas import (
    NaturalLanguageToolRequest, ExecuteCommandToolRequest, SystemInfoToolRequest,
    ToolError
)


class NaturalLanguageRequest(BaseModel):
    """Request model for natural language processing"""
    input_text: str = Field(..., description="Natural language input to convert to PowerShell")
    session_id: Optional[str] = Field(None, description="Session identifier for context tracking")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")


class ExecuteCommandRequest(BaseModel):
    """Request model for PowerShell command execution"""
    command: str = Field(..., description="PowerShell command to execute")
    session_id: Optional[str] = Field(None, description="Session identifier for context tracking")
    timeout: Optional[int] = Field(60, description="Execution timeout in seconds")
    use_sandbox: Optional[bool] = Field(True, description="Whether to execute in sandbox")


class SystemInfoRequest(BaseModel):
    """Request model for system information"""
    session_id: Optional[str] = Field(None, description="Session identifier for context tracking")
    include_modules: Optional[bool] = Field(True, description="Include PowerShell module information")
    include_environment: Optional[bool] = Field(False, description="Include environment variables")


class PowerShellAssistantMCP(MCPServerInterface):
    """FastMCP server implementation for PowerShell Assistant
    
    This class provides the main MCP server functionality using the FastMCP framework.
    It handles tool registration, request routing, and lifecycle management.
    """
    
    def __init__(self, config: ServerConfig):
        """Initialize the MCP server with configuration
        
        Args:
            config: Server configuration containing all component settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.app: Optional[FastMCP] = None
        self._running = False
        
        # Component references (will be injected)
        self.ai_engine = None
        self.security_engine = None
        self.executor = None
        self.context_manager = None
        self.logging_engine = None
        
        # Session tracking
        self.active_sessions: Dict[str, CommandContext] = {}
        
        # Tool discovery and registration
        self.tool_discovery = ToolDiscoveryManager()
        
        self.logger.info("PowerShellAssistantMCP initialized")
    
    def set_components(self, ai_engine=None, security_engine=None, executor=None, 
                      context_manager=None, logging_engine=None):
        """Inject component dependencies
        
        Args:
            ai_engine: AI processing engine
            security_engine: Security validation engine
            executor: PowerShell execution engine
            context_manager: Context management engine
            logging_engine: Logging and audit engine
        """
        self.ai_engine = ai_engine
        self.security_engine = security_engine
        self.executor = executor
        self.context_manager = context_manager
        self.logging_engine = logging_engine
        
        self.logger.info("Component dependencies injected")
    
    def set_tool_implementations(self, tool_implementations):
        """Set the integrated tool implementations
        
        Args:
            tool_implementations: MCPToolImplementations instance
        """
        self._tool_implementations = tool_implementations
        self.logger.info("Tool implementations set")
    
    def register_tools(self) -> None:
        """Register MCP tools with the FastMCP server"""
        if self.app is None:
            self.app = FastMCP("AI PowerShell Assistant")
        
        # Register tool handlers with discovery manager
        self.tool_discovery.register_tool_handler(
            "natural_language_to_powershell", 
            self._handle_natural_language_request
        )
        self.tool_discovery.register_tool_handler(
            "execute_powershell_command", 
            self._handle_execute_command
        )
        self.tool_discovery.register_tool_handler(
            "get_powershell_info", 
            self._handle_get_system_info
        )
        
        # Register natural language processing tool
        if self.config.mcp_server.enable_natural_language_tool:
            @self.app.tool()
            async def natural_language_to_powershell(request: NaturalLanguageToolRequest) -> Dict[str, Any]:
                """Convert natural language input to PowerShell commands
                
                This tool takes natural language descriptions and converts them to
                executable PowerShell commands using local AI models.
                """
                # Validate request using discovery manager
                validated_request = self.tool_discovery.validate_tool_request(
                    "natural_language_to_powershell", 
                    request.model_dump()
                )
                
                if isinstance(validated_request, ToolError):
                    return validated_request.model_dump()
                
                return await self._handle_natural_language_request(
                    request.input_text, 
                    request.session_id, 
                    request.context or {}
                )
        
        # Register command execution tool
        if self.config.mcp_server.enable_execute_command_tool:
            @self.app.tool()
            async def execute_powershell_command(request: ExecuteCommandToolRequest) -> Dict[str, Any]:
                """Execute PowerShell commands with security validation
                
                This tool executes PowerShell commands after security validation
                and returns formatted results with execution metadata.
                """
                # Validate request using discovery manager
                validated_request = self.tool_discovery.validate_tool_request(
                    "execute_powershell_command", 
                    request.model_dump()
                )
                
                if isinstance(validated_request, ToolError):
                    return validated_request.model_dump()
                
                return await self._handle_execute_command(
                    request.command,
                    request.session_id,
                    request.timeout,
                    request.use_sandbox
                )
        
        # Register system information tool
        if self.config.mcp_server.enable_system_info_tool:
            @self.app.tool()
            async def get_powershell_info(request: SystemInfoToolRequest) -> Dict[str, Any]:
                """Get PowerShell environment and system information
                
                This tool provides information about the PowerShell environment,
                available modules, and system configuration.
                """
                # Validate request using discovery manager
                validated_request = self.tool_discovery.validate_tool_request(
                    "get_powershell_info", 
                    request.model_dump()
                )
                
                if isinstance(validated_request, ToolError):
                    return validated_request.model_dump()
                
                return await self._handle_get_system_info(
                    request.session_id,
                    request.include_modules,
                    request.include_environment
                )
        
        self.logger.info("MCP tools registered successfully")
    
    async def start_server(self) -> None:
        """Start the MCP server"""
        try:
            if self.app is None:
                self.register_tools()
            
            self._running = True
            self.logger.info("Starting PowerShell Assistant MCP server")
            
            # Start the FastMCP server
            await self.app.run()
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            self.logger.error(traceback.format_exc())
            raise
    
    def shutdown(self) -> None:
        """Shutdown the MCP server gracefully"""
        try:
            self._running = False
            
            # Clean up active sessions
            for session_id in list(self.active_sessions.keys()):
                if self.context_manager:
                    self.context_manager.end_session(session_id)
            
            self.active_sessions.clear()
            
            self.logger.info("PowerShell Assistant MCP server shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during server shutdown: {e}")
            self.logger.error(traceback.format_exc())
    
    async def _handle_natural_language_request(self, input_text: str, 
                                             session_id: Optional[str],
                                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle natural language to PowerShell conversion requests"""
        # Use the integrated tool implementation
        if hasattr(self, '_tool_implementations'):
            return await self._tool_implementations.natural_language_to_powershell(
                input_text, session_id, context
            )
        
        # Fallback to legacy implementation
        correlation_id = None
        
        try:
            # Get or create session
            if not session_id and self.context_manager:
                session_id = self.context_manager.create_session(
                    UserRole.USER, 
                    self.config.platform
                )
            
            # Log user input
            if self.logging_engine:
                correlation_id = self.logging_engine.log_user_input(
                    session_id or "unknown",
                    input_text,
                    datetime.now(timezone.utc)
                )
            
            # Get current context
            cmd_context = None
            if self.context_manager and session_id:
                cmd_context = self.context_manager.get_current_context(session_id)
            
            # Process with AI engine
            if not self.ai_engine:
                return {
                    "success": False,
                    "error": "AI engine not available",
                    "correlation_id": correlation_id
                }
            
            suggestion = self.ai_engine.translate_natural_language(input_text, cmd_context)
            
            # Log AI processing
            if self.logging_engine and correlation_id:
                self.logging_engine.log_ai_processing(
                    correlation_id,
                    input_text,
                    suggestion.generated_command,
                    suggestion.confidence_score
                )
            
            return {
                "success": True,
                "original_input": suggestion.original_input,
                "generated_command": suggestion.generated_command,
                "confidence_score": suggestion.confidence_score,
                "explanation": suggestion.explanation,
                "alternatives": suggestion.alternatives,
                "session_id": session_id,
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Error processing natural language request: {e}")
            self.logger.error(traceback.format_exc())
            
            if self.logging_engine and correlation_id:
                self.logging_engine.log_error(correlation_id, e, {
                    "input_text": input_text,
                    "session_id": session_id
                })
            
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _handle_execute_command(self, command: str, session_id: Optional[str],
                                    timeout: int, use_sandbox: bool) -> Dict[str, Any]:
        """Handle PowerShell command execution requests"""
        # Use the integrated tool implementation
        if hasattr(self, '_tool_implementations'):
            return await self._tool_implementations.execute_powershell_command(
                command, session_id, timeout, use_sandbox
            )
        
        # Fallback to legacy implementation
        correlation_id = None
        
        try:
            # Get or create session
            if not session_id and self.context_manager:
                session_id = self.context_manager.create_session(
                    UserRole.USER,
                    self.config.platform
                )
            
            # Log command execution request
            if self.logging_engine:
                correlation_id = self.logging_engine.log_user_input(
                    session_id or "unknown",
                    f"EXECUTE: {command}",
                    datetime.now(timezone.utc)
                )
            
            # Security validation
            if self.security_engine:
                validation_result = self.security_engine.validate_command(command)
                
                if self.logging_engine and correlation_id:
                    self.logging_engine.log_security_validation(
                        correlation_id, command, validation_result
                    )
                
                if not validation_result.is_valid:
                    return {
                        "success": False,
                        "error": "Command blocked by security policy",
                        "blocked_reasons": validation_result.blocked_reasons,
                        "suggested_alternatives": validation_result.suggested_alternatives,
                        "correlation_id": correlation_id
                    }
            
            # Get execution context
            cmd_context = None
            if self.context_manager and session_id:
                cmd_context = self.context_manager.get_current_context(session_id)
            
            # Execute command
            if not self.executor:
                return {
                    "success": False,
                    "error": "Execution engine not available",
                    "correlation_id": correlation_id
                }
            
            # Choose execution method based on sandbox preference and security settings
            if use_sandbox and self.security_engine and self.config.security.sandbox_enabled:
                result = self.security_engine.execute_in_sandbox(command, timeout)
            else:
                result = self.executor.execute_command(command, cmd_context)
            
            # Log execution result
            if self.logging_engine and correlation_id:
                self.logging_engine.log_command_execution(correlation_id, command, result)
            
            # Update context
            if self.context_manager and session_id:
                self.context_manager.update_context(session_id, command, result)
            
            return {
                "success": result.success,
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
                "platform": result.platform.value,
                "sandbox_used": result.sandbox_used,
                "session_id": session_id,
                "correlation_id": correlation_id
            }
            
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self.logger.error(traceback.format_exc())
            
            if self.logging_engine and correlation_id:
                self.logging_engine.log_error(correlation_id, e, {
                    "command": command,
                    "session_id": session_id
                })
            
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def _handle_get_system_info(self, session_id: Optional[str],
                                    include_modules: bool,
                                    include_environment: bool) -> Dict[str, Any]:
        """Handle system information requests"""
        # Use the integrated tool implementation
        if hasattr(self, '_tool_implementations'):
            return await self._tool_implementations.get_powershell_info(
                session_id, include_modules, include_environment
            )
        
        # Fallback to legacy implementation
        correlation_id = None
        
        try:
            # Get or create session
            if not session_id and self.context_manager:
                session_id = self.context_manager.create_session(
                    UserRole.USER,
                    self.config.platform
                )
            
            # Log system info request
            if self.logging_engine:
                correlation_id = self.logging_engine.log_user_input(
                    session_id or "unknown",
                    "GET_SYSTEM_INFO",
                    datetime.now(timezone.utc)
                )
            
            # Get PowerShell information
            if not self.executor:
                return {
                    "success": False,
                    "error": "Execution engine not available",
                    "correlation_id": correlation_id
                }
            
            ps_info = self.executor.get_powershell_info()
            
            # Add additional system information
            system_info = {
                "powershell": ps_info,
                "platform": self.config.platform.value,
                "server_version": self.config.version,
                "session_id": session_id,
                "correlation_id": correlation_id
            }
            
            # Add modules if requested
            if include_modules:
                # This would be implemented by the executor
                system_info["modules"] = ps_info.get("modules", [])
            
            # Add environment if requested
            if include_environment:
                # This would be implemented by the executor
                system_info["environment"] = ps_info.get("environment", {})
            
            return {
                "success": True,
                **system_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            self.logger.error(traceback.format_exc())
            
            if self.logging_engine and correlation_id:
                self.logging_engine.log_error(correlation_id, e, {
                    "session_id": session_id
                })
            
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    # Legacy interface methods for compatibility
    def handle_natural_language_request(self, input_text: str, session_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for natural language processing"""
        return asyncio.run(self._handle_natural_language_request(input_text, session_id, {}))
    
    def handle_execute_command(self, command: str, session_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for command execution"""
        return asyncio.run(self._handle_execute_command(command, session_id, 60, True))
    
    def handle_get_system_info(self, session_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for system info"""
        return asyncio.run(self._handle_get_system_info(session_id, True, False))
    
    @property
    def is_running(self) -> bool:
        """Check if server is running"""
        return self._running
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_sessions.keys())