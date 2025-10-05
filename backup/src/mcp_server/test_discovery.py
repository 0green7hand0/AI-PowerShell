"""Integration tests for MCP tool discovery and registration"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.discovery import ToolDiscoveryManager
from mcp_server.schemas import ToolDefinition, ToolCategory, ToolStatus


class TestToolDiscoveryManager:
    """Test cases for ToolDiscoveryManager"""
    
    @pytest.fixture
    def temp_registry_path(self):
        """Create temporary registry file path"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def discovery_manager(self, temp_registry_path):
        """Create discovery manager with temporary registry"""
        return ToolDiscoveryManager(registry_path=temp_registry_path)
    
    def test_initialization(self, discovery_manager):
        """Test discovery manager initialization"""
        assert discovery_manager.registry is not None
        assert len(discovery_manager.registry.tools) >= 3  # Built-in tools
        assert discovery_manager.tool_handlers == {}
        
        # Check built-in tools are registered
        builtin_tools = ["natural_language_to_powershell", "execute_powershell_command", "get_powershell_info"]
        for tool_name in builtin_tools:
            assert tool_name in discovery_manager.registry.tools
            tool = discovery_manager.registry.tools[tool_name]
            assert tool.status == ToolStatus.AVAILABLE
    
    def test_register_custom_tool(self, discovery_manager):
        """Test registering a custom tool"""
        custom_tool = ToolDefinition(
            name="custom_test_tool",
            description="A custom test tool",
            category=ToolCategory.UTILITY,
            version="1.0.0",
            status=ToolStatus.AVAILABLE,
            request_schema={"type": "object"},
            response_schema={"type": "object"}
        )
        
        # Register tool
        result = discovery_manager.register_tool(custom_tool)
        assert result is True
        
        # Verify registration
        assert "custom_test_tool" in discovery_manager.registry.tools
        registered_tool = discovery_manager.get_tool_definition("custom_test_tool")
        assert registered_tool is not None
        assert registered_tool.name == "custom_test_tool"
        assert registered_tool.category == ToolCategory.UTILITY
    
    def test_register_duplicate_tool(self, discovery_manager):
        """Test registering duplicate tool"""
        # Try to register built-in tool again
        nl_tool = discovery_manager.get_tool_definition("natural_language_to_powershell")
        result = discovery_manager.register_tool(nl_tool)
        assert result is False  # Should fail due to same version
    
    def test_register_tool_version_update(self, discovery_manager):
        """Test updating tool version"""
        # Get existing tool
        existing_tool = discovery_manager.get_tool_definition("natural_language_to_powershell")
        
        # Create updated version
        updated_tool = ToolDefinition(
            name="natural_language_to_powershell",
            description="Updated description",
            category=existing_tool.category,
            version="2.0.0",  # New version
            status=ToolStatus.AVAILABLE,
            request_schema=existing_tool.request_schema,
            response_schema=existing_tool.response_schema
        )
        
        # Register updated tool
        result = discovery_manager.register_tool(updated_tool)
        assert result is True
        
        # Verify update
        registered_tool = discovery_manager.get_tool_definition("natural_language_to_powershell")
        assert registered_tool.version == "2.0.0"
        assert registered_tool.description == "Updated description"
    
    def test_unregister_tool(self, discovery_manager):
        """Test unregistering a tool"""
        # Register a custom tool first
        custom_tool = ToolDefinition(
            name="temp_tool",
            description="Temporary tool",
            category=ToolCategory.UTILITY,
            request_schema={},
            response_schema={}
        )
        discovery_manager.register_tool(custom_tool)
        
        # Verify it's registered
        assert "temp_tool" in discovery_manager.registry.tools
        
        # Unregister it
        result = discovery_manager.unregister_tool("temp_tool")
        assert result is True
        
        # Verify it's removed
        assert "temp_tool" not in discovery_manager.registry.tools
        assert discovery_manager.get_tool_definition("temp_tool") is None
    
    def test_unregister_nonexistent_tool(self, discovery_manager):
        """Test unregistering non-existent tool"""
        result = discovery_manager.unregister_tool("nonexistent_tool")
        assert result is False
    
    def test_register_tool_handler(self, discovery_manager):
        """Test registering tool handler"""
        def mock_handler(request):
            return {"success": True}
        
        # Register handler for existing tool
        result = discovery_manager.register_tool_handler("natural_language_to_powershell", mock_handler)
        assert result is True
        
        # Verify handler is registered
        handler = discovery_manager.get_tool_handler("natural_language_to_powershell")
        assert handler is not None
        assert handler == mock_handler
    
    def test_register_handler_for_unknown_tool(self, discovery_manager):
        """Test registering handler for unknown tool"""
        def mock_handler(request):
            return {"success": True}
        
        result = discovery_manager.register_tool_handler("unknown_tool", mock_handler)
        assert result is False
    
    def test_get_available_tools(self, discovery_manager):
        """Test getting available tools"""
        available_tools = discovery_manager.get_available_tools()
        assert len(available_tools) >= 3  # At least built-in tools
        
        # All returned tools should be available
        for tool in available_tools:
            assert tool.status == ToolStatus.AVAILABLE
    
    def test_get_tools_by_category(self, discovery_manager):
        """Test getting tools by category"""
        # Get natural language tools
        nl_tools = discovery_manager.get_tools_by_category(ToolCategory.NATURAL_LANGUAGE)
        assert len(nl_tools) >= 1
        assert all(tool.category == ToolCategory.NATURAL_LANGUAGE for tool in nl_tools)
        
        # Get command execution tools
        exec_tools = discovery_manager.get_tools_by_category(ToolCategory.COMMAND_EXECUTION)
        assert len(exec_tools) >= 1
        assert all(tool.category == ToolCategory.COMMAND_EXECUTION for tool in exec_tools)
        
        # Get system info tools
        info_tools = discovery_manager.get_tools_by_category(ToolCategory.SYSTEM_INFO)
        assert len(info_tools) >= 1
        assert all(tool.category == ToolCategory.SYSTEM_INFO for tool in info_tools)
    
    def test_set_tool_status(self, discovery_manager):
        """Test setting tool status"""
        # Set tool to maintenance
        result = discovery_manager.set_tool_status("natural_language_to_powershell", ToolStatus.MAINTENANCE)
        assert result is True
        
        # Verify status change
        tool = discovery_manager.get_tool_definition("natural_language_to_powershell")
        assert tool.status == ToolStatus.MAINTENANCE
        
        # Verify it's not in available tools
        available_tools = discovery_manager.get_available_tools()
        available_names = [tool.name for tool in available_tools]
        assert "natural_language_to_powershell" not in available_names
    
    def test_set_status_for_unknown_tool(self, discovery_manager):
        """Test setting status for unknown tool"""
        result = discovery_manager.set_tool_status("unknown_tool", ToolStatus.DISABLED)
        assert result is False
    
    def test_validate_tool_request(self, discovery_manager):
        """Test tool request validation"""
        # Valid request
        request_data = {
            "input_text": "test command",
            "session_id": "test_session"
        }
        result = discovery_manager.validate_tool_request("natural_language_to_powershell", request_data)
        assert hasattr(result, 'input_text')  # Should be a valid request object
        assert result.input_text == "test command"
        
        # Invalid request
        invalid_request_data = {
            "input_text": "",  # Empty input
        }
        result = discovery_manager.validate_tool_request("natural_language_to_powershell", invalid_request_data)
        assert hasattr(result, 'error_code')  # Should be an error object
    
    def test_format_tool_response(self, discovery_manager):
        """Test tool response formatting"""
        response_data = {
            "success": True,
            "generated_command": "Get-Process",
            "confidence_score": 0.95
        }
        result = discovery_manager.format_tool_response("natural_language_to_powershell", response_data)
        assert hasattr(result, 'success')
        assert result.success is True
        assert result.generated_command == "Get-Process"
    
    def test_registry_persistence(self, temp_registry_path):
        """Test registry persistence to file"""
        # Create manager and register custom tool
        manager1 = ToolDiscoveryManager(registry_path=temp_registry_path)
        
        custom_tool = ToolDefinition(
            name="persistent_tool",
            description="A persistent tool",
            category=ToolCategory.UTILITY,
            request_schema={},
            response_schema={}
        )
        manager1.register_tool(custom_tool)
        
        # Create new manager with same registry path
        manager2 = ToolDiscoveryManager(registry_path=temp_registry_path)
        
        # Verify tool was loaded from file
        assert "persistent_tool" in manager2.registry.tools
        loaded_tool = manager2.get_tool_definition("persistent_tool")
        assert loaded_tool.name == "persistent_tool"
        assert loaded_tool.description == "A persistent tool"
    
    def test_discover_tools_from_directory(self, discovery_manager):
        """Test discovering tools from directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a tool definition file
            tool_data = {
                "name": "discovered_tool",
                "description": "A discovered tool",
                "category": "utility",
                "version": "1.0.0",
                "status": "available",
                "request_schema": {"type": "object"},
                "response_schema": {"type": "object"}
            }
            
            tool_file = Path(temp_dir) / "discovered_tool.tool.json"
            with open(tool_file, 'w') as f:
                json.dump(tool_data, f)
            
            # Discover tools
            discovered_count = discovery_manager.discover_tools([temp_dir])
            assert discovered_count == 1
            
            # Verify tool was registered
            assert "discovered_tool" in discovery_manager.registry.tools
            tool = discovery_manager.get_tool_definition("discovered_tool")
            assert tool.name == "discovered_tool"
            assert tool.description == "A discovered tool"
    
    def test_discover_tools_invalid_file(self, discovery_manager):
        """Test discovering tools with invalid file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid tool definition file
            invalid_file = Path(temp_dir) / "invalid_tool.tool.json"
            with open(invalid_file, 'w') as f:
                f.write("invalid json content")
            
            # Discover tools (should handle error gracefully)
            discovered_count = discovery_manager.discover_tools([temp_dir])
            assert discovered_count == 0
    
    def test_get_registry_info(self, discovery_manager):
        """Test getting registry information"""
        info = discovery_manager.get_registry_info()
        
        assert "version" in info
        assert "last_updated" in info
        assert "total_tools" in info
        assert "available_tools" in info
        assert "categories" in info
        assert "tools" in info
        
        assert info["total_tools"] >= 3  # At least built-in tools
        assert info["available_tools"] >= 3
        assert len(info["categories"]) >= 3  # At least 3 categories
        
        # Check tool details
        for tool_name, tool_info in info["tools"].items():
            assert "version" in tool_info
            assert "status" in tool_info
            assert "category" in tool_info
    
    def test_invalid_tool_registration(self, discovery_manager):
        """Test registering invalid tool"""
        from pydantic import ValidationError
        
        # Tool with missing required fields - should fail at creation time
        with pytest.raises(ValidationError):
            invalid_tool = ToolDefinition(
                name="",  # Empty name
                description="Invalid tool",
                category=ToolCategory.UTILITY,
                request_schema={},
                response_schema={}
            )
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_registry_save_error(self, mock_open, temp_registry_path):
        """Test handling registry save errors"""
        manager = ToolDiscoveryManager(registry_path=temp_registry_path)
        
        custom_tool = ToolDefinition(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.UTILITY,
            request_schema={},
            response_schema={}
        )
        
        # Should handle save error gracefully
        result = manager.register_tool(custom_tool)
        # Tool should still be registered in memory even if save fails
        assert "test_tool" in manager.registry.tools


if __name__ == "__main__":
    pytest.main([__file__])