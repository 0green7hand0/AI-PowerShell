"""
历史记录管理器测试
"""

import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

from src.context.history import HistoryManager
from src.context.models import CommandEntry, CommandStatus


@pytest.fixture
def mock_storage():
    """创建模拟存储"""
    storage = Mock()
    storage.load_history = Mock(return_value=[])
    storage.save_history_batch = Mock()
    return storage


@pytest.fixture
def history_manager(mock_storage):
    """创建历史记录管理器实例"""
    return HistoryManager(storage=mock_storage, max_history=100)


@pytest.fixture
def history_manager_no_storage():
    """创建无存储的历史记录管理器实例"""
    return HistoryManager(storage=None, max_history=100)


@pytest.fixture
def sample_entries():
    """创建示例历史记录条目"""
    entries = []
    for i in range(10):
        entry = CommandEntry(
            user_input=f"command {i}",
            translated_command=f"Command-{i}",
            status=CommandStatus.COMPLETED if i % 2 == 0 else CommandStatus.FAILED,
            return_code=0 if i % 2 == 0 else 1,
            confidence_score=0.9,
            execution_time=0.5
        )
        entries.append(entry)
    return entries


class TestHistoryManagerInitialization:
    """测试历史记录管理器初始化"""
    
    def test_init_with_storage(self, mock_storage):
        """测试带存储初始化"""
        manager = HistoryManager(storage=mock_storage, max_history=50)
        
        assert manager.storage == mock_storage
        assert manager.max_history == 50
        assert len(manager.history_cache) == 0
        mock_storage.load_history.assert_called_once()
    
    def test_init_without_storage(self):
        """测试无存储初始化"""
        manager = HistoryManager(storage=None)
        
        assert manager.storage is None
        assert len(manager.history_cache) == 0


