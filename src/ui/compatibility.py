"""
UI 兼容性层

提供功能降级和向后兼容性支持。
"""

from typing import Optional
from .models import UIConfig, IconStyle
from .terminal_detector import TerminalDetector, TerminalCapabilities


class UICompatibilityLayer:
    """UI 兼容性层"""
    
    def __init__(self, config: Optional[UIConfig] = None):
        """
        初始化兼容性层
        
        Args:
            config: UI 配置对象
        """
        self.original_config = config or UIConfig()
        self.terminal_caps = TerminalDetector.detect()
        self.adjusted_config = self._adjust_config()
    
    def _adjust_config(self) -> UIConfig:
        """
        根据终端能力调整配置
        
        Returns:
            UIConfig: 调整后的配置
        """
        config = UIConfig(
            enable_colors=self.original_config.enable_colors,
            enable_icons=self.original_config.enable_icons,
            enable_progress=self.original_config.enable_progress,
            enable_animations=self.original_config.enable_animations,
            theme=self.original_config.theme,
            icon_style=self.original_config.icon_style,
            max_table_width=self.original_config.max_table_width,
            page_size=self.original_config.page_size,
            auto_pager=self.original_config.auto_pager,
        )
        
        # 如果终端不支持颜色，禁用颜色
        if not self.terminal_caps.supports_color:
            config.enable_colors = False
            config.theme = "minimal"
        
        # 如果不是交互式终端，禁用颜色和动画
        if not self.terminal_caps.is_interactive:
            config.enable_colors = False
            config.enable_animations = False
            config.enable_progress = False
        
        # 如果终端不支持 ANSI，禁用动画和进度
        if not self.terminal_caps.supports_ansi:
            config.enable_animations = False
            config.enable_progress = False
        
        # 根据终端能力调整图标样式
        if config.enable_icons:
            recommended_style = TerminalDetector.get_recommended_icon_style(self.terminal_caps)
            
            # 如果配置的样式不被支持，使用推荐样式
            if config.icon_style == IconStyle.EMOJI and not self.terminal_caps.supports_emoji:
                config.icon_style = IconStyle(recommended_style)
            elif config.icon_style == IconStyle.UNICODE and not self.terminal_caps.supports_unicode:
                config.icon_style = IconStyle.ASCII
        
        # 调整表格宽度
        safe_width = TerminalDetector.get_safe_width(
            self.terminal_caps,
            config.max_table_width
        )
        config.max_table_width = safe_width
        
        return config
    
    def get_config(self) -> UIConfig:
        """
        获取调整后的配置
        
        Returns:
            UIConfig: 调整后的配置
        """
        return self.adjusted_config
    
    def get_capabilities(self) -> TerminalCapabilities:
        """
        获取终端能力
        
        Returns:
            TerminalCapabilities: 终端能力对象
        """
        return self.terminal_caps
    
    def is_feature_available(self, feature: str) -> bool:
        """
        检查功能是否可用
        
        Args:
            feature: 功能名称 (colors, icons, progress, animations)
            
        Returns:
            bool: 功能是否可用
        """
        feature_map = {
            'colors': self.adjusted_config.enable_colors,
            'icons': self.adjusted_config.enable_icons,
            'progress': self.adjusted_config.enable_progress,
            'animations': self.adjusted_config.enable_animations,
        }
        
        return feature_map.get(feature, False)
    
    def get_degradation_report(self) -> dict:
        """
        获取功能降级报告
        
        Returns:
            dict: 降级报告
        """
        report = {
            'terminal_type': self.terminal_caps.terminal_type,
            'is_interactive': self.terminal_caps.is_interactive,
            'terminal_size': f"{self.terminal_caps.terminal_width}x{self.terminal_caps.terminal_height}",
            'degraded_features': [],
            'adjusted_settings': {},
        }
        
        # 检查哪些功能被降级
        if self.original_config.enable_colors and not self.adjusted_config.enable_colors:
            report['degraded_features'].append('colors')
            report['adjusted_settings']['colors'] = '禁用（终端不支持）'
        
        if self.original_config.enable_animations and not self.adjusted_config.enable_animations:
            report['degraded_features'].append('animations')
            report['adjusted_settings']['animations'] = '禁用（终端不支持）'
        
        if self.original_config.enable_progress and not self.adjusted_config.enable_progress:
            report['degraded_features'].append('progress')
            report['adjusted_settings']['progress'] = '禁用（终端不支持）'
        
        if self.original_config.icon_style != self.adjusted_config.icon_style:
            report['degraded_features'].append('icon_style')
            report['adjusted_settings']['icon_style'] = f'{self.original_config.icon_style.value} → {self.adjusted_config.icon_style.value}'
        
        if self.original_config.max_table_width != self.adjusted_config.max_table_width:
            report['adjusted_settings']['max_table_width'] = f'{self.original_config.max_table_width} → {self.adjusted_config.max_table_width}'
        
        return report
    
    def print_compatibility_info(self):
        """打印兼容性信息"""
        report = self.get_degradation_report()
        
        print("\n" + "=" * 60)
        print("🔧 终端兼容性信息")
        print("=" * 60)
        
        print(f"\n终端类型: {report['terminal_type']}")
        print(f"交互模式: {'是' if report['is_interactive'] else '否'}")
        print(f"终端尺寸: {report['terminal_size']}")
        
        print(f"\n终端能力:")
        print(f"  颜色支持: {'是' if self.terminal_caps.supports_color else '否'}")
        print(f"  Unicode 支持: {'是' if self.terminal_caps.supports_unicode else '否'}")
        print(f"  Emoji 支持: {'是' if self.terminal_caps.supports_emoji else '否'}")
        print(f"  ANSI 支持: {'是' if self.terminal_caps.supports_ansi else '否'}")
        print(f"  颜色深度: {self.terminal_caps.color_depth}")
        
        if report['degraded_features']:
            print(f"\n⚠️  降级的功能:")
            for feature in report['degraded_features']:
                print(f"  - {feature}")
        
        if report['adjusted_settings']:
            print(f"\n调整的设置:")
            for key, value in report['adjusted_settings'].items():
                print(f"  {key}: {value}")
        
        if not report['degraded_features']:
            print("\n✅ 所有功能均可正常使用")
        
        print("=" * 60 + "\n")


def create_compatible_ui_config(config: Optional[UIConfig] = None) -> UIConfig:
    """
    创建兼容的 UI 配置
    
    Args:
        config: 原始配置
        
    Returns:
        UIConfig: 兼容的配置
    """
    compat_layer = UICompatibilityLayer(config)
    return compat_layer.get_config()


def check_terminal_compatibility() -> TerminalCapabilities:
    """
    检查终端兼容性
    
    Returns:
        TerminalCapabilities: 终端能力对象
    """
    return TerminalDetector.detect()
