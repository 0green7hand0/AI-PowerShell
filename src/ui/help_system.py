"""
帮助系统

提供格式化的帮助信息和文档。
"""

from typing import List, Optional, Dict
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from .models import CommandDefinition, ArgumentDefinition
from .ui_manager import UIManager


class HelpSystem:
    """帮助系统 - 提供分层的格式化帮助信息"""
    
    def __init__(self, ui_manager: UIManager):
        """
        初始化帮助系统
        
        Args:
            ui_manager: UI 管理器实例
        """
        self.ui_manager = ui_manager
        self.commands: Dict[str, CommandDefinition] = {}
        self._initialize_commands()
    
    def _initialize_commands(self) -> None:
        """初始化命令定义"""
        # 主命令
        self.register_command(CommandDefinition(
            name="interactive",
            description="启动交互式模式，持续接收用户输入",
            usage="python -m src.main",
            examples=[
                "python -m src.main",
                "# 进入交互模式后输入中文描述",
            ],
            arguments=[],
            aliases=["i", "交互"]
        ))
        
        self.register_command(CommandDefinition(
            name="command",
            description="单次执行模式，翻译并执行中文描述",
            usage="python -m src.main -c <描述> [-a]",
            examples=[
                'python -m src.main -c "显示当前时间"',
                'python -m src.main -c "列出所有文件" -a',
            ],
            arguments=[
                ArgumentDefinition(
                    name="-c, --command",
                    type="string",
                    description="要翻译的中文描述",
                    required=True
                ),
                ArgumentDefinition(
                    name="-a, --auto",
                    type="flag",
                    description="自动执行，不需要用户确认",
                    required=False
                ),
            ],
            aliases=["c", "cmd"]
        ))
        
        # Template 命令及其子命令
        template_cmd = CommandDefinition(
            name="template",
            description="模板管理系统，用于创建、编辑和管理自定义脚本模板",
            usage="python -m src.main template <action> [options]",
            examples=[
                "python -m src.main template list",
                "python -m src.main template create",
            ],
            arguments=[],
            aliases=["t", "tmpl"]
        )
        
        # Template 子命令
        template_cmd.subcommands = [
            CommandDefinition(
                name="create",
                description="创建新的自定义模板",
                usage="python -m src.main template create",
                examples=["python -m src.main template create"],
                arguments=[]
            ),
            CommandDefinition(
                name="list",
                description="列出所有可用的模板",
                usage="python -m src.main template list [--custom-only]",
                examples=[
                    "python -m src.main template list",
                    "python -m src.main template list --custom-only",
                ],
                arguments=[
                    ArgumentDefinition(
                        name="--custom-only",
                        type="flag",
                        description="仅显示自定义模板",
                        required=False
                    )
                ]
            ),
            CommandDefinition(
                name="edit",
                description="编辑现有模板",
                usage="python -m src.main template edit <template_id>",
                examples=["python -m src.main template edit my_template"],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    )
                ]
            ),
            CommandDefinition(
                name="delete",
                description="删除模板",
                usage="python -m src.main template delete <template_id>",
                examples=["python -m src.main template delete my_template"],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    )
                ]
            ),
            CommandDefinition(
                name="export",
                description="导出模板到文件",
                usage="python -m src.main template export <template_id> -o <output_path>",
                examples=["python -m src.main template export my_template -o ./backup.zip"],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    ),
                    ArgumentDefinition(
                        name="-o, --output",
                        type="string",
                        description="输出路径",
                        required=True
                    )
                ]
            ),
            CommandDefinition(
                name="import",
                description="从文件导入模板",
                usage="python -m src.main template import <package_path> [--overwrite]",
                examples=[
                    "python -m src.main template import ./template.zip",
                    "python -m src.main template import ./template.zip --overwrite",
                ],
                arguments=[
                    ArgumentDefinition(
                        name="package_path",
                        type="string",
                        description="模板包路径",
                        required=True
                    ),
                    ArgumentDefinition(
                        name="--overwrite",
                        type="flag",
                        description="覆盖已存在的模板",
                        required=False
                    )
                ]
            ),
            CommandDefinition(
                name="history",
                description="查看模板的历史版本",
                usage="python -m src.main template history <template_id>",
                examples=["python -m src.main template history my_template"],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    )
                ]
            ),
            CommandDefinition(
                name="restore",
                description="恢复模板到指定版本",
                usage="python -m src.main template restore <template_id> <version>",
                examples=["python -m src.main template restore my_template 2"],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    ),
                    ArgumentDefinition(
                        name="version",
                        type="integer",
                        description="版本号",
                        required=True
                    )
                ]
            ),
            CommandDefinition(
                name="test",
                description="测试模板是否正常工作",
                usage="python -m src.main template test <template_id> [--no-script]",
                examples=[
                    "python -m src.main template test my_template",
                    "python -m src.main template test my_template --no-script",
                ],
                arguments=[
                    ArgumentDefinition(
                        name="template_id",
                        type="string",
                        description="模板ID",
                        required=True
                    ),
                    ArgumentDefinition(
                        name="--no-script",
                        type="flag",
                        description="不显示生成的脚本",
                        required=False
                    )
                ]
            ),
        ]
        
        self.register_command(template_cmd)
        
        # 交互模式特殊命令
        self.register_command(CommandDefinition(
            name="help",
            description="显示帮助信息",
            usage="help [command]",
            examples=[
                "help",
                "help template",
                "help template create",
            ],
            arguments=[
                ArgumentDefinition(
                    name="command",
                    type="string",
                    description="要查看帮助的命令（可选）",
                    required=False
                )
            ],
            aliases=["帮助", "?"]
        ))
        
        self.register_command(CommandDefinition(
            name="history",
            description="显示命令历史记录",
            usage="history",
            examples=["history"],
            arguments=[],
            aliases=["历史", "h"]
        ))
        
        self.register_command(CommandDefinition(
            name="clear",
            description="清空屏幕",
            usage="clear",
            examples=["clear"],
            arguments=[],
            aliases=["清屏", "cls"]
        ))
        
        self.register_command(CommandDefinition(
            name="exit",
            description="退出程序",
            usage="exit",
            examples=["exit"],
            arguments=[],
            aliases=["quit", "退出", "q"]
        ))
    
    def register_command(self, command: CommandDefinition) -> None:
        """
        注册命令定义
        
        Args:
            command: 命令定义对象
        """
        self.commands[command.name] = command
        # 注册别名
        for alias in command.aliases:
            self.commands[alias] = command
    
    def show_general_help(self) -> None:
        """显示总体帮助信息"""
        console = self.ui_manager.console
        
        # 标题
        self.ui_manager.print_header(
            "AI PowerShell 智能助手",
            "中文自然语言到 PowerShell 命令的智能转换"
        )
        
        # 概述
        overview_text = """
[bold primary]功能概述:[/bold primary]
  • 将中文自然语言转换为 PowerShell 命令
  • 智能安全检查和风险评估
  • 自定义脚本模板管理
  • 命令历史记录和上下文管理
        """
        console.print(Panel(overview_text.strip(), title="关于", border_style="primary"))
        console.print()
        
        # 使用模式
        console.print("[bold secondary]使用模式:[/bold secondary]")
        console.print()
        
        modes_table = self.ui_manager.create_table(show_header=True)
        modes_table.add_column("模式", style="primary", width=20)
        modes_table.add_column("命令", style="info", width=40)
        modes_table.add_column("说明", style="muted")
        
        modes_table.add_row(
            "交互模式",
            "python -m src.main",
            "持续接收用户输入"
        )
        modes_table.add_row(
            "单次执行",
            'python -m src.main -c "描述"',
            "翻译并执行一次"
        )
        modes_table.add_row(
            "模板管理",
            "python -m src.main template <action>",
            "管理自定义模板"
        )
        
        self.ui_manager.print_table(modes_table)
        console.print()
        
        # 主要命令
        console.print("[bold secondary]主要命令:[/bold secondary]")
        console.print()
        
        # 获取主要命令（排除别名）
        main_commands = {}
        for name, cmd in self.commands.items():
            if name == cmd.name:  # 只显示主命令，不显示别名
                main_commands[name] = cmd
        
        commands_table = self.ui_manager.create_table(show_header=True)
        commands_table.add_column("命令", style="primary", width=20)
        commands_table.add_column("说明", style="muted", width=50)
        
        # 按类别分组显示
        for cmd_name in ["interactive", "command", "template", "help", "history", "clear", "exit"]:
            if cmd_name in main_commands:
                cmd = main_commands[cmd_name]
                commands_table.add_row(cmd.name, cmd.description)
        
        self.ui_manager.print_table(commands_table)
        console.print()
        
        # 使用示例
        console.print("[bold secondary]使用示例:[/bold secondary]")
        console.print()
        
        examples = [
            ('交互模式', 'python -m src.main'),
            ('单次执行', 'python -m src.main -c "显示当前时间"'),
            ('自动执行', 'python -m src.main -c "列出所有文件" -a'),
            ('创建模板', 'python -m src.main template create'),
            ('列出模板', 'python -m src.main template list'),
        ]
        
        for title, example in examples:
            console.print(f"  [secondary]{title}:[/secondary]")
            console.print(f"    [info]{example}[/info]")
            console.print()
        
        # 获取更多帮助
        console.print("[muted]使用 'help <command>' 查看特定命令的详细帮助[/muted]")
        console.print("[muted]例如: help template, help command[/muted]")
        console.print()
    
    def show_command_help(self, command: str) -> None:
        """
        显示命令帮助信息
        
        Args:
            command: 命令名称（可以是主命令或子命令路径，如 "template.create"）
        """
        console = self.ui_manager.console
        
        # 解析命令路径
        parts = command.split('.')
        cmd_def = self.commands.get(parts[0])
        
        if not cmd_def:
            self.ui_manager.print_error(f"未知命令: {command}")
            suggestions = self.suggest_similar_commands(command)
            if suggestions:
                console.print(f"\n[muted]您是否想要:[/muted]")
                for suggestion in suggestions[:3]:
                    console.print(f"  [info]{suggestion}[/info]")
            return
        
        # 如果是子命令
        if len(parts) > 1:
            subcommand_name = parts[1]
            subcmd_def = None
            for subcmd in cmd_def.subcommands:
                if subcmd.name == subcommand_name:
                    subcmd_def = subcmd
                    break
            
            if not subcmd_def:
                self.ui_manager.print_error(f"未知子命令: {command}")
                return
            
            cmd_def = subcmd_def
        
        # 显示命令帮助
        self.ui_manager.print_header(f"命令: {cmd_def.name}", cmd_def.description)
        
        # 用法
        console.print("[bold secondary]用法:[/bold secondary]")
        console.print(f"  [info]{cmd_def.usage}[/info]")
        console.print()
        
        # 参数
        if cmd_def.arguments:
            console.print("[bold secondary]参数:[/bold secondary]")
            console.print()
            
            args_table = self.ui_manager.create_table(show_header=True)
            args_table.add_column("参数", style="primary", width=25)
            args_table.add_column("类型", style="secondary", width=12)
            args_table.add_column("必需", style="warning", width=8)
            args_table.add_column("说明", style="muted")
            
            for arg in cmd_def.arguments:
                required_str = "是" if arg.required else "否"
                args_table.add_row(
                    arg.name,
                    arg.type,
                    required_str,
                    arg.description
                )
                
                # 如果有默认值或选项，添加额外信息
                if arg.default:
                    args_table.add_row("", "", "", f"默认值: {arg.default}")
                if arg.choices:
                    args_table.add_row("", "", "", f"可选值: {', '.join(arg.choices)}")
            
            self.ui_manager.print_table(args_table)
            console.print()
        
        # 子命令
        if cmd_def.subcommands:
            console.print("[bold secondary]子命令:[/bold secondary]")
            console.print()
            
            subcmds_table = self.ui_manager.create_table(show_header=True)
            subcmds_table.add_column("子命令", style="primary", width=20)
            subcmds_table.add_column("说明", style="muted")
            
            for subcmd in cmd_def.subcommands:
                subcmds_table.add_row(subcmd.name, subcmd.description)
            
            self.ui_manager.print_table(subcmds_table)
            console.print()
            
            console.print(f"[muted]使用 'help {cmd_def.name}.<subcommand>' 查看子命令详细帮助[/muted]")
            console.print()
        
        # 示例
        if cmd_def.examples:
            console.print("[bold secondary]示例:[/bold secondary]")
            console.print()
            
            for i, example in enumerate(cmd_def.examples, 1):
                console.print(f"  {i}. [info]{example}[/info]")
            console.print()
        
        # 别名
        if cmd_def.aliases:
            console.print(f"[muted]别名: {', '.join(cmd_def.aliases)}[/muted]")
            console.print()
    
    def show_subcommand_help(self, parent_command: str, subcommand: str) -> None:
        """
        显示子命令帮助信息
        
        Args:
            parent_command: 父命令名称
            subcommand: 子命令名称
        """
        self.show_command_help(f"{parent_command}.{subcommand}")
    
    def list_all_commands(self) -> List[str]:
        """
        列出所有可用命令
        
        Returns:
            List[str]: 命令名称列表
        """
        # 只返回主命令，不包括别名
        return [name for name, cmd in self.commands.items() if name == cmd.name]
    
    def get_command_definition(self, command: str) -> Optional[CommandDefinition]:
        """
        获取命令定义
        
        Args:
            command: 命令名称
            
        Returns:
            Optional[CommandDefinition]: 命令定义对象，如果不存在则返回 None
        """
        return self.commands.get(command)
    
    def suggest_similar_commands(self, invalid_command: str) -> List[str]:
        """
        建议相似命令（使用编辑距离算法）
        
        Args:
            invalid_command: 无效的命令
            
        Returns:
            List[str]: 相似命令列表，按相似度排序
        """
        if not invalid_command:
            return []
        
        # 获取所有主命令（不包括别名）
        all_commands = self.list_all_commands()
        
        # 计算编辑距离并排序
        similarities = []
        for cmd in all_commands:
            distance = self._levenshtein_distance(invalid_command.lower(), cmd.lower())
            # 只考虑距离较小的命令（相似度较高）
            if distance <= max(3, len(invalid_command) // 2):
                similarities.append((cmd, distance))
        
        # 按距离排序
        similarities.sort(key=lambda x: x[1])
        
        # 返回前5个最相似的命令
        return [cmd for cmd, _ in similarities[:5]]
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离（Levenshtein距离）
        
        Args:
            s1: 第一个字符串
            s2: 第二个字符串
            
        Returns:
            int: 编辑距离
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # 插入、删除、替换的代价
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def show_interactive_help(self) -> None:
        """
        显示交互式帮助浏览界面
        
        允许用户浏览和搜索命令帮助
        """
        console = self.ui_manager.console
        
        while True:
            console.print("\n" + "=" * 60)
            console.print("[bold primary]交互式帮助系统[/bold primary]")
            console.print("=" * 60)
            console.print()
            console.print("[secondary]选项:[/secondary]")
            console.print("  [info]1.[/info] 查看总体帮助")
            console.print("  [info]2.[/info] 查看特定命令帮助")
            console.print("  [info]3.[/info] 列出所有命令")
            console.print("  [info]4.[/info] 搜索命令")
            console.print("  [info]0.[/info] 退出帮助")
            console.print()
            
            try:
                choice = input("请选择 (0-4): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    console.print()
                    self.show_general_help()
                elif choice == "2":
                    console.print()
                    cmd_name = input("请输入命令名称: ").strip()
                    if cmd_name:
                        console.print()
                        self.show_command_help(cmd_name)
                elif choice == "3":
                    console.print()
                    self._show_all_commands()
                elif choice == "4":
                    console.print()
                    keyword = input("请输入搜索关键词: ").strip()
                    if keyword:
                        console.print()
                        self._search_commands(keyword)
                else:
                    self.ui_manager.print_warning("无效的选择，请输入 0-4")
                
                input("\n按 Enter 继续...")
                
            except (KeyboardInterrupt, EOFError):
                break
        
        console.print("\n[muted]退出帮助系统[/muted]\n")
    
    def _show_all_commands(self) -> None:
        """显示所有可用命令的列表"""
        console = self.ui_manager.console
        
        console.print("[bold secondary]所有可用命令:[/bold secondary]")
        console.print()
        
        # 按类别分组
        categories = {
            "主要功能": ["interactive", "command"],
            "模板管理": ["template"],
            "交互命令": ["help", "history", "clear", "exit"],
        }
        
        for category, cmd_names in categories.items():
            console.print(f"\n[bold primary]{category}:[/bold primary]")
            
            table = self.ui_manager.create_table(show_header=False)
            table.add_column("命令", style="info", width=20)
            table.add_column("说明", style="muted", width=50)
            table.add_column("别名", style="secondary", width=20)
            
            for cmd_name in cmd_names:
                if cmd_name in self.commands:
                    cmd = self.commands[cmd_name]
                    aliases_str = ", ".join(cmd.aliases) if cmd.aliases else "-"
                    table.add_row(cmd.name, cmd.description, aliases_str)
            
            self.ui_manager.print_table(table)
    
    def _search_commands(self, keyword: str) -> None:
        """
        搜索包含关键词的命令
        
        Args:
            keyword: 搜索关键词
        """
        console = self.ui_manager.console
        keyword_lower = keyword.lower()
        
        # 搜索匹配的命令
        matches = []
        for name, cmd in self.commands.items():
            if name != cmd.name:  # 跳过别名
                continue
            
            # 在命令名称、描述、别名中搜索
            if (keyword_lower in cmd.name.lower() or
                keyword_lower in cmd.description.lower() or
                any(keyword_lower in alias.lower() for alias in cmd.aliases)):
                matches.append(cmd)
        
        if not matches:
            self.ui_manager.print_warning(f"未找到包含 '{keyword}' 的命令")
            
            # 提供建议
            suggestions = self.suggest_similar_commands(keyword)
            if suggestions:
                console.print("\n[muted]您可能想要:[/muted]")
                for suggestion in suggestions:
                    console.print(f"  [info]{suggestion}[/info]")
            return
        
        console.print(f"[bold secondary]找到 {len(matches)} 个匹配的命令:[/bold secondary]")
        console.print()
        
        table = self.ui_manager.create_table(show_header=True)
        table.add_column("命令", style="primary", width=20)
        table.add_column("说明", style="muted", width=50)
        
        for cmd in matches:
            table.add_row(cmd.name, cmd.description)
        
        self.ui_manager.print_table(table)
        console.print()
        console.print("[muted]使用 'help <command>' 查看详细帮助[/muted]")
    
    def show_quick_reference(self) -> None:
        """显示快速参考卡片"""
        console = self.ui_manager.console
        
        self.ui_manager.print_header("快速参考", "常用命令速查")
        
        # 创建多列布局
        quick_ref = [
            "[bold primary]基本命令[/bold primary]\n"
            "  help - 显示帮助\n"
            "  history - 查看历史\n"
            "  clear - 清空屏幕\n"
            "  exit - 退出程序",
            
            "[bold primary]模板管理[/bold primary]\n"
            "  template list - 列出模板\n"
            "  template create - 创建模板\n"
            "  template edit - 编辑模板\n"
            "  template delete - 删除模板",
            
            "[bold primary]执行模式[/bold primary]\n"
            "  交互模式 - 直接运行\n"
            "  单次执行 - 使用 -c\n"
            "  自动执行 - 添加 -a\n"
            "  查看版本 - 使用 -v",
        ]
        
        from rich.columns import Columns
        console.print(Columns(quick_ref, equal=True, expand=True))
        console.print()
    
    def show_examples_by_category(self, category: str) -> None:
        """
        按类别显示使用示例
        
        Args:
            category: 类别名称（如 "template", "command" 等）
        """
        console = self.ui_manager.console
        
        examples_map = {
            "template": [
                ("创建新模板", "python -m src.main template create"),
                ("列出所有模板", "python -m src.main template list"),
                ("编辑模板", "python -m src.main template edit my_template"),
                ("导出模板", "python -m src.main template export my_template -o backup.zip"),
                ("导入模板", "python -m src.main template import backup.zip"),
            ],
            "command": [
                ("显示当前时间", 'python -m src.main -c "显示当前时间"'),
                ("列出文件", 'python -m src.main -c "列出当前目录的所有文件"'),
                ("查看进程", 'python -m src.main -c "查看CPU使用率最高的5个进程"'),
                ("测试网络", 'python -m src.main -c "测试网络连接到 www.baidu.com"'),
            ],
            "interactive": [
                ("启动交互模式", "python -m src.main"),
                ("查看帮助", "输入: help"),
                ("查看历史", "输入: history"),
                ("清空屏幕", "输入: clear"),
                ("退出程序", "输入: exit"),
            ],
        }
        
        if category not in examples_map:
            self.ui_manager.print_error(f"未知类别: {category}")
            return
        
        console.print(f"[bold secondary]{category.upper()} 使用示例:[/bold secondary]")
        console.print()
        
        examples = examples_map[category]
        for i, (desc, example) in enumerate(examples, 1):
            console.print(f"  {i}. [secondary]{desc}[/secondary]")
            console.print(f"     [info]{example}[/info]")
            console.print()
    
    def format_command_usage(self, command: str) -> str:
        """
        格式化命令用法字符串
        
        Args:
            command: 命令名称
            
        Returns:
            str: 格式化的用法字符串
        """
        cmd_def = self.get_command_definition(command)
        if not cmd_def:
            return f"未知命令: {command}"
        
        return cmd_def.usage
