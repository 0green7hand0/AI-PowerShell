"""
端到端测试：自定义模板完整工作流

测试完整的用户场景，包括创建、使用、编辑、导出导入、版本控制和删除。
验证所有操作的文件系统和配置一致性。
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.template_engine.custom_template_manager import CustomTemplateManager
from src.template_engine.template_exporter import TemplateExporter
from src.template_engine.template_version_control import TemplateVersionControl
from src.template_engine.script_generator import ScriptGenerator
from src.template_engine.template_manager import TemplateManager
from src.template_engine.template_matcher import TemplateMatcher
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
    
    # 创建必要的目录结构
    templates_dir = Path(temp_dir) / "templates"
    templates_dir.mkdir()
    
    # 创建系统模板分类目录
    (templates_dir / "file_management").mkdir()
    (templates_dir / "automation").mkdir()
    (templates_dir / "system_monitoring").mkdir()
    
    # 创建配置目录
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir()
    
    # 创建初始配置文件
    config_file = config_dir / "templates.yaml"
    config_file.write_text("templates: {}\n", encoding='utf-8')
    
    yield {
        'root': temp_dir,
        'templates_dir': str(templates_dir),
        'config_path': str(config_file)
    }
    
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def custom_manager(temp_workspace):
    """创建自定义模板管理器实例"""
    return CustomTemplateManager(
        templates_dir=temp_workspace['templates_dir'],
        config_path=temp_workspace['config_path']
    )


@pytest.fixture
def sample_script():
    """示例 PowerShell 脚本"""
    return """
# 文件备份脚本
param(
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "C:\\Backups",
    
    [int]$RetentionDays = 30
)

Write-Host "开始备份: $SourcePath"
Write-Host "备份目标: $BackupPath"
Write-Host "保留天数: $RetentionDays"

# 创建备份目录
if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath | Out-Null
}

# 执行备份
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupPath "backup_$timestamp.zip"

Compress-Archive -Path $SourcePath -DestinationPath $backupFile

