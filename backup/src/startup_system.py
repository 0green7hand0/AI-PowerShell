"""System Integration and Startup Logic

This module provides comprehensive system startup, health checks,
monitoring, and graceful shutdown procedures.
"""

import asyncio
import logging
import signal
import sys
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration
from error_handling import error_handler, ErrorContext, ComponentHealthMonitor
from interfaces.base import Platform


class SystemState(Enum):
    """System state enumeration"""
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ComponentState(Enum):
    """Component state enumeration"""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"
    STOPPED = "stopped"


@dataclass
class StartupPhase:
    """Startup phase definition"""
    name: str
    description: str
    required_components: List[str]
    optional_components: List[str]
    startup_function: Callable
    timeout: int = 30
    critical: bool = True


@dataclass
class ComponentInfo:
    """Component information and status"""
    name: str
    state: ComponentState
    instance: Any
    health_check: Optional[Callable] = None
    startup_function: Optional[Callable] = None
    shutdown_function: Optional[Callable] = None
    dependencies: List[str] = None
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    startup_time: Optional[float] = None


class SystemIntegration:
    """Main system integration and startup management"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize system integration
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        
        # System state
        self.state = SystemState.INITIALIZING
        self.startup_time: Optional[float] = None
        self.shutdown_requested = False
        
        # Components
        self.components: Dict[str, ComponentInfo] = {}
        self.integration: Optional[AIPowerShellAssistantIntegration] = None
        
        # Health monitoring
        self.health_monitor = ComponentHealthMonitor()
        self.health_check_interval = 30
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Startup phases
        self.startup_phases: List[StartupPhase] = []
        self._setup_startup_phases()
        
        # Signal handlers
        self._setup_signal_handlers()
        
        self.logger.info("System integration initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_requested = True
            
            # Create shutdown task
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.shutdown())
        
        # Setup signal handlers for Unix systems
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, signal_handler)
    
    def _setup_startup_phases(self):
        """Setup startup phases in correct order"""
        
        # Phase 1: Configuration and Storage
        self.startup_phases.append(StartupPhase(
            name="configuration",
            description="Load configuration and initialize storage",
            required_components=["storage"],
            optional_components=[],
            startup_function=self._startup_phase_configuration,
            timeout=30,
            critical=True
        ))
        
        # Phase 2: Core Services
        self.startup_phases.append(StartupPhase(
            name="core_services",
            description="Initialize logging and context management",
            required_components=["logging_engine", "context_manager"],
            optional_components=[],
            startup_function=self._startup_phase_core_services,
            timeout=30,
            critical=True
        ))
        
        # Phase 3: Processing Engines
        self.startup_phases.append(StartupPhase(
            name="processing_engines",
            description="Initialize AI and security engines",
            required_components=["security_engine"],
            optional_components=["ai_engine"],  # AI engine is optional for degraded mode
            startup_function=self._startup_phase_processing_engines,
            timeout=60,
            critical=False  # Can run in degraded mode without AI
        ))
        
        # Phase 4: Execution Engine
        self.startup_phases.append(StartupPhase(
            name="execution_engine",
            description="Initialize PowerShell executor",
            required_components=[],
            optional_components=["executor"],  # Optional for info-only mode
            startup_function=self._startup_phase_execution_engine,
            timeout=30,
            critical=False
        ))
        
        # Phase 5: MCP Server
        self.startup_phases.append(StartupPhase(
            name="mcp_server",
            description="Initialize and start MCP server",
            required_components=["mcp_server"],
            optional_components=[],
            startup_function=self._startup_phase_mcp_server,
            timeout=30,
            critical=True
        ))
    
    async def startup(self) -> bool:
        """Execute complete system startup sequence
        
        Returns:
            True if startup successful, False otherwise
        """
        try:
            self.logger.info("Starting AI PowerShell Assistant system...")
            self.state = SystemState.STARTING
            startup_start = time.time()
            
            # Create integration instance
            self.integration = AIPowerShellAssistantIntegration(self.config_path)
            
            # Execute startup phases
            for phase in self.startup_phases:
                success = await self._execute_startup_phase(phase)
                
                if not success and phase.critical:
                    self.logger.error(f"Critical startup phase '{phase.name}' failed")
                    self.state = SystemState.ERROR
                    return False
                elif not success:
                    self.logger.warning(f"Optional startup phase '{phase.name}' failed - continuing in degraded mode")
                    self.state = SystemState.DEGRADED
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            # System is now running
            self.startup_time = time.time() - startup_start
            if self.state != SystemState.DEGRADED:
                self.state = SystemState.RUNNING
            
            self.logger.info(f"System startup completed in {self.startup_time:.2f} seconds")
            self.logger.info(f"System state: {self.state.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"System startup failed: {e}")
            self.logger.error(traceback.format_exc())
            
            # Handle startup error
            context = ErrorContext(
                component="system",
                operation="startup",
                additional_data={"config_path": self.config_path}
            )
            await error_handler.handle_error(e, context, "startup_error")
            
            self.state = SystemState.ERROR
            return False
    
    async def _execute_startup_phase(self, phase: StartupPhase) -> bool:
        """Execute a single startup phase
        
        Args:
            phase: Startup phase to execute
            
        Returns:
            True if phase completed successfully
        """
        try:
            self.logger.info(f"Executing startup phase: {phase.name}")
            
            # Execute phase with timeout
            await asyncio.wait_for(
                phase.startup_function(),
                timeout=phase.timeout
            )
            
            # Verify required components are ready
            for component_name in phase.required_components:
                if component_name not in self.components:
                    raise Exception(f"Required component '{component_name}' not initialized")
                
                component = self.components[component_name]
                if component.state not in [ComponentState.READY, ComponentState.RUNNING]:
                    raise Exception(f"Required component '{component_name}' not ready (state: {component.state.value})")
            
            self.logger.info(f"Startup phase '{phase.name}' completed successfully")
            return True
            
        except asyncio.TimeoutError:
            self.logger.error(f"Startup phase '{phase.name}' timed out after {phase.timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Startup phase '{phase.name}' failed: {e}")
            return False
    
    async def _startup_phase_configuration(self):
        """Startup phase 1: Configuration and Storage"""
        # Initialize storage
        if self.integration.storage:
            self._register_component(
                "storage",
                self.integration.storage,
                health_check=self.integration.storage.health_check,
                startup_function=self.integration.storage.initialize,
                shutdown_function=self.integration.storage.close
            )
            
            await self._start_component("storage")
    
    async def _startup_phase_core_services(self):
        """Startup phase 2: Core Services"""
        # Initialize logging engine
        if self.integration.logging_engine:
            self._register_component(
                "logging_engine",
                self.integration.logging_engine,
                startup_function=self.integration.logging_engine.initialize,
                shutdown_function=self.integration.logging_engine.stop
            )
            await self._start_component("logging_engine")
        
        # Initialize context manager
        if self.integration.context_manager:
            self._register_component(
                "context_manager",
                self.integration.context_manager,
                startup_function=self.integration.context_manager.initialize,
                shutdown_function=self.integration.context_manager.stop
            )
            await self._start_component("context_manager")
    
    async def _startup_phase_processing_engines(self):
        """Startup phase 3: Processing Engines"""
        # Initialize AI engine (optional)
        if self.integration.ai_engine:
            self._register_component(
                "ai_engine",
                self.integration.ai_engine,
                startup_function=self.integration.ai_engine.initialize,
                shutdown_function=self.integration.ai_engine.stop
            )
            
            try:
                await self._start_component("ai_engine")
            except Exception as e:
                self.logger.warning(f"AI engine initialization failed: {e} - continuing without AI")
        
        # Initialize security engine (required)
        if self.integration.security_engine:
            self._register_component(
                "security_engine",
                self.integration.security_engine,
                startup_function=self.integration.security_engine.initialize,
                shutdown_function=self.integration.security_engine.stop
            )
            await self._start_component("security_engine")
    
    async def _startup_phase_execution_engine(self):
        """Startup phase 4: Execution Engine"""
        # Initialize executor (optional)
        if self.integration.executor:
            self._register_component(
                "executor",
                self.integration.executor,
                startup_function=self.integration.executor.initialize,
                shutdown_function=self.integration.executor.stop
            )
            
            try:
                await self._start_component("executor")
            except Exception as e:
                self.logger.warning(f"Executor initialization failed: {e} - continuing in info-only mode")
    
    async def _startup_phase_mcp_server(self):
        """Startup phase 5: MCP Server"""
        # Initialize MCP server
        if self.integration.mcp_server:
            self._register_component(
                "mcp_server",
                self.integration.mcp_server,
                startup_function=self._start_mcp_server,
                shutdown_function=self.integration.mcp_server.shutdown
            )
            await self._start_component("mcp_server")
    
    async def _start_mcp_server(self):
        """Start MCP server with proper integration"""
        # Register tools and start server
        self.integration.mcp_server.register_tools()
        # Note: The actual server start is handled by the integration
    
    def _register_component(self, name: str, instance: Any, 
                           health_check: Optional[Callable] = None,
                           startup_function: Optional[Callable] = None,
                           shutdown_function: Optional[Callable] = None,
                           dependencies: Optional[List[str]] = None):
        """Register a component for management"""
        
        component = ComponentInfo(
            name=name,
            state=ComponentState.NOT_INITIALIZED,
            instance=instance,
            health_check=health_check,
            startup_function=startup_function,
            shutdown_function=shutdown_function,
            dependencies=dependencies or []
        )
        
        self.components[name] = component
        
        # Register with health monitor if health check available
        if health_check:
            self.health_monitor.register_component(
                name,
                health_check,
                self._recover_component
            )
        
        self.logger.debug(f"Registered component: {name}")
    
    async def _start_component(self, name: str):
        """Start a specific component"""
        if name not in self.components:
            raise Exception(f"Component '{name}' not registered")
        
        component = self.components[name]
        
        try:
            self.logger.debug(f"Starting component: {name}")
            component.state = ComponentState.INITIALIZING
            
            start_time = time.time()
            
            # Call startup function if available
            if component.startup_function:
                if asyncio.iscoroutinefunction(component.startup_function):
                    await component.startup_function()
                else:
                    component.startup_function()
            
            component.startup_time = time.time() - start_time
            component.state = ComponentState.RUNNING
            
            self.logger.info(f"Component '{name}' started successfully in {component.startup_time:.2f}s")
            
        except Exception as e:
            component.state = ComponentState.FAILED
            component.error_count += 1
            self.logger.error(f"Failed to start component '{name}': {e}")
            raise
    
    async def _recover_component(self, name: str) -> bool:
        """Attempt to recover a failed component"""
        if name not in self.components:
            return False
        
        component = self.components[name]
        
        try:
            self.logger.info(f"Attempting to recover component: {name}")
            
            # Stop component first if it's running
            if component.state in [ComponentState.RUNNING, ComponentState.DEGRADED]:
                await self._stop_component(name)
            
            # Restart component
            await self._start_component(name)
            
            self.logger.info(f"Component '{name}' recovered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to recover component '{name}': {e}")
            return False
    
    async def _stop_component(self, name: str):
        """Stop a specific component"""
        if name not in self.components:
            return
        
        component = self.components[name]
        
        try:
            self.logger.debug(f"Stopping component: {name}")
            component.state = ComponentState.STOPPING
            
            # Call shutdown function if available
            if component.shutdown_function:
                if asyncio.iscoroutinefunction(component.shutdown_function):
                    await component.shutdown_function()
                else:
                    component.shutdown_function()
            
            component.state = ComponentState.STOPPED
            self.logger.debug(f"Component '{name}' stopped")
            
        except Exception as e:
            component.state = ComponentState.FAILED
            self.logger.error(f"Error stopping component '{name}': {e}")
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all components"""
        try:
            await self.health_monitor.start_monitoring()
            self.logger.info("Health monitoring started")
        except Exception as e:
            self.logger.error(f"Failed to start health monitoring: {e}")
    
    async def shutdown(self):
        """Graceful system shutdown"""
        if self.shutdown_requested:
            return
        
        self.shutdown_requested = True
        self.logger.info("Initiating system shutdown...")
        
        try:
            self.state = SystemState.STOPPING
            
            # Stop health monitoring
            if self.health_monitor:
                await self.health_monitor.stop_monitoring()
            
            # Stop components in reverse order
            component_names = list(self.components.keys())
            for name in reversed(component_names):
                await self._stop_component(name)
            
            # Final cleanup
            if self.integration:
                await self.integration.shutdown()
            
            self.state = SystemState.STOPPED
            self.logger.info("System shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            self.logger.error(traceback.format_exc())
            self.state = SystemState.ERROR
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        component_status = {}
        
        for name, component in self.components.items():
            component_status[name] = {
                "state": component.state.value,
                "error_count": component.error_count,
                "startup_time": component.startup_time,
                "last_health_check": component.last_health_check.isoformat() if component.last_health_check else None
            }
            
            # Get health status if available
            if component.health_check:
                try:
                    if asyncio.iscoroutinefunction(component.health_check):
                        health_result = await component.health_check()
                    else:
                        health_result = component.health_check()
                    
                    component_status[name]["health"] = health_result
                except Exception as e:
                    component_status[name]["health"] = {"status": "error", "error": str(e)}
        
        return {
            "system_state": self.state.value,
            "startup_time": self.startup_time,
            "uptime": time.time() - self.startup_time if self.startup_time else 0,
            "components": component_status,
            "error_statistics": error_handler.get_error_statistics(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run health checks on all components"""
        health_results = {}
        
        for name, component in self.components.items():
            if component.health_check:
                try:
                    if asyncio.iscoroutinefunction(component.health_check):
                        result = await component.health_check()
                    else:
                        result = component.health_check()
                    
                    health_results[name] = result
                    component.last_health_check = datetime.now(timezone.utc)
                    
                except Exception as e:
                    health_results[name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    component.error_count += 1
            else:
                health_results[name] = {
                    "status": "no_health_check",
                    "message": "No health check available"
                }
        
        return health_results
    
    @property
    def is_running(self) -> bool:
        """Check if system is running"""
        return self.state in [SystemState.RUNNING, SystemState.DEGRADED]
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        return self.state == SystemState.RUNNING


# Main entry point function
async def main():
    """Main entry point for the AI PowerShell Assistant"""
    system = None
    
    try:
        # Create and start system
        system = SystemIntegration()
        
        startup_success = await system.startup()
        
        if not startup_success:
            print("System startup failed")
            return 1
        
        print(f"AI PowerShell Assistant started successfully")
        print(f"System state: {system.state.value}")
        
        # Keep running until shutdown requested
        while system.is_running and not system.shutdown_requested:
            await asyncio.sleep(1)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        return 0
    except Exception as e:
        print(f"System error: {e}")
        traceback.print_exc()
        return 1
    finally:
        if system:
            await system.shutdown()


if __name__ == "__main__":
    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)