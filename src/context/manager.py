"""
上下文管理器

本模块实现上下文管理器，负责会话管理、上下文维护和状态跟踪。
支持多会话管理、上下文快照和会话恢复功能。
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from pathlib import Path

from .models import (
    Session,
    CommandEntry,
    ContextSnapshot,
    UserPreferences,
    SessionStatus,
    CommandStatus
)
from ..interfaces.base import Context, ExecutionResult, Suggestion
from ..storage.interfaces import StorageInterface


logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器
    
    负责管理用户会话、命令历史和上下文状态。
    提供会话生命周期管理、上下文查询和历史记录功能。
    """
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        """初始化上下文管理器
        
        Args:
            storage: 存储接口实例，用于持久化会话数据
        """
        self.storage = storage
        self.current_session: Optional[Session] = None
        self.sessions: Dict[str, Session] = {}  # 会话缓存
        self.user_preferences: Dict[str, UserPreferences] = {}  # 用户偏好缓存
        
        logger.info("ContextManager initialized")
    
    # ========================================================================
    # 会话管理
    # ========================================================================
    
    def start_session(self, user_id: Optional[str] = None, 
                     working_directory: str = ".",
                     environment_vars: Optional[Dict[str, str]] = None) -> Session:
        """开始新会话
        
        Args:
            user_id: 用户 ID
            working_directory: 工作目录
            environment_vars: 环境变量
            
        Returns:
            Session: 新创建的会话对象
        """
        session = Session(
            user_id=user_id,
            working_directory=working_directory,
            environment_vars=environment_vars or {},
            status=SessionStatus.ACTIVE
        )
        
        self.current_session = session
        self.sessions[session.session_id] = session
        
        logger.info(f"Started new session: {session.session_id}")
        
        # 持久化会话
        if self.storage:
            self._save_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取指定会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Optional[Session]: 会话对象，如果不存在则返回 None
        """
        # 先从缓存查找
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # 从存储加载
        if self.storage:
            session_data = self.storage.load_session(session_id)
            if session_data:
                session = Session.from_dict(session_data)
                self.sessions[session_id] = session
                return session
        
        return None
    
    def get_current_session(self) -> Optional[Session]:
        """获取当前活跃会话
        
        Returns:
            Optional[Session]: 当前会话对象
        """
        return self.current_session
    
    def switch_session(self, session_id: str) -> bool:
        """切换到指定会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            bool: 切换是否成功
        """
        session = self.get_session(session_id)
        if session and session.is_active:
            self.current_session = session
            logger.info(f"Switched to session: {session_id}")
            return True
        
        logger.warning(f"Failed to switch to session: {session_id}")
        return False
    
    def terminate_session(self, session_id: Optional[str] = None):
        """终止会话
        
        Args:
            session_id: 会话 ID，如果为 None 则终止当前会话
        """
        if session_id is None:
            session = self.current_session
        else:
            session = self.get_session(session_id)
        
        if session:
            session.terminate()
            logger.info(f"Terminated session: {session.session_id}")
            
            # 持久化会话
            if self.storage:
                self._save_session(session)
            
            # 如果是当前会话，清除引用
            if self.current_session and self.current_session.session_id == session.session_id:
                self.current_session = None
    
    def cleanup_expired_sessions(self, timeout: int = 3600):
        """清理过期会话
        
        Args:
            timeout: 超时时间（秒），默认 1 小时
        """
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.is_active:
                time_since_activity = (now - session.last_activity).total_seconds()
                if time_since_activity > timeout:
                    session.status = SessionStatus.EXPIRED
                    expired_sessions.append(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    # ========================================================================
    # 命令管理
    # ========================================================================
    
    def add_command(self, user_input: str, suggestion: Suggestion, 
                   result: Optional[ExecutionResult] = None) -> CommandEntry:
        """添加命令到当前会话
        
        Args:
            user_input: 用户原始输入
            suggestion: AI 翻译建议
            result: 执行结果（可选）
            
        Returns:
            CommandEntry: 命令条目对象
        """
        if not self.current_session:
            logger.warning("No active session, starting new session")
            self.start_session()
        
        # 创建命令条目
        command_entry = CommandEntry(
            user_input=user_input,
            translated_command=suggestion.generated_command,
            confidence_score=suggestion.confidence_score,
            status=CommandStatus.PENDING if result is None else CommandStatus.COMPLETED
        )
        
        # 如果有执行结果，更新命令条目
        if result:
            command_entry.output = result.output
            command_entry.error = result.error
            command_entry.return_code = result.return_code
            command_entry.execution_time = result.execution_time
            command_entry.status = CommandStatus.COMPLETED if result.success else CommandStatus.FAILED
        
        # 添加到会话
        self.current_session.add_command(command_entry)
        
        logger.debug(f"Added command to session: {command_entry.command_id}")
        
        # 持久化会话
        if self.storage:
            self._save_session(self.current_session)
        
        return command_entry
    
    def update_command_status(self, command_id: str, status: CommandStatus, 
                             result: Optional[ExecutionResult] = None):
        """更新命令状态
        
        Args:
            command_id: 命令 ID
            status: 新状态
            result: 执行结果（可选）
        """
        if not self.current_session:
            logger.warning("No active session")
            return
        
        # 查找命令
        for cmd in self.current_session.command_history:
            if cmd.command_id == command_id:
                cmd.status = status
                
                # 更新执行结果
                if result:
                    cmd.output = result.output
                    cmd.error = result.error
                    cmd.return_code = result.return_code
                    cmd.execution_time = result.execution_time
                
                logger.debug(f"Updated command status: {command_id} -> {status.value}")
                
                # 持久化会话
                if self.storage:
                    self._save_session(self.current_session)
                
                break
    
    def get_command(self, command_id: str) -> Optional[CommandEntry]:
        """获取指定命令
        
        Args:
            command_id: 命令 ID
            
        Returns:
            Optional[CommandEntry]: 命令条目对象
        """
        if not self.current_session:
            return None
        
        for cmd in self.current_session.command_history:
            if cmd.command_id == command_id:
                return cmd
        
        return None
    
    # ========================================================================
    # 上下文查询
    # ========================================================================
    
    def get_context(self, depth: int = 5) -> Context:
        """获取当前上下文
        
        Args:
            depth: 历史深度，返回最近的 N 条命令
            
        Returns:
            Context: 上下文对象
        """
        if not self.current_session:
            # 如果没有活跃会话，创建一个临时上下文
            return Context(
                session_id="temp",
                command_history=[]
            )
        
        # 获取最近的命令
        recent_commands = self.current_session.get_recent_commands(depth)
        command_history = [cmd.translated_command for cmd in recent_commands]
        
        return Context(
            session_id=self.current_session.session_id,
            user_id=self.current_session.user_id,
            working_directory=self.current_session.working_directory,
            environment_vars=self.current_session.environment_vars,
            command_history=command_history
        )
    
    def get_recent_commands(self, limit: int = 10) -> List[CommandEntry]:
        """获取最近的命令
        
        Args:
            limit: 返回的命令数量
            
        Returns:
            List[CommandEntry]: 命令列表
        """
        if not self.current_session:
            return []
        
        return self.current_session.get_recent_commands(limit)
    
    def get_successful_commands(self) -> List[CommandEntry]:
        """获取所有成功的命令
        
        Returns:
            List[CommandEntry]: 成功的命令列表
        """
        if not self.current_session:
            return []
        
        return self.current_session.get_successful_commands()
    
    def get_failed_commands(self) -> List[CommandEntry]:
        """获取所有失败的命令
        
        Returns:
            List[CommandEntry]: 失败的命令列表
        """
        if not self.current_session:
            return []
        
        return self.current_session.get_failed_commands()
    
    # ========================================================================
    # 快照管理
    # ========================================================================
    
    def create_snapshot(self, description: str = "", 
                       tags: Optional[List[str]] = None) -> ContextSnapshot:
        """创建上下文快照
        
        Args:
            description: 快照描述
            tags: 标签列表
            
        Returns:
            ContextSnapshot: 快照对象
        """
        if not self.current_session:
            raise ValueError("No active session to snapshot")
        
        snapshot = ContextSnapshot(
            session=self.current_session,
            description=description,
            tags=tags or []
        )
        
        logger.info(f"Created context snapshot: {snapshot.snapshot_id}")
        
        # 持久化快照
        if self.storage:
            self.storage.save_snapshot(snapshot.to_dict())
        
        return snapshot
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """恢复上下文快照
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            bool: 恢复是否成功
        """
        if not self.storage:
            logger.error("Storage not available for snapshot restoration")
            return False
        
        snapshot_data = self.storage.load_snapshot(snapshot_id)
        if not snapshot_data:
            logger.error(f"Snapshot not found: {snapshot_id}")
            return False
        
        snapshot = ContextSnapshot.from_dict(snapshot_data)
        self.current_session = snapshot.session
        self.sessions[snapshot.session.session_id] = snapshot.session
        
        logger.info(f"Restored context snapshot: {snapshot_id}")
        return True
    
    # ========================================================================
    # 用户偏好管理
    # ========================================================================
    
    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """获取用户偏好设置
        
        Args:
            user_id: 用户 ID
            
        Returns:
            UserPreferences: 用户偏好对象
        """
        # 先从缓存查找
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # 从存储加载
        if self.storage:
            prefs_data = self.storage.load_user_preferences(user_id)
            if prefs_data:
                prefs = UserPreferences.from_dict(prefs_data)
                self.user_preferences[user_id] = prefs
                return prefs
        
        # 创建默认偏好
        prefs = UserPreferences(user_id=user_id)
        self.user_preferences[user_id] = prefs
        return prefs
    
    def save_user_preferences(self, preferences: UserPreferences):
        """保存用户偏好设置
        
        Args:
            preferences: 用户偏好对象
        """
        self.user_preferences[preferences.user_id] = preferences
        
        if self.storage:
            self.storage.save_user_preferences(preferences.to_dict())
        
        logger.info(f"Saved user preferences: {preferences.user_id}")
    
    # ========================================================================
    # 统计信息
    # ========================================================================
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取当前会话统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "duration": self.current_session.duration,
            "command_count": self.current_session.command_count,
            "successful_commands": self.current_session.successful_commands,
            "failed_commands": self.current_session.failed_commands,
            "start_time": self.current_session.start_time.isoformat(),
            "last_activity": self.current_session.last_activity.isoformat()
        }
    
    # ========================================================================
    # 私有方法
    # ========================================================================
    
    def _save_session(self, session: Session):
        """保存会话到存储
        
        Args:
            session: 会话对象
        """
        if self.storage:
            try:
                self.storage.save_session(session.to_dict())
            except Exception as e:
                logger.error(f"Failed to save session: {e}")
