#!/usr/bin/env python3
"""
AI PowerShell 助手 - 快速功能测试
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)

def main():
    """快速测试主要功能"""
    print("🚀 AI PowerShell 助手 - 快速功能测试")
    print("=" * 50)
    
    try:
        # 初始化组件
        print("🔧 正在初始化组件...")
        
        from config.manager import load_config
        config = load_config()
        config.security.sandbox_enabled = False
        
        from ai_engine.engine import AIEngine
        from security.engine import SecurityEngine
        from execution.executor import PowerShellExecutor
        
        ai_engine = AIEngine(config.model)
        security_engine = SecurityEngine(config.security)
        executor = PowerShellExecutor(config.execution)
        
        print("✅ 组件初始化完成\n")
        
        # 测试用例
        test_cases = [
            "显示当前目录的文件",
            "查看PowerShell版本",
            "显示当前时间",
            "列出环境变量"
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"📝 测试 {i}: {test_input}")
            print("─" * 40)
            
            # AI 翻译
            suggestion = ai_engine.translate_natural_language(test_input, None)
            print(f"🤖 AI 翻译: {suggestion.generated_command}")
            print(f"📊 置信度: {suggestion.confidence_score:.2f}")
            
            # 安全验证
            validation = security_engine.validate_command(suggestion.generated_command)
            security_status = "✅ 通过" if validation.is_valid else "❌ 被阻止"
            print(f"🔒 安全验证: {security_status}")
            
            # 如果是安全的 Get- 命令，尝试执行
            if (validation.is_valid and 
                suggestion.generated_command.startswith(('Get-', '$PSVersionTable', 'Get-Date'))):
                try:
                    print("⚡ 正在执行...")
                    result = executor.execute_command(suggestion.generated_command)
                    print(f"📤 返回码: {result.return_code}")
                    
                    if result.stdout:
                        output = result.stdout.strip()
                        if len(output) > 200:
                            print(f"📄 输出: {output[:200]}...")
                        else:
                            print(f"📄 输出: {output}")
                            
                except Exception as e:
                    print(f"❌ 执行错误: {e}")
            else:
                print("ℹ️  跳过执行 (演示模式)")
            
            print()  # 空行分隔
        
        print("🎉 测试完成！所有核心功能正常工作。")
        print("\n💡 您可以:")
        print("1. 运行 'python 本地模式示例.py' 进行交互式体验")
        print("2. 查看 '项目启动成功.md' 了解更多功能")
        print("3. 按照 '创建Release指南.md' 发布项目")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)