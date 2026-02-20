"""模板命令处理模块

此模块包含所有与模板相关的命令处理函数，包括创建、列出、编辑、删除、导出、导入、查看历史和恢复版本等操作。
"""

from pathlib import Path
from types import SimpleNamespace
from src.template_engine.exceptions import TemplateError
from src.ui.error_handler import ErrorCategory


def template_create_command(assistant):
    """处理 template create 命令 - 创建自定义模板"""
    if not assistant.custom_template_manager:
        error = Exception("自定义模板管理器未初始化")
        if assistant.error_handler:
            assistant.error_handler.display_error(
                error,
                category=ErrorCategory.CONFIG_ERROR,
                suggestions=[
                    "检查配置文件中的模板管理器设置",
                    "确认模板目录存在且可访问",
                    "尝试重新启动程序",
                ]
            )
        else:
            print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用新的交互式向导
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 运行交互式向导
        template_data = ui.interactive_template_wizard()
        
        if not template_data:
            return 1
        
        # 显示进度
        steps = [
            "验证模板信息",
            "解析脚本参数",
            "生成模板文件",
            "更新配置文件"
        ]
        
        with ui.show_progress_for_operation("创建模板", steps) as progress:
            # 创建模板
            template = assistant.custom_template_manager.create_template(
                name=template_data['name'],
                description=template_data['description'],
                category=template_data['category'],
                script_content=template_data['script_content'],
                keywords=template_data['keywords']
            )
        
        # 显示操作摘要
        details = {
            '分类': template.category,
            '文件路径': template.file_path,
            '参数数量': len(template.parameters) if template.parameters else 0,
            '关键词': ', '.join(template_data['keywords']) if template_data['keywords'] else '无'
        }
        
        ui.display_operation_summary('create', template, True, details)
        
        return 0
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板名称是否已存在",
                    "确认脚本内容格式正确",
                    "参考文档中的模板创建示例",
                ],
                related_commands=["template list"]
            )
        else:
            print(f"\n❌ 创建失败: {str(e)}")
        return 1
    except Exception as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                details="创建模板时发生未预期的错误",
                show_traceback=False
            )
        else:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        return 1


