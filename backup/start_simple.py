#!/usr/bin/env python3
"""
Simple startup script for AI PowerShell Assistant
"""

import sys
import asyncio
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
    print("🚀 AI PowerShell 智能助手启动中...")
    print("=" * 50)
    
    try:
        # Import and test basic components
        logger.info("导入核心模块...")
        
        # Test configuration
        from config.manager import load_config
        config = load_config()
        logger.info(f"✅ 配置加载成功 - 平台: {config.platform.value}")
        
        # Test AI engine
        from ai_engine.engine import AIEngine
        ai_engine = AIEngine(config.model)
        logger.info("✅ AI 引擎初始化成功")
        
        # Test security engine
        from security.engine import SecurityEngine
        security_engine = SecurityEngine(config.security)
        logger.info("✅ 安全引擎初始化成功")
        
        # Test executor
        from execution.executor import PowerShellExecutor
        executor = PowerShellExecutor(config.execution)
        logger.info("✅ 执行引擎初始化成功")
        
        print("\n🎉 所有核心组件初始化成功！")
        print("\n📋 可用功能:")
        print("1. 自然语言转 PowerShell 命令")
        print("2. 安全命令验证")
        print("3. PowerShell 命令执行")
        print("4. 上下文管理")
        
        print("\n💡 使用示例:")
        print("python examples/中文使用示例.py")
        
        print("\n🔧 测试基本功能:")
        
        # Test natural language translation
        test_input = "显示当前目录的文件"
        logger.info(f"测试输入: {test_input}")
        
        suggestion = ai_engine.translate_natural_language(test_input)
        print(f"✅ AI 翻译结果: {suggestion.generated_command}")
        
        # Test security validation
        validation = security_engine.validate_command(suggestion.generated_command)
        print(f"✅ 安全验证: {'通过' if validation.is_valid else '被阻止'}")
        
        if validation.is_valid:
            # Test execution (safe command)
            result = executor.execute_command(suggestion.generated_command)
            print(f"✅ 执行结果: 返回码 {result.return_code}")
            if result.stdout:
                print(f"   输出: {result.stdout[:100]}...")
        
        print("\n🎯 项目启动成功！所有核心功能正常工作。")
        
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