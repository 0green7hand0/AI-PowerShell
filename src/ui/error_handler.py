"""
错误处理器

提供分类错误处理、友好的错误消息格式和解决方案建议。
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .models import ErrorContext, UIConfig
from .theme_manager import ThemeManager


class ErrorCategory(str, Enum):
    """错误类别枚举"""
    USER_ERROR = "user_error"  # 用户输入或操作错误
    SYSTEM_ERROR = "system_error"  # 系统或运行时错误
    CONFIG_ERROR = "config_error"  # 配置错误
    VALIDATION_ERROR = "validation_error"  # 验证错误
    IO_ERROR = "io_error"  # 文件 I/O 错误
    NETWORK_ERROR = "network_error"  # 网络错误
    PERMISSION_ERROR = "permission_error"  # 权限错误
    UNKNOWN_ERROR = "unknown_error"  # 未知错误


class ErrorHandler:
    """错误处理器 - 提供友好的错误消息和解决方案建议"""
    
    # 错误类别到用户友好标题的映射
    CATEGORY_TITLES = {
        ErrorCategory.USER_ERROR: "用户输入错误",
        ErrorCategory.SYSTEM_ERROR: "系统错误",
        ErrorCategory.CONFIG_ERROR: "配置错误",
        ErrorCategory.VALIDATION_ERROR: "验证错误",
        ErrorCategory.IO_ERROR: "文件操作错误",
        ErrorCategory.NETWORK_ERROR: "网络错误",
        ErrorCategory.PERMISSION_ERROR: "权限错误",
        ErrorCategory.UNKNOWN_ERROR: "未知错误",
    }
    
    # 错误类别到图标的映射
    CATEGORY_ICONS = {
        ErrorCategory.USER_ERROR: "⚠️",
        ErrorCategory.SYSTEM_ERROR: "❌",
        ErrorCategory.CONFIG_ERROR: "⚙️",
        ErrorCategory.VALIDATION_ERROR: "🔍",
        ErrorCategory.IO_ERROR: "📁",
        ErrorCategory.NETWORK_ERROR: "🌐",
        ErrorCategory.PERMISSION_ERROR: "🔒",
        ErrorCategory.UNKNOWN_ERROR: "❓",
    }
    
    # 常见错误模式和建议
    ERROR_PATTERNS = {
        "file not found": {
            "category": ErrorCategory.IO_ERROR,
            "suggestions": [
                "检查文件路径是否正确",
                "确认文件是否存在",
                "检查文件名拼写是否正确",
            ],
        },
        "permission denied": {
            "category": ErrorCategory.PERMISSION_ERROR,
            "suggestions": [
                "以管理员权限运行程序",
                "检查文件或目录的访问权限",
                "确认当前用户有足够的权限",
            ],
        },
        "connection": {
            "category": ErrorCategory.NETWORK_ERROR,
            "suggestions": [
                "检查网络连接是否正常",
                "确认服务器地址是否正确",
                "检查防火墙设置",
            ],
        },
        "invalid": {
            "category": ErrorCategory.VALIDATION_ERROR,
            "suggestions": [
                "检查输入格式是否正确",
                "参考文档中的示例",
                "使用 --help 查看正确的用法",
            ],
        },
        "config": {
            "category": ErrorCategory.CONFIG_ERROR,
            "suggestions": [
                "检查配置文件格式是否正确",
                "确认所有必需的配置项都已设置",
                "尝试删除配置文件以使用默认配置",
            ],
        },
    }
    
    def __init__(self, config: Optional[UIConfig] = None):
        """
        初始化错误处理器
        
        Args:
            config: UI 配置对象
        """
        self.config = config or UIConfig()
        self.theme_manager = ThemeManager(self.config.theme)
        self.console = Console(theme=self.theme_manager.rich_theme)
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        根据异常类型和消息自动分类错误
        
        Args:
            error: 异常对象
            
        Returns:
            ErrorCategory: 错误类别
        """
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # 根据异常类型分类
        if "permission" in error_type or "access" in error_type:
            return ErrorCategory.PERMISSION_ERROR
        elif "io" in error_type or "file" in error_type:
            return ErrorCategory.IO_ERROR
        elif "config" in error_type or "configuration" in error_type:
            return ErrorCategory.CONFIG_ERROR
        elif "validation" in error_type or "value" in error_type:
            return ErrorCategory.VALIDATION_ERROR
        elif "network" in error_type or "connection" in error_type:
            return ErrorCategory.NETWORK_ERROR
        
        # 根据错误消息内容分类
        for pattern, info in self.ERROR_PATTERNS.items():
            if pattern in error_message:
                return info["category"]
        
        # 默认分类
        if isinstance(error, (ValueError, TypeError)):
            return ErrorCategory.USER_ERROR
        elif isinstance(error, (OSError, IOError)):
            return ErrorCategory.IO_ERROR
        elif isinstance(error, PermissionError):
            return ErrorCategory.PERMISSION_ERROR
        
        return ErrorCategory.SYSTEM_ERROR
    
    def get_suggestions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """
        根据错误获取解决方案建议
        
        Args:
            error: 异常对象
            category: 错误类别
            
        Returns:
            List[str]: 建议列表
        """
        suggestions = []
        error_message = str(error).lower()
        
        # 从错误模式中获取建议
        for pattern, info in self.ERROR_PATTERNS.items():
            if pattern in error_message:
                suggestions.extend(info["suggestions"])
        
        # 根据类别添加通用建议
        if not suggestions:
            if category == ErrorCategory.USER_ERROR:
                suggestions = [
                    "检查命令语法是否正确",
                    "使用 --help 查看命令用法",
                    "参考文档中的示例",
                ]
            elif category == ErrorCategory.SYSTEM_ERROR:
                suggestions = [
                    "尝试重新运行命令",
                    "检查系统资源是否充足",
                    "查看日志文件获取更多信息",
                ]
            elif category == ErrorCategory.CONFIG_ERROR:
                suggestions = [
                    "检查配置文件格式",
                    "确认所有必需配置项已设置",
                    "尝试使用默认配置",
                ]
            elif category == ErrorCategory.VALIDATION_ERROR:
                suggestions = [
                    "检查输入值的格式和类型",
                    "确认输入值在允许的范围内",
                    "参考文档中的有效值示例",
                ]
            elif category == ErrorCategory.IO_ERROR:
                suggestions = [
                    "检查文件路径是否正确",
                    "确认文件或目录存在",
                    "检查磁盘空间是否充足",
                ]
            elif category == ErrorCategory.PERMISSION_ERROR:
                suggestions = [
                    "以管理员权限运行",
                    "检查文件或目录权限",
                    "确认当前用户有足够权限",
                ]
        
        return suggestions
    
    def create_error_context(
        self,
        error: Exception,
        category: Optional[ErrorCategory] = None,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        related_commands: Optional[List[str]] = None
    ) -> ErrorContext:
        """
        创建错误上下文
        
        Args:
            error: 异常对象
            category: 错误类别（如果为 None 则自动分类）
            details: 额外的错误详情
            suggestions: 自定义建议列表
            related_commands: 相关命令列表
            
        Returns:
            ErrorContext: 错误上下文对象
        """
        if category is None:
            category = self.categorize_error(error)
        
        if suggestions is None:
            suggestions = self.get_suggestions(error, category)
        
        return ErrorContext(
            error_type=category.value,
            message=str(error),
            details=details,
            suggestions=suggestions,
            related_commands=related_commands or []
        )
    
    def format_error_message(self, context: ErrorContext) -> str:
        """
        格式化错误消息为友好的文本
        
        Args:
            context: 错误上下文
            
        Returns:
            str: 格式化的错误消息
        """
        lines = []
        
        # 错误标题
        category = ErrorCategory(context.error_type)
        title = self.CATEGORY_TITLES.get(category, "错误")
        icon = self.CATEGORY_ICONS.get(category, "❌")
        
        if self.config.enable_icons:
            lines.append(f"{icon} {title}")
        else:
            lines.append(f"[{title}]")
        
        # 错误消息
        lines.append(f"\n{context.message}")
        
        # 详细信息
        if context.details:
            lines.append(f"\n详细信息: {context.details}")
        
        # 解决方案建议
        if context.suggestions:
            lines.append("\n建议的解决方案:")
            for i, suggestion in enumerate(context.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
        
        # 相关命令
        if context.related_commands:
            lines.append("\n相关命令:")
            for cmd in context.related_commands:
                lines.append(f"  • {cmd}")
        
        return "\n".join(lines)
    
    def display_error(
        self,
        error: Exception,
        category: Optional[ErrorCategory] = None,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        related_commands: Optional[List[str]] = None,
        show_traceback: bool = False
    ) -> None:
        """
        显示格式化的错误消息
        
        Args:
            error: 异常对象
            category: 错误类别
            details: 额外的错误详情
            suggestions: 自定义建议列表
            related_commands: 相关命令列表
            show_traceback: 是否显示堆栈跟踪
        """
        context = self.create_error_context(
            error, category, details, suggestions, related_commands
        )
        
        # 创建错误面板
        category_enum = ErrorCategory(context.error_type)
        title = self.CATEGORY_TITLES.get(category_enum, "错误")
        icon = self.CATEGORY_ICONS.get(category_enum, "❌")
        
        if self.config.enable_icons:
            panel_title = f"{icon} {title}"
        else:
            panel_title = f"[{title}]"
        
        # 构建面板内容
        content_parts = []
        
        # 错误消息
        content_parts.append(f"[bold error]{context.message}[/bold error]")
        
        # 详细信息
        if context.details:
            content_parts.append(f"\n[muted]详细信息:[/muted] {context.details}")
        
        # 解决方案建议
        if context.suggestions:
            content_parts.append("\n[bold info]建议的解决方案:[/bold info]")
            for i, suggestion in enumerate(context.suggestions, 1):
                content_parts.append(f"  [info]{i}.[/info] {suggestion}")
        
        # 相关命令
        if context.related_commands:
            content_parts.append("\n[bold secondary]相关命令:[/bold secondary]")
            for cmd in context.related_commands:
                content_parts.append(f"  [secondary]•[/secondary] {cmd}")
        
        content = "\n".join(content_parts)
        
        # 显示错误面板
        panel = Panel(
            content,
            title=panel_title,
            border_style="error",
            expand=False,
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
        
        # 显示堆栈跟踪（如果需要）
        if show_traceback:
            self.console.print_exception()
    
    def display_error_table(self, errors: List[ErrorContext]) -> None:
        """
        以表格形式显示多个错误
        
        Args:
            errors: 错误上下文列表
        """
        if not errors:
            return
        
        table = Table(
            title="错误摘要",
            show_header=True,
            header_style="bold secondary",
            border_style="error",
        )
        
        table.add_column("类型", style="warning", no_wrap=True)
        table.add_column("消息", style="error")
        table.add_column("建议", style="info")
        
        for context in errors:
            category = ErrorCategory(context.error_type)
            error_type = self.CATEGORY_TITLES.get(category, "错误")
            
            suggestions_text = "\n".join(
                f"{i}. {s}" for i, s in enumerate(context.suggestions[:3], 1)
            ) if context.suggestions else "无"
            
            table.add_row(
                error_type,
                context.message[:50] + "..." if len(context.message) > 50 else context.message,
                suggestions_text
            )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def handle_error(
        self,
        error: Exception,
        category: Optional[ErrorCategory] = None,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        related_commands: Optional[List[str]] = None,
        show_traceback: bool = False,
        exit_on_error: bool = False
    ) -> ErrorContext:
        """
        处理错误的便捷方法
        
        Args:
            error: 异常对象
            category: 错误类别
            details: 额外的错误详情
            suggestions: 自定义建议列表
            related_commands: 相关命令列表
            show_traceback: 是否显示堆栈跟踪
            exit_on_error: 是否在错误后退出程序
            
        Returns:
            ErrorContext: 错误上下文对象
        """
        self.display_error(
            error,
            category,
            details,
            suggestions,
            related_commands,
            show_traceback
        )
        
        context = self.create_error_context(
            error, category, details, suggestions, related_commands
        )
        
        if exit_on_error:
            import sys
            sys.exit(1)
        
        return context
