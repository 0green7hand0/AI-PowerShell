"""
交互式输入管理器

提供增强的用户输入体验，包括：
- 命令自动补全
- 命令历史记录和浏览
- 智能建议
"""

from typing import List, Optional, Callable, Dict, Tuple
from pathlib import Path
from difflib import get_close_matches
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
from .ui_manager import UIManager


class CommandCompleter(Completer):
    """命令补全器"""
    
    def __init__(self, commands: List[str], subcommands: dict = None):
        """
        初始化命令补全器
        
        Args:
            commands: 主命令列表
            subcommands: 子命令字典 {主命令: [子命令列表]}
        """
        self.commands = commands
        self.subcommands = subcommands or {}
    
    def get_completions(self, document, complete_event):
        """
        获取补全建议
        
        Args:
            document: 当前文档
            complete_event: 补全事件
            
        Yields:
            Completion: 补全建议
        """
        text = document.text_before_cursor
        words = text.split()
        
        # 如果是空输入或只有一个词，补全主命令
        if len(words) == 0 or (len(words) == 1 and not text.endswith(' ')):
            word = words[0] if words else ''
            for cmd in self.commands:
                if cmd.startswith(word.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(word),
                        display=cmd,
                        display_meta='命令'
                    )
        
        # 如果有主命令，补全子命令
        elif len(words) >= 1:
            main_cmd = words[0].lower()
            if main_cmd in self.subcommands:
                current_word = words[-1] if not text.endswith(' ') else ''
                for subcmd in self.subcommands[main_cmd]:
                    if subcmd.startswith(current_word.lower()):
                        yield Completion(
                            subcmd,
                            start_position=-len(current_word),
                            display=subcmd,
                            display_meta='子命令'
                        )


