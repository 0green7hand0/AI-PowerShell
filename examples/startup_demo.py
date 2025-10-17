"""
启动体验演示

演示启动向导和系统检查功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui import StartupWizard, StartupExperience, UIManager


def demo_startup_wizard():
    """演示启动向导"""
    print("=" * 60)
    print("启动向导演示")
    print("=" * 60)
    print()
    
    ui_manager = UIManager()
    wizard = StartupWizard(ui_manager)
    
    # 运行系统检查
    print("运行系统检查...")
    print()
    checks = wizard.run_system_checks()
    
    # 显示检查结果
    wizard._display_check_results()
    
    print()
    print("=" * 60)


def demo_quick_check():
    """演示快速检查"""
    print("=" * 60)
    print("快速系统检查演示")
    print("=" * 60)
    print()
    
    ui_manager = UIManager()
    wizard = StartupWizard(ui_manager)
    
    # 快速检查
    success, checks = wizard.quick_system_check()
    
    print(f"检查结果: {'通过' if success else '失败'}")
    print(f"检查项数: {len(checks)}")
    print()
    
    for check in checks:
        status_icon = {
            "passed": "✓",
            "warning": "⚠",
            "failed": "✗",
        }.get(check.status.value, "?")
        
        print(f"{status_icon} {check.name}: {check.message}")
    
    print()
    print("=" * 60)


def demo_startup_experience():
    """演示启动体验"""
    print("=" * 60)
    print("启动体验演示")
    print("=" * 60)
    print()
    
    ui_manager = UIManager()
    startup = StartupExperience(ui_manager)
    
    # 显示启动横幅
    startup._display_startup_banner()
    
    # 显示功能概览
    startup._display_feature_overview()
    
    # 显示快速提示
    startup._display_quick_tips()
    
    # 显示就绪状态
    startup._display_ready_status(0.5)
    
    print()
    print("=" * 60)


def demo_session_summary():
    """演示会话摘要"""
    print("=" * 60)
    print("会话摘要演示")
    print("=" * 60)
    print()
    
    ui_manager = UIManager()
    startup = StartupExperience(ui_manager)
    
    # 模拟会话统计
    stats = {
        'commands_executed': 15,
        'successful_commands': 12,
        'failed_commands': 3,
        'session_duration': 180.5,
    }
    
    startup.display_session_summary(stats)
    
    print()
    print("=" * 60)


def main():
    """主函数"""
    demos = [
        ("1", "启动向导", demo_startup_wizard),
        ("2", "快速检查", demo_quick_check),
        ("3", "启动体验", demo_startup_experience),
        ("4", "会话摘要", demo_session_summary),
        ("5", "全部演示", None),
    ]
    
    print("\n启动体验演示程序")
    print("=" * 60)
    print("\n选择要演示的功能:")
    for key, name, _ in demos:
        print(f"  {key}. {name}")
    print()
    
    choice = input("请选择 (1-5): ").strip()
    print()
    
    if choice == "5":
        # 运行所有演示
        for key, name, func in demos[:-1]:
            if func:
                func()
                input("\n按 Enter 继续...")
                print("\n")
    else:
        # 运行选定的演示
        for key, name, func in demos:
            if key == choice and func:
                func()
                break
        else:
            print("无效的选择")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n演示已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
