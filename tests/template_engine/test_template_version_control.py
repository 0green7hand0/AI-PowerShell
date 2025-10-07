"""
模板版本控制测试
"""

import os
import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from src.template_engine.template_version_control import (
    TemplateVersionControl,
    TemplateVersion
)
from src.template_engine.exceptions import TemplateError, TemplateNotFoundError


@pytest.fixture
def temp_history_dir():
    """创建临时历史目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def version_control(temp_history_dir):
    """创建版本控制器实例"""
    return TemplateVersionControl(history_dir=temp_history_dir, max_versions=5)


@pytest.fixture
def sample_template_content():
    """示例模板内容"""
    return """
# 示例模板
param(
    [string]$Path = "{{PATH}}",
    [int]$Count = {{COUNT}}
)

Write-Host "Processing $Path with count $Count"
"""


@pytest.fixture
def sample_template_config():
    """示例模板配置"""
    return {
        "name": "示例模板",
        "description": "这是一个示例模板",
        "category": "custom",
        "keywords": ["test", "sample"],
        "parameters": {
            "PATH": {
                "type": "string",
                "description": "文件路径",
                "required": True
            },
            "COUNT": {
                "type": "integer",
                "description": "计数",
                "default": 10
            }
        }
    }


class TestTemplateVersion:
    """测试 TemplateVersion 数据类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        timestamp = datetime.now()
        version = TemplateVersion(
            template_id="test_template",
            version_number=1,
            timestamp=timestamp,
            content="test content",
            config={"key": "value"},
            change_description="Initial version"
        )
        
        data = version.to_dict()
        assert data['template_id'] == "test_template"
        assert data['version_number'] == 1
        assert data['timestamp'] == timestamp.isoformat()
        assert data['content'] == "test content"
        assert data['config'] == {"key": "value"}
        assert data['change_description'] == "Initial version"
    
    def test_from_dict(self):
        """测试从字典创建"""
        timestamp = datetime.now()
        data = {
            'template_id': "test_template",
            'version_number': 1,
            'timestamp': timestamp.isoformat(),
            'content': "test content",
            'config': {"key": "value"},
            'change_description': "Initial version"
        }
        
        version = TemplateVersion.from_dict(data)
        assert version.template_id == "test_template"
        assert version.version_number == 1
        assert version.timestamp == timestamp
        assert version.content == "test content"
        assert version.config == {"key": "value"}
        assert version.change_description == "Initial version"


