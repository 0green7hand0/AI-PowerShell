"""
Unit tests for configuration management API
Tests for task 2.6: 实现配置管理 API
"""
import pytest
from unittest.mock import patch, MagicMock


class TestGetConfigEndpoint:
    """Tests for GET /api/config endpoint"""
    
    def test_get_config_success(self, client, mock_assistant):
        """Test successful config retrieval"""
        # Setup mock config
        mock_config = MagicMock()
        
        # AI config
        mock_config.ai = MagicMock()
        mock_config.ai.provider = 'openai'
        mock_config.ai.model_name = 'gpt-4'
        mock_config.ai.temperature = 0.7
        mock_config.ai.max_tokens = 2000
        
        # Security config
        mock_config.security = MagicMock()
        mock_config.security.whitelist_mode = 'strict'
        mock_config.security.require_confirmation = True
        
        # Execution config
        mock_config.execution = MagicMock()
        mock_config.execution.timeout = 30
        mock_config.execution.shell_type = 'powershell'
        mock_config.execution.encoding = 'utf-8'
        
        # Logging config
        mock_config.logging = MagicMock()
        mock_config.logging.level = 'INFO'
        
        mock_assistant.config = mock_config
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.get('/api/config')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        
        # Verify AI config
        assert data['data']['ai']['provider'] == 'openai'
        assert data['data']['ai']['model_name'] == 'gpt-4'
        assert data['data']['ai']['temperature'] == 0.7
        assert data['data']['ai']['max_tokens'] == 2000
        
        # Verify security config
        assert data['data']['security']['whitelist_mode'] is True
        assert data['data']['security']['require_confirmation'] is True
        assert 'dangerous_patterns' in data['data']['security']
        
        # Verify execution config
        assert data['data']['execution']['timeout'] == 30
        assert data['data']['execution']['shell_type'] == 'powershell'
        assert data['data']['execution']['encoding'] == 'utf-8'
        
        # Verify general config
        assert 'general' in data['data']
        assert 'language' in data['data']['general']
        assert 'theme' in data['data']['general']
        assert data['data']['general']['log_level'] == 'INFO'
    
    def test_get_config_with_permissive_mode(self, client, mock_assistant):
        """Test config retrieval with permissive security mode"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.ai.provider = 'ollama'
        mock_config.ai.model_name = 'llama2'
        mock_config.ai.temperature = 0.5
        mock_config.ai.max_tokens = 1000
        
        mock_config.security = MagicMock()
        mock_config.security.whitelist_mode = 'permissive'
        mock_config.security.require_confirmation = False
        
        mock_config.execution = MagicMock()
        mock_config.execution.timeout = 60
        mock_config.execution.shell_type = 'pwsh'
        mock_config.execution.encoding = 'utf-8'
        
        mock_config.logging = MagicMock()
        mock_config.logging.level = 'DEBUG'
        
        mock_assistant.config = mock_config
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.get('/api/config')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['security']['whitelist_mode'] is False
        assert data['data']['security']['require_confirmation'] is False
    
    def test_get_config_assistant_error(self, client):
        """Test config retrieval when assistant fails"""
        with patch('api.config.get_assistant', side_effect=Exception('Assistant initialization failed')):
            response = client.get('/api/config')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'Failed to retrieve configuration' in data['error']['message']
    
    def test_get_config_response_structure(self, client, mock_assistant):
        """Test that response has correct structure"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.ai.provider = 'openai'
        mock_config.ai.model_name = 'gpt-4'
        mock_config.ai.temperature = 0.7
        mock_config.ai.max_tokens = 2000
        
        mock_config.security = MagicMock()
        mock_config.security.whitelist_mode = 'strict'
        mock_config.security.require_confirmation = True
        
        mock_config.execution = MagicMock()
        mock_config.execution.timeout = 30
        mock_config.execution.shell_type = 'powershell'
        mock_config.execution.encoding = 'utf-8'
        
        mock_config.logging = MagicMock()
        mock_config.logging.level = 'INFO'
        
        mock_assistant.config = mock_config
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.get('/api/config')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'success' in data
        assert 'data' in data
        assert 'ai' in data['data']
        assert 'security' in data['data']
        assert 'execution' in data['data']
        assert 'general' in data['data']


