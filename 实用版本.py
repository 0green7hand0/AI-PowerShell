#!/usr/bin/env python3
"""
AI PowerShell 助手 - 实用版本
专注于实际使用，简化复杂性
"""

import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    command: str
    output: str
    error: str
    return_code: int

class SimpleAITranslator:
    """简化的 AI 翻译器 - 基于规则的中文到 PowerShell 转换"""
    
    def __init__(self):
        self.translation_rules = {
            # 文件和目录操作
            r"(显示|列出|查看).*(当前|现在).*(目录|文件夹).*文件": "Get-ChildItem",
            r"(显示|列出|查看).*文件": "Get-ChildItem",
            r"(显示|查看).*(当前|现在).*(目录|位置|路径)": "Get-Location",
            r"(进入|切换|转到).*(目录|文件夹)": "Set-Location",
            
            # 系统信息
            r"(显示|查看|检查).*(时间|日期)": "Get-Date",
            r"(显示|查看|检查).*PowerShell.*版本": "$PSVersionTable",
            r"(显示|查看|列出).*(进程|任务)": "Get-Process",
            r"(显示|查看|列出).*服务": "Get-Service",
            r"(显示|查看|检查).*(内存|RAM)": "Get-WmiObject -Class Win32_PhysicalMemory",
            r"(显示|查看|检查).*(CPU|处理器)": "Get-WmiObject -Class Win32_Processor",
            r"(显示|查看|检查).*(磁盘|硬盘).*空间": "Get-WmiObject -Class Win32_LogicalDisk",
            
            # 网络相关
            r"(测试|检查).*网络.*连接": "Test-NetConnection",
            r"(显示|查看).*IP.*地址": "Get-NetIPAddress",
            r"(显示|查看).*网络.*配置": "Get-NetIPConfiguration",
            
            # 环境变量
            r"(显示|查看|列出).*环境.*变量": "Get-ChildItem Env:",
            r"(显示|查看).*PATH": "echo $env:PATH",
            
            # 系统状态
            r"(显示|查看).*系统.*信息": "Get-ComputerInfo",
            r"(显示|查看).*启动.*时间": "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object LastBootUpTime",
        }
    
    def translate(self, chinese_text: str) -> str:
        """将中文描述转换为 PowerShell 命令"""
        chinese_text = chinese_text.strip()
        
        # 尝试匹配规则
        for pattern, command in self.translation_rules.items():
            if re.search(pattern, chinese_text, re.IGNORECASE):
                return command
        
        # 如果没有匹配，返回提示
        return f"# 未找到匹配的命令，请尝试更具体的描述: {chinese_text}"

class SimpleSecurity:
    """简化的安全验证"""
    
    def __init__(self):
        # 危险命令模式
        self.dangerous_patterns = [
            r"Remove-Item.*-Recurse.*-Force",
            r"Format-Volume",
            r"Remove-Item.*C:\\",
            r"del.*C:\\",
            r"rmdir.*C:\\",
            r"Stop-Computer",
            r"Restart-Computer",
            r"shutdown",
        ]
        
        # 安全命令前缀
        self.safe_prefixes = [
            "Get-", "Show-", "Test-", "Find-", "Select-", "Where-", 
            "$PSVersionTable", "echo", "Write-"
        ]
    
    def is_safe(self, command: str) -> tuple[bool, str]:
        """检查命令是否安全"""
        command = command.strip()
        
        # 检查危险模式
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"危险命令被阻止: {pattern}"
        
        # 检查安全前缀
        for prefix in self.safe_prefixes:
            if command.startswith(prefix):
                return True, "安全命令"
        
        # 注释和空命令是安全的
        if command.startswith("#") or not command:
            return True, "注释或空命令"
        
        # 其他命令需要用户确认
        return True, "需要用户确认"

