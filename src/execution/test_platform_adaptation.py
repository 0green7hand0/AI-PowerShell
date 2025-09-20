"""Unit tests for cross-platform PowerShell command adaptation"""

import unittest
from unittest.mock import Mock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.executor import PowerShellExecutor, PowerShellDetector, PowerShellInfo, PowerShellVersion
from interfaces.base import Platform
from config.models import ExecutionConfig


class TestPlatformAdaptation(unittest.TestCase):
    """Test cross-platform command adaptation functionality"""
    
    def setUp(self):
        self.config = ExecutionConfig()
        self.config.powershell_executable = ""
        
        # Create mock detector
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
    
    def test_adapt_for_platform_empty_command(self):
        """Test adaptation of empty command"""
        result = self.executor.adapt_for_platform("", Platform.WINDOWS)
        self.assertEqual(result, "")
        
        result = self.executor.adapt_for_platform("   ", Platform.LINUX)
        self.assertEqual(result, "   ")
    
    def test_adapt_for_platform_no_changes_needed(self):
        """Test adaptation when no changes are needed"""
        command = "Get-Process | Where-Object {$_.CPU -gt 50}"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        # Should remain largely the same for PowerShell commands
        self.assertIn("Get-Process", result)


class TestPathAdaptation(unittest.TestCase):
    """Test path adaptation functionality"""
    
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
    
    def test_adapt_unix_paths_to_windows(self):
        """Test adapting Unix paths to Windows"""
        command = "Get-Content /tmp/file.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        self.assertIn("C:\\temp\\file.txt", result)
        self.assertNotIn("/tmp/file.txt", result)
    
    def test_adapt_windows_paths_to_unix(self):
        """Test adapting Windows paths to Unix"""
        command = "Get-Content C:\\temp\\file.txt"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        
        self.assertIn("/tmp/file.txt", result)
        self.assertNotIn("C:\\temp\\file.txt", result)
    
    def test_adapt_home_directory_unix_to_windows(self):
        """Test adapting Unix home directory to Windows"""
        command = "Get-Content /home/user/file.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        self.assertIn("C:\\Users\\user\\file.txt", result)
    
    def test_adapt_home_directory_windows_to_unix(self):
        """Test adapting Windows home directory to Unix"""
        command = "Get-Content C:\\Users\\user\\file.txt"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        
        self.assertIn("/home/user/file.txt", result)
    
    def test_adapt_program_files_paths(self):
        """Test adapting Program Files paths"""
        # Windows to Unix
        command = "& 'C:\\Program Files\\app\\app.exe'"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        self.assertIn("/usr/app/app.exe", result)
        
        # Unix to Windows
        command = "& '/usr/bin/app'"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        self.assertIn("C:\\Program Files\\bin\\app", result)
    
    def test_adapt_relative_paths(self):
        """Test adapting relative paths"""
        # Unix to Windows
        command = "Get-Content ./config/file.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        self.assertIn(".\\config\\file.txt", result)
        
        # Windows to Unix  
        command = "Get-Content .\\config\\file.txt"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        self.assertIn("./config/file.txt", result)
    
    def test_convert_unix_to_windows_path(self):
        """Test Unix to Windows path conversion"""
        # Test common directory mappings
        self.assertEqual(
            self.executor._convert_unix_to_windows_path("/tmp/file.txt"),
            "C:\\temp\\file.txt"
        )
        
        self.assertEqual(
            self.executor._convert_unix_to_windows_path("/home/user/doc.txt"),
            "C:\\Users\\user\\doc.txt"
        )
        
        self.assertEqual(
            self.executor._convert_unix_to_windows_path("/usr/bin/app"),
            "C:\\Program Files\\bin\\app"
        )
        
        self.assertEqual(
            self.executor._convert_unix_to_windows_path("/var/log/app.log"),
            "C:\\ProgramData\\log\\app.log"
        )
        
        # Test generic path
        self.assertEqual(
            self.executor._convert_unix_to_windows_path("/other/path"),
            "C:\\other\\path"
        )
    
    def test_convert_windows_to_unix_path(self):
        """Test Windows to Unix path conversion"""
        # Test common directory mappings
        self.assertEqual(
            self.executor._convert_windows_to_unix_path("C:\\temp\\file.txt"),
            "/tmp/file.txt"
        )
        
        self.assertEqual(
            self.executor._convert_windows_to_unix_path("C:\\Users\\user\\doc.txt"),
            "/home/user/doc.txt"
        )
        
        self.assertEqual(
            self.executor._convert_windows_to_unix_path("C:\\Program Files\\app\\app.exe"),
            "/usr/app/app.exe"
        )
        
        self.assertEqual(
            self.executor._convert_windows_to_unix_path("C:\\ProgramData\\log\\app.log"),
            "/var/log/app.log"
        )
        
        # Test path without drive letter
        self.assertEqual(
            self.executor._convert_windows_to_unix_path("relative\\path"),
            "relative/path"
        )


