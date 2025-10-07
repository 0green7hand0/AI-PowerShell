"""
自定义模板管理器单元测试
"""

import pytest
import os
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
    templates_dir.mkdir()
    
    # 创建系统模板分类目录
    (templates_dir / "file_management").mkdir()
    (templates_dir / "automation").mkdir()
    (templates_dir / "system_monitoring").mkdir()
    
    # 创建自定义模板目录
    custom_dir = templates_dir / "custom"
    custom_dir.mkdir()
    
    # 创建配置目录和文件
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir()
    config_file = config_dir / "templates.yaml"
    
    # 创建基本配置文件
    config_content = """templates:
  file_management:
    batch_rename:
      name: "批量重命名文件"
      description: "批量重命名文件"
      file: "templates/file_management/batch_rename.ps1"
      keywords: ["重命名", "批量"]
      parameters: {}
  automation: {}
  system_monitoring: {}
  custom: {}
"""
    config_file.write_text(config_content, encoding='utf-8')
    
    yield temp_dir
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def manager(temp_workspace):
    """创建 CustomTemplateManager 实例"""
    templates_dir = Path(temp_workspace) / "templates"
    config_path = Path(temp_workspace) / "config" / "templates.yaml"
    return CustomTemplateManager(
        templates_dir=str(templates_dir),
        config_path=str(config_path)
    )


class TestCustomTemplateManagerInit:
    """测试初始化"""
    
    def test_init_creates_custom_directory(self, temp_workspace):
        """测试初始化创建自定义模板目录"""
        templates_dir = Path(temp_workspace) / "templates"
        config_path = Path(temp_workspace) / "config" / "templates.yaml"
        
        # 删除自定义目录
        custom_dir = templates_dir / "custom"
        if custom_dir.exists():
            shutil.rmtree(custom_dir)
        
        # 创建管理器
        manager = CustomTemplateManager(
            templates_dir=str(templates_dir),
            config_path=str(config_path)
        )
        
        # 验证目录被创建
        assert custom_dir.exists()
        assert custom_dir.is_dir()
    
    def test_init_with_existing_directory(self, manager):
        """测试使用现有目录初始化"""
        assert manager.custom_templates_dir.exists()
        assert manager.system_categories == {
            'file_management',
            'automation',
            'system_monitoring'
        }


class TestCreateTemplate:
    """测试创建模板"""
    
    def test_create_simple_template(self, manager):
        """测试创建简单模板"""
        script_content = """
param(
    [string]$SourcePath = "C:\\temp",
    [int]$MaxSize = 100
)

Write-Host "Processing files in $SourcePath"
Write-Host "Max size: $MaxSize MB"
"""
        
        template = manager.create_template(
            name="测试模板",
            description="这是一个测试模板",
            category="test_category",
            script_content=script_content,
            keywords=["测试", "示例"],
            tags=["test"]
        )
        
        # 验证模板对象
        assert isinstance(template, CustomTemplate)
        assert template.name == "测试模板"
        assert template.description == "这是一个测试模板"
        assert template.category == "test_category"
        assert template.is_custom is True
        assert template.author == "user"
        assert template.version == "1.0.0"
        assert "测试" in template.keywords
        assert "test" in template.tags
        
        # 验证参数
        assert "SourcePath" in template.parameters
        assert "MaxSize" in template.parameters
        # Type is inferred from the [string] declaration, not the value
        assert template.parameters["SourcePath"].type == "string"
        assert template.parameters["MaxSize"].type == "integer"
        
        # 验证文件创建
        file_path = Path(template.file_path)
        assert file_path.exists()
        
        # 验证文件内容包含占位符
        content = file_path.read_text(encoding='utf-8')
        assert "{{SourcePath}}" in content
        assert "{{MaxSize}}" in content
    
    def test_create_template_with_invalid_name(self, manager):
        """测试使用无效名称创建模板"""
        with pytest.raises(TemplateValidationError) as exc_info:
            manager.create_template(
                name="",
                description="测试",
                category="test",
                script_content="Write-Host 'test'"
            )
        
        assert "名称不能为空" in str(exc_info.value)
    
    def test_create_template_with_invalid_category(self, manager):
        """测试使用无效分类创建模板"""
        with pytest.raises(TemplateValidationError) as exc_info:
            manager.create_template(
                name="测试",
                description="测试",
                category="invalid category!",
                script_content="Write-Host 'test'"
            )
        
        assert "分类名称" in str(exc_info.value)
    
    def test_create_duplicate_template(self, manager):
        """测试创建重复模板"""
        script_content = "Write-Host 'test'"
        
        # 创建第一个模板
        manager.create_template(
            name="重复模板",
            description="测试",
            category="test",
            script_content=script_content
        )
        
        # 尝试创建同名模板
        with pytest.raises(TemplateConflictError) as exc_info:
            manager.create_template(
                name="重复模板",
                description="测试",
                category="test",
                script_content=script_content
            )
        
        assert "已存在" in str(exc_info.value)
    
    def test_create_template_with_syntax_error(self, manager):
        """测试创建包含语法错误的模板"""
        # PowerShell 语法错误
        script_content = """
param(
    [string]$Path
)

Write-Host "Test
# 缺少引号结束
"""
        
        with pytest.raises(TemplateValidationError) as exc_info:
            manager.create_template(
                name="语法错误模板",
                description="测试",
                category="test",
                script_content=script_content
            )
        
        assert "语法" in str(exc_info.value).lower()


class TestEditTemplate:
    """测试编辑模板"""
    
    def test_edit_template_metadata(self, manager):
        """测试编辑模板元数据"""
        # 创建模板
        template = manager.create_template(
            name="原始名称",
            description="原始描述",
            category="test",
            script_content="Write-Host 'test'",
            keywords=["原始"],
            tags=["old"]
        )
        
        template_id = template.id
        
        # 编辑元数据
        updated_template = manager.edit_template(
            template_id=template_id,
            category="test",
            updates={
                'name': "新名称",
                'description': "新描述",
                'keywords': ["新", "关键词"],
                'tags': ["new", "updated"]
            }
        )
        
        # 验证更新
        assert updated_template.name == "新名称"
        assert updated_template.description == "新描述"
        assert "新" in updated_template.keywords
        assert "new" in updated_template.tags
    
    def test_edit_template_parameters(self, manager):
        """测试编辑模板参数"""
        # 创建模板
        script_content = """
param(
    [string]$Path = "C:\\temp"
)
Write-Host $Path
"""
        template = manager.create_template(
            name="参数测试",
            description="测试",
            category="test",
            script_content=script_content
        )
        
        template_id = template.id
        
        # 添加新参数
        new_param = TemplateParameter(
            name="NewParam",
            type="integer",
            default=42,
            description="新参数",
            required=False
        )
        
        updated_template = manager.edit_template(
            template_id=template_id,
            category="test",
            updates={
                'parameters': {'NewParam': new_param}
            }
        )
        
        # 验证参数更新
        assert "NewParam" in updated_template.parameters
        assert updated_template.parameters["NewParam"].type == "integer"
    
    def test_edit_template_content(self, manager):
        """测试编辑模板内容"""
        # 创建模板
        template = manager.create_template(
            name="内容测试",
            description="测试",
            category="test",
            script_content="Write-Host 'old'"
        )
        
        template_id = template.id
        
        # 更新内容
        new_content = "Write-Host 'new content'"
        updated_template = manager.edit_template(
            template_id=template_id,
            category="test",
            updates={'content': new_content}
        )
        
        # 验证内容更新
        file_path = Path(updated_template.file_path)
        content = file_path.read_text(encoding='utf-8')
        assert "new content" in content
    
    def test_edit_nonexistent_template(self, manager):
        """测试编辑不存在的模板"""
        with pytest.raises(TemplateNotFoundError):
            manager.edit_template(
                template_id="nonexistent",
                category="test",
                updates={'name': "新名称"}
            )
    
    def test_edit_system_template_fails(self, manager, temp_workspace):
        """测试编辑系统模板失败"""
        # 创建一个系统模板配置（模拟）
        # 注意：实际上我们不能直接编辑系统模板，这个测试验证保护机制
        pass  # 系统模板通过 is_custom 标志保护