class SimplePowerShellExecutor:
    """简化的 PowerShell 执行器"""
    
    def __init__(self):
        self.powershell_cmd = self._find_powershell()
    
    def _find_powershell(self) -> str:
        """查找可用的 PowerShell"""
        # 尝试 PowerShell Core
        try:
            subprocess.run(['pwsh', '--version'], capture_output=True, check=True)
            return 'pwsh'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # 尝试 Windows PowerShell
        try:
            subprocess.run(['powershell', '-Command', 'echo test'], capture_output=True, check=True)
            return 'powershell'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return None
    
    def execute(self, command: str, timeout: int = 30) -> CommandResult:
        """执行 PowerShell 命令"""
        if not self.powershell_cmd:
            return CommandResult(
                success=False,
                command=command,
                output="",
                error="PowerShell 不可用",
                return_code=-1
            )
        
        try:
            # 构建命令
            full_cmd = [self.powershell_cmd, '-Command', command]
            
            # 执行命令
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='gbk',  # Windows 中文编码
                errors='ignore'  # 忽略编码错误
            )
            
            return CommandResult(
                success=result.returncode == 0,
                command=command,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                command=command,
                output="",
                error=f"命令执行超时 ({timeout}秒)",
                return_code=-1
            )
        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                output="",
                error=f"执行错误: {e}",
                return_code=-1
            )

class PowerShellAssistant:
    """实用的 PowerShell 助手"""
    
    def __init__(self):
        self.translator = SimpleAITranslator()
        self.security = SimpleSecurity()
        self.executor = SimplePowerShellExecutor()
        
        print("🤖 AI PowerShell 助手已启动")
        if self.executor.powershell_cmd:
            print(f"✅ PowerShell 可用: {self.executor.powershell_cmd}")
        else:
            print("❌ PowerShell 不可用，请安装 PowerShell")
    
    def process_request(self, chinese_input: str, auto_execute: bool = False) -> CommandResult:
        """处理中文请求"""
        print(f"\n🗣️  输入: {chinese_input}")
        
        # 1. AI 翻译
        command = self.translator.translate(chinese_input)
        print(f"🤖 翻译: {command}")
        
        # 2. 安全检查
        is_safe, reason = self.security.is_safe(command)
        print(f"🔒 安全检查: {'✅ 通过' if is_safe else '❌ 被阻止'} - {reason}")
        
        if not is_safe:
            return CommandResult(
                success=False,
                command=command,
                output="",
                error=f"命令被安全系统阻止: {reason}",
                return_code=-1
            )
        
        # 3. 执行确认
        if command.startswith("#"):
            print("ℹ️  这是一个注释，跳过执行")
            return CommandResult(
                success=True,
                command=command,
                output=command,
                error="",
                return_code=0
            )
        
        if not auto_execute and not command.startswith(tuple(self.security.safe_prefixes)):
            confirm = input("🤔 是否执行此命令? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', '是']:
                print("⏭️  跳过执行")
                return CommandResult(
                    success=True,
                    command=command,
                    output="用户取消执行",
                    error="",
                    return_code=0
                )
        
        # 4. 执行命令
        print("⚡ 正在执行...")
        result = self.executor.execute(command)
        
        # 5. 显示结果
        if result.success:
            print(f"✅ 执行成功 (返回码: {result.return_code})")
            if result.output:
                output = result.output.strip()
                if len(output) > 500:
                    print(f"📄 输出:\n{output[:500]}...")
                    print("(输出已截断，完整输出请查看返回结果)")
                else:
                    print(f"📄 输出:\n{output}")
        else:
            print(f"❌ 执行失败 (返回码: {result.return_code})")
            if result.error:
                print(f"🚫 错误: {result.error}")
        
        return result
    
    def interactive_mode(self):
        """交互模式"""
        print("\n💬 进入交互模式 (输入 'quit' 退出)")
        print("💡 提示: 输入中文描述，我会转换为 PowerShell 命令并执行")
        
        while True:
            try:
                user_input = input("\n🗣️  请输入: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                self.process_request(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

def main():
    """主函数"""
    print("🚀 AI PowerShell 助手 - 实用版本")
    print("=" * 40)
    
    assistant = PowerShellAssistant()
    
    if len(sys.argv) > 1:
        # 命令行模式
        chinese_input = " ".join(sys.argv[1:])
        assistant.process_request(chinese_input, auto_execute=False)
    else:
        # 交互模式
        assistant.interactive_mode()

if __name__ == "__main__":
    main()