"""Comprehensive Error Handling and Recovery Mechanisms

This module provides comprehensive error handling, graceful degradation,
and recovery mechanisms for the AI PowerShell Assistant.
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import time

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.base import Platform, LogLevel


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    AI_ENGINE = "ai_engine"
    SECURITY_ENGINE = "security_engine"
    EXECUTOR = "executor"
    CONTEXT_MANAGER = "context_manager"
    LOGGING_ENGINE = "logging_engine"
    STORAGE = "storage"
    MCP_SERVER = "mcp_server"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Available recovery actions"""
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    RESTART_COMPONENT = "restart_component"
    FAIL_SAFE = "fail_safe"
    IGNORE = "ignore"
    ESCALATE = "escalate"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    component: str
    operation: str
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    user_input: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryStrategy:
    """Recovery strategy definition"""
    action: RecoveryAction
    max_retries: int = 3
    retry_delay: float = 1.0
    fallback_function: Optional[Callable] = None
    degraded_mode_function: Optional[Callable] = None
    escalation_threshold: int = 5


@dataclass
class ErrorRecord:
    """Error record for tracking and analysis"""
    timestamp: datetime
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    stack_trace: str
    recovery_attempted: bool = False
    recovery_successful: bool = False
    recovery_action: Optional[RecoveryAction] = None


