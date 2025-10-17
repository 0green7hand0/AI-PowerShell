"""
模板显示优化模块

使用表格和列表组件优化模板相关信息的显示。
"""

from typing import List, Dict, Any, Optional
from .table_manager import TableManager, ColumnConfig, TableConfig, SortOrder
from .ui_manager import UIManager


class TemplateDisplay:
    """模板显示管理器"""
    
    def __init__(self, ui_manager: UIManager):
        """
        初始化模板显示管理器
        
        Args:
            ui_manager: UI 管理器实例
        """
        self.ui_manager = ui_manager
        self.table_manager = TableManager(ui_manager.console)
    
    def display_template_list(
        self,
        templates: List[Any],
        title: str = "模板列表",
        group_by_category: bool = True,
        paginate: bool = False,
        sort_by: Optional[str] = None
    ) -> None:
        """
        显示模板列表
        
        Args:
            templates: 模板列表
            title: 标题
            group_by_category: 是否按分类分组
            paginate: 是否分页
            sort_by: 排序字段
        """
        if not templates:
            self.ui_manager.print_info("暂无模板")
            self.ui_manager.print_info(
                "💡 提示: 使用 'template create' 命令创建新模板",
                icon=False
            )
            return
        
        # 转换模板对象为字典
        template_data = []
        for template in templates:
            data = {
                'name': template.name,
                'category': template.category if hasattr(template, 'category') else 'N/A',
                'description': template.description[:50] + '...' if len(template.description) > 50 else template.description,
                'keywords': ', '.join(template.keywords[:3]) if hasattr(template, 'keywords') and template.keywords else '',
                'params': len(template.parameters) if hasattr(template, 'parameters') and template.parameters else 0,
            }
            template_data.append(data)
        
        # 排序
        if sort_by:
            template_data = self.table_manager.sort_data(template_data, sort_by)
        
        # 定义列
        columns = [
            ColumnConfig(name='name', header='模板名称', width=20, style='bold cyan'),
            ColumnConfig(name='category', header='分类', width=15, style='magenta'),
            ColumnConfig(name='description', header='描述', width=40),
            ColumnConfig(name='keywords', header='关键词', width=25, style='dim'),
            ColumnConfig(name='params', header='参数数', width=8, justify='center'),
        ]
        
        # 显示标题
        self.ui_manager.print_header(title, f"共 {len(templates)} 个模板")
        
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
            self.table_manager.display_table(
                template_data,
                columns,
                config,
                paginate=paginate
            )
    
    def display_template_detail(self, template: Any) -> None:
        """
        显示模板详细信息
        
        Args:
            template: 模板对象
        """
        self.ui_manager.print_header(f"模板详情: {template.name}")
        
        # 基本信息
        basic_info = {
            '名称': template.name,
            '描述': template.description,
            '分类': template.category if hasattr(template, 'category') else 'N/A',
        }
        
        if hasattr(template, 'keywords') and template.keywords:
            basic_info['关键词'] = ', '.join(template.keywords)
        
        self.ui_manager.print_dict(basic_info, "基本信息")
        
        # 参数信息
        if hasattr(template, 'parameters') and template.parameters:
            self.ui_manager.console.print("\n[bold primary]参数列表[/bold primary]")
            
            param_data = []
            for name, param in template.parameters.items():
                param_data.append({
                    'name': name,
                    'type': param.type if hasattr(param, 'type') else 'string',
                    'required': '是' if (hasattr(param, 'required') and param.required) else '否',
                    'default': str(param.default) if hasattr(param, 'default') and param.default else '-',
                    'description': param.description if hasattr(param, 'description') else '',
                })
            
            columns = [
                ColumnConfig(name='name', header='参数名', width=15, style='bold'),
                ColumnConfig(name='type', header='类型', width=10),
                ColumnConfig(name='required', header='必需', width=6, justify='center'),
                ColumnConfig(name='default', header='默认值', width=15),
                ColumnConfig(name='description', header='说明', width=30),
            ]
            
            config = TableConfig(show_lines=False, box_style='simple')
            self.table_manager.display_table(param_data, columns, config)
        
        # 示例
        if hasattr(template, 'examples') and template.examples:
            self.table_manager.display_list(
                template.examples,
                title="使用示例",
                numbered=True
            )
    
    def display_command_history(
        self,
        history: List[str],
        max_items: int = 20
    ) -> None:
        """
        显示命令历史
        
        Args:
            history: 历史命令列表
            max_items: 最多显示的条目数
        """
        if not history:
            self.ui_manager.print_info("暂无命令历史")
            return
        
        # 限制显示数量
        display_history = history[-max_items:] if len(history) > max_items else history
        
        self.ui_manager.print_header("命令历史", f"最近 {len(display_history)} 条")
        
        # 转换为表格数据
        history_data = []
        for i, cmd in enumerate(reversed(display_history), 1):
            history_data.append({
                'index': str(i),
                'command': cmd[:80] + '...' if len(cmd) > 80 else cmd,
            })
        
        columns = [
            ColumnConfig(name='index', header='#', width=5, justify='right', style='dim'),
            ColumnConfig(name='command', header='命令', width=100, style='cyan'),
        ]
        
        config = TableConfig(show_lines=False, box_style='minimal')
        self.table_manager.display_table(history_data, columns, config)
    
    def display_config_info(
        self,
        config: Dict[str, Any],
        title: str = "配置信息"
    ) -> None:
        """
        显示配置信息（分组显示）
        
        Args:
            config: 配置字典
            title: 标题
        """
        self.ui_manager.print_header(title)
        
        # 按配置类型分组
        grouped_config = self._group_config(config)
        
        for group_name, group_items in grouped_config.items():
            self.ui_manager.console.print(f"\n[bold secondary]{group_name}[/bold secondary]")
            
            config_data = []
            for key, value in group_items.items():
                config_data.append({
                    'key': key,
                    'value': self._format_config_value(value),
                })
            
            columns = [
                ColumnConfig(name='key', header='配置项', width=30, style='cyan'),
                ColumnConfig(name='value', header='值', width=50),
            ]
            
            config_table = TableConfig(show_lines=False, box_style='simple')
            self.table_manager.display_table(config_data, columns, config_table)
    
    def _group_config(self, config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        将配置按类型分组
        
        Args:
            config: 配置字典
            
        Returns:
            Dict[str, Dict[str, Any]]: 分组后的配置
        """
        groups = {
            'AI 配置': {},
            'UI 配置': {},
            '模板配置': {},
            '其他配置': {},
        }
        
        for key, value in config.items():
            key_lower = key.lower()
            if 'ai' in key_lower or 'model' in key_lower or 'provider' in key_lower:
                groups['AI 配置'][key] = value
            elif 'ui' in key_lower or 'theme' in key_lower or 'color' in key_lower:
                groups['UI 配置'][key] = value
            elif 'template' in key_lower:
                groups['模板配置'][key] = value
            else:
                groups['其他配置'][key] = value
        
        # 移除空组
        return {k: v for k, v in groups.items() if v}
    
    def _format_config_value(self, value: Any) -> str:
        """
        格式化配置值
        
        Args:
            value: 配置值
            
        Returns:
            str: 格式化后的字符串
        """
        if isinstance(value, bool):
            return '✓ 启用' if value else '✗ 禁用'
        elif isinstance(value, (list, tuple)):
            return ', '.join(str(v) for v in value)
        elif isinstance(value, dict):
            return f'{len(value)} 项配置'
        elif value is None:
            return '-'
        else:
            return str(value)
    
    def display_version_history(
        self,
        versions: List[Any],
        template_name: str
    ) -> None:
        """
        显示模板版本历史
        
        Args:
            versions: 版本列表
            template_name: 模板名称
        """
        if not versions:
            self.ui_manager.print_info(f"模板 '{template_name}' 暂无历史版本")
            return
        
        self.ui_manager.print_header(
            f"版本历史: {template_name}",
            f"共 {len(versions)} 个版本"
        )
        
        # 转换为表格数据
        version_data = []
        for version in versions:
            version_data.append({
                'version': version.version if hasattr(version, 'version') else 'N/A',
                'timestamp': version.timestamp if hasattr(version, 'timestamp') else 'N/A',
                'description': version.description if hasattr(version, 'description') else '',
                'size': f"{version.size} bytes" if hasattr(version, 'size') else 'N/A',
            })
        
        columns = [
            ColumnConfig(name='version', header='版本', width=10, style='bold cyan'),
            ColumnConfig(name='timestamp', header='时间', width=20, style='magenta'),
            ColumnConfig(name='description', header='说明', width=40),
            ColumnConfig(name='size', header='大小', width=15, justify='right', style='dim'),
        ]
        
        config = TableConfig(show_lines=False, box_style='rounded')
        self.table_manager.display_table(version_data, columns, config)
