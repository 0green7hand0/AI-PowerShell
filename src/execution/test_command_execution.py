"""Unit tests for PowerShell command execution functionality"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.executor import PowerShellExecutor, PowerShellDetector, PowerShellInfo, PowerShellVersion
from interfaces.base import Platform, CommandContext, ExecutionResult, OutputFormat, UserRole
from config.models import ExecutionConfig


class TestCommandExecution(unittest.TestCase):
    """Test PowerShell command execution functionality"""
    
    def setUp(self):
        self.config = ExecutionConfig()
        self.config.powershell_executable = ""  # Prevent auto-detection
        self.config.default_timeout = 30
        self.config.max_output_size = 1024
        
        # Create mock detector with available PowerShell
        self.mock_detector = Mock()
        self.mock_info = PowerShellInfo(
            version="7.3.0",
            edition="Core",
            executable_path="/usr/bin/pwsh",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=Platform.LINUX,
            is_available=True,
            supports_core_features=True,
            architecture="x64"
        )
        self.mock_detector.detect_powershell.return_value = self.mock_info
        self.mock_detector.current_platform = Platform.LINUX
        
        self.executor = PowerShellExecutor(self.config, detector=self.mock_detector)
        
        # Create test context
        self.context = CommandContext(
            current_directory="/tmp",
            environment_variables={"TEST_VAR": "test_value"},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
    
    @patch('subprocess.run')
    def test_execute_command_success(self, mock_run):
        """Test successful command execution"""
        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Process output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.executor.execute_command("Get-Process", self.context)
        
        self.assertTrue(result.success)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout, "Process output")
        self.assertEqual(result.stderr, "")
        self.assertGreater(result.execution_time, 0)
        self.assertEqual(result.platform, Platform.LINUX)
        self.assertFalse(result.sandbox_used)
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        
        expected_command = [
            "/usr/bin/pwsh",
            "-NoProfile",
            "-NonInteractive", 
            "-NoLogo",
            "-Command",
            "Get-Process"
        ]
        self.assertEqual(args[0], expected_command)
        self.assertEqual(kwargs['cwd'], "/tmp")
        self.assertIn('TEST_VAR', kwargs['env'])
        self.assertEqual(kwargs['env']['TEST_VAR'], "test_value")
        self.assertTrue(kwargs['capture_output'])
        self.assertTrue(kwargs['text'])
        self.assertEqual(kwargs['encoding'], 'utf-8')
        self.assertEqual(kwargs['errors'], 'replace')
        self.assertEqual(kwargs['timeout'], 30)
    
    @patch('subprocess.run')
    def test_execute_command_failure(self, mock_run):
        """Test command execution failure"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result
        
        result = self.executor.execute_command("Invalid-Command", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Command failed")
        self.assertGreater(result.execution_time, 0)
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command execution timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired('pwsh', 30)
        
        result = self.executor.execute_command("Start-Sleep 60", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, -1)
        self.assertEqual(result.stdout, "")
        self.assertIn("timed out", result.stderr)
        self.assertGreater(result.execution_time, 0)
    
    @patch('subprocess.run')
    def test_execute_command_exception(self, mock_run):
        """Test command execution with unexpected exception"""
        mock_run.side_effect = OSError("File not found")
        
        result = self.executor.execute_command("Get-Process", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, -1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Unexpected error", result.stderr)
        self.assertIn("File not found", result.stderr)
    
    def test_execute_command_powershell_not_available(self):
        """Test command execution when PowerShell is not available"""
        # Create executor with unavailable PowerShell
        mock_detector = Mock()
        mock_info = PowerShellInfo(
            version="",
            edition="",
            executable_path="",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=Platform.LINUX,
            is_available=False,
            supports_core_features=False,
            architecture=""
        )
        mock_detector.detect_powershell.return_value = mock_info
        mock_detector.current_platform = Platform.LINUX
        
        executor = PowerShellExecutor(self.config, detector=mock_detector)
        result = executor.execute_command("Get-Process", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, -1)
        self.assertIn("PowerShell is not available", result.stderr)
    
    def test_prepare_command_powershell_core(self):
        """Test command preparation for PowerShell Core"""
        command = "Get-Process"
        prepared = self.executor._prepare_command(command, self.context)
        
        expected = [
            "/usr/bin/pwsh",
            "-NoProfile",
            "-NonInteractive",
            "-NoLogo", 
            "-Command",
            "Get-Process"
        ]
        self.assertEqual(prepared, expected)
    
    def test_prepare_command_windows_powershell(self):
        """Test command preparation for Windows PowerShell"""
        # Update executor to use Windows PowerShell
        self.executor.powershell_info = PowerShellInfo(
            version="5.1.19041.1682",
            edition="Desktop",
            executable_path="powershell.exe",
            version_type=PowerShellVersion.WINDOWS_POWERSHELL,
            platform=Platform.WINDOWS,
            is_available=True,
            supports_core_features=False,
            architecture="AMD64"
        )
        self.executor.detector.current_platform = Platform.WINDOWS
        
        command = "Get-Process"
        prepared = self.executor._prepare_command(command, self.context)
        
        expected = [
            "powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-NoProfile",
            "-NonInteractive",
            "-NoLogo",
            "-Command",
            "Get-Process"
        ]
        self.assertEqual(prepared, expected)
    
    def test_prepare_environment(self):
        """Test environment preparation"""
        self.config.environment_variables = {"CONFIG_VAR": "config_value"}
        
        env = self.executor._prepare_environment(self.context)
        
        # Should include context variables
        self.assertEqual(env["TEST_VAR"], "test_value")
        
        # Should include config variables
        self.assertEqual(env["CONFIG_VAR"], "config_value")
        
        # Should include UTF-8 encoding
        self.assertEqual(env["PYTHONIOENCODING"], "utf-8")
        
        # Should include original environment
        self.assertIn("PATH", env)  # PATH should be preserved from os.environ
    
    def test_prepare_environment_windows(self):
        """Test environment preparation on Windows"""
        self.executor.detector.current_platform = Platform.WINDOWS
        
        env = self.executor._prepare_environment(self.context)
        
        # Should disable PowerShell telemetry on Windows
        self.assertEqual(env["POWERSHELL_TELEMETRY_OPTOUT"], "1")
    
    def test_truncate_output_normal(self):
        """Test output truncation with normal size"""
        output = "Normal output"
        truncated = self.executor._truncate_output(output)
        
        self.assertEqual(truncated, output)
    
    def test_truncate_output_large(self):
        """Test output truncation with large output"""
        # Create output larger than max_output_size
        large_output = "x" * (self.config.max_output_size + 100)
        truncated = self.executor._truncate_output(large_output)
        
        self.assertLess(len(truncated.encode('utf-8')), self.config.max_output_size + 200)
        self.assertIn("Output truncated", truncated)


class TestOutputFormatting(unittest.TestCase):
    """Test output formatting functionality"""
    
    def setUp(self):
        self.config = ExecutionConfig()
        self.config.powershell_executable = ""
        
        mock_detector = Mock()
        mock_info = PowerShellInfo(
            version="7.3.0",
            edition="Core", 
            executable_path="/usr/bin/pwsh",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=Platform.LINUX,
            is_available=True,
            supports_core_features=True,
            architecture="x64"
        )
        mock_detector.detect_powershell.return_value = mock_info
        
        self.executor = PowerShellExecutor(self.config, detector=mock_detector)
    
    def test_format_output_raw(self):
        """Test raw output formatting"""
        output = "Raw output text"
        formatted = self.executor.format_output(output, OutputFormat.RAW)
        
        self.assertEqual(formatted, output)
    
    def test_format_output_json_valid(self):
        """Test JSON output formatting with valid JSON"""
        json_output = '{"name": "test", "value": 123}'
        formatted = self.executor.format_output(json_output, OutputFormat.JSON)
        
        # Should be pretty-printed JSON
        self.assertIn('"name": "test"', formatted)
        self.assertIn('"value": 123', formatted)
        # Should be indented
        self.assertIn('  ', formatted)
    
    def test_format_output_json_invalid(self):
        """Test JSON output formatting with invalid JSON"""
        text_output = "This is not JSON"
        formatted = self.executor.format_output(text_output, OutputFormat.JSON)
        
        # Should wrap in JSON structure
        parsed = json.loads(formatted)
        self.assertEqual(parsed["output"], text_output)
        self.assertEqual(parsed["format"], "text")
        self.assertIn("timestamp", parsed)
    
    def test_format_output_empty(self):
        """Test formatting empty output"""
        formatted = self.executor.format_output("", OutputFormat.JSON)
        self.assertEqual(formatted, "")
        
        formatted = self.executor.format_output("   ", OutputFormat.RAW)
        self.assertEqual(formatted, "")
    
    def test_format_output_table_simple(self):
        """Test table formatting with simple tabular data"""
        table_output = "Name\tPID\tCPU\nprocess1\t1234\t50\nprocess2\t5678\t25"
        formatted = self.executor.format_output(table_output, OutputFormat.TABLE)
        
        # Should format as proper table
        lines = formatted.split('\n')
        self.assertGreater(len(lines), 2)  # Header + separator + data
        self.assertIn('|', lines[0])  # Should have column separators
        self.assertIn('-', lines[1])  # Should have separator line
    
    def test_format_output_table_non_tabular(self):
        """Test table formatting with non-tabular data"""
        text_output = "This is just regular text\nNot tabular at all"
        formatted = self.executor.format_output(text_output, OutputFormat.TABLE)
        
        # Should return as-is if not tabular
        self.assertEqual(formatted, text_output)
    
    def test_is_tabular_with_separator_valid(self):
        """Test tabular detection with valid table"""
        lines = ["Col1\tCol2\tCol3", "val1\tval2\tval3", "val4\tval5\tval6"]
        is_tabular = self.executor._is_tabular_with_separator(lines, '\t')
        
        self.assertTrue(is_tabular)
    
    def test_is_tabular_with_separator_invalid(self):
        """Test tabular detection with invalid table"""
        lines = ["Col1\tCol2", "val1\tval2\tval3"]  # Inconsistent columns
        is_tabular = self.executor._is_tabular_with_separator(lines, '\t')
        
        self.assertFalse(is_tabular)
    
    def test_is_tabular_with_separator_too_few_lines(self):
        """Test tabular detection with too few lines"""
        lines = ["Col1\tCol2"]  # Only header
        is_tabular = self.executor._is_tabular_with_separator(lines, '\t')
        
        self.assertFalse(is_tabular)
    
    def test_format_table_with_separator(self):
        """Test table formatting with specific separator"""
        lines = ["Name\tPID", "process1\t1234", "process2\t5678"]
        formatted = self.executor._format_table_with_separator(lines, '\t')
        
        lines = formatted.split('\n')
        self.assertEqual(len(lines), 4)  # Header + separator + 2 data rows
        
        # Check header
        self.assertIn("Name", lines[0])
        self.assertIn("PID", lines[0])
        self.assertIn(" | ", lines[0])
        
        # Check separator line
        self.assertTrue(all(c in '- |' for c in lines[1]))
        
        # Check data rows
        self.assertIn("process1", lines[2])
        self.assertIn("1234", lines[2])


class TestErrorHandling(unittest.TestCase):
    """Test error handling in command execution"""
    
    def setUp(self):
        self.config = ExecutionConfig()
        self.config.powershell_executable = ""
        
        mock_detector = Mock()
        mock_info = PowerShellInfo(
            version="7.3.0",
            edition="Core",
            executable_path="/usr/bin/pwsh",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=Platform.LINUX,
            is_available=True,
            supports_core_features=True,
            architecture="x64"
        )
        mock_detector.detect_powershell.return_value = mock_info
        mock_detector.current_platform = Platform.LINUX
        
        self.executor = PowerShellExecutor(self.config, detector=mock_detector)
        
        self.context = CommandContext(
            current_directory="/tmp",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
    
    @patch('subprocess.run')
    def test_encoding_error_handling(self, mock_run):
        """Test handling of encoding errors in output"""
        # Mock result with encoding issues
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Output with special chars: café"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.executor.execute_command("Get-Process", self.context)
        
        self.assertTrue(result.success)
        # Should handle UTF-8 encoding properly
        self.assertIn("café", result.stdout)
    
    @patch('subprocess.run')
    def test_called_process_error_handling(self, mock_run):
        """Test handling of CalledProcessError"""
        error = subprocess.CalledProcessError(
            returncode=1,
            cmd="pwsh",
            output="stdout output",
            stderr="stderr output"
        )
        mock_run.side_effect = error
        
        result = self.executor.execute_command("Get-Process", self.context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.return_code, 1)
    
    @patch('subprocess.run')
    def test_large_output_handling(self, mock_run):
        """Test handling of large output"""
        # Create large output
        large_output = "x" * (self.config.max_output_size + 100)
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = large_output
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.executor.execute_command("Get-Process", self.context)
        
        self.assertTrue(result.success)
        # Output should be truncated
        self.assertLess(len(result.stdout.encode('utf-8')), len(large_output.encode('utf-8')))
        self.assertIn("Output truncated", result.stdout)


if __name__ == '__main__':
    unittest.main()