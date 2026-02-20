"""
命令翻译准确率测试

测试系统将中文自然语言翻译成PowerShell命令的准确率。
包含100个多样化场景，覆盖不同复杂度和类型的命令。
"""

import pytest
import time
import statistics
from pathlib import Path
from typing import List, Dict, Tuple

from src.main import PowerShellAssistant
from src.interfaces.base import Suggestion, Context


class TestCommandTranslationAccuracy:
    """命令翻译准确率测试"""
    
    @pytest.fixture
    def assistant(self, tmp_path):
        """创建测试助手"""
        config_file = tmp_path / "accuracy_config.yaml"
        config_content = """
ai:
  provider: "local"
  model_name: "test"
  temperature: 0.7
  max_tokens: 512
  cache_enabled: true

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "WARNING"
  file: "logs/accuracy_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/accuracy"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    @pytest.fixture
    def assistant_with_mock_ai(self, tmp_path):
        """创建使用模拟AI提供商的测试助手"""
        config_file = tmp_path / "mock_ai_config.yaml"
        config_content = """
ai:
  provider: "mock"
  model_name: "test"
  temperature: 0.7
  max_tokens: 512
  cache_enabled: true
  use_ai_provider: true

security:
  sandbox_enabled: false
  require_confirmation: false
  whitelist_mode: "permissive"

execution:
  timeout: 30
  encoding: "utf-8"
  platform: "auto"

logging:
  level: "WARNING"
  file: "logs/mock_ai_test.log"

storage:
  storage_type: "file"
  base_path: "test_data/mock_ai"

context:
  max_history: 100
