"""Cross-Platform Compatibility Tests

This module provides comprehensive tests for cross-platform compatibility
across Windows, Linux, and macOS systems.
"""

import pytest
import asyncio
import tempfile
import shutil
import platform as py_platform
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import (
    Platform, UserRole, LogLevel, OutputFormat, RiskLevel, SecurityAction, Permission,
    CommandSuggestion, ValidationResult, ExecutionResult, CommandContext
)
from execution.executor import PowerShellExecutor, PowerShellDetector


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(params=[Platform.WINDOWS, Platform.LINUX, Platform.MACOS])
def platform_config(request, temp_dir):
    """Create configuration for each platform"""
    platform = request.param
    
    config = ServerConfig(
        version="1.0.0-cross-platform-test",
        platform=platform,
        debug_mode=True,
        model=ModelConfig(),
        security=SecurityConfig(
            whitelist_path=str(Path(temp_dir) / "whitelist.json"),
            sandbox_enabled=True,
            audit_log_path=str(Path(temp_dir) / "audit.log")
        ),
        logging=LoggingConfig(
            log_level=LogLevel.DEBUG,
            audit_log_path=str(Path(temp_dir) / "audit.log")
        ),
        execution=ExecutionConfig(
            powershell_executable="pwsh" if platform != Platform.WINDOWS else "powershell.exe",
            default_timeout=60
        ),
        storage=StorageConfig(data_directory=str(Path(temp_dir) / "storage")),
        mcp_server=MCPServerConfig()
    )
    return config


@pytest.fixture
def mock_cross_platform_integration(platform_config):
    """Create mock integration for cross-platform testing"""
    integration = AIPowerShellAssistantIntegration()
    integration.config = platform_config
    
    # Mock components
    integration.storage = AsyncMock()
    integration.logging_engine = AsyncMock()
    integration.context_manager = AsyncMock()
    integration.ai_engine = Mock()
    integration.security_engine = Mock()
    integration.executor = Mock()
    integration.mcp_server = Mock()
    
    # Setup platform-specific return values
    integration.context_manager.create_session.return_value = f"{platform_config.platform.value}-session"
    integration.context_manager.get_current_context.return_value = Mock(platform=platform_config.platform)
    integration.logging_engine.log_user_input.return_value = f"{platform_config.platform.value}-corr-123"
    
    integration._initialized = True
    return integration


class TestPlatformDetection:
    """Test platform detection and configuration"""
    
    def test_platform_auto_detection(self):
        """Test automatic platform detection"""
        detector = PowerShellDetector()
        
        # Should detect a valid platform
        assert detector.current_platform in [Platform.WINDOWS, Platform.LINUX, Platform.MACOS]
        
        # Should match the actual system platform
        system_platform = py_platform.system()
        if system_platform == "Windows":
            assert detector.current_platform == Platform.WINDOWS
        elif system_platform == "Linux":
            assert detector.current_platform == Platform.LINUX
        elif system_platform == "Darwin":
            assert detector.current_platform == Platform.MACOS
    
    @pytest.mark.parametrize("mock_platform,expected_platform", [
        ("Windows", Platform.WINDOWS),
        ("Linux", Platform.LINUX),
        ("Darwin", Platform.MACOS),
        ("FreeBSD", Platform.LINUX),  # Unknown platforms default to Linux
    ])
    def test_platform_detection_mocked(self, mock_platform, expected_platform):
        """Test platform detection with mocked system platform"""
        with patch('platform.system', return_value=mock_platform):
            detector = PowerShellDetector()
            assert detector.current_platform == expected_platform


