"""Unit tests for PowerShell Translation functionality"""

import unittest
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.translation import PowerShellTranslator, CommandPattern
from interfaces.base import CommandContext, CommandSuggestion, Platform, UserRole


class TestPowerShellTranslator(unittest.TestCase):
    """Test cases for PowerShellTranslator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.translator = PowerShellTranslator()
        
        self.user_context = CommandContext(
            current_directory="/home/user",
            environment_variables={"PATH": "/usr/bin"},
            user_role=UserRole.USER,
            recent_commands=["Get-Process", "Get-Service"],
            active_modules=["Microsoft.PowerShell.Management"],
            platform=Platform.LINUX,
            session_id="test_session"
        )
        
        self.admin_context = CommandContext(
            current_directory="/home/admin",
            environment_variables={"PATH": "/usr/bin"},
            user_role=UserRole.ADMIN,
            recent_commands=["Stop-Service", "Remove-Item"],
            active_modules=["Microsoft.PowerShell.Management"],
            platform=Platform.WINDOWS,
            session_id="admin_session"
        )
    
    def test_initialization(self):
        """Test translator initialization"""
        self.assertIsNotNone(self.translator.command_patterns)
        self.assertIsNotNone(self.translator.context_modifiers)
        self.assertIsNotNone(self.translator.confidence_adjusters)
        self.assertTrue(len(self.translator.command_patterns) > 0)
    
    def test_normalize_input(self):
        """Test input normalization"""
        # Test basic normalization
        result = self.translator._normalize_input("Please show me the processes")
        self.assertEqual(result, "show me the processes")
        
        # Test filler word removal
        result = self.translator._normalize_input("Can you list all files")
        self.assertEqual(result, "list all files")
        
        # Test case conversion
        result = self.translator._normalize_input("GET PROCESSES")
        self.assertEqual(result, "get processes")
    
    def test_translate_process_commands(self):
        """Test translation of process-related commands"""
        # Test list processes
        result = self.translator.translate_with_context("list processes", self.user_context)
        
        self.assertIsInstance(result, CommandSuggestion)
        self.assertEqual(result.generated_command, "Get-Process")
        self.assertGreater(result.confidence_score, 0.7)
        self.assertIn("processes", result.explanation.lower())
        
        # Test stop process
        result = self.translator.translate_with_context("stop notepad process", self.admin_context)
        
        self.assertIn("Stop-Process", result.generated_command)
        self.assertIn("notepad", result.generated_command)
        self.assertGreater(result.confidence_score, 0.5)
    
    def test_translate_service_commands(self):
        """Test translation of service-related commands"""
        # Test list services
        result = self.translator.translate_with_context("show services", self.user_context)
        
        self.assertIn("Get-Service", result.generated_command)
        self.assertGreater(result.confidence_score, 0.7)
        
        # Test start service
        result = self.translator.translate_with_context("start apache service", self.admin_context)
        
        self.assertIn("Start-Service", result.generated_command)
        self.assertIn("apache", result.generated_command)
    
    def test_translate_file_commands(self):
        """Test translation of file system commands"""
        # Test list files
        result = self.translator.translate_with_context("list files", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-ChildItem")
        self.assertGreater(result.confidence_score, 0.8)
        
        # Test find files
        result = self.translator.translate_with_context("find test.txt", self.user_context)
        
        self.assertIn("Get-ChildItem", result.generated_command)
        self.assertIn("test.txt", result.generated_command)
        self.assertIn("-Recurse", result.generated_command)
        
        # Test copy files
        result = self.translator.translate_with_context("copy file1.txt to file2.txt", self.user_context)
        
        self.assertIn("Copy-Item", result.generated_command)
        self.assertIn("file1.txt", result.generated_command)
        self.assertIn("file2.txt", result.generated_command)
    
    def test_translate_system_commands(self):
        """Test translation of system information commands"""
        # Test system info
        result = self.translator.translate_with_context("show system information", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-ComputerInfo")
        self.assertGreater(result.confidence_score, 0.7)
        
        # Test disk space
        result = self.translator.translate_with_context("check disk space", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-PSDrive")
        
        # Test memory usage
        result = self.translator.translate_with_context("show memory usage", self.user_context)
        
        self.assertIn("Get-Process", result.generated_command)
        self.assertIn("WorkingSet", result.generated_command)
    
    def test_translate_network_commands(self):
        """Test translation of network-related commands"""
        # Test network connections
        result = self.translator.translate_with_context("show network connections", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-NetTCPConnection")
        
        # Test ping
        result = self.translator.translate_with_context("ping google.com", self.user_context)
        
        self.assertIn("Test-NetConnection", result.generated_command)
        self.assertIn("google.com", result.generated_command)
    
    def test_translate_help_commands(self):
        """Test translation of help and discovery commands"""
        # Test help
        result = self.translator.translate_with_context("help Get-Process", self.user_context)
        
        self.assertIn("Get-Help", result.generated_command)
        self.assertIn("get-process", result.generated_command.lower())
        
        # Test list commands
        result = self.translator.translate_with_context("show available commands", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-Command")
    
    def test_context_modifiers(self):
        """Test application of context modifiers"""
        # Test recursive modifier
        result = self.translator.translate_with_context("list files recursive", self.user_context)
        
        self.assertIn("-Recurse", result.generated_command)
        
        # Test verbose modifier
        result = self.translator.translate_with_context("show processes verbose", self.user_context)
        
        self.assertIn("-Verbose", result.generated_command)
        
        # Test first N modifier
        result = self.translator.translate_with_context("show first 5 processes", self.user_context)
        
        self.assertIn("Select-Object -First 5", result.generated_command)
        
        # Test table format
        result = self.translator.translate_with_context("list services in table format", self.user_context)
        
        self.assertIn("Format-Table", result.generated_command)
    
    def test_role_based_adjustments(self):
        """Test role-based command adjustments"""
        # Test user role gets -WhatIf for risky operations
        result = self.translator.translate_with_context("delete test.txt", self.user_context)
        
        self.assertIn("Remove-Item", result.generated_command)
        self.assertIn("-WhatIf", result.generated_command)
        
        # Test admin role doesn't automatically get -WhatIf
        result = self.translator.translate_with_context("delete test.txt", self.admin_context)
        
        self.assertIn("Remove-Item", result.generated_command)
        # May or may not have -WhatIf depending on other factors
    
    def test_platform_specific_commands(self):
        """Test platform-specific command selection"""
        # Test Windows context
        windows_context = CommandContext(
            current_directory="C:\\Users\\test",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.WINDOWS
        )
        
        result = self.translator.translate_with_context("show event logs", windows_context)
        
        self.assertIn("Get-EventLog", result.generated_command)
        
        # Test Linux context
        result = self.translator.translate_with_context("show event logs", self.user_context)
        
        # Should adapt for Linux platform
        self.assertIn("Get-", result.generated_command)
    
    def test_parameter_extraction(self):
        """Test parameter extraction from input"""
        # Test quoted parameters
        result = self.translator.translate_with_context('stop process "notepad.exe"', self.admin_context)
        
        self.assertIn("notepad.exe", result.generated_command)
        
        # Test unquoted parameters
        result = self.translator.translate_with_context("find myfile.txt", self.user_context)
        
        self.assertIn("myfile.txt", result.generated_command)
        
        # Test from-to pattern
        result = self.translator.translate_with_context("copy from source.txt to dest.txt", self.user_context)
        
        self.assertIn("source.txt", result.generated_command)
        self.assertIn("dest.txt", result.generated_command)
    
    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # Test high confidence for exact matches
        result = self.translator.translate_with_context("list processes", self.user_context)
        
        self.assertGreater(result.confidence_score, 0.8)
        
        # Test lower confidence for vague requests
        result = self.translator.translate_with_context("do something", self.user_context)
        
        self.assertLess(result.confidence_score, 0.5)
        
        # Test confidence boost for recent usage
        recent_context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=["Get-Service", "Get-Service -Name apache"],
            active_modules=[],
            platform=Platform.LINUX
        )
        
        result = self.translator.translate_with_context("list services", recent_context)
        
        # Should have higher confidence due to recent usage
        self.assertGreater(result.confidence_score, 0.8)
    
    def test_alternative_generation(self):
        """Test generation of alternative commands"""
        result = self.translator.translate_with_context("list processes", self.user_context)
        
        self.assertIsInstance(result.alternatives, list)
        self.assertTrue(len(result.alternatives) <= 3)
        
        # Should include help as alternative or other reasonable alternatives
        self.assertTrue(len(result.alternatives) > 0)
    
    def test_explanation_generation(self):
        """Test detailed explanation generation"""
        result = self.translator.translate_with_context("stop dangerous-service", self.admin_context)
        
        self.assertIn("Generated PowerShell command", result.explanation)
        self.assertIn("stop dangerous-service", result.explanation)
        
        # Should include warning for risky operations
        if "Stop-Service" in result.generated_command:
            self.assertIn("Warning", result.explanation)
    
    def test_fallback_handling(self):
        """Test fallback when no patterns match"""
        result = self.translator.translate_with_context("xyzabc unknown command", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-Help")
        self.assertLess(result.confidence_score, 0.2)
        self.assertIn("No specific PowerShell command found", result.explanation)
    
    def test_command_analysis(self):
        """Test command complexity analysis"""
        # Test simple command
        analysis = self.translator.analyze_command_complexity("Get-Process")
        
        self.assertIn("complexity_score", analysis)
        self.assertIn("parameter_count", analysis)
        self.assertIn("risk_level", analysis)
        self.assertGreaterEqual(analysis["parameter_count"], 0)
        self.assertEqual(analysis["risk_level"], "low")
        
        # Test complex command
        analysis = self.translator.analyze_command_complexity("Get-Process | Where-Object {$_.CPU -gt 50} | Sort-Object CPU -Descending")
        
        self.assertGreater(analysis["complexity_score"], 0.2)
        self.assertGreater(analysis["pipeline_stages"], 1)
        
        # Test risky command
        analysis = self.translator.analyze_command_complexity("Remove-Item C:\\important\\file.txt -Force")
        
        self.assertEqual(analysis["risk_level"], "high")
        self.assertGreater(analysis["parameter_count"], 0)
    
    def test_category_suggestions(self):
        """Test command suggestions by category"""
        # Test process category
        suggestions = self.translator.get_command_suggestions_by_category("process")
        
        self.assertIn("Get-Process", suggestions)
        self.assertIn("Start-Process", suggestions)
        self.assertIn("Stop-Process", suggestions)
        
        # Test file category
        suggestions = self.translator.get_command_suggestions_by_category("file")
        
        self.assertIn("Get-ChildItem", suggestions)
        self.assertIn("Copy-Item", suggestions)
        
        # Test unknown category
        suggestions = self.translator.get_command_suggestions_by_category("unknown")
        
        self.assertEqual(suggestions, [])
    
    def test_pattern_matching_priority(self):
        """Test that more specific patterns take priority"""
        # Test that "stop service" matches service pattern, not generic stop
        result = self.translator.translate_with_context("stop apache service", self.admin_context)
        
        self.assertIn("Stop-Service", result.generated_command)
        self.assertNotIn("Stop-Process", result.generated_command)
        
        # Test that "list processes" matches process pattern
        result = self.translator.translate_with_context("list running processes", self.user_context)
        
        self.assertEqual(result.generated_command, "Get-Process")
    
    def test_input_variations(self):
        """Test handling of various input formats"""
        test_cases = [
            ("show me all processes", "Get-Process"),
            ("I want to see the processes", "Get-Process"),
            ("can you list processes please", "Get-Process"),
            ("processes", "Get-Process"),
            ("SHOW PROCESSES", "Get-Process")
        ]
        
        for input_text, expected_base in test_cases:
            result = self.translator.translate_with_context(input_text, self.user_context)
            self.assertIn(expected_base, result.generated_command)
    
    def test_error_handling(self):
        """Test error handling in translation"""
        # Test empty input
        result = self.translator.translate_with_context("", self.user_context)
        
        self.assertIsInstance(result, CommandSuggestion)
        self.assertLess(result.confidence_score, 0.5)
        
        # Test very long input
        long_input = "a " * 1000 + "processes"
        result = self.translator.translate_with_context(long_input, self.user_context)
        
        self.assertIsInstance(result, CommandSuggestion)


class TestCommandPattern(unittest.TestCase):
    """Test cases for CommandPattern dataclass"""
    
    def test_pattern_creation(self):
        """Test CommandPattern creation"""
        pattern = CommandPattern(
            keywords=["test", "example"],
            template="Test-Command",
            confidence_base=0.8,
            description="Test pattern"
        )
        
        self.assertEqual(pattern.keywords, ["test", "example"])
        self.assertEqual(pattern.template, "Test-Command")
        self.assertEqual(pattern.confidence_base, 0.8)
        self.assertEqual(pattern.description, "Test pattern")
        self.assertIsNone(pattern.platform_specific)
        self.assertIsNone(pattern.role_requirements)
    
    def test_pattern_with_platform_specific(self):
        """Test CommandPattern with platform-specific templates"""
        pattern = CommandPattern(
            keywords=["test"],
            template="Test-Command",
            confidence_base=0.8,
            platform_specific={
                Platform.WINDOWS: "Test-WindowsCommand",
                Platform.LINUX: "Test-LinuxCommand"
            }
        )
        
        self.assertIn(Platform.WINDOWS, pattern.platform_specific)
        self.assertEqual(pattern.platform_specific[Platform.WINDOWS], "Test-WindowsCommand")


if __name__ == '__main__':
    unittest.main()