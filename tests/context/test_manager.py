"""
上下文管理器测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from src.context.manager import ContextManager
from src.context.models import (
    Session,
    CommandEntry,
    ContextSnapshot,
    UserPreferences,
    SessionStatus,
    CommandStatus
)
from src.interfaces.base import Context, ExecutionResult, Suggestion


@pytest.fixture
def mock_storage():
    """创建模拟存储"""
    storage = Mock()
    storage.save_session = Mock()
    storage.load_session = Mock(return_value=None)
    storage.save_snapshot = Mock()
    storage.load_snapshot = Mock(return_value=None)
    storage.save_user_preferences = Mock()
    storage.load_user_preferences = Mock(return_value=None)
    return storage


@pytest.fixture
def context_manager(mock_storage):
    """创建上下文管理器实例"""
    return ContextManager(storage=mock_storage)


@pytest.fixture
def context_manager_no_storage():
    """创建无存储的上下文管理器实例"""
    return ContextManager(storage=None)


class TestContextManagerInitialization:
    """测试上下文管理器初始化"""
    
    def test_init_with_storage(self, mock_storage):
        """测试带存储初始化"""
        manager = ContextManager(storage=mock_storage)
        
        assert manager.storage == mock_storage
        assert manager.current_session is None
        assert len(manager.sessions) == 0
    
    def test_init_without_storage(self):
        """测试无存储初始化"""
        manager = ContextManager(storage=None)
        
        assert manager.storage is None
        assert manager.current_session is None


class TestSessionManagement:
    """测试会话管理"""
    
    def test_start_session(self, context_manager):
        """测试开始新会话"""
        session = context_manager.start_session(
            user_id="user123",
            working_directory="/home/user"
        )
        
        assert session is not None
        assert session.user_id == "user123"
        assert session.working_directory == "/home/user"
        assert session.status == SessionStatus.ACTIVE
        assert context_manager.current_session == session
        assert session.session_id in context_manager.sessions
    
    def test_start_session_saves_to_storage(self, context_manager, mock_storage):
        """测试开始会话时保存到存储"""
        session = context_manager.start_session()
        
        mock_storage.save_session.assert_called_once()
    
    def test_get_session(self, context_manager):
        """测试获取会话"""
        session = context_manager.start_session()
        
        retrieved = context_manager.get_session(session.session_id)
        
        assert retrieved == session
    
    def test_get_session_not_found(self, context_manager):
        """测试获取不存在的会话"""
        result = context_manager.get_session("nonexistent")
        
        assert result is None
    
    def test_get_current_session(self, context_manager):
        """测试获取当前会话"""
        assert context_manager.get_current_session() is None
        
        session = context_manager.start_session()
        
        assert context_manager.get_current_session() == session
    
    def test_switch_session(self, context_manager):
        """测试切换会话"""
        session1 = context_manager.start_session()
        session2 = context_manager.start_session()
        
        assert context_manager.current_session == session2
        
        success = context_manager.switch_session(session1.session_id)
        
        assert success is True
        assert context_manager.current_session == session1
    
    def test_switch_to_nonexistent_session(self, context_manager):
        """测试切换到不存在的会话"""
        success = context_manager.switch_session("nonexistent")
        
        assert success is False
    
    def test_terminate_session(self, context_manager):
        """测试终止会话"""
        session = context_manager.start_session()
        
        assert session.is_active is True
        
        context_manager.terminate_session(session.session_id)
        
        assert session.status == SessionStatus.TERMINATED
        assert session.end_time is not None
        assert context_manager.current_session is None
    
    def test_terminate_current_session(self, context_manager):
        """测试终止当前会话"""
        session = context_manager.start_session()
        
        context_manager.terminate_session()
        
        assert session.status == SessionStatus.TERMINATED
        assert context_manager.current_session is None
    
    def test_cleanup_expired_sessions(self, context_manager):
        """测试清理过期会话"""
        # 创建会话并修改最后活动时间
        session = context_manager.start_session()
        session.last_activity = datetime.now() - timedelta(hours=2)
        
        context_manager.cleanup_expired_sessions(timeout=3600)
        
        assert session.status == SessionStatus.EXPIRED


class TestCommandManagement:
    """测试命令管理"""
    
    def test_add_command(self, context_manager):
        """测试添加命令"""
        context_manager.start_session()
        
        suggestion = Suggestion(
            original_input="显示时间",
            generated_command="Get-Date",
            confidence_score=0.95,
            explanation="获取当前日期和时间"
        )
        
        entry = context_manager.add_command("显示时间", suggestion)
        
        assert entry is not None
        assert entry.user_input == "显示时间"
        assert entry.translated_command == "Get-Date"
        assert entry.confidence_score == 0.95
        assert len(context_manager.current_session.command_history) == 1
    
    def test_add_command_with_result(self, context_manager):
        """测试添加带执行结果的命令"""
        context_manager.start_session()
        
        suggestion = Suggestion(
            original_input="test",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="test"
        )
        
        result = ExecutionResult(
            success=True,
            command="Test-Command",
            output="Success",
            return_code=0,
            execution_time=0.5
        )
        
        entry = context_manager.add_command("test", suggestion, result)
        
        assert entry.status == CommandStatus.COMPLETED
        assert entry.output == "Success"
        assert entry.return_code == 0
        assert entry.execution_time == 0.5
    
    def test_add_command_creates_session(self, context_manager_no_storage):
        """测试添加命令时自动创建会话"""
        manager = context_manager_no_storage
        
        assert manager.current_session is None
        
        suggestion = Suggestion(
            original_input="test",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="test"
        )
        
        manager.add_command("test", suggestion)
        
        assert manager.current_session is not None
    
    def test_update_command_status(self, context_manager):
        """测试更新命令状态"""
        context_manager.start_session()
        
        suggestion = Suggestion(
            original_input="test",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="test"
        )
        
        entry = context_manager.add_command("test", suggestion)
        
        assert entry.status == CommandStatus.PENDING
        
        result = ExecutionResult(
            success=True,
            command="Test-Command",
            output="Done",
            return_code=0
        )
        
        context_manager.update_command_status(
            entry.command_id,
            CommandStatus.COMPLETED,
            result
        )
        
        assert entry.status == CommandStatus.COMPLETED
        assert entry.output == "Done"
    
    def test_get_command(self, context_manager):
        """测试获取命令"""
        context_manager.start_session()
        
        suggestion = Suggestion(
            original_input="test",
            generated_command="Test-Command",
            confidence_score=0.9,
            explanation="test"
        )
        
        entry = context_manager.add_command("test", suggestion)
        
        retrieved = context_manager.get_command(entry.command_id)
        
        assert retrieved == entry


class TestContextQuery:
    """测试上下文查询"""
    
    def test_get_context(self, context_manager):
        """测试获取上下文"""
        session = context_manager.start_session(
            user_id="user123",
            working_directory="/home/user"
        )
        
        # 添加一些命令
        for i in range(10):
            suggestion = Suggestion(
                original_input=f"command {i}",
                generated_command=f"Command-{i}",
                confidence_score=0.9,
                explanation="test"
            )
            context_manager.add_command(f"command {i}", suggestion)
        
        context = context_manager.get_context(depth=5)
        
        assert context.session_id == session.session_id
        assert context.user_id == "user123"
        assert context.working_directory == "/home/user"
        assert len(context.command_history) == 5
        assert context.command_history[-1] == "Command-9"
    
    def test_get_context_no_session(self, context_manager):
        """测试无会话时获取上下文"""
        context = context_manager.get_context()
        
        assert context.session_id == "temp"
        assert len(context.command_history) == 0
    
    def test_get_recent_commands(self, context_manager):
        """测试获取最近命令"""
        context_manager.start_session()
        
        for i in range(5):
            suggestion = Suggestion(
                original_input=f"cmd {i}",
                generated_command=f"Cmd-{i}",
                confidence_score=0.9,
                explanation="test"
            )
            context_manager.add_command(f"cmd {i}", suggestion)
        
        recent = context_manager.get_recent_commands(3)
        
        assert len(recent) == 3
        assert recent[0].user_input == "cmd 2"
        assert recent[-1].user_input == "cmd 4"
    
    def test_get_successful_commands(self, context_manager):
        """测试获取成功命令"""
        context_manager.start_session()
        
        # 添加成功命令
        suggestion1 = Suggestion(
            original_input="success",
            generated_command="Success-Cmd",
            confidence_score=0.9,
            explanation="test"
        )
        result1 = ExecutionResult(success=True, command="Success-Cmd", return_code=0)
        context_manager.add_command("success", suggestion1, result1)
        
        # 添加失败命令
        suggestion2 = Suggestion(
            original_input="fail",
            generated_command="Fail-Cmd",
            confidence_score=0.9,
            explanation="test"
        )
        result2 = ExecutionResult(success=False, command="Fail-Cmd", return_code=1)
        context_manager.add_command("fail", suggestion2, result2)
        
        successful = context_manager.get_successful_commands()
        
        assert len(successful) == 1
        assert successful[0].user_input == "success"
    
    def test_get_failed_commands(self, context_manager):
        """测试获取失败命令"""
        context_manager.start_session()
        
        suggestion = Suggestion(
            original_input="fail",
            generated_command="Fail-Cmd",
            confidence_score=0.9,
            explanation="test"
        )
        result = ExecutionResult(success=False, command="Fail-Cmd", error="Error", return_code=1)
        context_manager.add_command("fail", suggestion, result)
        
        failed = context_manager.get_failed_commands()
        
        assert len(failed) == 1
        assert failed[0].user_input == "fail"


class TestSnapshotManagement:
    """测试快照管理"""
    
    def test_create_snapshot(self, context_manager):
        """测试创建快照"""
        context_manager.start_session()
        
        snapshot = context_manager.create_snapshot(
            description="Test snapshot",
            tags=["test"]
        )
        
        assert snapshot is not None
        assert snapshot.description == "Test snapshot"
        assert "test" in snapshot.tags
        assert snapshot.session == context_manager.current_session
    
    def test_create_snapshot_no_session(self, context_manager):
        """测试无会话时创建快照"""
        with pytest.raises(ValueError):
            context_manager.create_snapshot()
    
    def test_restore_snapshot(self, context_manager, mock_storage):
        """测试恢复快照"""
        # 创建会话和快照
        session = context_manager.start_session()
        snapshot = context_manager.create_snapshot()
        
        # 模拟存储返回快照数据
        mock_storage.load_snapshot.return_value = snapshot.to_dict()
        
        # 终止当前会话
        context_manager.terminate_session()
        
        # 恢复快照
        success = context_manager.restore_snapshot(snapshot.snapshot_id)
        
        assert success is True
        assert context_manager.current_session is not None


class TestUserPreferences:
    """测试用户偏好管理"""
    
    def test_get_user_preferences(self, context_manager):
        """测试获取用户偏好"""
        prefs = context_manager.get_user_preferences("user123")
        
        assert prefs is not None
        assert prefs.user_id == "user123"
    
    def test_save_user_preferences(self, context_manager, mock_storage):
        """测试保存用户偏好"""
        prefs = UserPreferences(
            user_id="user123",
            auto_execute_safe_commands=True
        )
        
        context_manager.save_user_preferences(prefs)
        
        assert "user123" in context_manager.user_preferences
        mock_storage.save_user_preferences.assert_called_once()


class TestStatistics:
    """测试统计信息"""
    
    def test_get_session_stats(self, context_manager):
        """测试获取会话统计"""
        context_manager.start_session()
        
        # 添加一些命令
        suggestion1 = Suggestion(
            original_input="success",
            generated_command="Success-Cmd",
            confidence_score=0.9,
            explanation="test"
        )
        result1 = ExecutionResult(success=True, command="Success-Cmd", return_code=0)
        context_manager.add_command("success", suggestion1, result1)
        
        suggestion2 = Suggestion(
            original_input="fail",
            generated_command="Fail-Cmd",
            confidence_score=0.9,
            explanation="test"
        )
        result2 = ExecutionResult(success=False, command="Fail-Cmd", return_code=1)
        context_manager.add_command("fail", suggestion2, result2)
        
        stats = context_manager.get_session_stats()
        
        assert stats["command_count"] == 2
        assert stats["successful_commands"] == 1
        assert stats["failed_commands"] == 1
        assert "session_id" in stats
        assert "duration" in stats
    
    def test_get_session_stats_no_session(self, context_manager):
        """测试无会话时获取统计"""
        stats = context_manager.get_session_stats()
        
        assert stats == {}
