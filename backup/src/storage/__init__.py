"""Storage system for AI PowerShell Assistant"""

from .interfaces import (
    StorageInterface,
    ModelStorageInterface,
    HistoryStorageInterface,
    PreferencesStorageInterface,
    CacheStorageInterface,
    StorageManager
)

from .file_storage import (
    FileModelStorage,
    SQLiteHistoryStorage,
    JSONPreferencesStorage,
    FileCacheStorage
)

from .factory import (
    StorageFactory,
    get_storage_manager,
    initialize_storage,
    close_storage
)

from .migration import (
    MigrationManager,
    create_migration_manager
)

__all__ = [
    # Interfaces
    'StorageInterface',
    'ModelStorageInterface', 
    'HistoryStorageInterface',
    'PreferencesStorageInterface',
    'CacheStorageInterface',
    'StorageManager',
    
    # Implementations
    'FileModelStorage',
    'SQLiteHistoryStorage',
    'JSONPreferencesStorage',
    'FileCacheStorage',
    
    # Factory
    'StorageFactory',
    'get_storage_manager',
    'initialize_storage',
    'close_storage',
    
    # Migration
    'MigrationManager',
    'create_migration_manager'
]