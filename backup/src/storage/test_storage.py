"""Tests for storage system"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.file_storage import (
    FileModelStorage, SQLiteHistoryStorage, 
    JSONPreferencesStorage, FileCacheStorage
)
from storage.factory import StorageFactory, get_storage_manager, initialize_storage
from storage.interfaces import StorageManager
from context.models import HistoryEntry, UserPreferences, ExecutionResult
from config.models import StorageConfig


class TestFileModelStorage:
    """Test file-based model storage"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileModelStorage(self.temp_dir)
        self.storage.initialize()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.storage.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_store_and_load_model(self):
        """Test storing and loading model data"""
        model_name = "test_model"
        model_data = b"fake model data"
        metadata = {
            "type": "llama-cpp",
            "version": "1.0",
            "size": len(model_data)
        }
        
        # Store model
        path = self.storage.store_model(model_name, model_data, metadata)
        assert path is not None
        assert Path(path).exists()
        
        # Load model
        loaded_data = self.storage.load_model(model_name)
        assert loaded_data == model_data
        
        # Check metadata
        stored_metadata = self.storage.get_model_metadata(model_name)
        assert stored_metadata is not None
        assert stored_metadata["type"] == "llama-cpp"
        assert stored_metadata["version"] == "1.0"
        assert "stored_at" in stored_metadata
        assert "checksum" in stored_metadata
    
    def test_list_models(self):
        """Test listing stored models"""
        # Initially empty
        models = self.storage.list_models()
        assert len(models) == 0
        
        # Store some models
        self.storage.store_model("model1", b"data1", {"type": "llama"})
        self.storage.store_model("model2", b"data2", {"type": "ollama"})
        
        models = self.storage.list_models()
        assert len(models) == 2
        
        model_names = [m["name"] for m in models]
        assert "model1" in model_names
        assert "model2" in model_names
    
    def test_delete_model(self):
        """Test deleting stored model"""
        model_name = "test_model"
        self.storage.store_model(model_name, b"data", {"type": "test"})
        
        # Verify model exists
        assert self.storage.load_model(model_name) is not None
        
        # Delete model
        result = self.storage.delete_model(model_name)
        assert result is True
        
        # Verify model is gone
        assert self.storage.load_model(model_name) is None
        assert self.storage.get_model_metadata(model_name) is None
    
    def test_get_model_path(self):
        """Test getting model file path"""
        model_name = "test_model"
        self.storage.store_model(model_name, b"data", {"type": "test"})
        
        path = self.storage.get_model_path(model_name)
        assert path is not None
        assert Path(path).exists()
        
        # Non-existent model
        path = self.storage.get_model_path("nonexistent")
        assert path is None
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality"""
        # Store some data
        self.storage.store_model("model1", b"data1", {"type": "test"})
        self.storage.store_model("model2", b"data2", {"type": "test"})
        
        # Create backup
        backup_path = self.storage.backup()
        assert Path(backup_path).exists()
        
        # Delete original data
        self.storage.delete_model("model1")
        self.storage.delete_model("model2")
        assert len(self.storage.list_models()) == 0
        
        # Restore from backup
        self.storage.restore(backup_path)
        
        # Verify data is restored
        models = self.storage.list_models()
        assert len(models) == 2
        assert self.storage.load_model("model1") == b"data1"
        assert self.storage.load_model("model2") == b"data2"


class TestSQLiteHistoryStorage:
    """Test SQLite-based history storage"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SQLiteHistoryStorage(self.temp_dir)
        self.storage.initialize()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.storage.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_entry(self, session_id="test_session") -> HistoryEntry:
        """Create a test history entry"""
        from interfaces.base import ExecutionResult
        
        return HistoryEntry(
            session_id=session_id,
            command="Get-Process",
            natural_language_input="test command",
            execution_result=ExecutionResult(
                success=True,
                return_code=0,
                stdout="test output",
                stderr="",
                execution_time=1.0,
                platform="windows",
                sandbox_used=False
            ),
            timestamp=datetime.now(),
            context_snapshot={"test": "data"},
            user_feedback=None,
            success_rating=0.9
        )
    
    def test_add_and_get_entry(self):
        """Test adding and retrieving history entries"""
        entry = self._create_test_entry()
        
        # Add entry
        entry_id = self.storage.add_entry(entry)
        assert entry_id is not None
        
        # Get entry
        retrieved_entry = self.storage.get_entry(entry_id)
        assert retrieved_entry is not None
        assert retrieved_entry.session_id == entry.session_id
        assert retrieved_entry.natural_language_input == entry.natural_language_input
        assert retrieved_entry.command == entry.command
        assert retrieved_entry.success_rating == entry.success_rating
    
    def test_get_entries_with_filtering(self):
        """Test getting entries with various filters"""
        # Add multiple entries
        entry1 = self._create_test_entry("session1")
        entry2 = self._create_test_entry("session2")
        entry3 = self._create_test_entry("session1")
        
        self.storage.add_entry(entry1)
        self.storage.add_entry(entry2)
        self.storage.add_entry(entry3)
        
        # Get all entries
        all_entries = self.storage.get_entries()
        assert len(all_entries) == 3
        
        # Filter by session
        session1_entries = self.storage.get_entries(session_id="session1")
        assert len(session1_entries) == 2
        
        # Filter with limit
        limited_entries = self.storage.get_entries(limit=2)
        assert len(limited_entries) == 2
    
    def test_update_entry(self):
        """Test updating history entries"""
        entry = self._create_test_entry()
        entry_id = self.storage.add_entry(entry)
        
        # Update entry
        updates = {
            "natural_language_input": "updated command",
            "success_rating": 0.5
        }
        result = self.storage.update_entry(entry_id, updates)
        assert result is True
        
        # Verify update
        updated_entry = self.storage.get_entry(entry_id)
        assert updated_entry.natural_language_input == "updated command"
        assert updated_entry.success_rating == 0.5
    
    def test_delete_entry(self):
        """Test deleting history entries"""
        entry = self._create_test_entry()
        entry_id = self.storage.add_entry(entry)
        
        # Verify entry exists
        assert self.storage.get_entry(entry_id) is not None
        
        # Delete entry
        result = self.storage.delete_entry(entry_id)
        assert result is True
        
        # Verify entry is gone
        assert self.storage.get_entry(entry_id) is None
    
    def test_search_entries(self):
        """Test searching history entries"""
        entry1 = self._create_test_entry()
        entry1.natural_language_input = "list processes"
        entry1.command = "Get-Process"
        
        entry2 = self._create_test_entry()
        entry2.natural_language_input = "show services"
        entry2.command = "Get-Service"
        
        self.storage.add_entry(entry1)
        self.storage.add_entry(entry2)
        
        # Search for "process"
        results = self.storage.search_entries("process")
        assert len(results) == 1
        assert results[0].natural_language_input == "list processes"
        
        # Search for "Get-"
        results = self.storage.search_entries("Get-")
        assert len(results) == 2
    
    def test_entry_count(self):
        """Test getting entry count"""
        assert self.storage.get_entry_count() == 0
        
        self.storage.add_entry(self._create_test_entry())
        assert self.storage.get_entry_count() == 1
        
        self.storage.add_entry(self._create_test_entry())
        assert self.storage.get_entry_count() == 2
    
    def test_delete_entries_before(self):
        """Test deleting entries before a cutoff time"""
        # Add entries with different timestamps
        old_entry = self._create_test_entry()
        old_entry.timestamp = datetime.now() - timedelta(days=2)
        
        new_entry = self._create_test_entry()
        new_entry.timestamp = datetime.now()
        
        self.storage.add_entry(old_entry)
        self.storage.add_entry(new_entry)
        
        # Delete entries older than 1 day
        cutoff = datetime.now() - timedelta(days=1)
        deleted_count = self.storage.delete_entries_before(cutoff)
        
        assert deleted_count == 1
        assert self.storage.get_entry_count() == 1


