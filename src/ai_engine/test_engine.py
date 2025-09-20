"""Unit tests for AI Engine implementation"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.engine import AIEngine
from ai_engine.providers import FallbackProvider, LlamaCppProvider, OllamaProvider
from config.models import ModelConfig
from interfaces.base import (
    CommandContext, CommandSuggestion, ErrorSuggestion, ExecutionResult,
    Platform, UserRole
)


class TestAIEngine(unittest.TestCase):
    """Test cases for AIEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = ModelConfig(
            model_type="fallback",
            model_path="/tmp/test_model.gguf",
            context_length=2048,
            temperature=0.7,
            max_tokens=256
        )
        
        self.context = CommandContext(
            current_directory="/home/user",
            environment_variables={"PATH": "/usr/bin"},
            user_role=UserRole.USER,
            recent_commands=["Get-Process", "Get-Service"],
            active_modules=["Microsoft.PowerShell.Management"],
            platform=Platform.LINUX,
            session_id="test_session"
        )
    
    def test_initialization_with_fallback(self):
        """Test AI engine initialization with fallback provider"""
        engine = AIEngine(self.config)
        
        self.assertIsNotNone(engine.provider)
        self.assertIsInstance(engine.provider, FallbackProvider)
        self.assertTrue(engine.provider.is_available())
    
    @patch('ai_engine.engine.LlamaCppProvider')
    def test_initialization_with_llama_cpp(self, mock_provider_class):
        """Test AI engine initialization with LLaMA-CPP provider"""
        # Mock successful provider initialization
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider_class.return_value = mock_provider
        
        config = ModelConfig(model_type="llama-cpp")
        engine = AIEngine(config)
        
        self.assertEqual(engine.provider, mock_provider)
        mock_provider_class.assert_called_once_with(config)
    
    @patch('ai_engine.engine.OllamaProvider')
    def test_initialization_with_ollama(self, mock_provider_class):
        """Test AI engine initialization with Ollama provider"""
        # Mock successful provider initialization
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider_class.return_value = mock_provider
        
        config = ModelConfig(model_type="ollama")
        engine = AIEngine(config)
        
        self.assertEqual(engine.provider, mock_provider)
        mock_provider_class.assert_called_once_with(config)
    
    def test_translate_natural_language_success(self):
        """Test successful natural language translation"""
        engine = AIEngine(self.config)
        
        # Mock provider response
        engine.provider.generate_command = Mock(return_value="Get-Process | Sort-Object CPU -Descending")
        
        result = engine.translate_natural_language("show high CPU processes", self.context)
        
        self.assertIsInstance(result, CommandSuggestion)
        self.assertEqual(result.original_input, "show high CPU processes")
        # Enhanced translation should now handle this with high confidence
        self.assertIn("Get-Process", result.generated_command)
        self.assertGreater(result.confidence_score, 0.0)
        self.assertIsInstance(result.explanation, str)
        self.assertIsInstance(result.alternatives, list)
    
    def test_translate_natural_language_with_provider_error(self):
        """Test natural language translation when provider fails"""
        engine = AIEngine(self.config)
        
        # Mock provider to raise exception
        engine.provider.generate_command = Mock(side_effect=Exception("Provider error"))
        
        result = engine.translate_natural_language("unknown random command", self.context)
        
        self.assertIsInstance(result, CommandSuggestion)
        # Enhanced translation should still work even if AI provider fails
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertIsInstance(result.explanation, str)
    
    def test_detect_command_errors(self):
        """Test command error detection"""
        engine = AIEngine(self.config)
        
        # Test with command that has syntax errors
        command = "Get-Process | Where-Object {$_.Name -eq 'test'"  # Missing closing brace
        
        errors = engine.detect_command_errors(command)
        
        self.assertIsInstance(errors, list)
        # Should detect the missing brace
        brace_errors = [e for e in errors if "brace" in e.description.lower()]
        self.assertTrue(len(brace_errors) > 0)
    
    def test_detect_command_errors_with_ai_provider(self):
        """Test error detection with AI provider"""
        engine = AIEngine(self.config)
        
        # Mock AI provider error detection
        mock_ai_errors = [
            ErrorSuggestion(
                error_type="syntax",
                description="Missing parameter value",
                suggested_fix="Add value after -Name parameter",
                confidence=0.8
            )
        ]
        
        # Replace with mock provider that supports error detection
        mock_provider = Mock()
        mock_provider.detect_errors.return_value = mock_ai_errors
        # Make sure it's not the fallback provider
        mock_provider.__class__.__name__ = "MockProvider"
        engine.provider = mock_provider
        
        errors = engine.detect_command_errors("Get-Process -Name")
        
        # Should have AI errors plus any rule-based errors
        self.assertGreaterEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, "syntax")
        self.assertIn("parameter", errors[0].description.lower())
    
    def test_suggest_corrections(self):
        """Test correction suggestions"""
        engine = AIEngine(self.config)
        
        command = "get-proces"  # Misspelled cmdlet
        error = "Cmdlet not found"
        
        corrections = engine.suggest_corrections(command, error)
        
        self.assertIsInstance(corrections, list)
        self.assertTrue(len(corrections) > 0)
    
    def test_suggest_corrections_with_ai_provider(self):
        """Test corrections with AI provider"""
        engine = AIEngine(self.config)
        
        # Mock AI provider corrections
        mock_corrections = ["Get-Process", "Get-Process -Name test"]
        
        mock_provider = Mock()
        mock_provider.suggest_corrections.return_value = mock_corrections
        # Make sure it's not the fallback provider
        mock_provider.__class__.__name__ = "MockProvider"
        engine.provider = mock_provider
        
        corrections = engine.suggest_corrections("get-proces", "not found")
        
        # Enhanced error detection should now provide corrections
        self.assertIsInstance(corrections, list)
        self.assertTrue(len(corrections) > 0)
    
    def test_update_context(self):
        """Test context update functionality"""
        engine = AIEngine(self.config)
        
        command = "Get-Process"
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Process list",
            stderr="",
            execution_time=1.5,
            platform=Platform.LINUX,
            sandbox_used=False,
            correlation_id="test_correlation"
        )
        
        # Should not raise exception
        engine.update_context(command, result)
        
        # Verify context history was updated
        self.assertIn("test_correlation", engine.context_history)
    
    def test_build_translation_prompt(self):
        """Test prompt building for translation"""
        engine = AIEngine(self.config)
        
        prompt = engine._build_translation_prompt("list processes", self.context)
        
        self.assertIn("list processes", prompt)
        self.assertIn(self.context.current_directory, prompt)
        self.assertIn(self.context.platform.value, prompt)
        self.assertIn("Get-Process", prompt)  # Recent command should be included
    
    def test_parse_command_response(self):
        """Test parsing of AI provider response"""
        engine = AIEngine(self.config)
        
        # Test with clean response
        response = "Get-Process | Sort-Object CPU -Descending"
        suggestion = engine._parse_command_response(response, "show high CPU processes")
        
        self.assertEqual(suggestion.generated_command, response)
        self.assertGreater(suggestion.confidence_score, 0.0)
        
        # Test with code block response
        response_with_code = "```powershell\nGet-Service\n```"
        suggestion = engine._parse_command_response(response_with_code, "list services")
        
        self.assertEqual(suggestion.generated_command, "Get-Service")
    
    def test_calculate_confidence(self):
        """Test confidence score calculation"""
        engine = AIEngine(self.config)
        
        # Test with valid PowerShell command
        high_confidence = engine._calculate_confidence("Get-Process", "list processes")
        self.assertGreater(high_confidence, 0.5)
        
        # Test with suspicious command
        low_confidence = engine._calculate_confidence("rm -rf /", "delete files")
        self.assertLess(low_confidence, 0.5)
    
    def test_generate_explanation(self):
        """Test explanation generation"""
        engine = AIEngine(self.config)
        
        explanation = engine._generate_explanation("Get-Process", "list processes")
        self.assertIn("Retrieves", explanation)
        self.assertIn("list processes", explanation)
    
    def test_generate_alternatives(self):
        """Test alternative command generation"""
        engine = AIEngine(self.config)
        
        alternatives = engine._generate_alternatives("Get-Process", "list processes")
        self.assertIsInstance(alternatives, list)
        self.assertTrue(len(alternatives) <= 3)
    
    def test_detect_syntax_errors(self):
        """Test rule-based syntax error detection"""
        engine = AIEngine(self.config)
        
        # Test mismatched parentheses
        errors = engine._detect_syntax_errors("Get-Process | Where-Object {$_.Name -eq 'test'")
        brace_errors = [e for e in errors if "brace" in e.description.lower()]
        self.assertTrue(len(brace_errors) > 0)
        
        # Test invalid parameter syntax
        errors = engine._detect_syntax_errors("Get-Process -Name -Path")
        param_errors = [e for e in errors if "parameter" in e.description.lower()]
        self.assertTrue(len(param_errors) > 0)
    
    def test_generate_rule_based_corrections(self):
        """Test rule-based correction generation"""
        engine = AIEngine(self.config)
        
        corrections = engine._generate_rule_based_corrections("get-proces", "cmdlet not found")
        self.assertTrue(any("Get-Process" in correction for correction in corrections))
    
    def test_deduplicate_errors(self):
        """Test error deduplication"""
        engine = AIEngine(self.config)
        
        errors = [
            ErrorSuggestion("syntax", "Missing brace", "Add brace", 0.9),
            ErrorSuggestion("syntax", "Missing brace", "Add closing brace", 0.8),  # Duplicate
            ErrorSuggestion("parameter", "Invalid param", "Fix param", 0.7)
        ]
        
        unique_errors = engine._deduplicate_errors(errors)
        self.assertEqual(len(unique_errors), 2)
    
    def test_get_provider_info(self):
        """Test provider information retrieval"""
        engine = AIEngine(self.config)
        
        info = engine.get_provider_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn('type', info)
        self.assertIn('available', info)
        self.assertIn('model_type', info)
    
    def test_enhanced_translation_integration(self):
        """Test integration of enhanced translation with AI engine"""
        engine = AIEngine(self.config)
        
        # Test that enhanced translation is used for high-confidence matches
        result = engine.translate_natural_language("list processes", self.context)
        
        self.assertEqual(result.generated_command, "Get-Process")
        self.assertGreater(result.confidence_score, 0.6)
        self.assertIn("processes", result.explanation.lower())
    
    def test_command_analysis_integration(self):
        """Test command analysis functionality"""
        engine = AIEngine(self.config)
        
        analysis = engine.get_command_analysis("Get-Process | Sort-Object CPU")
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('complexity_score', analysis)
        self.assertIn('risk_level', analysis)
    
    def test_category_suggestions_integration(self):
        """Test category-based suggestions"""
        engine = AIEngine(self.config)
        
        suggestions = engine.get_suggestions_by_category("process")
        
        self.assertIsInstance(suggestions, list)
        self.assertIn("Get-Process", suggestions)
    
    def test_enhanced_error_detection_integration(self):
        """Test enhanced error detection integration"""
        engine = AIEngine(self.config)
        
        # Test with a command that has multiple error types
        errors = engine.detect_command_errors("get-proces -Nam")
        
        self.assertGreater(len(errors), 0)
        # Should detect both cmdlet case and parameter issues
        error_types = {e.error_type for e in errors}
        self.assertIn("cmdlet", error_types)
    
    def test_command_structure_validation(self):
        """Test command structure validation"""
        engine = AIEngine(self.config)
        
        analysis = engine.validate_command_structure("Get-Process | Sort-Object CPU")
        
        self.assertIsInstance(analysis, dict)
        self.assertIn('cmdlet_count', analysis)
        self.assertIn('pipeline_stages', analysis)
        self.assertEqual(analysis['cmdlet_count'], 2)
        self.assertEqual(analysis['pipeline_stages'], 2)
    
    def test_cmdlet_info_integration(self):
        """Test cmdlet information retrieval"""
        engine = AIEngine(self.config)
        
        info = engine.get_cmdlet_info("Get-Process")
        
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], "Get-Process")
        self.assertIn('parameters', info)
        self.assertIn('aliases', info)
    
    def test_command_safety_analysis(self):
        """Test command safety analysis"""
        engine = AIEngine(self.config)
        
        # Test safe command
        safe_analysis = engine.analyze_command_safety("Get-Process")
        self.assertTrue(safe_analysis['is_safe'])
        self.assertEqual(safe_analysis['risk_level'], 'low')
        
        # Test risky command
        risky_analysis = engine.analyze_command_safety("Remove-Item * -Recurse -Force")
        self.assertFalse(risky_analysis['is_safe'])
        self.assertEqual(risky_analysis['risk_level'], 'high')
    
    def test_enhanced_corrections_integration(self):
        """Test enhanced correction suggestions"""
        engine = AIEngine(self.config)
        
        corrections = engine.suggest_corrections("Get-Proces -Nam notepad", "cmdlet error")
        
        self.assertIsInstance(corrections, list)
        self.assertTrue(len(corrections) > 0)
        # Should suggest corrected version
        self.assertTrue(any("Get-Process" in correction for correction in corrections))
    
    def test_reload_provider(self):
        """Test provider reloading"""
        engine = AIEngine(self.config)
        
        result = engine.reload_provider()
        
        # Should succeed with fallback provider
        self.assertTrue(result)
        self.assertIsNotNone(engine.provider)


class TestFallbackProvider(unittest.TestCase):
    """Test cases for FallbackProvider"""
    
    def setUp(self):
        self.provider = FallbackProvider()
        self.context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
    
    def test_is_available(self):
        """Test that fallback provider is always available"""
        self.assertTrue(self.provider.is_available())
    
    def test_generate_command_with_keywords(self):
        """Test command generation with keyword matching"""
        # Test list keyword
        command = self.provider.generate_command("list files", self.context)
        self.assertIn("Get-", command)
        
        # Test process keyword
        command = self.provider.generate_command("show process info", self.context)
        self.assertEqual(command, "Get-Process")
        
        # Test service keyword
        command = self.provider.generate_command("list services", self.context)
        self.assertEqual(command, "Get-Service")
    
    def test_generate_command_fallback(self):
        """Test command generation fallback"""
        command = self.provider.generate_command("unknown request", self.context)
        self.assertEqual(command, "Get-Help")
    
    def test_detect_errors(self):
        """Test basic error detection"""
        # Test empty command
        errors = self.provider.detect_errors("")
        self.assertTrue(any(e.error_type == "empty" for e in errors))
        
        # Test mismatched braces
        errors = self.provider.detect_errors("Get-Process | Where-Object {$_.Name")
        self.assertTrue(any("brace" in e.description.lower() for e in errors))
    
    def test_suggest_corrections(self):
        """Test basic correction suggestions"""
        corrections = self.provider.suggest_corrections("get-process", "not found")
        self.assertIn("Get-Process", corrections)
        
        # Test fallback corrections
        corrections = self.provider.suggest_corrections("unknown", "error")
        self.assertIn("Get-Help", corrections)


