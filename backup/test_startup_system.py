"""Tests for System Integration and Startup Logic

This module tests the comprehensive startup system, health checks,
and graceful shutdown procedures.
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

from startup_system import (
    SystemIntegration, SystemState, ComponentState, StartupPhase,
    ComponentInfo
)
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import Platform, LogLevel


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


@pytest.fixture
def mock_integration():
    """Create mock integration for testing"""
    integration = Mock()
    
    # Mock components
    integration.storage = AsyncMock()
    integration.logging_engine = AsyncMock()
    integration.context_manager = AsyncMock()
    integration.ai_engine = AsyncMock()
    integration.security_engine = AsyncMock()
    integration.executor = AsyncMock()
    integration.mcp_server = Mock()
    
    # Mock health checks
    integration.storage.health_check = AsyncMock(return_value={"status": "healthy"})
    integration.logging_engine.health_check = AsyncMock(return_value={"status": "healthy"})
    integration.context_manager.health_check = AsyncMock(return_value={"status": "healthy"})
    integration.ai_engine.health_check = AsyncMock(return_value={"status": "healthy"})
    integration.security_engine.health_check = AsyncMock(return_value={"status": "healthy"})
    integration.executor.health_check = AsyncMock(return_value={"status": "healthy"})
    
    # Mock startup/shutdown functions
    integration.storage.initialize = AsyncMock()
    integration.storage.close = AsyncMock()
    integration.logging_engine.initialize = AsyncMock()
    integration.logging_engine.stop = AsyncMock()
    integration.context_manager.initialize = AsyncMock()
    integration.context_manager.stop = AsyncMock()
    integration.ai_engine.initialize = AsyncMock()
    integration.ai_engine.stop = AsyncMock()
    integration.security_engine.initialize = AsyncMock()
    integration.security_engine.stop = AsyncMock()
    integration.executor.initialize = AsyncMock()
    integration.executor.stop = AsyncMock()
    integration.mcp_server.register_tools = Mock()
    integration.mcp_server.shutdown = Mock()
    
    return integration


class TestSystemIntegration:
    """Test system integration functionality"""
    
    @pytest.mark.asyncio
    async def test_system_initialization(self):
        """Test system initialization"""
        system = SystemIntegration()
        
        assert system.state == SystemState.INITIALIZING
        assert len(system.startup_phases) > 0
        assert system.components == {}
        assert not system.shutdown_requested
    
    @pytest.mark.asyncio
    async def test_component_registration(self):
        """Test component registration"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_health_check = AsyncMock(return_value={"status": "healthy"})
        mock_startup = AsyncMock()
        mock_shutdown = AsyncMock()
        
        system._register_component(
            "test_component",
            mock_component,
            health_check=mock_health_check,
            startup_function=mock_startup,
            shutdown_function=mock_shutdown
        )
        
        assert "test_component" in system.components
        component = system.components["test_component"]
        assert component.name == "test_component"
        assert component.state == ComponentState.NOT_INITIALIZED
        assert component.instance == mock_component
        assert component.health_check == mock_health_check
        assert component.startup_function == mock_startup
        assert component.shutdown_function == mock_shutdown
    
    @pytest.mark.asyncio
    async def test_component_startup(self):
        """Test component startup"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_startup = AsyncMock()
        
        system._register_component(
            "test_component",
            mock_component,
            startup_function=mock_startup
        )
        
        await system._start_component("test_component")
        
        component = system.components["test_component"]
        assert component.state == ComponentState.RUNNING
        assert component.startup_time is not None
        mock_startup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_component_startup_failure(self):
        """Test component startup failure handling"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_startup = AsyncMock(side_effect=Exception("Startup failed"))
        
        system._register_component(
            "test_component",
            mock_component,
            startup_function=mock_startup
        )
        
        with pytest.raises(Exception, match="Startup failed"):
            await system._start_component("test_component")
        
        component = system.components["test_component"]
        assert component.state == ComponentState.FAILED
        assert component.error_count == 1
    
    @pytest.mark.asyncio
    async def test_component_shutdown(self):
        """Test component shutdown"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_shutdown = AsyncMock()
        
        system._register_component(
            "test_component",
            mock_component,
            shutdown_function=mock_shutdown
        )
        
        # Set component to running state
        system.components["test_component"].state = ComponentState.RUNNING
        
        await system._stop_component("test_component")
        
        component = system.components["test_component"]
        assert component.state == ComponentState.STOPPED
        mock_shutdown.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_startup_phase_execution(self):
        """Test startup phase execution"""
        system = SystemIntegration()
        
        # Mock a simple startup function
        startup_called = False
        
        async def mock_startup():
            nonlocal startup_called
            startup_called = True
        
        phase = StartupPhase(
            name="test_phase",
            description="Test phase",
            required_components=[],
            optional_components=[],
            startup_function=mock_startup,
            timeout=5
        )
        
        result = await system._execute_startup_phase(phase)
        
        assert result is True
        assert startup_called is True
    
    @pytest.mark.asyncio
    async def test_startup_phase_timeout(self):
        """Test startup phase timeout handling"""
        system = SystemIntegration()
        
        async def slow_startup():
            await asyncio.sleep(10)  # Longer than timeout
        
        phase = StartupPhase(
            name="slow_phase",
            description="Slow phase",
            required_components=[],
            optional_components=[],
            startup_function=slow_startup,
            timeout=1  # Short timeout
        )
        
        result = await system._execute_startup_phase(phase)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self):
        """Test health monitoring functionality"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_health_check = AsyncMock(return_value={"status": "healthy"})
        
        system._register_component(
            "test_component",
            mock_component,
            health_check=mock_health_check
        )
        
        # Start health monitoring
        await system._start_health_monitoring()
        
        # Run health checks
        health_results = await system.run_health_checks()
        
        assert "test_component" in health_results
        assert health_results["test_component"]["status"] == "healthy"
        
        # Stop health monitoring
        await system.health_monitor.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_component_recovery(self):
        """Test component recovery functionality"""
        system = SystemIntegration()
        
        mock_component = Mock()
        mock_startup = AsyncMock()
        mock_shutdown = AsyncMock()
        
        system._register_component(
            "test_component",
            mock_component,
            startup_function=mock_startup,
            shutdown_function=mock_shutdown
        )
        
        # Set component to failed state
        system.components["test_component"].state = ComponentState.FAILED
        
        # Attempt recovery
        result = await system._recover_component("test_component")
        
        assert result is True
        assert system.components["test_component"].state == ComponentState.RUNNING
        mock_shutdown.assert_called_once()
        mock_startup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_system_status(self):
        """Test system status reporting"""
        system = SystemIntegration()
        system.state = SystemState.RUNNING
        system.startup_time = 5.0
        
        mock_component = Mock()
        mock_health_check = AsyncMock(return_value={"status": "healthy"})
        
        system._register_component(
            "test_component",
            mock_component,
            health_check=mock_health_check
        )
        
        system.components["test_component"].state = ComponentState.RUNNING
        system.components["test_component"].startup_time = 2.0
        
        status = await system.get_system_status()
        
        assert status["system_state"] == "running"
        assert status["startup_time"] == 5.0
        assert "components" in status
        assert "test_component" in status["components"]
        assert status["components"]["test_component"]["state"] == "running"
        assert status["components"]["test_component"]["startup_time"] == 2.0
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Test graceful system shutdown"""
        system = SystemIntegration()
        
        # Add mock components
        mock_component1 = Mock()
        mock_component2 = Mock()
        mock_shutdown1 = AsyncMock()
        mock_shutdown2 = AsyncMock()
        
        system._register_component("component1", mock_component1, shutdown_function=mock_shutdown1)
        system._register_component("component2", mock_component2, shutdown_function=mock_shutdown2)
        
        # Set components to running state
        system.components["component1"].state = ComponentState.RUNNING
        system.components["component2"].state = ComponentState.RUNNING
        
        # Mock integration
        system.integration = AsyncMock()
        
        await system.shutdown()
        
        assert system.state == SystemState.STOPPED
        assert system.shutdown_requested is True
        
        # Verify components were shut down
        mock_shutdown1.assert_called_once()
        mock_shutdown2.assert_called_once()
        system.integration.shutdown.assert_called_once()


class TestStartupPhases:
    """Test startup phase functionality"""
    
    @pytest.mark.asyncio
    async def test_startup_phases_order(self):
        """Test that startup phases are in correct order"""
        system = SystemIntegration()
        
        phase_names = [phase.name for phase in system.startup_phases]
        
        expected_order = [
            "configuration",
            "core_services", 
            "processing_engines",
            "execution_engine",
            "mcp_server"
        ]
        
        assert phase_names == expected_order
    
    @pytest.mark.asyncio
    async def test_critical_vs_optional_phases(self):
        """Test critical vs optional phase handling"""
        system = SystemIntegration()
        
        # Find critical and optional phases
        critical_phases = [p for p in system.startup_phases if p.critical]
        optional_phases = [p for p in system.startup_phases if not p.critical]
        
        assert len(critical_phases) > 0
        assert len(optional_phases) > 0
        
        # Configuration and MCP server should be critical
        critical_names = [p.name for p in critical_phases]
        assert "configuration" in critical_names
        assert "mcp_server" in critical_names
        
        # Processing engines should be optional (for degraded mode)
        optional_names = [p.name for p in optional_phases]
        assert "processing_engines" in optional_names


class TestIntegrationScenarios:
    """Test integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_successful_startup_sequence(self, mock_integration):
        """Test successful complete startup sequence"""
        with patch('startup_system.AIPowerShellAssistantIntegration', return_value=mock_integration):
            system = SystemIntegration()
            
            # Mock the startup phases to avoid actual component initialization
            async def mock_config_phase():
                system._register_component("storage", mock_integration.storage)
                system.components["storage"].state = ComponentState.RUNNING
            
            async def mock_core_phase():
                system._register_component("logging_engine", mock_integration.logging_engine)
                system._register_component("context_manager", mock_integration.context_manager)
                system.components["logging_engine"].state = ComponentState.RUNNING
                system.components["context_manager"].state = ComponentState.RUNNING
            
            async def mock_processing_phase():
                system._register_component("security_engine", mock_integration.security_engine)
                system.components["security_engine"].state = ComponentState.RUNNING
            
            async def mock_execution_phase():
                pass  # Optional phase
            
            async def mock_mcp_phase():
                system._register_component("mcp_server", mock_integration.mcp_server)
                system.components["mcp_server"].state = ComponentState.RUNNING
            
            # Replace startup phase functions
            system.startup_phases[0].startup_function = mock_config_phase
            system.startup_phases[1].startup_function = mock_core_phase
            system.startup_phases[2].startup_function = mock_processing_phase
            system.startup_phases[3].startup_function = mock_execution_phase
            system.startup_phases[4].startup_function = mock_mcp_phase
            
            result = await system.startup()
            
            assert result is True
            assert system.state in [SystemState.RUNNING, SystemState.DEGRADED]
            assert system.startup_time is not None
    
    @pytest.mark.asyncio
    async def test_degraded_mode_startup(self, mock_integration):
        """Test startup in degraded mode when optional components fail"""
        with patch('startup_system.AIPowerShellAssistantIntegration', return_value=mock_integration):
            system = SystemIntegration()
            
            # Mock startup phases with some failures
            async def mock_config_phase():
                system._register_component("storage", mock_integration.storage)
                system.components["storage"].state = ComponentState.RUNNING
            
            async def mock_core_phase():
                system._register_component("logging_engine", mock_integration.logging_engine)
                system._register_component("context_manager", mock_integration.context_manager)
                system.components["logging_engine"].state = ComponentState.RUNNING
                system.components["context_manager"].state = ComponentState.RUNNING
            
            async def mock_processing_phase():
                # Fail AI engine (optional), succeed security engine (required)
                system._register_component("security_engine", mock_integration.security_engine)
                system.components["security_engine"].state = ComponentState.RUNNING
                # AI engine fails - this should not prevent startup
            
            async def mock_execution_phase():
                # Executor fails - this should not prevent startup (optional)
                raise Exception("Executor failed")
            
            async def mock_mcp_phase():
                system._register_component("mcp_server", mock_integration.mcp_server)
                system.components["mcp_server"].state = ComponentState.RUNNING
            
            # Replace startup phase functions
            system.startup_phases[0].startup_function = mock_config_phase
            system.startup_phases[1].startup_function = mock_core_phase
            system.startup_phases[2].startup_function = mock_processing_phase
            system.startup_phases[3].startup_function = mock_execution_phase
            system.startup_phases[4].startup_function = mock_mcp_phase
            
            result = await system.startup()
            
            assert result is True
            assert system.state == SystemState.DEGRADED  # Should be degraded due to failures
    
    @pytest.mark.asyncio
    async def test_critical_failure_startup(self, mock_integration):
        """Test startup failure when critical component fails"""
        with patch('startup_system.AIPowerShellAssistantIntegration', return_value=mock_integration):
            system = SystemIntegration()
            
            # Mock startup phases with critical failure
            async def mock_config_phase():
                raise Exception("Critical storage failure")
            
            # Replace first (critical) startup phase function
            system.startup_phases[0].startup_function = mock_config_phase
            
            result = await system.startup()
            
            assert result is False
            assert system.state == SystemState.ERROR


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])