#!/usr/bin/env python3
"""
AI PowerShell Assistant - 集成演示
这个文件展示各组件如何协同工作
"""

import sys
import os
import asyncio
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("🔗 AI PowerShell Assistant 集成演示")
print("=" * 50)

async def demo_integration():
    """演示组件集成工作流程"""
    
    print("\n📋 模拟完整工作流程:")
    
    # 1. 配置加载
    print("\n1️⃣  配置系统初始化...")
    try:
        from config.models import ServerConfig
        config = ServerConfig.create_default()
        print(f"   ✅ 配置加载成功 - 服务端口: {config.server.port}")
    except Exception as e:
        print(f"   ❌ 配置加载失败: {e}")
        return
    
    # 2. 用户输入处理
    print("\n2️⃣  用户输入自然语言...")
    user_input = "显示CPU使用率最高的5个进程"
    session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"   📝 用户输入: {user_input}")
    print(f"   🆔 会话ID: {session_id}")
    
    # 3. MCP请求构建
    print("\n3️⃣  构建MCP请求...")
    try:
        from mcp_server.schemas import NaturalLanguageToolRequest
        request = NaturalLanguageToolRequest(
            input_text=user_input,
            session_id=session_id,
            include_explanation=True,
            include_alternatives=True
        )
        print(f"   ✅ MCP请求构建成功")
        print(f"   📊 请求参数: {request.model_dump()}")
    except Exception as e:
        print(f"   ❌ MCP请求构建失败: {e}")
        return
    
    # 4. AI引擎处理（模拟）
    print("\n4️⃣  AI引擎处理自然语言...")
    try:
        # 模拟AI处理结果
        ai_result = {
            "success": True,
            "original_input": user_input,
            "generated_command": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5",
            "confidence_score": 0.92,
            "explanation": "获取所有进程，按CPU使用率降序排列，选择前5个",
            "alternatives": [
                "Get-Process | Sort-Object CPU -Descending | Format-Table -First 5",
                "Get-Process | Where-Object {$_.CPU -gt 0} | Sort-Object CPU -Descending | Select-Object -First 5"
            ]
        }
        print(f"   ✅ AI处理成功")
        print(f"   💻 生成命令: {ai_result['generated_command']}")
        print(f"   📈 置信度: {ai_result['confidence_score']}")
        print(f"   💡 解释: {ai_result['explanation']}")
    except Exception as e:
        print(f"   ❌ AI处理失败: {e}")
        return
    
    # 5. 安全验证（模拟）
    print("\n5️⃣  安全引擎验证命令...")
    try:
        command = ai_result['generated_command']
        # 模拟安全验证
        security_result = {
            "is_valid": True,
            "risk_level": "LOW",
            "action": "allow",
            "blocked_reasons": [],
            "suggested_alternatives": []
        }
        print(f"   ✅ 安全验证通过")
        print(f"   🛡️  风险等级: {security_result['risk_level']}")
        print(f"   ✅ 操作: {security_result['action']}")
    except Exception as e:
        print(f"   ❌ 安全验证失败: {e}")
        return
    
    # 6. 命令执行（模拟）
    print("\n6️⃣  执行引擎运行PowerShell...")
    try:
        # 模拟命令执行结果
        execution_result = {
            "success": True,
            "return_code": 0,
            "stdout": "ProcessName    CPU    WorkingSet\n-----------    ---    ----------\nchrome         45.2   234567890\nfirefox        23.1   156789012\nvscode         12.8   98765432\noutlook        8.5    87654321\nteams          6.2    76543210",
            "stderr": "",
            "execution_time": 1.23,
            "platform": "Windows",
            "sandbox_used": True
        }
        print(f"   ✅ 命令执行成功")
        print(f"   ⏱️  执行时间: {execution_result['execution_time']}秒")
        print(f"   🐳 沙箱执行: {execution_result['sandbox_used']}")
        print(f"   📤 输出预览:")
        for line in execution_result['stdout'].split('\n')[:3]:
            print(f"      {line}")
    except Exception as e:
        print(f"   ❌ 命令执行失败: {e}")
        return
    
    # 7. 日志记录（模拟）
    print("\n7️⃣  日志引擎记录审计信息...")
    try:
        correlation_id = f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        audit_log = {
            "timestamp": datetime.now().isoformat(),
            "correlation_id": correlation_id,
            "session_id": session_id,
            "user_input": user_input,
            "generated_command": ai_result['generated_command'],
            "security_validation": security_result,
            "execution_result": execution_result,
            "processing_time_ms": 1250
        }
        print(f"   ✅ 审计日志记录成功")
        print(f"   🔗 关联ID: {correlation_id}")
        print(f"   ⏱️  总处理时间: {audit_log['processing_time_ms']}ms")
    except Exception as e:
        print(f"   ❌ 日志记录失败: {e}")
        return
    
    # 8. 响应构建
    print("\n8️⃣  构建最终响应...")
    try:
        from mcp_server.schemas import NaturalLanguageToolResponse
        response = NaturalLanguageToolResponse(
            success=True,
            original_input=ai_result['original_input'],
            generated_command=ai_result['generated_command'],
            confidence_score=ai_result['confidence_score'],
            explanation=ai_result['explanation'],
            alternatives=ai_result['alternatives'],
            session_id=session_id,
            correlation_id=correlation_id,
            processing_time_ms=audit_log['processing_time_ms']
        )
        print(f"   ✅ 响应构建成功")
        print(f"   📦 响应大小: {len(str(response.model_dump()))} 字符")
    except Exception as e:
        print(f"   ❌ 响应构建失败: {e}")
        return
    
    print("\n🎉 完整工作流程演示完成!")
    print("\n📊 流程总结:")
    print("   用户输入 → AI翻译 → 安全验证 → 命令执行 → 日志记录 → 响应返回")
    print("\n🔍 关键特性:")
    print("   ✅ 自然语言理解")
    print("   ✅ 三层安全保护")
    print("   ✅ 沙箱安全执行")
    print("   ✅ 全程审计跟踪")
    print("   ✅ 跨平台兼容")

def demo_project_structure():
    """演示项目结构和文件组织"""
    print("\n📁 项目结构解析:")
    print("=" * 30)
    
    structure = {
        "src/": "源代码目录",
        "├── interfaces/": "基础接口定义",
        "├── mcp_server/": "MCP服务器核心",
        "├── ai_engine/": "AI处理引擎",
        "├── security/": "安全验证系统",
        "├── execution/": "PowerShell执行",
        "├── log_engine/": "日志审计系统",
        "├── storage/": "数据存储系统",
        "├── context/": "上下文管理",
        "└── config/": "配置管理",
        "docs/": "完整文档",
        "├── api/": "API参考文档",
        "├── user/": "用户使用指南",
        "├── developer/": "开发者指南",
        "└── troubleshooting/": "故障排除",
        "k8s/": "Kubernetes部署配置",
        "scripts/": "部署和管理脚本",
        "config/": "配置模板",
        "tests/": "测试代码（在src/中）"
    }
    
    for path, description in structure.items():
        print(f"{path:<20} {description}")

if __name__ == "__main__":
    print("🚀 开始集成演示...")
    
    # 运行异步演示
    asyncio.run(demo_integration())
    
    # 显示项目结构
    demo_project_structure()
    
    print("\n📚 学习建议:")
    print("1. 运行这个演示了解完整流程")
    print("2. 查看 src/main_integration.py 了解真实集成代码")
    print("3. 运行测试文件验证各组件功能")
    print("4. 启动完整服务进行实际测试")
    print("5. 查看文档深入了解每个组件")