"""
存储引擎模块

提供数据持久化和历史记录管理功能。
"""

from .interfaces import StorageInterface
from .file_storage import FileStorage
from .factory import StorageFactory

__all__ = [
    'StorageInterface',
    'FileStorage',
    'StorageFactory',
]
