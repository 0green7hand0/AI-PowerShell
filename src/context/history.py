"""
历史记录管理器

本模块实现命令历史记录管理功能，支持历史查询、搜索、过滤和统计分析。
提供丰富的历史记录操作接口，帮助用户快速查找和重用历史命令。
"""

from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .models import CommandEntry, Session, CommandStatus
from ..storage.interfaces import StorageInterface


logger = logging.getLogger(__name__)


class HistoryManager:
    """历史记录管理器
    
    负责管理命令历史记录，提供查询、搜索、过滤和统计功能。
    支持跨会话的历史记录管理和持久化。
    """
    
    def __init__(self, storage: Optional[StorageInterface] = None, max_history: int = 1000):
        """初始化历史记录管理器
        
        Args:
            storage: 存储接口实例
            max_history: 最大历史记录数量
        """
        self.storage = storage
        self.max_history = max_history
        self.history_cache: List[CommandEntry] = []
        
        # 加载历史记录
        self._load_history()
        
        logger.info(f"HistoryManager initialized with max_history={max_history}")
    
    # ========================================================================
    # 基础操作
    # ========================================================================
    
    def add_entry(self, entry: CommandEntry):
        """添加历史记录条目
        
        Args:
            entry: 命令条目对象
        """
        self.history_cache.append(entry)
        
        # 限制历史记录数量
        if len(self.history_cache) > self.max_history:
            self.history_cache = self.history_cache[-self.max_history:]
        
        logger.debug(f"Added history entry: {entry.command_id}")
        
        # 持久化
        if self.storage:
            self._save_history()
    
    def get_all(self, limit: Optional[int] = None) -> List[CommandEntry]:
        """获取所有历史记录
        
        Args:
            limit: 返回的最大记录数，None 表示返回所有
            
        Returns:
            List[CommandEntry]: 历史记录列表
        """
        if limit is None:
            return self.history_cache.copy()
        return self.history_cache[-limit:]
    
    def get_by_id(self, command_id: str) -> Optional[CommandEntry]:
        """根据 ID 获取历史记录
        
        Args:
            command_id: 命令 ID
            
        Returns:
            Optional[CommandEntry]: 命令条目对象
        """
        for entry in self.history_cache:
            if entry.command_id == command_id:
                return entry
        return None
    
    def clear(self):
        """清空历史记录"""
        self.history_cache.clear()
        logger.info("Cleared all history")
        
        if self.storage:
            self._save_history()
    
    def remove_entry(self, command_id: str) -> bool:
        """删除指定历史记录
        
        Args:
            command_id: 命令 ID
            
        Returns:
            bool: 删除是否成功
        """
        for i, entry in enumerate(self.history_cache):
            if entry.command_id == command_id:
                del self.history_cache[i]
                logger.debug(f"Removed history entry: {command_id}")
                
                if self.storage:
                    self._save_history()
                
                return True
        
        return False
    
    # ========================================================================
    # 查询和搜索
    # ========================================================================
    
    def search(self, query: str, search_in: str = "all") -> List[CommandEntry]:
        """搜索历史记录
        
        Args:
            query: 搜索关键词
            search_in: 搜索范围，可选值：'all', 'input', 'command', 'output'
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        query_lower = query.lower()
        results = []
        
        for entry in self.history_cache:
            match = False
            
            if search_in in ["all", "input"]:
                if query_lower in entry.user_input.lower():
                    match = True
            
            if search_in in ["all", "command"]:
                if query_lower in entry.translated_command.lower():
                    match = True
            
            if search_in in ["all", "output"]:
                if query_lower in entry.output.lower():
                    match = True
            
            if match:
                results.append(entry)
        
        logger.debug(f"Search '{query}' found {len(results)} results")
        return results
    
    def filter_by_status(self, status: CommandStatus) -> List[CommandEntry]:
        """按状态过滤历史记录
        
        Args:
            status: 命令状态
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        return [entry for entry in self.history_cache if entry.status == status]
    
    def filter_by_date_range(self, start_date: datetime, 
                            end_date: Optional[datetime] = None) -> List[CommandEntry]:
        """按日期范围过滤历史记录
        
        Args:
            start_date: 开始日期
            end_date: 结束日期，None 表示到现在
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        if end_date is None:
            end_date = datetime.now()
        
        return [
            entry for entry in self.history_cache
            if start_date <= entry.timestamp <= end_date
        ]
    
    def filter_by_success(self, successful: bool = True) -> List[CommandEntry]:
        """按执行结果过滤历史记录
        
        Args:
            successful: True 返回成功的命令，False 返回失败的命令
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        if successful:
            return [entry for entry in self.history_cache if entry.is_successful]
        else:
            return [entry for entry in self.history_cache if entry.has_error]
    
    def filter_by_confidence(self, min_confidence: float = 0.0, 
                            max_confidence: float = 1.0) -> List[CommandEntry]:
        """按置信度范围过滤历史记录
        
        Args:
            min_confidence: 最小置信度
            max_confidence: 最大置信度
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        return [
            entry for entry in self.history_cache
            if min_confidence <= entry.confidence_score <= max_confidence
        ]
    
    def filter_by_custom(self, predicate: Callable[[CommandEntry], bool]) -> List[CommandEntry]:
        """使用自定义条件过滤历史记录
        
        Args:
            predicate: 过滤函数，接受 CommandEntry 返回 bool
            
        Returns:
            List[CommandEntry]: 匹配的历史记录列表
        """
        return [entry for entry in self.history_cache if predicate(entry)]
    
    # ========================================================================
    # 统计分析
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取历史记录统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        if not self.history_cache:
            return {
                "total_commands": 0,
                "successful_commands": 0,
                "failed_commands": 0,
                "average_confidence": 0.0,
                "average_execution_time": 0.0
            }
        
        total = len(self.history_cache)
        successful = sum(1 for entry in self.history_cache if entry.is_successful)
        failed = sum(1 for entry in self.history_cache if entry.has_error)
        
        avg_confidence = sum(entry.confidence_score for entry in self.history_cache) / total
        avg_execution_time = sum(entry.execution_time for entry in self.history_cache) / total
        
        return {
            "total_commands": total,
            "successful_commands": successful,
            "failed_commands": failed,
            "success_rate": successful / total if total > 0 else 0.0,
            "average_confidence": avg_confidence,
            "average_execution_time": avg_execution_time,
            "oldest_entry": self.history_cache[0].timestamp.isoformat() if self.history_cache else None,
            "newest_entry": self.history_cache[-1].timestamp.isoformat() if self.history_cache else None
        }
    
    def get_most_used_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最常用的命令
        
        Args:
            limit: 返回的命令数量
            
        Returns:
            List[Dict[str, Any]]: 命令使用统计列表
        """
        command_counts = defaultdict(int)
        command_examples = {}
        
        for entry in self.history_cache:
            cmd = entry.translated_command
            command_counts[cmd] += 1
            if cmd not in command_examples:
                command_examples[cmd] = entry
        
        # 排序并返回前 N 个
        sorted_commands = sorted(
            command_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                "command": cmd,
                "count": count,
                "example_input": command_examples[cmd].user_input,
                "last_used": command_examples[cmd].timestamp.isoformat()
            }
            for cmd, count in sorted_commands
        ]
    
    def get_command_patterns(self) -> Dict[str, int]:
        """分析命令模式
        
        Returns:
            Dict[str, int]: 命令模式统计
        """
        patterns = defaultdict(int)
        
        for entry in self.history_cache:
            # 提取命令的第一个单词（通常是 cmdlet 名称）
            cmd = entry.translated_command.strip()
            if cmd:
                first_word = cmd.split()[0]
                patterns[first_word] += 1
        
        return dict(patterns)
    
    def get_time_distribution(self) -> Dict[str, int]:
        """获取命令执行的时间分布
        
        Returns:
            Dict[str, int]: 按小时统计的命令数量
        """
        distribution = defaultdict(int)
        
        for entry in self.history_cache:
            hour = entry.timestamp.hour
            distribution[f"{hour:02d}:00"] += 1
        
        return dict(sorted(distribution.items()))
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """分析错误命令
        
        Returns:
            Dict[str, Any]: 错误分析结果
        """
        failed_entries = self.filter_by_success(successful=False)
        
        if not failed_entries:
            return {
                "total_errors": 0,
                "common_errors": [],
                "error_rate": 0.0
            }
        
        # 统计常见错误
        error_counts = defaultdict(int)
        for entry in failed_entries:
            # 提取错误的第一行作为错误类型
            error_line = entry.error.split('\n')[0] if entry.error else "Unknown error"
            error_counts[error_line] += 1
        
        common_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_errors": len(failed_entries),
            "error_rate": len(failed_entries) / len(self.history_cache) if self.history_cache else 0.0,
            "common_errors": [
                {"error": error, "count": count}
                for error, count in common_errors
            ]
        }
    
    # ========================================================================
    # 历史记录导出和导入
    # ========================================================================
    
    def export_history(self, filepath: str, format: str = "json"):
        """导出历史记录到文件
        
        Args:
            filepath: 文件路径
            format: 导出格式，支持 'json' 和 'csv'
        """
        import json
        from pathlib import Path
        
        if format == "json":
            data = [entry.to_dict() for entry in self.history_cache]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            import csv
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "User Input", "Command", "Status",
                    "Return Code", "Execution Time", "Confidence"
                ])
                for entry in self.history_cache:
                    writer.writerow([
                        entry.timestamp.isoformat(),
                        entry.user_input,
                        entry.translated_command,
                        entry.status.value,
                        entry.return_code,
                        entry.execution_time,
                        entry.confidence_score
                    ])
        
        logger.info(f"Exported history to {filepath} ({format})")
    
    def import_history(self, filepath: str, format: str = "json"):
        """从文件导入历史记录
        
        Args:
            filepath: 文件路径
            format: 导入格式，支持 'json'
        """
        import json
        
        if format == "json":
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry_data in data:
                entry = CommandEntry.from_dict(entry_data)
                self.history_cache.append(entry)
            
            # 限制历史记录数量
            if len(self.history_cache) > self.max_history:
                self.history_cache = self.history_cache[-self.max_history:]
            
            logger.info(f"Imported {len(data)} entries from {filepath}")
            
            # 持久化
            if self.storage:
                self._save_history()
    
    # ========================================================================
    # 私有方法
    # ========================================================================
    
    def _load_history(self):
        """从存储加载历史记录"""
        if not self.storage:
            return
        
        try:
            history_data = self.storage.load_history(limit=self.max_history)
            if history_data:
                self.history_cache = [
                    CommandEntry.from_dict(entry) for entry in history_data
                ]
                logger.info(f"Loaded {len(self.history_cache)} history entries")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
    
    def _save_history(self):
        """保存历史记录到存储"""
        if not self.storage:
            return
        
        try:
            history_data = [entry.to_dict() for entry in self.history_cache]
            self.storage.save_history_batch(history_data)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
