"""
进度管理器测试
"""

import pytest
import sys
from pathlib import Path
import time

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.progress_manager import ProgressManager
from src.ui.models import UIConfig, ProgressTask
from rich.console import Console


class TestProgressManager:
    """测试进度管理器"""
    
    @pytest.fixture
    def console(self):
        """创建 Console 实例"""
        return Console()
    
    @pytest.fixture
    def progress_manager(self, console):
        """创建进度管理器实例"""
        config = UIConfig(enable_progress=True)
        return ProgressManager(console, config)
    
    def test_progress_manager_initialization(self, progress_manager):
        """测试进度管理器初始化"""
        assert progress_manager is not None
        assert progress_manager.console is not None
        assert progress_manager.config is not None
        assert len(progress_manager.active_tasks) == 0
    
    def test_start_spinner(self, progress_manager):
        """测试启动 spinner"""
        progress_manager.start_spinner("task1", "加载中...")
        
        assert "task1" in progress_manager.active_tasks
        task = progress_manager.active_tasks["task1"]
        assert task.task_id == "task1"
        assert task.description == "加载中..."
        assert task.total == 0
        
        # 清理
        progress_manager.stop_all()
    
    def test_start_progress(self, progress_manager):
        """测试启动进度条"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        
        assert "task1" in progress_manager.active_tasks
        task = progress_manager.active_tasks["task1"]
        assert task.task_id == "task1"
        assert task.description == "处理中..."
        assert task.total == 100
        assert task.completed == 0
        
        # 清理
        progress_manager.stop_all()
    
    def test_update_progress_with_completed(self, progress_manager):
        """测试使用绝对值更新进度"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        
        progress_manager.update_progress("task1", completed=50)
        task = progress_manager.active_tasks["task1"]
        assert task.completed == 50
        
        progress_manager.update_progress("task1", completed=100)
        task = progress_manager.active_tasks["task1"]
        assert task.completed == 100
        
        # 清理
        progress_manager.stop_all()
    
    def test_update_progress_with_advance(self, progress_manager):
        """测试使用相对值更新进度"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        
        progress_manager.update_progress("task1", advance=10)
        task = progress_manager.active_tasks["task1"]
        assert task.completed == 10
        
        progress_manager.update_progress("task1", advance=20)
        task = progress_manager.active_tasks["task1"]
        assert task.completed == 30
        
        # 清理
        progress_manager.stop_all()
    
    def test_update_progress_description(self, progress_manager):
        """测试更新进度描述"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        
        progress_manager.update_progress("task1", description="新的描述")
        task = progress_manager.active_tasks["task1"]
        assert task.description == "新的描述"
        
        # 清理
        progress_manager.stop_all()
    
    def test_finish_progress_success(self, progress_manager):
        """测试成功完成进度"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        progress_manager.update_progress("task1", completed=50)
        
        progress_manager.finish_progress("task1", success=True)
        
        # 任务应该被移除
        assert "task1" not in progress_manager.active_tasks
    
    def test_finish_progress_failure(self, progress_manager):
        """测试失败完成进度"""
        progress_manager.start_progress("task1", "处理中...", total=100)
        progress_manager.update_progress("task1", completed=50)
        
        progress_manager.finish_progress("task1", success=False)
        
        # 任务应该被移除
        assert "task1" not in progress_manager.active_tasks
    
    def test_multiple_concurrent_tasks(self, progress_manager):
        """测试多个并发任务"""
        # 启动多个任务
        progress_manager.start_progress("task1", "任务1", total=100)
        progress_manager.start_progress("task2", "任务2", total=50)
        progress_manager.start_spinner("task3", "任务3")
        
        assert len(progress_manager.active_tasks) == 3
        assert "task1" in progress_manager.active_tasks
        assert "task2" in progress_manager.active_tasks
        assert "task3" in progress_manager.active_tasks
        
        # 更新各个任务
        progress_manager.update_progress("task1", completed=50)
        progress_manager.update_progress("task2", completed=25)
        
        assert progress_manager.active_tasks["task1"].completed == 50
        assert progress_manager.active_tasks["task2"].completed == 25
        
        # 完成任务
        progress_manager.finish_progress("task1")
        assert "task1" not in progress_manager.active_tasks
        assert len(progress_manager.active_tasks) == 2
        
        # 清理
        progress_manager.stop_all()
    
    def test_stop_all(self, progress_manager):
        """测试停止所有任务"""
        progress_manager.start_progress("task1", "任务1", total=100)
        progress_manager.start_progress("task2", "任务2", total=50)
        
        assert len(progress_manager.active_tasks) == 2
        
        progress_manager.stop_all()
        
        assert len(progress_manager.active_tasks) == 0
        assert progress_manager._progress is None
    
    def test_progress_context_success(self, progress_manager):
        """测试进度上下文管理器（成功）"""
        with progress_manager.progress_context("task1", "处理中", total=100) as pm:
            assert "task1" in pm.active_tasks
            pm.update_progress("task1", advance=50)
            assert pm.active_tasks["task1"].completed == 50
        
        # 上下文退出后任务应该被移除
        assert "task1" not in progress_manager.active_tasks
    
    def test_progress_context_with_exception(self, progress_manager):
        """测试进度上下文管理器（异常）"""
        with pytest.raises(ValueError):
            with progress_manager.progress_context("task1", "处理中", total=100) as pm:
                pm.update_progress("task1", advance=50)
                raise ValueError("测试异常")
        
        # 即使发生异常，任务也应该被移除
        assert "task1" not in progress_manager.active_tasks
    
    def test_get_task_status(self, progress_manager):
        """测试获取任务状态"""
        progress_manager.start_progress("task1", "处理中", total=100)
        
        task = progress_manager.get_task_status("task1")
        assert task is not None
        assert task.task_id == "task1"
        assert task.total == 100
        
        # 不存在的任务
        task = progress_manager.get_task_status("nonexistent")
        assert task is None
        
        # 清理
        progress_manager.stop_all()
    
    def test_has_active_tasks(self, progress_manager):
        """测试检查是否有活动任务"""
        assert not progress_manager.has_active_tasks()
        
        progress_manager.start_progress("task1", "处理中", total=100)
        assert progress_manager.has_active_tasks()
        
        progress_manager.finish_progress("task1")
        assert not progress_manager.has_active_tasks()
    
    def test_progress_disabled(self, console):
        """测试禁用进度功能"""
        config = UIConfig(enable_progress=False)
        pm = ProgressManager(console, config)
        
        # 禁用时不应该创建任务
        pm.start_progress("task1", "处理中", total=100)
        assert len(pm.active_tasks) == 0
        
        pm.update_progress("task1", completed=50)
        assert len(pm.active_tasks) == 0


class TestProgressTask:
    """测试进度任务模型"""
    
    def test_progress_task_creation(self):
        """测试创建进度任务"""
        task = ProgressTask(
            task_id="task1",
            description="测试任务",
            total=100,
            completed=0
        )
        
        assert task.task_id == "task1"
        assert task.description == "测试任务"
        assert task.total == 100
        assert task.completed == 0
    
    def test_progress_task_percentage(self):
        """测试计算完成百分比"""
        task = ProgressTask(
            task_id="task1",
            description="测试任务",
            total=100,
            completed=50
        )
        
        assert task.percentage == 50.0
        
        task.completed = 75
        assert task.percentage == 75.0
        
        task.completed = 100
        assert task.percentage == 100.0
    
    def test_progress_task_percentage_zero_total(self):
        """测试总数为0时的百分比"""
        task = ProgressTask(
            task_id="task1",
            description="测试任务",
            total=0,
            completed=0
        )
        
        assert task.percentage == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
