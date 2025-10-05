"""File-based storage implementations"""

import os
import json
import pickle
import shutil
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import hashlib
import uuid

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.interfaces import (
    ModelStorageInterface, HistoryStorageInterface, 
    PreferencesStorageInterface, CacheStorageInterface
)
from context.models import HistoryEntry, UserPreferences


class FileModelStorage(ModelStorageInterface):
    """File-based AI model storage"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.models_dir = self.storage_dir / "models"
        self.metadata_file = self.storage_dir / "model_metadata.json"
        self._metadata_cache = {}
    
    def initialize(self) -> None:
        """Initialize storage directories"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self._load_metadata()
    
    def close(self) -> None:
        """Save metadata and cleanup"""
        self._save_metadata()
    
    def _load_metadata(self) -> None:
        """Load model metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self._metadata_cache = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load model metadata: {e}")
                self._metadata_cache = {}
        else:
            self._metadata_cache = {}
    
    def _save_metadata(self) -> None:
        """Save model metadata to file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata_cache, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save model metadata: {e}")
    
    def store_model(self, model_name: str, model_data: bytes, metadata: Dict[str, Any]) -> str:
        """Store AI model data and return storage path"""
        model_path = self.models_dir / f"{model_name}.model"
        
        # Write model data
        with open(model_path, 'wb') as f:
            f.write(model_data)
        
        # Update metadata
        self._metadata_cache[model_name] = {
            **metadata,
            'stored_at': datetime.now().isoformat(),
            'file_path': str(model_path),
            'file_size': len(model_data),
            'checksum': hashlib.sha256(model_data).hexdigest()
        }
        
        self._save_metadata()
        return str(model_path)
    
    def load_model(self, model_name: str) -> Optional[bytes]:
        """Load AI model data"""
        model_path = self.models_dir / f"{model_name}.model"
        
        if not model_path.exists():
            return None
        
        try:
            with open(model_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return None
    
    def get_model_metadata(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        return self._metadata_cache.get(model_name)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all stored models with metadata"""
        models = []
        for name, metadata in self._metadata_cache.items():
            models.append({
                'name': name,
                **metadata
            })
        return models
    
    def delete_model(self, model_name: str) -> bool:
        """Delete stored model"""
        model_path = self.models_dir / f"{model_name}.model"
        
        try:
            if model_path.exists():
                model_path.unlink()
            
            if model_name in self._metadata_cache:
                del self._metadata_cache[model_name]
                self._save_metadata()
            
            return True
        except Exception as e:
            print(f"Error deleting model {model_name}: {e}")
            return False
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Get file system path to model"""
        model_path = self.models_dir / f"{model_name}.model"
        return str(model_path) if model_path.exists() else None
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of model storage"""
        if backup_path is None:
            backup_path = str(self.storage_dir.parent / f"models_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy models directory
        if self.models_dir.exists():
            shutil.copytree(self.models_dir, backup_dir / "models", dirs_exist_ok=True)
        
        # Copy metadata
        if self.metadata_file.exists():
            shutil.copy2(self.metadata_file, backup_dir / "model_metadata.json")
        
        return str(backup_dir)
    
    def restore(self, backup_path: str) -> None:
        """Restore model storage from backup"""
        backup_dir = Path(backup_path)
        
        if not backup_dir.exists():
            raise ValueError(f"Backup directory does not exist: {backup_path}")
        
        # Restore models
        backup_models_dir = backup_dir / "models"
        if backup_models_dir.exists():
            if self.models_dir.exists():
                shutil.rmtree(self.models_dir)
            shutil.copytree(backup_models_dir, self.models_dir)
        
        # Restore metadata
        backup_metadata_file = backup_dir / "model_metadata.json"
        if backup_metadata_file.exists():
            shutil.copy2(backup_metadata_file, self.metadata_file)
            self._load_metadata()
    
    def migrate(self, from_version: str, to_version: str) -> None:
        """Migrate model storage between versions"""
        # For now, no migration needed
        pass


class SQLiteHistoryStorage(HistoryStorageInterface):
    """SQLite-based command history storage"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.db_path = self.storage_dir / "history.db"
        self.connection = None
    
    def initialize(self) -> None:
        """Initialize SQLite database"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS history_entries (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                natural_language_input TEXT,
                execution_result TEXT,
                context_snapshot TEXT,
                user_feedback TEXT,
                success_rating REAL,
                entry_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON history_entries(session_id)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON history_entries(timestamp)')
        self.connection.execute('CREATE INDEX IF NOT EXISTS idx_entry_id ON history_entries(entry_id)')
        
        self.connection.commit()
    
    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def add_entry(self, entry: HistoryEntry) -> str:
        """Add history entry and return entry ID"""
        entry_id = str(uuid.uuid4())
        
        self.connection.execute('''
            INSERT INTO history_entries 
            (id, session_id, timestamp, command, natural_language_input, 
             execution_result, context_snapshot, user_feedback, success_rating, entry_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry_id,
            entry.session_id,
            entry.timestamp.isoformat(),
            entry.command,
            entry.natural_language_input,
            json.dumps(entry.execution_result.__dict__ if entry.execution_result else None),
            json.dumps(entry.context_snapshot),
            entry.user_feedback,
            entry.success_rating,
            entry.entry_id
        ))
        
        self.connection.commit()
        return entry_id
    
    def get_entry(self, entry_id: str) -> Optional[HistoryEntry]:
        """Get history entry by ID"""
        cursor = self.connection.execute(
            'SELECT * FROM history_entries WHERE id = ?', (entry_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_entry(row)
    
    def get_entries(self, 
                   limit: Optional[int] = None,
                   offset: int = 0,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   session_id: Optional[str] = None,
                   command_pattern: Optional[str] = None) -> List[HistoryEntry]:
        """Get history entries with filtering"""
        query = 'SELECT * FROM history_entries WHERE 1=1'
        params = []
        
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time.isoformat())
        
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time.isoformat())
        
        if session_id:
            query += ' AND session_id = ?'
            params.append(session_id)
        
        if command_pattern:
            query += ' AND (command LIKE ? OR natural_language_input LIKE ?)'
            params.extend([f'%{command_pattern}%', f'%{command_pattern}%'])
        
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT ? OFFSET ?'
            params.extend([limit, offset])
        
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_entry(row) for row in rows]
    
    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update history entry"""
        if not updates:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ['command', 'natural_language_input', 'user_feedback', 'success_rating']:
                set_clauses.append(f'{key} = ?')
                params.append(value)
            elif key == 'execution_result':
                set_clauses.append('execution_result = ?')
                params.append(json.dumps(value.__dict__ if value else None))
            elif key == 'context_snapshot':
                set_clauses.append('context_snapshot = ?')
                params.append(json.dumps(value))
        
        if not set_clauses:
            return False
        
        params.append(entry_id)
        query = f'UPDATE history_entries SET {", ".join(set_clauses)} WHERE id = ?'
        
        cursor = self.connection.execute(query, params)
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete history entry"""
        cursor = self.connection.execute('DELETE FROM history_entries WHERE id = ?', (entry_id,))
        self.connection.commit()
        return cursor.rowcount > 0
    
    def delete_entries_before(self, cutoff_time: datetime) -> int:
        """Delete entries older than cutoff time"""
        cursor = self.connection.execute(
            'DELETE FROM history_entries WHERE timestamp < ?', 
            (cutoff_time.isoformat(),)
        )
        self.connection.commit()
        return cursor.rowcount
    
    def get_entry_count(self) -> int:
        """Get total number of history entries"""
        cursor = self.connection.execute('SELECT COUNT(*) FROM history_entries')
        return cursor.fetchone()[0]
    
    def search_entries(self, query: str, limit: Optional[int] = None) -> List[HistoryEntry]:
        """Search history entries by text"""
        sql_query = '''
            SELECT * FROM history_entries 
            WHERE command LIKE ? OR natural_language_input LIKE ?
            ORDER BY timestamp DESC
        '''
        
        params = [f'%{query}%', f'%{query}%']
        
        if limit:
            sql_query += ' LIMIT ?'
            params.append(limit)
        
        cursor = self.connection.execute(sql_query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_entry(row) for row in rows]
    
    def _row_to_entry(self, row) -> HistoryEntry:
        """Convert database row to HistoryEntry"""
        from interfaces.base import ExecutionResult
        
        execution_result = None
        if row['execution_result']:
            try:
                result_data = json.loads(row['execution_result'])
                if result_data:
                    execution_result = ExecutionResult(**result_data)
            except Exception:
                pass
        
        context_snapshot = {}
        if row['context_snapshot']:
            try:
                context_snapshot = json.loads(row['context_snapshot'])
            except Exception:
                pass
        
        return HistoryEntry(
            session_id=row['session_id'],
            command=row['command'],
            natural_language_input=row['natural_language_input'],
            execution_result=execution_result,
            timestamp=datetime.fromisoformat(row['timestamp']),
            context_snapshot=context_snapshot,
            user_feedback=row['user_feedback'],
            success_rating=row['success_rating'],
            entry_id=row['entry_id'] or row['id']
        )
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of history database"""
        if backup_path is None:
            backup_path = str(self.storage_dir.parent / f"history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(self.db_path, backup_file)
        return str(backup_file)
    
    def restore(self, backup_path: str) -> None:
        """Restore history database from backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise ValueError(f"Backup file does not exist: {backup_path}")
        
        # Close current connection
        if self.connection:
            self.connection.close()
        
        # Replace database file
        shutil.copy2(backup_file, self.db_path)
        
        # Reconnect
        self.initialize()
    
    def migrate(self, from_version: str, to_version: str) -> None:
        """Migrate history database between versions"""
        # For now, no migration needed
        pass


class JSONPreferencesStorage(PreferencesStorageInterface):
    """JSON-based user preferences storage"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.preferences_file = self.storage_dir / "user_preferences.json"
        self._preferences_cache = None
    
    def initialize(self) -> None:
        """Initialize preferences storage"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_preferences()
    
    def close(self) -> None:
        """Save preferences and cleanup"""
        self._save_preferences()
    
    def _load_preferences(self) -> None:
        """Load preferences from file"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._preferences_cache = UserPreferences(**data)
            except Exception as e:
                print(f"Warning: Failed to load preferences: {e}")
                self._preferences_cache = UserPreferences(session_id="default")
        else:
            self._preferences_cache = UserPreferences(session_id="default")
    
    def _save_preferences(self) -> None:
        """Save preferences to file"""
        if self._preferences_cache is None:
            return
        
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self._preferences_cache.__dict__, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save preferences: {e}")
    
    def save_preferences(self, preferences: UserPreferences) -> None:
        """Save user preferences"""
        self._preferences_cache = preferences
        self._save_preferences()
    
    def load_preferences(self) -> Optional[UserPreferences]:
        """Load user preferences"""
        if self._preferences_cache is None:
            self._load_preferences()
        return self._preferences_cache
    
    def update_preference(self, key: str, value: Any) -> None:
        """Update specific preference"""
        if self._preferences_cache is None:
            self._load_preferences()
        
        if hasattr(self._preferences_cache, key):
            setattr(self._preferences_cache, key, value)
            self._save_preferences()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get specific preference value"""
        if self._preferences_cache is None:
            self._load_preferences()
        
        return getattr(self._preferences_cache, key, default)
    
    def delete_preference(self, key: str) -> bool:
        """Delete specific preference"""
        if self._preferences_cache is None:
            self._load_preferences()
        
        if hasattr(self._preferences_cache, key):
            delattr(self._preferences_cache, key)
            self._save_preferences()
            return True
        return False
    
    def reset_preferences(self) -> None:
        """Reset preferences to defaults"""
        self._preferences_cache = UserPreferences(session_id="default")
        self._save_preferences()
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of preferences"""
        if backup_path is None:
            backup_path = str(self.storage_dir.parent / f"preferences_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.preferences_file.exists():
            shutil.copy2(self.preferences_file, backup_file)
        
        return str(backup_file)
    
    def restore(self, backup_path: str) -> None:
        """Restore preferences from backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise ValueError(f"Backup file does not exist: {backup_path}")
        
        shutil.copy2(backup_file, self.preferences_file)
        self._load_preferences()
    
    def migrate(self, from_version: str, to_version: str) -> None:
        """Migrate preferences between versions"""
        # For now, no migration needed
        pass


class FileCacheStorage(CacheStorageInterface):
    """File-based cache storage with TTL support"""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = Path(storage_dir)
        self.cache_dir = self.storage_dir / "cache"
        self.metadata_file = self.storage_dir / "cache_metadata.json"
        self._metadata_cache = {}
    
    def initialize(self) -> None:
        """Initialize cache storage"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_metadata()
        self.cleanup_expired()
    
    def close(self) -> None:
        """Save metadata and cleanup"""
        self._save_metadata()
    
    def _load_metadata(self) -> None:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self._metadata_cache = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load cache metadata: {e}")
                self._metadata_cache = {}
        else:
            self._metadata_cache = {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata_cache, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save cache metadata: {e}")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key"""
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with optional TTL in seconds"""
        cache_path = self._get_cache_path(key)
        
        # Serialize value
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"Warning: Failed to cache value for key {key}: {e}")
            return
        
        # Update metadata
        expires_at = None
        if ttl is not None:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        self._metadata_cache[key] = {
            'file_path': str(cache_path),
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'size': cache_path.stat().st_size
        }
        
        self._save_metadata()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        if not self.exists(key):
            return default
        
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Failed to load cached value for key {key}: {e}")
            # Clean up corrupted cache entry
            self.delete(key)
            return default
    
    def delete(self, key: str) -> bool:
        """Delete cache entry"""
        cache_path = self._get_cache_path(key)
        
        # Check if key exists
        if key not in self._metadata_cache and not cache_path.exists():
            return False
        
        try:
            if cache_path.exists():
                cache_path.unlink()
            
            if key in self._metadata_cache:
                del self._metadata_cache[key]
                self._save_metadata()
            
            return True
        except Exception as e:
            print(f"Warning: Failed to delete cache entry {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if cache key exists and is not expired"""
        if key not in self._metadata_cache:
            return False
        
        metadata = self._metadata_cache[key]
        
        # Check expiration
        if metadata.get('expires_at'):
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if datetime.now() > expires_at:
                self.delete(key)
                return False
        
        # Check file exists
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            self.delete(key)
            return False
        
        return True
    
    def clear(self) -> None:
        """Clear all cache entries"""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            self._metadata_cache = {}
            self._save_metadata()
        except Exception as e:
            print(f"Warning: Failed to clear cache: {e}")
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        expired_keys = []
        now = datetime.now()
        
        for key, metadata in self._metadata_cache.items():
            if metadata.get('expires_at'):
                expires_at = datetime.fromisoformat(metadata['expires_at'])
                if now > expires_at:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def get_size(self) -> int:
        """Get cache size in bytes"""
        total_size = 0
        for metadata in self._metadata_cache.values():
            total_size += metadata.get('size', 0)
        return total_size
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create backup of cache storage"""
        if backup_path is None:
            backup_path = str(self.storage_dir.parent / f"cache_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy cache directory
        if self.cache_dir.exists():
            shutil.copytree(self.cache_dir, backup_dir / "cache", dirs_exist_ok=True)
        
        # Copy metadata
        if self.metadata_file.exists():
            shutil.copy2(self.metadata_file, backup_dir / "cache_metadata.json")
        
        return str(backup_dir)
    
    def restore(self, backup_path: str) -> None:
        """Restore cache storage from backup"""
        backup_dir = Path(backup_path)
        
        if not backup_dir.exists():
            raise ValueError(f"Backup directory does not exist: {backup_path}")
        
        # Restore cache
        backup_cache_dir = backup_dir / "cache"
        if backup_cache_dir.exists():
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
            shutil.copytree(backup_cache_dir, self.cache_dir)
        
        # Restore metadata
        backup_metadata_file = backup_dir / "cache_metadata.json"
        if backup_metadata_file.exists():
            shutil.copy2(backup_metadata_file, self.metadata_file)
            self._load_metadata()
    
    def migrate(self, from_version: str, to_version: str) -> None:
        """Migrate cache storage between versions"""
        # For cache, we can just clear it during migration
        self.clear()


class FileStorage:
    """Unified file-based storage implementation
    
    This class provides a unified interface to all storage components
    and manages their lifecycle and configuration.
    """
    
    def __init__(self, config):
        """Initialize unified file storage
        
        Args:
            config: Storage configuration object
        """
        self.config = config
        self.base_path = Path(config.base_path)
        
        # Initialize component storages
        self.model_storage = FileModelStorage(str(self.base_path / "models"))
        self.history_storage = SQLiteHistoryStorage(str(self.base_path / "history.db"))
        self.preferences_storage = JSONPreferencesStorage(str(self.base_path / "preferences"))
        self.cache_storage = FileCacheStorage(str(self.base_path / "cache"))
        
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all storage components"""
        if self._initialized:
            return
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize all components
        self.model_storage.initialize()
        self.history_storage.initialize()
        self.preferences_storage.initialize()
        self.cache_storage.initialize()
        
        self._initialized = True
    
    async def close(self) -> None:
        """Close all storage components"""
        if not self._initialized:
            return
        
        self.model_storage.close()
        self.history_storage.close()
        self.preferences_storage.close()
        self.cache_storage.close()
        
        self._initialized = False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on storage components"""
        health_status = {
            "status": "healthy",
            "components": {}
        }
        
        try:
            # Check if base directory is accessible
            if not self.base_path.exists():
                health_status["status"] = "unhealthy"
                health_status["components"]["base_path"] = {
                    "status": "error",
                    "message": "Base path does not exist"
                }
            else:
                health_status["components"]["base_path"] = {"status": "healthy"}
            
            # Check component health
            components = {
                "model_storage": self.model_storage,
                "history_storage": self.history_storage,
                "preferences_storage": self.preferences_storage,
                "cache_storage": self.cache_storage
            }
            
            for name, component in components.items():
                try:
                    # Basic health check - try to access the component
                    if hasattr(component, 'health_check'):
                        component_health = component.health_check()
                    else:
                        # Basic check - see if component is accessible
                        component_health = {"status": "healthy"}
                    
                    health_status["components"][name] = component_health
                except Exception as e:
                    health_status["status"] = "unhealthy"
                    health_status["components"][name] = {
                        "status": "error",
                        "message": str(e)
                    }
            
        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    # Delegate methods to appropriate storage components
    def save_command_history(self, session_id: str, command: str, result) -> None:
        """Save command to history"""
        return self.history_storage.save_command(session_id, command, result)
    
    def get_command_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve command history"""
        return self.history_storage.get_history(session_id, limit)
    
    def save_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> None:
        """Save user preferences"""
        return self.preferences_storage.save_preferences(session_id, preferences)
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Retrieve user preferences"""
        return self.preferences_storage.get_preferences(session_id)
    
    def save_configuration(self, config: Dict[str, Any]) -> None:
        """Save system configuration"""
        config_file = self.base_path / "system_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load system configuration"""
        config_file = self.base_path / "system_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    # Cache operations
    def cache_set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value"""
        return self.cache_storage.set(key, value, ttl)
    
    def cache_get(self, key: str, default: Any = None) -> Any:
        """Get cache value"""
        return self.cache_storage.get(key, default)
    
    def cache_delete(self, key: str) -> bool:
        """Delete cache entry"""
        return self.cache_storage.delete(key)
    
    def cache_exists(self, key: str) -> bool:
        """Check if cache key exists"""
        return self.cache_storage.exists(key)
    
    # Model operations
    def save_model(self, model_id: str, model_data: bytes, metadata: Dict[str, Any]) -> None:
        """Save AI model"""
        return self.model_storage.save_model(model_id, model_data, metadata)
    
    def load_model(self, model_id: str) -> Optional[bytes]:
        """Load AI model"""
        return self.model_storage.load_model(model_id)
    
    def get_model_metadata(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model metadata"""
        return self.model_storage.get_metadata(model_id)
    
    def list_models(self) -> List[str]:
        """List available models"""
        return self.model_storage.list_models()
    
    @property
    def is_initialized(self) -> bool:
        """Check if storage is initialized"""
        return self._initialized