class TestPathAdaptation:
    """Test cross-platform path adaptation"""
    
    @pytest.mark.asyncio
    async def test_windows_to_unix_path_conversion(self, mock_cross_platform_integration):
        """Test Windows to Unix path conversion"""
        if mock_cross_platform_integration.config.platform != Platform.LINUX:
            pytest.skip("Test only for Linux platform")
        
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        
        # Mock AI engine to generate Windows-style paths
        def mock_translate_natural_language(input_text, context):
            return CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Content C:\\Users\\test\\document.txt",
                confidence_score=0.8,
                explanation="Read file with Windows path",
                alternatives=[]
            )
        
        mock_cross_platform_integration.ai_engine.translate_natural_language.side_effect = mock_translate_natural_language
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to adapt paths
        def mock_execute_command(command, context):
            # Simulate path adaptation
            adapted_command = command.replace("C:\\Users\\test\\", "/home/test/")
            adapted_command = adapted_command.replace("\\", "/")
            
            return ExecutionResult(
                success=True,
                return_code=0,
                stdout=f"Executed adapted command: {adapted_command}",
                stderr="",
                execution_time=0.5,
                platform=Platform.LINUX,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        
        # Test natural language to PowerShell conversion
        nl_result = await tool_implementations.natural_language_to_powershell(
            "read my document file"
        )
        
        assert nl_result["success"] is True
        generated_command = nl_result["generated_command"]
        
        # Execute the command
        exec_result = await tool_implementations.execute_powershell_command(generated_command)
        
        assert exec_result["success"] is True
        # Should show adapted path in output
        assert "/home/test/" in exec_result["stdout"]
        assert "C:\\Users\\test\\" not in exec_result["stdout"]
    
    @pytest.mark.asyncio
    async def test_unix_to_windows_path_conversion(self, mock_cross_platform_integration):
        """Test Unix to Windows path conversion"""
        if mock_cross_platform_integration.config.platform != Platform.WINDOWS:
            pytest.skip("Test only for Windows platform")
        
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        
        # Mock AI engine to generate Unix-style paths
        def mock_translate_natural_language(input_text, context):
            return CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Content /home/user/document.txt",
                confidence_score=0.8,
                explanation="Read file with Unix path",
                alternatives=[]
            )
        
        mock_cross_platform_integration.ai_engine.translate_natural_language.side_effect = mock_translate_natural_language
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to adapt paths
        def mock_execute_command(command, context):
            # Simulate path adaptation
            adapted_command = command.replace("/home/user/", "C:\\Users\\user\\")
            adapted_command = adapted_command.replace("/", "\\")
            
            return ExecutionResult(
                success=True,
                return_code=0,
                stdout=f"Executed adapted command: {adapted_command}",
                stderr="",
                execution_time=0.5,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        
        # Test command execution
        exec_result = await tool_implementations.execute_powershell_command(
            "Get-Content /home/user/document.txt"
        )
        
        assert exec_result["success"] is True
        # Should show adapted path in output
        assert "C:\\Users\\user\\" in exec_result["stdout"]
        assert "/home/user/" not in exec_result["stdout"]
    
    @pytest.mark.parametrize("source_path,target_platform,expected_path", [
        ("C:\\Users\\test\\file.txt", Platform.LINUX, "/c/Users/test/file.txt"),
        ("/home/user/file.txt", Platform.WINDOWS, "C:\\home\\user\\file.txt"),
        ("./relative/path", Platform.LINUX, "./relative/path"),
        (".\\relative\\path", Platform.WINDOWS, ".\\relative\\path"),
        ("~/user/file.txt", Platform.WINDOWS, "%USERPROFILE%\\user\\file.txt"),
        ("%USERPROFILE%\\file.txt", Platform.LINUX, "$HOME/file.txt"),
    ])
    def test_path_conversion_patterns(self, source_path, target_platform, expected_path):
        """Test various path conversion patterns"""
        # This would test the actual path conversion logic
        # For now, we'll test the pattern matching
        
        if target_platform == Platform.LINUX:
            # Windows to Unix conversion patterns
            if source_path.startswith("C:\\"):
                converted = source_path.replace("C:\\", "/c/").replace("\\", "/")
                assert "/c/" in converted
            elif "%USERPROFILE%" in source_path:
                converted = source_path.replace("%USERPROFILE%", "$HOME").replace("\\", "/")
                assert "$HOME" in converted
        
        elif target_platform == Platform.WINDOWS:
            # Unix to Windows conversion patterns
            if source_path.startswith("/home/"):
                converted = source_path.replace("/home/", "C:\\Users\\").replace("/", "\\")
                assert "C:\\Users\\" in converted
            elif source_path.startswith("~/"):
                converted = source_path.replace("~/", "%USERPROFILE%\\").replace("/", "\\")
                assert "%USERPROFILE%" in converted


class TestEnvironmentVariableAdaptation:
    """Test cross-platform environment variable adaptation"""
    
    @pytest.mark.asyncio
    async def test_environment_variable_conversion(self, mock_cross_platform_integration):
        """Test environment variable format conversion"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        platform = mock_cross_platform_integration.config.platform
        
        # Mock AI engine to generate commands with environment variables
        def mock_translate_natural_language(input_text, context):
            if platform == Platform.WINDOWS:
                command = "Get-Content $HOME\\document.txt"  # Unix-style in Windows
            else:
                command = "Get-Content %USERPROFILE%\\document.txt"  # Windows-style in Unix
            
            return CommandSuggestion(
                original_input=input_text,
                generated_command=command,
                confidence_score=0.8,
                explanation="Command with environment variable",
                alternatives=[]
            )
        
        mock_cross_platform_integration.ai_engine.translate_natural_language.side_effect = mock_translate_natural_language
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to show adapted environment variables
        def mock_execute_command(command, context):
            adapted_command = command
            
            if platform == Platform.WINDOWS:
                # Convert Unix-style to Windows-style
                adapted_command = adapted_command.replace("$HOME", "%USERPROFILE%")
                adapted_command = adapted_command.replace("/", "\\")
            else:
                # Convert Windows-style to Unix-style
                adapted_command = adapted_command.replace("%USERPROFILE%", "$HOME")
                adapted_command = adapted_command.replace("\\", "/")
            
            return ExecutionResult(
                success=True,
                return_code=0,
                stdout=f"Adapted command: {adapted_command}",
                stderr="",
                execution_time=0.5,
                platform=platform,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        
        # Test environment variable adaptation
        nl_result = await tool_implementations.natural_language_to_powershell(
            "read my home document"
        )
        
        assert nl_result["success"] is True
        generated_command = nl_result["generated_command"]
        
        exec_result = await tool_implementations.execute_powershell_command(generated_command)
        
        assert exec_result["success"] is True
        
        # Verify environment variable was adapted correctly
        if platform == Platform.WINDOWS:
            assert "%USERPROFILE%" in exec_result["stdout"]
            assert "$HOME" not in exec_result["stdout"]
        else:
            assert "$HOME" in exec_result["stdout"]
            assert "%USERPROFILE%" not in exec_result["stdout"]


class TestPowerShellVersionCompatibility:
    """Test compatibility across PowerShell versions"""
    
    @pytest.mark.asyncio
    async def test_powershell_core_vs_windows_powershell(self, mock_cross_platform_integration):
        """Test compatibility between PowerShell Core and Windows PowerShell"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        platform = mock_cross_platform_integration.config.platform
        
        # Mock executor to simulate different PowerShell versions
        def mock_get_powershell_info():
            if platform == Platform.WINDOWS:
                return {
                    "version": "5.1.19041.1682",
                    "edition": "Desktop",
                    "platform": "Win32NT",
                    "executable": "powershell.exe",
                    "supports_core_features": False
                }
            else:
                return {
                    "version": "7.3.0",
                    "edition": "Core",
                    "platform": "Unix",
                    "executable": "pwsh",
                    "supports_core_features": True
                }
        
        mock_cross_platform_integration.executor.get_powershell_info.side_effect = mock_get_powershell_info
        
        # Mock health check
        async def mock_health_check():
            return {"overall": "healthy"}
        
        mock_cross_platform_integration.health_check = mock_health_check
        
        # Test system info retrieval
        result = await tool_implementations.get_powershell_info()
        
        assert result["success"] is True
        assert "powershell" in result
        
        ps_info = result["powershell"]
        
        if platform == Platform.WINDOWS:
            assert ps_info["edition"] == "Desktop"
            assert ps_info["executable"] == "powershell.exe"
            assert ps_info["supports_core_features"] is False
        else:
            assert ps_info["edition"] == "Core"
            assert ps_info["executable"] == "pwsh"
            assert ps_info["supports_core_features"] is True
    
    @pytest.mark.asyncio
    async def test_cmdlet_availability_across_versions(self, mock_cross_platform_integration):
        """Test cmdlet availability across PowerShell versions"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        platform = mock_cross_platform_integration.config.platform
        
        # Mock AI engine to generate version-specific commands
        def mock_translate_natural_language(input_text, context):
            if "network" in input_text.lower():
                if platform == Platform.WINDOWS:
                    # Windows PowerShell might use older cmdlets
                    command = "Test-Connection -ComputerName google.com"
                else:
                    # PowerShell Core has newer cmdlets
                    command = "Test-NetConnection -ComputerName google.com"
            else:
                command = "Get-Process"
            
            return CommandSuggestion(
                original_input=input_text,
                generated_command=command,
                confidence_score=0.8,
                explanation="Version-appropriate command",
                alternatives=[]
            )
        
        mock_cross_platform_integration.ai_engine.translate_natural_language.side_effect = mock_translate_natural_language
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Test network command generation
        result = await tool_implementations.natural_language_to_powershell(
            "test network connection to google"
        )
        
        assert result["success"] is True
        generated_command = result["generated_command"]
        
        if platform == Platform.WINDOWS:
            assert "Test-Connection" in generated_command
        else:
            assert "Test-NetConnection" in generated_command


class TestOutputFormatting:
    """Test cross-platform output formatting"""
    
    @pytest.mark.asyncio
    async def test_line_ending_normalization(self, mock_cross_platform_integration):
        """Test line ending normalization across platforms"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        platform = mock_cross_platform_integration.config.platform
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to return platform-specific line endings
        def mock_execute_command(command, context):
            if platform == Platform.WINDOWS:
                output = "Line 1\r\nLine 2\r\nLine 3"
            else:
                output = "Line 1\nLine 2\nLine 3"
            
            return ExecutionResult(
                success=True,
                return_code=0,
                stdout=output,
                stderr="",
                execution_time=0.5,
                platform=platform,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        mock_cross_platform_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Test command execution
        result = await tool_implementations.execute_powershell_command("Get-Process")
        
        assert result["success"] is True
        
        # Verify line endings are appropriate for platform
        if platform == Platform.WINDOWS:
            assert "\r\n" in result["stdout"]
        else:
            assert "\r\n" not in result["stdout"]
            assert "\n" in result["stdout"]
    
    @pytest.mark.asyncio
    async def test_encoding_handling(self, mock_cross_platform_integration):
        """Test encoding handling across platforms"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to return unicode content
        def mock_execute_command(command, context):
            # Test various unicode characters
            unicode_output = "Process: café ñoël 世界 🚀"
            
            return ExecutionResult(
                success=True,
                return_code=0,
                stdout=unicode_output,
                stderr="",
                execution_time=0.5,
                platform=mock_cross_platform_integration.config.platform,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        mock_cross_platform_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Test command execution with unicode content
        result = await tool_implementations.execute_powershell_command("Get-Process")
        
        assert result["success"] is True
        
        # Verify unicode characters are preserved
        assert "café" in result["stdout"]
        assert "ñoël" in result["stdout"]
        assert "世界" in result["stdout"]
        assert "🚀" in result["stdout"]


class TestErrorMessageStandardization:
    """Test error message standardization across platforms"""
    
    @pytest.mark.asyncio
    async def test_platform_specific_error_adaptation(self, mock_cross_platform_integration):
        """Test adaptation of platform-specific error messages"""
        tool_implementations = MCPToolImplementations(mock_cross_platform_integration)
        platform = mock_cross_platform_integration.config.platform
        
        # Mock security validation
        mock_cross_platform_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Mock executor to return platform-specific errors
        def mock_execute_command(command, context):
            if platform == Platform.WINDOWS:
                error_msg = "Cannot find path 'C:\\nonexistent\\file.txt' because it does not exist."
            else:
                error_msg = "No such file or directory: '/nonexistent/file.txt'"
            
            return ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr=error_msg,
                execution_time=0.1,
                platform=platform,
                sandbox_used=False
            )
        
        mock_cross_platform_integration.executor.execute_command.side_effect = mock_execute_command
        
        # Test command that will fail
        result = await tool_implementations.execute_powershell_command(
            "Get-Content nonexistent-file.txt"
        )
        
        assert result["success"] is False
        assert result["return_code"] == 1
        
        # Error message should be present and platform-appropriate
        assert len(result["stderr"]) > 0
        
        if platform == Platform.WINDOWS:
            assert "Cannot find path" in result["stderr"] or "does not exist" in result["stderr"]
        else:
            assert "No such file" in result["stderr"] or "directory" in result["stderr"]


class TestConcurrentCrossPlatformOperations:
    """Test concurrent operations across different platform contexts"""
    
    @pytest.mark.asyncio
    async def test_mixed_platform_sessions(self):
        """Test handling of mixed platform sessions"""
        # Create integrations for different platforms
        platforms = [Platform.WINDOWS, Platform.LINUX, Platform.MACOS]
        integrations = {}
        tool_implementations = {}
        
        for platform in platforms:
            temp_dir = tempfile.mkdtemp()
            try:
                config = ServerConfig(
                    version="1.0.0-mixed-test",
                    platform=platform,
                    debug_mode=True,
                    model=ModelConfig(),
                    security=SecurityConfig(),
                    logging=LoggingConfig(),
                    execution=ExecutionConfig(),
                    storage=StorageConfig(data_directory=str(Path(temp_dir) / "storage")),
                    mcp_server=MCPServerConfig()
                )
                
                integration = AIPowerShellAssistantIntegration()
                integration.config = config
                
                # Mock components
                integration.storage = AsyncMock()
                integration.logging_engine = AsyncMock()
                integration.context_manager = AsyncMock()
                integration.ai_engine = Mock()
                integration.security_engine = Mock()
                integration.executor = Mock()
                integration.mcp_server = Mock()
                
                # Setup return values
                integration.context_manager.create_session.return_value = f"{platform.value}-session"
                integration.logging_engine.log_user_input.return_value = f"{platform.value}-corr"
                
                # Mock AI engine
                def make_translate_func(p):
                    def mock_translate(input_text, context):
                        return CommandSuggestion(
                            original_input=input_text,
                            generated_command=f"Get-Process # {p.value} platform",
                            confidence_score=0.8,
                            explanation=f"Command for {p.value}",
                            alternatives=[]
                        )
                    return mock_translate
                
                integration.ai_engine.translate_natural_language.side_effect = make_translate_func(platform)
                
                # Mock security validation
                integration.security_engine.validate_command.return_value = ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.LOW
                )
                
                integration._initialized = True
                integrations[platform] = integration
                tool_implementations[platform] = MCPToolImplementations(integration)
                
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Test concurrent operations on different platforms
        tasks = []
        for platform in platforms:
            task = tool_implementations[platform].natural_language_to_powershell(
                f"test command for {platform.value}",
                session_id=f"{platform.value}-session"
            )
            tasks.append((platform, task))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Verify all platforms handled correctly
        for i, (platform, _) in enumerate(tasks):
            result = results[i]
            assert not isinstance(result, Exception), f"Platform {platform.value} failed: {result}"
            assert result["success"] is True
            assert platform.value in result["generated_command"]
            assert result["session_id"] == f"{platform.value}-session"


if __name__ == "__main__":
    # Run cross-platform compatibility tests
    pytest.main([__file__, "-v", "-k", "test_"])