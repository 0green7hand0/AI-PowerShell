"""
测试模板分类管理功能

测试 CustomTemplateManager 的分类管理方法。
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.template_engine.custom_template_manager import CustomTemplateManager
from src.template_engine.custom_models import CustomTemplate
from src.template_engine.models import TemplateParameter
from src.template_engine.exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateConflictError,
    TemplateValidationError
)


@pytest.fixture
def temp_workspace():
    """创建临时工作空间"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建目录结构
    templates_dir = Path(temp_dir) / "templates"
    config_dir = Path(temp_dir) / "config"
    
    templates_dir.mkdir()
    config_dir.mkdir()
    
    # 创建系统模板目录
    (templates_dir / "file_management").mkdir()
    (templates_dir / "automation").mkdir()
    (templates_dir / "system_monitoring").mkdir()
    
    # 创建自定义模板目录
    custom_dir = templates_dir / "custom"
    custom_dir.mkdir()
    
    # 创建配置文件
    config_path = config_dir / "templates.yaml"
    config_content = """templates:
  file_management:
    batch_rename:
      name: "批量重命名"
      description: "批量重命名文件"
      file: "templates/file_management/batch_rename.ps1"
      keywords: ["重命名", "批量"]
      parameters: {}
  
  automation:
    backup_files:
      name: "文件备份"
      description: "备份文件"
      file: "templates/automation/backup_files.ps1"
      keywords: ["备份"]
      parameters: {}
  
  custom: {}
"""
    config_path.write_text(config_content, encoding='utf-8')
    
    yield {
        'temp_dir': temp_dir,
        'templates_dir': str(templates_dir),
        'config_path': str(config_path)
    }
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def manager(temp_workspace):
    """创建 CustomTemplateManager 实例"""
    return CustomTemplateManager(
        templates_dir=temp_workspace['templates_dir'],
        config_path=temp_workspace['config_path']
    )


class TestCreateCategory:
    """测试创建分类功能"""
    
    def test_create_valid_category(self, manager, temp_workspace):
        """测试创建有效的分类"""
        result = manager.create_category("my_scripts")
        
        assert result is True
        
        # 验证目录已创建
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "my_scripts"
        assert category_dir.exists()
        assert category_dir.is_dir()
    
    def test_create_category_with_underscore(self, manager, temp_workspace):
        """测试创建包含下划线的分类"""
        result = manager.create_category("my_custom_scripts")
        
        assert result is True
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "my_custom_scripts"
        assert category_dir.exists()
    
    def test_create_category_with_hyphen(self, manager, temp_workspace):
        """测试创建包含连字符的分类"""
        result = manager.create_category("my-scripts")
        
        assert result is True
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "my-scripts"
        assert category_dir.exists()
    
    def test_create_duplicate_category(self, manager):
        """测试创建重复的分类"""
        manager.create_category("test_category")
        
        with pytest.raises(TemplateConflictError) as exc_info:
            manager.create_category("test_category")
        
        assert "已存在" in str(exc_info.value)
    
    def test_create_system_category(self, manager):
        """测试创建系统分类名称（应该失败）"""
        with pytest.raises(TemplateConflictError) as exc_info:
            manager.create_category("file_management")
        
        assert "系统分类" in str(exc_info.value)
    
    def test_create_category_invalid_name_empty(self, manager):
        """测试创建空名称的分类"""
        with pytest.raises(TemplateValidationError) as exc_info:
            manager.create_category("")
        
        assert "不能为空" in str(exc_info.value)
    
    def test_create_category_invalid_name_special_chars(self, manager):
        """测试创建包含特殊字符的分类"""
        with pytest.raises(TemplateValidationError) as exc_info:
            manager.create_category("my@scripts")
        
        assert "只能包含" in str(exc_info.value)


