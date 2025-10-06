"""
AI 引擎模块

负责将中文自然语言转换为 PowerShell 命令。
包含翻译逻辑、AI 提供商集成和错误检测功能。
"""

from .engine import AIEngine, TranslationCache
from .translation import NaturalLanguageTranslator
from .providers import AIProvider, get_provider, MockProvider
from .error_detection import ErrorDetector

__all__ = [
    'AIEngine',
    'TranslationCache',
    'NaturalLanguageTranslator',
    'AIProvider',
    'get_provider',
    'MockProvider',
    'ErrorDetector',
]
