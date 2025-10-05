"""Tests for configuration management system"""

import os
import json
import yaml
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.manager import ConfigurationManager, get_config, load_config
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, StorageConfig, ExecutionConfig, MCPServerConfig
from interfaces.base import LogLevel, LogFormat, LogOutput, Platform


class TestConfigurationManager:
    """Test configuration manager functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.yaml")
        self.manager = ConfigurationManager(self.config_file)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_configuration_creation(self):
        """Test that default configuration is created correctly"""
        config = self.manager.load_configuration()
        
        assert isinstance(config, ServerConfig)
        assert isinstance(config.model, ModelConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.logging, LoggingConfig)
        
        # Check default values
        assert config.model.model_type == "llama-cpp"
        assert config.model.context_length == 4096
        assert config.security.sandbox_enabled is True
        assert config.logging.log_level == LogLevel.INFO
    
    def test_configuration_file_creation(self):
        """Test that configuration file is created when it doesn't exist"""
        assert not Path(self.config_file).exists()
        
        self.manager.load_configuration()
        
        assert Path(self.config_file).exists()
    
    def test_yaml_configuration_loading(self):
        """Test loading configuration from YAML file"""
        config_data = {
            'model': {
                'model_type': 'ollama',
                'context_length': 8192,
                'temperature': 0.5
            },
            'security': {
                'sandbox_enabled': False,
                'require_confirmation_for_admin': False
            },
            'logging': {
                'log_level': 'debug',
                'log_format': 'text'
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = self.manager.load_configuration()
        
        assert config.model.model_type == 'ollama'
        assert config.model.context_length == 8192
        assert config.model.temperature == 0.5
        assert config.security.sandbox_enabled is False
        assert config.security.require_confirmation_for_admin is False
        assert config.logging.log_level == LogLevel.DEBUG
        assert config.logging.log_format == LogFormat.TEXT
    
    def test_json_configuration_loading(self):
        """Test loading configuration from JSON file"""
        json_config_file = os.path.join(self.temp_dir, "test_config.json")
        self.manager.config_file = json_config_file
        
        config_data = {
            'model': {
                'model_type': 'transformers',
                'max_tokens': 1024
            },
            'execution': {
                'default_timeout': 120,
                'powershell_executable': 'pwsh'
            }
        }
        
        with open(json_config_file, 'w') as f:
            json.dump(config_data, f)
        
        config = self.manager.load_configuration()
        
        assert config.model.model_type == 'transformers'
        assert config.model.max_tokens == 1024
        assert config.execution.default_timeout == 120
        assert config.execution.powershell_executable == 'pwsh'
    
    def test_environment_variable_overrides(self):
        """Test that environment variables override configuration"""
        with patch.dict(os.environ, {
            'AI_PS_MODEL_TYPE': 'custom-model',
            'AI_PS_MODEL_CONTEXT_LENGTH': '2048',
            'AI_PS_MODEL_TEMPERATURE': '0.3',
            'AI_PS_SECURITY_SANDBOX_ENABLED': 'false',
            'AI_PS_LOG_LEVEL': 'error',
            'AI_PS_DEBUG_MODE': 'true'
        }):
            config = self.manager.load_configuration()
            
            assert config.model.model_type == 'custom-model'
            assert config.model.context_length == 2048
            assert config.model.temperature == 0.3
            assert config.security.sandbox_enabled is False
            assert config.logging.log_level == LogLevel.ERROR
            assert config.debug_mode is True
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Reset to valid config first
        self.manager.config = ServerConfig()
        
        # Test invalid context length
        self.manager.config.model.context_length = -1
        with pytest.raises(ValueError, match="context length must be positive"):
            self.manager._validate_configuration()
        
        # Reset and test invalid temperature
        self.manager.config = ServerConfig()
        self.manager.config.model.temperature = 3.0
        with pytest.raises(ValueError, match="temperature must be between"):
            self.manager._validate_configuration()
        
        # Reset and test invalid timeout
        self.manager.config = ServerConfig()
        self.manager.config.security.sandbox_timeout = -5
        with pytest.raises(ValueError, match="timeout must be positive"):
            self.manager._validate_configuration()
        
        # Reset and test invalid port
        self.manager.config = ServerConfig()
        self.manager.config.mcp_server.port = 70000
        with pytest.raises(ValueError, match="port must be between"):
            self.manager._validate_configuration()
    
    def test_configuration_update(self):
        """Test updating configuration"""
        updates = {
            'model': {
                'temperature': 0.8,
                'max_tokens': 256
            },
            'security': {
                'sandbox_enabled': False
            }
        }
        
        self.manager.update_config(updates)
        
        assert self.manager.config.model.temperature == 0.8
        assert self.manager.config.model.max_tokens == 256
        assert self.manager.config.security.sandbox_enabled is False
    
    def test_configuration_reset(self):
        """Test resetting configuration to defaults"""
        # Modify configuration
        self.manager.config.model.temperature = 0.9
        self.manager.config.security.sandbox_enabled = False
        
        # Reset to defaults
        self.manager.reset_to_defaults()
        
        assert self.manager.config.model.temperature == 0.7  # Default
        assert self.manager.config.security.sandbox_enabled is True  # Default
    
    def test_invalid_configuration_file_handling(self):
        """Test handling of invalid configuration files"""
        # Create invalid YAML file
        with open(self.config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        # Should not raise exception, should use defaults
        config = self.manager.load_configuration()
        assert isinstance(config, ServerConfig)
        assert config.model.model_type == "llama-cpp"  # Default value
    
    def test_directory_creation(self):
        """Test that required directories are created"""
        config_dir = Path(self.config_file).parent
        data_dir = config_dir.parent / "data"
        logs_dir = config_dir.parent / "logs"
        cache_dir = config_dir.parent / "cache"
        models_dir = config_dir.parent / "models"
        
        # Ensure directories don't exist initially
        for directory in [data_dir, logs_dir, cache_dir, models_dir]:
            if directory.exists():
                import shutil
                shutil.rmtree(directory)
        
        self.manager._ensure_directories()
        
        # Check that directories were created
        assert config_dir.exists()
        assert data_dir.exists()
        assert logs_dir.exists()
        assert cache_dir.exists()
        assert models_dir.exists()
    
    def test_enum_serialization(self):
        """Test that enums are properly serialized to strings"""
        config_dict = {
            'logging': {
                'log_level': LogLevel.DEBUG,
                'log_format': LogFormat.JSON,
                'log_output': [LogOutput.FILE, LogOutput.CONSOLE]
            },
            'platform': Platform.LINUX
        }
        
        self.manager._convert_enums_to_strings(config_dict)
        
        assert config_dict['logging']['log_level'] == 'debug'
        assert config_dict['logging']['log_format'] == 'json'
        assert config_dict['logging']['log_output'] == ['file', 'console']
        assert config_dict['platform'] == 'linux'


class TestGlobalConfigurationFunctions:
    """Test global configuration functions"""
    
    def test_get_config(self):
        """Test getting global configuration"""
        config = get_config()
        assert isinstance(config, ServerConfig)
    
    def test_load_config_with_file(self):
        """Test loading configuration with specific file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'model': {'model_type': 'test-model'},
                'debug_mode': True
            }
            yaml.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = load_config(temp_file)
            assert config.model.model_type == 'test-model'
            assert config.debug_mode is True
        finally:
            os.unlink(temp_file)


class TestConfigurationModels:
    """Test configuration model classes"""
    
    def test_model_config_defaults(self):
        """Test ModelConfig default values"""
        config = ModelConfig()
        
        assert config.model_type == "llama-cpp"
        assert config.context_length == 4096
        assert config.temperature == 0.7
        assert config.max_tokens == 512
        assert config.gpu_layers == 0
        assert config.threads == 4
        assert config.model_path.endswith("default.gguf")
    
    def test_security_config_defaults(self):
        """Test SecurityConfig default values"""
        config = SecurityConfig()
        
        assert config.sandbox_enabled is True
        assert config.sandbox_image == "mcr.microsoft.com/powershell:latest"
        assert config.require_confirmation_for_admin is True
        assert config.max_sandbox_memory == "512m"
        assert config.max_sandbox_cpu == "1.0"
        assert config.sandbox_timeout == 300
        assert config.whitelist_path.endswith("security_whitelist.json")
        assert config.audit_log_path.endswith("audit.log")
    
    def test_logging_config_defaults(self):
        """Test LoggingConfig default values"""
        config = LoggingConfig()
        
        assert config.log_level == LogLevel.INFO
        assert config.log_format == LogFormat.JSON
        assert LogOutput.FILE in config.log_output
        assert LogOutput.CONSOLE in config.log_output
        assert config.max_log_file_size == "100MB"
        assert config.log_retention_days == 30
        assert config.enable_correlation_tracking is True
        assert config.sensitive_data_masking is True
    
    def test_storage_config_defaults(self):
        """Test StorageConfig default values"""
        config = StorageConfig()
        
        assert config.history_max_entries == 10000
        assert config.backup_enabled is True
        assert config.backup_interval_hours == 24
        assert config.data_directory.endswith(os.path.join(".ai-powershell-assistant", "data"))
        assert config.preferences_file.endswith("user_preferences.json")
        assert config.cache_directory.endswith("cache")
    
    def test_execution_config_defaults(self):
        """Test ExecutionConfig default values"""
        config = ExecutionConfig()
        
        assert config.default_timeout == 60
        assert config.max_output_size == 1024 * 1024
        assert isinstance(config.environment_variables, dict)
        assert config.working_directory == str(Path.cwd())
        
        # PowerShell executable should be platform-appropriate
        if os.name == 'nt':
            assert config.powershell_executable == "powershell.exe"
        else:
            assert config.powershell_executable == "pwsh"
    
    def test_mcp_server_config_defaults(self):
        """Test MCPServerConfig default values"""
        config = MCPServerConfig()
        
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.max_concurrent_requests == 10
        assert config.request_timeout == 300
        assert config.enable_cors is True
        assert "*" in config.cors_origins
        assert config.enable_natural_language_tool is True
        assert config.enable_execute_command_tool is True
        assert config.enable_system_info_tool is True
    
    def test_server_config_platform_detection(self):
        """Test ServerConfig platform auto-detection"""
        config = ServerConfig()
        
        # Platform should be auto-detected
        assert config.platform in [Platform.WINDOWS, Platform.LINUX, Platform.MACOS]
        assert config.version == "0.1.0"
        assert config.debug_mode is False
    
    def test_server_config_debug_mode_log_level(self):
        """Test that debug mode adjusts log level"""
        config = ServerConfig()
        config.debug_mode = True
        config.__post_init__()
        
        assert config.logging.log_level == LogLevel.DEBUG


if __name__ == "__main__":
    pytest.main([__file__])