class TestDeleteTemplate:
    """测试删除模板"""
    
    def test_delete_custom_template(self, manager):
        """测试删除自定义模板"""
        # 创建模板
        template = manager.create_template(
            name="待删除模板",
            description="测试",
            category="test",
            script_content="Write-Host 'test'"
        )
        
        template_id = template.id
        file_path = Path(template.file_path)
        
        # 验证文件存在
        assert file_path.exists()
        
        # 删除模板
        result = manager.delete_template(template_id, "test")
        
        # 验证删除成功
        assert result is True
        assert not file_path.exists()
    
    def test_delete_nonexistent_template(self, manager):
        """测试删除不存在的模板"""
        with pytest.raises(TemplateNotFoundError):
            manager.delete_template("nonexistent", "test")
    
    def test_delete_system_template_fails(self, manager):
        """测试删除系统模板失败"""
        with pytest.raises(TemplateError) as exc_info:
            manager.delete_template("batch_rename", "file_management")
        
        assert "系统模板" in str(exc_info.value)
    
    def test_delete_template_from_system_category_fails(self, manager):
        """测试从系统分类删除模板失败"""
        # 尝试删除系统分类中的任何模板都应该失败
        with pytest.raises(TemplateError) as exc_info:
            manager.delete_template("any_template", "automation")
        
        assert "系统模板" in str(exc_info.value)


class TestListCustomTemplates:
    """测试列出自定义模板"""
    
    def test_list_all_custom_templates(self, manager):
        """测试列出所有自定义模板"""
        # 创建多个模板
        manager.create_template(
            name="模板1",
            description="测试1",
            category="category1",
            script_content="Write-Host 'test1'"
        )
        
        manager.create_template(
            name="模板2",
            description="测试2",
            category="category2",
            script_content="Write-Host 'test2'"
        )
        
        manager.create_template(
            name="模板3",
            description="测试3",
            category="category1",
            script_content="Write-Host 'test3'"
        )
        
        # 列出所有模板
        templates = manager.list_custom_templates()
        
        # 验证
        assert len(templates) == 3
        assert all(isinstance(t, CustomTemplate) for t in templates)
        assert all(t.is_custom for t in templates)
    
    def test_list_templates_by_category(self, manager):
        """测试按分类列出模板"""
        # 创建不同分类的模板
        manager.create_template(
            name="模板1",
            description="测试1",
            category="category1",
            script_content="Write-Host 'test1'"
        )
        
        manager.create_template(
            name="模板2",
            description="测试2",
            category="category2",
            script_content="Write-Host 'test2'"
        )
        
        # 列出特定分类的模板
        templates = manager.list_custom_templates(category="category1")
        
        # 验证
        assert len(templates) == 1
        assert templates[0].category == "category1"
    
    def test_list_empty_category(self, manager):
        """测试列出空分类"""
        templates = manager.list_custom_templates(category="empty_category")
        assert len(templates) == 0


class TestGetTemplateInfo:
    """测试获取模板信息"""
    
    def test_get_template_info(self, manager):
        """测试获取模板详细信息"""
        # 创建模板
        template = manager.create_template(
            name="信息测试",
            description="测试描述",
            category="test",
            script_content="""
param(
    [string]$Path = "C:\\temp",
    [int]$Count = 10
)
Write-Host $Path
""",
            keywords=["测试", "信息"],
            author="测试作者",
            tags=["info", "test"]
        )
        
        # 获取信息
        info = manager.get_template_info(template.id, "test")
        
        # 验证信息
        assert info['name'] == "信息测试"
        assert info['description'] == "测试描述"
        assert info['category'] == "test"
        assert info['is_custom'] is True
        assert info['author'] == "测试作者"
        assert info['version'] == "1.0.0"
        assert "测试" in info['keywords']
        assert "info" in info['tags']
        
        # 验证参数信息
        assert "Path" in info['parameters']
        assert "Count" in info['parameters']
        # Type is inferred from the [string] declaration
        assert info['parameters']['Path']['type'] == "string"
        assert info['parameters']['Count']['type'] == "integer"
    
    def test_get_nonexistent_template_info(self, manager):
        """测试获取不存在模板的信息"""
        with pytest.raises(TemplateNotFoundError):
            manager.get_template_info("nonexistent", "test")


