"""
Unit tests for the LoggingEngine implementation
"""

import unittest
import tempfile
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from log_engine.engine import LoggingEngine, CorrelationContext, LogFormatter, LogWriter
from config.models import LoggingConfig
from interfaces.base import (
    LogLevel, LogFormat, LogOutput, AuditEventType, ValidationResult,
    ExecutionResult, Platform, RiskLevel, Permission
)


class TestCorrelationContext(unittest.TestCase):
    """Test correlation context management"""
    
    def setUp(self):
        self.context = CorrelationContext()
    
    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID"""
        correlation_id = "test_123"
        self.context.set_correlation_id(correlation_id)
        self.assertEqual(self.context.get_correlation_id(), correlation_id)
    
    def test_clear_correlation_id(self):
        """Test clearing correlation ID"""
        self.context.set_correlation_id("test_123")
        self.context.clear_correlation_id()
        self.assertIsNone(self.context.get_correlation_id())
    
    def test_no_correlation_id_initially(self):
        """Test that no correlation ID exists initially"""
        self.assertIsNone(self.context.get_correlation_id())


class TestLogFormatter(unittest.TestCase):
    """Test log formatting functionality"""
    
    def setUp(self):
        self.config = LoggingConfig(
            log_format=LogFormat.JSON,
            sensitive_data_masking=True
        )
        self.formatter = LogFormatter(self.config)
    
    def test_json_format(self):
        """Test JSON formatting"""
        entry = {
            'correlation_id': 'test_123',
            'timestamp': datetime(2024, 1, 1, 12, 0, 0),
            'message': 'test message'
        }
        
        formatted = self.formatter.format_log_entry(entry)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed['correlation_id'], 'test_123')
        self.assertEqual(parsed['message'], 'test message')
        self.assertIn('timestamp', parsed)
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked"""
        entry = {
            'correlation_id': 'test_123',
            'password': 'secret123',
            'token': 'bearer_token_here',
            'normal_field': 'normal_value'
        }
        
        formatted = self.formatter.format_log_entry(entry)
        parsed = json.loads(formatted)
        
        self.assertEqual(parsed['password'], '***MASKED***')
        self.assertEqual(parsed['token'], '***MASKED***')
        self.assertEqual(parsed['normal_field'], 'normal_value')
    
    def test_structured_format(self):
        """Test structured text formatting"""
        self.config.log_format = LogFormat.STRUCTURED
        formatter = LogFormatter(self.config)
        
        entry = {
            'correlation_id': 'test_123',
            'timestamp': '2024-01-01T12:00:00',
            'level': 'INFO',
            'event_type': 'test_event',
            'message': 'test message'
        }
        
        formatted = formatter.format_log_entry(entry)
        
        self.assertIn('[2024-01-01T12:00:00] INFO [test_123] test_event', formatted)
        self.assertIn('message: test message', formatted)
    
    def test_text_format(self):
        """Test simple text formatting"""
        self.config.log_format = LogFormat.TEXT
        formatter = LogFormatter(self.config)
        
        entry = {
            'correlation_id': 'test_123',
            'timestamp': '2024-01-01T12:00:00',
            'level': 'INFO',
            'message': 'test message'
        }
        
        formatted = formatter.format_log_entry(entry)
        expected = "[2024-01-01T12:00:00] INFO [test_123] test message"
        self.assertEqual(formatted, expected)


