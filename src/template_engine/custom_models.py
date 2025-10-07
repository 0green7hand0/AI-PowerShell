"""
自定义模板数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from .models import Template, TemplateParameter


@dataclass
class CustomTemplate(Template):
    """
    自定义模板（扩展基础 Template 类）
    
    用户创建的自定义模板，包含额外的元数据用于版本控制、
    作者信息和标签管理。
    
    Attributes:
        is_custom: 标识这是一个自定义模板（始终为 True）
        created_at: 模板创建时间
        updated_at: 模板最后更新时间
        author: 模板作者（默认为 "user"）
        version: 模板版本号（语义化版本）
        tags: 模板标签列表，用于分类和搜索
    """
    is_custom: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = "user"
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    
    def update_timestamp(self):
        """更新最后修改时间"""
        self.updated_at = datetime.now()
    
    def increment_version(self, version_type: str = "patch"):
        """
        递增版本号
        
        Args:
            version_type: 版本类型 - "major", "minor", 或 "patch"
        """
        major, minor, patch = map(int, self.version.split('.'))
        
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        self.version = f"{major}.{minor}.{patch}"
        self.update_timestamp()


@dataclass
class ParameterInfo:
    """
    参数信息（用于模板创建过程中的参数识别）
    
    在从现有脚本创建模板时，此类用于存储识别出的参数信息，
    包括参数的原始值、推断的类型和在脚本中的位置。
    
    Attributes:
        name: 参数名称（不包含 $ 符号）
        original_value: 参数的原始值（从脚本中提取）
        type: 推断的参数类型（string, integer, boolean, path）
        line_number: 参数在脚本中的行号
        context: 参数所在的代码上下文（前后几行代码）
        is_required: 是否为必需参数
        description: 参数描述（可选，用户可以添加）
    """
    name: str
    original_value: str
    type: str
    line_number: int
    context: str
    is_required: bool = False
    description: str = ""
    
    def to_template_parameter(self, default_value: any = None) -> TemplateParameter:
        """
        转换为 TemplateParameter 对象
        
        Args:
            default_value: 参数的默认值（如果未提供，使用 original_value）
        
        Returns:
            TemplateParameter 对象
        """
        return TemplateParameter(
            name=self.name,
            type=self.type,
            default=default_value if default_value is not None else self.original_value,
            description=self.description,
            required=self.is_required
        )


@dataclass
class TemplatePackage:
    """
    模板包（用于导入导出）
    
    用于打包模板文件、配置和元数据，以便在不同环境间
    传输或与其他用户共享。
    
    Attributes:
        template_file: 模板文件内容（PowerShell 脚本）
        config: 模板配置信息（参数、关键词等）
        metadata: 模板元数据（作者、版本、创建时间等）
        version: 包格式版本（用于兼容性检查）
        checksum: 包内容的校验和（用于验证完整性）
    """
    template_file: str
    config: Dict
    metadata: Dict
    version: str = "1.0"
    checksum: Optional[str] = None
    
    def validate(self) -> bool:
        """
        验证包的完整性
        
        Returns:
            True 如果包有效，否则 False
        """
        # 检查必需字段
        if not self.template_file or not self.config or not self.metadata:
            return False
        
        # 检查配置中的必需键
        required_config_keys = ['name', 'description', 'parameters']
        if not all(key in self.config for key in required_config_keys):
            return False
        
        # 检查元数据中的必需键
        required_metadata_keys = ['created_at', 'author', 'version']
        if not all(key in self.metadata for key in required_metadata_keys):
            return False
        
        return True
    
    def calculate_checksum(self) -> str:
        """
        计算包内容的校验和
        
        Returns:
            SHA256 校验和字符串
        """
        import hashlib
        
        content = f"{self.template_file}{str(self.config)}{str(self.metadata)}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def verify_checksum(self) -> bool:
        """
        验证包的校验和
        
        Returns:
            True 如果校验和匹配，否则 False
        """
        if self.checksum is None:
            return False
        return self.calculate_checksum() == self.checksum


@dataclass
class TemplateVersion:
    """
    模板版本（用于版本控制）
    
    存储模板的历史版本，支持版本回滚和变更追踪。
    
    Attributes:
        template_id: 模板的唯一标识符
        version_number: 版本号（递增的整数）
        content: 该版本的模板内容
        config: 该版本的模板配置
        timestamp: 版本创建时间
        change_description: 变更描述（用户提供的说明）
        author: 进行此次修改的作者
        file_path: 版本文件的存储路径
    """
    template_id: str
    version_number: int
    content: str
    config: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    change_description: str = ""
    author: str = "user"
    file_path: Optional[str] = None
    
    def get_version_tag(self) -> str:
        """
        获取版本标签
        
        Returns:
            格式化的版本标签，如 "v1_20251007_120000"
        """
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        return f"v{self.version_number}_{timestamp_str}"
    
    def get_display_info(self) -> str:
        """
        获取版本的显示信息
        
        Returns:
            格式化的版本信息字符串
        """
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        desc = self.change_description if self.change_description else "No description"
        return f"Version {self.version_number} | {timestamp_str} | {self.author} | {desc}"
    
    def __str__(self):
        return f"TemplateVersion(id={self.template_id}, version={self.version_number}, timestamp={self.timestamp})"


@dataclass
class ValidationResult:
    """
    验证结果
    
    用于存储模板验证的结果，包括验证是否通过、
    错误信息和警告信息。
    
    Attributes:
        is_valid: 验证是否通过
        errors: 错误列表（阻止模板使用的问题）
        warnings: 警告列表（不阻止使用但建议修复的问题）
        suggestions: 改进建议列表
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """添加错误"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)
    
    def add_suggestion(self, suggestion: str):
        """添加建议"""
        self.suggestions.append(suggestion)
    
    def get_summary(self) -> str:
        """
        获取验证结果摘要
        
        Returns:
            格式化的验证结果摘要
        """
        lines = []
        
        if self.is_valid:
            lines.append("✓ 验证通过")
        else:
            lines.append("✗ 验证失败")
        
        if self.errors:
            lines.append(f"\n错误 ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"  {i}. {error}")
        
        if self.warnings:
            lines.append(f"\n警告 ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {warning}")
        
        if self.suggestions:
            lines.append(f"\n建议 ({len(self.suggestions)}):")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
        
        return "\n".join(lines)
    
    def __str__(self):
        return self.get_summary()
