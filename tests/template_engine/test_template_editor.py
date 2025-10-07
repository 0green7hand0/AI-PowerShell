"""
模板编辑器单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.template_engine.template_editor import TemplateEditor
from src.template_engine.models import Template, TemplateParameter
from src.template_engine.custom_models import CustomTemplate, ValidationResult
from src.template_engine.exceptions import (
    TemplateValidationError,
    TemplateIOError
)
from src.template_engine.template_validator import TemplateValidator
from src.template_engine.template_version_control import TemplateVersionControl


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_template(temp_dir):
    """创建示例模板"""
    template_file = os.path.join(temp_dir, "test_template.ps1")
    
    # 创建模板文件
    content = """# Test Template
param(
    [string]$Name = "World"
)

Write-Host "Hello, {{NAME}}!"
"""
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 创建模板对象
    from src.template_engine.models import TemplateCategory
    template = Template(
        id="test_template",
        name="Test Template",
        description="A test template",
        file_path=template_file,
        category=TemplateCategory.FILE_MANAGEMENT,
        keywords=["test", "hello"],
        parameters={
            "NAME": TemplateParameter(
                name="NAME",
                type="string",
                default="World",
                description="Name to greet",
                required=False
            )
        }
    )
    
    return template


@pytest.fixture
def sample_custom_template(temp_dir):
    """创建示例自定义模板"""
    template_file = os.path.join(temp_dir, "custom_template.ps1")
    
    content = """# Custom Template
param(
    [string]$Path = "C:\\temp"
)

