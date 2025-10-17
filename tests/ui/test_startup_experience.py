"""
启动体验测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ui.startup_experience import StartupExperience, StartupPerformanceOptimizer
from src.ui.startup_wizard import CheckStatus, SystemCheck
from src.ui.ui_manager import UIManager


class TestStartupExperience:
    """启动体验测试"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器"""
        return UIManager()
    
    @pytest.fixture
    def startup(self, ui_manager):
        """创建启动体验管理器"""
        return StartupExperience(ui_manager)
    
    def test_initialization(self, startup):
        """测试初始化"""
        assert startup.ui_manager is not None
        assert startup.wizard is not None
    
    @patch('src.ui.startup_experience.StartupWizard')
    def test_run_startup_sequence_first_run(self, mock_wizard_class, startup):
        """测试启动序列 - 首次运行"""
        # 模拟首次运行
        mock_wizard = Mock()
        mock_wizard.is_first_run.return_value = True
        mock_wizard.run_welcome_wizard.return_value = True
        startup.wizard = mock_wizard
        
        result = startup.run_startup_sequence()
        
        assert result
        mock_wizard.run_welcome_wizard.assert_called_once()
    
    @patch('src.ui.startup_experience.StartupWizard')
    def test_run_startup_sequence_not_first_run(self, mock_wizard_class, startup):
        """测试启动序列 - 非首次运行"""
        # 模拟非首次运行
        mock_wizard = Mock()
        mock_wizard.is_first_run.return_value = False
        mock_wizard.quick_system_check.return_value = (True, [])
        startup.wizard = mock_wizard
        
        result = startup.run_startup_sequence()
        
        assert result
        mock_wizard.quick_system_check.assert_called_once()
    
    @patch('src.ui.startup_experience.StartupWizard')
    def test_run_startup_sequence_with_warnings(self, mock_wizard_class, startup):
        """测试启动序列 - 有警告"""
        # 模拟有警告的检查结果
        mock_wizard = Mock()
        mock_wizard.is_first_run.return_value = False
        
        warning_check = SystemCheck(
            name="Test",
            status=CheckStatus.WARNING,
            message="Warning message"
        )
        mock_wizard.quick_system_check.return_value = (False, [warning_check])
        startup.wizard = mock_wizard
        
        result = startup.run_startup_sequence()
        
        # 即使有警告也应该继续
        assert not result  # 返回 False 因为检查失败
        mock_wizard.quick_system_check.assert_called_once()
    
    def test_display_startup_banner(self, startup):
        """测试显示启动横幅"""
        # 不应该抛出异常
        startup._display_startup_banner()
    
    def test_display_startup_warnings_with_warnings(self, startup):
        """测试显示启动警告 - 有警告"""
        checks = [
            SystemCheck(
                name="Test Warning",
                status=CheckStatus.WARNING,
                message="This is a warning"
            ),
            SystemCheck(
                name="Test Failed",
                status=CheckStatus.FAILED,
                message="This failed"
            )
        ]
        
        # 不应该抛出异常
        startup._display_startup_warnings(checks)
    
    def test_display_startup_warnings_no_warnings(self, startup):
        """测试显示启动警告 - 无警告"""
        checks = [
            SystemCheck(
                name="Test",
                status=CheckStatus.PASSED,
                message="OK"
            )
        ]
        
        # 不应该抛出异常
        startup._display_startup_warnings(checks)
    
    def test_display_feature_overview(self, startup):
        """测试显示功能概览"""
        # 不应该抛出异常
        startup._display_feature_overview()
    
    def test_display_quick_tips(self, startup):
        """测试显示快速提示"""
        # 不应该抛出异常
        startup._display_quick_tips()
    
    def test_display_ready_status(self, startup):
        """测试显示就绪状态"""
        # 不应该抛出异常
        startup._display_ready_status(0.5)
    
    def test_display_session_summary(self, startup):
        """测试显示会话摘要"""
        stats = {
            'commands_executed': 10,
            'successful_commands': 8,
            'failed_commands': 2,
            'session_duration': 120.5,
        }
        
        # 不应该抛出异常
        startup.display_session_summary(stats)
    
    def test_display_session_summary_empty_stats(self, startup):
        """测试显示会话摘要 - 空统计"""
        stats = {}
        
        # 不应该抛出异常
        startup.display_session_summary(stats)


class TestStartupPerformanceOptimizer:
    """启动性能优化器测试"""
    
    def test_lazy_import_heavy_modules(self):
        """测试延迟导入重型模块"""
        # 不应该抛出异常
        StartupPerformanceOptimizer.lazy_import_heavy_modules()
    
    def test_preload_common_data(self):
        """测试预加载常用数据"""
        # 不应该抛出异常
        StartupPerformanceOptimizer.preload_common_data()
    
    def test_cache_system_info(self):
        """测试缓存系统信息"""
        info = StartupPerformanceOptimizer.cache_system_info()
        
        # 应该返回字典
        assert isinstance(info, dict)
        
        # 应该包含必要的键
        assert 'platform' in info
        assert 'python_version' in info
        assert 'machine' in info
        
        # 值不应该为空
        assert info['platform']
        assert info['python_version']
