"""
模板管理界面优化模块

提供增强的模板管理命令界面，包括图标、颜色、交互式向导和操作反馈。
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

from .ui_manager import UIManager
from .table_manager import TableManager, ColumnConfig, TableConfig
from .progress_manager import ProgressManager
from ..template_engine.custom_models import CustomTemplate
from ..template_engine.exceptions import TemplateError


class TemplateManagerUI:
    """模板管理界面管理器"""
    
    # 模板分类图标映射
    CATEGORY_ICONS = {
        'automation': '🤖',
        'file_management': '📁',
        'system_monitoring': '📊',
        'custom': '⚙️',
        'default': '📄'
    }
    
    # 模板状态图标
    STATUS_ICONS = {
        'active': '✓',
        'inactive': '✗',
        'custom': '★',
        'system': '◆'
    }
    
    def __init__(self, ui_manager: Optional[UIManager] = None):
        """
        初始化模板管理界面
        
        Args:
            ui_manager: UI 管理器实例
        """
        self.ui_manager = ui_manager or UIManager()
        self.table_manager = TableManager(self.ui_manager.console)
        self.progress_manager = ProgressManager(self.ui_manager.console)
    
    def display_template_list_enhanced(
        self,
        templates: List[Any],
        title: str = "模板列表",
        show_icons: bool = True,
        group_by_category: bool = True
    ) -> None:
        """
        显示增强的模板列表（带图标和颜色）
        
        Args:
            templates: 模板列表
            title: 标题
            show_icons: 是否显示图标
            group_by_category: 是否按分类分组
        """
        if not templates:
            self.ui_manager.print_info("暂无模板")
            self.ui_manager.console.print(
                "\n💡 [dim]提示: 使用 'template create' 命令创建新模板[/dim]"
            )
            return
        
        # 显示标题
        self.ui_manager.print_header(title, f"共 {len(templates)} 个模板")
        
        # 转换模板对象为显示数据
        template_data = []
        for template in templates:
            # 获取分类图标
            category = getattr(template, 'category', 'default')
            icon = self.CATEGORY_ICONS.get(category, self.CATEGORY_ICONS['default'])
            
            # 判断是否为自定义模板
            is_custom = isinstance(template, CustomTemplate) or getattr(template, 'is_custom', False)
            status_icon = self.STATUS_ICONS['custom'] if is_custom else self.STATUS_ICONS['system']
            
            # 格式化名称（带图标）
            name_display = f"{icon} {template.name}" if show_icons else template.name
            if is_custom:
                name_display = f"{status_icon} {name_display}"
            
            # 格式化描述
            desc = template.description
            if len(desc) > 50:
                desc = desc[:47] + '...'
            
            # 格式化关键词
            keywords = getattr(template, 'keywords', [])
            keywords_display = ', '.join(keywords[:3]) if keywords else '-'
            if len(keywords) > 3:
                keywords_display += f' (+{len(keywords) - 3})'
            
            # 参数数量
            params = getattr(template, 'parameters', {})
            param_count = len(params) if params else 0
            
            data = {
                'name': name_display,
                'category': category,
                'description': desc,
                'keywords': keywords_display,
                'params': param_count,
                'type': '自定义' if is_custom else '系统',
            }
            template_data.append(data)
        
        # 定义列
        columns = [
            ColumnConfig(name='name', header='模板名称', width=30, style='bold cyan'),
            ColumnConfig(name='category', header='分类', width=15, style='magenta'),
            ColumnConfig(name='description', header='描述', width=40),
            ColumnConfig(name='keywords', header='关键词', width=20, style='dim'),
            ColumnConfig(name='params', header='参数', width=6, justify='center'),
            ColumnConfig(name='type', header='类型', width=8, style='yellow'),
        ]
        
        if group_by_category:
            # 按分类分组
            grouped_data = {}
            for data in template_data:
                category = data['category']
                if category not in grouped_data:
                    grouped_data[category] = []
                grouped_data[category].append(data)
            
            # 显示分组表格
            self.table_manager.display_grouped_data(
                grouped_data,
                columns,
                TableConfig(show_lines=False, box_style='rounded')
            )
        else:
            # 显示单个表格
            config = TableConfig(
                title=None,
                show_lines=False,
                box_style='rounded'
            )
            self.table_manager.display_table(template_data, columns, config)
        
        # 显示图例
        if show_icons:
            self._display_legend()
    
    def _display_legend(self) -> None:
        """显示图标图例"""
        self.ui_manager.console.print("\n[dim]图例:[/dim]")
        legend_items = [
            f"{self.STATUS_ICONS['custom']} 自定义模板",
            f"{self.STATUS_ICONS['system']} 系统模板",
            f"{self.CATEGORY_ICONS['automation']} 自动化",
            f"{self.CATEGORY_ICONS['file_management']} 文件管理",
            f"{self.CATEGORY_ICONS['system_monitoring']} 系统监控",
        ]
        self.ui_manager.console.print("  " + "  |  ".join(legend_items), style="dim")
    
    def interactive_template_wizard(self) -> Optional[Dict[str, Any]]:
        """
        交互式模板创建向导
        
        Returns:
            包含模板信息的字典，如果取消则返回 None
        """
        self.ui_manager.console.print(
            Panel.fit(
                "[bold cyan]🎨 模板创建向导[/bold cyan]\n"
                "[dim]按照步骤创建您的自定义模板[/dim]",
                border_style="cyan"
            )
        )
        
        try:
            # 步骤 1: 基本信息
            self.ui_manager.console.print("\n[bold]步骤 1/4: 基本信息[/bold]", style="primary")
            
            name = Prompt.ask(
                "  📝 模板名称",
                console=self.ui_manager.console
            ).strip()
            
            if not name:
                self.ui_manager.print_error("模板名称不能为空")
                return None
            
            description = Prompt.ask(
                "  📄 模板描述",
                console=self.ui_manager.console
            ).strip()
            
            if not description:
                self.ui_manager.print_error("模板描述不能为空")
                return None
            
            # 步骤 2: 分类选择
            self.ui_manager.console.print("\n[bold]步骤 2/4: 选择分类[/bold]", style="primary")
            
            categories = [
                ("automation", "🤖 自动化", "自动化任务和脚本"),
                ("file_management", "📁 文件管理", "文件和目录操作"),
                ("system_monitoring", "📊 系统监控", "系统状态和性能监控"),
                ("custom", "⚙️  自定义", "其他自定义功能"),
            ]
            
            self.ui_manager.console.print()
            for i, (cat_id, cat_name, cat_desc) in enumerate(categories, 1):
                self.ui_manager.console.print(
                    f"  [{i}] {cat_name} - [dim]{cat_desc}[/dim]"
                )
            
            category_choice = Prompt.ask(
                "\n  选择分类",
                choices=["1", "2", "3", "4"],
                default="4",
                console=self.ui_manager.console
            )
            
            category = categories[int(category_choice) - 1][0]
            
            # 步骤 3: 关键词
            self.ui_manager.console.print("\n[bold]步骤 3/4: 关键词[/bold]", style="primary")
            
            keywords_input = Prompt.ask(
                "  🏷️  关键词 (逗号分隔，可选)",
                default="",
                console=self.ui_manager.console
            ).strip()
            
            keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else []
            
            # 步骤 4: 脚本内容
            self.ui_manager.console.print("\n[bold]步骤 4/4: 脚本内容[/bold]", style="primary")
            
            self.ui_manager.console.print("\n  选择脚本来源:")
            self.ui_manager.console.print("  [1] 📂 从文件导入")
            self.ui_manager.console.print("  [2] ✏️  直接输入内容")
            
            source_choice = Prompt.ask(
                "\n  选择",
                choices=["1", "2"],
                default="1",
                console=self.ui_manager.console
            )
            
            script_content = ""
            
            if source_choice == "1":
                file_path = Prompt.ask(
                    "  📁 脚本文件路径",
                    console=self.ui_manager.console
                ).strip()
                
                if not Path(file_path).exists():
                    self.ui_manager.print_error(f"文件不存在: {file_path}")
                    return None
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        script_content = f.read()
                except Exception as e:
                    self.ui_manager.print_error(f"读取文件失败: {str(e)}")
                    return None
            else:
                self.ui_manager.console.print(
                    "\n  [dim]请输入脚本内容 (输入 'END' 单独一行结束):[/dim]"
                )
                lines = []
                while True:
                    try:
                        line = input()
                        if line.strip() == 'END':
                            break
                        lines.append(line)
                    except EOFError:
                        break
                script_content = '\n'.join(lines)
            
            if not script_content.strip():
                self.ui_manager.print_error("脚本内容不能为空")
                return None
            
            # 确认信息
            self.ui_manager.console.print("\n" + "─" * 60)
            self.ui_manager.console.print("[bold]📋 模板信息确认[/bold]", style="primary")
            self.ui_manager.console.print()
            self.ui_manager.console.print(f"  名称: [cyan]{name}[/cyan]")
            self.ui_manager.console.print(f"  描述: {description}")
            self.ui_manager.console.print(f"  分类: [magenta]{category}[/magenta]")
            if keywords:
                self.ui_manager.console.print(f"  关键词: {', '.join(keywords)}")
            self.ui_manager.console.print(f"  脚本长度: {len(script_content)} 字符")
            self.ui_manager.console.print("─" * 60)
            
            confirm = Confirm.ask(
                "\n确认创建模板?",
                default=True,
                console=self.ui_manager.console
            )
            
            if not confirm:
                self.ui_manager.print_warning("已取消创建")
                return None
            
            return {
                'name': name,
                'description': description,
                'category': category,
                'keywords': keywords,
                'script_content': script_content
            }
            
        except KeyboardInterrupt:
            self.ui_manager.print_warning("\n已取消创建")
            return None
        except Exception as e:
            self.ui_manager.print_error(f"向导执行失败: {str(e)}")
            return None
    
    def interactive_template_editor(
        self,
        template: Any
    ) -> Optional[Dict[str, Any]]:
        """
        交互式模板编辑界面
        
        Args:
            template: 要编辑的模板对象
            
        Returns:
            包含更新信息的字典，如果取消则返回 None
        """
        self.ui_manager.console.print(
            Panel.fit(
                f"[bold cyan]✏️  编辑模板: {template.name}[/bold cyan]\n"
                "[dim]选择要修改的字段[/dim]",
                border_style="cyan"
            )
        )
        
        # 显示当前值
        self.ui_manager.console.print("\n[bold]当前配置:[/bold]")
        current_info = {
            '名称': template.name,
            '描述': template.description,
            '分类': getattr(template, 'category', 'N/A'),
        }
        
        keywords = getattr(template, 'keywords', [])
        if keywords:
            current_info['关键词'] = ', '.join(keywords)
        
        tags = getattr(template, 'tags', [])
        if tags:
            current_info['标签'] = ', '.join(tags)
        
        self.ui_manager.print_dict(current_info, title=None)
        
        # 可编辑字段
        self.ui_manager.console.print("\n[bold]可编辑的字段:[/bold]")
        fields = [
            ("name", "📝 名称", template.name),
            ("description", "📄 描述", template.description),
            ("keywords", "🏷️  关键词", ', '.join(keywords) if keywords else "无"),
            ("tags", "🔖 标签", ', '.join(tags) if tags else "无"),
        ]
        
        for i, (field_id, field_name, current_value) in enumerate(fields, 1):
            self.ui_manager.console.print(
                f"  [{i}] {field_name} - [dim]当前: {current_value}[/dim]"
            )
        
        self.ui_manager.console.print("  [0] ✓ 完成编辑")
        
        updates = {}
        
        try:
            while True:
                choice = Prompt.ask(
                    "\n选择要编辑的字段",
                    choices=["0", "1", "2", "3", "4"],
                    default="0",
                    console=self.ui_manager.console
                )
                
                if choice == "0":
                    break
                
                field_id, field_name, current_value = fields[int(choice) - 1]
                
                if field_id in ["keywords", "tags"]:
                    new_value = Prompt.ask(
                        f"  新{field_name} (逗号分隔)",
                        default=current_value,
                        console=self.ui_manager.console
                    ).strip()
                    if new_value:
                        updates[field_id] = [v.strip() for v in new_value.split(',')]
                else:
                    new_value = Prompt.ask(
                        f"  新{field_name}",
                        default=current_value,
                        console=self.ui_manager.console
                    ).strip()
                    if new_value and new_value != current_value:
                        updates[field_id] = new_value
                
                self.ui_manager.print_success(f"{field_name} 已更新")
            
            if not updates:
                self.ui_manager.print_info("未进行任何修改")
                return None
            
            # 确认更新
            self.ui_manager.console.print("\n[bold]将要应用的更新:[/bold]")
            for key, value in updates.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                self.ui_manager.console.print(f"  • {key}: [cyan]{value}[/cyan]")
            
            confirm = Confirm.ask(
                "\n确认应用更新?",
                default=True,
                console=self.ui_manager.console
            )
            
            if not confirm:
                self.ui_manager.print_warning("已取消更新")
                return None
            
            return updates
            
        except KeyboardInterrupt:
            self.ui_manager.print_warning("\n已取消编辑")
            return None
    
    def confirm_template_deletion(
        self,
        template: Any
    ) -> bool:
        """
        模板删除确认对话框
        
        Args:
            template: 要删除的模板对象
            
        Returns:
            是否确认删除
        """
        self.ui_manager.console.print(
            Panel.fit(
                "[bold red]🗑️  删除模板[/bold red]\n"
                "[yellow]⚠️  警告: 此操作不可恢复![/yellow]",
                border_style="red"
            )
        )
        
        # 显示模板信息
        self.ui_manager.console.print("\n[bold]模板信息:[/bold]")
        template_info = {
            '名称': template.name,
            '描述': template.description,
            '分类': getattr(template, 'category', 'N/A'),
            '文件': getattr(template, 'file_path', 'N/A'),
        }
        
        self.ui_manager.print_dict(template_info, title=None)
        
        # 第一次确认
        first_confirm = Confirm.ask(
            "\n[yellow]确认要删除此模板吗?[/yellow]",
            default=False,
            console=self.ui_manager.console
        )
        
        if not first_confirm:
            return False
        
        # 第二次确认（输入模板名称）
        self.ui_manager.console.print(
            f"\n[yellow]请输入模板名称 '[cyan]{template.name}[/cyan]' 以确认删除:[/yellow]"
        )
        
        name_confirm = Prompt.ask(
            "  模板名称",
            console=self.ui_manager.console
        ).strip()
        
        return name_confirm == template.name
    
    def display_operation_summary(
        self,
        operation: str,
        template: Any,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        显示操作结果摘要
        
        Args:
            operation: 操作类型 (create, edit, delete, etc.)
            template: 模板对象
            success: 操作是否成功
            details: 额外的详细信息
        """
        # 操作图标映射
        operation_icons = {
            'create': '✨',
            'edit': '✏️',
            'delete': '🗑️',
            'export': '📤',
            'import': '📥',
            'move': '🔄',
        }
        
        icon = operation_icons.get(operation, '✓')
        
        if success:
            title = f"[bold green]{icon} 操作成功[/bold green]"
            border_style = "green"
        else:
            title = f"[bold red]✗ 操作失败[/bold red]"
            border_style = "red"
        
        # 构建摘要内容
        summary_lines = [title]
        summary_lines.append("")
        summary_lines.append(f"[bold]操作:[/bold] {operation}")
        summary_lines.append(f"[bold]模板:[/bold] {template.name if template else 'N/A'}")
        
        if details:
            summary_lines.append("")
            summary_lines.append("[bold]详细信息:[/bold]")
            for key, value in details.items():
                summary_lines.append(f"  • {key}: [cyan]{value}[/cyan]")
        
        self.ui_manager.console.print(
            Panel(
                "\n".join(summary_lines),
                border_style=border_style,
                padding=(1, 2)
            )
        )
    
    def display_template_detail_enhanced(
        self,
        template: Any
    ) -> None:
        """
        显示增强的模板详细信息
        
        Args:
            template: 模板对象
        """
        # 获取分类图标
        category = getattr(template, 'category', 'default')
        icon = self.CATEGORY_ICONS.get(category, self.CATEGORY_ICONS['default'])
        
        # 判断是否为自定义模板
        is_custom = isinstance(template, CustomTemplate) or getattr(template, 'is_custom', False)
        status_icon = self.STATUS_ICONS['custom'] if is_custom else self.STATUS_ICONS['system']
        
        # 标题
        title = f"{icon} {status_icon} {template.name}"
        self.ui_manager.console.print(
            Panel.fit(
                f"[bold cyan]{title}[/bold cyan]\n"
                f"[dim]{template.description}[/dim]",
                border_style="cyan"
            )
        )
        
        # 基本信息
        basic_info = {
            '分类': f"{icon} {category}",
            '类型': '自定义模板' if is_custom else '系统模板',
        }
        
        keywords = getattr(template, 'keywords', [])
        if keywords:
            basic_info['关键词'] = ', '.join(keywords)
        
        tags = getattr(template, 'tags', [])
        if tags:
            basic_info['标签'] = ', '.join(tags)
        
        if hasattr(template, 'author'):
            basic_info['作者'] = template.author
        
        if hasattr(template, 'version'):
            basic_info['版本'] = template.version
        
        if hasattr(template, 'file_path'):
            basic_info['文件路径'] = template.file_path
        
        self.ui_manager.print_dict(basic_info, "📋 基本信息")
        
        # 参数信息
        parameters = getattr(template, 'parameters', {})
        if parameters:
            self.ui_manager.console.print("\n[bold primary]⚙️  参数列表[/bold primary]")
            
            param_data = []
            for name, param in parameters.items():
                param_data.append({
                    'name': name,
                    'type': getattr(param, 'type', 'string'),
                    'required': '✓' if getattr(param, 'required', False) else '✗',
                    'default': str(getattr(param, 'default', '-')) if getattr(param, 'default', None) else '-',
                    'description': getattr(param, 'description', ''),
                })
            
            columns = [
                ColumnConfig(name='name', header='参数名', width=15, style='bold cyan'),
                ColumnConfig(name='type', header='类型', width=10, style='magenta'),
                ColumnConfig(name='required', header='必需', width=6, justify='center'),
                ColumnConfig(name='default', header='默认值', width=15, style='yellow'),
                ColumnConfig(name='description', header='说明', width=30),
            ]
            
            config = TableConfig(show_lines=False, box_style='simple')
            self.table_manager.display_table(param_data, columns, config)
        
        # 示例
        examples = getattr(template, 'examples', [])
        if examples:
            self.ui_manager.console.print("\n[bold primary]💡 使用示例[/bold primary]")
            for i, example in enumerate(examples, 1):
                self.ui_manager.console.print(f"  {i}. [cyan]{example}[/cyan]")
    
    def show_progress_for_operation(
        self,
        operation: str,
        steps: List[str]
    ) -> Any:
        """
        为模板操作显示进度指示
        
        Args:
            operation: 操作名称
            steps: 操作步骤列表
            
        Returns:
            进度上下文管理器
        """
        # 使用进度上下文管理器
        return self.progress_manager.progress_context(
            task_id=f"operation_{operation}",
            description=f"正在{operation}...",
            total=len(steps)
        )
