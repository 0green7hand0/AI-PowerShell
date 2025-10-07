"""
模板创建器单元测试
"""

import pytest
import os
import tempfile
from pathlib import Path

from src.template_engine.template_creator import TemplateCreator
from src.template_engine.custom_models import ParameterInfo
from src.template_engine.exceptions import TemplateIOError


class TestTemplateCreator:
    """测试 TemplateCreator 类"""
    
    @pytest.fixture
    def creator(self):
        """创建 TemplateCreator 实例"""
        return TemplateCreator()
    
    # ========== 参数识别测试 ==========
    
    def test_identify_param_block_simple(self, creator):
        """测试识别简单的 param 块"""
        script = """
param(
    [string]$SourcePath = "C:\\Data",
    [int]$MaxSize = 100,
    [bool]$Recursive = $true
)
"""
        params = creator.identify_parameters(script)
        
        assert len(params) == 3
        
        # 检查第一个参数
        assert params[0].name == "SourcePath"
        assert params[0].type == "string"
        assert params[0].original_value == '"C:\\Data"'
        
        # 检查第二个参数
        assert params[1].name == "MaxSize"
        assert params[1].type == "int"
        assert params[1].original_value == "100"
        
        # 检查第三个参数
        assert params[2].name == "Recursive"
        assert params[2].type == "bool"
        assert params[2].original_value == "$true"
    
    def test_identify_param_block_with_attributes(self, creator):
        """测试识别带属性的 param 块"""
        script = """
param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,
    
    [Parameter(Mandatory=$false)]
    [int]$Timeout = 30
)
"""
        params = creator.identify_parameters(script)
        
        assert len(params) == 2
        assert params[0].name == "InputFile"
        assert params[0].is_required == True
        assert params[1].name == "Timeout"
        assert params[1].is_required == False
    
    def test_identify_variable_assignments(self, creator):
        """测试识别变量赋值"""
        script = """
# Configuration
$LogPath = "C:\\Logs\\app.log"
$MaxRetries = 5
$EnableDebug = $false
$Pattern = "*.txt"

# Process files
Get-ChildItem -Path $LogPath
"""
        params = creator.identify_parameters(script)
        
        # 应该识别出 4 个参数
        param_names = [p.name for p in params]
        assert "LogPath" in param_names
        assert "MaxRetries" in param_names
        assert "EnableDebug" in param_names
        assert "Pattern" in param_names
    
    def test_skip_loop_variables(self, creator):
        """测试跳过循环变量"""
        script = """
$SourcePath = "C:\\Data"

foreach ($item in $items) {
    $i = 0
    Write-Host $item
}
"""
        params = creator.identify_parameters(script)
        
        # 应该只识别 SourcePath，跳过 item 和 i
        assert len(params) == 1
        assert params[0].name == "SourcePath"
    
    def test_skip_system_variables(self, creator):
        """测试跳过系统变量"""
        script = """
$ErrorActionPreference = "Stop"
$PSScriptRoot = "C:\\Scripts"
$MyPath = "C:\\Data"
"""
        params = creator.identify_parameters(script)
        
        # 应该只识别 MyPath
        assert len(params) == 1
        assert params[0].name == "MyPath"
    
    def test_skip_expressions(self, creator):
        """测试跳过表达式"""
        script = """
$BasePath = "C:\\Data"
$FullPath = Join-Path $BasePath "subfolder"
$Count = Get-ChildItem | Measure-Object | Select-Object -ExpandProperty Count
$Sum = $a + $b
"""
        params = creator.identify_parameters(script)
        
        # 应该只识别 BasePath（其他都是表达式）
        assert len(params) == 1
        assert params[0].name == "BasePath"
    
    # ========== 类型推断测试 ==========
    
    def test_infer_type_string(self, creator):
        """测试推断字符串类型"""
        assert creator.infer_parameter_type('"Hello World"') == 'string'
        assert creator.infer_parameter_type("'Hello World'") == 'string'
        assert creator.infer_parameter_type('SomeValue') == 'string'
    
    def test_infer_type_integer(self, creator):
        """测试推断整数类型"""
        assert creator.infer_parameter_type('42') == 'integer'
        assert creator.infer_parameter_type('-100') == 'integer'
        assert creator.infer_parameter_type('3.14') == 'integer'
    
    def test_infer_type_boolean(self, creator):
        """测试推断布尔类型"""
        assert creator.infer_parameter_type('$true') == 'boolean'
        assert creator.infer_parameter_type('$false') == 'boolean'
        assert creator.infer_parameter_type('true') == 'boolean'
        assert creator.infer_parameter_type('false') == 'boolean'
    
    def test_infer_type_path(self, creator):
        """测试推断路径类型"""
        assert creator.infer_parameter_type('"C:\\Data\\file.txt"') == 'path'
        assert creator.infer_parameter_type("'C:/Users/test'") == 'path'
        assert creator.infer_parameter_type('"\\\\server\\share"') == 'path'
        assert creator.infer_parameter_type('"script.ps1"') == 'path'

    # ========== 占位符转换测试 ==========
    
    def test_convert_to_placeholders_simple(self, creator):
        """测试简单的占位符转换"""
        script = """
$SourcePath = "C:\\Data"
$MaxSize = 100

Get-ChildItem -Path $SourcePath
"""
        params = [
            ParameterInfo(
                name="SourcePath",
                original_value='"C:\\Data"',
                type="path",
                line_number=2,
                context=""
            ),
            ParameterInfo(
                name="MaxSize",
                original_value="100",
                type="integer",
                line_number=3,
                context=""
            )
        ]
        
        result = creator.convert_to_placeholders(script, params)
        
        assert "{{SourcePath}}" in result
        assert "{{MaxSize}}" in result
        assert '"C:\\Data"' not in result
        assert "100" not in result or "$MaxSize = {{MaxSize}}" in result
    
    def test_convert_to_placeholders_param_block(self, creator):
        """测试 param 块中的占位符转换"""
        script = """
param(
    [string]$InputFile = "input.txt",
    [int]$Timeout = 30
)
"""
        params = [
            ParameterInfo(
                name="InputFile",
                original_value='"input.txt"',
                type="path",
                line_number=3,
                context=""
            ),
            ParameterInfo(
                name="Timeout",
                original_value="30",
                type="integer",
                line_number=4,
                context=""
            )
        ]
        
        result = creator.convert_to_placeholders(script, params)
        
        assert "{{InputFile}}" in result
        assert "{{Timeout}}" in result
        assert "$InputFile" in result  # 参数名应该保留
        assert "$Timeout" in result
    
    def test_convert_to_placeholders_preserves_code(self, creator):
        """测试占位符转换保留其他代码"""
        script = """
$LogPath = "C:\\Logs\\app.log"

Write-Host "Processing files..."
Get-ChildItem -Path $LogPath
"""
        params = [
            ParameterInfo(
                name="LogPath",
                original_value='"C:\\Logs\\app.log"',
                type="path",
                line_number=2,
                context=""
            )
        ]
        
        result = creator.convert_to_placeholders(script, params)
        
        # 检查占位符
        assert "{{LogPath}}" in result
        
        # 检查其他代码是否保留
        assert "Write-Host" in result
        assert "Get-ChildItem" in result
        assert "$LogPath" in result  # 变量引用应该保留
    
    def test_convert_to_placeholders_multiple_occurrences(self, creator):
        """测试处理多次出现的值"""
        script = """
$DefaultPath = "C:\\Data"
$BackupPath = "C:\\Data"

# 只应该替换赋值，不替换其他地方的相同字符串
Write-Host "Path is C:\\Data"
"""
        params = [
            ParameterInfo(
                name="DefaultPath",
                original_value='"C:\\Data"',
                type="path",
                line_number=2,
                context=""
            )
        ]
        
        result = creator.convert_to_placeholders(script, params)
        
        # DefaultPath 应该被替换
        assert "$DefaultPath = {{DefaultPath}}" in result
        
        # BackupPath 不应该被替换（不在参数列表中）
        assert '$BackupPath = "C:\\Data"' in result
    
    # ========== 文件生成测试 ==========
    
    def test_generate_template_file_success(self, creator):
        """测试成功生成模板文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_template.ps1")
            content = """
