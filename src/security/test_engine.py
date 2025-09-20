"""Unit tests for SecurityEngine main class"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    SecurityRule, SecurityAction, RiskLevel, Permission, 
    ValidationResult, ExecutionResult, Platform
)
from config.models import SecurityConfig
from security.engine import SecurityEngine


class TestSecurityEngine(unittest.TestCase):
    """Test cases for SecurityEngine main class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary files for configuration
        self.temp_whitelist = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_whitelist.close()
        
        self.temp_audit = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        self.temp_audit.close()
        
        # Create test configuration
        self.config = SecurityConfig(
            whitelist_path=self.temp_whitelist.name,
            sandbox_enabled=False,  # Disable sandbox for unit tests
            require_confirmation_for_admin=True,
            audit_log_path=self.temp_audit.name,
            max_sandbox_memory="256m",
            max_sandbox_cpu="0.5",
            sandbox_timeout=60
        )
        
        # Create security engine
        self.security_engine = SecurityEngine(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        Path(self.temp_whitelist.name).unlink(missing_ok=True)
        Path(self.temp_audit.name).unlink(missing_ok=True)
    
    def test_initialization(self):
        """Test SecurityEngine initialization"""
        self.assertIsNotNone(self.security_engine.whitelist_validator)
        self.assertIsNotNone(self.security_engine.permission_checker)
        self.assertIsNone(self.security_engine.sandbox_manager)  # Disabled in config
    
    def test_initialization_with_sandbox(self):
        """Test SecurityEngine initialization with sandbox enabled"""
        config_with_sandbox = SecurityConfig(
            whitelist_path=self.temp_whitelist.name,
            sandbox_enabled=True,
            audit_log_path=self.temp_audit.name
        )
        
        with patch('security.engine.SandboxManager') as mock_sandbox:
            engine = SecurityEngine(config_with_sandbox)
            self.assertIsNotNone(engine.sandbox_manager)
            mock_sandbox.assert_called_once()
    
    def test_validate_command_allowed(self):
        """Test validation of allowed commands"""
        # Test safe read-only command
        result = self.security_engine.validate_command("Get-Process | Sort-Object CPU")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.blocked_reasons), 0)
        self.assertIsInstance(result.required_permissions, list)
        self.assertIsInstance(result.risk_assessment, RiskLevel)
    
    def test_validate_command_blocked(self):
        """Test validation of blocked commands"""
        # Test dangerous command that should be blocked
        result = self.security_engine.validate_command("Remove-Item C:\\* -Recurse -Force")
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.blocked_reasons), 0)
        self.assertEqual(result.risk_assessment, RiskLevel.CRITICAL)
        self.assertGreater(len(result.suggested_alternatives), 0)
    
    def test_validate_command_with_permissions(self):
        """Test validation of commands requiring permissions"""
        # Test command requiring admin permissions
        result = self.security_engine.validate_command("Stop-Service -Name Spooler")
        
        self.assertTrue(result.is_valid)  # Not blocked, but requires permissions
        self.assertIn(Permission.ADMIN, result.required_permissions)
    
    def test_check_permissions(self):
        """Test permission checking functionality"""
        # Test admin command
        permissions = self.security_engine.check_permissions("Set-ExecutionPolicy RemoteSigned")
        self.assertIn(Permission.ADMIN, permissions)
        
        # Test write command
        permissions = self.security_engine.check_permissions("Set-Content C:\\file.txt 'test'")
        self.assertIn(Permission.WRITE, permissions)
        
        # Test read-only command
        permissions = self.security_engine.check_permissions("Get-Process")
        self.assertEqual(len(permissions), 0)
    
    def test_execute_in_sandbox_disabled(self):
        """Test sandbox execution when disabled"""
        with self.assertRaises(RuntimeError) as context:
            self.security_engine.execute_in_sandbox("Get-Process", 30)
        
        self.assertIn("Sandbox execution is disabled", str(context.exception))
    
    def test_execute_in_sandbox_enabled(self):
        """Test sandbox execution when enabled"""
        # Create config with sandbox enabled
        config_with_sandbox = SecurityConfig(
            whitelist_path=self.temp_whitelist.name,
            sandbox_enabled=True,
            audit_log_path=self.temp_audit.name
        )
        
        # Mock sandbox manager
        mock_sandbox_instance = MagicMock()
        mock_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Process output",
            stderr="",
            execution_time=1.5,
            platform=Platform.LINUX,
            sandbox_used=True
        )
        mock_sandbox_instance.execute.return_value = mock_result
        
        with patch('security.engine.SandboxManager', return_value=mock_sandbox_instance):
            engine = SecurityEngine(config_with_sandbox)
            result = engine.execute_in_sandbox("Get-Process", 30)
        
        self.assertEqual(result, mock_result)
        mock_sandbox_instance.execute.assert_called_once_with("Get-Process", 30)
    
    def test_update_whitelist(self):
        """Test updating whitelist rules"""
        new_rules = [
            SecurityRule(
                pattern=r"Test-NewCommand",
                action=SecurityAction.BLOCK,
                risk_level=RiskLevel.HIGH,
                description="New test rule"
            )
        ]
        
        # Update rules
        self.security_engine.update_whitelist(new_rules)
        
        # Verify rules were updated
        self.assertEqual(len(self.security_engine.whitelist_validator.rules), 1)
        self.assertEqual(self.security_engine.whitelist_validator.rules[0].pattern, r"Test-NewCommand")
    
    def test_three_tier_validation_flow(self):
        """Test complete three-tier validation flow"""
        # Test command that passes all tiers
        safe_command = "Get-Service | Where-Object Status -eq Running"
        result = self.security_engine.validate_command(safe_command)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.blocked_reasons), 0)
        self.assertEqual(len(result.required_permissions), 0)
        
        # Test command blocked at tier 1 (whitelist)
        blocked_command = "Format-Volume -DriveLetter C"
        result = self.security_engine.validate_command(blocked_command)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.blocked_reasons), 0)
        
        # Test command requiring permissions at tier 2
        admin_command = "Stop-Service -Name Spooler"
        result = self.security_engine.validate_command(admin_command)
        
        self.assertTrue(result.is_valid)  # Not blocked
        self.assertIn(Permission.ADMIN, result.required_permissions)
    
    def test_logging_integration(self):
        """Test that security engine logs appropriately"""
        with patch('security.engine.logging.getLogger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            # Create new engine to capture logger calls
            engine = SecurityEngine(self.config)
            
            # Perform validation
            engine.validate_command("Get-Process")
            
            # Verify logging calls were made
            mock_logger_instance.info.assert_called()
    
    def test_error_handling_in_validation(self):
        """Test error handling during validation"""
        # Mock whitelist validator to raise exception
        with patch.object(self.security_engine.whitelist_validator, 'validate') as mock_validate:
            mock_validate.side_effect = Exception("Test error")
            
            # Validation should handle the error gracefully
            with self.assertRaises(Exception):
                self.security_engine.validate_command("Get-Process")
    
    def test_configuration_validation(self):
        """Test that configuration is properly validated"""
        # Test with invalid configuration but sandbox disabled
        invalid_config = SecurityConfig(
            whitelist_path="",  # Empty path
            sandbox_enabled=False,  # Disable sandbox to avoid Docker dependency
            audit_log_path=""
        )
        
        # Should still initialize but with default paths
        engine = SecurityEngine(invalid_config)
        self.assertIsNotNone(engine.whitelist_validator)


class TestSecurityEngineIntegration(unittest.TestCase):
    """Integration tests for SecurityEngine"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_whitelist = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_whitelist.close()
        
        self.temp_audit = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False)
        self.temp_audit.close()
        
        self.config = SecurityConfig(
            whitelist_path=self.temp_whitelist.name,
            sandbox_enabled=False,
            audit_log_path=self.temp_audit.name
        )
    
    def tearDown(self):
        """Clean up integration test environment"""
        Path(self.temp_whitelist.name).unlink(missing_ok=True)
        Path(self.temp_audit.name).unlink(missing_ok=True)
    
    def test_end_to_end_security_validation(self):
        """Test complete end-to-end security validation"""
        engine = SecurityEngine(self.config)
        
        # Test scenarios from requirements
        test_scenarios = [
            {
                'command': 'Get-Process | Where-Object CPU -gt 50 | Select-Object Name, CPU',
                'should_be_valid': True,
                'expected_permissions': [],
                'expected_risk': RiskLevel.LOW
            },
            {
                'command': 'Remove-Item C:\\temp\\* -Recurse -Force',
                'should_be_valid': False,
                'expected_permissions': [],
                'expected_risk': RiskLevel.CRITICAL
            },
            {
                'command': 'Stop-Service -Name Spooler',
                'should_be_valid': True,
                'expected_permissions': [Permission.ADMIN],
                'expected_risk': RiskLevel.MEDIUM
            },
            {
                'command': 'Set-Content -Path C:\\temp\\file.txt -Value "Hello"',
                'should_be_valid': True,
                'expected_permissions': [Permission.WRITE],
                'expected_risk': RiskLevel.LOW
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(command=scenario['command']):
                result = engine.validate_command(scenario['command'])
                
                # Check validation result
                self.assertEqual(result.is_valid, scenario['should_be_valid'],
                               f"Validation result mismatch for: {scenario['command']}")
                
                # Check required permissions
                for expected_perm in scenario['expected_permissions']:
                    self.assertIn(expected_perm, result.required_permissions,
                                f"Expected permission {expected_perm} not found for: {scenario['command']}")
                
                # Check risk assessment
                risk_values = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
                self.assertGreaterEqual(
                    risk_values[result.risk_assessment],
                    risk_values[scenario['expected_risk']],
                    f"Risk level too low for: {scenario['command']}"
                )
    
    def test_performance_with_complex_commands(self):
        """Test performance with complex command validation"""
        import time
        
        engine = SecurityEngine(self.config)
        
        # Complex command with multiple operations
        complex_command = """
        Get-Process | Where-Object {$_.CPU -gt 50} | 
        ForEach-Object {
            Write-Host "High CPU Process: $($_.Name) - $($_.CPU)%"
            if ($_.Name -eq "notepad") {
                Stop-Process -Id $_.Id -Confirm:$false
            }
        } | 
        Out-File -FilePath C:\\temp\\high_cpu_report.txt -Append
        """
        
        start_time = time.time()
        result = engine.validate_command(complex_command)
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 2.0)
        
        # Should detect write permissions needed
        self.assertIn(Permission.WRITE, result.required_permissions)
    
    def test_concurrent_validation(self):
        """Test concurrent command validation"""
        import threading
        import time
        
        engine = SecurityEngine(self.config)
        results = []
        errors = []
        
        def validate_command(command):
            try:
                result = engine.validate_command(command)
                results.append((command, result))
            except Exception as e:
                errors.append((command, e))
        
        # Test commands
        commands = [
            "Get-Process",
            "Get-Service",
            "Stop-Service -Name Spooler",
            "Set-Content C:\\file.txt 'test'",
            "Remove-Item C:\\temp\\file.txt"
        ]
        
        # Create and start threads
        threads = []
        for command in commands:
            thread = threading.Thread(target=validate_command, args=(command,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=5.0)
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), len(commands))
        
        # Verify all commands were processed
        processed_commands = [cmd for cmd, _ in results]
        self.assertEqual(set(processed_commands), set(commands))


if __name__ == '__main__':
    unittest.main()