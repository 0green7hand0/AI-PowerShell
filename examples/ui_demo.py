"""
UI 系统演示脚本

展示新的 CLI UI 功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import UIManager
from src.ui.models import UIConfig


def main():
    """主函数"""
    # 创建 UI 管理器
    config = UIConfig(
        enable_colors=True,
        enable_icons=True,
        theme="default"
    )
    ui = UIManager(config)
    
    # 演示标题
    ui.print_header("AI PowerShell 智能助手", "CLI UI 系统演示")
    ui.print_newline()
    
    # 演示各种消息类型
    ui.print_success("这是一条成功消息")
    ui.print_error("这是一条错误消息")
    ui.print_warning("这是一条警告消息")
    ui.print_info("这是一条信息消息")
    ui.print_newline()
    
    # 演示表格
    table = ui.create_table(title="模板列表", show_header=True)
    table.add_column("名称", style="cyan", no_wrap=True)
    table.add_column("描述", style="white")
    table.add_column("分类", style="green")
    table.add_column("状态", justify="center")
    
    table.add_row("backup_script", "系统备份脚本", "自动化", "✓")
    table.add_row("network_test", "网络诊断工具", "网络", "✓")
    table.add_row("log_analyzer", "日志分析脚本", "监控", "✓")
    
    ui.print_table(table)
    ui.print_newline()
    
    # 演示列表
    ui.print_list(
        ["显示当前时间", "列出所有文件", "查看系统信息"],
        title="使用示例",
        numbered=True
    )
    ui.print_newline()
    
    # 演示字典
    ui.print_dict(
        {
            "版本": "2.0.0",
            "Python": "3.8+",
            "主题": "default",
            "图标": "emoji"
        },
        title="系统信息"
    )
    ui.print_newline()
    
    # 演示面板
    panel = ui.create_panel(
        "这是一个面板示例\n包含多行文本\n可以用于显示重要信息",
        title="提示",
        border_style="info"
    )
    ui.print_panel(panel)
    
    ui.print_newline()
    ui.print_success("UI 演示完成！")


if __name__ == "__main__":
    main()
