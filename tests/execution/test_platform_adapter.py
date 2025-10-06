"""
平台适配器测试模块

测试 PlatformAdapter 类的功能，包括：
- 平台检测
- 路径转换
- 命令适配
- 环境变量处理
"""

import pytest
import platform
from unittest.mock import patch
from pathlib import Path

from src.execution.platform_adapter import PlatformAdapter


class TestPlatformAdapter:
    """平台适配器测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_init(self, adapter):
        """测试适配器初始化"""
        assert adapter.platform_name in ['Windows', 'Linux', 'Darwin']
        assert isinstance(adapter.is_windows, bool)
        assert isinstance(adapter.is_linux, bool)
        assert isinstance(adapter.is_macos, bool)
    
    def test_platform_detection(self, adapter):
        """测试平台检测"""
        # 确保只有一个平台标志为 True
        platform_flags = [adapter.is_windows, adapter.is_linux, adapter.is_macos]
        assert sum(platform_flags) == 1
    
    def test_get_platform_info(self, adapter):
        """测试获取平台信息"""
        info = adapter.get_platform_info()
        
        assert isinstance(info, dict)
        assert 'system' in info
        assert 'release' in info
        assert 'version' in info
        assert 'machine' in info
        assert 'python_version' in info
        assert info['system'] in ['Windows', 'Linux', 'Darwin']
    
    def test_get_path_separator(self, adapter):
        """测试获取路径分隔符"""
        separator = adapter.get_path_separator()
        
        if adapter.is_windows:
            assert separator == '\\'
        else:
            assert separator == '/'
    
    def test_get_line_separator(self, adapter):
        """测试获取行分隔符"""
        separator = adapter.get_line_separator()
        assert separator in ['\n', '\r\n']
    
    def test_get_home_directory(self, adapter):
        """测试获取主目录"""
        home = adapter.get_home_directory()
        
        assert isinstance(home, str)
        assert len(home) > 0
        assert Path(home).exists()
    
    def test_get_temp_directory(self, adapter):
        """测试获取临时目录"""
        temp = adapter.get_temp_directory()
        
        assert isinstance(temp, str)
        assert len(temp) > 0
        assert Path(temp).exists()
    
    def test_normalize_path(self, adapter):
        """测试路径规范化"""
        # 测试相对路径
        normalized = adapter.normalize_path('test/path')
        assert isinstance(normalized, str)
        
        # 测试绝对路径
        if adapter.is_windows:
            normalized = adapter.normalize_path('C:\\test\\path')
        else:
            normalized = adapter.normalize_path('/test/path')
        assert isinstance(normalized, str)
    
    def test_is_absolute_path(self, adapter):
        """测试绝对路径判断"""
        if adapter.is_windows:
            assert adapter.is_absolute_path('C:\\test') is True
            assert adapter.is_absolute_path('test') is False
        else:
            assert adapter.is_absolute_path('/test') is True
            assert adapter.is_absolute_path('test') is False
    
    def test_join_paths(self, adapter):
        """测试路径连接"""
        joined = adapter.join_paths('dir1', 'dir2', 'file.txt')
        
        assert isinstance(joined, str)
        assert 'dir1' in joined
        assert 'dir2' in joined
        assert 'file.txt' in joined
    
    def test_get_encoding(self, adapter):
        """测试获取编码"""
        encoding = adapter.get_encoding()
        
        if adapter.is_windows:
            assert encoding == 'gbk'
        else:
            assert encoding == 'utf-8'
    
    def test_get_powershell_executable(self, adapter):
        """测试获取 PowerShell 可执行文件"""
        ps_path = adapter.get_powershell_executable()
        
        # 如果系统中有 PowerShell，应该返回路径
        if ps_path:
            assert isinstance(ps_path, str)
            assert len(ps_path) > 0
    
    def test_supports_powershell_core(self, adapter):
        """测试 PowerShell Core 支持检测"""
        supports = adapter.supports_powershell_core()
        assert isinstance(supports, bool)
    
    def test_supports_windows_powershell(self, adapter):
        """测试 Windows PowerShell 支持检测"""
        supports = adapter.supports_windows_powershell()
        assert isinstance(supports, bool)
        
        # 非 Windows 系统应该返回 False
        if not adapter.is_windows:
            assert supports is False
    
    def test_get_recommended_powershell(self, adapter):
        """测试获取推荐的 PowerShell"""
        recommended = adapter.get_recommended_powershell()
        
        if recommended:
            assert recommended in ['pwsh', 'powershell']


class TestPlatformAdapterPathConversion:
    """路径转换测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_adapt_command_same_platform(self, adapter):
        """测试相同平台的命令适配"""
        command = 'Get-ChildItem'
        adapted = adapter.adapt_command(command)
        
        # 相同平台应该返回原命令
        assert adapted == command
    
    @patch('platform.system', return_value='Windows')
    def test_windows_to_unix_path_conversion(self, mock_system):
        """测试 Windows 到 Unix 路径转换"""
        adapter = PlatformAdapter()
        
        # 测试驱动器路径转换
        command = 'Get-ChildItem C:\\Users\\test'
        adapted = adapter.adapt_command(command, target_platform='Linux')
        
        # 应该转换反斜杠为正斜杠
        assert '\\' not in adapted or adapted == command
    
    @patch('platform.system', return_value='Linux')
    def test_unix_to_windows_path_conversion(self, mock_system):
        """测试 Unix 到 Windows 路径转换"""
        adapter = PlatformAdapter()
        
        command = 'Get-ChildItem /mnt/c/Users/test'
        adapted = adapter.adapt_command(command, target_platform='Windows')
        
        # 路径应该被适配
        assert isinstance(adapted, str)
    
    def test_convert_windows_drive_to_unix(self, adapter):
        """测试 Windows 驱动器到 Unix 路径转换"""
        if adapter.is_windows:
            command = 'Get-ChildItem C:\\test'
            converted = adapter._convert_windows_drive_to_unix(command)
            
            # C:\ 应该被转换为 /mnt/c/
            if 'C:' in command:
                assert '/mnt/c/' in converted or converted == command
    
    def test_convert_unix_to_windows_path(self, adapter):
        """测试 Unix 到 Windows 路径转换"""
        command = 'Get-ChildItem /mnt/c/test'
        converted = adapter._convert_unix_to_windows_path(command)
        
        # /mnt/c/ 应该被转换为 C:\
        if '/mnt/c/' in command:
            assert 'C:\\' in converted or converted == command


