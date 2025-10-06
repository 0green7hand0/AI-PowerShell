"""
AI PowerShell 智能助手 - 主入口和控制器

本模块实现主控制器类 PowerShellAssistant，负责协调各个组件的工作，
处理用户请求，并提供交互式和命令行两种使用模式。
"""

import sys
import argparse
import uuid
from typing import Optional
from pathlib import Path

from src.interfaces.base import Context, Suggestion, ValidationResult, ExecutionResult
from src.ai_engine import AIEngine
from src.security import SecurityEngine
from src.execution import CommandExecutor
from src.config import ConfigManager, AppConfig
from src.log_engine import LogEngine
from src.storage import StorageFactory
from src.context import ContextManager


class PowerShellAssistant:
    """
    PowerShell 智能助手主控制器
    
    负责协调 AI 引擎、安全引擎、执行引擎等各个组件，
    实现完整的请求处理流程。
    
    Attributes:
        config: 应用配置对象
        ai_engine: AI 引擎实例
        security_engine: 安全引擎实例
        executor: 命令执行器实例
        log_engine: 日志引擎实例
        storage: 存储引擎实例
        context_manager: 上下文管理器实例
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 PowerShell 助手
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认配置
        """
        # 1. 加载配置
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load_config()
        
        # 2. 初始化日志引擎（最先初始化，用于记录其他组件的初始化过程）
        self.log_engine = LogEngine(self.config.logging)
        self.log_engine.info("Initializing PowerShell Assistant...")
        
        # 3. 初始化存储引擎
        self.storage = StorageFactory.create_storage(
            storage_type="file",  # 默认使用文件存储
            config=self.config.storage.model_dump()  # 转换为字典
        )
        self.log_engine.info("Storage engine initialized: file")
        
        # 4. 初始化上下文管理器
        self.context_manager = ContextManager(storage=self.storage)
        self.log_engine.info("Context manager initialized")
        
        # 5. 初始化 AI 引擎
        self.ai_engine = AIEngine(self.config.ai.model_dump())  # 转换为字典
        self.log_engine.info(f"AI engine initialized: {self.config.ai.provider}")
        
        # 6. 初始化安全引擎
        self.security_engine = SecurityEngine(self.config.security.model_dump())  # 转换为字典
        self.log_engine.info("Security engine initialized")
        
        # 7. 初始化执行引擎
        self.executor = CommandExecutor(self.config.execution.model_dump())  # 转换为字典
        self.log_engine.info("Execution engine initialized")
        
        self.log_engine.info("PowerShell Assistant initialization complete")
    
    def process_request(self, user_input: str, auto_execute: bool = False) -> ExecutionResult:
        """
        处理用户请求的完整流程
        
        这是核心的请求处理方法，实现了从用户输入到命令执行的完整流程：
        1. 生成关联 ID 并记录请求
        2. 使用 AI 引擎翻译自然语言
        3. 使用安全引擎验证命令
        4. 获取用户确认（如需要）
        5. 执行命令
        6. 记录结果并更新上下文
        
        Args:
            user_input: 用户输入的中文自然语言
            auto_execute: 是否自动执行（跳过用户确认）
            
        Returns:
            ExecutionResult: 命令执行结果
        """
        # 1. 生成关联 ID 并记录请求
        correlation_id = str(uuid.uuid4())
        self.log_engine.log_request(user_input, correlation_id=correlation_id)
        
        try:
            # 2. 获取当前上下文
            context = self._build_context()
            
            # 3. AI 翻译
            self.log_engine.info(f"Translating input: {user_input}")
            suggestion = self.ai_engine.translate_natural_language(user_input, context)
            self.log_engine.log_translation(
                user_input,
                suggestion.generated_command,
                suggestion.confidence_score
            )
            
            # 4. 安全验证
            self.log_engine.info(f"Validating command: {suggestion.generated_command}")
            validation = self.security_engine.validate_command(
                suggestion.generated_command,
                context
            )
            
            # 5. 检查验证结果
            if not validation.is_valid:
                self.log_engine.warning(
                    f"Command blocked: {', '.join(validation.blocked_reasons)}"
                )
                return ExecutionResult(
                    success=False,
                    command=suggestion.generated_command,
                    error=f"命令被安全引擎阻止: {', '.join(validation.blocked_reasons)}",
                    return_code=-1
                )
            
            # 6. 用户确认（如需要）
            if validation.requires_confirmation and not auto_execute:
                if not self._get_user_confirmation(suggestion, validation):
                    self.log_engine.info("User cancelled execution")
                    return ExecutionResult(
                        success=True,
                        command=suggestion.generated_command,
                        output="用户取消执行",
                        return_code=0
                    )
            
            # 7. 执行命令
            self.log_engine.info(f"Executing command: {suggestion.generated_command}")
            result = self.executor.execute(
                suggestion.generated_command,
                timeout=self.config.execution.timeout
            )
            self.log_engine.log_execution(suggestion.generated_command, result)
            
            # 8. 保存历史记录
            self._save_to_history(user_input, suggestion, result)
            
            # 9. 更新上下文
            self.context_manager.add_command(
                user_input=user_input,
                suggestion=suggestion,
                result=result
            )
            
            return result
            
        except Exception as e:
            self.log_engine.error(f"Error processing request: {str(e)}", 
                                 user_input=user_input,
                                 correlation_id=correlation_id)
            return ExecutionResult(
                success=False,
                command="",
                error=f"处理请求时发生错误: {str(e)}",
                return_code=-1
            )
    
    def _build_context(self) -> Context:
        """
        构建当前上下文
        
        Returns:
            Context: 包含会话信息和命令历史的上下文对象
        """
        session = self.context_manager.get_current_session()
        recent_commands = self.context_manager.get_recent_commands(limit=5)
        
        # 如果没有活动会话，创建一个临时会话 ID
        session_id = session.session_id if session else str(uuid.uuid4())
        
        return Context(
            session_id=session_id,
            working_directory=str(Path.cwd()),
            command_history=[cmd.translated_command for cmd in recent_commands]
        )
    
    def _get_user_confirmation(
        self,
        suggestion: Suggestion,
        validation: ValidationResult
    ) -> bool:
        """
        获取用户确认
        
        Args:
            suggestion: AI 生成的命令建议
            validation: 安全验证结果
            
        Returns:
            bool: 用户是否确认执行
        """
        print("\n" + "=" * 60)
        print("🤖 AI 翻译结果")
        print("=" * 60)
        print(f"原始输入: {suggestion.original_input}")
        print(f"生成命令: {suggestion.generated_command}")
        print(f"置信度: {suggestion.confidence_score:.2%}")
        print(f"说明: {suggestion.explanation}")
        
        if validation.warnings:
            print("\n⚠️  警告:")
            for warning in validation.warnings:
                print(f"  - {warning}")
        
        if validation.requires_elevation:
            print("\n🔐 此命令需要管理员权限")
        
        print("\n风险等级:", self._format_risk_level(validation.risk_level))
        print("=" * 60)
        
        response = input("\n是否执行此命令? (y/N): ").strip().lower()
        return response in ['y', 'yes', '是', 'Y']
    
    def _format_risk_level(self, risk_level) -> str:
        """格式化风险等级显示"""
        risk_colors = {
            "safe": "🟢 安全",
            "low": "🟡 低风险",
            "medium": "🟠 中等风险",
            "high": "🔴 高风险",
            "critical": "🔴 严重风险"
        }
        return risk_colors.get(risk_level.value, "❓ 未知")
    
    def _save_to_history(
        self,
        user_input: str,
        suggestion: Suggestion,
        result: ExecutionResult
    ):
        """
        保存到历史记录
        
        Args:
            user_input: 用户输入
            suggestion: AI 建议
            result: 执行结果
        """
        try:
            self.storage.save_history({
                "user_input": user_input,
                "command": suggestion.generated_command,
                "confidence": suggestion.confidence_score,
                "success": result.success,
                "output": result.output[:500] if result.output else "",  # 限制长度
                "error": result.error[:500] if result.error else "",
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat()
            })
        except Exception as e:
            self.log_engine.warning(f"Failed to save history: {e}")
    
    def interactive_mode(self):
        """
        交互式模式
        
        启动交互式命令行界面，持续接收用户输入并处理。
        用户可以输入中文自然语言，系统会翻译并执行相应的 PowerShell 命令。
        
        特殊命令:
            - exit, quit, 退出: 退出程序
            - help, 帮助: 显示帮助信息
            - history, 历史: 显示命令历史
            - clear, 清屏: 清空屏幕
        """
        # 启动新会话
        self.context_manager.start_session()
        
        print("=" * 60)
        print("🚀 AI PowerShell 智能助手 - 交互模式")
        print("=" * 60)
        print("输入中文描述，我会帮你生成并执行 PowerShell 命令")
        print("特殊命令: exit/quit/退出 - 退出程序")
        print("         help/帮助 - 显示帮助")
        print("         history/历史 - 显示命令历史")
        print("         clear/清屏 - 清空屏幕")
        print("=" * 60)
        print()
        
        while True:
            try:
                # 获取用户输入
                user_input = input("💬 请输入 > ").strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n👋 再见！")
                    break
                
                if user_input.lower() in ['help', '帮助']:
                    self._show_help()
                    continue
                
                if user_input.lower() in ['history', '历史']:
                    self._show_history()
                    continue
                
                if user_input.lower() in ['clear', '清屏']:
                    self._clear_screen()
                    continue
                
                # 处理正常请求
                result = self.process_request(user_input, auto_execute=False)
                
                # 显示结果
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 检测到 Ctrl+C，正在退出...")
                break
            except EOFError:
                print("\n\n👋 检测到 EOF，正在退出...")
                break
            except Exception as e:
                self.log_engine.log_error(e)
                print(f"\n❌ 发生错误: {str(e)}")
        
        # 结束会话
        self.context_manager.end_session()
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n" + "=" * 60)
        print("📖 帮助信息")
        print("=" * 60)
        print("AI PowerShell 智能助手可以将中文自然语言转换为 PowerShell 命令")
        print("\n使用示例:")
        print("  - 显示当前时间")
        print("  - 列出当前目录的所有文件")
        print("  - 查看CPU使用率最高的5个进程")
        print("  - 测试网络连接到 www.baidu.com")
        print("\n特殊命令:")
        print("  - exit/quit/退出: 退出程序")
        print("  - help/帮助: 显示此帮助信息")
        print("  - history/历史: 显示命令历史")
        print("  - clear/清屏: 清空屏幕")
        print("=" * 60 + "\n")
    
    def _show_history(self):
        """显示命令历史"""
        print("\n" + "=" * 60)
        print("📜 命令历史")
        print("=" * 60)
        
        recent_commands = self.context_manager.get_recent_commands(limit=10)
        
        if not recent_commands:
            print("暂无历史记录")
        else:
            for i, cmd_entry in enumerate(recent_commands, 1):
                status = "✅" if cmd_entry.status.value == "completed" else "❌"
                print(f"{i}. {status} {cmd_entry.user_input}")
                print(f"   命令: {cmd_entry.translated_command}")
                print(f"   时间: {cmd_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        
        print("=" * 60 + "\n")
    
    def _clear_screen(self):
        """清空屏幕"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _display_result(self, result: ExecutionResult):
        """
        显示执行结果
        
        Args:
            result: 执行结果对象
        """
        print("\n" + "-" * 60)
        
        if result.success:
            print("✅ 执行成功")
            if result.has_output:
                print(f"\n📄 输出:")
                print(result.output)
        else:
            print("❌ 执行失败")
            if result.has_error:
                print(f"\n🚫 错误:")
                print(result.error)
        
        if result.execution_time > 0:
            print(f"\n⏱️  执行时间: {result.execution_time:.3f} 秒")
        
        print("-" * 60 + "\n")


def main():
    """
    主函数 - 命令行模式入口
    
    支持两种使用模式:
    1. 交互模式: 不带参数启动，进入交互式命令行界面
    2. 单次执行模式: 通过 -c 参数指定要翻译的中文描述
    
    命令行参数:
        -c, --command: 要翻译的中文描述
        -a, --auto: 自动执行，不需要用户确认
        --config: 配置文件路径
        -v, --version: 显示版本信息
    """
    parser = argparse.ArgumentParser(
        description="AI PowerShell 智能助手 - 中文自然语言到 PowerShell 命令的智能转换",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互模式
  python -m src.main
  
  # 单次执行
  python -m src.main -c "显示当前时间"
  
  # 自动执行（不需要确认）
  python -m src.main -c "列出所有文件" -a
  
  # 使用自定义配置
  python -m src.main --config /path/to/config.yaml
        """
    )
    
    parser.add_argument(
        '-c', '--command',
        type=str,
        help='要翻译的中文描述（单次执行模式）'
    )
    
    parser.add_argument(
        '-a', '--auto',
        action='store_true',
        help='自动执行，不需要用户确认'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='AI PowerShell Assistant v2.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化助手
        assistant = PowerShellAssistant(config_path=args.config)
        
        if args.command:
            # 单次执行模式
            result = assistant.process_request(args.command, auto_execute=args.auto)
            assistant._display_result(result)
            
            # 返回适当的退出码
            sys.exit(0 if result.success else 1)
        else:
            # 交互模式
            assistant.interactive_mode()
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n👋 程序被中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生致命错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
