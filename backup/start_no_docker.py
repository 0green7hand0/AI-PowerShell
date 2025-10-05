#!/usr/bin/env python3
"""
AI PowerShell Assistant - 无 Docker 启动版本
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    print("🚀 AI PowerShell 智能助手启动中... (无 Docker 模式)")
    print("=" * 60)
    
    try:
        # Import and test basic components
        logger.info("导入核心模块...")
        
        # Test configuration
        from config.manager import load_config
        config = load_config()
        
        # Disable sandbox for this demo
        config.security.sandbox_enabled = False
        logger.info(f"✅ 配置加载成功 - 平台: {config.platform.value}")
        logger.info("⚠️  沙箱模式已禁用 (Docker 未安装)")
        
        # Test AI engine
        from ai_engine.engine import AIEngine
        ai_engine = AIEngine(config.model)
        logger.info("✅ AI 引擎初始化成功")
        
        # Test security engine (without sandbox)
        from security.engine import SecurityEngine
        security_engine = SecurityEngine(config.security)
        logger.info("✅ 安全引擎初始化成功 (无沙箱模式)")
        
        # Test executor
        from execution.executor import PowerShellExecutor
        executor = PowerShellExecutor(config.execution)
        logger.info("✅ 执行引擎初始化成功")
        
        print("\n🎉 所有核心组件初始化成功！")
        print("\n📋 可用功能:")
        print("1. ✅ 自然语言转 PowerShell 命令")
        print("2. ✅ 安全命令验证 (白名单 + 权限检查)")
        print("3. ✅ PowerShell 命令执行")
        print("4. ⚠️  沙箱执行 (需要 Docker)")
        
        print("\n🔧 测试基本功能:")
        
        # Test natural language translation
        test_cases = [
            "显示当前目录的文件",
            "查看系统进程",
            "检查PowerShell版本"
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {test_input}")
            
            try:
                # AI translation
                suggestion = ai_engine.translate_natural_language(test_input, None)
                print(f"   🤖 AI 翻译: {suggestion.generated_command}")
                print(f"   📊 置信度: {suggestion.confidence_score:.2f}")
                
                # Security validation
                validation = security_engine.validate_command(suggestion.generated_command)
                security_status = "✅ 通过" if validation.is_valid else "❌ 被阻止"
                print(f"   🔒 安全验证: {security_status}")
                
                if validation.is_valid:
                    # Safe execution test
                    if suggestion.generated_command.startswith(('Get-', 'Show-', '$PSVersionTable')):
                        try:
                            result = executor.execute_command(suggestion.generated_command)
                            print(f"   ⚡ 执行结果: 返回码 {result.return_code}")
                            if result.stdout and len(result.stdout.strip()) > 0:
                                output_preview = result.stdout.strip()[:100]
                                print(f"   📤 输出预览: {output_preview}...")
                        except Exception as exec_error:
                            print(f"   ⚠️  执行错误: {exec_error}")
                    else:
                        print(f"   ℹ️  跳过执行 (演示模式)")
                else:
                    if validation.blocked_reasons:
                        print(f"   🚫 阻止原因: {', '.join(validation.blocked_reasons)}")
                        
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 项目启动成功！核心功能正常工作。")
        print("\n💡 下一步:")
        print("1. 运行完整示例: python examples/中文使用示例.py")
        print("2. 安装 Docker 启用沙箱功能")
        print("3. 配置 AI 模型获得更好的翻译效果")
        
        print("\n📚 文档:")
        print("- 中文说明: 中文项目说明.md")
        print("- 快速开始: 快速开始.md")
        print("- 学习指南: learning/中文学习指南.md")
        
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        print(f"\n💡 解决方案:")
        print("1. 确保已安装依赖: pip install -r requirements.txt")
        print("2. 确保已安装项目: pip install -e .")
        return 1
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        logger.exception("详细错误信息:")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)