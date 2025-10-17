"""
UI 系统集成测试

测试 UI 系统各组件的集成和交互。
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ui import (
    UIManager, UIConfig, UIConfigManager, UICompatibilityLayer,
    ProgressManager, InteractiveInputManager, HelpSystem,
    TerminalDetector, create_compatible_ui_config
)
from src.ui.models import IconStyle


class TestUISystemIntegration:
    """UI 系统集成测试"""
    
    def test_ui_manager_initialization(self):
        """测试 UI 管理器初始化"""
        config = UIConfig()
        ui_manager = UIManager(config)
        
        assert ui_manager is not None
        assert ui_manager.config == config
        assert ui_manager.console is not None
        assert ui_manager.theme_manager is not None
    
    def test_ui_config_manager_lifecycle(self):
        """测试 UI 配置管理器生命周期"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            # 创建配置管理器
            config_manager = UIConfigManager(str(config_path))
            
            # 获取配置
            config = config_manager.get_config()
            assert config is not None
            
            # 更新配置
            success = config_manager.update_config({
                'enable_colors': False,
                'theme': 'minimal'
            })
            assert success
            
            # 验证更新
            updated_config = config_manager.get_config()
            assert updated_config.enable_colors == False
            assert updated_config.theme == 'minimal'
    
    def test_compatibility_layer_integration(self):
        """测试兼容性层集成"""
        # 创建原始配置
        original_config = UIConfig(
            enable_colors=True,
            enable_icons=True,
            icon_style=IconStyle.EMOJI
        )
        
        # 应用兼容性层
        compat_layer = UICompatibilityLayer(original_config)
        adjusted_config = compat_layer.get_config()
        
        assert adjusted_config is not None
        
        # 获取终端能力
        caps = compat_layer.get_capabilities()
        assert caps is not None
        
        # 获取降级报告
        report = compat_layer.get_degradation_report()
        assert 'terminal_type' in report
        assert 'degraded_features' in report
    
    def test_terminal_detection(self):
        """测试终端检测"""
        caps = TerminalDetector.detect()
        
        assert caps is not None
        assert caps.terminal_width > 0
        assert caps.terminal_height > 0
        assert caps.terminal_type is not None
        assert caps.color_depth in [8, 16, 256, 16777216]
    
    def test_ui_components_integration(self):
        """测试 UI 组件集成"""
        config = UIConfig()
        ui_manager = UIManager(config)
        
        # 测试进度管理器
        progress_manager = ProgressManager(ui_manager.console, config)
        assert progress_manager is not None
        
        # 测试交互式输入管理器
        input_manager = InteractiveInputManager(config)
        assert input_manager is not None
        
        # 测试帮助系统
        help_system = HelpSystem(ui_manager)
        assert help_system is not None
    
    def test_theme_switching(self):
        """测试主题切换"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            config_manager = UIConfigManager(str(config_path))
            
            # 切换到不同主题
            themes = ['default', 'dark', 'light', 'minimal']
            for theme in themes:
                success = config_manager.switch_theme(theme)
                assert success
                
                config = config_manager.get_config()
                assert config.theme == theme
    
    def test_icon_style_switching(self):
        """测试图标样式切换"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            config_manager = UIConfigManager(str(config_path))
            
            # 切换到不同图标样式
            styles = ['emoji', 'ascii', 'unicode', 'none']
            for style in styles:
                success = config_manager.set_icon_style(style)
                assert success
                
                config = config_manager.get_config()
                assert config.icon_style.value == style
    
    def test_feature_toggling(self):
        """测试功能开关"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            config_manager = UIConfigManager(str(config_path))
            
            # 测试各种功能开关
            features = ['colors', 'icons', 'progress', 'animations']
            for feature in features:
                # 禁用
                success = config_manager.toggle_feature(feature, False)
                assert success
                
                # 启用
                success = config_manager.toggle_feature(feature, True)
                assert success
    
    def test_ui_output_methods(self):
        """测试 UI 输出方法"""
        config = UIConfig()
        ui_manager = UIManager(config)
        
        # 测试各种输出方法（不会实际输出到终端）
        with patch('rich.console.Console.print'):
            ui_manager.print_success("Success message")
            ui_manager.print_error("Error message")
            ui_manager.print_warning("Warning message")
            ui_manager.print_info("Info message")
            ui_manager.print_header("Header", "Subtitle")
            ui_manager.print_dict({"key": "value"})
            ui_manager.print_list(["item1", "item2"])
    
    def test_compatible_config_creation(self):
        """测试兼容配置创建"""
        # 使用默认配置
        config = create_compatible_ui_config()
        assert config is not None
        
        # 使用自定义配置
        custom_config = UIConfig(enable_colors=True, theme='dark')
        config = create_compatible_ui_config(custom_config)
        assert config is not None


class TestUIConfigPersistence:
    """UI 配置持久化测试"""
    
    def test_config_save_and_load(self):
        """测试配置保存和加载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            # 创建并保存配置
            config_manager = UIConfigManager(str(config_path))
            config_manager.update_config({
                'enable_colors': False,
                'theme': 'minimal',
                'max_table_width': 100
            })
            
            # 重新加载配置
            new_config_manager = UIConfigManager(str(config_path))
            config = new_config_manager.get_config()
            
            assert config.enable_colors == False
            assert config.theme == 'minimal'
            assert config.max_table_width == 100
    
    def test_config_export_import(self):
        """测试配置导出和导入"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            export_path = Path(tmpdir) / "exported.yaml"
            
            # 创建配置
            config_manager = UIConfigManager(str(config_path))
            config_manager.update_config({'theme': 'dark'})
            
            # 导出配置
            success = config_manager.export_config(str(export_path))
            assert success
            assert export_path.exists()
            
            # 修改配置
            config_manager.update_config({'theme': 'light'})
            
            # 导入配置
            success = config_manager.import_config(str(export_path))
            assert success
            
            # 验证配置已恢复
            config = config_manager.get_config()
            assert config.theme == 'dark'
    
    def test_config_reset(self):
        """测试配置重置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            
            config_manager = UIConfigManager(str(config_path))
            
            # 修改配置
            config_manager.update_config({
                'enable_colors': False,
                'theme': 'minimal'
            })
            
            # 重置配置
            success = config_manager.reset_to_defaults()
            assert success
            
            # 验证配置已重置
            config = config_manager.get_config()
            assert config.enable_colors == True  # 默认值
            assert config.theme == 'default'  # 默认值


