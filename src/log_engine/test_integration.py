"""
Unit tests for logging integration interfaces (decorators, filters, etc.)
"""

import unittest
import tempfile
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from log_engine.engine import LoggingEngine
from log_engine.decorators import (
    LoggingDecorator, log_function, logging_context, PerformanceTracker
)
from log_engine.filters import (
    LogFilter, LogQuery, LogSearcher, LogExporter, FilterOperator, SortOrder
)
from config.models import LoggingConfig
from interfaces.base import (
    LogLevel, LogFormat, LogOutput, AuditEntry, AuditEventType,
    ValidationResult, ExecutionResult, Platform, RiskLevel, Permission
)


class TestLoggingDecorator(unittest.TestCase):
    """Test logging decorators"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_output=[LogOutput.FILE],
            audit_log_path=f"{self.temp_dir}/audit.log",
            performance_log_path=f"{self.temp_dir}/performance.log",
            log_level=LogLevel.DEBUG
        )
        self.engine = LoggingEngine(self.config)
        self.decorator = LoggingDecorator(self.engine)
    
    def tearDown(self):
        self.engine.shutdown()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_function_logging_success(self):
        """Test successful function execution logging"""
        
        @self.decorator
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        self.assertEqual(result, 5)
        
        # Check that logs were written
        with open(self.config.audit_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('function_entry', log_content)
            self.assertIn('function_exit', log_content)
            self.assertIn('test_function', log_content)
    
    def test_function_logging_error(self):
        """Test function error logging"""
        
        @self.decorator
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Check that error was logged
        with open(self.config.audit_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('function_error', log_content)
            self.assertIn('ValueError', log_content)
            self.assertIn('Test error', log_content)
    
    def test_performance_logging(self):
        """Test performance metrics logging"""
        
        @LoggingDecorator(self.engine, log_performance=True)
        def slow_function():
            time.sleep(0.01)  # Small delay to measure
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")
        
        # Check performance log
        with open(self.config.performance_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('performance_metrics', log_content)
            self.assertIn('execution_time_ms', log_content)
    
    def test_log_function_decorator(self):
        """Test convenience decorator factory"""
        
        @log_function(self.engine, component_name="test_component")
        def decorated_function(value):
            return value * 2
        
        result = decorated_function(5)
        self.assertEqual(result, 10)
        
        # Check that component name was used
        with open(self.config.audit_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('test_component', log_content)


class TestLoggingContext(unittest.TestCase):
    """Test logging context manager"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_output=[LogOutput.FILE],
            audit_log_path=f"{self.temp_dir}/audit.log",
            log_level=LogLevel.DEBUG
        )
        self.engine = LoggingEngine(self.config)
    
    def tearDown(self):
        self.engine.shutdown()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_successful_operation_context(self):
        """Test successful operation logging with context"""
        
        with logging_context(self.engine, "test_operation", session_id="sess_123") as ctx:
            ctx.add_data("step", "initialization")
            ctx.log_step("validate_input", input_valid=True)
            ctx.add_data("result", "success")
        
        # Check that operation was logged
        with open(self.config.audit_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('operation_start', log_content)
            self.assertIn('operation_complete', log_content)
            self.assertIn('operation_step', log_content)
            self.assertIn('test_operation', log_content)
            self.assertIn('sess_123', log_content)
    
    def test_failed_operation_context(self):
        """Test failed operation logging with context"""
        
        with self.assertRaises(ValueError):
            with logging_context(self.engine, "failing_operation") as ctx:
                ctx.log_step("step1", status="ok")
                raise ValueError("Operation failed")
        
        # Check that error was logged
        with open(self.config.audit_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('operation_start', log_content)
            self.assertIn('operation_error', log_content)
            self.assertIn('ValueError', log_content)
            self.assertIn('Operation failed', log_content)


class TestPerformanceTracker(unittest.TestCase):
    """Test performance tracking functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_output=[LogOutput.FILE],
            performance_log_path=f"{self.temp_dir}/performance.log",
            log_level=LogLevel.DEBUG
        )
        self.engine = LoggingEngine(self.config)
        self.tracker = PerformanceTracker(self.engine)
    
    def tearDown(self):
        self.engine.shutdown()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_operation_tracking(self):
        """Test complete operation tracking"""
        
        correlation_id = self.tracker.start_operation("op1", "test_operation")
        self.assertIsNotNone(correlation_id)
        
        # Add some checkpoints
        self.tracker.checkpoint("op1", "checkpoint1", data="test")
        time.sleep(0.01)  # Small delay
        self.tracker.checkpoint("op1", "checkpoint2", progress=50)
        
        # End operation
        summary = self.tracker.end_operation("op1", final_status="success")
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary['operation_name'], "test_operation")
        self.assertEqual(summary['checkpoints_count'], 2)
        self.assertGreater(summary['total_time_ms'], 0)
        
        # Check performance log
        with open(self.config.performance_log_path, 'r') as f:
            log_content = f.read()
            self.assertIn('performance_checkpoint', log_content)
            self.assertIn('performance_summary', log_content)
            self.assertIn('checkpoint1', log_content)
            self.assertIn('checkpoint2', log_content)


class TestLogFilter(unittest.TestCase):
    """Test log filtering functionality"""
    
    def setUp(self):
        # Create sample audit entries
        self.entries = [
            AuditEntry(
                correlation_id="corr1",
                session_id="sess1",
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                event_type=AuditEventType.USER_INPUT,
                user_input="list processes",
                generated_command=None,
                security_validation=None,
                execution_result=None,
                performance_metrics=None,
                error_details=None
            ),
            AuditEntry(
                correlation_id="corr2",
                session_id="sess1",
                timestamp=datetime(2024, 1, 1, 10, 1, 0),
                event_type=AuditEventType.AI_PROCESSING,
                user_input=None,
                generated_command="Get-Process",
                security_validation=None,
                execution_result=None,
                performance_metrics=None,
                error_details=None
            ),
            AuditEntry(
                correlation_id="corr3",
                session_id="sess2",
                timestamp=datetime(2024, 1, 1, 10, 2, 0),
                event_type=AuditEventType.ERROR_OCCURRED,
                user_input=None,
                generated_command=None,
                security_validation=None,
                execution_result=None,
                performance_metrics=None,
                error_details={"error_type": "ValueError", "error_message": "Invalid input"}
            )
        ]
    
    def test_equals_filter(self):
        """Test equals filter"""
        filter_obj = LogFilter("session_id", FilterOperator.EQUALS, "sess1")
        
        results = [entry for entry in self.entries if filter_obj.apply(entry)]
        self.assertEqual(len(results), 2)
        self.assertTrue(all(entry.session_id == "sess1" for entry in results))
    
    def test_contains_filter(self):
        """Test contains filter"""
        filter_obj = LogFilter("user_input", FilterOperator.CONTAINS, "process")
        
        results = [entry for entry in self.entries if filter_obj.apply(entry)]
        self.assertEqual(len(results), 1)
        self.assertIn("process", results[0].user_input.lower())
    
    def test_nested_field_filter(self):
        """Test filtering on nested fields"""
        filter_obj = LogFilter("error_details.error_type", FilterOperator.EQUALS, "ValueError")
        
        results = [entry for entry in self.entries if filter_obj.apply(entry)]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].error_details["error_type"], "ValueError")
    
    def test_exists_filter(self):
        """Test exists filter"""
        filter_obj = LogFilter("user_input", FilterOperator.EXISTS, None)
        
        results = [entry for entry in self.entries if filter_obj.apply(entry)]
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].user_input)


class TestLogQuery(unittest.TestCase):
    """Test log query functionality"""
    
    def setUp(self):
        # Create sample entries with different timestamps
        self.entries = [
            {"correlation_id": "corr1", "session_id": "sess1", "timestamp": "2024-01-01T10:00:00", 
             "event_type": "user_input", "execution_time_ms": 100},
            {"correlation_id": "corr2", "session_id": "sess1", "timestamp": "2024-01-01T10:01:00", 
             "event_type": "ai_processing", "execution_time_ms": 200},
            {"correlation_id": "corr3", "session_id": "sess2", "timestamp": "2024-01-01T10:02:00", 
             "event_type": "error_occurred", "execution_time_ms": 50}
        ]
    
    def test_single_filter_query(self):
        """Test query with single filter"""
        query = LogQuery().add_filter("session_id", FilterOperator.EQUALS, "sess1")
        
        results = query.execute(self.entries)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(entry["session_id"] == "sess1" for entry in results))
    
    def test_multiple_filters_query(self):
        """Test query with multiple filters"""
        query = (LogQuery()
                .add_filter("session_id", FilterOperator.EQUALS, "sess1")
                .add_filter("event_type", FilterOperator.EQUALS, "user_input"))
        
        results = query.execute(self.entries)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["correlation_id"], "corr1")
    
    def test_sorting_query(self):
        """Test query with sorting"""
        query = LogQuery().sort_by("execution_time_ms", SortOrder.DESC)
        
        results = query.execute(self.entries)
        self.assertEqual(len(results), 3)
        # Should be sorted by execution time descending
        self.assertEqual(results[0]["execution_time_ms"], 200)
        self.assertEqual(results[1]["execution_time_ms"], 100)
        self.assertEqual(results[2]["execution_time_ms"], 50)
    
    def test_pagination_query(self):
        """Test query with pagination"""
        query = LogQuery().paginate(limit=2, offset=1)
        
        results = query.execute(self.entries)
        self.assertEqual(len(results), 2)
        # Should skip first entry and return next 2
        self.assertEqual(results[0]["correlation_id"], "corr2")
        self.assertEqual(results[1]["correlation_id"], "corr3")


class TestLogSearcher(unittest.TestCase):
    """Test log searching functionality"""
    
    def setUp(self):
        self.entries = [
            {"correlation_id": "corr1", "session_id": "sess1", "user_input": "list processes",
             "event_type": "user_input", "timestamp": "2024-01-01T10:00:00"},
            {"correlation_id": "corr1", "session_id": "sess1", "generated_command": "Get-Process",
             "event_type": "ai_processing", "timestamp": "2024-01-01T10:00:30"},
            {"correlation_id": "corr2", "session_id": "sess2", "user_input": "show services",
             "event_type": "user_input", "timestamp": "2024-01-01T10:01:00"},
            {"correlation_id": "corr3", "session_id": "sess1", 
             "event_type": "error_occurred", "timestamp": "2024-01-01T10:02:00",
             "error_details": {"error_type": "ValueError", "error_message": "Invalid command"}}
        ]
        self.searcher = LogSearcher(self.entries)
    
    def test_text_search(self):
        """Test full-text search"""
        results = self.searcher.search_text("process")
        
        self.assertEqual(len(results), 2)  # Should find "processes" and "Get-Process"
    
    def test_correlation_id_search(self):
        """Test search by correlation ID"""
        results = self.searcher.search_by_correlation_id("corr1")
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(entry["correlation_id"] == "corr1" for entry in results))
    
    def test_session_search(self):
        """Test search by session ID"""
        results = self.searcher.search_by_session("sess1")
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(entry["session_id"] == "sess1" for entry in results))
    
    def test_time_range_search(self):
        """Test search by time range"""
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 10, 1, 0)
        
        results = self.searcher.search_by_time_range(start_time, end_time)
        
        self.assertEqual(len(results), 3)  # Should include entries at 10:00:00, 10:00:30, and 10:01:00
    
    def test_error_search(self):
        """Test search for errors"""
        results = self.searcher.search_errors()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["event_type"], "error_occurred")
    
    def test_error_search_by_type(self):
        """Test search for specific error type"""
        results = self.searcher.search_errors(error_type="ValueError")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["error_details"]["error_type"], "ValueError")


class TestLogExporter(unittest.TestCase):
    """Test log export functionality"""
    
    def setUp(self):
        self.entries = [
            {"correlation_id": "corr1", "session_id": "sess1", "timestamp": "2024-01-01T10:00:00",
             "event_type": "user_input", "user_input": "test command"},
            {"correlation_id": "corr2", "session_id": "sess2", "timestamp": "2024-01-01T10:01:00",
             "event_type": "error_occurred", "error_details": {"error_message": "Test error"}}
        ]
        self.exporter = LogExporter(self.entries)
    
    def test_json_export(self):
        """Test JSON export"""
        json_output = self.exporter.export_json()
        
        parsed = json.loads(json_output)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["correlation_id"], "corr1")
    
    def test_json_export_with_query(self):
        """Test JSON export with filtering"""
        query = LogQuery().add_filter("session_id", FilterOperator.EQUALS, "sess1")
        json_output = self.exporter.export_json(query)
        
        parsed = json.loads(json_output)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["session_id"], "sess1")
    
    def test_csv_export(self):
        """Test CSV export"""
        csv_output = self.exporter.export_csv(fields=["correlation_id", "session_id", "event_type"])
        
        lines = csv_output.split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 data rows
        
        # Check header
        self.assertEqual(lines[0], '"correlation_id","session_id","event_type"')
        
        # Check data
        self.assertIn('corr1', lines[1])
        self.assertIn('sess1', lines[1])
        self.assertIn('user_input', lines[1])
    
    def test_summary_report(self):
        """Test summary report generation"""
        report = self.exporter.export_summary_report()
        
        self.assertIn("Total Entries: 2", report)
        self.assertIn("Unique Sessions: 2", report)
        self.assertIn("Event Type Distribution:", report)
        self.assertIn("user_input: 1", report)
        self.assertIn("error_occurred: 1", report)


if __name__ == '__main__':
    unittest.main()