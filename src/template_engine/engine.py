"""
模板引擎主类

整合所有模块，提供统一的接口。
"""

from typing import Optional, Dict
from .template_manager import TemplateManager
from .intent_recognizer import IntentRecognizer
from .template_matcher import TemplateMatcher
from .script_generator import ScriptGenerator
from .models import Intent, GeneratedScript, TemplateMatch


class TemplateEngine:
    """模板引擎主类"""
    
    def __init__(self, config: Dict, ai_provider=None):
        """
        初始化模板引擎
        
        Args:
            config: 配置字典
            ai_provider: AI提供商实例（可选）
        """
        self.config = config
        self.ai_provider = ai_provider
        
        # 初始化各个模块
        self.template_manager = TemplateManager()
        self.intent_recognizer = IntentRecognizer()
        self.template_matcher = TemplateMatcher(self.template_manager)
        self.script_generator = ScriptGenerator(config, ai_provider)
        
        print(f"模板引擎初始化完成，加载了 {len(self.template_manager)} 个模板")
    
    def process_request(
        self,
        user_input: str,
        use_ai: bool = True,
        progress_callback=None
    ) -> Optional[GeneratedScript]:
        """
        处理用户请求，生成脚本
        
        Args:
            user_input: 用户输入的文本
            use_ai: 是否使用AI生成（如果为False，使用简单替换）
            progress_callback: 进度回调函数，接收 (step, total, description) 参数
            
        Returns:
            生成的脚本对象，如果无法处理则返回None
        """
        try:
            # 1. 识别意图
            if progress_callback:
                progress_callback(1, 3, "识别意图...")
            print(f"正在识别意图...")
            intent = self.intent_recognizer.recognize(user_input)
            print(f"✓ 识别结果: {intent}")
            
            # 2. 匹配模板
            if progress_callback:
                progress_callback(2, 3, "匹配模板...")
            print(f"正在匹配模板...")
            template_match = self.template_matcher.match(intent)
            
            if not template_match:
                print("✗ 未找到匹配的模板")
                return None
            
            print(f"✓ 匹配到模板: {template_match.template.name} (分数: {template_match.score:.2f})")
            
            # 3. 生成脚本
            if progress_callback:
                progress_callback(3, 3, "生成脚本...")
            print(f"正在生成脚本...")
            generated_script = self.script_generator.generate(
                template_match,
                intent,
                use_ai=use_ai
            )
            
            print(f"✓ 脚本生成完成: {generated_script.file_path}")
            
            return generated_script
            
        except Exception as e:
            print(f"✗ 处理请求失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_intent(self, user_input: str) -> Intent:
        """
        仅识别意图，不生成脚本
        
        Args:
            user_input: 用户输入
            
        Returns:
            Intent对象
        """
        return self.intent_recognizer.recognize(user_input)
    
    def find_template(self, user_input: str) -> Optional[TemplateMatch]:
        """
        查找匹配的模板
        
        Args:
            user_input: 用户输入
            
        Returns:
            匹配的模板，如果没有则返回None
        """
        intent = self.intent_recognizer.recognize(user_input)
        return self.template_matcher.match(intent)
    
    def list_templates(self) -> list:
        """
        列出所有可用的模板
        
        Returns:
            模板列表
        """
        return self.template_manager.list_templates()
    
    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """
        获取模板信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板信息字典
        """
        template = self.template_manager.get_template(template_id)
        
        if not template:
            return None
        
        return {
            'id': template.id,
            'name': template.name,
            'category': template.category.value,
            'description': template.description,
            'keywords': template.keywords,
            'parameters': {
                name: {
                    'type': param.type,
                    'default': param.default,
                    'description': param.description
                }
                for name, param in template.parameters.items()
            },
            'examples': template.examples
        }
    
    def __str__(self):
        return f"TemplateEngine(templates={len(self.template_manager)})"
