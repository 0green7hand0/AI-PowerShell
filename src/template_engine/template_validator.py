"""
模板验证器

负责验证模板的有效性，包括 PowerShell 语法检查、参数验证和占位符一致性检查。
"""

import re
import subprocess
import tempfile
import os
from typing import Dict, List, Set
from pathlib import Path

from .models import Template, TemplateParameter
from .custom_models import ValidationResult, CustomTemplate
from .exceptions import TemplateValidationError, TemplateSyntaxError
from .security_checker import SecurityChecker


class TemplateValidator:
    """
    模板验证器
    
    提供全面的模板验证功能，确保模板在使用前是有效和安全的。
    """
    
    def __init__(self, enable_security_checks: bool = True):
        """
        初始化验证器
        
        Args:
            enable_security_checks: 是否启用安全检查（默认启用）
        """
        self.placeholder_pattern = re.compile(r'\{\{(\w+)\}\}')
        self.param_block_pattern = re.compile(
            r'param\s*\((.*?)\)',
            re.DOTALL | re.IGNORECASE
        )
        self.enable_security_checks = enable_security_checks
        self.security_checker = SecurityChecker() if enable_security_checks else None
    
    def validate_template(self, template: Template) -> ValidationResult:
        """
        验证模板的完整性
        
        执行所有验证检查，包括语法、参数和占位符验证。
        
        Args:
            template: 要验证的模板对象
        
        Returns:
            ValidationResult: 验证结果对象
        """
        result = ValidationResult(is_valid=True)
        
        # 加载模板内容
        try:
            content = template.load_content()
        except Exception as e:
            result.add_error(f"无法加载模板内容: {str(e)}")
            return result
        
        # 1. 验证 PowerShell 语法
        syntax_result = self.validate_powershell_syntax(content)
        if not syntax_result.is_valid:
            result.is_valid = False
            result.errors.extend(syntax_result.errors)
        result.warnings.extend(syntax_result.warnings)
        
        # 2. 验证参数配置
        param_result = self.validate_parameters(template)
        if not param_result.is_valid:
            result.is_valid = False
            result.errors.extend(param_result.errors)
        result.warnings.extend(param_result.warnings)
        
        # 3. 验证占位符一致性
        placeholder_result = self.validate_placeholders(template)
        if not placeholder_result.is_valid:
            result.is_valid = False
            result.errors.extend(placeholder_result.errors)
        result.warnings.extend(placeholder_result.warnings)
        result.suggestions.extend(placeholder_result.suggestions)
        
        # 4. 安全检查
        if self.enable_security_checks and self.security_checker:
            security_result = self.validate_security(content)
            if not security_result.is_valid:
                result.is_valid = False
                result.errors.extend(security_result.errors)
            result.warnings.extend(security_result.warnings)
        
        return result
    
    def validate_powershell_syntax(self, script_content: str) -> ValidationResult:
        """
        验证 PowerShell 脚本语法
        
        使用 PowerShell 的 -Syntax 参数进行语法检查。
        
        Args:
            script_content: PowerShell 脚本内容
        
        Returns:
            ValidationResult: 语法验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 空脚本是有效的
        if not script_content or not script_content.strip():
            return result
        
        # 创建临时文件
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.ps1',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(script_content)
                temp_file = f.name
            
            # 使用 PowerShell 的 AST 解析器检查语法
            # 这比 PSParser 更准确，能捕获更多语法错误
            ps_command = f'''
$ErrorActionPreference = 'Stop'
try {{
    $content = Get-Content -Path "{temp_file}" -Raw -ErrorAction Stop
    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseInput($content, [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {{
        $errors | ForEach-Object {{ Write-Error $_.Message }}
        exit 1
    }}
    exit 0
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
'''
            
            process_result = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if process_result.returncode != 0:
                error_output = process_result.stderr.strip()
                if error_output:
                    # 清理错误信息，移除 PowerShell 的额外输出
                    lines = error_output.split('\n')
                    error_lines = [line for line in lines if line.strip() and not line.startswith('+') and 'CategoryInfo' not in line and 'FullyQualifiedErrorId' not in line]
                    if error_lines:
                        result.add_error(f"PowerShell 语法错误: {' '.join(error_lines)}")
                    else:
                        result.add_error("PowerShell 语法验证失败")
                else:
                    result.add_error("PowerShell 语法验证失败")
            
            # 检查警告
            if process_result.stdout:
                warnings = process_result.stdout.strip()
                if warnings and "WARNING" in warnings.upper():
                    result.add_warning(f"PowerShell 警告: {warnings}")
        
        except subprocess.TimeoutExpired:
            result.add_error("PowerShell 语法验证超时")
        
        except FileNotFoundError:
            result.add_error("未找到 PowerShell。请确保 PowerShell 已安装并在 PATH 中")
        
        except Exception as e:
            result.add_error(f"语法验证过程中发生错误: {str(e)}")
        
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        return result
    
    def validate_parameters(self, template: Template) -> ValidationResult:
        """
        验证参数配置
        
        检查参数类型和默认值的匹配性，以及必需参数的完整性。
        
        Args:
            template: 要验证的模板对象
        
        Returns:
            ValidationResult: 参数验证结果
        """
        result = ValidationResult(is_valid=True)
        
        if not template.parameters:
            result.add_warning("模板没有定义任何参数")
            return result
        
        for param_name, param in template.parameters.items():
            # 验证参数名称
            if not param_name or not param_name.strip():
                result.add_error(f"参数名称不能为空")
                continue
            
            if not re.match(r'^[a-zA-Z_]\w*$', param_name):
                result.add_error(
                    f"参数名称 '{param_name}' 无效。"
                    f"参数名称必须以字母或下划线开头，只能包含字母、数字和下划线"
                )
            
            # 验证参数类型
            valid_types = ['string', 'integer', 'boolean', 'path']
            if param.type not in valid_types:
                result.add_error(
                    f"参数 '{param_name}' 的类型 '{param.type}' 无效。"
                    f"有效类型: {', '.join(valid_types)}"
                )
                continue
            
            # 验证默认值与类型的匹配性
            if param.default is not None:
                type_validation = self._validate_parameter_type(
                    param_name,
                    param.type,
                    param.default
                )
                if not type_validation.is_valid:
                    result.is_valid = False
                    result.errors.extend(type_validation.errors)
                result.warnings.extend(type_validation.warnings)
            
            # 验证必需参数
            if param.required and param.default is not None:
                result.add_warning(
                    f"参数 '{param_name}' 标记为必需，但提供了默认值。"
                    f"建议移除默认值或将参数标记为可选"
                )
            
            # 验证参数描述
            if not param.description or not param.description.strip():
                result.add_suggestion(
                    f"建议为参数 '{param_name}' 添加描述，以提高模板的可用性"
                )
        
        return result
    
    def _validate_parameter_type(
        self,
        param_name: str,
        param_type: str,
        default_value: any
    ) -> ValidationResult:
        """
        验证参数默认值与类型的匹配性
        
        Args:
            param_name: 参数名称
            param_type: 参数类型
            default_value: 默认值
        
        Returns:
            ValidationResult: 类型验证结果
        """
        result = ValidationResult(is_valid=True)
        
        if param_type == 'string':
            if not isinstance(default_value, str):
                result.add_error(
                    f"参数 '{param_name}' 的类型为 string，"
                    f"但默认值 '{default_value}' 不是字符串"
                )
        
        elif param_type == 'integer':
            try:
                int(default_value)
            except (ValueError, TypeError):
                result.add_error(
                    f"参数 '{param_name}' 的类型为 integer，"
                    f"但默认值 '{default_value}' 不能转换为整数"
                )
        
        elif param_type == 'boolean':
            if not isinstance(default_value, bool):
                # 尝试解析字符串形式的布尔值
                if isinstance(default_value, str):
                    if default_value.lower() not in ['true', 'false', '1', '0']:
                        result.add_error(
                            f"参数 '{param_name}' 的类型为 boolean，"
                            f"但默认值 '{default_value}' 不是有效的布尔值"
                        )
                else:
                    result.add_error(
                        f"参数 '{param_name}' 的类型为 boolean，"
                        f"但默认值 '{default_value}' 不是布尔类型"
                    )
        
        elif param_type == 'path':
            if not isinstance(default_value, str):
                result.add_error(
                    f"参数 '{param_name}' 的类型为 path，"
                    f"但默认值不是字符串"
                )
            else:
                # 验证路径格式（不检查路径是否存在）
                if not default_value.strip():
                    result.add_warning(
                        f"参数 '{param_name}' 的默认路径为空"
                    )
                # 检查路径中的非法字符
                illegal_chars = ['<', '>', '|', '\0']
                if any(char in default_value for char in illegal_chars):
                    result.add_error(
                        f"参数 '{param_name}' 的默认路径包含非法字符"
                    )
        
        return result
    
    def validate_placeholders(self, template: Template) -> ValidationResult:
        """
        验证占位符与参数定义的一致性
        
        检查模板内容中的所有占位符是否在参数配置中定义，
        以及参数配置中的参数是否在模板中使用。
        
        Args:
            template: 要验证的模板对象
        
        Returns:
            ValidationResult: 占位符验证结果
        """
        result = ValidationResult(is_valid=True)
        
        # 加载模板内容
        try:
            content = template.load_content()
        except Exception as e:
            result.add_error(f"无法加载模板内容: {str(e)}")
            return result
        
        # 提取模板中的所有占位符
        placeholders = self._extract_placeholders(content)
        
        # 获取定义的参数名称
        defined_params = set(template.parameters.keys()) if template.parameters else set()
        
        # 检查未定义的占位符
        undefined_placeholders = placeholders - defined_params
        if undefined_placeholders:
            result.is_valid = False
            for placeholder in sorted(undefined_placeholders):
                result.add_error(
                    f"占位符 '{{{{{placeholder}}}}}' 在模板中使用，"
                    f"但未在参数配置中定义"
                )
        
        # 检查未使用的参数
        unused_params = defined_params - placeholders
        if unused_params:
            for param in sorted(unused_params):
                result.add_warning(
                    f"参数 '{param}' 在配置中定义，但未在模板中使用"
                )
                result.add_suggestion(
                    f"考虑在模板中使用 '{{{{{param}}}}}' 或从配置中移除该参数"
                )
        
        # 检查占位符格式
        format_issues = self._check_placeholder_format(content)
        if format_issues:
            result.warnings.extend(format_issues)
        
        return result
    
    def _extract_placeholders(self, content: str) -> Set[str]:
        """
        从模板内容中提取所有占位符
        
        Args:
            content: 模板内容
        
        Returns:
            Set[str]: 占位符名称集合
        """
        matches = self.placeholder_pattern.findall(content)
        return set(matches)
    
    def _check_placeholder_format(self, content: str) -> List[str]:
        """
        检查占位符格式问题
        
        Args:
            content: 模板内容
        
        Returns:
            List[str]: 格式问题列表
        """
        issues = []
        
        # 检查单个大括号（可能是格式错误）
        single_brace_pattern = re.compile(r'(?<!\{)\{(?!\{)(\w+)(?<!\})\}(?!\})')
        single_braces = single_brace_pattern.findall(content)
        if single_braces:
            issues.append(
                f"发现可能的占位符格式错误。"
                f"占位符应使用双大括号格式 '{{{{{single_braces[0]}}}}}'，"
                f"而不是单大括号 '{{{single_braces[0]}}}'"
            )
        
        # 检查占位符中的空格
        space_pattern = re.compile(r'\{\{(\s+\w+\s*|\s*\w+\s+|\s+\w+\s+)\}\}')
        space_matches = space_pattern.findall(content)
        if space_matches:
            issues.append(
                "占位符中不应包含前导或尾随空格。"
                f"例如: '{{{{ {space_matches[0].strip()} }}}}' 应改为 '{{{{{space_matches[0].strip()}}}}}'"
            )
        
        return issues
    
    def validate_security(self, script_content: str) -> ValidationResult:
        """
        执行安全检查
        
        检测危险命令、路径遍历攻击和网络访问。
        
        Args:
            script_content: 脚本内容
        
        Returns:
            ValidationResult: 安全验证结果
        """
        result = ValidationResult(is_valid=True)
        
        if not self.security_checker:
            return result
        
        # 执行安全检查
        security_result = self.security_checker.check_template(script_content)
        
        # 转换安全问题为验证结果
        for issue in security_result.issues:
            message = f"[{issue.category}] {issue.message}"
            if issue.line_number > 0:
                message += f" (行 {issue.line_number})"
            if issue.code_snippet:
                message += f": {issue.code_snippet}"
            
            if issue.severity in ['critical', 'high']:
                result.add_error(message)
            elif issue.severity == 'medium':
                result.add_warning(message)
            else:
                result.add_suggestion(f"建议检查: {message}")
        
        return result
    
    def generate_test_parameters(self, template: Template) -> Dict[str, any]:
        """
        为模板的每个参数生成测试值
        
        根据参数类型和配置生成合适的测试值。
        
        Args:
            template: 要测试的模板对象
        
        Returns:
            Dict[str, any]: 参数名到测试值的映射
        """
        test_params = {}
        
        if not template.parameters:
            return test_params
        
        for param_name, param in template.parameters.items():
            # 如果有默认值，优先使用默认值
            if param.default is not None:
                test_params[param_name] = param.default
                continue
            
            # 根据类型生成测试值
            if param.type == 'string':
                test_params[param_name] = f"test_{param_name.lower()}"
            
            elif param.type == 'integer':
                test_params[param_name] = 42
            
            elif param.type == 'boolean':
                test_params[param_name] = True
            
            elif param.type == 'path':
                # 生成一个安全的测试路径
                test_params[param_name] = f"C:\\Test\\{param_name}"
            
            else:
                # 未知类型，使用字符串
                test_params[param_name] = f"test_value_{param_name}"
        
        return test_params
    
    def preview_generated_script(
        self,
        template: Template,
        parameters: Dict[str, any] = None
    ) -> str:
        """
        显示使用给定参数生成的脚本预览
        
        将模板中的占位符替换为参数值，生成最终脚本的预览。
        
        Args:
            template: 模板对象
            parameters: 参数值字典（如果为 None，则使用生成的测试参数）
        
        Returns:
            str: 生成的脚本内容
        
        Raises:
            TemplateValidationError: 如果模板内容无法加载或参数缺失
        """
        # 加载模板内容
        try:
            content = template.load_content()
        except Exception as e:
            raise TemplateValidationError(f"无法加载模板内容: {str(e)}")
        
        # 如果没有提供参数，生成测试参数
        if parameters is None:
            parameters = self.generate_test_parameters(template)
        
        # 检查必需参数
        if template.parameters:
            for param_name, param in template.parameters.items():
                if param.required and param_name not in parameters:
                    raise TemplateValidationError(
                        f"缺少必需参数: {param_name}"
                    )
        
        # 替换占位符
        generated_script = content
        for param_name, param_value in parameters.items():
            placeholder = f"{{{{{param_name}}}}}"
            # 将值转换为字符串
            value_str = str(param_value)
            generated_script = generated_script.replace(placeholder, value_str)
        
        return generated_script
    
    def test_template(
        self,
        template: Template,
        parameters: Dict[str, any] = None
    ) -> Dict[str, any]:
        """
        使用示例参数测试模板
        
        生成测试参数，替换占位符，并验证生成的脚本。
        
        Args:
            template: 要测试的模板对象
            parameters: 可选的测试参数（如果为 None，则自动生成）
        
        Returns:
            Dict[str, any]: 测试结果，包含以下键:
                - success: bool - 测试是否成功
                - generated_script: str - 生成的脚本内容
                - test_parameters: Dict - 使用的测试参数
                - validation_result: ValidationResult - 验证结果
                - errors: List[str] - 错误列表
                - warnings: List[str] - 警告列表
        """
        result = {
            'success': False,
            'generated_script': '',
            'test_parameters': {},
            'validation_result': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 生成或使用提供的测试参数
            if parameters is None:
                test_params = self.generate_test_parameters(template)
            else:
                test_params = parameters
            
            result['test_parameters'] = test_params
            
            # 生成脚本预览
            try:
                generated_script = self.preview_generated_script(template, test_params)
                result['generated_script'] = generated_script
            except TemplateValidationError as e:
                result['errors'].append(f"生成脚本失败: {str(e)}")
                return result
            
            # 验证生成的脚本语法
            syntax_result = self.validate_powershell_syntax(generated_script)
            result['validation_result'] = syntax_result
            
            if not syntax_result.is_valid:
                result['errors'].extend(syntax_result.errors)
                result['warnings'].extend(syntax_result.warnings)
            else:
                result['success'] = True
                result['warnings'].extend(syntax_result.warnings)
        
        except Exception as e:
            result['errors'].append(f"测试过程中发生错误: {str(e)}")
        
        return result
