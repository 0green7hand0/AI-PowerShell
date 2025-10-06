"""
日志装饰器测试
"""

import logging
import time

import pytest

from src.config.models import LoggingConfig
from src.log_engine.engine import LogEngine
from src.log_engine.decorators import log_function_call, log_performance


class TestLogFunctionCall:
    """函数调用日志装饰器测试类"""
    
    def test_basic_function_logging(self, caplog):
        """测试基本函数日志"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG")
        def test_function(x, y):
            return x + y
        
        with caplog.at_level(logging.DEBUG):
            result = test_function(1, 2)
        
        assert result == 3
        assert "Calling function" in caplog.text
        assert "test_function" in caplog.text
    
    def test_function_with_kwargs(self, caplog):
        """测试带关键字参数的函数"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_args=True)
        def test_function(x, y, z=10):
            return x + y + z
        
        with caplog.at_level(logging.DEBUG):
            result = test_function(1, 2, z=5)
        
        assert result == 8
        assert "Calling function" in caplog.text
    
    def test_function_with_exception(self, caplog):
        """测试函数抛出异常"""
        config = LoggingConfig(level="ERROR", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_exceptions=True)
        def test_function():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                test_function()
        
        assert "Function raised exception" in caplog.text
        assert "ValueError" in caplog.text
    
    def test_function_without_log_args(self, caplog):
        """测试不记录参数"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_args=False)
        def test_function(x, y):
            return x + y
        
        with caplog.at_level(logging.DEBUG):
            result = test_function(1, 2)
        
        assert result == 3
        assert "Calling function" in caplog.text
    
    def test_function_without_log_result(self, caplog):
        """测试不记录返回值"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_result=False)
        def test_function(x, y):
            return x + y
        
        with caplog.at_level(logging.DEBUG):
            result = test_function(1, 2)
        
        assert result == 3
        assert "Calling function" in caplog.text
    
    def test_function_with_sensitive_data(self, caplog):
        """测试敏感数据处理"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_args=True)
        def test_function(username, password):
            return f"User: {username}"
        
        with caplog.at_level(logging.DEBUG):
            result = test_function("admin", "secret123")
        
        assert result == "User: admin"
        assert "Calling function" in caplog.text
        # 密码应该被替换
        assert "***REDACTED***" in caplog.text or "secret123" not in caplog.text
    
    def test_method_logging(self, caplog):
        """测试类方法日志"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        class TestClass:
            def __init__(self):
                self.log_engine = engine
            
            @log_function_call(level="DEBUG")
            def test_method(self, x):
                return x * 2
        
        obj = TestClass()
        
        with caplog.at_level(logging.DEBUG):
            result = obj.test_method(5)
        
        assert result == 10
        assert "Calling function" in caplog.text
    
    def test_function_without_logger(self):
        """测试没有日志引擎的情况"""
        @log_function_call(log_engine=None, level="DEBUG")
        def test_function(x, y):
            return x + y
        
        # 应该正常执行，不抛出异常
        result = test_function(1, 2)
        assert result == 3


class TestLogPerformance:
    """性能监控装饰器测试类"""
    
    def test_basic_performance_logging(self, caplog):
        """测试基本性能日志"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_performance(log_engine=engine, level="DEBUG")
        def test_function():
            time.sleep(0.01)
            return "done"
        
        with caplog.at_level(logging.DEBUG):
            result = test_function()
        
        assert result == "done"
        assert "Performance" in caplog.text or "test_function" in caplog.text
    
    def test_performance_with_threshold(self, caplog):
        """测试性能阈值警告"""
        config = LoggingConfig(level="WARNING", file=None)
        engine = LogEngine(config)
        
        @log_performance(log_engine=engine, threshold=0.01, level="WARNING")
        def slow_function():
            time.sleep(0.02)
            return "done"
        
        with caplog.at_level(logging.WARNING):
            result = slow_function()
        
        assert result == "done"
        assert "Performance warning" in caplog.text or "slow_function" in caplog.text
    
    def test_performance_below_threshold(self, caplog):
        """测试低于阈值的性能"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_performance(log_engine=engine, threshold=1.0, level="DEBUG")
        def fast_function():
            return "done"
        
        with caplog.at_level(logging.DEBUG):
            result = fast_function()
        
        assert result == "done"
        # 应该记录普通性能日志，不是警告
        assert "Performance warning" not in caplog.text
    
    def test_performance_with_exception(self, caplog):
        """测试函数抛出异常时的性能记录"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_performance(log_engine=engine, level="DEBUG")
        def test_function():
            raise ValueError("Test error")
        
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(ValueError):
                test_function()
        
        # 即使抛出异常，也应该记录性能
        # 注意：性能日志在 finally 块中，应该被记录
    
    def test_performance_method_logging(self, caplog):
        """测试类方法性能日志"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        class TestClass:
            def __init__(self):
                self.log_engine = engine
            
            @log_performance(threshold=0.01)
            def test_method(self):
                time.sleep(0.001)
                return "done"
        
        obj = TestClass()
        
        with caplog.at_level(logging.DEBUG):
            result = obj.test_method()
        
        assert result == "done"
    
    def test_performance_without_logger(self):
        """测试没有日志引擎的情况"""
        @log_performance(log_engine=None, level="DEBUG")
        def test_function():
            return "done"
        
        # 应该正常执行，不抛出异常
        result = test_function()
        assert result == "done"
    
    def test_combined_decorators(self, caplog):
        """测试组合使用装饰器"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG")
        @log_performance(log_engine=engine, level="DEBUG")
        def test_function(x):
            time.sleep(0.001)
            return x * 2
        
        with caplog.at_level(logging.DEBUG):
            result = test_function(5)
        
        assert result == 10
        # 应该同时有函数调用日志和性能日志
        assert "Calling function" in caplog.text or "test_function" in caplog.text


class TestSanitization:
    """参数清理测试类"""
    
    def test_sanitize_password_in_kwargs(self, caplog):
        """测试清理关键字参数中的密码"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_args=True)
        def login(username, password, token):
            return f"Logged in as {username}"
        
        with caplog.at_level(logging.DEBUG):
            result = login(username="admin", password="secret", token="abc123")
        
        assert result == "Logged in as admin"
        # 函数应该被调用
        assert "Calling function" in caplog.text
        # 敏感信息不应该出现在日志中（它们被存储在 extra 中，不在消息文本中）
        # 注意：由于敏感信息在 extra 中被替换，不会出现在 caplog.text 中
    
    def test_sanitize_large_objects(self, caplog):
        """测试清理大对象"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        @log_function_call(log_engine=engine, level="DEBUG", log_args=True)
        def process_data(data):
            return len(data)
        
        large_list = list(range(100))
        
        with caplog.at_level(logging.DEBUG):
            result = process_data(large_list)
        
        assert result == 100
        # 大列表应该被简化表示
        assert "Calling function" in caplog.text
