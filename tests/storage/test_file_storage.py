"""
文件存储测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from src.storage.file_storage import FileStorage


@pytest.fixture
def temp_storage_dir():
    """创建临时存储目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def file_storage(temp_storage_dir):
    """创建文件存储实例"""
    return FileStorage(base_path=temp_storage_dir)


class TestFileStorageInitialization:
    """测试文件存储初始化"""
    
    def test_init_creates_directories(self, temp_storage_dir):
        """测试初始化创建必要的目录"""
        storage = FileStorage(base_path=temp_storage_dir)
        
        assert storage.base_path.exists()
        assert storage.cache_dir.exists()
    
    def test_init_with_default_path(self):
        """测试使用默认路径初始化"""
        storage = FileStorage()
        
        assert storage.base_path.exists()
        assert "ai-powershell" in str(storage.base_path)


class TestHistoryOperations:
    """测试历史记录操作"""
    
    def test_save_history(self, file_storage):
        """测试保存历史记录"""
        entry = {
            "input": "显示当前时间",
            "command": "Get-Date",
            "success": True
        }
        
        result = file_storage.save_history(entry)
        
        assert result is True
        assert file_storage.history_file.exists()
    
    def test_load_history(self, file_storage):
        """测试加载历史记录"""
        # 保存多条记录
        entries = [
            {"input": "test1", "command": "cmd1", "success": True},
            {"input": "test2", "command": "cmd2", "success": True},
            {"input": "test3", "command": "cmd3", "success": False}
        ]
        
        for entry in entries:
            file_storage.save_history(entry)
        
        # 加载所有记录
        history = file_storage.load_history()
        
        assert len(history) == 3
        assert history[0]["input"] == "test1"
        assert history[2]["input"] == "test3"
    
    def test_load_history_with_limit(self, file_storage):
        """测试加载限制数量的历史记录"""
        # 保存5条记录
        for i in range(5):
            file_storage.save_history({
                "input": f"test{i}",
                "command": f"cmd{i}",
                "success": True
            })
        
        # 只加载最近的2条
        history = file_storage.load_history(limit=2)
        
        assert len(history) == 2
        assert history[0]["input"] == "test3"
        assert history[1]["input"] == "test4"
    
    def test_load_history_empty(self, file_storage):
        """测试加载空历史记录"""
        history = file_storage.load_history()
        
        assert history == []
    
    def test_clear_history(self, file_storage):
        """测试清除历史记录"""
        # 先保存一些记录
        file_storage.save_history({"input": "test", "command": "cmd", "success": True})
        
        # 清除
        result = file_storage.clear_history()
        
        assert result is True
        assert not file_storage.history_file.exists()
    
    def test_history_includes_timestamp(self, file_storage):
        """测试历史记录包含时间戳"""
        entry = {"input": "test", "command": "cmd", "success": True}
        
        file_storage.save_history(entry)
        history = file_storage.load_history()
        
        assert "timestamp" in history[0]
        # 验证时间戳格式
        timestamp = datetime.fromisoformat(history[0]["timestamp"])
        assert isinstance(timestamp, datetime)


class TestConfigOperations:
    """测试配置操作"""
    
    def test_save_config(self, file_storage):
        """测试保存配置"""
        config = {
            "ai": {
                "provider": "local",
                "model": "llama"
            },
            "security": {
                "sandbox_enabled": False
            }
        }
        
        result = file_storage.save_config(config)
        
        assert result is True
        assert file_storage.config_file.exists()
    
    def test_load_config(self, file_storage):
        """测试加载配置"""
        config = {
            "ai": {"provider": "local"},
            "security": {"sandbox_enabled": True}
        }
        
        file_storage.save_config(config)
        loaded_config = file_storage.load_config()
        
        assert loaded_config is not None
        assert loaded_config["ai"]["provider"] == "local"
        assert loaded_config["security"]["sandbox_enabled"] is True
    
    def test_load_config_not_exists(self, file_storage):
        """测试加载不存在的配置"""
        config = file_storage.load_config()
        
        assert config is None


class TestCacheOperations:
    """测试缓存操作"""
    
    def test_save_cache(self, file_storage):
        """测试保存缓存"""
        result = file_storage.save_cache("test_key", {"data": "test_value"})
        
        assert result is True
        cache_file = file_storage.cache_dir / "test_key.json"
        assert cache_file.exists()
    
    def test_load_cache(self, file_storage):
        """测试加载缓存"""
        test_value = {"data": "test_value", "count": 42}
        
        file_storage.save_cache("test_key", test_value)
        loaded_value = file_storage.load_cache("test_key")
        
        assert loaded_value == test_value
    
    def test_load_cache_not_exists(self, file_storage):
        """测试加载不存在的缓存"""
        value = file_storage.load_cache("non_existent_key")
        
        assert value is None
    
    def test_cache_with_ttl(self, file_storage):
        """测试带过期时间的缓存"""
        # 保存一个1秒后过期的缓存
        file_storage.save_cache("test_key", "test_value", ttl=1)
        
        # 立即加载应该成功
        value = file_storage.load_cache("test_key")
        assert value == "test_value"
        
        # 等待过期（这里我们通过修改缓存文件来模拟）
        import json
        cache_file = file_storage.cache_dir / "test_key.json"
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # 设置为过去的时间
        past_time = datetime.now() - timedelta(seconds=10)
        cache_data["expire_at"] = past_time.isoformat()
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f)
        
        # 再次加载应该返回 None
        value = file_storage.load_cache("test_key")
        assert value is None
        assert not cache_file.exists()  # 过期缓存应该被删除
    
    def test_clear_cache(self, file_storage):
        """测试清除所有缓存"""
        # 保存多个缓存
        file_storage.save_cache("key1", "value1")
        file_storage.save_cache("key2", "value2")
        file_storage.save_cache("key3", "value3")
        
        # 清除
        result = file_storage.clear_cache()
        
        assert result is True
        cache_files = list(file_storage.cache_dir.glob("*.json"))
        assert len(cache_files) == 0


class TestStorageInfo:
    """测试存储信息"""
    
    def test_get_storage_info(self, file_storage):
        """测试获取存储信息"""
        # 添加一些数据
        file_storage.save_history({"input": "test", "command": "cmd", "success": True})
        file_storage.save_config({"test": "config"})
        file_storage.save_cache("key1", "value1")
        
        info = file_storage.get_storage_info()
        
        assert "base_path" in info
        assert "history_file" in info
        assert "config_file" in info
        assert "cache_dir" in info
        assert info["history_exists"] is True
        assert info["config_exists"] is True
        assert info["history_count"] == 1
        assert info["cache_count"] == 1
        assert info["total_size"] > 0
    
    def test_get_storage_info_empty(self, file_storage):
        """测试获取空存储的信息"""
        info = file_storage.get_storage_info()
        
        assert info["history_exists"] is False
        assert info["config_exists"] is False
        assert info["history_count"] == 0
        assert info["cache_count"] == 0
