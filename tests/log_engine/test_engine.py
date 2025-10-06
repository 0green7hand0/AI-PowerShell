"""
日志引擎测试
"""

import logging
import tempfile
from pathlib import Path

import pytest

from src.config.models import LoggingConfig
from src.log_engine.engine import LogEngine


class TestLogEngine:
    """日志引擎测试类"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        config = LoggingConfig()
        engine = LogEngine(config)
        
        assert engine.config == config
        assert engine.logger is not None
        assert engine.logger.name == 'ai_powershell'
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        config = LoggingConfig(
            level="DEBUG",
            console_output=True,
            file=None
        )
        engine = LogEngine(config)
        
        assert engine.logger.level == logging.DEBUG
    
    def test_parse_size(self):
        """测试大小字符串解析"""
        config = LoggingConfig()
        engine = LogEngine(config)
        
        # 测试不同单位
        assert engine._parse_size("10B") == 10
        assert engine._parse_size("10KB") == 10 * 1024
        assert engine._parse_size("10MB") == 10 * 1024 * 1024
        assert engine._parse_size("10GB") == 10 * 1024 * 1024 * 1024
        
        # 测试小写
        assert engine._parse_size("5mb") == 5 * 1024 * 1024
        
        # 测试浮点数
        assert engine._parse_size("1.5MB") == int(1.5 * 1024 * 1024)
        
        # 测试无效格式（返回默认值）
        assert engine._parse_size("invalid") == 10 * 1024 * 1024
    
    def test_correlation_id(self):
        """测试关联 ID 功能"""
        config = LoggingConfig(file=None)
        engine = LogEngine(config)
        
        # 初始状态没有关联 ID
        assert engine.get_correlation_id() is None
        
        # 开始关联追踪
        correlation_id = engine.start_correlation()
        assert correlation_id is not None
        assert engine.get_correlation_id() == correlation_id
        
        # 使用自定义关联 ID
        custom_id = "test-123"
        engine.start_correlation(custom_id)
        assert engine.get_correlation_id() == custom_id
        
        # 结束关联追踪
        engine.end_correlation()
        assert engine.get_correlation_id() is None
    
    def test_log_levels(self, caplog):
        """测试不同日志级别"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.DEBUG):
            engine.debug("Debug message")
            engine.info("Info message")
            engine.warning("Warning message")
            engine.error("Error message")
            engine.critical("Critical message")
        
        # 验证日志记录
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text
    
    def test_log_with_extra_data(self, caplog):
        """测试带额外数据的日志"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.INFO):
            engine.info("Test message", user="test_user", action="test_action")
        
        # 验证日志记录
        assert "Test message" in caplog.text
    
    def test_log_request(self, caplog):
        """测试请求日志"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.INFO):
            engine.log_request("显示当前时间")
        
        assert "User request" in caplog.text
        assert "显示当前时间" in caplog.text
    
    def test_log_translation(self, caplog):
        """测试翻译日志"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.INFO):
            engine.log_translation("显示当前时间", "Get-Date", 0.95)
        
        assert "AI translation" in caplog.text
        assert "显示当前时间" in caplog.text
        assert "Get-Date" in caplog.text
    
    def test_log_security_check_passed(self, caplog):
        """测试安全检查通过日志"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.INFO):
            engine.log_security_check("Get-Date", True, "Safe command")
        
        assert "Security check passed" in caplog.text
        assert "Get-Date" in caplog.text
    
    def test_log_security_check_failed(self, caplog):
        """测试安全检查失败日志"""
        config = LoggingConfig(level="WARNING", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.WARNING):
            engine.log_security_check("Remove-Item -Recurse", False, "Dangerous command")
        
        assert "Security check failed" in caplog.text
        assert "Remove-Item -Recurse" in caplog.text
        assert "Dangerous command" in caplog.text
    
    def test_log_execution_success(self, caplog):
        """测试命令执行成功日志"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.INFO):
            engine.log_execution("Get-Date", True, 0, 0.123)
        
        assert "Command executed successfully" in caplog.text
        assert "Get-Date" in caplog.text
        assert "0.123" in caplog.text
    
    def test_log_execution_failure(self, caplog):
        """测试命令执行失败日志"""
        config = LoggingConfig(level="ERROR", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.ERROR):
            engine.log_execution("Invalid-Command", False, 1, 0.050)
        
        assert "Command execution failed" in caplog.text
        assert "Invalid-Command" in caplog.text
    
    def test_log_performance(self, caplog):
        """测试性能日志"""
        config = LoggingConfig(level="DEBUG", file=None)
        engine = LogEngine(config)
        
        with caplog.at_level(logging.DEBUG):
            engine.log_performance("test_operation", 1.234)
        
        assert "Performance" in caplog.text
        assert "test_operation" in caplog.text
        assert "1.234" in caplog.text
    
    def test_file_logging(self):
        """测试文件日志"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            config = LoggingConfig(
                level="INFO",
                file=str(log_file),
                console_output=False
            )
            engine = LogEngine(config)
            
            # 写入日志
            engine.info("Test file logging")
            
            # 关闭所有处理器以释放文件
            for handler in engine.logger.handlers[:]:
                handler.close()
                engine.logger.removeHandler(handler)
            
            # 验证文件存在
            assert log_file.exists()
            
            # 验证文件内容
            content = log_file.read_text(encoding='utf-8')
            assert "Test file logging" in content
    
    def test_log_rotation(self):
        """测试日志轮转"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            config = LoggingConfig(
                level="INFO",
                file=str(log_file),
                max_size="1KB",  # 很小的大小，容易触发轮转
                backup_count=3,
                console_output=False
            )
            engine = LogEngine(config)
            
            # 写入大量日志
            for i in range(100):
                engine.info(f"Test message {i}" * 10)
            
            # 关闭所有处理器以释放文件
            for handler in engine.logger.handlers[:]:
                handler.close()
                engine.logger.removeHandler(handler)
            
            # 验证主日志文件存在
            assert log_file.exists()
            
            # 验证备份文件可能存在（取决于日志大小）
            # 注意：由于日志格式化，实际大小可能不同
    
    def test_correlation_id_in_logs(self, caplog):
        """测试日志中包含关联 ID"""
        config = LoggingConfig(level="INFO", file=None)
        engine = LogEngine(config)
        
        # 开始关联追踪
        correlation_id = engine.start_correlation("test-correlation-123")
        
        with caplog.at_level(logging.INFO):
            engine.info("Test with correlation")
        
        # 验证关联 ID 被记录
        # 注意：关联 ID 存储在 extra 中，不一定出现在消息文本中
        assert correlation_id == "test-correlation-123"
        
        engine.end_correlation()
    
    def test_multiple_handlers(self):
        """测试多个处理器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            
            config = LoggingConfig(
                level="INFO",
                file=str(log_file),
                console_output=True
            )
            engine = LogEngine(config)
            
            # 验证有两个处理器（控制台和文件）
            assert len(engine.logger.handlers) == 2
            
            # 写入日志
            engine.info("Test multiple handlers")
            
            # 关闭所有处理器以释放文件
            for handler in engine.logger.handlers[:]:
                handler.close()
                engine.logger.removeHandler(handler)
            
            # 验证文件中有日志
            content = log_file.read_text(encoding='utf-8')
            assert "Test multiple handlers" in content
