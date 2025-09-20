"""Storage interfaces for AI PowerShell Assistant"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from context.models import HistoryEntry, UserPreferences


class StorageInterface(ABC):
    """Base interface for all storage operations"""
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize storage backend"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close storage connections and cleanup"""
        pass
    
    @abstractmethod
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of storage data"""
        pass
    
    @abstractmethod
    def restore(self, backup_path: str) -> None:
        """Restore storage data from backup"""
        pass
    
    @abstractmethod
    def migrate(self, from_version: str, to_version: str) -> None:
        """Migrate data between versions"""
        pass


class ModelStorageInterface(StorageInterface):
    """Interface for AI model storage operations"""
    
    @abstractmethod
    def store_model(self, model_name: str, model_data: bytes, metadata: Dict[str, Any]) -> str:
        """Store AI model data and return storage path"""
        pass
    
    @abstractmethod
    def load_model(self, model_name: str) -> Optional[bytes]:
        """Load AI model data"""
        pass
    
    @abstractmethod
    def get_model_metadata(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """List all stored models with metadata"""
        pass
    
    @abstractmethod
    def delete_model(self, model_name: str) -> bool:
        """Delete stored model"""
        pass
    
    @abstractmethod
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get file system path to model"""
        pass


class HistoryStorageInterface(StorageInterface):
    """Interface for command history storage operations"""
    
    @abstractmethod
    def add_entry(self, entry: HistoryEntry) -> str:
        """Add history entry and return entry ID"""
        pass
    
    @abstractmethod
    def get_entry(self, entry_id: str) -> Optional[HistoryEntry]:
        """Get history entry by ID"""
        pass
    
    @abstractmethod
    def get_entries(self, 
                   limit: Optional[int] = None,
                   offset: int = 0,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   session_id: Optional[str] = None,
                   command_pattern: Optional[str] = None) -> List[HistoryEntry]:
        """Get history entries with filtering"""
        pass
    
    @abstractmethod
    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update history entry"""
        pass
    
    @abstractmethod
    def delete_entry(self, entry_id: str) -> bool:
        """Delete history entry"""
        pass
    
    @abstractmethod
    def delete_entries_before(self, cutoff_time: datetime) -> int:
        """Delete entries older than cutoff time"""
        pass
    
    @abstractmethod
    def get_entry_count(self) -> int:
        """Get total number of history entries"""
        pass
    
    @abstractmethod
    def search_entries(self, query: str, limit: Optional[int] = None) -> List[HistoryEntry]:
        """Search history entries by text"""
        pass


class PreferencesStorageInterface(StorageInterface):
    """Interface for user preferences storage operations"""
    
    @abstractmethod
    def save_preferences(self, preferences: UserPreferences) -> None:
        """Save user preferences"""
        pass
    
    @abstractmethod
    def load_preferences(self) -> Optional[UserPreferences]:
        """Load user preferences"""
        pass
    
    @abstractmethod
    def update_preference(self, key: str, value: Any) -> None:
        """Update specific preference"""
        pass
    
    @abstractmethod
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get specific preference value"""
        pass
    
    @abstractmethod
    def delete_preference(self, key: str) -> bool:
        """Delete specific preference"""
        pass
    
    @abstractmethod
    def reset_preferences(self) -> None:
        """Reset preferences to defaults"""
        pass


class CacheStorageInterface(StorageInterface):
    """Interface for cache storage operations"""
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with optional TTL in seconds"""
        pass
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if cache key exists"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries"""
        pass
    
    @abstractmethod
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        pass
    
    @abstractmethod
    def get_size(self) -> int:
        """Get cache size in bytes"""
        pass


class StorageManager:
    """Manages all storage interfaces"""
    
    def __init__(self, 
                 model_storage: ModelStorageInterface,
                 history_storage: HistoryStorageInterface,
                 preferences_storage: PreferencesStorageInterface,
                 cache_storage: CacheStorageInterface):
        self.models = model_storage
        self.history = history_storage
        self.preferences = preferences_storage
        self.cache = cache_storage
    
    def initialize_all(self) -> None:
        """Initialize all storage backends"""
        self.models.initialize()
        self.history.initialize()
        self.preferences.initialize()
        self.cache.initialize()
    
    def close_all(self) -> None:
        """Close all storage backends"""
        self.models.close()
        self.history.close()
        self.preferences.close()
        self.cache.close()
    
    def backup_all(self, backup_dir: str) -> Dict[str, str]:
        """Backup all storage data"""
        backup_paths = {}
        backup_paths['models'] = self.models.backup(f"{backup_dir}/models")
        backup_paths['history'] = self.history.backup(f"{backup_dir}/history")
        backup_paths['preferences'] = self.preferences.backup(f"{backup_dir}/preferences")
        backup_paths['cache'] = self.cache.backup(f"{backup_dir}/cache")
        return backup_paths
    
    def restore_all(self, backup_paths: Dict[str, str]) -> None:
        """Restore all storage data from backups"""
        if 'models' in backup_paths:
            self.models.restore(backup_paths['models'])
        if 'history' in backup_paths:
            self.history.restore(backup_paths['history'])
        if 'preferences' in backup_paths:
            self.preferences.restore(backup_paths['preferences'])
        if 'cache' in backup_paths:
            self.cache.restore(backup_paths['cache'])