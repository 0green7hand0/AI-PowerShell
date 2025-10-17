"""
AI PowerShell 智能助手 - 主入口和控制器

本模块实现主控制器类 PowerShellAssistant，负责协调各个组件的工作，
处理用户请求，并提供交互式和命令行两种使用模式。
"""

import sys
import argparse
import uuid
import time
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
from src.template_engine import TemplateEngine
from src.template_engine.custom_template_manager import CustomTemplateManager
from src.template_engine.exceptions import TemplateError
from src.ui import (
    ErrorHandler, UIConfig, UIManager, ProgressManager,
    InteractiveInputManager, HelpSystem, UIConfigLoader, UIConfigManager,
    UICompatibilityLayer, create_compatible_ui_config
)
from src.ui.error_handler import ErrorCategory


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
        
        # 8. 初始化模板引擎
        try:
            self.template_engine = TemplateEngine(
                self.config.model_dump(),
                ai_provider=self.ai_engine.translator.ai_provider if hasattr(self.ai_engine.translator, 'ai_provider') else None
            )
            self.log_engine.info("Template engine initialized")
        except Exception as e:
            self.log_engine.warning(f"Template engine initialization failed: {e}")
            self.template_engine = None
        
        # 9. 初始化自定义模板管理器
        try:
            if self.template_engine:
                self.custom_template_manager = CustomTemplateManager(
                    templates_dir="templates",
                    config_path="config/templates.yaml"
                )
                self.log_engine.info("Custom template manager initialized")
            else:
                self.custom_template_manager = None
        except Exception as e:
            self.log_engine.warning(f"Custom template manager initialization failed: {e}")
            self.custom_template_manager = None
        
        # 10. 初始化 UI 系统
        try:
            # 初始化 UI 配置管理器
            self.ui_config_manager = UIConfigManager()
            original_config = self.ui_config_manager.get_config()
            
            # 应用兼容性层，根据终端能力调整配置
            self.ui_compatibility = UICompatibilityLayer(original_config)
            self.ui_config = self.ui_compatibility.get_config()
            
            # 初始化 UI 管理器
            self.ui_manager = UIManager(self.ui_config)
            
            # 初始化错误处理器
            self.error_handler = ErrorHandler(self.ui_config)
            
            # 初始化进度管理器
            self.progress_manager = ProgressManager(self.ui_manager.console, self.ui_config)
            
            # 初始化交互式输入管理器
            self.interactive_input = InteractiveInputManager(self.ui_manager)
            
            # 初始化帮助系统
            self.help_system = HelpSystem(self.ui_manager)
            
            self.log_engine.info("UI system initialized")
        except Exception as e:
            self.log_engine.warning(f"UI system initialization failed: {e}")
            self.ui_manager = None
            self.error_handler = None
            self.progress_manager = None
            self.interactive_input = None
            self.help_system = None
        
        self.log_engine.info("PowerShell Assistant initialization complete")
    
    def process_request(self, user_input: str, auto_execute: bool = False) -> ExecutionResult:
        """
        处理用户请求的完整流程
        
        这是核心的请求处理方法，实现了从用户输入到命令执行的完整流程：
        1. 检查是否是脚本生成请求
        2. 如果是脚本生成，使用模板引擎处理
        3. 否则使用原有的命令翻译流程
        
        Args:
            user_input: 用户输入的中文自然语言
            auto_execute: 是否自动执行（跳过用户确认）
            
        Returns:
            ExecutionResult: 命令执行结果
        """
        # 检查是否是脚本生成请求
        if self._is_script_generation_request(user_input):
            return self._handle_script_generation(user_input, auto_execute)
        
        # 否则使用原有的命令翻译流程
        return self._handle_command_translation(user_input, auto_execute)
    
    def _is_script_generation_request(self, user_input: str) -> bool:
        """
        判断是否是脚本生成请求
        
        Args:
            user_input: 用户输入
            
        Returns:
            bool: 是否是脚本生成请求
        """
        keywords = ['生成脚本', '创建脚本', '写个脚本', '帮我写', '生成一个脚本']
        return any(keyword in user_input for keyword in keywords)
    
    def _handle_command_translation(self, user_input: str, auto_execute: bool = False) -> ExecutionResult:
        """
        处理命令翻译请求（原有流程）
        
        Args:
            user_input: 用户输入
            auto_execute: 是否自动执行
            
        Returns:
            ExecutionResult: 执行结果
        """
        # 1. 生成关联 ID 并记录请求
        correlation_id = str(uuid.uuid4())
        self.log_engine.log_request(user_input, correlation_id=correlation_id)
        
        try:
            # 2. 获取当前上下文
            context = self._build_context()
            
            # 3. AI 翻译
            self.log_engine.info(f"Translating input: {user_input}")
            
            # 使用进度指示器显示翻译过程
            if self.progress_manager:
                with self.progress_manager.create_spinner("正在翻译命令...") as spinner:
                    suggestion = self.ai_engine.translate_natural_language(user_input, context)
                    spinner.update("翻译完成")
            else:
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
            
            # 使用错误处理器显示友好的错误消息
            if self.error_handler:
                self.error_handler.display_error(
                    e,
                    details=f"处理用户输入时发生错误: {user_input}",
                    suggestions=[
                        "检查输入的命令描述是否清晰",
                        "尝试使用更简单的描述",
                        "查看日志文件获取详细错误信息",
                    ],
                    related_commands=["help", "history"]
                )
            
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
        if self.ui_manager:
            # 使用增强的 UI 显示
            self.ui_manager.print_newline()
            self.ui_manager.print_header("🤖 AI 翻译结果")
            
            # 显示命令信息
            info_data = {
                "原始输入": suggestion.original_input,
                "生成命令": suggestion.generated_command,
                "置信度": f"{suggestion.confidence_score:.2%}",
                "说明": suggestion.explanation
            }
            self.ui_manager.print_dict(info_data)
            
            # 显示警告
            if validation.warnings:
                self.ui_manager.print_newline()
                self.ui_manager.print_warning("警告信息:", icon=True)
                for warning in validation.warnings:
                    self.ui_manager.console.print(f"  - {warning}", style="warning")
            
            # 显示权限要求
            if validation.requires_elevation:
                self.ui_manager.print_newline()
                self.ui_manager.print_info("🔐 此命令需要管理员权限", icon=False)
            
            # 显示风险等级
            self.ui_manager.print_newline()
            risk_display = self._format_risk_level(validation.risk_level)
            self.ui_manager.console.print(f"风险等级: {risk_display}")
            
            self.ui_manager.print_separator()
            self.ui_manager.print_newline()
        else:
            # 降级到基本显示
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
    
    def _handle_script_generation(self, user_input: str, auto_execute: bool = False) -> ExecutionResult:
        """
        处理脚本生成请求
        
        Args:
            user_input: 用户输入
            auto_execute: 是否自动执行
            
        Returns:
            ExecutionResult: 执行结果
        """
        if not self.template_engine:
            error_msg = "模板引擎未初始化，无法生成脚本"
            
            if self.error_handler:
                self.error_handler.display_error(
                    Exception(error_msg),
                    category=ErrorCategory.CONFIG_ERROR,
                    suggestions=[
                        "检查配置文件中的模板引擎设置",
                        "确认模板目录存在且可访问",
                        "尝试重新启动程序",
                    ]
                )
            
            return ExecutionResult(
                success=False,
                command="",
                error=error_msg,
                return_code=-1
            )
        
        print("\n🤖 正在生成脚本...")
        print("=" * 60)
        
        try:
            # 使用模板引擎生成脚本
            generated_script = self.template_engine.process_request(
                user_input,
                use_ai=False  # 暂时使用简单替换，避免AI调用问题
            )
            
            if not generated_script:
                error_msg = "无法生成脚本，请尝试更具体的描述"
                
                if self.error_handler:
                    self.error_handler.display_error(
                        Exception(error_msg),
                        category=ErrorCategory.USER_ERROR,
                        suggestions=[
                            "提供更详细的脚本需求描述",
                            "使用 'template list' 查看可用模板",
                            "参考示例命令格式",
                        ],
                        related_commands=["template list", "help"]
                    )
                
                return ExecutionResult(
                    success=False,
                    command="",
                    error=error_msg,
                    return_code=-1
                )
            
            # 显示生成的脚本信息
            self._display_generated_script(generated_script)
            
            # 询问是否执行
            if not auto_execute:
                response = input("\n是否执行此脚本? (y/N): ").strip().lower()
                if response not in ['y', 'yes', '是']:
                    print(f"\n脚本已保存到: {generated_script.file_path}")
                    print("未执行")
                    return ExecutionResult(
                        success=True,
                        command=f"Script saved: {generated_script.file_path}",
                        output=f"脚本已保存，未执行",
                        return_code=0
                    )
            
            # 执行脚本
            print("\n🚀 正在执行脚本...")
            result = self.executor.execute_script_file(generated_script.file_path)
            
            # 显示结果
            self._display_result(result)
            
            return result
            
        except Exception as e:
            self.log_engine.error(f"Script generation failed: {str(e)}")
            
            # 使用错误处理器显示友好的错误消息
            if self.error_handler:
                self.error_handler.display_error(
                    e,
                    details=f"生成脚本时发生错误: {user_input}",
                    suggestions=[
                        "检查模板配置是否正确",
                        "确认所需参数都已提供",
                        "查看日志文件获取详细错误信息",
                    ],
                    related_commands=["template list", "template test"],
                    show_traceback=False
                )
            else:
                import traceback
                traceback.print_exc()
            
            return ExecutionResult(
                success=False,
                command="",
                error=f"脚本生成失败: {str(e)}",
                return_code=-1
            )
    
    def _display_generated_script(self, script):
        """
        显示生成的脚本信息
        
        Args:
            script: GeneratedScript对象
        """
        print("\n✓ 脚本生成完成!")
        print("=" * 60)
        print(f"📄 脚本信息:")
        print(f"  模板: {script.template_name}")
        print(f"  文件: {script.file_path}")
        print(f"  用户需求: {script.user_request}")
        
        if script.parameters:
            print(f"\n📋 参数:")
            for key, value in script.parameters.items():
                print(f"  {key}: {value}")
        
        print("\n📝 脚本预览 (前20行):")
        print("-" * 60)
        lines = script.content.split('\n')[:20]
        for line in lines:
            print(line)
        if len(script.content.split('\n')) > 20:
            print("...")
        print("-" * 60)
    
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
        session_start_time = time.time()
        commands_executed = 0
        successful_commands = 0
        failed_commands = 0
        
        # 运行启动体验
        from src.ui.startup_experience import StartupExperience
        startup = StartupExperience()
        startup_success = startup.run_startup_sequence()
        
        if not startup_success:
            self.log_engine.warning("Startup checks failed, but continuing anyway")
        
        while True:
            try:
                # 获取用户输入 - 使用增强的交互式输入系统
                if self.interactive_input:
                    user_input = self.interactive_input.get_user_input("💬 请输入 > ")
                else:
                    user_input = input("💬 请输入 > ").strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n👋 再见！")
                    break
                
                if user_input.lower() in ['help', '帮助']:
                    if self.help_system:
                        self.help_system.show_main_help()
                    else:
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
                
                # 更新统计
                commands_executed += 1
                if result.success:
                    successful_commands += 1
                else:
                    failed_commands += 1
                
                # 显示结果
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 检测到 Ctrl+C，正在退出...")
                break
            except EOFError:
                print("\n\n👋 检测到 EOF，正在退出...")
                break
            except Exception as e:
                self.log_engine.error(f"Error in interactive mode: {str(e)}")
                
                # 使用错误处理器显示友好的错误消息
                if self.error_handler:
                    self.error_handler.display_error(
                        e,
                        details="交互模式执行时发生错误",
                        suggestions=[
                            "检查输入命令是否正确",
                            "使用 'help' 查看可用命令",
                            "查看日志文件获取详细信息",
                        ],
                        show_traceback=False
                    )
                else:
                    print(f"\n❌ 发生错误: {str(e)}")
        
        # 显示会话摘要
        session_duration = time.time() - session_start_time
        startup.display_session_summary({
            'commands_executed': commands_executed,
            'successful_commands': successful_commands,
            'failed_commands': failed_commands,
            'session_duration': session_duration,
        })
        
        # 结束会话
        self.context_manager.terminate_session()
    
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
        from src.ui import UIManager, TableManager, ColumnConfig, TableConfig
        
        ui_manager = UIManager()
        table_manager = TableManager(ui_manager.console)
        
        recent_commands = self.context_manager.get_recent_commands(limit=20)
        
        if not recent_commands:
            ui_manager.print_info("暂无历史记录")
            return
        
        ui_manager.print_header("📜 命令历史", f"最近 {len(recent_commands)} 条")
        
        # 转换为表格数据
        history_data = []
        for i, cmd_entry in enumerate(recent_commands, 1):
            history_data.append({
                'index': str(i),
                'status': '✓' if cmd_entry.status.value == "completed" else '✗',
                'input': cmd_entry.user_input[:40] + '...' if len(cmd_entry.user_input) > 40 else cmd_entry.user_input,
                'command': cmd_entry.translated_command[:50] + '...' if len(cmd_entry.translated_command) > 50 else cmd_entry.translated_command,
                'time': cmd_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        columns = [
            ColumnConfig(name='index', header='#', width=4, justify='right', style='muted'),
            ColumnConfig(name='status', header='状态', width=6, justify='center', style='bold'),
            ColumnConfig(name='input', header='用户输入', width=35, style='primary'),
            ColumnConfig(name='command', header='执行命令', width=40, style='secondary'),
            ColumnConfig(name='time', header='时间', width=20, style='muted'),
        ]
        
        config = TableConfig(show_lines=False, box_style='rounded')
        table_manager.display_table(history_data, columns, config)
        
        ui_manager.print_newline()
    
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
        if self.ui_manager:
            # 使用增强的 UI 显示
            self.ui_manager.print_newline()
            self.ui_manager.print_separator("-", 60)
            
            if result.success:
                self.ui_manager.print_success("执行成功")
                if result.has_output:
                    self.ui_manager.print_newline()
                    self.ui_manager.console.print("📄 输出:", style="info")
                    self.ui_manager.console.print(result.output)
            else:
                self.ui_manager.print_error("执行失败")
                if result.has_error:
                    self.ui_manager.print_newline()
                    self.ui_manager.console.print("🚫 错误:", style="error")
                    self.ui_manager.console.print(result.error, style="error")
            
            if result.execution_time > 0:
                self.ui_manager.print_newline()
                self.ui_manager.console.print(
                    f"⏱️  执行时间: {result.execution_time:.3f} 秒",
                    style="muted"
                )
            
            self.ui_manager.print_separator("-", 60)
            self.ui_manager.print_newline()
        else:
            # 降级到基本显示
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


def template_create_command(assistant: PowerShellAssistant):
    """处理 template create 命令 - 创建自定义模板"""
    if not assistant.custom_template_manager:
        error = Exception("自定义模板管理器未初始化")
        if assistant.error_handler:
            assistant.error_handler.display_error(
                error,
                category=ErrorCategory.CONFIG_ERROR,
                suggestions=[
                    "检查配置文件中的模板管理器设置",
                    "确认模板目录存在且可访问",
                    "尝试重新启动程序",
                ]
            )
        else:
            print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用新的交互式向导
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 运行交互式向导
        template_data = ui.interactive_template_wizard()
        
        if not template_data:
            return 1
        
        # 显示进度
        steps = [
            "验证模板信息",
            "解析脚本参数",
            "生成模板文件",
            "更新配置文件"
        ]
        
        with ui.show_progress_for_operation("创建模板", steps) as progress:
            # 创建模板
            template = assistant.custom_template_manager.create_template(
                name=template_data['name'],
                description=template_data['description'],
                category=template_data['category'],
                script_content=template_data['script_content'],
                keywords=template_data['keywords']
            )
        
        # 显示操作摘要
        details = {
            '分类': template.category,
            '文件路径': template.file_path,
            '参数数量': len(template.parameters) if template.parameters else 0,
            '关键词': ', '.join(template_data['keywords']) if template_data['keywords'] else '无'
        }
        
        ui.display_operation_summary('create', template, True, details)
        
        return 0
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板名称是否已存在",
                    "确认脚本内容格式正确",
                    "参考文档中的模板创建示例",
                ],
                related_commands=["template list"]
            )
        else:
            print(f"\n❌ 创建失败: {str(e)}")
        return 1
    except Exception as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                details="创建模板时发生未预期的错误",
                show_traceback=False
            )
        else:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        return 1


