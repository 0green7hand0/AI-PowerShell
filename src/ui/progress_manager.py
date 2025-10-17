"""
进度管理器

管理各种进度指示器和加载动画。
"""

from typing import Dict, Optional, Any
from contextlib import contextmanager
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn,
    TimeRemainingColumn,
    TaskID
)
from rich.console import Console

from .models import ProgressTask, UIConfig


class ProgressManager:
    """进度管理器 - 支持多种进度显示类型"""
    
    def __init__(self, console: Console, config: Optional[UIConfig] = None):
        """
        初始化进度管理器
        
        Args:
            console: Rich Console 实例
            config: UI 配置对象
        """
        self.console = console
        self.config = config or UIConfig()
        self.active_tasks: Dict[str, ProgressTask] = {}
        self._progress: Optional[Progress] = None
        self._rich_task_ids: Dict[str, TaskID] = {}
    
    def _ensure_progress(self) -> Progress:
        """
        确保 Progress 实例存在
        
        Returns:
            Progress: Rich Progress 实例
        """
        if self._progress is None:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
                transient=False
            )
        return self._progress
    
    def start_spinner(self, task_id: str, description: str) -> None:
        """
        启动加载动画（spinner）
        
        Args:
            task_id: 任务 ID
            description: 任务描述
        """
        if not self.config.enable_progress:
            return
        
        # 创建进度任务
        task = ProgressTask(
            task_id=task_id,
            description=description,
            total=0,  # Spinner 不需要总数
            completed=0
        )
        self.active_tasks[task_id] = task
        
        # 创建 Rich 进度任务
        progress = self._ensure_progress()
        if not progress.live.is_started:
            progress.start()
        
        rich_task_id = progress.add_task(description, total=None)
        self._rich_task_ids[task_id] = rich_task_id
    
    def start_progress(
        self, 
        task_id: str, 
        description: str, 
        total: int = 100
    ) -> None:
        """
        启动进度条
        
        Args:
            task_id: 任务 ID
            description: 任务描述
            total: 总步骤数
        """
        if not self.config.enable_progress:
            return
        
        # 创建进度任务
        task = ProgressTask(
            task_id=task_id,
            description=description,
            total=total,
            completed=0
        )
        self.active_tasks[task_id] = task
        
        # 创建 Rich 进度任务
        progress = self._ensure_progress()
        if not progress.live.is_started:
            progress.start()
        
        rich_task_id = progress.add_task(description, total=total)
        self._rich_task_ids[task_id] = rich_task_id
    
    def update_progress(
        self, 
        task_id: str, 
        completed: Optional[int] = None,
        advance: Optional[int] = None,
        description: Optional[str] = None
    ) -> None:
        """
        更新进度
        
        Args:
            task_id: 任务 ID
            completed: 已完成数量（绝对值）
            advance: 前进步数（相对值）
            description: 更新任务描述
        """
        if not self.config.enable_progress or task_id not in self.active_tasks:
            return
        
        task = self.active_tasks[task_id]
        
        # 更新任务状态
        if completed is not None:
            task.completed = completed
        elif advance is not None:
            task.completed += advance
        
        if description is not None:
            task.description = description
        
        # 更新 Rich 进度
        if self._progress and task_id in self._rich_task_ids:
            rich_task_id = self._rich_task_ids[task_id]
            
            update_kwargs: Dict[str, Any] = {}
            if completed is not None:
                update_kwargs['completed'] = completed
            if advance is not None:
                update_kwargs['advance'] = advance
            if description is not None:
                update_kwargs['description'] = description
            
            if update_kwargs:
                self._progress.update(rich_task_id, **update_kwargs)
    
    def finish_progress(self, task_id: str, success: bool = True) -> None:
        """
        完成进度
        
        Args:
            task_id: 任务 ID
            success: 是否成功
        """
        if not self.config.enable_progress or task_id not in self.active_tasks:
            return
        
        task = self.active_tasks[task_id]
        
        # 更新 Rich 进度为完成状态
        if self._progress and task_id in self._rich_task_ids:
            rich_task_id = self._rich_task_ids[task_id]
            
            # 如果有总数，设置为完成
            if task.total > 0:
                self._progress.update(rich_task_id, completed=task.total)
            
            # 更新描述显示完成状态
            status_icon = "✓" if success else "✗"
            status_text = "完成" if success else "失败"
            self._progress.update(
                rich_task_id,
                description=f"{status_icon} {task.description} - {status_text}"
            )
        
        # 清理任务
        del self.active_tasks[task_id]
        if task_id in self._rich_task_ids:
            del self._rich_task_ids[task_id]
        
        # 如果没有活动任务，停止进度显示
        if not self.active_tasks and self._progress:
            self._progress.stop()
            self._progress = None
    
    def stop_all(self) -> None:
        """停止所有进度显示"""
        if self._progress:
            self._progress.stop()
            self._progress = None
        
        self.active_tasks.clear()
        self._rich_task_ids.clear()
    
    @contextmanager
    def progress_context(
        self, 
        task_id: str, 
        description: str, 
        total: Optional[int] = None
    ):
        """
        进度上下文管理器，自动管理进度的开始和结束
        
        Args:
            task_id: 任务 ID
            description: 任务描述
            total: 总步骤数（None 表示使用 spinner）
            
        Yields:
            ProgressManager: 自身实例，用于更新进度
            
        Example:
            with progress_manager.progress_context("task1", "处理中", 100) as pm:
                for i in range(100):
                    # 执行任务
                    pm.update_progress("task1", advance=1)
        """
        try:
            if total is None:
                self.start_spinner(task_id, description)
            else:
                self.start_progress(task_id, description, total)
            
            yield self
            
            self.finish_progress(task_id, success=True)
        except Exception as e:
            self.finish_progress(task_id, success=False)
            raise
    
    @contextmanager
    def create_spinner(self, description: str):
        """
        创建spinner上下文管理器（便捷方法）
        
        Args:
            description: 任务描述
            
        Yields:
            SpinnerContext: Spinner上下文对象
            
        Example:
            with progress_manager.create_spinner("正在处理...") as spinner:
                # 执行任务
                spinner.update("处理完成")
        """
        import uuid
        task_id = str(uuid.uuid4())
        
        class SpinnerContext:
            def __init__(self, manager, task_id):
                self.manager = manager
                self.task_id = task_id
            
            def update(self, description: str):
                """更新spinner描述"""
                if self.task_id in self.manager.active_tasks:
                    self.manager.update_progress(self.task_id, description=description)
        
        try:
            self.start_spinner(task_id, description)
            yield SpinnerContext(self, task_id)
            self.finish_progress(task_id, success=True)
        except Exception as e:
            self.finish_progress(task_id, success=False)
            raise
    
    def get_task_status(self, task_id: str) -> Optional[ProgressTask]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Optional[ProgressTask]: 任务对象，如果不存在返回 None
        """
        return self.active_tasks.get(task_id)
    
    def has_active_tasks(self) -> bool:
        """
        检查是否有活动任务
        
        Returns:
            bool: 是否有活动任务
        """
        return len(self.active_tasks) > 0
