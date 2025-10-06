"""
上下文管理模块

本模块提供上下文管理功能，包括会话管理、命令历史记录和用户偏好设置。
"""

from .models import (
    CommandEntry,
    Session,
    ContextSnapshot,
    UserPreferences,
    SessionStatus,
    CommandStatus
)
from .manager import ContextManager
from .history import HistoryManager

__all__ = [
    'CommandEntry',
    'Session',
    'ContextSnapshot',
    'UserPreferences',
    'SessionStatus',
    'CommandStatus',
    'ContextManager',
    'HistoryManager'
]
