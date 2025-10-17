"""
UI 配置管理器

管理 UI 配置的加载、保存和更新。
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any

from .models import UIConfig, ThemeColors, IconStyle
from .config_loader import UIConfigLoader


class UIConfigManager:
    """UI 配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path or UIConfigLoader.DEFAULT_CONFIG_PATH)
        self.config = UIConfigLoader.load_config(str(self.config_path))
        self.themes = UIConfigLoader.load_themes(str(self.config_path))
    
    def get_config(self) -> UIConfig:
        """
        获取当前配置
        
        Returns:
            UIConfig: UI 配置对象
        """
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """
        更新配置
        
        Args:
            updates: 要更新的配置项
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 更新配置对象
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # 保存到文件
            return self.save_config()
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
            else:
                data = {}
            
            # 更新 UI 配置部分
            ui_data = data.get('ui', {})
            
            # 更新颜色设置
            colors = ui_data.get('colors', {})
            colors['enabled'] = self.config.enable_colors
            colors['theme'] = self.config.theme
            ui_data['colors'] = colors
            
            # 更新图标设置
            icons = ui_data.get('icons', {})
            icons['enabled'] = self.config.enable_icons
            icons['style'] = self.config.icon_style.value
            ui_data['icons'] = icons
            
            # 更新进度设置
            progress = ui_data.get('progress', {})
            progress['enabled'] = self.config.enable_progress
            progress['animations'] = self.config.enable_animations
            ui_data['progress'] = progress
            
            # 更新显示设置
            display = ui_data.get('display', {})
            display['max_width'] = self.config.max_table_width
            display['page_size'] = self.config.page_size
            display['auto_pager'] = self.config.auto_pager
            ui_data['display'] = display
            
            data['ui'] = ui_data
            
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def switch_theme(self, theme_name: str) -> bool:
        """
        切换主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            bool: 是否切换成功
        """
        if theme_name not in self.themes and theme_name not in ['default', 'dark', 'light', 'minimal']:
            print(f"未知的主题: {theme_name}")
            return False
        
        return self.update_config({'theme': theme_name})
    
    def set_icon_style(self, style: str) -> bool:
        """
        设置图标样式
        
        Args:
            style: 图标样式 (emoji, ascii, unicode, none)
            
        Returns:
            bool: 是否设置成功
        """
        try:
            icon_style = IconStyle(style)
            return self.update_config({'icon_style': icon_style})
        except ValueError:
            print(f"无效的图标样式: {style}")
            return False
    
    def toggle_feature(self, feature: str, enabled: Optional[bool] = None) -> bool:
        """
        切换功能开关
        
        Args:
            feature: 功能名称 (colors, icons, progress, animations)
            enabled: 是否启用，None 表示切换当前状态
            
        Returns:
            bool: 是否切换成功
        """
        feature_map = {
            'colors': 'enable_colors',
            'icons': 'enable_icons',
            'progress': 'enable_progress',
            'animations': 'enable_animations',
        }
        
        if feature not in feature_map:
            print(f"未知的功能: {feature}")
            return False
        
        config_key = feature_map[feature]
        current_value = getattr(self.config, config_key)
        new_value = not current_value if enabled is None else enabled
        
        return self.update_config({config_key: new_value})
    
    def get_available_themes(self) -> list:
        """
        获取可用的主题列表
        
        Returns:
            list: 主题名称列表
        """
        return list(self.themes.keys())
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Optional[ThemeColors]:
        """
        获取主题颜色配置
        
        Args:
            theme_name: 主题名称，None 表示当前主题
            
        Returns:
            ThemeColors: 主题颜色对象
        """
        name = theme_name or self.config.theme
        return self.themes.get(name)
    
    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            bool: 是否重置成功
        """
        self.config = UIConfig()
        return self.save_config()
    
    def export_config(self, output_path: str) -> bool:
        """
        导出配置到文件
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取当前配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 写入到输出文件
            with open(output, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, input_path: str) -> bool:
        """
        从文件导入配置
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            bool: 是否导入成功
        """
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                print(f"配置文件不存在: {input_path}")
                return False
            
            # 读取输入配置
            with open(input_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 写入到当前配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            # 重新加载配置
            self.config = UIConfigLoader.load_config(str(self.config_path))
            self.themes = UIConfigLoader.load_themes(str(self.config_path))
            
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
