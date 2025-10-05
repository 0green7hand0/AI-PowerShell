"""Unified output formatting and standardization for PowerShell command results"""

import json
import re
import html
import unicodedata
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import OutputFormat, Platform


class OutputEncoding(Enum):
    """Output encoding types"""
    UTF8 = "utf-8"
    ASCII = "ascii"
    LATIN1 = "latin-1"


class PaginationMode(Enum):
    """Pagination modes for large output"""
    NONE = "none"
    TRUNCATE = "truncate"
    PAGINATE = "paginate"
    SUMMARY = "summary"


@dataclass
class FormattingOptions:
    """Configuration options for output formatting"""
    max_output_size: int = 1024 * 1024  # 1MB default
    max_lines: int = 1000
    max_line_length: int = 500
    pagination_mode: PaginationMode = PaginationMode.TRUNCATE
    encoding: OutputEncoding = OutputEncoding.UTF8
    preserve_formatting: bool = True
    escape_html: bool = False
    normalize_unicode: bool = True
    table_max_columns: int = 20
    table_max_column_width: int = 50
    json_indent: int = 2
    include_metadata: bool = True


@dataclass
class FormattedOutput:
    """Formatted output result with metadata"""
    content: str
    format_type: OutputFormat
    encoding: str
    is_truncated: bool
    original_size: int
    formatted_size: int
    line_count: int
    processing_time_ms: float
    metadata: Dict[str, Any]
    warnings: List[str]