class ComponentHealthMonitor:
    """Monitor component health and detect failures"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.component_status: Dict[str, Dict[str, Any]] = {}
        self.health_check_interval = 30  # seconds
        self.failure_threshold = 3
        self.recovery_cooldown = 60  # seconds
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
    
    def register_component(self, component_name: str, health_check_func: Callable, 
                          recovery_func: Optional[Callable] = None):
        """Register a component for health monitoring"""
        self.component_status[component_name] = {
            "health_check": health_check_func,
            "recovery_func": recovery_func,
            "status": "unknown",
            "last_check": None,
            "failure_count": 0,
            "last_recovery": None,
            "consecutive_failures": 0
        }
        self.logger.info(f"Registered component for monitoring: {component_name}")
    
    async def start_monitoring(self):
        """Start health monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Component health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Component health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                await self._check_all_components()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying
    
    async def _check_all_components(self):
        """Check health of all registered components"""
        for component_name, status in self.component_status.items():
            try:
                await self._check_component_health(component_name, status)
            except Exception as e:
                self.logger.error(f"Error checking health of {component_name}: {e}")
    
    async def _check_component_health(self, component_name: str, status: Dict[str, Any]):
        """Check health of a specific component"""
        try:
            health_check = status["health_check"]
            
            # Call health check function
            if asyncio.iscoroutinefunction(health_check):
                health_result = await health_check()
            else:
                health_result = health_check()
            
            # Update status
            status["last_check"] = datetime.now(timezone.utc)
            
            if health_result and health_result.get("status") == "healthy":
                if status["status"] != "healthy":
                    self.logger.info(f"Component {component_name} recovered")
                status["status"] = "healthy"
                status["consecutive_failures"] = 0
            else:
                status["status"] = "unhealthy"
                status["failure_count"] += 1
                status["consecutive_failures"] += 1
                
                self.logger.warning(f"Component {component_name} health check failed: {health_result}")
                
                # Attempt recovery if threshold reached
                if (status["consecutive_failures"] >= self.failure_threshold and
                    status["recovery_func"] and
                    self._should_attempt_recovery(status)):
                    
                    await self._attempt_recovery(component_name, status)
        
        except Exception as e:
            status["status"] = "error"
            status["failure_count"] += 1
            status["consecutive_failures"] += 1
            self.logger.error(f"Health check failed for {component_name}: {e}")
    
    def _should_attempt_recovery(self, status: Dict[str, Any]) -> bool:
        """Determine if recovery should be attempted"""
        last_recovery = status.get("last_recovery")
        if last_recovery:
            time_since_recovery = (datetime.now(timezone.utc) - last_recovery).total_seconds()
            return time_since_recovery > self.recovery_cooldown
        return True
    
    async def _attempt_recovery(self, component_name: str, status: Dict[str, Any]):
        """Attempt to recover a failed component"""
        try:
            self.logger.info(f"Attempting recovery for component: {component_name}")
            recovery_func = status["recovery_func"]
            
            if asyncio.iscoroutinefunction(recovery_func):
                recovery_result = await recovery_func()
            else:
                recovery_result = recovery_func()
            
            status["last_recovery"] = datetime.now(timezone.utc)
            
            if recovery_result:
                self.logger.info(f"Recovery successful for component: {component_name}")
                status["consecutive_failures"] = 0
            else:
                self.logger.warning(f"Recovery failed for component: {component_name}")
        
        except Exception as e:
            self.logger.error(f"Recovery attempt failed for {component_name}: {e}")
    
    def get_component_status(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific component"""
        return self.component_status.get(component_name)
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all components"""
        return self.component_status.copy()


class ErrorHandler:
    """Comprehensive error handling and recovery system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_records: List[ErrorRecord] = []
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.health_monitor = ComponentHealthMonitor()
        self.max_error_records = 1000
        self.error_counts: Dict[str, int] = {}
        
        # Setup default recovery strategies
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """Setup default recovery strategies for different error types"""
        
        # AI Engine errors
        self.recovery_strategies["ai_engine_unavailable"] = RecoveryStrategy(
            action=RecoveryAction.FALLBACK,
            fallback_function=self._ai_engine_fallback
        )
        
        self.recovery_strategies["ai_processing_error"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=2,
            retry_delay=1.0
        )
        
        # Security Engine errors
        self.recovery_strategies["security_engine_unavailable"] = RecoveryStrategy(
            action=RecoveryAction.FAIL_SAFE,
            fallback_function=self._security_fail_safe
        )
        
        # Executor errors
        self.recovery_strategies["executor_unavailable"] = RecoveryStrategy(
            action=RecoveryAction.DEGRADE,
            degraded_mode_function=self._executor_degraded_mode
        )
        
        self.recovery_strategies["execution_timeout"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=1,
            retry_delay=2.0
        )
        
        # Storage errors
        self.recovery_strategies["storage_unavailable"] = RecoveryStrategy(
            action=RecoveryAction.DEGRADE,
            degraded_mode_function=self._storage_degraded_mode
        )
        
        # Network errors
        self.recovery_strategies["network_error"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_retries=3,
            retry_delay=2.0
        )
        
        # Configuration errors
        self.recovery_strategies["configuration_error"] = RecoveryStrategy(
            action=RecoveryAction.FALLBACK,
            fallback_function=self._configuration_fallback
        )
    
    async def handle_error(self, error: Exception, context: ErrorContext, 
                          error_type: Optional[str] = None) -> Dict[str, Any]:
        """Handle an error with appropriate recovery strategy"""
        
        # Classify error
        error_type = error_type or self._classify_error(error, context)
        severity = self._determine_severity(error, context)
        category = self._determine_category(context.component)
        
        # Create error record
        error_record = ErrorRecord(
            timestamp=datetime.now(timezone.utc),
            error_type=error_type,
            error_message=str(error),
            severity=severity,
            category=category,
            context=context,
            stack_trace=traceback.format_exc()
        )
        
        # Log error
        self._log_error(error_record)
        
        # Store error record
        self._store_error_record(error_record)
        
        # Attempt recovery
        recovery_result = await self._attempt_recovery(error_record)
        
        # Merge recovery result into response
        response = {
            "error_handled": True,
            "error_type": error_type,
            "severity": severity.value,
            "recovery_attempted": recovery_result["attempted"],
            "recovery_successful": recovery_result["successful"],
            "recovery_action": recovery_result.get("action"),
            "correlation_id": context.correlation_id
        }
        
        # Add all recovery result keys to response
        for key, value in recovery_result.items():
            if key not in response:
                response[key] = value
        
        return response
    
    def _classify_error(self, error: Exception, context: ErrorContext) -> str:
        """Classify error type based on exception and context"""
        error_name = type(error).__name__
        
        # Generic classification first (takes precedence)
        if isinstance(error, TimeoutError):
            return "timeout_error"
        elif isinstance(error, ConnectionError):
            return "network_error"
        elif isinstance(error, PermissionError):
            return "permission_error"
        elif isinstance(error, FileNotFoundError):
            return "file_not_found_error"
        elif isinstance(error, ValueError):
            return "validation_error"
        
        # Component-specific classification
        if context.component == "ai_engine":
            if "unavailable" in str(error).lower() or "not available" in str(error).lower():
                return "ai_engine_unavailable"
            return "ai_processing_error"
        
        elif context.component == "security_engine":
            if "unavailable" in str(error).lower():
                return "security_engine_unavailable"
            return "security_validation_error"
        
        elif context.component == "executor":
            if "unavailable" in str(error).lower():
                return "executor_unavailable"
            elif "timeout" in str(error).lower():
                return "execution_timeout"
            return "execution_error"
        
        elif context.component == "storage":
            if "unavailable" in str(error).lower():
                return "storage_unavailable"
            return "storage_error"
        
        return f"{error_name.lower()}_error"
    
    def _determine_severity(self, error: Exception, context: ErrorContext) -> ErrorSeverity:
        """Determine error severity"""
        error_str = str(error).lower()
        
        # Critical errors
        if (context.component in ["security_engine", "mcp_server"] or
            "critical" in error_str or
            "fatal" in error_str):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if (context.component in ["ai_engine", "executor"] or
            "unavailable" in error_str or
            isinstance(error, (ConnectionError, PermissionError))):
            # Exception for timeout errors which should be medium severity
            if isinstance(error, TimeoutError):
                return ErrorSeverity.MEDIUM
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if (isinstance(error, (TimeoutError, ValueError)) or
            "timeout" in error_str or
            "validation" in error_str):
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _determine_category(self, component: str) -> ErrorCategory:
        """Determine error category from component"""
        try:
            return ErrorCategory(component.lower())
        except ValueError:
            return ErrorCategory.UNKNOWN
    
    def _log_error(self, error_record: ErrorRecord):
        """Log error with appropriate level"""
        log_message = (f"Error in {error_record.context.component}: "
                      f"{error_record.error_message}")
        
        if error_record.context.correlation_id:
            log_message += f" [Correlation ID: {error_record.context.correlation_id}]"
        
        if error_record.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_record.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_record.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _store_error_record(self, error_record: ErrorRecord):
        """Store error record for analysis"""
        self.error_records.append(error_record)
        
        # Maintain maximum records
        if len(self.error_records) > self.max_error_records:
            self.error_records = self.error_records[-self.max_error_records:]
        
        # Update error counts
        error_key = f"{error_record.category.value}:{error_record.error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    async def _attempt_recovery(self, error_record: ErrorRecord) -> Dict[str, Any]:
        """Attempt recovery based on error type"""
        error_type = error_record.error_type
        strategy = self.recovery_strategies.get(error_type)
        
        if not strategy:
            return {"attempted": False, "successful": False}
        
        error_record.recovery_attempted = True
        error_record.recovery_action = strategy.action
        
        try:
            if strategy.action == RecoveryAction.RETRY:
                return await self._retry_recovery(error_record, strategy)
            
            elif strategy.action == RecoveryAction.FALLBACK:
                return await self._fallback_recovery(error_record, strategy)
            
            elif strategy.action == RecoveryAction.DEGRADE:
                return await self._degrade_recovery(error_record, strategy)
            
            elif strategy.action == RecoveryAction.FAIL_SAFE:
                return await self._fail_safe_recovery(error_record, strategy)
            
            else:
                return {"attempted": True, "successful": False, "action": strategy.action.value}
        
        except Exception as recovery_error:
            self.logger.error(f"Recovery attempt failed: {recovery_error}")
            return {"attempted": True, "successful": False, "error": str(recovery_error)}
    
    async def _retry_recovery(self, error_record: ErrorRecord, strategy: RecoveryStrategy) -> Dict[str, Any]:
        """Implement retry recovery strategy"""
        # Note: Actual retry would be implemented by the calling code
        # This just indicates that retry should be attempted
        return {
            "attempted": True,
            "successful": True,
            "action": "retry",
            "max_retries": strategy.max_retries,
            "retry_delay": strategy.retry_delay,
            "fallback_result": None
        }
    
    async def _fallback_recovery(self, error_record: ErrorRecord, strategy: RecoveryStrategy) -> Dict[str, Any]:
        """Implement fallback recovery strategy"""
        if strategy.fallback_function:
            try:
                if asyncio.iscoroutinefunction(strategy.fallback_function):
                    fallback_result = await strategy.fallback_function(error_record.context)
                else:
                    fallback_result = strategy.fallback_function(error_record.context)
                
                error_record.recovery_successful = True
                return {
                    "attempted": True,
                    "successful": True,
                    "action": "fallback",
                    "fallback_result": fallback_result
                }
            except Exception as e:
                self.logger.error(f"Fallback function failed: {e}")
                return {"attempted": True, "successful": False, "error": str(e)}
        
        return {"attempted": False, "successful": False}
    
    async def _degrade_recovery(self, error_record: ErrorRecord, strategy: RecoveryStrategy) -> Dict[str, Any]:
        """Implement degraded mode recovery strategy"""
        if strategy.degraded_mode_function:
            try:
                if asyncio.iscoroutinefunction(strategy.degraded_mode_function):
                    degraded_result = await strategy.degraded_mode_function(error_record.context)
                else:
                    degraded_result = strategy.degraded_mode_function(error_record.context)
                
                error_record.recovery_successful = True
                return {
                    "attempted": True,
                    "successful": True,
                    "action": "degrade",
                    "degraded_result": degraded_result,
                    "fallback_result": degraded_result  # Also provide as fallback_result for compatibility
                }
            except Exception as e:
                self.logger.error(f"Degraded mode function failed: {e}")
                return {"attempted": True, "successful": False, "error": str(e)}
        
        return {"attempted": False, "successful": False}
    
    async def _fail_safe_recovery(self, error_record: ErrorRecord, strategy: RecoveryStrategy) -> Dict[str, Any]:
        """Implement fail-safe recovery strategy"""
        if strategy.fallback_function:
            try:
                if asyncio.iscoroutinefunction(strategy.fallback_function):
                    fail_safe_result = await strategy.fallback_function(error_record.context)
                else:
                    fail_safe_result = strategy.fallback_function(error_record.context)
                
                error_record.recovery_successful = True
                return {
                    "attempted": True,
                    "successful": True,
                    "action": "fail_safe",
                    "fail_safe_result": fail_safe_result,
                    "fallback_result": fail_safe_result  # Also provide as fallback_result for compatibility
                }
            except Exception as e:
                self.logger.error(f"Fail-safe function failed: {e}")
                return {"attempted": True, "successful": False, "error": str(e)}
        
        return {"attempted": False, "successful": False}
    
    # Fallback and degraded mode implementations
    def _ai_engine_fallback(self, context: ErrorContext) -> Dict[str, Any]:
        """Fallback for AI engine unavailable"""
        return {
            "success": False,
            "error": "AI engine not available - using rule-based fallback",
            "error_code": "AI_ENGINE_UNAVAILABLE",
            "fallback_mode": True,
            "suggested_command": "# AI processing unavailable - please provide PowerShell command directly"
        }
    
    def _security_fail_safe(self, context: ErrorContext) -> Dict[str, Any]:
        """Fail-safe for security engine unavailable"""
        return {
            "success": False,
            "error": "Security engine unavailable - command execution blocked for safety",
            "error_code": "SECURITY_ENGINE_UNAVAILABLE",
            "fail_safe_mode": True,
            "blocked_reasons": ["Security validation unavailable"]
        }
    
    def _executor_degraded_mode(self, context: ErrorContext) -> Dict[str, Any]:
        """Degraded mode for executor unavailable"""
        return {
            "success": False,
            "error": "PowerShell executor unavailable - system information only",
            "error_code": "EXECUTOR_UNAVAILABLE",
            "degraded_mode": True,
            "available_operations": ["system_info", "help"]
        }
    
    def _storage_degraded_mode(self, context: ErrorContext) -> Dict[str, Any]:
        """Degraded mode for storage unavailable"""
        return {
            "success": True,
            "warning": "Storage unavailable - operating in memory-only mode",
            "degraded_mode": True,
            "limitations": ["No command history", "No user preferences", "No persistent cache"]
        }
    
    def _configuration_fallback(self, context: ErrorContext) -> Dict[str, Any]:
        """Fallback for configuration errors"""
        return {
            "success": True,
            "warning": "Configuration error - using default settings",
            "fallback_mode": True,
            "default_config_used": True
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        total_errors = len(self.error_records)
        
        if total_errors == 0:
            return {"total_errors": 0}
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = sum(
                1 for record in self.error_records 
                if record.severity == severity
            )
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = sum(
                1 for record in self.error_records 
                if record.category == category
            )
        
        # Recent errors (last hour)
        one_hour_ago = datetime.now(timezone.utc).timestamp() - 3600
        recent_errors = sum(
            1 for record in self.error_records 
            if record.timestamp.timestamp() > one_hour_ago
        )
        
        # Recovery success rate
        recovery_attempts = sum(1 for record in self.error_records if record.recovery_attempted)
        recovery_successes = sum(1 for record in self.error_records if record.recovery_successful)
        recovery_rate = (recovery_successes / recovery_attempts * 100) if recovery_attempts > 0 else 0
        
        return {
            "total_errors": total_errors,
            "recent_errors_1h": recent_errors,
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "recovery_attempts": recovery_attempts,
            "recovery_successes": recovery_successes,
            "recovery_success_rate": round(recovery_rate, 2),
            "most_common_errors": dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def register_recovery_strategy(self, error_type: str, strategy: RecoveryStrategy):
        """Register custom recovery strategy"""
        self.recovery_strategies[error_type] = strategy
        self.logger.info(f"Registered recovery strategy for: {error_type}")
    
    def clear_error_records(self):
        """Clear stored error records"""
        self.error_records.clear()
        self.error_counts.clear()
        self.logger.info("Error records cleared")


# Global error handler instance
error_handler = ErrorHandler()


# Decorator for automatic error handling
def handle_errors(error_type: Optional[str] = None, component: str = "unknown"):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    component=component,
                    operation=func.__name__,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                
                recovery_result = await error_handler.handle_error(e, context, error_type)
                
                # Return error response
                return {
                    "success": False,
                    "error": str(e),
                    "error_handling": recovery_result
                }
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    component=component,
                    operation=func.__name__,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                
                # For sync functions, we can't use async error handling
                # Just log and return error
                error_handler.logger.error(f"Error in {component}.{func.__name__}: {e}")
                
                return {
                    "success": False,
                    "error": str(e),
                    "error_handling": {"attempted": False, "reason": "sync_function"}
                }
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator