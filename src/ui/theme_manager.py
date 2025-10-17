"""
主题管理器

管理 CLI 的颜色主题和样式配置。
"""

from typing import Dict, Optional
from rich.theme import Theme
from rich.style import Style

from .models import ThemeColors, ThemeName


class ThemeManager:
    """主题管理器"""
    
    # 预定义主题
    THEMES: Dict[str, ThemeColors] = {
        ThemeName.DEFAULT: ThemeColors(
            success="bold green",
            error="bold red",
            warning="bold yellow",
            info="bold blue",
            primary="bold cyan",
            secondary="bold magenta",
            muted="dim white",
            highlight="bold bright_cyan"
        ),
        ThemeName.DARK: ThemeColors(
            success="bold bright_green",
            error="bold bright_red",
            warning="bold bright_yellow",
            info="bold bright_blue",
            primary="bold bright_cyan",
            secondary="bold bright_magenta",
            muted="dim bright_white",
            highlight="bold bright_cyan on black"
        ),
        ThemeName.LIGHT: ThemeColors(
            success="bold green",
            error="bold red",
            warning="bold yellow",
            info="bold blue",
            primary="bold blue",
            secondary="bold magenta",
            muted="dim black",
            highlight="bold blue on white"
        ),
        ThemeName.MINIMAL: ThemeColors(
            success="white",
            error="white",
            warning="white",
            info="white",
            primary="white",
            secondary="white",
            muted="dim white",
            highlight="bold white"
        ),
    }
    
    def __init__(self, theme_name: str = ThemeName.DEFAULT):
        """
        初始化主题管理器
        
        Args:
            theme_name: 主题名称
        """
        self.theme_name = theme_name
        self.colors = self._load_theme_colors(theme_name)
        self.rich_theme = self._create_rich_theme()
    
    def _load_theme_colors(self, theme_name: str) -> ThemeColors:
        """
        加载主题颜色
        
        Args:
            theme_name: 主题名称
            
        Returns:
            ThemeColors: 主题颜色配置
        """
        return self.THEMES.get(theme_name, self.THEMES[ThemeName.DEFAULT])
    
    def _create_rich_theme(self) -> Theme:
        """
        创建 Rich 主题对象
        
        Returns:
            Theme: Rich 主题对象
        """
        return Theme({
            "success": self.colors.success,
            "error": self.colors.error,
            "warning": self.colors.warning,
            "info": self.colors.info,
            "primary": self.colors.primary,
            "secondary": self.colors.secondary,
            "muted": self.colors.muted,
            "highlight": self.colors.highlight,
        })
    
    def get_color(self, element: str) -> str:
        """
        获取元素的颜色
        
        Args:
            element: 元素名称
            
        Returns:
            str: 颜色字符串
        """
        return getattr(self.colors, element, "white")
    
    def get_style(self, element: str) -> Style:
        """
        获取元素的样式
        
        Args:
            element: 元素名称
            
        Returns:
            Style: Rich 样式对象
        """
        color = self.get_color(element)
        return Style.parse(color)
    
    def list_available_themes(self) -> list:
        """
        列出可用的主题
        
        Returns:
            list: 主题名称列表
        """
        return list(self.THEMES.keys())
    
    def switch_theme(self, theme_name: str) -> None:
        """
        切换主题
        
        Args:
            theme_name: 新主题名称
        """
        if theme_name in self.THEMES:
            self.theme_name = theme_name
            self.colors = self._load_theme_colors(theme_name)
            self.rich_theme = self._create_rich_theme()
    
    def add_custom_theme(self, name: str, colors: ThemeColors) -> None:
        """
        添加自定义主题
        
        Args:
            name: 主题名称
            colors: 主题颜色配置
        """
        self.THEMES[name] = colors
