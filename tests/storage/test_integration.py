"""
存储引擎集成测试

测试存储引擎各组件的协同工作。
"""

import pytest
import tempfile
import shutil

from src.storage.factory import StorageFactory
from src.storage.interfaces import StorageInterface


@pytest.fixture
def temp_storage_dir():
    """创建临时存储目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def clear_factory_cache():
    """每个测试前清除工厂缓存"""
    StorageFactory.clear_cache()
    yield
    StorageFactory.clear_cache()


class TestStorageIntegration:
    """测试存储引擎集成"""
    
    def test_complete_workflow(self, temp_storage_dir):
        """测试完整的存储工作流程"""
        # 1. 通过工厂创建存储
        storage = StorageFactory.create_storage(
            storage_type="file",
            config={"base_path": temp_storage_dir}
        )
        
        assert isinstance(storage, StorageInterface)
        
        # 2. 保存配置
        config = {
            "ai": {"provider": "local", "model": "llama"},
            "security": {"sandbox_enabled": False}
        }
        assert storage.save_config(config) is True
        
        # 3. 保存历史记录
        history_entries = [
            {"input": "显示当前时间", "command": "Get-Date", "success": True},
            {"input": "列出文件", "command": "Get-ChildItem", "success": True},
            {"input": "显示进程", "command": "Get-Process", "success": True}
        ]
        
        for entry in history_entries:
            assert storage.save_history(entry) is True
        
        # 4. 保存缓存
        cache_data = {
            "translation_cache": {"显示时间": "Get-Date"},
            "model_cache": {"last_used": "llama"}
        }
        
        for key, value in cache_data.items():
            assert storage.save_cache(key, value) is True
        
        # 5. 验证数据加载
        loaded_config = storage.load_config()
        assert loaded_config["ai"]["provider"] == "local"
        
        loaded_history = storage.load_history()
        assert len(loaded_history) == 3
        assert loaded_history[0]["input"] == "显示当前时间"
        
        translation_cache = storage.load_cache("translation_cache")
        assert translation_cache["显示时间"] == "Get-Date"
        
        # 6. 获取存储信息
        info = storage.get_storage_info()
        assert info["history_count"] == 3
        assert info["cache_count"] == 2
        assert info["config_exists"] is True
        assert info["total_size"] > 0
    
    def test_factory_returns_same_instance(self, temp_storage_dir):
        """测试工厂对相同配置返回相同实例"""
        config = {"base_path": temp_storage_dir}
        
        storage1 = StorageFactory.create_storage("file", config)
        storage2 = StorageFactory.create_storage("file", config)
        
        # 应该是同一个实例
        assert storage1 is storage2
        
        # 在一个实例上保存数据
        storage1.save_history({"input": "test", "command": "cmd", "success": True})
        
        # 在另一个实例上应该能读取
        history = storage2.load_history()
        assert len(history) == 1
    
    def test_storage_persistence(self, temp_storage_dir):
        """测试数据持久化"""
        config = {"base_path": temp_storage_dir}
        
        # 创建第一个存储实例并保存数据
        storage1 = StorageFactory.create_storage("file", config)
        storage1.save_history({"input": "test1", "command": "cmd1", "success": True})
        storage1.save_config({"test": "value"})
        storage1.save_cache("key1", "value1")
        
        # 清除工厂缓存
        StorageFactory.clear_cache()
        
        # 创建新的存储实例（使用相同路径）
        storage2 = StorageFactory.create_storage("file", config)
        
        # 应该能读取之前保存的数据
        history = storage2.load_history()
        assert len(history) == 1
        assert history[0]["input"] == "test1"
        
        loaded_config = storage2.load_config()
        assert loaded_config["test"] == "value"
        
        cached_value = storage2.load_cache("key1")
        assert cached_value == "value1"
    
    def test_multiple_storage_instances(self):
        """测试多个独立的存储实例"""
        temp_dir1 = tempfile.mkdtemp()
        temp_dir2 = tempfile.mkdtemp()
        
        try:
            # 创建两个不同的存储实例
            storage1 = StorageFactory.create_storage("file", {"base_path": temp_dir1})
            storage2 = StorageFactory.create_storage("file", {"base_path": temp_dir2})
            
            # 在不同实例上保存不同数据
            storage1.save_history({"input": "storage1", "command": "cmd1", "success": True})
            storage2.save_history({"input": "storage2", "command": "cmd2", "success": True})
            
            # 验证数据隔离
            history1 = storage1.load_history()
            history2 = storage2.load_history()
            
            assert len(history1) == 1
            assert len(history2) == 1
            assert history1[0]["input"] == "storage1"
            assert history2[0]["input"] == "storage2"
        finally:
            shutil.rmtree(temp_dir1, ignore_errors=True)
            shutil.rmtree(temp_dir2, ignore_errors=True)
    
    def test_default_storage(self):
        """测试默认存储"""
        storage = StorageFactory.get_default_storage()
        
        # 应该能正常使用
        assert storage.save_history({"input": "test", "command": "cmd", "success": True})
        
        history = storage.load_history()
        assert len(history) >= 1
        
        # 清理
        storage.clear_history()
