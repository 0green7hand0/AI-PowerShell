"""
Logging decorators and context managers for automatic logging integration
"""

import functools
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union
from contextlib import contextmanager

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import PerformanceMetrics, AuditEventType
from log_engine.engine import LoggingEngine


class LoggingDecorator:
    """Decorator for automatic function logging with performance tracking"""
    
    def __init__(self, logging_engine: LoggingEngine, 
                 log_entry: bool = True, log_exit: bool = True,
                 log_performance: bool = True, log_errors: bool = True,
                 component_name: Optional[str] = None):
        self.logging_engine = logging_engine
        self.log_entry = log_entry
        self.log_exit = log_exit
        self.log_performance = log_performance
        self.log_errors = log_errors
        self.component_name = component_name
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or generate correlation ID
            correlation_id = self.logging_engine.correlation_context.get_correlation_id()
            if not correlation_id:
                correlation_id = self.logging_engine.generate_correlation_id()
                self.logging_engine.correlation_context.set_correlation_id(correlation_id)
            
            component = self.component_name or func.__module__
            function_name = f"{component}.{func.__name__}"
            
            # Performance tracking
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                # Log function entry
                if self.log_entry:
                    self._log_function_entry(correlation_id, function_name, args, kwargs)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate performance metrics
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                end_memory = self._get_memory_usage()
                memory_delta = end_memory - start_memory
                
                # Log function exit
                if self.log_exit:
                    self._log_function_exit(correlation_id, function_name, result, execution_time)
                
                # Log performance metrics
                if self.log_performance:
                    self._log_performance_metrics(
                        correlation_id, function_name, execution_time, 
                        memory_delta, end_memory
                    )
                
                return result
                
            except Exception as e:
                # Calculate performance metrics for error case
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000
                
                # Log error
                if self.log_errors:
                    self._log_function_error(correlation_id, function_name, e, execution_time)
                
                raise
        
        return wrapper
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback if psutil is not available
            return 0.0
    
    def _log_function_entry(self, correlation_id: str, function_name: str, 
                           args: tuple, kwargs: dict):
        """Log function entry"""
        entry = {
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'function_entry',
            'level': 'DEBUG',
            'component': 'function_tracer',
            'function_name': function_name,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys()) if kwargs else []
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry)
    
    def _log_function_exit(self, correlation_id: str, function_name: str, 
                          result: Any, execution_time: float):
        """Log function exit"""
        entry = {
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'function_exit',
            'level': 'DEBUG',
            'component': 'function_tracer',
            'function_name': function_name,
            'execution_time_ms': execution_time,
            'result_type': type(result).__name__ if result is not None else 'None'
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry)
    
    def _log_performance_metrics(self, correlation_id: str, function_name: str,
                                execution_time: float, memory_delta: float, 
                                current_memory: float):
        """Log performance metrics"""
        metrics = PerformanceMetrics(
            memory_usage_mb=current_memory,
            cpu_usage_percent=0.0,  # Would need more complex tracking for CPU
            processing_time_ms=execution_time
        )
        
        entry = {
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'performance_metrics',
            'level': 'INFO',
            'component': 'performance_tracker',
            'function_name': function_name,
            'performance': {
                'execution_time_ms': execution_time,
                'memory_usage_mb': current_memory,
                'memory_delta_mb': memory_delta
            }
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry, log_type="performance")
    
    def _log_function_error(self, correlation_id: str, function_name: str,
                           error: Exception, execution_time: float):
        """Log function error"""
        entry = {
            'correlation_id': correlation_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'function_error',
            'level': 'ERROR',
            'component': 'function_tracer',
            'function_name': function_name,
            'execution_time_ms': execution_time,
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry)


def log_function(logging_engine: LoggingEngine, **decorator_kwargs):
    """Convenience decorator factory for function logging"""
    return LoggingDecorator(logging_engine, **decorator_kwargs)


def log_ai_processing(logging_engine: LoggingEngine):
    """Specialized decorator for AI processing functions"""
    return LoggingDecorator(
        logging_engine, 
        component_name="ai_engine",
        log_performance=True
    )


def log_security_validation(logging_engine: LoggingEngine):
    """Specialized decorator for security validation functions"""
    return LoggingDecorator(
        logging_engine,
        component_name="security_engine", 
        log_performance=True,
        log_errors=True
    )


def log_command_execution(logging_engine: LoggingEngine):
    """Specialized decorator for command execution functions"""
    return LoggingDecorator(
        logging_engine,
        component_name="execution_engine",
        log_performance=True,
        log_errors=True
    )


