"""Security Engine Module

This module provides three-tier security validation:
1. Command whitelist validation
2. Dynamic permission checking  
3. Docker sandbox execution

Interfaces to implement:
- SecurityEngineInterface: Main security validation interface
"""

from .engine import SecurityEngine, WhitelistValidator, PermissionChecker, SandboxManager
from .confirmation import (
    ConfirmationManager, ConfirmationRequest, ConfirmationResponse, ConfirmationResult,
    ConsoleConfirmationProvider, MockConfirmationProvider, PermissionEscalationLogger
)

__all__ = [
    'SecurityEngine',
    'WhitelistValidator', 
    'PermissionChecker',
    'SandboxManager',
    'ConfirmationManager',
    'ConfirmationRequest',
    'ConfirmationResponse', 
    'ConfirmationResult',
    'ConsoleConfirmationProvider',
    'MockConfirmationProvider',
    'PermissionEscalationLogger'
]