"""Security Engine Implementation

Provides three-tier security validation:
1. Command whitelist validation
2. Dynamic permission checking  
3. Docker sandbox execution
"""

import json
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    SecurityEngineInterface, SecurityRule, ValidationResult, 
    ExecutionResult, SecurityAction, RiskLevel, Permission, Platform
)
from config.models import SecurityConfig
from security.confirmation import (
    ConfirmationManager, ConfirmationResult, ConsoleConfirmationProvider,
    PermissionEscalationLogger
)


class SecurityEngine(SecurityEngineInterface):
    """Main security engine implementing three-tier protection"""
    
    def __init__(self, config: SecurityConfig):
        """Initialize security engine with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize whitelist validator
        self.whitelist_validator = WhitelistValidator(config.whitelist_path)
        
        # Initialize permission checker
        self.permission_checker = PermissionChecker(config.require_confirmation_for_admin)
        
        # Initialize confirmation manager
        confirmation_provider = ConsoleConfirmationProvider()
        self.confirmation_manager = ConfirmationManager(confirmation_provider)
        
        # Initialize escalation logger
        self.escalation_logger = PermissionEscalationLogger()
        
        # Initialize sandbox manager (if enabled)
        self.sandbox_manager = None
        if config.sandbox_enabled:
            self.sandbox_manager = SandboxManager(
                image=config.sandbox_image,
                memory_limit=config.max_sandbox_memory,
                cpu_limit=config.max_sandbox_cpu,
                timeout=config.sandbox_timeout
            )
    
    def validate_command(self, command: str) -> ValidationResult:
        """Validate command through all security tiers"""
        self.logger.info(f"Validating command: {command[:100]}...")
        
        # Tier 1: Whitelist validation
        whitelist_result = self.whitelist_validator.validate(command)
        if not whitelist_result.is_valid:
            self.logger.warning(f"Command blocked by whitelist: {whitelist_result.blocked_reasons}")
            return whitelist_result
        
        # Tier 2: Permission checking
        required_permissions = self.permission_checker.check_permissions(command)
        
        # Combine results
        result = ValidationResult(
            is_valid=whitelist_result.is_valid,
            blocked_reasons=whitelist_result.blocked_reasons,
            required_permissions=required_permissions,
            suggested_alternatives=whitelist_result.suggested_alternatives,
            risk_assessment=whitelist_result.risk_assessment
        )
        
        self.logger.info(f"Command validation result: valid={result.is_valid}, risk={result.risk_assessment}")
        return result
    
    def check_permissions(self, command: str) -> List[Permission]:
        """Check required permissions for command"""
        return self.permission_checker.check_permissions(command)
    
    def execute_in_sandbox(self, command: str, timeout: int) -> ExecutionResult:
        """Execute command in sandboxed environment (Tier 3)"""
        if not self.sandbox_manager:
            raise RuntimeError("Sandbox execution is disabled")
        
        self.logger.info(f"Executing command in sandbox: {command[:100]}...")
        return self.sandbox_manager.execute(command, timeout)
    
    def update_whitelist(self, rules: List[SecurityRule]) -> None:
        """Update security whitelist rules"""
        self.logger.info(f"Updating whitelist with {len(rules)} rules")
        self.whitelist_validator.update_rules(rules)
    
    def request_permission_confirmation(self, command: str, required_permissions: List[Permission], session_id: str) -> bool:
        """Request user confirmation for elevated permissions"""
        if not required_permissions:
            return True  # No permissions required
        
        # Generate risk description based on permissions
        risk_description = self._generate_permission_risk_description(command, required_permissions)
        
        # Request confirmation
        response = self.confirmation_manager.request_permission_confirmation(
            command=command,
            required_permissions=required_permissions,
            session_id=session_id,
            risk_description=risk_description
        )
        
        # Log escalation attempt
        self.escalation_logger.log_escalation_attempt(
            session_id=session_id,
            command=command,
            required_permissions=required_permissions,
            confirmation_result=response.result,
            user_comment=response.user_comment
        )
        
        return response.result == ConfirmationResult.APPROVED
    
    def _generate_permission_risk_description(self, command: str, permissions: List[Permission]) -> str:
        """Generate detailed risk description for permission request"""
        risk_parts = []
        
        if Permission.ADMIN in permissions:
            risk_parts.append("requires administrative privileges")
        if Permission.WRITE in permissions:
            risk_parts.append("will modify files or system state")
        if Permission.EXECUTE in permissions:
            risk_parts.append("will execute external programs")
        
        # Add command-specific risks
        command_lower = command.lower()
        if "remove-item" in command_lower and "-force" in command_lower:
            risk_parts.append("performs forced file deletion")
        elif "stop-service" in command_lower or "start-service" in command_lower:
            risk_parts.append("modifies system services")
        elif "set-executionpolicy" in command_lower:
            risk_parts.append("changes PowerShell security policy")
        elif "format-" in command_lower:
            risk_parts.append("performs disk formatting (DESTRUCTIVE)")
        
        if risk_parts:
            return f"This command {' and '.join(risk_parts)}."
        else:
            return "This command requires elevated permissions."


class WhitelistValidator:
    """Command whitelist validation system"""
    
    def __init__(self, whitelist_path: str):
        """Initialize whitelist validator"""
        self.whitelist_path = Path(whitelist_path)
        self.rules: List[SecurityRule] = []
        self.logger = logging.getLogger(f"{__name__}.WhitelistValidator")
        
        # Load existing rules or create default ones
        self._load_rules()
    
    def validate(self, command: str) -> ValidationResult:
        """Validate command against whitelist rules"""
        self.logger.debug(f"Validating command against {len(self.rules)} rules")
        
        # Normalize command for matching
        normalized_command = self._normalize_command(command)
        
        blocked_reasons = []
        suggested_alternatives = []
        highest_risk = RiskLevel.LOW
        
        # Check each rule
        for rule in self.rules:
            if self._matches_pattern(normalized_command, rule.pattern):
                self.logger.debug(f"Command matches rule: {rule.description}")
                
                # Update highest risk level
                if self._risk_level_value(rule.risk_level) > self._risk_level_value(highest_risk):
                    highest_risk = rule.risk_level
                
                # Handle different actions
                if rule.action == SecurityAction.BLOCK:
                    blocked_reasons.append(f"Blocked by rule: {rule.description}")
                    suggested_alternatives.extend(self._get_alternatives(command, rule))
                elif rule.action == SecurityAction.REQUIRE_CONFIRMATION:
                    # This will be handled by the permission checker
                    pass
        
        # Determine if command is valid
        is_valid = len(blocked_reasons) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            blocked_reasons=blocked_reasons,
            required_permissions=[],  # Will be filled by permission checker
            suggested_alternatives=suggested_alternatives,
            risk_assessment=highest_risk
        )
    
    def update_rules(self, rules: List[SecurityRule]) -> None:
        """Update whitelist rules"""
        self.rules = rules
        self._save_rules()
        self.logger.info(f"Updated whitelist with {len(rules)} rules")
    
    def _load_rules(self) -> None:
        """Load rules from file or create defaults"""
        try:
            if self.whitelist_path.exists():
                with open(self.whitelist_path, 'r') as f:
                    data = json.load(f)
                    self.rules = [
                        SecurityRule(
                            pattern=rule['pattern'],
                            action=SecurityAction(rule['action']),
                            risk_level=RiskLevel(rule['risk_level']),
                            description=rule['description']
                        )
                        for rule in data.get('rules', [])
                    ]
                self.logger.info(f"Loaded {len(self.rules)} rules from {self.whitelist_path}")
            else:
                self._create_default_rules()
        except Exception as e:
            self.logger.error(f"Error loading rules: {e}")
            self._create_default_rules()
    
    def _save_rules(self) -> None:
        """Save rules to file"""
        try:
            # Ensure directory exists
            self.whitelist_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'rules': [
                    {
                        'pattern': rule.pattern,
                        'action': rule.action.value,
                        'risk_level': rule.risk_level.value,
                        'description': rule.description
                    }
                    for rule in self.rules
                ]
            }
            
            with open(self.whitelist_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.rules)} rules to {self.whitelist_path}")
        except Exception as e:
            self.logger.error(f"Error saving rules: {e}")
    
    def _create_default_rules(self) -> None:
        """Create default security rules"""
        self.rules = [
            # High-risk destructive commands
            SecurityRule(
                pattern=r"Remove-Item.*-Recurse.*-Force",
                action=SecurityAction.BLOCK,
                risk_level=RiskLevel.CRITICAL,
                description="Recursive forced deletion is blocked for safety"
            ),
            SecurityRule(
                pattern=r"Remove-Item.*-Force",
                action=SecurityAction.BLOCK,
                risk_level=RiskLevel.HIGH,
                description="Forced deletion operations are blocked for safety"
            ),
            SecurityRule(
                pattern=r"Format-Volume|Format-Disk",
                action=SecurityAction.BLOCK,
                risk_level=RiskLevel.CRITICAL,
                description="Disk formatting operations are blocked"
            ),
            SecurityRule(
                pattern=r"Stop-Computer|Restart-Computer",
                action=SecurityAction.REQUIRE_CONFIRMATION,
                risk_level=RiskLevel.HIGH,
                description="System shutdown/restart requires confirmation"
            ),
            
            # Registry modifications
            SecurityRule(
                pattern=r"Set-ItemProperty.*HKLM:|New-ItemProperty.*HKLM:",
                action=SecurityAction.REQUIRE_CONFIRMATION,
                risk_level=RiskLevel.HIGH,
                description="System registry modifications require confirmation"
            ),
            
            # Service management
            SecurityRule(
                pattern=r"Stop-Service|Start-Service|Set-Service",
                action=SecurityAction.REQUIRE_CONFIRMATION,
                risk_level=RiskLevel.MEDIUM,
                description="Service management requires confirmation"
            ),
            
            # Network operations
            SecurityRule(
                pattern=r"Invoke-WebRequest|Invoke-RestMethod|wget|curl",
                action=SecurityAction.REQUIRE_CONFIRMATION,
                risk_level=RiskLevel.MEDIUM,
                description="Network requests require confirmation"
            ),
            
            # Process management
            SecurityRule(
                pattern=r"Stop-Process.*-Force",
                action=SecurityAction.REQUIRE_CONFIRMATION,
                risk_level=RiskLevel.MEDIUM,
                description="Forced process termination requires confirmation"
            ),
            
            # Safe read-only operations (explicitly allowed)
            SecurityRule(
                pattern=r"Get-.*|Select-.*|Where-.*|Sort-.*|Measure-.*|Format-.*",
                action=SecurityAction.ALLOW,
                risk_level=RiskLevel.LOW,
                description="Read-only operations are allowed"
            ),
        ]
        
        self._save_rules()
        self.logger.info(f"Created {len(self.rules)} default security rules")
    
    def _normalize_command(self, command: str) -> str:
        """Normalize command for pattern matching"""
        # Remove extra whitespace and convert to lowercase for case-insensitive matching
        return ' '.join(command.strip().split())
    
    def _matches_pattern(self, command: str, pattern: str) -> bool:
        """Check if command matches security rule pattern"""
        try:
            return bool(re.search(pattern, command, re.IGNORECASE))
        except re.error as e:
            self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return False
    
    def _risk_level_value(self, risk_level: RiskLevel) -> int:
        """Convert risk level to numeric value for comparison"""
        return {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }[risk_level]
    
    def _get_alternatives(self, command: str, rule: SecurityRule) -> List[str]:
        """Get safer alternatives for blocked commands"""
        alternatives = []
        
        # Provide specific alternatives based on the blocked command
        if "Remove-Item" in command and "-Recurse" in command:
            alternatives.append("Use Get-ChildItem to list files first, then remove specific items")
            alternatives.append("Remove files one by one without -Recurse flag")
        
        if "Format-" in command:
            alternatives.append("Use Get-Volume or Get-Disk to inspect first")
            alternatives.append("Consider using Clear-Disk for data wiping instead")
        
        if "Stop-Computer" in command or "Restart-Computer" in command:
            alternatives.append("Use shutdown /s /t 0 or shutdown /r /t 0 for immediate action")
            alternatives.append("Schedule restart with shutdown /r /t 300 for delayed action")
        
        return alternatives


class PermissionChecker:
    """Dynamic permission checking system"""
    
    def __init__(self, require_admin_confirmation: bool = True):
        """Initialize permission checker"""
        self.require_admin_confirmation = require_admin_confirmation
        self.logger = logging.getLogger(f"{__name__}.PermissionChecker")
        
        # Define patterns that require specific permissions
        self.permission_patterns = {
            Permission.ADMIN: [
                r"Set-ItemProperty.*HKLM:",
                r"New-ItemProperty.*HKLM:",
                r"Remove-ItemProperty.*HKLM:",
                r"Stop-Service|Start-Service|Set-Service",
                r"Stop-Computer|Restart-Computer",
                r"New-LocalUser|Remove-LocalUser|Set-LocalUser",
                r"Add-LocalGroupMember|Remove-LocalGroupMember",
                r"Install-Module|Uninstall-Module",
                r"Set-ExecutionPolicy",
            ],
            Permission.WRITE: [
                r"Set-Content|Add-Content|Out-File",
                r"New-Item.*-ItemType.*(File|Directory)",
                r"Copy-Item|Move-Item|Rename-Item",
                r"Remove-Item",
                r"Set-ItemProperty(?!.*HKLM:)",  # Set-ItemProperty but not HKLM (which is admin)
            ],
            Permission.EXECUTE: [
                r"Start-Process|Invoke-Expression",
                r"&\s*[\"'].*[\"']",  # & "command"
                r"\.\s*/.*\.ps1",     # ./script.ps1
            ]
        }
    
    def check_permissions(self, command: str) -> List[Permission]:
        """Check what permissions are required for the command"""
        required_permissions = []
        
        for permission, patterns in self.permission_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    if permission not in required_permissions:
                        required_permissions.append(permission)
                    break
        
        self.logger.debug(f"Command requires permissions: {[p.value for p in required_permissions]}")
        return required_permissions


class SandboxManager:
    """Docker sandbox execution manager"""
    
    def __init__(self, image: str, memory_limit: str, cpu_limit: str, timeout: int):
        """Initialize sandbox manager"""
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.SandboxManager")
        
        # Check if Docker is available
        self._check_docker_availability()
    
    def execute(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute command in Docker sandbox"""
        if timeout is None:
            timeout = self.timeout
        
        start_time = time.time()
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(command)
                script_path = f.name
            
            # Build Docker command
            docker_cmd = [
                'docker', 'run', '--rm',
                '--memory', self.memory_limit,
                '--cpus', self.cpu_limit,
                '--network', 'none',  # No network access
                '--read-only',        # Read-only filesystem
                '--tmpfs', '/tmp',    # Writable tmp directory
                '-v', f'{script_path}:/script.ps1:ro',
                self.image,
                'pwsh', '-File', '/script.ps1'
            ]
            
            self.logger.debug(f"Executing Docker command: {' '.join(docker_cmd)}")
            
            # Execute with timeout
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            
            execution_time = time.time() - start_time
            
            # Clean up temporary file
            Path(script_path).unlink(missing_ok=True)
            
            return ExecutionResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                platform=Platform.LINUX,  # Docker containers are Linux-based
                sandbox_used=True
            )
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command execution timed out after {timeout} seconds")
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Command execution timed out after {timeout} seconds",
                execution_time=timeout,
                platform=Platform.LINUX,
                sandbox_used=True
            )
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Sandbox execution failed: {e}")
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=f"Sandbox execution failed: {str(e)}",
                execution_time=execution_time,
                platform=Platform.LINUX,
                sandbox_used=True
            )
    
    def _check_docker_availability(self) -> None:
        """Check if Docker is available and pull required image"""
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Docker is not running")
            
            # Check if image exists, pull if not
            result = subprocess.run(['docker', 'image', 'inspect', self.image],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                self.logger.info(f"Pulling Docker image: {self.image}")
                result = subprocess.run(['docker', 'pull', self.image],
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to pull Docker image: {self.image}")
            
            self.logger.info("Docker sandbox is ready")
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Docker not available: {e}")
            raise RuntimeError(f"Docker sandbox unavailable: {e}")