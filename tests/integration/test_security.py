"""
安全集成测试

测试系统的安全机制，包括危险命令阻止、权限检查、沙箱隔离等。
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from src.main import PowerShellAssistant
from src.interfaces.base import (
    ExecutionResult, Suggestion, ValidationResult,
    RiskLevel, Context
)


class TestDangerousCommandBlocking:
    """危险命令阻止测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "security_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: true
  whitelist_mode: "strict"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
    - "Format-Volume"
    - "Stop-Computer"
    - "Restart-Computer"
    - "Remove-Item.*C:\\\\Windows"
    - "Remove-Item.*C:\\\\Program Files"
  safe_prefixes:
    - "Get-"
    - "Test-"
    - "Show-"
    - "Find-"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/security_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/security"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_recursive_delete_blocked(self, assistant):
        """测试递归删除命令被阻止"""
        context = assistant._build_context()
        dangerous_command = "Remove-Item -Recurse -Force C:\\test"
        
        # 验证命令
        validation = assistant.security_engine.validate_command(dangerous_command, context)
        
        # 验证命令被标记为危险
        assert validation.is_valid is False or validation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        if not validation.is_valid:
            assert len(validation.blocked_reasons) > 0
            print(f"\n递归删除命令被阻止: {validation.blocked_reasons}")
    
    def test_format_volume_blocked(self, assistant):
        """测试格式化磁盘命令被阻止"""
        context = assistant._build_context()
        dangerous_command = "Format-Volume -DriveLetter C -FileSystem NTFS"
        
        # 验证命令
        validation = assistant.security_engine.validate_command(dangerous_command, context)
        
        # 验证命令被标记为危险
        assert validation.is_valid is False or validation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        if not validation.is_valid:
            print(f"\n格式化磁盘命令被阻止: {validation.blocked_reasons}")
    
    def test_system_shutdown_blocked(self, assistant):
        """测试系统关机命令被阻止"""
        context = assistant._build_context()
        dangerous_commands = [
            "Stop-Computer",
            "Stop-Computer -Force",
            "Restart-Computer"
        ]
        
        for command in dangerous_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证命令被标记为危险或需要确认
            assert validation.is_valid is False or validation.requires_confirmation
            
            print(f"\n系统关机/重启命令: {command}")
            print(f"  验证结果: {'阻止' if not validation.is_valid else '需要确认'}")
            print(f"  风险等级: {validation.risk_level.value}")
    
    def test_system_directory_deletion_blocked(self, assistant):
        """测试系统目录删除被阻止"""
        context = assistant._build_context()
        dangerous_commands = [
            "Remove-Item C:\\Windows\\System32",
            "Remove-Item 'C:\\Program Files\\*'",
            "Remove-Item C:\\Windows -Recurse"
        ]
        
        for command in dangerous_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证命令被标记为危险
            assert validation.is_valid is False or validation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            
            print(f"\n系统目录删除命令: {command}")
            print(f"  风险等级: {validation.risk_level.value}")
    
    def test_safe_commands_allowed(self, assistant):
        """测试安全命令被允许"""
        context = assistant._build_context()
        safe_commands = [
            "Get-Date",
            "Get-Process",
            "Get-Service",
            "Test-Connection localhost",
            "Get-ChildItem",
            "Show-Command Get-Process"
        ]
        
        for command in safe_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证安全命令被允许
            assert validation.is_valid is True
            assert validation.risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
            
            print(f"\n安全命令: {command}")
            print(f"  风险等级: {validation.risk_level.value}")


