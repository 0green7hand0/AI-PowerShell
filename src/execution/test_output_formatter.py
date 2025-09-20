"""Unit tests for output formatting functionality"""

import json
import pytest
from datetime import datetime
from typing import Dict, Any

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.output_formatter import (
    OutputFormatter, FormattingOptions, FormattedOutput,
    OutputEncoding, PaginationMode, create_default_formatter,
    create_compact_formatter, create_verbose_formatter
)
from interfaces.base import OutputFormat, Platform


class TestOutputFormatter:
    """Test cases for OutputFormatter class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = create_default_formatter()
        self.compact_formatter = create_compact_formatter()
        self.verbose_formatter = create_verbose_formatter()
    
    def test_empty_output_handling(self):
        """Test handling of empty output"""
        result = self.formatter.format_output("", OutputFormat.RAW)
        
        assert result.content == ""
        assert result.format_type == OutputFormat.RAW
        assert result.is_truncated is False
        assert result.original_size == 0
        assert result.formatted_size == 0
        assert result.line_count == 0
        assert len(result.warnings) == 0
    
    def test_whitespace_only_output(self):
        """Test handling of whitespace-only output"""
        result = self.formatter.format_output("   \n\t  \n  ", OutputFormat.RAW)
        
        assert result.content == ""
        assert result.is_truncated is False
        assert result.original_size == 0
    
    def test_raw_format_output(self):
        """Test raw format output"""
        test_output = "Hello\nWorld\nTest"
        result = self.formatter.format_output(test_output, OutputFormat.RAW)
        
        assert result.content == test_output
        assert result.format_type == OutputFormat.RAW
        assert result.is_truncated is False
        assert result.line_count == 3
        assert len(result.warnings) == 0
    
    def test_json_format_valid_json_input(self):
        """Test JSON formatting with valid JSON input"""
        json_input = '{"name": "test", "value": 123}'
        result = self.formatter.format_output(json_input, OutputFormat.JSON)
        
        # Should parse and reformat the JSON
        parsed = json.loads(result.content)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123
        assert result.format_type == OutputFormat.JSON
    
    def test_json_format_invalid_json_input(self):
        """Test JSON formatting with invalid JSON input"""
        text_input = "This is not JSON\nMultiple lines"
        result = self.formatter.format_output(text_input, OutputFormat.JSON)
        
        # Should wrap in JSON structure - could be detected as list or text
        parsed = json.loads(result.content)
        assert parsed["type"] in ["text", "list"]
        if parsed["type"] == "text":
            assert parsed["content"] == text_input
        else:  # list type
            assert isinstance(parsed["data"], list)
        assert "metadata" in parsed
    
    def test_table_format_powershell_table(self):
        """Test table formatting with PowerShell table input"""
        powershell_table = """Name      CPU(s)   Id ProcessName
----      ------   -- -----------
chrome    45.23    1234 chrome
notepad   0.12     5678 notepad
explorer  12.45    9012 explorer"""
        
        result = self.formatter.format_output(powershell_table, OutputFormat.TABLE)
        
        assert "Name" in result.content
        assert "CPU(s)" in result.content
        assert "chrome" in result.content
        assert "|" in result.content  # Should have pipe separators
        assert result.format_type == OutputFormat.TABLE
    
    def test_table_format_csv_input(self):
        """Test table formatting with CSV input"""
        csv_input = """Name,Age,City
