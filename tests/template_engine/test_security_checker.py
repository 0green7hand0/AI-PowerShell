"""
安全检查器测试
"""

import pytest
from src.template_engine.security_checker import (
    SecurityChecker,
    SecurityIssue,
    SecurityCheckResult
)


class TestSecurityChecker:
    """测试 SecurityChecker 类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.checker = SecurityChecker()
    
    def test_init(self):
        """测试初始化"""
        assert self.checker is not None
        assert self.checker.issues == []
    
    def test_safe_script(self):
        """测试安全脚本"""
        script = """
        param(
            [string]$Name,
            [int]$Count
        )
        
        Write-Host "Hello, $Name"
        for ($i = 0; $i -lt $Count; $i++) {
            Write-Output "Iteration $i"
        }
        """
        
        result = self.checker.check_template(script)
        assert result.is_safe
        assert len(result.issues) == 0
    
    def test_dangerous_command_critical(self):
        """测试检测关键危险命令"""
        script = """
        Remove-Item C:\\temp\\* -Recurse -Force
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        assert len(result.issues) > 0
        
        critical_issues = [i for i in result.issues if i.severity == 'critical']
        assert len(critical_issues) > 0
        assert critical_issues[0].category == 'dangerous_command'
    
    def test_dangerous_command_format_volume(self):
        """测试检测格式化卷命令"""
        script = """
        Format-Volume -DriveLetter D -FileSystem NTFS
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        critical_issues = [i for i in result.issues if i.severity == 'critical']
        assert len(critical_issues) > 0
    
    def test_dangerous_command_high(self):
        """测试检测高危命令"""
        script = """
        Remove-Item $env:TEMP\\file.txt -Force
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        high_issues = [i for i in result.issues if i.severity == 'high']
        assert len(high_issues) > 0
    
    def test_dangerous_command_invoke_expression(self):
        """测试检测 Invoke-Expression"""
        script = """
        $command = "Get-Process"
        Invoke-Expression $command
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        high_issues = [i for i in result.issues if i.severity == 'high']
        assert len(high_issues) > 0
        assert any('Invoke-Expression' in i.message for i in high_issues)
    
    def test_dangerous_command_medium(self):
        """测试检测中危命令"""
        script = """
        Remove-Item C:\\temp\\file.txt
        """
        
        result = self.checker.check_template(script)
        # Medium severity doesn't make it unsafe
        assert result.is_safe
        
        medium_issues = [i for i in result.issues if i.severity == 'medium']
        assert len(medium_issues) > 0
    
    def test_check_dangerous_commands_method(self):
        """测试 check_dangerous_commands 方法"""
        script = """
        Stop-Computer -Force
        """
        
        issues = self.checker.check_dangerous_commands(script)
        assert len(issues) > 0
        assert issues[0].severity == 'critical'
        assert issues[0].category == 'dangerous_command'
        assert issues[0].line_number > 0
    
    def test_dangerous_commands_skip_comments(self):
        """测试跳过注释行"""
        script = """
        # Remove-Item C:\\Windows -Recurse -Force
        # This is just a comment
        Write-Host "Safe command"
        """
        
        result = self.checker.check_template(script)
        assert result.is_safe
        assert len(result.issues) == 0
    
    def test_network_access_high(self):
        """测试检测高危网络访问"""
        script = """
        Invoke-WebRequest -Uri "https://example.com" -OutFile "file.txt"
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        network_issues = [i for i in result.issues if i.category == 'network_access']
        assert len(network_issues) > 0
        assert network_issues[0].severity == 'high'
    
    def test_network_access_invoke_restmethod(self):
        """测试检测 Invoke-RestMethod"""
        script = """
        $response = Invoke-RestMethod -Uri "https://api.example.com/data"
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        network_issues = [i for i in result.issues if i.category == 'network_access']
        assert len(network_issues) > 0
    
    def test_network_access_medium(self):
        """测试检测中危网络访问"""
        script = """
        Test-Connection -ComputerName "server.local"
        """
        
        result = self.checker.check_template(script)
        # Medium severity doesn't make it unsafe
        assert result.is_safe
        
        network_issues = [i for i in result.issues if i.category == 'network_access']
        assert len(network_issues) > 0
        assert network_issues[0].severity == 'medium'
    
    def test_check_network_access_method(self):
        """测试 check_network_access 方法"""
        script = """
        wget https://example.com/file.zip
        """
        
        issues = self.checker.check_network_access(script)
        assert len(issues) > 0
        assert issues[0].category == 'network_access'
    
    def test_network_commands_skip_comments(self):
        """测试网络命令跳过注释"""
        script = """
        # Invoke-WebRequest -Uri "https://example.com"
        Write-Host "No network access"
        """
        
        result = self.checker.check_template(script)
        assert result.is_safe
    
    def test_validate_file_path_safe(self):
        """测试验证安全路径"""
        safe_paths = [
            "C:\\Users\\Documents\\file.txt",
            "D:\\Projects\\script.ps1",
            ".\\relative\\path.txt",
            "output.log"
        ]
        
        for path in safe_paths:
            is_safe, message = self.checker.validate_file_path(path)
            assert is_safe, f"Path should be safe: {path}, but got: {message}"
    
    def test_validate_file_path_traversal(self):
        """测试检测路径遍历攻击"""
        dangerous_paths = [
            "..\\..\\Windows\\System32\\file.txt",
            "../../../etc/passwd",
            "C:\\temp\\..\\..\\Windows\\file.txt"
        ]
        
        for path in dangerous_paths:
            is_safe, message = self.checker.validate_file_path(path)
            assert not is_safe, f"Path should be unsafe: {path}"
            assert "路径遍历" in message or "父目录引用" in message
    
    def test_validate_file_path_sensitive(self):
        """测试检测敏感路径"""
        sensitive_paths = [
            "C:\\Windows\\System32\\config.sys",
            "C:\\Program Files\\app\\file.exe",
            "$env:SystemRoot\\file.txt"
        ]
        
        for path in sensitive_paths:
            is_safe, message = self.checker.validate_file_path(path)
            assert not is_safe, f"Path should be unsafe: {path}"
            assert "敏感路径" in message
    
    def test_path_security_in_script(self):
        """测试脚本中的路径安全检查"""
        script = """
        $file = "..\\..\\Windows\\System32\\file.txt"
        Copy-Item -Path $file -Destination "C:\\temp"
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        path_issues = [i for i in result.issues if i.category == 'path_traversal']
        assert len(path_issues) > 0
    
    def test_path_security_with_path_parameter(self):
        """测试 -Path 参数的路径安全"""
        script = """
        Remove-Item -Path "C:\\Windows\\System32\\file.txt"
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        
        path_issues = [i for i in result.issues if i.category == 'path_traversal']
        assert len(path_issues) > 0
    
    def test_multiple_security_issues(self):
        """测试检测多个安全问题"""
        script = """
        # Multiple security issues
        Remove-Item C:\\Windows\\file.txt -Force
        Invoke-WebRequest -Uri "https://malicious.com"
        $path = "..\\..\\sensitive\\data.txt"
        Copy-Item -Path $path -Destination "C:\\temp"
        """
        
        result = self.checker.check_template(script)
        assert not result.is_safe
        assert len(result.issues) >= 3
        
        # Check we have different categories
        categories = set(i.category for i in result.issues)
        assert 'dangerous_command' in categories
        assert 'network_access' in categories
        assert 'path_traversal' in categories
    
    def test_security_issue_line_numbers(self):
        """测试安全问题包含行号"""
        script = """Line 1
