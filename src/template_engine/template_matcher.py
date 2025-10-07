"""
模板匹配器

根据用户意图匹配最合适的脚本模板。
"""

from typing import List, Optional
from .models import Intent, Template, TemplateMatch, TemplateCategory
from .custom_models import CustomTemplate


class TemplateMatcher:
    """模板匹配器"""
    
    def __init__(self, template_manager):
        """
        初始化模板匹配器
        
        Args:
            template_manager: 模板管理器实例
        """
        self.template_manager = template_manager
        self.action_to_template = self._build_action_mapping()
    
    def _build_action_mapping(self) -> dict:
        """构建操作到模板的映射"""
        return {
            'rename': ['batch_rename'],
            'organize': ['file_organizer'],
            'monitor': ['resource_monitor'],
            'backup': ['backup_files'],
            'cleanup': ['disk_cleanup'],
        }
    
    def match(self, intent: Intent) -> Optional[TemplateMatch]:
        """
        匹配模板
        
        Args:
            intent: 用户意图
            
        Returns:
            最佳匹配的模板，如果没有匹配则返回None
        """
        # 获取所有候选模板
        candidates = self._get_candidates(intent)
        
        if not candidates:
            return None
        
        # 计算每个候选模板的匹配分数
        matches = []
        for template in candidates:
            score, matched_keywords = self._calculate_score(intent, template)
            
            if score > 0:
                matches.append(TemplateMatch(
                    template=template,
                    score=score,
                    matched_keywords=matched_keywords,
                    reason=f"匹配操作: {intent.action}, 目标: {intent.target}"
                ))
        
        # 按分数排序
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # 返回最佳匹配
        return matches[0] if matches else None
    
    def _get_candidates(self, intent: Intent) -> List[Template]:
        """获取候选模板"""
        candidates = []
        
        # 1. 根据操作类型获取模板
        template_ids = self.action_to_template.get(intent.action, [])
        for template_id in template_ids:
            template = self.template_manager.get_template(template_id)
            if template:
                candidates.append(template)
        
        # 2. 如果没有找到，尝试关键词搜索
        if not candidates:
            keywords = [intent.action, intent.target] + list(intent.parameters.keys())
            candidates = self.template_manager.search_templates(keywords)
        
        return candidates
    
    def _calculate_score(
        self,
        intent: Intent,
        template: Template
    ) -> tuple[float, List[str]]:
        """
        计算匹配分数（支持系统模板和自定义模板）
        
        Returns:
            (分数, 匹配的关键词列表)
        """
        score = 0.0
        matched_keywords = []
        
        # 1. 操作类型匹配 (权重: 10)
        if intent.action in template.keywords:
            score += 10
            matched_keywords.append(intent.action)
        
        # 2. 目标对象匹配 (权重: 5)
        if intent.target in template.keywords:
            score += 5
            matched_keywords.append(intent.target)
        
        # 3. 参数匹配 (权重: 3)
        for param_name in intent.parameters.keys():
            if param_name in template.parameters:
                score += 3
                matched_keywords.append(param_name)
        
        # 4. 关键词部分匹配 (权重: 2)
        intent_text = intent.raw_input.lower()
        for keyword in template.keywords:
            if keyword.lower() in intent_text:
                score += 2
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
        
        # 5. 对于自定义模板，检查标签匹配 (权重: 2)
        if isinstance(template, CustomTemplate):
            for tag in template.tags:
                if tag.lower() in intent_text:
                    score += 2
                    if tag not in matched_keywords:
                        matched_keywords.append(tag)
        
        # 6. 置信度加成
        score *= intent.confidence
        
        return score, matched_keywords
    
    def get_all_matches(self, intent: Intent, top_n: int = 3) -> List[TemplateMatch]:
        """
        获取所有匹配的模板
        
        Args:
            intent: 用户意图
            top_n: 返回前N个匹配
            
        Returns:
            匹配列表
        """
        candidates = self._get_candidates(intent)
        
        matches = []
        for template in candidates:
            score, matched_keywords = self._calculate_score(intent, template)
            
            if score > 0:
                matches.append(TemplateMatch(
                    template=template,
                    score=score,
                    matched_keywords=matched_keywords
                ))
        
        # 按分数排序
        matches.sort(key=lambda x: x.score, reverse=True)
        
        return matches[:top_n]