Write-Host "Processing {{PATH}}"
"""
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    from src.template_engine.models import TemplateCategory
    template = CustomTemplate(
        id="custom_template",
        name="Custom Template",
        description="A custom template",
        file_path=template_file,
        category=TemplateCategory.AUTOMATION,
        keywords=["custom", "path"],
        parameters={
            "PATH": TemplateParameter(
                name="PATH",
                type="path",
                default="C:\\temp",
                description="Path to process",
                required=True
            )
        },
        is_custom=True,
        author="test_user",
        version="1.0.0",
        tags=["test", "custom"]
    )
    
    return template


@pytest.fixture
def editor(temp_dir):
    """创建模板编辑器实例"""
    history_dir = os.path.join(temp_dir, ".history")
    version_control = TemplateVersionControl(history_dir=history_dir)
    validator = TemplateValidator()
    return TemplateEditor(validator=validator, version_control=version_control)


class TestUpdateMetadata:
    """测试元数据更新功能"""
    
    def test_update_name(self, editor, sample_template):
        """测试更新模板名称"""
        updates = {'name': 'Updated Template Name'}
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert updated.name == 'Updated Template Name'
        assert updated.description == sample_template.description
    
    def test_update_description(self, editor, sample_template):
        """测试更新模板描述"""
        updates = {'description': 'Updated description'}
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert updated.description == 'Updated description'
        assert updated.name == sample_template.name
    
    def test_update_keywords(self, editor, sample_template):
        """测试更新关键词"""
        updates = {'keywords': ['new', 'keywords', 'list']}
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert updated.keywords == ['new', 'keywords', 'list']
    
    def test_update_category(self, editor, sample_template):
        """测试更新分类"""
        updates = {'category': 'new_category'}
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert updated.category == 'new_category'
    
    def test_update_custom_template_tags(self, editor, sample_custom_template):
        """测试更新自定义模板标签"""
        updates = {'tags': ['tag1', 'tag2', 'tag3']}
        updated = editor.update_metadata(sample_custom_template, updates, create_backup=False)
        
        assert updated.tags == ['tag1', 'tag2', 'tag3']
    
    def test_update_custom_template_timestamp(self, editor, sample_custom_template):
        """测试更新自定义模板时间戳"""
        original_time = sample_custom_template.updated_at
        
        # 等待一小段时间确保时间戳不同
        import time
        time.sleep(0.01)
        
        updates = {'name': 'Updated Name'}
        updated = editor.update_metadata(sample_custom_template, updates, create_backup=False)
        
        assert updated.updated_at > original_time
    
    def test_update_multiple_fields(self, editor, sample_template):
        """测试同时更新多个字段"""
        updates = {
            'name': 'New Name',
            'description': 'New Description',
            'keywords': ['new', 'keywords'],
            'category': 'new_category'
        }
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert updated.name == 'New Name'
        assert updated.description == 'New Description'
        assert updated.keywords == ['new', 'keywords']
        assert updated.category == 'new_category'
    
    def test_empty_name_raises_error(self, editor, sample_template):
        """测试空名称抛出错误"""
        updates = {'name': ''}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert "名称不能为空" in str(exc_info.value)
    
    def test_long_name_raises_error(self, editor, sample_template):
        """测试过长名称抛出错误"""
        updates = {'name': 'x' * 101}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert "名称过长" in str(exc_info.value)
    
    def test_long_description_raises_error(self, editor, sample_template):
        """测试过长描述抛出错误"""
        updates = {'description': 'x' * 501}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert "描述过长" in str(exc_info.value)
    
    def test_invalid_category_format(self, editor, sample_template):
        """测试无效分类格式"""
        updates = {'category': 'invalid category!'}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert "分类名称" in str(exc_info.value)
    
    def test_invalid_keywords_type(self, editor, sample_template):
        """测试无效关键词类型"""
        updates = {'keywords': 'not a list'}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_metadata(sample_template, updates, create_backup=False)
        
        assert "关键词必须是列表" in str(exc_info.value)


class TestUpdateParameters:
    """测试参数更新功能"""
    
    def test_add_new_parameter(self, editor, sample_template):
        """测试添加新参数"""
        new_param = TemplateParameter(
            name="NEW_PARAM",
            type="string",
            default="default_value",
            description="A new parameter",
            required=False
        )
        
        parameter_updates = {'NEW_PARAM': new_param}
        updated = editor.update_parameters(sample_template, parameter_updates, create_backup=False)
        
        assert 'NEW_PARAM' in updated.parameters
        assert updated.parameters['NEW_PARAM'].name == "NEW_PARAM"
    
    def test_update_existing_parameter(self, editor, sample_template):
        """测试更新现有参数"""
        updated_param = TemplateParameter(
            name="NAME",
            type="string",
            default="Updated Default",
            description="Updated description",
            required=True
        )
        
        parameter_updates = {'NAME': updated_param}
        updated = editor.update_parameters(sample_template, parameter_updates, create_backup=False)
        
        assert updated.parameters['NAME'].default == "Updated Default"
        assert updated.parameters['NAME'].required == True
    
    def test_update_multiple_parameters(self, editor, sample_template):
        """测试更新多个参数"""
        param1 = TemplateParameter(
            name="PARAM1",
            type="string",
            default="value1",
            description="Parameter 1",
            required=False
        )
        
        param2 = TemplateParameter(
            name="PARAM2",
            type="integer",
            default="42",
            description="Parameter 2",
            required=True
        )
        
        parameter_updates = {'PARAM1': param1, 'PARAM2': param2}
        updated = editor.update_parameters(sample_template, parameter_updates, create_backup=False)
        
        assert 'PARAM1' in updated.parameters
        assert 'PARAM2' in updated.parameters
    
    def test_invalid_parameter_type_raises_error(self, editor, sample_template):
        """测试无效参数类型抛出错误"""
        parameter_updates = {'INVALID': "not a TemplateParameter object"}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_parameters(sample_template, parameter_updates, create_backup=False)
        
        assert "必须是 TemplateParameter 类型" in str(exc_info.value)
    
    def test_parameter_validation_failure(self, editor, sample_template):
        """测试参数验证失败"""
        # 创建一个类型不匹配的参数
        invalid_param = TemplateParameter(
            name="INVALID",
            type="integer",
            default="not_an_integer",  # 类型不匹配
            description="Invalid parameter",
            required=False
        )
        
        parameter_updates = {'INVALID': invalid_param}
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_parameters(sample_template, parameter_updates, create_backup=False)
        
        assert "参数配置验证失败" in str(exc_info.value)
    
    def test_update_parameters_on_custom_template(self, editor, sample_custom_template):
        """测试在自定义模板上更新参数"""
        original_time = sample_custom_template.updated_at
        
        import time
        time.sleep(0.01)
        
        new_param = TemplateParameter(
            name="NEW_PARAM",
            type="boolean",
            default=True,
            description="New boolean parameter",
            required=False
        )
        
        parameter_updates = {'NEW_PARAM': new_param}
        updated = editor.update_parameters(sample_custom_template, parameter_updates, create_backup=False)
        
        assert 'NEW_PARAM' in updated.parameters
        assert updated.updated_at > original_time


class TestUpdateContent:
    """测试内容更新功能"""
    
    def test_update_content_success(self, editor, sample_template):
        """测试成功更新内容"""
        new_content = """# Updated Template
