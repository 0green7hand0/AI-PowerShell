"""
日志引擎主类

提供结构化日志记录和关联追踪功能
"""

import logging
import logging.handlers
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar

from ..config.models import LoggingConfig


# 使用 ContextVar 存储 correlation ID，支持异步环境
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class LogEngine:
    """
    日志引擎主类
    
    功能：
    - 结构化日志记录
    - 关联追踪（correlation ID）
    - 多级别日志支持
    - 文件和控制台输出
    - 日志轮转
    """
    
    def __init__(self, config: LoggingConfig):
        """
        初始化日志引擎
        
        Args:
            config: 日志配置
        """
        self.config = config
        self.logger = self._setup_logger()
        self._current_correlation_id: Optional[str] = None
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        Returns:
            配置好的 Logger 实例
        """
        # 创建 logger
        logger = logging.getLogger('ai_powershell')
        logger.setLevel(getattr(logging, self.config.level))
        
        # 清除已有的 handlers
        logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            self.config.format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        if self.config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config.level))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self.config.file:
            log_file = Path(self.config.file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 解析最大文件大小
            max_bytes = self._parse_size(self.config.max_size)
            
            # 使用 RotatingFileHandler 实现日志轮转
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, self.config.level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _parse_size(self, size_str: str) -> int:
        """
        解析大小字符串（如 "10MB"）为字节数
        
        Args:
            size_str: 大小字符串
            
        Returns:
            字节数
        """
        size_str = size_str.upper().strip()
        
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
        }
        
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                try:
                    number = float(size_str[:-len(unit)])
                    return int(number * multiplier)
                except ValueError:
                    pass
        
        # 默认返回 10MB
        return 10 * 1024 * 1024
    
    def start_correlation(self, correlation_id: Optional[str] = None) -> str:
        """
        开始一个新的关联追踪
        
        Args:
            correlation_id: 可选的关联 ID，如果不提供则自动生成
            
        Returns:
            关联 ID
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        self._current_correlation_id = correlation_id
        correlation_id_var.set(correlation_id)
        
        return correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """
        获取当前的关联 ID
        
        Returns:
            当前关联 ID，如果没有则返回 None
        """
        # 优先从 ContextVar 获取（支持异步）
        ctx_id = correlation_id_var.get()
        if ctx_id:
            return ctx_id
        
        return self._current_correlation_id
    
    def end_correlation(self):
        """结束当前的关联追踪"""
        self._current_correlation_id = None
        correlation_id_var.set(None)
    
    def _add_correlation_id(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        添加关联 ID 到额外信息中
        
        Args:
            extra: 额外信息字典
            
        Returns:
            包含关联 ID 的额外信息字典
        """
        if extra is None:
            extra = {}
        
        correlation_id = self.get_correlation_id()
        if correlation_id:
            extra['correlation_id'] = correlation_id
        
        return extra
    
    def debug(self, message: str, **kwargs):
        """
        记录 DEBUG 级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        extra = self._add_correlation_id(kwargs)
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """
        记录 INFO 级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        extra = self._add_correlation_id(kwargs)
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """
        记录 WARNING 级别日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        extra = self._add_correlation_id(kwargs)
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """
        记录 ERROR 级别日志
        
        Args:
            message: 日志消息
            exc_info: 是否包含异常信息
            **kwargs: 额外的上下文信息
        """
        extra = self._add_correlation_id(kwargs)
        self.logger.error(message, exc_info=exc_info, extra=extra)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """
        记录 CRITICAL 级别日志
        
        Args:
            message: 日志消息
            exc_info: 是否包含异常信息
            **kwargs: 额外的上下文信息
        """
        extra = self._add_correlation_id(kwargs)
        self.logger.critical(message, exc_info=exc_info, extra=extra)
    
    def log_request(self, user_input: str, **kwargs):
        """
        记录用户请求
        
        Args:
            user_input: 用户输入
            **kwargs: 额外的上下文信息
        """
        kwargs['event'] = 'user_request'
        kwargs['user_input'] = user_input
        kwargs['timestamp'] = datetime.now().isoformat()
        self.info(f"User request: {user_input}", **kwargs)
    
    def log_translation(self, input_text: str, command: str, confidence: float, **kwargs):
        """
        记录 AI 翻译
        
        Args:
            input_text: 输入文本
            command: 生成的命令
            confidence: 置信度
            **kwargs: 额外的上下文信息
        """
        kwargs['event'] = 'ai_translation'
        kwargs['input_text'] = input_text
        kwargs['command'] = command
        kwargs['confidence'] = confidence
        self.info(f"AI translation: {input_text} -> {command} (confidence: {confidence})", **kwargs)
    
    def log_security_check(self, command: str, is_valid: bool, reason: str = "", **kwargs):
        """
        记录安全检查
        
        Args:
            command: 检查的命令
            is_valid: 是否通过验证
            reason: 原因说明
            **kwargs: 额外的上下文信息
        """
        kwargs['event'] = 'security_check'
        kwargs['command'] = command
        kwargs['is_valid'] = is_valid
        kwargs['reason'] = reason
        
        if is_valid:
            self.info(f"Security check passed: {command}", **kwargs)
        else:
            self.warning(f"Security check failed: {command} - {reason}", **kwargs)
    
    def log_execution(self, command: str, success: bool, return_code: int = 0, 
                     execution_time: float = 0.0, **kwargs):
        """
        记录命令执行
        
        Args:
            command: 执行的命令
            success: 是否成功
            return_code: 返回码
            execution_time: 执行时间（秒）
            **kwargs: 额外的上下文信息
        """
        kwargs['event'] = 'command_execution'
        kwargs['command'] = command
        kwargs['success'] = success
        kwargs['return_code'] = return_code
        kwargs['execution_time'] = execution_time
        
        if success:
            self.info(
                f"Command executed successfully: {command} (time: {execution_time:.3f}s)",
                **kwargs
            )
        else:
            self.error(
                f"Command execution failed: {command} (code: {return_code})",
                **kwargs
            )
    
    def log_performance(self, operation: str, duration: float, **kwargs):
        """
        记录性能指标
        
        Args:
            operation: 操作名称
            duration: 持续时间（秒）
            **kwargs: 额外的上下文信息
        """
        kwargs['event'] = 'performance'
        kwargs['operation'] = operation
        kwargs['duration'] = duration
        self.debug(f"Performance: {operation} took {duration:.3f}s", **kwargs)
