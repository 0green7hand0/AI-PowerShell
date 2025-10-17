#!/usr/bin/env python3
"""Test backend AI engine"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.main import PowerShellAssistant
from src.interfaces.base import Context

def test_translation():
    print("Initializing PowerShell Assistant...")
    assistant = PowerShellAssistant()
    
    print(f"AI Engine config: {assistant.config.ai}")
    print(f"Provider: {assistant.config.ai.provider}")
    print(f"Model: {assistant.config.ai.model_name}")
    print(f"Use AI Provider: {assistant.config.ai.use_ai_provider}")
    
    # Test translation
    context = Context(
        session_id="test",
        working_directory=os.getcwd(),
        command_history=[]
    )
    
    text = "在桌面创建一个txt文档"
    print(f"\nTranslating: {text}")
    
    suggestion = assistant.ai_engine.translate_natural_language(text, context)
    
    print(f"\nResult:")
    print(f"  Command: {suggestion.generated_command}")
    print(f"  Confidence: {suggestion.confidence_score}")
    print(f"  Explanation: {suggestion.explanation}")

if __name__ == "__main__":
    test_translation()