class TestBasicOperations:
    """测试基础操作"""
    
    def test_add_entry(self, history_manager):
        """测试添加历史记录"""
        entry = CommandEntry(user_input="test", translated_command="Test-Command")
        
        history_manager.add_entry(entry)
        
        assert len(history_manager.history_cache) == 1
        assert history_manager.history_cache[0] == entry
    
    def test_add_entry_saves_to_storage(self, history_manager, mock_storage):
        """测试添加记录时保存到存储"""
        entry = CommandEntry(user_input="test", translated_command="Test-Command")
        
        history_manager.add_entry(entry)
        
        mock_storage.save_history_batch.assert_called_once()
    
    def test_add_entry_respects_max_history(self, history_manager_no_storage):
        """测试添加记录时遵守最大数量限制"""
        manager = history_manager_no_storage
        manager.max_history = 5
        
        for i in range(10):
            entry = CommandEntry(user_input=f"cmd {i}")
            manager.add_entry(entry)
        
        assert len(manager.history_cache) == 5
        assert manager.history_cache[0].user_input == "cmd 5"
        assert manager.history_cache[-1].user_input == "cmd 9"
    
    def test_get_all(self, history_manager, sample_entries):
        """测试获取所有历史记录"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        all_entries = history_manager.get_all()
        
        assert len(all_entries) == 10
    
    def test_get_all_with_limit(self, history_manager, sample_entries):
        """测试获取限定数量的历史记录"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        limited = history_manager.get_all(limit=5)
        
        assert len(limited) == 5
        assert limited[0].user_input == "command 5"
    
    def test_get_by_id(self, history_manager):
        """测试根据 ID 获取记录"""
        entry = CommandEntry(user_input="test")
        history_manager.add_entry(entry)
        
        retrieved = history_manager.get_by_id(entry.command_id)
        
        assert retrieved == entry
    
    def test_get_by_id_not_found(self, history_manager):
        """测试获取不存在的记录"""
        result = history_manager.get_by_id("nonexistent")
        
        assert result is None
    
    def test_clear(self, history_manager, sample_entries):
        """测试清空历史记录"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        assert len(history_manager.history_cache) > 0
        
        history_manager.clear()
        
        assert len(history_manager.history_cache) == 0
    
    def test_remove_entry(self, history_manager):
        """测试删除指定记录"""
        entry = CommandEntry(user_input="test")
        history_manager.add_entry(entry)
        
        assert len(history_manager.history_cache) == 1
        
        success = history_manager.remove_entry(entry.command_id)
        
        assert success is True
        assert len(history_manager.history_cache) == 0
    
    def test_remove_entry_not_found(self, history_manager):
        """测试删除不存在的记录"""
        success = history_manager.remove_entry("nonexistent")
        
        assert success is False


class TestSearchAndFilter:
    """测试搜索和过滤"""
    
    def test_search_in_input(self, history_manager):
        """测试在输入中搜索"""
        history_manager.add_entry(CommandEntry(user_input="显示时间"))
        history_manager.add_entry(CommandEntry(user_input="列出文件"))
        history_manager.add_entry(CommandEntry(user_input="显示日期"))
        
        results = history_manager.search("显示", search_in="input")
        
        assert len(results) == 2
        assert all("显示" in r.user_input for r in results)
    
    def test_search_in_command(self, history_manager):
        """测试在命令中搜索"""
        history_manager.add_entry(CommandEntry(translated_command="Get-Date"))
        history_manager.add_entry(CommandEntry(translated_command="Get-Process"))
        history_manager.add_entry(CommandEntry(translated_command="Set-Location"))
        
        results = history_manager.search("Get", search_in="command")
        
        assert len(results) == 2
    
    def test_search_in_all(self, history_manager):
        """测试在所有字段中搜索"""
        history_manager.add_entry(CommandEntry(
            user_input="test input",
            translated_command="Test-Command",
            output="test output"
        ))
        
        results = history_manager.search("test", search_in="all")
        
        assert len(results) == 1
    
    def test_filter_by_status(self, history_manager, sample_entries):
        """测试按状态过滤"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        completed = history_manager.filter_by_status(CommandStatus.COMPLETED)
        failed = history_manager.filter_by_status(CommandStatus.FAILED)
        
        assert len(completed) == 5
        assert len(failed) == 5
    
    def test_filter_by_date_range(self, history_manager):
        """测试按日期范围过滤"""
        now = datetime.now()
        
        # 添加不同时间的记录
        entry1 = CommandEntry(user_input="old")
        entry1.timestamp = now - timedelta(days=2)
        history_manager.add_entry(entry1)
        
        entry2 = CommandEntry(user_input="recent")
        entry2.timestamp = now - timedelta(hours=1)
        history_manager.add_entry(entry2)
        
        # 过滤最近 1 天的记录
        start = now - timedelta(days=1)
        results = history_manager.filter_by_date_range(start)
        
        assert len(results) == 1
        assert results[0].user_input == "recent"
    
    def test_filter_by_success(self, history_manager, sample_entries):
        """测试按执行结果过滤"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        successful = history_manager.filter_by_success(successful=True)
        failed = history_manager.filter_by_success(successful=False)
        
        assert len(successful) == 5
        assert len(failed) == 5
    
    def test_filter_by_confidence(self, history_manager):
        """测试按置信度过滤"""
        history_manager.add_entry(CommandEntry(confidence_score=0.5))
        history_manager.add_entry(CommandEntry(confidence_score=0.8))
        history_manager.add_entry(CommandEntry(confidence_score=0.95))
        
        results = history_manager.filter_by_confidence(min_confidence=0.7)
        
        assert len(results) == 2
    
    def test_filter_by_custom(self, history_manager):
        """测试自定义过滤"""
        history_manager.add_entry(CommandEntry(execution_time=0.5))
        history_manager.add_entry(CommandEntry(execution_time=1.5))
        history_manager.add_entry(CommandEntry(execution_time=2.5))
        
        # 过滤执行时间大于 1 秒的命令
        results = history_manager.filter_by_custom(
            lambda entry: entry.execution_time > 1.0
        )
        
        assert len(results) == 2


class TestStatistics:
    """测试统计分析"""
    
    def test_get_statistics(self, history_manager, sample_entries):
        """测试获取统计信息"""
        for entry in sample_entries:
            history_manager.add_entry(entry)
        
        stats = history_manager.get_statistics()
        
        assert stats["total_commands"] == 10
        assert stats["successful_commands"] == 5
        assert stats["failed_commands"] == 5
        assert stats["success_rate"] == 0.5
        assert "average_confidence" in stats
        assert "average_execution_time" in stats
    
    def test_get_statistics_empty(self, history_manager):
        """测试空历史记录的统计"""
        stats = history_manager.get_statistics()
        
        assert stats["total_commands"] == 0
        assert stats["successful_commands"] == 0
    
    def test_get_most_used_commands(self, history_manager):
        """测试获取最常用命令"""
        # 添加重复命令
        for i in range(5):
            history_manager.add_entry(CommandEntry(translated_command="Get-Date"))
        for i in range(3):
            history_manager.add_entry(CommandEntry(translated_command="Get-Process"))
        history_manager.add_entry(CommandEntry(translated_command="Get-Location"))
        
        most_used = history_manager.get_most_used_commands(limit=3)
        
        assert len(most_used) == 3
        assert most_used[0]["command"] == "Get-Date"
        assert most_used[0]["count"] == 5
        assert most_used[1]["command"] == "Get-Process"
        assert most_used[1]["count"] == 3
    
    def test_get_command_patterns(self, history_manager):
        """测试分析命令模式"""
        history_manager.add_entry(CommandEntry(translated_command="Get-Date"))
        history_manager.add_entry(CommandEntry(translated_command="Get-Process"))
        history_manager.add_entry(CommandEntry(translated_command="Set-Location"))
        history_manager.add_entry(CommandEntry(translated_command="Get-ChildItem"))
        
        patterns = history_manager.get_command_patterns()
        
        assert patterns["Get-Date"] == 1
        assert patterns["Get-Process"] == 1
        assert patterns["Set-Location"] == 1
        assert patterns["Get-ChildItem"] == 1
    
    def test_get_time_distribution(self, history_manager):
        """测试获取时间分布"""
        now = datetime.now()
        
        for i in range(5):
            entry = CommandEntry(user_input=f"cmd {i}")
            entry.timestamp = now.replace(hour=10)
            history_manager.add_entry(entry)
        
        for i in range(3):
            entry = CommandEntry(user_input=f"cmd {i}")
            entry.timestamp = now.replace(hour=14)
            history_manager.add_entry(entry)
        
        distribution = history_manager.get_time_distribution()
        
        assert "10:00" in distribution
        assert distribution["10:00"] == 5
        assert "14:00" in distribution
        assert distribution["14:00"] == 3
    
    def test_get_error_analysis(self, history_manager):
        """测试错误分析"""
        # 添加成功命令
        for i in range(7):
            history_manager.add_entry(CommandEntry(
                status=CommandStatus.COMPLETED,
                return_code=0
            ))
        
        # 添加失败命令
        for i in range(3):
            history_manager.add_entry(CommandEntry(
                status=CommandStatus.FAILED,
                error="Command not found"
            ))
        
        analysis = history_manager.get_error_analysis()
        
        assert analysis["total_errors"] == 3
        assert analysis["error_rate"] == 0.3
        assert len(analysis["common_errors"]) > 0


class TestExportImport:
    """测试导出和导入"""
    
    def test_export_history_json(self, history_manager, sample_entries):
        """测试导出为 JSON"""
        for entry in sample_entries[:3]:
            history_manager.add_entry(entry)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            history_manager.export_history(filepath, format="json")
            
            # 验证文件存在且包含数据
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert len(data) == 3
            assert data[0]["user_input"] == "command 0"
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_export_history_csv(self, history_manager, sample_entries):
        """测试导出为 CSV"""
        for entry in sample_entries[:3]:
            history_manager.add_entry(entry)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filepath = f.name
        
        try:
            history_manager.export_history(filepath, format="csv")
            
            # 验证文件存在
            assert Path(filepath).exists()
            
            # 读取并验证内容
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            assert len(lines) == 4  # 1 header + 3 data rows
            assert "Timestamp" in lines[0]
        finally:
            Path(filepath).unlink(missing_ok=True)
    
    def test_import_history_json(self, history_manager_no_storage):
        """测试从 JSON 导入"""
        manager = history_manager_no_storage
        
        # 创建测试数据
        test_data = [
            {
                "command_id": "test-1",
                "user_input": "test 1",
                "translated_command": "Test-1",
                "status": "completed",
                "return_code": 0,
                "timestamp": datetime.now().isoformat()
            },
            {
                "command_id": "test-2",
                "user_input": "test 2",
                "translated_command": "Test-2",
                "status": "completed",
                "return_code": 0,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(test_data, f)
            filepath = f.name
        
        try:
            manager.import_history(filepath, format="json")
            
            assert len(manager.history_cache) == 2
            assert manager.history_cache[0].user_input == "test 1"
            assert manager.history_cache[1].user_input == "test 2"
        finally:
            Path(filepath).unlink(missing_ok=True)
