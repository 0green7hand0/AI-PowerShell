"""
集成测试：自定义模板与现有模板引擎的集成

测试自定义模板的加载、搜索、匹配和脚本生成功能。
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.template_engine.template_manager import TemplateManager
from src.template_engine.template_matcher import TemplateMatcher
from src.template_engine.script_generator import ScriptGenerator
from src.template_engine.custom_template_manager import CustomTemplateManager
from src.template_engine.models import Intent, TemplateCategory
from src.template_engine.custom_models import CustomTemplate


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def config_with_custom_template(temp_dir):
    """创建包含自定义模板的配置"""
    # 创建模板目录
    templates_dir = Path(temp_dir) / "templates" / "custom" / "test_category"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建自定义模板文件
    template_file = templates_dir / "my_custom_script.ps1"
    template_content = """# 自定义测试脚本
param(
    [string]$TestParam = "{{TEST_PARAM}}",
    [int]$NumberParam = {{NUMBER_PARAM}}
)

Write-Host "测试参数: $TestParam"
Write-Host "数字参数: $NumberParam"

# 执行自定义逻辑
Get-ChildItem -Path $TestParam | Select-Object -First $NumberParam
"""
    template_file.write_text(template_content, encoding='utf-8')
    
    # 创建配置文件
    config_dir = Path(temp_dir) / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "templates.yaml"
    config_content = """templates:
  file_management:
    batch_rename:
      name: "批量重命名文件"
      file: "templates/file_management/batch_rename.ps1"
      description: "按规则批量重命名文件"
      keywords:
        - "重命名"
        - "rename"
      parameters:
        SOURCE_PATH:
          type: "string"
          default: "."
          description: "源文件夹路径"
  
  custom:
    my_custom_script:
      name: "我的自定义脚本"
      file: "{template_file}"
      description: "这是一个测试用的自定义脚本"
      category: "automation"
      keywords:
        - "自定义"
        - "测试"
        - "custom"
      parameters:
        TEST_PARAM:
          type: "string"
          default: "."
          description: "测试参数"
          required: true
        NUMBER_PARAM:
          type: "integer"
          default: 10
          description: "数字参数"
          required: false
      is_custom: true
      created_at: "2025-10-07T10:00:00"
      updated_at: "2025-10-07T10:00:00"
      author: "test_user"
      version: "1.0.0"
      tags:
        - "测试"
        - "示例"
