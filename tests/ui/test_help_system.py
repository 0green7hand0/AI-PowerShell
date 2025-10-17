"""
帮助系统测试
"""

import pytest
import sys
from pathlib import Path
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui import UIManager, HelpSystem
from src.ui.models import UIConfig, CommandDefinition, ArgumentDefinition


class TestHelpSystem:
    """测试帮助系统"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def help_system(self, ui_manager):
        """创建帮助系统实例"""
        return HelpSystem(ui_manager)
    
    def test_help_system_initialization(self, help_system):
        """测试帮助系统初始化"""
        assert help_system is not None
        assert help_system.ui_manager is not None
        assert help_system.commands is not None
        assert len(help_system.commands) > 0
    
    def test_register_command(self, help_system):
        """测试注册命令"""
        cmd = CommandDefinition(
            name="test_cmd",
            description="测试命令",
            usage="test_cmd [options]",
            examples=["test_cmd --help"],
            aliases=["tc"]
        )
        
        help_system.register_command(cmd)
        
        # 验证命令已注册
        assert "test_cmd" in help_system.commands
        assert help_system.commands["test_cmd"] == cmd
        
        # 验证别名已注册
        assert "tc" in help_system.commands
        assert help_system.commands["tc"] == cmd
    
    def test_list_all_commands(self, help_system):
        """测试列出所有命令"""
        commands = help_system.list_all_commands()
        
        assert isinstance(commands, list)
        assert len(commands) > 0
        
        # 验证主要命令存在
        assert "interactive" in commands
        assert "command" in commands
        assert "template" in commands
        assert "help" in commands
    
    def test_get_command_definition(self, help_system):
        """测试获取命令定义"""
        # 获取存在的命令
        cmd = help_system.get_command_definition("help")
        assert cmd is not None
        assert cmd.name == "help"
        assert cmd.description is not None
        
        # 获取不存在的命令
        cmd = help_system.get_command_definition("nonexistent")
        assert cmd is None
    
    def test_get_command_by_alias(self, help_system):
        """测试通过别名获取命令"""
        # help 命令有别名 "帮助"
        cmd = help_system.get_command_definition("帮助")
        assert cmd is not None
        assert cmd.name == "help"
    
    def test_show_general_help(self, help_system, capsys):
        """测试显示总体帮助"""
        help_system.show_general_help()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含关键信息
        assert len(output) > 0
        assert "AI PowerShell" in output or "智能助手" in output
    
    def test_show_command_help_existing(self, help_system, capsys):
        """测试显示存在的命令帮助"""
        help_system.show_command_help("help")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含命令信息
        assert len(output) > 0
        assert "help" in output.lower()
    
    def test_show_command_help_nonexistent(self, help_system, capsys):
        """测试显示不存在的命令帮助"""
        help_system.show_command_help("nonexistent_command")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证显示错误信息
        assert len(output) > 0
        assert "未知命令" in output or "unknown" in output.lower()
    
    def test_show_subcommand_help(self, help_system, capsys):
        """测试显示子命令帮助"""
        help_system.show_subcommand_help("template", "create")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含子命令信息
        assert len(output) > 0
        assert "create" in output.lower()


class TestCommandSuggestions:
    """测试命令建议功能"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def help_system(self, ui_manager):
        """创建帮助系统实例"""
        return HelpSystem(ui_manager)
    
    def test_suggest_similar_commands_exact_match(self, help_system):
        """测试完全匹配的命令建议"""
        suggestions = help_system.suggest_similar_commands("help")
        
        # 完全匹配应该返回该命令
        assert "help" in suggestions
    
    def test_suggest_similar_commands_typo(self, help_system):
        """测试拼写错误的命令建议"""
        # "hlep" 应该建议 "help"
        suggestions = help_system.suggest_similar_commands("hlep")
        
        assert len(suggestions) > 0
        assert "help" in suggestions
    
    def test_suggest_similar_commands_partial(self, help_system):
        """测试部分匹配的命令建议"""
        # "templa" 应该建议 "template"
        suggestions = help_system.suggest_similar_commands("templa")
        
        assert len(suggestions) > 0
        # template 应该在建议中
        assert "template" in suggestions
    
    def test_suggest_similar_commands_empty(self, help_system):
        """测试空输入的命令建议"""
        suggestions = help_system.suggest_similar_commands("")
        
        # 空输入应该返回空列表
        assert suggestions == []
    
    def test_suggest_similar_commands_no_match(self, help_system):
        """测试完全不匹配的命令建议"""
        suggestions = help_system.suggest_similar_commands("xyzabc123")
        
        # 完全不匹配可能返回空列表或距离较远的命令
        assert isinstance(suggestions, list)
    
    def test_levenshtein_distance(self, help_system):
        """测试编辑距离计算"""
        # 相同字符串距离为 0
        distance = help_system._levenshtein_distance("hello", "hello")
        assert distance == 0
        
        # 一个字符差异
        distance = help_system._levenshtein_distance("hello", "hallo")
        assert distance == 1
        
        # 完全不同
        distance = help_system._levenshtein_distance("abc", "xyz")
        assert distance == 3
        
        # 空字符串
        distance = help_system._levenshtein_distance("", "hello")
        assert distance == 5
        
        distance = help_system._levenshtein_distance("hello", "")
        assert distance == 5


