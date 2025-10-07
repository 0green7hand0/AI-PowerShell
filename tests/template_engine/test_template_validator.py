"""
模板验证器单元测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.template_engine.template_validator import TemplateValidator
from src.template_engine.models import Template, TemplateParameter, TemplateCategory
from src.template_engine.custom_models import ValidationResult


class TestTemplateValidator:
    """模板验证器测试类"""
    
    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        return TemplateValidator()
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def create_temp_template(self, temp_dir: Path, content: str, parameters: dict = None) -> Template:
        """创建临时模板文件"""
        template_file = temp_dir / "test_template.ps1"
        template_file.write_text(content, encoding='utf-8')
        
        return Template(
            id="test_template",
            name="Test Template",
            category=TemplateCategory.AUTOMATION,
            file_path=str(template_file),
            description="Test template",
            keywords=["test"],
            parameters=parameters or {}
        )


class TestPowerShellSyntaxValidation(TestTemplateValidator):
    """PowerShell 语法验证测试"""
    
    def test_valid_powershell_syntax(self, validator):
        """测试有效的 PowerShell 语法"""
        valid_script = """
# 这是一个有效的 PowerShell 脚本
param(
    [string]$Name = "World"
)

Write-Host "Hello, $Name!"
"""
        result = validator.validate_powershell_syntax(valid_script)
        assert result.is_valid, f"Expected valid, got errors: {result.errors}"
    
    def test_invalid_powershell_syntax_missing_quote(self, validator):
        """测试缺少引号的语法错误"""
        invalid_script = """
Write-Host "Hello, World
"""
        result = validator.validate_powershell_syntax(invalid_script)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_invalid_powershell_syntax_missing_brace(self, validator):
        """测试缺少大括号的语法错误"""
        invalid_script = """
