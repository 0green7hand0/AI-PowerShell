"""Unit tests for whitelist validation system"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import SecurityRule, SecurityAction, RiskLevel
from security.engine import WhitelistValidator


class TestWhitelistValidator(unittest.TestCase):
    """Test cases for WhitelistValidator"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary file for whitelist
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.whitelist_path = self.temp_file.name
        
        # Create validator instance
        self.validator = WhitelistValidator(self.whitelist_path)
    
    def tearDown(self):
        """Clean up test environment"""
        Path(self.whitelist_path).unlink(missing_ok=True)
    
    def test_initialization_creates_default_rules(self):
        """Test that validator creates default rules on initialization"""
        self.assertGreater(len(self.validator.rules), 0)
        
        # Check that critical rules exist
        rule_patterns = [rule.pattern for rule in self.validator.rules]
        self.assertIn(r"Remove-Item.*-Recurse.*-Force", rule_patterns)
        self.assertIn(r"Format-Volume|Format-Disk", rule_patterns)
    
    def test_validate_blocked_command(self):
        """Test validation of blocked commands"""
        # Test recursive deletion (should be blocked)
        result = self.validator.validate("Remove-Item C:\\temp -Recurse -Force")
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.blocked_reasons), 0)
        self.assertEqual(result.risk_assessment, RiskLevel.CRITICAL)
        self.assertGreater(len(result.suggested_alternatives), 0)
    
    def test_validate_allowed_command(self):
        """Test validation of allowed commands"""
        # Test read-only command (should be allowed)
        result = self.validator.validate("Get-Process | Where-Object CPU -gt 50")
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.blocked_reasons), 0)
    
    def test_validate_confirmation_required_command(self):
        """Test validation of commands requiring confirmation"""
        # Test service stop (should require confirmation but not be blocked)
        result = self.validator.validate("Stop-Service -Name Spooler")
        
        self.assertTrue(result.is_valid)  # Not blocked, but may require confirmation
        self.assertEqual(len(result.blocked_reasons), 0)
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case insensitive"""
        # Test with different cases
        commands = [
            "remove-item C:\\temp -recurse -force",
            "REMOVE-ITEM C:\\temp -RECURSE -FORCE",
            "Remove-Item C:\\temp -Recurse -Force"
        ]
        
        for command in commands:
            result = self.validator.validate(command)
            self.assertFalse(result.is_valid, f"Command should be blocked: {command}")
    
    def test_multiple_rule_matching(self):
        """Test command matching multiple rules"""
        # Create a command that matches multiple patterns
        result = self.validator.validate("Stop-Service Spooler; Remove-Item C:\\temp\\file.txt")
        
        # Should still be valid (no blocking rules matched)
        self.assertTrue(result.is_valid)
    
    def test_risk_level_assessment(self):
        """Test risk level assessment with multiple rules"""
        # Test command with high risk
        result = self.validator.validate("Stop-Computer -Force")
        self.assertIn(result.risk_assessment, [RiskLevel.HIGH, RiskLevel.MEDIUM])
        
        # Test command with critical risk
        result = self.validator.validate("Format-Volume -DriveLetter C")
        self.assertEqual(result.risk_assessment, RiskLevel.CRITICAL)
    
    def test_normalize_command(self):
        """Test command normalization"""
        # Test with extra whitespace
        command_with_spaces = "  Get-Process   |   Where-Object   CPU  -gt  50  "
        normalized = self.validator._normalize_command(command_with_spaces)
        
        self.assertEqual(normalized, "Get-Process | Where-Object CPU -gt 50")
    
    def test_invalid_regex_pattern(self):
        """Test handling of invalid regex patterns"""
        # Create rule with invalid regex
        invalid_rule = SecurityRule(
            pattern="[invalid regex",  # Missing closing bracket
            action=SecurityAction.BLOCK,
            risk_level=RiskLevel.HIGH,
            description="Invalid regex test"
        )
        
        self.validator.rules.append(invalid_rule)
        
        # Should not crash and should not match
        result = self.validator.validate("Get-Process")
        self.assertTrue(result.is_valid)
    
    def test_update_rules(self):
        """Test updating whitelist rules"""
        new_rules = [
            SecurityRule(
                pattern=r"Test-Command",
                action=SecurityAction.BLOCK,
                risk_level=RiskLevel.MEDIUM,
                description="Test rule"
            )
        ]
        
        self.validator.update_rules(new_rules)
        
        # Check that rules were updated
        self.assertEqual(len(self.validator.rules), 1)
        self.assertEqual(self.validator.rules[0].pattern, r"Test-Command")
        
        # Check that file was saved
        self.assertTrue(Path(self.whitelist_path).exists())
    
    def test_load_rules_from_file(self):
        """Test loading rules from existing file"""
        # Create test rules file
        test_rules = {
            "rules": [
                {
                    "pattern": r"Test-Pattern",
                    "action": "block",
                    "risk_level": "high",
                    "description": "Test rule from file"
                }
            ]
        }
        
        with open(self.whitelist_path, 'w') as f:
            json.dump(test_rules, f)
        
        # Create new validator to load from file
        new_validator = WhitelistValidator(self.whitelist_path)
        
        self.assertEqual(len(new_validator.rules), 1)
        self.assertEqual(new_validator.rules[0].pattern, r"Test-Pattern")
        self.assertEqual(new_validator.rules[0].action, SecurityAction.BLOCK)
        self.assertEqual(new_validator.rules[0].risk_level, RiskLevel.HIGH)
    
    def test_save_rules_to_file(self):
        """Test saving rules to file"""
        # Validator should have saved default rules
        self.assertTrue(Path(self.whitelist_path).exists())
        
        # Load and verify file content
        with open(self.whitelist_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('rules', data)
        self.assertGreater(len(data['rules']), 0)
        
        # Verify rule structure
        rule = data['rules'][0]
        self.assertIn('pattern', rule)
        self.assertIn('action', rule)
        self.assertIn('risk_level', rule)
        self.assertIn('description', rule)
    
    def test_get_alternatives_for_blocked_commands(self):
        """Test generation of alternative suggestions"""
        # Test recursive deletion alternatives
        result = self.validator.validate("Remove-Item C:\\temp -Recurse -Force")
        self.assertGreater(len(result.suggested_alternatives), 0)
        
        # Check that alternatives contain helpful suggestions
        alternatives_text = ' '.join(result.suggested_alternatives).lower()
        self.assertIn('get-childitem', alternatives_text)
    
    def test_specific_command_patterns(self):
        """Test specific command patterns from requirements"""
        test_cases = [
            # Should be blocked
            ("Remove-Item C:\\* -Recurse -Force", False, RiskLevel.CRITICAL),
            ("Format-Volume -DriveLetter C -FileSystem NTFS", False, RiskLevel.CRITICAL),
            
            # Should require confirmation
            ("Stop-Computer -ComputerName localhost", True, RiskLevel.HIGH),
            ("Restart-Computer -Force", True, RiskLevel.HIGH),
            ("Stop-Service -Name Spooler -Force", True, RiskLevel.MEDIUM),
            
            # Should be allowed
            ("Get-Process | Sort-Object CPU -Descending", True, RiskLevel.LOW),
            ("Get-Service | Where-Object Status -eq Running", True, RiskLevel.LOW),
            ("Select-Object -Property Name, CPU", True, RiskLevel.LOW),
        ]
        
        for command, should_be_valid, expected_risk in test_cases:
            with self.subTest(command=command):
                result = self.validator.validate(command)
                self.assertEqual(result.is_valid, should_be_valid, 
                               f"Command validation failed: {command}")
                
                # Risk level should be at least the expected level
                risk_values = {
                    RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, 
                    RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4
                }
                self.assertGreaterEqual(
                    risk_values[result.risk_assessment], 
                    risk_values[expected_risk],
                    f"Risk level too low for: {command}"
                )


class TestWhitelistValidatorIntegration(unittest.TestCase):
    """Integration tests for WhitelistValidator"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.whitelist_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up integration test environment"""
        Path(self.whitelist_path).unlink(missing_ok=True)
    
    def test_real_world_powershell_commands(self):
        """Test with real-world PowerShell commands"""
        validator = WhitelistValidator(self.whitelist_path)
        
        # Safe commands that should be allowed
        safe_commands = [
            "Get-Process | Where-Object {$_.CPU -gt 50} | Select-Object Name, CPU",
            "Get-Service | Sort-Object Status | Format-Table",
            "Get-ChildItem C:\\temp | Measure-Object -Property Length -Sum",
            "Get-EventLog -LogName System -Newest 10",
            "Get-WmiObject -Class Win32_ComputerSystem",
        ]
        
        for command in safe_commands:
            with self.subTest(command=command):
                result = validator.validate(command)
                self.assertTrue(result.is_valid, f"Safe command blocked: {command}")
        
        # Dangerous commands that should be blocked
        dangerous_commands = [
            "Remove-Item C:\\Windows\\System32 -Recurse -Force",
            "Format-Volume -DriveLetter C -Confirm:$false",
            "Get-ChildItem C:\\ -Recurse | Remove-Item -Force",
        ]
        
        for command in dangerous_commands:
            with self.subTest(command=command):
                result = validator.validate(command)
                self.assertFalse(result.is_valid, f"Dangerous command allowed: {command}")
    
    def test_performance_with_many_rules(self):
        """Test performance with large number of rules"""
        import time
        
        validator = WhitelistValidator(self.whitelist_path)
        
        # Add many rules
        many_rules = []
        for i in range(1000):
            many_rules.append(SecurityRule(
                pattern=f"Test-Command{i}",
                action=SecurityAction.ALLOW,
                risk_level=RiskLevel.LOW,
                description=f"Test rule {i}"
            ))
        
        validator.update_rules(many_rules)
        
        # Test validation performance
        start_time = time.time()
        result = validator.validate("Get-Process")
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second)
        self.assertLess(end_time - start_time, 1.0)
        self.assertTrue(result.is_valid)


if __name__ == '__main__':
    unittest.main()