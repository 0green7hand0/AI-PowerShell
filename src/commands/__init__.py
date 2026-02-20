"""命令处理模块包

此包包含所有命令处理函数，按功能分类到不同的模块中。
"""

from src.commands.template_commands import (
    template_create_command,
    template_list_command,
    template_edit_command,
    template_delete_command,
    template_export_command,
    template_import_command,
    template_history_command,
    template_restore_command,
    template_test_command
)

from src.commands.ui_commands import (
    ui_config_show_command,
    ui_config_set_command,
    ui_config_reset_command,
    ui_check_command
)

__all__ = [
    # 模板命令
    'template_create_command',
    'template_list_command',
    'template_edit_command',
    'template_delete_command',
    'template_export_command',
    'template_import_command',
    'template_history_command',
    'template_restore_command',
    'template_test_command',
    # UI 命令
    'ui_config_show_command',
    'ui_config_set_command',
    'ui_config_reset_command',
    'ui_check_command'
]
