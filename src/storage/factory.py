"""
存储工厂

提供统一的存储实例创建接口，支持不同的存储后端。
"""

from typing import Optional, Dict, Any
from enum import Enum

from .interfaces import StorageInterface
from .file_storage import FileStorage


class StorageType(Enum):
    """存储类型枚举"""
    FILE = "file"
    MEMORY = "memory"
    DATABASE = "database"


class StorageFactory:
    """存储工厂类"""
    
    _instances: Dict[str, StorageInterface] = {}
    
    @classmethod
    def create_storage(
        cls,
        storage_type: str = "file",
        config: Optional[Dict[str, Any]] = None
    ) -> StorageInterface:
        """
        创建存储实例
        
        Args:
            storage_type: 存储类型 ("file", "memory", "database")
            config: 存储配置
            
        Returns:
            StorageInterface: 存储实例
            
        Raises:
            ValueError: 不支持的存储类型
        """
        if config is None:
            config = {}
        
        # 创建缓存键
        cache_key = f"{storage_type}:{str(config)}"
        
        # 检查是否已有实例
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # 根据类型创建实例
        if storage_type == StorageType.FILE.value:
            instance = cls._create_file_storage(config)
        elif storage_type == StorageType.MEMORY.value:
            instance = cls._create_memory_storage(config)
        elif storage_type == StorageType.DATABASE.value:
            instance = cls._create_database_storage(config)
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")
        
        # 缓存实例
        cls._instances[cache_key] = instance
        
        return instance
    
    @classmethod
    def _create_file_storage(cls, config: Dict[str, Any]) -> FileStorage:
        """
        创建文件存储实例
        
        Args:
            config: 配置字典，可包含 base_path
            
        Returns:
            FileStorage: 文件存储实例
        """
        base_path = config.get("base_path")
        return FileStorage(base_path=base_path)
    
    @classmethod
    def _create_memory_storage(cls, config: Dict[str, Any]) -> StorageInterface:
        """
        创建内存存储实例（未实现）
        
        Args:
            config: 配置字典
            
        Returns:
            StorageInterface: 内存存储实例
            
        Raises:
            NotImplementedError: 内存存储尚未实现
        """
        raise NotImplementedError("内存存储尚未实现")
    
    @classmethod
    def _create_database_storage(cls, config: Dict[str, Any]) -> StorageInterface:
        """
        创建数据库存储实例（未实现）
        
        Args:
            config: 配置字典
            
        Returns:
            StorageInterface: 数据库存储实例
            
        Raises:
            NotImplementedError: 数据库存储尚未实现
        """
        raise NotImplementedError("数据库存储尚未实现")
    
    @classmethod
    def get_default_storage(cls) -> StorageInterface:
        """
        获取默认存储实例（文件存储）
        
        Returns:
            StorageInterface: 默认存储实例
        """
        return cls.create_storage(storage_type=StorageType.FILE.value)
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除所有缓存的存储实例"""
        cls._instances.clear()
