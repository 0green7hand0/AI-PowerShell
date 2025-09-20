"""
Log filtering, searching, and export functionality
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import asdict
from enum import Enum

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import AuditEntry, AuditEventType, LogLevel


class FilterOperator(Enum):
    """Operators for filtering"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


class SortOrder(Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class LogFilter:
    """Represents a single filter condition"""
    
    def __init__(self, field: str, operator: FilterOperator, value: Any):
        self.field = field
        self.operator = operator
        self.value = value
    
    def apply(self, entry: Union[AuditEntry, Dict[str, Any]]) -> bool:
        """Apply filter to an entry"""
        if isinstance(entry, AuditEntry):
            entry_dict = asdict(entry)
        else:
            entry_dict = entry
        
        # Get field value using dot notation (e.g., "performance.memory_usage_mb")
        field_value = self._get_nested_value(entry_dict, self.field)
        
        return self._evaluate_condition(field_value, self.operator, self.value)
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _evaluate_condition(self, field_value: Any, operator: FilterOperator, 
                           filter_value: Any) -> bool:
        """Evaluate filter condition"""
        if operator == FilterOperator.EXISTS:
            return field_value is not None
        
        if operator == FilterOperator.NOT_EXISTS:
            return field_value is None
        
        if field_value is None:
            return False
        
        if operator == FilterOperator.EQUALS:
            return field_value == filter_value
        
        elif operator == FilterOperator.NOT_EQUALS:
            return field_value != filter_value
        
        elif operator == FilterOperator.CONTAINS:
            return str(filter_value).lower() in str(field_value).lower()
        
        elif operator == FilterOperator.NOT_CONTAINS:
            return str(filter_value).lower() not in str(field_value).lower()
        
        elif operator == FilterOperator.STARTS_WITH:
            return str(field_value).lower().startswith(str(filter_value).lower())
        
        elif operator == FilterOperator.ENDS_WITH:
            return str(field_value).lower().endswith(str(filter_value).lower())
        
        elif operator == FilterOperator.GREATER_THAN:
            try:
                return float(field_value) > float(filter_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == FilterOperator.LESS_THAN:
            try:
                return float(field_value) < float(filter_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == FilterOperator.GREATER_EQUAL:
            try:
                return float(field_value) >= float(filter_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == FilterOperator.LESS_EQUAL:
            try:
                return float(field_value) <= float(filter_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == FilterOperator.IN:
            return field_value in filter_value
        
        elif operator == FilterOperator.NOT_IN:
            return field_value not in filter_value
        
        elif operator == FilterOperator.REGEX:
            try:
                pattern = re.compile(str(filter_value), re.IGNORECASE)
                return bool(pattern.search(str(field_value)))
            except re.error:
                return False
        
        return False


class LogQuery:
    """Represents a complex log query with multiple filters and sorting"""
    
    def __init__(self):
        self.filters: List[LogFilter] = []
        self.sort_field: Optional[str] = None
        self.sort_order: SortOrder = SortOrder.DESC
        self.limit: Optional[int] = None
        self.offset: int = 0
    
    def add_filter(self, field: str, operator: FilterOperator, value: Any) -> 'LogQuery':
        """Add a filter condition"""
        self.filters.append(LogFilter(field, operator, value))
        return self
    
    def sort_by(self, field: str, order: SortOrder = SortOrder.DESC) -> 'LogQuery':
        """Set sorting criteria"""
        self.sort_field = field
        self.sort_order = order
        return self
    
    def paginate(self, limit: int, offset: int = 0) -> 'LogQuery':
        """Set pagination"""
        self.limit = limit
        self.offset = offset
        return self
    
    def execute(self, entries: List[Union[AuditEntry, Dict[str, Any]]]) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Execute query against entries"""
        # Apply filters
        filtered_entries = []
        for entry in entries:
            if all(filter_condition.apply(entry) for filter_condition in self.filters):
                filtered_entries.append(entry)
        
        # Apply sorting
        if self.sort_field:
            filtered_entries.sort(
                key=lambda x: self._get_sort_key(x, self.sort_field),
                reverse=(self.sort_order == SortOrder.DESC)
            )
        
        # Apply pagination
        start_idx = self.offset
        end_idx = start_idx + self.limit if self.limit else len(filtered_entries)
        
        return filtered_entries[start_idx:end_idx]
    
    def _get_sort_key(self, entry: Union[AuditEntry, Dict[str, Any]], field: str) -> Any:
        """Get sort key for an entry"""
        if isinstance(entry, AuditEntry):
            entry_dict = asdict(entry)
        else:
            entry_dict = entry
        
        keys = field.split('.')
        current = entry_dict
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return ""  # Default sort value for missing fields
        
        return current if current is not None else ""


class LogSearcher:
    """Advanced log searching and filtering functionality"""
    
    def __init__(self, entries: List[Union[AuditEntry, Dict[str, Any]]]):
        self.entries = entries
    
    def search_text(self, search_term: str, fields: Optional[List[str]] = None) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Full-text search across specified fields or all text fields"""
        if fields is None:
            # Default searchable fields
            fields = [
                'user_input', 'generated_command', 'error_details.error_message',
                'event_type', 'correlation_id', 'session_id'
            ]
        
        search_term_lower = search_term.lower()
        results = []
        
        for entry in self.entries:
            if isinstance(entry, AuditEntry):
                entry_dict = asdict(entry)
            else:
                entry_dict = entry
            
            # Search in specified fields
            for field in fields:
                field_value = self._get_nested_value(entry_dict, field)
                if field_value and search_term_lower in str(field_value).lower():
                    results.append(entry)
                    break
        
        return results
    
    def search_by_correlation_id(self, correlation_id: str) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find all entries with specific correlation ID"""
        query = LogQuery().add_filter('correlation_id', FilterOperator.EQUALS, correlation_id)
        return query.execute(self.entries)
    
    def search_by_session(self, session_id: str) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find all entries for a specific session"""
        query = LogQuery().add_filter('session_id', FilterOperator.EQUALS, session_id)
        return query.execute(self.entries)
    
    def search_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find entries within time range"""
        results = []
        for entry in self.entries:
            if isinstance(entry, AuditEntry):
                entry_time = entry.timestamp
            else:
                timestamp_str = entry.get('timestamp')
                if timestamp_str:
                    try:
                        entry_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                else:
                    continue
            
            if start_time <= entry_time <= end_time:
                results.append(entry)
        
        return results
    
    def search_errors(self, error_type: Optional[str] = None) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find error entries, optionally filtered by error type"""
        query = LogQuery().add_filter('event_type', FilterOperator.EQUALS, AuditEventType.ERROR_OCCURRED.value)
        
        if error_type:
            query.add_filter('error_details.error_type', FilterOperator.EQUALS, error_type)
        
        return query.execute(self.entries)
    
    def search_performance_issues(self, min_execution_time_ms: float = 1000,
                                 min_memory_usage_mb: float = 100) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find entries with performance issues"""
        results = []
        
        # Search for slow operations
        slow_query = LogQuery().add_filter('performance.processing_time_ms', 
                                         FilterOperator.GREATER_EQUAL, min_execution_time_ms)
        slow_results = slow_query.execute(self.entries)
        results.extend(slow_results)
        
        # Search for high memory usage
        memory_query = LogQuery().add_filter('performance.memory_usage_mb',
                                           FilterOperator.GREATER_EQUAL, min_memory_usage_mb)
        memory_results = memory_query.execute(self.entries)
        results.extend(memory_results)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for entry in results:
            entry_id = id(entry)
            if entry_id not in seen:
                seen.add(entry_id)
                unique_results.append(entry)
        
        return unique_results
    
    def search_security_events(self, risk_level: Optional[str] = None) -> List[Union[AuditEntry, Dict[str, Any]]]:
        """Find security-related events"""
        query = LogQuery().add_filter('event_type', FilterOperator.EQUALS, 
                                    AuditEventType.SECURITY_VALIDATION.value)
        
        if risk_level:
            query.add_filter('validation_result.risk_assessment', FilterOperator.EQUALS, risk_level)
        
        return query.execute(self.entries)
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current


class LogExporter:
    """Export logs in various formats with filtering"""
    
    def __init__(self, entries: List[Union[AuditEntry, Dict[str, Any]]]):
        self.entries = entries
    
    def export_json(self, query: Optional[LogQuery] = None, 
                   pretty_print: bool = True) -> str:
        """Export logs as JSON"""
        entries_to_export = query.execute(self.entries) if query else self.entries
        
        # Convert AuditEntry objects to dictionaries
        export_data = []
        for entry in entries_to_export:
            if isinstance(entry, AuditEntry):
                export_data.append(asdict(entry))
            else:
                export_data.append(entry)
        
        if pretty_print:
            return json.dumps(export_data, indent=2, default=self._json_serializer)
        else:
            return json.dumps(export_data, default=self._json_serializer)
    
    def export_csv(self, query: Optional[LogQuery] = None,
                  fields: Optional[List[str]] = None) -> str:
        """Export logs as CSV"""
        entries_to_export = query.execute(self.entries) if query else self.entries
        
        if not entries_to_export:
            return ""
        
        # Default fields for CSV export
        if fields is None:
            fields = [
                'timestamp', 'correlation_id', 'session_id', 'event_type',
                'user_input', 'generated_command', 'error_details.error_message'
            ]
        
        # Create CSV content
        lines = []
        
        # Header
        lines.append(','.join(f'"{field}"' for field in fields))
        
        # Data rows
        for entry in entries_to_export:
            if isinstance(entry, AuditEntry):
                entry_dict = asdict(entry)
            else:
                entry_dict = entry
            
            row_values = []
            for field in fields:
                value = self._get_nested_value(entry_dict, field)
                if value is None:
                    value = ""
                # Escape quotes and wrap in quotes
                escaped_value = str(value).replace('"', '""')
                row_values.append(f'"{escaped_value}"')
            
            lines.append(','.join(row_values))
        
        return '\n'.join(lines)
    
    def export_summary_report(self, query: Optional[LogQuery] = None) -> str:
        """Export a summary report of log statistics"""
        entries_to_export = query.execute(self.entries) if query else self.entries
        
        if not entries_to_export:
            return "No entries found."
        
        # Calculate statistics
        total_entries = len(entries_to_export)
        event_types = {}
        sessions = set()
        correlations = set()
        errors = 0
        
        earliest_time = None
        latest_time = None
        
        for entry in entries_to_export:
            if isinstance(entry, AuditEntry):
                event_type = entry.event_type.value
                session_id = entry.session_id
                correlation_id = entry.correlation_id
                timestamp = entry.timestamp
                is_error = entry.event_type == AuditEventType.ERROR_OCCURRED
            else:
                event_type = entry.get('event_type', 'unknown')
                session_id = entry.get('session_id', 'unknown')
                correlation_id = entry.get('correlation_id', 'unknown')
                timestamp_str = entry.get('timestamp')
                is_error = event_type == AuditEventType.ERROR_OCCURRED.value
                
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    except ValueError:
                        timestamp = None
                else:
                    timestamp = None
            
            # Count event types
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Track sessions and correlations
            sessions.add(session_id)
            correlations.add(correlation_id)
            
            # Count errors
            if is_error:
                errors += 1
            
            # Track time range
            if timestamp:
                if earliest_time is None or timestamp < earliest_time:
                    earliest_time = timestamp
                if latest_time is None or timestamp > latest_time:
                    latest_time = timestamp
        
        # Generate report
        report_lines = [
            "=== LOG SUMMARY REPORT ===",
            f"Total Entries: {total_entries}",
            f"Unique Sessions: {len(sessions)}",
            f"Unique Correlations: {len(correlations)}",
            f"Error Count: {errors}",
            ""
        ]
        
        if earliest_time and latest_time:
            report_lines.extend([
                f"Time Range: {earliest_time.isoformat()} to {latest_time.isoformat()}",
                f"Duration: {latest_time - earliest_time}",
                ""
            ])
        
        report_lines.append("Event Type Distribution:")
        for event_type, count in sorted(event_types.items()):
            percentage = (count / total_entries) * 100
            report_lines.append(f"  {event_type}: {count} ({percentage:.1f}%)")
        
        return '\n'.join(report_lines)
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and other objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)