class TestListCategories:
    """测试列出分类功能"""
    
    def test_list_all_categories(self, manager):
        """测试列出所有分类（系统+自定义）"""
        # 创建一些自定义分类
        manager.create_category("custom1")
        manager.create_category("custom2")
        
        categories = manager.list_categories(include_system=True)
        
        # 应该包含系统分类和自定义分类
        category_names = [cat['name'] for cat in categories]
        
        assert "file_management" in category_names
        assert "automation" in category_names
        assert "system_monitoring" in category_names
        assert "custom1" in category_names
        assert "custom2" in category_names
    
    def test_list_custom_categories_only(self, manager):
        """测试只列出自定义分类"""
        manager.create_category("custom1")
        manager.create_category("custom2")
        
        categories = manager.list_categories(include_system=False)
        
        category_names = [cat['name'] for cat in categories]
        
        assert "file_management" not in category_names
        assert "custom1" in category_names
        assert "custom2" in category_names
    
    def test_list_categories_with_template_count(self, manager, temp_workspace):
        """测试分类列表包含模板数量"""
        # 创建分类
        manager.create_category("test_category")
        
        # 创建一些模板文件
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "test_category"
        (category_dir / "template1.ps1").write_text("# Template 1")
        (category_dir / "template2.ps1").write_text("# Template 2")
        
        categories = manager.list_categories(include_system=False)
        
        test_cat = next(cat for cat in categories if cat['name'] == 'test_category')
        assert test_cat['template_count'] == 2
    
    def test_list_categories_system_flag(self, manager):
        """测试分类列表正确标记系统分类"""
        manager.create_category("custom1")
        
        categories = manager.list_categories(include_system=True)
        
        # 检查系统分类标记
        file_mgmt = next(cat for cat in categories if cat['name'] == 'file_management')
        assert file_mgmt['is_system'] is True
        
        # 检查自定义分类标记
        custom1 = next(cat for cat in categories if cat['name'] == 'custom1')
        assert custom1['is_system'] is False
    
    def test_list_categories_includes_path(self, manager, temp_workspace):
        """测试分类列表包含路径信息"""
        manager.create_category("test_category")
        
        categories = manager.list_categories(include_system=False)
        
        test_cat = next(cat for cat in categories if cat['name'] == 'test_category')
        assert 'path' in test_cat
        assert "test_category" in test_cat['path']


class TestDeleteCategory:
    """测试删除分类功能"""
    
    def test_delete_empty_category(self, manager, temp_workspace):
        """测试删除空分类"""
        # 创建空分类
        manager.create_category("empty_category")
        
        # 删除分类
        result = manager.delete_category("empty_category")
        
        assert result is True
        
        # 验证目录已删除
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "empty_category"
        assert not category_dir.exists()
    
    def test_delete_non_empty_category_without_force(self, manager, temp_workspace):
        """测试删除非空分类（不使用 force）"""
        # 创建分类并添加模板
        manager.create_category("test_category")
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "test_category"
        (category_dir / "template1.ps1").write_text("# Template 1")
        
        # 尝试删除应该失败
        with pytest.raises(TemplateError) as exc_info:
            manager.delete_category("test_category", force=False)
        
        assert "不为空" in str(exc_info.value)
        assert category_dir.exists()
    
    def test_delete_non_empty_category_with_force(self, manager, temp_workspace):
        """测试强制删除非空分类"""
        # 创建分类并添加模板
        manager.create_category("test_category")
        category_dir = Path(temp_workspace['templates_dir']) / "custom" / "test_category"
        (category_dir / "template1.ps1").write_text("# Template 1")
        (category_dir / "template2.ps1").write_text("# Template 2")
        
        # 强制删除
        result = manager.delete_category("test_category", force=True)
        
        assert result is True
        assert not category_dir.exists()
    
    def test_delete_system_category(self, manager):
        """测试删除系统分类（应该失败）"""
        with pytest.raises(TemplateError) as exc_info:
            manager.delete_category("file_management")
        
        assert "系统分类" in str(exc_info.value)
    
    def test_delete_non_existent_category(self, manager):
        """测试删除不存在的分类"""
        with pytest.raises(TemplateNotFoundError) as exc_info:
            manager.delete_category("non_existent")
        
        assert "不存在" in str(exc_info.value)


