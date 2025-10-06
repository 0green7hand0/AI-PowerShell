"""
执行引擎模块

本模块负责 PowerShell 命令的实际执行，包括：
- 跨平台 PowerShell 检测和执行
- 平台适配和命令转换
- 输出格式化和编码处理
"""

from .executor import CommandExecutor
from .platform_adapter import PlatformAdapter
from .output_formatter import OutputFormatter

__all__ = [
    'CommandExecutor',
    'PlatformAdapter',
    'OutputFormatter',
]
