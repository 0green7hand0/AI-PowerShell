"""PowerShell Execution Engine Module

This module provides cross-platform PowerShell command execution with
unified output formatting and platform adaptation.

Interfaces to implement:
- ExecutorInterface: Main PowerShell execution interface
- ContextManagerInterface: Context and session management
"""

from .executor import PowerShellExecutor, PowerShellDetector, PowerShellInfo, PowerShellVersion
from .output_formatter import (
    OutputFormatter, FormattingOptions, FormattedOutput, OutputEncoding, 
    PaginationMode, create_default_formatter, create_compact_formatter, 
    create_verbose_formatter
)
from .platform_adapter import (
    PlatformOutputAdapter, PlatformAdaptationOptions, AdaptationResult,
    ErrorMessageType, create_default_adapter, create_strict_adapter,
    create_minimal_adapter
)
# from .context import ContextManager  # Will be implemented in task 7

__all__ = [
    "PowerShellExecutor",
    "PowerShellDetector", 
    "PowerShellInfo",
    "PowerShellVersion",
    "OutputFormatter",
    "FormattingOptions",
    "FormattedOutput",
    "OutputEncoding",
    "PaginationMode",
    "create_default_formatter",
    "create_compact_formatter",
    "create_verbose_formatter",
    "PlatformOutputAdapter",
    "PlatformAdaptationOptions",
    "AdaptationResult",
    "ErrorMessageType",
    "create_default_adapter",
    "create_strict_adapter",
    "create_minimal_adapter"
]