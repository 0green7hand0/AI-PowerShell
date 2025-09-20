"""Context Manager implementation for tracking state and managing sessions"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import logging

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    ContextManagerInterface, CommandContext, ExecutionResult, 
    Platform, UserRole, StorageInterface
)
from .models import (
    UserSession, UserPreferences, ContextState, HistoryEntry, 
    HistoryFilter, CommandPattern, SuggestionContext, SessionStatus
)
from .history import CommandHistoryManager


class ContextManager(ContextManagerInterface):
    """
    Manages user sessions, context state, and provides context-aware suggestions.
    
    Responsibilities:
    - Track working directory and environment variables
    - Manage user sessions and preferences
    - Provide context-aware command suggestions
    - Maintain session state and history
    """
    
    def __init__(self, storage: StorageInterface, config: Dict[str, Any] = None):
        self.storage = storage
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # In-memory session storage
        self._sessions: Dict[str, UserSession] = {}
        self._context_states: Dict[str, ContextState] = {}
        self._session_lock = threading.RLock()
        
        # Configuration
        self.session_timeout = self.config.get('session_timeout_minutes', 60)
        self.max_recent_commands = self.config.get('max_recent_commands', 10)
        self.max_sessions = self.config.get('max_concurrent_sessions', 100)
        
        # Initialize history manager
        self.history_manager = CommandHistoryManager(storage, config)
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def create_session(self, user_role: UserRole, platform: Platform, 
                      working_directory: str = None) -> str:
        """Create a new user session and return session ID"""
        import uuid
        
        session_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        # Get current working directory if not provided
        if not working_directory:
            working_directory = os.getcwd()
        
        # Create session
        session = UserSession(
            session_id=session_id,
            user_role=user_role,
            platform=platform,
            created_at=current_time,
            last_activity=current_time,
            working_directory=working_directory,
            environment_variables=dict(os.environ)
        )
        
        # Create initial context state
        context_state = ContextState(
            session_id=session_id,
            current_directory=working_directory,
            environment_variables=dict(os.environ),
            recent_commands=[],
            active_modules=[]
        )
        
        with self._session_lock:
            # Clean up old sessions if we're at the limit
            if len(self._sessions) >= self.max_sessions:
                self._cleanup_old_sessions()
                # If still at limit after cleanup, remove oldest session
                if len(self._sessions) >= self.max_sessions:
                    oldest_session_id = min(self._sessions.keys(), 
                                           key=lambda sid: self._sessions[sid].last_activity)
                    self.end_session(oldest_session_id)
            
            self._sessions[session_id] = session
            self._context_states[session_id] = context_state
        
        self.logger.info(f"Created new session {session_id} for {user_role.value} on {platform.value}")
        return session_id
    
    def end_session(self, session_id: str) -> None:
        """End a user session and clean up resources"""
        with self._session_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.status = SessionStatus.INACTIVE
                session.last_activity = datetime.utcnow()
                
                # Save final session state to storage
                self._save_session_to_storage(session)
                
                # Remove from active sessions
                del self._sessions[session_id]
                if session_id in self._context_states:
                    del self._context_states[session_id]
                
                self.logger.info(f"Ended session {session_id}")
    
    def get_current_context(self, session_id: str) -> CommandContext:
        """Get current execution context for a session"""
        with self._session_lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self._sessions[session_id]
            context_state = self._context_states.get(session_id)
            
            if not context_state:
                # Create default context state
                context_state = ContextState(
                    session_id=session_id,
                    current_directory=session.working_directory,
                    environment_variables=session.environment_variables,
                    recent_commands=[],
                    active_modules=session.active_modules
                )
                self._context_states[session_id] = context_state
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            
            return CommandContext(
                current_directory=context_state.current_directory,
                environment_variables=context_state.environment_variables,
                user_role=session.user_role,
                recent_commands=context_state.recent_commands.copy(),
                active_modules=context_state.active_modules.copy(),
                platform=session.platform,
                session_id=session_id
            )
    
    def update_context(self, session_id: str, command: str, result: ExecutionResult) -> None:
        """Update execution context with command results"""
        with self._session_lock:
            if session_id not in self._sessions:
                self.logger.warning(f"Attempted to update context for unknown session {session_id}")
                return
            
            session = self._sessions[session_id]
            context_state = self._context_states.get(session_id)
            
            if not context_state:
                context_state = ContextState(
                    session_id=session_id,
                    current_directory=session.working_directory,
                    environment_variables=session.environment_variables,
                    recent_commands=[],
                    active_modules=session.active_modules
                )
                self._context_states[session_id] = context_state
            
            # Update recent commands
            context_state.recent_commands.append(command)
            if len(context_state.recent_commands) > self.max_recent_commands:
                context_state.recent_commands = context_state.recent_commands[-self.max_recent_commands:]
            
            # Update last command result
            context_state.last_command_result = result
            context_state.timestamp = datetime.utcnow()
            
            # Update session activity and command count
            session.last_activity = datetime.utcnow()
            session.command_count += 1
            
            # Try to detect working directory changes from command output
            self._update_working_directory(context_state, command, result)
            
            # Try to detect loaded modules
            self._update_active_modules(context_state, command, result)
            
            # Add to command history
            try:
                context_snapshot = {
                    'working_directory': context_state.current_directory,
                    'active_modules': context_state.active_modules.copy(),
                    'environment_vars_count': len(context_state.environment_variables)
                }
                self.history_manager.add_history_entry(
                    session_id=session_id,
                    command=command,
                    natural_language_input=None,  # Will be set by caller if available
                    execution_result=result,
                    context_snapshot=context_snapshot
                )
            except Exception as e:
                self.logger.warning(f"Failed to add command to history: {e}")
            
            self.logger.debug(f"Updated context for session {session_id} with command: {command[:50]}...")
    
    def get_session_preferences(self, session_id: str) -> UserPreferences:
        """Get user preferences for a session"""
        try:
            prefs_data = self.storage.get_user_preferences(session_id)
            if prefs_data:
                return UserPreferences(
                    session_id=session_id,
                    preferences=prefs_data.get('preferences', {}),
                    command_patterns=prefs_data.get('command_patterns', {}),
                    favorite_commands=prefs_data.get('favorite_commands', []),
                    preferred_output_format=prefs_data.get('preferred_output_format', 'table'),
                    ai_confidence_threshold=prefs_data.get('ai_confidence_threshold', 0.7),
                    security_confirmation_level=prefs_data.get('security_confirmation_level', 'medium'),
                    created_at=datetime.fromisoformat(prefs_data.get('created_at', datetime.utcnow().isoformat())),
                    updated_at=datetime.fromisoformat(prefs_data.get('updated_at', datetime.utcnow().isoformat()))
                )
        except Exception as e:
            self.logger.warning(f"Failed to load preferences for session {session_id}: {e}")
        
        # Return default preferences
        return UserPreferences(session_id=session_id)
    
    def save_session_preferences(self, preferences: UserPreferences) -> None:
        """Save user preferences for a session"""
        try:
            preferences.updated_at = datetime.utcnow()
            prefs_data = {
                'preferences': preferences.preferences,
                'command_patterns': preferences.command_patterns,
                'favorite_commands': preferences.favorite_commands,
                'preferred_output_format': preferences.preferred_output_format,
                'ai_confidence_threshold': preferences.ai_confidence_threshold,
                'security_confirmation_level': preferences.security_confirmation_level,
                'created_at': preferences.created_at.isoformat(),
                'updated_at': preferences.updated_at.isoformat()
            }
            self.storage.save_user_preferences(preferences.session_id, prefs_data)
            self.logger.debug(f"Saved preferences for session {preferences.session_id}")
        except Exception as e:
            self.logger.error(f"Failed to save preferences for session {preferences.session_id}: {e}")
    
    def get_suggestion_context(self, session_id: str) -> SuggestionContext:
        """Get context for generating command suggestions"""
        context = self.get_current_context(session_id)
        preferences = self.get_session_preferences(session_id)
        patterns = self._get_learned_patterns(session_id)
        
        return SuggestionContext(
            current_directory=context.current_directory,
            recent_commands=context.recent_commands,
            active_modules=context.active_modules,
            user_patterns=patterns,
            environment_variables=context.environment_variables,
            platform=context.platform,
            user_role=context.user_role,
            session_preferences=preferences
        )
    
    def learn_from_command(self, session_id: str, natural_input: str, 
                          command: str, success: bool, user_feedback: str = None) -> None:
        """Learn from user command patterns for future suggestions"""
        try:
            # Update command patterns in preferences
            preferences = self.get_session_preferences(session_id)
            
            # Track command frequency
            if command in preferences.command_patterns:
                preferences.command_patterns[command] += 1
            else:
                preferences.command_patterns[command] = 1
            
            # Add to favorites if successful and used frequently
            if success and preferences.command_patterns[command] >= 3:
                if command not in preferences.favorite_commands:
                    preferences.favorite_commands.append(command)
                    # Keep only top 20 favorites
                    if len(preferences.favorite_commands) > 20:
                        # Sort by frequency and keep top ones
                        sorted_favs = sorted(preferences.favorite_commands, 
                                           key=lambda c: preferences.command_patterns.get(c, 0), 
                                           reverse=True)
                        preferences.favorite_commands = sorted_favs[:20]
            
            self.save_session_preferences(preferences)
            
            # Use history manager for pattern learning
            if natural_input:
                # Create a mock execution result for learning
                result = ExecutionResult(
                    success=success,
                    return_code=0 if success else 1,
                    stdout="",
                    stderr="",
                    execution_time=0.0,
                    platform=self._sessions[session_id].platform,
                    sandbox_used=False
                )
                
                context_snapshot = {
                    'working_directory': self._context_states[session_id].current_directory,
                    'active_modules': self._context_states[session_id].active_modules.copy()
                }
                
                self.history_manager.add_history_entry(
                    session_id=session_id,
                    command=command,
                    natural_language_input=natural_input,
                    execution_result=result,
                    context_snapshot=context_snapshot
                )
            
            self.logger.debug(f"Learned from command for session {session_id}: {command[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to learn from command for session {session_id}: {e}")
    
    def get_command_history(self, session_id: str, filter_criteria: HistoryFilter = None) -> List[HistoryEntry]:
        """Get command history for a session"""
        if not filter_criteria:
            filter_criteria = HistoryFilter(session_id=session_id)
        else:
            filter_criteria.session_id = session_id
        
        return self.history_manager.get_history(filter_criteria)
    
    def search_command_history(self, session_id: str, query: str, limit: int = 50) -> List[HistoryEntry]:
        """Search command history"""
        return self.history_manager.search_history(session_id, query, limit)
    
    def get_command_suggestions(self, session_id: str, natural_input: str) -> List[Dict[str, Any]]:
        """Get personalized command suggestions based on history and patterns"""
        context = self.get_current_context(session_id)
        context_dict = {
            'current_directory': context.current_directory,
            'recent_commands': context.recent_commands,
            'active_modules': context.active_modules,
            'platform': context.platform.value,
            'user_role': context.user_role.value
        }
        
        return self.history_manager.get_command_suggestions(session_id, natural_input, context_dict)
    
    def get_usage_analytics(self, session_id: str, days: int = 30) -> Dict[str, Any]:
        """Get command usage analytics for a session"""
        return self.history_manager.get_usage_analytics(session_id, days)
    
    def update_command_feedback(self, entry_id: str, feedback: str, rating: float) -> None:
        """Update user feedback for a command history entry"""
        self.history_manager.update_user_feedback(entry_id, feedback, rating)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        with self._session_lock:
            return [sid for sid, session in self._sessions.items() 
                   if session.status == SessionStatus.ACTIVE]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        with self._session_lock:
            if session_id not in self._sessions:
                return None
            
            session = self._sessions[session_id]
            context_state = self._context_states.get(session_id)
            
            return {
                'session_id': session.session_id,
                'user_role': session.user_role.value,
                'platform': session.platform.value,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'status': session.status.value,
                'working_directory': session.working_directory,
                'command_count': session.command_count,
                'recent_commands_count': len(context_state.recent_commands) if context_state else 0,
                'active_modules_count': len(session.active_modules)
            }
    
    # Private helper methods
    
    def _update_working_directory(self, context_state: ContextState, 
                                 command: str, result: ExecutionResult) -> None:
        """Try to detect working directory changes from command execution"""
        if not result.success:
            return
        
        # Check for directory change commands
        cmd_lower = command.lower().strip()
        if cmd_lower.startswith(('cd ', 'set-location ', 'sl ', 'chdir ')):
            # Try to extract the new directory from the command
            # This is a simple heuristic - could be improved
            parts = command.split()
            if len(parts) > 1:
                new_dir = parts[1].strip('\'"')
                if os.path.isabs(new_dir):
                    context_state.current_directory = new_dir
                else:
                    # Relative path
                    try:
                        new_path = os.path.join(context_state.current_directory, new_dir)
                        context_state.current_directory = os.path.normpath(new_path)
                    except Exception:
                        pass  # Keep current directory if path resolution fails
    
    def _update_active_modules(self, context_state: ContextState, 
                              command: str, result: ExecutionResult) -> None:
        """Try to detect loaded PowerShell modules from command execution"""
        if not result.success:
            return
        
        cmd_lower = command.lower().strip()
        
        # Check for module import commands
        if cmd_lower.startswith(('import-module ', 'ipmo ')):
            parts = command.split()
            if len(parts) > 1:
                module_name = parts[1].strip('\'"')
                if module_name not in context_state.active_modules:
                    context_state.active_modules.append(module_name)
        
        # Check for module removal commands
        elif cmd_lower.startswith(('remove-module ', 'rmo ')):
            parts = command.split()
            if len(parts) > 1:
                module_name = parts[1].strip('\'"')
                if module_name in context_state.active_modules:
                    context_state.active_modules.remove(module_name)
    
    def _get_learned_patterns(self, session_id: str) -> List[CommandPattern]:
        """Get learned command patterns for a session"""
        # This would typically load from storage
        # For now, return empty list - will be implemented with storage
        return []
    
    def _update_command_pattern(self, session_id: str, natural_input: str, 
                               command: str, success: bool) -> None:
        """Update or create a command pattern based on usage"""
        # This would typically update patterns in storage
        # Implementation depends on storage backend
        pass
    
    def _save_session_to_storage(self, session: UserSession) -> None:
        """Save session data to persistent storage"""
        try:
            session_data = {
                'session_id': session.session_id,
                'user_role': session.user_role.value,
                'platform': session.platform.value,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'status': session.status.value,
                'working_directory': session.working_directory,
                'command_count': session.command_count
            }
            # Save to storage (implementation depends on storage backend)
            self.logger.debug(f"Saved session {session.session_id} to storage")
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {e}")
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up expired or old sessions"""
        current_time = datetime.utcnow()
        timeout_delta = timedelta(minutes=self.session_timeout)
        
        sessions_to_remove = []
        
        for session_id, session in self._sessions.items():
            if (current_time - session.last_activity) > timeout_delta:
                session.status = SessionStatus.EXPIRED
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            self.end_session(session_id)
        
        if sessions_to_remove:
            self.logger.info(f"Cleaned up {len(sessions_to_remove)} expired sessions")
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread for session cleanup"""
        import threading
        import time
        
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    with self._session_lock:
                        self._cleanup_old_sessions()
                except Exception as e:
                    self.logger.error(f"Error in cleanup thread: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        self.logger.info("Started session cleanup thread")