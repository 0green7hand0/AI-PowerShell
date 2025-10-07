"""
模板编辑器模块

提供模板编辑功能，包括元数据更新、参数更新和内容更新。
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .models import Template, TemplateParameter
from .custom_models import CustomTemplate, ValidationResult
from .exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
    TemplateIOError
)
from .template_validator import TemplateValidator
from .template_version_control import TemplateVersionControl


class TemplateEditor:
    """
    模板编辑器
    
    提供全面的模板编辑功能，支持元数据、参数和内容的更新，
    并自动创建版本备份和验证更改。
    """
    
    def __init__(
        self,
        validator: Optional[TemplateValidator] = None,
        version_control: Optional[TemplateVersionControl] = None
    ):
        """
        初始化模板编辑器
        
        Args:
            validator: 模板验证器实例（可选）
            version_control: 版本控制器实例（可选）
        """
        self.validator = validator or TemplateValidator()
        self.version_control = version_control or TemplateVersionControl()
    
    def update_metadata(
        self,
        template: Template,
        updates: Dict[str, Any],
        create_backup: bool = True
    ) -> Template:
        """
        更新模板元数据
        
        支持更新模板的名称、描述、关键词、分类等元数据。
        
        Args:
            template: 要更新的模板对象
            updates: 更新的字段字典，可包含:
                - name: 模板名称
                - description: 模板描述
                - keywords: 关键词列表
                - category: 模板分类
                - tags: 标签列表（仅CustomTemplate）
            create_backup: 是否在更新前创建备份
            
        Returns:
            更新后的模板对象
            
        Raises:
            TemplateValidationError: 更新的数据无效
            TemplateError: 更新失败
        """
        # 验证更新数据
        self._validate_metadata_updates(updates)
        
        # 创建备份
        if create_backup:
            self._create_backup(template, "元数据更新")
        
        # 应用更新
        if 'name' in updates:
            template.name = updates['name']
        
        if 'description' in updates:
            template.description = updates['description']
        
        if 'keywords' in updates:
            if not isinstance(updates['keywords'], list):
                raise TemplateValidationError(
                    "关键词必须是列表类型",
                    details={'field': 'keywords', 'value': updates['keywords']}
                )
            template.keywords = updates['keywords']
        
        if 'category' in updates:
            template.category = updates['category']
        
        # CustomTemplate 特有字段
        if isinstance(template, CustomTemplate):
            if 'tags' in updates:
                if not isinstance(updates['tags'], list):
                    raise TemplateValidationError(
                        "标签必须是列表类型",
                        details={'field': 'tags', 'value': updates['tags']}
                    )
                template.tags = updates['tags']
            
            # 更新时间戳
            template.update_timestamp()
        
        return template
    
    def update_parameters(
        self,
        template: Template,
        parameter_updates: Dict[str, TemplateParameter],
        create_backup: bool = True
    ) -> Template:
        """
        更新模板参数配置
        
        Args:
            template: 要更新的模板对象
            parameter_updates: 参数更新字典，键为参数名，值为TemplateParameter对象
            create_backup: 是否在更新前创建备份
            
        Returns:
            更新后的模板对象
            
        Raises:
            TemplateValidationError: 参数配置无效
            TemplateError: 更新失败
        """
        # 创建备份
        if create_backup:
            self._create_backup(template, "参数配置更新")
        
        # 初始化参数字典（如果不存在）
        if template.parameters is None:
            template.parameters = {}
        
        # 应用参数更新
        for param_name, param in parameter_updates.items():
            if not isinstance(param, TemplateParameter):
                raise TemplateValidationError(
                    f"参数 '{param_name}' 必须是 TemplateParameter 类型",
                    details={'param_name': param_name, 'type': type(param).__name__}
                )
            
            template.parameters[param_name] = param
        
        # 验证更新后的参数配置
        validation_result = self.validator.validate_parameters(template)
        if not validation_result.is_valid:
            raise TemplateValidationError(
                "参数配置验证失败",
                details={'errors': validation_result.errors}
            )
        
        # 验证占位符一致性
        placeholder_result = self.validator.validate_placeholders(template)
        if not placeholder_result.is_valid:
            raise TemplateValidationError(
                "占位符验证失败",
                details={'errors': placeholder_result.errors}
            )
        
        # 更新时间戳
        if isinstance(template, CustomTemplate):
            template.update_timestamp()
        
        return template
    
    def update_content(
        self,
        template: Template,
        new_content: str,
        create_backup: bool = True,
        validate_syntax: bool = True
    ) -> Template:
        """
        更新模板脚本内容
        
        Args:
            template: 要更新的模板对象
            new_content: 新的模板内容
            create_backup: 是否在更新前创建备份
            validate_syntax: 是否验证PowerShell语法
            
        Returns:
            更新后的模板对象
            
        Raises:
            TemplateValidationError: 内容验证失败
            TemplateIOError: 文件操作失败
        """
        # 验证内容不为空
        if not new_content or not new_content.strip():
            raise TemplateValidationError(
                "模板内容不能为空",
                details={'content_length': len(new_content) if new_content else 0}
            )
        
        # 验证语法
        if validate_syntax:
            syntax_result = self.validator.validate_powershell_syntax(new_content)
            if not syntax_result.is_valid:
                raise TemplateValidationError(
                    "PowerShell 语法验证失败",
                    details={'errors': syntax_result.errors}
                )
        
        # 创建备份
        if create_backup:
            self._create_backup(template, "内容更新")
        
        # 更新内容到文件
        try:
            file_path = Path(template.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        except IOError as e:
            raise TemplateIOError(
                f"无法写入模板文件: {template.file_path}",
                details={'error': str(e), 'file_path': template.file_path}
            )
        
        # 验证占位符一致性
        placeholder_result = self.validator.validate_placeholders(template)
        if not placeholder_result.is_valid:
            # 占位符不一致是警告，不阻止更新
            print(f"警告: 占位符验证失败")
            for error in placeholder_result.errors:
                print(f"  - {error}")
        
        # 更新时间戳
        if isinstance(template, CustomTemplate):
            template.update_timestamp()
        
        return template
    
    def sync_to_file(
        self,
        template: Template,
        config_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        同步模板更改到文件系统
        
        将模板对象的所有更改同步到文件系统，包括模板文件和配置。
        
        Args:
            template: 要同步的模板对象
            config_data: 配置数据（可选，如果提供则写入配置文件）
            
        Returns:
            是否成功同步
            
        Raises:
            TemplateIOError: 文件操作失败
            TemplateValidationError: 模板验证失败
        """
        try:
            # 验证模板
            validation_result = self.validator.validate_template(template)
            if not validation_result.is_valid:
                raise TemplateValidationError(
                    "模板验证失败，无法同步",
                    details={'errors': validation_result.errors}
                )
            
            # 确保文件路径存在
            file_path = Path(template.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取当前内容（用于验证是否有更改）
            current_content = None
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                except:
                    pass
            
            # 加载模板内容
            new_content = template.load_content()
            
            # 如果内容有更改，写入文件
            if current_content != new_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            # 如果提供了配置数据，写入配置文件
            if config_data is not None:
                self._sync_config(template, config_data)
            
            return True
        
        except TemplateValidationError:
            raise
        
        except Exception as e:
            raise TemplateIOError(
                f"同步模板到文件系统失败: {str(e)}",
                details={'template_file': template.file_path, 'error': str(e)}
            )
    
    def _validate_metadata_updates(self, updates: Dict[str, Any]) -> None:
        """
        验证元数据更新
        
        Args:
            updates: 更新字典
            
        Raises:
            TemplateValidationError: 验证失败
        """
        # 验证名称
        if 'name' in updates:
            name = updates['name']
            if not name or not name.strip():
                raise TemplateValidationError(
                    "模板名称不能为空",
                    details={'field': 'name'}
                )
            
            if len(name) > 100:
                raise TemplateValidationError(
                    "模板名称过长（最多100个字符）",
                    details={'field': 'name', 'length': len(name)}
                )
        
        # 验证描述
        if 'description' in updates:
            description = updates['description']
            if description and len(description) > 500:
                raise TemplateValidationError(
                    "模板描述过长（最多500个字符）",
                    details={'field': 'description', 'length': len(description)}
                )
        
        # 验证分类
        if 'category' in updates:
            category = updates['category']
            if not category or not category.strip():
                raise TemplateValidationError(
                    "模板分类不能为空",
                    details={'field': 'category'}
                )
            
            # 验证分类名称格式（只允许字母、数字、下划线和连字符）
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', category):
                raise TemplateValidationError(
                    "分类名称只能包含字母、数字、下划线和连字符",
                    details={'field': 'category', 'value': category}
                )
    
    def _create_backup(
        self,
        template: Template,
        change_description: str = ""
    ) -> None:
        """
        创建模板备份
        
        Args:
            template: 要备份的模板
            change_description: 变更描述
        """
        try:
            # 加载当前内容
            content = template.load_content()
            
            # 准备配置数据
            from .models import TemplateCategory
            category_value = template.category
            if isinstance(category_value, TemplateCategory):
                category_value = category_value.value
            
            config = {
                'name': template.name,
                'description': template.description,
                'keywords': template.keywords,
                'category': category_value,
                'parameters': {
                    name: {
                        'type': param.type,
                        'default': param.default,
                        'description': param.description,
                        'required': param.required
                    }
                    for name, param in (template.parameters or {}).items()
                }
            }
            
            # 添加 CustomTemplate 特有字段
            if isinstance(template, CustomTemplate):
                config.update({
                    'is_custom': template.is_custom,
                    'created_at': template.created_at.isoformat(),
                    'updated_at': template.updated_at.isoformat(),
                    'author': template.author,
                    'version': template.version,
                    'tags': template.tags
                })
            
            # 创建版本
            template_id = self._get_template_id(template)
            self.version_control.create_version(
                template_id=template_id,
                content=content,
                config=config,
                change_description=change_description
            )
        
        except Exception as e:
            # 备份失败不应阻止编辑操作，只记录警告
            print(f"警告: 创建备份失败: {str(e)}")
    
    def _get_template_id(self, template: Template) -> str:
        """
        获取模板ID
        
        Args:
            template: 模板对象
            
        Returns:
            模板ID（基于文件路径或模板ID）
        """
        # 如果模板已有ID，直接使用
        if hasattr(template, 'id') and template.id:
            return template.id
        
        # 否则使用文件路径的相对路径作为ID
        file_path = Path(template.file_path)
        
        # 移除 templates/ 前缀和 .ps1 后缀
        relative_path = str(file_path)
        if relative_path.startswith('templates/') or relative_path.startswith('templates\\'):
            relative_path = relative_path[10:]
        
        if relative_path.endswith('.ps1'):
            relative_path = relative_path[:-4]
        
        # 将路径分隔符替换为下划线
        template_id = relative_path.replace('/', '_').replace('\\', '_')
        
        return template_id
    
    def _sync_config(
        self,
        template: Template,
        config_data: Dict[str, Any]
    ) -> None:
        """
        同步配置到配置文件
        
        Args:
            template: 模板对象
            config_data: 配置数据
        """
        # 这个方法预留给配置更新器使用
        # 实际的配置文件更新应该由 ConfigUpdater 处理
        pass