class OutputFormatter:
    """Unified output formatter for PowerShell command results"""
    
    def __init__(self, options: Optional[FormattingOptions] = None):
        self.options = options or FormattingOptions()
        self._table_detectors = [
            self._detect_powershell_table,
            self._detect_csv_table,
            self._detect_tsv_table,
            self._detect_pipe_table,
            self._detect_space_table
        ]
    
    def format_output(self, raw_output: str, format_type: OutputFormat, 
                     platform: Platform = Platform.WINDOWS) -> FormattedOutput:
        """
        Format command output according to specified format
        
        Args:
            raw_output: Raw command output
            format_type: Desired output format
            platform: Target platform for formatting
            
        Returns:
            FormattedOutput with formatted content and metadata
        """
        start_time = datetime.now()
        warnings = []
        
        # Handle empty output
        if not raw_output or not raw_output.strip():
            return FormattedOutput(
                content="",
                format_type=format_type,
                encoding=self.options.encoding.value,
                is_truncated=False,
                original_size=0,
                formatted_size=0,
                line_count=0,
                processing_time_ms=0.0,
                metadata={},
                warnings=[]
            )
        
        # Normalize encoding and handle special characters
        processed_output, encoding_warnings = self._process_encoding(raw_output)
        warnings.extend(encoding_warnings)
        
        # Apply size and line limits
        truncated_output, truncation_info = self._apply_limits(processed_output)
        if truncation_info["is_truncated"]:
            warnings.append(f"Output truncated: {truncation_info['reason']}")
        
        # Format according to specified type
        if format_type == OutputFormat.RAW:
            formatted_content = truncated_output
        elif format_type == OutputFormat.JSON:
            formatted_content = self._format_as_json(truncated_output, platform)
        elif format_type == OutputFormat.TABLE:
            formatted_content = self._format_as_table(truncated_output, platform)
        else:
            formatted_content = truncated_output
            warnings.append(f"Unknown format type: {format_type}, using raw format")
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build metadata
        metadata = {
            "platform": platform.value,
            "truncation_info": truncation_info,
            "detected_structure": self._detect_output_structure(truncated_output),
            "character_stats": self._analyze_characters(processed_output),
            "formatting_options": {
                "max_output_size": self.options.max_output_size,
                "max_lines": self.options.max_lines,
                "pagination_mode": self.options.pagination_mode.value
            }
        }
        
        return FormattedOutput(
            content=formatted_content,
            format_type=format_type,
            encoding=self.options.encoding.value,
            is_truncated=truncation_info["is_truncated"],
            original_size=len(raw_output.encode('utf-8')),
            formatted_size=len(formatted_content.encode('utf-8')),
            line_count=len(formatted_content.splitlines()),
            processing_time_ms=processing_time,
            metadata=metadata,
            warnings=warnings
        )
    
    def _process_encoding(self, raw_output: str) -> Tuple[str, List[str]]:
        """Process encoding and handle special characters"""
        warnings = []
        processed = raw_output
        
        # Normalize Unicode if requested
        if self.options.normalize_unicode:
            try:
                processed = unicodedata.normalize('NFKC', processed)
            except Exception as e:
                warnings.append(f"Unicode normalization failed: {e}")
        
        # Handle HTML escaping if requested
        if self.options.escape_html:
            processed = html.escape(processed)
        
        # Remove or replace problematic characters
        processed = self._clean_special_characters(processed)
        
        # Ensure valid UTF-8 encoding
        try:
            processed.encode(self.options.encoding.value)
        except UnicodeEncodeError as e:
            warnings.append(f"Encoding error: {e}")
            # Replace problematic characters
            processed = processed.encode(self.options.encoding.value, errors='replace').decode(self.options.encoding.value)
        
        return processed, warnings
    
    def _clean_special_characters(self, text: str) -> str:
        """Clean special characters that might cause issues"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Replace other control characters (except common ones like \n, \t, \r)
        cleaned = ""
        for char in text:
            if ord(char) < 32 and char not in '\n\t\r':
                # Replace with space or remove
                if char in '\x08\x0c':  # backspace, form feed
                    cleaned += ' '
                # Skip other control characters
            else:
                cleaned += char
        
        return cleaned
    
    def _apply_limits(self, output: str) -> Tuple[str, Dict[str, Any]]:
        """Apply size and line limits to output"""
        truncation_info = {
            "is_truncated": False,
            "reason": "",
            "original_lines": len(output.splitlines()),
            "original_size": len(output.encode('utf-8'))
        }
        
        lines = output.splitlines()
        
        # Apply line limit
        if len(lines) > self.options.max_lines:
            if self.options.pagination_mode == PaginationMode.TRUNCATE:
                lines = lines[:self.options.max_lines]
                lines.append(f"... [Output truncated - showing first {self.options.max_lines} of {truncation_info['original_lines']} lines]")
                truncation_info["is_truncated"] = True
                truncation_info["reason"] = f"Exceeded {self.options.max_lines} lines"
            elif self.options.pagination_mode == PaginationMode.SUMMARY:
                summary_lines = self._create_summary(lines)
                lines = summary_lines
                truncation_info["is_truncated"] = True
                truncation_info["reason"] = "Summarized large output"
        
        # Apply line length limit
        processed_lines = []
        for line in lines:
            if len(line) > self.options.max_line_length:
                truncated_line = line[:self.options.max_line_length] + "... [line truncated]"
                processed_lines.append(truncated_line)
                if not truncation_info["is_truncated"]:
                    truncation_info["is_truncated"] = True
                    truncation_info["reason"] = f"Lines exceeded {self.options.max_line_length} characters"
            else:
                processed_lines.append(line)
        
        result = '\n'.join(processed_lines)
        
        # Apply total size limit
        result_size = len(result.encode('utf-8'))
        if result_size > self.options.max_output_size:
            # Calculate how many characters we can keep (conservative estimate)
            max_chars = self.options.max_output_size // 2
            result = result[:max_chars] + f"\n... [Output truncated - exceeded {self.options.max_output_size} bytes]"
            truncation_info["is_truncated"] = True
            if not truncation_info["reason"]:
                truncation_info["reason"] = f"Exceeded {self.options.max_output_size} bytes"
        
        return result, truncation_info
    
    def _create_summary(self, lines: List[str]) -> List[str]:
        """Create a summary of large output"""
        if len(lines) <= 20:
            return lines
        
        summary = [
            f"=== OUTPUT SUMMARY ({len(lines)} total lines) ===",
            "",
            "First 10 lines:",
            *lines[:10],
            "",
            f"... [{len(lines) - 20} lines omitted] ...",
            "",
            "Last 10 lines:",
            *lines[-10:],
            "",
            "=== END SUMMARY ==="
        ]
        
        return summary
    
    def _format_as_json(self, output: str, platform: Platform) -> str:
        """Format output as JSON structure"""
        try:
            # Try to parse as existing JSON
            parsed = json.loads(output)
            return json.dumps(parsed, indent=self.options.json_indent, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        
        # Try to detect and parse structured data
        structure = self._detect_output_structure(output)
        
        if structure["type"] == "table":
            # Convert table to JSON array
            table_data = self._parse_table_data(output, structure)
            json_data = {
                "type": "table",
                "data": table_data,
                "metadata": {
                    "platform": platform.value,
                    "timestamp": datetime.now().isoformat(),
                    "row_count": len(table_data),
                    "column_count": len(table_data[0]) if table_data else 0
                }
            }
        elif structure["type"] == "list":
            # Convert list to JSON array
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            json_data = {
                "type": "list",
                "data": lines,
                "metadata": {
                    "platform": platform.value,
                    "timestamp": datetime.now().isoformat(),
                    "item_count": len(lines)
                }
            }
        else:
            # Wrap as text output
            json_data = {
                "type": "text",
                "content": output,
                "metadata": {
                    "platform": platform.value,
                    "timestamp": datetime.now().isoformat(),
                    "line_count": len(output.splitlines()),
                    "character_count": len(output)
                }
            }
        
        return json.dumps(json_data, indent=self.options.json_indent, ensure_ascii=False)
    
    def _format_as_table(self, output: str, platform: Platform) -> str:
        """Format output as a structured table"""
        structure = self._detect_output_structure(output)
        
        if structure["type"] == "table":
            return self._format_detected_table(output, structure)
        else:
            # Try to create a simple table from the output
            return self._create_simple_table(output)
    
    def _detect_output_structure(self, output: str) -> Dict[str, Any]:
        """Detect the structure of the output"""
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        
        if not lines:
            return {"type": "empty"}
        
        # Try table detection
        for detector in self._table_detectors:
            table_info = detector(lines)
            if table_info:
                return {"type": "table", "table_info": table_info}
        
        # Check if it's a simple list
        if self._is_simple_list(lines):
            return {"type": "list"}
        
        # Check if it's key-value pairs
        if self._is_key_value_pairs(lines):
            return {"type": "key_value"}
        
        # Default to text
        return {"type": "text"}
    
    def _detect_powershell_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Detect PowerShell table format (headers with dashes)"""
        if len(lines) < 3:
            return None
        
        # Look for header line followed by dashes
        for i in range(len(lines) - 2):
            header_line = lines[i]
            separator_line = lines[i + 1]
            
            # Check if separator line contains mostly dashes and spaces
            if re.match(r'^[\s\-]+$', separator_line) and len(separator_line.strip()) > 0:
                # Additional validation: check if header and separator have similar structure
                header_parts = len(re.split(r'\s{2,}', header_line.strip()))
                dash_groups = len(re.findall(r'-+', separator_line))
                
                # Should have similar number of columns
                if abs(header_parts - dash_groups) <= 1:
                    # Verify we have data lines after
                    if i + 2 < len(lines):
                        return {
                            "format": "powershell",
                            "header_index": i,
                            "separator_index": i + 1,
                            "data_start": i + 2,
                            "separator": "whitespace"
                        }
        
        return None
    
    def _detect_csv_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Detect CSV format"""
        if len(lines) < 2:
            return None
        
        # Check if lines contain commas consistently
        comma_counts = [line.count(',') for line in lines[:5]]
        if len(set(comma_counts)) == 1 and comma_counts[0] > 0:
            return {
                "format": "csv",
                "header_index": 0,
                "data_start": 1,
                "separator": ","
            }
        
        return None
    
    def _detect_tsv_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Detect TSV (tab-separated) format"""
        if len(lines) < 2:
            return None
        
        # Check if lines contain tabs consistently
        tab_counts = [line.count('\t') for line in lines[:5]]
        if len(set(tab_counts)) == 1 and tab_counts[0] > 0:
            return {
                "format": "tsv",
                "header_index": 0,
                "data_start": 1,
                "separator": "\t"
            }
        
        return None
    
    def _detect_pipe_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Detect pipe-separated table format"""
        if len(lines) < 2:
            return None
        
        # Check if lines contain pipes consistently
        pipe_counts = [line.count('|') for line in lines[:5]]
        if len(set(pipe_counts)) == 1 and pipe_counts[0] > 0:
            return {
                "format": "pipe",
                "header_index": 0,
                "data_start": 1,
                "separator": "|"
            }
        
        return None
    
    def _detect_space_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """Detect space-separated table format"""
        if len(lines) < 2:
            return None
        
        # Check if lines have consistent column structure with multiple spaces
        first_line_parts = re.split(r'\s{2,}', lines[0])
        if len(first_line_parts) < 2:
            return None
        
        # Check if other lines have similar structure
        consistent_columns = True
        for line in lines[1:5]:  # Check first few lines
            if len(lines) > 5:
                break
            parts = re.split(r'\s{2,}', line)
            if len(parts) != len(first_line_parts):
                consistent_columns = False
                break
        
        if consistent_columns:
            return {
                "format": "space",
                "header_index": 0,
                "data_start": 1,
                "separator": "multiple_spaces"
            }
        
        return None
    
    def _is_simple_list(self, lines: List[str]) -> bool:
        """Check if output is a simple list"""
        if len(lines) < 2:
            return False
        
        # Check if lines are similar in structure (no clear columns)
        for line in lines:
            if '\t' in line or ',' in line or '|' in line:
                return False
            if re.search(r'\s{3,}', line):  # Multiple spaces might indicate columns
                return False
            if ':' in line and re.match(r'^[^:]+:\s*.+$', line):  # Key-value pattern
                return False
        
        # Additional check: if lines contain structured data patterns, not a simple list
        structured_patterns = 0
        for line in lines:
            if re.search(r'\b\d+\b', line) and len(line.split()) > 3:  # Numbers with multiple words
                structured_patterns += 1
        
        # If more than half the lines look structured, it's probably not a simple list
        if structured_patterns > len(lines) * 0.5:
            return False
        
        return True
    
    def _is_key_value_pairs(self, lines: List[str]) -> bool:
        """Check if output contains key-value pairs"""
        if len(lines) < 2:
            return False
        
        kv_pattern = re.compile(r'^[^:]+:\s*.+$')
        kv_count = sum(1 for line in lines if kv_pattern.match(line))
        
        # Be more strict about key-value detection
        return kv_count >= len(lines) * 0.8 and kv_count >= 3  # At least 80% and minimum 3 lines
    
    def _parse_table_data(self, output: str, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse table data into structured format"""
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        table_info = structure["table_info"]
        
        if table_info["format"] in ["csv", "tsv", "pipe"]:
            return self._parse_delimited_table(lines, table_info)
        elif table_info["format"] == "powershell":
            return self._parse_powershell_table(lines, table_info)
        elif table_info["format"] == "space":
            return self._parse_space_table(lines, table_info)
        else:
            return []
    
    def _parse_delimited_table(self, lines: List[str], table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse delimited table (CSV, TSV, pipe-separated)"""
        separator = table_info["separator"]
        header_line = lines[table_info["header_index"]]
        headers = [col.strip() for col in header_line.split(separator)]
        
        data = []
        for line in lines[table_info["data_start"]:]:
            values = [val.strip() for val in line.split(separator)]
            # Pad with empty strings if not enough values
            while len(values) < len(headers):
                values.append("")
            
            row = {}
            for i, header in enumerate(headers):
                row[header] = values[i] if i < len(values) else ""
            data.append(row)
        
        return data
    
    def _parse_powershell_table(self, lines: List[str], table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse PowerShell table format"""
        header_line = lines[table_info["header_index"]]
        separator_line = lines[table_info["separator_index"]]
        
        # Find dash groups in separator line to determine column boundaries
        dash_groups = []
        current_start = None
        
        for i, char in enumerate(separator_line):
            if char == '-':
                if current_start is None:
                    current_start = i
            else:
                if current_start is not None:
                    dash_groups.append((current_start, i))
                    current_start = None
        
        # Handle last group if line ends with dashes
        if current_start is not None:
            dash_groups.append((current_start, len(separator_line)))
        
        # If we have dash groups, use them to determine column positions
        if dash_groups:
            column_positions = []
            for i, (dash_start, dash_end) in enumerate(dash_groups):
                # Use dash positions as the core column boundaries
                col_start = dash_start
                col_end = dash_end
                
                # For first column, start from beginning
                if i == 0:
                    col_start = 0
                    # End where the dashes end plus some padding
                    col_end = dash_end + 1
                else:
                    # Start after previous column ends
                    prev_end = column_positions[i-1][1]
                    col_start = prev_end
                    col_end = dash_end + 1
                
                # For last column, extend to end of line
                if i == len(dash_groups) - 1:
                    col_end = max(len(header_line), len(separator_line))
                
                column_positions.append((col_start, col_end))
        else:
            # Fall back to space-based parsing
            headers = re.split(r'\s{2,}', header_line.strip())
            column_positions = []
            pos = 0
            for header in headers:
                start = header_line.find(header, pos)
                # Find end by looking for next header or end of line
                if headers.index(header) < len(headers) - 1:
                    next_header = headers[headers.index(header) + 1]
                    next_start = header_line.find(next_header, start + len(header))
                    end = next_start
                else:
                    end = len(header_line)
                column_positions.append((start, end))
                pos = end
        
        # Extract headers using column positions
        headers = []
        for start, end in column_positions:
            if start < len(header_line):
                header = header_line[start:min(end, len(header_line))].strip()
                headers.append(header if header else f"Column{len(headers)+1}")
            else:
                headers.append(f"Column{len(headers)+1}")
        
        # Extract data
        data = []
        for line in lines[table_info["data_start"]:]:
            row = {}
            for i, (start, end) in enumerate(column_positions):
                if start < len(line):
                    value = line[start:min(end, len(line))].strip()
                else:
                    value = ""
                header = headers[i] if i < len(headers) else f"Column{i+1}"
                row[header] = value
            data.append(row)
        
        return data
    
    def _parse_space_table(self, lines: List[str], table_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse space-separated table"""
        header_line = lines[table_info["header_index"]]
        headers = re.split(r'\s{2,}', header_line)
        
        data = []
        for line in lines[table_info["data_start"]:]:
            values = re.split(r'\s{2,}', line)
            # Pad with empty strings if not enough values
            while len(values) < len(headers):
                values.append("")
            
            row = {}
            for i, header in enumerate(headers):
                row[header] = values[i] if i < len(values) else ""
            data.append(row)
        
        return data
    
    def _format_detected_table(self, output: str, structure: Dict[str, Any]) -> str:
        """Format a detected table with proper alignment"""
        table_data = self._parse_table_data(output, structure)
        
        if not table_data:
            return output
        
        # Get all unique headers
        all_headers = set()
        for row in table_data:
            all_headers.update(row.keys())
        
        headers = list(all_headers)[:self.options.table_max_columns]
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = min(
                max(
                    len(header),
                    max(len(str(row.get(header, ""))) for row in table_data)
                ),
                self.options.table_max_column_width
            )
        
        # Format the table
        formatted_lines = []
        
        # Header row
        header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
        formatted_lines.append(header_row)
        
        # Separator row
        separator_row = " | ".join("-" * col_widths[header] for header in headers)
        formatted_lines.append(separator_row)
        
        # Data rows
        for row in table_data:
            data_row = " | ".join(
                str(row.get(header, "")).ljust(col_widths[header])[:col_widths[header]]
                for header in headers
            )
            formatted_lines.append(data_row)
        
        return "\n".join(formatted_lines)
    
    def _create_simple_table(self, output: str) -> str:
        """Create a simple table from unstructured output"""
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        
        if not lines:
            return output
        
        # Create a simple two-column table: Line Number | Content
        col_widths = {
            "Line": max(4, len(str(len(lines)))),
            "Content": min(
                max(len(line) for line in lines) if lines else 0,
                self.options.table_max_column_width
            )
        }
        
        formatted_lines = []
        
        # Header
        header_row = f"{'Line'.ljust(col_widths['Line'])} | {'Content'.ljust(col_widths['Content'])}"
        formatted_lines.append(header_row)
        
        # Separator
        separator_row = f"{'-' * col_widths['Line']} | {'-' * col_widths['Content']}"
        formatted_lines.append(separator_row)
        
        # Data
        for i, line in enumerate(lines, 1):
            content = line[:col_widths['Content']]
            data_row = f"{str(i).ljust(col_widths['Line'])} | {content.ljust(col_widths['Content'])}"
            formatted_lines.append(data_row)
        
        return "\n".join(formatted_lines)
    
    def _analyze_characters(self, text: str) -> Dict[str, Any]:
        """Analyze character composition of text"""
        if not text:
            return {"total_chars": 0}
        
        stats = {
            "total_chars": len(text),
            "total_bytes": len(text.encode('utf-8')),
            "lines": len(text.splitlines()),
            "ascii_chars": sum(1 for c in text if ord(c) < 128),
            "unicode_chars": sum(1 for c in text if ord(c) >= 128),
            "control_chars": sum(1 for c in text if ord(c) < 32 and c not in '\n\t\r'),
            "whitespace_chars": sum(1 for c in text if c.isspace()),
            "printable_chars": sum(1 for c in text if c.isprintable())
        }
        
        stats["ascii_percentage"] = (stats["ascii_chars"] / stats["total_chars"]) * 100
        stats["unicode_percentage"] = (stats["unicode_chars"] / stats["total_chars"]) * 100
        
        return stats


def create_default_formatter() -> OutputFormatter:
    """Create a default output formatter with standard options"""
    return OutputFormatter(FormattingOptions())


def create_compact_formatter() -> OutputFormatter:
    """Create a compact formatter for limited output"""
    options = FormattingOptions(
        max_output_size=64 * 1024,  # 64KB
        max_lines=100,
        max_line_length=200,
        pagination_mode=PaginationMode.TRUNCATE,
        table_max_columns=10,
        table_max_column_width=30,
        json_indent=0
    )
    return OutputFormatter(options)


def create_verbose_formatter() -> OutputFormatter:
    """Create a verbose formatter for detailed output"""
    options = FormattingOptions(
        max_output_size=10 * 1024 * 1024,  # 10MB
        max_lines=10000,
        max_line_length=1000,
        pagination_mode=PaginationMode.SUMMARY,
        table_max_columns=50,
        table_max_column_width=100,
        json_indent=4,
        include_metadata=True
    )
    return OutputFormatter(options)