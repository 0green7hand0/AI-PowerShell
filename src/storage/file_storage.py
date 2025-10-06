"""
文件存储实现

基于文件系统的存储实现，支持历史记录、配置和缓存的持久化。
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os

from .interfaces import StorageInterface


class FileStorage(StorageInterface):
    """文件存储实现类"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化文件存储
        
        Args:
            base_path: 存储基础路径，默认为 ~/.ai-powershell
        """
        if base_path is None:
            base_path = os.path.expanduser("~/.ai-powershell")
        
        self.base_path = Path(base_path)
        self.history_file = self.base_path / "history.json"
        self.config_file = self.base_path / "config.yaml"
        self.cache_dir = self.base_path / "cache"
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_history(self, entry: Dict[str, Any]) -> bool:
        """
        保存历史记录
        
        Args:
            entry: 历史记录条目
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 加载现有历史
            history = self.load_history()
            
            # 添加时间戳
            if "timestamp" not in entry:
                entry["timestamp"] = datetime.now().isoformat()
            
            # 添加新记录
            history.append(entry)
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return False
    
    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        加载历史记录
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 如果指定了限制，返回最近的记录
            if limit is not None and limit > 0:
                return history[-limit:]
            
            return history
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return []
    
    def clear_history(self) -> bool:
        """
        清除所有历史记录
        
        Returns:
            bool: 清除是否成功
        """
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            print(f"清除历史记录失败: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        加载配置
        
        Returns:
            Optional[Dict[str, Any]]: 配置字典
        """
        try:
            if not self.config_file.exists():
                return None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None
    
    def save_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        保存缓存数据
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            
        Returns:
            bool: 保存是否成功
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            cache_data = {
                "value": value,
                "created_at": datetime.now().isoformat()
            }
            
            if ttl is not None:
                expire_at = datetime.now() + timedelta(seconds=ttl)
                cache_data["expire_at"] = expire_at.isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存缓存失败: {e}")
            return False
    
    def load_cache(self, key: str) -> Optional[Any]:
        """
        加载缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            if "expire_at" in cache_data:
                expire_at = datetime.fromisoformat(cache_data["expire_at"])
                if datetime.now() > expire_at:
                    # 删除过期缓存
                    cache_file.unlink()
                    return None
            
            return cache_data.get("value")
        except Exception as e:
            print(f"加载缓存失败: {e}")
            return None
    
    def clear_cache(self) -> bool:
        """
        清除所有缓存
        
        Returns:
            bool: 清除是否成功
        """
        try:
            if self.cache_dir.exists():
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储信息
        
        Returns:
            Dict[str, Any]: 存储信息
        """
        info = {
            "base_path": str(self.base_path),
            "history_file": str(self.history_file),
            "config_file": str(self.config_file),
            "cache_dir": str(self.cache_dir),
            "history_exists": self.history_file.exists(),
            "config_exists": self.config_file.exists(),
            "history_count": 0,
            "cache_count": 0,
            "total_size": 0
        }
        
        try:
            # 统计历史记录数
            if self.history_file.exists():
                history = self.load_history()
                info["history_count"] = len(history)
                info["total_size"] += self.history_file.stat().st_size
            
            # 统计配置文件大小
            if self.config_file.exists():
                info["total_size"] += self.config_file.stat().st_size
            
            # 统计缓存文件数和大小
            if self.cache_dir.exists():
                cache_files = list(self.cache_dir.glob("*.json"))
                info["cache_count"] = len(cache_files)
                for cache_file in cache_files:
                    info["total_size"] += cache_file.stat().st_size
        except Exception as e:
            print(f"获取存储信息失败: {e}")
        
        return info
    
    # ========================================================================
    # 上下文管理相关方法
    # ========================================================================
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        保存会话数据
        
        Args:
            session_data: 会话数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            sessions_dir = self.base_path / "sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            
            session_id = session_data.get("session_id")
            if not session_id:
                return False
            
            session_file = sessions_dir / f"{session_id}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存会话失败: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载会话数据
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话数据字典
        """
        try:
            sessions_dir = self.base_path / "sessions"
            session_file = sessions_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return session_data
        except Exception as e:
            print(f"加载会话失败: {e}")
            return None
    
    def save_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """
        保存上下文快照
        
        Args:
            snapshot_data: 快照数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            snapshots_dir = self.base_path / "snapshots"
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            
            snapshot_id = snapshot_data.get("snapshot_id")
            if not snapshot_id:
                return False
            
            snapshot_file = snapshots_dir / f"{snapshot_id}.json"
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存快照失败: {e}")
            return False
    
    def load_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        加载上下文快照
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            Optional[Dict[str, Any]]: 快照数据字典
        """
        try:
            snapshots_dir = self.base_path / "snapshots"
            snapshot_file = snapshots_dir / f"{snapshot_id}.json"
            
            if not snapshot_file.exists():
                return None
            
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            
            return snapshot_data
        except Exception as e:
            print(f"加载快照失败: {e}")
            return None
    
    def save_user_preferences(self, preferences_data: Dict[str, Any]) -> bool:
        """
        保存用户偏好设置
        
        Args:
            preferences_data: 用户偏好数据字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            preferences_dir = self.base_path / "preferences"
            preferences_dir.mkdir(parents=True, exist_ok=True)
            
            user_id = preferences_data.get("user_id")
            if not user_id:
                return False
            
            prefs_file = preferences_dir / f"{user_id}.json"
            
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preferences_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存用户偏好失败: {e}")
            return False
    
    def load_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        加载用户偏好设置
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户偏好数据字典
        """
        try:
            preferences_dir = self.base_path / "preferences"
            prefs_file = preferences_dir / f"{user_id}.json"
            
            if not prefs_file.exists():
                return None
            
            with open(prefs_file, 'r', encoding='utf-8') as f:
                preferences_data = json.load(f)
            
            return preferences_data
        except Exception as e:
            print(f"加载用户偏好失败: {e}")
            return None
    
    def save_history_batch(self, history_data: List[Dict[str, Any]]) -> bool:
        """
        批量保存历史记录
        
        Args:
            history_data: 历史记录列表
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 直接覆盖整个历史文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"批量保存历史记录失败: {e}")
            return False