class InteractiveInputManager:
    """交互式输入管理器"""
    
    def __init__(self, ui_manager: UIManager, history_file: Optional[str] = None):
        """
        初始化交互式输入管理器
        
        Args:
            ui_manager: UI 管理器实例
            history_file: 历史记录文件路径
        """
        self.ui_manager = ui_manager
        self.history_file = history_file or ".ai_powershell_history"
        
        # 确保历史文件目录存在
        history_path = Path(self.history_file)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化历史记录
        self.history = FileHistory(str(history_path))
        
        # 定义可用命令
        self.commands = [
            'help', '帮助',
            'history', '历史',
            'clear', '清屏',
            'exit', 'quit', '退出',
            'template'
        ]
        
        # 定义子命令
        self.subcommands = {
            'template': ['create', 'list', 'edit', 'delete', 'export', 'import', 'history', 'restore', 'test']
        }
        
        # 创建命令补全器
        self.completer = CommandCompleter(self.commands, self.subcommands)
        
        # 创建提示样式
        self.prompt_style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'input': '#ffffff',
        })
        
        # 延迟初始化会话（仅在需要时创建）
        self._session = None
    
    @property
    def session(self) -> PromptSession:
        """
        获取或创建 PromptSession
        
        Returns:
            PromptSession: 提示会话实例
        """
        if self._session is None:
            try:
                self._session = PromptSession(
                    history=self.history,
                    completer=self.completer,
                    auto_suggest=AutoSuggestFromHistory(),
                    style=self.prompt_style,
                    enable_history_search=True,
                    complete_while_typing=True
                )
            except Exception:
                # 如果无法创建会话（例如在测试环境中），返回 None
                pass
        return self._session
    
    def get_user_input(self, prompt: str = "💬 请输入 > ") -> str:
        """
        获取用户输入（带自动补全和历史记录）
        
        Args:
            prompt: 提示文本
            
        Returns:
            str: 用户输入
        """
        try:
            if self.session:
                return self.session.prompt(prompt).strip()
            else:
                # 回退到标准输入
                return input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            return ""
    
    def get_confirmation(self, message: str, default: bool = False) -> bool:
        """
        获取用户确认
        
        Args:
            message: 确认消息
            default: 默认值
            
        Returns:
            bool: 用户确认结果
        """
        suffix = " (Y/n): " if default else " (y/N): "
        try:
            if self.session:
                response = self.session.prompt(message + suffix).strip().lower()
            else:
                response = input(message + suffix).strip().lower()
            
            if not response:
                return default
            
            return response in ['y', 'yes', '是', 'Y']
        except (KeyboardInterrupt, EOFError):
            return False
    
    def select_from_list(self, options: List[str], title: str, allow_custom: bool = False) -> Optional[str]:
        """
        从列表中选择
        
        Args:
            options: 选项列表
            title: 标题
            allow_custom: 是否允许自定义输入
            
        Returns:
            str: 选中的选项，如果取消则返回 None
        """
        if not options:
            return None
        
        # 显示标题
        self.ui_manager.print_info(f"\n{title}")
        self.ui_manager.console.print("-" * 60)
        
        # 显示选项
        for i, option in enumerate(options, 1):
            self.ui_manager.console.print(f"[{i}] {option}")
        
        if allow_custom:
            self.ui_manager.console.print("[0] 自定义输入")
        
        # 创建选项补全器
        option_completer = WordCompleter(
            [str(i) for i in range(1, len(options) + 1)],
            ignore_case=True
        )
        
        # 获取用户选择
        try:
            if self.session:
                choice = self.session.prompt(
                    "\n选择 (输入编号): ",
                    completer=option_completer
                ).strip()
            else:
                choice = input("\n选择 (输入编号): ").strip()
            
            if not choice:
                return None
            
            # 处理自定义输入
            if allow_custom and choice == "0":
                if self.session:
                    custom = self.session.prompt("请输入: ").strip()
                else:
                    custom = input("请输入: ").strip()
                return custom if custom else None
            
            # 处理数字选择
            try:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
                else:
                    self.ui_manager.print_error("无效的选择")
                    return None
            except ValueError:
                self.ui_manager.print_error("请输入有效的数字")
                return None
                
        except (KeyboardInterrupt, EOFError):
            return None
    
    def get_multiline_input(self, prompt: str, end_marker: str = "END") -> str:
        """
        获取多行输入
        
        Args:
            prompt: 提示文本
            end_marker: 结束标记
            
        Returns:
            str: 多行输入内容
        """
        self.ui_manager.print_info(f"{prompt} (输入 '{end_marker}' 结束):")
        lines = []
        
        try:
            while True:
                if self.session:
                    line = self.session.prompt("... ")
                else:
                    line = input("... ")
                if line.strip() == end_marker:
                    break
                lines.append(line)
            return '\n'.join(lines)
        except (KeyboardInterrupt, EOFError):
            return '\n'.join(lines)
    
    def add_command(self, command: str):
        """
        添加命令到补全列表
        
        Args:
            command: 命令名称
        """
        if command not in self.commands:
            self.commands.append(command)
            # 重新创建补全器
            self.completer = CommandCompleter(self.commands, self.subcommands)
    
    def add_subcommand(self, main_command: str, subcommand: str):
        """
        添加子命令到补全列表
        
        Args:
            main_command: 主命令
            subcommand: 子命令
        """
        if main_command not in self.subcommands:
            self.subcommands[main_command] = []
        
        if subcommand not in self.subcommands[main_command]:
            self.subcommands[main_command].append(subcommand)
            # 重新创建补全器
            self.completer = CommandCompleter(self.commands, self.subcommands)
    
    def suggest_similar_commands(self, invalid_command: str, threshold: float = 0.6) -> List[str]:
        """
        为错误命令建议相似命令
        
        Args:
            invalid_command: 无效的命令
            threshold: 相似度阈值 (0-1)
            
        Returns:
            List[str]: 相似命令列表
        """
        # 获取所有可能的命令（包括主命令和子命令）
        all_commands = self.commands.copy()
        for subcmds in self.subcommands.values():
            all_commands.extend(subcmds)
        
        # 使用 difflib 查找相似命令
        suggestions = get_close_matches(
            invalid_command.lower(),
            [cmd.lower() for cmd in all_commands],
            n=3,
            cutoff=threshold
        )
        
        # 返回原始大小写的命令
        result = []
        for suggestion in suggestions:
            for cmd in all_commands:
                if cmd.lower() == suggestion:
                    result.append(cmd)
                    break
        
        return result
    
    def validate_command_structure(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        验证命令结构
        
        Args:
            command: 要验证的命令
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误消息)
        """
        if not command or not command.strip():
            return False, "命令不能为空"
        
        words = command.strip().split()
        main_cmd = words[0].lower()
        
        # 检查主命令是否有效
        if main_cmd not in self.commands:
            suggestions = self.suggest_similar_commands(main_cmd)
            if suggestions:
                return False, f"未知命令 '{main_cmd}'。您是否想输入: {', '.join(suggestions)}?"
            else:
                return False, f"未知命令 '{main_cmd}'。输入 'help' 查看可用命令。"
        
        # 如果有子命令，验证子命令
        if len(words) > 1 and main_cmd in self.subcommands:
            subcmd = words[1].lower()
            if subcmd not in self.subcommands[main_cmd]:
                suggestions = get_close_matches(
                    subcmd,
                    self.subcommands[main_cmd],
                    n=3,
                    cutoff=0.6
                )
                if suggestions:
                    return False, f"未知子命令 '{subcmd}'。您是否想输入: {', '.join(suggestions)}?"
                else:
                    return False, f"未知子命令 '{subcmd}'。可用子命令: {', '.join(self.subcommands[main_cmd])}"
        
        return True, None
    
    def get_command_help(self, command: str) -> Optional[str]:
        """
        获取命令帮助信息
        
        Args:
            command: 命令名称
            
        Returns:
            Optional[str]: 帮助信息
        """
        help_texts = {
            'help': '显示帮助信息',
            '帮助': '显示帮助信息',
            'history': '显示命令历史',
            '历史': '显示命令历史',
            'clear': '清空屏幕',
            '清屏': '清空屏幕',
            'exit': '退出程序',
            'quit': '退出程序',
            '退出': '退出程序',
            'template': '模板管理命令\n  子命令: create, list, edit, delete, export, import, history, restore, test'
        }
        
        return help_texts.get(command.lower())
    
    def get_parameter_hints(self, command: str) -> List[Dict[str, str]]:
        """
        获取命令参数提示
        
        Args:
            command: 命令字符串
            
        Returns:
            List[Dict[str, str]]: 参数提示列表
        """
        words = command.strip().split()
        if not words:
            return []
        
        main_cmd = words[0].lower()
        
        # 定义命令参数
        parameter_hints = {
            'template': {
                'create': [],
                'list': [
                    {'name': '--custom-only', 'description': '仅显示自定义模板', 'required': False}
                ],
                'edit': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True}
                ],
                'delete': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True}
                ],
                'export': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True},
                    {'name': '-o, --output', 'description': '输出路径', 'required': True}
                ],
                'import': [
                    {'name': 'package_path', 'description': '模板包路径', 'required': True},
                    {'name': '--overwrite', 'description': '覆盖已存在的模板', 'required': False}
                ],
                'history': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True}
                ],
                'restore': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True},
                    {'name': 'version', 'description': '版本号', 'required': True}
                ],
                'test': [
                    {'name': 'template_id', 'description': '模板ID', 'required': True},
                    {'name': '--no-script', 'description': '不显示生成的脚本', 'required': False}
                ]
            }
        }
        
        # 获取子命令参数
        if len(words) > 1 and main_cmd in parameter_hints:
            subcmd = words[1].lower()
            if subcmd in parameter_hints[main_cmd]:
                return parameter_hints[main_cmd][subcmd]
        
        return []
    
    def show_parameter_hints(self, command: str):
        """
        显示命令参数提示
        
        Args:
            command: 命令字符串
        """
        hints = self.get_parameter_hints(command)
        
        if hints:
            self.ui_manager.print_info("\n参数说明:")
            for hint in hints:
                required = "必需" if hint['required'] else "可选"
                self.ui_manager.console.print(
                    f"  • {hint['name']} ({required}): {hint['description']}"
                )
            print()


class CommandValidator(Validator):
    """命令验证器"""
    
    def __init__(self, input_manager: InteractiveInputManager):
        """
        初始化命令验证器
        
        Args:
            input_manager: 交互式输入管理器
        """
        self.input_manager = input_manager
    
    def validate(self, document):
        """
        验证命令
        
        Args:
            document: 文档对象
            
        Raises:
            ValidationError: 如果命令无效
        """
        text = document.text.strip()
        
        # 空命令不验证
        if not text:
            return
        
        # 验证命令结构
        is_valid, error_msg = self.input_manager.validate_command_structure(text)
        
        if not is_valid:
            raise ValidationError(
                message=error_msg,
                cursor_position=len(text)
            )
