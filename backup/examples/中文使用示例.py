#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI PowerShell 助手中文使用示例

本文件展示如何使用 AI PowerShell 助手进行各种操作，
包括自然语言处理、命令执行和系统管理任务。
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class PowerShellAssistant:
    """AI PowerShell 助手客户端
    
    提供简单易用的接口与 AI PowerShell 助手服务器交互
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """初始化客户端
        
        Args:
            base_url: 服务器基础 URL
        """
        self.base_url = base_url
        self.session_id = f"中文示例_{int(time.time())}"
        print(f"🤖 AI PowerShell 助手客户端已初始化")
        print(f"📡 服务器地址: {base_url}")
        print(f"🆔 会话ID: {self.session_id}")
    
    def 自然语言转换(self, 中文描述: str) -> Dict[str, Any]:
        """将中文自然语言转换为 PowerShell 命令
        
        Args:
            中文描述: 用中文描述想要执行的操作
            
        Returns:
            Dict[str, Any]: 包含生成命令和相关信息的响应
        """
        print(f"\n🔄 正在处理: {中文描述}")
        
        try:
            response = requests.post(
                f"{self.base_url}/natural_language_to_powershell",
                json={
                    "input_text": 中文描述,
                    "session_id": self.session_id,
                    "include_explanation": True,
                    "include_alternatives": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 转换成功!")
                    print(f"💻 生成的命令: {result.get('generated_command')}")
                    print(f"📊 置信度: {result.get('confidence_score', 0):.2%}")
                    print(f"💡 解释: {result.get('explanation')}")
                    
                    alternatives = result.get('alternatives', [])
                    if alternatives:
                        print(f"🔄 替代方案:")
                        for i, alt in enumerate(alternatives[:3], 1):
                            print(f"   {i}. {alt}")
                else:
                    print(f"❌ 转换失败: {result.get('error', '未知错误')}")
                
                return result
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            return {"success": False, "error": str(e)}
    
    def 执行命令(self, 命令: str, 使用沙箱: bool = True) -> Dict[str, Any]:
        """执行 PowerShell 命令
        
        Args:
            命令: 要执行的 PowerShell 命令
            使用沙箱: 是否在沙箱环境中执行
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        print(f"\n⚡ 正在执行命令: {命令}")
        print(f"🛡️ 沙箱模式: {'启用' if 使用沙箱 else '禁用'}")
        
        try:
            response = requests.post(
                f"{self.base_url}/execute_powershell_command",
                json={
                    "command": 命令,
                    "session_id": self.session_id,
                    "use_sandbox": 使用沙箱,
                    "timeout": 60
                },
                timeout=70
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 执行成功!")
                    print(f"⏱️ 执行时间: {result.get('execution_time', 0):.2f} 秒")
                    print(f"🖥️ 平台: {result.get('platform')}")
                    
                    stdout = result.get('stdout', '')
                    if stdout:
                        print(f"📤 输出结果:")
                        # 限制输出长度以便阅读
                        if len(stdout) > 500:
                            print(f"{stdout[:500]}...")
                            print(f"... (输出已截断，共 {len(stdout)} 字符)")
                        else:
                            print(stdout)
                    
                    stderr = result.get('stderr', '')
                    if stderr:
                        print(f"⚠️ 错误信息: {stderr}")
                else:
                    print(f"❌ 执行失败: {result.get('error', '未知错误')}")
                
                return result
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            return {"success": False, "error": str(e)}
    
    def 智能对话(self, 中文描述: str) -> Optional[Dict[str, Any]]:
        """智能对话模式：自动转换并询问是否执行
        
        Args:
            中文描述: 用中文描述想要执行的操作
            
        Returns:
            Optional[Dict[str, Any]]: 执行结果（如果用户选择执行）
        """
        # 1. 先进行自然语言转换
        转换结果 = self.自然语言转换(中文描述)
        
        if not 转换结果.get('success'):
            return None
        
        生成的命令 = 转换结果.get('generated_command')
        置信度 = 转换结果.get('confidence_score', 0)
        
        # 2. 根据置信度和命令类型决定是否需要确认
        需要确认 = True
        if 置信度 > 0.9 and any(生成的命令.startswith(safe) for safe in ['Get-', 'Show-', 'Test-']):
            需要确认 = False
        
        if 需要确认:
            print(f"\n❓ 是否执行此命令？")
            print(f"   命令: {生成的命令}")
            print(f"   置信度: {置信度:.2%}")
            
            while True:
                选择 = input("请选择 (y=执行/n=取消/s=沙箱执行): ").lower().strip()
                if 选择 in ['y', 'yes', '是', '执行']:
                    return self.执行命令(生成的命令, 使用沙箱=False)
                elif 选择 in ['s', 'sandbox', '沙箱']:
                    return self.执行命令(生成的命令, 使用沙箱=True)
                elif 选择 in ['n', 'no', '否', '取消']:
                    print("❌ 用户取消执行")
                    return None
                else:
                    print("请输入 y/n/s")
        else:
            print(f"🚀 高置信度安全命令，自动执行...")
            return self.执行命令(生成的命令, 使用沙箱=True)
    
    def 获取系统信息(self) -> Dict[str, Any]:
        """获取系统信息
        
        Returns:
            Dict[str, Any]: 系统信息
        """
        print(f"\n📊 正在获取系统信息...")
        
        try:
            response = requests.post(
                f"{self.base_url}/get_powershell_info",
                json={
                    "session_id": self.session_id,
                    "include_modules": True,
                    "include_environment": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 系统信息获取成功!")
                    
                    powershell_info = result.get('powershell', {})
                    print(f"🖥️ PowerShell 版本: {powershell_info.get('version')}")
                    print(f"📦 平台: {result.get('platform')}")
                    print(f"🔧 服务器版本: {result.get('server_version')}")
                    
                    modules = result.get('modules', [])
                    if modules:
                        print(f"📚 已加载模块数量: {len(modules)}")
                else:
                    print(f"❌ 获取失败: {result.get('error', '未知错误')}")
                
                return result
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            return {"success": False, "error": str(e)}


def 系统管理示例():
    """系统管理任务示例"""
    print("=" * 60)
    print("🔧 系统管理任务示例")
    print("=" * 60)
    
    助手 = PowerShellAssistant()
    
    # 获取系统信息
    助手.获取系统信息()
    
    # 系统管理任务列表
    管理任务 = [
        "显示CPU使用率最高的5个进程",
        "检查磁盘空间使用情况",
        "列出所有正在运行的Windows服务",
        "显示网络连接状态",
        "查看系统启动时间"
    ]
    
    for 任务 in 管理任务:
        print(f"\n" + "─" * 40)
        助手.智能对话(任务)
        time.sleep(1)  # 避免请求过于频繁


def 文件管理示例():
    """文件管理任务示例"""
    print("=" * 60)
    print("📁 文件管理任务示例")
    print("=" * 60)
    
    助手 = PowerShellAssistant()
    
    文件任务 = [
        "列出当前目录下的所有文件",
        "查找所有.txt文件",
        "显示文件夹大小",
        "检查文件权限",
        "创建一个测试文件夹"
    ]
    
    for 任务 in 文件任务:
        print(f"\n" + "─" * 40)
        助手.智能对话(任务)
        time.sleep(1)


def 网络诊断示例():
    """网络诊断任务示例"""
    print("=" * 60)
    print("🌐 网络诊断任务示例")
    print("=" * 60)
    
    助手 = PowerShellAssistant()
    
    网络任务 = [
        "测试到百度的网络连接",
        "显示本机IP地址",
        "查看网络适配器信息",
        "显示路由表",
        "检查DNS设置"
    ]
    
    for 任务 in 网络任务:
        print(f"\n" + "─" * 40)
        助手.智能对话(任务)
        time.sleep(1)


def 交互式演示():
    """交互式演示模式"""
    print("=" * 60)
    print("🎮 交互式演示模式")
    print("=" * 60)
    print("请用中文描述您想要执行的操作，输入 'quit' 或 '退出' 结束")
    print("示例：'显示所有正在运行的进程'、'检查磁盘空间'等")
    print("=" * 60)
    
    助手 = PowerShellAssistant()
    
    while True:
        try:
            用户输入 = input("\n💬 请描述您的需求: ").strip()
            
            if not 用户输入:
                continue
                
            if 用户输入.lower() in ['quit', 'exit', '退出', '结束']:
                print("👋 感谢使用 AI PowerShell 助手！")
                break
            
            if 用户输入 in ['help', '帮助']:
                print("📖 使用帮助:")
                print("- 用中文描述您想要执行的操作")
                print("- 例如：'显示进程列表'、'检查服务状态'")
                print("- 输入 '退出' 结束程序")
                continue
            
            助手.智能对话(用户输入)
            
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，感谢使用！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    print("🤖 AI PowerShell 助手中文使用示例")
    print("=" * 60)
    
    while True:
        print("\n请选择演示模式:")
        print("1. 系统管理示例")
        print("2. 文件管理示例") 
        print("3. 网络诊断示例")
        print("4. 交互式演示")
        print("5. 退出")
        
        try:
            选择 = input("\n请输入选项 (1-5): ").strip()
            
            if 选择 == '1':
                系统管理示例()
            elif 选择 == '2':
                文件管理示例()
            elif 选择 == '3':
                网络诊断示例()
            elif 选择 == '4':
                交互式演示()
            elif 选择 == '5':
                print("👋 感谢使用 AI PowerShell 助手！")
                break
            else:
                print("❌ 无效选项，请输入 1-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，感谢使用！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")