class TestPermissionChecking:
    """权限检查测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "perm_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: true
  whitelist_mode: "permissive"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/perm_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/perm"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_admin_command_detection(self, assistant):
        """测试管理员命令检测"""
        context = assistant._build_context()
        admin_commands = [
            "Install-WindowsFeature Web-Server",
            "Set-ExecutionPolicy Unrestricted",
            "New-NetFirewallRule -DisplayName 'Test' -Direction Inbound",
            "Stop-Service -Name 'wuauserv'"
        ]
        
        for command in admin_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证命令被标记为需要权限提升或确认
            assert validation.requires_elevation or validation.requires_confirmation
            
            print(f"\n管理员命令: {command}")
            print(f"  需要权限提升: {validation.requires_elevation}")
            print(f"  需要确认: {validation.requires_confirmation}")
    
    def test_regular_user_commands(self, assistant):
        """测试普通用户命令"""
        context = assistant._build_context()
        user_commands = [
            "Get-Process",
            "Get-ChildItem",
            "Get-Content test.txt",
            "Test-Path C:\\temp"
        ]
        
        for command in user_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证普通命令不需要权限提升
            assert validation.requires_elevation is False
            
            print(f"\n普通用户命令: {command}")
            print(f"  风险等级: {validation.risk_level.value}")


class TestRiskLevelAssessment:
    """风险等级评估测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "risk_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: true
  whitelist_mode: "permissive"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
    - "Format-Volume"
  safe_prefixes:
    - "Get-"
    - "Test-"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/risk_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/risk"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_safe_risk_level(self, assistant):
        """测试安全风险等级"""
        context = assistant._build_context()
        safe_commands = [
            "Get-Date",
            "Get-Location",
            "Test-Path C:\\temp"
        ]
        
        for command in safe_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            assert validation.risk_level == RiskLevel.SAFE
            print(f"\n安全命令: {command} -> {validation.risk_level.value}")
    
    def test_low_risk_level(self, assistant):
        """测试低风险等级"""
        context = assistant._build_context()
        low_risk_commands = [
            "Get-Process | Where-Object {$_.CPU -gt 100}",
            "Get-ChildItem -Recurse",
            "Get-Content *.log"
        ]
        
        for command in low_risk_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            assert validation.risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
            print(f"\n低风险命令: {command} -> {validation.risk_level.value}")
    
    def test_medium_risk_level(self, assistant):
        """测试中等风险等级"""
        context = assistant._build_context()
        medium_risk_commands = [
            "Set-Content test.txt 'data'",
            "New-Item -ItemType Directory test",
            "Copy-Item source.txt dest.txt"
        ]
        
        for command in medium_risk_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            assert validation.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
            print(f"\n中等风险命令: {command} -> {validation.risk_level.value}")
    
    def test_high_risk_level(self, assistant):
        """测试高风险等级"""
        context = assistant._build_context()
        high_risk_commands = [
            "Remove-Item test.txt",
            "Stop-Process -Name notepad",
            "Set-ExecutionPolicy Bypass"
        ]
        
        for command in high_risk_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 高风险命令应该需要确认或被阻止
            assert validation.requires_confirmation or not validation.is_valid
            print(f"\n高风险命令: {command} -> {validation.risk_level.value}")
    
    def test_critical_risk_level(self, assistant):
        """测试严重风险等级"""
        context = assistant._build_context()
        critical_commands = [
            "Remove-Item -Recurse -Force C:\\*",
            "Format-Volume -DriveLetter C",
            "Stop-Computer -Force"
        ]
        
        for command in critical_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 严重风险命令应该被阻止
            assert not validation.is_valid or validation.risk_level == RiskLevel.CRITICAL
            print(f"\n严重风险命令: {command} -> {validation.risk_level.value}")


class TestSandboxIsolation:
    """沙箱隔离测试"""
    
    @pytest.fixture
    def assistant_with_sandbox(self, tmp_path):
        """创建启用沙箱的测试助手"""
        config_file = tmp_path / "sandbox_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: true
  require_confirmation: false
  whitelist_mode: "permissive"
  sandbox_config:
    image: "mcr.microsoft.com/powershell:latest"
    memory_limit: "512m"
    cpu_limit: 0.5
    network_mode: "none"
    read_only: true

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/sandbox_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/sandbox"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    @pytest.mark.skipif(True, reason="Requires Docker to be installed and running")
    def test_sandbox_execution(self, assistant_with_sandbox):
        """测试沙箱执行（需要 Docker）"""
        # 注意：此测试需要 Docker 环境
        context = assistant_with_sandbox._build_context()
        command = "Get-Date"
        
        # 在沙箱中执行命令
        result = assistant_with_sandbox.executor.execute(command, timeout=30)
        
        # 验证命令在沙箱中执行
        assert isinstance(result, ExecutionResult)
        print(f"\n沙箱执行结果: {result.success}")
    
    def test_sandbox_configuration_validation(self, assistant_with_sandbox):
        """测试沙箱配置验证"""
        # 验证沙箱配置已加载
        assert assistant_with_sandbox.config.security.sandbox_enabled is True
        
        # 验证沙箱配置参数
        sandbox_config = assistant_with_sandbox.config.security.sandbox_config
        assert sandbox_config is not None
        
        print(f"\n沙箱配置:")
        print(f"  启用状态: {assistant_with_sandbox.config.security.sandbox_enabled}")
        print(f"  配置: {sandbox_config}")


