"""Unit tests for CommandHistoryManager"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Platform, ExecutionResult
from context.history import CommandHistoryManager, CommandTokenizer, PatternMatcher
from context.models import HistoryEntry, HistoryFilter, CommandPattern


class MockStorage:
    """Mock storage implementation for testing"""
    
    def __init__(self):
        self.history = {}
        self.preferences = {}
    
    def save_command_history(self, session_id: str, command: str, result: ExecutionResult) -> None:
        if session_id not in self.history:
            self.history[session_id] = []
        self.history[session_id].append({
            'command': command,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_command_history(self, session_id: str, limit: int = 100) -> list:
        return self.history.get(session_id, [])[:limit]
    
    def save_user_preferences(self, session_id: str, preferences: dict) -> None:
        self.preferences[session_id] = preferences
    
    def get_user_preferences(self, session_id: str) -> dict:
        return self.preferences.get(session_id, {})
    
    def save_configuration(self, config: dict) -> None:
        pass
    
    def load_configuration(self) -> dict:
        return {}


class TestCommandHistoryManager(unittest.TestCase):
    """Test cases for CommandHistoryManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_storage = MockStorage()
        self.config = {
            'max_history_entries': 1000,
            'pattern_min_occurrences': 2,
            'pattern_confidence_threshold': 0.6,
            'learning_window_days': 30
        }
        self.history_manager = CommandHistoryManager(self.mock_storage, self.config)
        
        # Sample execution result
        self.success_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Command executed successfully",
            stderr="",
            execution_time=1.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        
        self.failure_result = ExecutionResult(
            success=False,
            return_code=1,
            stdout="",
            stderr="Command not recognized",
            execution_time=0.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
    
    def test_add_history_entry(self):
        """Test adding a command to history"""
        session_id = "test_session_1"
        command = "Get-Process"
        natural_input = "show running processes"
        
        entry_id = self.history_manager.add_history_entry(
            session_id=session_id,
            command=command,
            natural_language_input=natural_input,
            execution_result=self.success_result
        )
        
        self.assertIsNotNone(entry_id)
        
        # Check that entry was added to cache
        self.assertIn(session_id, self.history_manager._history_cache)
        self.assertEqual(len(self.history_manager._history_cache[session_id]), 1)
        
        entry = self.history_manager._history_cache[session_id][0]
        self.assertEqual(entry.command, command)
        self.assertEqual(entry.natural_language_input, natural_input)
        self.assertEqual(entry.execution_result, self.success_result)
    
    def test_get_history_with_filter(self):
        """Test retrieving history with filtering"""
        session_id = "test_session_2"
        
        # Add multiple entries
        commands = ["Get-Process", "Get-Service", "Stop-Service"]
        for i, command in enumerate(commands):
            self.history_manager.add_history_entry(
                session_id=session_id,
                command=command,
                natural_language_input=f"command {i}",
                execution_result=self.success_result if i % 2 == 0 else self.failure_result
            )
        
        # Test basic retrieval
        filter_criteria = HistoryFilter(session_id=session_id)
        history = self.history_manager.get_history(filter_criteria)
        self.assertEqual(len(history), 3)
        
        # Test success-only filter
        filter_criteria = HistoryFilter(session_id=session_id, success_only=True)
        history = self.history_manager.get_history(filter_criteria)
        self.assertEqual(len(history), 2)  # Only successful commands
        
        # Test command pattern filter
        filter_criteria = HistoryFilter(session_id=session_id, command_pattern="Get-.*")
        history = self.history_manager.get_history(filter_criteria)
        self.assertEqual(len(history), 2)  # Get-Process and Get-Service
        
        # Test limit
        filter_criteria = HistoryFilter(session_id=session_id, limit=2)
        history = self.history_manager.get_history(filter_criteria)
        self.assertEqual(len(history), 2)
    
    def test_search_history(self):
        """Test searching command history"""
        session_id = "test_session_3"
        
        # Add entries with different commands
        commands = [
            "Get-Process -Name chrome",
            "Get-Service -Name spooler",
            "Stop-Process -Id 1234"
        ]
        
        for command in commands:
            self.history_manager.add_history_entry(
                session_id=session_id,
                command=command,
                natural_language_input="test input",
                execution_result=self.success_result
            )
        
        # Search for "Process" commands
        results = self.history_manager.search_history(session_id, "Process")
        self.assertEqual(len(results), 2)  # Get-Process and Stop-Process
        
        # Search for specific parameter
        results = self.history_manager.search_history(session_id, "Name")
        self.assertEqual(len(results), 2)  # Commands with -Name parameter
    
    def test_command_suggestions_pattern_based(self):
        """Test getting command suggestions based on patterns"""
        session_id = "test_session_4"
        
        # Add repeated successful commands to build patterns
        natural_inputs = [
            "show running processes",
            "list running processes", 
            "display running processes"
        ]
        command = "Get-Process"
        
        for natural_input in natural_inputs:
            self.history_manager.add_history_entry(
                session_id=session_id,
                command=command,
                natural_language_input=natural_input,
                execution_result=self.success_result
            )
        
        # Get suggestions for similar input
        suggestions = self.history_manager.get_command_suggestions(
            session_id, "show processes"
        )
        
        self.assertGreater(len(suggestions), 0)
        
        # Check that at least one suggestion is the expected command
        suggested_commands = [s['command'] for s in suggestions]
        self.assertIn(command, suggested_commands)
    
    def test_command_suggestions_history_based(self):
        """Test getting suggestions based on similar historical commands"""
        session_id = "test_session_5"
        
        # Add a command with natural language input
        self.history_manager.add_history_entry(
            session_id=session_id,
            command="Get-EventLog -LogName System -Newest 10",
            natural_language_input="show recent system events",
            execution_result=self.success_result
        )
        
        # Get suggestions for similar input
        suggestions = self.history_manager.get_command_suggestions(
            session_id, "show system events"
        )
        
        self.assertGreater(len(suggestions), 0)
        
        # Check that suggestion includes the historical command
        suggested_commands = [s['command'] for s in suggestions]
        self.assertIn("Get-EventLog -LogName System -Newest 10", suggested_commands)
    
    def test_learned_patterns_generation(self):
        """Test generation of learned patterns from history"""
        session_id = "test_session_6"
        
        # Add multiple similar commands to create a pattern
        similar_commands = [
            ("list processes", "Get-Process"),
            ("show processes", "Get-Process"),
            ("display processes", "Get-Process")
        ]
        
        for natural_input, command in similar_commands:
            self.history_manager.add_history_entry(
                session_id=session_id,
                command=command,
                natural_language_input=natural_input,
                execution_result=self.success_result
            )
        
        # Generate patterns
        patterns = self.history_manager.get_learned_patterns(session_id)
        
        self.assertGreater(len(patterns), 0)
        
        # Check pattern properties - find the pattern with highest usage
        pattern = max(patterns, key=lambda p: p.usage_count)
        self.assertEqual(pattern.session_id, session_id)
        self.assertEqual(pattern.usage_count, 3)  # All three commands should be grouped
        self.assertEqual(pattern.success_rate, 1.0)
        self.assertGreater(pattern.confidence_score, 0.6)
    
    def test_user_feedback_update(self):
        """Test updating user feedback for history entries"""
        session_id = "test_session_7"
        
        # Add a history entry
        entry_id = self.history_manager.add_history_entry(
            session_id=session_id,
            command="Get-Process",
            natural_language_input="show processes",
            execution_result=self.success_result
        )
        
        # Update feedback
        feedback = "This command worked perfectly"
        rating = 0.9
        
        self.history_manager.update_user_feedback(entry_id, feedback, rating)
        
        # Check that feedback was updated
        entry = self.history_manager._history_cache[session_id][0]
        self.assertEqual(entry.user_feedback, feedback)
        self.assertEqual(entry.success_rating, rating)
    
    def test_usage_analytics(self):
        """Test getting usage analytics"""
        session_id = "test_session_8"
        
        # Add various commands with different success rates
        commands_data = [
            ("Get-Process", True),
            ("Get-Service", True),
            ("Get-Process", True),
            ("Invalid-Command", False),
            ("Get-Process", True)
        ]
        
        for command, success in commands_data:
            result = self.success_result if success else self.failure_result
            self.history_manager.add_history_entry(
                session_id=session_id,
                command=command,
                natural_language_input="test input",
                execution_result=result
            )
        
        # Get analytics
        analytics = self.history_manager.get_usage_analytics(session_id, days=30)
        
        self.assertEqual(analytics['total_commands'], 5)
        self.assertEqual(analytics['successful_commands'], 4)
        self.assertEqual(analytics['success_rate'], 0.8)
        
        # Check most used commands
        most_used = analytics['most_used_commands']
        self.assertEqual(most_used[0][0], "Get-Process")  # Most frequent command
        self.assertEqual(most_used[0][1], 3)  # Used 3 times
    
    def test_cleanup_old_history(self):
        """Test cleaning up old history entries"""
        session_id = "test_session_9"
        
        # Add entries with different timestamps
        old_entry = self.history_manager.add_history_entry(
            session_id=session_id,
            command="Old-Command",
            natural_language_input="old command",
            execution_result=self.success_result
        )
        
        # Manually set old timestamp
        if session_id in self.history_manager._history_cache:
            self.history_manager._history_cache[session_id][0].timestamp = \
                datetime.utcnow() - timedelta(days=100)
        
        # Add recent entry
        recent_entry = self.history_manager.add_history_entry(
            session_id=session_id,
            command="Recent-Command",
            natural_language_input="recent command",
            execution_result=self.success_result
        )
        
        # Cleanup old entries (keep 30 days)
        removed_count = self.history_manager.cleanup_old_history(session_id, days_to_keep=30)
        
        self.assertEqual(removed_count, 1)
        
        # Check that only recent entry remains
        remaining_entries = self.history_manager._history_cache[session_id]
        self.assertEqual(len(remaining_entries), 1)
        self.assertEqual(remaining_entries[0].command, "Recent-Command")
    
    def test_history_cache_size_limit(self):
        """Test that history cache respects size limits"""
        session_id = "test_session_10"
        
        # Set a small cache limit for testing
        original_limit = self.history_manager.max_history_entries
        self.history_manager.max_history_entries = 3
        
        try:
            # Add more entries than the limit
            for i in range(5):
                self.history_manager.add_history_entry(
                    session_id=session_id,
                    command=f"Command-{i}",
                    natural_language_input=f"input {i}",
                    execution_result=self.success_result
                )
            
            # Check that cache size is limited
            cached_entries = self.history_manager._history_cache[session_id]
            self.assertEqual(len(cached_entries), 3)
            
            # Check that most recent entries are kept
            commands = [entry.command for entry in cached_entries]
            self.assertIn("Command-4", commands)  # Most recent
            self.assertIn("Command-3", commands)
            self.assertIn("Command-2", commands)
            self.assertNotIn("Command-0", commands)  # Oldest should be removed
            
        finally:
            # Restore original limit
            self.history_manager.max_history_entries = original_limit


class TestCommandTokenizer(unittest.TestCase):
    """Test cases for CommandTokenizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tokenizer = CommandTokenizer()
    
    def test_tokenize_natural_language(self):
        """Test natural language tokenization"""
        text = "Show me the running processes on the system"
        tokens = self.tokenizer.tokenize_natural_language(text)
        
        # Should extract meaningful words and remove stop words
        expected_tokens = ["show", "running", "processes", "system"]
        self.assertEqual(set(tokens), set(expected_tokens))
    
    def test_tokenize_command(self):
        """Test PowerShell command tokenization"""
        command = "Get-Process -Name chrome | Sort-Object CPU"
        tokens = self.tokenizer.tokenize_command(command)
        
        # Should extract cmdlets and parameters
        self.assertIn("Get-Process", tokens)
        self.assertIn("Sort-Object", tokens)
        self.assertIn("-Name", tokens)
    
    def test_tokenize_empty_input(self):
        """Test tokenization with empty input"""
        self.assertEqual(self.tokenizer.tokenize_natural_language(""), [])
        self.assertEqual(self.tokenizer.tokenize_command(""), [])


class TestPatternMatcher(unittest.TestCase):
    """Test cases for PatternMatcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.matcher = PatternMatcher()
    
    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical patterns"""
        pattern1 = "show processes system"
        pattern2 = "show processes system"
        
        similarity = self.matcher.calculate_similarity(pattern1, pattern2)
        self.assertEqual(similarity, 1.0)
    
    def test_calculate_similarity_partial(self):
        """Test similarity calculation for partially matching patterns"""
        pattern1 = "show running processes"
        pattern2 = "show processes system"
        
        similarity = self.matcher.calculate_similarity(pattern1, pattern2)
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)
    
    def test_calculate_similarity_no_match(self):
        """Test similarity calculation for non-matching patterns"""
        pattern1 = "show processes"
        pattern2 = "list services"
        
        similarity = self.matcher.calculate_similarity(pattern1, pattern2)
        self.assertEqual(similarity, 0.0)
    
    def test_calculate_similarity_empty(self):
        """Test similarity calculation with empty patterns"""
        self.assertEqual(self.matcher.calculate_similarity("", ""), 1.0)
        self.assertEqual(self.matcher.calculate_similarity("test", ""), 0.0)
        self.assertEqual(self.matcher.calculate_similarity("", "test"), 0.0)


if __name__ == '__main__':
    unittest.main()