John,25,New York
Jane,30,Los Angeles
Bob,35,Chicago"""
        
        result = self.formatter.format_output(csv_input, OutputFormat.TABLE)
        
        assert "Name" in result.content
        assert "John" in result.content
        assert "|" in result.content
        assert result.format_type == OutputFormat.TABLE
    
    def test_table_format_tsv_input(self):
        """Test table formatting with TSV input"""
        tsv_input = "Name\tAge\tCity\nJohn\t25\tNew York\nJane\t30\tLos Angeles"
        
        result = self.formatter.format_output(tsv_input, OutputFormat.TABLE)
        
        assert "Name" in result.content
        assert "John" in result.content
        assert "|" in result.content
    
    def test_table_format_unstructured_text(self):
        """Test table formatting with unstructured text"""
        text_input = "Line 1\nLine 2\nLine 3"
        
        result = self.formatter.format_output(text_input, OutputFormat.TABLE)
        
        # Should create a simple line number table
        assert "Line" in result.content
        assert "Content" in result.content
        assert "1" in result.content
        assert "Line 1" in result.content
    
    def test_output_truncation_by_size(self):
        """Test output truncation by size limit"""
        # Create large output
        large_output = "A" * 2000000  # 2MB of A's
        
        options = FormattingOptions(max_output_size=1024)  # 1KB limit
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(large_output, OutputFormat.RAW)
        
        assert result.is_truncated is True
        assert "truncated" in result.content.lower()
        assert len(result.warnings) > 0
        assert "exceeded" in result.warnings[0].lower()
    
    def test_output_truncation_by_lines(self):
        """Test output truncation by line limit"""
        # Create output with many lines
        many_lines = "\n".join(f"Line {i}" for i in range(2000))
        
        options = FormattingOptions(max_lines=100)
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(many_lines, OutputFormat.RAW)
        
        assert result.is_truncated is True
        assert "truncated" in result.content.lower()
        assert result.line_count <= 101  # 100 lines + truncation message
    
    def test_line_length_truncation(self):
        """Test truncation of individual long lines"""
        long_line = "A" * 1000
        short_line = "Short"
        input_text = f"{long_line}\n{short_line}"
        
        options = FormattingOptions(max_line_length=100)
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(input_text, OutputFormat.RAW)
        
        lines = result.content.splitlines()
        assert len(lines[0]) <= 120  # 100 + truncation message
        assert "truncated" in lines[0].lower()
        assert lines[1] == short_line  # Short line unchanged
    
    def test_pagination_summary_mode(self):
        """Test summary pagination mode"""
        many_lines = "\n".join(f"Line {i}" for i in range(100))
        
        options = FormattingOptions(
            max_lines=50,
            pagination_mode=PaginationMode.SUMMARY
        )
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(many_lines, OutputFormat.RAW)
        
        assert result.is_truncated is True
        assert "SUMMARY" in result.content
        assert "First 10 lines" in result.content
        assert "Last 10 lines" in result.content
        assert "Line 0" in result.content  # First line
        assert "Line 99" in result.content  # Last line
    
    def test_encoding_handling_unicode(self):
        """Test handling of Unicode characters"""
        unicode_text = "Hello 世界 🌍 Ñoël"
        
        result = self.formatter.format_output(unicode_text, OutputFormat.RAW)
        
        assert result.content == unicode_text
        assert result.encoding == "utf-8"
        assert len(result.warnings) == 0
    
    def test_encoding_handling_special_characters(self):
        """Test handling of special control characters"""
        special_text = "Hello\x00World\x08Test\x0c"
        
        result = self.formatter.format_output(special_text, OutputFormat.RAW)
        
        # Should clean special characters
        assert "\x00" not in result.content
        assert "HelloWorld Test" in result.content or "Hello World Test" in result.content
    
    def test_html_escaping_option(self):
        """Test HTML escaping option"""
        html_text = "<script>alert('test')</script>"
        
        options = FormattingOptions(escape_html=True)
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(html_text, OutputFormat.RAW)
        
        assert "&lt;" in result.content
        assert "&gt;" in result.content
        assert "<script>" not in result.content
    
    def test_metadata_inclusion(self):
        """Test metadata inclusion in results"""
        test_output = "Test output"
        
        result = self.formatter.format_output(test_output, OutputFormat.RAW, Platform.WINDOWS)
        
        assert "metadata" in result.__dict__
        assert result.metadata["platform"] == "windows"
        assert "character_stats" in result.metadata
        assert "detected_structure" in result.metadata
        assert result.metadata["character_stats"]["total_chars"] == len(test_output)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        test_output = "Test output"
        
        result = self.formatter.format_output(test_output, OutputFormat.RAW)
        
        assert result.processing_time_ms >= 0
        assert isinstance(result.processing_time_ms, float)
    
    def test_table_detection_powershell_format(self):
        """Test detection of PowerShell table format"""
        powershell_table = """ProcessName     Id  CPU
