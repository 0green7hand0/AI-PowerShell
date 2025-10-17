"""
表格和列表管理器

提供格式化的表格和列表显示功能，支持排序、筛选和分页。
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from rich.table import Table
from rich.console import Console
from rich.box import ROUNDED, MINIMAL, SIMPLE
from enum import Enum


class SortOrder(str, Enum):
    """排序顺序"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class ColumnConfig:
    """列配置"""
    name: str
    header: str
    width: Optional[int] = None
    justify: str = "left"
    style: Optional[str] = None
    no_wrap: bool = False
    sortable: bool = True


@dataclass
class TableConfig:
    """表格配置"""
    title: Optional[str] = None
    show_header: bool = True
    show_lines: bool = False
    show_edge: bool = True
    box_style: str = "rounded"
    expand: bool = False
    min_width: Optional[int] = None
    max_width: Optional[int] = None


class TableManager:
    """表格和列表管理器"""
    
    BOX_STYLES = {
        "rounded": ROUNDED,
        "minimal": MINIMAL,
        "simple": SIMPLE,
    }
    
    def __init__(self, console: Console, page_size: int = 20):
        """
        初始化表格管理器
        
        Args:
            console: Rich Console 实例
            page_size: 分页大小
        """
        self.console = console
        self.page_size = page_size
    
    def create_table(
        self,
        columns: List[ColumnConfig],
        config: Optional[TableConfig] = None
    ) -> Table:
        """
        创建表格
        
        Args:
            columns: 列配置列表
            config: 表格配置
            
        Returns:
            Table: Rich 表格对象
        """
        config = config or TableConfig()
        
        table = Table(
            title=config.title,
            show_header=config.show_header,
            show_lines=config.show_lines,
            show_edge=config.show_edge,
            box=self.BOX_STYLES.get(config.box_style, ROUNDED),
            expand=config.expand,
            min_width=config.min_width,
            title_style="bold cyan",
            header_style="bold magenta",
        )
        
        # 添加列
        for col in columns:
            table.add_column(
                col.header,
                justify=col.justify,
                style=col.style,
                no_wrap=col.no_wrap,
                width=col.width,
            )
        
        return table
    
    def add_rows(
        self,
        table: Table,
        data: List[Dict[str, Any]],
        columns: List[ColumnConfig],
        row_style: Optional[Callable[[Dict[str, Any]], str]] = None
    ) -> None:
        """
        向表格添加行
        
        Args:
            table: 表格对象
            data: 数据列表
            columns: 列配置
            row_style: 行样式函数，接收行数据返回样式字符串
        """
        for row_data in data:
            row_values = []
            for col in columns:
                value = row_data.get(col.name, "")
                # 转换为字符串
                if value is None:
                    value = ""
                elif isinstance(value, bool):
                    value = "✓" if value else "✗"
                else:
                    value = str(value)
                row_values.append(value)
            
            # 应用行样式
            style = row_style(row_data) if row_style else None
            table.add_row(*row_values, style=style)
    
    def display_table(
        self,
        data: List[Dict[str, Any]],
        columns: List[ColumnConfig],
        config: Optional[TableConfig] = None,
        row_style: Optional[Callable[[Dict[str, Any]], str]] = None,
        paginate: bool = False
    ) -> None:
        """
        显示表格
        
        Args:
            data: 数据列表
            columns: 列配置
            config: 表格配置
            row_style: 行样式函数
            paginate: 是否分页
        """
        if paginate and len(data) > self.page_size:
            self._display_paginated_table(data, columns, config, row_style)
        else:
            table = self.create_table(columns, config)
            self.add_rows(table, data, columns, row_style)
            self.console.print(table)
    
    def _display_paginated_table(
        self,
        data: List[Dict[str, Any]],
        columns: List[ColumnConfig],
        config: Optional[TableConfig],
        row_style: Optional[Callable[[Dict[str, Any]], str]]
    ) -> None:
        """
        分页显示表格
        
        Args:
            data: 数据列表
            columns: 列配置
            config: 表格配置
            row_style: 行样式函数
        """
        total_pages = (len(data) + self.page_size - 1) // self.page_size
        current_page = 1
        
        while current_page <= total_pages:
            start_idx = (current_page - 1) * self.page_size
            end_idx = min(start_idx + self.page_size, len(data))
            page_data = data[start_idx:end_idx]
            
            # 更新标题显示页码
            page_config = config or TableConfig()
            original_title = page_config.title or ""
            page_config.title = f"{original_title} (Page {current_page}/{total_pages})"
            
            table = self.create_table(columns, page_config)
            self.add_rows(table, page_data, columns, row_style)
            self.console.print(table)
            
            # 显示分页提示
            if current_page < total_pages:
                self.console.print(
                    f"\n[muted]Showing {start_idx + 1}-{end_idx} of {len(data)} items. "
                    f"Press Enter for next page, 'q' to quit...[/muted]"
                )
                user_input = input().strip().lower()
                if user_input == 'q':
                    break
                current_page += 1
            else:
                self.console.print(
                    f"\n[muted]Showing {start_idx + 1}-{end_idx} of {len(data)} items.[/muted]"
                )
                break
    
    def sort_data(
        self,
        data: List[Dict[str, Any]],
        sort_by: str,
        order: SortOrder = SortOrder.ASC
    ) -> List[Dict[str, Any]]:
        """
        排序数据
        
        Args:
            data: 数据列表
            sort_by: 排序字段
            order: 排序顺序
            
        Returns:
            List[Dict[str, Any]]: 排序后的数据
        """
        reverse = (order == SortOrder.DESC)
        
        try:
            return sorted(
                data,
                key=lambda x: x.get(sort_by, ""),
                reverse=reverse
            )
        except TypeError:
            # 如果比较失败，转换为字符串再排序
            return sorted(
                data,
                key=lambda x: str(x.get(sort_by, "")),
                reverse=reverse
            )
    
    def filter_data(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        筛选数据
        
        Args:
            data: 数据列表
            filters: 筛选条件字典
            
        Returns:
            List[Dict[str, Any]]: 筛选后的数据
        """
        filtered_data = data
        
        for key, value in filters.items():
            if value is None:
                continue
            
            if isinstance(value, str):
                # 字符串模糊匹配
                filtered_data = [
                    item for item in filtered_data
                    if value.lower() in str(item.get(key, "")).lower()
                ]
            else:
                # 精确匹配
                filtered_data = [
                    item for item in filtered_data
                    if item.get(key) == value
                ]
        
        return filtered_data
    
    def display_list(
        self,
        items: List[str],
        title: Optional[str] = None,
        numbered: bool = False,
        bullet: str = "•",
        style: Optional[str] = None
    ) -> None:
        """
        显示列表
        
        Args:
            items: 列表项
            title: 标题
            numbered: 是否编号
            bullet: 项目符号
            style: 样式
        """
        if title:
            self.console.print(f"\n[bold primary]{title}[/bold primary]")
        
        for i, item in enumerate(items, 1):
            if numbered:
                prefix = f"{i}."
            else:
                prefix = bullet
            
            item_style = style or ""
            self.console.print(f"  {prefix} {item}", style=item_style)
    
    def display_dict_list(
        self,
        items: List[Dict[str, Any]],
        title: Optional[str] = None,
        key_style: str = "secondary",
        value_style: str = ""
    ) -> None:
        """
        显示字典列表（键值对格式）
        
        Args:
            items: 字典列表
            title: 标题
            key_style: 键的样式
            value_style: 值的样式
        """
        if title:
            self.console.print(f"\n[bold primary]{title}[/bold primary]")
        
        for item in items:
            self.console.print()
            for key, value in item.items():
                self.console.print(
                    f"  [{key_style}]{key}:[/{key_style}] "
                    f"[{value_style}]{value}[/{value_style}]"
                )
    
    def display_grouped_data(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        columns: List[ColumnConfig],
        config: Optional[TableConfig] = None
    ) -> None:
        """
        显示分组数据
        
        Args:
            data: 分组数据字典，键为组名，值为该组的数据列表
            columns: 列配置
            config: 表格配置
        """
        for group_name, group_data in data.items():
            # 显示组标题
            self.console.print(f"\n[bold primary]{group_name}[/bold primary]")
            
            if not group_data:
                self.console.print("  [muted]No items[/muted]")
                continue
            
            # 显示该组的表格
            group_config = config or TableConfig()
            group_config.title = None  # 组名已经单独显示
            
            table = self.create_table(columns, group_config)
            self.add_rows(table, group_data, columns)
            self.console.print(table)
    
    def calculate_responsive_width(
        self,
        data: List[Dict[str, Any]],
        column_name: str,
        min_width: int = 10,
        max_width: int = 50
    ) -> int:
        """
        计算响应式列宽
        
        Args:
            data: 数据列表
            column_name: 列名
            min_width: 最小宽度
            max_width: 最大宽度
            
        Returns:
            int: 计算出的列宽
        """
        if not data:
            return min_width
        
        # 计算该列所有值的最大长度
        max_length = max(
            len(str(item.get(column_name, "")))
            for item in data
        )
        
        # 限制在最小和最大宽度之间
        return max(min_width, min(max_length + 2, max_width))