class TestJSONPreferencesStorage:
    """Test JSON-based preferences storage"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONPreferencesStorage(self.temp_dir)
        self.storage.initialize()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.storage.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_preferences(self):
        """Test saving and loading preferences"""
        preferences = UserPreferences(session_id="test_session")
        preferences.preferred_output_format = "json"
        
        # Save preferences
        self.storage.save_preferences(preferences)
        
        # Load preferences
        loaded_preferences = self.storage.load_preferences()
        assert loaded_preferences is not None
        assert loaded_preferences.preferred_output_format == "json"
    
    def test_update_preference(self):
        """Test updating individual preferences"""
        # Set initial preferences
        preferences = UserPreferences(session_id="test_session")
        self.storage.save_preferences(preferences)
        
        # Update specific preference
        self.storage.update_preference("preferred_output_format", "table")
        
        # Verify update
        loaded_preferences = self.storage.load_preferences()
        assert loaded_preferences.preferred_output_format == "table"
    
    def test_get_preference(self):
        """Test getting individual preference values"""
        preferences = UserPreferences(session_id="test_session")
        preferences.preferred_output_format = "json"
        self.storage.save_preferences(preferences)
        
        # Get existing preference
        value = self.storage.get_preference("preferred_output_format")
        assert value == "json"
        
        # Get non-existent preference with default
        value = self.storage.get_preference("nonexistent", "default_value")
        assert value == "default_value"
    
    def test_reset_preferences(self):
        """Test resetting preferences to defaults"""
        # Set custom preferences
        preferences = UserPreferences(session_id="test_session")
        preferences.preferred_output_format = "custom"
        self.storage.save_preferences(preferences)
        
        # Reset to defaults
        self.storage.reset_preferences()
        
        # Verify reset
        loaded_preferences = self.storage.load_preferences()
        assert loaded_preferences.preferred_output_format == "table"  # Default value


class TestFileCacheStorage:
    """Test file-based cache storage"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileCacheStorage(self.temp_dir)
        self.storage.initialize()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.storage.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_set_and_get_cache(self):
        """Test setting and getting cache values"""
        key = "test_key"
        value = {"data": "test_value", "number": 42}
        
        # Set cache value
        self.storage.set(key, value)
        
        # Get cache value
        retrieved_value = self.storage.get(key)
        assert retrieved_value == value
        
        # Get non-existent key
        assert self.storage.get("nonexistent") is None
        assert self.storage.get("nonexistent", "default") == "default"
    
    def test_cache_with_ttl(self):
        """Test cache with TTL (time-to-live)"""
        key = "ttl_key"
        value = "ttl_value"
        
        # Set cache with 1 second TTL
        self.storage.set(key, value, ttl=1)
        
        # Should exist immediately
        assert self.storage.exists(key)
        assert self.storage.get(key) == value
        
        # Wait for expiration (simulate by manipulating metadata)
        import time
        time.sleep(1.1)
        
        # Should be expired
        assert not self.storage.exists(key)
        assert self.storage.get(key) is None
    
    def test_delete_cache(self):
        """Test deleting cache entries"""
        key = "delete_key"
        value = "delete_value"
        
        self.storage.set(key, value)
        assert self.storage.exists(key)
        
        # Delete cache entry
        result = self.storage.delete(key)
        assert result is True
        assert not self.storage.exists(key)
        
        # Delete non-existent key
        result = self.storage.delete("nonexistent")
        assert result is False
    
    def test_clear_cache(self):
        """Test clearing all cache entries"""
        # Set multiple cache entries
        self.storage.set("key1", "value1")
        self.storage.set("key2", "value2")
        self.storage.set("key3", "value3")
        
        # Clear all
        self.storage.clear()
        
        # Verify all entries are gone
        assert not self.storage.exists("key1")
        assert not self.storage.exists("key2")
        assert not self.storage.exists("key3")
    
    def test_cleanup_expired(self):
        """Test cleaning up expired entries"""
        # Set entries with different TTLs
        self.storage.set("short_ttl", "value1", ttl=1)
        self.storage.set("long_ttl", "value2", ttl=3600)
        self.storage.set("no_ttl", "value3")
        
        # Simulate expiration by manipulating metadata
        import time
        time.sleep(1.1)
        
        # Cleanup expired entries
        expired_count = self.storage.cleanup_expired()
        assert expired_count == 1
        
        # Verify only expired entry is gone
        assert not self.storage.exists("short_ttl")
        assert self.storage.exists("long_ttl")
        assert self.storage.exists("no_ttl")


