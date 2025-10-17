#!/usr/bin/env python
"""
AI PowerShell 智能助手启动脚本
"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行主程序
from src.main import main

if __name__ == "__main__":
    main()
