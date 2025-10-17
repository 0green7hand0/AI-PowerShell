"""
模板显示测试
"""

import pytest
import sys
from pathlib import Path
from io import StringIO
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui import UIManager, TemplateDisplay
from src.ui.models import UIConfig


class MockTemplate:
    """模拟模板对象"""
    
    def __init__(self, name, category, description, keywords=None, parameters=None):
        self.name = name
        self.category = category
        self.description = description
        self.keywords = keywords or []
        self.parameters = parameters or {}


class MockParameter:
    """模拟参数对象"""
    
    def __init__(self, type='string', required=False, default=None, description=''):
        self.type = type
        self.required = required
        self.default = default
        self.description = description


class MockVersion:
    """模拟版本对象"""
    
    def __init__(self, version, timestamp, description='', size=1024):
        self.version = version
        self.timestamp = timestamp
        self.description = description
        self.size = size


class TestTemplateDisplay:
    """测试模板显示"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def template_display(self, ui_manager):
        """创建模板显示实例"""
        return TemplateDisplay(ui_manager)
    
    @pytest.fixture
    def sample_templates(self):
        """创建示例模板"""
        return [
            MockTemplate(
                'template_a',
                'automation',
                'Template A description',
                keywords=['test', 'automation'],
                parameters={'param1': MockParameter()}
            ),
            MockTemplate(
                'template_b',
                'file_management',
                'Template B description',
                keywords=['file', 'management'],
                parameters={'param1': MockParameter(), 'param2': MockParameter()}
            ),
            MockTemplate(
                'template_c',
                'automation',
                'Template C description with a very long description that should be truncated',
                keywords=['test', 'auto', 'long'],
                parameters={}
            ),
        ]
    
    def test_template_display_initialization(self, template_display):
        """测试模板显示初始化"""
        assert template_display is not None
        assert template_display.ui_manager is not None
        assert template_display.table_manager is not None
    
    def test_display_template_list(self, template_display, sample_templates):
        """测试显示模板列表"""
        # 不应该抛出异常
        template_display.display_template_list(sample_templates)
    
    def test_display_template_list_grouped(self, template_display, sample_templates):
        """测试分组显示模板列表"""
        template_display.display_template_list(
            sample_templates,
            group_by_category=True
        )
    
    def test_display_template_list_sorted(self, template_display, sample_templates):
        """测试排序显示模板列表"""
        template_display.display_template_list(
            sample_templates,
            sort_by='name',
            group_by_category=False
        )
    
    def test_display_empty_template_list(self, template_display):
        """测试显示空模板列表"""
        template_display.display_template_list([])
    
    def test_display_template_detail(self, template_display, sample_templates):
        """测试显示模板详情"""
        template = sample_templates[0]
        template_display.display_template_detail(template)
    
    def test_display_template_detail_with_examples(self, template_display):
        """测试显示带示例的模板详情"""
        template = MockTemplate(
            'test_template',
            'test',
            'Test description',
            keywords=['test'],
            parameters={'param1': MockParameter(description='Test param')}
        )
        template.examples = ['Example 1', 'Example 2']
        
        template_display.display_template_detail(template)
    
    def test_display_command_history(self, template_display):
        """测试显示命令历史"""
        history = [
            'command 1',
            'command 2',
            'command 3 with a very long text that should be truncated in the display',
        ]
        
        template_display.display_command_history(history)
    
    def test_display_empty_command_history(self, template_display):
        """测试显示空命令历史"""
        template_display.display_command_history([])
    
    def test_display_command_history_limit(self, template_display):
        """测试命令历史显示限制"""
        history = [f'command {i}' for i in range(50)]
        
        # 应该只显示最近的 20 条
        template_display.display_command_history(history, max_items=20)
    
    def test_display_config_info(self, template_display):
        """测试显示配置信息"""
        config = {
            'ai_provider': 'openai',
            'ai_model': 'gpt-4',
            'ui_theme': 'dark',
            'ui_colors': True,
            'template_dir': '/path/to/templates',
            'other_setting': 'value',
        }
        
        template_display.display_config_info(config)
    
    def test_display_version_history(self, template_display):
        """测试显示版本历史"""
        versions = [
            MockVersion('1.0', datetime.now(), 'Initial version', 1024),
            MockVersion('1.1', datetime.now(), 'Bug fixes', 2048),
            MockVersion('2.0', datetime.now(), 'Major update', 3072),
        ]
        
        template_display.display_version_history(versions, 'test_template')
    
    def test_display_empty_version_history(self, template_display):
        """测试显示空版本历史"""
        template_display.display_version_history([], 'test_template')
    
    def test_format_config_value_boolean(self, template_display):
        """测试格式化布尔配置值"""
        assert '✓' in template_display._format_config_value(True)
        assert '✗' in template_display._format_config_value(False)
    
    def test_format_config_value_list(self, template_display):
        """测试格式化列表配置值"""
        result = template_display._format_config_value(['a', 'b', 'c'])
        assert 'a, b, c' == result
    
    def test_format_config_value_dict(self, template_display):
        """测试格式化字典配置值"""
        result = template_display._format_config_value({'a': 1, 'b': 2})
        assert '2 项配置' in result
    
    def test_format_config_value_none(self, template_display):
        """测试格式化 None 配置值"""
        result = template_display._format_config_value(None)
        assert result == '-'
    
    def test_group_config(self, template_display):
        """测试配置分组"""
        config = {
            'ai_provider': 'openai',
            'ui_theme': 'dark',
            'template_dir': '/path',
            'other': 'value',
        }
        
        grouped = template_display._group_config(config)
        
        assert 'AI 配置' in grouped
        assert 'UI 配置' in grouped
        assert 'ai_provider' in grouped['AI 配置']
        assert 'ui_theme' in grouped['UI 配置']
    
    def test_long_description_truncation(self, template_display, sample_templates):
        """测试长描述截断"""
        # template_c 有很长的描述，应该被截断
        template_display.display_template_list(sample_templates)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
