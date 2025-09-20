"""Unit tests for AI Provider implementations"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import subprocess

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.providers import (
    AIProviderInterface, FallbackProvider, LlamaCppProvider, OllamaProvider
)
from config.models import ModelConfig
from interfaces.base import CommandContext, ErrorSuggestion, Platform, UserRole


class TestAIProviderInterface(unittest.TestCase):
    """Test cases for AIProviderInterface abstract class"""
    
    def test_interface_methods(self):
        """Test that interface defines required methods"""
        # Verify abstract methods exist
        self.assertTrue(hasattr(AIProviderInterface, 'is_available'))
        self.assertTrue(hasattr(AIProviderInterface, 'generate_command'))
        self.assertTrue(hasattr(AIProviderInterface, 'detect_errors'))
        self.assertTrue(hasattr(AIProviderInterface, 'suggest_corrections'))
    
    def test_cannot_instantiate_interface(self):
        """Test that abstract interface cannot be instantiated"""
        with self.assertRaises(TypeError):
            AIProviderInterface()


class TestFallbackProvider(unittest.TestCase):
    """Comprehensive test cases for FallbackProvider"""
    
    def setUp(self):
        self.provider = FallbackProvider()
        self.context = CommandContext(
            current_directory="/home/user",
            environment_variables={"PATH": "/usr/bin"},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
    
    def test_is_available(self):
        """Test that fallback provider is always available"""
        self.assertTrue(self.provider.is_available())
    
    def test_command_templates_loaded(self):
        """Test that command templates are properly loaded"""
        self.assertIsInstance(self.provider.command_templates, dict)
        self.assertIn('list', self.provider.command_templates)
        self.assertIn('find', self.provider.command_templates)
        self.assertIn('get', self.provider.command_templates)
    
    def test_generate_command_list_category(self):
        """Test command generation for 'list' category"""
        command = self.provider.generate_command("list files", self.context)
        self.assertEqual(command, "Get-ChildItem")
        
        command = self.provider.generate_command("list processes", self.context)
        self.assertEqual(command, "Get-Process")  # Pattern matching takes precedence
    
    def test_generate_command_find_category(self):
        """Test command generation for 'find' category"""
        command = self.provider.generate_command("find test", self.context)
        expected = 'Get-ChildItem -Recurse -Filter "*test*"'
        self.assertEqual(command, expected)
        
        command = self.provider.generate_command("find something else", self.context)
        expected = 'Get-ChildItem -Recurse -Filter "*something*"'
        self.assertEqual(command, expected)
    
    def test_generate_command_stop_category(self):
        """Test command generation for 'stop' category"""
        command = self.provider.generate_command("stop notepad", self.context)
        expected = 'Stop-Process -Name "notepad"'
        self.assertEqual(command, expected)
    
    def test_generate_command_start_category(self):
        """Test command generation for 'start' category"""
        command = self.provider.generate_command("start calculator", self.context)
        expected = 'Start-Process "calculator"'
        self.assertEqual(command, expected)
    
    def test_generate_command_get_category(self):
        """Test command generation for 'get' category"""
        command = self.provider.generate_command("get process", self.context)
        expected = 'Get-Process'  # Pattern matching takes precedence
        self.assertEqual(command, expected)
    
    def test_generate_command_set_category(self):
        """Test command generation for 'set' category"""
        command = self.provider.generate_command("set location", self.context)
        expected = 'Set-Location "location"'
        self.assertEqual(command, expected)
    
    def test_generate_command_help_category(self):
        """Test command generation for 'help' category"""
        command = self.provider.generate_command("help me", self.context)
        self.assertEqual(command, "Get-Help")
    
    def test_generate_command_pattern_matching(self):
        """Test command generation with pattern matching fallbacks"""
        # Test process pattern
        command = self.provider.generate_command("show me the running processes", self.context)
        self.assertEqual(command, "Get-Process")
        
        # Test service pattern
        command = self.provider.generate_command("display all services", self.context)
        self.assertEqual(command, "Get-Service")
        
        # Test file pattern
        command = self.provider.generate_command("show files in directory", self.context)
        self.assertEqual(command, "Get-ChildItem")
        
        # Test event pattern
        command = self.provider.generate_command("check event logs", self.context)
        self.assertEqual(command, "Get-EventLog -LogName System -Newest 10")
    
    def test_generate_command_default_fallback(self):
        """Test default fallback when no patterns match"""
        command = self.provider.generate_command("unknown random request", self.context)
        self.assertEqual(command, "Get-Help")
    
    def test_detect_errors_empty_command(self):
        """Test error detection for empty commands"""
        errors = self.provider.detect_errors("")
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, "empty")
        self.assertEqual(errors[0].confidence, 1.0)
    
    def test_detect_errors_mismatched_braces(self):
        """Test error detection for mismatched braces"""
        errors = self.provider.detect_errors("Get-Process | Where-Object {$_.Name -eq 'test'")
        
        brace_errors = [e for e in errors if "brace" in e.description.lower()]
        self.assertTrue(len(brace_errors) > 0)
        self.assertEqual(brace_errors[0].error_type, "syntax")
        self.assertEqual(brace_errors[0].confidence, 0.9)
    
    def test_detect_errors_cmdlet_case(self):
        """Test error detection for cmdlet case issues"""
        errors = self.provider.detect_errors("get-process")
        
        case_errors = [e for e in errors if "cmdlet" in e.error_type.lower()]
        self.assertTrue(len(case_errors) > 0)
        self.assertEqual(case_errors[0].confidence, 0.7)
    
    def test_detect_errors_valid_command(self):
        """Test error detection for valid commands"""
        errors = self.provider.detect_errors("Get-Process")
        
        # Should not detect case errors for properly formatted cmdlets
        case_errors = [e for e in errors if "cmdlet" in e.error_type.lower()]
        self.assertEqual(len(case_errors), 0)
    
    def test_suggest_corrections_common_cmdlets(self):
        """Test correction suggestions for common cmdlets"""
        corrections = self.provider.suggest_corrections("get-process", "not found")
        self.assertIn("Get-Process", corrections)
        
        corrections = self.provider.suggest_corrections("get-service", "not found")
        self.assertIn("Get-Service", corrections)
        
        corrections = self.provider.suggest_corrections("get-childitem", "not found")
        self.assertIn("Get-ChildItem", corrections)
    
    def test_suggest_corrections_fallback(self):
        """Test fallback correction suggestions"""
        corrections = self.provider.suggest_corrections("unknown-command", "not found")
        
        self.assertIn("Get-Help", corrections)
        self.assertIn("Get-Command", corrections)
        self.assertTrue(len(corrections) <= 3)
    
    def test_suggest_corrections_limit(self):
        """Test that corrections are limited to 3 items"""
        corrections = self.provider.suggest_corrections("test", "error")
        self.assertTrue(len(corrections) <= 3)


class TestLlamaCppProvider(unittest.TestCase):
    """Comprehensive test cases for LlamaCppProvider"""
    
    def setUp(self):
        self.config = ModelConfig(
            model_type="llama-cpp",
            model_path="/tmp/test_model.gguf",
            context_length=2048,
            temperature=0.7,
            max_tokens=256,
            threads=4,
            gpu_layers=0
        )
        
        self.context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=["Get-Process"],
            active_modules=["Microsoft.PowerShell.Management"],
            platform=Platform.LINUX
        )
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_initialization_success(self, mock_exists, mock_llama_cpp):
        """Test successful initialization"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        
        self.assertTrue(provider.model_loaded)
        self.assertTrue(provider.is_available())
        mock_llama_cpp.Llama.assert_called_once_with(
            model_path="/tmp/test_model.gguf",
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )
    
    def test_initialization_no_library(self):
        """Test initialization when llama-cpp-python is not available"""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'llama_cpp'")):
            provider = LlamaCppProvider(self.config)
            
            self.assertFalse(provider.model_loaded)
            self.assertFalse(provider.is_available())
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_initialization_model_not_found(self, mock_exists, mock_llama_cpp):
        """Test initialization when model file doesn't exist"""
        mock_exists.return_value = False
        
        provider = LlamaCppProvider(self.config)
        
        self.assertFalse(provider.model_loaded)
        self.assertFalse(provider.is_available())
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_initialization_model_load_error(self, mock_exists, mock_llama_cpp):
        """Test initialization when model loading fails"""
        mock_exists.return_value = True
        mock_llama_cpp.Llama.side_effect = Exception("Model load error")
        
        provider = LlamaCppProvider(self.config)
        
        self.assertFalse(provider.model_loaded)
        self.assertFalse(provider.is_available())
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_generate_command_success(self, mock_exists, mock_llama_cpp):
        """Test successful command generation"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': 'Get-Process | Sort-Object CPU -Descending'}]
        }
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        result = provider.generate_command("list high CPU processes", self.context)
        
        self.assertEqual(result, "Get-Process | Sort-Object CPU -Descending")
        mock_model.assert_called_once()
        
        # Verify call parameters
        call_args = mock_model.call_args[0]
        call_kwargs = mock_model.call_args[1]
        
        self.assertIn("list high CPU processes", call_args[0])
        self.assertEqual(call_kwargs['max_tokens'], 256)
        self.assertEqual(call_kwargs['temperature'], 0.7)
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_generate_command_not_available(self, mock_exists, mock_llama_cpp):
        """Test command generation when provider is not available"""
        mock_exists.return_value = False
        
        provider = LlamaCppProvider(self.config)
        
        with self.assertRaises(RuntimeError):
            provider.generate_command("test", self.context)
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_detect_errors_success(self, mock_exists, mock_llama_cpp):
        """Test successful error detection"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': '[{"type": "syntax", "description": "Missing brace", "fix": "Add closing brace", "confidence": 0.9}]'}]
        }
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        errors = provider.detect_errors("Get-Process | Where-Object {$_.Name")
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, "syntax")
        self.assertEqual(errors[0].description, "Missing brace")
        self.assertEqual(errors[0].confidence, 0.9)
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_detect_errors_invalid_json(self, mock_exists, mock_llama_cpp):
        """Test error detection with invalid JSON response"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': 'Invalid JSON response'}]
        }
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        errors = provider.detect_errors("test command")
        
        self.assertEqual(len(errors), 0)
    
    @patch('ai_engine.providers.llama_cpp', create=True)
    @patch('pathlib.Path.exists')
    def test_suggest_corrections_success(self, mock_exists, mock_llama_cpp):
        """Test successful correction suggestions"""
        mock_exists.return_value = True
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': 'Get-Process\nGet-Process -Name test\nGet-Process | Sort-Object Name'}]
        }
        mock_llama_cpp.Llama.return_value = mock_model
        
        provider = LlamaCppProvider(self.config)
        corrections = provider.suggest_corrections("get-proces", "cmdlet not found")
        
        self.assertEqual(len(corrections), 3)
        self.assertIn("Get-Process", corrections)
        self.assertIn("Get-Process -Name test", corrections)


class TestOllamaProvider(unittest.TestCase):
    """Comprehensive test cases for OllamaProvider"""
    
    def setUp(self):
        self.config = ModelConfig(
            model_type="ollama",
            model_path="llama2",
            temperature=0.7,
            max_tokens=256
        )
        
        self.context = CommandContext(
            current_directory="/home/user",
            environment_variables={},
            user_role=UserRole.USER,
            recent_commands=[],
            active_modules=[],
            platform=Platform.LINUX
        )
    
    @patch('subprocess.run')
    def test_initialization_success(self, mock_run):
        """Test successful initialization"""
        mock_run.return_value = Mock(returncode=0, stdout="llama2\ncodellama\n")
        
        provider = OllamaProvider(self.config)
        
        self.assertTrue(provider.is_available())
        mock_run.assert_called_once_with(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_initialization_ollama_not_found(self, mock_run):
        """Test initialization when Ollama is not installed"""
        mock_run.side_effect = FileNotFoundError()
        
        provider = OllamaProvider(self.config)
        
        self.assertFalse(provider.is_available())
    
    @patch('subprocess.run')
    def test_initialization_ollama_timeout(self, mock_run):
        """Test initialization when Ollama times out"""
        mock_run.side_effect = subprocess.TimeoutExpired("ollama", 10)
        
        provider = OllamaProvider(self.config)
        
        self.assertFalse(provider.is_available())
    
    @patch('subprocess.run')
    def test_initialization_model_not_available(self, mock_run):
        """Test initialization when requested model is not available"""
        mock_run.return_value = Mock(returncode=0, stdout="codellama\nother-model\n")
        
        provider = OllamaProvider(self.config)
        
        self.assertFalse(provider.is_available())
    
    @patch('subprocess.run')
    def test_extract_model_name(self, mock_run):
        """Test model name extraction from config"""
        mock_run.return_value = Mock(returncode=0, stdout="test-model\n")
        
        # Test with simple name
        config = ModelConfig(model_path="test-model")
        provider = OllamaProvider(config)
        self.assertEqual(provider.model_name, "test-model")
        
        # Test with path-like name
        config = ModelConfig(model_path="models/test-model.gguf")
        provider = OllamaProvider(config)
        self.assertEqual(provider.model_name, "test-model")
    
    @patch('subprocess.run')
    def test_generate_command_success(self, mock_run):
        """Test successful command generation"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "Get-Process | Sort-Object CPU"}')  # generate call
        ]
        
        provider = OllamaProvider(self.config)
        result = provider.generate_command("list processes by CPU", self.context)
        
        self.assertEqual(result, "Get-Process | Sort-Object CPU")
        
        # Verify generate call
        generate_call = mock_run.call_args_list[1]
        self.assertEqual(generate_call[0][0], ["ollama", "generate", "--format", "json"])
        
        # Verify input data
        input_data = json.loads(generate_call[1]['input'])
        self.assertEqual(input_data['model'], 'llama2')
        self.assertIn('list processes by CPU', input_data['prompt'])
    
    @patch('subprocess.run')
    def test_generate_command_not_available(self, mock_run):
        """Test command generation when provider is not available"""
        mock_run.return_value = Mock(returncode=1, stderr="Ollama not running")
        
        provider = OllamaProvider(self.config)
        
        with self.assertRaises(RuntimeError):
            provider.generate_command("test", self.context)
    
    @patch('subprocess.run')
    def test_generate_command_generation_error(self, mock_run):
        """Test command generation when Ollama generation fails"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=1, stderr="Generation failed")  # generate call
        ]
        
        provider = OllamaProvider(self.config)
        
        with self.assertRaises(RuntimeError):
            provider.generate_command("test", self.context)
    
    @patch('subprocess.run')
    def test_detect_errors_success(self, mock_run):
        """Test successful error detection"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "[{\\"type\\": \\"syntax\\", \\"description\\": \\"Missing parameter\\", \\"fix\\": \\"Add parameter value\\", \\"confidence\\": 0.8}]"}')  # detect call
        ]
        
        provider = OllamaProvider(self.config)
        errors = provider.detect_errors("Get-Process -Name")
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].error_type, "syntax")
        self.assertEqual(errors[0].description, "Missing parameter")
    
    @patch('subprocess.run')
    def test_detect_errors_invalid_response(self, mock_run):
        """Test error detection with invalid response"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "Invalid JSON"}')  # detect call
        ]
        
        provider = OllamaProvider(self.config)
        errors = provider.detect_errors("test command")
        
        self.assertEqual(len(errors), 0)
    
    @patch('subprocess.run')
    def test_suggest_corrections_success(self, mock_run):
        """Test successful correction suggestions"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "Get-Process\\nGet-Process -Name test\\nGet-Service"}')  # corrections call
        ]
        
        provider = OllamaProvider(self.config)
        corrections = provider.suggest_corrections("get-proces", "not found")
        
        self.assertEqual(len(corrections), 3)
        self.assertIn("Get-Process", corrections)
        self.assertIn("Get-Process -Name test", corrections)
        self.assertIn("Get-Service", corrections)
    
    @patch('subprocess.run')
    def test_suggest_corrections_limit(self, mock_run):
        """Test that corrections are limited to 3 items"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="llama2\n"),  # list call
            Mock(returncode=0, stdout='{"response": "Correction1\\nCorrection2\\nCorrection3\\nCorrection4\\nCorrection5"}')  # corrections call
        ]
        
        provider = OllamaProvider(self.config)
        corrections = provider.suggest_corrections("test", "error")
        
        self.assertEqual(len(corrections), 3)


if __name__ == '__main__':
    unittest.main()