class TestMoveTemplate:
    """测试移动模板功能"""
    
    def test_move_template_to_new_category(self, manager, temp_workspace):
        """测试移动模板到新分类"""
        # 创建源分类和目标分类
        manager.create_category("source_category")
        manager.create_category("target_category")
        
        # 创建模板
        script_content = """
param(
    [string]$Path = "C:\\test"
)

Write-Host "Path: $Path"
"""
        template = manager.create_template(
            name="Test Template",
            description="A test template",
            category="source_category",
            script_content=script_content,
            keywords=["test"]
        )
        
        # 移动模板
        moved_template = manager.move_template(
            template_id=template.id,
            from_category="source_category",
            to_category="target_category"
        )
        
        # 验证模板已移动
        assert moved_template.category == "target_category"
        assert "target_category" in moved_template.file_path
        
        # 验证源文件不存在
        source_file = Path(temp_workspace['templates_dir']) / "custom" / "source_category" / f"{template.id}.ps1"
        assert not source_file.exists()
        
        # 验证目标文件存在
        target_file = Path(temp_workspace['templates_dir']) / "custom" / "target_category" / f"{template.id}.ps1"
        assert target_file.exists()
    
    def test_move_template_updates_config(self, manager):
        """测试移动模板更新配置"""
        # 创建分类和模板
        manager.create_category("cat1")
        manager.create_category("cat2")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        template = manager.create_template(
            name="Test Template",
            description="Test",
            category="cat1",
            script_content=script_content
        )
        
        # 移动模板
        manager.move_template(
            template_id=template.id,
            from_category="cat1",
            to_category="cat2"
        )
        
        # 验证配置已更新
        # 源分类中不应该有该模板
        source_config = manager.config_updater.get_template_config(template.id, "cat1")
        assert source_config is None
        
        # 目标分类中应该有该模板
        target_config = manager.config_updater.get_template_config(template.id, "cat2")
        assert target_config is not None
        assert target_config['name'] == "Test Template"
    
    def test_move_template_to_existing_template(self, manager):
        """测试移动模板到已存在同名模板的分类"""
        # 创建分类
        manager.create_category("cat1")
        manager.create_category("cat2")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        
        # 在两个分类中创建同名模板
        template1 = manager.create_template(
            name="Same Name",
            description="Template 1",
            category="cat1",
            script_content=script_content
        )
        
        template2 = manager.create_template(
            name="Same Name",
            description="Template 2",
            category="cat2",
            script_content=script_content
        )
        
        # 尝试移动应该失败（因为 ID 相同）
        with pytest.raises(TemplateConflictError) as exc_info:
            manager.move_template(
                template_id=template1.id,
                from_category="cat1",
                to_category="cat2"
            )
        
        assert "已存在" in str(exc_info.value)
    
    def test_move_template_to_system_category(self, manager):
        """测试移动模板到系统分类（应该失败）"""
        # 创建自定义分类和模板
        manager.create_category("custom_cat")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        template = manager.create_template(
            name="Test Template",
            description="Test",
            category="custom_cat",
            script_content=script_content
        )
        
        # 尝试移动到系统分类
        with pytest.raises(TemplateError) as exc_info:
            manager.move_template(
                template_id=template.id,
                from_category="custom_cat",
                to_category="file_management"
            )
        
        assert "系统分类" in str(exc_info.value)
    
    def test_move_non_existent_template(self, manager):
        """测试移动不存在的模板"""
        manager.create_category("cat1")
        manager.create_category("cat2")
        
        with pytest.raises(TemplateNotFoundError):
            manager.move_template(
                template_id="non_existent",
                from_category="cat1",
                to_category="cat2"
            )
    
    def test_move_template_creates_target_category_if_needed(self, manager):
        """测试移动模板时自动创建目标分类目录"""
        # 创建源分类和模板
        manager.create_category("source_cat")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        template = manager.create_template(
            name="Test Template",
            description="Test",
            category="source_cat",
            script_content=script_content
        )
        
        # 移动到新分类（目录不存在）
        moved_template = manager.move_template(
            template_id=template.id,
            from_category="source_cat",
            to_category="new_target_cat"
        )
        
        # 验证目标目录已创建
        assert moved_template.category == "new_target_cat"
        target_file = Path(moved_template.file_path)
        assert target_file.exists()
        assert target_file.parent.exists()


