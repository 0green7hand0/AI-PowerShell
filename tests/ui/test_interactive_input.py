"""
交互式输入管理器测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.ui.interactive_input import InteractiveInputManager, CommandCompleter, CommandValidator
from src.ui.ui_manager import UIManager


@pytest.fixture
def ui_manager():
    """创建 UI 管理器实例"""
    return UIManager()


@pytest.fixture
def input_manager(ui_manager, tmp_path):
    """创建交互式输入管理器实例"""
    history_file = tmp_path / ".test_history"
    return InteractiveInputManager(ui_manager, str(history_file))


class TestCommandCompleter:
    """命令补全器测试"""
    
    def test_completer_initialization(self):
        """测试补全器初始化"""
        commands = ['help', 'history', 'exit']
        subcommands = {'template': ['create', 'list']}
        completer = CommandCompleter(commands, subcommands)
        
        assert completer.commands == commands
        assert completer.subcommands == subcommands
    
    def test_main_command_completion(self):
        """测试主命令补全"""
        commands = ['help', 'history', 'exit']
        completer = CommandCompleter(commands)
        
        # 创建模拟文档
        mock_doc = Mock()
        mock_doc.text_before_cursor = 'he'
        
        completions = list(completer.get_completions(mock_doc, None))
        
        # 应该补全为 'help'
        assert len(completions) > 0
        assert any(c.text == 'help' for c in completions)
    
    def test_subcommand_completion(self):
        """测试子命令补全"""
        commands = ['template']
        subcommands = {'template': ['create', 'list', 'edit']}
        completer = CommandCompleter(commands, subcommands)
        
        # 创建模拟文档
        mock_doc = Mock()
        mock_doc.text_before_cursor = 'template cr'
        
        completions = list(completer.get_completions(mock_doc, None))
        
        # 应该补全为 'create'
        assert len(completions) > 0
        assert any(c.text == 'create' for c in completions)
    
    def test_empty_completion(self):
        """测试空输入补全"""
        commands = ['help', 'history']
        completer = CommandCompleter(commands)
        
        mock_doc = Mock()
        mock_doc.text_before_cursor = ''
        
        completions = list(completer.get_completions(mock_doc, None))
        
        # 应该返回所有主命令
        assert len(completions) == len(commands)


class TestInteractiveInputManager:
    """交互式输入管理器测试"""
    
    def test_initialization(self, input_manager):
        """测试初始化"""
        assert input_manager.ui_manager is not None
        assert input_manager.history is not None
        assert input_manager.completer is not None
        # Session may be None in test environment without console
        assert hasattr(input_manager, '_session')
    
    def test_commands_list(self, input_manager):
        """测试命令列表"""
        assert 'help' in input_manager.commands
        assert '帮助' in input_manager.commands
        assert 'history' in input_manager.commands
        assert 'exit' in input_manager.commands
        assert 'template' in input_manager.commands
    
    def test_subcommands_list(self, input_manager):
        """测试子命令列表"""
        assert 'template' in input_manager.subcommands
        assert 'create' in input_manager.subcommands['template']
        assert 'list' in input_manager.subcommands['template']
        assert 'edit' in input_manager.subcommands['template']
    
    def test_add_command(self, input_manager):
        """测试添加命令"""
        new_command = 'newcmd'
        input_manager.add_command(new_command)
        
        assert new_command in input_manager.commands
    
    def test_add_subcommand(self, input_manager):
        """测试添加子命令"""
        main_cmd = 'template'
        new_subcmd = 'newsubcmd'
        
        input_manager.add_subcommand(main_cmd, new_subcmd)
        
        assert new_subcmd in input_manager.subcommands[main_cmd]
    
    def test_suggest_similar_commands(self, input_manager):
        """测试相似命令建议"""
        # 测试拼写错误
        suggestions = input_manager.suggest_similar_commands('hlep')
        assert 'help' in suggestions
        
        # 测试中文命令
        suggestions = input_manager.suggest_similar_commands('帮')
        assert '帮助' in suggestions
        
        # 测试完全不相关的命令
        suggestions = input_manager.suggest_similar_commands('xyz123')
        assert len(suggestions) == 0
    
    def test_validate_command_structure_valid(self, input_manager):
        """测试有效命令验证"""
        is_valid, error = input_manager.validate_command_structure('help')
        assert is_valid is True
        assert error is None
        
        is_valid, error = input_manager.validate_command_structure('template list')
        assert is_valid is True
        assert error is None
    
    def test_validate_command_structure_invalid_main(self, input_manager):
        """测试无效主命令验证"""
        is_valid, error = input_manager.validate_command_structure('invalidcmd')
        assert is_valid is False
        assert error is not None
        assert 'invalidcmd' in error
    
    def test_validate_command_structure_invalid_sub(self, input_manager):
        """测试无效子命令验证"""
        is_valid, error = input_manager.validate_command_structure('template invalidsubcmd')
        assert is_valid is False
        assert error is not None
        assert 'invalidsubcmd' in error
    
    def test_validate_command_structure_empty(self, input_manager):
        """测试空命令验证"""
        is_valid, error = input_manager.validate_command_structure('')
        assert is_valid is False
        assert error is not None
    
    def test_get_command_help(self, input_manager):
        """测试获取命令帮助"""
        help_text = input_manager.get_command_help('help')
        assert help_text is not None
        assert '帮助' in help_text or '显示' in help_text
        
        help_text = input_manager.get_command_help('template')
        assert help_text is not None
        assert '模板' in help_text
    
    def test_get_parameter_hints(self, input_manager):
        """测试获取参数提示"""
        # 测试 template edit 命令
        hints = input_manager.get_parameter_hints('template edit')
        assert len(hints) > 0
        assert any(h['name'] == 'template_id' for h in hints)
        
        # 测试 template export 命令
        hints = input_manager.get_parameter_hints('template export')
        assert len(hints) > 0
        assert any(h['name'] == 'template_id' for h in hints)
        assert any('-o' in h['name'] or '--output' in h['name'] for h in hints)
    
    @patch('builtins.input')
    def test_get_user_input(self, mock_input, input_manager):
        """测试获取用户输入"""
        mock_input.return_value = 'test input'
        
        result = input_manager.get_user_input()
        
        assert result == 'test input'
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    def test_get_confirmation_yes(self, mock_input, input_manager):
        """测试获取确认 - 是"""
        mock_input.return_value = 'y'
        
        result = input_manager.get_confirmation('确认吗?')
        
        assert result is True
    
    @patch('builtins.input')
    def test_get_confirmation_no(self, mock_input, input_manager):
        """测试获取确认 - 否"""
        mock_input.return_value = 'n'
        
        result = input_manager.get_confirmation('确认吗?')
        
        assert result is False
    
    @patch('builtins.input')
    def test_get_confirmation_default(self, mock_input, input_manager):
        """测试获取确认 - 默认值"""
        mock_input.return_value = ''
        
        result = input_manager.get_confirmation('确认吗?', default=True)
        assert result is True
        
        mock_input.return_value = ''
        result = input_manager.get_confirmation('确认吗?', default=False)
        assert result is False
    
    @patch('builtins.input')
    def test_select_from_list(self, mock_input, input_manager):
        """测试从列表选择"""
        options = ['选项1', '选项2', '选项3']
        mock_input.return_value = '2'
        
        result = input_manager.select_from_list(options, '请选择')
        
        assert result == '选项2'
    
    @patch('builtins.input')
    def test_select_from_list_invalid(self, mock_input, input_manager):
        """测试从列表选择 - 无效选择"""
        options = ['选项1', '选项2']
        mock_input.return_value = '99'
        
        result = input_manager.select_from_list(options, '请选择')
        
        assert result is None
    
    @patch('builtins.input')
    def test_get_multiline_input(self, mock_input, input_manager):
        """测试获取多行输入"""
        mock_input.side_effect = ['line 1', 'line 2', 'END']
        
        result = input_manager.get_multiline_input('输入内容')
        
        assert result == 'line 1\nline 2'
    
    def test_history_file_creation(self, tmp_path):
        """测试历史文件创建"""
        history_file = tmp_path / "subdir" / ".history"
        ui_manager = UIManager()
        
        input_manager = InteractiveInputManager(ui_manager, str(history_file))
        
        # 历史文件的父目录应该被创建
        assert history_file.parent.exists()


class TestCommandValidator:
    """命令验证器测试"""
    
    def test_validator_initialization(self, input_manager):
        """测试验证器初始化"""
        validator = CommandValidator(input_manager)
        assert validator.input_manager is input_manager
    
    def test_validate_empty_command(self, input_manager):
        """测试验证空命令"""
        validator = CommandValidator(input_manager)
        mock_doc = Mock()
        mock_doc.text = ''
        
        # 空命令不应该抛出异常
        validator.validate(mock_doc)
    
    def test_validate_valid_command(self, input_manager):
        """测试验证有效命令"""
        validator = CommandValidator(input_manager)
        mock_doc = Mock()
        mock_doc.text = 'help'
        
        # 有效命令不应该抛出异常
        validator.validate(mock_doc)
    
    def test_validate_invalid_command(self, input_manager):
        """测试验证无效命令"""
        from prompt_toolkit.validation import ValidationError
        
        validator = CommandValidator(input_manager)
        mock_doc = Mock()
        mock_doc.text = 'invalidcommand'
        
        # 无效命令应该抛出 ValidationError
        with pytest.raises(ValidationError):
            validator.validate(mock_doc)
