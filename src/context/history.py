"""Command history management and learning capabilities"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from collections import defaultdict, Counter
import threading

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.base import ExecutionResult, StorageInterface
from .models import (
    HistoryEntry, HistoryFilter, CommandPattern, UserPreferences
)


class CommandHistoryManager:
    """
    Manages command history storage, search, and learning capabilities.
    
    Responsibilities:
    - Store and retrieve command history with search and filtering
    - Implement pattern recognition for user command preferences
    - Create learning algorithms for personalized command suggestions
    - Provide analytics on command usage patterns
    """
    
    def __init__(self, storage: StorageInterface, config: Dict[str, Any] = None):
        self.storage = storage
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_history_entries = self.config.get('max_history_entries', 10000)
        self.pattern_min_occurrences = self.config.get('pattern_min_occurrences', 3)
        self.pattern_confidence_threshold = self.config.get('pattern_confidence_threshold', 0.7)
        self.learning_window_days = self.config.get('learning_window_days', 30)
        
        # In-memory caches
        self._pattern_cache: Dict[str, List[CommandPattern]] = {}
        self._history_cache: Dict[str, List[HistoryEntry]] = {}
        self._cache_lock = threading.RLock()
        
        # Pattern recognition components
        self._command_tokenizer = CommandTokenizer()
        self._pattern_matcher = PatternMatcher()
        self._suggestion_engine = SuggestionEngine()
    
    def add_history_entry(self, session_id: str, command: str, 
                         natural_language_input: Optional[str],
                         execution_result: ExecutionResult,
                         context_snapshot: Dict[str, Any] = None) -> str:
        """Add a new command to history and return entry ID"""
        import uuid
        
        entry = HistoryEntry(
            session_id=session_id,
            command=command,
            natural_language_input=natural_language_input,
            execution_result=execution_result,
            timestamp=datetime.utcnow(),
            context_snapshot=context_snapshot or {}
        )
        
        try:
            # Save to persistent storage
            self.storage.save_command_history(session_id, command, execution_result)
            
            # Update in-memory cache
            with self._cache_lock:
                if session_id not in self._history_cache:
                    self._history_cache[session_id] = []
                
                self._history_cache[session_id].append(entry)
                
                # Maintain cache size limit
                if len(self._history_cache[session_id]) > self.max_history_entries:
                    self._history_cache[session_id] = self._history_cache[session_id][-self.max_history_entries:]
            
            # Update patterns if this was a successful command
            if execution_result.success and natural_language_input:
                self._update_patterns(session_id, natural_language_input, command, entry)
            
            self.logger.debug(f"Added history entry for session {session_id}: {command[:50]}...")
            return entry.entry_id
            
        except Exception as e:
            self.logger.error(f"Failed to add history entry for session {session_id}: {e}")
            raise
    
    def get_history(self, filter_criteria: HistoryFilter) -> List[HistoryEntry]:
        """Retrieve command history with filtering and pagination"""
        try:
            # Try to get from cache first
            if filter_criteria.session_id:
                with self._cache_lock:
                    cached_entries = self._history_cache.get(filter_criteria.session_id, [])
                    if cached_entries:
                        return self._filter_entries(cached_entries, filter_criteria)
            
            # Fall back to storage
            storage_entries = self.storage.get_command_history(
                filter_criteria.session_id or "", 
                filter_criteria.limit
            )
            
            # Convert storage format to HistoryEntry objects
            entries = []
            for entry_data in storage_entries:
                if isinstance(entry_data, dict):
                    # Reconstruct HistoryEntry from storage data
                    entry = self._reconstruct_history_entry(entry_data)
                    if entry:
                        entries.append(entry)
            
            return self._filter_entries(entries, filter_criteria)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve history: {e}")
            return []
    
    def search_history(self, session_id: str, query: str, limit: int = 50) -> List[HistoryEntry]:
        """Search command history using text matching"""
        filter_criteria = HistoryFilter(
            session_id=session_id,
            command_pattern=query,
            limit=limit
        )
        return self.get_history(filter_criteria)
    
    def get_command_suggestions(self, session_id: str, natural_input: str, 
                               context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get personalized command suggestions based on history and patterns"""
        try:
            # Get learned patterns for this session
            patterns = self.get_learned_patterns(session_id)
            
            # Get recent successful commands
            recent_filter = HistoryFilter(
                session_id=session_id,
                success_only=True,
                limit=20,
                start_date=datetime.utcnow() - timedelta(days=7)
            )
            recent_history = self.get_history(recent_filter)
            
            # Generate suggestions using multiple strategies
            suggestions = []
            
            # Strategy 1: Pattern matching
            pattern_suggestions = self._get_pattern_suggestions(natural_input, patterns)
            suggestions.extend(pattern_suggestions)
            
            # Strategy 2: Similar command history
            history_suggestions = self._get_history_suggestions(natural_input, recent_history)
            suggestions.extend(history_suggestions)
            
            # Strategy 3: Frequency-based suggestions
            frequency_suggestions = self._get_frequency_suggestions(session_id, natural_input)
            suggestions.extend(frequency_suggestions)
            
            # Rank and deduplicate suggestions
            ranked_suggestions = self._rank_suggestions(suggestions, context)
            
            return ranked_suggestions[:10]  # Return top 10 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get command suggestions for session {session_id}: {e}")
            return []
    
    def get_learned_patterns(self, session_id: str) -> List[CommandPattern]:
        """Get learned command patterns for a session"""
        with self._cache_lock:
            if session_id in self._pattern_cache:
                return self._pattern_cache[session_id].copy()
        
        # Load patterns from storage or generate from history
        patterns = self._generate_patterns_from_history(session_id)
        
        with self._cache_lock:
            self._pattern_cache[session_id] = patterns
        
        return patterns
    
    def update_user_feedback(self, entry_id: str, feedback: str, rating: float) -> None:
        """Update user feedback for a history entry"""
        try:
            # Find the entry in cache
            with self._cache_lock:
                for session_entries in self._history_cache.values():
                    for entry in session_entries:
                        if hasattr(entry, 'entry_id') and entry.entry_id == entry_id:
                            entry.user_feedback = feedback
                            entry.success_rating = rating
                            
                            # Update patterns based on feedback
                            if rating > 0.7 and entry.natural_language_input:
                                self._reinforce_pattern(entry.session_id, 
                                                      entry.natural_language_input, 
                                                      entry.command, rating)
                            break
            
            self.logger.debug(f"Updated feedback for entry {entry_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update feedback for entry {entry_id}: {e}")
    
    def get_usage_analytics(self, session_id: str, days: int = 30) -> Dict[str, Any]:
        """Get command usage analytics for a session"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            filter_criteria = HistoryFilter(
                session_id=session_id,
                start_date=start_date,
                limit=1000
            )
            
            history = self.get_history(filter_criteria)
            
            if not history:
                return {}
            
            # Calculate analytics
            total_commands = len(history)
            successful_commands = sum(1 for entry in history if entry.execution_result.success)
            success_rate = successful_commands / total_commands if total_commands > 0 else 0
            
            # Command frequency analysis
            command_counter = Counter(entry.command for entry in history)
            most_used_commands = command_counter.most_common(10)
            
            # Time-based analysis
            commands_by_hour = defaultdict(int)
            for entry in history:
                hour = entry.timestamp.hour
                commands_by_hour[hour] += 1
            
            # Error analysis
            error_patterns = defaultdict(int)
            for entry in history:
                if not entry.execution_result.success and entry.execution_result.stderr:
                    # Extract error type from stderr
                    error_type = self._extract_error_type(entry.execution_result.stderr)
                    error_patterns[error_type] += 1
            
            return {
                'total_commands': total_commands,
                'successful_commands': successful_commands,
                'success_rate': success_rate,
                'most_used_commands': most_used_commands,
                'commands_by_hour': dict(commands_by_hour),
                'error_patterns': dict(error_patterns),
                'analysis_period_days': days,
                'first_command_date': min(entry.timestamp for entry in history).isoformat() if history else None,
                'last_command_date': max(entry.timestamp for entry in history).isoformat() if history else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics for session {session_id}: {e}")
            return {}
    
    def cleanup_old_history(self, session_id: str = None, days_to_keep: int = 90) -> int:
        """Clean up old history entries and return number of entries removed"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            removed_count = 0
            
            with self._cache_lock:
                if session_id:
                    # Clean specific session
                    if session_id in self._history_cache:
                        original_count = len(self._history_cache[session_id])
                        self._history_cache[session_id] = [
                            entry for entry in self._history_cache[session_id]
                            if entry.timestamp > cutoff_date
                        ]
                        removed_count = original_count - len(self._history_cache[session_id])
                else:
                    # Clean all sessions
                    for sid in list(self._history_cache.keys()):
                        original_count = len(self._history_cache[sid])
                        self._history_cache[sid] = [
                            entry for entry in self._history_cache[sid]
                            if entry.timestamp > cutoff_date
                        ]
                        removed_count += original_count - len(self._history_cache[sid])
            
            self.logger.info(f"Cleaned up {removed_count} old history entries")
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old history: {e}")
            return 0
    
    # Private helper methods
    
    def _filter_entries(self, entries: List[HistoryEntry], 
                       filter_criteria: HistoryFilter) -> List[HistoryEntry]:
        """Apply filtering criteria to history entries"""
        filtered = entries
        
        # Date filtering
        if filter_criteria.start_date:
            filtered = [e for e in filtered if e.timestamp >= filter_criteria.start_date]
        if filter_criteria.end_date:
            filtered = [e for e in filtered if e.timestamp <= filter_criteria.end_date]
        
        # Command pattern filtering
        if filter_criteria.command_pattern:
            pattern = re.compile(filter_criteria.command_pattern, re.IGNORECASE)
            filtered = [e for e in filtered if pattern.search(e.command)]
        
        # Success filtering
        if filter_criteria.success_only:
            filtered = [e for e in filtered if e.execution_result.success]
        
        # Sorting
        if filter_criteria.sort_by == "timestamp":
            filtered.sort(key=lambda e: e.timestamp, 
                         reverse=(filter_criteria.sort_order == "desc"))
        elif filter_criteria.sort_by == "command":
            filtered.sort(key=lambda e: e.command, 
                         reverse=(filter_criteria.sort_order == "desc"))
        elif filter_criteria.sort_by == "success":
            filtered.sort(key=lambda e: e.execution_result.success, 
                         reverse=(filter_criteria.sort_order == "desc"))
        
        # Pagination
        start_idx = filter_criteria.offset
        end_idx = start_idx + filter_criteria.limit
        return filtered[start_idx:end_idx]
    
    def _reconstruct_history_entry(self, entry_data: Dict[str, Any]) -> Optional[HistoryEntry]:
        """Reconstruct HistoryEntry from storage data"""
        try:
            # This is a simplified reconstruction - would need to match storage format
            return HistoryEntry(
                session_id=entry_data.get('session_id', ''),
                command=entry_data.get('command', ''),
                natural_language_input=entry_data.get('natural_language_input'),
                execution_result=entry_data.get('result'),  # Assuming ExecutionResult object
                timestamp=datetime.fromisoformat(entry_data.get('timestamp', datetime.utcnow().isoformat())),
                context_snapshot=entry_data.get('context_snapshot', {})
            )
        except Exception as e:
            self.logger.warning(f"Failed to reconstruct history entry: {e}")
            return None
    
    def _update_patterns(self, session_id: str, natural_input: str, 
                        command: str, entry: HistoryEntry) -> None:
        """Update learned patterns based on successful command execution"""
        try:
            # Tokenize natural language input
            nl_tokens = self._command_tokenizer.tokenize_natural_language(natural_input)
            cmd_tokens = self._command_tokenizer.tokenize_command(command)
            
            # Create or update pattern
            pattern_key = self._generate_pattern_key(nl_tokens)
            
            with self._cache_lock:
                if session_id not in self._pattern_cache:
                    self._pattern_cache[session_id] = []
                
                patterns = self._pattern_cache[session_id]
                
                # Find existing pattern or create new one
                existing_pattern = None
                for pattern in patterns:
                    if pattern.natural_language_pattern == pattern_key:
                        existing_pattern = pattern
                        break
                
                if existing_pattern:
                    # Update existing pattern
                    existing_pattern.usage_count += 1
                    existing_pattern.last_used = entry.timestamp
                    # Recalculate success rate and confidence
                    existing_pattern.success_rate = min(1.0, existing_pattern.success_rate + 0.1)
                    existing_pattern.confidence_score = min(1.0, existing_pattern.confidence_score + 0.05)
                else:
                    # Create new pattern
                    new_pattern = CommandPattern(
                        pattern_id=f"{session_id}_{len(patterns)}",
                        session_id=session_id,
                        natural_language_pattern=pattern_key,
                        command_template=self._generalize_command(command),
                        usage_count=1,
                        success_rate=1.0,
                        confidence_score=0.5,
                        created_at=entry.timestamp,
                        last_used=entry.timestamp
                    )
                    patterns.append(new_pattern)
            
        except Exception as e:
            self.logger.error(f"Failed to update patterns for session {session_id}: {e}")
    
    def _generate_patterns_from_history(self, session_id: str) -> List[CommandPattern]:
        """Generate command patterns from historical data"""
        try:
            # Get recent successful commands with natural language input
            filter_criteria = HistoryFilter(
                session_id=session_id,
                success_only=True,
                limit=500,
                start_date=datetime.utcnow() - timedelta(days=self.learning_window_days)
            )
            
            history = self.get_history(filter_criteria)
            
            # Group by natural language patterns
            pattern_groups = defaultdict(list)
            for entry in history:
                if entry.natural_language_input:
                    nl_tokens = self._command_tokenizer.tokenize_natural_language(entry.natural_language_input)
                    pattern_key = self._generate_pattern_key(nl_tokens)
                    pattern_groups[pattern_key].append(entry)
            
            # Create patterns from groups with sufficient occurrences
            patterns = []
            for pattern_key, entries in pattern_groups.items():
                if len(entries) >= self.pattern_min_occurrences:
                    # Calculate pattern statistics
                    usage_count = len(entries)
                    success_rate = sum(1 for e in entries if e.execution_result.success) / usage_count
                    
                    # Generate command template from most common command
                    commands = [entry.command for entry in entries]
                    most_common_command = Counter(commands).most_common(1)[0][0]
                    command_template = self._generalize_command(most_common_command)
                    
                    # Calculate confidence based on consistency and success rate
                    confidence = min(1.0, (success_rate * 0.7) + (usage_count / 20 * 0.3))
                    
                    if confidence >= self.pattern_confidence_threshold:
                        pattern = CommandPattern(
                            pattern_id=f"{session_id}_{len(patterns)}",
                            session_id=session_id,
                            natural_language_pattern=pattern_key,
                            command_template=command_template,
                            usage_count=usage_count,
                            success_rate=success_rate,
                            confidence_score=confidence,
                            created_at=min(e.timestamp for e in entries),
                            last_used=max(e.timestamp for e in entries)
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to generate patterns from history for session {session_id}: {e}")
            return []
    
    def _get_pattern_suggestions(self, natural_input: str, 
                               patterns: List[CommandPattern]) -> List[Dict[str, Any]]:
        """Get command suggestions based on learned patterns"""
        suggestions = []
        
        try:
            nl_tokens = self._command_tokenizer.tokenize_natural_language(natural_input)
            input_pattern = self._generate_pattern_key(nl_tokens)
            
            for pattern in patterns:
                similarity = self._pattern_matcher.calculate_similarity(input_pattern, 
                                                                      pattern.natural_language_pattern)
                if similarity > 0.6:  # Similarity threshold
                    suggestion = {
                        'command': pattern.command_template,
                        'confidence': pattern.confidence_score * similarity,
                        'source': 'pattern',
                        'usage_count': pattern.usage_count,
                        'success_rate': pattern.success_rate,
                        'explanation': f"Based on learned pattern (used {pattern.usage_count} times)"
                    }
                    suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"Failed to get pattern suggestions: {e}")
        
        return suggestions
    
    def _get_history_suggestions(self, natural_input: str, 
                               history: List[HistoryEntry]) -> List[Dict[str, Any]]:
        """Get suggestions based on similar historical commands"""
        suggestions = []
        
        try:
            for entry in history:
                if entry.natural_language_input:
                    similarity = self._calculate_text_similarity(natural_input, 
                                                               entry.natural_language_input)
                    if similarity > 0.5:  # Similarity threshold
                        suggestion = {
                            'command': entry.command,
                            'confidence': similarity * 0.8,  # Slightly lower confidence than patterns
                            'source': 'history',
                            'timestamp': entry.timestamp.isoformat(),
                            'success': entry.execution_result.success,
                            'explanation': f"Similar to previous command from {entry.timestamp.strftime('%Y-%m-%d')}"
                        }
                        suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"Failed to get history suggestions: {e}")
        
        return suggestions
    
    def _get_frequency_suggestions(self, session_id: str, 
                                 natural_input: str) -> List[Dict[str, Any]]:
        """Get suggestions based on command frequency"""
        suggestions = []
        
        try:
            # Get most frequently used commands
            filter_criteria = HistoryFilter(
                session_id=session_id,
                success_only=True,
                limit=100,
                start_date=datetime.utcnow() - timedelta(days=14)
            )
            
            recent_history = self.get_history(filter_criteria)
            command_counter = Counter(entry.command for entry in recent_history)
            
            # Suggest top commands if input contains relevant keywords
            nl_lower = natural_input.lower()
            for command, count in command_counter.most_common(5):
                # Simple keyword matching
                if any(word in command.lower() for word in nl_lower.split() if len(word) > 2):
                    suggestion = {
                        'command': command,
                        'confidence': min(0.6, count / 10),  # Lower confidence, frequency-based
                        'source': 'frequency',
                        'usage_count': count,
                        'explanation': f"Frequently used command ({count} times recently)"
                    }
                    suggestions.append(suggestion)
        
        except Exception as e:
            self.logger.error(f"Failed to get frequency suggestions: {e}")
        
        return suggestions
    
    def _rank_suggestions(self, suggestions: List[Dict[str, Any]], 
                         context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Rank and deduplicate suggestions"""
        # Remove duplicates based on command
        seen_commands = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            command = suggestion['command']
            if command not in seen_commands:
                seen_commands.add(command)
                unique_suggestions.append(suggestion)
        
        # Sort by confidence score
        unique_suggestions.sort(key=lambda s: s['confidence'], reverse=True)
        
        return unique_suggestions
    
    def _reinforce_pattern(self, session_id: str, natural_input: str, 
                          command: str, rating: float) -> None:
        """Reinforce a pattern based on positive user feedback"""
        try:
            with self._cache_lock:
                if session_id in self._pattern_cache:
                    patterns = self._pattern_cache[session_id]
                    nl_tokens = self._command_tokenizer.tokenize_natural_language(natural_input)
                    pattern_key = self._generate_pattern_key(nl_tokens)
                    
                    for pattern in patterns:
                        if pattern.natural_language_pattern == pattern_key:
                            # Boost confidence based on rating
                            confidence_boost = (rating - 0.5) * 0.1
                            pattern.confidence_score = min(1.0, pattern.confidence_score + confidence_boost)
                            pattern.success_rate = min(1.0, pattern.success_rate + confidence_boost * 0.5)
                            break
        
        except Exception as e:
            self.logger.error(f"Failed to reinforce pattern: {e}")
    
    def _generate_pattern_key(self, tokens: List[str]) -> str:
        """Generate a pattern key from tokenized natural language"""
        # More sophisticated pattern generation
        # Group similar verbs and normalize nouns to create semantic patterns
        
        # Verb synonyms - group similar action words
        verb_groups = {
            'display_action': {'show', 'list', 'display', 'get', 'view'},
            'search_action': {'find', 'search', 'locate'},
            'stop_action': {'stop', 'kill', 'terminate'},
            'start_action': {'start', 'run', 'launch', 'execute'}
        }
        
        # Noun normalizations
        noun_normalizations = {
            'processes': 'process',
            'services': 'service', 
            'files': 'file',
            'directories': 'directory',
            'folders': 'directory'
        }
        
        # Extract and normalize tokens
        normalized_tokens = []
        
        for token in tokens:
            # Normalize verbs to action groups
            verb_found = False
            for action_type, verbs in verb_groups.items():
                if token in verbs:
                    normalized_tokens.append(action_type)
                    verb_found = True
                    break
            
            if not verb_found:
                # Normalize nouns
                normalized_token = noun_normalizations.get(token, token)
                normalized_tokens.append(normalized_token)
        
        # Create pattern from normalized tokens
        return " ".join(sorted(set(normalized_tokens)))
    
    def _generalize_command(self, command: str) -> str:
        """Generalize a command by replacing specific values with placeholders"""
        # Simple generalization - replace numbers and paths with placeholders
        generalized = re.sub(r'\d+', '{number}', command)
        generalized = re.sub(r'[A-Za-z]:\\[^\s]+', '{path}', generalized)
        generalized = re.sub(r'/[^\s]+', '{path}', generalized)
        return generalized
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _extract_error_type(self, stderr: str) -> str:
        """Extract error type from stderr output"""
        # Simple error type extraction
        if "not recognized" in stderr.lower():
            return "command_not_found"
        elif "access denied" in stderr.lower():
            return "access_denied"
        elif "parameter" in stderr.lower():
            return "parameter_error"
        elif "syntax" in stderr.lower():
            return "syntax_error"
        else:
            return "unknown_error"


class CommandTokenizer:
    """Tokenizes natural language and PowerShell commands"""
    
    def tokenize_natural_language(self, text: str) -> List[str]:
        """Tokenize natural language input"""
        # Simple tokenization - could use more sophisticated NLP
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if word not in stop_words and len(word) > 2]
    
    def tokenize_command(self, command: str) -> List[str]:
        """Tokenize PowerShell command"""
        # Extract cmdlet names and important parameters
        tokens = []
        
        # Extract cmdlet names (Get-Process, Set-Location, etc.)
        cmdlets = re.findall(r'\b[A-Z][a-z]+-[A-Z][a-z]+\b', command)
        tokens.extend(cmdlets)
        
        # Extract parameter names
        params = re.findall(r'-\w+', command)
        tokens.extend(params)
        
        return tokens


class PatternMatcher:
    """Matches patterns between natural language inputs"""
    
    def calculate_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between two patterns"""
        words1 = set(pattern1.split())
        words2 = set(pattern2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


class SuggestionEngine:
    """Generates and ranks command suggestions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rank_suggestions(self, suggestions: List[Dict[str, Any]], 
                        context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Rank suggestions based on multiple factors"""
        # This could be expanded with more sophisticated ranking algorithms
        return sorted(suggestions, key=lambda s: s.get('confidence', 0), reverse=True)