def template_list_command(assistant: PowerShellAssistant, custom_only: bool = False):
    """处理 template list 命令 - 列出模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的模板显示界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板列表
        if custom_only:
            templates = assistant.custom_template_manager.list_custom_templates()
            title = "📋 自定义模板列表"
        else:
            # 获取所有模板（系统 + 自定义）
            templates = assistant.custom_template_manager.list_custom_templates()
            # 如果有 template_manager，也包含系统模板
            if hasattr(assistant, 'template_manager') and assistant.template_manager:
                system_templates = assistant.template_manager.list_templates()
                templates.extend(system_templates)
            title = "📋 模板列表"
        
        # 显示增强的模板列表
        ui.display_template_list_enhanced(
            templates,
            title=title,
            show_icons=True,
            group_by_category=True
        )
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_edit_command(assistant: PowerShellAssistant, template_id: str):
    """处理 template edit 命令 - 编辑模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的编辑界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板信息
        template_info = assistant.custom_template_manager.get_template_info(template_id, 'custom')
        if not template_info:
            ui.ui_manager.print_error(f"模板不存在: {template_id}")
            return 1
        
        # 创建临时模板对象用于显示
        from types import SimpleNamespace
        template = SimpleNamespace(**template_info)
        
        # 运行交互式编辑器
        updates = ui.interactive_template_editor(template)
        
        if not updates:
            return 0
        
        # 显示进度
        steps = [
            "验证更新信息",
            "应用更新",
            "更新配置文件"
        ]
        
        with ui.show_progress_for_operation("更新模板", steps) as progress:
            # 应用更新
            updated_template = assistant.custom_template_manager.edit_template(
                template_id,
                'custom',
                updates
            )
        
        # 显示操作摘要
        details = {
            '更新字段': ', '.join(updates.keys()),
            '新名称': updated_template.name if 'name' in updates else template.name,
            '新描述': updated_template.description if 'description' in updates else template.description
        }
        
        ui.display_operation_summary('edit', updated_template, True, details)
        
        return 0
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板 ID 是否正确",
                    "确认模板是自定义模板",
                    "使用 'template list' 查看可用模板",
                ]
            )
        else:
            print(f"\n❌ 编辑失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_delete_command(assistant: PowerShellAssistant, template_id: str):
    """处理 template delete 命令 - 删除模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的删除确认界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板信息
        template_info = assistant.custom_template_manager.get_template_info(template_id, 'custom')
        if not template_info:
            ui.ui_manager.print_error(f"模板不存在: {template_id}")
            return 1
        
        # 创建临时模板对象用于显示
        from types import SimpleNamespace
        template = SimpleNamespace(**template_info)
        
        # 显示删除确认对话框
        confirmed = ui.confirm_template_deletion(template)
        
        if not confirmed:
            ui.ui_manager.print_warning("已取消删除")
            return 0
        
        # 显示进度
        steps = [
            "删除模板文件",
            "更新配置文件",
            "清理相关资源"
        ]
        
        with ui.show_progress_for_operation("删除模板", steps) as progress:
            # 执行删除
            success = assistant.custom_template_manager.delete_template(template_id, 'custom')
        
        if success:
            # 显示操作摘要
            details = {
                '模板名称': template.name,
                '分类': template.category,
                '文件路径': template.file_path
            }
            ui.display_operation_summary('delete', template, True, details)
            return 0
        else:
            ui.ui_manager.print_error("删除失败")
            return 1
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板 ID 是否正确",
                    "确认模板是自定义模板",
                    "使用 'template list' 查看可用模板",
                ]
            )
        else:
            print(f"\n❌ 删除失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_export_command(assistant: PowerShellAssistant, template_id: str, output_path: str):
    """处理 template export 命令 - 导出模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"📦 导出模板: {template_id}")
        print("=" * 60)
        
        # 导出模板
        print("\n正在导出模板...")
        exported_path = assistant.custom_template_manager.export_template(template_id, output_path)
        
        print(f"\n✅ 模板已导出到: {exported_path}")
        print("=" * 60)
        
        return 0
        
    except TemplateError as e:
        print(f"\n❌ 导出失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_import_command(assistant: PowerShellAssistant, package_path: str, overwrite: bool = False):
    """处理 template import 命令 - 导入模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"📥 导入模板")
        print("=" * 60)
        
        if not Path(package_path).exists():
            print(f"\n❌ 文件不存在: {package_path}")
            return 1
        
        # 导入模板
        print(f"\n正在导入模板包: {package_path}")
        template = assistant.custom_template_manager.import_template(package_path, overwrite=overwrite)
        
        print(f"\n✅ 模板导入成功!")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        print("=" * 60)
        
        return 0
        
    except TemplateError as e:
        print(f"\n❌ 导入失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_history_command(assistant: PowerShellAssistant, template_id: str):
    """处理 template history 命令 - 查看模板历史"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        from src.ui import UIManager, TemplateDisplay
        
        ui_manager = UIManager()
        template_display = TemplateDisplay(ui_manager)
        
        # 获取历史版本
        versions = assistant.custom_template_manager.version_control.list_versions(template_id)
        
        template_display.display_version_history(versions, template_id)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_restore_command(assistant: PowerShellAssistant, template_id: str, version: int):
    """处理 template restore 命令 - 恢复模板版本"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"🔄 恢复模板版本")
        print("=" * 60)
        
        # 确认恢复
        print(f"\n将恢复模板 '{template_id}' 到版本 {version}")
        confirm = input("确认恢复? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', '是']:
            print("\n❌ 取消恢复")
            return 1
        
        # 恢复版本
        print("\n正在恢复版本...")
        success = assistant.custom_template_manager.version_control.restore_version(template_id, version)
        
        if success:
            print(f"\n✅ 已恢复到版本 {version}")
            return 0
        else:
            print("\n❌ 恢复失败")
            return 1
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_config_show_command(assistant: PowerShellAssistant):
    """处理 ui config show 命令 - 显示当前 UI 配置"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        from src.ui import UIManager
        
        ui = UIManager(assistant.ui_config)
        
        ui.print_header("⚙️ UI 配置", "当前配置信息")
        
        config_data = {
            "彩色输出": "启用" if assistant.ui_config.enable_colors else "禁用",
            "图标显示": "启用" if assistant.ui_config.enable_icons else "禁用",
            "进度指示": "启用" if assistant.ui_config.enable_progress else "禁用",
            "动画效果": "启用" if assistant.ui_config.enable_animations else "禁用",
            "当前主题": assistant.ui_config.theme,
            "图标样式": assistant.ui_config.icon_style.value,
            "表格最大宽度": str(assistant.ui_config.max_table_width),
            "分页大小": str(assistant.ui_config.page_size),
            "自动分页": "启用" if assistant.ui_config.auto_pager else "禁用",
        }
        
        ui.print_dict(config_data)
        ui.print_newline()
        
        # 显示可用主题
        themes = assistant.ui_config_manager.get_available_themes()
        if themes:
            ui.print_info("可用主题:", icon=True)
            ui.print_list(themes)
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_config_set_command(assistant: PowerShellAssistant, key: str, value: str):
    """处理 ui config set 命令 - 设置 UI 配置项"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        # 解析值
        bool_values = {'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False}
        
        updates = {}
        
        # 处理不同的配置项
        if key == 'theme':
            success = assistant.ui_config_manager.switch_theme(value)
            if success:
                print(f"✅ 主题已切换为: {value}")
                return 0
            else:
                print(f"❌ 切换主题失败")
                return 1
        elif key == 'icon_style':
            success = assistant.ui_config_manager.set_icon_style(value)
            if success:
                print(f"✅ 图标样式已设置为: {value}")
                return 0
            else:
                print(f"❌ 设置图标样式失败")
                return 1
        elif key in ['colors', 'icons', 'progress', 'animations']:
            if value.lower() not in bool_values:
                print(f"❌ 无效的值: {value}，请使用 true/false")
                return 1
            enabled = bool_values[value.lower()]
            success = assistant.ui_config_manager.toggle_feature(key, enabled)
            if success:
                status = "启用" if enabled else "禁用"
                print(f"✅ {key} 已{status}")
                return 0
            else:
                print(f"❌ 设置失败")
                return 1
        elif key == 'max_table_width':
            try:
                width = int(value)
                updates['max_table_width'] = width
            except ValueError:
                print(f"❌ 无效的宽度值: {value}")
                return 1
        elif key == 'page_size':
            try:
                size = int(value)
                updates['page_size'] = size
            except ValueError:
                print(f"❌ 无效的大小值: {value}")
                return 1
        elif key == 'auto_pager':
            if value.lower() not in bool_values:
                print(f"❌ 无效的值: {value}，请使用 true/false")
                return 1
            updates['auto_pager'] = bool_values[value.lower()]
        else:
            print(f"❌ 未知的配置项: {key}")
            return 1
        
        if updates:
            success = assistant.ui_config_manager.update_config(updates)
            if success:
                print(f"✅ 配置已更新: {key} = {value}")
                return 0
            else:
                print(f"❌ 更新配置失败")
                return 1
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_config_reset_command(assistant: PowerShellAssistant):
    """处理 ui config reset 命令 - 重置 UI 配置"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        print("\n⚠️  警告: 这将重置所有 UI 配置为默认值")
        confirm = input("确认重置? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', '是']:
            print("❌ 取消重置")
            return 0
        
        success = assistant.ui_config_manager.reset_to_defaults()
        if success:
            print("✅ UI 配置已重置为默认值")
            return 0
        else:
            print("❌ 重置失败")
            return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_check_command(assistant: PowerShellAssistant):
    """处理 ui check 命令 - 检查终端兼容性"""
    try:
        if hasattr(assistant, 'ui_compatibility') and assistant.ui_compatibility:
            assistant.ui_compatibility.print_compatibility_info()
        else:
            # 如果没有兼容性层，创建一个临时的
            from src.ui import UICompatibilityLayer
            compat = UICompatibilityLayer()
            compat.print_compatibility_info()
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_test_command(assistant: PowerShellAssistant, template_id: str, show_script: bool = True):
    """处理 template test 命令 - 测试模板"""
    if not assistant.template_engine:
        print("❌ 模板引擎未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"🧪 测试模板")
        print("=" * 60)
        
        # 从模板引擎获取模板
        # 模板ID格式: category.template_name
        template = None
        for tmpl in assistant.template_engine.template_manager.templates.values():
            if tmpl.id == template_id:
                template = tmpl
                break
        
        if not template:
            print(f"\n❌ 未找到模板: {template_id}")
            print("\n💡 提示: 使用 'template list' 查看可用模板")
            return 1
        
        print(f"\n模板: {template.name}")
        print(f"描述: {template.description}")
        
        # 执行测试
        print("\n正在生成测试参数...")
        from src.template_engine.template_validator import TemplateValidator
        validator = TemplateValidator()
        
        test_result = validator.test_template(template)
        
        # 显示测试参数
        print("\n📋 测试参数:")
        print("-" * 60)
        if test_result['test_parameters']:
            for param_name, param_value in test_result['test_parameters'].items():
                param_info = template.parameters.get(param_name)
                param_type = param_info.type if param_info else "unknown"
                print(f"  {param_name} ({param_type}): {param_value}")
        else:
            print("  (无参数)")
        
        # 显示生成的脚本
        if show_script and test_result['generated_script']:
            print("\n📄 生成的脚本预览:")
            print("-" * 60)
            script_lines = test_result['generated_script'].split('\n')
            # 显示前20行
            for i, line in enumerate(script_lines[:20], 1):
                print(f"{i:3d} | {line}")
            if len(script_lines) > 20:
                print(f"... (共 {len(script_lines)} 行，仅显示前 20 行)")
        
        # 显示验证结果
        print("\n✅ 验证结果:")
        print("-" * 60)
        
        if test_result['success']:
            print("  ✓ 语法验证通过")
            print("  ✓ 脚本生成成功")
        else:
            print("  ✗ 测试失败")
        
        # 显示错误
        if test_result['errors']:
            print("\n❌ 错误:")
            for error in test_result['errors']:
                print(f"  • {error}")
        
        # 显示警告
        if test_result['warnings']:
            print("\n⚠️  警告:")
            for warning in test_result['warnings']:
                print(f"  • {warning}")
        
        # 返回状态
        if test_result['success']:
            print("\n✅ 模板测试通过")
            return 0
        else:
            print("\n❌ 模板测试失败")
            return 1
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """
    主函数 - 命令行模式入口
    
    支持两种使用模式:
    1. 交互模式: 不带参数启动，进入交互式命令行界面
    2. 单次执行模式: 通过 -c 参数指定要翻译的中文描述
    3. 模板管理模式: 通过 template 子命令管理自定义模板
    
    命令行参数:
        -c, --command: 要翻译的中文描述
        -a, --auto: 自动执行，不需要用户确认
        --config: 配置文件路径
        -v, --version: 显示版本信息
        template: 模板管理子命令
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
  
  # 模板管理
  python -m src.main template create
  python -m src.main template list
  python -m src.main template edit <template_id>
  python -m src.main template delete <template_id>
  python -m src.main template export <template_id> -o <output_path>
  python -m src.main template import <package_path>
  python -m src.main template history <template_id>
  python -m src.main template restore <template_id> <version>
  python -m src.main template test <template_id>
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
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest='subcommand', help='子命令')
    
    # template 子命令
    template_parser = subparsers.add_parser('template', help='模板管理')
    template_subparsers = template_parser.add_subparsers(dest='template_action', help='模板操作')
    
    # template create
    create_parser = template_subparsers.add_parser('create', help='创建自定义模板')
    
    # template list
    list_parser = template_subparsers.add_parser('list', help='列出所有自定义模板')
    list_parser.add_argument('--custom-only', action='store_true', help='仅显示自定义模板')
    
    # template edit
    edit_parser = template_subparsers.add_parser('edit', help='编辑模板')
    edit_parser.add_argument('template_id', help='模板ID')
    
    # template delete
    delete_parser = template_subparsers.add_parser('delete', help='删除模板')
    delete_parser.add_argument('template_id', help='模板ID')
    
    # template export
    export_parser = template_subparsers.add_parser('export', help='导出模板')
    export_parser.add_argument('template_id', help='模板ID')
    export_parser.add_argument('-o', '--output', required=True, help='输出路径')
    
    # template import
    import_parser = template_subparsers.add_parser('import', help='导入模板')
    import_parser.add_argument('package_path', help='模板包路径')
    import_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的模板')
    
    # template history
    history_parser = template_subparsers.add_parser('history', help='查看模板历史')
    history_parser.add_argument('template_id', help='模板ID')
    
    # template restore
    restore_parser = template_subparsers.add_parser('restore', help='恢复模板版本')
    restore_parser.add_argument('template_id', help='模板ID')
    restore_parser.add_argument('version', type=int, help='版本号')
    
    # template test
    test_parser = template_subparsers.add_parser('test', help='测试模板')
    test_parser.add_argument('template_id', help='模板ID')
    test_parser.add_argument('--no-script', action='store_true', help='不显示生成的脚本')
    
    # ui 子命令
    ui_parser = subparsers.add_parser('ui', help='UI 配置管理')
    ui_subparsers = ui_parser.add_subparsers(dest='ui_action', help='UI 操作')
    
    # ui config show
    ui_show_parser = ui_subparsers.add_parser('show', help='显示当前 UI 配置')
    
    # ui config set
    ui_set_parser = ui_subparsers.add_parser('set', help='设置 UI 配置项')
    ui_set_parser.add_argument('key', help='配置项名称')
    ui_set_parser.add_argument('value', help='配置项值')
    
    # ui config reset
    ui_reset_parser = ui_subparsers.add_parser('reset', help='重置 UI 配置为默认值')
    
    # ui check
    ui_check_parser = ui_subparsers.add_parser('check', help='检查终端兼容性')
    
    args = parser.parse_args()
    
    try:
        # 初始化助手
        assistant = PowerShellAssistant(config_path=args.config)
        
        # 处理模板管理子命令
        if args.subcommand == 'template':
            if not args.template_action:
                print("❌ 请指定模板操作命令")
                print("使用 'python -m src.main template --help' 查看帮助")
                sys.exit(1)
            
            # 根据不同的模板操作调用相应的函数
            if args.template_action == 'create':
                exit_code = template_create_command(assistant)
            elif args.template_action == 'list':
                exit_code = template_list_command(assistant, args.custom_only)
            elif args.template_action == 'edit':
                exit_code = template_edit_command(assistant, args.template_id)
            elif args.template_action == 'delete':
                exit_code = template_delete_command(assistant, args.template_id)
            elif args.template_action == 'export':
                exit_code = template_export_command(assistant, args.template_id, args.output)
            elif args.template_action == 'import':
                exit_code = template_import_command(assistant, args.package_path, args.overwrite)
            elif args.template_action == 'history':
                exit_code = template_history_command(assistant, args.template_id)
            elif args.template_action == 'restore':
                exit_code = template_restore_command(assistant, args.template_id, args.version)
            elif args.template_action == 'test':
                exit_code = template_test_command(assistant, args.template_id, not args.no_script)
            else:
                print(f"❌ 未知的模板操作: {args.template_action}")
                exit_code = 1
            
            sys.exit(exit_code)
        
        elif args.subcommand == 'ui':
            if not args.ui_action:
                print("❌ 请指定 UI 操作命令")
                print("使用 'python -m src.main ui --help' 查看帮助")
                sys.exit(1)
            
            # 根据不同的 UI 操作调用相应的函数
            if args.ui_action == 'show':
                exit_code = ui_config_show_command(assistant)
            elif args.ui_action == 'set':
                exit_code = ui_config_set_command(assistant, args.key, args.value)
            elif args.ui_action == 'reset':
                exit_code = ui_config_reset_command(assistant)
            elif args.ui_action == 'check':
                exit_code = ui_check_command(assistant)
            else:
                print(f"❌ 未知的 UI 操作: {args.ui_action}")
                exit_code = 1
            
            sys.exit(exit_code)
        
        elif args.command:
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
        # 尝试使用错误处理器
        try:
            error_handler = ErrorHandler(UIConfig())
            error_handler.display_error(
                e,
                category=ErrorCategory.SYSTEM_ERROR,
                details="程序启动或执行时发生致命错误",
                suggestions=[
                    "检查配置文件是否正确",
                    "确认所有依赖已正确安装",
                    "查看日志文件获取详细错误信息",
                    "尝试使用默认配置重新运行",
                ],
                show_traceback=True
            )
        except:
            # 如果错误处理器也失败，使用基本错误输出
            print(f"\n❌ 发生致命错误: {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main()
