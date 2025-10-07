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
from src.template_engine import TemplateEngine
from src.template_engine.custom_template_manager import CustomTemplateManager
from src.template_engine.exceptions import TemplateError


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
            return ExecutionResult(
                success=False,
                command="",
                error="模板引擎未初始化，无法生成脚本",
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
                return ExecutionResult(
                    success=False,
                    command="",
                    error="无法生成脚本，请尝试更具体的描述",
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


def template_create_command(assistant: PowerShellAssistant):
    """处理 template create 命令 - 创建自定义模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    print("\n" + "=" * 60)
    print("🎨 创建自定义模板")
    print("=" * 60)
    
    try:
        # 1. 模板基本信息
        print("\n1️⃣  模板基本信息")
        print("-" * 60)
        name = input("模板名称: ").strip()
        if not name:
            print("❌ 模板名称不能为空")
            return 1
        
        description = input("模板描述: ").strip()
        if not description:
            print("❌ 模板描述不能为空")
            return 1
        
        category = input("模板分类 (默认: custom): ").strip() or "custom"
        keywords_input = input("关键词 (逗号分隔): ").strip()
        keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else []
        
        # 2. 脚本来源
        print("\n2️⃣  脚本来源")
        print("-" * 60)
        print("[1] 从文件导入")
        print("[2] 直接输入脚本内容")
        choice = input("选择 (1/2): ").strip()
        
        script_content = ""
        if choice == "1":
            file_path = input("脚本文件路径: ").strip()
            if not Path(file_path).exists():
                print(f"❌ 文件不存在: {file_path}")
                return 1
            with open(file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        elif choice == "2":
            print("请输入脚本内容 (输入 'END' 结束):")
            lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            script_content = '\n'.join(lines)
        else:
            print("❌ 无效的选择")
            return 1
        
        if not script_content.strip():
            print("❌ 脚本内容不能为空")
            return 1
        
        # 3. 创建模板
        print("\n3️⃣  正在创建模板...")
        print("-" * 60)
        
        template = assistant.custom_template_manager.create_template(
            name=name,
            description=description,
            category=category,
            script_content=script_content,
            keywords=keywords
        )
        
        print("\n✅ 模板创建成功!")
        print("=" * 60)
        print(f"📄 模板信息:")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        print(f"  文件: {template.file_path}")
        if template.parameters:
            print(f"  参数数量: {len(template.parameters)}")
        if keywords:
            print(f"  关键词: {', '.join(keywords)}")
        print("=" * 60)
        
        return 0
        
    except TemplateError as e:
        print(f"\n❌ 创建失败: {str(e)}")
        return 1
    except Exception as e:
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
        print("\n" + "=" * 60)
        print("📋 模板列表")
        print("=" * 60)
        
        templates = assistant.custom_template_manager.list_custom_templates()
        
        if not templates:
            print("\n暂无自定义模板")
            print("\n💡 提示: 使用 'template create' 命令创建新模板")
        else:
            print(f"\n找到 {len(templates)} 个自定义模板:\n")
            
            # 按分类分组
            by_category = {}
            for template in templates:
                cat = template.category
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(template)
            
            for category, cat_templates in by_category.items():
                print(f"\n📁 {category}")
                print("-" * 60)
                for template in cat_templates:
                    print(f"  • {template.name}")
                    print(f"    描述: {template.description}")
                    if hasattr(template, 'keywords') and template.keywords:
                        print(f"    关键词: {', '.join(template.keywords)}")
                    if template.parameters:
                        print(f"    参数: {len(template.parameters)} 个")
                    print()
        
        print("=" * 60)
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
        # 获取模板信息
        template = assistant.custom_template_manager.get_template_info(template_id)
        if not template:
            print(f"❌ 模板不存在: {template_id}")
            return 1
        
        print("\n" + "=" * 60)
        print(f"✏️  编辑模板: {template.name}")
        print("=" * 60)
        
        print("\n当前配置:")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        if hasattr(template, 'keywords') and template.keywords:
            print(f"  关键词: {', '.join(template.keywords)}")
        
        print("\n可编辑的字段:")
        print("[1] 名称")
        print("[2] 描述")
        print("[3] 关键词")
        print("[0] 完成编辑")
        
        updates = {}
        
        while True:
            choice = input("\n选择要编辑的字段 (0-3): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                new_name = input("新名称: ").strip()
                if new_name:
                    updates['name'] = new_name
            elif choice == "2":
                new_desc = input("新描述: ").strip()
                if new_desc:
                    updates['description'] = new_desc
            elif choice == "3":
                new_keywords = input("新关键词 (逗号分隔): ").strip()
                if new_keywords:
                    updates['keywords'] = [k.strip() for k in new_keywords.split(',')]
            else:
                print("❌ 无效的选择")
        
        if not updates:
            print("\n未进行任何修改")
            return 0
        
        # 应用更新
        print("\n正在更新模板...")
        updated_template = assistant.custom_template_manager.edit_template(template_id, updates)
        
        print("\n✅ 模板更新成功!")
        print(f"  名称: {updated_template.name}")
        print(f"  描述: {updated_template.description}")
        
        return 0
        
    except TemplateError as e:
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
        # 获取模板信息
        template = assistant.custom_template_manager.get_template_info(template_id)
        if not template:
            print(f"❌ 模板不存在: {template_id}")
            return 1
        
        print("\n" + "=" * 60)
        print(f"🗑️  删除模板")
        print("=" * 60)
        
        print(f"\n模板信息:")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        print(f"  文件: {template.file_path}")
        
        # 确认删除
        print("\n⚠️  警告: 此操作不可恢复!")
        confirm = input("\n确认删除? 输入模板名称以确认: ").strip()
        
        if confirm != template.name:
            print("\n❌ 名称不匹配，取消删除")
            return 1
        
        # 执行删除
        print("\n正在删除模板...")
        success = assistant.custom_template_manager.delete_template(template_id)
        
        if success:
            print("\n✅ 模板已删除")
            return 0
        else:
            print("\n❌ 删除失败")
            return 1
        
    except TemplateError as e:
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
        print("\n" + "=" * 60)
        print(f"📜 模板历史: {template_id}")
        print("=" * 60)
        
        # 获取历史版本
        versions = assistant.custom_template_manager.version_control.list_versions(template_id)
        
        if not versions:
            print("\n暂无历史版本")
        else:
            print(f"\n找到 {len(versions)} 个历史版本:\n")
            for version in versions:
                print(f"版本 {version.version_number}")
                print(f"  时间: {version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                if version.change_description:
                    print(f"  说明: {version.change_description}")
                print()
        
        print("=" * 60)
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
        print(f"\n❌ 发生致命错误: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
