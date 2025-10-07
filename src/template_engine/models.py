"""
模板引擎数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TemplateCategory(Enum):
    """模板分类"""
    FILE_MANAGEMENT = "file_management"
    SYSTEM_MONITORING = "system_monitoring"
    AUTOMATION = "automation"
    DATA_PROCESSING = "data_processing"
    OFFICE_AUTOMATION = "office_automation"


@dataclass
class TemplateParameter:
    """模板参数"""
    name: str
    type: str  # string, integer, boolean
    default: any
    description: str
    required: bool = False


@dataclass
class Template:
    """脚本模板"""
    id: str
    name: str
    category: TemplateCategory
    file_path: str
    description: str
    keywords: List[str]
    parameters: Dict[str, TemplateParameter]
    examples: List[str] = field(default_factory=list)
    content: Optional[str] = None
    
    def load_content(self) -> str:
        """加载模板内容"""
        if self.content is None:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
        return self.content


@dataclass
class Intent:
    """用户意图"""
    action: str  # 操作类型：rename, organize, monitor, backup, cleanup
    target: str  # 目标对象：files, system, disk
    parameters: Dict[str, any] = field(default_factory=dict)
    confidence: float = 0.0
    raw_input: str = ""
    
    def __str__(self):
        return f"Intent(action={self.action}, target={self.target}, confidence={self.confidence:.2f})"


@dataclass
class TemplateMatch:
    """模板匹配结果"""
    template: Template
    score: float
    matched_keywords: List[str] = field(default_factory=list)
    reason: str = ""
    
    def __str__(self):
        return f"TemplateMatch(template={self.template.name}, score={self.score:.2f})"


@dataclass
class GeneratedScript:
    """生成的脚本"""
    template_id: str
    template_name: str
    content: str
    file_path: str
    parameters: Dict[str, any]
    user_request: str
    generated_at: datetime = field(default_factory=datetime.now)
    
    def save(self):
        """保存脚本到文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def __str__(self):
        return f"GeneratedScript(template={self.template_name}, file={self.file_path})"
