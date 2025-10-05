"""AI Provider implementations for different local AI frameworks

This module provides concrete implementations for various local AI providers
including LLaMA-CPP, Ollama, and fallback rule-based processing.
"""

import logging
import json
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import CommandContext, ErrorSuggestion, ExecutionResult
from config.models import ModelConfig


logger = logging.getLogger(__name__)


class AIProviderInterface(ABC):
    """Abstract interface for AI providers"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and ready"""
        pass
    
    @abstractmethod
    def generate_command(self, prompt: str, context: CommandContext) -> str:
        """Generate PowerShell command from prompt"""
        pass
    
    @abstractmethod
    def detect_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect errors in PowerShell command"""
        pass
    
    @abstractmethod
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """Suggest corrections for command errors"""
        pass


class LlamaCppProvider(AIProviderInterface):
    """LLaMA-CPP provider for local AI inference"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_loaded = False
        self._llama_cpp = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize LLaMA-CPP model"""
        try:
            # Try to import llama-cpp-python
            import llama_cpp
            self._llama_cpp = llama_cpp
            
            # Check if model file exists
            model_path = Path(self.config.model_path)
            if not model_path.exists():
                logger.warning(f"Model file not found: {self.config.model_path}")
                return
            
            # Initialize model
            self.model = llama_cpp.Llama(
                model_path=str(model_path),
                n_ctx=self.config.context_length,
                n_threads=self.config.threads,
                n_gpu_layers=self.config.gpu_layers,
                verbose=False
            )
            
            self.model_loaded = True
            logger.info("LLaMA-CPP model loaded successfully")
            
        except ImportError:
            logger.warning("llama-cpp-python not installed, provider unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize LLaMA-CPP model: {e}")
    
    def is_available(self) -> bool:
        """Check if LLaMA-CPP is available"""
        return self.model_loaded and self._llama_cpp is not None
    
    def generate_command(self, prompt: str, context: CommandContext) -> str:
        """Generate PowerShell command using LLaMA-CPP"""
        if not self.is_available():
            raise RuntimeError("LLaMA-CPP provider not available")
        
        try:
            # Generate response
            response = self.model(
                prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stop=["User:", "Human:", "\n\n"],
                echo=False
            )
            
            generated_text = response['choices'][0]['text'].strip()
            logger.debug(f"LLaMA-CPP generated: {generated_text[:100]}...")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating command with LLaMA-CPP: {e}")
            raise
    
    def detect_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect errors using LLaMA-CPP"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""Analyze this PowerShell command for errors:
Command: {command}

List any syntax errors, logical issues, or potential problems.
Respond with a JSON array of errors in this format:
[{{"type": "syntax", "description": "error description", "fix": "suggested fix", "confidence": 0.8}}]

If no errors found, respond with: []
"""
            
            response = self.model(
                prompt,
                max_tokens=256,
                temperature=0.3,
                stop=["\n\n"],
                echo=False
            )
            
            result_text = response['choices'][0]['text'].strip()
            
            # Try to parse JSON response
            try:
                errors_data = json.loads(result_text)
                errors = []
                
                for error_data in errors_data:
                    errors.append(ErrorSuggestion(
                        error_type=error_data.get('type', 'unknown'),
                        description=error_data.get('description', ''),
                        suggested_fix=error_data.get('fix', ''),
                        confidence=error_data.get('confidence', 0.5)
                    ))
                
                return errors
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse error detection response as JSON")
                return []
            
        except Exception as e:
            logger.error(f"Error detecting errors with LLaMA-CPP: {e}")
            return []
    
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """Suggest corrections using LLaMA-CPP"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""Fix this PowerShell command:
Original command: {command}
Error: {error}

Provide 2-3 corrected versions of the command.
Respond with only the corrected commands, one per line.
"""
            
            response = self.model(
                prompt,
                max_tokens=200,
                temperature=0.5,
                stop=["\n\n"],
                echo=False
            )
            
            corrections = response['choices'][0]['text'].strip().split('\n')
            return [cmd.strip() for cmd in corrections if cmd.strip()]
            
        except Exception as e:
            logger.error(f"Error suggesting corrections with LLaMA-CPP: {e}")
            return []


