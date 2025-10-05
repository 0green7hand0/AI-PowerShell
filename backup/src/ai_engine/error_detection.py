"""Intelligent PowerShell Error Detection and Correction

This module provides advanced error detection and correction capabilities
for PowerShell commands, including syntax validation, parameter checking,
and intelligent correction suggestions.
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import ErrorSuggestion


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of PowerShell errors"""
    SYNTAX = "syntax"
    PARAMETER = "parameter"
    CMDLET = "cmdlet"
    MODULE = "module"
    LOGIC = "logic"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class PowerShellCmdlet:
    """Represents a PowerShell cmdlet with its parameters"""
    name: str
    parameters: List[str]
    required_parameters: List[str] = None
    parameter_sets: List[List[str]] = None
    aliases: List[str] = None
    module: str = None
    
    def __post_init__(self):
        if self.required_parameters is None:
            self.required_parameters = []
        if self.parameter_sets is None:
            self.parameter_sets = []
        if self.aliases is None:
            self.aliases = []


class PowerShellErrorDetector:
    """Advanced PowerShell error detection and correction engine"""
    
    def __init__(self):
        self.cmdlets = self._load_cmdlet_definitions()
        self.common_typos = self._load_common_typos()
        self.syntax_patterns = self._load_syntax_patterns()
        self.security_patterns = self._load_security_patterns()
    
    def _load_cmdlet_definitions(self) -> Dict[str, PowerShellCmdlet]:
        """Load PowerShell cmdlet definitions"""
        cmdlets = {}
        
        # Core cmdlets with their parameters
        cmdlet_definitions = [
            PowerShellCmdlet(
                name="Get-Process",
                parameters=["Name", "Id", "ProcessName", "ComputerName", "Module", "FileVersionInfo"],
                aliases=["gps", "ps"]
            ),
            PowerShellCmdlet(
                name="Stop-Process",
                parameters=["Name", "Id", "ProcessName", "Force", "PassThru", "WhatIf", "Confirm"],
                required_parameters=["Name", "Id"],
                aliases=["spps", "kill"]
            ),
            PowerShellCmdlet(
                name="Start-Process",
                parameters=["FilePath", "ArgumentList", "WorkingDirectory", "Credential", "WindowStyle", "Wait", "PassThru"],
                required_parameters=["FilePath"],
                aliases=["saps", "start"]
            ),
            PowerShellCmdlet(
                name="Get-Service",
                parameters=["Name", "DisplayName", "Status", "ComputerName", "DependentServices", "RequiredServices"],
                aliases=["gsv"]
            ),
            PowerShellCmdlet(
                name="Start-Service",
                parameters=["Name", "DisplayName", "PassThru", "WhatIf", "Confirm"],
                required_parameters=["Name"],
                aliases=["sasv"]
            ),
            PowerShellCmdlet(
                name="Stop-Service",
                parameters=["Name", "DisplayName", "Force", "PassThru", "WhatIf", "Confirm"],
                required_parameters=["Name"],
                aliases=["spsv"]
            ),
            PowerShellCmdlet(
                name="Get-ChildItem",
                parameters=["Path", "Filter", "Include", "Exclude", "Recurse", "Depth", "Force", "Name", "Attributes"],
                aliases=["gci", "ls", "dir"]
            ),
            PowerShellCmdlet(
                name="Copy-Item",
                parameters=["Path", "Destination", "Container", "Force", "Filter", "Include", "Exclude", "Recurse", "PassThru"],
                required_parameters=["Path", "Destination"],
                aliases=["cpi", "cp", "copy"]
            ),
            PowerShellCmdlet(
                name="Move-Item",
                parameters=["Path", "Destination", "Force", "Filter", "Include", "Exclude", "PassThru"],
                required_parameters=["Path", "Destination"],
                aliases=["mi", "mv", "move"]
            ),
            PowerShellCmdlet(
                name="Remove-Item",
                parameters=["Path", "Filter", "Include", "Exclude", "Recurse", "Force", "WhatIf", "Confirm"],
                required_parameters=["Path"],
                aliases=["ri", "rm", "rmdir", "del", "erase", "rd"]
            ),
            PowerShellCmdlet(
                name="Set-Location",
                parameters=["Path", "LiteralPath", "PassThru", "StackName"],
                aliases=["sl", "cd", "chdir"]
            ),
            PowerShellCmdlet(
                name="Get-Location",
                parameters=["PSProvider", "PSDrive", "StackName"],
                aliases=["gl", "pwd"]
            ),
            PowerShellCmdlet(
                name="New-Item",
                parameters=["Path", "ItemType", "Value", "Force", "Name"],
                required_parameters=["Path"],
                aliases=["ni"]
            ),
            PowerShellCmdlet(
                name="Get-Content",
                parameters=["Path", "ReadCount", "TotalCount", "Tail", "Filter", "Include", "Exclude", "Force", "Credential", "Raw"],
                required_parameters=["Path"],
                aliases=["gc", "cat", "type"]
            ),
            PowerShellCmdlet(
                name="Set-Content",
                parameters=["Path", "Value", "PassThru", "Filter", "Include", "Exclude", "Force", "Credential", "WhatIf", "Confirm"],
                required_parameters=["Path", "Value"],
                aliases=["sc"]
            ),
            PowerShellCmdlet(
                name="Out-File",
                parameters=["FilePath", "Encoding", "Append", "Force", "NoClobber", "Width", "InputObject"],
                required_parameters=["FilePath"]
            ),
            PowerShellCmdlet(
                name="Where-Object",
                parameters=["FilterScript", "Property", "Value", "EQ", "NE", "GT", "GE", "LT", "LE", "Like", "NotLike", "Match", "NotMatch", "Contains", "NotContains", "In", "NotIn"],
                aliases=["where", "?"]
            ),
            PowerShellCmdlet(
                name="Select-Object",
                parameters=["Property", "ExcludeProperty", "ExpandProperty", "First", "Last", "Skip", "SkipLast", "Unique", "Wait", "Index"],
                aliases=["select"]
            ),
            PowerShellCmdlet(
                name="Sort-Object",
                parameters=["Property", "Descending", "Unique", "InputObject", "Culture", "CaseSensitive"],
                aliases=["sort"]
            ),
            PowerShellCmdlet(
                name="Format-Table",
                parameters=["Property", "AutoSize", "RepeatHeader", "HideTableHeaders", "Wrap", "GroupBy"],
                aliases=["ft"]
            ),
            PowerShellCmdlet(
                name="Format-List",
                parameters=["Property", "GroupBy", "View", "ShowError", "DisplayError", "Force", "Expand"],
                aliases=["fl"]
            ),
            PowerShellCmdlet(
                name="Get-Help",
                parameters=["Name", "Path", "Category", "Component", "Functionality", "Role", "Full", "Detailed", "Examples", "Parameter", "Online", "ShowWindow"],
                aliases=["help", "man"]
            ),
            PowerShellCmdlet(
                name="Get-Command",
                parameters=["Name", "Verb", "Noun", "Module", "FullyQualifiedModule", "TotalCount", "Syntax", "ShowCommandInfo", "All", "ListImported", "ParameterName", "ParameterType", "CommandType"],
                aliases=["gcm"]
            )
        ]
        
        # Build cmdlet lookup dictionary
        for cmdlet in cmdlet_definitions:
            cmdlets[cmdlet.name.lower()] = cmdlet
            # Add aliases
            for alias in cmdlet.aliases:
                cmdlets[alias.lower()] = cmdlet
        
        return cmdlets
    
    def _load_common_typos(self) -> Dict[str, str]:
        """Load common PowerShell command typos and their corrections"""
        return {
            # Common cmdlet misspellings
            "get-proces": "Get-Process",
            "get-proccess": "Get-Process",
            "get-prcess": "Get-Process",
            "getprocess": "Get-Process",
            "get-servic": "Get-Service",
            "get-service": "Get-Service",
            "getservice": "Get-Service",
            "get-childitem": "Get-ChildItem",
            "get-childitems": "Get-ChildItem",
            "getchilditem": "Get-ChildItem",
            "copy-item": "Copy-Item",
            "copyitem": "Copy-Item",
            "move-item": "Move-Item",
            "moveitem": "Move-Item",
            "remove-item": "Remove-Item",
            "removeitem": "Remove-Item",
            "set-location": "Set-Location",
            "setlocation": "Set-Location",
            "get-location": "Get-Location",
            "getlocation": "Get-Location",
            "new-item": "New-Item",
            "newitem": "New-Item",
            "get-content": "Get-Content",
            "getcontent": "Get-Content",
            "set-content": "Set-Content",
            "setcontent": "Set-Content",
            "out-file": "Out-File",
            "outfile": "Out-File",
            "where-object": "Where-Object",
            "whereobject": "Where-Object",
            "select-object": "Select-Object",
            "selectobject": "Select-Object",
            "sort-object": "Sort-Object",
            "sortobject": "Sort-Object",
            "format-table": "Format-Table",
            "formattable": "Format-Table",
            "format-list": "Format-List",
            "formatlist": "Format-List",
            "get-help": "Get-Help",
            "gethelp": "Get-Help",
            "get-command": "Get-Command",
            "getcommand": "Get-Command",
            
            # Common parameter misspellings
            "-recurse": "-Recurse",
            "-force": "-Force",
            "-whatif": "-WhatIf",
            "-confirm": "-Confirm",
            "-passthru": "-PassThru",
            "-computername": "-ComputerName",
            "-filepath": "-FilePath",
            "-workingdirectory": "-WorkingDirectory",
            "-argumentlist": "-ArgumentList",
            "-displayname": "-DisplayName",
            "-includeusername": "-IncludeUserName",
            
            # Common operator misspellings
            "-eq": "-eq",
            "-ne": "-ne",
            "-gt": "-gt",
            "-ge": "-ge",
            "-lt": "-lt",
            "-le": "-le",
            "-like": "-like",
            "-notlike": "-notlike",
            "-match": "-match",
            "-notmatch": "-notmatch",
            "-contains": "-contains",
            "-notcontains": "-notcontains"
        }
    
    def _load_syntax_patterns(self) -> List[Tuple[str, str, str]]:
        """Load syntax error patterns (pattern, description, suggestion)"""
        return [
            # Bracket mismatches
            (r'\{[^}]*$', "Unclosed curly brace", "Add closing brace '}'"),
            (r'\([^)]*$', "Unclosed parenthesis", "Add closing parenthesis ')'"),
            (r'\[[^\]]*$', "Unclosed square bracket", "Add closing bracket ']'"),
            (r'^[^{]*\}', "Unmatched closing brace", "Add opening brace '{' or remove closing brace"),
            (r'^[^(]*\)', "Unmatched closing parenthesis", "Add opening parenthesis '(' or remove closing parenthesis"),
            (r'^[^\[]*\]', "Unmatched closing bracket", "Add opening bracket '[' or remove closing bracket"),
            
            # Quote mismatches
            (r'"[^"]*$', "Unclosed double quote", "Add closing double quote"),
            (r"'[^']*$", "Unclosed single quote", "Add closing single quote"),
            
            # Parameter syntax errors
            (r'-\w+\s+-\w+', "Missing parameter value", "Add value between parameters"),
            (r'-\w+\s*$', "Parameter without value", "Add value after parameter"),
            (r'--\w+', "Double dash parameter", "Use single dash for PowerShell parameters"),
            
            # Pipeline errors
            (r'\|\s*$', "Incomplete pipeline", "Add command after pipe"),
            (r'^\s*\|', "Pipeline starts with pipe", "Add command before pipe"),
            (r'\|\s*\|', "Empty pipeline stage", "Add command between pipes"),
            
            # Variable syntax errors
            (r'\$\s+\w+', "Space after dollar sign", "Remove space: $variableName"),
            (r'\$\d+\w+', "Invalid variable name", "Variable names cannot start with numbers"),
            
            # Cmdlet format errors
            (r'^[a-z]+-[a-z]+', "Lowercase cmdlet", "Use PascalCase: Verb-Noun"),
            (r'^\w+\s+\w+', "Space in cmdlet name", "Use hyphen: Verb-Noun"),
            
            # Common logic errors
            (r'Get-\w+.*\|\s*Remove-Item', "Dangerous pipeline", "Be careful piping Get commands to Remove-Item"),
            (r'Remove-Item.*-Recurse.*-Force', "Destructive command", "Double-check before using -Recurse -Force"),
        ]
    
    def _load_security_patterns(self) -> List[Tuple[str, str, str]]:
        """Load security-related error patterns"""
        return [
            (r'Invoke-Expression.*\$', "Code injection risk", "Avoid Invoke-Expression with user input"),
            (r'iex.*\$', "Code injection risk", "Avoid iex (Invoke-Expression) with variables"),
            (r'Remove-Item.*\*.*-Recurse', "Mass deletion", "Be very careful with wildcards and -Recurse"),
            (r'Format.*C:', "Disk formatting", "This command could format your disk!"),
            (r'Stop-Computer|Restart-Computer', "System shutdown", "This will shut down/restart the computer"),
            (r'Remove-Item.*-Path\s+[C-Z]:\\', "System file deletion", "Deleting system files can break Windows"),
        ]
    
    def detect_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect errors in PowerShell command
        
        Args:
            command: PowerShell command to analyze
            
        Returns:
            List of detected errors with suggestions
        """
        errors = []
        
        # Basic validation
        if not command or not command.strip():
            errors.append(ErrorSuggestion(
                error_type=ErrorType.SYNTAX.value,
                description="Empty command",
                suggested_fix="Enter a PowerShell command",
                confidence=1.0
            ))
            return errors
        
        # Syntax error detection
        errors.extend(self._detect_syntax_errors(command))
        
        # Cmdlet validation
        errors.extend(self._detect_cmdlet_errors(command))
        
        # Parameter validation
        errors.extend(self._detect_parameter_errors(command))
        
        # Logic error detection
        errors.extend(self._detect_logic_errors(command))
        
        # Security issue detection
        errors.extend(self._detect_security_issues(command))
        
        # Performance issue detection
        errors.extend(self._detect_performance_issues(command))
        
        return errors
    
    def _detect_syntax_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect syntax errors using pattern matching"""
        errors = []
        
        for pattern, description, suggestion in self.syntax_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.SYNTAX.value,
                    description=description,
                    suggested_fix=suggestion,
                    confidence=0.8
                ))
        
        return errors
    
    def _detect_cmdlet_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect cmdlet-related errors"""
        errors = []
        
        # Extract potential cmdlets from command
        cmdlet_pattern = r'\b([A-Za-z]+-[A-Za-z]+)\b'
        potential_cmdlets = re.findall(cmdlet_pattern, command)
        
        for cmdlet in potential_cmdlets:
            cmdlet_lower = cmdlet.lower()
            
            # Check if cmdlet exists
            if cmdlet_lower not in self.cmdlets:
                # Check for typos
                suggestion = self._find_cmdlet_suggestion(cmdlet)
                if suggestion:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.CMDLET.value,
                        description=f"Unknown cmdlet '{cmdlet}'",
                        suggested_fix=f"Did you mean '{suggestion}'?",
                        confidence=0.7
                    ))
                else:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.CMDLET.value,
                        description=f"Unknown cmdlet '{cmdlet}'",
                        suggested_fix="Check spelling or use Get-Command to find available cmdlets",
                        confidence=0.6
                    ))
            else:
                # Cmdlet exists, check for case issues
                correct_cmdlet = self.cmdlets[cmdlet_lower].name
                if cmdlet != correct_cmdlet:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.CMDLET.value,
                        description=f"Incorrect cmdlet case '{cmdlet}'",
                        suggested_fix=f"Use correct case: '{correct_cmdlet}'",
                        confidence=0.9
                    ))
        
        return errors
    
    def _detect_parameter_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect parameter-related errors"""
        errors = []
        
        # Extract cmdlet and its parameters
        cmdlet_match = re.match(r'\s*([A-Za-z]+-[A-Za-z]+)', command)
        if not cmdlet_match:
            return errors
        
        cmdlet_name = cmdlet_match.group(1).lower()
        if cmdlet_name not in self.cmdlets:
            return errors
        
        cmdlet_def = self.cmdlets[cmdlet_name]
        
        # Extract parameters from command
        param_pattern = r'-([A-Za-z]+)(?:\s+([^-\s][^\s]*(?:\s+[^-\s][^\s]*)*?))?'
        used_params = re.findall(param_pattern, command)
        
        # Check parameter validity
        for param_name, param_value in used_params:
            param_name_proper = None
            
            # Find matching parameter (case-insensitive)
            for valid_param in cmdlet_def.parameters:
                if param_name.lower() == valid_param.lower():
                    param_name_proper = valid_param
                    break
            
            if not param_name_proper:
                # Parameter not found, suggest similar ones
                suggestion = self._find_parameter_suggestion(param_name, cmdlet_def.parameters)
                if suggestion:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.PARAMETER.value,
                        description=f"Unknown parameter '-{param_name}' for {cmdlet_def.name}",
                        suggested_fix=f"Did you mean '-{suggestion}'?",
                        confidence=0.7
                    ))
                else:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.PARAMETER.value,
                        description=f"Unknown parameter '-{param_name}' for {cmdlet_def.name}",
                        suggested_fix=f"Use Get-Help {cmdlet_def.name} to see valid parameters",
                        confidence=0.6
                    ))
            else:
                # Parameter exists, check case
                if param_name != param_name_proper:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.PARAMETER.value,
                        description=f"Incorrect parameter case '-{param_name}'",
                        suggested_fix=f"Use correct case: '-{param_name_proper}'",
                        confidence=0.8
                    ))
                
                # Check if parameter has value when needed
                if not param_value and param_name_proper in cmdlet_def.required_parameters:
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.PARAMETER.value,
                        description=f"Required parameter '-{param_name_proper}' missing value",
                        suggested_fix=f"Add value after '-{param_name_proper}'",
                        confidence=0.9
                    ))
        
        # Check for missing required parameters
        used_param_names = {param[0].lower() for param in used_params}
        for required_param in cmdlet_def.required_parameters:
            if required_param.lower() not in used_param_names:
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.PARAMETER.value,
                    description=f"Missing required parameter '-{required_param}'",
                    suggested_fix=f"Add '-{required_param} <value>' to the command",
                    confidence=0.8
                ))
        
        return errors
    
    def _detect_logic_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect logical errors in command structure"""
        errors = []
        
        # Check for common logic issues
        
        # Piping Get-* to Remove-Item without filtering
        if re.search(r'Get-\w+.*\|\s*Remove-Item', command, re.IGNORECASE):
            if not re.search(r'Where-Object|\?|Select-Object', command, re.IGNORECASE):
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.LOGIC.value,
                    description="Piping Get command directly to Remove-Item",
                    suggested_fix="Add Where-Object to filter results before removing",
                    confidence=0.7
                ))
        
        # Using Select-Object after Sort-Object without specifying properties
        if re.search(r'Sort-Object.*\|\s*Select-Object\s+-First', command, re.IGNORECASE):
            if not re.search(r'Sort-Object\s+\w+', command, re.IGNORECASE):
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.LOGIC.value,
                    description="Sorting without specifying property",
                    suggested_fix="Specify property to sort by: Sort-Object PropertyName",
                    confidence=0.6
                ))
        
        # Using -Force without -WhatIf on destructive operations
        destructive_cmdlets = ['Remove-Item', 'Stop-Process', 'Stop-Service']
        for cmdlet in destructive_cmdlets:
            if re.search(rf'{cmdlet}.*-Force', command, re.IGNORECASE):
                if not re.search(r'-WhatIf', command, re.IGNORECASE):
                    errors.append(ErrorSuggestion(
                        error_type=ErrorType.LOGIC.value,
                        description=f"Using -Force with {cmdlet} without -WhatIf",
                        suggested_fix="Consider adding -WhatIf to preview changes",
                        confidence=0.5
                    ))
        
        return errors
    
    def _detect_security_issues(self, command: str) -> List[ErrorSuggestion]:
        """Detect security-related issues"""
        errors = []
        
        for pattern, description, suggestion in self.security_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.SECURITY.value,
                    description=description,
                    suggested_fix=suggestion,
                    confidence=0.9
                ))
        
        return errors
    
    def _detect_performance_issues(self, command: str) -> List[ErrorSuggestion]:
        """Detect potential performance issues"""
        errors = []
        
        # Using Get-ChildItem -Recurse on large directories without filtering
        if re.search(r'Get-ChildItem.*-Recurse', command, re.IGNORECASE):
            if not re.search(r'-Filter|-Include|-Exclude', command, re.IGNORECASE):
                errors.append(ErrorSuggestion(
                    error_type=ErrorType.PERFORMANCE.value,
                    description="Recursive directory listing without filtering",
                    suggested_fix="Consider using -Filter, -Include, or -Exclude to limit results",
                    confidence=0.6
                ))
        
        # Using Where-Object in pipeline when Select-Object could be more efficient
        if re.search(r'Get-\w+.*\|\s*Where-Object.*\|\s*Select-Object', command, re.IGNORECASE):
            errors.append(ErrorSuggestion(
                error_type=ErrorType.PERFORMANCE.value,
                description="Filtering after selection in pipeline",
                suggested_fix="Consider filtering before selecting for better performance",
                confidence=0.4
            ))
        
        return errors
    
    def _find_cmdlet_suggestion(self, cmdlet: str) -> Optional[str]:
        """Find suggestion for misspelled cmdlet"""
        cmdlet_lower = cmdlet.lower()
        
        # Check direct typo corrections
        if cmdlet_lower in self.common_typos:
            return self.common_typos[cmdlet_lower]
        
        # Find similar cmdlets using edit distance
        best_match = None
        best_distance = float('inf')
        
        for known_cmdlet_key, cmdlet_obj in self.cmdlets.items():
            distance = self._levenshtein_distance(cmdlet_lower, known_cmdlet_key)
            if distance < best_distance and distance <= 2:  # Allow up to 2 character differences
                best_distance = distance
                best_match = cmdlet_obj.name
        
        return best_match
    
    def _find_parameter_suggestion(self, param: str, valid_params: List[str]) -> Optional[str]:
        """Find suggestion for misspelled parameter"""
        param_lower = param.lower()
        
        # Find similar parameters using edit distance
        best_match = None
        best_distance = float('inf')
        
        for valid_param in valid_params:
            distance = self._levenshtein_distance(param_lower, valid_param.lower())
            if distance < best_distance and distance <= 2:  # Allow up to 2 character differences
                best_distance = distance
                best_match = valid_param
        
        return best_match
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def suggest_corrections(self, command: str, errors: List[ErrorSuggestion]) -> List[str]:
        """Generate corrected versions of the command
        
        Args:
            command: Original command with errors
            errors: List of detected errors
            
        Returns:
            List of corrected command suggestions
        """
        corrections = []
        
        # Start with original command
        corrected_command = command
        
        # Apply corrections based on error types
        for error in errors:
            if error.error_type == ErrorType.CMDLET.value:
                corrected_command = self._apply_cmdlet_correction(corrected_command, error)
            elif error.error_type == ErrorType.PARAMETER.value:
                corrected_command = self._apply_parameter_correction(corrected_command, error)
            elif error.error_type == ErrorType.SYNTAX.value:
                corrected_command = self._apply_syntax_correction(corrected_command, error)
        
        if corrected_command != command:
            corrections.append(corrected_command)
        
        # Generate alternative corrections
        corrections.extend(self._generate_alternative_corrections(command, errors))
        
        # Remove duplicates and limit to 3
        unique_corrections = []
        for correction in corrections:
            if correction not in unique_corrections:
                unique_corrections.append(correction)
        
        return unique_corrections[:3]
    
    def _apply_cmdlet_correction(self, command: str, error: ErrorSuggestion) -> str:
        """Apply cmdlet correction to command"""
        # Extract suggestion from error message
        if "Did you mean" in error.suggested_fix:
            suggestion_match = re.search(r"'([^']+)'", error.suggested_fix)
            if suggestion_match:
                suggested_cmdlet = suggestion_match.group(1)
                # Replace first cmdlet in command
                cmdlet_pattern = r'\b([A-Za-z]+-[A-Za-z]+)\b'
                return re.sub(cmdlet_pattern, suggested_cmdlet, command, count=1)
        
        return command
    
    def _apply_parameter_correction(self, command: str, error: ErrorSuggestion) -> str:
        """Apply parameter correction to command"""
        # Extract suggestion from error message
        if "Did you mean" in error.suggested_fix:
            suggestion_match = re.search(r"'-([^']+)'", error.suggested_fix)
            if suggestion_match:
                suggested_param = suggestion_match.group(1)
                # Find and replace the incorrect parameter
                param_pattern = r'-\w+'
                # This is a simplified replacement - in practice, you'd want more sophisticated logic
                return re.sub(param_pattern, f'-{suggested_param}', command, count=1)
        
        return command
    
    def _apply_syntax_correction(self, command: str, error: ErrorSuggestion) -> str:
        """Apply syntax correction to command"""
        # Handle common syntax fixes
        if "Add closing brace" in error.suggested_fix:
            return command + "}"
        elif "Add closing parenthesis" in error.suggested_fix:
            return command + ")"
        elif "Add closing bracket" in error.suggested_fix:
            return command + "]"
        elif "Add closing double quote" in error.suggested_fix:
            return command + '"'
        elif "Add closing single quote" in error.suggested_fix:
            return command + "'"
        
        return command
    
    def _generate_alternative_corrections(self, command: str, errors: List[ErrorSuggestion]) -> List[str]:
        """Generate alternative correction approaches"""
        alternatives = []
        
        # If there are cmdlet errors, suggest using Get-Help
        cmdlet_errors = [e for e in errors if e.error_type == ErrorType.CMDLET.value]
        if cmdlet_errors:
            alternatives.append("Get-Help")
            alternatives.append("Get-Command")
        
        # If there are parameter errors, suggest using Get-Help with the cmdlet
        param_errors = [e for e in errors if e.error_type == ErrorType.PARAMETER.value]
        if param_errors:
            cmdlet_match = re.match(r'\s*([A-Za-z]+-[A-Za-z]+)', command)
            if cmdlet_match:
                cmdlet_name = cmdlet_match.group(1)
                alternatives.append(f"Get-Help {cmdlet_name} -Parameter *")
        
        return alternatives
    
    def get_cmdlet_info(self, cmdlet_name: str) -> Optional[PowerShellCmdlet]:
        """Get information about a specific cmdlet"""
        return self.cmdlets.get(cmdlet_name.lower())
    
    def validate_command_structure(self, command: str) -> Dict[str, any]:
        """Validate overall command structure and provide analysis"""
        analysis = {
            'is_valid': True,
            'cmdlet_count': 0,
            'pipeline_stages': 0,
            'parameter_count': 0,
            'has_variables': False,
            'has_loops': False,
            'complexity_score': 0
        }
        
        # Count cmdlets
        cmdlet_pattern = r'\b([A-Za-z]+-[A-Za-z]+)\b'
        cmdlets = re.findall(cmdlet_pattern, command)
        analysis['cmdlet_count'] = len(cmdlets)
        
        # Count pipeline stages
        analysis['pipeline_stages'] = command.count('|') + 1
        
        # Count parameters
        param_pattern = r'-[A-Za-z]+'
        parameters = re.findall(param_pattern, command)
        analysis['parameter_count'] = len(parameters)
        
        # Check for variables
        analysis['has_variables'] = bool(re.search(r'\$\w+', command))
        
        # Check for loops
        analysis['has_loops'] = bool(re.search(r'\b(foreach|for|while)\b', command, re.IGNORECASE))
        
        # Calculate complexity score
        complexity = 0
        complexity += analysis['cmdlet_count'] * 0.1
        complexity += (analysis['pipeline_stages'] - 1) * 0.2
        complexity += analysis['parameter_count'] * 0.05
        if analysis['has_variables']:
            complexity += 0.1
        if analysis['has_loops']:
            complexity += 0.3
        
        analysis['complexity_score'] = complexity
        
        return analysis