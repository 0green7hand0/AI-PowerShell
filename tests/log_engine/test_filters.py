"""
日志过滤器测试
"""

import logging

import pytest

from src.log_engine.filters import (
    SensitiveDataFilter,
    LogLevelFilter,
    ModuleFilter,
    CorrelationFilter
)


class TestSensitiveDataFilter:
    """敏感信息过滤器测试类"""
    
    def test_filter_password(self):
        """测试过滤密码"""
        filter_obj = SensitiveDataFilter()
        
        # 创建日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='User login with password="secret123"',
            args=(),
            exc_info=None
        )
        
        # 应用过滤器
        result = filter_obj.filter(record)
        
        assert result is True
        assert "***REDACTED***" in record.msg
        assert "secret123" not in record.msg
    
    def test_filter_token(self):
        """测试过滤令牌"""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='API request with token="abc123xyz"',
            args=(),
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert "***REDACTED***" in record.msg
        assert "abc123xyz" not in record.msg
    
    def test_filter_api_key(self):
        """测试过滤 API 密钥"""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='Config: api_key="sk-1234567890"',
            args=(),
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert "***REDACTED***" in record.msg
        assert "sk-1234567890" not in record.msg
    
    def test_filter_credit_card(self):
        """测试过滤信用卡号"""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Payment with card 1234-5678-9012-3456",
            args=(),
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert "***REDACTED***" in record.msg
    
    def test_filter_dict_args(self):
        """测试过滤字典参数"""
        filter_obj = SensitiveDataFilter()
        
        # 注意：LogRecord 会自动解包单元素元组，所以直接传字典
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User data: %(username)s",
            args={"username": "admin", "password": "secret"},
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        # 密码应该被替换
        assert isinstance(record.args, dict)
        assert record.args["password"] == "***REDACTED***"
        assert record.args["username"] == "admin"
    
    def test_custom_patterns(self):
        """测试自定义模式"""
        custom_patterns = [
            (r'ssn["\']?\s*[:=]\s*["\']?(\d{3}-\d{2}-\d{4})', 'ssn'),
        ]
        filter_obj = SensitiveDataFilter(custom_patterns=custom_patterns)
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='User SSN: ssn="123-45-6789"',
            args=(),
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert "***REDACTED***" in record.msg
        assert "123-45-6789" not in record.msg
    
    def test_custom_redaction_text(self):
        """测试自定义替换文本"""
        filter_obj = SensitiveDataFilter(redaction_text="[HIDDEN]")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='password="secret"',
            args=(),
            exc_info=None
        )
        
        result = filter_obj.filter(record)
        
        assert result is True
        assert "[HIDDEN]" in record.msg
        assert "secret" not in record.msg
    
    def test_no_sensitive_data(self):
        """测试没有敏感数据的情况"""
        filter_obj = SensitiveDataFilter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal log message without sensitive data",
            args=(),
            exc_info=None
        )
        
        original_msg = record.msg
        result = filter_obj.filter(record)
        
        assert result is True
        assert record.msg == original_msg


class TestLogLevelFilter:
    """日志级别过滤器测试类"""
    
    def test_filter_by_range(self):
        """测试按范围过滤"""
        filter_obj = LogLevelFilter(
            min_level=logging.INFO,
            max_level=logging.ERROR
        )
        
        # DEBUG 应该被过滤掉
        debug_record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0,
            msg="Debug", args=(), exc_info=None
        )
        assert filter_obj.filter(debug_record) is False
        
        # INFO 应该通过
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Info", args=(), exc_info=None
        )
        assert filter_obj.filter(info_record) is True
        
        # ERROR 应该通过
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Error", args=(), exc_info=None
        )
        assert filter_obj.filter(error_record) is True
        
        # CRITICAL 应该被过滤掉
        critical_record = logging.LogRecord(
            name="test", level=logging.CRITICAL, pathname="", lineno=0,
            msg="Critical", args=(), exc_info=None
        )
        assert filter_obj.filter(critical_record) is False
    
    def test_filter_by_allowed_levels(self):
        """测试按允许级别过滤"""
        filter_obj = LogLevelFilter(
            allowed_levels={logging.INFO, logging.ERROR}
        )
        
        # DEBUG 应该被过滤掉
        debug_record = logging.LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0,
            msg="Debug", args=(), exc_info=None
        )
        assert filter_obj.filter(debug_record) is False
        
        # INFO 应该通过
        info_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Info", args=(), exc_info=None
        )
        assert filter_obj.filter(info_record) is True
        
        # WARNING 应该被过滤掉
        warning_record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="", lineno=0,
            msg="Warning", args=(), exc_info=None
        )
        assert filter_obj.filter(warning_record) is False
        
        # ERROR 应该通过
        error_record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=0,
            msg="Error", args=(), exc_info=None
        )
        assert filter_obj.filter(error_record) is True


class TestModuleFilter:
    """模块过滤器测试类"""
    
    def test_filter_by_allowed_modules(self):
        """测试按允许模块过滤"""
        filter_obj = ModuleFilter(
            allowed_modules={"src.ai_engine", "src.security"}
        )
        
        # 允许的模块应该通过
        allowed_record = logging.LogRecord(
            name="src.ai_engine.engine", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(allowed_record) is True
        
        # 不允许的模块应该被过滤
        blocked_record = logging.LogRecord(
            name="src.execution.executor", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(blocked_record) is False
    
    def test_filter_by_blocked_modules(self):
        """测试按阻止模块过滤"""
        filter_obj = ModuleFilter(
            blocked_modules={"src.test", "src.debug"}
        )
        
        # 阻止的模块应该被过滤
        blocked_record = logging.LogRecord(
            name="src.test.module", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(blocked_record) is False
        
        # 其他模块应该通过
        allowed_record = logging.LogRecord(
            name="src.ai_engine.engine", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(allowed_record) is True
    
    def test_no_filters(self):
        """测试没有过滤规则的情况"""
        filter_obj = ModuleFilter()
        
        # 所有模块都应该通过
        record = logging.LogRecord(
            name="any.module", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(record) is True


class TestCorrelationFilter:
    """关联 ID 过滤器测试类"""
    
    def test_filter_by_correlation_ids(self):
        """测试按关联 ID 过滤"""
        filter_obj = CorrelationFilter(
            correlation_ids={"test-123", "test-456"}
        )
        
        # 匹配的关联 ID 应该通过
        allowed_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        allowed_record.correlation_id = "test-123"
        assert filter_obj.filter(allowed_record) is True
        
        # 不匹配的关联 ID 应该被过滤
        blocked_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        blocked_record.correlation_id = "test-789"
        assert filter_obj.filter(blocked_record) is False
    
    def test_require_correlation_id(self):
        """测试要求必须有关联 ID"""
        filter_obj = CorrelationFilter(require_correlation_id=True)
        
        # 有关联 ID 的应该通过
        with_id_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        with_id_record.correlation_id = "test-123"
        assert filter_obj.filter(with_id_record) is True
        
        # 没有关联 ID 的应该被过滤
        without_id_record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(without_id_record) is False
    
    def test_no_filters(self):
        """测试没有过滤规则的情况"""
        filter_obj = CorrelationFilter()
        
        # 所有记录都应该通过
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="",
            lineno=0, msg="Test", args=(), exc_info=None
        )
        assert filter_obj.filter(record) is True
        
        # 即使有关联 ID 也应该通过
        record.correlation_id = "test-123"
        assert filter_obj.filter(record) is True