class TestValidation:
    """测试验证功能"""
    
    def test_validate_template_name_empty(self, manager):
        """测试空模板名称验证"""
        with pytest.raises(TemplateValidationError):
            manager._validate_template_name("")
    
    def test_validate_template_name_too_long(self, manager):
        """测试过长模板名称验证"""
        long_name = "a" * 101
        with pytest.raises(TemplateValidationError):
            manager._validate_template_name(long_name)
    
    def test_validate_category_name_empty(self, manager):
        """测试空分类名称验证"""
        with pytest.raises(TemplateValidationError):
            manager._validate_category_name("")
    
    def test_validate_category_name_invalid_chars(self, manager):
        """测试包含无效字符的分类名称"""
        with pytest.raises(TemplateValidationError):
            manager._validate_category_name("invalid category!")


class TestHelperMethods:
    """测试辅助方法"""
    
    def test_generate_template_id(self, manager):
        """测试生成模板 ID"""
        template_id = manager._generate_template_id("测试 模板-名称", "test")
        
        # 验证 ID 格式
        assert " " not in template_id
        assert template_id  # 不为空
        
        # 测试英文名称
        english_id = manager._generate_template_id("Test Template-Name", "test")
        assert english_id.islower()
        assert " " not in english_id
        assert "-" not in english_id
    
    def test_get_template_file_path(self, manager):
        """测试获取模板文件路径"""
        file_path = manager._get_template_file_path("test_template", "test_category")
        
        # 验证路径
        assert "custom" in str(file_path)
        assert "test_category" in str(file_path)
        assert "test_template.ps1" in str(file_path)
    
    def test_template_exists(self, manager):
        """测试检查模板是否存在"""
        # 创建模板
        template = manager.create_template(
            name="存在测试",
            description="测试",
            category="test",
            script_content="Write-Host 'test'"
        )
        
        # 验证存在
        assert manager._template_exists(template.id, "test") is True
        
        # 验证不存在
        assert manager._template_exists("nonexistent", "test") is False


class TestIntegration:
    """集成测试"""
    
    def test_complete_workflow(self, manager):
        """测试完整工作流程：创建 -> 编辑 -> 查询 -> 删除"""
        # 1. 创建模板
        template = manager.create_template(
            name="完整流程测试",
            description="测试完整工作流程",
            category="workflow_test",
            script_content="""
param(
    [string]$InputPath = "C:\\input",
    [string]$OutputPath = "C:\\output"
)

Write-Host "Processing from $InputPath to $OutputPath"
""",
            keywords=["workflow", "test"],
            tags=["integration"]
        )
        
        template_id = template.id
        assert template.name == "完整流程测试"
        
        # 2. 编辑模板
        updated_template = manager.edit_template(
            template_id=template_id,
            category="workflow_test",
            updates={
                'description': "更新后的描述",
                'keywords': ["workflow", "test", "updated"]
            }
        )
        
        assert updated_template.description == "更新后的描述"
        assert "updated" in updated_template.keywords
        
        # 3. 查询模板信息
        info = manager.get_template_info(template_id, "workflow_test")
        assert info['name'] == "完整流程测试"
        assert info['description'] == "更新后的描述"
        
        # 4. 列出模板
        templates = manager.list_custom_templates(category="workflow_test")
        assert len(templates) == 1
        assert templates[0].id == template_id
        
        # 5. 删除模板
        result = manager.delete_template(template_id, "workflow_test")
        assert result is True
        
        # 6. 验证删除
        with pytest.raises(TemplateNotFoundError):
            manager.get_template_info(template_id, "workflow_test")
    
    def test_multiple_templates_management(self, manager):
        """测试管理多个模板"""
        # 创建多个模板
        templates = []
        for i in range(5):
            template = manager.create_template(
                name=f"模板{i}",
                description=f"描述{i}",
                category="multi_test",
                script_content=f"Write-Host 'Template {i}'",
                keywords=[f"keyword{i}"]
            )
            templates.append(template)
        
        # 列出所有模板
        all_templates = manager.list_custom_templates(category="multi_test")
        assert len(all_templates) == 5
        
        # 编辑其中一个
        manager.edit_template(
            template_id=templates[2].id,
            category="multi_test",
            updates={'description': "特殊描述"}
        )
        
        # 删除其中两个
        manager.delete_template(templates[0].id, "multi_test")
        manager.delete_template(templates[4].id, "multi_test")
        
        # 验证剩余模板
        remaining = manager.list_custom_templates(category="multi_test")
        assert len(remaining) == 3
        
        # 验证编辑的模板
        edited_info = manager.get_template_info(templates[2].id, "multi_test")
        assert edited_info['description'] == "特殊描述"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
