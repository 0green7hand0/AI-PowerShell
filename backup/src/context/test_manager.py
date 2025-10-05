"""Unit tests for ContextManager"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import os
import tempfile
import threading
import time

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Platform, UserRole, ExecutionResult, CommandContext
from context.manager import ContextManager
from context.models import UserSession, UserPreferences, SessionStatus


class MockStorage:
    """Mock storage implementation for testing"""
    
    def __init__(self):
        self.preferences = {}
        self.history = {}
        self.config = {}
    
    def save_user_preferences(self, session_id: str, preferences: dict) -> None:
        self.preferences[session_id] = preferences
    
    def get_user_preferences(self, session_id: str) -> dict:
        return self.preferences.get(session_id, {})
    
    def save_command_history(self, session_id: str, command: str, result: ExecutionResult) -> None:
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append({'command': command, 'result': result})
    
    def get_command_history(self, session_id: str, limit: int = 100) -> list:
        return self.history.get(session_id, [])[:limit]
    
    def save_configuration(self, config: dict) -> None:
        self.config.update(config)
    
    def load_configuration(self) -> dict:
        return self.config.copy()


class TestContextManager(unittest.TestCase):
    """Test cases for ContextManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_storage = MockStorage()
        self.config = {
            'session_timeout_minutes': 30,
            'max_recent_commands': 5,
            'max_concurrent_sessions': 10
        }
        self.context_manager = ContextManager(self.mock_storage, self.config)
    
    def tearDown(self):
        """Clean up after tests"""
        # End all active sessions
        for session_id in self.context_manager.get_active_sessions():
            self.context_manager.end_session(session_id)
    
    def test_create_session(self):
        """Test session creation"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, self.context_manager._sessions)
        self.assertIn(session_id, self.context_manager._context_states)
        
        session = self.context_manager._sessions[session_id]
        self.assertEqual(session.user_role, UserRole.USER)
        self.assertEqual(session.platform, Platform.WINDOWS)
        self.assertEqual(session.status, SessionStatus.ACTIVE)
        self.assertEqual(session.command_count, 0)
    
    def test_create_session_with_working_directory(self):
        """Test session creation with specific working directory"""
        test_dir = "/test/directory"
        session_id = self.context_manager.create_session(
            user_role=UserRole.ADMIN,
            platform=Platform.LINUX,
            working_directory=test_dir
        )
        
        session = self.context_manager._sessions[session_id]
        self.assertEqual(session.working_directory, test_dir)
        
        context_state = self.context_manager._context_states[session_id]
        self.assertEqual(context_state.current_directory, test_dir)
    
    def test_end_session(self):
        """Test session termination"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        self.assertIn(session_id, self.context_manager._sessions)
        
        self.context_manager.end_session(session_id)
        
        self.assertNotIn(session_id, self.context_manager._sessions)
        self.assertNotIn(session_id, self.context_manager._context_states)
    
    def test_get_current_context(self):
        """Test getting current execution context"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.ADMIN,
            platform=Platform.MACOS
        )
        
        context = self.context_manager.get_current_context(session_id)
        
        self.assertIsInstance(context, CommandContext)
        self.assertEqual(context.user_role, UserRole.ADMIN)
        self.assertEqual(context.platform, Platform.MACOS)
        self.assertEqual(context.session_id, session_id)
        self.assertIsInstance(context.recent_commands, list)
        self.assertIsInstance(context.active_modules, list)
        self.assertIsInstance(context.environment_variables, dict)
    
    def test_get_current_context_invalid_session(self):
        """Test getting context for invalid session"""
        with self.assertRaises(ValueError):
            self.context_manager.get_current_context("invalid_session_id")
    
    def test_update_context(self):
        """Test updating execution context"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        # Create mock execution result
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Command executed successfully",
            stderr="",
            execution_time=1.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        command = "Get-Process"
        self.context_manager.update_context(session_id, command, result)
        
        # Check that context was updated
        context = self.context_manager.get_current_context(session_id)
        self.assertIn(command, context.recent_commands)
        
        # Check that session was updated
        session = self.context_manager._sessions[session_id]
        self.assertEqual(session.command_count, 1)
        
        # Check that context state was updated
        context_state = self.context_manager._context_states[session_id]
        self.assertEqual(context_state.last_command_result, result)
    
    def test_update_context_recent_commands_limit(self):
        """Test that recent commands list respects the limit"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="OK",
            stderr="",
            execution_time=1.0,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        # Add more commands than the limit
        max_commands = self.config['max_recent_commands']
        for i in range(max_commands + 3):
            command = f"Get-Process -Id {i}"
            self.context_manager.update_context(session_id, command, result)
        
        context = self.context_manager.get_current_context(session_id)
        self.assertEqual(len(context.recent_commands), max_commands)
        
        # Check that the most recent commands are kept
        self.assertIn(f"Get-Process -Id {max_commands + 2}", context.recent_commands)
        self.assertNotIn("Get-Process -Id 0", context.recent_commands)
    
    def test_working_directory_update(self):
        """Test working directory detection from commands"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS,
            working_directory="C:\\Users"
        )
        
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="",
            stderr="",
            execution_time=1.0,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        # Test absolute path change
        self.context_manager.update_context(session_id, "cd C:\\Windows", result)
        context = self.context_manager.get_current_context(session_id)
        self.assertEqual(context.current_directory, "C:\\Windows")
        
        # Test relative path change
        self.context_manager.update_context(session_id, "cd System32", result)
        context = self.context_manager.get_current_context(session_id)
        self.assertEqual(context.current_directory, "C:\\Windows\\System32")
    
    def test_module_tracking(self):
        """Test PowerShell module tracking"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="",
            stderr="",
            execution_time=1.0,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        # Test module import
        self.context_manager.update_context(session_id, "Import-Module ActiveDirectory", result)
        context = self.context_manager.get_current_context(session_id)
        self.assertIn("ActiveDirectory", context.active_modules)
        
        # Test module removal
        self.context_manager.update_context(session_id, "Remove-Module ActiveDirectory", result)
        context = self.context_manager.get_current_context(session_id)
        self.assertNotIn("ActiveDirectory", context.active_modules)
    
    def test_user_preferences(self):
        """Test user preferences management"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        # Test getting default preferences
        prefs = self.context_manager.get_session_preferences(session_id)
        self.assertEqual(prefs.session_id, session_id)
        self.assertEqual(prefs.preferred_output_format, "table")
        self.assertEqual(prefs.ai_confidence_threshold, 0.7)
        
        # Test saving preferences
        prefs.preferred_output_format = "json"
        prefs.ai_confidence_threshold = 0.8
        prefs.favorite_commands = ["Get-Process", "Get-Service"]
        
        self.context_manager.save_session_preferences(prefs)
        
        # Test loading saved preferences
        loaded_prefs = self.context_manager.get_session_preferences(session_id)
        self.assertEqual(loaded_prefs.preferred_output_format, "json")
        self.assertEqual(loaded_prefs.ai_confidence_threshold, 0.8)
        self.assertEqual(loaded_prefs.favorite_commands, ["Get-Process", "Get-Service"])
    
    def test_learn_from_command(self):
        """Test learning from command patterns"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.USER,
            platform=Platform.WINDOWS
        )
        
        command = "Get-Process | Sort-Object CPU -Descending"
        natural_input = "show processes by CPU usage"
        
        # Learn from successful command multiple times
        for _ in range(3):
            self.context_manager.learn_from_command(
                session_id, natural_input, command, success=True
            )
        
        # Check that command was added to patterns and favorites
        prefs = self.context_manager.get_session_preferences(session_id)
        self.assertEqual(prefs.command_patterns[command], 3)
        self.assertIn(command, prefs.favorite_commands)
    
    def test_suggestion_context(self):
        """Test getting suggestion context"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.ADMIN,
            platform=Platform.LINUX
        )
        
        # Add some context
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="",
            stderr="",
            execution_time=1.0,
            platform=Platform.LINUX,
            sandbox_used=False
        )
        
        self.context_manager.update_context(session_id, "Get-Process", result)
        
        suggestion_context = self.context_manager.get_suggestion_context(session_id)
        
        self.assertEqual(suggestion_context.platform, Platform.LINUX)
        self.assertEqual(suggestion_context.user_role, UserRole.ADMIN)
        self.assertIn("Get-Process", suggestion_context.recent_commands)
        self.assertIsInstance(suggestion_context.session_preferences, UserPreferences)
    
    def test_session_info(self):
        """Test getting session information"""
        session_id = self.context_manager.create_session(
            user_role=UserRole.ADMIN,
            platform=Platform.MACOS
        )
        
        info = self.context_manager.get_session_info(session_id)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['session_id'], session_id)
        self.assertEqual(info['user_role'], 'admin')
        self.assertEqual(info['platform'], 'macos')
        self.assertEqual(info['status'], 'active')
        self.assertEqual(info['command_count'], 0)
    
    def test_session_info_invalid_session(self):
        """Test getting info for invalid session"""
        info = self.context_manager.get_session_info("invalid_session")
        self.assertIsNone(info)
    
    def test_active_sessions(self):
        """Test getting active sessions list"""
        # Create multiple sessions
        session1 = self.context_manager.create_session(UserRole.USER, Platform.WINDOWS)
        session2 = self.context_manager.create_session(UserRole.ADMIN, Platform.LINUX)
        
        active_sessions = self.context_manager.get_active_sessions()
        
        self.assertIn(session1, active_sessions)
        self.assertIn(session2, active_sessions)
        self.assertEqual(len(active_sessions), 2)
        
        # End one session
        self.context_manager.end_session(session1)
        
        active_sessions = self.context_manager.get_active_sessions()
        self.assertNotIn(session1, active_sessions)
        self.assertIn(session2, active_sessions)
        self.assertEqual(len(active_sessions), 1)
    
    def test_max_sessions_limit(self):
        """Test maximum concurrent sessions limit"""
        max_sessions = self.config['max_concurrent_sessions']
        
        # Create sessions up to the limit
        session_ids = []
        for i in range(max_sessions):
            session_id = self.context_manager.create_session(UserRole.USER, Platform.WINDOWS)
            session_ids.append(session_id)
        
        self.assertEqual(len(self.context_manager._sessions), max_sessions)
        
        # Creating one more should trigger cleanup
        new_session = self.context_manager.create_session(UserRole.USER, Platform.WINDOWS)
        
        # Should still be at or below the limit
        self.assertLessEqual(len(self.context_manager._sessions), max_sessions)
        self.assertIn(new_session, self.context_manager._sessions)
    
    @patch('time.sleep')
    def test_session_cleanup_thread(self, mock_sleep):
        """Test automatic session cleanup"""
        # Create a session
        session_id = self.context_manager.create_session(UserRole.USER, Platform.WINDOWS)
        
        # Manually set last activity to old time
        session = self.context_manager._sessions[session_id]
        session.last_activity = datetime.utcnow() - timedelta(hours=2)
        
        # Trigger cleanup manually
        self.context_manager._cleanup_old_sessions()
        
        # Session should be removed
        self.assertNotIn(session_id, self.context_manager._sessions)
    
    def test_thread_safety(self):
        """Test thread safety of context manager operations"""
        session_ids = []
        errors = []
        
        def create_sessions():
            try:
                for i in range(10):
                    session_id = self.context_manager.create_session(UserRole.USER, Platform.WINDOWS)
                    session_ids.append(session_id)
                    time.sleep(0.01)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)
        
        def update_contexts():
            try:
                for _ in range(20):
                    if session_ids:
                        session_id = session_ids[0] if session_ids else None
                        if session_id and session_id in self.context_manager._sessions:
                            result = ExecutionResult(
                                success=True,
                                return_code=0,
                                stdout="",
                                stderr="",
                                execution_time=1.0,
                                platform=Platform.WINDOWS,
                                sandbox_used=False
                            )
                            self.context_manager.update_context(session_id, "Get-Process", result)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        # Run operations in parallel
        threads = []
        for _ in range(3):
            t1 = threading.Thread(target=create_sessions)
            t2 = threading.Thread(target=update_contexts)
            threads.extend([t1, t2])
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Check that no errors occurred
        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        
        # Clean up created sessions
        for session_id in session_ids:
            if session_id in self.context_manager._sessions:
                self.context_manager.end_session(session_id)


if __name__ == '__main__':
    unittest.main()