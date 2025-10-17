"""
Unit tests for command translation API
Tests for task 2.2: 实现命令翻译 API
"""
import pytest
from unittest.mock import patch, MagicMock
import json


class TestTranslateEndpoint:
    """Tests for /api/command/translate endpoint"""
    
    def test_translate_success(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test successful command translation"""
        # Setup mocks
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['command'] == 'Get-Date'
        assert data['data']['confidence'] == 0.95
        assert data['data']['explanation'] == 'Gets the current date and time'
        assert data['data']['security']['level'] == 'safe'
        assert data['data']['security']['warnings'] == []
        assert data['data']['security']['requires_confirmation'] is False
        assert data['data']['security']['requires_elevation'] is False
    
    def test_translate_with_context(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test translation with context"""
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={
                    'input': '显示CPU使用率',
                    'context': {
                        'sessionId': 'test-session-123',
                        'history': ['Get-Date', 'Get-Process']
                    }
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify context was passed
        mock_assistant.ai_engine.translate_natural_language.assert_called_once()
        call_args = mock_assistant.ai_engine.translate_natural_language.call_args
        assert call_args[0][0] == '显示CPU使用率'
        assert call_args[0][1].session_id == 'test-session-123'
    
    def test_translate_high_risk_command(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test translation of high-risk command"""
        # Setup high-risk validation
        mock_validation.risk_level.value = 'high'
        mock_validation.warnings = ['This command will delete files']
        mock_validation.requires_confirmation = True
        mock_validation.requires_elevation = True
        
        mock_suggestion.generated_command = 'Remove-Item -Recurse -Force'
        mock_suggestion.explanation = 'Deletes files recursively'
        
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '删除所有文件'}
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['security']['level'] == 'high'
        assert len(data['data']['security']['warnings']) > 0
        assert data['data']['security']['requires_confirmation'] is True
        assert data['data']['security']['requires_elevation'] is True
    
    def test_translate_missing_input(self, client):
        """Test translation with missing input"""
        response = client.post('/api/command/translate', 
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_translate_empty_body(self, client):
        """Test translation with empty request body"""
        response = client.post('/api/command/translate',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Request body is required' in data['error']['message']
    
    def test_translate_invalid_json(self, client):
        """Test translation with invalid JSON"""
        response = client.post('/api/command/translate',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_translate_ai_engine_error(self, client, mock_assistant):
        """Test translation when AI engine fails"""
        mock_assistant.ai_engine.translate_natural_language.side_effect = Exception('AI service unavailable')
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_translate_security_engine_error(self, client, mock_assistant, mock_suggestion):
        """Test translation when security check fails"""
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.side_effect = Exception('Security check failed')
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
    
    def test_translate_assistant_initialization_error(self, client):
        """Test translation when assistant fails to initialize"""
        with patch('api.command.get_assistant', side_effect=RuntimeError('Failed to initialize')):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 503
    
    def test_translate_different_risk_levels(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test translation with different security risk levels"""
        risk_levels = ['safe', 'low', 'medium', 'high', 'critical']
        
        for risk_level in risk_levels:
            mock_validation.risk_level.value = risk_level
            mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
            mock_assistant.security_engine.validate_command.return_value = mock_validation
            
            with patch('api.command.get_assistant', return_value=mock_assistant):
                response = client.post('/api/command/translate', 
                    json={'input': 'test command'}
                )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['data']['security']['level'] == risk_level
    
    def test_translate_with_empty_input(self, client):
        """Test translation with empty input string"""
        response = client.post('/api/command/translate', 
            json={'input': ''}
        )
        
        # Should fail validation or return error
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert data['success'] is False
    
    def test_translate_with_very_long_input(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test translation with very long input"""
        long_input = 'a' * 10000
        
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': long_input}
            )
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_translate_response_structure(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test that response has correct structure"""
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'success' in data
        assert 'data' in data
        assert 'command' in data['data']
        assert 'confidence' in data['data']
        assert 'explanation' in data['data']
        assert 'security' in data['data']
        assert 'level' in data['data']['security']
        assert 'warnings' in data['data']['security']
        assert 'requires_confirmation' in data['data']['security']
        assert 'requires_elevation' in data['data']['security']
    
    def test_translate_confidence_score_range(self, client, mock_assistant, mock_suggestion, mock_validation):
        """Test that confidence score is in valid range"""
        mock_assistant.ai_engine.translate_natural_language.return_value = mock_suggestion
        mock_assistant.security_engine.validate_command.return_value = mock_validation
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/translate', 
                json={'input': '显示当前时间'}
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        confidence = data['data']['confidence']
        assert 0.0 <= confidence <= 1.0


class TestTranslateRequestValidation:
    """Tests for TranslateRequest model validation"""
    
    def test_valid_request(self):
        """Test valid request model"""
        from models.command import TranslateRequest
        
        request = TranslateRequest(input='显示当前时间')
        assert request.input == '显示当前时间'
        assert request.context is None
    
    def test_request_with_context(self):
        """Test request with context"""
        from models.command import TranslateRequest
        
        request = TranslateRequest(
            input='显示CPU使用率',
            context={'sessionId': 'test-123', 'history': []}
        )
        assert request.input == '显示CPU使用率'
        assert request.context['sessionId'] == 'test-123'
    
    def test_request_missing_input(self):
        """Test request without required input field"""
        from models.command import TranslateRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            TranslateRequest()


class TestTranslateResponseModel:
    """Tests for TranslateResponse model"""
    
    def test_valid_response(self):
        """Test valid response model"""
        from models.command import TranslateResponse, SecurityInfo
        
        security = SecurityInfo(
            level='safe',
            warnings=[],
            requires_confirmation=False,
            requires_elevation=False
        )
        
        response = TranslateResponse(
            command='Get-Date',
            confidence=0.95,
            explanation='Gets current date',
            security=security
        )
        
        assert response.command == 'Get-Date'
        assert response.confidence == 0.95
        assert response.security.level == 'safe'


class TestSecurityInfoModel:
    """Tests for SecurityInfo model"""
    
    def test_valid_security_info(self):
        """Test valid security info"""
        from models.command import SecurityInfo
        
        security = SecurityInfo(
            level='high',
            warnings=['This command is dangerous'],
            requires_confirmation=True,
            requires_elevation=True
        )
        
        assert security.level == 'high'
        assert len(security.warnings) == 1
        assert security.requires_confirmation is True
        assert security.requires_elevation is True
    
    def test_security_info_defaults(self):
        """Test security info with default values"""
        from models.command import SecurityInfo
        
        security = SecurityInfo(level='safe')
        
        assert security.level == 'safe'
        assert security.warnings == []
        assert security.requires_confirmation is False
        assert security.requires_elevation is False


class TestExecuteEndpoint:
    """Tests for /api/command/execute endpoint - Task 2.3"""
    
    def test_execute_success(self, client, mock_assistant, mock_execution_result):
        """Test successful command execution"""
        # Setup mock
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['output'] == "2025-10-08 14:30:00"
        assert data['data']['error'] is None
        assert data['data']['return_code'] == 0
        assert 'execution_time' in data['data']
        assert isinstance(data['data']['execution_time'], float)
        
        # Verify executor was called
        mock_assistant.executor.execute.assert_called_once()
        
        # Verify logging was called
        mock_assistant.log_engine.log_execution.assert_called_once()
    
    def test_execute_with_custom_timeout(self, client, mock_assistant, mock_execution_result):
        """Test execution with custom timeout"""
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Process',
                    'session_id': 'test-session-123',
                    'timeout': 60
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Verify timeout was passed to executor
        call_args = mock_assistant.executor.execute.call_args
        assert call_args[1]['timeout'] == 60
    
    def test_execute_with_default_timeout(self, client, mock_assistant, mock_execution_result):
        """Test execution with default timeout (30 seconds)"""
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        
        # Verify default timeout was used
        call_args = mock_assistant.executor.execute.call_args
        assert call_args[1]['timeout'] == 30
    
    def test_execute_command_with_error(self, client, mock_assistant):
        """Test execution of command that returns error"""
        # Setup mock with error result
        error_result = MagicMock()
        error_result.output = None
        error_result.error = "Command not found"
        error_result.return_code = 1
        
        mock_assistant.executor.execute.return_value = error_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Invalid-Command',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['error'] == "Command not found"
        assert data['data']['return_code'] == 1
    
    def test_execute_missing_command(self, client):
        """Test execution with missing command field"""
        response = client.post('/api/command/execute',
            json={
                'session_id': 'test-session-123'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_execute_missing_session_id(self, client):
        """Test execution with missing session_id field"""
        response = client.post('/api/command/execute',
            json={
                'command': 'Get-Date'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_execute_empty_body(self, client):
        """Test execution with empty request body"""
        response = client.post('/api/command/execute',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Request body is required' in data['error']['message']
    
    def test_execute_invalid_json(self, client):
        """Test execution with invalid JSON"""
        response = client.post('/api/command/execute',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_execute_executor_exception(self, client, mock_assistant):
        """Test execution when executor raises exception"""
        mock_assistant.executor.execute.side_effect = Exception('Execution failed')
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_execute_assistant_initialization_error(self, client):
        """Test execution when assistant fails to initialize"""
        with patch('api.command.get_assistant', side_effect=RuntimeError('Failed to initialize')):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 503
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 503
    
    def test_execute_timeout_exception(self, client, mock_assistant):
        """Test execution when command times out"""
        mock_assistant.executor.execute.side_effect = TimeoutError('Command timed out')
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Start-Sleep -Seconds 100',
                    'session_id': 'test-session-123',
                    'timeout': 5
                }
            )
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
    
    def test_execute_response_structure(self, client, mock_assistant, mock_execution_result):
        """Test that response has correct structure"""
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'success' in data
        assert 'data' in data
        assert 'output' in data['data']
        assert 'error' in data['data']
        assert 'execution_time' in data['data']
        assert 'return_code' in data['data']
    
    def test_execute_logs_execution(self, client, mock_assistant, mock_execution_result):
        """Test that execution is logged"""
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        command = 'Get-Process | Select-Object -First 5'
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': command,
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        
        # Verify log_execution was called with correct arguments
        mock_assistant.log_engine.log_execution.assert_called_once_with(
            command,
            mock_execution_result
        )
    
    def test_execute_measures_execution_time(self, client, mock_assistant, mock_execution_result):
        """Test that execution time is measured"""
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': 'Get-Date',
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify execution_time is present and is a positive number
        assert 'execution_time' in data['data']
        assert isinstance(data['data']['execution_time'], float)
        assert data['data']['execution_time'] >= 0
    
    def test_execute_with_multiline_command(self, client, mock_assistant, mock_execution_result):
        """Test execution with multiline command"""
        multiline_command = """Get-Process | 
            Where-Object {$_.CPU -gt 10} | 
            Select-Object -First 5"""
        
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': multiline_command,
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_execute_with_special_characters(self, client, mock_assistant, mock_execution_result):
        """Test execution with special characters in command"""
        command_with_special_chars = 'Write-Output "Hello $world & <test>"'
        
        mock_assistant.executor.execute.return_value = mock_execution_result
        mock_assistant.log_engine.log_execution.return_value = None
        
        with patch('api.command.get_assistant', return_value=mock_assistant):
            response = client.post('/api/command/execute',
                json={
                    'command': command_with_special_chars,
                    'session_id': 'test-session-123'
                }
            )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_execute_invalid_timeout_type(self, client):
        """Test execution with invalid timeout type"""
        response = client.post('/api/command/execute',
            json={
                'command': 'Get-Date',
                'session_id': 'test-session-123',
                'timeout': 'invalid'
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestExecuteRequestModel:
    """Tests for ExecuteRequest model validation"""
    
    def test_valid_request(self):
        """Test valid execute request"""
        from models.command import ExecuteRequest
        
        request = ExecuteRequest(
            command='Get-Date',
            session_id='test-session-123'
        )
        
        assert request.command == 'Get-Date'
        assert request.session_id == 'test-session-123'
        assert request.timeout == 30  # Default timeout
    
    def test_request_with_custom_timeout(self):
        """Test request with custom timeout"""
        from models.command import ExecuteRequest
        
        request = ExecuteRequest(
            command='Get-Process',
            session_id='test-session-123',
            timeout=60
        )
        
        assert request.timeout == 60
    
    def test_request_missing_command(self):
        """Test request without required command field"""
        from models.command import ExecuteRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ExecuteRequest(session_id='test-session-123')
    
    def test_request_missing_session_id(self):
        """Test request without required session_id field"""
        from models.command import ExecuteRequest
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ExecuteRequest(command='Get-Date')


class TestExecuteResponseModel:
    """Tests for ExecuteResponse model"""
    
    def test_valid_response(self):
        """Test valid execute response"""
        from models.command import ExecuteResponse
        
        response = ExecuteResponse(
            output='2025-10-08 14:30:00',
            error=None,
            execution_time=0.234,
            return_code=0
        )
        
        assert response.output == '2025-10-08 14:30:00'
        assert response.error is None
        assert response.execution_time == 0.234
        assert response.return_code == 0
    
    def test_response_with_error(self):
        """Test response with error"""
        from models.command import ExecuteResponse
        
        response = ExecuteResponse(
            output=None,
            error='Command not found',
            execution_time=0.1,
            return_code=1
        )
        
        assert response.output is None
        assert response.error == 'Command not found'
        assert response.return_code == 1
