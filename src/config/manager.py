"""Configuration management with environment-based settings"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import asdict

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from .models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, StorageConfig, ExecutionConfig, MCPServerConfig
from interfaces.base import LogLevel, LogFormat, LogOutput, Platform


class ConfigurationManager:
    """Manages configuration loading, validation, and environment-based overrides"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config: ServerConfig = ServerConfig()
        self._ensure_directories()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        config_dir = Path.home() / ".ai-powershell-assistant" / "config"
        return str(config_dir / "config.yaml")
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create other required directories relative to config directory
        base_dir = config_path.parent.parent
        directories = [
            base_dir / "data",
            base_dir / "logs", 
            base_dir / "cache",
            base_dir / "models",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_configuration(self) -> ServerConfig:
        """Load configuration from file and environment variables"""
        # Start with default configuration
        self.config = ServerConfig()
        
        # Load from file if it exists
        if Path(self.config_file).exists():
            self._load_from_file()
        else:
            # Create default configuration file
            self.save_configuration()
        
        # Apply environment variable overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        return self.config
    
    def _load_from_file(self) -> None:
        """Load configuration from YAML or JSON file"""
        config_path = Path(self.config_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if data:
                self._update_config_from_dict(data)
                
        except Exception as e:
            print(f"Warning: Failed to load configuration from {config_path}: {e}")
            print("Using default configuration")
    
    def _update_config_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary data"""
        # Update model config
        if 'model' in data:
            model_data = data['model']
            for key, value in model_data.items():
                if hasattr(self.config.model, key):
                    setattr(self.config.model, key, value)
        
        # Update security config
        if 'security' in data:
            security_data = data['security']
            for key, value in security_data.items():
                if hasattr(self.config.security, key):
                    setattr(self.config.security, key, value)
        
        # Update logging config
        if 'logging' in data:
            logging_data = data['logging']
            for key, value in logging_data.items():
                if hasattr(self.config.logging, key):
                    if key == 'log_level' and isinstance(value, str):
                        setattr(self.config.logging, key, LogLevel(value.lower()))
                    elif key == 'log_format' and isinstance(value, str):
                        setattr(self.config.logging, key, LogFormat(value.lower()))
                    elif key == 'log_output' and isinstance(value, list):
                        setattr(self.config.logging, key, [LogOutput(v.lower()) for v in value])
                    else:
                        setattr(self.config.logging, key, value)
        
        # Update storage config
        if 'storage' in data:
            storage_data = data['storage']
            for key, value in storage_data.items():
                if hasattr(self.config.storage, key):
                    setattr(self.config.storage, key, value)
        
        # Update execution config
        if 'execution' in data:
            execution_data = data['execution']
            for key, value in execution_data.items():
                if hasattr(self.config.execution, key):
                    setattr(self.config.execution, key, value)
        
        # Update MCP server config
        if 'mcp_server' in data:
            mcp_data = data['mcp_server']
            for key, value in mcp_data.items():
                if hasattr(self.config.mcp_server, key):
                    setattr(self.config.mcp_server, key, value)
        
        # Update global settings
        global_keys = ['debug_mode', 'platform', 'version']
        for key in global_keys:
            if key in data and hasattr(self.config, key):
                if key == 'platform' and isinstance(data[key], str):
                    setattr(self.config, key, Platform(data[key].lower()))
                else:
                    setattr(self.config, key, data[key])
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            # Model configuration
            'AI_PS_MODEL_TYPE': ('model', 'model_type'),
            'AI_PS_MODEL_PATH': ('model', 'model_path'),
            'AI_PS_MODEL_CONTEXT_LENGTH': ('model', 'context_length', int),
            'AI_PS_MODEL_TEMPERATURE': ('model', 'temperature', float),
            'AI_PS_MODEL_MAX_TOKENS': ('model', 'max_tokens', int),
            
            # Security configuration
            'AI_PS_SECURITY_SANDBOX_ENABLED': ('security', 'sandbox_enabled', bool),
            'AI_PS_SECURITY_SANDBOX_IMAGE': ('security', 'sandbox_image'),
            'AI_PS_SECURITY_WHITELIST_PATH': ('security', 'whitelist_path'),
            'AI_PS_SECURITY_REQUIRE_ADMIN_CONFIRMATION': ('security', 'require_confirmation_for_admin', bool),
            
            # Logging configuration
            'AI_PS_LOG_LEVEL': ('logging', 'log_level', lambda x: LogLevel(x.lower())),
            'AI_PS_LOG_FORMAT': ('logging', 'log_format', lambda x: LogFormat(x.lower())),
            'AI_PS_AUDIT_LOG_PATH': ('logging', 'audit_log_path'),
            
            # Storage configuration
            'AI_PS_DATA_DIRECTORY': ('storage', 'data_directory'),
            'AI_PS_CACHE_DIRECTORY': ('storage', 'cache_directory'),
            
            # Execution configuration
            'AI_PS_POWERSHELL_EXECUTABLE': ('execution', 'powershell_executable'),
            'AI_PS_DEFAULT_TIMEOUT': ('execution', 'default_timeout', int),
            
            # MCP Server configuration
            'AI_PS_MCP_HOST': ('mcp_server', 'host'),
            'AI_PS_MCP_PORT': ('mcp_server', 'port', int),
            
            # Global settings
            'AI_PS_DEBUG_MODE': ('debug_mode', bool),
            'AI_PS_PLATFORM': ('platform', lambda x: Platform(x.lower())),
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_config_value(config_path, env_value)
    
    def _set_config_value(self, config_path: Union[tuple, str], value: str) -> None:
        """Set configuration value from environment variable"""
        try:
            if isinstance(config_path, tuple):
                if len(config_path) == 2:
                    # Check if it's a direct config attribute (like debug_mode)
                    first_element = config_path[0]
                    if hasattr(self.config, first_element):
                        current_value = getattr(self.config, first_element)
                        # If current value is not a config object (has no __dict__), it's a direct attribute
                        if not hasattr(current_value, '__dict__'):
                            # Direct config attribute with converter
                            key, converter = config_path
                            if converter == bool:
                                converted_value = value.lower() in ('true', '1', 'yes', 'on')
                            elif converter == int:
                                converted_value = int(value)
                            elif converter == float:
                                converted_value = float(value)
                            elif callable(converter):
                                converted_value = converter(value)
                            else:
                                converted_value = value
                            setattr(self.config, key, converted_value)
                            return
                    
                    # Section.key format
                    section, key = config_path
                    if hasattr(self.config, section):
                        section_obj = getattr(self.config, section)
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
                            
                elif len(config_path) == 3:
                    section, key, converter = config_path
                    
                    # Convert value
                    if converter == bool:
                        converted_value = value.lower() in ('true', '1', 'yes', 'on')
                    elif converter == int:
                        converted_value = int(value)
                    elif converter == float:
                        converted_value = float(value)
                    elif callable(converter):
                        converted_value = converter(value)
                    else:
                        converted_value = value
                    
                    # Set value
                    if hasattr(self.config, section):
                        section_obj = getattr(self.config, section)
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, converted_value)
            else:
                # Direct config attribute
                if isinstance(config_path, str):
                    key = config_path
                    converted_value = value
                    if hasattr(self.config, key):
                        setattr(self.config, key, converted_value)
                    
        except Exception as e:
            print(f"Warning: Failed to set config value for {config_path}: {e}")
    
    def _validate_configuration(self) -> None:
        """Validate configuration values"""
        # Validate model configuration
        if self.config.model.context_length <= 0:
            raise ValueError("Model context length must be positive")
        
        if not (0.0 <= self.config.model.temperature <= 2.0):
            raise ValueError("Model temperature must be between 0.0 and 2.0")
        
        # Validate security configuration
        if self.config.security.sandbox_timeout <= 0:
            raise ValueError("Sandbox timeout must be positive")
        
        # Validate execution configuration
        if self.config.execution.default_timeout <= 0:
            raise ValueError("Default execution timeout must be positive")
        
        # Validate MCP server configuration
        if not (1 <= self.config.mcp_server.port <= 65535):
            raise ValueError("MCP server port must be between 1 and 65535")
    
    def save_configuration(self) -> None:
        """Save current configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert configuration to dictionary
        config_dict = asdict(self.config)
        
        # Convert enums to strings for serialization
        self._convert_enums_to_strings(config_dict)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save configuration to {config_path}: {e}")
    
    def _convert_enums_to_strings(self, data: Dict[str, Any]) -> None:
        """Convert enum values to strings for serialization"""
        for key, value in data.items():
            if isinstance(value, dict):
                self._convert_enums_to_strings(value)
            elif hasattr(value, 'value'):  # Enum
                data[key] = value.value
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if hasattr(item, 'value'):  # Enum
                        value[i] = item.value
    
    def get_config(self) -> ServerConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        self._update_config_from_dict(updates)
        self._validate_configuration()
        self.save_configuration()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = ServerConfig()
        self.save_configuration()


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_config() -> ServerConfig:
    """Get the global configuration"""
    return config_manager.get_config()


def load_config(config_file: Optional[str] = None) -> ServerConfig:
    """Load configuration from file"""
    if config_file:
        global config_manager
        config_manager = ConfigurationManager(config_file)
    return config_manager.load_configuration()


def save_config() -> None:
    """Save current configuration"""
    config_manager.save_configuration()