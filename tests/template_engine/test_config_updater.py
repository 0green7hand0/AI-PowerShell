"""
配置文件更新器测试模块
"""

import os
import pytest
import tempfile
import shutil
import threading
import time
from pathlib import Path
import yaml

from src.template_engine.config_updater import ConfigUpdater
from src.template_engine.exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateConflictError
)


@pytest.fixture
def temp_config_dir():
    """创建临时配置目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config():
    """示例配置数据"""
    return {
        'templates': {
            'file_management': {
                'batch_rename': {
                    'name': '批量重命名文件',
                    'file': 'templates/file_management/batch_rename.ps1',
                    'description': '按规则批量重命名文件',
                    'keywords': ['重命名', 'rename'],
                    'parameters': {
                        'SOURCE_PATH': {
                            'type': 'string',
                            'default': '.',
                            'description': '源文件夹路径'
                        }
                    }
                }
            },
            'automation': {
                'backup_files': {
                    'name': '文件备份',
                    'file': 'templates/automation/backup_files.ps1',
                    'description': '自动备份文件',
                    'keywords': ['备份', 'backup']
                }
            }
        }
    }


@pytest.fixture
def config_updater(temp_config_dir, sample_config):
    """创建配置更新器实例"""
    config_path = Path(temp_config_dir) / "templates.yaml"
    
    # 创建配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f, allow_unicode=True)
    
    return ConfigUpdater(str(config_path))


class TestConfigUpdaterInit:
    """测试配置更新器初始化"""
    
    def test_init_with_existing_config(self, config_updater):
        """测试使用现有配置文件初始化"""
        assert config_updater.config_path.exists()
        assert config_updater.backup_dir.exists()
    
    def test_init_with_nonexistent_config(self, temp_config_dir):
        """测试使用不存在的配置文件初始化"""
        config_path = Path(temp_config_dir) / "nonexistent.yaml"
        
        with pytest.raises(TemplateError, match="配置文件不存在"):
            ConfigUpdater(str(config_path))


class TestAddTemplateConfig:
    """测试添加模板配置"""
    
    def test_add_new_template_to_existing_category(self, config_updater):
        """测试向现有分类添加新模板"""
        new_config = {
            'name': '新模板',
            'file': 'templates/custom/new_template.ps1',
            'description': '测试模板',
            'keywords': ['test']
        }
        
        result = config_updater.add_template_config(
            'new_template',
            'file_management',
            new_config
        )
        
        assert result is True
        
        # 验证配置已添加
        saved_config = config_updater.get_template_config(
            'new_template',
            'file_management'
        )
        assert saved_config == new_config
    
    def test_add_template_to_new_category(self, config_updater):
        """测试向新分类添加模板"""
        new_config = {
            'name': '自定义模板',
            'file': 'templates/custom/my_template.ps1',
            'description': '自定义测试模板'
        }
        
        result = config_updater.add_template_config(
            'my_template',
            'custom',
            new_config
        )
        
        assert result is True
        
        # 验证配置已添加
        saved_config = config_updater.get_template_config(
            'my_template',
            'custom'
        )
        assert saved_config == new_config
    
    def test_add_duplicate_template(self, config_updater):
        """测试添加重复的模板"""
        new_config = {
            'name': '重复模板',
            'file': 'templates/test.ps1'
        }
        
        with pytest.raises(TemplateConflictError, match="已存在"):
            config_updater.add_template_config(
                'batch_rename',
                'file_management',
                new_config
            )


class TestUpdateTemplateConfig:
    """测试更新模板配置"""
    
    def test_update_existing_template(self, config_updater):
        """测试更新现有模板"""
        updated_config = {
            'name': '批量重命名文件（更新）',
            'file': 'templates/file_management/batch_rename.ps1',
            'description': '更新后的描述',
            'keywords': ['重命名', 'rename', 'update']
        }
        
        result = config_updater.update_template_config(
            'batch_rename',
            'file_management',
            updated_config
        )
        
        assert result is True
        
        # 验证配置已更新
        saved_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        assert saved_config['name'] == '批量重命名文件（更新）'
        assert saved_config['description'] == '更新后的描述'
        assert 'update' in saved_config['keywords']
    
    def test_update_nonexistent_template(self, config_updater):
        """测试更新不存在的模板"""
        updated_config = {
            'name': '不存在的模板',
            'file': 'templates/test.ps1'
        }
        
        with pytest.raises(TemplateNotFoundError, match="不存在"):
            config_updater.update_template_config(
                'nonexistent',
                'file_management',
                updated_config
            )


class TestRemoveTemplateConfig:
    """测试移除模板配置"""
    
    def test_remove_existing_template(self, config_updater):
        """测试移除现有模板"""
        result = config_updater.remove_template_config(
            'batch_rename',
            'file_management'
        )
        
        assert result is True
        
        # 验证配置已移除
        saved_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        assert saved_config is None
    
    def test_remove_nonexistent_template(self, config_updater):
        """测试移除不存在的模板"""
        with pytest.raises(TemplateNotFoundError, match="不存在"):
            config_updater.remove_template_config(
                'nonexistent',
                'file_management'
            )


class TestBackupAndRestore:
    """测试备份和恢复功能"""
    
    def test_backup_config(self, config_updater):
        """测试创建配置备份"""
        backup_path = config_updater.backup_config()
        
        assert backup_path is not None
        assert Path(backup_path).exists()
        assert 'templates_' in backup_path
        assert backup_path.endswith('.yaml')
    
    def test_restore_config(self, config_updater):
        """测试从备份恢复配置"""
        # 创建备份
        backup_path = config_updater.backup_config()
        
        # 读取备份内容
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # 修改配置
        original_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        modified_config = original_config.copy()
        modified_config['name'] = '修改后的名称'
        config_updater.update_template_config(
            'batch_rename',
            'file_management',
            modified_config
        )
        
        # 验证修改已生效
        with open(config_updater.config_path, 'r', encoding='utf-8') as f:
            modified_content = f.read()
        assert '修改后的名称' in modified_content
        assert modified_content != backup_content
        
        # 恢复配置
        result = config_updater.restore_config(backup_path)
        assert result is True
        
        # 验证配置已恢复
        with open(config_updater.config_path, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        # 恢复后的内容应该和备份一致
        assert restored_content == backup_content
    
    def test_restore_from_nonexistent_backup(self, config_updater):
        """测试从不存在的备份恢复"""
        with pytest.raises(TemplateError, match="备份文件不存在"):
            config_updater.restore_config('nonexistent_backup.yaml')
    
    def test_restore_from_invalid_backup(self, config_updater, temp_config_dir):
        """测试从无效的备份文件恢复"""
        # 创建无效的备份文件
        invalid_backup = Path(temp_config_dir) / "invalid_backup.yaml"
        with open(invalid_backup, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(TemplateError, match="备份文件格式无效"):
            config_updater.restore_config(str(invalid_backup))


class TestBackupManagement:
    """测试备份管理功能"""
    
    def test_list_backups(self, config_updater):
        """测试列出备份文件"""
        # 清理现有备份
        existing_backups = config_updater.list_backups()
        for backup in existing_backups:
            try:
                Path(backup).unlink()
            except:
                pass
        
        # 创建备份
        backup1 = config_updater.backup_config()
        
        backups = config_updater.list_backups()
        
        assert len(backups) >= 1
        assert backup1 in backups
        assert all(Path(b).exists() for b in backups)
    
    def test_cleanup_old_backups(self, config_updater):
        """测试清理旧备份"""
        # 清理现有备份
        existing_backups = config_updater.list_backups()
        for backup in existing_backups:
            try:
                Path(backup).unlink()
            except:
                pass
        
        # 手动创建多个备份文件（避免时间戳问题）
        backup_dir = config_updater.backup_dir
        for i in range(5):
            backup_file = backup_dir / f"templates_2025010{i}_120000.yaml"
            shutil.copy2(config_updater.config_path, backup_file)
            # 设置不同的修改时间
            os.utime(backup_file, (time.time() - (5 - i) * 10, time.time() - (5 - i) * 10))
        
        # 验证创建了5个备份
        backups_before = config_updater.list_backups()
        assert len(backups_before) == 5, f"Expected 5 backups, got {len(backups_before)}"
        
        # 清理，只保留2个
        deleted_count = config_updater.cleanup_old_backups(keep_count=2)
        
        assert deleted_count == 3, f"Expected to delete 3 backups, deleted {deleted_count}"
        
        # 验证只剩2个备份
        backups = config_updater.list_backups()
        assert len(backups) == 2, f"Expected 2 backups remaining, got {len(backups)}"


class TestConcurrency:
    """测试并发访问安全性"""
    
    def test_concurrent_add_operations(self, config_updater):
        """测试并发添加操作"""
        results = []
        errors = []
        
        def add_template(index):
            try:
                config = {
                    'name': f'模板{index}',
                    'file': f'templates/test_{index}.ps1'
                }
                result = config_updater.add_template_config(
                    f'template_{index}',
                    'custom',
                    config
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程同时添加模板
        threads = []
        for i in range(10):
            thread = threading.Thread(target=add_template, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有操作都成功
        assert len(results) == 10
        assert all(results)
        assert len(errors) == 0
    
    def test_concurrent_update_operations(self, config_updater):
        """测试并发更新操作"""
        # 先添加一个模板
        config_updater.add_template_config(
            'test_template',
            'custom',
            {'name': '测试模板', 'file': 'test.ps1', 'counter': 0}
        )
        
        results = []
        
        def update_template(index):
            try:
                config = config_updater.get_template_config(
                    'test_template',
                    'custom'
                )
                config['counter'] = index
                config_updater.update_template_config(
                    'test_template',
                    'custom',
                    config
                )
                results.append(True)
            except Exception:
                results.append(False)
        
        # 创建多个线程同时更新模板
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_template, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有操作都成功（由于锁机制）
        assert all(results)
        
        # 验证最终配置是有效的
        final_config = config_updater.get_template_config(
            'test_template',
            'custom'
        )
        assert final_config is not None
        assert 'counter' in final_config


class TestMoveTemplateConfig:
    """测试移动模板配置"""
    
    def test_move_template_to_existing_category(self, config_updater):
        """测试移动模板到现有分类"""
        # 获取原始配置
        original_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        
        # 移动模板
        result = config_updater.move_template_config(
            'batch_rename',
            'file_management',
            'automation',
            original_config
        )
        
        assert result is True
        
        # 验证源位置不存在
        source_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        assert source_config is None
        
        # 验证目标位置存在
        target_config = config_updater.get_template_config(
            'batch_rename',
            'automation'
        )
        assert target_config is not None
        assert target_config['name'] == original_config['name']
    
    def test_move_template_to_new_category(self, config_updater):
        """测试移动模板到新分类"""
        original_config = config_updater.get_template_config(
            'backup_files',
            'automation'
        )
        
        # 移动到新分类
        result = config_updater.move_template_config(
            'backup_files',
            'automation',
            'new_category',
            original_config
        )
        
        assert result is True
        
        # 验证新分类已创建并包含模板
        target_config = config_updater.get_template_config(
            'backup_files',
            'new_category'
        )
        assert target_config is not None
    
    def test_move_nonexistent_template(self, config_updater):
        """测试移动不存在的模板"""
        config = {'name': 'Test', 'file': 'test.ps1'}
        
        with pytest.raises(TemplateNotFoundError, match="不存在"):
            config_updater.move_template_config(
                'nonexistent',
                'file_management',
                'automation',
                config
            )
    
    def test_move_template_to_existing_location(self, config_updater):
        """测试移动模板到已存在同名模板的位置"""
        # 先在目标位置添加一个同名模板
        config_updater.add_template_config(
            'batch_rename',
            'automation',
            {'name': 'Existing', 'file': 'existing.ps1'}
        )
        
        # 尝试移动应该失败
        original_config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        
        with pytest.raises(TemplateConflictError, match="已存在"):
            config_updater.move_template_config(
                'batch_rename',
                'file_management',
                'automation',
                original_config
            )


class TestGetTemplateConfig:
    """测试获取模板配置"""
    
    def test_get_existing_template(self, config_updater):
        """测试获取现有模板配置"""
        config = config_updater.get_template_config(
            'batch_rename',
            'file_management'
        )
        
        assert config is not None
        assert config['name'] == '批量重命名文件'
        assert 'parameters' in config
    
    def test_get_nonexistent_template(self, config_updater):
        """测试获取不存在的模板配置"""
        config = config_updater.get_template_config(
            'nonexistent',
            'file_management'
        )
        
        assert config is None


class TestErrorHandling:
    """测试错误处理"""
    
    def test_corrupted_config_file(self, config_updater):
        """测试损坏的配置文件"""
        # 损坏配置文件
        with open(config_updater.config_path, 'w') as f:
            f.write("invalid: yaml: [content")
        
        with pytest.raises(TemplateError, match="配置文件解析失败"):
            config_updater._load_config()
    
    def test_permission_error(self, config_updater):
        """测试权限错误（模拟）"""
        # 这个测试在某些系统上可能不适用
        # 可以通过模拟文件系统错误来测试
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
