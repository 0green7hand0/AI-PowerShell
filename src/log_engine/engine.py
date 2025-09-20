"""
Logging Engine Implementation

Provides comprehensive full-chain logging with correlation tracking,
structured JSON output, and audit trail capabilities.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TextIO
from dataclasses import asdict
import threading
from contextlib import contextmanager

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    LoggingEngineInterface, AuditEntry, AuditEventType, ValidationResult,
    ExecutionResult, PerformanceMetrics, LogLevel, LogFormat, LogOutput
)
from config.models import LoggingConfig


class CorrelationContext:
    """Thread-local storage for correlation IDs"""
    
    def __init__(self):
        self._local = threading.local()
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for current thread"""
        self._local.correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for current thread"""
        return getattr(self._local, 'correlation_id', None)
    
    def clear_correlation_id(self) -> None:
        """Clear correlation ID for current thread"""
        if hasattr(self._local, 'correlation_id'):
            delattr(self._local, 'correlation_id')


class LogFormatter:
    """Handles different log output formats"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.sensitive_fields = {
            'password', 'token', 'key', 'secret', 'credential',
            'auth', 'authorization', 'bearer'
        }
    
    def format_log_entry(self, entry: Dict[str, Any]) -> str:
        """Format log entry according to configuration"""
        if self.config.sensitive_data_masking:
            entry = self._mask_sensitive_data(entry)
        
        if self.config.log_format == LogFormat.JSON:
            return json.dumps(entry, default=self._json_serializer, ensure_ascii=False)
        elif self.config.log_format == LogFormat.STRUCTURED:
            return self._format_structured(entry)
        else:  # TEXT format
            return self._format_text(entry)
    
    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive information in log data"""
        if not isinstance(data, dict):
            return data
        
        masked_data = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                masked_data[key] = "***MASKED***"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            elif isinstance(value, str) and len(value) > 50:
                # Potentially sensitive long strings
                masked_data[key] = value[:20] + "...***TRUNCATED***"
            else:
                masked_data[key] = value
        
        return masked_data
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and other objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    def _format_structured(self, entry: Dict[str, Any]) -> str:
        """Format as structured text"""
        timestamp = entry.get('timestamp', datetime.utcnow().isoformat())
        level = entry.get('level', 'INFO')
        correlation_id = entry.get('correlation_id', 'N/A')
        event_type = entry.get('event_type', 'unknown')
        
        lines = [
            f"[{timestamp}] {level} [{correlation_id}] {event_type}"
        ]
        
        for key, value in entry.items():
            if key not in ['timestamp', 'level', 'correlation_id', 'event_type']:
                lines.append(f"  {key}: {value}")
        
        return '\n'.join(lines)
    
    def _format_text(self, entry: Dict[str, Any]) -> str:
        """Format as simple text"""
        timestamp = entry.get('timestamp', datetime.utcnow().isoformat())
        level = entry.get('level', 'INFO')
        correlation_id = entry.get('correlation_id', 'N/A')
        message = entry.get('message', str(entry))
        
        return f"[{timestamp}] {level} [{correlation_id}] {message}"


class LogWriter:
    """Handles writing logs to different outputs"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.file_handles: Dict[str, TextIO] = {}
        self._setup_file_logging()
    
    def _setup_file_logging(self):
        """Setup file logging handlers"""
        if LogOutput.FILE in self.config.log_output:
            # Ensure log directory exists
            log_path = Path(self.config.audit_log_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup performance log directory
            perf_path = Path(self.config.performance_log_path)
            perf_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write_log(self, formatted_entry: str, log_type: str = "audit") -> None:
        """Write formatted log entry to configured outputs"""
        if LogOutput.CONSOLE in self.config.log_output:
            print(formatted_entry)
        
        if LogOutput.FILE in self.config.log_output:
            log_file = (self.config.audit_log_path if log_type == "audit" 
                       else self.config.performance_log_path)
            
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(formatted_entry + '\n')
                    f.flush()
            except Exception as e:
                # Fallback to console if file writing fails
                print(f"Failed to write to log file {log_file}: {e}")
                print(formatted_entry)
    
    def close(self):
        """Close all file handles"""
        for handle in self.file_handles.values():
            try:
                handle.close()
            except Exception:
                pass
        self.file_handles.clear()


class LoggingEngine(LoggingEngineInterface):
    """
    Main logging engine implementation with correlation tracking and audit trails
    """
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.correlation_context = CorrelationContext()
        self.formatter = LogFormatter(config)
        self.writer = LogWriter(config)
        self.audit_entries: List[AuditEntry] = []
        self._lock = threading.Lock()
        
        # Setup Python logging integration
        self._setup_python_logging()
    
    def _setup_python_logging(self):
        """Setup integration with Python's logging module"""
        # Create custom handler that integrates with our logging system
        class CorrelationHandler(logging.Handler):
            def __init__(self, logging_engine):
                super().__init__()
                self.logging_engine = logging_engine
            
            def emit(self, record):
                correlation_id = self.logging_engine.correlation_context.get_correlation_id()
                if correlation_id:
                    # Add correlation ID to log record
                    record.correlation_id = correlation_id
        
        # Add our handler to root logger
        handler = CorrelationHandler(self)
        logging.getLogger().addHandler(handler)
    
    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID"""
        return f"req_{uuid.uuid4().hex[:12]}"
    
    @contextmanager
    def correlation_context_manager(self, correlation_id: Optional[str] = None):
        """Context manager for correlation ID tracking"""
        if correlation_id is None:
            correlation_id = self.generate_correlation_id()
        
        self.correlation_context.set_correlation_id(correlation_id)
        try:
            yield correlation_id
        finally:
            self.correlation_context.clear_correlation_id()
    
    def _create_log_entry(self, event_type: AuditEventType, correlation_id: str,
                         session_id: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized log entry"""
        entry = {
            'correlation_id': correlation_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type.value,
            'level': self.config.log_level.value.upper(),
            'component': 'logging_engine'
        }
        
        # Add performance metrics if available
        if 'performance_metrics' in kwargs:
            metrics = kwargs['performance_metrics']
            if isinstance(metrics, PerformanceMetrics):
                entry['performance'] = asdict(metrics)
        
        # Add other data
        entry.update(kwargs)
        
        return entry
    
    def _log_and_store(self, entry: Dict[str, Any], audit_entry: Optional[AuditEntry] = None):
        """Log entry and optionally store in audit trail"""
        formatted_entry = self.formatter.format_log_entry(entry)
        self.writer.write_log(formatted_entry)
        
        if audit_entry:
            with self._lock:
                self.audit_entries.append(audit_entry)
                # Keep only recent entries to prevent memory issues
                if len(self.audit_entries) > 10000:
                    self.audit_entries = self.audit_entries[-5000:]
    
    def log_user_input(self, session_id: str, input_text: str, 
                      timestamp: datetime) -> str:
        """Log user input and return correlation ID"""
        correlation_id = self.generate_correlation_id()
        
        entry = self._create_log_entry(
            AuditEventType.USER_INPUT,
            correlation_id,
            session_id,
            user_input=input_text,
            timestamp=timestamp.isoformat()
        )
        
        audit_entry = AuditEntry(
            correlation_id=correlation_id,
            session_id=session_id,
            timestamp=timestamp,
            event_type=AuditEventType.USER_INPUT,
            user_input=input_text,
            generated_command=None,
            security_validation=None,
            execution_result=None,
            performance_metrics=None,
            error_details=None
        )
        
        self._log_and_store(entry, audit_entry)
        return correlation_id
    
    def log_ai_processing(self, correlation_id: str, input_text: str,
                         generated_command: str, confidence: float) -> None:
        """Log AI processing details"""
        entry = self._create_log_entry(
            AuditEventType.AI_PROCESSING,
            correlation_id,
            "unknown",  # Session ID should be tracked separately
            input_text=input_text,
            generated_command=generated_command,
            confidence_score=confidence,
            processing_component="ai_engine"
        )
        
        self._log_and_store(entry)
    
    def log_security_validation(self, correlation_id: str, command: str,
                               validation_result: ValidationResult) -> None:
        """Log security validation results"""
        entry = self._create_log_entry(
            AuditEventType.SECURITY_VALIDATION,
            correlation_id,
            "unknown",
            command=command,
            validation_result={
                'is_valid': validation_result.is_valid,
                'blocked_reasons': validation_result.blocked_reasons,
                'required_permissions': [p.value for p in validation_result.required_permissions],
                'risk_assessment': validation_result.risk_assessment.value
            },
            processing_component="security_engine"
        )
        
        self._log_and_store(entry)
    
    def log_command_execution(self, correlation_id: str, command: str,
                             execution_result: ExecutionResult) -> None:
        """Log command execution details"""
        entry = self._create_log_entry(
            AuditEventType.COMMAND_EXECUTION,
            correlation_id,
            "unknown",
            command=command,
            execution_result={
                'success': execution_result.success,
                'return_code': execution_result.return_code,
                'execution_time': execution_result.execution_time,
                'platform': execution_result.platform.value,
                'sandbox_used': execution_result.sandbox_used
            },
            processing_component="execution_engine"
        )
        
        self._log_and_store(entry)
    
    def log_error(self, correlation_id: str, error: Exception,
                  context: Dict[str, Any]) -> None:
        """Log error information"""
        entry = self._create_log_entry(
            AuditEventType.ERROR_OCCURRED,
            correlation_id,
            context.get('session_id', 'unknown'),
            error_type=type(error).__name__,
            error_message=str(error),
            error_context=context,
            level="ERROR"
        )
        
        audit_entry = AuditEntry(
            correlation_id=correlation_id,
            session_id=context.get('session_id', 'unknown'),
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.ERROR_OCCURRED,
            user_input=context.get('user_input'),
            generated_command=context.get('generated_command'),
            security_validation=None,
            execution_result=None,
            performance_metrics=None,
            error_details={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context
            }
        )
        
        self._log_and_store(entry, audit_entry)
    
    def get_audit_trail(self, session_id: str, start_time: datetime,
                       end_time: datetime) -> List[AuditEntry]:
        """Retrieve audit trail entries"""
        with self._lock:
            filtered_entries = []
            for entry in self.audit_entries:
                if (entry.session_id == session_id and
                    start_time <= entry.timestamp <= end_time):
                    filtered_entries.append(entry)
            
            return sorted(filtered_entries, key=lambda x: x.timestamp)
    
    def export_logs(self, format_type: str, filter_criteria: Dict[str, Any]) -> str:
        """Export logs in specified format with filtering"""
        # This is a basic implementation - could be enhanced with more sophisticated filtering
        with self._lock:
            filtered_entries = self.audit_entries.copy()
        
        # Apply filters
        if 'session_id' in filter_criteria:
            filtered_entries = [e for e in filtered_entries 
                              if e.session_id == filter_criteria['session_id']]
        
        if 'start_time' in filter_criteria:
            start_time = filter_criteria['start_time']
            filtered_entries = [e for e in filtered_entries if e.timestamp >= start_time]
        
        if 'end_time' in filter_criteria:
            end_time = filter_criteria['end_time']
            filtered_entries = [e for e in filtered_entries if e.timestamp <= end_time]
        
        if 'event_type' in filter_criteria:
            event_type = filter_criteria['event_type']
            filtered_entries = [e for e in filtered_entries if e.event_type == event_type]
        
        # Format output
        if format_type.lower() == 'json':
            return json.dumps([asdict(entry) for entry in filtered_entries], 
                            default=self.formatter._json_serializer, indent=2)
        else:
            # Default to structured text
            lines = []
            for entry in filtered_entries:
                entry_dict = asdict(entry)
                formatted = self.formatter._format_structured(entry_dict)
                lines.append(formatted)
                lines.append("-" * 80)
            return '\n'.join(lines)
    
    def shutdown(self):
        """Cleanup resources"""
        self.writer.close()