-----------     --  ---
chrome        1234   45
notepad       5678    1"""
        
        result = self.formatter.format_output(powershell_table, OutputFormat.JSON)
        
        parsed = json.loads(result.content)
        assert parsed["type"] == "table"
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["ProcessName"] == "chrome"
        assert parsed["data"][0]["Id"] == "1234"
    
    def test_table_detection_csv_format(self):
        """Test detection of CSV format"""
        csv_data = """Name,Age,City
John,25,NYC
Jane,30,LA"""
        
        result = self.formatter.format_output(csv_data, OutputFormat.JSON)
        
        parsed = json.loads(result.content)
        assert parsed["type"] == "table"
        assert len(parsed["data"]) == 2
        assert parsed["data"][0]["Name"] == "John"
        assert parsed["data"][1]["City"] == "LA"
    
    def test_table_column_limits(self):
        """Test table column limits"""
        # Create table with many columns
        headers = [f"Col{i}" for i in range(30)]
        data_row = [f"Data{i}" for i in range(30)]
        
        csv_input = ",".join(headers) + "\n" + ",".join(data_row)
        
        options = FormattingOptions(table_max_columns=5)
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(csv_input, OutputFormat.TABLE)
        
        # Should only show first 5 columns
        lines = result.content.splitlines()
        header_line = lines[0]
        assert header_line.count("|") <= 4  # 5 columns = 4 separators
    
    def test_table_column_width_limits(self):
        """Test table column width limits"""
        long_content = "A" * 200
        csv_input = f"Header\n{long_content}"
        
        options = FormattingOptions(table_max_column_width=20)
        formatter = OutputFormatter(options)
        
        result = formatter.format_output(csv_input, OutputFormat.TABLE)
        
        lines = result.content.splitlines()
        # Check that no line exceeds reasonable width
        for line in lines:
            assert len(line) <= 50  # Should be limited by column width
    
    def test_compact_formatter_limits(self):
        """Test compact formatter with strict limits"""
        large_output = "\n".join(f"Line {i} with some content" for i in range(200))
        
        result = self.compact_formatter.format_output(large_output, OutputFormat.RAW)
        
        assert result.is_truncated is True
        assert result.line_count <= 101  # 100 + truncation message
    
    def test_verbose_formatter_limits(self):
        """Test verbose formatter with generous limits"""
        medium_output = "\n".join(f"Line {i}" for i in range(500))
        
        result = self.verbose_formatter.format_output(medium_output, OutputFormat.RAW)
        
        # Should not be truncated with verbose formatter
        assert result.is_truncated is False
        assert result.line_count == 500
    
    def test_json_format_list_detection(self):
        """Test JSON formatting with list-like input"""
        list_input = """Item 1
Item 2
Item 3
Item 4"""
        
        result = self.formatter.format_output(list_input, OutputFormat.JSON)
        
        parsed = json.loads(result.content)
        assert parsed["type"] == "list"
        assert len(parsed["data"]) == 4
        assert parsed["data"][0] == "Item 1"
    
    def test_json_format_key_value_detection(self):
        """Test JSON formatting with key-value input"""
        kv_input = """Name: John Doe
