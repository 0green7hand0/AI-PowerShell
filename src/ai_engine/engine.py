"""
AI 引擎主类

负责协调 AI 翻译流程，包括缓存管理、翻译器调用和错误检测。
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from ..interfaces.base import AIEngineInterface, Suggestion, Context


class TranslationCache:
    """翻译缓存类
    
    使用内存缓存来存储最近的翻译结果，提高响应速度。
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        """初始化缓存
        
        Args:
            max_size: 缓存最大条目数
            ttl_seconds: 缓存过期时间（秒）
        """
        self._cache: Dict[str, tuple[Suggestion, datetime]] = {}
        self._max_size = max_size
        self._ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, text: str) -> Optional[Suggestion]:
        """从缓存获取翻译结果
        
        Args:
            text: 用户输入文本
            
        Returns:
            Optional[Suggestion]: 缓存的建议，如果不存在或已过期则返回 None
        """
        if text not in self._cache:
            return None
        
        suggestion, timestamp = self._cache[text]
        
        # 检查是否过期
        if datetime.now() - timestamp > self._ttl:
            del self._cache[text]
            return None
        
        return suggestion
    
    def set(self, text: str, suggestion: Suggestion):
        """将翻译结果存入缓存
        
        Args:
            text: 用户输入文本
            suggestion: 翻译建议
        """
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[text] = (suggestion, datetime.now())
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class AIEngine(AIEngineInterface):
    """AI 引擎主类
    
    协调各个子模块完成自然语言到 PowerShell 命令的翻译。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化 AI 引擎
        
        Args:
            config: 配置字典，包含 AI 引擎相关配置
        """
        self.config = config or {}
        self.cache = TranslationCache(
            max_size=self.config.get('cache_max_size', 100),
            ttl_seconds=self.config.get('cache_ttl', 3600)
        )
        
        # 延迟导入以避免循环依赖
        self._translator = None
        self._error_detector = None
        self._provider = None
    
    @property
    def translator(self):
        """懒加载翻译器"""
        if self._translator is None:
            from .translation import NaturalLanguageTranslator
            self._translator = NaturalLanguageTranslator(self.config)
        return self._translator
    
    @property
    def error_detector(self):
        """懒加载错误检测器"""
        if self._error_detector is None:
            from .error_detection import ErrorDetector
            self._error_detector = ErrorDetector()
        return self._error_detector
    
    def translate_natural_language(
        self, 
        text: str, 
        context: Context,
        progress_callback=None
    ) -> Suggestion:
        """将自然语言翻译为 PowerShell 命令
        
        Args:
            text: 用户输入的自然语言文本
            context: 当前上下文信息
            progress_callback: 进度回调函数，接收 (step, total, description) 参数
            
        Returns:
            Suggestion: 包含生成命令和相关信息的建议对象
            
        Raises:
            ValueError: 当输入文本为空或无效时
            RuntimeError: 当 AI 引擎不可用时
        """
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")
        
        text = text.strip()
        
        # 1. 检查缓存
        if progress_callback:
            progress_callback(1, 4, "检查缓存...")
        
        cached = self.cache.get(text)
        if cached:
            if progress_callback:
                progress_callback(4, 4, "从缓存获取结果")
            return cached
        
        # 2. 使用翻译器进行翻译
        if progress_callback:
            progress_callback(2, 4, "AI 模型处理中...")
        
        suggestion = self.translator.translate(text, context)
        
        # 3. 错误检测和修正
        if progress_callback:
            progress_callback(3, 4, "错误检测和修正...")
        
        if self.error_detector.has_errors(suggestion.generated_command):
            suggestion = self.error_detector.fix(suggestion)
        
        # 4. 缓存结果
        if progress_callback:
            progress_callback(4, 4, "完成")
        
        self.cache.set(text, suggestion)
        
        return suggestion
    
    def validate_command(self, command: str) -> bool:
        """验证生成的命令是否有效
        
        Args:
            command: 待验证的 PowerShell 命令
            
        Returns:
            bool: 命令是否有效
        """
        if not command or not command.strip():
            return False
        
        # 基本语法检查
        command = command.strip()
        
        # 检查是否包含基本的 PowerShell 命令结构
        if not any(char.isalnum() for char in command):
            return False
        
        # 使用错误检测器进行更详细的验证
        return not self.error_detector.has_errors(command)
    
    def get_command_explanation(self, command: str) -> str:
        """获取命令的详细解释
        
        Args:
            command: PowerShell 命令
            
        Returns:
            str: 命令的详细解释
        """
        if not command or not command.strip():
            return "无效的命令"
        
        # 使用翻译器生成解释
        return self.translator.explain_command(command)
    
    def clear_cache(self):
        """清空翻译缓存"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息
        
        Returns:
            Dict[str, int]: 包含缓存大小等统计信息
        """
        return {
            'size': self.cache.size(),
            'max_size': self.cache._max_size
        }
