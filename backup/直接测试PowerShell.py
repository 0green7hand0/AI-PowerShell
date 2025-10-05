#!/usr/bin/env python3
"""
直接测试 PowerShell 执行功能
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)

def main():
    """直接测试 PowerShell 执行"""
    print("⚡ PowerShell 执行引擎测试")
    print("=" * 40)
    
    try:
        # 初始化执行引擎
        from config.manager import load_config
        from execution.executor import PowerShellExecutor
        from security.engine import SecurityEngine
        
        config = load_config()
        config.security.sandbox_enabled = False
        
        executor = PowerShellExecutor(config.execution)
        security_engine = SecurityEngine(config.security)
        
        print("✅ 执行引擎初始化完成\n")
        
        # 测试命令
        test_commands = [
            "Get-Date",
            "$PSVersionTable",
            "Get-Location",
            "Get-ChildItem -Path . | Select-Object -First 3",
            "Get-Process | Select-Object -First 3 Name, CPU"
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"📝 测试 {i}: {command}")
            print("─" * 30)
            
            # 安全验证
            validation = security_engine.validate_command(command)
            if validation.is_valid:
                print("🔒 安全验证: ✅ 通过")
                
                try:
                    # 执行命令
                    result = executor.execute_command(command, None)
                    print(f"📤 返回码: {result.return_code}")
                    print(f"⏱️  执行时间: {result.execution_time:.2f}秒")
                    
                    if result.stdout:
                        output = result.stdout.strip()
                        if len(output) > 300:
                            print(f"📄 输出:\n{output[:300]}...")
                        else:
                            print(f"📄 输出:\n{output}")
                    
                    if result.stderr:
                        print(f"⚠️  错误: {result.stderr.strip()}")
                        
                except Exception as e:
                    print(f"❌ 执行失败: {e}")
            else:
                print("🔒 安全验证: ❌ 被阻止")
                if validation.blocked_reasons:
                    print(f"🚫 原因: {', '.join(validation.blocked_reasons)}")
            
            print()  # 空行
        
        print("🎉 PowerShell 执行测试完成！")
        
        # 交互式测试
        print("\n💬 交互式测试 (输入 'quit' 退出):")
        while True:
            command = input("\nPowerShell> ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
                
            if not command:
                continue
            
            # 安全验证
            validation = security_engine.validate_command(command)
            if not validation.is_valid:
                print(f"🚫 命令被阻止: {', '.join(validation.blocked_reasons)}")
                continue
            
            try:
                result = executor.execute_command(command, None)
                print(f"返回码: {result.return_code}")
                
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(f"错误: {result.stderr.strip()}")
                    
            except Exception as e:
                print(f"执行错误: {e}")
        
        print("👋 测试结束")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)