""".format(template_file=str(template_file).replace('\\', '\\\\'))
    
    config_file.write_text(config_content, encoding='utf-8')
    
    return {
        'config_path': str(config_file),
        'template_file': str(template_file),
        'temp_dir': temp_dir
    }


class TestCustomTemplateLoading:
    """测试自定义模板的加载"""
    
    def test_load_custom_template(self, config_with_custom_template):
        """测试加载自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 验证模板已加载
        assert len(manager.templates) > 0
        
        # 获取自定义模板
        custom_template = manager.get_template('my_custom_script')
        assert custom_template is not None
        assert isinstance(custom_template, CustomTemplate)
        
        # 验证模板属性
        assert custom_template.name == "我的自定义脚本"
        assert custom_template.is_custom is True
        assert custom_template.author == "test_user"
        assert custom_template.version == "1.0.0"
        assert "测试" in custom_template.tags
        assert "示例" in custom_template.tags
    
    def test_list_custom_templates_only(self, config_with_custom_template):
        """测试只列出自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 列出所有自定义模板
        custom_templates = manager.list_templates(custom_only=True)
        
        # 验证结果
        assert len(custom_templates) == 1
        assert all(isinstance(t, CustomTemplate) for t in custom_templates)
        assert custom_templates[0].id == 'my_custom_script'
    
    def test_list_all_templates(self, config_with_custom_template):
        """测试列出所有模板（包括系统模板和自定义模板）"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 列出所有模板
        all_templates = manager.list_templates()
        
        # 验证包含系统模板和自定义模板
        assert len(all_templates) >= 2
        
        # 验证包含自定义模板
        custom_count = sum(1 for t in all_templates if isinstance(t, CustomTemplate))
        assert custom_count == 1
    
    def test_custom_template_parameters(self, config_with_custom_template):
        """测试自定义模板的参数配置"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        custom_template = manager.get_template('my_custom_script')
        
        # 验证参数
        assert 'TEST_PARAM' in custom_template.parameters
        assert 'NUMBER_PARAM' in custom_template.parameters
        
        test_param = custom_template.parameters['TEST_PARAM']
        assert test_param.type == 'string'
        assert test_param.default == '.'
        assert test_param.required is True
        
        number_param = custom_template.parameters['NUMBER_PARAM']
        assert number_param.type == 'integer'
        assert number_param.default == 10
        assert number_param.required is False


class TestCustomTemplateSearch:
    """测试自定义模板的搜索和匹配"""
    
    def test_search_custom_template_by_keyword(self, config_with_custom_template):
        """测试通过关键词搜索自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 搜索关键词
        results = manager.search_templates(['自定义'])
        
        # 验证结果
        assert len(results) >= 1
        assert any(t.id == 'my_custom_script' for t in results)
    
    def test_search_custom_template_by_tag(self, config_with_custom_template):
        """测试通过标签搜索自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 搜索标签
        results = manager.search_templates(['测试'])
        
        # 验证结果
        assert len(results) >= 1
        custom_template = next((t for t in results if t.id == 'my_custom_script'), None)
        assert custom_template is not None
        assert isinstance(custom_template, CustomTemplate)
    
    def test_search_custom_template_by_name(self, config_with_custom_template):
        """测试通过名称搜索自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 搜索名称
        results = manager.search_templates(['自定义脚本'])
        
        # 验证结果
        assert len(results) >= 1
        assert any(t.id == 'my_custom_script' for t in results)
    
    def test_search_custom_template_by_description(self, config_with_custom_template):
        """测试通过描述搜索自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        
        # 搜索描述
        results = manager.search_templates(['测试用'])
        
        # 验证结果
        assert len(results) >= 1
        assert any(t.id == 'my_custom_script' for t in results)


class TestCustomTemplateMatching:
    """测试自定义模板的匹配"""
    
    def test_match_custom_template(self, config_with_custom_template):
        """测试匹配自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建意图
        intent = Intent(
            action='custom',
            target='script',
            parameters={'test_param': '.', 'number_param': 5},
            confidence=0.9,
            raw_input='运行我的自定义测试脚本'
        )
        
        # 匹配模板
        match = matcher.match(intent)
        
        # 验证匹配结果
        assert match is not None
        assert match.template.id == 'my_custom_script'
        assert match.score > 0
    
    def test_custom_template_score_calculation(self, config_with_custom_template):
        """测试自定义模板的评分计算"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建包含关键词的意图（使用配置中的关键词）
        intent = Intent(
            action='custom',
            target='script',
            parameters={},
            confidence=1.0,
            raw_input='运行自定义测试脚本'
        )
        
        # 获取所有匹配
        matches = matcher.get_all_matches(intent, top_n=5)
        
        # 验证自定义模板在结果中
        custom_match = next((m for m in matches if m.template.id == 'my_custom_script'), None)
        assert custom_match is not None
        
        # 验证关键词或标签匹配增加了分数
        assert len(custom_match.matched_keywords) > 0
        assert custom_match.score > 0
    
    def test_match_system_and_custom_templates(self, config_with_custom_template):
        """测试同时匹配系统模板和自定义模板"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建通用意图
        intent = Intent(
            action='rename',
            target='files',
            parameters={},
            confidence=0.8,
            raw_input='重命名文件'
        )
        
        # 获取所有匹配
        matches = matcher.get_all_matches(intent, top_n=5)
        
        # 验证包含系统模板
        assert len(matches) > 0
        assert any(m.template.id == 'batch_rename' for m in matches)