class TestCrossPlatformCompatibility:
    """跨平台兼容性测试"""
    
    @pytest.mark.skipif(os.name != 'nt', reason="Windows specific test")
    def test_windows_compatibility(self):
        """测试 Windows 兼容性"""
        caps = TerminalDetector.detect()
        assert caps is not None
        
        # Windows 特定检查
        config = create_compatible_ui_config()
        assert config is not None
    
    @pytest.mark.skipif(os.name == 'nt', reason="Unix specific test")
    def test_unix_compatibility(self):
        """测试 Unix 兼容性"""
        caps = TerminalDetector.detect()
        assert caps is not None
        
        # Unix 特定检查
        config = create_compatible_ui_config()
        assert config is not None
    
    def test_non_interactive_terminal(self):
        """测试非交互式终端"""
        with patch('sys.stdin.isatty', return_value=False):
            with patch('sys.stdout.isatty', return_value=False):
                caps = TerminalDetector.detect()
                assert caps.is_interactive == False
                
                # 非交互式终端应该禁用某些功能
                config = UIConfig(enable_animations=True, enable_progress=True)
                compat_layer = UICompatibilityLayer(config)
                adjusted_config = compat_layer.get_config()
                
                assert adjusted_config.enable_animations == False
                assert adjusted_config.enable_progress == False
    
    def test_no_color_environment(self):
        """测试 NO_COLOR 环境变量"""
        with patch.dict(os.environ, {'NO_COLOR': '1'}):
            caps = TerminalDetector.detect()
            assert caps.supports_color == False
            
            config = UIConfig(enable_colors=True)
            compat_layer = UICompatibilityLayer(config)
            adjusted_config = compat_layer.get_config()
            
            assert adjusted_config.enable_colors == False


class TestUIPerformance:
    """UI 性能测试"""
    
    def test_ui_initialization_performance(self):
        """测试 UI 初始化性能"""
        import time
        
        start_time = time.time()
        
        config = UIConfig()
        ui_manager = UIManager(config)
        progress_manager = ProgressManager(ui_manager.console, config)
        input_manager = InteractiveInputManager(config)
        help_system = HelpSystem(ui_manager)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # 初始化应该在 1 秒内完成
        assert elapsed < 1.0
    
    def test_config_operations_performance(self):
        """测试配置操作性能"""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "ui.yaml"
            config_manager = UIConfigManager(str(config_path))
            
            start_time = time.time()
            
            # 执行多次配置更新
            for i in range(10):
                config_manager.update_config({'max_table_width': 100 + i})
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # 10 次更新应该在 1 秒内完成
            assert elapsed < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