@contextmanager
def logging_context(logging_engine: LoggingEngine, 
                   operation_name: str,
                   session_id: Optional[str] = None,
                   correlation_id: Optional[str] = None,
                   **context_data):
    """
    Context manager for automatic logging of operations with correlation tracking
    
    Usage:
        with logging_context(engine, "user_request", session_id="sess_123") as ctx:
            # Your operation code here
            ctx.add_data("step", "validation")
            # More operations...
    """
    
    class LoggingContextManager:
        def __init__(self, engine: LoggingEngine, correlation_id: str, 
                    operation_name: str, session_id: str):
            self.engine = engine
            self.correlation_id = correlation_id
            self.operation_name = operation_name
            self.session_id = session_id
            self.start_time = time.time()
            self.context_data = {}
            self.steps = []
        
        def add_data(self, key: str, value: Any):
            """Add data to the logging context"""
            self.context_data[key] = value
        
        def log_step(self, step_name: str, **step_data):
            """Log an intermediate step"""
            step_entry = {
                'correlation_id': self.correlation_id,
                'session_id': self.session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'operation_step',
                'level': 'DEBUG',
                'component': 'operation_tracker',
                'operation_name': self.operation_name,
                'step_name': step_name,
                'step_data': step_data
            }
            
            formatted_entry = self.engine.formatter.format_log_entry(step_entry)
            self.engine.writer.write_log(formatted_entry)
            
            self.steps.append({
                'step_name': step_name,
                'timestamp': datetime.utcnow(),
                'data': step_data
            })
    
    # Setup correlation ID
    if correlation_id is None:
        correlation_id = logging_engine.generate_correlation_id()
    
    # Set correlation context
    with logging_engine.correlation_context_manager(correlation_id):
        context_manager = LoggingContextManager(
            logging_engine, correlation_id, operation_name, session_id or "unknown"
        )
        
        # Log operation start
        start_entry = {
            'correlation_id': correlation_id,
            'session_id': session_id or "unknown",
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'operation_start',
            'level': 'INFO',
            'component': 'operation_tracker',
            'operation_name': operation_name,
            'context_data': context_data
        }
        
        formatted_entry = logging_engine.formatter.format_log_entry(start_entry)
        logging_engine.writer.write_log(formatted_entry)
        
        try:
            yield context_manager
            
            # Log successful completion
            end_time = time.time()
            execution_time = (end_time - context_manager.start_time) * 1000
            
            completion_entry = {
                'correlation_id': correlation_id,
                'session_id': session_id or "unknown",
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'operation_complete',
                'level': 'INFO',
                'component': 'operation_tracker',
                'operation_name': operation_name,
                'execution_time_ms': execution_time,
                'steps_count': len(context_manager.steps),
                'final_context_data': context_manager.context_data
            }
            
            formatted_entry = logging_engine.formatter.format_log_entry(completion_entry)
            logging_engine.writer.write_log(formatted_entry)
            
        except Exception as e:
            # Log operation failure
            end_time = time.time()
            execution_time = (end_time - context_manager.start_time) * 1000
            
            error_entry = {
                'correlation_id': correlation_id,
                'session_id': session_id or "unknown",
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': 'operation_error',
                'level': 'ERROR',
                'component': 'operation_tracker',
                'operation_name': operation_name,
                'execution_time_ms': execution_time,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'steps_completed': len(context_manager.steps),
                'context_data': context_manager.context_data
            }
            
            formatted_entry = logging_engine.formatter.format_log_entry(error_entry)
            logging_engine.writer.write_log(formatted_entry)
            
            raise


class PerformanceTracker:
    """Utility class for detailed performance tracking"""
    
    def __init__(self, logging_engine: LoggingEngine):
        self.logging_engine = logging_engine
        self.active_operations = {}
    
    def start_operation(self, operation_id: str, operation_name: str,
                       correlation_id: Optional[str] = None) -> str:
        """Start tracking an operation"""
        if correlation_id is None:
            correlation_id = self.logging_engine.correlation_context.get_correlation_id()
            if correlation_id is None:
                correlation_id = self.logging_engine.generate_correlation_id()
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        self.active_operations[operation_id] = {
            'operation_name': operation_name,
            'correlation_id': correlation_id,
            'start_time': start_time,
            'start_memory': start_memory,
            'checkpoints': []
        }
        
        return correlation_id
    
    def checkpoint(self, operation_id: str, checkpoint_name: str, **data):
        """Add a performance checkpoint"""
        if operation_id not in self.active_operations:
            return
        
        operation = self.active_operations[operation_id]
        current_time = time.time()
        current_memory = self._get_memory_usage()
        
        checkpoint = {
            'name': checkpoint_name,
            'timestamp': current_time,
            'elapsed_ms': (current_time - operation['start_time']) * 1000,
            'memory_mb': current_memory,
            'memory_delta_mb': current_memory - operation['start_memory'],
            'data': data
        }
        
        operation['checkpoints'].append(checkpoint)
        
        # Log checkpoint
        entry = {
            'correlation_id': operation['correlation_id'],
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'performance_checkpoint',
            'level': 'DEBUG',
            'component': 'performance_tracker',
            'operation_name': operation['operation_name'],
            'checkpoint': checkpoint
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry, log_type="performance")
    
    def end_operation(self, operation_id: str, **final_data) -> Optional[Dict[str, Any]]:
        """End operation tracking and return performance summary"""
        if operation_id not in self.active_operations:
            return None
        
        operation = self.active_operations.pop(operation_id)
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        total_time = (end_time - operation['start_time']) * 1000
        total_memory_delta = end_memory - operation['start_memory']
        
        summary = {
            'operation_name': operation['operation_name'],
            'correlation_id': operation['correlation_id'],
            'total_time_ms': total_time,
            'total_memory_delta_mb': total_memory_delta,
            'final_memory_mb': end_memory,
            'checkpoints_count': len(operation['checkpoints']),
            'checkpoints': operation['checkpoints'],
            'final_data': final_data
        }
        
        # Log operation summary
        entry = {
            'correlation_id': operation['correlation_id'],
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'performance_summary',
            'level': 'INFO',
            'component': 'performance_tracker',
            'performance_summary': summary
        }
        
        formatted_entry = self.logging_engine.formatter.format_log_entry(entry)
        self.logging_engine.writer.write_log(formatted_entry, log_type="performance")
        
        return summary
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0