class TestEnvironmentVariableAdaptation(unittest.TestCase):
    """Test environment variable adaptation functionality"""
    
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
    
    def test_adapt_unix_env_vars_to_windows(self):
        """Test adapting Unix environment variables to Windows"""
        command = "Get-Content $HOME/file.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        self.assertIn("%USERPROFILE%", result)
        self.assertNotIn("$HOME", result)
    
    def test_adapt_windows_env_vars_to_unix(self):
        """Test adapting Windows environment variables to Unix"""
        command = "Get-Content %USERPROFILE%\\file.txt"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        
        self.assertIn("$HOME", result)
        self.assertNotIn("%USERPROFILE%", result)
    
    def test_adapt_user_variables(self):
        """Test adapting user-related environment variables"""
        # Unix to Windows
        command = "Write-Host $USER"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        self.assertIn("%USERNAME%", result)
        
        # Windows to Unix
        command = "Write-Host %USERNAME%"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        self.assertIn("$USER", result)
    
    def test_adapt_shell_variables(self):
        """Test adapting shell-related environment variables"""
        # Unix to Windows
        command = "& $SHELL -c 'echo test'"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        self.assertIn("%COMSPEC%", result)
        
        # Windows to Unix
        command = "& %COMSPEC% /c echo test"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        self.assertIn("$SHELL", result)
    
    def test_adapt_custom_env_vars(self):
        """Test adapting custom environment variables"""
        # Unix to Windows
        command = "Write-Host $MY_CUSTOM_VAR"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        self.assertIn("%MY_CUSTOM_VAR%", result)
        
        # Windows to Unix
        command = "Write-Host %MY_CUSTOM_VAR%"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        self.assertIn("$MY_CUSTOM_VAR", result)


class TestCommandAdaptation(unittest.TestCase):
    """Test platform-specific command adaptation"""
    
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
    
    def test_adapt_unix_commands_to_windows(self):
        """Test adapting Unix commands to Windows PowerShell equivalents"""
        test_cases = [
            ("ls", "Get-ChildItem"),
            ("ls /tmp", "Get-ChildItem", "C:\\temp"),  # Path should be adapted too
            ("cat file.txt", "Get-Content file.txt"),
            ("grep pattern file.txt", "Select-String pattern file.txt"),
            ("ps", "Get-Process"),
            ("kill 1234", "Stop-Process -Id 1234"),
            ("which pwsh", "Get-Command pwsh"),
            ("pwd", "Get-Location"),
            ("cd /tmp", "Set-Location", "C:\\temp"),  # Path should be adapted too
            ("mkdir newdir", "New-Item -ItemType Directory -Path newdir"),
            ("rm file.txt", "Remove-Item file.txt"),
            ("cp src.txt dst.txt", "Copy-Item src.txt dst.txt"),
            ("mv old.txt new.txt", "Move-Item old.txt new.txt")
        ]
        
        for test_case in test_cases:
            unix_cmd = test_case[0]
            expected_command = test_case[1]
            expected_path = test_case[2] if len(test_case) > 2 else None
            
            with self.subTest(unix_cmd=unix_cmd):
                result = self.executor.adapt_for_platform(unix_cmd, Platform.WINDOWS)
                self.assertIn(expected_command, result)
                if expected_path:
                    self.assertIn(expected_path, result)
    
    def test_adapt_windows_commands_to_unix(self):
        """Test adapting Windows commands to Unix equivalents"""
        test_cases = [
            ("dir", "ls"),
            ("dir C:\\temp", "ls", "/tmp"),  # Path should be adapted too
            ("type file.txt", "cat file.txt"),
            ("findstr pattern file.txt", "grep pattern file.txt"),
            ("tasklist", "ps aux"),
            ("taskkill /PID 1234", "kill /PID 1234"),
            ("where pwsh", "which pwsh"),
            ("md newdir", "mkdir newdir"),
            ("del file.txt", "rm file.txt"),
            ("copy src.txt dst.txt", "cp src.txt dst.txt"),
            ("move old.txt new.txt", "mv old.txt new.txt"),
            ("ren old.txt new.txt", "mv old.txt new.txt")
        ]
        
        for test_case in test_cases:
            windows_cmd = test_case[0]
            expected_command = test_case[1]
            expected_path = test_case[2] if len(test_case) > 2 else None
            
            with self.subTest(windows_cmd=windows_cmd):
                result = self.executor.adapt_for_platform(windows_cmd, Platform.LINUX)
                self.assertIn(expected_command, result)
                if expected_path:
                    self.assertIn(expected_path, result)
    
    def test_adapt_commands_at_line_end(self):
        """Test adapting commands at end of line"""
        command = "ls\nps\npwd"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        self.assertIn("Get-ChildItem\n", result)
        self.assertIn("Get-Process\n", result)
        self.assertIn("Get-Location", result)
    
    def test_adapt_commands_preserve_context(self):
        """Test that command adaptation preserves surrounding context"""
        command = "if (Test-Path file.txt) { cat file.txt | grep pattern }"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        # Should adapt the commands but preserve the PowerShell structure
        self.assertIn("Get-Content", result)
        self.assertIn("Select-String", result)
        self.assertIn("if (Test-Path", result)
        self.assertIn(")", result)
        self.assertIn("{", result)
        self.assertIn("}", result)