param(
    [string]$Path = {{PATH}}
)

Get-ChildItem -Path $Path
"""
            
            result = creator.generate_template_file(content, file_path)
            
            assert result == True
            assert os.path.exists(file_path)
            
            # 验证内容
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == content
    
    def test_generate_template_file_creates_directory(self, creator):
        """测试自动创建目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "subdir", "nested", "test_template.ps1")
            content = "# Test template"
            
            result = creator.generate_template_file(content, file_path)
            
            assert result == True
            assert os.path.exists(file_path)
            assert os.path.exists(os.path.dirname(file_path))
    
    def test_generate_template_file_invalid_path(self, creator):
        """测试无效路径抛出异常"""
        # 使用无效的路径（包含非法字符）
        if os.name == 'nt':  # Windows
            invalid_path = "C:\\invalid<>path\\test.ps1"
        else:  # Unix-like
            invalid_path = "/root/no_permission/test.ps1"
        
        content = "# Test"
        
        with pytest.raises(TemplateIOError):
            creator.generate_template_file(content, invalid_path)
    
    # ========== 完整流程测试 ==========
    
    def test_create_from_script_complete_workflow(self, creator):
        """测试完整的创建流程"""
        script = """
param(
    [string]$SourcePath = "C:\\Data",
    [int]$MaxSize = 100
)

$LogFile = "C:\\Logs\\app.log"

Write-Host "Processing files in $SourcePath"
Get-ChildItem -Path $SourcePath | Where-Object { $_.Length -lt $MaxSize }
"""
        
        metadata = {
            'name': 'Test Template',
            'description': 'A test template',
            'category': 'custom'
        }
        
        template_content, param_config = creator.create_from_script(script, metadata)
        
        # 验证模板内容包含占位符
        assert "{{SourcePath}}" in template_content
        assert "{{MaxSize}}" in template_content
        assert "{{LogFile}}" in template_content
        
        # 验证参数配置
        assert "SourcePath" in param_config
        assert "MaxSize" in param_config
        assert "LogFile" in param_config
        
        assert param_config["SourcePath"]["type"] == "string"
        assert param_config["MaxSize"]["type"] == "int"
        assert param_config["LogFile"]["type"] == "path"
    
    def test_create_from_script_no_parameters(self, creator):
        """测试没有参数的脚本"""
        script = """
Write-Host "Hello World"
Get-Date
"""
        
        metadata = {'name': 'Simple Template'}
        
        template_content, param_config = creator.create_from_script(script, metadata)
        
        # 应该返回原始内容
        assert "Write-Host" in template_content
        assert "Get-Date" in template_content
        
        # 参数配置应该为空
        assert len(param_config) == 0
    
    def test_create_from_script_complex_param_block(self, creator):
        """测试复杂的 param 块"""
        script = """
param(
    [Parameter(Mandatory=$true, HelpMessage="Enter source path")]
    [ValidateNotNullOrEmpty()]
    [string]$SourcePath,
    
    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 1000)]
    [int]$MaxFiles = 100,
    
    [switch]$Recursive
)

Get-ChildItem -Path $SourcePath -Recurse:$Recursive | Select-Object -First $MaxFiles
"""
        
        metadata = {'name': 'Complex Template'}
        
        template_content, param_config = creator.create_from_script(script, metadata)
        
        # 验证参数识别
        assert "SourcePath" in param_config
        assert "MaxFiles" in param_config
        assert "Recursive" in param_config
        
        # 验证必需标记
        assert param_config["SourcePath"]["required"] == True
        assert param_config["MaxFiles"]["required"] == False
    
    # ========== 辅助方法测试 ==========
    
    def test_get_line_number(self, creator):
        """测试获取行号"""
        content = """Line 1
Line 2
Line 3
Target Line
Line 5"""
        
        line_num = creator._get_line_number(content, "Target Line")
        assert line_num == 4
    
    def test_get_context(self, creator):
        """测试获取上下文"""
        content = """Line 1
Line 2
Line 3
Target Line
Line 5
Line 6"""
        
        context = creator._get_context(content, 4, context_lines=1)
        
        assert "Line 3" in context
        assert "Target Line" in context
        assert "Line 5" in context
        assert "Line 1" not in context
        assert "Line 6" not in context
    
    def test_split_parameters_simple(self, creator):
        """测试分割简单参数"""
        param_block = "[string]$Path, [int]$Size, [bool]$Flag"
        
        params = creator._split_parameters(param_block)
        
        assert len(params) == 3
        assert "[string]$Path" in params
        assert "[int]$Size" in params
        assert "[bool]$Flag" in params
    
    def test_split_parameters_with_nested_parens(self, creator):
        """测试分割包含嵌套括号的参数"""
        param_block = """
[Parameter(Mandatory=$true)]
[string]$Path,
[ValidateRange(1, 100)]
[int]$Size
"""
        
        params = creator._split_parameters(param_block)
        
        assert len(params) == 2
        # 第一个参数应该包含完整的属性
        assert "Parameter(Mandatory=$true)" in params[0]
        assert "ValidateRange(1, 100)" in params[1]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
