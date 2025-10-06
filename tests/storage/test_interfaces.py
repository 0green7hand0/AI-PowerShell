"""
存储接口测试
"""

import pytest
from src.storage.interfaces import StorageInterface


def test_storage_interface_is_abstract():
    """测试 StorageInterface 是抽象类"""
    with pytest.raises(TypeError):
        StorageInterface()


def test_storage_interface_has_required_methods():
    """测试 StorageInterface 定义了所有必需的方法"""
    required_methods = [
        'save_history',
        'load_history',
        'clear_history',
        'save_config',
        'load_config',
        'save_cache',
        'load_cache',
        'clear_cache',
        'get_storage_info'
    ]
    
    for method in required_methods:
        assert hasattr(StorageInterface, method), f"缺少方法: {method}"