class TestLlamaCppProvider(unittest.TestCase):
    """Test cases for LlamaCppProvider"""
    
    def setUp(self):
        self.config = ModelConfig(
            model_type="llama-cpp",
            model_path="/tmp/test_model.gguf"
        )
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_initialization_success(self, mock_exists, mock_llama_cpp):
        """Test successful LLaMA-CPP initialization"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        
        self.assertTrue(provider.is_available())
        mock_llama_cpp.Llama.assert_called_once()
    
    def test_initialization_no_library(self):
        """Test initialization when llama-cpp-python is not installed"""
        with patch('builtins.__import__', side_effect=ImportError):
            provider = LlamaCppProvider(self.config)
            self.assertFalse(provider.is_available())
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_generate_command(self, mock_exists, mock_llama_cpp):
        """Test command generation with LLaMA-CPP"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': 'Get-Process | Sort-Object CPU -Descending'}]
        }
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
        
        result = provider.generate_command("list high CPU processes", context)
        
        self.assertEqual(result, "Get-Process | Sort-Object CPU -Descending")
        mock_model.assert_called_once()


class TestOllamaProvider(unittest.TestCase):
    """Test cases for OllamaProvider"""
    
    def setUp(self):
        self.config = ModelConfig(
            model_type="ollama",
            model_path="llama2"
        )
    
    @patch('subprocess.run')
    def test_initialization_success(self, mock_run):
        """Test successful Ollama initialization"""
        mock_run.return_value = Mock(returncode=0, stdout="llama2\n")
        
        provider = OllamaProvider(self.config)
        
        self.assertTrue(provider.is_available())
    
    @patch('subprocess.run')
    def test_initialization_ollama_not_found(self, mock_run):
        """Test initialization when Ollama is not found"""
        mock_run.side_effect = FileNotFoundError()
        
        provider = OllamaProvider(self.config)
        
        self.assertFalse(provider.is_available())
    
    @patch('subprocess.run')
    def test_generate_command(self, mock_run):
        """Test command generation with Ollama"""
        # Mock ollama list call
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "Get-Process"}')  # generate call
        ]
        
        provider = OllamaProvider(self.config)
        context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
        
        result = provider.generate_command("list processes", context)
        
        self.assertEqual(result, "Get-Process")


if __name__ == '__main__':
    unittest.main()