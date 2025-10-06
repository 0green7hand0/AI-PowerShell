"""
基础接口和数据模型定义

本模块定义了 AI PowerShell 智能助手的核心接口和数据模型，
用于实现模块间的解耦和标准化通信。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# 枚举类型定义
# ============================================================================

class RiskLevel(Enum):
    """风险等级枚举"""
    SAFE = "safe"           # 安全命令
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中等风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 严重风险


class ExecutionStatus(Enum):
    """执行状态枚举"""
    SUCCESS = "success"     # 执行成功
    FAILED = "failed"       # 执行失败
    TIMEOUT = "timeout"     # 执行超时
    CANCELLED = "cancelled" # 用户取消


# ============================================================================
# 数据模型定义
# ============================================================================

@dataclass
class Suggestion:
    """AI 翻译建议数据模型"""
    original_input: str                      # 原始用户输入
    generated_command: str                   # 生成的 PowerShell 命令
    confidence_score: float                  # 置信度分数 (0.0-1.0)
    explanation: str                         # 命令解释说明
    alternatives: List[str] = field(default_factory=list)  # 备选命令列表
    timestamp: datetime = field(default_factory=datetime.now)  # 生成时间
    
    def __post_init__(self):
        """验证数据有效性"""
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0.0 and 1.0")
        if not self.original_input or not self.generated_command:
            raise ValueError("original_input and generated_command cannot be empty")


@dataclass
class ValidationResult:
    """安全验证结果数据模型"""
    is_valid: bool                           # 是否通过验证
    risk_level: RiskLevel                    # 风险等级
    blocked_reasons: List[str] = field(default_factory=list)  # 阻止原因列表
    requires_confirmation: bool = False      # 是否需要用户确认
    requires_elevation: bool = False         # 是否需要权限提升
    warnings: List[str] = field(default_factory=list)  # 警告信息列表
    timestamp: datetime = field(default_factory=datetime.now)  # 验证时间
    
    @property
    def is_dangerous(self) -> bool:
        """判断是否为危险命令"""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


@dataclass
class ExecutionResult:
    """命令执行结果数据模型"""
    success: bool                            # 执行是否成功
    command: str                             # 执行的命令
    output: str = ""                         # 标准输出
    error: str = ""                          # 错误输出
    return_code: int = 0                     # 返回码
    execution_time: float = 0.0              # 执行时间（秒）
    status: ExecutionStatus = ExecutionStatus.SUCCESS  # 执行状态
    timestamp: datetime = field(default_factory=datetime.now)  # 执行时间
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    @property
    def has_output(self) -> bool:
        """判断是否有输出"""
        return bool(self.output.strip())
    
    @property
    def has_error(self) -> bool:
        """判断是否有错误"""
        return bool(self.error.strip())


@dataclass
class Context:
    """上下文数据模型"""
    session_id: str                          # 会话 ID
    user_id: Optional[str] = None            # 用户 ID
    working_directory: str = "."             # 工作目录
    environment_vars: Dict[str, str] = field(default_factory=dict)  # 环境变量
    command_history: List[str] = field(default_factory=list)  # 命令历史
    timestamp: datetime = field(default_factory=datetime.now)  # 上下文创建时间
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据
    
    def add_command(self, command: str):
        """添加命令到历史记录"""
        self.command_history.append(command)
    
    def get_recent_commands(self, limit: int = 5) -> List[str]:
        """获取最近的命令"""
        return self.command_history[-limit:]


# ============================================================================
# 接口定义
# ============================================================================

class AIEngineInterface(ABC):
    """AI 引擎接口
    
    定义 AI 引擎的核心功能，负责将自然语言转换为 PowerShell 命令。
    """
    
    @abstractmethod
    def translate_natural_language(self, text: str, context: Context) -> Suggestion:
        """将自然语言翻译为 PowerShell 命令
        
        Args:
            text: 用户输入的自然语言文本
            context: 当前上下文信息
            
        Returns:
            Suggestion: 包含生成命令和相关信息的建议对象
            
        Raises:
            ValueError: 当输入文本为空或无效时
            RuntimeError: 当 AI 引擎不可用时
        """
        pass
    
    @abstractmethod
    def validate_command(self, command: str) -> bool:
        """验证生成的命令是否有效
        
        Args:
            command: 待验证的 PowerShell 命令
            
        Returns:
            bool: 命令是否有效
        """
        pass
    
    @abstractmethod
    def get_command_explanation(self, command: str) -> str:
        """获取命令的详细解释
        
        Args:
            command: PowerShell 命令
            
        Returns:
            str: 命令的详细解释
        """
        pass


class SecurityEngineInterface(ABC):
    """安全引擎接口
    
    定义安全引擎的核心功能，负责命令的安全验证和风险评估。
    """
    
    @abstractmethod
    def validate_command(self, command: str, context: Context) -> ValidationResult:
        """验证命令的安全性
        
        Args:
            command: 待验证的 PowerShell 命令
            context: 当前上下文信息
            
        Returns:
            ValidationResult: 包含验证结果和风险评估的对象
        """
        pass
    
    @abstractmethod
    def check_permissions(self, command: str) -> bool:
        """检查命令所需的权限
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 当前用户是否有足够权限执行该命令
        """
        pass
    
    @abstractmethod
    def is_dangerous_command(self, command: str) -> bool:
        """判断命令是否危险
        
        Args:
            command: PowerShell 命令
            
        Returns:
            bool: 命令是否被认为是危险的
        """
        pass


class ExecutorInterface(ABC):
    """执行器接口
    
    定义执行器的核心功能，负责 PowerShell 命令的实际执行。
    """
    
    @abstractmethod
    def execute(self, command: str, timeout: int = 30) -> ExecutionResult:
        """执行 PowerShell 命令
        
        Args:
            command: 要执行的 PowerShell 命令
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 包含执行结果的对象
            
        Raises:
            TimeoutError: 当命令执行超时时
            RuntimeError: 当执行环境不可用时
        """
        pass
    
    @abstractmethod
    def execute_async(self, command: str, timeout: int = 30) -> Any:
        """异步执行 PowerShell 命令
        
        Args:
            command: 要执行的 PowerShell 命令
            timeout: 超时时间（秒）
            
        Returns:
            异步执行的 Future 或 Task 对象
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查 PowerShell 是否可用
        
        Returns:
            bool: PowerShell 是否在系统中可用
        """
        pass


class StorageInterface(ABC):
    """存储接口
    
    定义存储引擎的核心功能，负责数据的持久化。
    """
    
    @abstractmethod
    def save_history(self, entry: Dict[str, Any]) -> bool:
        """保存历史记录
        
        Args:
            entry: 历史记录条目
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """加载历史记录
        
        Args:
            limit: 加载的最大记录数
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        pass
    
    @abstractmethod
    def load_config(self) -> Dict[str, Any]:
        """加载配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        pass


class LoggerInterface(ABC):
    """日志接口
    
    定义日志引擎的核心功能，负责系统日志记录。
    """
    
    @abstractmethod
    def log_request(self, user_input: str, correlation_id: str):
        """记录用户请求
        
        Args:
            user_input: 用户输入
            correlation_id: 关联 ID
        """
        pass
    
    @abstractmethod
    def log_translation(self, input_text: str, command: str, confidence: float):
        """记录 AI 翻译
        
        Args:
            input_text: 输入文本
            command: 生成的命令
            confidence: 置信度
        """
        pass
    
    @abstractmethod
    def log_execution(self, command: str, result: ExecutionResult):
        """记录命令执行
        
        Args:
            command: 执行的命令
            result: 执行结果
        """
        pass
    
    @abstractmethod
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """记录错误
        
        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        pass
