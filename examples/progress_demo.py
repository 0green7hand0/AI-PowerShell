"""
进度管理器演示

展示如何使用 ProgressManager 来显示各种进度指示器。
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import UIManager
from src.ui.models import UIConfig


def demo_spinner():
    """演示 Spinner 加载动画"""
    print("\n=== Spinner 演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    pm.start_spinner("loading", "正在加载数据...")
    time.sleep(2)
    pm.finish_progress("loading", success=True)
    
    print("✓ Spinner 演示完成\n")


def demo_progress_bar():
    """演示进度条"""
    print("\n=== 进度条演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    pm.start_progress("processing", "处理文件中...", total=100)
    
    for i in range(0, 101, 10):
        time.sleep(0.2)
        pm.update_progress("processing", completed=i)
    
    pm.finish_progress("processing", success=True)
    
    print("✓ 进度条演示完成\n")


def demo_multiple_tasks():
    """演示多个并发任务"""
    print("\n=== 多任务演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    # 启动多个任务
    pm.start_progress("task1", "下载文件...", total=100)
    pm.start_progress("task2", "解压文件...", total=50)
    pm.start_spinner("task3", "验证数据...")
    
    # 模拟任务进度
    for i in range(10):
        time.sleep(0.2)
        pm.update_progress("task1", advance=10)
        if i < 5:
            pm.update_progress("task2", advance=10)
    
    # 完成任务
    pm.finish_progress("task1", success=True)
    pm.finish_progress("task2", success=True)
    pm.finish_progress("task3", success=True)
    
    print("✓ 多任务演示完成\n")


def demo_context_manager():
    """演示上下文管理器"""
    print("\n=== 上下文管理器演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    with pm.progress_context("backup", "备份数据...", total=100) as progress:
        for i in range(0, 101, 20):
            time.sleep(0.3)
            progress.update_progress("backup", completed=i)
    
    print("✓ 上下文管理器演示完成\n")


def demo_with_ai_engine():
    """演示与 AI 引擎集成"""
    print("\n=== AI 引擎集成演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    # 模拟 AI 翻译过程
    pm.start_progress("ai_translate", "AI 翻译中...", total=4)
    
    steps = [
        "检查缓存...",
        "AI 模型处理中...",
        "错误检测和修正...",
        "完成"
    ]
    
    for i, step in enumerate(steps, 1):
        time.sleep(0.5)
        pm.update_progress("ai_translate", completed=i, description=step)
    
    pm.finish_progress("ai_translate", success=True)
    
    print("✓ AI 引擎集成演示完成\n")


def demo_with_template_engine():
    """演示与模板引擎集成"""
    print("\n=== 模板引擎集成演示 ===")
    ui = UIManager()
    pm = ui.progress_manager
    
    # 模拟模板处理过程
    pm.start_progress("template", "模板处理中...", total=3)
    
    steps = [
        "识别意图...",
        "匹配模板...",
        "生成脚本..."
    ]
    
    for i, step in enumerate(steps, 1):
        time.sleep(0.5)
        pm.update_progress("template", completed=i, description=step)
    
    pm.finish_progress("template", success=True)
    
    print("✓ 模板引擎集成演示完成\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("进度管理器功能演示")
    print("="*60)
    
    try:
        demo_spinner()
        demo_progress_bar()
        demo_multiple_tasks()
        demo_context_manager()
        demo_with_ai_engine()
        demo_with_template_engine()
        
        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n演示被用户中断")
    except Exception as e:
        print(f"\n\n演示出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
