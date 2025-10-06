"""
配置数据模型

使用 Pydantic 进行数据验证和配置管理
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class AIConfig(BaseModel):
    """AI 引擎配置"""
    
    provider: str = Field(
        default="local",
        description="AI 提供商: local, ollama, openai"
    )
    model_name: str = Field(
        default="llama",
        description="AI 模型名称"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="生成温度，控制随机性"
    )
    max_tokens: int = Field(
        default=256,
        ge=1,
        le=4096,
        description="最大生成 token 数"
    )
    cache_enabled: bool = Field(
        default=True,
        description="是否启用翻译缓存"
    )
    cache_size: int = Field(
        default=100,
        ge=0,
        description="缓存大小"
    )
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """验证 AI 提供商"""
        allowed = ['local', 'ollama', 'openai', 'azure']
        if v not in allowed:
            raise ValueError(f"provider 必须是以下之一: {', '.join(allowed)}")
        return v


class SecurityConfig(BaseModel):
    """安全引擎配置"""
    
    sandbox_enabled: bool = Field(
        default=False,
        description="是否启用沙箱执行"
    )
    require_confirmation: bool = Field(
        default=True,
        description="是否需要用户确认"
    )
    whitelist_mode: str = Field(
        default="strict",
        description="白名单模式: strict, moderate, permissive"
    )
    dangerous_patterns: List[str] = Field(
        default_factory=lambda: [
            r"Remove-Item.*-Recurse.*-Force",
            r"Format-Volume",
            r"Remove-Item.*C:\\",
            r"Stop-Computer",
            r"Restart-Computer",
        ],
        description="危险命令模式列表"
    )
    safe_prefixes: List[str] = Field(
        default_factory=lambda: [
            "Get-", "Show-", "Test-", "Find-",
            "Select-", "Where-", "echo", "Write-"
        ],
        description="安全命令前缀列表"
    )
    custom_rules: List[str] = Field(
        default_factory=list,
        description="自定义安全规则"
    )
    
    @field_validator('whitelist_mode')
    @classmethod
    def validate_whitelist_mode(cls, v: str) -> str:
        """验证白名单模式"""
        allowed = ['strict', 'moderate', 'permissive']
        if v not in allowed:
            raise ValueError(f"whitelist_mode 必须是以下之一: {', '.join(allowed)}")
        return v


class ExecutionConfig(BaseModel):
    """执行引擎配置"""
    
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="命令执行超时时间（秒）"
    )
    encoding: str = Field(
        default="utf-8",
        description="输出编码格式"
    )
    platform: str = Field(
        default="auto",
        description="平台类型: auto, windows, linux, macos"
    )
    powershell_path: Optional[str] = Field(
        default=None,
        description="PowerShell 可执行文件路径（可选）"
    )
    auto_detect_powershell: bool = Field(
        default=True,
        description="是否自动检测 PowerShell"
    )
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """验证平台类型"""
        allowed = ['auto', 'windows', 'linux', 'macos']
        if v not in allowed:
            raise ValueError(f"platform 必须是以下之一: {', '.join(allowed)}")
        return v
    
    @field_validator('encoding')
    @classmethod
    def validate_encoding(cls, v: str) -> str:
        """验证编码格式"""
        try:
            # 尝试使用该编码
            "test".encode(v)
        except LookupError:
            raise ValueError(f"不支持的编码格式: {v}")
        return v


class LoggingConfig(BaseModel):
    """日志配置"""
    
    level: str = Field(
        default="INFO",
        description="日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    file: Optional[str] = Field(
        default="logs/assistant.log",
        description="日志文件路径"
    )
    max_size: str = Field(
        default="10MB",
        description="日志文件最大大小"
    )
    backup_count: int = Field(
        default=5,
        ge=0,
        description="日志文件备份数量"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    console_output: bool = Field(
        default=True,
        description="是否输出到控制台"
    )
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """验证日志级别"""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"level 必须是以下之一: {', '.join(allowed)}")
        return v_upper


class StorageConfig(BaseModel):
    """存储配置"""
    
    base_path: str = Field(
        default="~/.ai-powershell",
        description="存储基础路径"
    )
    history_file: str = Field(
        default="history.json",
        description="历史记录文件名"
    )
    config_file: str = Field(
        default="config.yaml",
        description="配置文件名"
    )
    cache_dir: str = Field(
        default="cache",
        description="缓存目录名"
    )
    max_history_size: int = Field(
        default=1000,
        ge=0,
        description="最大历史记录数量"
    )


class ContextConfig(BaseModel):
    """上下文管理配置"""
    
    max_context_depth: int = Field(
        default=5,
        ge=1,
        le=50,
        description="最大上下文深度"
    )
    session_timeout: int = Field(
        default=3600,
        ge=60,
        description="会话超时时间（秒）"
    )
    enable_learning: bool = Field(
        default=True,
        description="是否启用学习功能"
    )


class AppConfig(BaseModel):
    """应用总配置"""
    
    ai: AIConfig = Field(
        default_factory=AIConfig,
        description="AI 引擎配置"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="安全引擎配置"
    )
    execution: ExecutionConfig = Field(
        default_factory=ExecutionConfig,
        description="执行引擎配置"
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="日志配置"
    )
    storage: StorageConfig = Field(
        default_factory=StorageConfig,
        description="存储配置"
    )
    context: ContextConfig = Field(
        default_factory=ContextConfig,
        description="上下文管理配置"
    )
    
    model_config = {
        'validate_assignment': True,
        'extra': 'forbid',  # 禁止额外字段
    }
