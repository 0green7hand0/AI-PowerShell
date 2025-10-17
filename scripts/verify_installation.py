#!/usr/bin/env python3
"""
安装验证脚本
验证所有依赖项是否正确安装
"""

import sys
import importlib
from typing import List, Tuple


def check_module(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """
    检查模块是否可以导入
    
    Args:
        module_name: 要检查的模块名
        package_name: 包名（如果与模块名不同）
    
    Returns:
        (是否成功, 版本信息或错误信息)
    """
    display_name = package_name or module_name
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        return True, f"{display_name}: {version}"
    except ImportError as e:
        return False, f"{display_name}: 未安装 - {str(e)}"
    except Exception as e:
        return False, f"{display_name}: 错误 - {str(e)}"


def main():
    """主函数"""
    print("=" * 60)
    print("AI PowerShell 智能助手 - 安装验证")
    print("=" * 60)
    print()
    
    # 核心依赖
    core_deps = [
        ("yaml", "PyYAML"),
        ("pydantic", "pydantic"),
        ("structlog", "structlog"),
    ]
    
    # UI 依赖
    ui_deps = [
        ("rich", "rich"),
        ("click", "click"),
        ("prompt_toolkit", "prompt-toolkit"),
        ("colorama", "colorama"),
    ]
    
    # AI 依赖（可选）
    ai_deps = [
        ("ollama", "ollama"),
    ]
    
    # Docker 依赖（可选）
    docker_deps = [
        ("docker", "docker"),
    ]
    
    # 测试依赖（开发环境）
    test_deps = [
        ("pytest", "pytest"),
        ("pytest_cov", "pytest-cov"),
        ("pytest_asyncio", "pytest-asyncio"),
    ]
    
    # 代码质量工具（开发环境）
    dev_deps = [
        ("black", "black"),
        ("flake8", "flake8"),
        ("mypy", "mypy"),
    ]
    
    all_results: List[Tuple[str, bool, str]] = []
    
    # 检查核心依赖
    print("核心依赖:")
    print("-" * 60)
    for module, package in core_deps:
        success, message = check_module(module, package)
        all_results.append(("核心", success, message))
        status = "✓" if success else "✗"
        print(f"  {status} {message}")
    print()
    
    # 检查 UI 依赖
    print("UI 依赖:")
    print("-" * 60)
    for module, package in ui_deps:
        success, message = check_module(module, package)
        all_results.append(("UI", success, message))
        status = "✓" if success else "✗"
        print(f"  {status} {message}")
    print()
    
    # 检查 AI 依赖
    print("AI 依赖 (可选):")
    print("-" * 60)
    for module, package in ai_deps:
        success, message = check_module(module, package)
        all_results.append(("AI", success, message))
        status = "✓" if success else "⚠"
        print(f"  {status} {message}")
    print()
    
    # 检查 Docker 依赖
    print("Docker 依赖 (可选):")
    print("-" * 60)
    for module, package in docker_deps:
        success, message = check_module(module, package)
        all_results.append(("Docker", success, message))
        status = "✓" if success else "⚠"
        print(f"  {status} {message}")
    print()
    
    # 检查测试依赖
    print("测试依赖 (开发环境):")
    print("-" * 60)
    for module, package in test_deps:
        success, message = check_module(module, package)
        all_results.append(("测试", success, message))
        status = "✓" if success else "⚠"
        print(f"  {status} {message}")
    print()
    
    # 检查开发工具
    print("开发工具 (开发环境):")
    print("-" * 60)
    for module, package in dev_deps:
        success, message = check_module(module, package)
        all_results.append(("开发", success, message))
        status = "✓" if success else "⚠"
        print(f"  {status} {message}")
    print()
    
    # 统计结果
    print("=" * 60)
    print("验证摘要:")
    print("-" * 60)
    
    core_success = sum(1 for cat, success, _ in all_results if cat == "核心" and success)
    core_total = sum(1 for cat, _, _ in all_results if cat == "核心")
    
    ui_success = sum(1 for cat, success, _ in all_results if cat == "UI" and success)
    ui_total = sum(1 for cat, _, _ in all_results if cat == "UI")
    
    ai_success = sum(1 for cat, success, _ in all_results if cat == "AI" and success)
    ai_total = sum(1 for cat, _, _ in all_results if cat == "AI")
    
    docker_success = sum(1 for cat, success, _ in all_results if cat == "Docker" and success)
    docker_total = sum(1 for cat, _, _ in all_results if cat == "Docker")
    
    test_success = sum(1 for cat, success, _ in all_results if cat == "测试" and success)
    test_total = sum(1 for cat, _, _ in all_results if cat == "测试")
    
    dev_success = sum(1 for cat, success, _ in all_results if cat == "开发" and success)
    dev_total = sum(1 for cat, _, _ in all_results if cat == "开发")
    
    print(f"核心依赖: {core_success}/{core_total}")
    print(f"UI 依赖: {ui_success}/{ui_total}")
    print(f"AI 依赖: {ai_success}/{ai_total} (可选)")
    print(f"Docker 依赖: {docker_success}/{docker_total} (可选)")
    print(f"测试依赖: {test_success}/{test_total} (开发)")
    print(f"开发工具: {dev_success}/{dev_total} (开发)")
    print()
    
    # 检查 Python 版本
    print("Python 版本:")
    print("-" * 60)
    py_version = sys.version_info
    print(f"  当前版本: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version >= (3, 8):
        print("  ✓ Python 版本满足要求 (>= 3.8)")
    else:
        print("  ✗ Python 版本过低，需要 >= 3.8")
    print()
    
    # 最终结果
    print("=" * 60)
    
    # 核心和 UI 依赖必须全部安装
    required_success = core_success == core_total and ui_success == ui_total
    
    if required_success and py_version >= (3, 8):
        print("✓ 安装验证通过！")
        print()
        print("您可以运行以下命令启动应用：")
        print("  python src/main.py")
        print("  python src/main.py --interactive")
        print()
        if ai_success < ai_total:
            print("注意: AI 功能需要安装 ollama 或其他 AI 提供商")
        if docker_success < docker_total:
            print("注意: 沙箱执行功能需要安装 Docker")
        return 0
    else:
        print("✗ 安装验证失败！")
        print()
        print("请安装缺失的依赖：")
        print("  pip install -r requirements.txt")
        print()
        if test_success < test_total or dev_success < dev_total:
            print("开发环境还需要安装：")
            print("  pip install -r requirements-dev.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
