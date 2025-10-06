"""
日志装饰器

提供函数调用日志和性能监控装饰器
"""

import functools
import time
from typing import Any, Callable, Optional

from .engine import LogEngine


def log_function_call(
    log_engine: Optional[LogEngine] = None,
    level: str = "DEBUG",
    log_args: bool = True,
    log_result: bool = True,
    log_exceptions: bool = True
) -> Callable:
    """
    函数调用日志装饰器
    
    记录函数的调用、参数、返回值和异常
    
    Args:
        log_engine: 日志引擎实例，如果为 None 则从函数参数中获取
        level: 日志级别（DEBUG, INFO, WARNING, ERROR）
        log_args: 是否记录函数参数
        log_result: 是否记录返回值
        log_exceptions: 是否记录异常
        
    Returns:
        装饰器函数
        
    Example:
        @log_function_call(log_engine=my_logger, level="INFO")
        def my_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 获取日志引擎
            logger = log_engine
            if logger is None:
                # 尝试从第一个参数获取（通常是 self）
                if args and hasattr(args[0], 'log_engine'):
                    logger = args[0].log_engine
            
            # 如果没有日志引擎，直接执行函数
            if logger is None:
                return func(*args, **kwargs)
            
            # 准备日志信息
            func_name = f"{func.__module__}.{func.__qualname__}"
            log_method = getattr(logger, level.lower(), logger.debug)
            
            # 记录函数调用
            call_info = {"function": func_name}
            
            if log_args:
                # 记录参数（避免记录敏感信息）
                safe_args = _sanitize_args(args)
                safe_kwargs = _sanitize_kwargs(kwargs)
                call_info["func_args"] = safe_args
                call_info["func_kwargs"] = safe_kwargs
            
            log_method(f"Calling function: {func_name}", **call_info)
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录返回值
                if log_result:
                    result_info = {
                        "function": func_name,
                        "result_type": type(result).__name__
                    }
                    log_method(f"Function returned: {func_name}", **result_info)
                
                return result
                
            except Exception as e:
                # 记录异常
                if log_exceptions:
                    error_info = {
                        "function": func_name,
                        "exception_type": type(e).__name__,
                        "exception_message": str(e)
                    }
                    logger.error(
                        f"Function raised exception: {func_name}",
                        exc_info=True,
                        **error_info
                    )
                raise
        
        return wrapper
    return decorator


def log_performance(
    log_engine: Optional[LogEngine] = None,
    threshold: float = 0.0,
    level: str = "DEBUG"
) -> Callable:
    """
    性能监控装饰器
    
    记录函数执行时间，如果超过阈值则记录警告
    
    Args:
        log_engine: 日志引擎实例，如果为 None 则从函数参数中获取
        threshold: 时间阈值（秒），超过此值记录警告
        level: 日志级别（DEBUG, INFO, WARNING）
        
    Returns:
        装饰器函数
        
    Example:
        @log_performance(log_engine=my_logger, threshold=1.0)
        def slow_function():
            time.sleep(2)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 获取日志引擎
            logger = log_engine
            if logger is None:
                # 尝试从第一个参数获取（通常是 self）
                if args and hasattr(args[0], 'log_engine'):
                    logger = args[0].log_engine
            
            # 记录开始时间
            start_time = time.time()
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                return result
            finally:
                # 计算执行时间
                duration = time.time() - start_time
                
                # 如果有日志引擎，记录性能
                if logger:
                    func_name = f"{func.__module__}.{func.__qualname__}"
                    
                    # 如果超过阈值，记录警告
                    if threshold > 0 and duration > threshold:
                        logger.warning(
                            f"Performance warning: {func_name} took {duration:.3f}s (threshold: {threshold}s)",
                            operation=func_name,
                            duration=duration,
                            threshold=threshold,
                            event="performance_warning"
                        )
                    else:
                        # 否则记录普通性能日志
                        logger.log_performance(func_name, duration)
        
        return wrapper
    return decorator


def _sanitize_args(args: tuple) -> list:
    """
    清理参数，避免记录敏感信息
    
    Args:
        args: 函数位置参数
        
    Returns:
        清理后的参数列表
    """
    sanitized = []
    for arg in args:
        # 跳过 self 和 cls
        if hasattr(arg, '__class__') and arg.__class__.__name__ in ['type', 'ABCMeta']:
            continue
        
        # 转换为字符串表示
        arg_str = _safe_repr(arg)
        sanitized.append(arg_str)
    
    return sanitized


def _sanitize_kwargs(kwargs: dict) -> dict:
    """
    清理关键字参数，避免记录敏感信息
    
    Args:
        kwargs: 函数关键字参数
        
    Returns:
        清理后的参数字典
    """
    sanitized = {}
    
    # 敏感参数名称列表
    sensitive_keys = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
        'apikey', 'access_token', 'auth', 'authorization', 'credential'
    }
    
    for key, value in kwargs.items():
        # 检查是否是敏感参数
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = _safe_repr(value)
    
    return sanitized


def _safe_repr(obj: Any, max_length: int = 100) -> str:
    """
    安全地获取对象的字符串表示
    
    Args:
        obj: 对象
        max_length: 最大长度
        
    Returns:
        对象的字符串表示
    """
    try:
        # 对于基本类型，直接返回
        if isinstance(obj, (str, int, float, bool, type(None))):
            repr_str = repr(obj)
        # 对于列表和元组，限制长度
        elif isinstance(obj, (list, tuple)):
            if len(obj) > 5:
                repr_str = f"{type(obj).__name__}(length={len(obj)})"
            else:
                repr_str = repr(obj)
        # 对于字典，限制长度
        elif isinstance(obj, dict):
            if len(obj) > 5:
                repr_str = f"dict(keys={len(obj)})"
            else:
                repr_str = repr(obj)
        # 其他对象，使用类型名称
        else:
            repr_str = f"<{type(obj).__name__}>"
        
        # 限制长度
        if len(repr_str) > max_length:
            repr_str = repr_str[:max_length] + "..."
        
        return repr_str
    except Exception:
        return "<repr failed>"
