"""
脚本生成器

使用AI根据模板和用户需求生成定制化的PowerShell脚本。
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .models import Template, Intent, GeneratedScript, TemplateMatch
from .custom_models import CustomTemplate


class ScriptGenerator:
    """脚本生成器"""
    
    def __init__(self, config: Dict, ai_provider=None):
        """
        初始化脚本生成器
        
        Args:
            config: 配置字典
            ai_provider: AI提供商实例
        """
        self.config = config
        self.ai_provider = ai_provider
        self.output_dir = config.get('script_saving', {}).get('output_dir', 'scripts/generated')
        
        # 确保输出目录存在
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        template_match: TemplateMatch,
        intent: Intent,
        use_ai: bool = True
    ) -> GeneratedScript:
        """
        生成脚本
        
        Args:
            template_match: 模板匹配结果
            intent: 用户意图
            use_ai: 是否使用AI生成（如果为False，使用简单替换）
            
        Returns:
            生成的脚本对象
        """
        template = template_match.template
        
        # 加载模板内容
        template_content = template.load_content()
        
        # 生成脚本内容
        if use_ai and self.ai_provider:
            script_content = self._generate_with_ai(
                template_content,
                intent,
                template
            )
        else:
            script_content = self._generate_simple(
                template_content,
                intent,
                template
            )
        
        # 添加生成说明
        script_content = self._add_generation_comment(
            script_content,
            intent.raw_input,
            template.name,
            template
        )
        
        # 生成文件路径
        file_path = self._generate_file_path(template.id)
        
        # 创建脚本对象
        generated_script = GeneratedScript(
            template_id=template.id,
            template_name=template.name,
            content=script_content,
            file_path=file_path,
            parameters=intent.parameters,
            user_request=intent.raw_input
        )
        
        # 保存脚本
        generated_script.save()
        
        return generated_script
    
    def _generate_with_ai(
        self,
        template_content: str,
        intent: Intent,
        template: Template
    ) -> str:
        """使用AI生成脚本"""
        
        # 构建提示词
        prompt = self._build_prompt(template_content, intent, template)
        
        try:
            # 调用AI生成
            from ..interfaces.base import Context
            
            context = Context(
                session_id="script_generation",
                working_directory=".",
                command_history=[]
            )
            
            # 使用AI提供商生成
            suggestion = self.ai_provider.generate(prompt, context)
            
            # 提取生成的脚本
            script_content = self._extract_script(suggestion.generated_command)
            
            return script_content
            
        except Exception as e:
            print(f"警告: AI生成失败，使用简单替换: {e}")
            return self._generate_simple(template_content, intent, template)
    
    def _generate_simple(
        self,
        template_content: str,
        intent: Intent,
        template: Template
    ) -> str:
        """使用简单替换生成脚本"""
        
        script_content = template_content
        
        # 构建参数映射
        param_values = self._build_parameter_values(intent, template)
        
        # 替换所有参数占位符
        for param_name, param_value in param_values.items():
            placeholder = f"{{{{{param_name}}}}}"
            
            # 根据参数类型格式化值
            if isinstance(param_value, bool):
                formatted_value = "$true" if param_value else "$false"
            elif isinstance(param_value, str):
                formatted_value = f'"{param_value}"'
            else:
                formatted_value = str(param_value)
            
            script_content = script_content.replace(placeholder, formatted_value)
        
        return script_content
    
    def _build_parameter_values(
        self,
        intent: Intent,
        template: Template
    ) -> Dict[str, any]:
        """构建参数值映射"""
        
        param_values = {}
        
        # 从意图中提取的参数
        extracted_params = intent.parameters
        
        # 遍历模板参数
        for param_name, param_def in template.parameters.items():
            # 优先使用提取的参数
            if param_name.lower() in [k.lower() for k in extracted_params.keys()]:
                # 找到匹配的键（忽略大小写）
                for k, v in extracted_params.items():
                    if k.lower() == param_name.lower():
                        param_values[param_name] = v
                        break
            else:
                # 使用默认值
                param_values[param_name] = param_def.default
        
        # 智能推断常见参数
        param_values = self._infer_parameters(param_values, intent)
        
        return param_values
    
    def _infer_parameters(
        self,
        param_values: Dict[str, any],
        intent: Intent
    ) -> Dict[str, any]:
        """智能推断参数值"""
        
        # 推断源路径
        if 'SOURCE_PATH' in param_values:
            if 'path' in intent.parameters:
                param_values['SOURCE_PATH'] = intent.parameters['path']
            elif param_values['SOURCE_PATH'] == '{{SOURCE_PATH}}':
                param_values['SOURCE_PATH'] = '.'
        
        # 推断文件模式
        if 'FILE_PATTERN' in param_values:
            if 'file_type' in intent.parameters:
                file_type = intent.parameters['file_type']
                param_values['FILE_PATTERN'] = f'*.{file_type}'
            elif param_values['FILE_PATTERN'] == '{{FILE_PATTERN}}':
                param_values['FILE_PATTERN'] = '*.*'
        
        # 推断命名前缀
        if 'NAME_PREFIX' in param_values:
            if 'naming_pattern' in intent.parameters:
                param_values['NAME_PREFIX'] = intent.parameters['naming_pattern']
            elif param_values['NAME_PREFIX'] == '{{NAME_PREFIX}}':
                param_values['NAME_PREFIX'] = 'file'
        
        # 推断阈值
        if 'CPU_THRESHOLD' in param_values:
            if 'threshold' in intent.parameters:
                param_values['CPU_THRESHOLD'] = intent.parameters['threshold']
            elif param_values['CPU_THRESHOLD'] == '{{CPU_THRESHOLD}}':
                param_values['CPU_THRESHOLD'] = 80
        
        # 推断时间间隔
        if 'CHECK_INTERVAL' in param_values:
            if 'interval' in intent.parameters:
                param_values['CHECK_INTERVAL'] = intent.parameters['interval']
            elif param_values['CHECK_INTERVAL'] == '{{CHECK_INTERVAL}}':
                param_values['CHECK_INTERVAL'] = 30
        
        # 推断天数
        if 'DAYS_OLD' in param_values:
            if 'days' in intent.parameters:
                param_values['DAYS_OLD'] = intent.parameters['days']
            elif param_values['DAYS_OLD'] == '{{DAYS_OLD}}':
                param_values['DAYS_OLD'] = 30
        
        # 设置布尔值默认值
        for key in ['USE_DATE', 'INCLUDE_SUBFOLDERS', 'COMPRESS', 
                    'CLEAN_TEMP', 'CLEAN_RECYCLE_BIN', 'CREATE_SUBFOLDERS']:
            if key in param_values and param_values[key] == f'{{{{{key}}}}}':
                param_values[key] = True
        
        # 设置整数默认值
        for key in ['START_NUMBER', 'NUMBER_DIGITS', 'TOP_PROCESSES', 
                    'KEEP_VERSIONS', 'MIN_FILE_SIZE', 'DURATION']:
            if key in param_values and param_values[key] == f'{{{{{key}}}}}':
                if key == 'START_NUMBER':
                    param_values[key] = 1
                elif key == 'NUMBER_DIGITS':
                    param_values[key] = 3
                elif key == 'TOP_PROCESSES':
                    param_values[key] = 5
                elif key == 'KEEP_VERSIONS':
                    param_values[key] = 7
                elif key == 'DURATION':
                    param_values[key] = 0
                else:
                    param_values[key] = 0
        
        # 设置字符串默认值
        for key in ['DATE_FORMAT', 'MOVE_FILES', 'BACKUP_PATH', 'EXCLUDE_PATTERNS']:
            if key in param_values and param_values[key] == f'{{{{{key}}}}}':
                if key == 'DATE_FORMAT':
                    param_values[key] = 'yyyyMMdd'
                elif key == 'MOVE_FILES':
                    param_values[key] = 'move'
                elif key == 'BACKUP_PATH':
                    param_values[key] = 'D:\\Backups'
                elif key == 'EXCLUDE_PATTERNS':
                    param_values[key] = ''
        
        return param_values
    
    def _build_prompt(
        self,
        template_content: str,
        intent: Intent,
        template: Template
    ) -> str:
        """构建AI提示词"""
        
        prompt_template = self.config.get('ai_generation', {}).get(
            'prompt_template',
            """你是一个 PowerShell 脚本专家。请根据用户需求定制以下脚本模板。