class OllamaProvider(AIProviderInterface):
    """Ollama provider for local AI inference"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_name = self._extract_model_name()
        self._check_availability()
    
    def _extract_model_name(self) -> str:
        """Extract model name from config"""
        # For Ollama, model_path might be just the model name
        model_path = Path(self.config.model_path)
        if model_path.suffix:
            return model_path.stem
        return self.config.model_path or "llama2"
    
    def _check_availability(self) -> None:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.available = result.returncode == 0
            
            if self.available:
                # Check if our model is available
                if self.model_name not in result.stdout:
                    logger.warning(f"Model {self.model_name} not found in Ollama")
                    self.available = False
                else:
                    logger.info(f"Ollama provider available with model: {self.model_name}")
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Ollama not found or not responding")
            self.available = False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        return getattr(self, 'available', False)
    
    def generate_command(self, prompt: str, context: CommandContext) -> str:
        """Generate PowerShell command using Ollama"""
        if not self.is_available():
            raise RuntimeError("Ollama provider not available")
        
        try:
            # Prepare Ollama request
            ollama_prompt = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            # Call Ollama API
            result = subprocess.run(
                ["ollama", "generate", "--format", "json"],
                input=json.dumps(ollama_prompt),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Ollama generation failed: {result.stderr}")
            
            response_data = json.loads(result.stdout)
            generated_text = response_data.get('response', '').strip()
            
            logger.debug(f"Ollama generated: {generated_text[:100]}...")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating command with Ollama: {e}")
            raise
    
    def detect_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect errors using Ollama"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""Analyze this PowerShell command for errors:
{command}

List any syntax errors or issues. Format as JSON array:
[{{"type": "error_type", "description": "what's wrong", "fix": "how to fix", "confidence": 0.8}}]
"""
            
            ollama_prompt = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 256}
            }
            
            result = subprocess.run(
                ["ollama", "generate", "--format", "json"],
                input=json.dumps(ollama_prompt),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                result_text = response_data.get('response', '').strip()
                
                try:
                    errors_data = json.loads(result_text)
                    errors = []
                    
                    for error_data in errors_data:
                        errors.append(ErrorSuggestion(
                            error_type=error_data.get('type', 'unknown'),
                            description=error_data.get('description', ''),
                            suggested_fix=error_data.get('fix', ''),
                            confidence=error_data.get('confidence', 0.5)
                        ))
                    
                    return errors
                    
                except json.JSONDecodeError:
                    pass
            
            return []
            
        except Exception as e:
            logger.error(f"Error detecting errors with Ollama: {e}")
            return []
    
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """Suggest corrections using Ollama"""
        if not self.is_available():
            return []
        
        try:
            prompt = f"""Fix this PowerShell command:
Command: {command}
Error: {error}

Provide 2-3 corrected commands, one per line:
"""
            
            ollama_prompt = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "num_predict": 200}
            }
            
            result = subprocess.run(
                ["ollama", "generate", "--format", "json"],
                input=json.dumps(ollama_prompt),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                corrections_text = response_data.get('response', '').strip()
                corrections = [cmd.strip() for cmd in corrections_text.split('\n') if cmd.strip()]
                return corrections[:3]  # Limit to 3 corrections
            
            return []
            
        except Exception as e:
            logger.error(f"Error suggesting corrections with Ollama: {e}")
            return []


class FallbackProvider(AIProviderInterface):
    """Fallback provider using rule-based command generation"""
    
    def __init__(self):
        self.command_templates = self._load_command_templates()
    
    def _load_command_templates(self) -> Dict[str, List[str]]:
        """Load predefined command templates"""
        return {
            'list': [
                'Get-ChildItem',
                'Get-Process',
                'Get-Service',
                'Get-EventLog -LogName System -Newest 10'
            ],
            'find': [
                'Get-ChildItem -Recurse -Filter "*{query}*"',
                'Select-String -Path "*.txt" -Pattern "{query}"',
                'Get-Process | Where-Object {{$_.Name -like "*{query}*"}}'
            ],
            'stop': [
                'Stop-Process -Name "{query}"',
                'Stop-Service -Name "{query}"'
            ],
            'start': [
                'Start-Process "{query}"',
                'Start-Service -Name "{query}"'
            ],
            'get': [
                'Get-{query}',
                'Get-Command *{query}*',
                'Get-Help {query}'
            ],
            'set': [
                'Set-Location "{query}"',
                'Set-ExecutionPolicy {query}'
            ],
            'help': [
                'Get-Help',
                'Get-Command',
                'Get-Member'
            ]
        }
    
    def is_available(self) -> bool:
        """Fallback provider is always available"""
        return True
    
    def generate_command(self, prompt: str, context: CommandContext) -> str:
        """Generate command using rule-based templates"""
        # Extract key words from prompt
        prompt_lower = prompt.lower()
        
        # Simple keyword matching - check for specific patterns first
        words = prompt_lower.split()
        
        # Check for specific patterns (order matters - more specific first)
        if any(word in prompt_lower for word in ['process', 'task']) and 'list' in prompt_lower:
            return 'Get-Process'
        elif any(word in prompt_lower for word in ['service', 'daemon']) and 'list' in prompt_lower:
            return 'Get-Service'
        elif any(word in prompt_lower for word in ['service', 'daemon']):
            return 'Get-Service'
        elif any(word in prompt_lower for word in ['process', 'task', 'cpu']):
            return 'Get-Process'
        elif any(word in prompt_lower for word in ['file', 'folder', 'directory']):
            return 'Get-ChildItem'
        elif any(word in prompt_lower for word in ['event', 'log']):
            return 'Get-EventLog -LogName System -Newest 10'
        
        # Fallback to category matching
        for category, templates in self.command_templates.items():
            if category in prompt_lower:
                # Use first template for simplicity
                template = templates[0]
                
                # Try to extract query term
                if len(words) > 1:
                    # Find word after the category keyword
                    try:
                        category_index = words.index(category)
                        if category_index + 1 < len(words):
                            query = words[category_index + 1]
                            if '{query}' in template:
                                return template.format(query=query)
                    except ValueError:
                        pass
                
                return template
        
        # Default fallback
        return 'Get-Help'
    
    def detect_errors(self, command: str) -> List[ErrorSuggestion]:
        """Basic rule-based error detection"""
        errors = []
        
        # Check for common issues
        if not command.strip():
            errors.append(ErrorSuggestion(
                error_type="empty",
                description="Command is empty",
                suggested_fix="Enter a PowerShell command",
                confidence=1.0
            ))
        
        # Check for obvious syntax issues
        if command.count('(') != command.count(')'):
            errors.append(ErrorSuggestion(
                error_type="syntax",
                description="Mismatched parentheses",
                suggested_fix="Check parentheses are properly matched",
                confidence=0.9
            ))
        
        if command.count('{') != command.count('}'):
            errors.append(ErrorSuggestion(
                error_type="syntax",
                description="Mismatched braces",
                suggested_fix="Check braces are properly matched",
                confidence=0.9
            ))
        
        # Check for invalid cmdlet format
        if not any(char.isupper() for char in command) and '-' in command:
            errors.append(ErrorSuggestion(
                error_type="cmdlet",
                description="Cmdlet names should use PascalCase (e.g., Get-Process)",
                suggested_fix="Capitalize the first letter of each word in cmdlet names",
                confidence=0.7
            ))
        
        return errors
    
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """Basic rule-based corrections"""
        corrections = []
        
        # Common corrections
        if 'get-process' in command.lower():
            corrections.append('Get-Process')
        if 'get-service' in command.lower():
            corrections.append('Get-Service')
        if 'get-childitem' in command.lower():
            corrections.append('Get-ChildItem')
        
        # If no specific corrections, suggest help
        if not corrections:
            corrections.extend([
                'Get-Help',
                'Get-Command',
                'Get-Command *' + command.split()[0] + '*' if command.split() else 'Get-Help'
            ])
        
        return corrections[:3]