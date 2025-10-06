"""
接口定义模块

提供 AI PowerShell 智能助手的核心接口和数据模型定义。
"""

from .base import (
    # 枚举类型
    RiskLevel,
    ExecutionStatus,
    
    # 数据模型
    Suggestion,
    ValidationResult,
    ExecutionResult,
    Context,
    
    # 接口定义
    AIEngineInterface,
    SecurityEngineInterface,
    ExecutorInterface,
    StorageInterface,
    LoggerInterface,
)

__all__ = [
    # 枚举类型
    "RiskLevel",
    "ExecutionStatus",
    
    # 数据模型
    "Suggestion",
    "ValidationResult",
    "ExecutionResult",
    "Context",
    
    # 接口定义
    "AIEngineInterface",
    "SecurityEngineInterface",
    "ExecutorInterface",
    "StorageInterface",
    "LoggerInterface",
]
