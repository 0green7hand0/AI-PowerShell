"""Data models for context management"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Platform, UserRole, ExecutionResult


class SessionStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class PreferenceCategory(Enum):
    COMMAND_STYLE = "command_style"
    OUTPUT_FORMAT = "output_format"
    SECURITY_LEVEL = "security_level"
    AI_BEHAVIOR = "ai_behavior"


@dataclass
class UserSession:
    """Represents a user session with context and state"""
    session_id: str
    user_role: UserRole
    platform: Platform
    created_at: datetime
    last_activity: datetime
    status: SessionStatus = SessionStatus.ACTIVE
    working_directory: str = ""
    environment_variables: Dict[str, str] = field(default_factory=dict)
    active_modules: List[str] = field(default_factory=list)
    command_count: int = 0
    
    def __post_init__(self):
        if not self.working_directory:
            import os
            self.working_directory = os.getcwd()


@dataclass
class UserPreferences:
    """User preferences and personalization settings"""
    session_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    command_patterns: Dict[str, int] = field(default_factory=dict)  # command -> frequency
    favorite_commands: List[str] = field(default_factory=list)
    preferred_output_format: str = "table"
    ai_confidence_threshold: float = 0.7
    security_confirmation_level: str = "medium"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ContextState:
    """Current context state for command execution"""
    session_id: str
    current_directory: str
    environment_variables: Dict[str, str]
    recent_commands: List[str]
    active_modules: List[str]
    last_command_result: Optional[ExecutionResult] = None
    context_variables: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HistoryEntry:
    """Command history entry"""
    session_id: str
    command: str
    natural_language_input: Optional[str]
    execution_result: ExecutionResult
    timestamp: datetime
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    user_feedback: Optional[str] = None
    success_rating: Optional[float] = None  # 0.0 to 1.0
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class HistoryFilter:
    """Filter criteria for command history queries"""
    session_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    command_pattern: Optional[str] = None
    success_only: bool = False
    limit: int = 100
    offset: int = 0
    sort_by: str = "timestamp"  # timestamp, command, success
    sort_order: str = "desc"  # asc, desc


@dataclass
class CommandPattern:
    """Represents a learned command pattern"""
    pattern_id: str
    session_id: str
    natural_language_pattern: str
    command_template: str
    usage_count: int
    success_rate: float
    confidence_score: float
    created_at: datetime
    last_used: datetime
    
    def __post_init__(self):
        if not hasattr(self, 'pattern_id'):
            self.pattern_id = str(uuid.uuid4())


@dataclass
class SuggestionContext:
    """Context for generating command suggestions"""
    current_directory: str
    recent_commands: List[str]
    active_modules: List[str]
    user_patterns: List[CommandPattern]
    environment_variables: Dict[str, str]
    platform: Platform
    user_role: UserRole
    session_preferences: UserPreferences