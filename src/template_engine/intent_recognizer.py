"""
意图识别器

识别用户输入的意图，提取操作类型、目标对象和参数信息。
"""

import re
from typing import Dict, List, Tuple, Optional

from .models import Intent


class IntentRecognizer:
    """意图识别器"""
    
    def __init__(self):
        """初始化意图识别器"""
        self.action_patterns = self._build_action_patterns()
        self.target_patterns = self._build_target_patterns()
        self.parameter_extractors = self._build_parameter_extractors()
    
    def _build_action_patterns(self) -> Dict[str, List[str]]:
        """构建操作类型匹配模式"""
        return {
            'rename': [
                r'重命名', r'改名', r'rename', r'更名'
            ],
            'organize': [
                r'整理', r'分类', r'归档', r'organize', r'排序'
            ],
            'monitor': [
                r'监控', r'监测', r'检查', r'monitor', r'watch', r'观察'
            ],
            'backup': [
                r'备份', r'backup', r'保存', r'归档'
            ],
            'cleanup': [
                r'清理', r'清空', r'删除', r'cleanup', r'clean', r'清除'
            ],
            'search': [
                r'搜索', r'查找', r'find', r'search', r'寻找'
            ],
            'copy': [
                r'复制', r'拷贝', r'copy'
            ],
            'move': [
                r'移动', r'move', r'转移'
            ]
        }
    
    def _build_target_patterns(self) -> Dict[str, List[str]]:
        """构建目标对象匹配模式"""
        return {
            'files': [
                r'文件', r'file', r'照片', r'图片', r'文档', r'视频',
                r'photo', r'image', r'document', r'video'
            ],
            'folders': [
                r'文件夹', r'目录', r'folder', r'directory'
            ],
            'system': [
                r'系统', r'system', r'电脑', r'计算机', r'computer'
            ],
            'cpu': [
                r'CPU', r'cpu', r'处理器', r'processor'
            ],
            'memory': [
                r'内存', r'memory', r'RAM', r'ram'
            ],
            'disk': [
                r'磁盘', r'硬盘', r'disk', r'drive', r'空间'
            ],
            'network': [
                r'网络', r'network', r'连接', r'connection'
            ]
        }
    
    def _build_parameter_extractors(self) -> Dict[str, callable]:
        """构建参数提取器"""
        return {
            'file_type': self._extract_file_type,
            'path': self._extract_path,
            'naming_pattern': self._extract_naming_pattern,
            'threshold': self._extract_threshold,
            'interval': self._extract_interval,
            'days': self._extract_days,
        }
    
    def recognize(self, user_input: str) -> Intent:
        """
        识别用户意图
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Intent对象
        """
        user_input = user_input.strip()
        
        # 识别操作类型
        action, action_confidence = self._recognize_action(user_input)
        
        # 识别目标对象
        target, target_confidence = self._recognize_target(user_input)
        
        # 提取参数
        parameters = self._extract_parameters(user_input, action, target)
        
        # 计算总体置信度
        confidence = (action_confidence + target_confidence) / 2
        
        return Intent(
            action=action,
            target=target,
            parameters=parameters,
            confidence=confidence,
            raw_input=user_input
        )
    
    def _recognize_action(self, text: str) -> Tuple[str, float]:
        """
        识别操作类型
        
        Returns:
            (操作类型, 置信度)
        """
        text_lower = text.lower()
        
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return action, 0.9
        
        # 默认操作
        return 'unknown', 0.3
    
    def _recognize_target(self, text: str) -> Tuple[str, float]:
        """
        识别目标对象
        
        Returns:
            (目标对象, 置信度)
        """
        text_lower = text.lower()
        
        for target, patterns in self.target_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return target, 0.9
        
        # 默认目标
        return 'files', 0.5
    
    def _extract_parameters(
        self,
        text: str,
        action: str,
        target: str
    ) -> Dict[str, any]:
        """提取参数"""
        parameters = {}
        
        for param_name, extractor in self.parameter_extractors.items():
            value = extractor(text)
            if value is not None:
                parameters[param_name] = value
        
        return parameters
    
    def _extract_file_type(self, text: str) -> Optional[str]:
        """提取文件类型"""
        # 匹配文件扩展名
        match = re.search(r'\b(jpg|jpeg|png|gif|pdf|doc|docx|txt|mp4|avi|zip)\b', text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        
        # 匹配文件类型描述
        type_map = {
            '照片': 'jpg',
            '图片': 'jpg',
            '文档': 'docx',
            '视频': 'mp4',
            '音频': 'mp3',
        }
        
        for keyword, ext in type_map.items():
            if keyword in text:
                return ext
        
        return None
    
    def _extract_path(self, text: str) -> Optional[str]:
        """提取路径"""
        # 匹配Windows路径
        match = re.search(r'[A-Za-z]:\\[^\s]+', text)
        if match:
            return match.group(0)
        
        # 匹配相对路径
        match = re.search(r'\./[^\s]+', text)
        if match:
            return match.group(0)
        
        # 匹配常见位置
        location_map = {
            '桌面': '$env:USERPROFILE\\Desktop',
            '文档': '$env:USERPROFILE\\Documents',
            '下载': '$env:USERPROFILE\\Downloads',
            '图片': '$env:USERPROFILE\\Pictures',
        }
        
        for keyword, path in location_map.items():
            if keyword in text:
                return path
        
        return None
    
    def _extract_naming_pattern(self, text: str) -> Optional[str]:
        """提取命名规则"""
        # 匹配 "xxx_序号" 模式
        match = re.search(r'([a-zA-Z0-9_\u4e00-\u9fa5]+)_?序号', text)
        if match:
            return match.group(1)
        
        # 匹配 "改成 xxx" 模式
        match = re.search(r'改成\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)', text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_threshold(self, text: str) -> Optional[int]:
        """提取阈值"""
        # 匹配 "超过 80%" 模式
        match = re.search(r'超过\s*(\d+)\s*%', text)
        if match:
            return int(match.group(1))
        
        # 匹配 "大于 80" 模式
        match = re.search(r'大于\s*(\d+)', text)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_interval(self, text: str) -> Optional[int]:
        """提取时间间隔"""
        # 匹配 "每30秒" 模式
        match = re.search(r'每\s*(\d+)\s*秒', text)
        if match:
            return int(match.group(1))
        
        # 匹配 "30秒一次" 模式
        match = re.search(r'(\d+)\s*秒\s*一次', text)
        if match:
            return int(match.group(1))
        
        return None
    
    def _extract_days(self, text: str) -> Optional[int]:
        """提取天数"""
        # 匹配 "30天前" 模式
        match = re.search(r'(\d+)\s*天\s*前', text)
        if match:
            return int(match.group(1))
        
        # 匹配 "最近7天" 模式
        match = re.search(r'最近\s*(\d+)\s*天', text)
        if match:
            return int(match.group(1))
        
        return None
