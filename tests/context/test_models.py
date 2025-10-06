"""
上下文数据模型测试
"""

import pytest
from datetime import datetime, timedelta
import uuid

from src.context.models import (
    CommandEntry,
    Session,
    ContextSnapshot,
    UserPreferences,
    SessionStatus,
    CommandStatus
)


class TestCommandEntry:
    """测试命令条目数据模型"""
    
    def test_create_command_entry(self):
        """测试创建命令条目"""
        entry = CommandEntry(
            user_input="显示当前时间",
            translated_command="Get-Date",
            status=CommandStatus.COMPLETED,
            confidence_score=0.95
        )
        
        assert entry.user_input == "显示当前时间"
        assert entry.translated_command == "Get-Date"
        assert entry.status == CommandStatus.COMPLETED
        assert entry.confidence_score == 0.95
        assert entry.command_id is not None
    
    def test_command_entry_default_values(self):
        """测试命令条目默认值"""
        entry = CommandEntry()
        
        assert entry.user_input == ""
        assert entry.translated_command == ""
        assert entry.status == CommandStatus.PENDING
        assert entry.return_code == 0
        assert entry.execution_time == 0.0
    
    def test_is_successful(self):
        """测试成功判断"""
        entry = CommandEntry(
            status=CommandStatus.COMPLETED,
            return_code=0
        )
        
        assert entry.is_successful is True
        
        entry.return_code = 1
        assert entry.is_successful is False
    
    def test_has_error(self):
        """测试错误判断"""
        entry = CommandEntry(error="Some error")
        assert entry.has_error is True
        
        entry = CommandEntry(status=CommandStatus.FAILED)
        assert entry.has_error is True
        
        entry = CommandEntry()
        assert entry.has_error is False
    
    def test_to_dict(self):
        """测试转换为字典"""
        entry = CommandEntry(
            user_input="test",
            translated_command="Test-Command"
        )
        
        data = entry.to_dict()
        
        assert isinstance(data, dict)
        assert data["user_input"] == "test"
        assert data["translated_command"] == "Test-Command"
        assert "command_id" in data
        assert "timestamp" in data
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "command_id": str(uuid.uuid4()),
            "user_input": "test",
            "translated_command": "Test-Command",
            "status": "completed",
            "return_code": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        entry = CommandEntry.from_dict(data)
        
        assert entry.user_input == "test"
        assert entry.translated_command == "Test-Command"
        assert entry.status == CommandStatus.COMPLETED


class TestSession:
    """测试会话数据模型"""
    
    def test_create_session(self):
        """测试创建会话"""
        session = Session(
            user_id="user123",
            working_directory="/home/user"
        )
        
        assert session.user_id == "user123"
        assert session.working_directory == "/home/user"
        assert session.status == SessionStatus.ACTIVE
        assert session.session_id is not None
    
    def test_session_default_values(self):
        """测试会话默认值"""
        session = Session()
        
        assert session.status == SessionStatus.ACTIVE
        assert session.working_directory == "."
        assert len(session.command_history) == 0
        assert len(session.environment_vars) == 0
    
    def test_add_command(self):
        """测试添加命令"""
        session = Session()
        entry = CommandEntry(user_input="test")
        
        initial_time = session.last_activity
        session.add_command(entry)
        
        assert len(session.command_history) == 1
        assert session.command_history[0] == entry
        assert session.last_activity >= initial_time
    
    def test_get_recent_commands(self):
        """测试获取最近命令"""
        session = Session()
        
        for i in range(10):
            entry = CommandEntry(user_input=f"command {i}")
            session.add_command(entry)
        
        recent = session.get_recent_commands(5)
        
        assert len(recent) == 5
        assert recent[0].user_input == "command 5"
        assert recent[-1].user_input == "command 9"
    
    def test_get_successful_commands(self):
        """测试获取成功命令"""
        session = Session()
        
        # 添加成功命令
        entry1 = CommandEntry(status=CommandStatus.COMPLETED, return_code=0)
        session.add_command(entry1)
        
        # 添加失败命令
        entry2 = CommandEntry(status=CommandStatus.FAILED)
        session.add_command(entry2)
        
        successful = session.get_successful_commands()
        
        assert len(successful) == 1
        assert successful[0] == entry1
    
    def test_get_failed_commands(self):
        """测试获取失败命令"""
        session = Session()
        
        entry1 = CommandEntry(error="error message")
        session.add_command(entry1)
        
        entry2 = CommandEntry(status=CommandStatus.COMPLETED, return_code=0)
        session.add_command(entry2)
        
        failed = session.get_failed_commands()
        
        assert len(failed) == 1
        assert failed[0] == entry1
    
    def test_session_properties(self):
        """测试会话属性"""
        session = Session()
        
        assert session.command_count == 0
        assert session.successful_commands == 0
        assert session.failed_commands == 0
        assert session.is_active is True
        
        # 添加命令
        session.add_command(CommandEntry(status=CommandStatus.COMPLETED, return_code=0))
        session.add_command(CommandEntry(status=CommandStatus.FAILED))
        
        assert session.command_count == 2
        assert session.successful_commands == 1
        assert session.failed_commands == 1
    
    def test_terminate_session(self):
        """测试终止会话"""
        session = Session()
        
        assert session.is_active is True
        assert session.end_time is None
        
        session.terminate()
        
        assert session.status == SessionStatus.TERMINATED
        assert session.end_time is not None
        assert session.is_active is False
    
    def test_session_duration(self):
        """测试会话持续时间"""
        session = Session()
        
        # 模拟一些时间流逝
        import time
        time.sleep(0.1)
        
        duration = session.duration
        
        assert duration > 0
        assert duration < 1  # 应该小于 1 秒
    
    def test_to_dict(self):
        """测试转换为字典"""
        session = Session(user_id="user123")
        session.add_command(CommandEntry(user_input="test"))
        
        data = session.to_dict()
        
        assert isinstance(data, dict)
        assert data["user_id"] == "user123"
        assert "session_id" in data
        assert "command_history" in data
        assert len(data["command_history"]) == 1
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "session_id": str(uuid.uuid4()),
            "user_id": "user123",
            "status": "active",
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "working_directory": "/home/user",
            "command_history": []
        }
        
        session = Session.from_dict(data)
        
        assert session.user_id == "user123"
        assert session.status == SessionStatus.ACTIVE
        assert session.working_directory == "/home/user"


