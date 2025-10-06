"""
权限检查测试
"""

import pytest
import platform
from src.security.permissions import PermissionChecker


class TestPermissionChecker:
    """测试权限检查器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.checker = PermissionChecker()
    
    def test_requires_admin_service_commands(self):
        """测试服务命令需要管理员权限"""
        assert self.checker.requires_admin("Start-Service -Name Spooler")
        assert self.checker.requires_admin("Stop-Service -Name Spooler")
        assert self.checker.requires_admin("Restart-Service -Name Spooler")
    
    def test_requires_admin_execution_policy(self):
        """测试设置执行策略需要管理员权限"""
        assert self.checker.requires_admin("Set-ExecutionPolicy RemoteSigned")
        assert self.checker.requires_admin("Set-ExecutionPolicy Unrestricted")
    
    def test_requires_admin_registry_hklm(self):
        """测试 HKLM 注册表操作需要管理员权限"""
        assert self.checker.requires_admin("Set-ItemProperty -Path HKLM:\\Software\\Test -Name Value -Value 1")
        assert self.checker.requires_admin("New-ItemProperty -Path HKLM:\\Software\\Test -Name Value -Value 1")
        assert self.checker.requires_admin("Remove-ItemProperty -Path HKLM:\\Software\\Test -Name Value")
    
    def test_requires_admin_user_management(self):
        """测试用户管理需要管理员权限"""
        assert self.checker.requires_admin("New-LocalUser -Name TestUser")
        assert self.checker.requires_admin("Remove-LocalUser -Name TestUser")
        assert self.checker.requires_admin("Add-LocalGroupMember -Group Administrators -Member TestUser")
    
    def test_requires_admin_network_config(self):
        """测试网络配置需要管理员权限"""
        assert self.checker.requires_admin("Set-NetIPAddress -InterfaceAlias Ethernet -IPAddress 192.168.1.100")
        assert self.checker.requires_admin("Disable-NetAdapter -Name Ethernet")
        assert self.checker.requires_admin("Enable-NetAdapter -Name Ethernet")
    
    def test_requires_admin_computer_management(self):
        """测试计算机管理需要管理员权限"""
        assert self.checker.requires_admin("Stop-Computer")
        assert self.checker.requires_admin("Restart-Computer")
        assert self.checker.requires_admin("Rename-Computer -NewName NewPC")
    
    def test_not_requires_admin_get_commands(self):
        """测试 Get-* 命令不需要管理员权限"""
        assert not self.checker.requires_admin("Get-Date")
        assert not self.checker.requires_admin("Get-Process")
        assert not self.checker.requires_admin("Get-Service")
        assert not self.checker.requires_admin("Get-ChildItem")
    
    def test_not_requires_admin_read_only(self):
        """测试只读命令不需要管理员权限"""
        assert not self.checker.requires_admin("Test-Path C:\\Windows")
        assert not self.checker.requires_admin("Select-String -Path test.txt -Pattern 'hello'")
        assert not self.checker.requires_admin("Where-Object {$_.Name -eq 'test'}")
    
    def test_check_current_permissions(self):
        """测试检查当前权限"""
        # 这个测试结果取决于运行测试的用户权限
        result = self.checker.check_current_permissions()
        assert isinstance(result, bool)
    
    def test_get_elevation_command_windows(self):
        """测试 Windows 权限提升命令"""
        if platform.system() == "Windows":
            command = "Get-Service"
            elevated = self.checker.get_elevation_command(command)
            assert "Start-Process" in elevated
            assert "RunAs" in elevated
            assert command in elevated
    
    def test_get_elevation_command_unix(self):
        """测试 Unix/Linux 权限提升命令"""
        if platform.system() in ["Linux", "Darwin"]:
            command = "Get-Service"
            elevated = self.checker.get_elevation_command(command)
            assert "sudo" in elevated
            assert command in elevated
    
    def test_get_permission_info(self):
        """测试获取权限信息"""
        info = self.checker.get_permission_info()
        
        assert "platform" in info
        assert "is_admin" in info
        assert "can_elevate" in info
        assert "user" in info
        
        assert isinstance(info["platform"], str)
        assert isinstance(info["is_admin"], bool)
        assert isinstance(info["can_elevate"], bool)
        assert isinstance(info["user"], str)
    
    def test_platform_detection(self):
        """测试平台检测"""
        assert self.checker.platform in ["Windows", "Linux", "Darwin"]
    
    def test_case_insensitive_pattern_matching(self):
        """测试大小写不敏感的模式匹配"""
        assert self.checker.requires_admin("start-service -Name Spooler")
        assert self.checker.requires_admin("START-SERVICE -Name Spooler")
        assert self.checker.requires_admin("Start-Service -Name Spooler")
    
    def test_requires_admin_firewall(self):
        """测试防火墙命令需要管理员权限"""
        assert self.checker.requires_admin("Set-NetFirewallProfile -Profile Domain -Enabled False")
        assert self.checker.requires_admin("New-NetFirewallRule -DisplayName Test -Direction Inbound")
    
    def test_requires_admin_disk_operations(self):
        """测试磁盘操作需要管理员权限"""
        assert self.checker.requires_admin("Format-Volume -DriveLetter C")
        assert self.checker.requires_admin("Initialize-Disk -Number 1")
        assert self.checker.requires_admin("New-Partition -DiskNumber 1 -Size 100GB")
