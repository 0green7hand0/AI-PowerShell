"""
平台适配器模块

本模块实现跨平台命令适配功能，包括：
- Windows、Linux、macOS 平台检测
- 命令路径转换（Windows 路径 <-> Unix 路径）
- 平台特定命令映射
- 环境变量处理
"""

import platform
import os
from pathlib import Path
from typing import Dict, Optional, List


class PlatformAdapter:
    """平台适配器类
    
    负责将命令适配到不同的操作系统平台，处理路径、命令和环境变量的差异。
    """
    
    def __init__(self):
        """初始化平台适配器"""
        self.platform_name = platform.system()  # 'Windows', 'Linux', 'Darwin'
        self.is_windows = self.platform_name == "Windows"
        self.is_linux = self.platform_name == "Linux"
        self.is_macos = self.platform_name == "Darwin"
        
        # 平台特定的命令映射
        self.command_mappings = self._init_command_mappings()
    
    def _init_command_mappings(self) -> Dict[str, Dict[str, str]]:
        """初始化平台特定的命令映射
        
        Returns:
            Dict: 命令映射字典，格式为 {source_platform: {command: adapted_command}}
        """
        return {
            # Windows 到 Unix 的命令映射
            'windows_to_unix': {
                'dir': 'Get-ChildItem',
                'cls': 'Clear-Host',
                'copy': 'Copy-Item',
                'move': 'Move-Item',
                'del': 'Remove-Item',
                'type': 'Get-Content',
                'md': 'New-Item -ItemType Directory',
                'rd': 'Remove-Item',
            },
            # Unix 到 Windows 的命令映射
            'unix_to_windows': {
                'ls': 'Get-ChildItem',
                'clear': 'Clear-Host',
                'cp': 'Copy-Item',
                'mv': 'Move-Item',
                'rm': 'Remove-Item',
                'cat': 'Get-Content',
                'mkdir': 'New-Item -ItemType Directory',
                'rmdir': 'Remove-Item',
            }
        }
    
    def adapt_command(self, command: str, target_platform: Optional[str] = None) -> str:
        """适配命令到目标平台
        
        Args:
            command: 原始命令
            target_platform: 目标平台 ('Windows', 'Linux', 'Darwin')，
                           如果为 None 则使用当前平台
            
        Returns:
            str: 适配后的命令
        """
        if target_platform is None:
            target_platform = self.platform_name
        
        # PowerShell 命令通常是跨平台的，主要处理路径
        adapted_command = self._adapt_paths(command, target_platform)
        
        return adapted_command
    
    def _adapt_paths(self, command: str, target_platform: str) -> str:
        """适配命令中的路径
        
        Args:
            command: 原始命令
            target_platform: 目标平台
            
        Returns:
            str: 路径适配后的命令
        """
        # 如果目标平台与当前平台相同，不需要适配
        if target_platform == self.platform_name:
            return command
        
        # Windows 到 Unix 路径转换
        if self.is_windows and target_platform in ['Linux', 'Darwin']:
            # 将反斜杠转换为正斜杠
            command = command.replace('\\', '/')
            # 转换驱动器路径 (C:\ -> /mnt/c/)
            command = self._convert_windows_drive_to_unix(command)
        
        # Unix 到 Windows 路径转换
        elif not self.is_windows and target_platform == 'Windows':
            # 将正斜杠转换为反斜杠（在引号内的路径）
            command = self._convert_unix_to_windows_path(command)
        
        return command
    
    def _convert_windows_drive_to_unix(self, command: str) -> str:
        """将 Windows 驱动器路径转换为 Unix 路径
        
        Args:
            command: 包含 Windows 路径的命令
            
        Returns:
            str: 转换后的命令
        """
        import re
        
        # 匹配 C:\ 或 C:/ 格式的驱动器路径
        pattern = r'([A-Za-z]):[/\\]'
        
        def replace_drive(match):
            drive_letter = match.group(1).lower()
            return f'/mnt/{drive_letter}/'
        
        return re.sub(pattern, replace_drive, command)
    
    def _convert_unix_to_windows_path(self, command: str) -> str:
        """将 Unix 路径转换为 Windows 路径
        
        Args:
            command: 包含 Unix 路径的命令
            
        Returns:
            str: 转换后的命令
        """
        import re
        
        # 匹配 /mnt/c/ 格式的路径
        pattern = r'/mnt/([a-z])/'
        
        def replace_mount(match):
            drive_letter = match.group(1).upper()
            return f'{drive_letter}:\\'
        
        return re.sub(pattern, replace_mount, command)
    
    def normalize_path(self, path: str) -> str:
        """规范化路径为当前平台格式
        
        Args:
            path: 原始路径
            
        Returns:
            str: 规范化后的路径
        """
        # 使用 pathlib 进行跨平台路径处理
        normalized = Path(path).as_posix() if not self.is_windows else str(Path(path))
        return normalized
    
    def get_home_directory(self) -> str:
        """获取用户主目录
        
        Returns:
            str: 用户主目录路径
        """
        return str(Path.home())
    
    def get_temp_directory(self) -> str:
        """获取临时目录
        
        Returns:
            str: 临时目录路径
        """
        import tempfile
        return tempfile.gettempdir()
    
    def expand_environment_variables(self, command: str) -> str:
        """展开命令中的环境变量
        
        Args:
            command: 包含环境变量的命令
            
        Returns:
            str: 展开环境变量后的命令
        """
        # PowerShell 使用 $env:VAR 格式
        # 这里不展开，让 PowerShell 自己处理
        return command
    
    def get_platform_info(self) -> Dict[str, str]:
        """获取平台信息
        
        Returns:
            Dict: 包含平台详细信息的字典
        """
        return {
            'system': self.platform_name,
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'is_windows': str(self.is_windows),
            'is_linux': str(self.is_linux),
            'is_macos': str(self.is_macos),
        }
    
    def get_path_separator(self) -> str:
        """获取路径分隔符
        
        Returns:
            str: 路径分隔符 ('\\' for Windows, '/' for Unix)
        """
        return os.sep
    
    def get_line_separator(self) -> str:
        """获取行分隔符
        
        Returns:
            str: 行分隔符 ('\\r\\n' for Windows, '\\n' for Unix)
        """
        return os.linesep
    
    def is_absolute_path(self, path: str) -> bool:
        """判断是否为绝对路径
        
        Args:
            path: 路径字符串
            
        Returns:
            bool: 是否为绝对路径
        """
        return Path(path).is_absolute()
    
    def join_paths(self, *paths: str) -> str:
        """连接路径
        
        Args:
            *paths: 要连接的路径部分
            
        Returns:
            str: 连接后的路径
        """
        return str(Path(*paths))
    
    def get_encoding(self) -> str:
        """获取平台默认编码
        
        Returns:
            str: 编码名称
        """
        if self.is_windows:
            # Windows 中文系统使用 GBK
            return 'gbk'
        else:
            # Unix 系统使用 UTF-8
            return 'utf-8'
    
    def adapt_command_for_shell(self, command: str, shell_type: str = 'powershell') -> str:
        """为特定 shell 适配命令
        
        Args:
            command: 原始命令
            shell_type: shell 类型 ('powershell', 'bash', 'cmd')
            
        Returns:
            str: 适配后的命令
        """
        if shell_type == 'powershell':
            # PowerShell 命令不需要特殊处理
            return command
        elif shell_type == 'bash':
            # 如果需要在 bash 中执行 PowerShell 命令
            return f'pwsh -Command "{command}"'
        elif shell_type == 'cmd':
            # 如果需要在 cmd 中执行 PowerShell 命令
            return f'powershell -Command "{command}"'
        else:
            return command
    
    def get_powershell_executable(self) -> Optional[str]:
        """获取 PowerShell 可执行文件路径
        
        Returns:
            str: PowerShell 可执行文件路径，如果不存在则返回 None
        """
        import shutil
        
        # 优先查找 PowerShell Core
        pwsh_path = shutil.which('pwsh')
        if pwsh_path:
            return pwsh_path
        
        # 在 Windows 上查找 Windows PowerShell
        if self.is_windows:
            ps_path = shutil.which('powershell')
            if ps_path:
                return ps_path
        
        return None
    
    def supports_powershell_core(self) -> bool:
        """检查是否支持 PowerShell Core
        
        Returns:
            bool: 是否支持 PowerShell Core
        """
        import shutil
        return shutil.which('pwsh') is not None
    
    def supports_windows_powershell(self) -> bool:
        """检查是否支持 Windows PowerShell
        
        Returns:
            bool: 是否支持 Windows PowerShell
        """
        import shutil
        return self.is_windows and shutil.which('powershell') is not None
    
    def get_recommended_powershell(self) -> Optional[str]:
        """获取推荐的 PowerShell 版本
        
        Returns:
            str: 推荐的 PowerShell 命令名称 ('pwsh' 或 'powershell')
        """
        # 优先推荐 PowerShell Core（跨平台）
        if self.supports_powershell_core():
            return 'pwsh'
        
        # 其次推荐 Windows PowerShell（仅 Windows）
        if self.supports_windows_powershell():
            return 'powershell'
        
        return None
