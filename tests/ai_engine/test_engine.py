"""
AI 引擎主类测试
"""

import pytest
from datetime import datetime
from src.ai_engine.engine import AIEngine, TranslationCache
from src.interfaces.base import Suggestion, Context


class TestTranslationCache:
    """翻译缓存测试"""
    
    def test_cache_initialization(self):
        """测试缓存初始化"""
        cache = TranslationCache(max_size=10, ttl_seconds=60)
        assert cache.size() == 0
        assert cache._max_size == 10
    
    def test_cache_set_and_get(self):
        """测试缓存存取"""
        cache = TranslationCache()
        
        suggestion = Suggestion(
            original_input="显示文件",
            generated_command="Get-ChildItem",
            confidence_score=0.95,
            explanation="列出文件"
        )
        
        cache.set("显示文件", suggestion)
        
        result = cache.get("显示文件")
        assert result is not None
        assert result.generated_command == "Get-ChildItem"
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = TranslationCache()
        result = cache.get("不存在的键")
        assert result is None
    
    def test_cache_max_size(self):
        """测试缓存大小限制"""
        cache = TranslationCache(max_size=2)
        
        for i in range(3):
            suggestion = Suggestion(
                original_input=f"输入{i}",
                generated_command=f"命令{i}",
                confidence_score=0.9,
                explanation=f"解释{i}"
            )
            cache.set(f"输入{i}", suggestion)
        
        # 缓存大小应该不超过 max_size
        assert cache.size() <= 2
    
    def test_cache_clear(self):
        """测试清空缓存"""
        cache = TranslationCache()
        
        suggestion = Suggestion(
            original_input="测试",
            generated_command="Test",
            confidence_score=0.9,
            explanation="测试"
        )
        cache.set("测试", suggestion)
        
        assert cache.size() == 1
        cache.clear()
        assert cache.size() == 0


class TestAIEngine:
    """AI 引擎测试"""
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = AIEngine()
        assert engine is not None
        assert engine.cache is not None
    
    def test_engine_with_config(self):
        """测试带配置的引擎初始化"""
        config = {
            'cache_max_size': 50,
            'cache_ttl': 1800
        }
        engine = AIEngine(config)
        assert engine.cache._max_size == 50
    
    def test_translate_empty_input(self):
        """测试空输入"""
        engine = AIEngine()
        context = Context(session_id="test-session")
        
        with pytest.raises(ValueError, match="输入文本不能为空"):
            engine.translate_natural_language("", context)
    
    def test_translate_with_cache(self):
        """测试缓存命中"""
        engine = AIEngine()
        context = Context(session_id="test-session")
        
        # 第一次翻译
        result1 = engine.translate_natural_language("显示文件", context)
        
        # 第二次应该从缓存获取
        result2 = engine.translate_natural_language("显示文件", context)
        
        assert result1.generated_command == result2.generated_command
    
    def test_validate_command_valid(self):
        """测试有效命令验证"""
        engine = AIEngine()
        
        assert engine.validate_command("Get-ChildItem") is True
        assert engine.validate_command("Get-Process") is True
    
    def test_validate_command_invalid(self):
        """测试无效命令验证"""
        engine = AIEngine()
        
        assert engine.validate_command("") is False
        assert engine.validate_command("   ") is False
    
    def test_get_command_explanation(self):
        """测试获取命令解释"""
        engine = AIEngine()
        
        explanation = engine.get_command_explanation("Get-ChildItem")
        assert explanation is not None
        assert len(explanation) > 0
    
    def test_clear_cache(self):
        """测试清空缓存"""
        engine = AIEngine()
        context = Context(session_id="test-session")
        
        # 添加一些缓存
        engine.translate_natural_language("显示文件", context)
        assert engine.cache.size() > 0
        
        # 清空缓存
        engine.clear_cache()
        assert engine.cache.size() == 0
    
    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        engine = AIEngine()
        
        stats = engine.get_cache_stats()
        assert 'size' in stats
        assert 'max_size' in stats
        assert stats['size'] >= 0
