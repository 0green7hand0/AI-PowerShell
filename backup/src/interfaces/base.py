"""AI PowerShell 助手的基础接口和抽象类

本模块定义了所有组件必须实现的核心接口，
以及整个系统中使用的通用数据模型和枚举类型。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import uuid


# 类型安全的枚举定义
class Platform(Enum):
    """支持的操作系统平台"""
    WINDOWS = "windows"  # Windows 系统
    LINUX = "linux"      # Linux 系统
    MACOS = "macos"      # macOS 系统


class SecurityAction(Enum):
    """安全验证动作"""
    ALLOW = "allow"                          # 允许执行
    BLOCK = "block"                          # 阻止执行
    REQUIRE_CONFIRMATION = "require_confirmation"  # 需要用户确认


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"          # 低风险
    MEDIUM = "medium"    # 中等风险
    HIGH = "high"        # 高风险
    CRITICAL = "critical"  # 严重风险


class UserRole(Enum):
    """用户角色"""
    USER = "user"      # 普通用户
    ADMIN = "admin"    # 管理员
    SYSTEM = "system"  # 系统用户


class Permission(Enum):
    """权限类型"""
    READ = "read"        # 读取权限
    WRITE = "write"      # 写入权限
    EXECUTE = "execute"  # 执行权限
    ADMIN = "admin"      # 管理员权限


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"        # 调试信息
    INFO = "info"          # 一般信息
    WARNING = "warning"    # 警告信息
    ERROR = "error"        # 错误信息
    CRITICAL = "critical"  # 严重错误


class LogFormat(Enum):
    """日志格式"""
    JSON = "json"              # JSON 格式
    TEXT = "text"              # 纯文本格式
    STRUCTURED = "structured"  # 结构化格式


class LogOutput(Enum):
    """日志输出目标"""
    FILE = "file"                    # 文件输出
    CONSOLE = "console"              # 控制台输出
    SYSLOG = "syslog"                # 系统日志
    ELASTICSEARCH = "elasticsearch"  # Elasticsearch


class AuditEventType(Enum):
    """审计事件类型"""
    USER_INPUT = "user_input"                    # 用户输入
    AI_PROCESSING = "ai_processing"              # AI 处理
    SECURITY_VALIDATION = "security_validation"  # 安全验证
    COMMAND_EXECUTION = "command_execution"      # 命令执行
    ERROR_OCCURRED = "error_occurred"            # 错误发生


class OutputFormat(Enum):
    """输出格式"""
    JSON = "json"    # JSON 格式
    TABLE = "table"  # 表格格式
    RAW = "raw"      # 原始格式


# 核心数据模型
@dataclass
class CommandSuggestion:
    """AI 生成的命令建议
    
    包含原始输入、生成的命令、置信度等信息
    """
    original_input: str      # 原始用户输入
    generated_command: str   # 生成的 PowerShell 命令
    confidence_score: float  # 置信度分数 (0.0-1.0)
    explanation: str         # 命令解释说明
    alternatives: List[str]  # 替代命令选项
    correlation_id: str = None  # 关联 ID，用于追踪
    
    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())


@dataclass
class ExecutionResult:
    """PowerShell 命令执行结果
    
    包含执行状态、输出、错误信息等
    """
    success: bool           # 执行是否成功
    return_code: int        # 返回码
    stdout: str            # 标准输出
    stderr: str            # 标准错误输出
    execution_time: float  # 执行时间（秒）
    platform: Platform     # 执行平台
    sandbox_used: bool     # 是否使用沙箱
    correlation_id: str = None  # 关联 ID
    
    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())


@dataclass
class SecurityRule:
    """安全验证规则
    
    定义命令的安全检查规则
    """
    pattern: str              # 匹配模式（正则表达式）
    action: SecurityAction    # 执行动作
    risk_level: RiskLevel     # 风险等级
    description: str          # 规则描述


@dataclass
class CommandContext:
    """命令执行上下文
    
    包含执行环境的相关信息
    """
    current_directory: str              # 当前工作目录
    environment_variables: Dict[str, str]  # 环境变量
    user_role: UserRole                 # 用户角色
    recent_commands: List[str]          # 最近执行的命令
    active_modules: List[str]           # 活跃的 PowerShell 模块
    platform: Platform                 # 操作系统平台
    session_id: str = None             # 会话 ID
    
    def __post_init__(self):
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())


@dataclass
class ValidationResult:
    """安全验证结果
    
    包含验证状态和相关信息
    """
    is_valid: bool                        # 是否通过验证
    blocked_reasons: List[str]            # 被阻止的原因
    required_permissions: List[Permission]  # 需要的权限
    suggested_alternatives: List[str]     # 建议的替代方案
    risk_assessment: RiskLevel            # 风险评估


@dataclass
class ErrorSuggestion:
    """错误修复建议
    
    为命令错误提供修复建议
    """
    error_type: str      # 错误类型
    description: str     # 错误描述
    suggested_fix: str   # 建议的修复方案
    confidence: float    # 建议的置信度


@dataclass
class PerformanceMetrics:
    """性能指标
    
    记录操作的性能数据
    """
    memory_usage_mb: float      # 内存使用量（MB）
    cpu_usage_percent: float    # CPU 使用率（%）
    processing_time_ms: float   # 处理时间（毫秒）
    timestamp: datetime = None  # 时间戳
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class AuditEntry:
    """审计日志条目
    
    记录系统操作的完整审计信息
    """
    correlation_id: str                           # 关联 ID
    session_id: str                              # 会话 ID
    timestamp: datetime                          # 时间戳
    event_type: AuditEventType                   # 事件类型
    user_input: Optional[str]                    # 用户输入
    generated_command: Optional[str]             # 生成的命令
    security_validation: Optional[ValidationResult]  # 安全验证结果
    execution_result: Optional[ExecutionResult]  # 执行结果
    performance_metrics: Optional[PerformanceMetrics]  # 性能指标
    error_details: Optional[Dict[str, Any]]      # 错误详情


# 抽象基类接口定义
class AIEngineInterface(ABC):
    """AI 处理引擎的抽象接口
    
    定义了 AI 引擎必须实现的核心功能：
    - 自然语言到 PowerShell 命令的转换
    - 命令错误检测和修复建议
    - 上下文学习和更新
    """
    
    @abstractmethod
    def translate_natural_language(self, input_text: str, context: CommandContext) -> CommandSuggestion:
        """将自然语言转换为 PowerShell 命令
        
        Args:
            input_text: 用户的自然语言输入
            context: 当前执行上下文
            
        Returns:
            CommandSuggestion: 包含生成命令和相关信息的建议
        """
        pass
    
    @abstractmethod
    def detect_command_errors(self, command: str) -> List[ErrorSuggestion]:
        """检测 PowerShell 命令中的错误
        
        Args:
            command: 要检测的 PowerShell 命令
            
        Returns:
            List[ErrorSuggestion]: 错误检测结果和修复建议列表
        """
        pass
    
    @abstractmethod
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """为命令错误提供修复建议
        
        Args:
            command: 出错的命令
            error: 错误信息
            
        Returns:
            List[str]: 修复建议列表
        """
        pass
    
    @abstractmethod
    def update_context(self, command: str, result: ExecutionResult) -> None:
        """使用执行结果更新 AI 上下文
        
        Args:
            command: 执行的命令
            result: 执行结果
        """
        pass


class SecurityEngineInterface(ABC):
    """安全验证引擎的抽象接口
    
    实现三层安全保护机制：
    1. 命令白名单验证
    2. 权限检查
    3. 沙箱执行环境
    """
    
    @abstractmethod
    def validate_command(self, command: str) -> ValidationResult:
        """根据安全规则验证命令
        
        Args:
            command: 要验证的 PowerShell 命令
            
        Returns:
            ValidationResult: 验证结果，包含是否通过和详细信息
        """
        pass
    
    @abstractmethod
    def check_permissions(self, command: str) -> List[Permission]:
        """检查命令所需的权限
        
        Args:
            command: 要检查的命令
            
        Returns:
            List[Permission]: 执行该命令所需的权限列表
        """
        pass
    
    @abstractmethod
    def execute_in_sandbox(self, command: str, timeout: int) -> ExecutionResult:
        """在沙箱环境中执行命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 沙箱执行结果
        """
        pass
    
    @abstractmethod
    def update_whitelist(self, rules: List[SecurityRule]) -> None:
        """更新安全白名单规则
        
        Args:
            rules: 新的安全规则列表
        """
        pass


class ExecutorInterface(ABC):
    """PowerShell 执行器的抽象接口
    
    负责跨平台的 PowerShell 命令执行：
    - 命令执行和结果处理
    - 平台适配和兼容性
    - 输出格式化
    """
    
    @abstractmethod
    def execute_command(self, command: str, context: CommandContext) -> ExecutionResult:
        """执行 PowerShell 命令
        
        Args:
            command: 要执行的 PowerShell 命令
            context: 执行上下文
            
        Returns:
            ExecutionResult: 命令执行结果
        """
        pass
    
    @abstractmethod
    def get_powershell_info(self) -> Dict[str, Any]:
        """获取 PowerShell 环境信息
        
        Returns:
            Dict[str, Any]: PowerShell 版本、模块等环境信息
        """
        pass
    
    @abstractmethod
    def format_output(self, raw_output: str, format_type: OutputFormat) -> str:
        """格式化命令输出
        
        Args:
            raw_output: 原始输出
            format_type: 目标格式类型
            
        Returns:
            str: 格式化后的输出
        """
        pass
    
    @abstractmethod
    def adapt_for_platform(self, command: str, target_platform: Platform) -> str:
        """为特定平台适配命令
        
        Args:
            command: 原始命令
            target_platform: 目标平台
            
        Returns:
            str: 适配后的命令
        """
        pass


class LoggingEngineInterface(ABC):
    """日志引擎的抽象接口
    
    提供全面的审计跟踪和日志记录功能：
    - 用户操作日志
    - 系统处理过程日志
    - 错误和异常日志
    - 审计轨迹查询
    """
    
    @abstractmethod
    def log_user_input(self, session_id: str, input_text: str, timestamp: datetime) -> str:
        """记录用户输入并返回关联 ID
        
        Args:
            session_id: 会话 ID
            input_text: 用户输入内容
            timestamp: 时间戳
            
        Returns:
            str: 生成的关联 ID，用于追踪整个处理流程
        """
        pass
    
    @abstractmethod
    def log_ai_processing(self, correlation_id: str, input_text: str, 
                         generated_command: str, confidence: float) -> None:
        """记录 AI 处理详情
        
        Args:
            correlation_id: 关联 ID
            input_text: 原始输入
            generated_command: 生成的命令
            confidence: 置信度
        """
        pass
    
    @abstractmethod
    def log_security_validation(self, correlation_id: str, command: str, 
                               validation_result: ValidationResult) -> None:
        """记录安全验证结果
        
        Args:
            correlation_id: 关联 ID
            command: 被验证的命令
            validation_result: 验证结果
        """
        pass
    
    @abstractmethod
    def log_command_execution(self, correlation_id: str, command: str, 
                             execution_result: ExecutionResult) -> None:
        """记录命令执行详情
        
        Args:
            correlation_id: 关联 ID
            command: 执行的命令
            execution_result: 执行结果
        """
        pass
    
    @abstractmethod
    def log_error(self, correlation_id: str, error: Exception, 
                  context: Dict[str, Any]) -> None:
        """记录错误信息
        
        Args:
            correlation_id: 关联 ID
            error: 异常对象
            context: 错误上下文信息
        """
        pass
    
    @abstractmethod
    def get_audit_trail(self, session_id: str, start_time: datetime, 
                       end_time: datetime) -> List[AuditEntry]:
        """检索审计轨迹条目
        
        Args:
            session_id: 会话 ID
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[AuditEntry]: 审计条目列表
        """
        pass


class StorageInterface(ABC):
    """存储操作的抽象接口
    
    负责数据的持久化存储：
    - 命令历史记录
    - 用户偏好设置
    - 系统配置管理
    """
    
    @abstractmethod
    def save_command_history(self, session_id: str, command: str, 
                           result: ExecutionResult) -> None:
        """保存命令到历史记录
        
        Args:
            session_id: 会话 ID
            command: 执行的命令
            result: 执行结果
        """
        pass
    
    @abstractmethod
    def get_command_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """检索命令历史记录
        
        Args:
            session_id: 会话 ID
            limit: 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 历史命令列表
        """
        pass
    
    @abstractmethod
    def save_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> None:
        """保存用户偏好设置
        
        Args:
            session_id: 会话 ID
            preferences: 用户偏好设置字典
        """
        pass
    
    @abstractmethod
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """检索用户偏好设置
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Dict[str, Any]: 用户偏好设置
        """
        pass
    
    @abstractmethod
    def save_configuration(self, config: Dict[str, Any]) -> None:
        """保存系统配置
        
        Args:
            config: 系统配置字典
        """
        pass
    
    @abstractmethod
    def load_configuration(self) -> Dict[str, Any]:
        """加载系统配置
        
        Returns:
            Dict[str, Any]: 系统配置字典
        """
        pass


class ContextManagerInterface(ABC):
    """上下文管理器的抽象接口
    
    管理用户会话和执行上下文：
    - 会话生命周期管理
    - 执行上下文维护
    - 历史状态跟踪
    """
    
    @abstractmethod
    def get_current_context(self, session_id: str) -> CommandContext:
        """获取当前执行上下文
        
        Args:
            session_id: 会话 ID
            
        Returns:
            CommandContext: 当前的命令执行上下文
        """
        pass
    
    @abstractmethod
    def update_context(self, session_id: str, command: str, result: ExecutionResult) -> None:
        """更新执行上下文
        
        Args:
            session_id: 会话 ID
            command: 执行的命令
            result: 执行结果
        """
        pass
    
    @abstractmethod
    def create_session(self, user_role: UserRole, platform: Platform) -> str:
        """创建新的用户会话
        
        Args:
            user_role: 用户角色
            platform: 操作系统平台
            
        Returns:
            str: 新创建的会话 ID
        """
        pass
    
    @abstractmethod
    def end_session(self, session_id: str) -> None:
        """结束用户会话
        
        Args:
            session_id: 要结束的会话 ID
        """
        pass


class MCPServerInterface(ABC):
    """MCP 服务器实现的抽象接口
    
    基于 Model Context Protocol 的服务器接口：
    - MCP 工具注册和管理
    - 服务器生命周期控制
    - 请求处理和响应
    """
    
    @abstractmethod
    def register_tools(self) -> None:
        """注册 MCP 工具
        
        将所有可用的工具注册到 MCP 服务器中
        """
        pass
    
    @abstractmethod
    def start_server(self) -> None:
        """启动 MCP 服务器
        
        启动服务器并开始监听客户端请求
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """关闭 MCP 服务器
        
        优雅地关闭服务器并清理资源
        """
        pass
    
    @abstractmethod
    def handle_natural_language_request(self, input_text: str, session_id: str) -> Dict[str, Any]:
        """处理自然语言到 PowerShell 的转换请求
        
        Args:
            input_text: 用户的自然语言输入
            session_id: 会话 ID
            
        Returns:
            Dict[str, Any]: 包含生成命令和相关信息的响应
        """
        pass
    
    @abstractmethod
    def handle_execute_command(self, command: str, session_id: str) -> Dict[str, Any]:
        """处理 PowerShell 命令执行请求
        
        Args:
            command: 要执行的 PowerShell 命令
            session_id: 会话 ID
            
        Returns:
            Dict[str, Any]: 包含执行结果的响应
        """
        pass
    
    @abstractmethod
    def handle_get_system_info(self, session_id: str) -> Dict[str, Any]:
        """处理系统信息查询请求
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Dict[str, Any]: 包含系统信息的响应
        """
        pass