param(
    [string]$Name = "World"
)

Write-Host "Goodbye, {{NAME}}!"
"""
        
        updated = editor.update_content(sample_template, new_content, create_backup=False)
        
        # 验证文件已更新
        with open(sample_template.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content == new_content
    
    def test_update_content_with_syntax_validation(self, editor, sample_template):
        """测试带语法验证的内容更新"""
        new_content = """# Valid PowerShell
Write-Host "This is valid PowerShell"
"""
        
        updated = editor.update_content(
            sample_template,
            new_content,
            create_backup=False,
            validate_syntax=True
        )
        
        with open(sample_template.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content == new_content
    
    def test_empty_content_raises_error(self, editor, sample_template):
        """测试空内容抛出错误"""
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_content(sample_template, "", create_backup=False)
        
        assert "内容不能为空" in str(exc_info.value)
    
    def test_whitespace_only_content_raises_error(self, editor, sample_template):
        """测试仅空白内容抛出错误"""
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_content(sample_template, "   \n\t  ", create_backup=False)
        
        assert "内容不能为空" in str(exc_info.value)
    
    def test_invalid_syntax_raises_error(self, editor, sample_template):
        """测试无效语法抛出错误"""
        invalid_content = """# Invalid PowerShell
Write-Host "Unclosed string
"""
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.update_content(
                sample_template,
                invalid_content,
                create_backup=False,
                validate_syntax=True
            )
        
        assert "语法验证失败" in str(exc_info.value)
    
    def test_skip_syntax_validation(self, editor, sample_template):
        """测试跳过语法验证"""
        # 即使语法无效，如果跳过验证也应该成功
        invalid_content = """# Potentially Invalid
Write-Host "Test"
"""
        
        # 不应抛出异常
        updated = editor.update_content(
            sample_template,
            invalid_content,
            create_backup=False,
            validate_syntax=False
        )
        
        with open(sample_template.file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        assert file_content == invalid_content
    
    def test_update_content_creates_directory(self, editor, sample_template, temp_dir):
        """测试更新内容时创建目录"""
        # 创建一个不存在目录的模板
        new_file = os.path.join(temp_dir, "subdir", "new_template.ps1")
        sample_template.file_path = new_file
        
        new_content = """Write-Host "Test"
"""
        
        updated = editor.update_content(sample_template, new_content, create_backup=False)
        
        assert os.path.exists(new_file)
        assert os.path.exists(os.path.dirname(new_file))
    
    def test_update_content_on_custom_template(self, editor, sample_custom_template):
        """测试在自定义模板上更新内容"""
        original_time = sample_custom_template.updated_at
        
        import time
        time.sleep(0.01)
        
        new_content = """# Updated Custom Template
