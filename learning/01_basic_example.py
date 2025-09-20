#!/usr/bin/env python3
"""
AI PowerShell Assistant - 基础学习示例
这个文件展示了项目的核心概念和基本用法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 1. 基础接口 - 了解项目的核心抽象
from interfaces.base import Platform, OutputFormat, UserRole

print("=== 1. 基础概念演示 ===")
print(f"支持的平台: {[p.value for p in Platform]}")
print(f"输出格式: {[f.value for f in OutputFormat]}")
print(f"用户角色: {[r.value for r in UserRole]}")

# 2. 配置系统 - 了解如何管理配置
from config.models import ServerConfig

print("\n=== 2. 配置系统演示 ===")
try:
    # 创建默认配置
    config = ServerConfig.create_default()
    print(f"默认服务器端口: {config.server.port}")
    print(f"AI模型类型: {config.ai_model.model_type}")
    print(f"安全沙箱启用: {config.security.sandbox_enabled}")
except Exception as e:
    print(f"配置加载失败: {e}")

# 3. MCP服务器架构 - 了解服务器如何工作
from mcp_server.schemas import NaturalLanguageToolRequest, ExecuteCommandToolRequest

print("\n=== 3. MCP工具请求格式演示 ===")

# 自然语言请求示例
nl_request = NaturalLanguageToolRequest(
    input_text="显示所有正在运行的进程",
    session_id="demo_session",
    include_explanation=True
)
print(f"自然语言请求: {nl_request.input_text}")

# 命令执行请求示例
cmd_request = ExecuteCommandToolRequest(
    command="Get-Process",
    session_id="demo_session",
    use_sandbox=True,
    timeout=30
)
print(f"命令执行请求: {cmd_request.command}")

print("\n=== 4. 项目核心流程 ===")
print("1. 用户输入自然语言 -> AI引擎翻译 -> PowerShell命令")
print("2. PowerShell命令 -> 安全验证 -> 沙箱执行 -> 返回结果")
print("3. 全程记录日志 -> 审计跟踪 -> 性能监控")

print("\n=== 学习建议 ===")
print("1. 先运行这个示例了解基本概念")
print("2. 查看 src/interfaces/base.py 了解核心接口")
print("3. 查看 src/mcp_server/server.py 了解服务器架构")
print("4. 查看测试文件了解各组件如何工作")
print("5. 运行完整系统进行实际测试")