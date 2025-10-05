#!/usr/bin/env python3
"""
修复复杂版本 - 让原来的架构真正可用
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(level=logging.WARNING)

def create_mock_context():
    """创建模拟的上下文对象"""
    from interfaces.base import Platform
    
    class MockCommandContext:
        def __init__(self):
            self.session_id = "mock_session"
            self.user_id = "mock_user"
            self.platform = Platform.WINDOWS
            self.working_directory = str(Path.cwd())
            self.environment_variables = {}
            self.previous_commands = []
    
    return MockCommandContext()

class FixedPowerShellAssistant:
    """修复后的 PowerShell 助手 - 使用原架构但修复接口问题"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mock_context = create_mock_context()
        
        # 初始化组件
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有组件"""
        try:
            print("🔧 初始化复杂版本组件...")
            
            # 加载配置
            from config.manager import load_config
            self.config = load_config()
            self.config.security.sandbox_enabled = False  # 禁用沙箱避免 Docker 问题
            print("  ✅ 配置管理")
            
            # 初始化 AI 引擎
            from ai_engine.engine import AIEngine
            self.ai_engine = AIEngine(self.config.model)
            print("  ✅ AI 引擎 (回退模式)")
            
            # 初始化安全引擎
            from security.engine import SecurityEngine
            self.security_engine = SecurityEngine(self.config.security)
            print("  ✅ 安全引擎")
            
            # 初始化执行引擎
            from execution.executor import PowerShellExecutor
            self.executor = PowerShellExecutor(self.config.execution)
            print("  ✅ 执行引擎")
            
            print("🎉 复杂版本组件初始化完成")
            
        except Exception as e:
            print(f"❌ 组件初始化失败: {e}")
            raise
    
    def translate_natural_language(self, chinese_input: str) -> dict:
        """AI 翻译功能"""
        try:
            # 使用修复的上下文调用
            suggestion = self.ai_engine.translate_natural_language(chinese_input, self.mock_context)
            
            return {
                'success': True,
                'original_input': suggestion.original_input,
                'generated_command': suggestion.generated_command,
                'confidence_score': suggestion.confidence_score,
                'explanation': suggestion.explanation,
                'alternatives': suggestion.alternatives
            }
        except Exception as e:
            self.logger.error(f"AI 翻译失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'generated_command': f"# AI 翻译失败: {chinese_input}",
                'confidence_score': 0.0
            }
    
    def validate_command(self, command: str) -> dict:
        """安全验证功能"""
        try:
            validation = self.security_engine.validate_command(command)
            
            return {
                'success': True,
                'is_valid': validation.is_valid,
                'risk_level': validation.risk_assessment.value if validation.risk_assessment else 'unknown',
                'blocked_reasons': validation.blocked_reasons,
                'required_permissions': [perm.value for perm in validation.required_permissions] if validation.required_permissions else [],
                'suggested_alternatives': validation.suggested_alternatives
            }
        except Exception as e:
            self.logger.error(f"安全验证失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'is_valid': False
            }
    
    def execute_command(self, command: str) -> dict:
        """执行 PowerShell 命令"""
        try:
            # 使用修复的上下文调用
            result = self.executor.execute_command(command, self.mock_context)
            
            return {
                'success': result.success,
                'return_code': result.return_code,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': result.execution_time,
                'platform': result.platform.value if result.platform else 'unknown',
                'sandbox_used': result.sandbox_used
            }
        except Exception as e:
            self.logger.error(f"命令执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'return_code': -1,
                'stdout': '',
                'stderr': str(e)
            }
    
    def process_request(self, chinese_input: str, auto_execute: bool = False) -> dict:
        """完整的请求处理流程"""
        print(f"\n🗣️  输入: {chinese_input}")
        
        # 1. AI 翻译
        translation_result = self.translate_natural_language(chinese_input)
        if not translation_result['success']:
            return translation_result
        
        command = translation_result['generated_command']
        print(f"🤖 AI 翻译: {command}")
        print(f"📊 置信度: {translation_result['confidence_score']:.2f}")
        
        if translation_result.get('explanation'):
            print(f"💡 说明: {translation_result['explanation']}")
        
        # 2. 安全验证
        validation_result = self.validate_command(command)
        if not validation_result['success']:
            return validation_result
        
        is_valid = validation_result['is_valid']
        print(f"🔒 安全验证: {'✅ 通过' if is_valid else '❌ 被阻止'}")
        
        if not is_valid:
            if validation_result.get('blocked_reasons'):
                print(f"🚫 阻止原因: {', '.join(validation_result['blocked_reasons'])}")
            return {
                'success': False,
                'error': 'Command blocked by security policy',
                'validation_result': validation_result
            }
        
        # 3. 执行确认
        if command.startswith('#'):
            print("ℹ️  这是一个注释，跳过执行")
            return {
                'success': True,
                'message': 'Comment skipped',
                'translation_result': translation_result,
                'validation_result': validation_result
            }
        
        if not auto_execute:
            confirm = input("🤔 是否执行此命令? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                print("⏭️  跳过执行")
                return {
                    'success': True,
                    'message': 'Execution cancelled by user',
                    'translation_result': translation_result,
                    'validation_result': validation_result
                }
        
        # 4. 执行命令
        print("⚡ 正在执行...")
        execution_result = self.execute_command(command)
        
        # 5. 显示结果
        if execution_result['success']:
            print(f"✅ 执行成功 (返回码: {execution_result['return_code']})")
            if execution_result['stdout']:
                output = execution_result['stdout'].strip()
                if len(output) > 500:
                    print(f"📄 输出:\n{output[:500]}...")
                    print("(输出已截断)")
                else:
                    print(f"📄 输出:\n{output}")
        else:
            print(f"❌ 执行失败 (返回码: {execution_result['return_code']})")
            if execution_result['stderr']:
                print(f"🚫 错误: {execution_result['stderr']}")
        
        return {
            'success': True,
            'translation_result': translation_result,
            'validation_result': validation_result,
            'execution_result': execution_result
        }
    
    def interactive_mode(self):
        """交互模式"""
        print("\n💬 进入复杂版本交互模式 (输入 'quit' 退出)")
        print("💡 提示: 使用完整的企业级架构处理您的请求")
        
        while True:
            try:
                user_input = input("\n🗣️  请输入: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                self.process_request(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主函数"""
    print("🚀 AI PowerShell 助手 - 修复的复杂版本")
    print("=" * 50)
    print("🏗️  使用企业级架构 + 修复的接口")
    
    try:
        assistant = FixedPowerShellAssistant()
        
        if len(sys.argv) > 1:
            # 命令行模式
            chinese_input = " ".join(sys.argv[1:])
            result = assistant.process_request(chinese_input, auto_execute=False)
            return 0
        else:
            # 交互模式
            assistant.interactive_mode()
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)