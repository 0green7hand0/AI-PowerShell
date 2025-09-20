"""Natural Language to PowerShell Command Translation

This module provides enhanced command generation with confidence scoring,
context-aware suggestions, and command explanation features.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import CommandSuggestion, CommandContext, Platform, UserRole


logger = logging.getLogger(__name__)


@dataclass
class CommandPattern:
    """Represents a command pattern for translation"""
    keywords: List[str]
    template: str
    confidence_base: float
    platform_specific: Dict[Platform, str] = None
    role_requirements: List[UserRole] = None
    description: str = ""


class PowerShellTranslator:
    """Enhanced PowerShell command translator with context awareness"""
    
    def __init__(self):
        self.command_patterns = self._load_command_patterns()
        self.context_modifiers = self._load_context_modifiers()
        self.confidence_adjusters = self._load_confidence_adjusters()
    
    def _load_command_patterns(self) -> List[CommandPattern]:
        """Load predefined command patterns for translation"""
        return [
            # Process management - more specific patterns first
            CommandPattern(
                keywords=["processes", "process", "running"],
                template="Get-Process",
                confidence_base=0.9,
                description="Lists running processes"
            ),
            CommandPattern(
                keywords=["kill", "stop", "terminate", "process"],
                template="Stop-Process -Name '{target}'",
                confidence_base=0.8,
                role_requirements=[UserRole.ADMIN],
                description="Stops a running process"
            ),
            CommandPattern(
                keywords=["start", "run", "launch", "execute"],
                template="Start-Process '{target}'",
                confidence_base=0.8,
                description="Starts a new process"
            ),
            
            # Service management
            CommandPattern(
                keywords=["services", "service", "daemon"],
                template="Get-Service",
                confidence_base=0.9,
                description="Lists system services"
            ),
            CommandPattern(
                keywords=["start", "service"],
                template="Start-Service -Name '{target}'",
                confidence_base=0.8,
                role_requirements=[UserRole.ADMIN],
                description="Starts a system service"
            ),
            CommandPattern(
                keywords=["stop", "service"],
                template="Stop-Service -Name '{target}'",
                confidence_base=0.8,
                role_requirements=[UserRole.ADMIN],
                description="Stops a system service"
            ),
            
            # File system operations
            CommandPattern(
                keywords=["files", "folders", "directory", "dir"],
                template="Get-ChildItem",
                confidence_base=0.9,
                platform_specific={
                    Platform.WINDOWS: "Get-ChildItem",
                    Platform.LINUX: "Get-ChildItem",
                    Platform.MACOS: "Get-ChildItem"
                },
                description="Lists files and folders"
            ),
            CommandPattern(
                keywords=["find", "search", "locate"],
                template="Get-ChildItem -Recurse -Filter '*{target}*'",
                confidence_base=0.8,
                description="Searches for files and folders"
            ),
            CommandPattern(
                keywords=["copy", "cp"],
                template="Copy-Item '{source}' '{destination}'",
                confidence_base=0.7,
                description="Copies files or folders"
            ),
            CommandPattern(
                keywords=["move", "mv", "rename"],
                template="Move-Item '{source}' '{destination}'",
                confidence_base=0.7,
                description="Moves or renames files or folders"
            ),
            CommandPattern(
                keywords=["delete", "remove", "rm"],
                template="Remove-Item '{target}'",
                confidence_base=0.6,
                role_requirements=[UserRole.ADMIN],
                description="Deletes files or folders"
            ),
            
            # System information
            CommandPattern(
                keywords=["system", "info", "information", "computer"],
                template="Get-ComputerInfo",
                confidence_base=0.8,
                description="Gets system information"
            ),
            CommandPattern(
                keywords=["disk", "space", "storage"],
                template="Get-PSDrive",
                confidence_base=0.8,
                description="Shows disk space information"
            ),
            CommandPattern(
                keywords=["memory", "ram", "usage"],
                template="Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10",
                confidence_base=0.7,
                description="Shows memory usage by processes"
            ),
            CommandPattern(
                keywords=["cpu", "processor", "performance"],
                template="Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
                confidence_base=0.7,
                description="Shows CPU usage by processes"
            ),
            
            # Network operations
            CommandPattern(
                keywords=["network", "connections", "netstat"],
                template="Get-NetTCPConnection",
                confidence_base=0.8,
                platform_specific={
                    Platform.WINDOWS: "Get-NetTCPConnection",
                    Platform.LINUX: "Get-NetTCPConnection",
                    Platform.MACOS: "Get-NetTCPConnection"
                },
                description="Shows network connections"
            ),
            CommandPattern(
                keywords=["ping", "test", "connectivity"],
                template="Test-NetConnection '{target}'",
                confidence_base=0.8,
                description="Tests network connectivity"
            ),
            
            # Event logs
            CommandPattern(
                keywords=["logs", "events", "eventlog"],
                template="Get-EventLog -LogName System -Newest 10",
                confidence_base=0.8,
                platform_specific={
                    Platform.WINDOWS: "Get-EventLog -LogName System -Newest 10",
                    Platform.LINUX: "Get-WinEvent -MaxEvents 10",
                    Platform.MACOS: "Get-WinEvent -MaxEvents 10"
                },
                description="Shows recent system events"
            ),
            
            # PowerShell help and discovery
            CommandPattern(
                keywords=["help", "manual", "documentation"],
                template="Get-Help {target}",
                confidence_base=0.9,
                description="Shows help for PowerShell commands"
            ),
            CommandPattern(
                keywords=["commands", "cmdlets", "available"],
                template="Get-Command",
                confidence_base=0.9,
                description="Lists available PowerShell commands"
            ),
            CommandPattern(
                keywords=["modules", "import"],
                template="Get-Module -ListAvailable",
                confidence_base=0.8,
                description="Lists available PowerShell modules"
            )
        ]
    
    def _load_context_modifiers(self) -> Dict[str, str]:
        """Load context-based command modifiers"""
        return {
            "recursive": " -Recurse",
            "force": " -Force",
            "verbose": " -Verbose",
            "whatif": " -WhatIf",
            "confirm": " -Confirm",
            "all": " -All",
            "detailed": " | Format-List",
            "table": " | Format-Table",
            "sort": " | Sort-Object",
            "filter": " | Where-Object",
            "select": " | Select-Object",
            "first": " | Select-Object -First",
            "last": " | Select-Object -Last",
            "unique": " | Sort-Object -Unique"
        }
    
    def _load_confidence_adjusters(self) -> Dict[str, float]:
        """Load confidence adjustment factors"""
        return {
            "exact_match": 0.3,
            "partial_match": 0.1,
            "context_match": 0.2,
            "platform_specific": 0.1,
            "role_appropriate": 0.1,
            "recent_usage": 0.15,
            "parameter_complete": 0.1,
            "safe_operation": 0.05,
            "risky_operation": -0.2,
            "missing_parameters": -0.3,
            "platform_mismatch": -0.2
        }
    
    def translate_with_context(self, input_text: str, context: CommandContext) -> CommandSuggestion:
        """Translate natural language to PowerShell with context awareness
        
        Args:
            input_text: Natural language description
            context: Current execution context
            
        Returns:
            CommandSuggestion with generated command and metadata
        """
        # Normalize input
        normalized_input = self._normalize_input(input_text)
        
        # Find matching patterns
        pattern_matches = self._find_pattern_matches(normalized_input, context)
        
        if not pattern_matches:
            return self._create_fallback_suggestion(input_text)
        
        # Select best pattern
        best_pattern, confidence, extracted_params = pattern_matches[0]
        
        # Generate command from pattern
        command = self._generate_command_from_pattern(
            best_pattern, extracted_params, context
        )
        
        # Apply context modifiers
        command = self._apply_context_modifiers(command, normalized_input, context)
        
        # Calculate final confidence
        final_confidence = self._calculate_final_confidence(
            confidence, command, context, input_text
        )
        
        # Generate explanation
        explanation = self._generate_detailed_explanation(
            best_pattern, command, input_text, context
        )
        
        # Generate alternatives
        alternatives = self._generate_context_alternatives(
            pattern_matches[1:3], extracted_params, context
        )
        
        return CommandSuggestion(
            original_input=input_text,
            generated_command=command,
            confidence_score=final_confidence,
            explanation=explanation,
            alternatives=alternatives
        )
    
    def _normalize_input(self, input_text: str) -> str:
        """Normalize input text for pattern matching"""
        # Convert to lowercase
        normalized = input_text.lower().strip()
        
        # Remove common filler words
        filler_words = ["please", "can", "you", "i", "want", "to", "need", "would", "like"]
        words = normalized.split()
        filtered_words = [w for w in words if w not in filler_words]
        
        return " ".join(filtered_words)
    
    def _find_pattern_matches(self, normalized_input: str, context: CommandContext) -> List[Tuple[CommandPattern, float, Dict[str, str]]]:
        """Find matching command patterns with confidence scores"""
        matches = []
        input_words = set(normalized_input.split())
        
        for pattern in self.command_patterns:
            # Calculate keyword match score
            pattern_keywords = set(pattern.keywords)
            matched_keywords = input_words.intersection(pattern_keywords)
            
            if not matched_keywords:
                continue
            
            # Base confidence from pattern
            confidence = pattern.confidence_base
            
            # Adjust for keyword match quality
            match_ratio = len(matched_keywords) / len(pattern_keywords)
            confidence += match_ratio * self.confidence_adjusters["exact_match"]
            
            # Boost confidence for more specific matches
            # If input contains multiple keywords from the pattern, it's more specific
            if len(matched_keywords) > 1:
                confidence += 0.2
            
            # Boost confidence for exact template matches
            if pattern.template.lower().replace("-", "").replace(" ", "") in normalized_input.replace("-", "").replace(" ", ""):
                confidence += 0.3
            
            # Check role requirements
            if pattern.role_requirements and context.user_role not in pattern.role_requirements:
                confidence += self.confidence_adjusters["role_appropriate"]
            
            # Check platform compatibility
            if pattern.platform_specific and context.platform in pattern.platform_specific:
                confidence += self.confidence_adjusters["platform_specific"]
            
            # Extract parameters from input
            extracted_params = self._extract_parameters(normalized_input, pattern)
            
            # Adjust confidence based on parameter completeness
            if "{target}" in pattern.template and "target" not in extracted_params:
                confidence += self.confidence_adjusters["missing_parameters"]
            elif extracted_params:
                confidence += self.confidence_adjusters["parameter_complete"]
            
            matches.append((pattern, confidence, extracted_params))
        
        # Sort by confidence (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _extract_parameters(self, input_text: str, pattern: CommandPattern) -> Dict[str, str]:
        """Extract parameters from input text based on pattern"""
        params = {}
        words = input_text.split()
        
        # Simple parameter extraction based on common patterns
        if "{target}" in pattern.template:
            # Look for quoted strings first
            quoted_match = re.search(r'["\']([^"\']+)["\']', input_text)
            if quoted_match:
                params["target"] = quoted_match.group(1)
            else:
                # Look for likely target words (nouns, file names, etc.)
                target_candidates = []
                for word in words:
                    if (word not in pattern.keywords and 
                        not word in ["the", "a", "an", "with", "for", "in", "on", "at"] and
                        len(word) > 2):
                        target_candidates.append(word)
                
                if target_candidates:
                    params["target"] = target_candidates[0]
        
        # Extract source and destination for copy/move operations
        if "{source}" in pattern.template and "{destination}" in pattern.template:
            # Look for "from X to Y" or "X to Y" patterns
            from_to_match = re.search(r'(?:from\s+)?([^\s]+)\s+to\s+([^\s]+)', input_text)
            if from_to_match:
                params["source"] = from_to_match.group(1)
                params["destination"] = from_to_match.group(2)
            else:
                # Look for two file-like arguments
                file_pattern = r'([a-zA-Z0-9_.-]+\.[a-zA-Z0-9]+)'
                file_matches = re.findall(file_pattern, input_text)
                if len(file_matches) >= 2:
                    params["source"] = file_matches[0]
                    params["destination"] = file_matches[1]
        
        return params
    
    def _generate_command_from_pattern(self, pattern: CommandPattern, params: Dict[str, str], context: CommandContext) -> str:
        """Generate command from pattern and parameters"""
        # Use platform-specific template if available
        if pattern.platform_specific and context.platform in pattern.platform_specific:
            template = pattern.platform_specific[context.platform]
        else:
            template = pattern.template
        
        # Replace parameters in template
        command = template
        for param_name, param_value in params.items():
            placeholder = f"{{{param_name}}}"
            if placeholder in command:
                command = command.replace(placeholder, param_value)
        
        # Remove unfilled placeholders
        command = re.sub(r'\s*\{[^}]+\}', '', command)
        
        return command.strip()
    
    def _apply_context_modifiers(self, command: str, input_text: str, context: CommandContext) -> str:
        """Apply context-based modifiers to the command"""
        modified_command = command
        
        # Apply modifiers based on input keywords
        for modifier_keyword, modifier_text in self.context_modifiers.items():
            if modifier_keyword in input_text:
                if modifier_keyword in ["first", "last"]:
                    # Extract number if present
                    number_match = re.search(rf'{modifier_keyword}\s+(\d+)', input_text)
                    if number_match:
                        number = number_match.group(1)
                        modified_command += f" | Select-Object -{modifier_keyword.title()} {number}"
                    else:
                        modified_command += modifier_text + " 10"  # Default to 10
                else:
                    modified_command += modifier_text
        
        # Context-aware modifications
        if context.user_role == UserRole.USER and any(risky in command.lower() for risky in ["remove", "delete", "stop"]):
            if "-WhatIf" not in modified_command:
                modified_command += " -WhatIf"
        
        return modified_command
    
    def _calculate_final_confidence(self, base_confidence: float, command: str, context: CommandContext, original_input: str) -> float:
        """Calculate final confidence score with additional factors"""
        confidence = base_confidence
        
        # Adjust for command safety
        risky_operations = ["remove-item", "stop-process", "stop-service", "format"]
        if any(risky in command.lower() for risky in risky_operations):
            confidence += self.confidence_adjusters["risky_operation"]
        else:
            confidence += self.confidence_adjusters["safe_operation"]
        
        # Adjust for recent usage (if command appears in recent history)
        if context.recent_commands:
            command_base = command.split()[0].lower() if command.split() else ""
            for recent_cmd in context.recent_commands:
                if command_base in recent_cmd.lower():
                    confidence += self.confidence_adjusters["recent_usage"]
                    break
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, confidence))
    
    def _generate_detailed_explanation(self, pattern: CommandPattern, command: str, original_input: str, context: CommandContext) -> str:
        """Generate detailed explanation for the command"""
        explanation_parts = [
            f"Generated PowerShell command for: '{original_input}'"
        ]
        
        if pattern.description:
            explanation_parts.append(f"Purpose: {pattern.description}")
        
        # Add parameter explanations
        if " -" in command:
            explanation_parts.append("Parameters used:")
            parameters = re.findall(r'-(\w+)', command)
            for param in parameters:
                param_explanations = {
                    "Name": "Specifies the name of the target",
                    "Path": "Specifies the file or folder path",
                    "Recurse": "Includes subdirectories in the operation",
                    "Force": "Forces the operation without confirmation",
                    "WhatIf": "Shows what would happen without executing",
                    "Verbose": "Provides detailed output",
                    "All": "Includes all items"
                }
                if param in param_explanations:
                    explanation_parts.append(f"  -{param}: {param_explanations[param]}")
        
        # Add safety warnings for risky operations
        risky_operations = ["Remove-Item", "Stop-Process", "Stop-Service"]
        if any(risky in command for risky in risky_operations):
            explanation_parts.append("⚠️  Warning: This operation can affect system stability. Use with caution.")
        
        # Add platform-specific notes
        if context.platform != Platform.WINDOWS:
            explanation_parts.append(f"Note: Command adapted for {context.platform.value} platform")
        
        return "\n".join(explanation_parts)
    
    def _generate_context_alternatives(self, pattern_matches: List[Tuple[CommandPattern, float, Dict[str, str]]], params: Dict[str, str], context: CommandContext) -> List[str]:
        """Generate alternative commands based on context"""
        alternatives = []
        
        # Generate alternatives from other matching patterns
        for pattern, confidence, extracted_params in pattern_matches:
            if confidence > 0.3:  # Only include reasonably confident alternatives
                alt_command = self._generate_command_from_pattern(pattern, extracted_params, context)
                if alt_command and alt_command not in alternatives:
                    alternatives.append(alt_command)
        
        # If no alternatives from patterns, add some generic ones
        if not alternatives:
            alternatives.extend(["Get-Help", "Get-Command"])
        
        # Add common variations based on the primary command
        if pattern_matches:
            primary_pattern = pattern_matches[0][0] if pattern_matches else None
            if primary_pattern:
                primary_command = self._generate_command_from_pattern(primary_pattern, params, context)
                
                # Add help variation
                if primary_command and not primary_command.startswith("Get-Help"):
                    cmd_name = primary_command.split()[0]
                    help_cmd = f"Get-Help {cmd_name}"
                    if help_cmd not in alternatives:
                        alternatives.append(help_cmd)
                
                # Add whatif variation for potentially destructive commands
                risky_operations = ["Remove-Item", "Stop-Process", "Stop-Service"]
                if any(risky in primary_command for risky in risky_operations):
                    if "-WhatIf" not in primary_command:
                        whatif_cmd = primary_command + " -WhatIf"
                        if whatif_cmd not in alternatives:
                            alternatives.append(whatif_cmd)
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _create_fallback_suggestion(self, input_text: str) -> CommandSuggestion:
        """Create fallback suggestion when no patterns match"""
        return CommandSuggestion(
            original_input=input_text,
            generated_command="Get-Help",
            confidence_score=0.1,
            explanation=f"No specific PowerShell command found for '{input_text}'. Try 'Get-Help' to explore available commands.",
            alternatives=["Get-Command", "Get-Command *keyword*", "Get-Module -ListAvailable"]
        )
    
    def get_command_suggestions_by_category(self, category: str) -> List[str]:
        """Get command suggestions by category"""
        category_commands = {
            "process": ["Get-Process", "Start-Process", "Stop-Process"],
            "service": ["Get-Service", "Start-Service", "Stop-Service"],
            "file": ["Get-ChildItem", "Copy-Item", "Move-Item", "Remove-Item"],
            "system": ["Get-ComputerInfo", "Get-PSDrive", "Get-EventLog"],
            "network": ["Get-NetTCPConnection", "Test-NetConnection"],
            "help": ["Get-Help", "Get-Command", "Get-Module"]
        }
        
        return category_commands.get(category.lower(), [])
    
    def analyze_command_complexity(self, command: str) -> Dict[str, Any]:
        """Analyze command complexity and provide insights"""
        analysis = {
            "complexity_score": 0,
            "parameter_count": 0,
            "pipeline_stages": 0,
            "risk_level": "low",
            "estimated_execution_time": "fast"
        }
        
        # Count parameters
        parameters = re.findall(r'-\w+', command)
        analysis["parameter_count"] = len(parameters)
        analysis["complexity_score"] += len(parameters) * 0.1
        
        # Count pipeline stages
        pipeline_stages = command.count('|') + 1
        analysis["pipeline_stages"] = pipeline_stages
        analysis["complexity_score"] += (pipeline_stages - 1) * 0.2
        
        # Assess risk level
        risky_operations = ["remove", "delete", "stop", "kill", "format"]
        if any(risky in command.lower() for risky in risky_operations):
            analysis["risk_level"] = "high"
            analysis["complexity_score"] += 0.3
        elif any(moderate in command.lower() for moderate in ["start", "restart", "move"]):
            analysis["risk_level"] = "medium"
            analysis["complexity_score"] += 0.1
        
        # Estimate execution time
        slow_operations = ["get-childitem -recurse", "get-process", "get-eventlog"]
        if any(slow in command.lower() for slow in slow_operations):
            analysis["estimated_execution_time"] = "slow"
            analysis["complexity_score"] += 0.2
        elif pipeline_stages > 2:
            analysis["estimated_execution_time"] = "medium"
            analysis["complexity_score"] += 0.1
        
        return analysis