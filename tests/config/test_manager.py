"""
配置管理器测试
"""

import os
import tempfile
import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from src.config.manager import ConfigManager
from src.config.models import AppConfig, AIConfig, SecurityConfig


class TestConfigManager:
    """测试配置管理器"""
    
    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "ai": {
                    "provider": "ollama",
                    "model_name": "llama2",
                    "temperature": 0.8
                },
                "security": {
                    "sandbox_enabled": True,
                    "whitelist_mode": "moderate"
                }
            }
            yaml.dump(config_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        
        # 清理
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_init(self):
        """测试初始化"""
        manager = ConfigManager()
        assert manager.config_path is None
        assert manager._config is None
        
        manager = ConfigManager(config_path="test.yaml")
        assert manager.config_path == "test.yaml"
    
    def test_load_config_from_file(self, temp_config_file):
        """测试从文件加载配置"""
        manager = ConfigManager()
        config = manager.load_config(temp_config_file)
        
        assert isinstance(config, AppConfig)
        assert config.ai.provider == "ollama"
        assert config.ai.model_name == "llama2"
        assert config.ai.temperature == 0.8
        assert config.security.sandbox_enabled is True
        assert config.security.whitelist_mode == "moderate"
    
    def test_load_config_file_not_found(self):
        """测试加载不存在的文件"""
        manager = ConfigManager()
        with pytest.raises(FileNotFoundError):
            manager.load_config("nonexistent.yaml")
    
    def test_load_config_invalid_yaml(self):
        """测试加载无效的 YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            with pytest.raises(yaml.YAMLError):
                manager.load_config(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_config_validation_error(self):
        """测试配置验证错误"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "ai": {
                    "provider": "invalid_provider"  # 无效的提供商
                }
            }
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            with pytest.raises(ValidationError):
                manager.load_config(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_config_empty_file(self):
        """测试加载空文件（使用默认配置）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            config = manager.load_config(temp_path)
            
            # 应该使用默认配置
            assert isinstance(config, AppConfig)
            assert config.ai.provider == "local"
        finally:
            os.unlink(temp_path)
    
    def test_get_config(self, temp_config_file):
        """测试获取配置"""
        manager = ConfigManager(config_path=temp_config_file)
        
        # 第一次调用会加载配置
        config1 = manager.get_config()
        assert isinstance(config1, AppConfig)
        
        # 第二次调用返回缓存的配置
        config2 = manager.get_config()
        assert config1 is config2
    
    def test_save_config(self, temp_dir):
        """测试保存配置"""
        config_path = os.path.join(temp_dir, "test_config.yaml")
        
        config = AppConfig(
            ai=AIConfig(provider="openai", model_name="gpt-4"),
            security=SecurityConfig(sandbox_enabled=True)
        )
        
        manager = ConfigManager()
        manager.save_config(config, config_path)
        
        # 验证文件已创建
        assert os.path.exists(config_path)
        
        # 验证内容
        with open(config_path, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['ai']['provider'] == "openai"
        assert saved_data['ai']['model_name'] == "gpt-4"
        assert saved_data['security']['sandbox_enabled'] is True
    
    def test_save_config_creates_directory(self, temp_dir):
        """测试保存配置时创建目录"""
        config_path = os.path.join(temp_dir, "subdir", "config.yaml")
        
        config = AppConfig()
        manager = ConfigManager()
        manager.save_config(config, config_path)
        
        assert os.path.exists(config_path)
    
    def test_update_config(self, temp_config_file):
        """测试更新配置"""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load_config()
        
        # 更新配置
        updates = {
            "ai": {
                "temperature": 0.9
            },
            "execution": {
                "timeout": 60
            }
        }
        
        updated_config = manager.update_config(updates)
        
        assert updated_config.ai.temperature == 0.9
        assert updated_config.execution.timeout == 60
        # 其他值应保持不变
        assert updated_config.ai.provider == "ollama"
    
    def test_reset_to_defaults(self, temp_config_file):
        """测试重置为默认配置"""
        manager = ConfigManager(config_path=temp_config_file)
        manager.load_config()
        
        # 重置
        default_config = manager.reset_to_defaults()
        
        assert default_config.ai.provider == "local"
        assert default_config.ai.model_name == "llama"
        assert default_config.security.sandbox_enabled is False
    
    def test_validate_config_valid(self):
        """测试验证有效配置"""
        manager = ConfigManager()
        
        config_data = {
            "ai": {
                "provider": "ollama",
                "temperature": 0.7
            }
        }
        
        is_valid, error = manager.validate_config(config_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_config_invalid(self):
        """测试验证无效配置"""
        manager = ConfigManager()
        
        config_data = {
            "ai": {
                "provider": "invalid_provider"
            }
        }
        
        is_valid, error = manager.validate_config(config_data)
        assert is_valid is False
        assert error is not None
    
    def test_create_default_config_file(self, temp_dir):
        """测试创建默认配置文件"""
        config_path = os.path.join(temp_dir, "default.yaml")
        
        ConfigManager.create_default_config_file(config_path)
        
        assert os.path.exists(config_path)
        
        # 验证可以加载
        manager = ConfigManager()
        config = manager.load_config(config_path)
        assert isinstance(config, AppConfig)
    
    def test_deep_update(self):
        """测试深度更新"""
        manager = ConfigManager()
        
        base = {
            "ai": {
                "provider": "local",
                "temperature": 0.7
            },
            "security": {
                "sandbox_enabled": False
            }
        }
        
        updates = {
            "ai": {
                "temperature": 0.9
            }
        }
        
        manager._deep_update(base, updates)
        
        # temperature 应该被更新
        assert base["ai"]["temperature"] == 0.9
        # provider 应该保持不变
        assert base["ai"]["provider"] == "local"
        # security 应该保持不变
        assert base["security"]["sandbox_enabled"] is False
    
    def test_load_from_default_paths(self, temp_dir):
        """测试从默认路径加载"""
        # 创建一个配置文件在默认路径之一
        config_path = os.path.join(temp_dir, "config.yaml")
        config_data = {
            "ai": {
                "provider": "ollama"  # 使用有效的提供商
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        # 修改默认路径以包含我们的测试路径
        manager = ConfigManager()
        manager._default_config_paths = [config_path]
        
        config = manager.load_config()
        assert config.ai.provider == "ollama"
    
    def test_load_from_default_paths_no_file(self):
        """测试从默认路径加载（无文件，使用默认配置）"""
        manager = ConfigManager()
        manager._default_config_paths = ["/nonexistent/path.yaml"]
        
        config = manager.load_config()
        
        # 应该返回默认配置
        assert isinstance(config, AppConfig)
        assert config.ai.provider == "local"
