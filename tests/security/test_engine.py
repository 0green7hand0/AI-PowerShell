"""
安全引擎主类测试
"""

import pytest
from unittest.mock import Mock, patch
from src.security.engine import SecurityEngine
from src.interfaces.base import Context, RiskLevel, ValidationResult


class TestSecurityEngine:
    """测试安全引擎主类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.config = {
            'whitelist_mode': 'strict',
            'require_confirmation': True,
            'sandbox_enabled': False
        }
        self.engine = SecurityEngine(self.config)
        self.context = Context(session_id="test-session")
    
    def test_initialization(self):
        """测试初始化"""
        assert self.engine.config == self.config
        assert self.engine.require_confirmation is True
        assert self.engine.whitelist is not None
        assert self.engine.permission_checker is not None
    
    def test_validate_safe_command(self):
        """测试验证安全命令"""
        result = self.engine.validate_command("Get-Date", self.context)
        
        assert result.is_valid is True
        assert result.risk_level == RiskLevel.SAFE
        assert result.requires_elevation is False
    
    def test_validate_dangerous_command(self):
        """测试验证危险命令"""
        result = self.engine.validate_command("Remove-Item C:\\test -Recurse -Force", self.context)
        
        assert result.is_valid is False
        assert result.risk_level == RiskLevel.CRITICAL
        assert len(result.blocked_reasons) > 0
    
    def test_validate_empty_command(self):
        """测试验证空命令"""
        result = self.engine.validate_command("", self.context)
        
        assert result.is_valid is False
        assert "命令为空" in result.blocked_reasons
    
    def test_validate_whitespace_command(self):
        """测试验证空白命令"""
        result = self.engine.validate_command("   ", self.context)
        
        assert result.is_valid is False
        assert "命令为空" in result.blocked_reasons
    
    def test_validate_command_requires_admin(self):
        """测试需要管理员权限的命令"""
        # Mock permission checker to simulate non-admin user
        with patch.object(self.engine.permission_checker, 'requires_admin', return_value=True):
            with patch.object(self.engine.permission_checker, 'check_current_permissions', return_value=False):
                result = self.engine.validate_command("Start-Service -Name Spooler", self.context)
                
                assert result.is_valid is False
                assert result.requires_elevation is True
                assert result.risk_level == RiskLevel.HIGH
                assert "管理员权限" in result.blocked_reasons[0]
    
    def test_validate_command_with_admin_permission(self):
        """测试有管理员权限时验证命令"""
        # Mock permission checker to simulate admin user
        with patch.object(self.engine.permission_checker, 'requires_admin', return_value=True):
            with patch.object(self.engine.permission_checker, 'check_current_permissions', return_value=True):
                result = self.engine.validate_command("Start-Service -Name Spooler", self.context)
                
                # 命令应该通过权限检查，但可能需要确认
                assert result.is_valid is True
                assert result.requires_elevation is True
    
    def test_check_permissions_safe_command(self):
        """测试检查安全命令的权限"""
        result = self.engine.check_permissions("Get-Date")
        assert result is True
    
    def test_check_permissions_admin_command_without_permission(self):
        """测试检查需要管理员权限的命令（无权限）"""
        with patch.object(self.engine.permission_checker, 'requires_admin', return_value=True):
            with patch.object(self.engine.permission_checker, 'check_current_permissions', return_value=False):
                result = self.engine.check_permissions("Start-Service -Name Spooler")
                assert result is False
    
    def test_check_permissions_admin_command_with_permission(self):
        """测试检查需要管理员权限的命令（有权限）"""
        with patch.object(self.engine.permission_checker, 'requires_admin', return_value=True):
            with patch.object(self.engine.permission_checker, 'check_current_permissions', return_value=True):
                result = self.engine.check_permissions("Start-Service -Name Spooler")
                assert result is True
    
    def test_is_dangerous_command(self):
        """测试判断危险命令"""
        assert self.engine.is_dangerous_command("Remove-Item C:\\test -Recurse -Force") is True
        assert self.engine.is_dangerous_command("Format-Volume -DriveLetter C") is True
        assert self.engine.is_dangerous_command("Get-Date") is False
        assert self.engine.is_dangerous_command("Get-Process") is False
    
    def test_get_user_confirmation_safe(self):
        """测试获取用户确认（安全命令）"""
        with patch('builtins.input', return_value='y'):
            result = self.engine.get_user_confirmation("Get-Date", RiskLevel.SAFE)
            assert result is True
    
    def test_get_user_confirmation_high_risk_yes(self):
        """测试获取用户确认（高风险命令，用户同意）"""
        with patch('builtins.input', return_value='y'):
            result = self.engine.get_user_confirmation("Stop-Computer", RiskLevel.HIGH)
            assert result is True
    
    def test_get_user_confirmation_high_risk_no(self):
        """测试获取用户确认（高风险命令，用户拒绝）"""
        with patch('builtins.input', return_value='n'):
            result = self.engine.get_user_confirmation("Stop-Computer", RiskLevel.HIGH)
            assert result is False
    
    def test_get_user_confirmation_various_inputs(self):
        """测试各种用户输入"""
        with patch('builtins.input', return_value='yes'):
            assert self.engine.get_user_confirmation("Get-Date", RiskLevel.SAFE) is True
        
        with patch('builtins.input', return_value='是'):
            assert self.engine.get_user_confirmation("Get-Date", RiskLevel.SAFE) is True
        
        with patch('builtins.input', return_value='no'):
            assert self.engine.get_user_confirmation("Get-Date", RiskLevel.SAFE) is False
        
        with patch('builtins.input', return_value=''):
            assert self.engine.get_user_confirmation("Get-Date", RiskLevel.SAFE) is False
    
    def test_should_confirm_with_require_confirmation(self):
        """测试配置要求确认时的行为"""
        engine = SecurityEngine({'require_confirmation': True})
        
        # 所有风险等级都需要确认
        assert engine._should_confirm(RiskLevel.SAFE) is True
        assert engine._should_confirm(RiskLevel.LOW) is True
        assert engine._should_confirm(RiskLevel.MEDIUM) is True
        assert engine._should_confirm(RiskLevel.HIGH) is True
    
    def test_should_confirm_without_require_confirmation(self):
        """测试配置不要求确认时的行为"""
        engine = SecurityEngine({'require_confirmation': False})
        
        # 只有中等及以上风险需要确认
        assert engine._should_confirm(RiskLevel.SAFE) is False
        assert engine._should_confirm(RiskLevel.LOW) is False
        assert engine._should_confirm(RiskLevel.MEDIUM) is True
        assert engine._should_confirm(RiskLevel.HIGH) is True
        assert engine._should_confirm(RiskLevel.CRITICAL) is True
    
    def test_sandbox_enabled(self):
        """测试启用沙箱"""
        config = {'sandbox_enabled': True}
        engine = SecurityEngine(config)
        
        assert engine.sandbox is not None
    
    def test_sandbox_disabled(self):
        """测试禁用沙箱"""
        config = {'sandbox_enabled': False}
        engine = SecurityEngine(config)
        
        assert engine.sandbox is None
    
    def test_validate_command_integration(self):
        """测试完整的验证流程"""
        # 测试一个需要确认的命令
        result = self.engine.validate_command("Set-Location C:\\", self.context)
        
        assert result.is_valid is True
        assert result.requires_confirmation is True
        assert result.risk_level == RiskLevel.MEDIUM
    
    def test_multiple_validations(self):
        """测试多次验证"""
        commands = [
            "Get-Date",
            "Get-Process",
            "Set-Location C:\\",
            "Remove-Item test.txt"
        ]
        
        for command in commands:
            result = self.engine.validate_command(command, self.context)
            assert isinstance(result, ValidationResult)
            assert hasattr(result, 'is_valid')
            assert hasattr(result, 'risk_level')