"""
        config_file.write_text(config_content, encoding='utf-8')
        return PowerShellAssistant(config_path=str(config_file))
    
    def get_test_cases(self) -> List[Dict[str, str]]:
        """获取测试用例集合（100个多样化场景）"""
        return [
            # 基础命令类（10个）
            {"input": "显示当前时间", "expected_pattern": "Get-Date"},
            {"input": "查看当前目录", "expected_pattern": "Get-Location|pwd"},
            {"input": "列出所有文件", "expected_pattern": "Get-ChildItem|ls|dir"},
            {"input": "显示系统信息", "expected_pattern": "systeminfo|Get-ComputerInfo"},
            {"input": "查看IP地址", "expected_pattern": "Get-NetIPAddress|ipconfig"},
            {"input": "显示进程列表", "expected_pattern": "Get-Process|ps"},
            {"input": "查看服务状态", "expected_pattern": "Get-Service"},
            {"input": "显示环境变量", "expected_pattern": "Get-ChildItem.*env:"},
            {"input": "查看磁盘空间", "expected_pattern": "Get-Volume|Get-WmiObject.*Win32_LogicalDisk"},
            {"input": "查看内存使用情况", "expected_pattern": "Get-Counter.*Memory|Get-WmiObject.*Win32_OperatingSystem"},
            
            # 文件操作类（15个）
            {"input": "创建新文件", "expected_pattern": "New-Item.*-ItemType File"},
            {"input": "创建新文件夹", "expected_pattern": "New-Item.*-ItemType Directory|mkdir"},
            {"input": "复制文件", "expected_pattern": "Copy-Item"},
            {"input": "移动文件", "expected_pattern": "Move-Item"},
            {"input": "重命名文件", "expected_pattern": "Rename-Item"},
            {"input": "删除文件", "expected_pattern": "Remove-Item"},
            {"input": "读取文件内容", "expected_pattern": "Get-Content|cat"},
            {"input": "写入文件内容", "expected_pattern": "Set-Content|Add-Content"},
            {"input": "查找包含特定文本的文件", "expected_pattern": "Select-String|Get-ChildItem.*-Recurse.*Select-String"},
            {"input": "批量重命名文件", "expected_pattern": "Rename-Item.*ForEach-Object"},
            {"input": "计算文件哈希值", "expected_pattern": "Get-FileHash"},
            {"input": "压缩文件", "expected_pattern": "Compress-Archive"},
            {"input": "解压缩文件", "expected_pattern": "Expand-Archive"},
            {"input": "查看文件属性", "expected_pattern": "Get-ItemProperty|Get-ChildItem.*-Force"},
            {"input": "设置文件权限", "expected_pattern": "Set-Acl"},
            
            # 进程管理类（10个）
            {"input": "启动新进程", "expected_pattern": "Start-Process"},
            {"input": "停止进程", "expected_pattern": "Stop-Process"},
            {"input": "杀死进程", "expected_pattern": "Stop-Process.*-Force"},
            {"input": "查看进程详细信息", "expected_pattern": "Get-Process.*Select-Object"},
            {"input": "查找特定进程", "expected_pattern": "Get-Process.*Where-Object"},
            {"input": "监控进程CPU使用", "expected_pattern": "Get-Counter.*Process"},
            {"input": "设置进程优先级", "expected_pattern": "Get-Process.*PriorityClass"},
            {"input": "列出所有运行中的进程", "expected_pattern": "Get-Process"},
            {"input": "查看进程启动时间", "expected_pattern": "Get-Process.*StartTime"},
            {"input": "结束所有指定名称的进程", "expected_pattern": "Get-Process.*Stop-Process"},
            
            # 服务管理类（8个）
            {"input": "启动服务", "expected_pattern": "Start-Service"},
            {"input": "停止服务", "expected_pattern": "Stop-Service"},
            {"input": "重启服务", "expected_pattern": "Restart-Service"},
            {"input": "设置服务自动启动", "expected_pattern": "Set-Service.*-StartupType Automatic"},
            {"input": "查看服务依赖关系", "expected_pattern": "Get-Service.*-DependentServices|Get-Service.*-RequiredServices"},
            {"input": "查找特定服务", "expected_pattern": "Get-Service.*Where-Object"},
            {"input": "查看服务状态变化", "expected_pattern": "Get-Service.*-Include*"},
            {"input": "创建新服务", "expected_pattern": "New-Service"},
            
            # 网络操作类（12个）
            {"input": "测试网络连接", "expected_pattern": "Test-Connection|ping"},
            {"input": "查看网络适配器", "expected_pattern": "Get-NetAdapter"},
            {"input": "查看网络连接", "expected_pattern": "Get-NetTCPConnection|netstat"},
            {"input": "查看路由表", "expected_pattern": "Get-NetRoute|route print"},
            {"input": "释放IP地址", "expected_pattern": "ipconfig.*-release"},
            {"input": "续订IP地址", "expected_pattern": "ipconfig.*-renew"},
            {"input": "清除DNS缓存", "expected_pattern": "ipconfig.*-flushdns"},
            {"input": "测试端口连接", "expected_pattern": "Test-NetConnection|New-Object.*System.Net.Sockets.TcpClient"},
            {"input": "下载文件", "expected_pattern": "Invoke-WebRequest|iwr|curl|wget"},
            {"input": "上传文件", "expected_pattern": "Invoke-WebRequest.*-Method POST"},
            {"input": "查看DNS服务器", "expected_pattern": "Get-NetDNSClientServerAddress"},
            {"input": "设置网络代理", "expected_pattern": "Set-ItemProperty.*ProxyServer"},
            
            # 系统管理类（10个）
            {"input": "查看系统版本", "expected_pattern": "Get-WmiObject.*Win32_OperatingSystem|$PSVersionTable"},
            {"input": "查看系统启动时间", "expected_pattern": "Get-WmiObject.*Win32_OperatingSystem.*LastBootUpTime"},
            {"input": "查看系统启动项", "expected_pattern": "Get-CimInstance.*Win32_StartupCommand|Get-ItemProperty.*Run"},
            {"input": "查看已安装的程序", "expected_pattern": "Get-WmiObject.*Win32_Product|Get-ItemProperty.*Uninstall"},
            {"input": "查看系统事件日志", "expected_pattern": "Get-EventLog|Get-WinEvent"},
            {"input": "查看系统错误日志", "expected_pattern": "Get-EventLog.*-EntryType Error|Get-WinEvent.*Error"},
            {"input": "查看系统警告日志", "expected_pattern": "Get-EventLog.*-EntryType Warning|Get-WinEvent.*Warning"},
            {"input": "查看系统更新历史", "expected_pattern": "Get-HotFix|Get-WindowsUpdateLog"},
            {"input": "查看系统启动过程", "expected_pattern": "Get-WinEvent.*Boot"},
            {"input": "查看系统性能计数器", "expected_pattern": "Get-Counter"},
            
            # 脚本和编程类（8个）
            {"input": "创建简单脚本", "expected_pattern": "New-Item.*\.ps1"},
            {"input": "执行PowerShell脚本", "expected_pattern": "&.*\.ps1|Invoke-Expression"},
            {"input": "查看脚本执行策略", "expected_pattern": "Get-ExecutionPolicy"},
            {"input": "设置脚本执行策略", "expected_pattern": "Set-ExecutionPolicy"},
            {"input": "创建函数", "expected_pattern": "function.*{"},
            {"input": "创建变量", "expected_pattern": "\\$.*=.*"},
            {"input": "使用条件语句", "expected_pattern": "if.*{"},
            {"input": "使用循环语句", "expected_pattern": "for.*{|foreach.*{|while.*{|do.*while"},
            
            # 安全类（7个）
            {"input": "查看当前用户", "expected_pattern": "whoami|Get-WmiObject.*Win32_ComputerSystem"},
            {"input": "查看用户权限", "expected_pattern": "Get-Member|Get-Acl"},
            {"input": "查看用户组", "expected_pattern": "Get-LocalGroup|Get-WmiObject.*Win32_Group"},
            {"input": "查看登录历史", "expected_pattern": "Get-EventLog.*Security.*4624|Get-WinEvent.*4624"},
            {"input": "查看锁定的用户", "expected_pattern": "Search-ADAccount.*-LockedOut"},
            {"input": "重置用户密码", "expected_pattern": "Set-LocalUser.*-Password"},
            {"input": "查看防火墙状态", "expected_pattern": "Get-NetFirewallProfile"},
            
            # 任务调度类（5个）
            {"input": "创建定时任务", "expected_pattern": "New-ScheduledTask"},
            {"input": "查看定时任务", "expected_pattern": "Get-ScheduledTask"},
            {"input": "启动定时任务", "expected_pattern": "Start-ScheduledTask"},
            {"input": "停止定时任务", "expected_pattern": "Stop-ScheduledTask"},
            {"input": "删除定时任务", "expected_pattern": "Unregister-ScheduledTask"},
            
            # 高级操作类（9个）
            {"input": "批量处理文件", "expected_pattern": "Get-ChildItem.*ForEach-Object"},
            {"input": "数据导出到CSV", "expected_pattern": "Export-Csv"},
            {"input": "从CSV导入数据", "expected_pattern": "Import-Csv"},
            {"input": "XML文件操作", "expected_pattern": "Get-Content.*Select-Xml"},
            {"input": "JSON文件操作", "expected_pattern": "ConvertFrom-Json|ConvertTo-Json"},
            {"input": "注册表操作", "expected_pattern": "Get-Item|Set-Item.*HKLM:|HKCU:"},
            {"input": "WMI查询", "expected_pattern": "Get-WmiObject|Get-CimInstance"},
            {"input": "事件监控", "expected_pattern": "Register-WmiEvent|Register-ObjectEvent"},
            {"input": "远程执行命令", "expected_pattern": "Invoke-Command.*-ComputerName"},
            
            # 其他类（8个）
            {"input": "查看PowerShell版本", "expected_pattern": "$PSVersionTable|Get-Host"},
            {"input": "获取帮助信息", "expected_pattern": "Get-Help"},
            {"input": "更新帮助文件", "expected_pattern": "Update-Help"},
            {"input": "查看历史命令", "expected_pattern": "Get-History"},
            {"input": "清除历史命令", "expected_pattern": "Clear-History"},
            {"input": "设置别名", "expected_pattern": "New-Alias"},
            {"input": "查看别名", "expected_pattern": "Get-Alias"},
            {"input": "清除屏幕", "expected_pattern": "Clear-Host|cls"}
        ]
    
    def test_command_translation_accuracy(self, assistant):
        """测试命令翻译准确率"""
        test_cases = self.get_test_cases()
        context = assistant._build_context()
        
        correct_count = 0
        total_count = len(test_cases)
        latencies = []
        failures = []
        
        print(f"\n命令翻译准确率测试: {total_count} 个场景")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            user_input = test_case["input"]
            expected_pattern = test_case["expected_pattern"]
            
            # 测量翻译时间
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            latency = time.time() - start_time
            latencies.append(latency)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            generated_command = suggestion.generated_command
            
            # 检查命令是否符合预期模式
            import re
            is_correct = False
            if generated_command:
                is_correct = bool(re.search(expected_pattern, generated_command, re.IGNORECASE))
            
            if is_correct:
                correct_count += 1
                status = "✓"
            else:
                status = "✗"
                failures.append({
                    "input": user_input,
                    "expected": expected_pattern,
                    "generated": generated_command
                })
            
            # 每10个测试打印一次进度
            if i % 10 == 0:
                current_accuracy = (correct_count / i) * 100
                print(f"测试 {i}/{total_count}: {status} '{user_input}' -> '{generated_command}'")
                print(f"当前准确率: {current_accuracy:.2f}%")
                print("-" * 80)
        
        # 计算最终准确率
        accuracy = (correct_count / total_count) * 100
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        print("\n" + "=" * 80)
        print(f"测试完成: {correct_count}/{total_count} 正确")
        print(f"最终准确率: {accuracy:.2f}%")
        print(f"平均响应时间: {avg_latency*1000:.2f}ms")
        
        # 打印失败的测试用例
        if failures:
            print(f"\n失败的测试用例 ({len(failures)}):")
            for failure in failures[:5]:  # 只显示前5个失败
                print(f"  输入: '{failure['input']}'")
                print(f"  期望: '{failure['expected']}'")
                print(f"  生成: '{failure['generated']}'")
                print()
            if len(failures) > 5:
                print(f"  ... 还有 {len(failures) - 5} 个失败用例")
        
        # 性能断言：准确率要求 ≥ 92%
        assert accuracy >= 92.0, f"翻译准确率 {accuracy:.2f}% 低于要求的 92%"
        
        # 性能断言：平均响应时间 < 2秒
        assert avg_latency < 2.0, f"平均响应时间 {avg_latency:.3f}s 超过要求的 2秒"
    
    def test_ai_generated_commands(self, assistant_with_mock_ai):
        """测试AI生成的命令"""
        # 使用模拟AI提供商进行测试
        assistant = assistant_with_mock_ai
        
        # 选择一些更复杂的测试用例，这些用例更可能需要AI模型来生成
        ai_test_cases = [
            # 复杂的文件操作
            {"input": "创建一个名为test的文件夹，然后在里面创建一个名为data.txt的文件，写入'hello world'", "expected_pattern": "New-Item"},
            {"input": "查找所有扩展名为.log的文件，按修改时间排序，显示最近5个", "expected_pattern": "Get-ChildItem"},
            {"input": "复制C盘根目录下所有txt文件到D盘backup文件夹", "expected_pattern": "Copy-Item|Get-ChildItem"},
            
            # 复杂的进程管理
            {"input": "查找CPU使用率超过50%的进程，显示进程名和PID", "expected_pattern": "Get-Process"},
            {"input": "停止所有名为notepad的进程", "expected_pattern": "Get-Process|Stop-Process"},
            
            # 复杂的网络操作
            {"input": "测试到百度的网络连接，显示详细信息", "expected_pattern": "Test-Connection|Test-NetConnection"},
            {"input": "下载百度首页到本地文件index.html", "expected_pattern": "Invoke-WebRequest|Get-ChildItem"},
            
            # 复杂的系统管理
            {"input": "查看系统最近10个错误事件", "expected_pattern": "Get-EventLog|Get-WinEvent"},
            {"input": "查看已安装的所有Microsoft软件", "expected_pattern": "Get-WmiObject|Get-ChildItem"},
            
            # 复杂的脚本和编程
            {"input": "创建一个函数，接受两个参数，返回它们的和", "expected_pattern": "function"},
            {"input": "使用循环创建10个文件夹，命名为folder1到folder10", "expected_pattern": "New-Item|for|foreach"},
        ]
        
        context = assistant._build_context()
        
        correct_count = 0
        total_count = len(ai_test_cases)
        latencies = []
        failures = []
        
        print(f"\nAI生成命令测试: {total_count} 个复杂场景")
        print("=" * 80)
        
        for i, test_case in enumerate(ai_test_cases, 1):
            user_input = test_case["input"]
            expected_pattern = test_case["expected_pattern"]
            
            # 测量翻译时间
            start_time = time.time()
            suggestion = assistant.ai_engine.translate_natural_language(user_input, context)
            latency = time.time() - start_time
            latencies.append(latency)
            
            # 验证结果
            assert isinstance(suggestion, Suggestion)
            generated_command = suggestion.generated_command
            
            # 检查命令是否符合预期模式
            import re
            is_correct = False
            if generated_command:
                is_correct = bool(re.search(expected_pattern, generated_command, re.IGNORECASE))
            
            if is_correct:
                correct_count += 1
                status = "✓"
            else:
                status = "✗"
                failures.append({
                    "input": user_input,
                    "expected": expected_pattern,
                    "generated": generated_command
                })
            
            print(f"测试 {i}/{total_count}: {status} '{user_input}' -> '{generated_command}'")
            print(f"响应时间: {latency*1000:.2f}ms")
            print("-" * 80)
        
        # 计算最终准确率
        accuracy = (correct_count / total_count) * 100
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        print("\n" + "=" * 80)
        print(f"AI生成命令测试完成: {correct_count}/{total_count} 正确")
        print(f"最终准确率: {accuracy:.2f}%")
        print(f"平均响应时间: {avg_latency*1000:.2f}ms")
        
        # 打印失败的测试用例
        if failures:
            print(f"\n失败的测试用例 ({len(failures)}):")
            for failure in failures:
                print(f"  输入: '{failure['input']}'")
                print(f"  期望: '{failure['expected']}'")
                print(f"  生成: '{failure['generated']}'")
                print()
        
        # 性能断言：AI生成命令的准确率要求 ≥ 60%（使用模拟提供商）
        assert accuracy >= 60.0, f"AI生成命令准确率 {accuracy:.2f}% 低于要求的 60%"
        
        # 性能断言：平均响应时间 < 1秒（模拟提供商应该很快）
        assert avg_latency < 1.0, f"AI生成命令平均响应时间 {avg_latency:.3f}s 超过要求的 1秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