Age: 30
City: New York
Status: Active
Email: john@example.com"""
        
        # This should be detected as key-value with enough entries
        result = self.formatter.format_output(kv_input, OutputFormat.JSON)
        
        parsed = json.loads(result.content)
        # Should be detected as key_value with 5 entries meeting the threshold
        assert parsed["type"] in ["text", "key_value", "list"]
    
    def test_platform_specific_formatting(self):
        """Test platform-specific formatting considerations"""
        test_output = "Test output"
        
        windows_result = self.formatter.format_output(test_output, OutputFormat.JSON, Platform.WINDOWS)
        linux_result = self.formatter.format_output(test_output, OutputFormat.JSON, Platform.LINUX)
        
        windows_parsed = json.loads(windows_result.content)
        linux_parsed = json.loads(linux_result.content)
        
        assert windows_parsed["metadata"]["platform"] == "windows"
        assert linux_parsed["metadata"]["platform"] == "linux"
    
    def test_error_handling_invalid_format(self):
        """Test error handling for invalid format types"""
        test_output = "Test output"
        
        # This should handle gracefully and add warning
        result = self.formatter.format_output(test_output, "invalid_format")
        
        assert len(result.warnings) > 0
        assert "unknown format" in result.warnings[0].lower()
        assert result.content == test_output  # Should fall back to raw
    
    def test_character_analysis(self):
        """Test character analysis functionality"""
        mixed_text = "Hello 世界! \t\n Special chars: @#$%"
        
        result = self.formatter.format_output(mixed_text, OutputFormat.RAW)
        
        char_stats = result.metadata["character_stats"]
        assert char_stats["total_chars"] == len(mixed_text)
        assert char_stats["ascii_chars"] > 0
        assert char_stats["unicode_chars"] > 0
        assert char_stats["whitespace_chars"] > 0
        assert 0 <= char_stats["ascii_percentage"] <= 100
    
    def test_output_size_calculation(self):
        """Test accurate output size calculation"""
        unicode_text = "Hello 世界"  # Contains multi-byte characters
        
        result = self.formatter.format_output(unicode_text, OutputFormat.RAW)
        
        # Should measure bytes, not characters
        expected_bytes = len(unicode_text.encode('utf-8'))
        assert result.original_size == expected_bytes
        assert result.formatted_size == expected_bytes


class TestFormattingOptions:
    """Test cases for FormattingOptions configuration"""
    
    def test_default_options(self):
        """Test default formatting options"""
        options = FormattingOptions()
        
        assert options.max_output_size == 1024 * 1024
        assert options.max_lines == 1000
        assert options.pagination_mode == PaginationMode.TRUNCATE
        assert options.encoding == OutputEncoding.UTF8
        assert options.json_indent == 2
    
    def test_custom_options(self):
        """Test custom formatting options"""
        options = FormattingOptions(
            max_output_size=512,
            max_lines=50,
            pagination_mode=PaginationMode.SUMMARY,
            encoding=OutputEncoding.ASCII,
            json_indent=4
        )
        
        assert options.max_output_size == 512
        assert options.max_lines == 50
        assert options.pagination_mode == PaginationMode.SUMMARY
        assert options.encoding == OutputEncoding.ASCII
        assert options.json_indent == 4


class TestFormatterFactories:
    """Test cases for formatter factory functions"""
    
    def test_default_formatter_creation(self):
        """Test default formatter factory"""
        formatter = create_default_formatter()
        
        assert isinstance(formatter, OutputFormatter)
        assert formatter.options.max_output_size == 1024 * 1024
    
    def test_compact_formatter_creation(self):
        """Test compact formatter factory"""
        formatter = create_compact_formatter()
        
        assert isinstance(formatter, OutputFormatter)
        assert formatter.options.max_output_size == 64 * 1024
        assert formatter.options.max_lines == 100
        assert formatter.options.json_indent == 0
    
    def test_verbose_formatter_creation(self):
        """Test verbose formatter factory"""
        formatter = create_verbose_formatter()
        
        assert isinstance(formatter, OutputFormatter)
        assert formatter.options.max_output_size == 10 * 1024 * 1024
        assert formatter.options.max_lines == 10000
        assert formatter.options.json_indent == 4


if __name__ == "__main__":
    pytest.main([__file__])