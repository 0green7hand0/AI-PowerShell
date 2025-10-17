"""
UI 管理器

统一管理所有 UI 组件和样式的核心类。
"""

from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, MINIMAL, SIMPLE

from .models import UIConfig, IconStyle
from .theme_manager import ThemeManager


class UIManager:
    """UI 管理器 - 统一管理所有 UI 组件"""
    
    # 图标映射
    ICONS = {
        IconStyle.EMOJI: {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "question": "❓",
            "rocket": "🚀",
            "gear": "⚙️",
            "folder": "📁",
            "file": "📄",
            "check": "✓",
            "cross": "✗",
            "arrow": "→",
            "bullet": "•",
        },
        IconStyle.ASCII: {
            "success": "[OK]",
            "error": "[X]",
            "warning": "[!]",
            "info": "[i]",
            "question": "[?]",
            "rocket": "[*]",
            "gear": "[#]",
            "folder": "[D]",
            "file": "[F]",
            "check": "[+]",
            "cross": "[-]",
            "arrow": "->",
            "bullet": "*",
        },
        IconStyle.UNICODE: {
            "success": "✓",
            "error": "✗",
            "warning": "⚠",
            "info": "ⓘ",
            "question": "?",
            "rocket": "➤",
            "gear": "⚙",
            "folder": "▶",
            "file": "▪",
            "check": "✓",
            "cross": "✗",
            "arrow": "→",
            "bullet": "•",
        },
    }
    
    def __init__(self, config: Optional[UIConfig] = None):
        """
        初始化 UI 管理器
        
        Args:
            config: UI 配置对象
        """
        self.config = config or UIConfig()
        self.theme_manager = ThemeManager(self.config.theme)
        self.console = Console(theme=self.theme_manager.rich_theme)
        
        # 延迟导入以避免循环依赖
        self._progress_manager = None
        
    def get_icon(self, icon_name: str) -> str:
        """
        获取图标
        
        Args:
            icon_name: 图标名称
            
        Returns:
            str: 图标字符串
        """
        if not self.config.enable_icons:
            return ""
        
        icon_set = self.ICONS.get(self.config.icon_style, self.ICONS[IconStyle.EMOJI])
        icon = icon_set.get(icon_name, "")
        return f"{icon} " if icon else ""
    
    def print_success(self, message: str, icon: bool = True) -> None:
        """
        打印成功消息
        
        Args:
            message: 消息内容
            icon: 是否显示图标
        """
        icon_str = self.get_icon("success") if icon else ""
        self.console.print(f"{icon_str}{message}", style="success")
    
    def print_error(self, message: str, icon: bool = True) -> None:
        """
        打印错误消息
        
        Args:
            message: 消息内容
            icon: 是否显示图标
        """
        icon_str = self.get_icon("error") if icon else ""
        self.console.print(f"{icon_str}{message}", style="error")
    
    def print_warning(self, message: str, icon: bool = True) -> None:
        """
        打印警告消息
        
        Args:
            message: 消息内容
            icon: 是否显示图标
        """
        icon_str = self.get_icon("warning") if icon else ""
        self.console.print(f"{icon_str}{message}", style="warning")
    
    def print_info(self, message: str, icon: bool = True) -> None:
        """
        打印信息消息
        
        Args:
            message: 消息内容
            icon: 是否显示图标
        """
        icon_str = self.get_icon("info") if icon else ""
        self.console.print(f"{icon_str}{message}", style="info")
    
    def print_header(self, title: str, subtitle: Optional[str] = None) -> None:
        """
        打印标题头部
        
        Args:
            title: 标题
            subtitle: 副标题
        """
        self.console.rule(f"[bold primary]{title}[/bold primary]")
        if subtitle:
            self.console.print(f"[muted]{subtitle}[/muted]", justify="center")
            self.console.print()
    
    def create_table(
        self,
        title: Optional[str] = None,
        show_header: bool = True,
        show_lines: bool = False,
        box_style: str = "rounded"
    ) -> Table:
        """
        创建表格
        
        Args:
            title: 表格标题
            show_header: 是否显示表头
            show_lines: 是否显示行线
            box_style: 边框样式
            
        Returns:
            Table: Rich 表格对象
        """
        box_map = {
            "rounded": ROUNDED,
            "minimal": MINIMAL,
            "simple": SIMPLE,
        }
        
        table = Table(
            title=title,
            show_header=show_header,
            show_lines=show_lines,
            box=box_map.get(box_style, ROUNDED),
            title_style="primary",
            header_style="secondary",
        )
        
        return table
    
    def create_panel(
        self,
        content: str,
        title: Optional[str] = None,
        border_style: str = "primary"
    ) -> Panel:
        """
        创建面板
        
        Args:
            content: 面板内容
            title: 面板标题
            border_style: 边框样式
            
        Returns:
            Panel: Rich 面板对象
        """
        return Panel(
            content,
            title=title,
            border_style=border_style,
            box=ROUNDED,
        )
    
    def print_table(self, table: Table) -> None:
        """
        打印表格
        
        Args:
            table: 表格对象
        """
        self.console.print(table)
    
    def print_panel(self, panel: Panel) -> None:
        """
        打印面板
        
        Args:
            panel: 面板对象
        """
        self.console.print(panel)
    
    def print_separator(self, char: str = "=", length: int = 60) -> None:
        """
        打印分隔线
        
        Args:
            char: 分隔符字符
            length: 分隔线长度
        """
        self.console.print(char * length, style="muted")
    
    def print_dict(self, data: Dict[str, Any], title: Optional[str] = None) -> None:
        """
        打印字典数据
        
        Args:
            data: 字典数据
            title: 标题
        """
        if title:
            self.console.print(f"\n[bold primary]{title}[/bold primary]")
        
        for key, value in data.items():
            self.console.print(f"  [secondary]{key}:[/secondary] {value}")
    
    def print_list(
        self,
        items: List[str],
        title: Optional[str] = None,
        numbered: bool = False
    ) -> None:
        """
        打印列表
        
        Args:
            items: 列表项
            title: 标题
            numbered: 是否编号
        """
        if title:
            self.console.print(f"\n[bold primary]{title}[/bold primary]")
        
        bullet = self.get_icon("bullet")
        for i, item in enumerate(items, 1):
            if numbered:
                self.console.print(f"  {i}. {item}")
            else:
                self.console.print(f"  {bullet}{item}")
    
    def clear_screen(self) -> None:
        """清空屏幕"""
        self.console.clear()
    
    def print_newline(self, count: int = 1) -> None:
        """
        打印空行
        
        Args:
            count: 空行数量
        """
        for _ in range(count):
            self.console.print()
    
    @property
    def progress_manager(self):
        """
        获取进度管理器实例（懒加载）
        
        Returns:
            ProgressManager: 进度管理器实例
        """
        if self._progress_manager is None:
            from .progress_manager import ProgressManager
            self._progress_manager = ProgressManager(self.console, self.config)
        return self._progress_manager
