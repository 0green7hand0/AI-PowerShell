"""
自定义模板管理器

协调所有自定义模板相关操作，包括创建、编辑、删除和查询。
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime

from .models import Template, TemplateParameter, TemplateCategory
from .custom_models import CustomTemplate, ParameterInfo
from .exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateConflictError,
    TemplateValidationError
)
from .template_creator import TemplateCreator
from .template_editor import TemplateEditor
from .template_validator import TemplateValidator
from .config_updater import ConfigUpdater
from .template_version_control import TemplateVersionControl


class CustomTemplateManager:
    """
    自定义模板管理器
    
    提供完整的自定义模板管理功能，协调各个组件完成
    模板的创建、编辑、删除和查询操作。
    """
    
    def __init__(
        self,
        templates_dir: str = "templates",
        config_path: str = "config/templates.yaml"
    ):
        """
        初始化自定义模板管理器
        
        Args:
            templates_dir: 模板根目录
            config_path: 配置文件路径
        """
        self.templates_dir = Path(templates_dir)
        self.custom_templates_dir = self.templates_dir / "custom"
        self.config_path = config_path
        
        # 初始化组件
        self.creator = TemplateCreator()
        self.validator = TemplateValidator()
        self.editor = TemplateEditor(
            validator=self.validator,
            version_control=TemplateVersionControl()
        )
        self.config_updater = ConfigUpdater(config_path)
        
        # 确保自定义模板目录存在
        self.custom_templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 系统模板分类（不允许删除）
        self.system_categories = {
            'file_management',
            'automation',
            'system_monitoring'
        }
    
    def create_template(
        self,
        name: str,
        description: str,
        category: str,
        script_content: str,
        keywords: Optional[List[str]] = None,
        author: str = "user",
        tags: Optional[List[str]] = None
    ) -> CustomTemplate:
        """
        创建新的自定义模板
        
        协调创建流程：参数识别 -> 验证 -> 文件生成 -> 配置更新
        
        Args:
            name: 模板名称
            description: 模板描述
            category: 模板分类
            script_content: PowerShell 脚本内容
            keywords: 关键词列表
            author: 模板作者
            tags: 标签列表
            
        Returns:
            创建的 CustomTemplate 对象
            
        Raises:
            TemplateValidationError: 验证失败
            TemplateConflictError: 模板已存在
            TemplateError: 创建失败
        """
        # 验证输入
        self._validate_template_name(name)
        self._validate_category_name(category)
        
        # 生成模板 ID
        template_id = self._generate_template_id(name, category)
        
        # 检查模板是否已存在
        if self._template_exists(template_id, category):
            raise TemplateConflictError(
                f"模板 '{name}' 在分类 '{category}' 中已存在",
                details={'template_id': template_id, 'category': category}
            )
        
        # 使用 TemplateCreator 从脚本创建模板
        metadata = {
            'name': name,
            'description': description,
            'category': category,
            'keywords': keywords or []
        }
        
        template_content, param_config = self.creator.create_from_script(
            script_content,
            metadata
        )
        
        # 生成文件路径
        file_path = self._get_template_file_path(template_id, category)
        
        # 验证模板语法
        syntax_result = self.validator.validate_powershell_syntax(template_content)
        if not syntax_result.is_valid:
            raise TemplateValidationError(
                "模板语法验证失败",
                details={'errors': syntax_result.errors}
            )
        
        # 生成模板文件
        self.creator.generate_template_file(template_content, str(file_path))
        
        # 创建 CustomTemplate 对象
        template = CustomTemplate(
            id=template_id,
            name=name,
            description=description,
            file_path=str(file_path),
            category=category,
            keywords=keywords or [],
            parameters={
                param_name: TemplateParameter(
                    name=param_name,
                    type=param_info['type'],
                    default=param_info['default'],
                    description=param_info.get('description', ''),
                    required=param_info.get('required', False)
                )
                for param_name, param_info in param_config.items()
            },
            is_custom=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            author=author,
            version="1.0.0",
            tags=tags or []
        )
        
        # 验证完整模板
        validation_result = self.validator.validate_template(template)
        if not validation_result.is_valid:
            # 清理已创建的文件
            if file_path.exists():
                file_path.unlink()
            raise TemplateValidationError(
                "模板验证失败",
                details={'errors': validation_result.errors}
            )
        
        # 更新配置文件
        config_data = self._template_to_config(template)
        try:
            self.config_updater.add_template_config(
                template_id=template_id,
                category=category,
                config=config_data
            )
        except Exception as e:
            # 配置更新失败，清理文件
            if file_path.exists():
                file_path.unlink()
            raise TemplateError(
                f"配置更新失败: {str(e)}",
                details={'template_id': template_id}
            )
        
        return template
    
    def edit_template(
        self,
        template_id: str,
        category: str,
        updates: Dict[str, Any]
    ) -> CustomTemplate:
        """
        编辑现有模板
        
        协调编辑流程：加载模板 -> 应用更新 -> 验证 -> 保存 -> 更新配置
        
        Args:
            template_id: 模板 ID
            category: 模板分类
            updates: 更新字典，可包含:
                - name: 新名称
                - description: 新描述
                - keywords: 新关键词列表
                - tags: 新标签列表
                - parameters: 参数更新字典
                - content: 新的脚本内容
                
        Returns:
            更新后的 CustomTemplate 对象
            
        Raises:
            TemplateNotFoundError: 模板不存在
            TemplateValidationError: 验证失败
            TemplateError: 编辑失败
        """
        # 加载现有模板
        template = self._load_template(template_id, category)
        
        # 确保是自定义模板
        if not isinstance(template, CustomTemplate):
            raise TemplateError(
                "只能编辑自定义模板",
                details={'template_id': template_id, 'is_custom': False}
            )
        
        # 应用元数据更新
        metadata_updates = {
            k: v for k, v in updates.items()
            if k in ['name', 'description', 'keywords', 'tags']
        }
        if metadata_updates:
            template = self.editor.update_metadata(template, metadata_updates)
        
        # 应用参数更新
        if 'parameters' in updates:
            template = self.editor.update_parameters(template, updates['parameters'])
        
        # 应用内容更新
        if 'content' in updates:
            template = self.editor.update_content(template, updates['content'])
        
        # 更新配置文件
        config_data = self._template_to_config(template)
        self.config_updater.update_template_config(
            template_id=template_id,
            category=category,
            config=config_data
        )
        
        return template
    
    def delete_template(
        self,
        template_id: str,
        category: str
    ) -> bool:
        """
        删除自定义模板
        
        删除模板文件和配置，包含安全检查防止删除系统模板。
        
        Args:
            template_id: 模板 ID
            category: 模板分类
            
        Returns:
            是否删除成功
            
        Raises:
            TemplateNotFoundError: 模板不存在
            TemplateError: 不允许删除系统模板或删除失败
        """
        # 安全检查：防止删除系统模板
        if category in self.system_categories:
            raise TemplateError(
                f"不允许删除系统模板分类 '{category}' 中的模板",
                details={'template_id': template_id, 'category': category}
            )
        
        # 加载模板以验证其存在
        template = self._load_template(template_id, category)
        
        # 确保是自定义模板
        if not isinstance(template, CustomTemplate) and not template.is_custom:
            raise TemplateError(
                "只能删除自定义模板",
                details={'template_id': template_id, 'is_custom': False}
            )
        
        # 删除模板文件
        file_path = Path(template.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as e:
                raise TemplateError(
                    f"无法删除模板文件: {str(e)}",
                    details={'file_path': str(file_path)}
                )
        
        # 从配置中移除
        try:
            self.config_updater.remove_template_config(
                template_id=template_id,
                category=category
            )
        except Exception as e:
            # 配置移除失败，但文件已删除，记录警告
            print(f"警告: 配置移除失败: {str(e)}")
        
        return True
    
    def list_custom_templates(
        self,
        category: Optional[str] = None
    ) -> List[CustomTemplate]:
        """
        列出所有自定义模板
        
        Args:
            category: 可选的分类过滤器
            
        Returns:
            CustomTemplate 对象列表
        """
        templates = []
        
        # 遍历自定义模板目录
        if category:
            # 只列出指定分类
            category_dir = self.custom_templates_dir / category
            if category_dir.exists():
                templates.extend(self._load_templates_from_directory(category_dir, category))
        else:
            # 列出所有自定义模板
            for category_dir in self.custom_templates_dir.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    templates.extend(
                        self._load_templates_from_directory(category_dir, category_name)
                    )
        
        return templates
    
    def get_template_info(
        self,
        template_id: str,
        category: str
    ) -> Dict[str, Any]:
        """
        获取模板详细信息
        
        Args:
            template_id: 模板 ID
            category: 模板分类
            
        Returns:
            包含模板详细信息的字典
            
        Raises:
            TemplateNotFoundError: 模板不存在
        """
        template = self._load_template(template_id, category)
        
        info = {
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'category': template.category,
            'file_path': template.file_path,
            'keywords': template.keywords,
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
        
        # 添加 CustomTemplate 特有信息
        if isinstance(template, CustomTemplate):
            info.update({
                'is_custom': template.is_custom,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat(),
                'author': template.author,
                'version': template.version,
                'tags': template.tags
            })
        
        return info
    
    def _validate_template_name(self, name: str) -> None:
        """验证模板名称"""
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
    
    def _validate_category_name(self, category: str) -> None:
        """验证分类名称"""
        if not category or not category.strip():
            raise TemplateValidationError(
                "分类名称不能为空",
                details={'field': 'category'}
            )
        
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', category):
            raise TemplateValidationError(
                "分类名称只能包含字母、数字、下划线和连字符",
                details={'field': 'category', 'value': category}
            )
    
    def _generate_template_id(self, name: str, category: str) -> str:
        """生成模板 ID"""
        # 将名称转换为有效的文件名
        import re
        import unicodedata
        
        # 移除特殊字符，保留字母、数字、空格和连字符
        # 对于非ASCII字符（如中文），使用拼音或保留原样
        safe_name = name.lower()
        
        # 移除标点符号和特殊字符
        safe_name = re.sub(r'[^\w\s-]', '', safe_name, flags=re.UNICODE)
        
        # 将空格和连字符替换为下划线
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        
        # 移除前后的下划线
        safe_name = safe_name.strip('_')
        
        # 如果结果为空（全是特殊字符），使用时间戳
        if not safe_name:
            from datetime import datetime
            safe_name = f"template_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return safe_name
    
    def _get_template_file_path(self, template_id: str, category: str) -> Path:
        """获取模板文件路径"""
        category_dir = self.custom_templates_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        return category_dir / f"{template_id}.ps1"
    
    def _template_exists(self, template_id: str, category: str) -> bool:
        """检查模板是否存在"""
        file_path = self._get_template_file_path(template_id, category)
        return file_path.exists()
    
    def _load_template(self, template_id: str, category: str) -> CustomTemplate:
        """加载模板"""
        # 从配置获取模板信息
        config = self.config_updater.get_template_config(template_id, category)
        
        if not config:
            raise TemplateNotFoundError(
                f"模板 '{template_id}' 在分类 '{category}' 中不存在",
                details={'template_id': template_id, 'category': category}
            )
        
        # 构建模板对象
        file_path = config.get('file', str(self._get_template_file_path(template_id, category)))
        
        # 解析参数
        parameters = {}
        if 'parameters' in config:
            for param_name, param_data in config['parameters'].items():
                parameters[param_name] = TemplateParameter(
                    name=param_name,
                    type=param_data.get('type', 'string'),
                    default=param_data.get('default'),
                    description=param_data.get('description', ''),
                    required=param_data.get('required', False)
                )
        
        # 创建模板对象
        if config.get('is_custom', False):
            template = CustomTemplate(
                id=template_id,
                name=config['name'],
                description=config.get('description', ''),
                file_path=file_path,
                category=category,
                keywords=config.get('keywords', []),
                parameters=parameters,
                is_custom=True,
                created_at=datetime.fromisoformat(config.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(config.get('updated_at', datetime.now().isoformat())),
                author=config.get('author', 'user'),
                version=config.get('version', '1.0.0'),
                tags=config.get('tags', [])
            )
        else:
            template = Template(
                id=template_id,
                name=config['name'],
                description=config.get('description', ''),
                file_path=file_path,
                category=category,
                keywords=config.get('keywords', []),
                parameters=parameters
            )
        
        return template
    
    def _load_templates_from_directory(
        self,
        directory: Path,
        category: str
    ) -> List[CustomTemplate]:
        """从目录加载所有模板"""
        templates = []
        
        for file_path in directory.glob("*.ps1"):
            template_id = file_path.stem
            try:
                template = self._load_template(template_id, category)
                if isinstance(template, CustomTemplate):
                    templates.append(template)
            except Exception as e:
                # 跳过加载失败的模板
                print(f"警告: 加载模板 {template_id} 失败: {str(e)}")
                continue
        
        return templates
    
    def create_category(self, category_name: str) -> bool:
        """
        创建新的模板分类目录
        
        Args:
            category_name: 分类名称
            
        Returns:
            是否创建成功
            
        Raises:
            TemplateValidationError: 分类名称无效
            TemplateConflictError: 分类已存在
            TemplateError: 创建失败
        """
        # 验证分类名称
        self._validate_category_name(category_name)
        
        # 检查是否为系统分类
        if category_name in self.system_categories:
            raise TemplateConflictError(
                f"分类 '{category_name}' 是系统分类，不能重复创建",
                details={'category': category_name, 'is_system': True}
            )
        
        # 检查分类目录是否已存在
        category_dir = self.custom_templates_dir / category_name
        if category_dir.exists():
            raise TemplateConflictError(
                f"分类 '{category_name}' 已存在",
                details={'category': category_name, 'path': str(category_dir)}
            )
        
        # 创建分类目录
        try:
            category_dir.mkdir(parents=True, exist_ok=False)
            return True
        except OSError as e:
            raise TemplateError(
                f"创建分类目录失败: {str(e)}",
                details={'category': category_name, 'path': str(category_dir)}
            )
    
    def list_categories(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        列出所有分类（系统+自定义）
        
        Args:
            include_system: 是否包含系统分类
            
        Returns:
            分类信息列表，每个分类包含:
                - name: 分类名称
                - is_system: 是否为系统分类
                - template_count: 模板数量
                - path: 分类目录路径
        """
        categories = []
        
        # 添加系统分类
        if include_system:
            for sys_category in self.system_categories:
                sys_category_dir = self.templates_dir / sys_category
                template_count = 0
                if sys_category_dir.exists():
                    template_count = len(list(sys_category_dir.glob("*.ps1")))
                
                categories.append({
                    'name': sys_category,
                    'is_system': True,
                    'template_count': template_count,
                    'path': str(sys_category_dir)
                })
        
        # 添加自定义分类
        if self.custom_templates_dir.exists():
            for category_dir in self.custom_templates_dir.iterdir():
                if category_dir.is_dir():
                    template_count = len(list(category_dir.glob("*.ps1")))
                    categories.append({
                        'name': category_dir.name,
                        'is_system': False,
                        'template_count': template_count,
                        'path': str(category_dir)
                    })
        
        # 按名称排序
        categories.sort(key=lambda x: (not x['is_system'], x['name']))
        
        return categories
    
    def delete_category(self, category_name: str, force: bool = False) -> bool:
        """
        删除空的自定义分类
        
        Args:
            category_name: 分类名称
            force: 是否强制删除（即使包含模板）
            
        Returns:
            是否删除成功
            
        Raises:
            TemplateError: 不允许删除系统分类、分类不为空或删除失败
        """
        # 安全检查：防止删除系统分类
        if category_name in self.system_categories:
            raise TemplateError(
                f"不允许删除系统分类 '{category_name}'",
                details={'category': category_name, 'is_system': True}
            )
        
        # 获取分类目录
        category_dir = self.custom_templates_dir / category_name
        
        # 检查分类是否存在
        if not category_dir.exists():
            raise TemplateNotFoundError(
                f"分类 '{category_name}' 不存在",
                details={'category': category_name, 'path': str(category_dir)}
            )
        
        # 检查分类是否为空
        templates = list(category_dir.glob("*.ps1"))
        if templates and not force:
            raise TemplateError(
                f"分类 '{category_name}' 不为空，包含 {len(templates)} 个模板",
                details={
                    'category': category_name,
                    'template_count': len(templates),
                    'hint': '使用 force=True 强制删除'
                }
            )
        
        # 删除分类目录及其内容
        try:
            import shutil
            shutil.rmtree(category_dir)
            
            # 如果强制删除，还需要从配置中移除所有模板
            if force and templates:
                for template_file in templates:
                    template_id = template_file.stem
                    try:
                        self.config_updater.remove_template_config(
                            template_id=template_id,
                            category=category_name
                        )
                    except Exception as e:
                        print(f"警告: 移除模板配置失败 {template_id}: {str(e)}")
            
            return True
            
        except OSError as e:
            raise TemplateError(
                f"删除分类目录失败: {str(e)}",
                details={'category': category_name, 'path': str(category_dir)}
            )
    
    def move_template(
        self,
        template_id: str,
        from_category: str,
        to_category: str
    ) -> CustomTemplate:
        """
        移动模板到其他分类
        
        Args:
            template_id: 模板 ID
            from_category: 源分类
            to_category: 目标分类
            
        Returns:
            移动后的 CustomTemplate 对象
            
        Raises:
            TemplateNotFoundError: 模板不存在
            TemplateConflictError: 目标分类中已存在同名模板
            TemplateError: 移动失败
        """
        # 验证目标分类名称
        self._validate_category_name(to_category)
        
        # 不允许移动到系统分类
        if to_category in self.system_categories:
            raise TemplateError(
                f"不允许移动模板到系统分类 '{to_category}'",
                details={'to_category': to_category, 'is_system': True}
            )
        
        # 加载源模板
        template = self._load_template(template_id, from_category)
        
        # 确保是自定义模板
        if not isinstance(template, CustomTemplate):
            raise TemplateError(
                "只能移动自定义模板",
                details={'template_id': template_id, 'is_custom': False}
            )
        
        # 检查目标分类中是否已存在同名模板
        if self._template_exists(template_id, to_category):
            raise TemplateConflictError(
                f"模板 '{template_id}' 在目标分类 '{to_category}' 中已存在",
                details={
                    'template_id': template_id,
                    'from_category': from_category,
                    'to_category': to_category
                }
            )
        
        # 获取源文件和目标文件路径
        source_file = Path(template.file_path)
        target_file = self._get_template_file_path(template_id, to_category)
        
        # 确保目标目录存在
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        try:
            import shutil
            shutil.move(str(source_file), str(target_file))
        except OSError as e:
            raise TemplateError(
                f"移动模板文件失败: {str(e)}",
                details={
                    'source': str(source_file),
                    'target': str(target_file)
                }
            )
        
        # 更新模板对象
        template.category = to_category
        template.file_path = str(target_file)
        template.updated_at = datetime.now()
        
        # 更新配置文件
        try:
            # 从源分类移除
            self.config_updater.remove_template_config(
                template_id=template_id,
                category=from_category
            )
            
            # 添加到目标分类
            config_data = self._template_to_config(template)
            self.config_updater.add_template_config(
                template_id=template_id,
                category=to_category,
                config=config_data
            )
            
        except Exception as e:
            # 配置更新失败，尝试回滚文件移动
            try:
                shutil.move(str(target_file), str(source_file))
            except Exception:
                pass
            
            raise TemplateError(
                f"更新配置失败: {str(e)}",
                details={
                    'template_id': template_id,
                    'from_category': from_category,
                    'to_category': to_category
                }
            )
        
        return template
    
    def _template_to_config(self, template: CustomTemplate) -> Dict[str, Any]:
        """将模板对象转换为配置字典"""
        config = {
            'name': template.name,
            'description': template.description,
            'file': template.file_path,
            'keywords': template.keywords,
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
        
        return config
