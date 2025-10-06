"""
存储接口定义

定义存储引擎的抽象接口，支持不同的存储后端实现。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class StorageInterface(ABC):
    """存储接口抽象基类"""
    
    @abstractmethod
    def save_history(self, entry: Dict[str, Any]) -> bool:
        """
        保存历史记录
        
        Args:
            entry: 历史记录条目，包含 input, command, success 等字段
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        加载历史记录
        
        Args:
            limit: 返回的最大记录数，None 表示返回所有记录
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        pass
    
    @abstractmethod
    def clear_history(self) -> bool:
        """
        清除所有历史记录
        
        Returns:
            bool: 清除是否成功
        """
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        加载配置
        
        Returns:
            Optional[Dict[str, Any]]: 配置字典，如果不存在返回 None
        """
        pass
    
    @abstractmethod
    def save_cache(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        保存缓存数据
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_cache(self, key: str) -> Optional[Any]:
        """
        加载缓存数据
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[Any]: 缓存值，如果不存在或已过期返回 None
        """
        pass
    
    @abstractmethod
    def clear_cache(self) -> bool:
        """
        清除所有缓存
        
        Returns:
            bool: 清除是否成功
        """
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储信息
        
        Returns:
            Dict[str, Any]: 存储信息，包括路径、大小等
        """
        pass
    
    # ========================================================================
    # 上下文管理相关方法
    # ========================================================================
    
    @abstractmethod
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        保存会话数据
        
        Args:
            session_data: 会话数据字典
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载会话数据
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话数据字典，如果不存在返回 None
        """
        pass
    
    @abstractmethod
    def save_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """
        保存上下文快照
        
        Args:
            snapshot_data: 快照数据字典
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        加载上下文快照
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            Optional[Dict[str, Any]]: 快照数据字典，如果不存在返回 None
        """
        pass
    
    @abstractmethod
    def save_user_preferences(self, preferences_data: Dict[str, Any]) -> bool:
        """
        保存用户偏好设置
        
        Args:
            preferences_data: 用户偏好数据字典
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        加载用户偏好设置
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户偏好数据字典，如果不存在返回 None
        """
        pass
    
    @abstractmethod
    def save_history_batch(self, history_data: List[Dict[str, Any]]) -> bool:
        """
        批量保存历史记录
        
        Args:
            history_data: 历史记录列表
            
        Returns:
            bool: 保存是否成功
        """
        pass