class TestLogWriter(unittest.TestCase):
    """Test log writing functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_output=[LogOutput.FILE],
            audit_log_path=os.path.join(self.temp_dir, "audit.log"),
            performance_log_path=os.path.join(self.temp_dir, "performance.log")
        )
        self.writer = LogWriter(self.config)
    
    def tearDown(self):
        self.writer.close()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_to_file(self):
        """Test writing logs to file"""
        test_entry = "Test log entry"
        self.writer.write_log(test_entry)
        
        # Check that file was created and contains the entry
        with open(self.config.audit_log_path, 'r') as f:
            content = f.read()
            self.assertIn(test_entry, content)
    
    def test_write_performance_log(self):
        """Test writing performance logs"""
        test_entry = "Performance log entry"
        self.writer.write_log(test_entry, log_type="performance")
        
        # Check that performance log file was created
        with open(self.config.performance_log_path, 'r') as f:
            content = f.read()
            self.assertIn(test_entry, content)
    
    @patch('builtins.print')
    def test_console_output(self, mock_print):
        """Test console output"""
        self.config.log_output = [LogOutput.CONSOLE]
        writer = LogWriter(self.config)
        
        test_entry = "Console log entry"
        writer.write_log(test_entry)
        
        mock_print.assert_called_with(test_entry)


class TestLoggingEngine(unittest.TestCase):
    """Test main LoggingEngine functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_output=[LogOutput.FILE],
            audit_log_path=os.path.join(self.temp_dir, "audit.log"),
            performance_log_path=os.path.join(self.temp_dir, "performance.log"),
            log_level=LogLevel.DEBUG
        )
        self.engine = LoggingEngine(self.config)
    
    def tearDown(self):
        self.engine.shutdown()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_correlation_id(self):
        """Test correlation ID generation"""
        correlation_id = self.engine.generate_correlation_id()
        
        self.assertIsInstance(correlation_id, str)
        self.assertTrue(correlation_id.startswith('req_'))
        self.assertEqual(len(correlation_id), 16)  # 'req_' + 12 hex chars
    
    def test_correlation_context_manager(self):
        """Test correlation context manager"""
        with self.engine.correlation_context_manager() as correlation_id:
            self.assertIsNotNone(correlation_id)
            self.assertEqual(
                self.engine.correlation_context.get_correlation_id(),
                correlation_id
            )
        
        # Should be cleared after context
        self.assertIsNone(self.engine.correlation_context.get_correlation_id())
    
    def test_log_user_input(self):
        """Test logging user input"""
        session_id = "session_123"
        input_text = "list high CPU processes"
        timestamp = datetime.utcnow()
        
        correlation_id = self.engine.log_user_input(session_id, input_text, timestamp)
        
        self.assertIsNotNone(correlation_id)
        self.assertTrue(correlation_id.startswith('req_'))
        
        # Check that audit entry was created
        self.assertEqual(len(self.engine.audit_entries), 1)
        audit_entry = self.engine.audit_entries[0]
        self.assertEqual(audit_entry.correlation_id, correlation_id)
        self.assertEqual(audit_entry.session_id, session_id)
        self.assertEqual(audit_entry.user_input, input_text)
        self.assertEqual(audit_entry.event_type, AuditEventType.USER_INPUT)
    
    def test_log_ai_processing(self):
        """Test logging AI processing"""
        correlation_id = "test_correlation_123"
        input_text = "list processes"
        generated_command = "Get-Process"
        confidence = 0.95
        
        self.engine.log_ai_processing(correlation_id, input_text, generated_command, confidence)
        
        # Check that log file contains the entry
        with open(self.config.audit_log_path, 'r') as f:
            content = f.read()
            self.assertIn(correlation_id, content)
            self.assertIn(generated_command, content)
            self.assertIn(str(confidence), content)
    
    def test_log_security_validation(self):
        """Test logging security validation"""
        correlation_id = "test_correlation_123"
        command = "Remove-Item -Recurse"
        validation_result = ValidationResult(
            is_valid=False,
            blocked_reasons=["High risk command"],
            required_permissions=[Permission.ADMIN],
            suggested_alternatives=["Use Get-ChildItem instead"],
            risk_assessment=RiskLevel.HIGH
        )
        
        self.engine.log_security_validation(correlation_id, command, validation_result)
        
        # Check that log file contains the entry
        with open(self.config.audit_log_path, 'r') as f:
            content = f.read()
            self.assertIn(correlation_id, content)
            self.assertIn(command, content)
            self.assertIn("false", content.lower())  # is_valid: false
    
    def test_log_command_execution(self):
        """Test logging command execution"""
        correlation_id = "test_correlation_123"
        command = "Get-Process"
        execution_result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Process list output",
            stderr="",
            execution_time=1.5,
            platform=Platform.WINDOWS,
            sandbox_used=True
        )
        
        self.engine.log_command_execution(correlation_id, command, execution_result)
        
        # Check that log file contains the entry
        with open(self.config.audit_log_path, 'r') as f:
            content = f.read()
            self.assertIn(correlation_id, content)
            self.assertIn(command, content)
            self.assertIn("true", content.lower())  # success: true
    
    def test_log_error(self):
        """Test logging errors"""
        correlation_id = "test_correlation_123"
        error = ValueError("Test error message")
        context = {
            'session_id': 'session_123',
            'user_input': 'invalid command',
            'component': 'ai_engine'
        }
        
        self.engine.log_error(correlation_id, error, context)
        
        # Check that audit entry was created
        error_entries = [e for e in self.engine.audit_entries 
                        if e.event_type == AuditEventType.ERROR_OCCURRED]
        self.assertEqual(len(error_entries), 1)
        
        error_entry = error_entries[0]
        self.assertEqual(error_entry.correlation_id, correlation_id)
        self.assertIsNotNone(error_entry.error_details)
        self.assertEqual(error_entry.error_details['error_type'], 'ValueError')
    
    def test_get_audit_trail(self):
        """Test retrieving audit trail"""
        session_id = "session_123"
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow() + timedelta(hours=1)
        
        # Log some entries
        self.engine.log_user_input(session_id, "test input 1", datetime.utcnow())
        self.engine.log_user_input(session_id, "test input 2", datetime.utcnow())
        self.engine.log_user_input("other_session", "other input", datetime.utcnow())
        
        # Get audit trail for specific session
        trail = self.engine.get_audit_trail(session_id, start_time, end_time)
        
        self.assertEqual(len(trail), 2)
        for entry in trail:
            self.assertEqual(entry.session_id, session_id)
            self.assertTrue(start_time <= entry.timestamp <= end_time)
    
    def test_export_logs_json(self):
        """Test exporting logs in JSON format"""
        session_id = "session_123"
        self.engine.log_user_input(session_id, "test input", datetime.utcnow())
        
        filter_criteria = {'session_id': session_id}
        exported = self.engine.export_logs('json', filter_criteria)
        
        # Should be valid JSON
        parsed = json.loads(exported)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['session_id'], session_id)
    
    def test_export_logs_text(self):
        """Test exporting logs in text format"""
        session_id = "session_123"
        self.engine.log_user_input(session_id, "test input", datetime.utcnow())
        
        filter_criteria = {'session_id': session_id}
        exported = self.engine.export_logs('text', filter_criteria)
        
        self.assertIsInstance(exported, str)
        self.assertIn(session_id, exported)
        self.assertIn("test input", exported)


if __name__ == '__main__':
    unittest.main()