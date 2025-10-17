"""
启动向导和系统检查测试
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ui.startup_wizard import StartupWizard, SystemCheck, CheckStatus
from src.ui.ui_manager import UIManager


class TestStartupWizard:
    """启动向导测试"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器"""
        return UIManager()
    
    @pytest.fixture
    def wizard(self, ui_manager):
        """创建启动向导"""
        return StartupWizard(ui_manager)
    
    def test_initialization(self, wizard):
        """测试初始化"""
        assert wizard.ui_manager is not None
        assert wizard.checks == []
    
    def test_is_first_run_marker_exists(self, wizard, tmp_path, monkeypatch):
        """测试首次运行检查 - 标记文件存在"""
        # 创建标记文件
        marker = tmp_path / ".ai_powershell_initialized"
        marker.touch()
        
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        assert not wizard.is_first_run()
    
    def test_is_first_run_marker_not_exists(self, wizard, tmp_path, monkeypatch):
        """测试首次运行检查 - 标记文件不存在"""
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        assert wizard.is_first_run()
    
    def test_mark_initialized(self, wizard, tmp_path, monkeypatch):
        """测试标记已初始化"""
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        wizard.mark_initialized()
        
        marker = tmp_path / ".ai_powershell_initialized"
        assert marker.exists()
    
    def test_check_python_version_passed(self, wizard):
        """测试 Python 版本检查 - 通过"""
        check = wizard._check_python_version()
        
        assert check.name == "Python 版本"
        # 当前运行的 Python 版本应该满足要求
        assert check.status == CheckStatus.PASSED
        assert "Python" in check.message
    
    def test_check_powershell_available(self, wizard):
        """测试 PowerShell 可用性检查"""
        check = wizard._check_powershell()
        
        assert check.name == "PowerShell"
        # 结果取决于系统环境，只验证返回了检查结果
        assert check.status in [CheckStatus.PASSED, CheckStatus.WARNING, CheckStatus.FAILED]
    
    def test_check_config_files_all_exist(self, wizard, tmp_path, monkeypatch):
        """测试配置文件检查 - 所有文件存在"""
        # 创建配置目录和文件
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "default.yaml").touch()
        (config_dir / "templates.yaml").touch()
        (config_dir / "ui.yaml").touch()
        
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_config_files()
        
        assert check.name == "配置文件"
        assert check.status == CheckStatus.PASSED
    
    def test_check_config_files_missing(self, wizard, tmp_path, monkeypatch):
        """测试配置文件检查 - 文件缺失"""
        # 修改工作目录（不创建配置文件）
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_config_files()
        
        assert check.name == "配置文件"
        assert check.status in [CheckStatus.WARNING, CheckStatus.FAILED]
        assert check.fix_available
    
    def test_check_log_directory_exists(self, wizard, tmp_path, monkeypatch):
        """测试日志目录检查 - 目录存在"""
        # 创建日志目录
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_log_directory()
        
        assert check.name == "日志目录"
        assert check.status == CheckStatus.PASSED
    
    def test_check_log_directory_not_exists(self, wizard, tmp_path, monkeypatch):
        """测试日志目录检查 - 目录不存在"""
        # 修改工作目录（不创建日志目录）
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_log_directory()
        
        assert check.name == "日志目录"
        assert check.status == CheckStatus.WARNING
        assert check.fix_available
    
    def test_check_template_directory_with_templates(self, wizard, tmp_path, monkeypatch):
        """测试模板目录检查 - 有模板文件"""
        # 创建模板目录和文件
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "test.yaml").touch()
        
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_template_directory()
        
        assert check.name == "模板目录"
        assert check.status == CheckStatus.PASSED
    
    def test_check_storage_directory_exists(self, wizard, tmp_path, monkeypatch):
        """测试存储目录检查 - 目录存在"""
        # 创建存储目录
        storage_dir = tmp_path / "data"
        storage_dir.mkdir()
        
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        check = wizard._check_storage_directory()
        
        assert check.name == "存储目录"
        assert check.status == CheckStatus.PASSED
    
    def test_check_dependencies_all_installed(self, wizard):
        """测试依赖包检查 - 所有包已安装"""
        check = wizard._check_dependencies()
        
        assert check.name == "依赖包"
        # 测试环境应该已安装所有依赖
        assert check.status == CheckStatus.PASSED
    
    def test_run_system_checks(self, wizard):
        """测试运行系统检查"""
        checks = wizard.run_system_checks()
        
        # 应该返回多个检查结果
        assert len(checks) > 0
        
        # 每个检查都应该有必要的属性
        for check in checks:
            assert check.name
            assert check.status in [CheckStatus.PASSED, CheckStatus.WARNING, CheckStatus.FAILED, CheckStatus.SKIPPED]
            assert check.message
    
    def test_quick_system_check(self, wizard):
        """测试快速系统检查"""
        success, checks = wizard.quick_system_check()
        
        # 应该返回布尔值和检查列表
        assert isinstance(success, bool)
        assert isinstance(checks, list)
        assert len(checks) > 0
    
    def test_has_fixable_issues_true(self, wizard):
        """测试是否有可修复问题 - 有"""
        wizard.checks = [
            SystemCheck(
                name="Test",
                status=CheckStatus.WARNING,
                message="Test",
                fix_available=True
            )
        ]
        
        assert wizard._has_fixable_issues()
    
    def test_has_fixable_issues_false(self, wizard):
        """测试是否有可修复问题 - 无"""
        wizard.checks = [
            SystemCheck(
                name="Test",
                status=CheckStatus.PASSED,
                message="Test"
            )
        ]
        
        assert not wizard._has_fixable_issues()
    
    def test_fix_issues_create_directories(self, wizard, tmp_path, monkeypatch):
        """测试修复问题 - 创建目录"""
        # 修改工作目录
        monkeypatch.chdir(tmp_path)
        
        wizard.checks = [
            SystemCheck(
                name="日志目录",
                status=CheckStatus.WARNING,
                message="不存在",
                fix_available=True,
                fix_command="create_log_dir"
            )
        ]
        
        wizard._fix_issues()
        
        # 验证目录已创建
        assert (tmp_path / "logs").exists()


class TestSystemCheck:
    """系统检查数据类测试"""
    
    def test_system_check_creation(self):
        """测试创建系统检查"""
        check = SystemCheck(
            name="Test Check",
            status=CheckStatus.PASSED,
            message="Test message",
            details="Test details",
            fix_available=True,
            fix_command="test_fix"
        )
        
        assert check.name == "Test Check"
        assert check.status == CheckStatus.PASSED
        assert check.message == "Test message"
        assert check.details == "Test details"
        assert check.fix_available
        assert check.fix_command == "test_fix"
    
    def test_system_check_minimal(self):
        """测试最小化系统检查"""
        check = SystemCheck(
            name="Test",
            status=CheckStatus.PASSED,
            message="OK"
        )
        
        assert check.name == "Test"
        assert check.status == CheckStatus.PASSED
        assert check.message == "OK"
        assert check.details is None
        assert not check.fix_available
        assert check.fix_command is None


class TestCheckStatus:
    """检查状态枚举测试"""
    
    def test_check_status_values(self):
        """测试检查状态值"""
        assert CheckStatus.PASSED.value == "passed"
        assert CheckStatus.WARNING.value == "warning"
        assert CheckStatus.FAILED.value == "failed"
        assert CheckStatus.SKIPPED.value == "skipped"
