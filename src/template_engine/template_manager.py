"""
模板管理器

负责加载、管理和查询脚本模板。
"""

import os
import yaml
from typing import Dict, List, Optional
from pathlib import Path

from .models import Template, TemplateCategory, TemplateParameter
from .custom_models import CustomTemplate


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, config_path: str = "config/templates.yaml"):
        """
        初始化模板管理器
        
        Args:
            config_path: 模板配置文件路径
        """
        self.config_path = config_path
        self.templates: Dict[str, Template] = {}
        self.config = {}
        self._load_config()
        self._load_templates()
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件不存在: {self.config_path}")
            self.config = {'templates': {}}
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}")
            self.config = {'templates': {}}
    
    def _load_templates(self):
        """从配置加载所有模板（包括系统模板和自定义模板）"""
        templates_config = self.config.get('templates', {})
        
        for category_name, category_templates in templates_config.items():
            # 处理自定义模板分类
            if category_name == 'custom':
                self._load_custom_templates(category_templates)
                continue
            
            # 处理系统模板分类
            try:
                category = TemplateCategory(category_name)
            except ValueError:
                print(f"警告: 未知的模板分类: {category_name}")
                continue
            
            for template_id, template_config in category_templates.items():
                try:
                    template = self._create_template(
                        template_id,
                        category,
                        template_config
                    )
                    self.templates[template_id] = template
                except Exception as e:
                    print(f"警告: 加载模板失败 {template_id}: {e}")
    
    def _load_custom_templates(self, custom_templates: Dict):
        """
        加载自定义模板
        
        Args:
            custom_templates: 自定义模板配置字典
        """
        for template_id, template_config in custom_templates.items():
            try:
                template = self._create_custom_template(
                    template_id,
                    template_config
                )
                self.templates[template_id] = template
            except Exception as e:
                print(f"警告: 加载自定义模板失败 {template_id}: {e}")
    
    def _create_custom_template(
        self,
        template_id: str,
        config: Dict
    ) -> CustomTemplate:
        """
        创建自定义模板对象
        
        Args:
            template_id: 模板ID
            config: 模板配置
            
        Returns:
            CustomTemplate对象
        """
        # 解析参数
        parameters = {}
        for param_name, param_config in config.get('parameters', {}).items():
            parameters[param_name] = TemplateParameter(
                name=param_name,
                type=param_config.get('type', 'string'),
                default=param_config.get('default'),
                description=param_config.get('description', ''),
                required=param_config.get('required', False)
            )
        
        # 推断分类（如果配置中有category字段，使用它；否则使用默认值）
        category_str = config.get('category', 'automation')
        try:
            category = TemplateCategory(category_str)
        except ValueError:
            # 如果分类无效，默认使用 AUTOMATION
            category = TemplateCategory.AUTOMATION
        
        # 解析时间戳
        created_at = config.get('created_at')
        if isinstance(created_at, str):
            from datetime import datetime
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.now()
        elif created_at is None:
            from datetime import datetime
            created_at = datetime.now()
        
        updated_at = config.get('updated_at')
        if isinstance(updated_at, str):
            from datetime import datetime
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = datetime.now()
        elif updated_at is None:
            from datetime import datetime
            updated_at = datetime.now()
        
        return CustomTemplate(
            id=template_id,
            name=config.get('name', template_id),
            category=category,
            file_path=config.get('file', ''),
            description=config.get('description', ''),
            keywords=config.get('keywords', []),
            parameters=parameters,
            examples=config.get('examples', []),
            is_custom=True,
            created_at=created_at,
            updated_at=updated_at,
            author=config.get('author', 'user'),
            version=config.get('version', '1.0.0'),
            tags=config.get('tags', [])
        )
    
    def _create_template(
        self,
        template_id: str,
        category: TemplateCategory,
        config: Dict
    ) -> Template:
        """创建模板对象"""
        
        # 解析参数
        parameters = {}
        for param_name, param_config in config.get('parameters', {}).items():
            parameters[param_name] = TemplateParameter(
                name=param_name,
                type=param_config.get('type', 'string'),
                default=param_config.get('default'),
                description=param_config.get('description', ''),
                required=param_config.get('required', False)
            )
        
        return Template(
            id=template_id,
            name=config.get('name', template_id),
            category=category,
            file_path=config.get('file', ''),
            description=config.get('description', ''),
            keywords=config.get('keywords', []),
            parameters=parameters,
            examples=config.get('examples', [])
        )
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            Template对象，如果不存在则返回None
        """
        return self.templates.get(template_id)
    
    def list_templates(
        self,
        category: Optional[TemplateCategory] = None,
        custom_only: bool = False
    ) -> List[Template]:
        """
        列出所有模板
        
        Args:
            category: 可选的分类筛选
            custom_only: 是否只列出自定义模板
            
        Returns:
            模板列表
        """
        templates = list(self.templates.values())
        
        # 筛选自定义模板
        if custom_only:
            templates = [t for t in templates if isinstance(t, CustomTemplate)]
        
        # 筛选分类
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def search_templates(self, keywords: List[str]) -> List[Template]:
        """
        搜索模板（包括系统模板和自定义模板）
        
        Args:
            keywords: 关键词列表
            
        Returns:
            匹配的模板列表
        """
        results = []
        
        for template in self.templates.values():
            # 检查关键词匹配
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # 检查模板关键词
                if any(keyword_lower in k.lower() for k in template.keywords):
                    results.append(template)
                    break
                
                # 检查模板名称
                if keyword_lower in template.name.lower():
                    results.append(template)
                    break
                
                # 检查模板描述
                if keyword_lower in template.description.lower():
                    results.append(template)
                    break
                
                # 对于自定义模板，还要检查标签
                if isinstance(template, CustomTemplate):
                    if any(keyword_lower in tag.lower() for tag in template.tags):
                        results.append(template)
                        break
        
        return results
    
    def get_template_by_category(
        self,
        category: TemplateCategory
    ) -> List[Template]:
        """
        按分类获取模板
        
        Args:
            category: 模板分类
            
        Returns:
            该分类下的所有模板
        """
        return [
            t for t in self.templates.values()
            if t.category == category
        ]
    
    def get_config(self, key: str, default=None):
        """
        获取配置项
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def __len__(self):
        """返回模板数量"""
        return len(self.templates)
    
    def __str__(self):
        return f"TemplateManager(templates={len(self.templates)})"
