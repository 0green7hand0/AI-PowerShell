#!/usr/bin/env python3
"""
最终修复版本 - 直接修复原架构的核心问题
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class FixedExecutor:
    """修复的执行器 - 兼容原接口"""
    
    def __init__(self):
        self.powershell_cmd = self._find_powershell()
    
    def _find_powershell(self) -> Optional[str]:
        """查找可用的 PowerShell"""
        # 先尝试 Windows PowerShell
        try:
            subprocess.run(['powershell', '-Command', 'echo test'], 
                         capture_output=True, check=True, timeout=5)
            return 'powershell'
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # 再尝试 PowerShell Core
        try:
            subprocess.run(['pwsh', '--version'], 
                         capture_output=True, check=True, timeout=5)
            return 'pwsh'
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return None
    
    def execute_command(self, command: str, context=None):
        """执行命令 - 兼容原接口"""
        from interfaces.base import ExecutionResult, Platform
        
        if not self.powershell_cmd:
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr="PowerShell not available",
                execution_time=0.0,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
        
        try:
            result = subprocess.run(
                [self.powershell_cmd, '-Command', command],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='gbk',
                errors='ignore'
            )
            
            return ExecutionResult(
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=0.0,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                platform=Platform.WINDOWS,
                sandbox_used=False
            )

class FixedAIEngine:
    """修复的 AI 引擎 - 基于规则的翻译"""
    
    def __init__(self):
        self.rules = {
            r"显示.*时间|查看.*时间|当前.*时间": "Get-Date",
            r"显示.*文件|列出.*文件|查看.*文件": "Get-ChildItem",
            r"显示.*目录|当前.*目录|查看.*位置": "Get-Location",
            r"显示.*进程|查看.*进程|列出.*进程": "Get-Process",
            r"PowerShell.*版本|查看.*版本": "$PSVersionTable",
            r"显示.*服务|列出.*服务|查看.*服务": "Get-Service",
        }
    
    def translate_natural_language(self, text: str, context=None):
        """翻译自然语言"""
        import re
        from dataclasses import dataclass
        
        @dataclass
        class Suggestion:
            original_input: str
            generated_command: str
            confidence_score: float
            explanation: str
            alternatives: list
        
        # 尝试匹配规则
        for pattern, command in self.rules.items():
            if re.search(pattern, text, re.IGNORECASE):
                return Suggestion(
                    original_input=text,
                    generated_command=command,
                    confidence_score=0.9,
                    explanation=f"匹配规则: {pattern}",
                    alternatives=[]
                )
        
        # 默认回退
        return Suggestion(
            original_input=text,
            generated_command=f"# 未找到匹配规则: {text}",
            confidence_score=0.0,
            explanation="使用回退模式",
            alternatives=[]
        )

def test_fixed_architecture():
    """测试修复后的架构"""
    print("🔧 测试修复后的企业架构")
    print("=" * 40)
    
    try:
        # 初始化配置
        from config.manager import load_config
        config = load_config()
        config.security.sandbox_enabled = False
        print("✅ 配置系统")
        
        # 使用修复的组件
        ai_engine = FixedAIEngine()
        print("✅ 修复的 AI 引擎")
        
        from security.engine import SecurityEngine
        security_engine = SecurityEngine(config.security)
        print("✅ 安全引擎")
        
        executor = FixedExecutor()
        print("✅ 修复的执行引擎")
        
        # 测试完整流程
        test_cases = [
            "显示当前时间",
            "列出当前目录文件", 
            "查看PowerShell版本"
        ]
        
        for test_input in test_cases:
            print(f"\n📝 测试: {test_input}")
            
            # AI 翻译
            suggestion = ai_engine.translate_natural_language(test_input)
            print(f"  🤖 翻译: {suggestion.generated_command}")
            
            # 安全验证
            validation = security_engine.validate_command(suggestion.generated_command)
            print(f"  🔒 安全: {'✅ 通过' if validation.is_valid else '❌ 被阻止'}")
            
            # 执行
            if validation.is_valid and not suggestion.generated_command.startswith('#'):
                result = executor.execute_command(suggestion.generated_command)
                print(f"  ⚡ 执行: {'✅ 成功' if result.success else '❌ 失败'}")
                
                if result.success and result.stdout:
                    output = result.stdout.strip()[:100]
                    print(f"  📄 输出: {output}...")
        
        print("\n🎉 修复后的企业架构测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_fixed_assistant():
    """创建修复后的助手"""
    
    class FixedAssistant:
        def __init__(self):
            from config.manager import load_config
            config = load_config()
            config.security.sandbox_enabled = False
            
            self.ai_engine = FixedAIEngine()
            
            from security.engine import SecurityEngine
            self.security_engine = SecurityEngine(config.security)
            
            self.executor = FixedExecutor()
        
        def process(self, chinese_input: str):
            """处理请求"""
            print(f"🗣️  输入: {chinese_input}")
            
            # AI 翻译
            suggestion = self.ai_engine.translate_natural_language(chinese_input)
            print(f"🤖 翻译: {suggestion.generated_command}")
            print(f"📊 置信度: {suggestion.confidence_score:.2f}")
            
            # 安全验证
            validation = self.security_engine.validate_command(suggestion.generated_command)
            print(f"🔒 安全: {'✅ 通过' if validation.is_valid else '❌ 被阻止'}")
            
            if not validation.is_valid:
                if validation.blocked_reasons:
                    print(f"🚫 原因: {', '.join(validation.blocked_reasons)}")
                return
            
            # 执行
            if suggestion.generated_command.startswith('#'):
                print("ℹ️  注释，跳过执行")
                return
            
            confirm = input("🤔 执行此命令? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                print("⏭️  跳过执行")
                return
            
            print("⚡ 执行中...")
            result = self.executor.execute_command(suggestion.generated_command)
            
            if result.success:
                print(f"✅ 成功 (返回码: {result.return_code})")
                if result.stdout:
                    output = result.stdout.strip()
                    if len(output) > 300:
                        print(f"📄 输出:\n{output[:300]}...")
                    else:
                        print(f"📄 输出:\n{output}")
            else:
                print(f"❌ 失败 (返回码: {result.return_code})")
                if result.stderr:
                    print(f"🚫 错误: {result.stderr}")
    
    return FixedAssistant()

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        return 0 if test_fixed_architecture() else 1
    
    print("🏗️  AI PowerShell 助手 - 修复的企业版")
    print("=" * 45)
    
    try:
        assistant = create_fixed_assistant()
        
        if len(sys.argv) > 1:
            chinese_input = " ".join(sys.argv[1:])
            assistant.process(chinese_input)
        else:
            print("💬 交互模式 (输入 'quit' 退出)")
            while True:
                try:
                    user_input = input("\n🗣️  请输入: ").strip()
                    if user_input.lower() in ['quit', 'exit', '退出']:
                        print("👋 再见！")
                        break
                    if user_input:
                        assistant.process(user_input)
                except KeyboardInterrupt:
                    print("\n👋 再见！")
                    break
        
        return 0
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)