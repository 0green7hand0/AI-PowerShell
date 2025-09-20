"""Unit tests for permission checking system"""

import unittest
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import Permission
from security.engine import PermissionChecker


class TestPermissionChecker(unittest.TestCase):
    """Test cases for PermissionChecker"""
    
    def setUp(self):
        """Set up test environment"""
        self.permission_checker = PermissionChecker(require_admin_confirmation=True)
    
    def test_admin_permission_detection(self):
        """Test detection of commands requiring admin permissions"""
        admin_commands = [
            "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Test -Name Value -Value 1",
            "New-ItemProperty -Path HKLM:\\SYSTEM\\Test -Name Key -Value Data",
            "Stop-Service -Name Spooler",
            "Start-Service -Name Themes",
            "Set-Service -Name Spooler -StartupType Disabled",
            "Stop-Computer -ComputerName localhost",
            "Restart-Computer -Force",
            "New-LocalUser -Name TestUser -Password (ConvertTo-SecureString 'Pass' -AsPlainText -Force)",
            "Remove-LocalUser -Name TestUser",
            "Add-LocalGroupMember -Group Administrators -Member TestUser",
            "Install-Module -Name PowerShellGet -Force",
            "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned",
        ]
        
        for command in admin_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                self.assertIn(Permission.ADMIN, permissions, 
                            f"Admin permission not detected for: {command}")
    
    def test_write_permission_detection(self):
        """Test detection of commands requiring write permissions"""
        write_commands = [
            "Set-Content -Path C:\\temp\\file.txt -Value 'Hello World'",
            "Add-Content -Path C:\\logs\\app.log -Value 'New entry'",
            "Out-File -FilePath C:\\output\\result.txt -InputObject $data",
            "New-Item -Path C:\\temp\\newfile.txt -ItemType File",
            "Copy-Item -Path C:\\source\\file.txt -Destination C:\\dest\\",
            "Move-Item -Path C:\\old\\file.txt -Destination C:\\new\\",
            "Rename-Item -Path C:\\temp\\old.txt -NewName new.txt",
            "Remove-Item -Path C:\\temp\\file.txt",
            "Set-ItemProperty -Path C:\\temp\\file.txt -Name IsReadOnly -Value $false",
        ]
        
        for command in write_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                self.assertIn(Permission.WRITE, permissions,
                            f"Write permission not detected for: {command}")
    
    def test_execute_permission_detection(self):
        """Test detection of commands requiring execute permissions"""
        execute_commands = [
            "Start-Process -FilePath notepad.exe",
            "Invoke-Expression 'Get-Process'",
            "& 'C:\\Program Files\\App\\app.exe'",
            ". ./script.ps1",
            "./myscript.ps1",
        ]
        
        for command in execute_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                self.assertIn(Permission.EXECUTE, permissions,
                            f"Execute permission not detected for: {command}")
    
    def test_multiple_permissions(self):
        """Test commands requiring multiple permissions"""
        # Command that writes and requires admin
        command = "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Test -Name Value -Value 1"
        permissions = self.permission_checker.check_permissions(command)
        
        self.assertIn(Permission.ADMIN, permissions)
        # Note: Registry operations are admin-level, not just write
    
    def test_read_only_commands(self):
        """Test that read-only commands require no special permissions"""
        read_only_commands = [
            "Get-Process",
            "Get-Service | Where-Object Status -eq Running",
            "Select-Object -Property Name, Status",
            "Sort-Object -Property CPU -Descending",
            "Measure-Object -Property Length -Sum",
            "Format-Table -AutoSize",
            "Where-Object {$_.CPU -gt 50}",
            "Group-Object -Property Status",
        ]
        
        for command in read_only_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                self.assertEqual(len(permissions), 0,
                               f"Read-only command should not require permissions: {command}")
    
    def test_case_insensitive_detection(self):
        """Test that permission detection is case insensitive"""
        commands_variants = [
            ("stop-service -name spooler", "Stop-Service -Name Spooler"),
            ("SET-CONTENT -path c:\\file.txt -value test", "Set-Content -Path C:\\file.txt -Value test"),
            ("start-process notepad", "Start-Process notepad"),
        ]
        
        for lower_cmd, upper_cmd in commands_variants:
            with self.subTest(lower=lower_cmd, upper=upper_cmd):
                lower_perms = self.permission_checker.check_permissions(lower_cmd)
                upper_perms = self.permission_checker.check_permissions(upper_cmd)
                
                self.assertEqual(set(lower_perms), set(upper_perms),
                               f"Case sensitivity issue: {lower_cmd} vs {upper_cmd}")
    
    def test_complex_command_parsing(self):
        """Test permission detection in complex command pipelines"""
        complex_commands = [
            # Pipeline with write operation
            ("Get-Process | Where-Object CPU -gt 50 | Out-File C:\\high_cpu.txt", [Permission.WRITE]),
            
            # Multiple operations
            ("Stop-Service Spooler; Start-Service Themes", [Permission.ADMIN]),
            
            # Conditional execution with admin operation
            ("if ($true) { Set-ExecutionPolicy RemoteSigned }", [Permission.ADMIN]),
            
            # Script block with file operations
            ("Get-ChildItem C:\\temp | ForEach-Object { Remove-Item $_.FullName }", [Permission.WRITE]),
        ]
        
        for command, expected_perms in complex_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                
                for expected_perm in expected_perms:
                    self.assertIn(expected_perm, permissions,
                                f"Expected permission {expected_perm} not found in: {command}")
    
    def test_permission_patterns_coverage(self):
        """Test that all permission patterns are properly defined"""
        # Verify that all permission types have patterns
        self.assertIn(Permission.ADMIN, self.permission_checker.permission_patterns)
        self.assertIn(Permission.WRITE, self.permission_checker.permission_patterns)
        self.assertIn(Permission.EXECUTE, self.permission_checker.permission_patterns)
        
        # Verify patterns are not empty
        for permission, patterns in self.permission_checker.permission_patterns.items():
            self.assertGreater(len(patterns), 0, f"No patterns defined for {permission}")
            
            # Verify patterns are valid regex
            import re
            for pattern in patterns:
                try:
                    re.compile(pattern)
                except re.error:
                    self.fail(f"Invalid regex pattern for {permission}: {pattern}")
    
    def test_no_duplicate_permissions(self):
        """Test that duplicate permissions are not returned"""
        # Command that might match multiple patterns for same permission
        command = "Set-Content C:\\file1.txt 'test'; Set-Content C:\\file2.txt 'test'"
        permissions = self.permission_checker.check_permissions(command)
        
        # Should not have duplicate WRITE permissions
        unique_permissions = list(set(permissions))
        self.assertEqual(len(permissions), len(unique_permissions),
                        "Duplicate permissions returned")
    
    def test_admin_confirmation_setting(self):
        """Test admin confirmation requirement setting"""
        # Test with confirmation required
        checker_with_confirmation = PermissionChecker(require_admin_confirmation=True)
        self.assertTrue(checker_with_confirmation.require_admin_confirmation)
        
        # Test with confirmation not required
        checker_without_confirmation = PermissionChecker(require_admin_confirmation=False)
        self.assertFalse(checker_without_confirmation.require_admin_confirmation)
    
    def test_registry_operations_detection(self):
        """Test specific registry operation detection"""
        registry_commands = [
            "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run -Name MyApp -Value 'C:\\app.exe'",
            "New-ItemProperty -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\MyService -Name Start -Value 2",
            "Get-ItemProperty -Path HKLM:\\SOFTWARE\\Test",  # This should NOT require admin (read-only)
            "Remove-ItemProperty -Path HKLM:\\SOFTWARE\\Test -Name OldValue",
        ]
        
        # HKLM operations should require admin
        for i, command in enumerate(registry_commands):
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                
                if i == 2:  # Get-ItemProperty is read-only
                    self.assertNotIn(Permission.ADMIN, permissions,
                                   f"Read-only registry operation should not require admin: {command}")
                else:
                    self.assertIn(Permission.ADMIN, permissions,
                                f"Registry write operation should require admin: {command}")
    
    def test_service_operations_detection(self):
        """Test service management operation detection"""
        service_commands = [
            ("Stop-Service -Name Spooler", True),
            ("Start-Service -Name Themes", True),
            ("Set-Service -Name Spooler -StartupType Manual", True),
            ("Restart-Service -Name Spooler", True),
            ("Get-Service -Name Spooler", False),  # Read-only
            ("Get-Service | Where-Object Status -eq Running", False),  # Read-only
        ]
        
        for command, should_require_admin in service_commands:
            with self.subTest(command=command):
                permissions = self.permission_checker.check_permissions(command)
                
                if should_require_admin:
                    self.assertIn(Permission.ADMIN, permissions,
                                f"Service management should require admin: {command}")
                else:
                    self.assertNotIn(Permission.ADMIN, permissions,
                                   f"Service query should not require admin: {command}")