用户需求：{user_request}

脚本模板：
{template_content}

任务：
1. 理解用户的具体需求
2. 将模板中的 {{参数}} 占位符替换为合适的值
3. 确保脚本可以直接运行
4. 保持代码清晰易读

请直接返回完整的 PowerShell 脚本："""
        )
        
        return prompt_template.format(
            user_request=intent.raw_input,
            template_content=template_content
        )
    
    def _extract_script(self, ai_output: str) -> str:
        """从AI输出中提取脚本"""
        
        # 移除可能的代码块标记
        script = ai_output.strip()
        
        if script.startswith('```'):
            lines = script.split('\n')
            script = '\n'.join(lines[1:-1]) if len(lines) > 2 else script
            script = script.strip()
        
        # 移除 powershell 标记
        if script.lower().startswith('powershell'):
            script = script[10:].strip()
        
        return script
    
    def _add_generation_comment(
        self,
        script_content: str,
        user_request: str,
        template_name: str,
        template: Template = None
    ) -> str:
        """添加生成说明注释"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 基础注释
        comment_lines = [
            "# ============================================",
            "# 此脚本由 AI PowerShell 智能助手生成",
            f"# 生成时间: {timestamp}",
            f"# 用户需求: {user_request}",
            f"# 基于模板: {template_name}"
        ]
        
        # 如果是自定义模板，添加额外信息
        if template and isinstance(template, CustomTemplate):
            comment_lines.append(f"# 模板类型: 自定义模板")
            comment_lines.append(f"# 模板作者: {template.author}")
            comment_lines.append(f"# 模板版本: {template.version}")
        
        comment_lines.append("# ============================================")
        comment_lines.append("")
        
        comment = "\n".join(comment_lines)
        
        return comment + script_content
    
    def _generate_file_path(self, template_id: str) -> str:
        """生成脚本文件路径"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{template_id}_{timestamp}.ps1"
        
        return os.path.join(self.output_dir, filename)
