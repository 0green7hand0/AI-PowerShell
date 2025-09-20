"""Data migration utilities for storage system"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.interfaces import StorageManager
from storage.factory import StorageFactory
from config.models import StorageConfig


class MigrationManager:
    """Manages data migrations between versions"""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager
        self.migration_history_file = Path("migration_history.json")
    
    def get_current_version(self) -> str:
        """Get current data version"""
        # For now, return a default version
        return "1.0.0"
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history"""
        if self.migration_history_file.exists():
            try:
                with open(self.migration_history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def record_migration(self, from_version: str, to_version: str, success: bool, details: str = "") -> None:
        """Record migration in history"""
        history = self.get_migration_history()
        
        migration_record = {
            "from_version": from_version,
            "to_version": to_version,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details
        }
        
        history.append(migration_record)
        
        try:
            with open(self.migration_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to record migration: {e}")
    
    def migrate_to_version(self, target_version: str) -> bool:
        """Migrate data to target version"""
        current_version = self.get_current_version()
        
        if current_version == target_version:
            print(f"Already at version {target_version}")
            return True
        
        print(f"Migrating from {current_version} to {target_version}")
        
        try:
            # Create backup before migration
            backup_path = self.create_backup(f"pre_migration_{target_version}")
            print(f"Created backup at: {backup_path}")
            
            # Perform migration
            success = self._perform_migration(current_version, target_version)
            
            if success:
                self.record_migration(current_version, target_version, True, "Migration completed successfully")
                print(f"Migration to {target_version} completed successfully")
            else:
                self.record_migration(current_version, target_version, False, "Migration failed")
                print(f"Migration to {target_version} failed")
                
                # Restore from backup on failure
                print("Restoring from backup...")
                self.restore_backup(backup_path)
            
            return success
            
        except Exception as e:
            error_msg = f"Migration failed with error: {e}"
            print(error_msg)
            self.record_migration(current_version, target_version, False, error_msg)
            return False
    
    def _perform_migration(self, from_version: str, to_version: str) -> bool:
        """Perform the actual migration"""
        # Define migration paths
        migration_map = {
            ("1.0.0", "1.1.0"): self._migrate_1_0_to_1_1,
            ("1.1.0", "1.2.0"): self._migrate_1_1_to_1_2,
            # Add more migration paths as needed
        }
        
        migration_key = (from_version, to_version)
        
        if migration_key in migration_map:
            return migration_map[migration_key]()
        else:
            # Try to find a migration path through intermediate versions
            return self._find_migration_path(from_version, to_version)
    
    def _find_migration_path(self, from_version: str, to_version: str) -> bool:
        """Find and execute migration path through intermediate versions"""
        # For now, just call the individual storage migration methods
        try:
            self.storage_manager.models.migrate(from_version, to_version)
            self.storage_manager.history.migrate(from_version, to_version)
            self.storage_manager.preferences.migrate(from_version, to_version)
            self.storage_manager.cache.migrate(from_version, to_version)
            return True
        except Exception as e:
            print(f"Migration path failed: {e}")
            return False
    
    def _migrate_1_0_to_1_1(self) -> bool:
        """Migrate from version 1.0.0 to 1.1.0"""
        print("Performing migration from 1.0.0 to 1.1.0")
        
        # Example migration: Add new fields to history entries
        # This would involve updating the database schema
        
        try:
            # Perform specific migration steps
            # For example, add new columns to history table
            if hasattr(self.storage_manager.history, 'connection'):
                connection = self.storage_manager.history.connection
                
                # Add new columns if they don't exist
                try:
                    connection.execute('ALTER TABLE history_entries ADD COLUMN new_field TEXT')
                    connection.commit()
                except Exception:
                    # Column might already exist
                    pass
            
            return True
            
        except Exception as e:
            print(f"Migration 1.0 to 1.1 failed: {e}")
            return False
    
    def _migrate_1_1_to_1_2(self) -> bool:
        """Migrate from version 1.1.0 to 1.2.0"""
        print("Performing migration from 1.1.0 to 1.2.0")
        
        try:
            # Example: Update preferences format
            preferences = self.storage_manager.preferences.load_preferences()
            if preferences:
                # Add new preference fields
                if not hasattr(preferences, 'new_preference'):
                    preferences.new_preference = "default_value"
                    self.storage_manager.preferences.save_preferences(preferences)
            
            return True
            
        except Exception as e:
            print(f"Migration 1.1 to 1.2 failed: {e}")
            return False
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a complete backup of all storage data"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = Path.cwd() / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup all storage components
        backup_paths = self.storage_manager.backup_all(str(backup_dir))
        
        # Create backup manifest
        manifest = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "version": self.get_current_version(),
            "backup_paths": backup_paths
        }
        
        manifest_file = backup_dir / "backup_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(backup_dir)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        backup_dir = Path(backup_path)
        manifest_file = backup_dir / "backup_manifest.json"
        
        if not manifest_file.exists():
            print(f"Backup manifest not found: {manifest_file}")
            return False
        
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            backup_paths = manifest.get("backup_paths", {})
            
            # Restore all storage components
            self.storage_manager.restore_all(backup_paths)
            
            print(f"Restored from backup: {manifest['backup_name']}")
            return True
            
        except Exception as e:
            print(f"Failed to restore backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        backup_root = Path.cwd() / "backups"
        
        if not backup_root.exists():
            return backups
        
        for backup_dir in backup_root.iterdir():
            if backup_dir.is_dir():
                manifest_file = backup_dir / "backup_manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            "name": manifest.get("backup_name", backup_dir.name),
                            "path": str(backup_dir),
                            "created_at": manifest.get("created_at"),
                            "version": manifest.get("version"),
                            "size": self._get_directory_size(backup_dir)
                        })
                    except Exception:
                        # Skip invalid backups
                        continue
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Clean up old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0
        
        backups_to_delete = backups[keep_count:]
        deleted_count = 0
        
        for backup in backups_to_delete:
            try:
                backup_path = Path(backup["path"])
                if backup_path.exists():
                    shutil.rmtree(backup_path)
                    deleted_count += 1
                    print(f"Deleted old backup: {backup['name']}")
            except Exception as e:
                print(f"Failed to delete backup {backup['name']}: {e}")
        
        return deleted_count


