#!/usr/bin/env python3
"""Test Ollama integration"""

import requests
import json

def test_ollama():
    prompt = """你是一个 PowerShell 命令专家。请将中文描述转换为标准的 PowerShell 命令。

用户输入: 在桌面创建一个txt文档

重要规则:
1. 只返回一行 PowerShell 命令，不要有任何解释或说明
2. 必须使用真实存在的 PowerShell cmdlet
3. 命令必须可以直接在 Windows PowerShell 中执行
4. 不要编造不存在的命令

常用 PowerShell 命令参考:
- 创建文件: New-Item
- 创建目录: New-Item -ItemType Directory
- 查看文件: Get-ChildItem

请直接返回 PowerShell 命令:"""

    data = {
        "model": "qwen3:30b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 100
        }
    }
    
    print("Sending request to Ollama...")
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=data,
        timeout=30
    )
    
    result = response.json()
    print(f"\nResponse: {result['response']}")
    print(f"\nCleaned command: {result['response'].strip().split()[0]}")

if __name__ == "__main__":
    test_ollama()