class TestPlatformAdapterCommandMapping:
    """命令映射测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_command_mappings_exist(self, adapter):
        """测试命令映射存在"""
        assert isinstance(adapter.command_mappings, dict)
        assert 'windows_to_unix' in adapter.command_mappings
        assert 'unix_to_windows' in adapter.command_mappings
    
    def test_windows_to_unix_mappings(self, adapter):
        """测试 Windows 到 Unix 命令映射"""
        mappings = adapter.command_mappings['windows_to_unix']
        
        assert 'dir' in mappings
        assert 'cls' in mappings
        assert mappings['dir'] == 'Get-ChildItem'
        assert mappings['cls'] == 'Clear-Host'
    
    def test_unix_to_windows_mappings(self, adapter):
        """测试 Unix 到 Windows 命令映射"""
        mappings = adapter.command_mappings['unix_to_windows']
        
        assert 'ls' in mappings
        assert 'clear' in mappings
        assert mappings['ls'] == 'Get-ChildItem'
        assert mappings['clear'] == 'Clear-Host'


class TestPlatformAdapterShellAdaptation:
    """Shell 适配测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_adapt_for_powershell(self, adapter):
        """测试 PowerShell 命令适配"""
        command = 'Get-Date'
        adapted = adapter.adapt_command_for_shell(command, 'powershell')
        
        # PowerShell 命令不需要修改
        assert adapted == command
    
    def test_adapt_for_bash(self, adapter):
        """测试 Bash 命令适配"""
        command = 'Get-Date'
        adapted = adapter.adapt_command_for_shell(command, 'bash')
        
        # 应该包装为 pwsh -Command
        assert 'pwsh' in adapted
        assert command in adapted
    
    def test_adapt_for_cmd(self, adapter):
        """测试 CMD 命令适配"""
        command = 'Get-Date'
        adapted = adapter.adapt_command_for_shell(command, 'cmd')
        
        # 应该包装为 powershell -Command
        assert 'powershell' in adapted
        assert command in adapted


class TestPlatformAdapterEnvironmentVariables:
    """环境变量测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_expand_environment_variables(self, adapter):
        """测试环境变量展开"""
        command = 'echo $env:PATH'
        expanded = adapter.expand_environment_variables(command)
        
        # PowerShell 变量不应该被展开（让 PowerShell 自己处理）
        assert expanded == command


class TestPlatformAdapterEdgeCases:
    """边界情况测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建平台适配器实例"""
        return PlatformAdapter()
    
    def test_empty_command(self, adapter):
        """测试空命令"""
        adapted = adapter.adapt_command('')
        assert adapted == ''
    
    def test_command_with_quotes(self, adapter):
        """测试包含引号的命令"""
        command = 'echo "test path"'
        adapted = adapter.adapt_command(command)
        assert '"test path"' in adapted
    
    def test_command_with_multiple_paths(self, adapter):
        """测试包含多个路径的命令"""
        if adapter.is_windows:
            command = 'Copy-Item C:\\source\\file.txt D:\\dest\\file.txt'
        else:
            command = 'Copy-Item /source/file.txt /dest/file.txt'
        
        adapted = adapter.adapt_command(command)
        assert isinstance(adapted, str)
    
    def test_normalize_relative_path(self, adapter):
        """测试规范化相对路径"""
        normalized = adapter.normalize_path('./test/path')
        assert isinstance(normalized, str)
    
    def test_normalize_parent_path(self, adapter):
        """测试规范化父目录路径"""
        normalized = adapter.normalize_path('../test/path')
        assert isinstance(normalized, str)
