#!/usr/bin/env python
"""
AI PowerShell 智能助手启动脚本
"""
import sys
import time
from pathlib import Path
from typing import Dict, Optional

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 颜色输出函数 (PowerShell风格)
def print_success(message: str):
    """打印成功消息 (PowerShell风格)"""
    print(f"\033[92m[+] {message}\033[0m")

def print_error(message: str):
    """打印错误消息 (PowerShell风格)"""
    print(f"\033[91m[-] {message}\033[0m")

def print_warning(message: str):
    """打印警告消息 (PowerShell风格)"""
    print(f"\033[93m[!] {message}\033[0m")

def print_info(message: str):
    """打印信息消息 (PowerShell风格)"""
    print(f"\033[96m[*] {message}\033[0m")

def print_header(message: str):
    """打印标题 (PowerShell风格)"""
    print(f"\033[95m{message}\033[0m")

def print_section(title: str):
    """打印章节标题 (PowerShell风格)"""
    print("\n" + "="*70)
    print(f"\033[95m{title}\033[0m")
    print("="*70)

# 检查本地AI服务
def check_local_ai() -> Dict[str, any]:
    """
    检查本地AI服务可用性
    
    Returns:
        Dict: 包含检查结果的字典
    """
    result = {
        "ollama_available": False,
        "models_available": False,
        "default_model_ready": False,
        "error": None,
        "models": []
    }
    
    try:
        import requests
        
        # 检查Ollama服务
        response = requests.get("http://localhost:11434/api/version", timeout=3)
        response.raise_for_status()
        result["ollama_available"] = True
        
        # 检查模型
        models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models_response.raise_for_status()
        
        models = models_response.json().get("models", [])
        result["models"] = models
        
        if len(models) > 0:
            result["models_available"] = True
            
            # 检查默认模型
            default_model = "qwen3:30b"
            model_exists = any(m.get("name") == default_model for m in models)
            if model_exists:
                result["default_model_ready"] = True
            else:
                result["error"] = f"默认模型 '{default_model}' 未找到"
        else:
            result["error"] = "未安装任何模型"
            
    except ImportError:
        result["error"] = "缺少requests库"
    except requests.ConnectionError:
        result["error"] = "Ollama服务未运行"
    except requests.Timeout:
        result["error"] = "Ollama服务响应超时"
    except Exception as e:
        result["error"] = str(e)
    
    return result

# 主启动函数
def main_with_ai_check():
    """
    带AI服务检查的主启动函数
    """
    # 极简启动信息
    print("AI PowerShell 智能助手 v2.0.0")
    
    # 快速检查AI服务
    ai_check_result = check_local_ai()
    
    # 显示AI模型信息
    if ai_check_result["ollama_available"]:
        if ai_check_result["default_model_ready"]:
            print("AI模型: qwen3:30b (就绪)")
        elif ai_check_result["models_available"]:
            model_count = len(ai_check_result["models"])
            print(f"AI模型: 已安装 {model_count} 个")
    elif ai_check_result["error"]:
        print(f"[!] AI服务: {ai_check_result['error']}")
    
    # 导入并运行主程序
    try:
        # 禁用详细初始化日志
        import os
        os.environ["AI_POWERSHELL_QUIET"] = "1"
        os.environ["LOG_LEVEL"] = "ERROR"  # 只显示错误级别日志
        os.environ["DISABLE_STARTUP_SCREEN"] = "1"  # 禁用启动欢迎屏幕
        
        # 重定向标准输出和标准错误，过滤掉不需要的日志
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        # 创建内存缓冲区
        f = io.StringIO()
        
        # 显示使用提示
        print("\n使用提示:")
        print("  - 输入中文命令描述，如: 显示当前时间")
        print("  - 输入 help 查看帮助信息")
        print("  - 输入 exit 退出程序")
        print("\n示例:")
        print("  - 列出当前目录的所有文件")
        print("  - 查看CPU使用率最高的5个进程")
        print("  - 测试网络连接到 www.baidu.com")
        print()
        
        # 导入主程序模块
        from src.main import PowerShellAssistant
        
        # 创建助手实例（重定向输出）
        with redirect_stdout(f), redirect_stderr(f):
            assistant = PowerShellAssistant()
        
        # 进入交互式模式，处理用户输入
        while True:
            try:
                # 显示输入提示
                user_input = input("💬 请输入 > ").strip()
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', '退出']:
                    print("\n👋 再见！")
                    break
                
                if user_input.lower() in ['help', '帮助']:
                    assistant._show_help()
                    continue
                
                if user_input.lower() in ['history', '历史']:
                    assistant._show_history()
                    continue
                
                if user_input.lower() in ['clear', '清屏']:
                    assistant._clear_screen()
                    continue
                
                # 处理正常请求（重定向输出）
                with redirect_stdout(f), redirect_stderr(f):
                    result = assistant.process_request(user_input, auto_execute=False)
                
                # 显示结果
                assistant._display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 检测到 Ctrl+C，正在退出...")
                break
            except EOFError:
                print("\n\n👋 检测到 EOF，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {str(e)}")
                continue
    except Exception as e:
        print(f"[-] 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main_with_ai_check()