class TestCategoryIntegration:
    """测试分类管理的集成场景"""
    
    def test_create_template_in_new_category(self, manager):
        """测试在新分类中创建模板"""
        # 先创建分类
        manager.create_category("my_category")
        
        # 在该分类中创建模板
        script_content = """
param([string]$Message = "Hello")
Write-Host $Message
"""
        template = manager.create_template(
            name="My Template",
            description="Test template",
            category="my_category",
            script_content=script_content
        )
        
        assert template.category == "my_category"
        assert "my_category" in template.file_path
    
    def test_list_templates_by_category(self, manager):
        """测试按分类列出模板"""
        # 创建多个分类和模板
        manager.create_category("cat1")
        manager.create_category("cat2")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        
        manager.create_template(
            name="Template 1",
            description="Test 1",
            category="cat1",
            script_content=script_content
        )
        
        manager.create_template(
            name="Template 2",
            description="Test 2",
            category="cat1",
            script_content=script_content
        )
        
        manager.create_template(
            name="Template 3",
            description="Test 3",
            category="cat2",
            script_content=script_content
        )
        
        # 列出 cat1 的模板
        cat1_templates = manager.list_custom_templates(category="cat1")
        assert len(cat1_templates) == 2
        
        # 列出 cat2 的模板
        cat2_templates = manager.list_custom_templates(category="cat2")
        assert len(cat2_templates) == 1
    
    def test_delete_category_after_moving_templates(self, manager):
        """测试移动所有模板后删除分类"""
        # 创建分类和模板
        manager.create_category("old_cat")
        manager.create_category("new_cat")
        
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        
        template1 = manager.create_template(
            name="Template 1",
            description="Test 1",
            category="old_cat",
            script_content=script_content
        )
        
        template2 = manager.create_template(
            name="Template 2",
            description="Test 2",
            category="old_cat",
            script_content=script_content
        )
        
        # 移动所有模板
        manager.move_template(template1.id, "old_cat", "new_cat")
        manager.move_template(template2.id, "old_cat", "new_cat")
        
        # 删除空分类
        result = manager.delete_category("old_cat")
        assert result is True
    
    def test_category_workflow(self, manager):
        """测试完整的分类管理工作流"""
        # 1. 创建分类
        manager.create_category("workflow_test")
        
        # 2. 列出分类
        categories = manager.list_categories(include_system=False)
        assert any(cat['name'] == 'workflow_test' for cat in categories)
        
        # 3. 在分类中创建模板
        script_content = """
param([string]$Name = "test")
Write-Host $Name
"""
        template = manager.create_template(
            name="Workflow Template",
            description="Test",
            category="workflow_test",
            script_content=script_content
        )
        
        # 4. 验证模板在分类中
        templates = manager.list_custom_templates(category="workflow_test")
        assert len(templates) == 1
        assert templates[0].id == template.id
        
        # 5. 创建新分类并移动模板
        manager.create_category("new_workflow")
        manager.move_template(template.id, "workflow_test", "new_workflow")
        
        # 6. 验证模板已移动
        old_templates = manager.list_custom_templates(category="workflow_test")
        assert len(old_templates) == 0
        
        new_templates = manager.list_custom_templates(category="new_workflow")
        assert len(new_templates) == 1
        
        # 7. 删除空分类
        manager.delete_category("workflow_test")
        
        # 8. 验证分类已删除
        categories = manager.list_categories(include_system=False)
        assert not any(cat['name'] == 'workflow_test' for cat in categories)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
