"""
模板管理界面测试
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.template_manager_ui import TemplateManagerUI
from src.ui import UIManager
from src.ui.models import UIConfig
from src.template_engine.custom_models import CustomTemplate
from src.template_engine.models import TemplateParameter


class MockTemplate:
    """模拟模板对象"""
    
    def __init__(self, name, category, description, keywords=None, parameters=None, is_custom=False):
        self.id = name.lower().replace(' ', '_')
        self.name = name
        self.category = category
        self.description = description
        self.keywords = keywords or []
        self.parameters = parameters or {}
        self.is_custom = is_custom
        self.file_path = f'/path/to/{self.id}.ps1'
        self.tags = []
        self.author = 'test_user'
        self.version = '1.0.0'


class TestTemplateManagerUI:
    """测试模板管理界面"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def template_ui(self, ui_manager):
        """创建模板管理界面实例"""
        return TemplateManagerUI(ui_manager)
    
    @pytest.fixture
    def sample_templates(self):
        """创建示例模板"""
        return [
            MockTemplate(
                'Automation Template',
                'automation',
                'Template for automation tasks',
                keywords=['auto', 'task'],
                parameters={'param1': Mock(type='string', required=True, default=None, description='Test param')},
                is_custom=False
            ),
            MockTemplate(
                'Custom File Manager',
                'file_management',
                'Custom file management template',
                keywords=['file', 'custom'],
                parameters={},
                is_custom=True
            ),
            MockTemplate(
                'System Monitor',
                'system_monitoring',
                'Monitor system resources',
                keywords=['monitor', 'system'],
                parameters={'interval': Mock(type='int', required=False, default=60, description='Check interval')},
                is_custom=False
            ),
        ]
    
    def test_template_manager_ui_initialization(self, template_ui):
        """测试模板管理界面初始化"""
        assert template_ui is not None
        assert template_ui.ui_manager is not None
        assert template_ui.table_manager is not None
        assert template_ui.progress_manager is not None
    
    def test_category_icons_mapping(self, template_ui):
        """测试分类图标映射"""
        assert 'automation' in template_ui.CATEGORY_ICONS
        assert 'file_management' in template_ui.CATEGORY_ICONS
        assert 'system_monitoring' in template_ui.CATEGORY_ICONS
        assert 'custom' in template_ui.CATEGORY_ICONS
        assert 'default' in template_ui.CATEGORY_ICONS
    
    def test_status_icons_mapping(self, template_ui):
        """测试状态图标映射"""
        assert 'active' in template_ui.STATUS_ICONS
        assert 'inactive' in template_ui.STATUS_ICONS
        assert 'custom' in template_ui.STATUS_ICONS
        assert 'system' in template_ui.STATUS_ICONS
    
    def test_display_template_list_enhanced(self, template_ui, sample_templates):
        """测试显示增强的模板列表"""
        # 不应该抛出异常
        template_ui.display_template_list_enhanced(sample_templates)
    
    def test_display_template_list_with_icons(self, template_ui, sample_templates):
        """测试显示带图标的模板列表"""
        template_ui.display_template_list_enhanced(
            sample_templates,
            show_icons=True
        )
    
    def test_display_template_list_without_icons(self, template_ui, sample_templates):
        """测试显示不带图标的模板列表"""
        template_ui.display_template_list_enhanced(
            sample_templates,
            show_icons=False
        )
    
    def test_display_template_list_grouped(self, template_ui, sample_templates):
        """测试分组显示模板列表"""
        template_ui.display_template_list_enhanced(
            sample_templates,
            group_by_category=True
        )
    
    def test_display_template_list_ungrouped(self, template_ui, sample_templates):
        """测试不分组显示模板列表"""
        template_ui.display_template_list_enhanced(
            sample_templates,
            group_by_category=False
        )
    
    def test_display_empty_template_list(self, template_ui):
        """测试显示空模板列表"""
        template_ui.display_template_list_enhanced([])
    
    def test_display_legend(self, template_ui):
        """测试显示图例"""
        # 不应该抛出异常
        template_ui._display_legend()
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_interactive_template_wizard_success(self, mock_confirm, mock_prompt, template_ui):
        """测试交互式模板创建向导 - 成功场景"""
        # 模拟用户输入
        mock_prompt.side_effect = [
            'Test Template',  # 名称
            'Test description',  # 描述
            '1',  # 分类选择
            'test, wizard',  # 关键词
            '1',  # 脚本来源选择
            '/path/to/script.ps1',  # 文件路径
        ]
        mock_confirm.return_value = True  # 确认创建
        
        # 模拟文件存在和读取
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = 'Write-Host "Test"'
                
                result = template_ui.interactive_template_wizard()
        
        assert result is not None
        assert result['name'] == 'Test Template'
        assert result['description'] == 'Test description'
        assert result['category'] == 'automation'
        assert 'test' in result['keywords']
    
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_interactive_template_wizard_cancel(self, mock_confirm, template_ui):
        """测试交互式模板创建向导 - 取消场景"""
        mock_confirm.return_value = False  # 取消创建
        
        with patch('src.ui.template_manager_ui.Prompt.ask') as mock_prompt:
            mock_prompt.side_effect = [
                'Test Template',
                'Test description',
                '1',
                '',
                '2',
            ]
            
            # 模拟输入脚本内容
            with patch('builtins.input', side_effect=['Write-Host "Test"', 'END']):
                result = template_ui.interactive_template_wizard()
        
        assert result is None
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    def test_interactive_template_wizard_empty_name(self, mock_prompt, template_ui):
        """测试交互式模板创建向导 - 空名称"""
        mock_prompt.side_effect = ['', 'Test description']
        
        result = template_ui.interactive_template_wizard()
        
        assert result is None
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_interactive_template_editor_success(self, mock_confirm, mock_prompt, template_ui, sample_templates):
        """测试交互式模板编辑器 - 成功场景"""
        template = sample_templates[0]
        
        # 模拟用户输入
        mock_prompt.side_effect = [
            '1',  # 选择编辑名称
            'New Name',  # 新名称
            '0',  # 完成编辑
        ]
        mock_confirm.return_value = True  # 确认更新
        
        result = template_ui.interactive_template_editor(template)
        
        assert result is not None
        assert 'name' in result
        assert result['name'] == 'New Name'
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_interactive_template_editor_cancel(self, mock_confirm, mock_prompt, template_ui, sample_templates):
        """测试交互式模板编辑器 - 取消场景"""
        template = sample_templates[0]
        
        mock_prompt.side_effect = ['0']  # 直接完成编辑，不做修改
        
        result = template_ui.interactive_template_editor(template)
        
        assert result is None
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_interactive_template_editor_multiple_fields(self, mock_confirm, mock_prompt, template_ui, sample_templates):
        """测试交互式模板编辑器 - 编辑多个字段"""
        template = sample_templates[0]
        
        # 模拟用户输入
        mock_prompt.side_effect = [
            '1',  # 选择编辑名称
            'New Name',  # 新名称
            '2',  # 选择编辑描述
            'New Description',  # 新描述
            '3',  # 选择编辑关键词
            'new, keywords',  # 新关键词
            '0',  # 完成编辑
        ]
        mock_confirm.return_value = True  # 确认更新
        
        result = template_ui.interactive_template_editor(template)
        
        assert result is not None
        assert 'name' in result
        assert 'description' in result
        assert 'keywords' in result
    
    @patch('src.ui.template_manager_ui.Confirm.ask')
    @patch('src.ui.template_manager_ui.Prompt.ask')
    def test_confirm_template_deletion_success(self, mock_prompt, mock_confirm, template_ui, sample_templates):
        """测试模板删除确认 - 确认删除"""
        template = sample_templates[0]
        
        mock_confirm.return_value = True  # 第一次确认
        mock_prompt.return_value = template.name  # 输入正确的模板名称
        
        result = template_ui.confirm_template_deletion(template)
        
        assert result is True
    
    @patch('src.ui.template_manager_ui.Confirm.ask')
    def test_confirm_template_deletion_cancel_first(self, mock_confirm, template_ui, sample_templates):
        """测试模板删除确认 - 第一次取消"""
        template = sample_templates[0]
        
        mock_confirm.return_value = False  # 第一次取消
        
        result = template_ui.confirm_template_deletion(template)
        
        assert result is False
    
    @patch('src.ui.template_manager_ui.Confirm.ask')
    @patch('src.ui.template_manager_ui.Prompt.ask')
    def test_confirm_template_deletion_wrong_name(self, mock_prompt, mock_confirm, template_ui, sample_templates):
        """测试模板删除确认 - 输入错误的名称"""
        template = sample_templates[0]
        
        mock_confirm.return_value = True  # 第一次确认
        mock_prompt.return_value = 'Wrong Name'  # 输入错误的模板名称
        
        result = template_ui.confirm_template_deletion(template)
        
        assert result is False
    
    def test_display_operation_summary_success(self, template_ui, sample_templates):
        """测试显示操作摘要 - 成功"""
        template = sample_templates[0]
        details = {
            '分类': 'automation',
            '文件路径': '/path/to/template.ps1',
        }
        
        # 不应该抛出异常
        template_ui.display_operation_summary('create', template, True, details)
    
    def test_display_operation_summary_failure(self, template_ui, sample_templates):
        """测试显示操作摘要 - 失败"""
        template = sample_templates[0]
        
        # 不应该抛出异常
        template_ui.display_operation_summary('delete', template, False)
    
    def test_display_operation_summary_different_operations(self, template_ui, sample_templates):
        """测试显示不同操作的摘要"""
        template = sample_templates[0]
        operations = ['create', 'edit', 'delete', 'export', 'import', 'move']
        
        for operation in operations:
            # 不应该抛出异常
            template_ui.display_operation_summary(operation, template, True)
    
    def test_display_template_detail_enhanced(self, template_ui, sample_templates):
        """测试显示增强的模板详情"""
        template = sample_templates[0]
        
        # 不应该抛出异常
        template_ui.display_template_detail_enhanced(template)
    
    def test_display_template_detail_enhanced_custom(self, template_ui, sample_templates):
        """测试显示自定义模板详情"""
        template = sample_templates[1]  # Custom template
        
        # 不应该抛出异常
        template_ui.display_template_detail_enhanced(template)
    
    def test_display_template_detail_enhanced_with_examples(self, template_ui, sample_templates):
        """测试显示带示例的模板详情"""
        template = sample_templates[0]
        template.examples = ['Example 1', 'Example 2', 'Example 3']
        
        # 不应该抛出异常
        template_ui.display_template_detail_enhanced(template)
    
    def test_show_progress_for_operation(self, template_ui):
        """测试显示操作进度"""
        steps = ['Step 1', 'Step 2', 'Step 3']
        
        # 不应该抛出异常
        progress_context = template_ui.show_progress_for_operation('测试操作', steps)
        assert progress_context is not None
    
    def test_template_list_with_long_description(self, template_ui):
        """测试显示带长描述的模板列表"""
        templates = [
            MockTemplate(
                'Long Desc Template',
                'automation',
                'This is a very long description that should be truncated in the display to fit the column width properly',
                keywords=['long', 'desc'],
                is_custom=False
            )
        ]
        
        # 不应该抛出异常
        template_ui.display_template_list_enhanced(templates)
    
    def test_template_list_with_many_keywords(self, template_ui):
        """测试显示带多个关键词的模板列表"""
        templates = [
            MockTemplate(
                'Many Keywords Template',
                'automation',
                'Template with many keywords',
                keywords=['key1', 'key2', 'key3', 'key4', 'key5'],
                is_custom=False
            )
        ]
        
        # 不应该抛出异常
        template_ui.display_template_list_enhanced(templates)
    
    def test_template_list_mixed_types(self, template_ui, sample_templates):
        """测试显示混合类型的模板列表"""
        # sample_templates 包含系统和自定义模板
        template_ui.display_template_list_enhanced(sample_templates)
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    def test_interactive_wizard_keyboard_interrupt(self, mock_prompt, template_ui):
        """测试交互式向导 - 键盘中断"""
        mock_prompt.side_effect = KeyboardInterrupt()
        
        result = template_ui.interactive_template_wizard()
        
        assert result is None
    
    @patch('src.ui.template_manager_ui.Prompt.ask')
    def test_interactive_editor_keyboard_interrupt(self, mock_prompt, template_ui, sample_templates):
        """测试交互式编辑器 - 键盘中断"""
        template = sample_templates[0]
        mock_prompt.side_effect = KeyboardInterrupt()
        
        result = template_ui.interactive_template_editor(template)
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