Line 2
Remove-Item -Recurse -Force
Line 4
"""
        
        result = self.checker.check_template(script)
        assert len(result.issues) > 0
        assert result.issues[0].line_number == 3
    
    def test_security_issue_code_snippet(self):
        """测试安全问题包含代码片段"""
        script = """
        Remove-Item C:\\temp -Recurse -Force
        """
        
        result = self.checker.check_template(script)
        assert len(result.issues) > 0
        assert result.issues[0].code_snippet
        assert "Remove-Item" in result.issues[0].code_snippet
    
    def test_case_insensitive_detection(self):
        """测试大小写不敏感检测"""
        scripts = [
            "remove-item -recurse -force",
            "REMOVE-ITEM -RECURSE -FORCE",
            "Remove-Item -Recurse -Force",
            "ReMoVe-ItEm -ReCuRsE -FoRcE"
        ]
        
        for script in scripts:
            result = self.checker.check_template(script)
            assert not result.is_safe, f"Should detect: {script}"
    
    def test_empty_script(self):
        """测试空脚本"""
        result = self.checker.check_template("")
        assert result.is_safe
        assert len(result.issues) == 0
    
    def test_script_with_only_comments(self):
        """测试只有注释的脚本"""
        script = """
        # This is a comment
        # Another comment
        # Remove-Item -Recurse -Force (in comment)
        """
        
        result = self.checker.check_template(script)
        assert result.is_safe
        assert len(result.issues) == 0


class TestSecurityIssue:
    """测试 SecurityIssue 数据类"""
    
    def test_create_security_issue(self):
        """测试创建安全问题"""
        issue = SecurityIssue(
            severity='high',
            category='dangerous_command',
            message='Test message',
            line_number=10,
            code_snippet='Remove-Item -Force'
        )
        
        assert issue.severity == 'high'
        assert issue.category == 'dangerous_command'
        assert issue.message == 'Test message'
        assert issue.line_number == 10
        assert issue.code_snippet == 'Remove-Item -Force'
    
    def test_security_issue_defaults(self):
        """测试安全问题默认值"""
        issue = SecurityIssue(
            severity='medium',
            category='network_access',
            message='Test'
        )
        
        assert issue.line_number == 0
        assert issue.code_snippet == ""


class TestSecurityCheckResult:
    """测试 SecurityCheckResult 数据类"""
    
    def test_create_result(self):
        """测试创建检查结果"""
        issues = [
            SecurityIssue('high', 'dangerous_command', 'Issue 1'),
            SecurityIssue('medium', 'network_access', 'Issue 2')
        ]
        
        result = SecurityCheckResult(is_safe=False, issues=issues)
        
        assert not result.is_safe
        assert len(result.issues) == 2
    
    def test_result_bool_conversion(self):
        """测试结果的布尔转换"""
        safe_result = SecurityCheckResult(is_safe=True, issues=[])
        unsafe_result = SecurityCheckResult(is_safe=False, issues=[])
        
        assert bool(safe_result) is True
        assert bool(unsafe_result) is False
    
    def test_empty_result(self):
        """测试空结果"""
        result = SecurityCheckResult(is_safe=True, issues=[])
        
        assert result.is_safe
        assert len(result.issues) == 0
        assert bool(result)


class TestSecurityCheckerIntegration:
    """集成测试"""
    
    def test_realistic_backup_script(self):
        """测试真实的备份脚本"""
        script = """
        param(
            [string]$SourcePath,
            [string]$DestinationPath
        )
        
        # Create backup
        if (Test-Path $SourcePath) {
            Copy-Item -Path $SourcePath -Destination $DestinationPath -Recurse
            Write-Host "Backup completed"
        }
        """
        
        checker = SecurityChecker()
        result = checker.check_template(script)
        
        # Should be safe - no dangerous operations
        assert result.is_safe
    
    def test_realistic_cleanup_script_with_issues(self):
        """测试有问题的清理脚本"""
        script = """
        param(
            [string]$TempPath
        )
        
        # Dangerous: force recursive delete
        Remove-Item $TempPath -Recurse -Force
        
        # Dangerous: accessing system directory
        Remove-Item "C:\\Windows\\Temp\\*" -Force
        """
        
        checker = SecurityChecker()
        result = checker.check_template(script)
        
        # Should be unsafe
        assert not result.is_safe
        assert len(result.issues) >= 2
    
    def test_realistic_download_script(self):
        """测试下载脚本"""
        script = """
        param(
            [string]$Url,
            [string]$OutputPath
        )
        
        # Download file
        Invoke-WebRequest -Uri $Url -OutFile $OutputPath
        Write-Host "Download completed"
        """
        
        checker = SecurityChecker()
        result = checker.check_template(script)
        
        # Should be unsafe due to network access
        assert not result.is_safe
        
        network_issues = [i for i in result.issues if i.category == 'network_access']
        assert len(network_issues) > 0
