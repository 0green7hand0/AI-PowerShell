"""Unit tests for PowerShell executor detection and version management"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import json
import platform
from pathlib import Path

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.executor import (
    PowerShellDetector, PowerShellExecutor, PowerShellVersion, PowerShellInfo
)
from interfaces.base import Platform
from config.models import ExecutionConfig


class TestPowerShellDetector(unittest.TestCase):
    """Test PowerShell detection functionality"""
    
    def setUp(self):
        self.detector = PowerShellDetector()
    
    def test_detect_platform_windows(self):
        """Test platform detection on Windows"""
        with patch('platform.system', return_value='Windows'):
            detector = PowerShellDetector()
            self.assertEqual(detector.current_platform, Platform.WINDOWS)
    
    def test_detect_platform_linux(self):
        """Test platform detection on Linux"""
        with patch('platform.system', return_value='Linux'):
            detector = PowerShellDetector()
            self.assertEqual(detector.current_platform, Platform.LINUX)
    
    def test_detect_platform_macos(self):
        """Test platform detection on macOS"""
        with patch('platform.system', return_value='Darwin'):
            detector = PowerShellDetector()
            self.assertEqual(detector.current_platform, Platform.MACOS)
    
    def test_detect_platform_unknown(self):
        """Test platform detection for unknown systems"""
        with patch('platform.system', return_value='FreeBSD'):
            detector = PowerShellDetector()
            self.assertEqual(detector.current_platform, Platform.LINUX)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_detect_powershell_core_success(self, mock_run, mock_which):
        """Test successful PowerShell Core detection"""
        # Mock finding pwsh executable
        mock_which.return_value = '/usr/bin/pwsh'
        
        # Mock successful version query
        version_table = {
            "PSVersion": "7.3.0",
            "PSEdition": "Core",
            "Platform": "Unix"
        }
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(version_table)
        mock_run.return_value = mock_result
        
        info = self.detector.detect_powershell()
        
        self.assertTrue(info.is_available)
        self.assertEqual(info.version, "7.3.0")
        self.assertEqual(info.edition, "Core")
        self.assertEqual(info.executable_path, '/usr/bin/pwsh')
        self.assertEqual(info.version_type, PowerShellVersion.POWERSHELL_CORE)
        self.assertTrue(info.supports_core_features)
    
    @patch('shutil.which')
    def test_detect_powershell_core_not_found(self, mock_which):
        """Test PowerShell Core not found"""
        mock_which.return_value = None
        
        with patch.object(self.detector, 'current_platform', Platform.LINUX):
            info = self.detector.detect_powershell()
            
            self.assertFalse(info.is_available)
            self.assertEqual(info.executable_path, "")
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_detect_powershell_core_timeout(self, mock_run, mock_which):
        """Test PowerShell Core detection with timeout"""
        mock_which.return_value = '/usr/bin/pwsh'
        mock_run.side_effect = subprocess.TimeoutExpired('pwsh', 10)
        
        with patch.object(self.detector, 'current_platform', Platform.LINUX):
            info = self.detector.detect_powershell()
            
            self.assertFalse(info.is_available)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_detect_windows_powershell_success(self, mock_exists, mock_run, mock_which):
        """Test successful Windows PowerShell detection"""
        # Mock Windows platform
        with patch.object(self.detector, 'current_platform', Platform.WINDOWS):
            # Mock PowerShell Core not found
            mock_which.return_value = None
            
            # Mock Windows PowerShell path exists
            mock_exists.return_value = True
            
            # Mock successful version query
            version_table = {
                "PSVersion": "5.1.19041.1682",
                "PSEdition": "Desktop",
                "Platform": "Win32NT"
            }
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps(version_table)
            mock_run.return_value = mock_result
            
            info = self.detector.detect_powershell()
            
            self.assertTrue(info.is_available)
            self.assertEqual(info.version, "5.1.19041.1682")
            self.assertEqual(info.edition, "Desktop")
            self.assertEqual(info.version_type, PowerShellVersion.WINDOWS_POWERSHELL)
            self.assertFalse(info.supports_core_features)
    
    def test_detect_windows_powershell_on_linux(self):
        """Test Windows PowerShell detection on non-Windows platform"""
        with patch.object(self.detector, 'current_platform', Platform.LINUX):
            info = self.detector._try_detect_windows_powershell()
            
            self.assertFalse(info.is_available)
            self.assertEqual(info.platform, Platform.LINUX)
    
    def test_caching_behavior(self):
        """Test that detection results are cached"""
        with patch.object(self.detector, '_try_detect_powershell_core') as mock_detect:
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
            mock_detect.return_value = mock_info
            
            # First call should trigger detection
            info1 = self.detector.detect_powershell()
            self.assertEqual(mock_detect.call_count, 1)
            
            # Second call should use cache
            info2 = self.detector.detect_powershell()
            self.assertEqual(mock_detect.call_count, 1)
            self.assertEqual(info1, info2)
            
            # Force refresh should trigger detection again
            info3 = self.detector.detect_powershell(force_refresh=True)
            self.assertEqual(mock_detect.call_count, 2)
    
    def test_installation_guide_windows(self):
        """Test installation guide for Windows"""
        with patch.object(self.detector, 'current_platform', Platform.WINDOWS):
            guide = self.detector.get_recommended_installation_guide()
            
            self.assertIn("PowerShell Core", guide)
            self.assertIn("winget install", guide)
            self.assertIn("Windows PowerShell", guide)
    
    def test_installation_guide_linux(self):
        """Test installation guide for Linux"""
        with patch.object(self.detector, 'current_platform', Platform.LINUX):
            guide = self.detector.get_recommended_installation_guide()
            
            self.assertIn("sudo apt install", guide)
            self.assertIn("sudo yum install", guide)
    
    def test_installation_guide_macos(self):
        """Test installation guide for macOS"""
        with patch.object(self.detector, 'current_platform', Platform.MACOS):
            guide = self.detector.get_recommended_installation_guide()
            
            self.assertIn("brew install", guide)


class TestPowerShellExecutor(unittest.TestCase):
    """Test PowerShell executor functionality"""
    
    def setUp(self):
        self.config = ExecutionConfig()
        # Override the auto-detected executable for testing
        self.config.powershell_executable = ""
        
    def test_executor_initialization_success(self):
        """Test successful executor initialization"""
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
        
        executor = PowerShellExecutor(self.config, detector=mock_detector)
        
        self.assertEqual(executor.powershell_info, mock_info)
        self.assertTrue(executor.is_available())
    
    def test_executor_initialization_not_available(self):
        """Test executor initialization when PowerShell not available"""
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
        
        executor = PowerShellExecutor(self.config, detector=mock_detector)
        
        self.assertFalse(executor.is_available())
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_custom_executable_validation_success(self, mock_run, mock_which):
        """Test successful custom executable validation"""
        mock_which.return_value = '/custom/pwsh'
        
        version_table = {
            "PSVersion": "7.2.0",
            "PSEdition": "Core",
            "Platform": "Unix"
        }
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(version_table)
        mock_run.return_value = mock_result
        
        config = ExecutionConfig(powershell_executable='/custom/pwsh')
        executor = PowerShellExecutor(config)
        
        self.assertTrue(executor.is_available())
        self.assertEqual(executor.powershell_info.executable_path, '/custom/pwsh')
        self.assertEqual(executor.powershell_info.version, "7.2.0")
    
    @patch('shutil.which')
    @patch('pathlib.Path.exists')
    def test_custom_executable_not_found(self, mock_exists, mock_which):
        """Test custom executable not found"""
        mock_which.return_value = None
        mock_exists.return_value = False
        
        config = ExecutionConfig(powershell_executable='/nonexistent/pwsh')
        
        with self.assertRaises(FileNotFoundError):
            PowerShellExecutor(config)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_custom_executable_validation_timeout(self, mock_run, mock_which):
        """Test custom executable validation timeout"""
        mock_which.return_value = '/custom/pwsh'
        mock_run.side_effect = subprocess.TimeoutExpired('pwsh', 10)
        
        config = ExecutionConfig(powershell_executable='/custom/pwsh')
        
        with self.assertRaises(RuntimeError):
            PowerShellExecutor(config)
    
    def test_get_powershell_info_available(self):
        """Test get_powershell_info when PowerShell is available"""
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
        
        executor = PowerShellExecutor(self.config, detector=mock_detector)
        info = executor.get_powershell_info()
        
        self.assertTrue(info["available"])
        self.assertEqual(info["version"], "7.3.0")
        self.assertEqual(info["edition"], "Core")
        self.assertEqual(info["executable_path"], "/usr/bin/pwsh")
        self.assertEqual(info["version_type"], "powershell_core")
        self.assertEqual(info["platform"], "linux")
        self.assertTrue(info["supports_core_features"])
        self.assertEqual(info["architecture"], "x64")
    
    def test_get_powershell_info_not_available(self):
        """Test get_powershell_info when PowerShell is not available"""
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
        mock_detector.get_recommended_installation_guide.return_value = "Install guide"
        mock_detector.current_platform = Platform.LINUX
        
        executor = PowerShellExecutor(self.config, detector=mock_detector)
        info = executor.get_powershell_info()
        
        self.assertFalse(info["available"])
        self.assertIn("error", info)
        self.assertIn("installation_guide", info)
        self.assertEqual(info["platform"], "linux")
    
    def test_implemented_methods(self):
        """Test that all methods are now implemented"""
        executor = PowerShellExecutor(self.config)
        
        # All methods should now be implemented
        # adapt_for_platform should not raise NotImplementedError
        try:
            result = executor.adapt_for_platform("Get-Process", Platform.WINDOWS)
            # Should return a string (the adapted command)
            self.assertIsInstance(result, str)
        except NotImplementedError:
            self.fail("adapt_for_platform should be implemented")


class TestPowerShellVersionDetection(unittest.TestCase):
    """Test PowerShell version detection edge cases"""
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_version_type_detection_core(self, mock_run, mock_which):
        """Test detection of PowerShell Core version type"""
        mock_which.return_value = '/usr/bin/pwsh'
        
        version_table = {
            "PSVersion": "7.3.0",
            "PSEdition": "Core"
        }
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(version_table)
        mock_run.return_value = mock_result
        
        detector = PowerShellDetector()
        info = detector._try_detect_powershell_core()
        
        self.assertEqual(info.version_type, PowerShellVersion.POWERSHELL_CORE)
        self.assertTrue(info.supports_core_features)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('pathlib.Path.exists')
    def test_version_type_detection_windows(self, mock_exists, mock_run, mock_which):
        """Test detection of Windows PowerShell version type"""
        detector = PowerShellDetector()
        
        with patch.object(detector, 'current_platform', Platform.WINDOWS):
            mock_which.return_value = None
            mock_exists.return_value = True
            
            version_table = {
                "PSVersion": "5.1.19041.1682",
                "PSEdition": "Desktop"
            }
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps(version_table)
            mock_run.return_value = mock_result
            
            info = detector._try_detect_windows_powershell()
            
            self.assertEqual(info.version_type, PowerShellVersion.WINDOWS_POWERSHELL)
            self.assertFalse(info.supports_core_features)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_json_parsing_error(self, mock_run, mock_which):
        """Test handling of JSON parsing errors"""
        mock_which.return_value = '/usr/bin/pwsh'
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Invalid JSON"
        mock_run.return_value = mock_result
        
        detector = PowerShellDetector()
        info = detector._try_detect_powershell_core()
        
        self.assertFalse(info.is_available)
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_command_failure(self, mock_run, mock_which):
        """Test handling of command execution failure"""
        mock_which.return_value = '/usr/bin/pwsh'
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        detector = PowerShellDetector()
        info = detector._try_detect_powershell_core()
        
        self.assertFalse(info.is_available)


if __name__ == '__main__':
    unittest.main()