def template_list_command(assistant, custom_only=False):
    """处理 template list 命令 - 列出模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的模板显示界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板列表
        if custom_only:
            templates = assistant.custom_template_manager.list_custom_templates()
            title = "📋 自定义模板列表"
        else:
            # 获取所有模板（系统 + 自定义）
            templates = assistant.custom_template_manager.list_custom_templates()
            # 如果有 template_manager，也包含系统模板
            if hasattr(assistant, 'template_manager') and assistant.template_manager:
                system_templates = assistant.template_manager.list_templates()
                templates.extend(system_templates)
            title = "📋 模板列表"
        
        # 显示增强的模板列表
        ui.display_template_list_enhanced(
            templates,
            title=title,
            show_icons=True,
            group_by_category=True
        )
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_edit_command(assistant, template_id):
    """处理 template edit 命令 - 编辑模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的编辑界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板信息
        template_info = assistant.custom_template_manager.get_template_info(template_id, 'custom')
        if not template_info:
            ui.ui_manager.print_error(f"模板不存在: {template_id}")
            return 1
        
        # 创建临时模板对象用于显示
        template = SimpleNamespace(**template_info)
        
        # 运行交互式编辑器
        updates = ui.interactive_template_editor(template)
        
        if not updates:
            return 0
        
        # 显示进度
        steps = [
            "验证更新信息",
            "应用更新",
            "更新配置文件"
        ]
        
        with ui.show_progress_for_operation("更新模板", steps) as progress:
            # 应用更新
            updated_template = assistant.custom_template_manager.edit_template(
                template_id,
                'custom',
                updates
            )
        
        # 显示操作摘要
        details = {
            '更新字段': ', '.join(updates.keys()),
            '新名称': updated_template.name if 'name' in updates else template.name,
            '新描述': updated_template.description if 'description' in updates else template.description
        }
        
        ui.display_operation_summary('edit', updated_template, True, details)
        
        return 0
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板 ID 是否正确",
                    "确认模板是自定义模板",
                    "使用 'template list' 查看可用模板",
                ]
            )
        else:
            print(f"\n❌ 编辑失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_delete_command(assistant, template_id):
    """处理 template delete 命令 - 删除模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        # 使用增强的删除确认界面
        from src.ui.template_manager_ui import TemplateManagerUI
        
        ui = TemplateManagerUI()
        
        # 获取模板信息
        template_info = assistant.custom_template_manager.get_template_info(template_id, 'custom')
        if not template_info:
            ui.ui_manager.print_error(f"模板不存在: {template_id}")
            return 1
        
        # 创建临时模板对象用于显示
        template = SimpleNamespace(**template_info)
        
        # 显示删除确认对话框
        confirmed = ui.confirm_template_deletion(template)
        
        if not confirmed:
            ui.ui_manager.print_warning("已取消删除")
            return 0
        
        # 显示进度
        steps = [
            "删除模板文件",
            "更新配置文件",
            "清理相关资源"
        ]
        
        with ui.show_progress_for_operation("删除模板", steps) as progress:
            # 执行删除
            success = assistant.custom_template_manager.delete_template(template_id, 'custom')
        
        if success:
            # 显示操作摘要
            details = {
                '模板名称': template.name,
                '分类': template.category,
                '文件路径': template.file_path
            }
            ui.display_operation_summary('delete', template, True, details)
            return 0
        else:
            ui.ui_manager.print_error("删除失败")
            return 1
        
    except TemplateError as e:
        if assistant.error_handler:
            assistant.error_handler.display_error(
                e,
                category=ErrorCategory.VALIDATION_ERROR,
                suggestions=[
                    "检查模板 ID 是否正确",
                    "确认模板是自定义模板",
                    "使用 'template list' 查看可用模板",
                ]
            )
        else:
            print(f"\n❌ 删除失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_export_command(assistant, template_id, output_path):
    """处理 template export 命令 - 导出模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"📦 导出模板: {template_id}")
        print("=" * 60)
        
        # 导出模板
        print("\n正在导出模板...")
        exported_path = assistant.custom_template_manager.export_template(template_id, output_path)
        
        print(f"\n✅ 模板已导出到: {exported_path}")
        print("=" * 60)
        
        return 0
        
    except TemplateError as e:
        print(f"\n❌ 导出失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_import_command(assistant, package_path, overwrite=False):
    """处理 template import 命令 - 导入模板"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"📥 导入模板")
        print("=" * 60)
        
        if not Path(package_path).exists():
            print(f"\n❌ 文件不存在: {package_path}")
            return 1
        
        # 导入模板
        print(f"\n正在导入模板包: {package_path}")
        template = assistant.custom_template_manager.import_template(package_path, overwrite=overwrite)
        
        print(f"\n✅ 模板导入成功!")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        print("=" * 60)
        
        return 0
        
    except TemplateError as e:
        print(f"\n❌ 导入失败: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_history_command(assistant, template_id):
    """处理 template history 命令 - 查看模板历史"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        from src.ui import UIManager, TemplateDisplay
        
        ui_manager = UIManager()
        template_display = TemplateDisplay(ui_manager)
        
        # 获取历史版本
        versions = assistant.custom_template_manager.version_control.list_versions(template_id)
        
        template_display.display_version_history(versions, template_id)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_restore_command(assistant, template_id, version):
    """处理 template restore 命令 - 恢复模板版本"""
    if not assistant.custom_template_manager:
        print("❌ 自定义模板管理器未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"🔄 恢复模板版本")
        print("=" * 60)
        
        # 确认恢复
        print(f"\n将恢复模板 '{template_id}' 到版本 {version}")
        confirm = input("确认恢复? (y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes', '是']:
            print("\n❌ 取消恢复")
            return 1
        
        # 恢复版本
        print("\n正在恢复版本...")
        success = assistant.custom_template_manager.version_control.restore_version(template_id, version)
        
        if success:
            print(f"\n✅ 已恢复到版本 {version}")
            return 0
        else:
            print("\n❌ 恢复失败")
            return 1
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


def template_test_command(assistant, template_id, show_script=True):
    """处理 template test 命令 - 测试模板"""
    if not assistant.template_engine:
        print("❌ 模板引擎未初始化")
        return 1
    
    try:
        print("\n" + "=" * 60)
        print(f"🧪 测试模板")
        print("=" * 60)
        
        # 从模板引擎获取模板
        # 模板ID格式: category.template_name
        template = None
        for tmpl in assistant.template_engine.template_manager.templates.values():
            if tmpl.id == template_id:
                template = tmpl
                break
        
        if not template:
            print(f"\n❌ 未找到模板: {template_id}")
            return 1
        
        # 测试模板
        print(f"\n模板信息:")
        print(f"  名称: {template.name}")
        print(f"  描述: {template.description}")
        print(f"  分类: {template.category}")
        print(f"  参数: {len(template.parameters)}")
        
        if show_script:
            print(f"\n脚本内容:")
            print("-" * 60)
            print(template.script_content)
            print("-" * 60)
        
        print(f"\n✅ 模板测试成功!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return 1
