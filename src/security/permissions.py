"""
权限检查模块

实现第二层安全验证：检查命令所需的权限，检测管理员权限需求。
"""

import os
import sys
import re
import platform
import ctypes
from typing import List, Tuple
import logging


class PermissionChecker:
    """权限检查器
    
    负责检查命令所需的权限，判断当前用户是否有足够权限执行命令。
    """
    
    # 需要管理员权限的命令模式
    ADMIN_REQUIRED_PATTERNS = [
        # 系统服务
        r"Start-Service",
        r"Stop-Service",
        r"Restart-Service",
        r"Set-Service",
        r"New-Service",
        r"Remove-Service",
        
        # 系统配置
        r"Set-ExecutionPolicy",
        r"Set-ItemProperty.*HKLM:",
        r"New-ItemProperty.*HKLM:",
        r"Remove-ItemProperty.*HKLM:",
        r"Set-NetFirewallProfile",
        r"New-NetFirewallRule",
        r"Set-NetFirewallRule",
        
        # 用户和组管理
        r"New-LocalUser",
        r"Remove-LocalUser",
        r"Set-LocalUser",
        r"Add-LocalGroupMember",
        r"Remove-LocalGroupMember",
        
        # 系统功能
        r"Enable-WindowsOptionalFeature",
        r"Disable-WindowsOptionalFeature",
        r"Install-WindowsFeature",
        r"Uninstall-WindowsFeature",
        
        # 磁盘和分区
        r"Format-Volume",
        r"Initialize-Disk",
        r"New-Partition",
        r"Clear-Disk",
        
        # 网络配置
        r"Set-NetIPAddress",
        r"New-NetIPAddress",
        r"Set-DnsClientServerAddress",
        r"Disable-NetAdapter",
        r"Enable-NetAdapter",
        
        # 计算机管理
        r"Rename-Computer",
        r"Add-Computer",
        r"Remove-Computer",
        r"Stop-Computer",
        r"Restart-Computer",
        
        # 软件安装
        r"Install-Package",
        r"Uninstall-Package",
        r"Install-Module.*-Scope\s+AllUsers",
        
        # 系统文件操作
        r"Remove-Item.*C:\\Windows",
        r"Remove-Item.*C:\\Program Files",
        r"Set-ItemProperty.*C:\\Windows",
    ]
    
    def __init__(self):
        """初始化权限检查器"""
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system()
        
        # 编译正则表达式
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.ADMIN_REQUIRED_PATTERNS
        ]
    
    def requires_admin(self, command: str) -> bool:
        """检查命令是否需要管理员权限
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 是否需要管理员权限
        """
        command = command.strip()
        
        # 检查是否匹配需要管理员权限的模式
        for pattern in self._compiled_patterns:
            if pattern.search(command):
                self.logger.info(f"命令需要管理员权限: {command}")
                return True
        
        return False
    
    def check_current_permissions(self) -> bool:
        """检查当前进程是否有管理员权限
        
        Returns:
            bool: 当前是否为管理员权限
        """
        if self.platform == "Windows":
            return self._is_admin_windows()
        elif self.platform in ["Linux", "Darwin"]:  # Darwin is macOS
            return self._is_admin_unix()
        else:
            self.logger.warning(f"未知平台: {self.platform}，假设无管理员权限")
            return False
    
    def _is_admin_windows(self) -> bool:
        """检查 Windows 系统的管理员权限
        
        Returns:
            bool: 是否为管理员
        """
        try:
            # 尝试调用 Windows API 检查管理员权限
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            self.logger.error(f"检查 Windows 管理员权限失败: {e}")
            return False
    
    def _is_admin_unix(self) -> bool:
        """检查 Unix/Linux/macOS 系统的管理员权限
        
        Returns:
            bool: 是否为 root 用户或有 sudo 权限
        """
        try:
            # 检查是否为 root 用户 (UID = 0)
            return os.geteuid() == 0
        except Exception as e:
            self.logger.error(f"检查 Unix 管理员权限失败: {e}")
            return False
    
    def get_elevation_command(self, command: str) -> str:
        """获取权限提升后的命令
        
        Args:
            command: 原始命令
            
        Returns:
            str: 提升权限后的命令
        """
        if self.platform == "Windows":
            # Windows: 使用 Start-Process -Verb RunAs
            return f'Start-Process powershell -Verb RunAs -ArgumentList "-Command", "{command}"'
        elif self.platform in ["Linux", "Darwin"]:
            # Unix/Linux/macOS: 使用 sudo
            return f'sudo pwsh -Command "{command}"'
        else:
            return command
    
    def log_elevation_attempt(self, command: str, user: str = None):
        """记录权限提升尝试
        
        Args:
            command: 尝试执行的命令
            user: 用户名（可选）
        """
        if user is None:
            try:
                user = os.getlogin()
            except:
                user = "unknown"
        
        self.logger.warning(
            f"权限提升尝试 - 用户: {user}, 命令: {command}"
        )
    
    def can_elevate(self) -> bool:
        """检查是否可以提升权限
        
        Returns:
            bool: 是否可以提升权限
        """
        # 如果已经是管理员，不需要提升
        if self.check_current_permissions():
            return True
        
        # Windows: 检查是否在管理员组中
        if self.platform == "Windows":
            try:
                # 尝试检查用户是否在管理员组中
                import win32security
                import win32api
                
                # 获取管理员组的 SID
                admin_sid = win32security.CreateWellKnownSid(
                    win32security.WinBuiltinAdministratorsSid
                )
                
                # 检查当前用户是否在管理员组中
                return win32security.CheckTokenMembership(None, admin_sid)
            except ImportError:
                # 如果没有 pywin32，假设可以提升
                self.logger.warning("pywin32 未安装，无法准确检查权限提升能力")
                return True
            except Exception as e:
                self.logger.error(f"检查权限提升能力失败: {e}")
                return False
        
        # Unix/Linux/macOS: 检查是否可以使用 sudo
        elif self.platform in ["Linux", "Darwin"]:
            try:
                import subprocess
                result = subprocess.run(
                    ['sudo', '-n', 'true'],
                    capture_output=True,
                    timeout=1
                )
                return result.returncode == 0
            except Exception as e:
                self.logger.error(f"检查 sudo 权限失败: {e}")
                return False
        
        return False
    
    def get_permission_info(self) -> dict:
        """获取当前权限信息
        
        Returns:
            dict: 权限信息字典
        """
        info = {
            "platform": self.platform,
            "is_admin": self.check_current_permissions(),
            "can_elevate": self.can_elevate(),
            "user": "unknown"
        }
        
        try:
            info["user"] = os.getlogin()
        except:
            pass
        
        if self.platform == "Windows":
            try:
                info["user"] = os.environ.get("USERNAME", "unknown")
            except:
                pass
        elif self.platform in ["Linux", "Darwin"]:
            try:
                info["user"] = os.environ.get("USER", "unknown")
                info["uid"] = os.geteuid()
                info["gid"] = os.getegid()
            except:
                pass
        
        return info
