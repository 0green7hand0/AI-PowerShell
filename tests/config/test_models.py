"""
配置数据模型测试
"""

import pytest
from pydantic import ValidationError

from src.config.models import (
    AIConfig,
    SecurityConfig,
    ExecutionConfig,
    LoggingConfig,
    StorageConfig,
    ContextConfig,
    AppConfig,
)


class TestAIConfig:
    """测试 AI 配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = AIConfig()
        assert config.provider == "local"
        assert config.model_name == "llama"
        assert config.temperature == 0.7
        assert config.max_tokens == 256
        assert config.cache_enabled is True
        assert config.cache_size == 100
    
    def test_valid_provider(self):
        """测试有效的提供商"""
        config = AIConfig(provider="ollama")
        assert config.provider == "ollama"
    
    def test_invalid_provider(self):
        """测试无效的提供商"""
        with pytest.raises(ValidationError):
            AIConfig(provider="invalid")
    
    def test_temperature_range(self):
        """测试温度范围"""
        # 有效范围
        config = AIConfig(temperature=0.0)
        assert config.temperature == 0.0
        
        config = AIConfig(temperature=2.0)
        assert config.temperature == 2.0
        
        # 无效范围
        with pytest.raises(ValidationError):
            AIConfig(temperature=-0.1)
        
        with pytest.raises(ValidationError):
            AIConfig(temperature=2.1)
    
    def test_max_tokens_range(self):
        """测试最大 token 范围"""
        # 有效范围
        config = AIConfig(max_tokens=1)
        assert config.max_tokens == 1
        
        config = AIConfig(max_tokens=4096)
        assert config.max_tokens == 4096
        
        # 无效范围
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=0)
        
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=4097)


class TestSecurityConfig:
    """测试安全配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = SecurityConfig()
        assert config.sandbox_enabled is False
        assert config.require_confirmation is True
        assert config.whitelist_mode == "strict"
        assert len(config.dangerous_patterns) > 0
        assert len(config.safe_prefixes) > 0
        assert len(config.custom_rules) == 0
    
    def test_valid_whitelist_mode(self):
        """测试有效的白名单模式"""
        for mode in ["strict", "moderate", "permissive"]:
            config = SecurityConfig(whitelist_mode=mode)
            assert config.whitelist_mode == mode
    
    def test_invalid_whitelist_mode(self):
        """测试无效的白名单模式"""
        with pytest.raises(ValidationError):
            SecurityConfig(whitelist_mode="invalid")
    
    def test_custom_patterns(self):
        """测试自定义模式"""
        config = SecurityConfig(
            dangerous_patterns=["custom-pattern"],
            safe_prefixes=["Custom-"],
            custom_rules=["rule1", "rule2"]
        )
        assert "custom-pattern" in config.dangerous_patterns
        assert "Custom-" in config.safe_prefixes
        assert len(config.custom_rules) == 2


class TestExecutionConfig:
    """测试执行配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = ExecutionConfig()
        assert config.timeout == 30
        assert config.encoding == "utf-8"
        assert config.platform == "auto"
        assert config.powershell_path is None
        assert config.auto_detect_powershell is True
    
    def test_timeout_range(self):
        """测试超时范围"""
        # 有效范围
        config = ExecutionConfig(timeout=1)
        assert config.timeout == 1
        
        config = ExecutionConfig(timeout=300)
        assert config.timeout == 300
        
        # 无效范围
        with pytest.raises(ValidationError):
            ExecutionConfig(timeout=0)
        
        with pytest.raises(ValidationError):
            ExecutionConfig(timeout=301)
    
    def test_valid_platform(self):
        """测试有效的平台"""
        for platform in ["auto", "windows", "linux", "macos"]:
            config = ExecutionConfig(platform=platform)
            assert config.platform == platform
    
    def test_invalid_platform(self):
        """测试无效的平台"""
        with pytest.raises(ValidationError):
            ExecutionConfig(platform="invalid")
    
    def test_valid_encoding(self):
        """测试有效的编码"""
        for encoding in ["utf-8", "gbk", "ascii", "latin-1"]:
            config = ExecutionConfig(encoding=encoding)
            assert config.encoding == encoding
    
    def test_invalid_encoding(self):
        """测试无效的编码"""
        with pytest.raises(ValidationError):
            ExecutionConfig(encoding="invalid-encoding")


class TestLoggingConfig:
    """测试日志配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file == "logs/assistant.log"
        assert config.max_size == "10MB"
        assert config.backup_count == 5
        assert config.console_output is True
    
    def test_valid_log_level(self):
        """测试有效的日志级别"""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = LoggingConfig(level=level)
            assert config.level == level
        
        # 测试小写转大写
        config = LoggingConfig(level="debug")
        assert config.level == "DEBUG"
    
    def test_invalid_log_level(self):
        """测试无效的日志级别"""
        with pytest.raises(ValidationError):
            LoggingConfig(level="INVALID")
    
    def test_backup_count_range(self):
        """测试备份数量范围"""
        config = LoggingConfig(backup_count=0)
        assert config.backup_count == 0
        
        config = LoggingConfig(backup_count=10)
        assert config.backup_count == 10
        
        with pytest.raises(ValidationError):
            LoggingConfig(backup_count=-1)


