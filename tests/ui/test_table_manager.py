"""
表格管理器测试
"""

import pytest
import sys
from pathlib import Path
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui import TableManager, ColumnConfig, TableConfig, SortOrder
from rich.console import Console


class TestTableManager:
    """测试表格管理器"""
    
    @pytest.fixture
    def console(self):
        """创建 Console 实例"""
        return Console(file=StringIO(), force_terminal=True)
    
    @pytest.fixture
    def table_manager(self, console):
        """创建表格管理器实例"""
        return TableManager(console, page_size=5)
    
    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        return [
            {'name': 'Template A', 'category': 'automation', 'params': 3, 'active': True},
            {'name': 'Template B', 'category': 'file_management', 'params': 2, 'active': False},
            {'name': 'Template C', 'category': 'automation', 'params': 5, 'active': True},
            {'name': 'Template D', 'category': 'monitoring', 'params': 1, 'active': True},
        ]
    
    @pytest.fixture
    def sample_columns(self):
        """创建示例列配置"""
        return [
            ColumnConfig(name='name', header='Name', width=20),
            ColumnConfig(name='category', header='Category', width=15),
            ColumnConfig(name='params', header='Params', width=8, justify='center'),
            ColumnConfig(name='active', header='Active', width=8, justify='center'),
        ]
    
    def test_table_manager_initialization(self, table_manager):
        """测试表格管理器初始化"""
        assert table_manager is not None
        assert table_manager.console is not None
        assert table_manager.page_size == 5
    
    def test_create_table(self, table_manager, sample_columns):
        """测试创建表格"""
        config = TableConfig(title="Test Table", show_header=True)
        table = table_manager.create_table(sample_columns, config)
        
        assert table is not None
        assert table.title == "Test Table"
        assert len(table.columns) == 4
    
    def test_add_rows(self, table_manager, sample_data, sample_columns):
        """测试添加行"""
        table = table_manager.create_table(sample_columns)
        table_manager.add_rows(table, sample_data, sample_columns)
        
        assert len(table.rows) == 4
    
    def test_sort_data_ascending(self, table_manager, sample_data):
        """测试升序排序"""
        sorted_data = table_manager.sort_data(sample_data, 'name', SortOrder.ASC)
        
        assert len(sorted_data) == 4
        assert sorted_data[0]['name'] == 'Template A'
        assert sorted_data[-1]['name'] == 'Template D'
    
    def test_sort_data_descending(self, table_manager, sample_data):
        """测试降序排序"""
        sorted_data = table_manager.sort_data(sample_data, 'params', SortOrder.DESC)
        
        assert len(sorted_data) == 4
        assert sorted_data[0]['params'] == 5
        assert sorted_data[-1]['params'] == 1
    
    def test_filter_data_string(self, table_manager, sample_data):
        """测试字符串筛选"""
        filtered = table_manager.filter_data(sample_data, {'category': 'automation'})
        
        assert len(filtered) == 2
        assert all(item['category'] == 'automation' for item in filtered)
    
    def test_filter_data_boolean(self, table_manager, sample_data):
        """测试布尔值筛选"""
        filtered = table_manager.filter_data(sample_data, {'active': True})
        
        assert len(filtered) == 3
        assert all(item['active'] is True for item in filtered)
    
    def test_filter_data_multiple(self, table_manager, sample_data):
        """测试多条件筛选"""
        filtered = table_manager.filter_data(
            sample_data,
            {'category': 'automation', 'active': True}
        )
        
        assert len(filtered) == 2
        assert all(
            item['category'] == 'automation' and item['active'] is True
            for item in filtered
        )
    
    def test_display_list(self, table_manager):
        """测试显示列表"""
        items = ['Item 1', 'Item 2', 'Item 3']
        
        # 不应该抛出异常
        table_manager.display_list(items, title="Test List")
        table_manager.display_list(items, numbered=True)
    
    def test_calculate_responsive_width(self, table_manager, sample_data):
        """测试计算响应式列宽"""
        width = table_manager.calculate_responsive_width(sample_data, 'name')
        
        # 最长的名称是 "Template X" (10 个字符) + 2 = 12
        assert width == 12
    
    def test_calculate_responsive_width_limits(self, table_manager):
        """测试列宽限制"""
        data = [{'text': 'a' * 100}]
        
        # 应该限制在最大宽度
        width = table_manager.calculate_responsive_width(data, 'text', max_width=50)
        assert width == 50
        
        # 应该限制在最小宽度
        data = [{'text': 'ab'}]
        width = table_manager.calculate_responsive_width(data, 'text', min_width=10)
        assert width == 10
    
    def test_display_table(self, table_manager, sample_data, sample_columns):
        """测试显示表格"""
        config = TableConfig(title="Test Display")
        
        # 不应该抛出异常
        table_manager.display_table(sample_data, sample_columns, config)
    
    def test_display_grouped_data(self, table_manager, sample_data, sample_columns):
        """测试显示分组数据"""
        grouped = {
            'Group 1': sample_data[:2],
            'Group 2': sample_data[2:],
        }
        
        # 不应该抛出异常
        table_manager.display_grouped_data(grouped, sample_columns)
    
    def test_row_style_function(self, table_manager, sample_data, sample_columns):
        """测试行样式函数"""
        def style_func(row):
            return "bold" if row['active'] else "dim"
        
        table = table_manager.create_table(sample_columns)
        table_manager.add_rows(table, sample_data, sample_columns, row_style=style_func)
        
        assert len(table.rows) == 4
    
    def test_empty_data(self, table_manager, sample_columns):
        """测试空数据"""
        table = table_manager.create_table(sample_columns)
        table_manager.add_rows(table, [], sample_columns)
        
        assert len(table.rows) == 0
    
    def test_boolean_display(self, table_manager, sample_columns):
        """测试布尔值显示"""
        data = [{'name': 'Test', 'category': 'test', 'params': 1, 'active': True}]
        
        table = table_manager.create_table(sample_columns)
        table_manager.add_rows(table, data, sample_columns)
        
        # 布尔值应该转换为 ✓ 或 ✗
        assert len(table.rows) == 1


class TestColumnConfig:
    """测试列配置"""
    
    def test_column_config_creation(self):
        """测试创建列配置"""
        col = ColumnConfig(
            name='test',
            header='Test Header',
            width=20,
            justify='center',
            style='bold'
        )
        
        assert col.name == 'test'
        assert col.header == 'Test Header'
        assert col.width == 20
        assert col.justify == 'center'
        assert col.style == 'bold'
        assert col.sortable is True
    
    def test_column_config_defaults(self):
        """测试列配置默认值"""
        col = ColumnConfig(name='test', header='Test')
        
        assert col.width is None
        assert col.justify == 'left'
        assert col.style is None
        assert col.no_wrap is False
        assert col.sortable is True


class TestTableConfig:
    """测试表格配置"""
    
    def test_table_config_creation(self):
        """测试创建表格配置"""
        config = TableConfig(
            title='Test Table',
            show_header=True,
            show_lines=True,
            box_style='rounded'
        )
        
        assert config.title == 'Test Table'
        assert config.show_header is True
        assert config.show_lines is True
        assert config.box_style == 'rounded'
    
    def test_table_config_defaults(self):
        """测试表格配置默认值"""
        config = TableConfig()
        
        assert config.title is None
        assert config.show_header is True
        assert config.show_lines is False
        assert config.show_edge is True
        assert config.box_style == 'rounded'
        assert config.expand is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