class TestStorageFactory:
    """Test storage factory"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_storage_manager(self):
        """Test creating storage manager"""
        config = StorageConfig()
        config.data_directory = str(Path(self.temp_dir) / "data")
        config.cache_directory = str(Path(self.temp_dir) / "cache")
        
        manager = StorageFactory.create_storage_manager(config)
        
        assert isinstance(manager, StorageManager)
        assert manager.models is not None
        assert manager.history is not None
        assert manager.preferences is not None
        assert manager.cache is not None
    
    def test_create_individual_storages(self):
        """Test creating individual storage instances"""
        storage_dir = str(Path(self.temp_dir) / "storage")
        
        model_storage = StorageFactory.create_model_storage(storage_dir)
        assert isinstance(model_storage, FileModelStorage)
        
        history_storage = StorageFactory.create_history_storage(storage_dir)
        assert isinstance(history_storage, SQLiteHistoryStorage)
        
        preferences_storage = StorageFactory.create_preferences_storage(storage_dir)
        assert isinstance(preferences_storage, JSONPreferencesStorage)
        
        cache_storage = StorageFactory.create_cache_storage(storage_dir)
        assert isinstance(cache_storage, FileCacheStorage)


class TestStorageManager:
    """Test storage manager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        config = StorageConfig()
        config.data_directory = str(Path(self.temp_dir) / "data")
        config.cache_directory = str(Path(self.temp_dir) / "cache")
        
        self.manager = StorageFactory.create_storage_manager(config)
        self.manager.initialize_all()
    
    def teardown_method(self):
        """Clean up test environment"""
        self.manager.close_all()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialize_and_close_all(self):
        """Test initializing and closing all storage backends"""
        # Should not raise any exceptions
        self.manager.initialize_all()
        self.manager.close_all()
    
    def test_backup_and_restore_all(self):
        """Test backing up and restoring all storage data"""
        # Add some test data
        self.manager.models.store_model("test_model", b"data", {"type": "test"})
        
        entry = HistoryEntry(
            session_id="test",
            command="test",
            natural_language_input="test",
            execution_result=None,
            timestamp=datetime.now(),
            context_snapshot={},
            user_feedback=None,
            success_rating=1.0
        )
        self.manager.history.add_entry(entry)
        
        preferences = UserPreferences(session_id="test")
        preferences.preferred_output_format = "json"
        self.manager.preferences.save_preferences(preferences)
        
        self.manager.cache.set("test_key", "test_value")
        
        # Create backup
        backup_dir = str(Path(self.temp_dir) / "backup")
        backup_paths = self.manager.backup_all(backup_dir)
        
        assert "models" in backup_paths
        assert "history" in backup_paths
        assert "preferences" in backup_paths
        assert "cache" in backup_paths
        
        # Clear data
        self.manager.models.delete_model("test_model")
        self.manager.cache.clear()
        
        # Restore from backup
        self.manager.restore_all(backup_paths)
        
        # Verify data is restored
        assert self.manager.models.load_model("test_model") == b"data"
        assert self.manager.cache.get("test_key") == "test_value"


class TestGlobalStorageManager:
    """Test global storage manager functions"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Reset global storage manager
        from storage.factory import close_storage
        close_storage()
    
    def teardown_method(self):
        """Clean up test environment"""
        from storage.factory import close_storage
        close_storage()
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_storage_manager(self):
        """Test getting global storage manager"""
        config = StorageConfig()
        config.data_directory = str(Path(self.temp_dir) / "data")
        config.cache_directory = str(Path(self.temp_dir) / "cache")
        
        manager = get_storage_manager(config)
        assert isinstance(manager, StorageManager)
        
        # Should return same instance on subsequent calls
        manager2 = get_storage_manager()
        assert manager is manager2
    
    def test_initialize_storage(self):
        """Test initializing global storage"""
        config = StorageConfig()
        config.data_directory = str(Path(self.temp_dir) / "data")
        config.cache_directory = str(Path(self.temp_dir) / "cache")
        
        manager = initialize_storage(config)
        assert isinstance(manager, StorageManager)
        
        # Should be accessible via get_storage_manager
        manager2 = get_storage_manager()
        assert manager is manager2


if __name__ == "__main__":
    pytest.main([__file__])