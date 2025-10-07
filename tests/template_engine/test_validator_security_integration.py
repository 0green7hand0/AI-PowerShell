"""
测试 TemplateValidator 与 SecurityChecker 的集成
"""

import pytest
import tempfile
from pathlib import Path

from src.template_engine.template_validator import TemplateValidator
from src.template_engine.models import Template, TemplateParameter, TemplateCategory


class TestValidatorSecurityIntegration:
    """测试验证器的安全检查集成"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.validator = TemplateValidator(enable_security_checks=True)
        self.temp_dir = tempfile.mkdtemp()
    
    def create_test_template(self, script_content: str, name: str = "test_template") -> Template:
        """创建测试模板"""
        template_file = Path(self.temp_dir) / f"{name}.ps1"
        template_file.write_text(script_content, encoding='utf-8')
        
        return Template(
            id=name,
            name=name,
            file_path=str(template_file),
            description="Test template",
            category=TemplateCategory.AUTOMATION,
            keywords=["test"],
            parameters={}
        )
    
    def test_validator_with_security_enabled(self):
        """测试启用安全检查的验证器"""
        validator = TemplateValidator(enable_security_checks=True)
        assert validator.enable_security_checks
        assert validator.security_checker is not None
    
    def test_validator_with_security_disabled(self):
        """测试禁用安全检查的验证器"""
        validator = TemplateValidator(enable_security_checks=False)
        assert not validator.enable_security_checks
        assert validator.security_checker is None
    
    def test_validate_safe_template(self):
        """测试验证安全模板"""
        script = """
        param(
            [string]$Name
        )
        
        Write-Host "Hello, $Name"
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        assert result.is_valid
    
    def test_validate_template_with_dangerous_command(self):
        """测试验证包含危险命令的模板"""
        script = """
        param(
            [string]$Path
        )
        
        Remove-Item $Path -Recurse -Force
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Should fail due to dangerous command
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any('dangerous_command' in error for error in result.errors)
    
    def test_validate_template_with_network_access(self):
        """测试验证包含网络访问的模板"""
        script = """
        param(
            [string]$Url
        )
        
        Invoke-WebRequest -Uri $Url
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Should fail due to network access
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any('network_access' in error for error in result.errors)
    
    def test_validate_template_with_path_traversal(self):
        """测试验证包含路径遍历的模板"""
        script = """
        $file = "..\\..\\Windows\\System32\\file.txt"
        Copy-Item -Path $file -Destination "C:\\temp"
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Should fail due to path traversal
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any('path_traversal' in error for error in result.errors)
    
    def test_validate_security_method(self):
        """测试 validate_security 方法"""
        script = """
        Remove-Item C:\\temp -Recurse -Force
        Invoke-WebRequest -Uri "https://example.com"
        """
        
        result = self.validator.validate_security(script)
        
        assert not result.is_valid
        assert len(result.errors) >= 2
    
    def test_validate_security_with_safe_script(self):
        """测试安全脚本的安全验证"""
        script = """
        param([string]$Name)
        Write-Host "Hello, $Name"
        """
        
        result = self.validator.validate_security(script)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_security_disabled_validator(self):
        """测试禁用安全检查时的行为"""
        validator = TemplateValidator(enable_security_checks=False)
        
        script = """
        Remove-Item C:\\Windows -Recurse -Force
        """
        
        template = self.create_test_template(script)
        result = validator.validate_template(template)
        
        # Should not check security, but may fail on syntax
        # The dangerous command should not be detected
        security_errors = [e for e in result.errors if 'dangerous_command' in e]
        assert len(security_errors) == 0
    
    def test_multiple_security_issues_in_template(self):
        """测试模板中的多个安全问题"""
        script = """
        param([string]$Path)
        
        # Multiple issues
        Remove-Item $Path -Recurse -Force
        Invoke-WebRequest -Uri "https://malicious.com"
        $sensitive = "C:\\Windows\\System32\\file.txt"
        Copy-Item -Path $sensitive -Destination "C:\\temp"
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        assert not result.is_valid
        # Should have multiple errors
        assert len(result.errors) >= 2
    
    def test_security_warnings_vs_errors(self):
        """测试安全警告与错误的区分"""
        script = """
        # Medium severity - should be warning
        Remove-Item C:\\temp\\file.txt
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Medium severity doesn't fail validation
        assert result.is_valid
        # But should have warnings
        assert len(result.warnings) > 0
    
    def test_security_check_with_comments(self):
        """测试安全检查跳过注释"""
        script = """
        # Remove-Item C:\\Windows -Recurse -Force
        # This is just a comment, not actual code
        Write-Host "Safe operation"
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Should be valid - dangerous command is in comment
        assert result.is_valid
    
    def test_combined_validation_failures(self):
        """测试组合验证失败（语法+安全）"""
        script = """
        param([string]$Path)
        
        # Syntax error
        if ($Path {
            Remove-Item $Path -Recurse -Force
        }
        """
        
        template = self.create_test_template(script)
        result = self.validator.validate_template(template)
        
        # Should fail on both syntax and security
        assert not result.is_valid
        assert len(result.errors) >= 1  # At least syntax or security error
    
    def test_security_error_format(self):
        """测试安全错误的格式"""
        script = """
        Remove-Item C:\\temp -Recurse -Force
        """
        
        result = self.validator.validate_security(script)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Check error format includes category
        error = result.errors[0]
        assert '[' in error and ']' in error  # Category in brackets
    
    def test_security_with_line_numbers(self):
        """测试安全错误包含行号"""
        script = """Line 1
Line 2
Remove-Item -Recurse -Force
Line 4
"""
        
        result = self.validator.validate_security(script)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Check that line number is included
        error = result.errors[0]
        assert '行' in error or 'line' in error.lower()
    
    def test_realistic_template_validation(self):
        """测试真实模板的验证"""
        script = """
        param(
            [Parameter(Mandatory=$true)]
            [string]$SourcePath,
            
            [Parameter(Mandatory=$true)]
            [string]$DestinationPath
        )
        
        # Safe backup operation
        if (Test-Path $SourcePath) {
            Copy-Item -Path $SourcePath -Destination $DestinationPath -Recurse
            Write-Host "Backup completed successfully"
        } else {
            Write-Error "Source path not found: $SourcePath"
        }
        """
        
        template = self.create_test_template(script)
        template.parameters = {
            'SourcePath': TemplateParameter(
                name='SourcePath',
                type='path',
                default=None,
                description='Source path',
                required=True
            ),
            'DestinationPath': TemplateParameter(
                name='DestinationPath',
                type='path',
                default=None,
                description='Destination path',
                required=True
            )
        }
        
        result = self.validator.validate_template(template)
        
        # Should be valid - safe operations
        assert result.is_valid


class TestSecurityCheckerDisabled:
    """测试禁用安全检查的场景"""
    
    def test_no_security_checker_when_disabled(self):
        """测试禁用时不创建安全检查器"""
        validator = TemplateValidator(enable_security_checks=False)
        
        assert validator.security_checker is None
    
    def test_validate_security_returns_valid_when_disabled(self):
        """测试禁用时 validate_security 返回有效结果"""
        validator = TemplateValidator(enable_security_checks=False)
        
        dangerous_script = "Remove-Item C:\\Windows -Recurse -Force"
        result = validator.validate_security(dangerous_script)
        
        # Should return valid when security checker is disabled
        assert result.is_valid
        assert len(result.errors) == 0
