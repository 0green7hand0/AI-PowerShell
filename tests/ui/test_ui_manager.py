"""
UI 管理器测试
"""

import pytest
import sys
from pathlib import Path
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui import UIManager, ThemeManager
from src.ui.models import UIConfig, IconStyle, ThemeName


class TestUIManager:
    """测试 UI 管理器"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(
            enable_colors=True,
            enable_icons=True,
            icon_style=IconStyle.EMOJI
        )
        return UIManager(config)
    
    def test_ui_manager_initialization(self, ui_manager):
        """测试 UI 管理器初始化"""
        assert ui_manager is not None
        assert ui_manager.config is not None
        assert ui_manager.theme_manager is not None
        assert ui_manager.console is not None
    
    def test_get_icon_emoji(self, ui_manager):
        """测试获取 emoji 图标"""
        icon = ui_manager.get_icon("success")
        assert icon == "✅ "
        
        icon = ui_manager.get_icon("error")
        assert icon == "❌ "
        
        icon = ui_manager.get_icon("warning")
        assert icon == "⚠️ "
        
        icon = ui_manager.get_icon("info")
        assert icon == "ℹ️ "
    
    def test_get_icon_disabled(self):
        """测试禁用图标"""
        config = UIConfig(enable_icons=False)
        ui = UIManager(config)
        
        icon = ui.get_icon("success")
        assert icon == ""
    
    def test_get_icon_ascii(self):
        """测试 ASCII 图标"""
        config = UIConfig(
            enable_icons=True,
            icon_style=IconStyle.ASCII
        )
        ui = UIManager(config)
        
        icon = ui.get_icon("success")
        assert icon == "[OK] "
        
        icon = ui.get_icon("error")
        assert icon == "[X] "
    
    def test_get_icon_unicode(self):
        """测试 Unicode 图标"""
        config = UIConfig(
            enable_icons=True,
            icon_style=IconStyle.UNICODE
        )
        ui = UIManager(config)
        
        icon = ui.get_icon("success")
        assert icon == "✓ "
        
        icon = ui.get_icon("error")
        assert icon == "✗ "
    
    def test_get_icon_unknown(self, ui_manager):
        """测试获取未知图标"""
        icon = ui_manager.get_icon("unknown_icon")
        assert icon == ""
    
    def test_create_table(self, ui_manager):
        """测试创建表格"""
        table = ui_manager.create_table(title="测试表格")
        assert table is not None
        assert table.title == "测试表格"
    
    def test_create_table_with_options(self, ui_manager):
        """测试创建带选项的表格"""
        table = ui_manager.create_table(
            title="测试表格",
            show_header=True,
            show_lines=True,
            box_style="minimal"
        )
        assert table is not None
        assert table.show_header is True
        assert table.show_lines is True
    
    def test_create_panel(self, ui_manager):
        """测试创建面板"""
        panel = ui_manager.create_panel("测试内容", title="测试面板")
        assert panel is not None
    
    def test_print_methods_no_error(self, ui_manager, capsys):
        """测试打印方法不抛出错误"""
        ui_manager.print_success("成功")
        ui_manager.print_error("错误")
        ui_manager.print_warning("警告")
        ui_manager.print_info("信息")
        
        # 验证有输出
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_print_with_icons(self, ui_manager, capsys):
        """测试带图标的打印"""
        ui_manager.print_success("成功", icon=True)
        captured = capsys.readouterr()
        assert "✅" in captured.out
        
        ui_manager.print_error("错误", icon=True)
        captured = capsys.readouterr()
        assert "❌" in captured.out
    
    def test_print_without_icons(self, ui_manager, capsys):
        """测试不带图标的打印"""
        ui_manager.print_success("成功", icon=False)
        captured = capsys.readouterr()
        assert "✅" not in captured.out
        assert "成功" in captured.out


class TestThemeManager:
    """测试主题管理器"""
    
    @pytest.fixture
    def theme_manager(self):
        """创建主题管理器实例"""
        return ThemeManager()
    
    def test_theme_manager_initialization(self, theme_manager):
        """测试主题管理器初始化"""
        assert theme_manager is not None
        assert theme_manager.theme_name == ThemeName.DEFAULT
        assert theme_manager.colors is not None
        assert theme_manager.rich_theme is not None
    
    def test_load_default_theme(self):
        """测试加载默认主题"""
        tm = ThemeManager(ThemeName.DEFAULT)
        assert tm.theme_name == ThemeName.DEFAULT
        assert tm.colors.success == "bold green"
        assert tm.colors.error == "bold red"
    
    def test_load_dark_theme(self):
        """测试加载暗色主题"""
        tm = ThemeManager(ThemeName.DARK)
        assert tm.theme_name == ThemeName.DARK
        assert tm.colors.success == "bold bright_green"
    
    def test_load_light_theme(self):
        """测试加载亮色主题"""
        tm = ThemeManager(ThemeName.LIGHT)
        assert tm.theme_name == ThemeName.LIGHT
        assert tm.colors.success == "bold green"
    
    def test_load_minimal_theme(self):
        """测试加载最小主题"""
        tm = ThemeManager(ThemeName.MINIMAL)
        assert tm.theme_name == ThemeName.MINIMAL
        assert tm.colors.success == "white"
        assert tm.colors.error == "white"
    
    def test_switch_theme(self, theme_manager):
        """测试切换主题"""
        # 初始为默认主题
        assert theme_manager.theme_name == ThemeName.DEFAULT
        
        # 切换到暗色主题
        theme_manager.switch_theme(ThemeName.DARK)
        assert theme_manager.theme_name == ThemeName.DARK
        assert theme_manager.colors.success == "bold bright_green"
        
        # 切换到亮色主题
        theme_manager.switch_theme(ThemeName.LIGHT)
        assert theme_manager.theme_name == ThemeName.LIGHT
        assert theme_manager.colors.success == "bold green"
    
    def test_switch_to_invalid_theme(self, theme_manager):
        """测试切换到无效主题"""
        original_theme = theme_manager.theme_name
        theme_manager.switch_theme("invalid_theme")
        # 主题不应该改变
        assert theme_manager.theme_name == original_theme
    
    def test_get_color(self, theme_manager):
        """测试获取颜色"""
        color = theme_manager.get_color("success")
        assert color == "bold green"
        
        color = theme_manager.get_color("error")
        assert color == "bold red"
    
    def test_get_style(self, theme_manager):
        """测试获取样式"""
        style = theme_manager.get_style("success")
        assert style is not None
    
    def test_list_available_themes(self, theme_manager):
        """测试列出可用主题"""
        themes = theme_manager.list_available_themes()
        assert len(themes) >= 4
        assert ThemeName.DEFAULT in themes
        assert ThemeName.DARK in themes
        assert ThemeName.LIGHT in themes
        assert ThemeName.MINIMAL in themes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
