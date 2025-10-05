"""Storage factory for creating storage instances"""

from pathlib import Path
from typing import Optional

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.interfaces import StorageManager
from storage.file_storage import (
    FileModelStorage, SQLiteHistoryStorage, 
    JSONPreferencesStorage, FileCacheStorage
)
from config.models import StorageConfig


class StorageFactory:
    """Factory for creating storage instances"""
    
    @staticmethod
    def create_storage_manager(config: StorageConfig) -> StorageManager:
        """Create a complete storage manager with all storage backends"""
        
        # Ensure directories exist
        data_dir = Path(config.data_directory)
        cache_dir = Path(config.cache_directory)
        
        data_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create storage instances
        model_storage = FileModelStorage(str(data_dir))
        history_storage = SQLiteHistoryStorage(str(data_dir))
        preferences_storage = JSONPreferencesStorage(str(data_dir))
        cache_storage = FileCacheStorage(str(cache_dir))
        
        return StorageManager(
            model_storage=model_storage,
            history_storage=history_storage,
            preferences_storage=preferences_storage,
            cache_storage=cache_storage
        )
    
    @staticmethod
    def create_model_storage(storage_dir: str) -> FileModelStorage:
        """Create model storage instance"""
        return FileModelStorage(storage_dir)
    
    @staticmethod
    def create_history_storage(storage_dir: str) -> SQLiteHistoryStorage:
        """Create history storage instance"""
        return SQLiteHistoryStorage(storage_dir)
    
    @staticmethod
    def create_preferences_storage(storage_dir: str) -> JSONPreferencesStorage:
        """Create preferences storage instance"""
        return JSONPreferencesStorage(storage_dir)
    
    @staticmethod
    def create_cache_storage(storage_dir: str) -> FileCacheStorage:
        """Create cache storage instance"""
        return FileCacheStorage(storage_dir)


# Global storage manager instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager(config: Optional[StorageConfig] = None) -> StorageManager:
    """Get the global storage manager instance"""
    global _storage_manager
    
    if _storage_manager is None:
        if config is None:
            from config.manager import get_config
            config = get_config().storage
        
        _storage_manager = StorageFactory.create_storage_manager(config)
        _storage_manager.initialize_all()
    
    return _storage_manager


def initialize_storage(config: StorageConfig) -> StorageManager:
    """Initialize global storage with specific configuration"""
    global _storage_manager
    
    if _storage_manager is not None:
        _storage_manager.close_all()
    
    _storage_manager = StorageFactory.create_storage_manager(config)
    _storage_manager.initialize_all()
    
    return _storage_manager


def close_storage() -> None:
    """Close global storage manager"""
    global _storage_manager
    
    if _storage_manager is not None:
        _storage_manager.close_all()
        _storage_manager = None