class TestStorageConfig:
    """测试存储配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = StorageConfig()
        assert config.base_path == "~/.ai-powershell"
        assert config.history_file == "history.json"
        assert config.config_file == "config.yaml"
        assert config.cache_dir == "cache"
        assert config.max_history_size == 1000
    
    def test_custom_values(self):
        """测试自定义值"""
        config = StorageConfig(
            base_path="/custom/path",
            history_file="custom_history.json",
            max_history_size=500
        )
        assert config.base_path == "/custom/path"
        assert config.history_file == "custom_history.json"
        assert config.max_history_size == 500


class TestContextConfig:
    """测试上下文配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = ContextConfig()
        assert config.max_context_depth == 5
        assert config.session_timeout == 3600
        assert config.enable_learning is True
    
    def test_context_depth_range(self):
        """测试上下文深度范围"""
        config = ContextConfig(max_context_depth=1)
        assert config.max_context_depth == 1
        
        config = ContextConfig(max_context_depth=50)
        assert config.max_context_depth == 50
        
        with pytest.raises(ValidationError):
            ContextConfig(max_context_depth=0)
        
        with pytest.raises(ValidationError):
            ContextConfig(max_context_depth=51)
    
    def test_session_timeout_range(self):
        """测试会话超时范围"""
        config = ContextConfig(session_timeout=60)
        assert config.session_timeout == 60
        
        with pytest.raises(ValidationError):
            ContextConfig(session_timeout=59)


class TestAppConfig:
    """测试应用配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = AppConfig()
        assert isinstance(config.ai, AIConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.execution, ExecutionConfig)
        assert isinstance(config.logging, LoggingConfig)
        assert isinstance(config.storage, StorageConfig)
        assert isinstance(config.context, ContextConfig)
    
    def test_nested_config(self):
        """测试嵌套配置"""
        config = AppConfig(
            ai=AIConfig(provider="ollama", temperature=0.5),
            security=SecurityConfig(sandbox_enabled=True),
            execution=ExecutionConfig(timeout=60)
        )
        assert config.ai.provider == "ollama"
        assert config.ai.temperature == 0.5
        assert config.security.sandbox_enabled is True
        assert config.execution.timeout == 60
    
    def test_dict_initialization(self):
        """测试字典初始化"""
        config_dict = {
            "ai": {
                "provider": "openai",
                "model_name": "gpt-4"
            },
            "security": {
                "whitelist_mode": "moderate"
            }
        }
        config = AppConfig(**config_dict)
        assert config.ai.provider == "openai"
        assert config.ai.model_name == "gpt-4"
        assert config.security.whitelist_mode == "moderate"
    
    def test_forbid_extra_fields(self):
        """测试禁止额外字段"""
        with pytest.raises(ValidationError):
            AppConfig(extra_field="not allowed")
    
    def test_validate_assignment(self):
        """测试赋值验证"""
        config = AppConfig()
        
        # 有效赋值
        config.ai = AIConfig(provider="ollama")
        assert config.ai.provider == "ollama"
        
        # 无效赋值
        with pytest.raises(ValidationError):
            config.ai = "invalid"
