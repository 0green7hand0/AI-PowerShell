"""
启动向导和系统检查

实现首次启动欢迎向导、系统状态检查和配置问题自动检测修复。
"""

import sys
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .ui_manager import UIManager
from .models import UIConfig


class CheckStatus(Enum):
    """检查状态"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SystemCheck:
    """系统检查结果"""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    fix_available: bool = False
    fix_command: Optional[str] = None


class StartupWizard:
    """启动向导 - 处理首次启动和系统检查"""
    
    FIRST_RUN_MARKER = ".ai_powershell_initialized"
    
    def __init__(self, ui_manager: Optional[UIManager] = None):
        """
        初始化启动向导
        
        Args:
            ui_manager: UI 管理器实例
        """
        self.ui_manager = ui_manager or UIManager()
        self.checks: List[SystemCheck] = []
    
    def is_first_run(self) -> bool:
        """
        检查是否首次运行
        
        Returns:
            bool: 是否首次运行
        """
        marker_path = Path(self.FIRST_RUN_MARKER)
        return not marker_path.exists()
    
    def mark_initialized(self) -> None:
        """标记已初始化"""
        marker_path = Path(self.FIRST_RUN_MARKER)
        marker_path.touch()
    
    def run_welcome_wizard(self) -> bool:
        """
        运行欢迎向导
        
        Returns:
            bool: 是否成功完成向导
        """
        self.ui_manager.clear_screen()
        
        # 显示欢迎信息
        self._display_welcome()
        
        # 运行系统检查
        self.ui_manager.print_newline()
        self.ui_manager.print_header("系统检查", "正在检查系统环境...")
        self.ui_manager.print_newline()
        
        self.run_system_checks()
        
        # 显示检查结果
        self._display_check_results()
        
        # 询问是否修复问题
        if self._has_fixable_issues():
            self.ui_manager.print_newline()
            response = input("是否自动修复可修复的问题? (y/N): ").strip().lower()
            if response in ['y', 'yes', '是']:
                self._fix_issues()
        
        # 标记已初始化
        self.mark_initialized()
        
        # 显示完成信息
        self.ui_manager.print_newline()
        self.ui_manager.print_success("欢迎向导完成!")
        self.ui_manager.print_info("按 Enter 继续...")
        input()
        
        return True
    
    def _display_welcome(self) -> None:
        """显示欢迎信息 - 现代简洁风格"""
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
        
        self.ui_manager.print_info("首次运行，正在进行系统检查...")
    
    def run_system_checks(self) -> List[SystemCheck]:
        """
        运行系统检查
        
        Returns:
            List[SystemCheck]: 检查结果列表
        """
        self.checks = []
        
        # 1. Python 版本检查
        self.checks.append(self._check_python_version())
        
        # 2. PowerShell 可用性检查
        self.checks.append(self._check_powershell())
        
        # 3. 配置文件检查
        self.checks.append(self._check_config_files())
        
        # 4. 日志目录检查
        self.checks.append(self._check_log_directory())
        
        # 5. 模板目录检查
        self.checks.append(self._check_template_directory())
        
        # 6. 存储目录检查
        self.checks.append(self._check_storage_directory())
        
        # 7. 依赖包检查
        self.checks.append(self._check_dependencies())
        
        return self.checks
    
    def _check_python_version(self) -> SystemCheck:
        """检查 Python 版本"""
        version = sys.version_info
        required_major, required_minor = 3, 8
        
        if version.major >= required_major and version.minor >= required_minor:
            return SystemCheck(
                name="Python 版本",
                status=CheckStatus.PASSED,
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details=f"满足最低要求 (>= {required_major}.{required_minor})"
            )
        else:
            return SystemCheck(
                name="Python 版本",
                status=CheckStatus.FAILED,
                message=f"Python {version.major}.{version.minor}.{version.micro}",
                details=f"需要 Python >= {required_major}.{required_minor}",
                fix_available=False
            )
    
    def _check_powershell(self) -> SystemCheck:
        """检查 PowerShell 可用性"""
        import subprocess
        
        try:
            # 尝试运行 PowerShell 命令
            result = subprocess.run(
                ['powershell', '-Command', 'echo test'],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                # 获取 PowerShell 版本
                version_result = subprocess.run(
                    ['powershell', '-Command', '$PSVersionTable.PSVersion.ToString()'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                version = version_result.stdout.strip() if version_result.returncode == 0 else "未知"
                
                return SystemCheck(
                    name="PowerShell",
                    status=CheckStatus.PASSED,
                    message=f"PowerShell {version}",
                    details="PowerShell 可用"
                )
            else:
                return SystemCheck(
                    name="PowerShell",
                    status=CheckStatus.WARNING,
                    message="PowerShell 响应异常",
                    details="PowerShell 可能未正确配置"
                )
        except FileNotFoundError:
            return SystemCheck(
                name="PowerShell",
                status=CheckStatus.FAILED,
                message="未找到 PowerShell",
                details="请确保 PowerShell 已安装并在 PATH 中",
                fix_available=False
            )
        except Exception as e:
            return SystemCheck(
                name="PowerShell",
                status=CheckStatus.WARNING,
                message="检查失败",
                details=f"无法检查 PowerShell: {str(e)}"
            )
    
    def _check_config_files(self) -> SystemCheck:
        """检查配置文件"""
        config_dir = Path("config")
        required_files = ["default.yaml", "templates.yaml", "ui.yaml"]
        
        if not config_dir.exists():
            return SystemCheck(
                name="配置文件",
                status=CheckStatus.FAILED,
                message="配置目录不存在",
                details=f"未找到 {config_dir}",
                fix_available=True,
                fix_command="create_config_dir"
            )
        
        missing_files = [f for f in required_files if not (config_dir / f).exists()]
        
        if not missing_files:
            return SystemCheck(
                name="配置文件",
                status=CheckStatus.PASSED,
                message="所有配置文件存在",
                details=f"找到 {len(required_files)} 个配置文件"
            )
        elif len(missing_files) < len(required_files):
            return SystemCheck(
                name="配置文件",
                status=CheckStatus.WARNING,
                message=f"缺少 {len(missing_files)} 个配置文件",
                details=f"缺少: {', '.join(missing_files)}",
                fix_available=True,
                fix_command="create_missing_configs"
            )
        else:
            return SystemCheck(
                name="配置文件",
                status=CheckStatus.FAILED,
                message="所有配置文件缺失",
                details="需要创建默认配置文件",
                fix_available=True,
                fix_command="create_all_configs"
            )
    
    def _check_log_directory(self) -> SystemCheck:
        """检查日志目录"""
        log_dir = Path("logs")
        
        if log_dir.exists() and log_dir.is_dir():
            return SystemCheck(
                name="日志目录",
                status=CheckStatus.PASSED,
                message="日志目录存在",
                details=str(log_dir.absolute())
            )
        else:
            return SystemCheck(
                name="日志目录",
                status=CheckStatus.WARNING,
                message="日志目录不存在",
                details="将在首次运行时创建",
                fix_available=True,
                fix_command="create_log_dir"
            )
    
    def _check_template_directory(self) -> SystemCheck:
        """检查模板目录"""
        template_dir = Path("templates")
        
        if not template_dir.exists():
            return SystemCheck(
                name="模板目录",
                status=CheckStatus.WARNING,
                message="模板目录不存在",
                details="将在首次运行时创建",
                fix_available=True,
                fix_command="create_template_dir"
            )
        
        # 检查是否有模板文件
        template_files = list(template_dir.rglob("*.yaml"))
        
        if template_files:
            return SystemCheck(
                name="模板目录",
                status=CheckStatus.PASSED,
                message=f"找到 {len(template_files)} 个模板",
                details=str(template_dir.absolute())
            )
        else:
            return SystemCheck(
                name="模板目录",
                status=CheckStatus.WARNING,
                message="模板目录为空",
                details="可以稍后添加自定义模板"
            )
    
    def _check_storage_directory(self) -> SystemCheck:
        """检查存储目录"""
        storage_dir = Path("data")
        
        if storage_dir.exists() and storage_dir.is_dir():
            return SystemCheck(
                name="存储目录",
                status=CheckStatus.PASSED,
                message="存储目录存在",
                details=str(storage_dir.absolute())
            )
        else:
            return SystemCheck(
                name="存储目录",
                status=CheckStatus.WARNING,
                message="存储目录不存在",
                details="将在首次运行时创建",
                fix_available=True,
                fix_command="create_storage_dir"
            )
    
    def _check_dependencies(self) -> SystemCheck:
        """检查依赖包"""
        required_packages = [
            'rich',
            'click',
            'prompt_toolkit',
            'pydantic',
            'yaml',
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if not missing_packages:
            return SystemCheck(
                name="依赖包",
                status=CheckStatus.PASSED,
                message="所有依赖包已安装",
                details=f"检查了 {len(required_packages)} 个包"
            )
        else:
            return SystemCheck(
                name="依赖包",
                status=CheckStatus.FAILED,
                message=f"缺少 {len(missing_packages)} 个依赖包",
                details=f"缺少: {', '.join(missing_packages)}",
                fix_available=True,
                fix_command="install_dependencies"
            )
    
    def _display_check_results(self) -> None:
        """显示检查结果"""
        from .table_manager import TableManager, ColumnConfig, TableConfig
        
        table_manager = TableManager(self.ui_manager.console)
        
        # 准备表格数据
        table_data = []
        for check in self.checks:
            status_icon = {
                CheckStatus.PASSED: "✓",
                CheckStatus.WARNING: "⚠",
                CheckStatus.FAILED: "✗",
                CheckStatus.SKIPPED: "-",
            }.get(check.status, "?")
            
            status_style = {
                CheckStatus.PASSED: "success",
                CheckStatus.WARNING: "warning",
                CheckStatus.FAILED: "error",
                CheckStatus.SKIPPED: "muted",
            }.get(check.status, "")
            
            table_data.append({
                'status': status_icon,
                'name': check.name,
                'message': check.message,
                'details': check.details or "",
            })
        
        # 定义列
        columns = [
            ColumnConfig(name='status', header='状态', width=6, justify='center', style='bold'),
            ColumnConfig(name='name', header='检查项', width=15, style='primary'),
            ColumnConfig(name='message', header='结果', width=30, style='secondary'),
            ColumnConfig(name='details', header='详情', width=40, style='muted'),
        ]
        
        config = TableConfig(show_lines=False, box_style='rounded')
        table_manager.display_table(table_data, columns, config)
        
        # 显示统计
        passed = sum(1 for c in self.checks if c.status == CheckStatus.PASSED)
        warnings = sum(1 for c in self.checks if c.status == CheckStatus.WARNING)
        failed = sum(1 for c in self.checks if c.status == CheckStatus.FAILED)
        
        self.ui_manager.print_newline()
        self.ui_manager.print_info(
            f"检查完成: {passed} 通过, {warnings} 警告, {failed} 失败"
        )
    
    def _has_fixable_issues(self) -> bool:
        """检查是否有可修复的问题"""
        return any(c.fix_available for c in self.checks if c.status != CheckStatus.PASSED)
    
    def _fix_issues(self) -> None:
        """修复问题"""
        self.ui_manager.print_newline()
        self.ui_manager.print_header("自动修复", "正在修复可修复的问题...")
        self.ui_manager.print_newline()
        
        for check in self.checks:
            if check.fix_available and check.status != CheckStatus.PASSED:
                self.ui_manager.print_info(f"修复: {check.name}...")
                
                try:
                    if check.fix_command == "create_config_dir":
                        Path("config").mkdir(exist_ok=True)
                        self.ui_manager.print_success(f"  ✓ 已创建配置目录")
                    
                    elif check.fix_command == "create_log_dir":
                        Path("logs").mkdir(exist_ok=True)
                        self.ui_manager.print_success(f"  ✓ 已创建日志目录")
                    
                    elif check.fix_command == "create_template_dir":
                        Path("templates").mkdir(exist_ok=True)
                        self.ui_manager.print_success(f"  ✓ 已创建模板目录")
                    
                    elif check.fix_command == "create_storage_dir":
                        Path("data").mkdir(exist_ok=True)
                        self.ui_manager.print_success(f"  ✓ 已创建存储目录")
                    
                    elif check.fix_command == "install_dependencies":
                        self.ui_manager.print_warning(
                            f"  请手动运行: pip install -r requirements.txt"
                        )
                    
                    else:
                        self.ui_manager.print_warning(f"  未知的修复命令: {check.fix_command}")
                
                except Exception as e:
                    self.ui_manager.print_error(f"  ✗ 修复失败: {str(e)}")
        
        self.ui_manager.print_newline()
        self.ui_manager.print_success("修复完成!")
    
    def quick_system_check(self) -> Tuple[bool, List[SystemCheck]]:
        """
        快速系统检查（用于每次启动）
        
        Returns:
            Tuple[bool, List[SystemCheck]]: (是否通过, 检查结果列表)
        """
        checks = [
            self._check_python_version(),
            self._check_config_files(),
            self._check_log_directory(),
        ]
        
        # 检查是否有严重问题
        has_critical_issues = any(c.status == CheckStatus.FAILED for c in checks)
        
        return not has_critical_issues, checks
