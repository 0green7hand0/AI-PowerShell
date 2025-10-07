"""
模板导入导出器

提供模板的打包导出和解包导入功能，支持模板在不同环境间传输和共享。
"""

import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

from .custom_models import TemplatePackage, CustomTemplate, ValidationResult
from .exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateConflictError,
    TemplateValidationError,
    TemplateIOError
)


class TemplateExporter:
    """
    模板导入导出器
    
    负责将模板打包为 ZIP 文件以便导出，以及从 ZIP 包中导入模板。
    支持包格式验证、冲突检测和处理。
    
    包结构:
        template_name.zip
        ├── template.ps1          # 模板脚本文件
        ├── config.json           # 模板配置
        ├── metadata.json         # 模板元数据
        └── manifest.json         # 包清单（版本、校验和等）
    """
    
    def __init__(self, templates_dir: str, config_path: str):
        """
        初始化导出器
        
        Args:
            templates_dir: 模板目录路径
            config_path: 配置文件路径
        """
        self.templates_dir = Path(templates_dir)
        self.config_path = Path(config_path)
        self.exports_dir = self.templates_dir / ".exports"
        
        # 确保导出目录存在
        self.exports_dir.mkdir(parents=True, exist_ok=True)
    
    def export_template(
        self,
        template: CustomTemplate,
        output_path: Optional[str] = None,
        include_metadata: bool = True
    ) -> str:
        """
        导出模板为 ZIP 包
        
        Args:
            template: 要导出的模板对象
            output_path: 输出路径（可选，默认保存到 .exports 目录）
            include_metadata: 是否包含元数据（作者、创建时间等）
        
        Returns:
            导出的 ZIP 文件路径
        
        Raises:
            TemplateNotFoundError: 模板文件不存在
            TemplateIOError: 文件操作失败
        """
        # 验证模板文件存在
        template_file_path = Path(template.file_path)
        if not template_file_path.exists():
            raise TemplateNotFoundError(
                f"Template file not found: {template.file_path}",
                {"template_id": template.id, "file_path": template.file_path}
            )
        
        # 读取模板内容
        try:
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except Exception as e:
            raise TemplateIOError(
                f"Failed to read template file: {str(e)}",
                {"file_path": template.file_path, "operation": "read"}
            )
        
        # 准备配置数据
        config_data = {
            "name": template.name,
            "description": template.description,
            "category": template.category.value if hasattr(template.category, 'value') else str(template.category),
            "keywords": template.keywords,
            "parameters": {
                name: {
                    "name": param.name,
                    "type": param.type,
                    "default": param.default,
                    "description": param.description,
                    "required": param.required
                }
                for name, param in template.parameters.items()
            }
        }
        
        # 准备元数据
        metadata = {}
        if include_metadata:
            metadata = {
                "template_id": template.id,
                "author": template.author,
                "version": template.version,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat(),
                "tags": template.tags,
                "is_custom": template.is_custom
            }
        
        # 创建包对象
        package = TemplatePackage(
            template_file=template_content,
            config=config_data,
            metadata=metadata,
            version="1.0"
        )
        
        # 计算校验和
        package.checksum = package.calculate_checksum()
        
        # 确定输出路径
        if output_path is None:
            safe_name = self._sanitize_filename(template.name)
            output_path = str(self.exports_dir / f"{safe_name}.zip")
        
        # 创建 ZIP 包
        try:
            self._create_zip_package(package, output_path, template.name)
        except Exception as e:
            raise TemplateIOError(
                f"Failed to create ZIP package: {str(e)}",
                {"output_path": output_path, "operation": "write"}
            )
        
        return output_path

    
    def import_template(
        self,
        package_path: str,
        target_category: Optional[str] = None,
        conflict_resolution: str = "ask"
    ) -> Tuple[Optional[CustomTemplate], str]:
        """
        从 ZIP 包导入模板
        
        Args:
            package_path: ZIP 包路径
            target_category: 目标分类（可选，默认使用包中的分类）
            conflict_resolution: 冲突解决策略 - "ask", "overwrite", "rename", "skip"
        
        Returns:
            (导入的模板对象, 操作结果消息)
        
        Raises:
            TemplateValidationError: 包格式无效
            TemplateConflictError: 模板冲突且未解决
            TemplateIOError: 文件操作失败
        """
        # 验证包文件存在
        package_path = Path(package_path)
        if not package_path.exists():
            raise TemplateNotFoundError(
                f"Package file not found: {package_path}",
                {"package_path": str(package_path)}
            )
        
        # 解压并验证包
        try:
            package = self._extract_and_validate_package(package_path)
        except Exception as e:
            raise TemplateValidationError(
                f"Failed to extract or validate package: {str(e)}",
                {"package_path": str(package_path)}
            )
        
        # 确定目标分类
        category = target_category or package.config.get("category", "custom")
        
        # 检查冲突
        template_name = package.config["name"]
        conflict_info = self._check_conflict(template_name, category)
        
        resolution = None
        if conflict_info["has_conflict"]:
            # 处理冲突
            resolution = self._handle_conflict(
                template_name,
                conflict_info,
                conflict_resolution
            )
            
            if resolution["action"] == "skip":
                return None, "Import skipped due to conflict"
            elif resolution["action"] == "rename":
                template_name = resolution["new_name"]
                package.config["name"] = template_name
            # overwrite 不需要特殊处理，直接覆盖
        
        # 创建模板对象
        template = self._create_template_from_package(package, category)
        
        # 保存模板文件
        try:
            self._save_template_files(template, package)
        except Exception as e:
            raise TemplateIOError(
                f"Failed to save template files: {str(e)}",
                {"template_name": template_name, "operation": "write"}
            )
        
        result_msg = f"Template '{template_name}' imported successfully"
        if conflict_info["has_conflict"] and resolution:
            result_msg += f" (conflict resolved: {resolution['action']})"
        
        return template, result_msg
    
    def validate_package(self, package_path: str) -> ValidationResult:
        """
        验证导入包的格式和完整性
        
        Args:
            package_path: ZIP 包路径
        
        Returns:
            ValidationResult 对象
        """
        result = ValidationResult(is_valid=True)
        
        # 检查文件存在
        package_path = Path(package_path)
        if not package_path.exists():
            result.add_error(f"Package file not found: {package_path}")
            return result
        
        # 检查是否为 ZIP 文件
        if not zipfile.is_zipfile(package_path):
            result.add_error("File is not a valid ZIP archive")
            return result
        
        try:
            with zipfile.ZipFile(package_path, 'r') as zf:
                # 检查必需文件
                required_files = ['template.ps1', 'config.json', 'manifest.json']
                file_list = zf.namelist()
                
                for required_file in required_files:
                    if required_file not in file_list:
                        result.add_error(f"Missing required file: {required_file}")
                
                if not result.is_valid:
                    return result
                
                # 验证 JSON 文件格式
                try:
                    config_data = json.loads(zf.read('config.json').decode('utf-8'))
                    manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
                except json.JSONDecodeError as e:
                    result.add_error(f"Invalid JSON format: {str(e)}")
                    return result
                
                # 验证配置完整性
                required_config_keys = ['name', 'description', 'parameters']
                for key in required_config_keys:
                    if key not in config_data:
                        result.add_error(f"Missing required config key: {key}")
                
                # 验证清单
                if 'version' not in manifest_data:
                    result.add_warning("Package version not specified")
                
                if 'checksum' in manifest_data:
                    # 验证校验和
                    template_content = zf.read('template.ps1').decode('utf-8')
                    package = TemplatePackage(
                        template_file=template_content,
                        config=config_data,
                        metadata=manifest_data.get('metadata', {}),
                        version=manifest_data.get('version', '1.0'),
                        checksum=manifest_data['checksum']
                    )
                    
                    if not package.verify_checksum():
                        result.add_error("Checksum verification failed - package may be corrupted")
                else:
                    result.add_warning("No checksum found - cannot verify package integrity")
                
                # 验证模板内容
                template_content = zf.read('template.ps1').decode('utf-8')
                if not template_content.strip():
                    result.add_error("Template file is empty")
                
        except Exception as e:
            result.add_error(f"Failed to validate package: {str(e)}")
        
        return result

    
    def _create_zip_package(
        self,
        package: TemplatePackage,
        output_path: str,
        template_name: str
    ):
        """
        创建 ZIP 包
        
        Args:
            package: 模板包对象
            output_path: 输出路径
            template_name: 模板名称
        """
        # 创建清单
        manifest = {
            "version": package.version,
            "checksum": package.checksum,
            "exported_at": datetime.now().isoformat(),
            "template_name": template_name,
            "metadata": package.metadata
        }
        
        # 创建 ZIP 文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 写入模板文件
            zf.writestr('template.ps1', package.template_file)
            
            # 写入配置
            zf.writestr('config.json', json.dumps(package.config, indent=2, ensure_ascii=False))
            
            # 写入清单
            zf.writestr('manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
            
            # 如果有元数据，单独写入
            if package.metadata:
                zf.writestr('metadata.json', json.dumps(package.metadata, indent=2, ensure_ascii=False))
    
    def _extract_and_validate_package(self, package_path: Path) -> TemplatePackage:
        """
        解压并验证包
        
        Args:
            package_path: 包文件路径
        
        Returns:
            TemplatePackage 对象
        
        Raises:
            TemplateValidationError: 包格式无效
        """
        # 先验证包
        validation_result = self.validate_package(str(package_path))
        if not validation_result.is_valid:
            raise TemplateValidationError(
                "Package validation failed",
                {"errors": validation_result.errors}
            )
        
        # 解压包
        with zipfile.ZipFile(package_path, 'r') as zf:
            template_content = zf.read('template.ps1').decode('utf-8')
            config_data = json.loads(zf.read('config.json').decode('utf-8'))
            manifest_data = json.loads(zf.read('manifest.json').decode('utf-8'))
            
            # 读取元数据（如果存在）
            metadata = {}
            if 'metadata.json' in zf.namelist():
                metadata = json.loads(zf.read('metadata.json').decode('utf-8'))
            elif 'metadata' in manifest_data:
                metadata = manifest_data['metadata']
            
            # 创建包对象
            package = TemplatePackage(
                template_file=template_content,
                config=config_data,
                metadata=metadata,
                version=manifest_data.get('version', '1.0'),
                checksum=manifest_data.get('checksum')
            )
            
            return package
    
    def _check_conflict(self, template_name: str, category: str) -> Dict:
        """
        检查模板名称冲突
        
        Args:
            template_name: 模板名称
            category: 模板分类
        
        Returns:
            冲突信息字典
        """
        # 构建目标路径 - 使用 sanitized 名称作为文件名
        sanitized_name = self._sanitize_filename(template_name)
        category_dir = self.templates_dir / category
        template_file = category_dir / f"{sanitized_name}.ps1"
        
        has_conflict = template_file.exists()
        
        return {
            "has_conflict": has_conflict,
            "existing_path": str(template_file) if has_conflict else None,
            "template_name": template_name,
            "category": category
        }
    
    def _handle_conflict(
        self,
        template_name: str,
        conflict_info: Dict,
        resolution: str
    ) -> Dict:
        """
        处理模板名称冲突
        
        Args:
            template_name: 模板名称
            conflict_info: 冲突信息
            resolution: 解决策略 - "ask", "overwrite", "rename", "skip"
        
        Returns:
            解决方案字典，包含 action 和可能的 new_name
        
        Raises:
            TemplateConflictError: 冲突未解决
        """
        if resolution == "skip":
            return {"action": "skip"}
        
        elif resolution == "overwrite":
            return {"action": "overwrite"}
        
        elif resolution == "rename":
            # 生成新名称
            new_name = self._generate_unique_name(template_name, conflict_info["category"])
            return {"action": "rename", "new_name": new_name}
        
        elif resolution == "ask":
            # 在实际应用中，这里应该提示用户选择
            # 为了自动化测试，默认使用 rename
            raise TemplateConflictError(
                f"Template '{template_name}' already exists in category '{conflict_info['category']}'",
                {
                    "template_name": template_name,
                    "existing_path": conflict_info["existing_path"],
                    "resolution_options": ["overwrite", "rename", "skip"]
                }
            )
        
        else:
            raise ValueError(f"Invalid conflict resolution strategy: {resolution}")
    
    def _generate_unique_name(self, base_name: str, category: str) -> str:
        """
        生成唯一的模板名称
        
        Args:
            base_name: 基础名称
            category: 模板分类
        
        Returns:
            唯一的模板名称
        """
        category_dir = self.templates_dir / category
        counter = 1
        
        while True:
            new_name = f"{base_name}_{counter}"
            template_file = category_dir / f"{self._sanitize_filename(new_name)}.ps1"
            
            if not template_file.exists():
                return new_name
            
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                raise TemplateError("Failed to generate unique template name")

    
    def _create_template_from_package(
        self,
        package: TemplatePackage,
        category: str
    ) -> CustomTemplate:
        """
        从包创建模板对象
        
        Args:
            package: 模板包
            category: 目标分类
        
        Returns:
            CustomTemplate 对象
        """
        from .models import TemplateParameter, TemplateCategory
        
        # 生成模板 ID - 使用 sanitized 名称
        template_name = package.config["name"]
        template_id = self._sanitize_filename(template_name)
        
        # 构建文件路径
        category_dir = self.templates_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        file_path = category_dir / f"{template_id}.ps1"
        
        # 转换参数
        parameters = {}
        for param_name, param_data in package.config.get("parameters", {}).items():
            parameters[param_name] = TemplateParameter(
                name=param_data["name"],
                type=param_data["type"],
                default=param_data.get("default"),
                description=param_data.get("description", ""),
                required=param_data.get("required", False)
            )
        
        # 尝试转换分类为枚举
        try:
            template_category = TemplateCategory(category)
        except ValueError:
            # 如果不是标准分类，使用字符串
            template_category = category
        
        # 创建模板对象
        template = CustomTemplate(
            id=template_id,
            name=package.config["name"],
            category=template_category,
            file_path=str(file_path),
            description=package.config.get("description", ""),
            keywords=package.config.get("keywords", []),
            parameters=parameters,
            is_custom=True,
            author=package.metadata.get("author", "imported"),
            version=package.metadata.get("version", "1.0.0"),
            tags=package.metadata.get("tags", [])
        )
        
        # 如果包中有时间戳，使用它们
        if "created_at" in package.metadata:
            try:
                template.created_at = datetime.fromisoformat(package.metadata["created_at"])
            except:
                pass
        
        if "updated_at" in package.metadata:
            try:
                template.updated_at = datetime.fromisoformat(package.metadata["updated_at"])
            except:
                pass
        
        return template
    
    def _save_template_files(self, template: CustomTemplate, package: TemplatePackage):
        """
        保存模板文件
        
        Args:
            template: 模板对象
            package: 模板包
        """
        # 确保目录存在
        file_path = Path(template.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存模板文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(package.template_file)
    
    def _sanitize_filename(self, name: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            name: 原始名称
        
        Returns:
            安全的文件名
        """
        # 移除或替换不安全字符（包括空格）
        unsafe_chars = '<>:"/\\|?* '
        safe_name = name
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # 移除前后下划线
        safe_name = safe_name.strip('_')
        
        # 限制长度
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
        
        return safe_name
    
    def list_exports(self) -> list:
        """
        列出所有导出的模板包
        
        Returns:
            导出包文件路径列表
        """
        if not self.exports_dir.exists():
            return []
        
        return [str(f) for f in self.exports_dir.glob("*.zip")]
    
    def delete_export(self, export_path: str) -> bool:
        """
        删除导出的模板包
        
        Args:
            export_path: 导出包路径
        
        Returns:
            True 如果删除成功
        """
        export_path = Path(export_path)
        
        if export_path.exists():
            try:
                export_path.unlink()
                return True
            except Exception:
                return False
        
        return False