if ($true) {
    Write-Host "Test"
"""
        result = validator.validate_powershell_syntax(invalid_script)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_invalid_powershell_syntax_undefined_command(self, validator):
        """测试未定义命令的语法"""
        # 注意: PowerShell 语法检查可能不会捕获未定义的命令
        # 这取决于 PowerShell 的版本和配置
        script = """
ThisCommandDoesNotExist-AtAll
"""
        result = validator.validate_powershell_syntax(script)
        # 语法检查可能通过，因为命令名称本身是有效的
        # 这个测试主要验证验证器不会崩溃
        assert isinstance(result, ValidationResult)
    
    def test_empty_script(self, validator):
        """测试空脚本"""
        result = validator.validate_powershell_syntax("")
        assert result.is_valid
    
    def test_script_with_comments_only(self, validator):
        """测试只有注释的脚本"""
        script = """
# This is a comment
# Another comment
"""
        result = validator.validate_powershell_syntax(script)
        assert result.is_valid


class TestParameterValidation(TestTemplateValidator):
    """参数验证测试"""
    
    def test_valid_string_parameter(self, validator, temp_dir):
        """测试有效的字符串参数"""
        content = "Write-Host {{NAME}}"
        parameters = {
            "NAME": TemplateParameter(
                name="NAME",
                type="string",
                default="Test",
                description="A test name",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
    
    def test_valid_integer_parameter(self, validator, temp_dir):
        """测试有效的整数参数"""
        content = "Write-Host {{COUNT}}"
        parameters = {
            "COUNT": TemplateParameter(
                name="COUNT",
                type="integer",
                default=10,
                description="A count",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
    
    def test_valid_integer_parameter_string_default(self, validator, temp_dir):
        """测试整数参数使用字符串形式的默认值"""
        content = "Write-Host {{COUNT}}"
        parameters = {
            "COUNT": TemplateParameter(
                name="COUNT",
                type="integer",
                default="10",
                description="A count",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
    
    def test_valid_boolean_parameter(self, validator, temp_dir):
        """测试有效的布尔参数"""
        content = "Write-Host {{ENABLED}}"
        parameters = {
            "ENABLED": TemplateParameter(
                name="ENABLED",
                type="boolean",
                default=True,
                description="Enable feature",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
    
    def test_valid_path_parameter(self, validator, temp_dir):
        """测试有效的路径参数"""
        content = "Get-ChildItem {{PATH}}"
        parameters = {
            "PATH": TemplateParameter(
                name="PATH",
                type="path",
                default="C:\\Users",
                description="A file path",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
    
    def test_invalid_parameter_type(self, validator, temp_dir):
        """测试无效的参数类型"""
        content = "Write-Host {{VALUE}}"
        parameters = {
            "VALUE": TemplateParameter(
                name="VALUE",
                type="invalid_type",
                default="test",
                description="A value",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("invalid_type" in error.lower() for error in result.errors)
    
    def test_string_parameter_with_integer_default(self, validator, temp_dir):
        """测试字符串参数使用整数默认值"""
        content = "Write-Host {{NAME}}"
        parameters = {
            "NAME": TemplateParameter(
                name="NAME",
                type="string",
                default=123,
                description="A name",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("string" in error.lower() for error in result.errors)
    
    def test_integer_parameter_with_invalid_default(self, validator, temp_dir):
        """测试整数参数使用无效默认值"""
        content = "Write-Host {{COUNT}}"
        parameters = {
            "COUNT": TemplateParameter(
                name="COUNT",
                type="integer",
                default="not_a_number",
                description="A count",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("integer" in error.lower() for error in result.errors)
    
    def test_boolean_parameter_with_invalid_default(self, validator, temp_dir):
        """测试布尔参数使用无效默认值"""
        content = "Write-Host {{ENABLED}}"
        parameters = {
            "ENABLED": TemplateParameter(
                name="ENABLED",
                type="boolean",
                default="maybe",
                description="Enable feature",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("boolean" in error.lower() for error in result.errors)
    
    def test_path_parameter_with_illegal_characters(self, validator, temp_dir):
        """测试路径参数包含非法字符"""
        content = "Get-ChildItem {{PATH}}"
        parameters = {
            "PATH": TemplateParameter(
                name="PATH",
                type="path",
                default="C:\\Users\\<invalid>",
                description="A file path",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("非法字符" in error for error in result.errors)
    
    def test_required_parameter_with_default_value(self, validator, temp_dir):
        """测试必需参数提供了默认值（应产生警告）"""
        content = "Write-Host {{NAME}}"
        parameters = {
            "NAME": TemplateParameter(
                name="NAME",
                type="string",
                default="Test",
                description="A name",
                required=True
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid  # 不是错误，只是警告
        assert len(result.warnings) > 0
        assert any("必需" in warning for warning in result.warnings)
    
    def test_parameter_without_description(self, validator, temp_dir):
        """测试参数没有描述（应产生建议）"""
        content = "Write-Host {{NAME}}"
        parameters = {
            "NAME": TemplateParameter(
                name="NAME",
                type="string",
                default="Test",
                description="",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert result.is_valid
        assert len(result.suggestions) > 0
    
    def test_invalid_parameter_name(self, validator, temp_dir):
        """测试无效的参数名称"""
        content = "Write-Host {{123INVALID}}"
        parameters = {
            "123INVALID": TemplateParameter(
                name="123INVALID",
                type="string",
                default="Test",
                description="Invalid name",
                required=False
            )
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_parameters(template)
        assert not result.is_valid
        assert any("参数名称" in error for error in result.errors)
    
    def test_template_without_parameters(self, validator, temp_dir):
        """测试没有参数的模板"""
        content = "Write-Host 'Hello, World!'"
        template = self.create_temp_template(temp_dir, content, {})
        result = validator.validate_parameters(template)
        assert result.is_valid
        assert len(result.warnings) > 0  # 应该有警告说没有参数


class TestPlaceholderValidation(TestTemplateValidator):
    """占位符验证测试"""
    
    def test_valid_placeholders(self, validator, temp_dir):
        """测试有效的占位符"""
        content = "Write-Host {{NAME}} {{AGE}}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name"),
            "AGE": TemplateParameter("AGE", "integer", 30, "Age")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert result.is_valid
    
    def test_undefined_placeholder(self, validator, temp_dir):
        """测试未定义的占位符"""
        content = "Write-Host {{NAME}} {{UNDEFINED}}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert not result.is_valid
        assert any("UNDEFINED" in error for error in result.errors)
    
    def test_unused_parameter(self, validator, temp_dir):
        """测试未使用的参数"""
        content = "Write-Host {{NAME}}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name"),
            "UNUSED": TemplateParameter("UNUSED", "string", "Value", "Unused param")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert result.is_valid  # 未使用的参数不是错误
        assert len(result.warnings) > 0
        assert any("UNUSED" in warning for warning in result.warnings)
    
    def test_multiple_undefined_placeholders(self, validator, temp_dir):
        """测试多个未定义的占位符"""
        content = "Write-Host {{NAME}} {{AGE}} {{CITY}}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert not result.is_valid
        assert len(result.errors) >= 2  # AGE 和 CITY 都未定义
    
    def test_placeholder_format_single_brace(self, validator, temp_dir):
        """测试单大括号格式错误"""
        content = "Write-Host {NAME}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        # 单大括号不会被识别为占位符
        # 这会导致 NAME 参数未使用，产生警告但仍然有效
        assert result.is_valid  # 未使用的参数不是错误
        assert len(result.warnings) > 0  # 应该有格式警告和未使用参数警告
    
    def test_placeholder_with_spaces(self, validator, temp_dir):
        """测试占位符包含空格"""
        content = "Write-Host {{ NAME }}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        # 带空格的占位符可能不会被正确识别
        assert len(result.warnings) > 0
    
    def test_no_placeholders(self, validator, temp_dir):
        """测试没有占位符的模板"""
        content = "Write-Host 'Hello, World!'"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert result.is_valid
        assert len(result.warnings) > 0  # NAME 参数未使用
    
    def test_duplicate_placeholders(self, validator, temp_dir):
        """测试重复的占位符"""
        content = "Write-Host {{NAME}} {{NAME}} {{NAME}}"
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "John", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_placeholders(template)
        assert result.is_valid  # 重复使用占位符是允许的


class TestCompleteTemplateValidation(TestTemplateValidator):
    """完整模板验证测试"""
    
    def test_valid_complete_template(self, validator, temp_dir):
        """测试完全有效的模板"""
        content = """
# 批量重命名文件
param(
    [string]$SourcePath = "{{SOURCE_PATH}}",
    [string]$Pattern = "{{PATTERN}}",
    [int]$StartNumber = {{START_NUMBER}}
)

Get-ChildItem -Path $SourcePath -Filter $Pattern | ForEach-Object {
    $newName = "File_$StartNumber.txt"
    Rename-Item -Path $_.FullName -NewName $newName
    $StartNumber++
}
"""
        parameters = {
            "SOURCE_PATH": TemplateParameter("SOURCE_PATH", "path", "C:\\Files", "Source directory"),
            "PATTERN": TemplateParameter("PATTERN", "string", "*.txt", "File pattern"),
            "START_NUMBER": TemplateParameter("START_NUMBER", "integer", 1, "Starting number")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_template(template)
        assert result.is_valid, f"Validation failed: {result.get_summary()}"
    
    def test_template_with_syntax_error(self, validator, temp_dir):
        """测试包含语法错误的模板"""
        content = """
Write-Host "Missing quote
Write-Host {{NAME}}
"""
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "Test", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_template(template)
        assert not result.is_valid
        assert any("语法" in error for error in result.errors)
    
    def test_template_with_parameter_type_mismatch(self, validator, temp_dir):
        """测试参数类型不匹配的模板"""
        content = "Write-Host {{COUNT}}"
        parameters = {
            "COUNT": TemplateParameter("COUNT", "integer", "not_a_number", "Count")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_template(template)
        assert not result.is_valid
        assert any("integer" in error.lower() for error in result.errors)
    
    def test_template_with_undefined_placeholder(self, validator, temp_dir):
        """测试包含未定义占位符的模板"""
        content = """
Write-Host {{NAME}}
Write-Host {{UNDEFINED_PARAM}}
"""
        parameters = {
            "NAME": TemplateParameter("NAME", "string", "Test", "Name")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_template(template)
        assert not result.is_valid
        assert any("UNDEFINED_PARAM" in error for error in result.errors)
    
    def test_template_with_multiple_issues(self, validator, temp_dir):
        """测试包含多个问题的模板"""
        content = """
Write-Host "Missing quote
Write-Host {{NAME}}
Write-Host {{UNDEFINED}}
"""
        parameters = {
            "NAME": TemplateParameter("NAME", "integer", "not_a_number", "Name"),
            "UNUSED": TemplateParameter("UNUSED", "string", "Value", "Unused")
        }
        template = self.create_temp_template(temp_dir, content, parameters)
        result = validator.validate_template(template)
        assert not result.is_valid
        # 应该有多个错误和警告
        assert len(result.errors) >= 2
        assert len(result.warnings) >= 1


class TestValidationResult:
    """ValidationResult 类测试"""
    
    def test_validation_result_creation(self):
        """测试创建验证结果"""
        result = ValidationResult(is_valid=True)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.suggestions) == 0
    
    def test_add_error(self):
        """测试添加错误"""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
    
    def test_add_warning(self):
        """测试添加警告"""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        assert result.is_valid  # 警告不影响有效性
        assert len(result.warnings) == 1
    
    def test_add_suggestion(self):
        """测试添加建议"""
        result = ValidationResult(is_valid=True)
        result.add_suggestion("Test suggestion")
        assert result.is_valid
        assert len(result.suggestions) == 1
    
    def test_get_summary(self):
        """测试获取摘要"""
        result = ValidationResult(is_valid=False)
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        result.add_suggestion("Suggestion 1")
        
        summary = result.get_summary()
        assert "验证失败" in summary
        assert "Error 1" in summary
        assert "Warning 1" in summary
        assert "Suggestion 1" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



class TestTemplateTestingFunctionality(TestTemplateValidator):
    """模板测试功能测试"""
    
    def test_generate_test_parameters_with_defaults(self, validator, temp_dir):
        """测试生成测试参数 - 使用默认值"""
        parameters = {
            'SOURCE_PATH': TemplateParameter(
                name='SOURCE_PATH',
                type='path',
                description='Source path',
                required=True,
                default='C:\\Source'
            ),
            'FILE_PATTERN': TemplateParameter(
                name='FILE_PATTERN',
                type='string',
                description='File pattern',
                required=False,
                default='*.txt'
            ),
            'MAX_COUNT': TemplateParameter(
                name='MAX_COUNT',
                type='integer',
                description='Max count',
                required=False,
                default=10
            )
        }
        
        template = self.create_temp_template(
            temp_dir,
            "Test content",
            parameters
        )
        
        test_params = validator.generate_test_parameters(template)
        
        # 应该使用默认值
        assert test_params['SOURCE_PATH'] == 'C:\\Source'
        assert test_params['FILE_PATTERN'] == '*.txt'
        assert test_params['MAX_COUNT'] == 10
    
    def test_generate_test_parameters_without_defaults(self, validator, temp_dir):
        """测试生成测试参数 - 无默认值"""
        parameters = {
            'NAME': TemplateParameter(
                name='NAME',
                type='string',
                default=None,
                description='Name',
                required=True
            ),
            'COUNT': TemplateParameter(
                name='COUNT',
                type='integer',
                default=None,
                description='Count',
                required=True
            ),
            'ENABLED': TemplateParameter(
                name='ENABLED',
                type='boolean',
                default=None,
                description='Enabled',
                required=False
            ),
            'OUTPUT_PATH': TemplateParameter(
                name='OUTPUT_PATH',
                type='path',
                default=None,
                description='Output path',
                required=True
            )
        }
        
        template = self.create_temp_template(
            temp_dir,
            "Test content",
            parameters
        )
        
        test_params = validator.generate_test_parameters(template)
        
        # 应该生成合适的测试值
        assert test_params['NAME'] == 'test_name'
        assert test_params['COUNT'] == 42
        assert test_params['ENABLED'] is True
        assert 'Test' in test_params['OUTPUT_PATH']
    
    def test_generate_test_parameters_empty(self, validator, temp_dir):
        """测试生成测试参数 - 无参数"""
        template = self.create_temp_template(temp_dir, "Test content", {})
        
        test_params = validator.generate_test_parameters(template)
        
        assert test_params == {}
    
    def test_preview_generated_script(self, validator, temp_dir):
        """测试脚本预览生成"""
        parameters = {
            'SOURCE_PATH': TemplateParameter(
                name='SOURCE_PATH',
                type='path',
                default=None,
                description='Source path',
                required=True
            ),
            'FILE_PATTERN': TemplateParameter(
                name='FILE_PATTERN',
                type='string',
                default='*.txt',
                description='File pattern',
                required=False
            )
        }
        
        content = """
param(
    [string]$SourcePath = "{{SOURCE_PATH}}",
    [string]$FilePattern = "{{FILE_PATTERN}}"
)

Get-ChildItem -Path $SourcePath -Filter $FilePattern
"""
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        # 使用自定义参数
        custom_params = {
            'SOURCE_PATH': 'C:\\MyFolder',
            'FILE_PATTERN': '*.log'
        }
        
        generated = validator.preview_generated_script(template, custom_params)
        
        # 检查占位符是否被替换
        assert '{{SOURCE_PATH}}' not in generated
        assert '{{FILE_PATTERN}}' not in generated
        assert 'C:\\MyFolder' in generated
        assert '*.log' in generated
    
    def test_preview_generated_script_with_auto_params(self, validator, temp_dir):
        """测试脚本预览 - 自动生成参数"""
        parameters = {
            'NAME': TemplateParameter(
                name='NAME',
                type='string',
                description='Name',
                required=True,
                default='TestName'
            )
        }
        
        content = "Write-Host 'Hello, {{NAME}}!'"
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        # 不提供参数，应该自动生成
        generated = validator.preview_generated_script(template)
        
        assert '{{NAME}}' not in generated
        assert 'TestName' in generated
    
    def test_preview_generated_script_missing_required_param(self, validator, temp_dir):
        """测试脚本预览 - 缺少必需参数"""
        parameters = {
            'REQUIRED_PARAM': TemplateParameter(
                name='REQUIRED_PARAM',
                type='string',
                default=None,
                description='Required param',
                required=True
            )
        }
        
        content = "Write-Host '{{REQUIRED_PARAM}}'"
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        # 提供空参数字典
        from src.template_engine.exceptions import TemplateValidationError
        with pytest.raises(TemplateValidationError, match="缺少必需参数"):
            validator.preview_generated_script(template, {})
    
    def test_test_template_success(self, validator, temp_dir):
        """测试模板测试 - 成功案例"""
        parameters = {
            'MESSAGE': TemplateParameter(
                name='MESSAGE',
                type='string',
                description='Message',
                required=False,
                default='Hello'
            )
        }
        
        content = """
param(
    [string]$Message = "{{MESSAGE}}"
)

Write-Host $Message
"""
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        result = validator.test_template(template)
        
        # 检查结果结构
        assert 'success' in result
        assert 'generated_script' in result
        assert 'test_parameters' in result
        assert 'validation_result' in result
        assert 'errors' in result
        assert 'warnings' in result
        
        # 检查测试成功
        assert result['success'] is True
        assert result['test_parameters']['MESSAGE'] == 'Hello'
        assert '{{MESSAGE}}' not in result['generated_script']
        assert 'Hello' in result['generated_script']
        assert len(result['errors']) == 0
    
    def test_test_template_with_custom_params(self, validator, temp_dir):
        """测试模板测试 - 使用自定义参数"""
        parameters = {
            'COUNT': TemplateParameter(
                name='COUNT',
                type='integer',
                default=None,
                description='Count',
                required=True
            )
        }
        
        content = """
param([int]$Count = {{COUNT}})
Write-Host "Count: $Count"
"""
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        custom_params = {'COUNT': 100}
        result = validator.test_template(template, custom_params)
        
        assert result['success'] is True
        assert result['test_parameters']['COUNT'] == 100
        assert '100' in result['generated_script']
    
    def test_test_template_syntax_error(self, validator, temp_dir):
        """测试模板测试 - 语法错误"""
        parameters = {
            'NAME': TemplateParameter(
                name='NAME',
                type='string',
                description='Name',
                required=False,
                default='Test'
            )
        }
        
        # 故意创建语法错误的脚本
        content = """
param([string]$Name = "{{NAME}}")
Write-Host "Hello, $Name
"""  # 缺少引号闭合
        
        template = self.create_temp_template(temp_dir, content, parameters)
        
        result = validator.test_template(template)
        
        # 测试应该失败
        assert result['success'] is False
        assert len(result['errors']) > 0
        assert result['generated_script'] != ''
    
    def test_test_template_no_parameters(self, validator, temp_dir):
        """测试模板测试 - 无参数模板"""
        content = """
Write-Host "This is a simple script"
Get-Date
"""
        
        template = self.create_temp_template(temp_dir, content, {})
        
        result = validator.test_template(template)
        
        assert result['success'] is True
        assert result['test_parameters'] == {}
        assert result['generated_script'] == content
