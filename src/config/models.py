"""Configuration data models and schemas"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path
import os

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import LogLevel, LogFormat, LogOutput, Platform


@dataclass
class ModelConfig:
    """AI model configuration"""
    model_type: str = "llama-cpp"  # "llama-cpp", "ollama", etc.
    model_path: str = ""
    context_length: int = 4096
    temperature: float = 0.7
    max_tokens: int = 512
    gpu_layers: int = 0
    threads: int = 4
    
    def __post_init__(self):
        if not self.model_path:
            # Default model path based on environment
            home_dir = Path.home()
            self.model_path = str(home_dir / ".ai-powershell-assistant" / "models" / "default.gguf")


@dataclass
class SecurityConfig:
    """Security engine configuration"""
    whitelist_path: str = ""
    sandbox_enabled: bool = True
    sandbox_image: str = "mcr.microsoft.com/powershell:latest"
    require_confirmation_for_admin: bool = True
    audit_log_path: str = ""
    max_sandbox_memory: str = "512m"
    max_sandbox_cpu: str = "1.0"
    sandbox_timeout: int = 300  # seconds
    
    def __post_init__(self):
        if not self.whitelist_path:
            config_dir = Path.home() / ".ai-powershell-assistant" / "config"
            self.whitelist_path = str(config_dir / "security_whitelist.json")
        
        if not self.audit_log_path:
            log_dir = Path.home() / ".ai-powershell-assistant" / "logs"
            self.audit_log_path = str(log_dir / "audit.log")


@dataclass
class LoggingConfig:
    """Logging engine configuration"""
    log_level: LogLevel = LogLevel.INFO
    log_format: LogFormat = LogFormat.JSON
    log_output: List[LogOutput] = field(default_factory=lambda: [LogOutput.FILE, LogOutput.CONSOLE])
    audit_log_path: str = ""
    performance_log_path: str = ""
    max_log_file_size: str = "100MB"
    log_retention_days: int = 30
    enable_correlation_tracking: bool = True
    sensitive_data_masking: bool = True
    
    def __post_init__(self):
        if not self.audit_log_path:
            log_dir = Path.home() / ".ai-powershell-assistant" / "logs"
            self.audit_log_path = str(log_dir / "audit.log")
        
        if not self.performance_log_path:
            log_dir = Path.home() / ".ai-powershell-assistant" / "logs"
            self.performance_log_path = str(log_dir / "performance.log")


@dataclass
class StorageConfig:
    """Storage configuration"""
    data_directory: str = ""
    history_max_entries: int = 10000
    preferences_file: str = ""
    cache_directory: str = ""
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    
    def __post_init__(self):
        if not self.data_directory:
            self.data_directory = str(Path.home() / ".ai-powershell-assistant" / "data")
        
        if not self.preferences_file:
            self.preferences_file = str(Path(self.data_directory) / "user_preferences.json")
        
        if not self.cache_directory:
            self.cache_directory = str(Path.home() / ".ai-powershell-assistant" / "cache")


@dataclass
class ExecutionConfig:
    """PowerShell execution configuration"""
    default_timeout: int = 60  # seconds
    max_output_size: int = 1024 * 1024  # 1MB
    powershell_executable: str = ""
    environment_variables: Dict[str, str] = field(default_factory=dict)
    working_directory: str = ""
    
    def __post_init__(self):
        if not self.powershell_executable:
            # Auto-detect PowerShell executable
            if os.name == 'nt':  # Windows
                self.powershell_executable = "powershell.exe"
            else:  # Linux/macOS
                self.powershell_executable = "pwsh"
        
        if not self.working_directory:
            self.working_directory = str(Path.cwd())


@dataclass
class MCPServerConfig:
    """MCP server configuration"""
    host: str = "localhost"
    port: int = 8000
    max_concurrent_requests: int = 10
    request_timeout: int = 300  # seconds
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Tool-specific settings
    enable_natural_language_tool: bool = True
    enable_execute_command_tool: bool = True
    enable_system_info_tool: bool = True


@dataclass
class ServerConfig:
    """Main server configuration combining all components"""
    # Component configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    mcp_server: MCPServerConfig = field(default_factory=MCPServerConfig)
    
    # Global settings
    debug_mode: bool = False
    platform: Platform = Platform.WINDOWS
    version: str = "0.1.0"
    
    def __post_init__(self):
        # Auto-detect platform if not set
        import platform as plt
        system = plt.system().lower()
        if system == "windows":
            self.platform = Platform.WINDOWS
        elif system == "linux":
            self.platform = Platform.LINUX
        elif system == "darwin":
            self.platform = Platform.MACOS
        
        # Adjust log level for debug mode
        if self.debug_mode:
            self.logging.log_level = LogLevel.DEBUG