"""
存储工厂测试
"""

import pytest
import tempfile
import shutil

from src.storage.factory import StorageFactory, StorageType
from src.storage.interfaces import StorageInterface
from src.storage.file_storage import FileStorage


@pytest.fixture
def temp_storage_dir():
    """创建临时存储目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def clear_factory_cache():
    """每个测试前清除工厂缓存"""
    StorageFactory.clear_cache()
    yield
    StorageFactory.clear_cache()


class TestStorageFactory:
    """测试存储工厂"""
    
    def test_create_file_storage(self, temp_storage_dir):
        """测试创建文件存储"""
        storage = StorageFactory.create_storage(
            storage_type="file",
            config={"base_path": temp_storage_dir}
        )
        
        assert isinstance(storage, FileStorage)
        assert isinstance(storage, StorageInterface)
    
    def test_create_file_storage_default_config(self):
        """测试使用默认配置创建文件存储"""
        storage = StorageFactory.create_storage(storage_type="file")
        
        assert isinstance(storage, FileStorage)
    
    def test_create_storage_with_enum(self, temp_storage_dir):
        """测试使用枚举类型创建存储"""
        storage = StorageFactory.create_storage(
            storage_type=StorageType.FILE.value,
            config={"base_path": temp_storage_dir}
        )
        
        assert isinstance(storage, FileStorage)
    
    def test_create_memory_storage_not_implemented(self):
        """测试创建内存存储（未实现）"""
        with pytest.raises(NotImplementedError):
            StorageFactory.create_storage(storage_type="memory")
    
    def test_create_database_storage_not_implemented(self):
        """测试创建数据库存储（未实现）"""
        with pytest.raises(NotImplementedError):
            StorageFactory.create_storage(storage_type="database")
    
    def test_create_invalid_storage_type(self):
        """测试创建无效的存储类型"""
        with pytest.raises(ValueError, match="不支持的存储类型"):
            StorageFactory.create_storage(storage_type="invalid_type")
    
    def test_get_default_storage(self):
        """测试获取默认存储"""
        storage = StorageFactory.get_default_storage()
        
        assert isinstance(storage, FileStorage)
        assert isinstance(storage, StorageInterface)
    
    def test_factory_caches_instances(self, temp_storage_dir):
        """测试工厂缓存实例"""
        config = {"base_path": temp_storage_dir}
        
        storage1 = StorageFactory.create_storage(storage_type="file", config=config)
        storage2 = StorageFactory.create_storage(storage_type="file", config=config)
        
        # 应该返回同一个实例
        assert storage1 is storage2
    
    def test_factory_different_configs_different_instances(self, temp_storage_dir):
        """测试不同配置创建不同实例"""
        temp_dir2 = tempfile.mkdtemp()
        
        try:
            storage1 = StorageFactory.create_storage(
                storage_type="file",
                config={"base_path": temp_storage_dir}
            )
            storage2 = StorageFactory.create_storage(
                storage_type="file",
                config={"base_path": temp_dir2}
            )
            
            # 应该是不同的实例
            assert storage1 is not storage2
        finally:
            shutil.rmtree(temp_dir2, ignore_errors=True)
    
    def test_clear_cache(self, temp_storage_dir):
        """测试清除缓存"""
        config = {"base_path": temp_storage_dir}
        
        storage1 = StorageFactory.create_storage(storage_type="file", config=config)
        
        # 清除缓存
        StorageFactory.clear_cache()
        
        storage2 = StorageFactory.create_storage(storage_type="file", config=config)
        
        # 清除缓存后应该创建新实例
        assert storage1 is not storage2


class TestStorageTypeEnum:
    """测试存储类型枚举"""
    
    def test_storage_type_values(self):
        """测试存储类型枚举值"""
        assert StorageType.FILE.value == "file"
        assert StorageType.MEMORY.value == "memory"
        assert StorageType.DATABASE.value == "database"
    
    def test_storage_type_members(self):
        """测试存储类型枚举成员"""
        types = [t.value for t in StorageType]
        
        assert "file" in types
        assert "memory" in types
        assert "database" in types
