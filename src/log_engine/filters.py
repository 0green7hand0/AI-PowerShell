"""
日志过滤器

提供敏感信息过滤和日志级别过滤功能
"""

import logging
import re
from typing import List, Pattern, Set


class SensitiveDataFilter(logging.Filter):
    """
    敏感信息过滤器
    
    自动检测并替换日志中的敏感信息，如密码、令牌等
    """
    
    # 默认的敏感信息模式
    DEFAULT_PATTERNS = [
        # 密码相关
        (r'password["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'password'),
        (r'passwd["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'passwd'),
        (r'pwd["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'pwd'),
        
        # 令牌相关
        (r'token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'token'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'api_key'),
        (r'access[_-]?token["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'access_token'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'secret'),
        
        # 认证相关
        (r'authorization["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'authorization'),
        (r'auth["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', 'auth'),
        
        # 信用卡号（简单模式）
        (r'(\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4})', 'credit_card'),
        
        # 邮箱地址（可选）
        # (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email'),
        
        # IP 地址（可选）
        # (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 'ip_address'),
    ]
    
    def __init__(
        self,
        name: str = "",
        custom_patterns: List[tuple] = None,
        redaction_text: str = "***REDACTED***"
    ):
        """
        初始化敏感信息过滤器
        
        Args:
            name: 过滤器名称
            custom_patterns: 自定义敏感信息模式列表，格式为 [(pattern, name), ...]
            redaction_text: 替换文本
        """
        super().__init__(name)
        self.redaction_text = redaction_text
        
        # 编译正则表达式模式
        self.patterns: List[tuple[Pattern, str]] = []
        
        # 添加默认模式
        for pattern, pattern_name in self.DEFAULT_PATTERNS:
            self.patterns.append((re.compile(pattern, re.IGNORECASE), pattern_name))
        
        # 添加自定义模式
        if custom_patterns:
            for pattern, pattern_name in custom_patterns:
                self.patterns.append((re.compile(pattern, re.IGNORECASE), pattern_name))
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            True 表示保留该日志记录
        """
        # 过滤消息内容
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._redact_sensitive_data(record.msg)
        
        # 过滤参数
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = self._redact_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                # 处理元组中的字典
                new_args = []
                for arg in record.args:
                    if isinstance(arg, dict):
                        new_args.append(self._redact_dict(arg))
                    elif isinstance(arg, str):
                        new_args.append(self._redact_sensitive_data(arg))
                    else:
                        new_args.append(arg)
                record.args = tuple(new_args)
        
        return True
    
    def _redact_sensitive_data(self, text: str) -> str:
        """
        替换文本中的敏感信息
        
        Args:
            text: 原始文本
            
        Returns:
            替换后的文本
        """
        for pattern, pattern_name in self.patterns:
            # 替换匹配的内容
            text = pattern.sub(
                lambda m: m.group(0).replace(m.group(1), self.redaction_text),
                text
            )
        
        return text
    
    def _redact_dict(self, data: dict) -> dict:
        """
        替换字典中的敏感信息
        
        Args:
            data: 原始字典
            
        Returns:
            替换后的字典
        """
        redacted = {}
        
        # 敏感键名列表
        sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
            'apikey', 'access_token', 'auth', 'authorization', 'credential',
            'private_key', 'secret_key'
        }
        
        for key, value in data.items():
            # 检查键名是否敏感
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                redacted[key] = self.redaction_text
            # 如果值是字符串，检查内容
            elif isinstance(value, str):
                redacted[key] = self._redact_sensitive_data(value)
            # 如果值是字典，递归处理
            elif isinstance(value, dict):
                redacted[key] = self._redact_dict(value)
            else:
                redacted[key] = value
        
        return redacted


class LogLevelFilter(logging.Filter):
    """
    日志级别过滤器
    
    只允许特定级别的日志通过
    """
    
    def __init__(
        self,
        name: str = "",
        min_level: int = logging.DEBUG,
        max_level: int = logging.CRITICAL,
        allowed_levels: Set[int] = None
    ):
        """
        初始化日志级别过滤器
        
        Args:
            name: 过滤器名称
            min_level: 最小日志级别
            max_level: 最大日志级别
            allowed_levels: 允许的日志级别集合（如果指定，则忽略 min_level 和 max_level）
        """
        super().__init__(name)
        self.min_level = min_level
        self.max_level = max_level
        self.allowed_levels = allowed_levels
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            True 表示保留该日志记录
        """
        # 如果指定了允许的级别集合
        if self.allowed_levels is not None:
            return record.levelno in self.allowed_levels
        
        # 否则使用范围过滤
        return self.min_level <= record.levelno <= self.max_level


class ModuleFilter(logging.Filter):
    """
    模块过滤器
    
    只允许特定模块的日志通过
    """
    
    def __init__(
        self,
        name: str = "",
        allowed_modules: Set[str] = None,
        blocked_modules: Set[str] = None
    ):
        """
        初始化模块过滤器
        
        Args:
            name: 过滤器名称
            allowed_modules: 允许的模块名称集合
            blocked_modules: 阻止的模块名称集合
        """
        super().__init__(name)
        self.allowed_modules = allowed_modules or set()
        self.blocked_modules = blocked_modules or set()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            True 表示保留该日志记录
        """
        module_name = record.name
        
        # 如果在阻止列表中，拒绝
        if self.blocked_modules:
            for blocked in self.blocked_modules:
                if module_name.startswith(blocked):
                    return False
        
        # 如果指定了允许列表，检查是否在列表中
        if self.allowed_modules:
            for allowed in self.allowed_modules:
                if module_name.startswith(allowed):
                    return True
            return False
        
        # 默认允许
        return True


class CorrelationFilter(logging.Filter):
    """
    关联 ID 过滤器
    
    只允许特定关联 ID 的日志通过
    """
    
    def __init__(
        self,
        name: str = "",
        correlation_ids: Set[str] = None,
        require_correlation_id: bool = False
    ):
        """
        初始化关联 ID 过滤器
        
        Args:
            name: 过滤器名称
            correlation_ids: 允许的关联 ID 集合
            require_correlation_id: 是否要求必须有关联 ID
        """
        super().__init__(name)
        self.correlation_ids = correlation_ids or set()
        self.require_correlation_id = require_correlation_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录
        
        Args:
            record: 日志记录
            
        Returns:
            True 表示保留该日志记录
        """
        # 获取关联 ID
        correlation_id = getattr(record, 'correlation_id', None)
        
        # 如果要求必须有关联 ID
        if self.require_correlation_id and not correlation_id:
            return False
        
        # 如果指定了允许的关联 ID 集合
        if self.correlation_ids and correlation_id:
            return correlation_id in self.correlation_ids
        
        # 默认允许
        return True