Write-Host "Updated content"
"""
        
        updated = editor.update_content(
            sample_custom_template,
            new_content,
            create_backup=False,
            validate_syntax=False
        )
        
        assert updated.updated_at > original_time


class TestSyncToFile:
    """测试文件同步功能"""
    
    def test_sync_to_file_success(self, editor, sample_template):
        """测试成功同步到文件"""
        result = editor.sync_to_file(sample_template)
        
        assert result == True
    
    def test_sync_to_file_with_validation_error(self, editor, sample_template):
        """测试验证失败时同步失败"""
        # 创建一个无效的模板（参数类型不匹配）
        sample_template.parameters['INVALID'] = TemplateParameter(
            name="INVALID",
            type="integer",
            default="not_an_integer",
            description="Invalid",
            required=False
        )
        
        with pytest.raises(TemplateValidationError) as exc_info:
            editor.sync_to_file(sample_template)
        
        assert "验证失败" in str(exc_info.value)
    
    def test_sync_creates_directory(self, editor, sample_template, temp_dir):
        """测试同步时创建目录"""
        new_file = os.path.join(temp_dir, "new_subdir", "template.ps1")
        
        # 先写入内容到新位置
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        with open(new_file, 'w', encoding='utf-8') as f:
            f.write("Write-Host 'Test'")
        
        sample_template.file_path = new_file
        sample_template.content = None  # 清除缓存，强制重新加载
        
        result = editor.sync_to_file(sample_template)
        
        assert result == True
        assert os.path.exists(os.path.dirname(new_file))


class TestVersionBackup:
    """测试版本备份集成"""
    
    def test_backup_created_on_metadata_update(self, editor, sample_template):
        """测试元数据更新时创建备份"""
        updates = {'name': 'Updated Name'}
        
        # 启用备份
        updated = editor.update_metadata(sample_template, updates, create_backup=True)
        
        # 验证备份已创建
        template_id = editor._get_template_id(sample_template)
        versions = editor.version_control.list_versions(template_id)
        
        assert len(versions) > 0
    
    def test_backup_created_on_parameter_update(self, editor, sample_template):
        """测试参数更新时创建备份"""
        new_param = TemplateParameter(
            name="NEW_PARAM",
            type="string",
            default="value",
            description="New parameter",
            required=False
        )
        
        parameter_updates = {'NEW_PARAM': new_param}
        updated = editor.update_parameters(sample_template, parameter_updates, create_backup=True)
        
        template_id = editor._get_template_id(sample_template)
        versions = editor.version_control.list_versions(template_id)
        
        assert len(versions) > 0
    
    def test_backup_created_on_content_update(self, editor, sample_template):
        """测试内容更新时创建备份"""
        new_content = """Write-Host "Updated"
"""
        
        updated = editor.update_content(sample_template, new_content, create_backup=True)
        
        template_id = editor._get_template_id(sample_template)
        versions = editor.version_control.list_versions(template_id)
        
        assert len(versions) > 0
    
    def test_no_backup_when_disabled(self, editor, sample_template):
        """测试禁用备份时不创建备份"""
        updates = {'name': 'Updated Name'}
        
        updated = editor.update_metadata(sample_template, updates, create_backup=False)
        
        template_id = editor._get_template_id(sample_template)
        versions = editor.version_control.list_versions(template_id)
        
        # 应该没有版本（或者只有之前的版本）
        assert len(versions) == 0


class TestGetTemplateId:
    """测试模板ID生成"""
    
    def test_get_template_id_removes_prefix(self, editor):
        """测试移除templates前缀"""
        from src.template_engine.models import TemplateCategory
        template = Template(
            id="test_id",
            name="Test",
            description="Test",
            file_path="templates/custom/my_template.ps1",
            category=TemplateCategory.FILE_MANAGEMENT,
            keywords=[],
            parameters={}
        )
        
        template_id = editor._get_template_id(template)
        
        # 应该使用模板的ID
        assert template_id == "test_id"
    
    def test_get_template_id_removes_suffix(self, editor):
        """测试移除.ps1后缀"""
        from src.template_engine.models import TemplateCategory
        template = Template(
            id="test_template",
            name="Test",
            description="Test",
            file_path="templates/test/template.ps1",
            category=TemplateCategory.FILE_MANAGEMENT,
            keywords=[],
            parameters={}
        )
        
        template_id = editor._get_template_id(template)
        
        assert template_id == "test_template"
    
    def test_get_template_id_replaces_separators(self, editor):
        """测试替换路径分隔符"""
        from src.template_engine.models import TemplateCategory
        template = Template(
            id="category_subcategory_template",
            name="Test",
            description="Test",
            file_path="templates/category/subcategory/template.ps1",
            category=TemplateCategory.FILE_MANAGEMENT,
            keywords=[],
            parameters={}
        )
        
        template_id = editor._get_template_id(template)
        
        assert template_id == "category_subcategory_template"
        assert "/" not in template_id
        assert "\\" not in template_id
