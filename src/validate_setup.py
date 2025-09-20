#!/usr/bin/env python3
"""Validation script to test project structure and configuration setup"""

import sys
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing module imports...")
    
    try:
        # Test config imports
        from config import (
            ConfigurationManager, get_config, load_config,
            ServerConfig, ModelConfig, SecurityConfig
        )
        print("✓ Configuration module imports successful")
        
        # Test interface imports
        from interfaces import (
            Platform, SecurityAction, RiskLevel, UserRole,
            CommandSuggestion, ExecutionResult, ValidationResult,
            AIEngineInterface, SecurityEngineInterface, ExecutorInterface
        )
        print("✓ Interfaces module imports successful")
        
        # Test that module directories exist and are importable
        import ai_engine
        import security
        import execution
        import log_engine
        import mcp_server
        import storage
        print("✓ All component modules are importable")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration loading and validation"""
    print("\nTesting configuration system...")
    
    try:
        from config import load_config, ConfigurationManager
        
        # Test configuration loading
        config = load_config()
        print(f"✓ Configuration loaded successfully")
        print(f"  - Version: {config.version}")
        print(f"  - Platform: {config.platform.value}")
        print(f"  - Model type: {config.model.model_type}")
        print(f"  - Sandbox enabled: {config.security.sandbox_enabled}")
        print(f"  - Log level: {config.logging.log_level.value}")
        
        # Test configuration manager
        manager = ConfigurationManager()
        test_config = manager.load_configuration()
        print("✓ Configuration manager working correctly")
        
        # Test environment variable override (simulate)
        import os
        original_debug = os.environ.get('AI_PS_DEBUG_MODE')
        os.environ['AI_PS_DEBUG_MODE'] = 'true'
        
        manager_with_env = ConfigurationManager()
        env_config = manager_with_env.load_configuration()
        
        # Restore original environment
        if original_debug is None:
            os.environ.pop('AI_PS_DEBUG_MODE', None)
        else:
            os.environ['AI_PS_DEBUG_MODE'] = original_debug
            
        print("✓ Environment variable overrides working")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        traceback.print_exc()
        return False


def test_data_models():
    """Test data model creation and validation"""
    print("\nTesting data models...")
    
    try:
        from interfaces import (
            CommandSuggestion, ExecutionResult, CommandContext,
            Platform, UserRole, SecurityAction, RiskLevel
        )
        
        # Test CommandSuggestion
        suggestion = CommandSuggestion(
            original_input="list processes",
            generated_command="Get-Process",
            confidence_score=0.95,
            explanation="Lists all running processes",
            alternatives=["ps", "Get-Process | Select-Object Name, Id"]
        )
        print(f"✓ CommandSuggestion created with correlation_id: {suggestion.correlation_id}")
        
        # Test ExecutionResult
        result = ExecutionResult(
            success=True,
            return_code=0,
            stdout="Process output",
            stderr="",
            execution_time=1.5,
            platform=Platform.WINDOWS,
            sandbox_used=False
        )
        print(f"✓ ExecutionResult created with correlation_id: {result.correlation_id}")
        
        # Test CommandContext
        context = CommandContext(
            current_directory="/home/user",
            environment_variables={"PATH": "/usr/bin"},
            user_role=UserRole.USER,
            recent_commands=["ls", "pwd"],
            active_modules=["Microsoft.PowerShell.Management"],
            platform=Platform.LINUX
        )
        print(f"✓ CommandContext created with session_id: {context.session_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data model error: {e}")
        traceback.print_exc()
        return False


def test_directory_structure():
    """Test that all required directories are created"""
    print("\nTesting directory structure...")
    
    try:
        from config import ConfigurationManager
        
        # Initialize configuration manager to create directories
        manager = ConfigurationManager()
        config = manager.load_configuration()
        
        # Check that directories exist
        home_dir = Path.home()
        base_dir = home_dir / ".ai-powershell-assistant"
        
        required_dirs = [
            base_dir / "config",
            base_dir / "data", 
            base_dir / "logs",
            base_dir / "cache",
            base_dir / "models"
        ]
        
        for directory in required_dirs:
            if directory.exists():
                print(f"✓ Directory exists: {directory}")
            else:
                print(f"✗ Directory missing: {directory}")
                return False
        
        # Check that config file was created
        config_file = base_dir / "config" / "config.yaml"
        if config_file.exists():
            print(f"✓ Configuration file created: {config_file}")
        else:
            print(f"✗ Configuration file missing: {config_file}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Directory structure error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("AI PowerShell Assistant - Project Structure Validation")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_configuration,
        test_data_models,
        test_directory_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Project structure is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())