class TestPermissionCheckerIntegration(unittest.TestCase):
    """Integration tests for PermissionChecker"""
    
    def test_real_world_scenarios(self):
        """Test with real-world command scenarios"""
        checker = PermissionChecker()
        
        # System administration scenario
        admin_scenario = [
            "Get-Service | Where-Object Status -eq Stopped",  # Query - no perms
            "Stop-Service -Name Spooler",  # Admin required
            "Set-Service -Name Spooler -StartupType Disabled",  # Admin required
            "Get-EventLog -LogName System -Newest 10",  # Query - no perms
        ]
        
        expected_perms = [[], [Permission.ADMIN], [Permission.ADMIN], []]
        
        for command, expected in zip(admin_scenario, expected_perms):
            with self.subTest(command=command):
                permissions = checker.check_permissions(command)
                self.assertEqual(set(permissions), set(expected),
                               f"Permission mismatch for: {command}")
        
        # File management scenario
        file_scenario = [
            "Get-ChildItem C:\\temp",  # Query - no perms
            "New-Item -Path C:\\temp\\backup -ItemType Directory",  # Write required
            "Copy-Item -Path C:\\data\\* -Destination C:\\temp\\backup\\",  # Write required
            "Remove-Item -Path C:\\temp\\old\\* -Recurse",  # Write required
        ]
        
        expected_perms = [[], [Permission.WRITE], [Permission.WRITE], [Permission.WRITE]]
        
        for command, expected in zip(file_scenario, expected_perms):
            with self.subTest(command=command):
                permissions = checker.check_permissions(command)
                self.assertEqual(set(permissions), set(expected),
                               f"Permission mismatch for: {command}")


if __name__ == '__main__':
    unittest.main()