class TestContextSnapshot:
    """测试上下文快照数据模型"""
    
    def test_create_snapshot(self):
        """测试创建快照"""
        session = Session(user_id="user123")
        snapshot = ContextSnapshot(
            session=session,
            description="Test snapshot",
            tags=["test", "backup"]
        )
        
        assert snapshot.session == session
        assert snapshot.description == "Test snapshot"
        assert "test" in snapshot.tags
        assert snapshot.snapshot_id is not None
    
    def test_snapshot_to_dict(self):
        """测试快照转换为字典"""
        session = Session()
        snapshot = ContextSnapshot(session=session)
        
        data = snapshot.to_dict()
        
        assert isinstance(data, dict)
        assert "snapshot_id" in data
        assert "session" in data
        assert "timestamp" in data
    
    def test_snapshot_from_dict(self):
        """测试从字典创建快照"""
        session_data = {
            "session_id": str(uuid.uuid4()),
            "status": "active",
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "command_history": []
        }
        
        data = {
            "snapshot_id": str(uuid.uuid4()),
            "session": session_data,
            "timestamp": datetime.now().isoformat(),
            "description": "Test",
            "tags": ["test"]
        }
        
        snapshot = ContextSnapshot.from_dict(data)
        
        assert snapshot.description == "Test"
        assert "test" in snapshot.tags


class TestUserPreferences:
    """测试用户偏好设置数据模型"""
    
    def test_create_preferences(self):
        """测试创建用户偏好"""
        prefs = UserPreferences(
            user_id="user123",
            auto_execute_safe_commands=True,
            history_limit=200
        )
        
        assert prefs.user_id == "user123"
        assert prefs.auto_execute_safe_commands is True
        assert prefs.history_limit == 200
    
    def test_preferences_default_values(self):
        """测试偏好默认值"""
        prefs = UserPreferences(user_id="user123")
        
        assert prefs.auto_execute_safe_commands is False
        assert prefs.confirmation_required is True
        assert prefs.history_limit == 100
        assert prefs.session_timeout == 3600
        assert prefs.preferred_shell == "pwsh"
        assert prefs.language == "zh-CN"
    
    def test_preferences_to_dict(self):
        """测试偏好转换为字典"""
        prefs = UserPreferences(user_id="user123")
        
        data = prefs.to_dict()
        
        assert isinstance(data, dict)
        assert data["user_id"] == "user123"
        assert "auto_execute_safe_commands" in data
        assert "history_limit" in data
    
    def test_preferences_from_dict(self):
        """测试从字典创建偏好"""
        data = {
            "user_id": "user123",
            "auto_execute_safe_commands": True,
            "history_limit": 200,
            "preferred_shell": "powershell"
        }
        
        prefs = UserPreferences.from_dict(data)
        
        assert prefs.user_id == "user123"
        assert prefs.auto_execute_safe_commands is True
        assert prefs.history_limit == 200
        assert prefs.preferred_shell == "powershell"
