"""Comprehensive End-to-End Workflow Tests

This module provides comprehensive end-to-end workflow tests that validate
complete user scenarios from start to finish.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

import sys
sys.path.insert(0, str(Path(__file__).parent))

from main_integration import AIPowerShellAssistantIntegration, MCPToolImplementations
from config.models import ServerConfig, ModelConfig, SecurityConfig, LoggingConfig, ExecutionConfig, StorageConfig, MCPServerConfig
from interfaces.base import (
    Platform, UserRole, LogLevel, OutputFormat, RiskLevel, SecurityAction, Permission,
    CommandSuggestion, ValidationResult, ExecutionResult
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def workflow_config(temp_dir):
    """Create configuration for workflow testing"""
    config = ServerConfig(
        version="1.0.0-workflow-test",
        platform=Platform.WINDOWS,
        debug_mode=True,
        model=ModelConfig(),
        security=SecurityConfig(
            whitelist_path=str(Path(temp_dir) / "whitelist.json"),
            sandbox_enabled=True,
            audit_log_path=str(Path(temp_dir) / "audit.log")
        ),
        logging=LoggingConfig(
            log_level=LogLevel.DEBUG,
            enable_correlation_tracking=True,
            audit_log_path=str(Path(temp_dir) / "audit.log")
        ),
        execution=ExecutionConfig(),
        storage=StorageConfig(data_directory=str(Path(temp_dir) / "storage")),
        mcp_server=MCPServerConfig()
    )
    return config


@pytest.fixture
def mock_workflow_integration(workflow_config):
    """Create mock integration for workflow testing"""
    integration = AIPowerShellAssistantIntegration()
    integration.config = workflow_config
    
    # Mock all components
    integration.storage = AsyncMock()
    integration.logging_engine = AsyncMock()
    integration.context_manager = AsyncMock()
    integration.ai_engine = Mock()
    integration.security_engine = Mock()
    integration.executor = Mock()
    integration.mcp_server = Mock()
    
    # Setup return values
    integration.context_manager.create_session.return_value = "workflow-session"
    integration.context_manager.get_current_context.return_value = Mock()
    integration.logging_engine.log_user_input.return_value = "workflow-corr"
    
    integration._initialized = True
    return integration


class TestSystemAdministrationWorkflows:
    """Test complete system administration workflows"""
    
    @pytest.mark.asyncio
    async def test_process_management_workflow(self, mock_workflow_integration):
        """Test complete process management workflow"""
        tool_implementations = MCPToolImplementations(mock_workflow_integration)
        
        # Setup AI engine responses for process management
        ai_responses = {
            "show running processes": CommandSuggestion(
                original_input="show running processes",
                generated_command="Get-Process | Where-Object {$_.Status -eq 'Running'}",
                confidence_score=0.95,
                explanation="Lists all running processes",
                alternatives=["Get-Process", "ps"]
            ),
            "find high cpu processes": CommandSuggestion(
                original_input="find high cpu processes",
                generated_command="Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
                confidence_score=0.92,
                explanation="Shows top 5 CPU-consuming processes",
                alternatives=["Get-Process | Sort-Object CPU"]
            ),
            "stop notepad process": CommandSuggestion(
                original_input="stop notepad process",
                generated_command="Stop-Process -Name notepad -Confirm:$false",
                confidence_score=0.88,
                explanation="Stops all notepad processes",
                alternatives=["Get-Process notepad | Stop-Process"]
            )
        }
        
        def mock_ai_translate(input_text, context):
            return ai_responses.get(input_text, CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Help",
                confidence_score=0.3,
                explanation="Fallback command",
                alternatives=[]
            ))
        
        mock_workflow_integration.ai_engine.translate_natural_language.side_effect = mock_ai_translate
        
        # Setup security validation
        def mock_security_validate(command):
            if "Stop-Process" in command:
                return ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[Permission.ADMIN],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.MEDIUM
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.LOW
                )
        
        mock_workflow_integration.security_engine.validate_command.side_effect = mock_security_validate
        
        # Setup execution responses
        execution_responses = {
            "Get-Process | Where-Object {$_.Status -eq 'Running'}": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "explorer", "Id": 1234}, {"Name": "chrome", "Id": 5678}]',
                stderr="",
                execution_time=0.5,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "chrome", "CPU": 45.2}, {"Name": "firefox", "CPU": 23.1}]',
                stderr="",
                execution_time=0.3,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Stop-Process -Name notepad -Confirm:$false": ExecutionResult(
                success=True,
                return_code=0,
                stdout="Process stopped successfully",
                stderr="",
                execution_time=0.2,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        }
        
        def mock_execute(command, context):
            return execution_responses.get(command, ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr="Command not found",
                execution_time=0.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ))
        
        mock_workflow_integration.executor.execute_command.side_effect = mock_execute
        mock_workflow_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Execute workflow steps
        workflow_steps = [
            "show running processes",
            "find high cpu processes", 
            "stop notepad process"
        ]
        
        workflow_results = []
        
        for step in workflow_steps:
            # Step 1: Natural language to PowerShell
            nl_result = await tool_implementations.natural_language_to_powershell(step)
            assert nl_result["success"] is True
            
            # Step 2: Execute the generated command
            exec_result = await tool_implementations.execute_powershell_command(
                nl_result["generated_command"]
            )
            
            workflow_results.append({
                "step": step,
                "nl_result": nl_result,
                "exec_result": exec_result
            })
        
        # Verify workflow completion
        assert len(workflow_results) == 3
        
        # Verify each step
        for i, result in enumerate(workflow_results):
            assert result["nl_result"]["success"] is True
            assert result["exec_result"]["success"] is True
            print(f"Step {i+1} ({result['step']}): SUCCESS")
        
        # Verify admin permission was detected for stop command
        stop_result = workflow_results[2]
        assert Permission.ADMIN in stop_result["nl_result"]["security_validation"]["required_permissions"]  
  @pytest.mark.asyncio
    async def test_file_management_workflow(self, mock_workflow_integration):
        """Test complete file management workflow"""
        tool_implementations = MCPToolImplementations(mock_workflow_integration)
        
        # Setup AI responses for file management
        ai_responses = {
            "list files in documents": CommandSuggestion(
                original_input="list files in documents",
                generated_command="Get-ChildItem -Path $env:USERPROFILE\\Documents",
                confidence_score=0.93,
                explanation="Lists files in Documents folder",
                alternatives=["ls ~/Documents", "dir Documents"]
            ),
            "find large files": CommandSuggestion(
                original_input="find large files",
                generated_command="Get-ChildItem -Recurse | Where-Object {$_.Length -gt 100MB}",
                confidence_score=0.89,
                explanation="Finds files larger than 100MB",
                alternatives=["Get-ChildItem -Recurse | Sort-Object Length"]
            ),
            "copy important files to backup": CommandSuggestion(
                original_input="copy important files to backup",
                generated_command="Copy-Item -Path 'C:\\Important\\*' -Destination 'C:\\Backup\\' -Recurse",
                confidence_score=0.85,
                explanation="Copies important files to backup location",
                alternatives=["robocopy C:\\Important C:\\Backup /E"]
            )
        }
        
        def mock_ai_translate(input_text, context):
            return ai_responses.get(input_text, CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Help",
                confidence_score=0.3,
                explanation="Fallback command",
                alternatives=[]
            ))
        
        mock_workflow_integration.ai_engine.translate_natural_language.side_effect = mock_ai_translate
        
        # Setup security validation
        def mock_security_validate(command):
            if "Copy-Item" in command:
                return ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[Permission.WRITE],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.LOW
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.LOW
                )
        
        mock_workflow_integration.security_engine.validate_command.side_effect = mock_security_validate
        
        # Setup execution responses
        execution_responses = {
            "Get-ChildItem -Path $env:USERPROFILE\\Documents": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "report.docx", "Length": 1024}, {"Name": "data.xlsx", "Length": 2048}]',
                stderr="",
                execution_time=0.4,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-ChildItem -Recurse | Where-Object {$_.Length -gt 100MB}": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "video.mp4", "Length": 209715200}, {"Name": "backup.zip", "Length": 157286400}]',
                stderr="",
                execution_time=2.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Copy-Item -Path 'C:\\Important\\*' -Destination 'C:\\Backup\\' -Recurse": ExecutionResult(
                success=True,
                return_code=0,
                stdout="Files copied successfully",
                stderr="",
                execution_time=5.2,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        }
        
        def mock_execute(command, context):
            return execution_responses.get(command, ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr="Command not found",
                execution_time=0.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ))
        
        mock_workflow_integration.executor.execute_command.side_effect = mock_execute
        mock_workflow_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Execute file management workflow
        workflow_steps = [
            "list files in documents",
            "find large files",
            "copy important files to backup"
        ]
        
        for step in workflow_steps:
            nl_result = await tool_implementations.natural_language_to_powershell(step)
            assert nl_result["success"] is True
            
            exec_result = await tool_implementations.execute_powershell_command(
                nl_result["generated_command"]
            )
            assert exec_result["success"] is True
            
            print(f"File management step '{step}': SUCCESS")
        
        # Verify write permission was detected for copy operation
        copy_nl_result = await tool_implementations.natural_language_to_powershell("copy important files to backup")
        assert Permission.WRITE in copy_nl_result["security_validation"]["required_permissions"]


class TestSecurityWorkflows:
    """Test security-focused workflows"""
    
    @pytest.mark.asyncio
    async def test_security_audit_workflow(self, mock_workflow_integration):
        """Test complete security audit workflow"""
        tool_implementations = MCPToolImplementations(mock_workflow_integration)
        
        # Setup AI responses for security audit
        ai_responses = {
            "check running services": CommandSuggestion(
                original_input="check running services",
                generated_command="Get-Service | Where-Object Status -eq Running",
                confidence_score=0.94,
                explanation="Lists all running services",
                alternatives=["Get-Service", "sc query"]
            ),
            "find suspicious processes": CommandSuggestion(
                original_input="find suspicious processes",
                generated_command="Get-Process | Where-Object {$_.ProcessName -notmatch '^(System|svchost|explorer|winlogon)$'}",
                confidence_score=0.87,
                explanation="Finds processes that might be suspicious",
                alternatives=["Get-Process | Sort-Object CPU -Descending"]
            ),
            "check network connections": CommandSuggestion(
                original_input="check network connections",
                generated_command="Get-NetTCPConnection | Where-Object State -eq Established",
                confidence_score=0.91,
                explanation="Shows established network connections",
                alternatives=["netstat -an", "Get-NetTCPConnection"]
            )
        }
        
        def mock_ai_translate(input_text, context):
            return ai_responses.get(input_text, CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Help",
                confidence_score=0.3,
                explanation="Fallback command",
                alternatives=[]
            ))
        
        mock_workflow_integration.ai_engine.translate_natural_language.side_effect = mock_ai_translate
        
        # Setup security validation (all commands should be allowed for audit)
        mock_workflow_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Setup execution responses
        execution_responses = {
            "Get-Service | Where-Object Status -eq Running": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "Spooler", "Status": "Running"}, {"Name": "Themes", "Status": "Running"}]',
                stderr="",
                execution_time=0.6,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-Process | Where-Object {$_.ProcessName -notmatch '^(System|svchost|explorer|winlogon)$'}": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"ProcessName": "chrome", "Id": 1234}, {"ProcessName": "notepad", "Id": 5678}]',
                stderr="",
                execution_time=0.8,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-NetTCPConnection | Where-Object State -eq Established": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"LocalAddress": "192.168.1.100", "RemoteAddress": "93.184.216.34", "State": "Established"}]',
                stderr="",
                execution_time=1.2,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        }
        
        def mock_execute(command, context):
            return execution_responses.get(command, ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr="Command not found",
                execution_time=0.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ))
        
        mock_workflow_integration.executor.execute_command.side_effect = mock_execute
        mock_workflow_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Execute security audit workflow
        audit_steps = [
            "check running services",
            "find suspicious processes",
            "check network connections"
        ]
        
        audit_results = []
        
        for step in audit_steps:
            nl_result = await tool_implementations.natural_language_to_powershell(step)
            assert nl_result["success"] is True
            
            exec_result = await tool_implementations.execute_powershell_command(
                nl_result["generated_command"]
            )
            assert exec_result["success"] is True
            
            audit_results.append({
                "step": step,
                "command": nl_result["generated_command"],
                "output": exec_result["stdout"]
            })
            
            print(f"Security audit step '{step}': SUCCESS")
        
        # Verify audit data was collected
        assert len(audit_results) == 3
        for result in audit_results:
            assert len(result["output"]) > 0
            assert "[]" not in result["output"]  # Should have actual data
    
    @pytest.mark.asyncio
    async def test_blocked_command_workflow(self, mock_workflow_integration):
        """Test workflow with blocked dangerous commands"""
        tool_implementations = MCPToolImplementations(mock_workflow_integration)
        
        # Setup AI to generate dangerous commands
        def mock_ai_translate(input_text, context):
            if "delete system files" in input_text:
                return CommandSuggestion(
                    original_input=input_text,
                    generated_command="Remove-Item C:\\Windows\\System32\\* -Recurse -Force",
                    confidence_score=0.75,
                    explanation="Deletes system files (DANGEROUS)",
                    alternatives=["Get-ChildItem C:\\Windows\\System32"]
                )
            else:
                return CommandSuggestion(
                    original_input=input_text,
                    generated_command="Get-Help",
                    confidence_score=0.3,
                    explanation="Safe fallback",
                    alternatives=[]
                )
        
        mock_workflow_integration.ai_engine.translate_natural_language.side_effect = mock_ai_translate
        
        # Setup security to block dangerous commands
        def mock_security_validate(command):
            if "Remove-Item" in command and "System32" in command:
                return ValidationResult(
                    is_valid=False,
                    blocked_reasons=["Dangerous system file deletion attempt"],
                    required_permissions=[],
                    suggested_alternatives=["Get-ChildItem to list files instead"],
                    risk_assessment=RiskLevel.CRITICAL
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    blocked_reasons=[],
                    required_permissions=[],
                    suggested_alternatives=[],
                    risk_assessment=RiskLevel.LOW
                )
        
        mock_workflow_integration.security_engine.validate_command.side_effect = mock_security_validate
        
        # Test dangerous command workflow
        nl_result = await tool_implementations.natural_language_to_powershell("delete system files")
        
        # Natural language processing should succeed
        assert nl_result["success"] is True
        assert "Remove-Item" in nl_result["generated_command"]
        
        # But security validation should block it
        assert nl_result["security_validation"]["is_valid"] is False
        assert len(nl_result["security_validation"]["blocked_reasons"]) > 0
        
        # Execution should be blocked
        exec_result = await tool_implementations.execute_powershell_command(
            nl_result["generated_command"]
        )
        
        assert exec_result["success"] is False
        assert exec_result["error_code"] == "SECURITY_BLOCKED"
        assert len(exec_result["blocked_reasons"]) > 0
        
        print("Dangerous command properly blocked by security system")


class TestTroubleshootingWorkflows:
    """Test troubleshooting and diagnostic workflows"""
    
    @pytest.mark.asyncio
    async def test_system_diagnostic_workflow(self, mock_workflow_integration):
        """Test complete system diagnostic workflow"""
        tool_implementations = MCPToolImplementations(mock_workflow_integration)
        
        # Setup AI responses for diagnostics
        ai_responses = {
            "check system health": CommandSuggestion(
                original_input="check system health",
                generated_command="Get-ComputerInfo | Select-Object TotalPhysicalMemory, CsProcessors, WindowsVersion",
                confidence_score=0.92,
                explanation="Gets basic system health information",
                alternatives=["Get-WmiObject Win32_ComputerSystem"]
            ),
            "check disk space": CommandSuggestion(
                original_input="check disk space",
                generated_command="Get-PSDrive -PSProvider FileSystem",
                confidence_score=0.95,
                explanation="Shows disk space usage",
                alternatives=["Get-WmiObject Win32_LogicalDisk"]
            ),
            "check event logs for errors": CommandSuggestion(
                original_input="check event logs for errors",
                generated_command="Get-EventLog -LogName System -EntryType Error -Newest 10",
                confidence_score=0.88,
                explanation="Shows recent system errors",
                alternatives=["Get-WinEvent -FilterHashtable @{LogName='System'; Level=2}"]
            )
        }
        
        def mock_ai_translate(input_text, context):
            return ai_responses.get(input_text, CommandSuggestion(
                original_input=input_text,
                generated_command="Get-Help",
                confidence_score=0.3,
                explanation="Fallback command",
                alternatives=[]
            ))
        
        mock_workflow_integration.ai_engine.translate_natural_language.side_effect = mock_ai_translate
        
        # All diagnostic commands should be allowed
        mock_workflow_integration.security_engine.validate_command.return_value = ValidationResult(
            is_valid=True,
            blocked_reasons=[],
            required_permissions=[],
            suggested_alternatives=[],
            risk_assessment=RiskLevel.LOW
        )
        
        # Setup diagnostic responses
        execution_responses = {
            "Get-ComputerInfo | Select-Object TotalPhysicalMemory, CsProcessors, WindowsVersion": ExecutionResult(
                success=True,
                return_code=0,
                stdout='{"TotalPhysicalMemory": 17179869184, "CsProcessors": 8, "WindowsVersion": "10.0.19041"}',
                stderr="",
                execution_time=1.5,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-PSDrive -PSProvider FileSystem": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"Name": "C", "Used": 107374182400, "Free": 429496729600}]',
                stderr="",
                execution_time=0.3,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ),
            "Get-EventLog -LogName System -EntryType Error -Newest 10": ExecutionResult(
                success=True,
                return_code=0,
                stdout='[{"TimeGenerated": "2024-01-15 10:30:00", "Source": "Service Control Manager", "Message": "Service failed to start"}]',
                stderr="",
                execution_time=2.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        }
        
        def mock_execute(command, context):
            return execution_responses.get(command, ExecutionResult(
                success=False,
                return_code=1,
                stdout="",
                stderr="Command not found",
                execution_time=0.1,
                platform=Platform.WINDOWS,
                sandbox_used=False
            ))
        
        mock_workflow_integration.executor.execute_command.side_effect = mock_execute
        mock_workflow_integration.executor.format_output.side_effect = lambda output, format_type: output
        
        # Execute diagnostic workflow
        diagnostic_steps = [
            "check system health",
            "check disk space", 
            "check event logs for errors"
        ]
        
        diagnostic_data = {}
        
        for step in diagnostic_steps:
            nl_result = await tool_implementations.natural_language_to_powershell(step)
            assert nl_result["success"] is True
            
            exec_result = await tool_implementations.execute_powershell_command(
                nl_result["generated_command"]
            )
            assert exec_result["success"] is True
            
            diagnostic_data[step] = {
                "command": nl_result["generated_command"],
                "output": exec_result["stdout"],
                "execution_time": exec_result["execution_time"]
            }
            
            print(f"Diagnostic step '{step}': SUCCESS ({exec_result['execution_time']}s)")
        
        # Verify diagnostic data collection
        assert len(diagnostic_data) == 3
        
        # Verify system health data
        health_output = diagnostic_data["check system health"]["output"]
        assert "TotalPhysicalMemory" in health_output
        assert "CsProcessors" in health_output
        
        # Verify disk space data
        disk_output = diagnostic_data["check disk space"]["output"]
        assert "Used" in disk_output
        assert "Free" in disk_output
        
        # Verify error log data
        error_output = diagnostic_data["check event logs for errors"]["output"]
        assert "TimeGenerated" in error_output
        assert "Message" in error_output


if __name__ == "__main__":
    # Run comprehensive workflow tests
    pytest.main([__file__, "-v", "-k", "test_"])