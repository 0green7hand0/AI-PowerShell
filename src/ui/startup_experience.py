"""
启动体验优化

优化交互模式的启动体验，包括功能概览、使用提示和就绪状态指示。
"""

import time
from typing import Optional, List, Dict
from pathlib import Path

from .ui_manager import UIManager
from .startup_wizard import StartupWizard, CheckStatus


class StartupExperience:
    """启动体验管理器"""
    
    def __init__(self, ui_manager: Optional[UIManager] = None):
        """
        初始化启动体验管理器
        
        Args:
            ui_manager: UI 管理器实例
        """
        self.ui_manager = ui_manager or UIManager()
        self.wizard = StartupWizard(self.ui_manager)
    
    def run_startup_sequence(self, skip_wizard: bool = False) -> bool:
        """
        运行启动序列
        
        Args:
            skip_wizard: 是否跳过欢迎向导
            
        Returns:
            bool: 是否成功启动
        """
        start_time = time.time()
        
        # 1. 检查是否首次运行
        if not skip_wizard and self.wizard.is_first_run():
            return self.wizard.run_welcome_wizard()
        
        # 2. 快速系统检查
        success, checks = self.wizard.quick_system_check()
        
        # 3. 显示启动信息
        self._display_startup_banner()
        
        # 4. 如果有问题，显示警告
        if not success:
            self._display_startup_warnings(checks)
        
        # 5. 显示功能概览
        self._display_feature_overview()
        
        # 6. 显示使用提示
        self._display_quick_tips()
        
        # 7. 显示就绪状态
        elapsed = time.time() - start_time
        self._display_ready_status(elapsed)
        
        return success
    
    def _display_startup_banner(self) -> None:
        """显示启动横幅 - 现代简洁风格"""
        from rich.panel import Panel
        from rich.text import Text
        
        # 创建标题文本
        title = Text()
        title.append("AI PowerShell", style="bold cyan")
        title.append(" ", style="")
        title.append("智能助手", style="bold white")
        
        # 创建副标题
        subtitle = Text()
        subtitle.append("将自然语言转换为 PowerShell 命令", style="dim white")
        
        # 创建版本信息
        version = Text()
        version.append("v2.0.0", style="dim cyan")
        
        # 组合内容
        content = Text()
        content.append(title)
        content.append("\n")
        content.append(subtitle)
        content.append("\n\n")
        content.append(version)
        
        # 创建面板
        panel = Panel(
            content,
            border_style="cyan",
            padding=(1, 2),
            expand=False
        )
        
        self.ui_manager.console.print()
        self.ui_manager.console.print(panel)
        self.ui_manager.console.print()
    
    def _display_startup_warnings(self, checks: List) -> None:
        """
        显示启动警告
        
        Args:
            checks: 检查结果列表
        """
        warnings = [c for c in checks if c.status != CheckStatus.PASSED]
        
        if warnings:
            self.ui_manager.print_newline()
            self.ui_manager.print_warning("检测到以下问题:")
            
            for check in warnings:
                icon = "⚠" if check.status == CheckStatus.WARNING else "✗"
                self.ui_manager.console.print(
                    f"  {icon} {check.name}: {check.message}",
                    style="warning" if check.status == CheckStatus.WARNING else "error"
                )
            
            self.ui_manager.print_newline()
            self.ui_manager.print_info("提示: 使用 'help' 命令查看帮助信息")
    
    def _display_feature_overview(self) -> None:
        """显示功能概览 - 简洁风格"""
        from rich.columns import Columns
        from rich.panel import Panel
        from rich.text import Text
        
        # 创建功能卡片
        features = [
            ("💬", "自然语言", "中文描述转命令"),
            ("🔒", "安全验证", "保护系统安全"),
            ("📝", "命令历史", "快速查看重用"),
        ]
        
        panels = []
        for icon, title, desc in features:
            content = Text()
            content.append(f"{icon} ", style="")
            content.append(title, style="bold white")
            content.append(f"\n{desc}", style="dim white")
            
            panel = Panel(
                content,
                border_style="dim cyan",
                padding=(0, 1),
                expand=True
            )
            panels.append(panel)
        
        self.ui_manager.console.print(Columns(panels, equal=True, expand=True))
    
    def _display_quick_tips(self) -> None:
        """显示快速提示 - 简洁风格"""
        from rich.table import Table
        
        self.ui_manager.print_newline()
        
        # 创建提示表格
        table = Table(
            show_header=False,
            show_edge=False,
            padding=(0, 2),
            box=None
        )
        
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="dim white")
        
        tips = [
            ("输入中文", "例如: 显示当前时间, 列出所有文件"),
            ("help", "查看帮助信息"),
            ("history", "查看命令历史"),
            ("exit", "退出程序 (或 Ctrl+C)"),
        ]
        
        for cmd, desc in tips:
            table.add_row(cmd, desc)
        
        self.ui_manager.console.print(table)
    
    def _display_ready_status(self, elapsed_time: float) -> None:
        """
        显示就绪状态 - 简洁风格
        
        Args:
            elapsed_time: 启动耗时（秒）
        """
        from rich.text import Text
        
        self.ui_manager.print_newline()
        
        # 创建就绪消息
        ready_text = Text()
        ready_text.append("●", style="bold green")
        ready_text.append(" Ready", style="bold white")
        ready_text.append(f"  ({elapsed_time:.2f}s)", style="dim white")
        
        self.ui_manager.console.print(ready_text)
        self.ui_manager.print_newline()
    
    def display_interactive_prompt(self) -> None:
        """显示交互式提示符（简化版，用于每次输入）"""
        # 这个方法可以在每次用户输入前调用，显示简洁的提示
        pass
    
    def display_session_summary(self, stats: Dict) -> None:
        """
        显示会话摘要（退出时）
        
        Args:
            stats: 会话统计信息
        """
        self.ui_manager.print_newline()
        self.ui_manager.print_separator("=", 60)
        self.ui_manager.print_header("📊 会话摘要", None)
        
        summary_items = [
            ("执行命令数", stats.get('commands_executed', 0)),
            ("成功执行", stats.get('successful_commands', 0)),
            ("失败执行", stats.get('failed_commands', 0)),
            ("会话时长", f"{stats.get('session_duration', 0):.1f} 秒"),
        ]
        
        for label, value in summary_items:
            self.ui_manager.console.print(
                f"  {label}:",
                style="secondary",
                end=" "
            )
            self.ui_manager.console.print(str(value), style="primary")
        
        self.ui_manager.print_newline()
        self.ui_manager.print_success("感谢使用 AI PowerShell 智能助手!")
        self.ui_manager.print_separator("=", 60)
        self.ui_manager.print_newline()


class StartupPerformanceOptimizer:
    """启动性能优化器"""
    
    @staticmethod
    def lazy_import_heavy_modules():
        """延迟导入重型模块"""
        # 这个方法可以用于延迟导入一些不是立即需要的模块
        # 例如: AI 引擎、模板引擎等
        pass
    
    @staticmethod
    def preload_common_data():
        """预加载常用数据"""
        # 预加载配置、模板等常用数据
        pass
    
    @staticmethod
    def cache_system_info():
        """缓存系统信息"""
        # 缓存系统信息以避免重复检查
        import platform
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'machine': platform.machine(),
        }
