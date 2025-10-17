"""
UI 配置加载器

从配置文件加载 UI 设置。
"""

import yaml
from pathlib import Path
from typing import Dict, Optional

from .models import UIConfig, ThemeColors, IconStyle


class UIConfigLoader:
    """UI 配置加载器"""
    
    DEFAULT_CONFIG_PATH = "config/ui.yaml"
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> UIConfig:
        """
        加载 UI 配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            UIConfig: UI 配置对象
        """
        path = Path(config_path or cls.DEFAULT_CONFIG_PATH)
        
        if not path.exists():
            return UIConfig()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            ui_data = data.get('ui', {})
            
            # 构建配置对象
            config = UIConfig(
                enable_colors=ui_data.get('colors', {}).get('enabled', True),
                enable_icons=ui_data.get('icons', {}).get('enabled', True),
                enable_progress=ui_data.get('progress', {}).get('enabled', True),
                enable_animations=ui_data.get('progress', {}).get('animations', True),
                theme=ui_data.get('colors', {}).get('theme', 'default'),
                icon_style=IconStyle(ui_data.get('icons', {}).get('style', 'emoji')),
                max_table_width=ui_data.get('display', {}).get('max_width', 120),
                page_size=ui_data.get('display', {}).get('page_size', 20),
                auto_pager=ui_data.get('display', {}).get('auto_pager', True),
            )
            
            return config
            
        except Exception as e:
            print(f"警告: 加载 UI 配置失败: {e}")
            return UIConfig()
    
    @classmethod
    def load_themes(cls, config_path: Optional[str] = None) -> Dict[str, ThemeColors]:
        """
        加载主题配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict[str, ThemeColors]: 主题字典
        """
        path = Path(config_path or cls.DEFAULT_CONFIG_PATH)
        
        if not path.exists():
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            themes_data = data.get('themes', {})
            themes = {}
            
            for theme_name, theme_colors in themes_data.items():
                themes[theme_name] = ThemeColors.from_dict(theme_colors)
            
            return themes
            
        except Exception as e:
            print(f"警告: 加载主题配置失败: {e}")
            return {}
