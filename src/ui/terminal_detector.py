"""
终端能力检测器

检测终端的功能支持情况，用于实现功能降级。
"""

import os
import sys
import platform
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class TerminalCapabilities:
    """终端能力"""
    supports_color: bool = True
    supports_unicode: bool = True
    supports_emoji: bool = True
    supports_ansi: bool = True
    terminal_width: int = 80
    terminal_height: int = 24
    is_interactive: bool = True
    terminal_type: str = "unknown"
    color_depth: int = 256  # 8, 16, 256, or 16777216 (24-bit)


class TerminalDetector:
    """终端能力检测器"""
    
    @staticmethod
    def detect() -> TerminalCapabilities:
        """
        检测终端能力
        
        Returns:
            TerminalCapabilities: 终端能力对象
        """
        caps = TerminalCapabilities()
        
        # 检测是否是交互式终端
        caps.is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
        
        # 检测终端类型
        caps.terminal_type = os.environ.get('TERM', 'unknown')
        
        # 检测终端尺寸
        try:
            import shutil
            size = shutil.get_terminal_size()
            caps.terminal_width = size.columns
            caps.terminal_height = size.lines
        except:
            caps.terminal_width = 80
            caps.terminal_height = 24
        
        # 检测颜色支持
        caps.supports_color = TerminalDetector._detect_color_support()
        caps.color_depth = TerminalDetector._detect_color_depth()
        
        # 检测 ANSI 支持
        caps.supports_ansi = TerminalDetector._detect_ansi_support()
        
        # 检测 Unicode 支持
        caps.supports_unicode = TerminalDetector._detect_unicode_support()
        
        # 检测 Emoji 支持
        caps.supports_emoji = TerminalDetector._detect_emoji_support()
        
        return caps
    
    @staticmethod
    def _detect_color_support() -> bool:
        """检测颜色支持"""
        # 检查环境变量
        if os.environ.get('NO_COLOR'):
            return False
        
        if os.environ.get('FORCE_COLOR'):
            return True
        
        # 检查 TERM 环境变量
        term = os.environ.get('TERM', '')
        if 'color' in term.lower():
            return True
        
        # Windows 10+ 支持 ANSI 颜色
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 尝试启用 ANSI 支持
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                # Windows 旧版本可能不支持
                return False
        
        # Unix-like 系统通常支持颜色
        return sys.stdout.isatty()
    
    @staticmethod
    def _detect_color_depth() -> int:
        """检测颜色深度"""
        term = os.environ.get('TERM', '')
        colorterm = os.environ.get('COLORTERM', '')
        
        # 24-bit color (truecolor)
        if 'truecolor' in colorterm.lower() or '24bit' in colorterm.lower():
            return 16777216
        
        # 256 colors
        if '256color' in term.lower():
            return 256
        
        # 16 colors
        if 'color' in term.lower():
            return 16
        
        # 8 colors (basic)
        return 8
    
    @staticmethod
    def _detect_ansi_support() -> bool:
        """检测 ANSI 转义序列支持"""
        # Windows 10+ 支持 ANSI
        if platform.system() == 'Windows':
            try:
                # Windows 10 版本 1511 及以上支持 ANSI
                version = platform.version()
                if version:
                    parts = version.split('.')
                    if len(parts) >= 2:
                        major = int(parts[0])
                        build = int(parts[2]) if len(parts) > 2 else 0
                        # Windows 10 build 10586 及以上
                        return major >= 10 and build >= 10586
            except:
                pass
            return False
        
        # Unix-like 系统通常支持 ANSI
        return True
    
    @staticmethod
    def _detect_unicode_support() -> bool:
        """检测 Unicode 支持"""
        try:
            # 检查系统编码
            encoding = sys.stdout.encoding or ''
            if 'utf' in encoding.lower():
                return True
            
            # 尝试编码测试字符
            test_char = '✓'
            test_char.encode(encoding)
            return True
        except:
            return False
    
    @staticmethod
    def _detect_emoji_support() -> bool:
        """检测 Emoji 支持"""
        # Windows 10+ 支持 Emoji
        if platform.system() == 'Windows':
            try:
                version = platform.version()
                if version:
                    parts = version.split('.')
                    if len(parts) >= 1:
                        major = int(parts[0])
                        return major >= 10
            except:
                pass
            return False
        
        # macOS 和现代 Linux 通常支持 Emoji
        if platform.system() in ['Darwin', 'Linux']:
            # 检查 locale 设置
            lang = os.environ.get('LANG', '')
            if 'utf' in lang.lower():
                return True
        
        return False
    
    @staticmethod
    def get_recommended_icon_style(caps: TerminalCapabilities) -> str:
        """
        根据终端能力推荐图标样式
        
        Args:
            caps: 终端能力对象
            
        Returns:
            str: 推荐的图标样式
        """
        if caps.supports_emoji:
            return "emoji"
        elif caps.supports_unicode:
            return "unicode"
        else:
            return "ascii"
    
    @staticmethod
    def should_enable_colors(caps: TerminalCapabilities) -> bool:
        """
        判断是否应该启用颜色
        
        Args:
            caps: 终端能力对象
            
        Returns:
            bool: 是否启用颜色
        """
        return caps.supports_color and caps.is_interactive
    
    @staticmethod
    def should_enable_animations(caps: TerminalCapabilities) -> bool:
        """
        判断是否应该启用动画
        
        Args:
            caps: 终端能力对象
            
        Returns:
            bool: 是否启用动画
        """
        return caps.supports_ansi and caps.is_interactive
    
    @staticmethod
    def get_safe_width(caps: TerminalCapabilities, max_width: int = 120) -> int:
        """
        获取安全的显示宽度
        
        Args:
            caps: 终端能力对象
            max_width: 最大宽度
            
        Returns:
            int: 安全的显示宽度
        """
        if caps.terminal_width < 40:
            return 40  # 最小宽度
        
        return min(caps.terminal_width - 2, max_width)