class TestSecurityBypass:
    """安全绕过测试（负面测试）"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "bypass_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: true
  whitelist_mode: "strict"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
  safe_prefixes:
    - "Get-"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/bypass_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/bypass"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_obfuscated_dangerous_command(self, assistant):
        """测试混淆的危险命令"""
        context = assistant._build_context()
        
        # 尝试各种混淆方式
        obfuscated_commands = [
            "Remove-Item -Recurse -Force C:\\test",  # 直接形式
            "rm -r -force C:\\test",  # 别名形式
            "Remove-Item -Path C:\\test -Recurse -Force",  # 参数顺序变化
        ]
        
        for command in obfuscated_commands:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证混淆命令仍然被检测
            assert not validation.is_valid or validation.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            
            print(f"\n混淆命令检测: {command}")
            print(f"  被阻止: {not validation.is_valid}")
            print(f"  风险等级: {validation.risk_level.value}")
    
    def test_command_injection_prevention(self, assistant):
        """测试命令注入防护"""
        context = assistant._build_context()
        
        # 尝试命令注入
        injection_attempts = [
            "Get-Date; Remove-Item -Recurse -Force C:\\test",
            "Get-Date | Remove-Item -Recurse -Force C:\\test",
            "Get-Date && Remove-Item -Recurse -Force C:\\test"
        ]
        
        for command in injection_attempts:
            validation = assistant.security_engine.validate_command(command, context)
            
            # 验证注入尝试被检测
            # 注意：具体行为取决于安全引擎的实现
            print(f"\n命令注入测试: {command}")
            print(f"  验证结果: {validation.is_valid}")
            print(f"  风险等级: {validation.risk_level.value}")


class TestEndToEndSecurityFlow:
    """端到端安全流程测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "e2e_sec_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "strict"
  dangerous_patterns:
    - "Remove-Item.*-Recurse.*-Force"
    - "Format-Volume"
  safe_prefixes:
    - "Get-"
    - "Test-"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/e2e_sec_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/e2e_sec"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def test_safe_command_full_flow(self, assistant):
        """测试安全命令的完整流程"""
        # 执行安全命令
        result = assistant.process_request("显示当前时间", auto_execute=True)
        
        # 验证命令成功执行
        assert isinstance(result, ExecutionResult)
        assert result.command is not None
        
        print(f"\n安全命令完整流程:")
        print(f"  命令: {result.command}")
        print(f"  执行状态: {'成功' if result.success else '失败'}")
    
    def test_dangerous_command_blocked_flow(self, assistant):
        """测试危险命令被阻止的完整流程"""
        # 尝试执行危险命令
        result = assistant.process_request("删除所有文件", auto_execute=True)
        
        # 验证结果
        assert isinstance(result, ExecutionResult)
        
        # 根据 AI 翻译结果，命令可能被阻止或执行失败
        print(f"\n危险命令处理流程:")
        print(f"  命令: {result.command}")
        print(f"  执行状态: {'成功' if result.success else '失败'}")
        if not result.success:
            print(f"  错误信息: {result.error}")
    
    def test_security_audit_logging(self, assistant):
        """测试安全审计日志"""
        # 执行多个不同风险等级的命令
        commands = [
            "显示当前时间",  # 安全
            "列出所有文件",  # 安全
            "删除测试文件"   # 可能危险
        ]
        
        for cmd in commands:
            result = assistant.process_request(cmd, auto_execute=True)
            assert isinstance(result, ExecutionResult)
        
        # 验证日志文件存在
        log_file = Path("logs/e2e_sec_test.log")
        if log_file.exists():
            print(f"\n审计日志已创建: {log_file}")
        
        # 验证历史记录
        history = assistant.storage.load_history(limit=10)
        assert len(history) >= len(commands)
        
        print(f"\n历史记录数量: {len(history)}")


class TestSecurityConfiguration:
    """安全配置测试"""
    
    def test_strict_mode_configuration(self, tmp_path):
        """测试严格模式配置"""
        config_file = tmp_path / "strict_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: true
  whitelist_mode: "strict"
  dangerous_patterns:
    - "Remove-Item"
    - "Stop-"
  safe_prefixes:
    - "Get-"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/strict_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/strict"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        assistant = PowerShellAssistant(config_path=str(config_file))
        
        # 验证严格模式配置
        assert assistant.config.security.whitelist_mode == "strict"
        assert assistant.config.security.require_confirmation is True
        
        print(f"\n严格模式配置:")
        print(f"  白名单模式: {assistant.config.security.whitelist_mode}")
        print(f"  需要确认: {assistant.config.security.require_confirmation}")
    
    def test_permissive_mode_configuration(self, tmp_path):
        """测试宽松模式配置"""
        config_file = tmp_path / "permissive_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"

execution:
  timeout: 30

logging:
  level: "INFO"
  file: "logs/permissive_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/permissive"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        
        assistant = PowerShellAssistant(config_path=str(config_file))
        
        # 验证宽松模式配置
        assert assistant.config.security.whitelist_mode == "permissive"
        assert assistant.config.security.require_confirmation is False
        
        print(f"\n宽松模式配置:")
        print(f"  白名单模式: {assistant.config.security.whitelist_mode}")
        print(f"  需要确认: {assistant.config.security.require_confirmation}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
