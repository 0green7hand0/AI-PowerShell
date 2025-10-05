"""Unit tests for PowerShell Error Detection functionality"""

import unittest
from unittest.mock import Mock, patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.error_detection import PowerShellErrorDetector, PowerShellCmdlet, ErrorType
from interfaces.base import ErrorSuggestion


class TestPowerShellErrorDetector(unittest.TestCase):
    """Test cases for PowerShellErrorDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = PowerShellErrorDetector()
    
    def test_initialization(self):
        """Test error detector initialization"""
        self.assertIsNotNone(self.detector.cmdlets)
        self.assertIsNotNone(self.detector.common_typos)
        self.assertIsNotNone(self.detector.syntax_patterns)
        self.assertIsNotNone(self.detector.security_patterns)
        
        # Check that common cmdlets are loaded
        self.assertIn("get-process", self.detector.cmdlets)
        self.assertIn("get-service", self.detector.cmdlets)
        self.assertIn("get-childitem", self.detector.cmdlets)
    
    def test_detect_empty_command(self):
        """Test detection of empty commands"""
        errors = self.detector.detect_errors("")
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, ErrorType.SYNTAX.value)
        self.assertEqual(errors[0].confidence, 1.0)
        self.assertIn("Empty command", errors[0].description)
    
    def test_detect_syntax_errors(self):
        """Test detection of syntax errors"""
        # Test unclosed brace
        errors = self.detector.detect_errors("Get-Process | Where-Object {$_.Name -eq 'test'")
        brace_errors = [e for e in errors if "brace" in e.description.lower()]
        self.assertTrue(len(brace_errors) > 0)
        
        # Test unclosed parenthesis
        errors = self.detector.detect_errors("Get-Process | Where-Object ($_.CPU -gt 50")
        paren_errors = [e for e in errors if "parenthesis" in e.description.lower()]
        self.assertTrue(len(paren_errors) > 0)
        
        # Test unclosed quote
        errors = self.detector.detect_errors('Get-Process -Name "notepad')
        quote_errors = [e for e in errors if "quote" in e.description.lower()]
        self.assertTrue(len(quote_errors) > 0)
    
    def test_detect_cmdlet_errors(self):
        """Test detection of cmdlet errors"""
        # Test unknown cmdlet
        errors = self.detector.detect_errors("Get-UnknownCmdlet")
        cmdlet_errors = [e for e in errors if e.error_type == ErrorType.CMDLET.value]
        self.assertTrue(len(cmdlet_errors) > 0)
        
        # Test cmdlet typo
        errors = self.detector.detect_errors("Get-Proces")
        typo_errors = [e for e in errors if "Get-Process" in e.suggested_fix]
        self.assertTrue(len(typo_errors) > 0)
        
        # Test incorrect case
        errors = self.detector.detect_errors("get-process")
        case_errors = [e for e in errors if "case" in e.description.lower()]
        self.assertTrue(len(case_errors) > 0)
    
    def test_detect_parameter_errors(self):
        """Test detection of parameter errors"""
        # Test unknown parameter
        errors = self.detector.detect_errors("Get-Process -UnknownParam value")
        param_errors = [e for e in errors if e.error_type == ErrorType.PARAMETER.value]
        self.assertTrue(len(param_errors) > 0)
        
        # Test parameter typo
        errors = self.detector.detect_errors("Get-Process -Nam notepad")
        typo_errors = [e for e in errors if "Name" in e.suggested_fix]
        self.assertTrue(len(typo_errors) > 0)
        
        # Test missing required parameter value
        errors = self.detector.detect_errors("Stop-Process -Name")
        missing_errors = [e for e in errors if "missing value" in e.description.lower()]
        self.assertTrue(len(missing_errors) > 0)
    
    def test_detect_logic_errors(self):
        """Test detection of logical errors"""
        # Test dangerous pipeline
        errors = self.detector.detect_errors("Get-ChildItem | Remove-Item")
        logic_errors = [e for e in errors if e.error_type == ErrorType.LOGIC.value]
        self.assertTrue(len(logic_errors) > 0)
        
        # Test using -Force without -WhatIf
        errors = self.detector.detect_errors("Remove-Item test.txt -Force")
        force_errors = [e for e in errors if "WhatIf" in e.suggested_fix]
        self.assertTrue(len(force_errors) > 0)
    
    def test_detect_security_issues(self):
        """Test detection of security issues"""
        # Test Invoke-Expression with variable
        errors = self.detector.detect_errors("Invoke-Expression $userInput")
        security_errors = [e for e in errors if e.error_type == ErrorType.SECURITY.value]
        self.assertTrue(len(security_errors) > 0)
        
        # Test mass deletion
        errors = self.detector.detect_errors("Remove-Item * -Recurse")
        deletion_errors = [e for e in errors if "deletion" in e.description.lower()]
        self.assertTrue(len(deletion_errors) > 0)
    
    def test_detect_performance_issues(self):
        """Test detection of performance issues"""
        # Test recursive listing without filtering
        errors = self.detector.detect_errors("Get-ChildItem -Recurse")
        perf_errors = [e for e in errors if e.error_type == ErrorType.PERFORMANCE.value]
        self.assertTrue(len(perf_errors) > 0)
    
    def test_suggest_corrections(self):
        """Test correction suggestions"""
        # Test cmdlet correction
        errors = [ErrorSuggestion(
            error_type=ErrorType.CMDLET.value,
            description="Unknown cmdlet 'Get-Proces'",
            suggested_fix="Did you mean 'Get-Process'?",
            confidence=0.8
        )]
        
        corrections = self.detector.suggest_corrections("Get-Proces", errors)
        self.assertTrue(len(corrections) > 0)
        self.assertIn("Get-Process", corrections[0])
    
    def test_cmdlet_info_retrieval(self):
        """Test cmdlet information retrieval"""
        # Test existing cmdlet
        info = self.detector.get_cmdlet_info("Get-Process")
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "Get-Process")
        self.assertIn("Name", info.parameters)
        
        # Test cmdlet alias
        info = self.detector.get_cmdlet_info("gps")
        self.assertIsNotNone(info)
        self.assertEqual(info.name, "Get-Process")
        
        # Test non-existent cmdlet
        info = self.detector.get_cmdlet_info("NonExistentCmdlet")
        self.assertIsNone(info)
    
    def test_validate_command_structure(self):
        """Test command structure validation"""
        # Test simple command
        analysis = self.detector.validate_command_structure("Get-Process")
        self.assertTrue(analysis['is_valid'])
        self.assertEqual(analysis['cmdlet_count'], 1)
        self.assertEqual(analysis['pipeline_stages'], 1)
        self.assertFalse(analysis['has_variables'])
        
        # Test complex command
        analysis = self.detector.validate_command_structure("Get-Process | Where-Object {$_.CPU -gt 50} | Sort-Object CPU")
        self.assertEqual(analysis['cmdlet_count'], 3)
        self.assertEqual(analysis['pipeline_stages'], 3)
        self.assertTrue(analysis['has_variables'])
        self.assertGreater(analysis['complexity_score'], 0.3)
    
    def test_levenshtein_distance(self):
        """Test Levenshtein distance calculation"""
        # Test identical strings
        distance = self.detector._levenshtein_distance("test", "test")
        self.assertEqual(distance, 0)
        
        # Test single character difference
        distance = self.detector._levenshtein_distance("test", "best")
        self.assertEqual(distance, 1)
        
        # Test multiple differences
        distance = self.detector._levenshtein_distance("kitten", "sitting")
        self.assertEqual(distance, 3)
    
    def test_find_cmdlet_suggestion(self):
        """Test cmdlet suggestion finding"""
        # Test known typo
        suggestion = self.detector._find_cmdlet_suggestion("Get-Proces")
        self.assertEqual(suggestion, "Get-Process")
        
        # Test similar cmdlet
        suggestion = self.detector._find_cmdlet_suggestion("Get-Proccess")
        self.assertEqual(suggestion, "Get-Process")
        
        # Test completely different string
        suggestion = self.detector._find_cmdlet_suggestion("CompletelyDifferent")
        self.assertIsNone(suggestion)
    
    def test_find_parameter_suggestion(self):
        """Test parameter suggestion finding"""
        valid_params = ["Name", "Id", "ProcessName", "ComputerName"]
        
        # Test close match
        suggestion = self.detector._find_parameter_suggestion("Nam", valid_params)
        self.assertEqual(suggestion, "Name")
        
        # Test exact match (different case)
        suggestion = self.detector._find_parameter_suggestion("name", valid_params)
        self.assertEqual(suggestion, "Name")
        
        # Test no close match
        suggestion = self.detector._find_parameter_suggestion("CompletelyDifferent", valid_params)
        self.assertIsNone(suggestion)
    
    def test_apply_corrections(self):
        """Test application of corrections"""
        # Test cmdlet correction
        error = ErrorSuggestion(
            error_type=ErrorType.CMDLET.value,
            description="Unknown cmdlet",
            suggested_fix="Did you mean 'Get-Process'?",
            confidence=0.8
        )
        
        corrected = self.detector._apply_cmdlet_correction("Get-Proces", error)
        self.assertEqual(corrected, "Get-Process")
        
        # Test syntax correction
        error = ErrorSuggestion(
            error_type=ErrorType.SYNTAX.value,
            description="Unclosed brace",
            suggested_fix="Add closing brace '}'",
            confidence=0.9
        )
        
        corrected = self.detector._apply_syntax_correction("Get-Process | Where-Object {$_.Name", error)
        self.assertEqual(corrected, "Get-Process | Where-Object {$_.Name}")
    
    def test_common_typos_correction(self):
        """Test common typos are corrected"""
        # Test various common typos
        typos_and_corrections = [
            ("get-proces", "Get-Process"),
            ("get-servic", "Get-Service"),
            ("copy-item", "Copy-Item"),
            ("remove-item", "Remove-Item")
        ]
        
        for typo, expected in typos_and_corrections:
            suggestion = self.detector._find_cmdlet_suggestion(typo)
            self.assertEqual(suggestion, expected)
    
    def test_parameter_case_sensitivity(self):
        """Test parameter case sensitivity detection"""
        errors = self.detector.detect_errors("Get-Process -name notepad")
        
        case_errors = [e for e in errors if "case" in e.description.lower() and e.error_type == ErrorType.PARAMETER.value]
        self.assertTrue(len(case_errors) > 0)
    
    def test_pipeline_error_detection(self):
        """Test pipeline-specific error detection"""
        # Test incomplete pipeline
        errors = self.detector.detect_errors("Get-Process |")
        pipeline_errors = [e for e in errors if "pipeline" in e.description.lower()]
        self.assertTrue(len(pipeline_errors) > 0)
        
        # Test pipeline starting with pipe
        errors = self.detector.detect_errors("| Sort-Object Name")
        start_errors = [e for e in errors if "pipe" in e.description.lower()]
        self.assertTrue(len(start_errors) > 0)
    
    def test_variable_syntax_errors(self):
        """Test variable syntax error detection"""
        # Test space after dollar sign
        errors = self.detector.detect_errors("Get-Process | Where-Object {$ _.Name -eq 'test'}")
        var_errors = [e for e in errors if "dollar" in e.description.lower()]
        self.assertTrue(len(var_errors) > 0)
    
    def test_security_pattern_detection(self):
        """Test security pattern detection"""
        security_commands = [
            "Invoke-Expression $input",
            "iex $userdata",
            "Remove-Item * -Recurse -Force",
            "Format C:",
            "Stop-Computer"
        ]
        
        for cmd in security_commands:
            errors = self.detector.detect_errors(cmd)
            security_errors = [e for e in errors if e.error_type == ErrorType.SECURITY.value]
            self.assertTrue(len(security_errors) > 0, f"No security errors detected for: {cmd}")
    
    def test_alternative_corrections(self):
        """Test generation of alternative corrections"""
        errors = [ErrorSuggestion(
            error_type=ErrorType.CMDLET.value,
            description="Unknown cmdlet",
            suggested_fix="Check spelling",
            confidence=0.6
        )]
        
        corrections = self.detector.suggest_corrections("Unknown-Cmdlet", errors)
        
        # Should include help commands as alternatives
        self.assertTrue(any("Get-Help" in correction for correction in corrections))
        self.assertTrue(any("Get-Command" in correction for correction in corrections))
    
    def test_complex_command_analysis(self):
        """Test analysis of complex commands"""
        complex_command = "Get-Process | Where-Object {$_.CPU -gt 50} | Sort-Object CPU -Descending | Select-Object -First 5 | Format-Table Name, CPU"
        
        analysis = self.detector.validate_command_structure(complex_command)
        
        self.assertEqual(analysis['cmdlet_count'], 5)
        self.assertEqual(analysis['pipeline_stages'], 5)
        self.assertTrue(analysis['has_variables'])
        self.assertGreater(analysis['complexity_score'], 0.5)
        self.assertGreater(analysis['parameter_count'], 3)


class TestPowerShellCmdlet(unittest.TestCase):
    """Test cases for PowerShellCmdlet dataclass"""
    
    def test_cmdlet_creation(self):
        """Test PowerShellCmdlet creation"""
        cmdlet = PowerShellCmdlet(
            name="Test-Cmdlet",
            parameters=["Param1", "Param2"],
            required_parameters=["Param1"],
            aliases=["test"]
        )
        
        self.assertEqual(cmdlet.name, "Test-Cmdlet")
        self.assertEqual(cmdlet.parameters, ["Param1", "Param2"])
        self.assertEqual(cmdlet.required_parameters, ["Param1"])
        self.assertEqual(cmdlet.aliases, ["test"])
    
    def test_cmdlet_defaults(self):
        """Test PowerShellCmdlet default values"""
        cmdlet = PowerShellCmdlet(
            name="Test-Cmdlet",
            parameters=["Param1"]
        )
        
        self.assertEqual(cmdlet.required_parameters, [])
        self.assertEqual(cmdlet.parameter_sets, [])
        self.assertEqual(cmdlet.aliases, [])
        self.assertIsNone(cmdlet.module)


class TestErrorType(unittest.TestCase):
    """Test cases for ErrorType enum"""
    
    def test_error_types(self):
        """Test ErrorType enum values"""
        self.assertEqual(ErrorType.SYNTAX.value, "syntax")
        self.assertEqual(ErrorType.PARAMETER.value, "parameter")
        self.assertEqual(ErrorType.CMDLET.value, "cmdlet")
        self.assertEqual(ErrorType.MODULE.value, "module")
        self.assertEqual(ErrorType.LOGIC.value, "logic")
        self.assertEqual(ErrorType.SECURITY.value, "security")
        self.assertEqual(ErrorType.PERFORMANCE.value, "performance")


if __name__ == '__main__':
    unittest.main()