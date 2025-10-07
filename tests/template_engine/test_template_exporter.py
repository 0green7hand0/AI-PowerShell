"""
模板导入导出器测试
"""

import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest

from src.template_engine.template_exporter import TemplateExporter
from src.template_engine.custom_models import (
    CustomTemplate,
    TemplatePackage,
    ValidationResult
)
from src.template_engine.models import TemplateParameter, TemplateCategory
from src.template_engine.exceptions import (
    TemplateNotFoundError,
    TemplateConflictError,
    TemplateValidationError,
    TemplateIOError
)


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def templates_dir(temp_dir):
    """创建模板目录结构"""
    templates_path = Path(temp_dir) / "templates"
    templates_path.mkdir(parents=True, exist_ok=True)
    
    # 创建自定义分类目录
    custom_dir = templates_path / "custom"
    custom_dir.mkdir(exist_ok=True)
    
    return str(templates_path)


@pytest.fixture
def config_path(temp_dir):
    """创建配置文件"""
    config_file = Path(temp_dir) / "config" / "templates.yaml"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text("templates: {}", encoding='utf-8')
    return str(config_file)


@pytest.fixture
def exporter(templates_dir, config_path):
    """创建导出器实例"""
    return TemplateExporter(templates_dir, config_path)


@pytest.fixture
def sample_template(templates_dir):
    """创建示例模板"""
    # 使用 sanitized 文件名，这样导入时会产生冲突
    template_file = Path(templates_dir) / "custom" / "Test_Template.ps1"
    template_content = """# Test Template
param(
    [string]$SourcePath = "C:\\temp",
    [int]$MaxSize = 100
)

Write-Host "Processing $SourcePath with max size $MaxSize"
"""
    template_file.write_text(template_content, encoding='utf-8')
    
    template = CustomTemplate(
        id="Test_Template",
        name="Test Template",
        category=TemplateCategory.AUTOMATION,
        file_path=str(template_file),
        description="A test template for unit testing",
        keywords=["test", "sample"],
        parameters={
            "SOURCE_PATH": TemplateParameter(
                name="SOURCE_PATH",
                type="string",
                default="C:\\temp",
                description="Source path",
                required=True
            ),
            "MAX_SIZE": TemplateParameter(
                name="MAX_SIZE",
                type="integer",
                default=100,
                description="Maximum size",
                required=False
            )
        },
        author="test_user",
        version="1.0.0",
        tags=["test", "automation"]
    )
    
    return template


class TestTemplateExporter:
    """测试模板导出功能"""
    
    def test_export_template_success(self, exporter, sample_template):
        """测试成功导出模板"""
        # 导出模板
        output_path = exporter.export_template(sample_template)
        
        # 验证文件存在
        assert os.path.exists(output_path)
        assert output_path.endswith('.zip')
        
        # 验证 ZIP 内容
        with zipfile.ZipFile(output_path, 'r') as zf:
            file_list = zf.namelist()
            assert 'template.ps1' in file_list
            assert 'config.json' in file_list
            assert 'manifest.json' in file_list
            assert 'metadata.json' in file_list
            
            # 验证模板内容
            template_content = zf.read('template.ps1').decode('utf-8')
            assert 'Test Template' in template_content
            assert 'SourcePath' in template_content
            
            # 验证配置
            config_data = json.loads(zf.read('config.json').decode('utf-8'))
            assert config_data['name'] == 'Test Template'
            assert config_data['description'] == 'A test template for unit testing'
            assert 'SOURCE_PATH' in config_data['parameters']
            assert 'MAX_SIZE' in config_data['parameters']
            
            # 验证清单
            manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
            assert 'version' in manifest_data
            assert 'checksum' in manifest_data
            assert 'exported_at' in manifest_data
    
    def test_export_template_custom_path(self, exporter, sample_template, temp_dir):
        """测试导出到自定义路径"""
        custom_path = os.path.join(temp_dir, "custom_export.zip")
        
        output_path = exporter.export_template(sample_template, output_path=custom_path)
        
        assert output_path == custom_path
        assert os.path.exists(custom_path)
    
    def test_export_template_without_metadata(self, exporter, sample_template):
        """测试导出时不包含元数据"""
        output_path = exporter.export_template(sample_template, include_metadata=False)
        
        with zipfile.ZipFile(output_path, 'r') as zf:
            # 清单中应该没有元数据
            manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
            assert manifest_data['metadata'] == {}
    
    def test_export_template_file_not_found(self, exporter, sample_template):
        """测试导出不存在的模板文件"""
        sample_template.file_path = "/nonexistent/path/template.ps1"
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            exporter.export_template(sample_template)
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_export_template_checksum(self, exporter, sample_template):
        """测试导出包含正确的校验和"""
        output_path = exporter.export_template(sample_template)
        
        with zipfile.ZipFile(output_path, 'r') as zf:
            manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
            checksum = manifest_data['checksum']
            
            # 验证校验和不为空
            assert checksum
            assert len(checksum) == 64  # SHA256 长度