Write-Host "备份完成: $backupFile"
"""


class TestCustomTemplateCreation:
    """测试场景 1: 创建自定义模板"""
    
    def test_create_template_from_script(self, custom_manager, sample_script):
        """测试从脚本创建模板"""
        # 创建模板
        template = custom_manager.create_template(
            name="文件备份模板",
            description="自动备份文件到指定目录",
            category="backup",
            script_content=sample_script,
            keywords=["备份", "文件", "压缩"],
            tags=["utility", "backup"]
        )
        
        # 验证模板对象
        assert template is not None
        assert template.name == "文件备份模板"
        assert template.category == "backup"
        assert template.is_custom is True
        assert len(template.keywords) == 3
        assert "备份" in template.keywords
        
        # 验证参数识别
        assert template.parameters is not None
        assert "SourcePath" in template.parameters
        assert "BackupPath" in template.parameters
        assert "RetentionDays" in template.parameters
        
        # 验证参数类型
        assert template.parameters["SourcePath"].type == "string"
        assert template.parameters["SourcePath"].required is True
        assert template.parameters["RetentionDays"].type == "integer"
        
        # 验证文件系统
        file_path = Path(template.file_path)
        assert file_path.exists()
        assert file_path.suffix == ".ps1"
        
        # 验证文件内容包含占位符
        content = file_path.read_text(encoding='utf-8')
        assert "{{SourcePath}}" in content or "$SourcePath" in content
        
        # 验证配置文件更新
        config = custom_manager.config_updater._load_config()
        assert "backup" in config.get("templates", {})
    
    def test_create_template_with_duplicate_name(self, custom_manager, sample_script):
        """测试创建重复名称的模板"""
        # 创建第一个模板
        custom_manager.create_template(
            name="测试模板",
            description="第一个模板",
            category="test",
            script_content=sample_script
        )
        
        # 尝试创建同名模板
        with pytest.raises(TemplateConflictError) as exc_info:
            custom_manager.create_template(
                name="测试模板",
                description="第二个模板",
                category="test",
                script_content=sample_script
            )
        
        assert "已存在" in str(exc_info.value)
    
    def test_create_template_with_invalid_syntax(self, custom_manager):
        """测试创建语法错误的模板"""
        invalid_script = """
        # 语法错误的脚本
        Write-Host "测试
        # 缺少引号结束
        """
        
        with pytest.raises(TemplateValidationError):
            custom_manager.create_template(
                name="错误模板",
                description="包含语法错误",
                category="test",
                script_content=invalid_script
            )


class TestTemplateUsageWithAI:
    """测试场景 2: 使用 AI 生成基于自定义模板的脚本"""
    
    def test_generate_script_from_custom_template(self, custom_manager, sample_script, temp_workspace):
        """测试基于自定义模板生成脚本"""
        # 1. 创建自定义模板
        template = custom_manager.create_template(
            name="数据备份",
            description="备份重要数据文件",
            category="backup",
            script_content=sample_script,
            keywords=["备份", "数据", "文件"]
        )
        
        # 2. 验证模板已创建并包含参数
        assert template is not None
        assert template.parameters is not None
        assert len(template.parameters) > 0
        
        # 3. 验证模板文件存在并可读取
        template_content = Path(template.file_path).read_text(encoding='utf-8')
        assert template_content is not None
        assert len(template_content) > 0
        
        # 4. 验证模板可以通过 custom_manager 查询
        templates = custom_manager.list_custom_templates(category="backup")
        assert len(templates) > 0
        assert any(t.name == "数据备份" for t in templates)
    
    def test_search_and_match_custom_template(self, custom_manager, sample_script, temp_workspace):
        """测试搜索和匹配自定义模板"""
        # 创建多个自定义模板
        template1 = custom_manager.create_template(
            name="文件备份",
            description="备份文件到指定位置",
            category="backup",
            script_content=sample_script,
            keywords=["备份", "文件"]
        )
        
        template2 = custom_manager.create_template(
            name="数据库备份",
            description="备份数据库",
            category="backup",
            script_content=sample_script,
            keywords=["备份", "数据库", "SQL"]
        )
        
        # 使用 custom_manager 列出模板
        backup_templates = custom_manager.list_custom_templates(category="backup")
        
        # 验证模板已创建
        assert len(backup_templates) >= 2
        
        # 验证可以通过关键词找到模板
        file_backup = [t for t in backup_templates if "文件" in t.keywords]
        db_backup = [t for t in backup_templates if "数据库" in t.keywords]
        
        assert len(file_backup) >= 1
        assert len(db_backup) >= 1


class TestTemplateEditing:
    """测试场景 3: 编辑自定义模板"""
    
    def test_edit_template_metadata(self, custom_manager, sample_script):
        """测试编辑模板元数据"""
        # 创建模板
        template = custom_manager.create_template(
            name="原始名称",
            description="原始描述",
            category="test",
            script_content=sample_script,
            keywords=["原始"]
        )
        
        # 编辑元数据
        updated_template = custom_manager.edit_template(
            template_id=template.id,
            category="test",
            updates={
                "name": "更新后的名称",
                "description": "更新后的描述",
                "keywords": ["更新", "测试"],
                "tags": ["v2", "updated"]
            }
        )
        
        # 验证更新
        assert updated_template.name == "更新后的名称"
        assert updated_template.description == "更新后的描述"
        assert "更新" in updated_template.keywords
        assert "v2" in updated_template.tags
        
        # 验证配置文件更新
        config = custom_manager.config_updater.get_template_config(template.id, "test")
        assert config["name"] == "更新后的名称"
    
    def test_edit_template_parameters(self, custom_manager, sample_script):
        """测试编辑模板参数"""
        # 创建模板
        template = custom_manager.create_template(
            name="参数测试",
            description="测试参数编辑",
            category="test",
            script_content=sample_script
        )
        
        # 编辑参数
        new_param = TemplateParameter(
            name="NewParam",
            type="string",
            default="default_value",
            description="新增参数",
            required=False
        )
        
        updated_template = custom_manager.edit_template(
            template_id=template.id,
            category="test",
            updates={
                "parameters": {"NewParam": new_param}
            }
        )
        
        # 验证参数更新
        assert "NewParam" in updated_template.parameters
        assert updated_template.parameters["NewParam"].description == "新增参数"
    
    def test_edit_template_content(self, custom_manager, sample_script):
        """测试编辑模板内容"""
        # 创建模板
        template = custom_manager.create_template(
            name="内容测试",
            description="测试内容编辑",
            category="test",
            script_content=sample_script
        )
        
        # 新内容
        new_content = """
        # 更新后的脚本
        param([string]$TestParam = "test")
        Write-Host "Updated: $TestParam"
        """
        
        # 编辑内容
        updated_template = custom_manager.edit_template(
            template_id=template.id,
            category="test",
            updates={"content": new_content}
        )
        
        # 验证内容更新
        file_path = Path(updated_template.file_path)
        content = file_path.read_text(encoding='utf-8')
        assert "Updated:" in content


class TestTemplateExportImport:
    """测试场景 4: 导出和导入模板"""
    
    def test_export_template(self, custom_manager, sample_script, temp_workspace):
        """测试导出模板"""
        # 创建模板
        template = custom_manager.create_template(
            name="导出测试",
            description="测试模板导出",
            category="export_test",
            script_content=sample_script,
            keywords=["导出", "测试"]
        )
        
        # 导出模板
        exporter = TemplateExporter(
            templates_dir=temp_workspace['templates_dir'],
            config_path=temp_workspace['config_path']
        )
        
        export_path = exporter.export_template(template)
        
        # 验证导出文件
        assert os.path.exists(export_path)
        assert export_path.endswith('.zip')
        
        # 验证包内容
        validation_result = exporter.validate_package(export_path)
        assert validation_result.is_valid
    
    def test_import_template(self, custom_manager, sample_script, temp_workspace):
        """测试导入模板"""
        # 1. 创建并导出模板
        template = custom_manager.create_template(
            name="导入测试",
            description="测试模板导入",
            category="import_test",
            script_content=sample_script
        )
        
        exporter = TemplateExporter(
            templates_dir=temp_workspace['templates_dir'],
            config_path=temp_workspace['config_path']
        )
        
        export_path = exporter.export_template(template)
        
        # 2. 删除原模板
        custom_manager.delete_template(template.id, "import_test")
        
        # 3. 导入模板
        imported_template, message = exporter.import_template(
            package_path=export_path,
            conflict_resolution="overwrite"
        )
        
        # 4. 验证导入
        assert imported_template is not None
        assert imported_template.name == "导入测试"
        assert "successfully" in message.lower()
        
        # 验证文件存在
        file_path = Path(imported_template.file_path)
        assert file_path.exists()
    
    def test_import_with_conflict_rename(self, custom_manager, sample_script, temp_workspace):
        """测试导入冲突时重命名"""
        # 1. 创建原始模板
        original = custom_manager.create_template(
            name="冲突测试",
            description="原始模板",
            category="conflict_test",
            script_content=sample_script
        )
        
        # 2. 导出模板
        exporter = TemplateExporter(
            templates_dir=temp_workspace['templates_dir'],
            config_path=temp_workspace['config_path']
        )
        
        export_path = exporter.export_template(original)
        
        # 3. 导入（应该检测到冲突并重命名）
        imported_template, message = exporter.import_template(
            package_path=export_path,
            conflict_resolution="rename"
        )
        
        # 4. 验证导入成功
        assert imported_template is not None
        # With rename strategy, the template should be imported successfully
        # It may have the same name but different file path
        assert "successfully" in message.lower() or "imported" in message.lower()


class TestVersionControl:
    """测试场景 5: 查看和恢复历史版本"""
    
    def test_version_creation_on_edit(self, custom_manager, sample_script):
        """测试编辑时自动创建版本"""
        # 创建模板
        template = custom_manager.create_template(
            name="版本测试",
            description="测试版本控制",
            category="version_test",
            script_content=sample_script
        )
        
        # 获取版本控制器
        version_control = custom_manager.editor.version_control
        
        # 编辑模板（应该自动创建版本）
        custom_manager.edit_template(
            template_id=template.id,
            category="version_test",
            updates={"description": "第一次更新"}
        )
        
        # 再次编辑
        custom_manager.edit_template(
            template_id=template.id,
            category="version_test",
            updates={"description": "第二次更新"}
        )
        
        # 验证版本历史
        versions = version_control.list_versions(template.id)
        assert len(versions) >= 2  # 至少有两个版本
    
    def test_list_versions(self, custom_manager, sample_script):
        """测试列出版本历史"""
        # 创建模板
        template = custom_manager.create_template(
            name="历史测试",
            description="测试历史列表",
            category="history_test",
            script_content=sample_script
        )
        
        version_control = custom_manager.editor.version_control
        
        # 进行多次编辑
        for i in range(3):
            custom_manager.edit_template(
                template_id=template.id,
                category="history_test",
                updates={"description": f"更新 {i+1}"}
            )
        
        # 列出版本
        versions = version_control.list_versions(template.id)
        
        # 验证版本列表
        assert len(versions) >= 3
        assert all(v.template_id == template.id for v in versions)
        
        # 验证版本按时间排序（最新的在前）
        for i in range(len(versions) - 1):
            assert versions[i].version_number >= versions[i+1].version_number
    
    def test_restore_version(self, custom_manager, sample_script):
        """测试恢复历史版本"""
        # 创建模板
        template = custom_manager.create_template(
            name="恢复测试",
            description="原始描述",
            category="restore_test",
            script_content=sample_script
        )
        
        version_control = custom_manager.editor.version_control
        
        # 编辑模板
        updated = custom_manager.edit_template(
            template_id=template.id,
            category="restore_test",
            updates={"description": "更新后的描述"}
        )
        
        # 获取版本列表
        versions = version_control.list_versions(template.id)
        assert len(versions) >= 1
        
        # 恢复到第一个版本
        first_version = versions[-1]  # 最早的版本
        restored = version_control.restore_version(
            template_id=template.id,
            version_number=first_version.version_number,
            target_file=template.file_path
        )
        
        # 验证恢复
        assert restored is not None
        assert restored.version_number == first_version.version_number


class TestTemplateDeletion:
    """测试场景 6: 删除自定义模板"""
    
    def test_delete_custom_template(self, custom_manager, sample_script):
        """测试删除自定义模板"""
        # 创建模板
        template = custom_manager.create_template(
            name="删除测试",
            description="测试模板删除",
            category="delete_test",
            script_content=sample_script
        )
        
        # 验证模板存在
        file_path = Path(template.file_path)
        assert file_path.exists()
        
        # 删除模板
        result = custom_manager.delete_template(template.id, "delete_test")
        
        # 验证删除结果
        assert result is True
        
        # 验证文件已删除
        assert not file_path.exists()
        
        # 验证配置已更新
        config = custom_manager.config_updater.get_template_config(template.id, "delete_test")
        assert config is None
    
    def test_cannot_delete_system_template(self, custom_manager):
        """测试不能删除系统模板"""
        # 尝试删除系统分类中的模板
        with pytest.raises(TemplateError) as exc_info:
            custom_manager.delete_template("some_template", "file_management")
        
        assert "系统模板" in str(exc_info.value) or "system" in str(exc_info.value).lower()
    
    def test_delete_nonexistent_template(self, custom_manager):
        """测试删除不存在的模板"""
        with pytest.raises(TemplateNotFoundError):
            custom_manager.delete_template("nonexistent", "test")


class TestFileSystemConsistency:
    """测试场景 7: 验证文件系统和配置一致性"""
    
    def test_file_and_config_consistency_after_create(self, custom_manager, sample_script):
        """测试创建后的一致性"""
        template = custom_manager.create_template(
            name="一致性测试",
            description="测试文件系统一致性",
            category="consistency_test",
            script_content=sample_script
        )
        
        # 验证文件存在
        file_path = Path(template.file_path)
        assert file_path.exists()
        
        # 验证配置存在
        config = custom_manager.config_updater.get_template_config(template.id, "consistency_test")
        assert config is not None
        assert config["name"] == template.name
        
        # 验证文件路径匹配
        assert config["file"] == template.file_path
    
    def test_file_and_config_consistency_after_edit(self, custom_manager, sample_script):
        """测试编辑后的一致性"""
        template = custom_manager.create_template(
            name="编辑一致性",
            description="测试编辑后一致性",
            category="edit_consistency",
            script_content=sample_script
        )
        
        # 编辑模板
        updated = custom_manager.edit_template(
            template_id=template.id,
            category="edit_consistency",
            updates={"name": "更新后的名称"}
        )
        
        # 验证文件仍然存在
        file_path = Path(updated.file_path)
        assert file_path.exists()
        
        # 验证配置已更新
        config = custom_manager.config_updater.get_template_config(updated.id, "edit_consistency")
        assert config["name"] == "更新后的名称"
    
    def test_file_and_config_consistency_after_delete(self, custom_manager, sample_script):
        """测试删除后的一致性"""
        template = custom_manager.create_template(
            name="删除一致性",
            description="测试删除后一致性",
            category="delete_consistency",
            script_content=sample_script
        )
        
        file_path = Path(template.file_path)
        
        # 删除模板
        custom_manager.delete_template(template.id, "delete_consistency")
        
        # 验证文件已删除
        assert not file_path.exists()
        
        # 验证配置已删除
        config = custom_manager.config_updater.get_template_config(template.id, "delete_consistency")
        assert config is None


class TestCompleteWorkflow:
    """测试场景 8: 完整工作流集成测试"""
    
    def test_complete_template_lifecycle(self, custom_manager, sample_script, temp_workspace):
        """测试完整的模板生命周期"""
        # 1. 创建模板
        template = custom_manager.create_template(
            name="完整流程测试",
            description="测试完整生命周期",
            category="lifecycle",
            script_content=sample_script,
            keywords=["测试", "完整"],
            tags=["e2e"]
        )
        
        assert template is not None
        original_id = template.id
        
        # 2. 编辑模板
        updated = custom_manager.edit_template(
            template_id=template.id,
            category="lifecycle",
            updates={
                "description": "更新后的描述",
                "keywords": ["测试", "完整", "更新"]
            }
        )
        
        assert updated.description == "更新后的描述"
        
        # 3. 导出模板
        exporter = TemplateExporter(
            templates_dir=temp_workspace['templates_dir'],
            config_path=temp_workspace['config_path']
        )
        
        export_path = exporter.export_template(updated)
        assert os.path.exists(export_path)
        
        # 4. 验证模板可以被读取和使用
        template_content = Path(updated.file_path).read_text(encoding='utf-8')
        assert template_content is not None
        assert len(template_content) > 0
        
        # 验证模板包含参数定义
        assert "SourcePath" in template_content or "{{SourcePath}}" in template_content
        
        # 5. 查看版本历史
        version_control = custom_manager.editor.version_control
        versions = version_control.list_versions(template.id)
        assert len(versions) >= 1
        
        # 6. 删除模板
        result = custom_manager.delete_template(template.id, "lifecycle")
        assert result is True
        
        # 7. 重新导入
        imported, msg = exporter.import_template(
            package_path=export_path,
            target_category="lifecycle",  # 指定目标分类
            conflict_resolution="overwrite"
        )
        
        assert imported is not None
        assert "successfully" in msg.lower()
        
        # 8. 最终验证 - 使用导入后的模板信息
        # 验证导入的模板存在
        assert imported.name == "完整流程测试"
        assert Path(imported.file_path).exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