class TestInteractiveHelp:
    """测试交互式帮助功能"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def help_system(self, ui_manager):
        """创建帮助系统实例"""
        return HelpSystem(ui_manager)
    
    def test_show_quick_reference(self, help_system, capsys):
        """测试显示快速参考"""
        help_system.show_quick_reference()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含快速参考信息
        assert len(output) > 0
        assert "快速参考" in output or "reference" in output.lower()
    
    def test_show_examples_by_category_template(self, help_system, capsys):
        """测试显示模板类别的示例"""
        help_system.show_examples_by_category("template")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含模板示例
        assert len(output) > 0
        assert "template" in output.lower()
    
    def test_show_examples_by_category_command(self, help_system, capsys):
        """测试显示命令类别的示例"""
        help_system.show_examples_by_category("command")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证输出包含命令示例
        assert len(output) > 0
    
    def test_show_examples_by_category_invalid(self, help_system, capsys):
        """测试显示无效类别的示例"""
        help_system.show_examples_by_category("invalid_category")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证显示错误信息
        assert len(output) > 0
        assert "未知类别" in output or "unknown" in output.lower()
    
    def test_format_command_usage(self, help_system):
        """测试格式化命令用法"""
        usage = help_system.format_command_usage("help")
        
        assert usage is not None
        assert isinstance(usage, str)
        assert len(usage) > 0
    
    def test_format_command_usage_invalid(self, help_system):
        """测试格式化无效命令用法"""
        usage = help_system.format_command_usage("nonexistent")
        
        assert usage is not None
        assert "未知命令" in usage


class TestCommandDefinitions:
    """测试命令定义的完整性"""
    
    @pytest.fixture
    def ui_manager(self):
        """创建 UI 管理器实例"""
        config = UIConfig(enable_colors=True, enable_icons=True)
        return UIManager(config)
    
    @pytest.fixture
    def help_system(self, ui_manager):
        """创建帮助系统实例"""
        return HelpSystem(ui_manager)
    
    def test_all_main_commands_defined(self, help_system):
        """测试所有主要命令都已定义"""
        required_commands = ["interactive", "command", "template", "help", "history", "clear", "exit"]
        
        for cmd_name in required_commands:
            cmd = help_system.get_command_definition(cmd_name)
            assert cmd is not None, f"命令 {cmd_name} 未定义"
            assert cmd.name == cmd_name
            assert cmd.description is not None and len(cmd.description) > 0
            assert cmd.usage is not None and len(cmd.usage) > 0
    
    def test_template_subcommands_defined(self, help_system):
        """测试模板子命令都已定义"""
        template_cmd = help_system.get_command_definition("template")
        assert template_cmd is not None
        assert len(template_cmd.subcommands) > 0
        
        required_subcommands = ["create", "list", "edit", "delete", "export", "import", "history", "restore", "test"]
        
        subcommand_names = [sub.name for sub in template_cmd.subcommands]
        for subcmd_name in required_subcommands:
            assert subcmd_name in subcommand_names, f"子命令 {subcmd_name} 未定义"
    
    def test_command_has_examples(self, help_system):
        """测试命令都有使用示例"""
        main_commands = ["interactive", "command", "template"]
        
        for cmd_name in main_commands:
            cmd = help_system.get_command_definition(cmd_name)
            assert cmd is not None
            assert len(cmd.examples) > 0, f"命令 {cmd_name} 没有示例"
    
    def test_command_arguments_complete(self, help_system):
        """测试命令参数定义完整"""
        cmd = help_system.get_command_definition("command")
        assert cmd is not None
        assert len(cmd.arguments) > 0
        
        # 验证参数定义完整
        for arg in cmd.arguments:
            assert arg.name is not None and len(arg.name) > 0
            assert arg.type is not None and len(arg.type) > 0
            assert arg.description is not None and len(arg.description) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
