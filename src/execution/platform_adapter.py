"""Platform-specific output processing and normalization"""

import re
import os
import platform
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Platform, OutputFormat
from execution.output_formatter import OutputFormatter, FormattingOptions, FormattedOutput


class ErrorMessageType(Enum):
    """Types of error messages for standardization"""
    FILE_NOT_FOUND = "file_not_found"
    ACCESS_DENIED = "access_denied"
    COMMAND_NOT_FOUND = "command_not_found"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PERMISSION_ERROR = "permission_error"
    GENERIC_ERROR = "generic_error"


@dataclass
class PlatformAdaptationOptions:
    """Configuration for platform-specific adaptations"""
    normalize_paths: bool = True
    standardize_errors: bool = True
    convert_line_endings: bool = True
    normalize_encoding: bool = True
    adapt_command_output: bool = True
    preserve_original_format: bool = False
    target_platform: Optional[Platform] = None


@dataclass
class AdaptationResult:
    """Result of platform adaptation"""
    adapted_content: str
    original_content: str
    adaptations_applied: List[str]
    platform_detected: Platform
    target_platform: Platform
    warnings: List[str]
    metadata: Dict[str, Any]


class PlatformOutputAdapter:
    """Handles platform-specific output processing and normalization"""
    
    def __init__(self, options: Optional[PlatformAdaptationOptions] = None):
        self.options = options or PlatformAdaptationOptions()
        self.current_platform = self._detect_current_platform()
        
        # Error message patterns for different platforms
        self._error_patterns = {
            Platform.WINDOWS: {
                ErrorMessageType.FILE_NOT_FOUND: [
                    r"cannot find path '([^']+)' because it does not exist",
                    r"the system cannot find the file specified",
                    r"could not find file '([^']+)'"
                ],
                ErrorMessageType.ACCESS_DENIED: [
                    r"access to the path '([^']+)' is denied",
                    r"access denied",
                    r"unauthorized access"
                ],
                ErrorMessageType.COMMAND_NOT_FOUND: [
                    r"'([^']+)' is not recognized as an internal or external command",
                    r"the term '([^']+)' is not recognized"
                ]
            },
            Platform.LINUX: {
                ErrorMessageType.FILE_NOT_FOUND: [
                    r"no such file or directory: '([^']+)'",
                    r"cannot access '([^']+)': no such file or directory"
                ],
                ErrorMessageType.ACCESS_DENIED: [
                    r"permission denied: '([^']+)'",
                    r"access denied"
                ],
                ErrorMessageType.COMMAND_NOT_FOUND: [
                    r"command not found: ([^\s]+)",
                    r"([^\s]+): command not found"
                ]
            },
            Platform.MACOS: {
                ErrorMessageType.FILE_NOT_FOUND: [
                    r"no such file or directory: '([^']+)'",
                    r"cannot access '([^']+)': no such file or directory"
                ],
                ErrorMessageType.ACCESS_DENIED: [
                    r"permission denied: '([^']+)'",
                    r"operation not permitted"
                ],
                ErrorMessageType.COMMAND_NOT_FOUND: [
                    r"command not found: ([^\s]+)",
                    r"([^\s]+): command not found"
                ]
            }
        }
        
        # Standard error messages
        self._standard_errors = {
            ErrorMessageType.FILE_NOT_FOUND: "File or directory not found: {path}",
            ErrorMessageType.ACCESS_DENIED: "Access denied: {path}",
            ErrorMessageType.COMMAND_NOT_FOUND: "Command not found: {command}",
            ErrorMessageType.SYNTAX_ERROR: "Syntax error in command",
            ErrorMessageType.TIMEOUT: "Operation timed out",
            ErrorMessageType.NETWORK_ERROR: "Network connection error",
            ErrorMessageType.PERMISSION_ERROR: "Insufficient permissions",
            ErrorMessageType.GENERIC_ERROR: "An error occurred: {message}"
        }
    
    def _detect_current_platform(self) -> Platform:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        else:
            return Platform.LINUX  # Default fallback
    
    def adapt_output(self, output: str, source_platform: Platform, 
                    target_platform: Optional[Platform] = None) -> AdaptationResult:
        """
        Adapt output from source platform to target platform
        
        Args:
            output: Raw output to adapt
            source_platform: Platform where output originated
            target_platform: Target platform (defaults to current platform)
            
        Returns:
            AdaptationResult with adapted content and metadata
        """
        if target_platform is None:
            target_platform = self.options.target_platform or self.current_platform
        
        adaptations_applied = []
        warnings = []
        adapted_content = output
        
        # Skip adaptation if source and target are the same
        if source_platform == target_platform and not self.options.preserve_original_format:
            return AdaptationResult(
                adapted_content=output,
                original_content=output,
                adaptations_applied=[],
                platform_detected=source_platform,
                target_platform=target_platform,
                warnings=[],
                metadata={"no_adaptation_needed": True}
            )
        
        # Apply path normalization
        if self.options.normalize_paths:
            adapted_content, path_warnings = self._normalize_paths(
                adapted_content, source_platform, target_platform
            )
            if path_warnings:
                warnings.extend(path_warnings)
                adaptations_applied.append("path_normalization")
        
        # Apply error message standardization
        if self.options.standardize_errors:
            adapted_content, error_warnings = self._standardize_error_messages(
                adapted_content, source_platform
            )
            if error_warnings:
                warnings.extend(error_warnings)
                adaptations_applied.append("error_standardization")
        
        # Apply line ending conversion
        if self.options.convert_line_endings:
            adapted_content, line_warnings = self._convert_line_endings(
                adapted_content, target_platform
            )
            if line_warnings:
                warnings.extend(line_warnings)
                adaptations_applied.append("line_ending_conversion")
        
        # Apply encoding normalization
        if self.options.normalize_encoding:
            adapted_content, encoding_warnings = self._normalize_encoding(adapted_content)
            if encoding_warnings:
                warnings.extend(encoding_warnings)
                adaptations_applied.append("encoding_normalization")
        
        # Apply command output adaptation
        if self.options.adapt_command_output:
            adapted_content, cmd_warnings = self._adapt_command_output(
                adapted_content, source_platform, target_platform
            )
            if cmd_warnings:
                warnings.extend(cmd_warnings)
                adaptations_applied.append("command_output_adaptation")
        
        # Build metadata
        metadata = {
            "source_platform": source_platform.value,
            "target_platform": target_platform.value,
            "current_platform": self.current_platform.value,
            "adaptation_options": {
                "normalize_paths": self.options.normalize_paths,
                "standardize_errors": self.options.standardize_errors,
                "convert_line_endings": self.options.convert_line_endings,
                "normalize_encoding": self.options.normalize_encoding,
                "adapt_command_output": self.options.adapt_command_output
            },
            "content_analysis": self._analyze_content(output, adapted_content)
        }
        
        return AdaptationResult(
            adapted_content=adapted_content,
            original_content=output,
            adaptations_applied=adaptations_applied,
            platform_detected=source_platform,
            target_platform=target_platform,
            warnings=warnings,
            metadata=metadata
        )
    
    def _normalize_paths(self, content: str, source_platform: Platform, 
                        target_platform: Platform) -> Tuple[str, List[str]]:
        """Normalize file paths for target platform"""
        warnings = []
        adapted = content
        
        if source_platform == target_platform:
            return adapted, warnings
        
        # Windows to Unix conversion
        if source_platform == Platform.WINDOWS and target_platform in [Platform.LINUX, Platform.MACOS]:
            # Convert Windows drive paths (C:\path) to Unix paths (/path)
            drive_pattern = r'([A-Za-z]):\\([^\\"\s]*(?:\\[^\\"\s]*)*)'
            matches = re.findall(drive_pattern, adapted)
            for drive, path in matches:
                windows_path = f"{drive}:\\{path}"
                unix_path = f"/{drive.lower()}/{path.replace(chr(92), '/')}"  # Using chr(92) for backslash
                adapted = adapted.replace(windows_path, unix_path)
                warnings.append(f"Converted Windows path {windows_path} to Unix path {unix_path}")
            
            # Convert Windows relative paths
            rel_pattern = r'\.\\([^\\"\s]*(?:\\[^\\"\s]*)*)'
            adapted = re.sub(rel_pattern, lambda m: './' + m.group(1).replace(chr(92), '/'), adapted)
        
        # Unix to Windows conversion
        elif source_platform in [Platform.LINUX, Platform.MACOS] and target_platform == Platform.WINDOWS:
            # Convert Unix absolute paths to Windows paths
            unix_pattern = r'/([a-zA-Z])/([^/\s]*(?:/[^/\s]*)*)'
            matches = re.findall(unix_pattern, adapted)
            for drive, path in matches:
                unix_path = f"/{drive}/{path}"
                windows_path = f"{drive.upper()}:\\{path.replace('/', chr(92))}"
                adapted = adapted.replace(unix_path, windows_path)
                warnings.append(f"Converted Unix path {unix_path} to Windows path {windows_path}")
            
            # Convert Unix relative paths
            rel_pattern = r'\.\/([^/\s]*(?:/[^/\s]*)*)'
            adapted = re.sub(rel_pattern, lambda m: '.' + chr(92) + m.group(1).replace('/', chr(92)), adapted)
        
        return adapted, warnings
    
    def _standardize_error_messages(self, content: str, source_platform: Platform) -> Tuple[str, List[str]]:
        """Standardize error messages across platforms"""
        warnings = []
        adapted = content
        
        if source_platform not in self._error_patterns:
            return adapted, warnings
        
        platform_patterns = self._error_patterns[source_platform]
        
        for error_type, patterns in platform_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, adapted, re.IGNORECASE))
                for match in reversed(matches):  # Process in reverse to avoid index issues
                    original_error = match.group(0)
                    
                    # Extract parameters from the match
                    if error_type == ErrorMessageType.FILE_NOT_FOUND:
                        path = match.group(1) if match.groups() else "unknown"
                        standard_error = self._standard_errors[error_type].format(path=path)
                    elif error_type == ErrorMessageType.ACCESS_DENIED:
                        path = match.group(1) if match.groups() else "unknown"
                        standard_error = self._standard_errors[error_type].format(path=path)
                    elif error_type == ErrorMessageType.COMMAND_NOT_FOUND:
                        command = match.group(1) if match.groups() else "unknown"
                        standard_error = self._standard_errors[error_type].format(command=command)
                    else:
                        standard_error = self._standard_errors[error_type]
                    
                    # Replace using position to avoid multiple replacements
                    start, end = match.span()
                    adapted = adapted[:start] + standard_error + adapted[end:]
                    warnings.append(f"Standardized error message: {error_type.value}")
        
        return adapted, warnings
    
    def _convert_line_endings(self, content: str, target_platform: Platform) -> Tuple[str, List[str]]:
        """Convert line endings for target platform"""
        warnings = []
        
        # Detect current line endings
        has_crlf = '\r\n' in content
        has_lf = '\n' in content and not has_crlf
        has_cr = '\r' in content and not has_crlf
        
        if target_platform == Platform.WINDOWS:
            # Convert to CRLF
            if has_lf or has_cr:
                content = content.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
                warnings.append("Converted line endings to Windows format (CRLF)")
        else:
            # Convert to LF (Unix/Linux/macOS)
            if has_crlf or has_cr:
                content = content.replace('\r\n', '\n').replace('\r', '\n')
                warnings.append("Converted line endings to Unix format (LF)")
        
        return content, warnings
    
    def _normalize_encoding(self, content: str) -> Tuple[str, List[str]]:
        """Normalize text encoding"""
        warnings = []
        original_content = content
        
        try:
            # Ensure content is valid UTF-8
            content.encode('utf-8')
        except UnicodeEncodeError:
            # Replace problematic characters
            content = content.encode('utf-8', errors='replace').decode('utf-8')
            warnings.append("Replaced invalid UTF-8 characters")
        
        # Normalize common encoding issues
        replacements = {
            '\u2018': "'",  # Left single quotation mark
            '\u2019': "'",  # Right single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...', # Ellipsis
        }
        
        for unicode_char, replacement in replacements.items():
            if unicode_char in content:
                content = content.replace(unicode_char, replacement)
                warnings.append(f"Normalized Unicode character: {unicode_char}")
        
        # Only return warnings if content actually changed
        if content == original_content and not warnings:
            return content, []
        
        return content, warnings
    
    def _adapt_command_output(self, content: str, source_platform: Platform, 
                             target_platform: Platform) -> Tuple[str, List[str]]:
        """Adapt command-specific output formats"""
        warnings = []
        adapted = content
        
        # Adapt directory listing output
        adapted, dir_warnings = self._adapt_directory_listing(adapted, source_platform, target_platform)
        warnings.extend(dir_warnings)
        
        # Adapt process listing output
        adapted, proc_warnings = self._adapt_process_listing(adapted, source_platform, target_platform)
        warnings.extend(proc_warnings)
        
        # Adapt environment variable output
        adapted, env_warnings = self._adapt_environment_variables(adapted, source_platform, target_platform)
        warnings.extend(env_warnings)
        
        return adapted, warnings
    
    def _adapt_directory_listing(self, content: str, source_platform: Platform, 
                                target_platform: Platform) -> Tuple[str, List[str]]:
        """Adapt directory listing output between platforms"""
        warnings = []
        
        # Windows dir command to Unix ls format
        if source_platform == Platform.WINDOWS and target_platform in [Platform.LINUX, Platform.MACOS]:
            # Look for Windows dir output pattern - more flexible matching
            dir_pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}\s+[AP]M)\s+(<DIR>|\d+)\s+(.+)'
            matches = re.findall(dir_pattern, content)
            
            if matches:
                # Convert to Unix-like format
                adapted_content = content
                for date, time, size, name in reversed(matches):  # Process in reverse order
                    if size == '<DIR>':
                        permissions = 'drwxr-xr-x'
                        size_str = '4096'
                    else:
                        permissions = '-rw-r--r--'
                        size_str = size.strip()
                    
                    unix_line = f"{permissions} 1 user user {size_str.rjust(8)} {date} {name.strip()}"
                    
                    # Find and replace the exact line
                    original_pattern = rf'{re.escape(date)}\s+{re.escape(time)}\s+{re.escape(size)}\s+{re.escape(name)}'
                    adapted_content = re.sub(original_pattern, unix_line, adapted_content)
                
                content = adapted_content
                warnings.append("Converted Windows directory listing to Unix format")
        
        return content, warnings
    
    def _adapt_process_listing(self, content: str, source_platform: Platform, 
                              target_platform: Platform) -> Tuple[str, List[str]]:
        """Adapt process listing output between platforms"""
        warnings = []
        
        # Windows tasklist to Unix ps format
        if source_platform == Platform.WINDOWS and target_platform in [Platform.LINUX, Platform.MACOS]:
            # Look for Windows tasklist output - be more specific about the pattern
            tasklist_pattern = r'([^\s]+\.exe)\s+(\d+)\s+(Console|Services)\s+(\d+)\s+([\d,]+\s+K)'
            if re.search(tasklist_pattern, content):
                # Add Unix-style header if not present and this looks like a process list
                if 'PID' not in content and 'COMMAND' not in content and '.exe' in content:
                    content = "  PID TTY      STAT   TIME COMMAND\n" + content
                    warnings.append("Added Unix-style process listing header")
        
        return content, warnings
    
    def _adapt_environment_variables(self, content: str, source_platform: Platform, 
                                    target_platform: Platform) -> Tuple[str, List[str]]:
        """Adapt environment variable syntax between platforms"""
        warnings = []
        
        # Windows %VAR% to Unix $VAR
        if source_platform == Platform.WINDOWS and target_platform in [Platform.LINUX, Platform.MACOS]:
            env_pattern = r'%([A-Za-z_][A-Za-z0-9_]*)%'
            matches = re.findall(env_pattern, content)
            for var_name in matches:
                windows_var = f"%{var_name}%"
                unix_var = f"${var_name}"
                content = content.replace(windows_var, unix_var)
            
            if matches:
                warnings.append("Converted Windows environment variables to Unix format")
        
        # Unix $VAR to Windows %VAR%
        elif source_platform in [Platform.LINUX, Platform.MACOS] and target_platform == Platform.WINDOWS:
            env_pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)'
            matches = re.findall(env_pattern, content)
            for var_name in matches:
                unix_var = f"${var_name}"
                windows_var = f"%{var_name}%"
                content = content.replace(unix_var, windows_var)
            
            if matches:
                warnings.append("Converted Unix environment variables to Windows format")
        
        return content, warnings
    
    def _analyze_content(self, original: str, adapted: str) -> Dict[str, Any]:
        """Analyze content changes during adaptation"""
        return {
            "original_length": len(original),
            "adapted_length": len(adapted),
            "length_change": len(adapted) - len(original),
            "original_lines": len(original.splitlines()),
            "adapted_lines": len(adapted.splitlines()),
            "lines_change": len(adapted.splitlines()) - len(original.splitlines()),
            "similarity_ratio": self._calculate_similarity(original, adapted)
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        common_chars = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
        max_length = max(len(text1), len(text2))
        
        return common_chars / max_length if max_length > 0 else 1.0
    
    def create_fallback_formatter(self, platform: Platform) -> OutputFormatter:
        """Create a fallback formatter for when adaptation fails"""
        options = FormattingOptions(
            max_output_size=512 * 1024,  # 512KB
            max_lines=500,
            pagination_mode=PaginationMode.TRUNCATE,
            preserve_formatting=True,
            include_metadata=True
        )
        
        return OutputFormatter(options)
    
    def format_with_adaptation(self, output: str, format_type: OutputFormat,
                              source_platform: Platform, 
                              target_platform: Optional[Platform] = None) -> FormattedOutput:
        """Format output with platform adaptation"""
        try:
            # First adapt the output
            adaptation_result = self.adapt_output(output, source_platform, target_platform)
            
            # Then format the adapted output
            formatter = OutputFormatter()
            formatted_result = formatter.format_output(
                adaptation_result.adapted_content, 
                format_type, 
                adaptation_result.target_platform
            )
            
            # Add adaptation metadata to the formatted result
            formatted_result.metadata["platform_adaptation"] = {
                "adaptations_applied": adaptation_result.adaptations_applied,
                "adaptation_warnings": adaptation_result.warnings,
                "source_platform": adaptation_result.platform_detected.value,
                "target_platform": adaptation_result.target_platform.value
            }
            
            # Merge warnings
            formatted_result.warnings.extend(adaptation_result.warnings)
            
            return formatted_result
            
        except Exception as e:
            # Fallback to basic formatting without adaptation
            fallback_formatter = self.create_fallback_formatter(source_platform)
            result = fallback_formatter.format_output(output, format_type, source_platform)
            result.warnings.append(f"Platform adaptation failed: {str(e)}")
            return result


def create_default_adapter() -> PlatformOutputAdapter:
    """Create a default platform adapter with standard options"""
    return PlatformOutputAdapter(PlatformAdaptationOptions())


def create_strict_adapter() -> PlatformOutputAdapter:
    """Create a strict adapter that applies all adaptations"""
    options = PlatformAdaptationOptions(
        normalize_paths=True,
        standardize_errors=True,
        convert_line_endings=True,
        normalize_encoding=True,
        adapt_command_output=True,
        preserve_original_format=False
    )
    return PlatformOutputAdapter(options)


def create_minimal_adapter() -> PlatformOutputAdapter:
    """Create a minimal adapter that only does essential adaptations"""
    options = PlatformAdaptationOptions(
        normalize_paths=False,
        standardize_errors=True,
        convert_line_endings=False,
        normalize_encoding=True,
        adapt_command_output=False,
        preserve_original_format=True
    )
    return PlatformOutputAdapter(options)