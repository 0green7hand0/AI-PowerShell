"""
Unit tests for data models
Tests model validation and serialization
"""
import pytest
from pydantic import ValidationError
from datetime import datetime


class TestCommandModels:
    """Tests for command-related models"""
    
    def test_translate_request_valid(self):
        """Test valid TranslateRequest"""
        from models.command import TranslateRequest
        
        request = TranslateRequest(input='显示当前时间')
        assert request.input == '显示当前时间'
        assert request.context is None
    
    def test_translate_request_with_context(self):
        """Test TranslateRequest with context"""
        from models.command import TranslateRequest
        
        context = {'sessionId': 'test-123', 'history': ['Get-Date']}
        request = TranslateRequest(input='test', context=context)
        
        assert request.context == context
    
    def test_translate_request_missing_input(self):
        """Test TranslateRequest without input"""
        from models.command import TranslateRequest
        
        with pytest.raises(ValidationError):
            TranslateRequest()
    
    def test_security_info_valid(self):
        """Test valid SecurityInfo"""
        from models.command import SecurityInfo
        
        security = SecurityInfo(
            level='high',
            warnings=['Dangerous command'],
            requires_confirmation=True,
            requires_elevation=True
        )
        
        assert security.level == 'high'
        assert len(security.warnings) == 1
        assert security.requires_confirmation is True
    
    def test_security_info_defaults(self):
        """Test SecurityInfo default values"""
        from models.command import SecurityInfo
        
        security = SecurityInfo(level='safe')
        
        assert security.warnings == []
        assert security.requires_confirmation is False
        assert security.requires_elevation is False
    
    def test_execute_request_valid(self):
        """Test valid ExecuteRequest"""
        from models.command import ExecuteRequest
        
        request = ExecuteRequest(
            command='Get-Date',
            session_id='test-123'
        )
        
        assert request.command == 'Get-Date'
        assert request.session_id == 'test-123'
        assert request.timeout == 30
    
    def test_execute_request_custom_timeout(self):
        """Test ExecuteRequest with custom timeout"""
        from models.command import ExecuteRequest
        
        request = ExecuteRequest(
            command='Get-Process',
            session_id='test-123',
            timeout=60
        )
        
        assert request.timeout == 60
    
    def test_execute_response_valid(self):
        """Test valid ExecuteResponse"""
        from models.command import ExecuteResponse
        
        response = ExecuteResponse(
            output='test output',
            error=None,
            execution_time=0.5,
            return_code=0
        )
        
        assert response.output == 'test output'
        assert response.error is None
        assert response.execution_time == 0.5
        assert response.return_code == 0


class TestHistoryModels:
    """Tests for history-related models"""
    
    def test_history_item_valid(self):
        """Test valid HistoryItem"""
        from models.history import HistoryItem
        
        item = HistoryItem(
            id='test-123',
            user_input='显示时间',
            command='Get-Date',
            success=True,
            timestamp=datetime.now(),
            execution_time=0.5
        )
        
        assert item.id == 'test-123'
        assert item.user_input == '显示时间'
        assert item.success is True
    
    def test_history_item_with_output(self):
        """Test HistoryItem with output"""
        from models.history import HistoryItem
        
        item = HistoryItem(
            id='test-123',
            user_input='test',
            command='Get-Date',
            success=True,
            output='2025-10-08',
            timestamp=datetime.now(),
            execution_time=0.5
        )
        
        assert item.output == '2025-10-08'
    
    def test_history_item_with_error(self):
        """Test HistoryItem with error"""
        from models.history import HistoryItem
        
        item = HistoryItem(
            id='test-123',
            user_input='test',
            command='Invalid-Command',
            success=False,
            error='Command not found',
            timestamp=datetime.now(),
            execution_time=0.1
        )
        
        assert item.success is False
        assert item.error == 'Command not found'
    
    def test_history_list_response_valid(self):
        """Test valid HistoryListResponse"""
        from models.history import HistoryListResponse, HistoryItem
        
        items = [
            HistoryItem(
                id='1',
                user_input='test',
                command='Get-Date',
                success=True,
                timestamp=datetime.now(),
                execution_time=0.5
            )
        ]
        
        response = HistoryListResponse(
            items=items,
            total=1,
            page=1,
            limit=20
        )
        
        assert len(response.items) == 1
        assert response.total == 1
        assert response.page == 1


class TestTemplateModels:
    """Tests for template-related models"""
    
    def test_template_parameter_valid(self):
        """Test valid TemplateParameter"""
        from models.template import TemplateParameter
        
        param = TemplateParameter(
            name='sourcePath',
            type='string',
            required=True,
            description='Source directory path'
        )
        
        assert param.name == 'sourcePath'
        assert param.type == 'string'
        assert param.required is True
    
    def test_template_parameter_with_default(self):
        """Test TemplateParameter with default value"""
        from models.template import TemplateParameter
        
        param = TemplateParameter(
            name='timeout',
            type='number',
            required=False,
            default=30
        )
        
        assert param.default == 30
        assert param.required is False
    
    def test_template_parameter_with_options(self):
        """Test TemplateParameter with options"""
        from models.template import TemplateParameter
        
        param = TemplateParameter(
            name='action',
            type='select',
            required=True,
            options=['copy', 'move', 'delete']
        )
        
        assert len(param.options) == 3
        assert 'copy' in param.options
    
    def test_template_valid(self):
        """Test valid Template"""
        from models.template import Template, TemplateParameter
        
        params = [
            TemplateParameter(name='path', type='string', required=True)
        ]
        
        template = Template(
            id='test-123',
            name='Backup Script',
            description='Backup files',
            category='automation',
            script_content='Copy-Item...',
            parameters=params,
            keywords=['backup', 'copy'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert template.name == 'Backup Script'
        assert template.category == 'automation'
        assert len(template.parameters) == 1
        assert len(template.keywords) == 2
    
    def test_template_without_parameters(self):
        """Test Template without parameters"""
        from models.template import Template
        
        template = Template(
            id='test-123',
            name='Simple Script',
            description='Test',
            category='automation',
            script_content='Get-Date',
            parameters=[],
            keywords=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert len(template.parameters) == 0
    
    def test_generate_script_request_valid(self):
        """Test valid GenerateScriptRequest"""
        from models.template import GenerateScriptRequest
        
        request = GenerateScriptRequest(
            parameters={
                'sourcePath': 'C:\\Data',
                'targetPath': 'D:\\Backup'
            }
        )
        
        assert 'sourcePath' in request.parameters
        assert request.parameters['sourcePath'] == 'C:\\Data'


class TestConfigModels:
    """Tests for config-related models"""
    
    def test_config_update_request_valid(self):
        """Test valid ConfigUpdateRequest"""
        from models.config import ConfigUpdateRequest
        
        request = ConfigUpdateRequest(
            ai_config={'provider': 'openai', 'model': 'gpt-4'},
            security_config={'whitelist_mode': True},
            execution_config={'timeout': 60}
        )
        
        assert request.ai_config['provider'] == 'openai'
        assert request.security_config['whitelist_mode'] is True
        assert request.execution_config['timeout'] == 60
    
    def test_config_update_request_partial(self):
        """Test ConfigUpdateRequest with partial update"""
        from models.config import ConfigUpdateRequest
        
        request = ConfigUpdateRequest(
            ai_config={'model': 'gpt-4'}
        )
        
        assert request.ai_config['model'] == 'gpt-4'
        assert request.security_config is None
        assert request.execution_config is None