class TestComplexAdaptation(unittest.TestCase):
    """Test complex adaptation scenarios"""
    
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
    
    def test_adapt_complex_command_unix_to_windows(self):
        """Test adapting complex command from Unix to Windows"""
        command = "ls /home/$USER | grep .txt | cat > /tmp/output.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        # Should adapt paths, environment variables, and commands
        self.assertIn("Get-ChildItem", result)
        self.assertIn("C:\\Users", result)  # Path should be adapted
        self.assertIn("%USERNAME%", result)  # Environment variable should be adapted
        self.assertIn("Select-String", result)
        self.assertIn("Get-Content", result)
        self.assertIn("C:\\temp\\output.txt", result)
    
    def test_adapt_complex_command_windows_to_unix(self):
        """Test adapting complex command from Windows to Unix"""
        command = "dir C:\\Users\\%USERNAME% | findstr .txt | type > C:\\temp\\output.txt"
        result = self.executor.adapt_for_platform(command, Platform.LINUX)
        
        # Should adapt paths, environment variables, and commands
        self.assertIn("ls", result)
        self.assertIn("/home/$USER", result)
        self.assertIn("grep", result)
        self.assertIn("cat", result)
        self.assertIn("/tmp/output.txt", result)
    
    def test_adapt_mixed_content(self):
        """Test adapting command with mixed PowerShell and platform-specific content"""
        command = "Get-Process | Where-Object {$_.Name -eq 'pwsh'} | ForEach-Object { ls /proc/$($_.Id) }"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        # Should preserve PowerShell cmdlets but adapt Unix commands and paths
        self.assertIn("Get-Process", result)
        self.assertIn("Where-Object", result)
        self.assertIn("ForEach-Object", result)
        self.assertIn("Get-ChildItem", result)  # ls should be adapted
        # Path adaptation might be complex here, but the structure should be preserved
    
    def test_adapt_quoted_paths(self):
        """Test adapting paths within quotes"""
        command = 'Get-Content "/tmp/file with spaces.txt"'
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        # Should adapt the path even within quotes
        self.assertIn("C:\\temp\\file with spaces.txt", result)
    
    def test_adapt_multiple_paths_in_command(self):
        """Test adapting multiple paths in single command"""
        command = "Copy-Item /home/user/src.txt /tmp/dst.txt"
        result = self.executor.adapt_for_platform(command, Platform.WINDOWS)
        
        self.assertIn("C:\\Users\\user\\src.txt", result)
        self.assertIn("C:\\temp\\dst.txt", result)


if __name__ == '__main__':
    unittest.main()