class TestCustomTemplateScriptGeneration:
    """测试基于自定义模板的脚本生成"""
    
    def test_generate_script_from_custom_template(self, config_with_custom_template):
        """测试从自定义模板生成脚本"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建输出目录
        output_dir = Path(config_with_custom_template['temp_dir']) / "scripts" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'script_saving': {
                'output_dir': str(output_dir)
            }
        }
        
        generator = ScriptGenerator(config)
        
        # 创建意图
        intent = Intent(
            action='custom',
            target='script',
            parameters={'TEST_PARAM': 'C:\\Test', 'NUMBER_PARAM': 5},
            confidence=0.9,
            raw_input='运行我的自定义脚本'
        )
        
        # 匹配模板
        match = matcher.match(intent)
        assert match is not None
        
        # 生成脚本
        generated_script = generator.generate(match, intent, use_ai=False)
        
        # 验证生成的脚本
        assert generated_script is not None
        assert generated_script.template_id == 'my_custom_script'
        assert os.path.exists(generated_script.file_path)
        
        # 读取生成的脚本内容
        with open(generated_script.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证参数已替换
        assert '"C:\\Test"' in content or '"C:\\\\Test"' in content
        assert '5' in content
        
        # 验证不包含占位符
        assert '{{TEST_PARAM}}' not in content
        assert '{{NUMBER_PARAM}}' not in content
    
    def test_generated_script_has_custom_template_comment(self, config_with_custom_template):
        """测试生成的脚本包含自定义模板注释"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建输出目录
        output_dir = Path(config_with_custom_template['temp_dir']) / "scripts" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'script_saving': {
                'output_dir': str(output_dir)
            }
        }
        
        generator = ScriptGenerator(config)
        
        # 创建意图
        intent = Intent(
            action='custom',
            target='script',
            parameters={},
            confidence=0.9,
            raw_input='运行自定义脚本'
        )
        
        # 匹配模板
        match = matcher.match(intent)
        assert match is not None
        
        # 生成脚本
        generated_script = generator.generate(match, intent, use_ai=False)
        
        # 读取生成的脚本内容
        with open(generated_script.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证包含自定义模板信息
        assert '模板类型: 自定义模板' in content
        assert '模板作者: test_user' in content
        assert '模板版本: 1.0.0' in content
    
    def test_generate_script_with_default_parameters(self, config_with_custom_template):
        """测试使用默认参数生成脚本"""
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        # 创建输出目录
        output_dir = Path(config_with_custom_template['temp_dir']) / "scripts" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'script_saving': {
                'output_dir': str(output_dir)
            }
        }
        
        generator = ScriptGenerator(config)
        
        # 创建意图（不提供参数）
        intent = Intent(
            action='custom',
            target='script',
            parameters={},
            confidence=0.9,
            raw_input='运行自定义脚本'
        )
        
        # 匹配模板
        match = matcher.match(intent)
        assert match is not None
        
        # 生成脚本
        generated_script = generator.generate(match, intent, use_ai=False)
        
        # 读取生成的脚本内容
        with open(generated_script.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证使用了默认参数
        assert '"."' in content  # TEST_PARAM 的默认值
        assert '10' in content   # NUMBER_PARAM 的默认值


class TestCustomTemplateIntegrationWorkflow:
    """测试完整的自定义模板工作流"""
    
    def test_end_to_end_workflow(self, config_with_custom_template):
        """测试端到端工作流：搜索 -> 匹配 -> 生成"""
        # 1. 初始化管理器
        manager = TemplateManager(config_with_custom_template['config_path'])
        matcher = TemplateMatcher(manager)
        
        output_dir = Path(config_with_custom_template['temp_dir']) / "scripts" / "generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'script_saving': {
                'output_dir': str(output_dir)
            }
        }
        
        generator = ScriptGenerator(config)
        
        # 2. 搜索自定义模板
        search_results = manager.search_templates(['自定义', '测试'])
        assert len(search_results) > 0
        
        custom_template = next((t for t in search_results if isinstance(t, CustomTemplate)), None)
        assert custom_template is not None
        
        # 3. 创建意图并匹配
        intent = Intent(
            action='custom',
            target='script',
            parameters={'TEST_PARAM': 'D:\\Data', 'NUMBER_PARAM': 20},
            confidence=0.95,
            raw_input='使用自定义测试脚本处理数据'
        )
        
        match = matcher.match(intent)
        assert match is not None
        assert isinstance(match.template, CustomTemplate)
        
        # 4. 生成脚本
        generated_script = generator.generate(match, intent, use_ai=False)
        
        # 5. 验证结果
        assert generated_script is not None
        assert os.path.exists(generated_script.file_path)
        
        with open(generated_script.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证参数替换
        assert 'D:\\Data' in content or 'D:\\\\Data' in content
        assert '20' in content
        
        # 验证自定义模板标记
        assert '模板类型: 自定义模板' in content
        assert custom_template.name in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
