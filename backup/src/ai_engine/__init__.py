"""AI Engine Module for Natural Language Processing

This module provides local AI model integration for converting natural language
to PowerShell commands and intelligent error detection.

Main components:
- AIEngine: Main AI processing engine
- AIProviderInterface: Abstract interface for AI providers
- LlamaCppProvider: LLaMA-CPP integration
- OllamaProvider: Ollama integration
- FallbackProvider: Rule-based fallback processing
"""

from .engine import AIEngine
from .providers import (
    AIProviderInterface,
    LlamaCppProvider,
    OllamaProvider,
    FallbackProvider
)
from .translation import PowerShellTranslator, CommandPattern
from .error_detection import PowerShellErrorDetector, PowerShellCmdlet, ErrorType

__all__ = [
    'AIEngine',
    'AIProviderInterface',
    'LlamaCppProvider',
    'OllamaProvider',
    'FallbackProvider',
    'PowerShellTranslator',
    'CommandPattern',
    'PowerShellErrorDetector',
    'PowerShellCmdlet',
    'ErrorType'
]