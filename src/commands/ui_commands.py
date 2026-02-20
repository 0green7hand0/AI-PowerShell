"""UI 命令处理模块

此模块包含所有与 UI 相关的命令处理函数，包括显示 UI 配置、设置 UI 配置、重置 UI 配置和检查终端兼容性等操作。
"""


def ui_config_show_command(assistant):
    """处理 ui config show 命令 - 显示当前 UI 配置"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        from src.ui import UIManager
        
        ui = UIManager(assistant.ui_config)
        
        ui.print_header("⚙️ UI 配置", "当前配置信息")
        
        config_data = {
            "彩色输出": "启用" if assistant.ui_config.enable_colors else "禁用",
            "图标显示": "启用" if assistant.ui_config.enable_icons else "禁用",
            "进度指示": "启用" if assistant.ui_config.enable_progress else "禁用",
            "动画效果": "启用" if assistant.ui_config.enable_animations else "禁用",
            "当前主题": assistant.ui_config.theme,
            "图标样式": assistant.ui_config.icon_style.value,
            "表格最大宽度": str(assistant.ui_config.max_table_width),
            "分页大小": str(assistant.ui_config.page_size),
            "自动分页": "启用" if assistant.ui_config.auto_pager else "禁用",
        }
        
        ui.print_dict(config_data)
        ui.print_newline()
        
        # 显示可用主题
        themes = assistant.ui_config_manager.get_available_themes()
        if themes:
            ui.print_info("可用主题:", icon=True)
            ui.print_list(themes)
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_config_set_command(assistant, key, value):
    """处理 ui config set 命令 - 设置 UI 配置项"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        # 解析值
        bool_values = {'true': True, 'false': False, 'yes': True, 'no': False, '1': True, '0': False}
        
        updates = {}
        
        # 处理不同的配置项
        if key == 'theme':
            success = assistant.ui_config_manager.switch_theme(value)
            if success:
                print(f"✅ 主题已切换为: {value}")
                return 0
            else:
                print(f"❌ 切换主题失败")
                return 1
        elif key == 'icon_style':
            success = assistant.ui_config_manager.set_icon_style(value)
            if success:
                print(f"✅ 图标样式已设置为: {value}")
                return 0
            else:
                print(f"❌ 设置图标样式失败")
                return 1
        elif key in ['colors', 'icons', 'progress', 'animations']:
            if value.lower() not in bool_values:
                print(f"❌ 无效的值: {value}，请使用 true/false")
                return 1
            enabled = bool_values[value.lower()]
            success = assistant.ui_config_manager.toggle_feature(key, enabled)
            if success:
                status = "启用" if enabled else "禁用"
                print(f"✅ {key} 已{status}")
                return 0
            else:
                print(f"❌ 设置失败")
                return 1
        elif key == 'max_table_width':
            try:
                width = int(value)
                updates['max_table_width'] = width
            except ValueError:
                print(f"❌ 无效的宽度值: {value}")
                return 1
        elif key == 'page_size':
            try:
                size = int(value)
                updates['page_size'] = size
            except ValueError:
                print(f"❌ 无效的大小值: {value}")
                return 1
        elif key == 'auto_pager':
            if value.lower() not in bool_values:
                print(f"❌ 无效的值: {value}，请使用 true/false")
                return 1
            updates['auto_pager'] = bool_values[value.lower()]
        else:
            print(f"❌ 未知的配置项: {key}")
            return 1
        
        if updates:
            success = assistant.ui_config_manager.update_config(updates)
            if success:
                print(f"✅ 配置已更新: {key} = {value}")
                return 0
            else:
                print(f"❌ 更新配置失败")
                return 1
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_config_reset_command(assistant):
    """处理 ui config reset 命令 - 重置 UI 配置"""
    if not assistant.ui_config_manager:
        print("❌ UI 配置管理器未初始化")
        return 1
    
    try:
        print("\n⚠️  警告: 这将重置所有 UI 配置为默认值")
        confirm = input("确认重置? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', '是']:
            print("❌ 取消重置")
            return 0
        
        success = assistant.ui_config_manager.reset_to_defaults()
        if success:
            print("✅ UI 配置已重置为默认值")
            return 0
        else:
            print("❌ 重置失败")
            return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def ui_check_command(assistant):
    """处理 ui check 命令 - 检查终端兼容性"""
    try:
        if hasattr(assistant, 'ui_compatibility') and assistant.ui_compatibility:
            assistant.ui_compatibility.print_compatibility_info()
        else:
            # 如果没有兼容性层，创建一个临时的
            from src.ui import UICompatibilityLayer
            compat = UICompatibilityLayer()
            compat.print_compatibility_info()
        
        return 0
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1
