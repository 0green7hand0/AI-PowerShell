#!/usr/bin/env python3
"""
AI PowerShell 助手 - 本地模式示例
不需要启动服务器，直接使用组件
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)  # 减少日志输出

def main():
    """本地模式演示"""
    print("🤖 AI PowerShell 助手 - 本地模式演示")
    print("=" * 50)
    
    try:
        # 初始化组件
        print("🔧 初始化组件...")
        
        from config.manager import load_config
        config = load_config()
        config.security.sandbox_enabled = False  # 禁用沙箱
        
        from ai_engine.engine import AIEngine
        from security.engine import SecurityEngine
        from execution.executor import PowerShellExecutor
        
        ai_engine = AIEngine(config.model)
        security_engine = SecurityEngine(config.security)
        executor = PowerShellExecutor(config.execution)
        
        print("✅ 组件初始化完成")
        
        # 演示菜单
        while True:
            print("\n" + "=" * 50)
            print("📋 请选择演示模式:")
            print("1. 系统管理示例")
            print("2. 文件管理示例")
            print("3. 网络诊断示例")
            print("4. 交互式演示")
            print("5. 退出")
            
            choice = input("\n请输入选项 (1-5): ").strip()
            
            if choice == "1":
                system_management_demo(ai_engine, security_engine, executor)
            elif choice == "2":
                file_management_demo(ai_engine, security_engine, executor)
            elif choice == "3":
                network_diagnostic_demo(ai_engine, security_engine, executor)
            elif choice == "4":
                interactive_demo(ai_engine, security_engine, executor)
            elif choice == "5":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选项，请输入 1-5")
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0

def system_management_demo(ai_engine, security_engine, executor):
    """系统管理示例"""
    print("\n🔧 系统管理任务示例")
    print("=" * 50)
    
    tasks = [
        "显示CPU使用率最高的5个进程",
        "检查磁盘空间使用情况",
        "列出所有正在运行的Windows服务",
        "显示网络连接状态",
        "查看系统启动时间"
    ]
    
    for task in tasks:
        process_task(task, ai_engine, security_engine, executor)

def file_management_demo(ai_engine, security_engine, executor):
    """文件管理示例"""
    print("\n📁 文件管理任务示例")
    print("=" * 50)
    
    tasks = [
        "列出当前目录下的所有文件",
        "显示文件夹大小",
        "查找最近修改的文件",
        "显示文件权限",
        "检查临时文件夹"
    ]
    
    for task in tasks:
        process_task(task, ai_engine, security_engine, executor)

def network_diagnostic_demo(ai_engine, security_engine, executor):
    """网络诊断示例"""
    print("\n🌐 网络诊断任务示例")
    print("=" * 50)
    
    tasks = [
        "测试网络连接",
        "显示网络配置",
        "检查DNS设置",
        "显示路由表",
        "测试端口连通性"
    ]
    
    for task in tasks:
        process_task(task, ai_engine, security_engine, executor)

def interactive_demo(ai_engine, security_engine, executor):
    """交互式演示"""
    print("\n💬 交互式演示模式")
    print("=" * 50)
    print("请输入中文描述，我会转换为 PowerShell 命令")
    print("输入 'quit' 退出交互模式")
    
    while True:
        user_input = input("\n🗣️  您的需求: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("退出交互模式")
            break
            
        if not user_input:
            continue
            
        process_task(user_input, ai_engine, security_engine, executor)

def process_task(task, ai_engine, security_engine, executor):
    """处理单个任务"""
    print(f"\n🔄 正在处理: {task}")
    print("─" * 40)
    
    try:
        # AI 翻译
        suggestion = ai_engine.translate_natural_language(task, None)
        print(f"🤖 AI 翻译: {suggestion.generated_command}")
        print(f"📊 置信度: {suggestion.confidence_score:.2f}")
        
        if suggestion.explanation:
            print(f"💡 说明: {suggestion.explanation}")
        
        # 安全验证
        validation = security_engine.validate_command(suggestion.generated_command)
        security_status = "✅ 通过" if validation.is_valid else "❌ 被阻止"
        print(f"🔒 安全验证: {security_status}")
        
        if not validation.is_valid:
            if validation.blocked_reasons:
                print(f"🚫 阻止原因: {', '.join(validation.blocked_reasons)}")
            return
        
        # 询问是否执行
        if suggestion.generated_command.startswith('#'):
            print("ℹ️  这是一个注释，跳过执行")
            return
            
        execute = input("🤔 是否执行此命令? (y/N): ").strip().lower()
        
        if execute in ['y', 'yes', '是', '执行']:
            try:
                print("⚡ 正在执行...")
                result = executor.execute_command(suggestion.generated_command)
                
                print(f"📤 执行结果:")
                print(f"   返回码: {result.return_code}")
                
                if result.stdout:
                    output = result.stdout.strip()
                    if len(output) > 500:
                        print(f"   输出: {output[:500]}...")
                        print("   (输出已截断)")
                    else:
                        print(f"   输出: {output}")
                
                if result.stderr:
                    print(f"   错误: {result.stderr.strip()}")
                    
            except Exception as exec_error:
                print(f"❌ 执行错误: {exec_error}")
        else:
            print("⏭️  跳过执行")
            
    except Exception as e:
        print(f"❌ 处理错误: {e}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)