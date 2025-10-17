"""
UI 模块 - CLI 用户界面增强

本模块提供现代化的 CLI 用户界面组件，包括：
- 彩色输出和主题管理
- 进度指示器和加载动画
- 交互式输入和自动补全
- 格式化的表格和列表显示
- 增强的帮助系统
"""

from .models import UIConfig, ThemeColors, IconStyle
from .ui_manager import UIManager
from .progress_manager import ProgressManager
from .interactive_input import InteractiveInputManager
from .help_system import HelpSystem
from .theme_manager import ThemeManager
from .error_handler import ErrorHandler
from .config_loader import UIConfigLoader
from .config_manager import UIConfigManager
from .table_manager import TableManager, ColumnConfig, TableConfig, SortOrder
from .template_display import TemplateDisplay
from .template_manager_ui import TemplateManagerUI
from .startup_wizard import StartupWizard, SystemCheck, CheckStatus
from .startup_experience import StartupExperience, StartupPerformanceOptimizer
from .terminal_detector import TerminalDetector, TerminalCapabilities
from .compatibility import UICompatibilityLayer, create_compatible_ui_config, check_terminal_compatibility

__all__ = [
    'UIConfig',
    'ThemeColors',
    'IconStyle',
    'UIManager',
    'ProgressManager',
    'InteractiveInputManager',
    'HelpSystem',
    'ThemeManager',
    'ErrorHandler',
    'UIConfigLoader',
    'UIConfigManager',
    'TableManager',
    'ColumnConfig',
    'TableConfig',
    'SortOrder',
    'TemplateDisplay',
    'TemplateManagerUI',
    'StartupWizard',
    'SystemCheck',
    'CheckStatus',
    'StartupExperience',
    'StartupPerformanceOptimizer',
    'TerminalDetector',
    'TerminalCapabilities',
    'UICompatibilityLayer',
    'create_compatible_ui_config',
    'check_terminal_compatibility',
]

__version__ = '1.0.0'