class TestTemplateImporter:
    """测试模板导入功能"""
    
    def test_import_template_success(self, exporter, sample_template):
        """测试成功导入模板"""
        # 先导出
        export_path = exporter.export_template(sample_template)
        
        # 删除原始模板文件
        os.remove(sample_template.file_path)
        
        # 导入
        imported_template, message = exporter.import_template(
            export_path,
            conflict_resolution="overwrite"
        )
        
        # 验证导入结果
        assert imported_template is not None
        assert imported_template.name == "Test Template"
        assert "imported successfully" in message
        
        # 验证文件已创建
        assert os.path.exists(imported_template.file_path)
        
        # 验证内容
        with open(imported_template.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Template' in content
    
    def test_import_template_to_different_category(self, exporter, sample_template, templates_dir):
        """测试导入到不同分类"""
        # 导出
        export_path = exporter.export_template(sample_template)
        
        # 创建新分类目录
        new_category = "imported"
        new_category_dir = Path(templates_dir) / new_category
        new_category_dir.mkdir(exist_ok=True)
        
        # 导入到新分类
        imported_template, message = exporter.import_template(
            export_path,
            target_category=new_category,
            conflict_resolution="overwrite"
        )
        
        # 验证分类
        assert new_category in imported_template.file_path
    
    def test_import_template_conflict_overwrite(self, exporter, sample_template):
        """测试导入时覆盖现有模板"""
        # 导出
        export_path = exporter.export_template(sample_template)
        
        # 修改原始文件
        with open(sample_template.file_path, 'w', encoding='utf-8') as f:
            f.write("# Modified content")
        
        # 导入并覆盖
        imported_template, message = exporter.import_template(
            export_path,
            conflict_resolution="overwrite"
        )
        
        # 验证文件被覆盖
        with open(imported_template.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Template' in content
            assert 'Modified content' not in content
    
    def test_import_template_conflict_rename(self, exporter, sample_template):
        """测试导入时重命名"""
        # 导出
        export_path = exporter.export_template(sample_template)
        
        # 导入到同一分类（custom）以产生冲突，并重命名
        imported_template, message = exporter.import_template(
            export_path,
            target_category="custom",  # 导入到同一分类
            conflict_resolution="rename"
        )
        
        # 验证名称不同
        assert imported_template.name != sample_template.name
        assert imported_template.name.startswith("Test Template")
        assert "_" in imported_template.name
    
    def test_import_template_conflict_skip(self, exporter, sample_template):
        """测试导入时跳过"""
        # 导出
        export_path = exporter.export_template(sample_template)
        
        # 导入到同一分类并跳过
        result, message = exporter.import_template(
            export_path,
            target_category="custom",  # 导入到同一分类
            conflict_resolution="skip"
        )
        
        # 验证跳过
        assert result is None
        assert "skipped" in message.lower()
    
    def test_import_template_conflict_ask_raises_error(self, exporter, sample_template):
        """测试导入时询问策略抛出异常"""
        # 导出
        export_path = exporter.export_template(sample_template)
        
        # 导入到同一分类时使用 ask 策略应该抛出异常
        with pytest.raises(TemplateConflictError) as exc_info:
            exporter.import_template(
                export_path,
                target_category="custom",  # 导入到同一分类
                conflict_resolution="ask"
            )
        
        assert "already exists" in str(exc_info.value).lower()
    
    def test_import_template_package_not_found(self, exporter):
        """测试导入不存在的包"""
        with pytest.raises(TemplateNotFoundError):
            exporter.import_template("/nonexistent/package.zip")
    
    def test_import_template_invalid_package(self, exporter, temp_dir):
        """测试导入无效的包"""
        # 创建无效的 ZIP 文件
        invalid_zip = os.path.join(temp_dir, "invalid.zip")
        with zipfile.ZipFile(invalid_zip, 'w') as zf:
            zf.writestr('random.txt', 'invalid content')
        
        with pytest.raises(TemplateValidationError):
            exporter.import_template(invalid_zip, conflict_resolution="overwrite")


class TestPackageValidation:
    """测试包验证功能"""
    
    def test_validate_package_success(self, exporter, sample_template):
        """测试验证有效的包"""
        export_path = exporter.export_template(sample_template)
        
        result = exporter.validate_package(export_path)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_package_not_found(self, exporter):
        """测试验证不存在的包"""
        result = exporter.validate_package("/nonexistent/package.zip")
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
    
    def test_validate_package_not_zip(self, exporter, temp_dir):
        """测试验证非 ZIP 文件"""
        not_zip = os.path.join(temp_dir, "not_zip.txt")
        with open(not_zip, 'w') as f:
            f.write("This is not a ZIP file")
        
        result = exporter.validate_package(not_zip)
        
        assert not result.is_valid
        assert any("not a valid ZIP" in error for error in result.errors)
    
    def test_validate_package_missing_files(self, exporter, temp_dir):
        """测试验证缺少必需文件的包"""
        incomplete_zip = os.path.join(temp_dir, "incomplete.zip")
        with zipfile.ZipFile(incomplete_zip, 'w') as zf:
            zf.writestr('template.ps1', '# Template')
            # 缺少 config.json 和 manifest.json
        
        result = exporter.validate_package(incomplete_zip)
        
        assert not result.is_valid
        assert any("Missing required file" in error for error in result.errors)
    
    def test_validate_package_invalid_json(self, exporter, temp_dir):
        """测试验证包含无效 JSON 的包"""
        invalid_json_zip = os.path.join(temp_dir, "invalid_json.zip")
        with zipfile.ZipFile(invalid_json_zip, 'w') as zf:
            zf.writestr('template.ps1', '# Template')
            zf.writestr('config.json', 'invalid json {')
            zf.writestr('manifest.json', '{}')
        
        result = exporter.validate_package(invalid_json_zip)
        
        assert not result.is_valid
        assert any("Invalid JSON" in error for error in result.errors)
    
    def test_validate_package_missing_config_keys(self, exporter, temp_dir):
        """测试验证缺少必需配置键的包"""
        incomplete_config_zip = os.path.join(temp_dir, "incomplete_config.zip")
        with zipfile.ZipFile(incomplete_config_zip, 'w') as zf:
            zf.writestr('template.ps1', '# Template')
            zf.writestr('config.json', json.dumps({"name": "Test"}))  # 缺少其他键
            zf.writestr('manifest.json', json.dumps({"version": "1.0"}))
        
        result = exporter.validate_package(incomplete_config_zip)
        
        assert not result.is_valid
        assert any("Missing required config key" in error for error in result.errors)
    
    def test_validate_package_checksum_mismatch(self, exporter, sample_template, temp_dir):
        """测试验证校验和不匹配的包"""
        # 先创建有效的包
        export_path = exporter.export_template(sample_template)
        
        # 修改包内容但不更新校验和
        modified_zip = os.path.join(temp_dir, "modified.zip")
        with zipfile.ZipFile(export_path, 'r') as zf_in:
            with zipfile.ZipFile(modified_zip, 'w') as zf_out:
                for item in zf_in.infolist():
                    data = zf_in.read(item.filename)
                    if item.filename == 'template.ps1':
                        # 修改模板内容
                        data = b'# Modified template'
                    zf_out.writestr(item, data)
        
        result = exporter.validate_package(modified_zip)
        
        assert not result.is_valid
        assert any("Checksum verification failed" in error for error in result.errors)
    
    def test_validate_package_empty_template(self, exporter, temp_dir):
        """测试验证空模板文件的包"""
        empty_template_zip = os.path.join(temp_dir, "empty_template.zip")
        with zipfile.ZipFile(empty_template_zip, 'w') as zf:
            zf.writestr('template.ps1', '')  # 空文件
            zf.writestr('config.json', json.dumps({
                "name": "Test",
                "description": "Test",
                "parameters": {}
            }))
            zf.writestr('manifest.json', json.dumps({"version": "1.0"}))
        
        result = exporter.validate_package(empty_template_zip)
        
        assert not result.is_valid
        assert any("empty" in error.lower() for error in result.errors)


class TestConflictHandling:
    """测试冲突处理功能"""
    
    def test_check_conflict_no_conflict(self, exporter):
        """测试检查不存在的模板（无冲突）"""
        conflict_info = exporter._check_conflict("nonexistent_template", "custom")
        
        assert not conflict_info["has_conflict"]
        assert conflict_info["template_name"] == "nonexistent_template"
    
    def test_check_conflict_exists(self, exporter, sample_template):
        """测试检查已存在的模板（有冲突）"""
        # sample_template 的文件名是 Test_Template.ps1
        # 检查 "Test Template" 会被 sanitize 成 "Test_Template"，应该能检测到冲突
        conflict_info = exporter._check_conflict("Test Template", "custom")
        
        assert conflict_info["has_conflict"]
        assert conflict_info["existing_path"] is not None
    
    def test_generate_unique_name(self, exporter, sample_template):
        """测试生成唯一名称"""
        unique_name = exporter._generate_unique_name("Test Template", "custom")
        
        assert unique_name != "Test Template"
        assert unique_name.startswith("Test Template")
        assert "_" in unique_name
    
    def test_handle_conflict_skip(self, exporter):
        """测试跳过冲突"""
        conflict_info = {"has_conflict": True, "template_name": "Test", "category": "custom"}
        
        resolution = exporter._handle_conflict("Test", conflict_info, "skip")
        
        assert resolution["action"] == "skip"
    
    def test_handle_conflict_overwrite(self, exporter):
        """测试覆盖冲突"""
        conflict_info = {"has_conflict": True, "template_name": "Test", "category": "custom"}
        
        resolution = exporter._handle_conflict("Test", conflict_info, "overwrite")
        
        assert resolution["action"] == "overwrite"
    
    def test_handle_conflict_rename(self, exporter):
        """测试重命名冲突"""
        conflict_info = {"has_conflict": True, "template_name": "Test", "category": "custom"}
        
        resolution = exporter._handle_conflict("Test", conflict_info, "rename")
        
        assert resolution["action"] == "rename"
        assert "new_name" in resolution
        assert resolution["new_name"] != "Test"


class TestUtilityMethods:
    """测试工具方法"""
    
    def test_sanitize_filename(self, exporter):
        """测试文件名清理"""
        # 测试不安全字符
        unsafe_name = 'test<>:"/\\|?*template'
        safe_name = exporter._sanitize_filename(unsafe_name)
        
        assert '<' not in safe_name
        assert '>' not in safe_name
        assert ':' not in safe_name
        assert '"' not in safe_name
        assert '/' not in safe_name
        assert '\\' not in safe_name
        assert '|' not in safe_name
        assert '?' not in safe_name
        assert '*' not in safe_name
    
    def test_sanitize_filename_length_limit(self, exporter):
        """测试文件名长度限制"""
        long_name = 'a' * 200
        safe_name = exporter._sanitize_filename(long_name)
        
        assert len(safe_name) <= 100
    
    def test_sanitize_filename_whitespace(self, exporter):
        """测试文件名空格处理"""
        name_with_spaces = '  test template  '
        safe_name = exporter._sanitize_filename(name_with_spaces)
        
        assert not safe_name.startswith(' ')
        assert not safe_name.endswith(' ')
    
    def test_list_exports(self, exporter, sample_template):
        """测试列出导出文件"""
        # 导出几个模板
        export1 = exporter.export_template(sample_template)
        
        exports = exporter.list_exports()
        
        assert len(exports) >= 1
        assert export1 in exports
    
    def test_list_exports_empty(self, exporter):
        """测试列出空导出目录"""
        # 删除导出目录
        if exporter.exports_dir.exists():
            shutil.rmtree(exporter.exports_dir)
        
        exports = exporter.list_exports()
        
        assert exports == []
    
    def test_delete_export(self, exporter, sample_template):
        """测试删除导出文件"""
        export_path = exporter.export_template(sample_template)
        
        assert os.path.exists(export_path)
        
        result = exporter.delete_export(export_path)
        
        assert result is True
        assert not os.path.exists(export_path)
    
    def test_delete_export_nonexistent(self, exporter):
        """测试删除不存在的导出文件"""
        result = exporter.delete_export("/nonexistent/export.zip")
        
        assert result is False


class TestTemplatePackageModel:
    """测试 TemplatePackage 数据模型"""
    
    def test_package_validate_success(self):
        """测试有效包的验证"""
        package = TemplatePackage(
            template_file="# Template content",
            config={
                "name": "Test",
                "description": "Test template",
                "parameters": {}
            },
            metadata={
                "created_at": "2025-10-07T10:00:00",
                "author": "test",
                "version": "1.0.0"
            }
        )
        
        assert package.validate()
    
    def test_package_validate_missing_template(self):
        """测试缺少模板内容的包"""
        package = TemplatePackage(
            template_file="",
            config={"name": "Test", "description": "Test", "parameters": {}},
            metadata={"created_at": "2025-10-07", "author": "test", "version": "1.0"}
        )
        
        assert not package.validate()
    
    def test_package_validate_missing_config_keys(self):
        """测试缺少配置键的包"""
        package = TemplatePackage(
            template_file="# Content",
            config={"name": "Test"},  # 缺少其他键
            metadata={"created_at": "2025-10-07", "author": "test", "version": "1.0"}
        )
        
        assert not package.validate()
    
    def test_package_calculate_checksum(self):
        """测试计算校验和"""
        package = TemplatePackage(
            template_file="# Template",
            config={"name": "Test", "description": "Test", "parameters": {}},
            metadata={"created_at": "2025-10-07", "author": "test", "version": "1.0"}
        )
        
        checksum = package.calculate_checksum()
        
        assert checksum
        assert len(checksum) == 64  # SHA256
    
    def test_package_verify_checksum_success(self):
        """测试验证正确的校验和"""
        package = TemplatePackage(
            template_file="# Template",
            config={"name": "Test", "description": "Test", "parameters": {}},
            metadata={"created_at": "2025-10-07", "author": "test", "version": "1.0"}
        )
        
        package.checksum = package.calculate_checksum()
        
        assert package.verify_checksum()
    
    def test_package_verify_checksum_mismatch(self):
        """测试验证不匹配的校验和"""
        package = TemplatePackage(
            template_file="# Template",
            config={"name": "Test", "description": "Test", "parameters": {}},
            metadata={"created_at": "2025-10-07", "author": "test", "version": "1.0"}
        )
        
        package.checksum = "invalid_checksum"
        
        assert not package.verify_checksum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
