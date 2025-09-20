"""Main Integration Module for AI PowerShell Assistant

This module implements the complete integration of all components and provides
the main MCP tool implementations with full pipeline integration.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import traceback

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config.manager import ConfigurationManager, load_config
from config.models import ServerConfig
from interfaces.base import Platform, UserRole, AuditEventType, RiskLevel
from mcp_server.server import PowerShellAssistantMCP
from ai_engine.engine import AIEngine
from security.engine import SecurityEngine
from execution.executor import PowerShellExecutor
from context.manager import ContextManager
from log_engine.engine import LoggingEngine
from storage.file_storage import FileStorage
from error_handling import error_handler, ErrorContext, handle_errors


class AIPowerShellAssistantIntegration:
    """Main integration class that orchestrates all components
    
    This class provides the complete integration of all system components
    and implements the main MCP tools with full pipeline functionality.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the integration with all components
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config: Optional[ServerConfig] = None
        self.config_manager: Optional[ConfigManager] = None
        
        # Core components
        self.mcp_server: Optional[PowerShellAssistantMCP] = None
        self.ai_engine: Optional[AIEngine] = None
        self.security_engine: Optional[SecurityEngine] = None
        self.executor: Optional[PowerShellExecutor] = None
        self.context_manager: Optional[ContextManager] = None
        self.logging_engine: Optional[LoggingEngine] = None
        self.storage: Optional[FileStorage] = None
        
        # State tracking
        self._initialized = False
        self._running = False
        self._shutdown_requested = False
        
        # Load configuration
        self._load_configuration(config_path)
    
    def _load_configuration(self, config_path: Optional[str] = None) -> None:
        """Load system configuration"""
        try:
            if config_path:
                self.config_manager = ConfigurationManager(config_path)
                self.config = self.config_manager.load_configuration()
            else:
                self.config = load_config()
            
            # Setup logging based on configuration
            logging.basicConfig(
                level=getattr(logging, self.config.logging.log_level.value.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            self.logger.info(f"Configuration loaded successfully")
            self.logger.info(f"Platform: {self.config.platform.value}")
            self.logger.info(f"Version: {self.config.version}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize_components(self) -> None:
        """Initialize all system components in the correct order"""
        try:
            self.logger.info("Initializing AI PowerShell Assistant components...")
            
            # 1. Initialize storage first (needed by other components)
            self.logger.info("Initializing storage...")
            self.storage = FileStorage(self.config.storage)
            await self.storage.initialize()
            
            # 2. Initialize logging engine
            self.logger.info("Initializing logging engine...")
            self.logging_engine = LoggingEngine(self.config.logging)
            await self.logging_engine.initialize()
            
            # 3. Initialize context manager
            self.logger.info("Initializing context manager...")
            self.context_manager = ContextManager(
                self.config.context, 
                self.storage
            )
            await self.context_manager.initialize()
            
            # 4. Initialize AI engine
            self.logger.info("Initializing AI engine...")
            self.ai_engine = AIEngine(self.config.model)
            await self.ai_engine.initialize()
            
            # 5. Initialize security engine
            self.logger.info("Initializing security engine...")
            self.security_engine = SecurityEngine(self.config.security)
            await self.security_engine.initialize()
            
            # 6. Initialize PowerShell executor
            self.logger.info("Initializing PowerShell executor...")
            self.executor = PowerShellExecutor(self.config.execution)
            await self.executor.initialize()
            
            # 7. Initialize MCP server and inject dependencies
            self.logger.info("Initializing MCP server...")
            self.mcp_server = PowerShellAssistantMCP(self.config)
            self.mcp_server.set_components(
                ai_engine=self.ai_engine,
                security_engine=self.security_engine,
                executor=self.executor,
                context_manager=self.context_manager,
                logging_engine=self.logging_engine
            )
            
            # 8. Create and set tool implementations
            tool_implementations = MCPToolImplementations(self)
            self.mcp_server.set_tool_implementations(tool_implementations)
            
            # 9. Register MCP tools
            self.mcp_server.register_tools()
            
            self._initialized = True
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            self.logger.error(traceback.format_exc())
            
            # Handle error with recovery system
            context = ErrorContext(
                component="integration",
                operation="initialize_components",
                additional_data={"config_path": str(self.config.storage.data_directory)}
            )
            await error_handler.handle_error(e, context, "initialization_error")
            
            await self._cleanup_components()
            raise
    
    async def start_server(self) -> None:
        """Start the MCP server and all components"""
        try:
            if not self._initialized:
                await self.initialize_components()
            
            self.logger.info("Starting AI PowerShell Assistant MCP server...")
            
            # Start all components that need startup
            if self.logging_engine:
                await self.logging_engine.start()
            
            if self.context_manager:
                await self.context_manager.start()
            
            if self.ai_engine:
                await self.ai_engine.start()
            
            if self.security_engine:
                await self.security_engine.start()
            
            if self.executor:
                await self.executor.start()
            
            # Start MCP server (this will block)
            self._running = True
            self.logger.info("AI PowerShell Assistant is ready to accept requests")
            
            if self.mcp_server:
                await self.mcp_server.start_server()
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.logger.error(traceback.format_exc())
            await self.shutdown()
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all components"""
        if self._shutdown_requested:
            return
        
        self._shutdown_requested = True
        self.logger.info("Shutting down AI PowerShell Assistant...")
        
        try:
            # Stop MCP server first
            if self.mcp_server:
                self.mcp_server.shutdown()
            
            # Stop other components in reverse order
            if self.executor:
                await self.executor.stop()
            
            if self.security_engine:
                await self.security_engine.stop()
            
            if self.ai_engine:
                await self.ai_engine.stop()
            
            if self.context_manager:
                await self.context_manager.stop()
            
            if self.logging_engine:
                await self.logging_engine.stop()
            
            if self.storage:
                await self.storage.close()
            
            self._running = False
            self.logger.info("Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.logger.error(traceback.format_exc())
    
    async def _cleanup_components(self) -> None:
        """Clean up components after initialization failure"""
        components = [
            self.storage, self.logging_engine, self.context_manager,
            self.ai_engine, self.security_engine, self.executor
        ]
        
        for component in components:
            if component:
                try:
                    if hasattr(component, 'stop'):
                        await component.stop()
                    elif hasattr(component, 'close'):
                        await component.close()
                except Exception as e:
                    self.logger.error(f"Error cleaning up component {component}: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        health_status = {
            "overall": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {}
        }
        
        components = {
            "storage": self.storage,
            "logging_engine": self.logging_engine,
            "context_manager": self.context_manager,
            "ai_engine": self.ai_engine,
            "security_engine": self.security_engine,
            "executor": self.executor,
            "mcp_server": self.mcp_server
        }
        
        overall_healthy = True
        
        for name, component in components.items():
            try:
                if component and hasattr(component, 'health_check'):
                    component_health = await component.health_check()
                    health_status["components"][name] = component_health
                    
                    if component_health.get("status") != "healthy":
                        overall_healthy = False
                else:
                    health_status["components"][name] = {
                        "status": "not_available" if component is None else "no_health_check",
                        "message": "Component not available" if component is None else "No health check method"
                    }
                    if component is None:
                        overall_healthy = False
                        
            except Exception as e:
                health_status["components"][name] = {
                    "status": "error",
                    "error": str(e)
                }
                overall_healthy = False
        
        health_status["overall"] = "healthy" if overall_healthy else "unhealthy"
        return health_status
    
    @property
    def is_running(self) -> bool:
        """Check if the server is running"""
        return self._running and not self._shutdown_requested
    
    @property
    def is_initialized(self) -> bool:
        """Check if components are initialized"""
        return self._initialized


# Main MCP Tool Implementations with Full Pipeline Integration
class MCPToolImplementations:
    """Complete MCP tool implementations with full pipeline integration
    
    This class provides the actual tool implementations that integrate
    all components in the correct order with proper error handling.
    """
    
    def __init__(self, integration: AIPowerShellAssistantIntegration):
        """Initialize with integration instance
        
        Args:
            integration: Main integration instance with all components
        """
        self.integration = integration
        self.logger = logging.getLogger(__name__)
    
    async def natural_language_to_powershell(self, 
                                           input_text: str,
                                           session_id: Optional[str] = None,
                                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Complete natural language to PowerShell conversion with full pipeline
        
        This implements the complete pipeline:
        1. Input validation and logging
        2. Session management and context retrieval
        3. AI processing with local models
        4. Security validation of generated commands
        5. Context updates and learning
        6. Comprehensive logging and audit trail
        
        Args:
            input_text: Natural language input to convert
            session_id: Optional session identifier
            context: Optional additional context
            
        Returns:
            Complete response with generated command and metadata
        """
        correlation_id = None
        
        try:
            # 1. Input validation
            if not input_text or not input_text.strip():
                return {
                    "success": False,
                    "error": "Input text cannot be empty",
                    "error_code": "INVALID_INPUT"
                }
            
            input_text = input_text.strip()
            
            # 2. Session management
            if not session_id and self.integration.context_manager:
                session_id = self.integration.context_manager.create_session(
                    UserRole.USER,
                    self.integration.config.platform
                )
            
            # 3. Logging - Start of request
            if self.integration.logging_engine:
                correlation_id = self.integration.logging_engine.log_user_input(
                    session_id or "unknown",
                    input_text,
                    datetime.now(timezone.utc)
                )
            
            # 4. Get current context
            cmd_context = None
            if self.integration.context_manager and session_id:
                cmd_context = self.integration.context_manager.get_current_context(session_id)
            
            # 5. AI processing with graceful degradation
            if not self.integration.ai_engine:
                # Handle AI engine unavailable with fallback
                context = ErrorContext(
                    component="ai_engine",
                    operation="translate_natural_language",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=input_text
                )
                
                recovery_result = await error_handler.handle_error(
                    Exception("AI engine not available"), 
                    context, 
                    "ai_engine_unavailable"
                )
                
                # Return fallback response
                fallback_result = recovery_result.get("fallback_result", {})
                return {
                    **fallback_result,
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            
            # Translate natural language to PowerShell with error handling
            try:
                suggestion = self.integration.ai_engine.translate_natural_language(
                    input_text, 
                    cmd_context
                )
            except Exception as ai_error:
                # Handle AI processing error with retry/fallback
                context = ErrorContext(
                    component="ai_engine",
                    operation="translate_natural_language",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=input_text
                )
                
                recovery_result = await error_handler.handle_error(
                    ai_error, 
                    context, 
                    "ai_processing_error"
                )
                
                # Check if recovery suggests retry
                if recovery_result.get("recovery_action") == "retry":
                    # Implement retry logic here if needed
                    pass
                
                # Return error with recovery information
                return {
                    "success": False,
                    "error": str(ai_error),
                    "error_code": "AI_PROCESSING_ERROR",
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            
            # 6. Log AI processing
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_ai_processing(
                    correlation_id,
                    input_text,
                    suggestion.generated_command,
                    suggestion.confidence_score
                )
            
            # 7. Security validation of generated command
            security_validation = None
            if self.integration.security_engine:
                validation_result = self.integration.security_engine.validate_command(
                    suggestion.generated_command
                )
                
                security_validation = {
                    "is_valid": validation_result.is_valid,
                    "risk_level": validation_result.risk_assessment.value if validation_result.risk_assessment else "unknown",
                    "blocked_reasons": validation_result.blocked_reasons,
                    "required_permissions": [perm.value for perm in validation_result.required_permissions]
                }
                
                # Log security validation
                if self.integration.logging_engine and correlation_id:
                    self.integration.logging_engine.log_security_validation(
                        correlation_id,
                        suggestion.generated_command,
                        validation_result
                    )
            
            # 8. Update context with successful translation
            if self.integration.context_manager and session_id:
                # Create a mock execution result for context update
                from interfaces.base import ExecutionResult
                mock_result = ExecutionResult(
                    success=True,
                    return_code=0,
                    stdout="",
                    stderr="",
                    execution_time=0.0,
                    platform=self.integration.config.platform,
                    sandbox_used=False
                )
                
                self.integration.context_manager.update_context(
                    session_id,
                    suggestion.generated_command,
                    mock_result
                )
            
            # 9. Prepare response
            response = {
                "success": True,
                "original_input": suggestion.original_input,
                "generated_command": suggestion.generated_command,
                "confidence_score": suggestion.confidence_score,
                "explanation": suggestion.explanation,
                "alternatives": suggestion.alternatives,
                "session_id": session_id,
                "correlation_id": correlation_id,
                "security_validation": security_validation,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in natural_language_to_powershell: {e}")
            self.logger.error(traceback.format_exc())
            
            # Log error
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_error(correlation_id, e, {
                    "input_text": input_text,
                    "session_id": session_id,
                    "context": context
                })
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "PROCESSING_ERROR",
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def execute_powershell_command(self,
                                       command: str,
                                       session_id: Optional[str] = None,
                                       timeout: int = 60,
                                       use_sandbox: bool = True) -> Dict[str, Any]:
        """Complete PowerShell command execution with full security and logging
        
        This implements the complete execution pipeline:
        1. Input validation and sanitization
        2. Session management and context retrieval
        3. Security validation (whitelist, permissions, risk assessment)
        4. Sandbox or direct execution based on security policy
        5. Output formatting and standardization
        6. Context updates and learning
        7. Comprehensive logging and audit trail
        
        Args:
            command: PowerShell command to execute
            session_id: Optional session identifier
            timeout: Execution timeout in seconds
            use_sandbox: Whether to use sandbox execution
            
        Returns:
            Complete execution result with metadata
        """
        correlation_id = None
        
        try:
            # 1. Input validation
            if not command or not command.strip():
                return {
                    "success": False,
                    "error": "Command cannot be empty",
                    "error_code": "INVALID_COMMAND"
                }
            
            command = command.strip()
            
            # 2. Session management
            if not session_id and self.integration.context_manager:
                session_id = self.integration.context_manager.create_session(
                    UserRole.USER,
                    self.integration.config.platform
                )
            
            # 3. Logging - Start of execution request
            if self.integration.logging_engine:
                correlation_id = self.integration.logging_engine.log_user_input(
                    session_id or "unknown",
                    f"EXECUTE: {command}",
                    datetime.now(timezone.utc)
                )
            
            # 4. Security validation with graceful degradation
            if not self.integration.security_engine:
                # Handle security engine unavailable with fail-safe
                context = ErrorContext(
                    component="security_engine",
                    operation="validate_command",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=command
                )
                
                recovery_result = await error_handler.handle_error(
                    Exception("Security engine not available"), 
                    context, 
                    "security_engine_unavailable"
                )
                
                # Return fail-safe response (block execution for safety)
                fail_safe_result = recovery_result.get("fail_safe_result", {})
                return {
                    **fail_safe_result,
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            
            validation_result = self.integration.security_engine.validate_command(command)
            
            # Log security validation
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_security_validation(
                    correlation_id,
                    command,
                    validation_result
                )
            
            # Check if command is blocked
            if not validation_result.is_valid:
                return {
                    "success": False,
                    "error": "Command blocked by security policy",
                    "error_code": "SECURITY_BLOCKED",
                    "blocked_reasons": validation_result.blocked_reasons,
                    "suggested_alternatives": validation_result.suggested_alternatives,
                    "risk_assessment": {
                        "risk_level": validation_result.risk_assessment.value if validation_result.risk_assessment else "unknown"
                    },
                    "correlation_id": correlation_id
                }
            
            # 5. Get execution context
            cmd_context = None
            if self.integration.context_manager and session_id:
                cmd_context = self.integration.context_manager.get_current_context(session_id)
            
            # 6. Execute command with graceful degradation
            if not self.integration.executor:
                # Handle executor unavailable with degraded mode
                context = ErrorContext(
                    component="executor",
                    operation="execute_command",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=command
                )
                
                recovery_result = await error_handler.handle_error(
                    Exception("Execution engine not available"), 
                    context, 
                    "executor_unavailable"
                )
                
                # Return degraded mode response
                degraded_result = recovery_result.get("degraded_result", {})
                return {
                    **degraded_result,
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            
            # Choose execution method based on security policy and sandbox preference
            execution_result = None
            
            try:
                if (use_sandbox and 
                    self.integration.config.security.sandbox_enabled and
                    validation_result.risk_assessment and
                    validation_result.risk_assessment == RiskLevel.HIGH):
                    
                    # Execute in sandbox
                    execution_result = self.integration.security_engine.execute_in_sandbox(
                        command, 
                        timeout
                    )
                else:
                    # Direct execution
                    execution_result = self.integration.executor.execute_command(
                        command, 
                        cmd_context
                    )
            except TimeoutError as timeout_error:
                # Handle execution timeout with retry
                context = ErrorContext(
                    component="executor",
                    operation="execute_command",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=command,
                    additional_data={"timeout": timeout, "use_sandbox": use_sandbox}
                )
                
                recovery_result = await error_handler.handle_error(
                    timeout_error, 
                    context, 
                    "execution_timeout"
                )
                
                return {
                    "success": False,
                    "error": "Command execution timed out",
                    "error_code": "EXECUTION_TIMEOUT",
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            except Exception as exec_error:
                # Handle other execution errors
                context = ErrorContext(
                    component="executor",
                    operation="execute_command",
                    correlation_id=correlation_id,
                    session_id=session_id,
                    user_input=command
                )
                
                recovery_result = await error_handler.handle_error(
                    exec_error, 
                    context, 
                    "execution_error"
                )
                
                return {
                    "success": False,
                    "error": str(exec_error),
                    "error_code": "EXECUTION_ERROR",
                    "correlation_id": correlation_id,
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error_handling": recovery_result
                }
            
            # 7. Log execution result
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_command_execution(
                    correlation_id,
                    command,
                    execution_result
                )
            
            # 8. Update context with execution result
            if self.integration.context_manager and session_id:
                self.integration.context_manager.update_context(
                    session_id,
                    command,
                    execution_result
                )
            
            # 9. Format output
            formatted_output = execution_result.stdout
            if self.integration.executor:
                try:
                    from interfaces.base import OutputFormat
                    formatted_output = self.integration.executor.format_output(
                        execution_result.stdout,
                        OutputFormat.JSON
                    )
                except Exception as format_error:
                    self.logger.warning(f"Output formatting failed: {format_error}")
                    # Use raw output as fallback
                    formatted_output = execution_result.stdout
            
            # 10. Prepare response
            response = {
                "success": execution_result.success,
                "return_code": execution_result.return_code,
                "stdout": formatted_output,
                "stderr": execution_result.stderr,
                "execution_time": execution_result.execution_time,
                "platform": execution_result.platform.value,
                "sandbox_used": execution_result.sandbox_used,
                "session_id": session_id,
                "correlation_id": correlation_id,
                "security_validation": {
                    "is_valid": validation_result.is_valid,
                    "risk_level": validation_result.risk_assessment.value if validation_result.risk_assessment else "low",
                    "required_permissions": [perm.value for perm in validation_result.required_permissions]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in execute_powershell_command: {e}")
            self.logger.error(traceback.format_exc())
            
            # Log error
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_error(correlation_id, e, {
                    "command": command,
                    "session_id": session_id,
                    "timeout": timeout,
                    "use_sandbox": use_sandbox
                })
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR",
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_powershell_info(self,
                                session_id: Optional[str] = None,
                                include_modules: bool = True,
                                include_environment: bool = False) -> Dict[str, Any]:
        """Get comprehensive PowerShell system information
        
        This provides detailed information about:
        1. PowerShell version and capabilities
        2. Available modules and cmdlets
        3. System environment and configuration
        4. Security settings and constraints
        5. Performance metrics and health status
        
        Args:
            session_id: Optional session identifier
            include_modules: Whether to include module information
            include_environment: Whether to include environment variables
            
        Returns:
            Comprehensive system information
        """
        correlation_id = None
        
        try:
            # 1. Session management
            if not session_id and self.integration.context_manager:
                session_id = self.integration.context_manager.create_session(
                    UserRole.USER,
                    self.integration.config.platform
                )
            
            # 2. Logging - Start of info request
            if self.integration.logging_engine:
                correlation_id = self.integration.logging_engine.log_user_input(
                    session_id or "unknown",
                    "GET_SYSTEM_INFO",
                    datetime.now(timezone.utc)
                )
            
            # 3. Get PowerShell information with graceful degradation
            if not self.integration.executor:
                # Handle executor unavailable with degraded mode
                context = ErrorContext(
                    component="executor",
                    operation="get_powershell_info",
                    correlation_id=correlation_id,
                    session_id=session_id
                )
                
                recovery_result = await error_handler.handle_error(
                    Exception("Execution engine not available"), 
                    context, 
                    "executor_unavailable"
                )
                
                # Return basic system info without PowerShell details
                return {
                    "success": True,
                    "powershell": {"status": "unavailable", "message": "Executor not available"},
                    "platform": self.integration.config.platform.value,
                    "server_version": self.integration.config.version,
                    "session_id": session_id,
                    "correlation_id": correlation_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "degraded_mode": True,
                    "error_handling": recovery_result
                }
            
            ps_info = self.integration.executor.get_powershell_info()
            
            # 4. Build comprehensive system information
            system_info = {
                "success": True,
                "powershell": ps_info,
                "platform": self.integration.config.platform.value,
                "server_version": self.integration.config.version,
                "session_id": session_id,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # 5. Add component health information
            try:
                health_status = await self.integration.health_check()
                system_info["health"] = health_status
            except Exception as health_error:
                self.logger.warning(f"Health check failed: {health_error}")
                system_info["health"] = {"status": "unknown", "error": str(health_error)}
            
            # 6. Add security configuration (safe subset)
            if self.integration.security_engine:
                try:
                    security_info = {
                        "sandbox_enabled": self.integration.config.security.sandbox_enabled,
                        "whitelist_enabled": True,  # Always enabled
                        "permission_checking_enabled": True,  # Always enabled
                        "audit_logging_enabled": self.integration.config.logging.enable_correlation_tracking
                    }
                    system_info["security"] = security_info
                except Exception as security_error:
                    self.logger.warning(f"Security info collection failed: {security_error}")
            
            # 7. Add AI engine information
            if self.integration.ai_engine:
                try:
                    ai_info = {
                        "model_type": self.integration.config.model.model_type,
                        "model_available": True,
                        "context_length": self.integration.config.model.context_length
                    }
                    system_info["ai_engine"] = ai_info
                except Exception as ai_error:
                    self.logger.warning(f"AI engine info collection failed: {ai_error}")
            
            # 8. Add modules if requested
            if include_modules:
                try:
                    # This would be implemented by getting available PowerShell modules
                    modules_info = ps_info.get("modules", [])
                    system_info["modules"] = modules_info
                except Exception as modules_error:
                    self.logger.warning(f"Module info collection failed: {modules_error}")
                    system_info["modules"] = []
            
            # 9. Add environment if requested
            if include_environment:
                try:
                    # This would be implemented by getting environment variables
                    env_info = ps_info.get("environment", {})
                    # Filter sensitive environment variables
                    filtered_env = {k: v for k, v in env_info.items() 
                                  if not any(sensitive in k.upper() 
                                           for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN'])}
                    system_info["environment"] = filtered_env
                except Exception as env_error:
                    self.logger.warning(f"Environment info collection failed: {env_error}")
                    system_info["environment"] = {}
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error in get_powershell_info: {e}")
            self.logger.error(traceback.format_exc())
            
            # Log error
            if self.integration.logging_engine and correlation_id:
                self.integration.logging_engine.log_error(correlation_id, e, {
                    "session_id": session_id,
                    "include_modules": include_modules,
                    "include_environment": include_environment
                })
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "INFO_COLLECTION_ERROR",
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Convenience function for creating and running the integration
async def create_and_run_integration(config_path: Optional[str] = None) -> AIPowerShellAssistantIntegration:
    """Create and run the complete AI PowerShell Assistant integration
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Running integration instance
    """
    integration = AIPowerShellAssistantIntegration(config_path)
    await integration.start_server()
    return integration


if __name__ == "__main__":
    # Example usage
    async def main():
        integration = None
        try:
            integration = await create_and_run_integration()
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if integration:
                await integration.shutdown()
    
    asyncio.run(main())