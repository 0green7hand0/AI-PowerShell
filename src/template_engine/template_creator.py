"""
模板创建器

从现有的 PowerShell 脚本创建模板，包括参数识别、类型推断和占位符转换。
"""

import re
import os
from typing import List, Tuple, Dict, Optional
from pathlib import Path

from .custom_models import ParameterInfo
from .exceptions import TemplateIOError, TemplateSyntaxError


class TemplateCreator:
    """
    模板创建器
    
    负责从现有的 PowerShell 脚本创建模板，包括：
    - 识别脚本中的参数（param() 块和变量赋值）
    - 推断参数类型
    - 将参数转换为占位符格式
    - 生成模板文件
    """
    
    def __init__(self):
        """初始化模板创建器"""
        # 参数块正则模式不再使用，改用手动解析
        self.param_block_pattern = None
        
        # 变量赋值模式
        self.variable_pattern = re.compile(
            r'^\s*\$(\w+)\s*=\s*(.+?)(?:\s*#.*)?$',
            re.MULTILINE
        )
        
        # PowerShell 参数属性模式
        self.parameter_attribute_pattern = re.compile(
            r'\[Parameter\((.*?)\)\]',
            re.DOTALL | re.IGNORECASE
        )
        
        # 类型声明模式
        self.type_declaration_pattern = re.compile(
            r'\[(\w+)\]\s*\$(\w+)',
            re.IGNORECASE
        )
    
    def create_from_script(
        self,
        script_content: str,
        metadata: Dict[str, any]
    ) -> Tuple[str, Dict]:
        """
        从脚本创建模板
        
        Args:
            script_content: PowerShell 脚本内容
            metadata: 模板元数据（名称、描述、分类等）
        
        Returns:
            元组 (模板内容, 参数配置字典)
        """
        # 识别参数
        parameters = self.identify_parameters(script_content)
        
        # 转换为占位符
        template_content = self.convert_to_placeholders(script_content, parameters)
        
        # 生成参数配置
        param_config = {
            param.name: {
                'type': param.type,
                'default': param.original_value,
                'description': param.description,
                'required': param.is_required
            }
            for param in parameters
        }
        
        return template_content, param_config

    def identify_parameters(self, script_content: str) -> List[ParameterInfo]:
        """
        识别脚本中的参数
        
        支持以下模式：
        1. param() 块中的参数定义
        2. 简单的变量赋值 ($变量名 = 值)
        3. 带类型声明的参数 ([string]$变量名)
        
        Args:
            script_content: PowerShell 脚本内容
        
        Returns:
            识别出的参数信息列表
        """
        parameters = []
        param_names_seen = set()
        
        # 1. 识别 param() 块中的参数
        param_block_params = self._identify_param_block_parameters(script_content)
        for param in param_block_params:
            if param.name not in param_names_seen:
                parameters.append(param)
                param_names_seen.add(param.name)
        
        # 2. 识别变量赋值
        variable_params = self._identify_variable_assignments(script_content)
        for param in variable_params:
            # 避免重复添加已在 param 块中定义的参数
            if param.name not in param_names_seen:
                parameters.append(param)
                param_names_seen.add(param.name)
        
        return parameters
    
    def _identify_param_block_parameters(self, script_content: str) -> List[ParameterInfo]:
        """
        识别 param() 块中的参数
        
        Args:
            script_content: PowerShell 脚本内容
        
        Returns:
            参数信息列表
        """
        parameters = []
        
        # 手动查找 param 块（处理嵌套括号）
        param_blocks = self._extract_param_blocks(script_content)
        
        for block in param_blocks:
            # 分割参数（按逗号分隔，但要考虑嵌套的括号）
            param_definitions = self._split_parameters(block)
            
            for param_def in param_definitions:
                param_info = self._parse_parameter_definition(param_def, script_content)
                if param_info:
                    parameters.append(param_info)
        
        return parameters
    
    def _extract_param_blocks(self, script_content: str) -> List[str]:
        """
        提取 param() 块，正确处理嵌套括号
        
        Args:
            script_content: PowerShell 脚本内容
        
        Returns:
            param 块内容列表
        """
        blocks = []
        
        # 查找 "param(" 的位置
        pattern = re.compile(r'\bparam\s*\(', re.IGNORECASE)
        
        for match in pattern.finditer(script_content):
            start_pos = match.end()  # 开始括号之后的位置
            
            # 从这里开始计数括号，找到匹配的结束括号
            paren_count = 1
            pos = start_pos
            in_string = False
            string_char = None
            
            while pos < len(script_content) and paren_count > 0:
                char = script_content[pos]
                
                # 处理字符串
                if char in ('"', "'") and (pos == 0 or script_content[pos-1] != '`'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                
                # 只在字符串外计数括号
                if not in_string:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                
                pos += 1
            
            if paren_count == 0:
                # 找到了匹配的括号
                block_content = script_content[start_pos:pos-1]
                blocks.append(block_content)
        
        return blocks
    
    def _split_parameters(self, param_block: str) -> List[str]:
        """
        分割参数块中的参数定义
        
        考虑嵌套的括号和引号，正确分割参数。
        
        Args:
            param_block: param() 块的内容
        
        Returns:
            参数定义列表
        """
        parameters = []
        current_param = []
        paren_depth = 0
        bracket_depth = 0
        in_string = False
        string_char = None
        
        for char in param_block:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                    # 找到参数分隔符
                    param_str = ''.join(current_param).strip()
                    if param_str:
                        parameters.append(param_str)
                    current_param = []
                    continue
            
            current_param.append(char)
        
        # 添加最后一个参数
        param_str = ''.join(current_param).strip()
        if param_str:
            parameters.append(param_str)
        
        return parameters
    
    def _parse_parameter_definition(
        self,
        param_def: str,
        script_content: str
    ) -> Optional[ParameterInfo]:
        """
        解析单个参数定义
        
        Args:
            param_def: 参数定义字符串
            script_content: 完整的脚本内容（用于获取上下文）
        
        Returns:
            ParameterInfo 对象，如果解析失败则返回 None
        """
        # 移除前导/尾随空白
        param_def = param_def.strip()
        
        if not param_def:
            return None
        
        # 检查是否有 [Parameter(...)] 属性
        is_required = False
        original_param_def = param_def
        
        # 检查 Mandatory 标记（在移除属性之前）
        param_attr_match = re.search(r'\[Parameter\(([^\]]*)\)\]', param_def, re.IGNORECASE)
        if param_attr_match:
            param_attr_content = param_attr_match.group(1)
            # 检查 Mandatory=$true 或 Mandatory=true
            if re.search(r'Mandatory\s*=\s*\$?true', param_attr_content, re.IGNORECASE):
                is_required = True
        
        # 移除所有属性声明
        while '[Parameter' in param_def or '[Validate' in param_def or '[switch]' in param_def.lower():
            # 移除 [Parameter(...)] 属性
            param_def = re.sub(r'\[Parameter\([^\]]*\)\]\s*', '', param_def, flags=re.IGNORECASE)
            # 移除 [Validate...(...)] 属性
            param_def = re.sub(r'\[Validate\w+\([^\]]*\)\]\s*', '', param_def, flags=re.IGNORECASE)
            # 移除 [ValidateNotNullOrEmpty()] 等无参数属性
            param_def = re.sub(r'\[Validate\w+\(\)\]\s*', '', param_def, flags=re.IGNORECASE)
            # 移除 [switch] 类型
            param_def = re.sub(r'\[switch\]\s*', '', param_def, flags=re.IGNORECASE)
            
            # 防止无限循环
            if param_def == original_param_def:
                break
            original_param_def = param_def
        
        param_def = param_def.strip()
        
        # 提取类型声明和参数名
        type_match = self.type_declaration_pattern.search(param_def)
        if type_match:
            param_type = type_match.group(1).lower()
            # 标准化类型名称
            if param_type == 'int' or param_type == 'int32' or param_type == 'int64':
                param_type = 'integer'
            elif param_type == 'bool':
                param_type = 'boolean'
            param_name = type_match.group(2)
        else:
            # 没有类型声明，尝试提取参数名
            var_match = re.search(r'\$(\w+)', param_def)
            if not var_match:
                return None
            param_name = var_match.group(1)
            param_type = 'string'  # 默认类型
        
        # 提取默认值（在 = 之后，到行尾或逗号）
        default_value = ''
        default_match = re.search(r'=\s*(.+?)$', param_def, re.DOTALL)
        if default_match:
            default_value = default_match.group(1).strip()
            # 移除尾部的逗号
            default_value = default_value.rstrip(',').strip()
            # 如果没有显式类型，从默认值推断
            if not type_match:
                param_type = self.infer_parameter_type(default_value)
        
        # 获取行号和上下文
        line_number = self._get_line_number(script_content, '$' + param_name)
        context = self._get_context(script_content, line_number)
        
        return ParameterInfo(
            name=param_name,
            original_value=default_value,
            type=param_type,
            line_number=line_number,
            context=context,
            is_required=is_required
        )

    def _identify_variable_assignments(self, script_content: str) -> List[ParameterInfo]:
        """
        识别变量赋值
        
        Args:
            script_content: PowerShell 脚本内容
        
        Returns:
            参数信息列表
        """
        parameters = []
        
        # 查找所有变量赋值
        for match in self.variable_pattern.finditer(script_content):
            var_name = match.group(1)
            var_value = match.group(2).strip()
            
            # 跳过一些常见的非参数变量
            if self._should_skip_variable(var_name, var_value):
                continue
            
            # 推断类型
            param_type = self.infer_parameter_type(var_value)
            
            # 获取行号和上下文
            line_number = self._get_line_number(script_content, match.group(0))
            context = self._get_context(script_content, line_number)
            
            parameters.append(ParameterInfo(
                name=var_name,
                original_value=var_value,
                type=param_type,
                line_number=line_number,
                context=context,
                is_required=False
            ))
        
        return parameters
    
    def _should_skip_variable(self, var_name: str, var_value: str) -> bool:
        """
        判断是否应该跳过某个变量
        
        跳过以下变量：
        - 循环变量（$i, $item, $_）
        - 系统变量（$PSScriptRoot, $ErrorActionPreference 等）
        - 计算结果（包含运算符或函数调用）
        
        Args:
            var_name: 变量名
            var_value: 变量值
        
        Returns:
            True 如果应该跳过，否则 False
        """
        # 常见的循环变量
        loop_vars = {'i', 'j', 'k', 'item', 'file', 'line', '_'}
        if var_name.lower() in loop_vars:
            return True
        
        # PowerShell 系统变量
        system_vars = {
            'PSScriptRoot', 'PSCommandPath', 'ErrorActionPreference',
            'VerbosePreference', 'DebugPreference', 'WarningPreference',
            'InformationPreference', 'ProgressPreference'
        }
        if var_name in system_vars:
            return True
        
        # 包含函数调用或运算符的表达式
        if any(op in var_value for op in ['(', ')', '+', '-', '*', '/', '%', '-eq', '-ne', '-gt', '-lt']):
            # 但允许简单的字符串拼接
            if not (var_value.startswith('"') or var_value.startswith("'")):
                return True
        
        return False
    
    def infer_parameter_type(self, value: str) -> str:
        """
        推断参数类型
        
        根据参数的默认值推断其类型。
        
        Args:
            value: 参数值
        
        Returns:
            参数类型：'string', 'integer', 'boolean', 'path'
        """
        if not value:
            return 'string'
        
        value = value.strip()
        
        # 布尔值
        if value.lower() in ('$true', '$false', 'true', 'false'):
            return 'boolean'
        
        # 整数
        if re.match(r'^-?\d+$', value):
            return 'integer'
        
        # 浮点数（也归类为 integer，PowerShell 会处理）
        if re.match(r'^-?\d+\.\d+$', value):
            return 'integer'
        
        # 路径（包含路径分隔符或常见路径模式）
        if any(pattern in value for pattern in ['\\', '/', ':', 'C:', 'D:', '.ps1', '.txt', '.log']):
            return 'path'
        
        # 引号包围的字符串
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            # 检查引号内的内容是否是路径
            inner_value = value[1:-1]
            if any(pattern in inner_value for pattern in ['\\', '/', ':', '.ps1', '.txt', '.log']):
                return 'path'
            return 'string'
        
        # 默认为字符串
        return 'string'

    def convert_to_placeholders(
        self,
        script_content: str,
        parameters: List[ParameterInfo]
    ) -> str:
        """
        将参数转换为占位符格式
        
        将脚本中的参数值替换为 {{参数名}} 格式的占位符。
        
        Args:
            script_content: 原始脚本内容
            parameters: 参数信息列表
        
        Returns:
            转换后的模板内容
        """
        template_content = script_content
        
        # 按行号倒序排序，从后往前替换，避免位置偏移
        sorted_params = sorted(parameters, key=lambda p: p.line_number, reverse=True)
        
        for param in sorted_params:
            # 跳过没有原始值的参数
            if not param.original_value:
                continue
            
            # 构建占位符
            placeholder = f"{{{{{param.name}}}}}"
            
            # 替换模式：
            # 1. param 块中的默认值: = "value" 或 = value
            # 2. 变量赋值: $VarName = "value" 或 $VarName = value
            
            # 模式 1: 在 param 块中的默认值（保留 $VarName）
            param_default_pattern = re.compile(
                rf'(\${param.name}\s*=\s*)(["\']?)({re.escape(param.original_value)})\2',
                re.IGNORECASE
            )
            
            # 尝试替换
            if param_default_pattern.search(template_content):
                # 保留参数名，只替换默认值
                template_content = param_default_pattern.sub(
                    rf'\1{placeholder}',
                    template_content
                )
        
        return template_content
    
    def generate_template_file(
        self,
        template_content: str,
        file_path: str
    ) -> bool:
        """
        生成模板文件
        
        将模板内容写入指定的文件路径。
        
        Args:
            template_content: 模板内容
            file_path: 目标文件路径
        
        Returns:
            True 如果成功，否则抛出异常
        
        Raises:
            TemplateIOError: 文件写入失败
        """
        try:
            # 确保目录存在
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            return True
        
        except OSError as e:
            raise TemplateIOError(
                f"Failed to write template file: {file_path}",
                details={
                    'file_path': file_path,
                    'operation': 'write',
                    'os_error': str(e)
                }
            )
    
    def _get_line_number(self, content: str, search_text: str) -> int:
        """
        获取文本在内容中的行号
        
        Args:
            content: 完整内容
            search_text: 要搜索的文本
        
        Returns:
            行号（从 1 开始）
        """
        try:
            index = content.index(search_text)
            return content[:index].count('\n') + 1
        except ValueError:
            return 0
    
    def _get_context(self, content: str, line_number: int, context_lines: int = 2) -> str:
        """
        获取指定行的上下文
        
        Args:
            content: 完整内容
            line_number: 目标行号
            context_lines: 上下文行数
        
        Returns:
            上下文字符串
        """
        lines = content.split('\n')
        
        if line_number <= 0 or line_number > len(lines):
            return ""
        
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        context_lines_list = lines[start:end]
        return '\n'.join(context_lines_list)
