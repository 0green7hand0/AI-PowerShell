#!/usr/bin/env python3
"""
AI PowerShell Assistant - 组件导览
这个文件带你了解项目的各个核心组件
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("🏗️  AI PowerShell Assistant 组件导览")
print("=" * 50)

# 1. AI引擎组件
print("\n🤖 1. AI引擎 (src/ai_engine/)")
print("   作用: 将自然语言转换为PowerShell命令")
print("   核心文件:")
print("   - engine.py: AI引擎主类")
print("   - providers.py: 不同AI模型提供者")
print("   - translation.py: 翻译逻辑")
print("   - error_detection.py: 错误检测")

try:
    from ai_engine.engine import AIEngine
    print("   ✅ AI引擎模块加载成功")
except ImportError as e:
    print(f"   ❌ AI引擎模块加载失败: {e}")

# 2. 安全引擎组件
print("\n🔒 2. 安全引擎 (src/security/)")
print("   作用: 三层安全验证保护系统")
print("   核心文件:")
print("   - engine.py: 安全引擎主类")
print("   - whitelist.py: 命令白名单验证")
print("   - permissions.py: 权限检查")
print("   - confirmation.py: 用户确认机制")
print("   - sandbox.py: Docker沙箱执行")

try:
    from security.engine import SecurityEngine
    print("   ✅ 安全引擎模块加载成功")
except ImportError as e:
    print(f"   ❌ 安全引擎模块加载失败: {e}")

# 3. 执行引擎组件
print("\n⚡ 3. 执行引擎 (src/execution/)")
print("   作用: 跨平台PowerShell命令执行")
print("   核心文件:")
print("   - executor.py: 命令执行器")
print("   - platform_adapter.py: 平台适配")
print("   - output_formatter.py: 输出格式化")

try:
    from execution.executor import PowerShellExecutor
    print("   ✅ 执行引擎模块加载成功")
except ImportError as e:
    print(f"   ❌ 执行引擎模块加载失败: {e}")

# 4. MCP服务器组件
print("\n🌐 4. MCP服务器 (src/mcp_server/)")
print("   作用: 基于FastMCP的API服务器")
print("   核心文件:")
print("   - server.py: MCP服务器主类")
print("   - schemas.py: 请求/响应数据模型")
print("   - discovery.py: 工具发现和注册")

try:
    from mcp_server.server import PowerShellAssistantMCP
    print("   ✅ MCP服务器模块加载成功")
except ImportError as e:
    print(f"   ❌ MCP服务器模块加载失败: {e}")

# 5. 日志引擎组件
print("\n📊 5. 日志引擎 (src/log_engine/)")
print("   作用: 全面的审计跟踪和性能监控")
print("   核心文件:")
print("   - engine.py: 日志引擎主类")
print("   - filters.py: 日志过滤器")
print("   - decorators.py: 日志装饰器")

try:
    from log_engine.engine import LoggingEngine
    print("   ✅ 日志引擎模块加载成功")
except ImportError as e:
    print(f"   ❌ 日志引擎模块加载失败: {e}")

# 6. 存储引擎组件
print("\n💾 6. 存储引擎 (src/storage/)")
print("   作用: 配置和数据持久化")
print("   核心文件:")
print("   - file_storage.py: 文件存储实现")
print("   - interfaces.py: 存储接口定义")
print("   - migration.py: 数据迁移")

try:
    from storage.file_storage import FileStorage
    print("   ✅ 存储引擎模块加载成功")
except ImportError as e:
    print(f"   ❌ 存储引擎模块加载失败: {e}")

# 7. 上下文管理组件
print("\n🧠 7. 上下文管理 (src/context/)")
print("   作用: 会话和历史记录管理")
print("   核心文件:")
print("   - manager.py: 上下文管理器")
print("   - history.py: 历史记录")
print("   - models.py: 数据模型")

try:
    from context.manager import ContextManager
    print("   ✅ 上下文管理模块加载成功")
except ImportError as e:
    print(f"   ❌ 上下文管理模块加载失败: {e}")

print("\n🔄 组件交互流程:")
print("1. MCP服务器接收请求")
print("2. AI引擎处理自然语言")
print("3. 安全引擎验证命令")
print("4. 执行引擎运行PowerShell")
print("5. 日志引擎记录全过程")
print("6. 存储引擎保存数据")
print("7. 上下文管理维护会话")

print("\n📖 下一步学习建议:")
print("1. 查看 src/interfaces/base.py 了解组件间的接口")
print("2. 运行 learning/03_integration_demo.py 看组件如何协作")
print("3. 查看测试文件了解每个组件的具体功能")
print("4. 运行完整系统进行实际体验")