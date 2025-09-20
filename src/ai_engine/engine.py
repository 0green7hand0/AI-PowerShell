"""AI 引擎自然语言处理实现

本模块提供主要的 AIEngine 类，集成多个本地 AI 框架
用于 PowerShell 命令生成和错误检测。
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import re

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import (
    AIEngineInterface, CommandSuggestion, CommandContext, ErrorSuggestion,
    ExecutionResult, Platform, UserRole
)
from config.models import ModelConfig
from .providers import AIProviderInterface, LlamaCppProvider, OllamaProvider, FallbackProvider
from .translation import PowerShellTranslator
from .error_detection import PowerShellErrorDetector


logger = logging.getLogger(__name__)


class AIEngine(AIEngineInterface):
    """用于自然语言处理和命令生成的主要 AI 引擎
    
    集成多种本地 AI 模型提供商，支持：
    - 自然语言到 PowerShell 命令的转换
    - 命令错误检测和修复建议
    - 上下文学习和历史记录
    """
    
    def __init__(self, config: ModelConfig):
        """使用配置初始化 AI 引擎
        
        Args:
            config: 模型配置设置
        """
        self.config = config
        self.provider: Optional[AIProviderInterface] = None
        self.fallback_provider = FallbackProvider()
        self.translator = PowerShellTranslator()
        self.error_detector = PowerShellErrorDetector()
        self.context_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize the AI provider
        self._initialize_provider()
    
    def _initialize_provider(self) -> None:
        """Initialize the appropriate AI provider based on configuration"""
        try:
            if self.config.model_type.lower() == "llama-cpp":
                self.provider = LlamaCppProvider(self.config)
            elif self.config.model_type.lower() == "ollama":
                self.provider = OllamaProvider(self.config)
            else:
                logger.warning(f"Unknown model type: {self.config.model_type}, using fallback")
                self.provider = self.fallback_provider
            
            # Test provider initialization
            if not self.provider.is_available():
                logger.warning("Primary AI provider not available, using fallback")
                self.provider = self.fallback_provider
            else:
                logger.info(f"AI provider initialized: {self.config.model_type}")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI provider: {e}")
            self.provider = self.fallback_provider
    
    def translate_natural_language(self, input_text: str, context: CommandContext) -> CommandSuggestion:
        """Convert natural language to PowerShell command
        
        Args:
            input_text: Natural language description of desired action
            context: Current execution context
            
        Returns:
            CommandSuggestion with generated command and metadata
        """
        start_time = time.time()
        
        try:
            # First try enhanced pattern-based translation
            enhanced_suggestion = self.translator.translate_with_context(input_text, context)
            
            # If confidence is high enough, use enhanced suggestion
            if enhanced_suggestion.confidence_score >= 0.6:
                self._update_context_history(context.session_id, input_text, enhanced_suggestion)
                processing_time = time.time() - start_time
                logger.info(f"Enhanced translation completed in {processing_time:.2f}s with confidence {enhanced_suggestion.confidence_score}")
                return enhanced_suggestion
            
            # Otherwise, try AI provider if available
            if self.provider and self.provider != self.fallback_provider:
                # Build context-aware prompt
                prompt = self._build_translation_prompt(input_text, context)
                
                # Generate command using AI provider
                response = self.provider.generate_command(prompt, context)
                
                # Parse and validate response
                ai_suggestion = self._parse_command_response(response, input_text)
                
                # Combine AI suggestion with enhanced translation insights
                combined_suggestion = self._combine_suggestions(enhanced_suggestion, ai_suggestion, input_text)
                
                # Update context history
                self._update_context_history(context.session_id, input_text, combined_suggestion)
                
                processing_time = time.time() - start_time
                logger.info(f"Combined AI+Enhanced translation completed in {processing_time:.2f}s with confidence {combined_suggestion.confidence_score}")
                
                return combined_suggestion
            else:
                # Use enhanced suggestion as fallback
                self._update_context_history(context.session_id, input_text, enhanced_suggestion)
                processing_time = time.time() - start_time
                logger.info(f"Enhanced translation (fallback) completed in {processing_time:.2f}s with confidence {enhanced_suggestion.confidence_score}")
                return enhanced_suggestion
            
        except Exception as e:
            logger.error(f"Error in natural language translation: {e}")
            # Return fallback suggestion
            return self._create_fallback_suggestion(input_text, context)
    
    def detect_command_errors(self, command: str) -> List[ErrorSuggestion]:
        """Detect errors in PowerShell commands
        
        Args:
            command: PowerShell command to analyze
            
        Returns:
            List of detected errors and suggestions
        """
        errors = []
        
        try:
            # Use enhanced error detector
            enhanced_errors = self.error_detector.detect_errors(command)
            errors.extend(enhanced_errors)
            
            # Use AI provider for additional error detection if available
            if self.provider and self.provider != self.fallback_provider:
                try:
                    ai_errors = self.provider.detect_errors(command)
                    errors.extend(ai_errors)
                except Exception as e:
                    logger.debug(f"AI provider error detection failed: {e}")
            
            # Add legacy rule-based error detection as fallback
            legacy_errors = self._detect_syntax_errors(command)
            errors.extend(legacy_errors)
            
            # Remove duplicates
            unique_errors = self._deduplicate_errors(errors)
            
            logger.debug(f"Detected {len(unique_errors)} errors in command: {command[:50]}...")
            return unique_errors
            
        except Exception as e:
            logger.error(f"Error in command error detection: {e}")
            return []
    
    def suggest_corrections(self, command: str, error: str) -> List[str]:
        """Suggest corrections for command errors
        
        Args:
            command: Original command with errors
            error: Error message or description
            
        Returns:
            List of suggested corrections
        """
        try:
            # First detect errors to get structured error information
            detected_errors = self.detect_command_errors(command)
            
            # Use enhanced error detector for corrections
            enhanced_corrections = self.error_detector.suggest_corrections(command, detected_errors)
            if enhanced_corrections:
                return enhanced_corrections
            
            # Use AI provider for intelligent corrections if available
            if self.provider and self.provider != self.fallback_provider:
                try:
                    ai_corrections = self.provider.suggest_corrections(command, error)
                    if ai_corrections:
                        return ai_corrections
                except Exception as e:
                    logger.debug(f"AI provider correction failed: {e}")
            
            # Fallback to legacy rule-based corrections
            return self._generate_rule_based_corrections(command, error)
            
        except Exception as e:
            logger.error(f"Error generating corrections: {e}")
            return []
    
    def update_context(self, command: str, result: ExecutionResult) -> None:
        """Update AI context with execution results
        
        Args:
            command: Executed command
            result: Execution result
        """
        try:
            # Update provider context if supported
            if hasattr(self.provider, 'update_context'):
                self.provider.update_context(command, result)
            
            # Update local context history
            if result.correlation_id:
                session_id = getattr(result, 'session_id', result.correlation_id)
                self._update_execution_history(session_id, command, result)
            
            logger.debug(f"Updated context for command: {command[:50]}...")
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
    
    def _build_translation_prompt(self, input_text: str, context: CommandContext) -> str:
        """Build context-aware prompt for command generation"""
        prompt_parts = [
            "Convert the following natural language request to a PowerShell command.",
            f"Request: {input_text}",
            "",
            "Context:",
            f"- Current directory: {context.current_directory}",
            f"- Platform: {context.platform.value}",
            f"- User role: {context.user_role.value}",
        ]
        
        if context.recent_commands:
            prompt_parts.extend([
                "- Recent commands:",
                *[f"  {cmd}" for cmd in context.recent_commands[-3:]]
            ])
        
        if context.active_modules:
            prompt_parts.append(f"- Available modules: {', '.join(context.active_modules)}")
        
        prompt_parts.extend([
            "",
            "Generate a PowerShell command that:",
            "1. Accomplishes the requested task",
            "2. Is appropriate for the current platform and context",
            "3. Follows PowerShell best practices",
            "4. Is safe to execute",
            "",
            "Respond with only the PowerShell command, no explanations."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_command_response(self, response: str, original_input: str) -> CommandSuggestion:
        """Parse AI provider response into CommandSuggestion"""
        # Clean up response
        command = response.strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = ["PowerShell command:", "Command:", "PS>", ">"]
        for prefix in prefixes_to_remove:
            if command.startswith(prefix):
                command = command[len(prefix):].strip()
        
        # Extract command from code blocks if present
        code_block_match = re.search(r'```(?:powershell|ps1)?\s*\n?(.*?)\n?```', command, re.DOTALL)
        if code_block_match:
            command = code_block_match.group(1).strip()
        
        # Calculate confidence score based on command characteristics
        confidence = self._calculate_confidence(command, original_input)
        
        # Generate explanation
        explanation = self._generate_explanation(command, original_input)
        
        # Generate alternatives
        alternatives = self._generate_alternatives(command, original_input)
        
        return CommandSuggestion(
            original_input=original_input,
            generated_command=command,
            confidence_score=confidence,
            explanation=explanation,
            alternatives=alternatives
        )
    
    def _calculate_confidence(self, command: str, original_input: str) -> float:
        """Calculate confidence score for generated command"""
        confidence = 0.5  # Base confidence
        
        # Check if command looks like valid PowerShell
        if re.match(r'^[A-Z][a-z]+-[A-Z][a-z]+', command):
            confidence += 0.2
        
        # Check for common PowerShell patterns
        powershell_patterns = [
            r'Get-\w+', r'Set-\w+', r'New-\w+', r'Remove-\w+',
            r'\|\s*\w+', r'-\w+\s+\w+', r'\$\w+'
        ]
        
        for pattern in powershell_patterns:
            if re.search(pattern, command):
                confidence += 0.1
        
        # Penalize for suspicious patterns
        suspicious_patterns = [
            r'rm\s+-rf', r'del\s+/s', r'format\s+c:', r'shutdown'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                confidence -= 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_explanation(self, command: str, original_input: str) -> str:
        """Generate explanation for the command"""
        # Simple explanation based on command structure
        if command.startswith('Get-'):
            return f"Retrieves information based on your request: '{original_input}'"
        elif command.startswith('Set-'):
            return f"Configures or modifies settings as requested: '{original_input}'"
        elif command.startswith('New-'):
            return f"Creates new items as requested: '{original_input}'"
        elif command.startswith('Remove-'):
            return f"Removes items as requested: '{original_input}'"
        else:
            return f"Executes PowerShell command for: '{original_input}'"
    
    def _generate_alternatives(self, command: str, original_input: str) -> List[str]:
        """Generate alternative commands"""
        alternatives = []
        
        # Generate variations based on common patterns
        if 'Get-Process' in command:
            alternatives.extend([
                "Get-Process | Sort-Object CPU -Descending",
                "Get-Process | Where-Object {$_.CPU -gt 10}",
                "Get-Process | Select-Object Name, CPU, Memory"
            ])
        elif 'Get-Service' in command:
            alternatives.extend([
                "Get-Service | Where-Object {$_.Status -eq 'Running'}",
                "Get-Service | Sort-Object Status",
                "Get-Service | Select-Object Name, Status, StartType"
            ])
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _create_fallback_suggestion(self, input_text: str, context: CommandContext) -> CommandSuggestion:
        """Create fallback suggestion when AI processing fails"""
        return CommandSuggestion(
            original_input=input_text,
            generated_command="# AI processing unavailable - please enter PowerShell command manually",
            confidence_score=0.0,
            explanation="AI model is currently unavailable. Please enter your PowerShell command directly.",
            alternatives=["Get-Help", "Get-Command", "Get-Member"]
        )
    
    def _detect_syntax_errors(self, command: str) -> List[ErrorSuggestion]:
        """Rule-based syntax error detection"""
        errors = []
        
        # Check for common syntax issues
        if command.count('(') != command.count(')'):
            errors.append(ErrorSuggestion(
                error_type="syntax",
                description="Mismatched parentheses",
                suggested_fix="Check that all opening parentheses have matching closing parentheses",
                confidence=0.9
            ))
        
        if command.count('{') != command.count('}'):
            errors.append(ErrorSuggestion(
                error_type="syntax",
                description="Mismatched braces",
                suggested_fix="Check that all opening braces have matching closing braces",
                confidence=0.9
            ))
        
        # Check for invalid parameter syntax
        invalid_param_pattern = r'-\w+\s*-\w+'
        if re.search(invalid_param_pattern, command):
            errors.append(ErrorSuggestion(
                error_type="parameter",
                description="Invalid parameter syntax",
                suggested_fix="Parameters should have values between them, not be consecutive",
                confidence=0.8
            ))
        
        return errors
    
    def _generate_rule_based_corrections(self, command: str, error: str) -> List[str]:
        """Generate rule-based corrections for common errors"""
        corrections = []
        
        # Common cmdlet misspellings
        misspelling_map = {
            'get-proces': 'Get-Process',
            'get-servic': 'Get-Service',
            'set-locatio': 'Set-Location',
            'get-childite': 'Get-ChildItem'
        }
        
        for misspelling, correction in misspelling_map.items():
            if misspelling in command.lower():
                corrected = command.replace(misspelling, correction)
                corrections.append(corrected)
        
        # Parameter corrections
        if '-Path' not in command and 'path' in error.lower():
            corrections.append(command + ' -Path "."')
        
        return corrections
    
    def _deduplicate_errors(self, errors: List[ErrorSuggestion]) -> List[ErrorSuggestion]:
        """Remove duplicate error suggestions"""
        seen = set()
        unique_errors = []
        
        for error in errors:
            key = (error.error_type, error.description)
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)
        
        return unique_errors
    
    def _update_context_history(self, session_id: str, input_text: str, suggestion: CommandSuggestion) -> None:
        """Update context history for learning"""
        if session_id not in self.context_history:
            self.context_history[session_id] = []
        
        entry = {
            'timestamp': time.time(),
            'input': input_text,
            'command': suggestion.generated_command,
            'confidence': suggestion.confidence_score
        }
        
        self.context_history[session_id].append(entry)
        
        # Keep only recent history (last 100 entries)
        if len(self.context_history[session_id]) > 100:
            self.context_history[session_id] = self.context_history[session_id][-100:]
    
    def _update_execution_history(self, session_id: str, command: str, result: ExecutionResult) -> None:
        """Update execution history for learning"""
        # This would integrate with the storage system in a full implementation
        if session_id not in self.context_history:
            self.context_history[session_id] = []
        
        entry = {
            'timestamp': time.time(),
            'command': command,
            'success': result.success,
            'execution_time': result.execution_time
        }
        
        self.context_history[session_id].append(entry)
        logger.debug(f"Execution result for session {session_id}: success={result.success}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current AI provider"""
        if self.provider:
            return {
                'type': self.provider.__class__.__name__,
                'available': self.provider.is_available(),
                'model_path': getattr(self.config, 'model_path', 'N/A'),
                'model_type': self.config.model_type
            }
        return {'type': 'None', 'available': False}
    
    def reload_provider(self) -> bool:
        """Reload the AI provider (useful for model updates)"""
        try:
            self._initialize_provider()
            return self.provider is not None and self.provider.is_available()
        except Exception as e:
            logger.error(f"Failed to reload provider: {e}")
            return False
    
    def _combine_suggestions(self, enhanced_suggestion: CommandSuggestion, ai_suggestion: CommandSuggestion, original_input: str) -> CommandSuggestion:
        """Combine enhanced pattern-based and AI-generated suggestions"""
        # Choose the suggestion with higher confidence
        if ai_suggestion.confidence_score > enhanced_suggestion.confidence_score:
            primary_suggestion = ai_suggestion
            secondary_suggestion = enhanced_suggestion
        else:
            primary_suggestion = enhanced_suggestion
            secondary_suggestion = ai_suggestion
        
        # Combine alternatives
        combined_alternatives = []
        combined_alternatives.extend(primary_suggestion.alternatives)
        
        # Add secondary suggestion as alternative if different
        if secondary_suggestion.generated_command != primary_suggestion.generated_command:
            combined_alternatives.insert(0, secondary_suggestion.generated_command)
        
        # Add unique alternatives from secondary suggestion
        for alt in secondary_suggestion.alternatives:
            if alt not in combined_alternatives:
                combined_alternatives.append(alt)
        
        # Limit to 3 alternatives
        combined_alternatives = combined_alternatives[:3]
        
        # Combine explanations
        combined_explanation = primary_suggestion.explanation
        if secondary_suggestion.explanation and secondary_suggestion.explanation != primary_suggestion.explanation:
            combined_explanation += f"\n\nAlternative approach: {secondary_suggestion.explanation}"
        
        return CommandSuggestion(
            original_input=original_input,
            generated_command=primary_suggestion.generated_command,
            confidence_score=primary_suggestion.confidence_score,
            explanation=combined_explanation,
            alternatives=combined_alternatives
        )
    
    def get_command_analysis(self, command: str) -> Dict[str, Any]:
        """Get detailed analysis of a PowerShell command"""
        return self.translator.analyze_command_complexity(command)
    
    def get_suggestions_by_category(self, category: str) -> List[str]:
        """Get command suggestions by category"""
        return self.translator.get_command_suggestions_by_category(category)
    
    def validate_command_structure(self, command: str) -> Dict[str, Any]:
        """Validate PowerShell command structure"""
        return self.error_detector.validate_command_structure(command)
    
    def get_cmdlet_info(self, cmdlet_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a PowerShell cmdlet"""
        cmdlet_info = self.error_detector.get_cmdlet_info(cmdlet_name)
        if cmdlet_info:
            return {
                'name': cmdlet_info.name,
                'parameters': cmdlet_info.parameters,
                'required_parameters': cmdlet_info.required_parameters,
                'aliases': cmdlet_info.aliases,
                'module': cmdlet_info.module
            }
        return None
    
    def analyze_command_safety(self, command: str) -> Dict[str, Any]:
        """Analyze command for safety and security issues"""
        errors = self.detect_command_errors(command)
        security_errors = [e for e in errors if e.error_type == "security"]
        
        safety_analysis = {
            'is_safe': len(security_errors) == 0,
            'risk_level': 'low',
            'security_issues': [e.description for e in security_errors],
            'recommendations': [e.suggested_fix for e in security_errors]
        }
        
        # Determine risk level based on command content
        risky_patterns = ['Remove-Item', 'Stop-Process', 'Format', 'Invoke-Expression']
        if any(pattern in command for pattern in risky_patterns):
            safety_analysis['risk_level'] = 'high'
        elif any(pattern in command for pattern in ['Start-Service', 'Stop-Service', 'Restart']):
            safety_analysis['risk_level'] = 'medium'
        
        return safety_analysis