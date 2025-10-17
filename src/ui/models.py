"""
UI 数据模型

定义 UI 系统使用的数据结构和配置模型。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class IconStyle(str, Enum):
    """图标样式枚举"""
    EMOJI = "emoji"
    ASCII = "ascii"
    UNICODE = "unicode"
    NONE = "none"


class ThemeName(str, Enum):
    """主题名称枚举"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    MINIMAL = "minimal"
    CUSTOM = "custom"


@dataclass
class UIConfig:
    """UI 配置"""
    enable_colors: bool = True
    enable_icons: bool = True
    enable_progress: bool = True
    enable_animations: bool = True
    theme: str = "default"
    icon_style: IconStyle = IconStyle.EMOJI
    max_table_width: int = 120
    page_size: int = 20
    auto_pager: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UIConfig':
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class ThemeColors:
    """主题颜色配置"""
    success: str = "green"
    error: str = "red"
    warning: str = "yellow"
    info: str = "blue"
    primary: str = "cyan"
    secondary: str = "magenta"
    muted: str = "dim"
    highlight: str = "bold cyan"
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThemeColors':
        """从字典创建主题颜色"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class ArgumentDefinition:
    """命令参数定义"""
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[str] = None
    choices: Optional[List[str]] = None


@dataclass
class CommandDefinition:
    """命令定义"""
    name: str
    description: str
    usage: str
    examples: List[str] = field(default_factory=list)
    arguments: List[ArgumentDefinition] = field(default_factory=list)
    subcommands: List['CommandDefinition'] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)


@dataclass
class ProgressTask:
    """进度任务"""
    task_id: str
    description: str
    total: int = 100
    completed: int = 0
    
    @property
    def percentage(self) -> float:
        """计算完成百分比"""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100


@dataclass
class ErrorContext:
    """错误上下文"""
    error_type: str
    message: str
    details: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