class TestTemplateVersionControl:
    """测试 TemplateVersionControl 类"""
    
    def test_init(self, temp_history_dir):
        """测试初始化"""
        vc = TemplateVersionControl(history_dir=temp_history_dir, max_versions=10)
        assert vc.history_dir == Path(temp_history_dir)
        assert vc.max_versions == 10
        assert vc.history_dir.exists()
    
    def test_create_version(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试创建版本"""
        version = version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Initial version"
        )
        
        assert version.template_id == "test_template"
        assert version.version_number == 1
        assert version.content == sample_template_content
        assert version.config == sample_template_config
        assert version.change_description == "Initial version"
        assert isinstance(version.timestamp, datetime)
    
    def test_create_multiple_versions(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试创建多个版本"""
        # 创建第一个版本
        v1 = version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        assert v1.version_number == 1
        
        # 创建第二个版本
        v2 = version_control.create_version(
            template_id="test_template",
            content=sample_template_content + "\n# Updated",
            config=sample_template_config,
            change_description="Version 2"
        )
        assert v2.version_number == 2
        
        # 创建第三个版本
        v3 = version_control.create_version(
            template_id="test_template",
            content=sample_template_content + "\n# Updated again",
            config=sample_template_config,
            change_description="Version 3"
        )
        assert v3.version_number == 3
    
    def test_list_versions(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试列出版本"""
        # 创建多个版本
        for i in range(3):
            version_control.create_version(
                template_id="test_template",
                content=f"{sample_template_content}\n# Version {i+1}",
                config=sample_template_config,
                change_description=f"Version {i+1}"
            )
        
        # 列出版本
        versions = version_control.list_versions("test_template")
        assert len(versions) == 3
        
        # 验证按版本号降序排列
        assert versions[0].version_number == 3
        assert versions[1].version_number == 2
        assert versions[2].version_number == 1
    
    def test_list_versions_empty(self, version_control):
        """测试列出空版本列表"""
        versions = version_control.list_versions("nonexistent_template")
        assert len(versions) == 0
    
    def test_get_version(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试获取特定版本"""
        # 创建版本
        version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        
        version_control.create_version(
            template_id="test_template",
            content=sample_template_content + "\n# Updated",
            config=sample_template_config,
            change_description="Version 2"
        )
        
        # 获取版本1
        v1 = version_control.get_version("test_template", 1)
        assert v1 is not None
        assert v1.version_number == 1
        assert v1.change_description == "Version 1"
        
        # 获取版本2
        v2 = version_control.get_version("test_template", 2)
        assert v2 is not None
        assert v2.version_number == 2
        assert v2.change_description == "Version 2"
    
    def test_get_version_not_found(self, version_control):
        """测试获取不存在的版本"""
        version = version_control.get_version("test_template", 999)
        assert version is None
    
    def test_restore_version(
        self,
        version_control,
        sample_template_content,
        sample_template_config,
        temp_history_dir
    ):
        """测试恢复版本"""
        # 创建目标文件路径
        target_file = os.path.join(temp_history_dir, "test_template.ps1")
        
        # 创建初始版本
        v1_content = sample_template_content
        version_control.create_version(
            template_id="test_template",
            content=v1_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        
        # 创建第二个版本
        v2_content = sample_template_content + "\n# Updated"
        version_control.create_version(
            template_id="test_template",
            content=v2_content,
            config=sample_template_config,
            change_description="Version 2"
        )
        
        # 写入当前内容（版本2）
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(v2_content)
        
        # 恢复到版本1
        restored = version_control.restore_version(
            template_id="test_template",
            version_number=1,
            target_file=target_file
        )
        
        assert restored.version_number == 1
        
        # 验证文件内容已恢复
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content == v1_content
    
    def test_restore_version_not_found(
        self,
        version_control,
        temp_history_dir
    ):
        """测试恢复不存在的版本"""
        target_file = os.path.join(temp_history_dir, "test_template.ps1")
        
        with pytest.raises(TemplateNotFoundError):
            version_control.restore_version(
                template_id="test_template",
                version_number=999,
                target_file=target_file
            )
    
    def test_restore_creates_backup(
        self,
        version_control,
        sample_template_content,
        sample_template_config,
        temp_history_dir
    ):
        """测试恢复前创建备份"""
        target_file = os.path.join(temp_history_dir, "test_template.ps1")
        
        # 创建版本1
        version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        
        # 创建版本2
        v2_content = sample_template_content + "\n# Updated"
        version_control.create_version(
            template_id="test_template",
            content=v2_content,
            config=sample_template_config,
            change_description="Version 2"
        )
        
        # 写入当前内容
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(v2_content)
        
        # 恢复到版本1（应该创建当前版本的备份）
        version_control.restore_version(
            template_id="test_template",
            version_number=1,
            target_file=target_file
        )
        
        # 验证创建了备份（应该有3个版本：v1, v2, 和恢复前的备份）
        versions = version_control.list_versions("test_template")
        assert len(versions) == 3
    
    def test_cleanup_old_versions(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试清理旧版本"""
        # 创建10个版本（超过max_versions=5）
        for i in range(10):
            version_control.create_version(
                template_id="test_template",
                content=f"{sample_template_content}\n# Version {i+1}",
                config=sample_template_config,
                change_description=f"Version {i+1}"
            )
        
        # 验证只保留了最新的5个版本
        versions = version_control.list_versions("test_template")
        assert len(versions) == 5
        
        # 验证保留的是版本6-10
        version_numbers = [v.version_number for v in versions]
        assert version_numbers == [10, 9, 8, 7, 6]
    
    def test_cleanup_old_versions_manual(
        self,
        sample_template_content,
        sample_template_config,
        temp_history_dir
    ):
        """测试手动清理旧版本"""
        # 创建一个max_versions=3的版本控制器
        vc = TemplateVersionControl(history_dir=temp_history_dir, max_versions=3)
        
        # 创建5个版本
        for i in range(5):
            vc.create_version(
                template_id="test_template",
                content=f"{sample_template_content}\n# Version {i+1}",
                config=sample_template_config,
                change_description=f"Version {i+1}"
            )
        
        # 验证只保留了3个版本
        versions = vc.list_versions("test_template")
        assert len(versions) == 3
        assert versions[0].version_number == 5
        assert versions[1].version_number == 4
        assert versions[2].version_number == 3
    
    def test_delete_all_versions(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试删除所有版本"""
        # 创建多个版本
        for i in range(3):
            version_control.create_version(
                template_id="test_template",
                content=f"{sample_template_content}\n# Version {i+1}",
                config=sample_template_config,
                change_description=f"Version {i+1}"
            )
        
        # 验证版本存在
        versions = version_control.list_versions("test_template")
        assert len(versions) == 3
        
        # 删除所有版本
        result = version_control.delete_all_versions("test_template")
        assert result is True
        
        # 验证版本已删除
        versions = version_control.list_versions("test_template")
        assert len(versions) == 0
    
    def test_get_version_diff(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试版本差异比较"""
        # 创建版本1
        version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        
        # 创建版本2（内容不同）
        v2_content = sample_template_content + "\n# Updated"
        version_control.create_version(
            template_id="test_template",
            content=v2_content,
            config=sample_template_config,
            change_description="Version 2"
        )
        
        # 比较差异
        diff = version_control.get_version_diff("test_template", 1, 2)
        assert diff is not None
        assert diff['version1'] == 1
        assert diff['version2'] == 2
        assert diff['content_changed'] is True
        assert diff['config_changed'] is False
        assert 'timestamp1' in diff
        assert 'timestamp2' in diff
    
    def test_get_version_diff_not_found(self, version_control):
        """测试比较不存在的版本"""
        diff = version_control.get_version_diff("test_template", 1, 2)
        assert diff is None
    
    def test_version_persistence(
        self,
        version_control,
        sample_template_content,
        sample_template_config,
        temp_history_dir
    ):
        """测试版本持久化"""
        # 创建版本
        v1 = version_control.create_version(
            template_id="test_template",
            content=sample_template_content,
            config=sample_template_config,
            change_description="Version 1"
        )
        
        # 创建新的版本控制器实例（模拟重启）
        new_vc = TemplateVersionControl(history_dir=temp_history_dir)
        
        # 验证可以读取之前创建的版本
        versions = new_vc.list_versions("test_template")
        assert len(versions) == 1
        assert versions[0].version_number == v1.version_number
        assert versions[0].content == v1.content
        assert versions[0].config == v1.config
    
    def test_concurrent_version_creation(
        self,
        version_control,
        sample_template_content,
        sample_template_config
    ):
        """测试并发创建版本"""
        # 快速创建多个版本
        versions = []
        for i in range(5):
            v = version_control.create_version(
                template_id="test_template",
                content=f"{sample_template_content}\n# Version {i+1}",
                config=sample_template_config,
                change_description=f"Version {i+1}"
            )
            versions.append(v)
        
        # 验证版本号是连续的
        version_numbers = [v.version_number for v in versions]
        assert version_numbers == [1, 2, 3, 4, 5]
    
    def test_version_with_special_characters(
        self,
        version_control,
        sample_template_config
    ):
        """测试包含特殊字符的版本"""
        special_content = """
# 特殊字符测试
$path = "C:\\Users\\测试\\文件.txt"
Write-Host "中文内容 & 特殊符号 <>"
"""
        
        version = version_control.create_version(
            template_id="test_template",
            content=special_content,
            config=sample_template_config,
            change_description="包含特殊字符的版本"
        )
        
        # 验证可以正确保存和读取
        retrieved = version_control.get_version("test_template", version.version_number)
        assert retrieved is not None
        assert retrieved.content == special_content
        assert retrieved.change_description == "包含特殊字符的版本"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