def create_migration_manager(config: Optional[StorageConfig] = None) -> MigrationManager:
    """Create a migration manager with storage"""
    if config is None:
        from config.manager import get_config
        config = get_config().storage
    
    storage_manager = StorageFactory.create_storage_manager(config)
    storage_manager.initialize_all()
    
    return MigrationManager(storage_manager)


# CLI interface for migrations
def main():
    """Command-line interface for data migrations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data migration utility")
    parser.add_argument("command", choices=["migrate", "backup", "restore", "list-backups", "cleanup"])
    parser.add_argument("--version", help="Target version for migration")
    parser.add_argument("--backup-path", help="Path to backup for restore")
    parser.add_argument("--backup-name", help="Name for backup")
    parser.add_argument("--keep-count", type=int, default=5, help="Number of backups to keep during cleanup")
    
    args = parser.parse_args()
    
    migration_manager = create_migration_manager()
    
    if args.command == "migrate":
        if not args.version:
            print("Error: --version required for migrate command")
            return 1
        
        success = migration_manager.migrate_to_version(args.version)
        return 0 if success else 1
    
    elif args.command == "backup":
        backup_path = migration_manager.create_backup(args.backup_name)
        print(f"Backup created: {backup_path}")
        return 0
    
    elif args.command == "restore":
        if not args.backup_path:
            print("Error: --backup-path required for restore command")
            return 1
        
        success = migration_manager.restore_backup(args.backup_path)
        return 0 if success else 1
    
    elif args.command == "list-backups":
        backups = migration_manager.list_backups()
        if not backups:
            print("No backups found")
        else:
            print("Available backups:")
            for backup in backups:
                size_mb = backup["size"] / (1024 * 1024)
                print(f"  {backup['name']} - {backup['created_at']} - {size_mb:.1f}MB")
        return 0
    
    elif args.command == "cleanup":
        deleted_count = migration_manager.cleanup_old_backups(args.keep_count)
        print(f"Deleted {deleted_count} old backups")
        return 0


if __name__ == "__main__":
    exit(main())