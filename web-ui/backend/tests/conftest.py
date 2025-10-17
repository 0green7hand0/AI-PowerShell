"""
Pytest configuration and fixtures for backend tests
"""
import sys
import os
import pytest
from unittest.mock import Mock, MagicMock

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Create Flask app for testing"""
    from app import create_app
    app, socketio = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def mock_assistant():
    """Create mock PowerShellAssistant"""
    assistant = MagicMock()
    
    # Mock AI engine
    assistant.ai_engine = MagicMock()
    
    # Mock security engine
    assistant.security_engine = MagicMock()
    
    # Mock executor
    assistant.executor = MagicMock()
    
    # Mock log engine
    assistant.log_engine = MagicMock()
    
    # Mock storage engine
    assistant.storage = MagicMock()
    
    return assistant


@pytest.fixture
def mock_suggestion():
    """Create mock command suggestion"""
    from unittest.mock import MagicMock
    suggestion = MagicMock()
    suggestion.generated_command = "Get-Date"
    suggestion.confidence_score = 0.95
    suggestion.explanation = "Gets the current date and time"
    return suggestion


@pytest.fixture
def mock_validation():
    """Create mock security validation"""
    from unittest.mock import MagicMock
    validation = MagicMock()
    validation.risk_level = MagicMock()
    validation.risk_level.value = 'safe'
    validation.warnings = []
    validation.requires_confirmation = False
    validation.requires_elevation = False
    return validation


@pytest.fixture
def mock_execution_result():
    """Create mock execution result"""
    from unittest.mock import MagicMock
    result = MagicMock()
    result.output = "2025-10-08 14:30:00"
    result.error = None
    result.return_code = 0
    return result