class TestUpdateConfigEndpoint:
    """Tests for PUT /api/config endpoint"""
    
    def test_update_ai_config(self, client, mock_assistant):
        """Test updating AI configuration"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'ai': {
                'provider': 'ollama',
                'model_name': 'llama2',
                'temperature': 0.8,
                'max_tokens': 3000
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
        assert 'Configuration updated successfully' in data['message']
        
        # Verify config_manager.update_config was called
        assert mock_assistant.config_manager.update_config.called
        
        # Verify config was reloaded
        mock_assistant.config_manager.load_config.assert_called_once()
    
    def test_update_security_config(self, client, mock_assistant):
        """Test updating security configuration"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'security': {
                'whitelist_mode': True,
                'require_confirmation': False
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        
        # Verify update_config was called with correct values
        calls = mock_assistant.config_manager.update_config.call_args_list
        assert any('security.whitelist_mode' in str(call) for call in calls)
    
    def test_update_execution_config(self, client, mock_assistant):
        """Test updating execution configuration"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'execution': {
                'timeout': 60,
                'shell_type': 'pwsh',
                'encoding': 'utf-16'
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert mock_assistant.config_manager.update_config.called
    
    def test_update_general_config(self, client, mock_assistant):
        """Test updating general configuration"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'general': {
                'log_level': 'DEBUG'
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
    
    def test_update_multiple_sections(self, client, mock_assistant):
        """Test updating multiple configuration sections"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'ai': {
                'temperature': 0.9
            },
            'security': {
                'require_confirmation': True
            },
            'execution': {
                'timeout': 45
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        
        # Verify multiple updates were made
        assert mock_assistant.config_manager.update_config.call_count >= 3
    
    def test_update_config_empty_body(self, client):
        """Test update with empty request body"""
        response = client.put('/api/config',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        # Empty body is treated as invalid JSON
        assert 'JSON' in data['error']['message'] or 'body' in data['error']['message'].lower()
    
    def test_update_config_invalid_json(self, client):
        """Test update with invalid JSON"""
        response = client.put('/api/config',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_config_validation_error(self, client, mock_assistant):
        """Test update with validation error"""
        mock_config = MagicMock()
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        # Create a proper ValidationError by trying to validate invalid data
        from pydantic import ValidationError, BaseModel, Field
        
        class TestModel(BaseModel):
            temperature: float = Field(ge=0, le=1)
        
        try:
            TestModel(temperature=2.0)
        except ValidationError as ve:
            mock_assistant.config_manager.update_config.side_effect = ve
        
        update_data = {
            'ai': {
                'temperature': 2.0  # Invalid value
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_config_assistant_error(self, client):
        """Test update when assistant fails"""
        with patch('api.config.get_assistant', side_effect=Exception('Assistant initialization failed')):
            response = client.put('/api/config', json={'ai': {'temperature': 0.8}})
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_config_manager_error(self, client, mock_assistant):
        """Test update when config manager fails"""
        mock_config = MagicMock()
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        mock_assistant.config_manager.update_config.side_effect = Exception('Failed to update config')
        
        update_data = {
            'ai': {
                'temperature': 0.8
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_config_partial_update(self, client, mock_assistant):
        """Test partial configuration update"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        # Only update one field
        update_data = {
            'ai': {
                'temperature': 0.6
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        
        # Verify only temperature was updated
        calls = [str(call) for call in mock_assistant.config_manager.update_config.call_args_list]
        assert any('temperature' in call for call in calls)
    
    def test_update_config_whitelist_mode_conversion(self, client, mock_assistant):
        """Test whitelist_mode boolean to string conversion"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        # Test True -> 'strict'
        update_data = {
            'security': {
                'whitelist_mode': True
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        
        # Verify 'strict' was passed
        calls = mock_assistant.config_manager.update_config.call_args_list
        assert any(call[0][1] == 'strict' for call in calls if 'whitelist_mode' in str(call))
        
        # Test False -> 'permissive'
        mock_assistant.config_manager.reset_mock()
        update_data = {
            'security': {
                'whitelist_mode': False
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        
        # Verify 'permissive' was passed
        calls = mock_assistant.config_manager.update_config.call_args_list
        assert any(call[0][1] == 'permissive' for call in calls if 'whitelist_mode' in str(call))
    
    def test_update_config_response_structure(self, client, mock_assistant):
        """Test that response has correct structure"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'ai': {
                'temperature': 0.7
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify response structure
        assert 'success' in data
        assert 'data' in data
        assert 'message' in data
    
    def test_update_config_ignores_unknown_fields(self, client, mock_assistant):
        """Test that unknown fields are ignored"""
        mock_config = MagicMock()
        mock_config.ai = MagicMock()
        mock_config.security = MagicMock()
        mock_config.execution = MagicMock()
        mock_config.logging = MagicMock()
        
        mock_assistant.config = mock_config
        mock_assistant.config_manager = MagicMock()
        
        update_data = {
            'ai': {
                'temperature': 0.7,
                'unknown_field': 'should be ignored'
            },
            'unknown_section': {
                'field': 'value'
            }
        }
        
        with patch('api.config.get_assistant', return_value=mock_assistant):
            response = client.put('/api/config', json=update_data)
        
        # Should succeed and ignore unknown fields
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestConfigModels:
    """Tests for configuration data models"""
    
    def test_ai_config_model(self):
        """Test AIConfig model"""
        from models.config import AIConfig
        
        config = AIConfig(
            provider='openai',
            model_name='gpt-4',
            temperature=0.7,
            max_tokens=2000
        )
        
        assert config.provider == 'openai'
        assert config.model_name == 'gpt-4'
        assert config.temperature == 0.7
        assert config.max_tokens == 2000
    
    def test_security_config_model(self):
        """Test SecurityConfig model"""
        from models.config import SecurityConfig
        
        config = SecurityConfig(
            whitelist_mode=True,
            require_confirmation=True,
            dangerous_patterns=['rm -rf', 'Remove-Item']
        )
        
        assert config.whitelist_mode is True
        assert config.require_confirmation is True
        assert len(config.dangerous_patterns) == 2
    
    def test_security_config_defaults(self):
        """Test SecurityConfig default values"""
        from models.config import SecurityConfig
        
        config = SecurityConfig()
        
        assert config.whitelist_mode is False
        assert config.require_confirmation is True
        assert config.dangerous_patterns == []
    
    def test_execution_config_model(self):
        """Test ExecutionConfig model"""
        from models.config import ExecutionConfig
        
        config = ExecutionConfig(
            timeout=60,
            shell_type='pwsh',
            encoding='utf-8'
        )
        
        assert config.timeout == 60
        assert config.shell_type == 'pwsh'
        assert config.encoding == 'utf-8'
    
    def test_execution_config_defaults(self):
        """Test ExecutionConfig default values"""
        from models.config import ExecutionConfig
        
        config = ExecutionConfig()
        
        assert config.timeout == 30
        assert config.shell_type == 'powershell'
        assert config.encoding == 'utf-8'
    
    def test_general_config_model(self):
        """Test GeneralConfig model"""
        from models.config import GeneralConfig
        
        config = GeneralConfig(
            language='en-US',
            theme='dark',
            log_level='DEBUG'
        )
        
        assert config.language == 'en-US'
        assert config.theme == 'dark'
        assert config.log_level == 'DEBUG'
    
    def test_general_config_defaults(self):
        """Test GeneralConfig default values"""
        from models.config import GeneralConfig
        
        config = GeneralConfig()
        
        assert config.language == 'zh-CN'
        assert config.theme == 'light'
        assert config.log_level == 'INFO'
    
    def test_app_config_model(self):
        """Test AppConfig model"""
        from models.config import AppConfig, AIConfig, SecurityConfig, ExecutionConfig, GeneralConfig
        
        config = AppConfig(
            ai=AIConfig(provider='openai', model_name='gpt-4'),
            security=SecurityConfig(),
            execution=ExecutionConfig(),
            general=GeneralConfig()
        )
        
        assert config.ai.provider == 'openai'
        assert config.security.whitelist_mode is False
        assert config.execution.timeout == 30
        assert config.general.language == 'zh-CN'
    
    def test_config_model_validation(self):
        """Test config model validation"""
        from models.config import AIConfig
        from pydantic import ValidationError
        
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            AIConfig()
