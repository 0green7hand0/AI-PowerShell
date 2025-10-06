"""
上下文管理数据模型

本模块定义了上下文管理相关的数据模型，包括会话、命令历史等。
用于维护用户交互的上下文信息，支持智能命令建议和历史追踪。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ============================================================================
# 枚举类型定义
# ============================================================================

class SessionStatus(Enum):
    """会话状态枚举"""
    ACTIVE = "active"           # 活跃会话
    INACTIVE = "inactive"       # 非活跃会话
    EXPIRED = "expired"         # 已过期会话
    TERMINATED = "terminated"   # 已终止会话


class CommandStatus(Enum):
    """命令状态枚举"""
    PENDING = "pending"         # 等待执行
    EXECUTING = "executing"     # 执行中
    COMPLETED = "completed"     # 执行完成
    FAILED = "failed"           # 执行失败
    CANCELLED = "cancelled"     # 已取消


# ============================================================================
# 数据模型定义
# ============================================================================

@dataclass
class CommandEntry:
    """命令历史条目数据模型"""
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 命令唯一标识
    user_input: str = ""                     # 用户原始输入
    translated_command: str = ""             # 翻译后的命令
    status: CommandStatus = CommandStatus.PENDING  # 命令状态
    output: str = ""                         # 命令输出
    error: str = ""                          # 错误信息
    return_code: int = 0                     # 返回码
    execution_time: float = 0.0              # 执行时间（秒）
    confidence_score: float = 0.0            # AI 翻译置信度
    timestamp: datetime = field(default_factory=datetime.now)  # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    @property
    def is_successful(self) -> bool:
        """判断命令是否执行成功"""
        return self.status == CommandStatus.COMPLETED and self.return_code == 0
    
    @property
    def has_error(self) -> bool:
        """判断是否有错误"""
        return bool(self.error.strip()) or self.status == CommandStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "command_id": self.command_id,
            "user_input": self.user_input,
            "translated_command": self.translated_command,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "execution_time": self.execution_time,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandEntry':
        """从字典创建实例"""
        return cls(
            command_id=data.get("command_id", str(uuid.uuid4())),
            user_input=data.get("user_input", ""),
            translated_command=data.get("translated_command", ""),
            status=CommandStatus(data.get("status", "pending")),
            output=data.get("output", ""),
            error=data.get("error", ""),
            return_code=data.get("return_code", 0),
            execution_time=data.get("execution_time", 0.0),
            confidence_score=data.get("confidence_score", 0.0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            metadata=data.get("metadata", {})
        )


@dataclass
class Session:
    """会话数据模型"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 会话唯一标识
    user_id: Optional[str] = None            # 用户 ID
    status: SessionStatus = SessionStatus.ACTIVE  # 会话状态
    start_time: datetime = field(default_factory=datetime.now)  # 会话开始时间
    last_activity: datetime = field(default_factory=datetime.now)  # 最后活动时间
    end_time: Optional[datetime] = None      # 会话结束时间
    working_directory: str = "."             # 工作目录
    environment_vars: Dict[str, str] = field(default_factory=dict)  # 环境变量
    command_history: List[CommandEntry] = field(default_factory=list)  # 命令历史
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    @property
    def duration(self) -> float:
        """获取会话持续时间（秒）"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def command_count(self) -> int:
        """获取命令总数"""
        return len(self.command_history)
    
    @property
    def successful_commands(self) -> int:
        """获取成功执行的命令数"""
        return sum(1 for cmd in self.command_history if cmd.is_successful)
    
    @property
    def failed_commands(self) -> int:
        """获取失败的命令数"""
        return sum(1 for cmd in self.command_history if cmd.has_error)
    
    @property
    def is_active(self) -> bool:
        """判断会话是否活跃"""
        return self.status == SessionStatus.ACTIVE
    
    def add_command(self, command_entry: CommandEntry):
        """添加命令到历史记录"""
        self.command_history.append(command_entry)
        self.last_activity = datetime.now()
    
    def get_recent_commands(self, limit: int = 5) -> List[CommandEntry]:
        """获取最近的命令"""
        return self.command_history[-limit:]
    
    def get_successful_commands(self) -> List[CommandEntry]:
        """获取所有成功的命令"""
        return [cmd for cmd in self.command_history if cmd.is_successful]
    
    def get_failed_commands(self) -> List[CommandEntry]:
        """获取所有失败的命令"""
        return [cmd for cmd in self.command_history if cmd.has_error]
    
    def terminate(self):
        """终止会话"""
        self.status = SessionStatus.TERMINATED
        self.end_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "working_directory": self.working_directory,
            "environment_vars": self.environment_vars,
            "command_history": [cmd.to_dict() for cmd in self.command_history],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """从字典创建实例"""
        return cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            user_id=data.get("user_id"),
            status=SessionStatus(data.get("status", "active")),
            start_time=datetime.fromisoformat(data["start_time"]) if "start_time" in data else datetime.now(),
            last_activity=datetime.fromisoformat(data["last_activity"]) if "last_activity" in data else datetime.now(),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            working_directory=data.get("working_directory", "."),
            environment_vars=data.get("environment_vars", {}),
            command_history=[CommandEntry.from_dict(cmd) for cmd in data.get("command_history", [])],
            metadata=data.get("metadata", {})
        )


@dataclass
class ContextSnapshot:
    """上下文快照数据模型
    
    用于保存某个时间点的完整上下文状态，支持上下文恢复和分析。
    """
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))  # 快照唯一标识
    session: Session = field(default_factory=Session)  # 会话信息
    timestamp: datetime = field(default_factory=datetime.now)  # 快照时间
    description: str = ""                    # 快照描述
    tags: List[str] = field(default_factory=list)  # 标签
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "snapshot_id": self.snapshot_id,
            "session": self.session.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextSnapshot':
        """从字典创建实例"""
        return cls(
            snapshot_id=data.get("snapshot_id", str(uuid.uuid4())),
            session=Session.from_dict(data.get("session", {})),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            description=data.get("description", ""),
            tags=data.get("tags", [])
        )


@dataclass
class UserPreferences:
    """用户偏好设置数据模型"""
    user_id: str                             # 用户 ID
    auto_execute_safe_commands: bool = False  # 自动执行安全命令
    confirmation_required: bool = True       # 是否需要确认
    history_limit: int = 100                 # 历史记录限制
    session_timeout: int = 3600              # 会话超时时间（秒）
    preferred_shell: str = "pwsh"            # 首选 Shell
    language: str = "zh-CN"                  # 语言偏好
    theme: str = "default"                   # 主题
    custom_settings: Dict[str, Any] = field(default_factory=dict)  # 自定义设置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "user_id": self.user_id,
            "auto_execute_safe_commands": self.auto_execute_safe_commands,
            "confirmation_required": self.confirmation_required,
            "history_limit": self.history_limit,
            "session_timeout": self.session_timeout,
            "preferred_shell": self.preferred_shell,
            "language": self.language,
            "theme": self.theme,
            "custom_settings": self.custom_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """从字典创建实例"""
        return cls(
            user_id=data["user_id"],
            auto_execute_safe_commands=data.get("auto_execute_safe_commands", False),
            confirmation_required=data.get("confirmation_required", True),
            history_limit=data.get("history_limit", 100),
            session_timeout=data.get("session_timeout", 3600),
            preferred_shell=data.get("preferred_shell", "pwsh"),
            language=data.get("language", "zh-CN"),
            theme=data.get("theme", "default"),
            custom_settings=data.get("custom_settings", {})
        )
