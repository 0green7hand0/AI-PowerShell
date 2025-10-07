"""
测试CLI命令函数
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import (
    template_create_command,
    template_list_command,
    template_edit_command,
    template_delete_command,
    template_export_command,
    template_import_command,
    template_history_command,
    template_restore_command,
    PowerShellAssistant
)
from src.template_engine.custom_models import CustomTemplate
from src.template_engine.models import TemplateParameter
from src.template_engine.exceptions import TemplateError


class TestTemplateCLICommands:
    """测试模板CLI命令"""
    
    @pytest.fixture
    def mock_assistant(self):
        """创建模拟的助手对象"""
        assistant = Mock(spec=PowerShellAssistant)
        assistant.custom_template_manager = Mock()
        return assistant
    
    @pytest.fixture
    def sample_template(self):
        """创建示例模板"""
        from src.template_engine.models import TemplateCategory
        return CustomTemplate(
            id="test_template",
            name="test_template",
            description="Test template description",
            category=TemplateCategory.AUTOMATION,
            file_path="templates/custom/test_template.ps1",
            keywords=["test", "sample"],
            parameters={
                "param1": TemplateParameter(
                    name="param1",
                    type="string",
                    description="Test parameter",
                    required=True,
                    default=""
                )
            }
        )
    
    def test_template_list_command_no_manager(self, capsys):
        """测试列表命令 - 无管理器"""
        assistant = Mock(spec=PowerShellAssistant)
        assistant.custom_template_manager = None
        
        result = template_list_command(assistant)
        
        assert result == 1
        captured = capsys.readouterr()
        assert "自定义模板管理器未初始化" in captured.out
    
    def test_template_list_command_empty(self, mock_assistant, capsys):
        """测试列表命令 - 空列表"""
        mock_assistant.custom_template_manager.list_custom_templates.return_value = []
        
        result = template_list_command(mock_assistant)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "暂无自定义模板" in captured.out
    
    def test_template_list_command_with_templates(self, mock_assistant, sample_template, capsys):
        """测试列表命令 - 有模板"""
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [sample_template]
        
        result = template_list_command(mock_assistant)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "test_template" in captured.out
        assert "Test template description" in captured.out
    
    def test_template_delete_command_not_found(self, mock_assistant, capsys):
        """测试删除命令 - 模板不存在"""
        mock_assistant.custom_template_manager.get_template_info.return_value = None
        
        result = template_delete_command(mock_assistant, "nonexistent")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "模板不存在" in captured.out
    
    @patch('builtins.input', return_value='wrong_name')
    def test_template_delete_command_wrong_confirmation(self, mock_input, mock_assistant, sample_template, capsys):
        """测试删除命令 - 确认名称错误"""
        mock_assistant.custom_template_manager.get_template_info.return_value = sample_template
        
        result = template_delete_command(mock_assistant, "test_template")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "名称不匹配" in captured.out
    
    @patch('builtins.input', return_value='test_template')
    def test_template_delete_command_success(self, mock_input, mock_assistant, sample_template, capsys):
        """测试删除命令 - 成功"""
        mock_assistant.custom_template_manager.get_template_info.return_value = sample_template
        mock_assistant.custom_template_manager.delete_template.return_value = True
        
        result = template_delete_command(mock_assistant, "test_template")
        
        assert result == 0
        captured = capsys.readouterr()
        assert "模板已删除" in captured.out
    
    def test_template_export_command_success(self, mock_assistant, capsys):
        """测试导出命令 - 成功"""
        mock_assistant.custom_template_manager.export_template.return_value = "/path/to/export.zip"
        
        result = template_export_command(mock_assistant, "test_template", "/path/to/output")
        
        assert result == 0
        captured = capsys.readouterr()
        assert "模板已导出到" in captured.out
    
    def test_template_export_command_error(self, mock_assistant, capsys):
        """测试导出命令 - 错误"""
        mock_assistant.custom_template_manager.export_template.side_effect = TemplateError("Export failed")
        
        result = template_export_command(mock_assistant, "test_template", "/path/to/output")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "导出失败" in captured.out
    
    def test_template_import_command_file_not_found(self, mock_assistant, capsys):
        """测试导入命令 - 文件不存在"""
        result = template_import_command(mock_assistant, "/nonexistent/file.zip")
        
        assert result == 1
        captured = capsys.readouterr()
        assert "文件不存在" in captured.out
    
    def test_template_history_command_no_versions(self, mock_assistant, capsys):
        """测试历史命令 - 无版本"""
        mock_assistant.custom_template_manager.version_control.list_versions.return_value = []
        
        result = template_history_command(mock_assistant, "test_template")
        
        assert result == 0
        captured = capsys.readouterr()
        assert "暂无历史版本" in captured.out
    
    @patch('builtins.input', return_value='n')
    def test_template_restore_command_cancelled(self, mock_input, mock_assistant, capsys):
        """测试恢复命令 - 取消"""
        result = template_restore_command(mock_assistant, "test_template", 1)
        
        assert result == 1
        captured = capsys.readouterr()
        assert "取消恢复" in captured.out
    
    @patch('builtins.input', return_value='y')
    def test_template_restore_command_success(self, mock_input, mock_assistant, capsys):
        """测试恢复命令 - 成功"""
        mock_assistant.custom_template_manager.version_control.restore_version.return_value = True
        
        result = template_restore_command(mock_assistant, "test_template", 1)
        
        assert result == 0
        captured = capsys.readouterr()
        assert "已恢复到版本" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
