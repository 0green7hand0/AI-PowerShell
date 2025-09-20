"""PowerShell Executor with cross-platform support and version management"""

import os
import platform
import subprocess
import shutil
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    ExecutorInterface, Platform, CommandContext, ExecutionResult, 
    OutputFormat, PerformanceMetrics
)
from config.models import ExecutionConfig


class PowerShellVersion(Enum):
    """PowerShell version types"""
    WINDOWS_POWERSHELL = "windows_powershell"  # 5.1 and below
    POWERSHELL_CORE = "powershell_core"       # 6.0 and above


@dataclass
class PowerShellInfo:
    """Information about detected PowerShell installation"""
    version: str
    edition: str
    executable_path: str
    version_type: PowerShellVersion
    platform: Platform
    is_available: bool
    supports_core_features: bool
    architecture: str


class PowerShellDetector:
    """Detects and manages PowerShell installations across platforms"""
    
    def __init__(self):
        self.current_platform = self._detect_platform()
        self._powershell_cache: Optional[PowerShellInfo] = None
    
    def _detect_platform(self) -> Platform:
        """Detect the current platform"""
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        else:
            # Default to Linux for unknown Unix-like systems
            return Platform.LINUX
    
    def detect_powershell(self, force_refresh: bool = False) -> PowerShellInfo:
        """
        Detect available PowerShell installation
        
        Args:
            force_refresh: Force re-detection even if cached
            
        Returns:
            PowerShellInfo object with detection results
        """
        if self._powershell_cache and not force_refresh:
            return self._powershell_cache
        
        # Try PowerShell Core first (cross-platform)
        pwsh_info = self._try_detect_powershell_core()
        if pwsh_info.is_available:
            self._powershell_cache = pwsh_info
            return pwsh_info
        
        # Fall back to Windows PowerShell on Windows
        if self.current_platform == Platform.WINDOWS:
            ps_info = self._try_detect_windows_powershell()
            if ps_info.is_available:
                self._powershell_cache = ps_info
                return ps_info
        
        # No PowerShell found
        self._powershell_cache = PowerShellInfo(
            version="",
            edition="",
            executable_path="",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=self.current_platform,
            is_available=False,
            supports_core_features=False,
            architecture=""
        )
        return self._powershell_cache
    
    def _try_detect_powershell_core(self) -> PowerShellInfo:
        """Try to detect PowerShell Core (pwsh)"""
        executable_names = ["pwsh", "pwsh.exe"]
        
        for exe_name in executable_names:
            exe_path = shutil.which(exe_name)
            if exe_path:
                try:
                    # Get version information
                    result = subprocess.run(
                        [exe_path, "-NoProfile", "-Command", "$PSVersionTable | ConvertTo-Json"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        version_info = json.loads(result.stdout)
                        return PowerShellInfo(
                            version=version_info.get("PSVersion", "Unknown"),
                            edition=version_info.get("PSEdition", "Core"),
                            executable_path=exe_path,
                            version_type=PowerShellVersion.POWERSHELL_CORE,
                            platform=self.current_platform,
                            is_available=True,
                            supports_core_features=True,
                            architecture=version_info.get("Platform", platform.machine())
                        )
                except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                    continue
        
        return PowerShellInfo(
            version="",
            edition="",
            executable_path="",
            version_type=PowerShellVersion.POWERSHELL_CORE,
            platform=self.current_platform,
            is_available=False,
            supports_core_features=False,
            architecture=""
        )
    
    def _try_detect_windows_powershell(self) -> PowerShellInfo:
        """Try to detect Windows PowerShell (Windows only)"""
        if self.current_platform != Platform.WINDOWS:
            return PowerShellInfo(
                version="",
                edition="",
                executable_path="",
                version_type=PowerShellVersion.WINDOWS_POWERSHELL,
                platform=self.current_platform,
                is_available=False,
                supports_core_features=False,
                architecture=""
            )
        
        # Common Windows PowerShell paths
        possible_paths = [
            "powershell.exe",  # In PATH
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe"
        ]
        
        for exe_path in possible_paths:
            try:
                # Check if it's in PATH first
                if exe_path == "powershell.exe":
                    full_path = shutil.which(exe_path)
                    if not full_path:
                        continue
                    exe_path = full_path
                elif not Path(exe_path).exists():
                    continue
                
                # Get version information
                result = subprocess.run(
                    [exe_path, "-NoProfile", "-Command", "$PSVersionTable | ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version_info = json.loads(result.stdout)
                    version = version_info.get("PSVersion", "Unknown")
                    
                    # Check if it's actually Windows PowerShell (5.1 or below)
                    if isinstance(version, str) and version.startswith("5."):
                        return PowerShellInfo(
                            version=version,
                            edition=version_info.get("PSEdition", "Desktop"),
                            executable_path=exe_path,
                            version_type=PowerShellVersion.WINDOWS_POWERSHELL,
                            platform=self.current_platform,
                            is_available=True,
                            supports_core_features=False,  # Limited cross-platform features
                            architecture=version_info.get("Platform", platform.machine())
                        )
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                continue
        
        return PowerShellInfo(
            version="",
            edition="",
            executable_path="",
            version_type=PowerShellVersion.WINDOWS_POWERSHELL,
            platform=self.current_platform,
            is_available=False,
            supports_core_features=False,
            architecture=""
        )
    
    def get_recommended_installation_guide(self) -> str:
        """Get installation guide for PowerShell on current platform"""
        if self.current_platform == Platform.WINDOWS:
            return (
                "PowerShell Core (recommended):\n"
                "1. Download from: https://github.com/PowerShell/PowerShell/releases\n"
                "2. Or install via winget: winget install Microsoft.PowerShell\n"
                "3. Or install via Chocolatey: choco install powershell-core\n\n"
                "Windows PowerShell (legacy):\n"
                "Should be pre-installed on Windows. If missing, enable Windows Features."
            )
        elif self.current_platform == Platform.LINUX:
            return (
                "PowerShell Core installation:\n"
                "Ubuntu/Debian: sudo apt install powershell\n"
                "CentOS/RHEL: sudo yum install powershell\n"
                "Arch Linux: yay -S powershell-bin\n"
                "Or download from: https://github.com/PowerShell/PowerShell/releases"
            )
        elif self.current_platform == Platform.MACOS:
            return (
                "PowerShell Core installation:\n"
                "Homebrew: brew install powershell\n"
                "Or download from: https://github.com/PowerShell/PowerShell/releases"
            )
        else:
            return "Please visit https://github.com/PowerShell/PowerShell/releases for installation instructions."


class PowerShellExecutor(ExecutorInterface):
    """Cross-platform PowerShell command executor with version management"""
    
    def __init__(self, config: ExecutionConfig, detector: Optional[PowerShellDetector] = None):
        self.config = config
        self.detector = detector or PowerShellDetector()
        self.powershell_info = self.detector.detect_powershell()
        
        # Override executable if specified in config
        if config.powershell_executable:
            self._validate_custom_executable(config.powershell_executable)
    
    def _validate_custom_executable(self, executable_path: str) -> None:
        """Validate and update PowerShell info for custom executable"""
        if not Path(executable_path).exists() and not shutil.which(executable_path):
            raise FileNotFoundError(f"PowerShell executable not found: {executable_path}")
        
        # Try to get version info for custom executable
        try:
            result = subprocess.run(
                [executable_path, "-NoProfile", "-Command", "$PSVersionTable | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_info = json.loads(result.stdout)
                version = version_info.get("PSVersion", "Unknown")
                
                # Determine version type
                version_type = PowerShellVersion.POWERSHELL_CORE
                if isinstance(version, str) and version.startswith("5."):
                    version_type = PowerShellVersion.WINDOWS_POWERSHELL
                
                self.powershell_info = PowerShellInfo(
                    version=version,
                    edition=version_info.get("PSEdition", "Unknown"),
                    executable_path=executable_path,
                    version_type=version_type,
                    platform=self.detector.current_platform,
                    is_available=True,
                    supports_core_features=version_type == PowerShellVersion.POWERSHELL_CORE,
                    architecture=version_info.get("Platform", platform.machine())
                )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            raise RuntimeError(f"Failed to validate PowerShell executable {executable_path}: {e}")
    
    def is_available(self) -> bool:
        """Check if PowerShell is available"""
        return self.powershell_info.is_available
    
    def get_powershell_info(self) -> Dict[str, Any]:
        """Get PowerShell environment information"""
        if not self.is_available():
            return {
                "available": False,
                "error": "PowerShell not found",
                "installation_guide": self.detector.get_recommended_installation_guide(),
                "platform": self.detector.current_platform.value
            }
        
        return {
            "available": True,
            "version": self.powershell_info.version,
            "edition": self.powershell_info.edition,
            "executable_path": self.powershell_info.executable_path,
            "version_type": self.powershell_info.version_type.value,
            "platform": self.powershell_info.platform.value,
            "supports_core_features": self.powershell_info.supports_core_features,
            "architecture": self.powershell_info.architecture
        }
    
    def execute_command(self, command: str, context: CommandContext) -> ExecutionResult:
        """Execute PowerShell command with proper encoding and error handling"""
        if not self.is_available():
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr="PowerShell is not available on this system",
                execution_time=0.0,
                platform=self.detector.current_platform,
                sandbox_used=False
            )
        
        start_time = time.time()
        
        try:
            # Prepare the command with proper encoding handling
            full_command = self._prepare_command(command, context)
            
            # Execute the command
            result = subprocess.run(
                full_command,
                cwd=context.current_directory,
                env=self._prepare_environment(context),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Handle encoding errors gracefully
                timeout=self.config.default_timeout
            )
            
            execution_time = time.time() - start_time
            
            # Handle output size limits
            stdout = self._truncate_output(result.stdout)
            stderr = self._truncate_output(result.stderr)
            
            return ExecutionResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                platform=self.detector.current_platform,
                sandbox_used=False  # Sandbox integration will be handled by security engine
            )
            
        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Command timed out after {self.config.default_timeout} seconds",
                execution_time=execution_time,
                platform=self.detector.current_platform,
                sandbox_used=False
            )
            
        except subprocess.CalledProcessError as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                return_code=e.returncode,
                stdout=self._truncate_output(e.stdout or ""),
                stderr=self._truncate_output(e.stderr or ""),
                execution_time=execution_time,
                platform=self.detector.current_platform,
                sandbox_used=False
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Unexpected error during command execution: {str(e)}",
                execution_time=execution_time,
                platform=self.detector.current_platform,
                sandbox_used=False
            )
    
    def _prepare_command(self, command: str, context: CommandContext) -> List[str]:
        """Prepare command for execution with proper arguments"""
        executable = self.powershell_info.executable_path
        
        # Base arguments for PowerShell execution
        args = [
            executable,
            "-NoProfile",  # Don't load user profile for faster startup
            "-NonInteractive",  # Don't prompt for user input
            "-NoLogo",  # Don't show PowerShell logo
            "-Command",  # Execute the following command
            command
        ]
        
        # Add execution policy bypass for Windows PowerShell if needed
        if (self.powershell_info.version_type == PowerShellVersion.WINDOWS_POWERSHELL and 
            self.detector.current_platform == Platform.WINDOWS):
            args.insert(1, "-ExecutionPolicy")
            args.insert(2, "Bypass")
        
        return args
    
    def _prepare_environment(self, context: CommandContext) -> Dict[str, str]:
        """Prepare environment variables for command execution"""
        env = os.environ.copy()
        
        # Add context environment variables
        env.update(context.environment_variables)
        
        # Add config environment variables
        env.update(self.config.environment_variables)
        
        # Ensure UTF-8 encoding for output
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Set PowerShell output encoding
        if self.detector.current_platform == Platform.WINDOWS:
            env['POWERSHELL_TELEMETRY_OPTOUT'] = '1'  # Disable telemetry
        
        return env
    
    def _truncate_output(self, output: str) -> str:
        """Truncate output if it exceeds maximum size"""
        if len(output.encode('utf-8')) > self.config.max_output_size:
            # Calculate how many characters we can keep
            max_chars = self.config.max_output_size // 2  # Conservative estimate
            truncated = output[:max_chars]
            return truncated + f"\n... [Output truncated - exceeded {self.config.max_output_size} bytes]"
        return output
    
    def format_output(self, raw_output: str, format_type: OutputFormat) -> str:
        """Format command output according to specified format"""
        if not raw_output.strip():
            return ""
        
        if format_type == OutputFormat.RAW:
            return raw_output
        
        elif format_type == OutputFormat.JSON:
            try:
                # Try to parse as JSON first
                import json
                parsed = json.loads(raw_output)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in a JSON structure
                return json.dumps({
                    "output": raw_output,
                    "format": "text",
                    "timestamp": datetime.now().isoformat()
                }, indent=2, ensure_ascii=False)
        
        elif format_type == OutputFormat.TABLE:
            return self._format_as_table(raw_output)
        
        else:
            return raw_output
    
    def _format_as_table(self, output: str) -> str:
        """Format output as a table if possible"""
        lines = output.strip().split('\n')
        
        if len(lines) < 2:
            return output
        
        # Try to detect if this looks like tabular data
        # Look for consistent column separators
        potential_separators = ['\t', '  ', ' | ', ',']
        
        for separator in potential_separators:
            if self._is_tabular_with_separator(lines, separator):
                return self._format_table_with_separator(lines, separator)
        
        # If no tabular format detected, return as-is
        return output
    
    def _is_tabular_with_separator(self, lines: List[str], separator: str) -> bool:
        """Check if lines form a table with the given separator"""
        if len(lines) < 2:
            return False
        
        # Check if header and at least one data row have same number of columns
        header_cols = len(lines[0].split(separator))
        if header_cols < 2:
            return False
        
        # Check first few data rows
        for i in range(1, min(4, len(lines))):
            if len(lines[i].split(separator)) != header_cols:
                return False
        
        return True
    
    def _format_table_with_separator(self, lines: List[str], separator: str) -> str:
        """Format lines as a proper table"""
        rows = [line.split(separator) for line in lines]
        
        # Calculate column widths
        col_widths = []
        for col_idx in range(len(rows[0])):
            max_width = max(len(str(row[col_idx]).strip()) for row in rows)
            col_widths.append(max_width)
        
        # Format the table
        formatted_lines = []
        for row_idx, row in enumerate(rows):
            formatted_row = " | ".join(
                str(cell).strip().ljust(col_widths[col_idx]) 
                for col_idx, cell in enumerate(row)
            )
            formatted_lines.append(formatted_row)
            
            # Add separator line after header
            if row_idx == 0:
                separator_line = " | ".join("-" * width for width in col_widths)
                formatted_lines.append(separator_line)
        
        return "\n".join(formatted_lines)
    
    def adapt_for_platform(self, command: str, target_platform: Platform) -> str:
        """Adapt command for specific platform"""
        if not command.strip():
            return command
        
        # Start with the original command
        adapted_command = command
        
        # Apply environment variable adaptations first
        adapted_command = self._adapt_environment_variables(adapted_command, target_platform)
        
        # Apply path adaptations
        adapted_command = self._adapt_paths(adapted_command, target_platform)
        
        # Apply platform-specific command adaptations
        adapted_command = self._adapt_platform_specific_commands(adapted_command, target_platform)
        
        return adapted_command
    
    def _adapt_paths(self, command: str, target_platform: Platform) -> str:
        """Adapt file paths for target platform"""
        adapted = command
        import re
        
        if target_platform == Platform.WINDOWS:
            # Convert Unix paths to Windows paths
            
            # Pattern for Unix relative paths with forward slashes (do this first)
            unix_rel_pattern = r'\./[a-zA-Z0-9_/\.\-]+'
            matches = re.findall(unix_rel_pattern, adapted)
            for match in matches:
                windows_path = match.replace('/', '\\')
                adapted = adapted.replace(match, windows_path)
            
            # Pattern for Unix absolute paths (starting with /) - but not ./
            unix_abs_pattern = r'(?<!\.)\/[a-zA-Z0-9_/\.\-]+'
            matches = re.findall(unix_abs_pattern, adapted)
            for match in matches:
                windows_path = self._convert_unix_to_windows_path(match)
                adapted = adapted.replace(match, windows_path)
            
        else:  # Linux or macOS
            # Convert Windows paths to Unix paths
            
            # Pattern for Windows drive paths (C:\, D:\, etc.)
            win_drive_pattern = r'[A-Za-z]:\\[a-zA-Z0-9_\\\.\s\-]*'
            matches = re.findall(win_drive_pattern, adapted)
            for match in matches:
                unix_path = self._convert_windows_to_unix_path(match)
                adapted = adapted.replace(match, unix_path)
            
            # Pattern for Windows relative paths with backslashes
            win_rel_pattern = r'\.\\[a-zA-Z0-9_\\\.\-]+'
            matches = re.findall(win_rel_pattern, adapted)
            for match in matches:
                unix_path = match.replace('\\', '/')
                adapted = adapted.replace(match, unix_path)
        
        return adapted
    
    def _convert_unix_to_windows_path(self, unix_path: str) -> str:
        """Convert Unix absolute path to Windows equivalent"""
        # Simple conversion - in real implementation might need more sophisticated mapping
        if unix_path.startswith('/tmp'):
            return unix_path.replace('/tmp', 'C:\\temp').replace('/', '\\')
        elif unix_path.startswith('/home'):
            return unix_path.replace('/home', 'C:\\Users').replace('/', '\\')
        elif unix_path.startswith('/usr'):
            return unix_path.replace('/usr', 'C:\\Program Files').replace('/', '\\')
        elif unix_path.startswith('/var'):
            return unix_path.replace('/var', 'C:\\ProgramData').replace('/', '\\')
        else:
            # Generic conversion
            return ('C:' + unix_path).replace('/', '\\')
    
    def _convert_windows_to_unix_path(self, windows_path: str) -> str:
        """Convert Windows path to Unix equivalent"""
        # Remove drive letter and convert separators
        if len(windows_path) >= 3 and windows_path[1:3] == ':\\':
            # Has drive letter
            path_without_drive = windows_path[3:]
            unix_path = '/' + path_without_drive.replace('\\', '/')
            
            # Map common Windows directories to Unix equivalents
            if unix_path.startswith('/temp'):
                return unix_path.replace('/temp', '/tmp')
            elif unix_path.startswith('/Users'):
                return unix_path.replace('/Users', '/home')
            elif unix_path.startswith('/Program Files'):
                return unix_path.replace('/Program Files', '/usr')
            elif unix_path.startswith('/ProgramData'):
                return unix_path.replace('/ProgramData', '/var')
            else:
                return unix_path
        else:
            # No drive letter, just convert separators
            return windows_path.replace('\\', '/')
    
    def _adapt_environment_variables(self, command: str, target_platform: Platform) -> str:
        """Adapt environment variable syntax for target platform"""
        adapted = command
        
        if target_platform == Platform.WINDOWS:
            # Convert Unix environment variables ($VAR) to Windows (%VAR%)
            import re
            
            # Pattern for Unix environment variables
            unix_env_pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)'
            adapted = re.sub(unix_env_pattern, r'%\1%', adapted)
            
            # Convert common Unix environment variables to Windows equivalents
            env_mappings = {
                '%HOME%': '%USERPROFILE%',
                '%USER%': '%USERNAME%',
                '%SHELL%': '%COMSPEC%'
            }
            
            for unix_var, windows_var in env_mappings.items():
                adapted = adapted.replace(unix_var, windows_var)
                
        else:  # Linux or macOS
            # Convert Windows environment variables (%VAR%) to Unix ($VAR)
            import re
            
            # Pattern for Windows environment variables
            win_env_pattern = r'%([A-Za-z_][A-Za-z0-9_]*)%'
            adapted = re.sub(win_env_pattern, r'$\1', adapted)
            
            # Convert common Windows environment variables to Unix equivalents
            env_mappings = {
                '$USERPROFILE': '$HOME',
                '$USERNAME': '$USER',
                '$COMSPEC': '$SHELL'
            }
            
            for windows_var, unix_var in env_mappings.items():
                adapted = adapted.replace(windows_var, unix_var)
        
        return adapted
    
    def _adapt_platform_specific_commands(self, command: str, target_platform: Platform) -> str:
        """Adapt platform-specific commands and cmdlets"""
        adapted = command
        
        # Common command adaptations
        if target_platform == Platform.WINDOWS:
            # Adapt Unix-style commands to Windows equivalents
            command_mappings = [
                (r'\bls\b(?=\s|$)', 'Get-ChildItem'),
                (r'\bcat\b(?=\s)', 'Get-Content'),
                (r'\bgrep\b(?=\s)', 'Select-String'),
                (r'\bps\b(?=\s|$)', 'Get-Process'),
                (r'\bkill\b(?=\s)', 'Stop-Process -Id'),
                (r'\bwhich\b(?=\s)', 'Get-Command'),
                (r'\bpwd\b(?=\s|$)', 'Get-Location'),
                (r'\bcd\b(?=\s)', 'Set-Location'),
                (r'\bmkdir\b(?=\s)', 'New-Item -ItemType Directory -Path'),
                (r'\brm\b(?=\s)', 'Remove-Item'),
                (r'\bcp\b(?=\s)', 'Copy-Item'),
                (r'\bmv\b(?=\s)', 'Move-Item')
            ]
        else:  # Linux or macOS
            # Adapt Windows-style commands to Unix equivalents
            command_mappings = [
                (r'\bdir\b(?=\s|$)', 'ls'),
                (r'\btype\b(?=\s)', 'cat'),
                (r'\bfindstr\b(?=\s)', 'grep'),
                (r'\btasklist\b(?=\s|$)', 'ps aux'),
                (r'\btaskkill\b(?=\s)', 'kill'),
                (r'\bwhere\b(?=\s)', 'which'),
                (r'\bmd\b(?=\s)', 'mkdir'),
                (r'\bdel\b(?=\s)', 'rm'),
                (r'\bcopy\b(?=\s)', 'cp'),
                (r'\bmove\b(?=\s)', 'mv'),
                (r'\bren\b(?=\s)', 'mv')
            ]
        
        # Apply command mappings using regex
        import re
        for pattern, replacement in command_mappings:
            adapted = re.sub(pattern, replacement, adapted)
        
        return adapted