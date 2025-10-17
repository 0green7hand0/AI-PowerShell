"""
Unit tests for Template API endpoints
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestTemplateAPI:
    """Test suite for template management API"""
    
    def test_get_templates_success(self, client, mock_assistant):
        """Test successful retrieval of template list"""
        # Mock template data
        mock_template = MagicMock()
        mock_template.name = "test_template"
        mock_template.description = "Test template description"
        mock_template.category = "custom"
        mock_template.script_content = "Get-Process"
        mock_template.parameters = []
        mock_template.keywords = ["test", "process"]
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'templates' in data['data']
            assert len(data['data']['templates']) == 1
            assert data['data']['templates'][0]['name'] == "test_template"
    
    def test_get_templates_with_category_filter(self, client, mock_assistant):
        """Test template list with category filter"""
        mock_template = MagicMock()
        mock_template.name = "automation_template"
        mock_template.description = "Automation template"
        mock_template.category = "automation"
        mock_template.script_content = "Start-Process"
        mock_template.parameters = []
        mock_template.keywords = ["automation"]
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates?category=automation')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 1
            assert data['data']['templates'][0]['category'] == "automation"
    
    def test_get_templates_with_search(self, client, mock_assistant):
        """Test template list with search query"""
        mock_template = MagicMock()
        mock_template.name = "backup_script"
        mock_template.description = "Backup files to remote location"
        mock_template.category = "automation"
        mock_template.script_content = "Copy-Item"
        mock_template.parameters = []
        mock_template.keywords = ["backup", "copy"]
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates?search=backup')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 1
            assert 'backup' in data['data']['templates'][0]['name'].lower()
    
    def test_get_templates_empty_list(self, client, mock_assistant):
        """Test template list when no templates exist"""
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.list_custom_templates.return_value = []
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 0
    
    def test_get_templates_manager_not_initialized(self, client, mock_assistant):
        """Test template list when manager is not initialized"""
        mock_assistant.custom_template_manager = None
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 0
    
    def test_get_template_detail_success(self, client, mock_assistant):
        """Test successful retrieval of template detail"""
        mock_template = MagicMock()
        mock_template.name = "test_template"
        mock_template.description = "Test template"
        mock_template.category = "custom"
        mock_template.script_content = "Get-Process"
        mock_template.parameters = []
        mock_template.keywords = ["test"]
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates/test_template')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['name'] == "test_template"
    
    def test_get_template_detail_not_found(self, client, mock_assistant):
        """Test template detail when template not found"""
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.return_value = None
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates/nonexistent')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
            assert 'not found' in data['error']['message'].lower()
    
    def test_create_template_success(self, client, mock_assistant):
        """Test successful template creation"""
        mock_template = MagicMock()
        mock_template.id = "test_template"
        mock_template.name = "Test Template"
        mock_template.description = "A test template"
        mock_template.category = "custom"
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.create_template.return_value = mock_template
        
        template_data = {
            'name': 'Test Template',
            'description': 'A test template',
            'category': 'custom',
            'script_content': 'Get-Process | Select-Object -First 5',
            'keywords': ['test', 'process']
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['name'] == "Test Template"
            assert 'created successfully' in data['data']['message'].lower()
    
    def test_create_template_missing_required_fields(self, client, mock_assistant):
        """Test template creation with missing required fields"""
        template_data = {
            'name': 'Test Template'
            # Missing description and script_content
        }
        
        mock_assistant.custom_template_manager = MagicMock()
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'required' in data['error']['message'].lower()
    
    def test_create_template_invalid_name(self, client, mock_assistant):
        """Test template creation with invalid name"""
        template_data = {
            'name': 'A' * 150,  # Too long
            'description': 'Test description',
            'script_content': 'Get-Process'
        }
        
        mock_assistant.custom_template_manager = MagicMock()
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'too long' in data['error']['message'].lower()
    
    def test_create_template_invalid_category(self, client, mock_assistant):
        """Test template creation with invalid category"""
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'category': 'invalid category!',  # Contains invalid characters
            'script_content': 'Get-Process'
        }
        
        mock_assistant.custom_template_manager = MagicMock()
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
    
    def test_create_template_manager_not_initialized(self, client, mock_assistant):
        """Test template creation when manager not initialized"""
        mock_assistant.custom_template_manager = None
        
        template_data = {
            'name': 'Test Template',
            'description': 'Test description',
            'script_content': 'Get-Process'
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 503
            data = response.get_json()
            assert data['success'] is False
            assert 'not initialized' in data['error']['message'].lower()
    
    def test_update_template_success(self, client, mock_assistant):
        """Test successful template update"""
        mock_template_info = {
            'id': 'test_template',
            'name': 'Test Template',
            'category': 'custom'
        }
        
        mock_updated_template = MagicMock()
        mock_updated_template.id = "test_template"
        mock_updated_template.name = "Updated Template"
        mock_updated_template.description = "Updated description"
        mock_updated_template.category = "custom"
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template_info
        mock_assistant.custom_template_manager.edit_template.return_value = mock_updated_template
        
        update_data = {
            'name': 'Updated Template',
            'description': 'Updated description'
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.put('/api/templates/test_template', json=update_data)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['name'] == "Updated Template"
    
    def test_update_template_not_found(self, client, mock_assistant):
        """Test template update when template not found"""
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.side_effect = Exception("Not found")
        mock_assistant.custom_template_manager.list_categories.return_value = []
        
        update_data = {
            'name': 'Updated Template'
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.put('/api/templates/nonexistent', json=update_data)
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
    
    def test_delete_template_success(self, client, mock_assistant):
        """Test successful template deletion"""
        mock_template_info = {
            'id': 'test_template',
            'name': 'Test Template',
            'category': 'custom'
        }
        
        mock_assistant.custom_template_manager = MagicMock()
        # Mock both get_template_info and list_categories for the delete logic
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template_info
        mock_assistant.custom_template_manager.list_categories.return_value = [
            {'name': 'custom', 'is_system': False, 'template_count': 1}
        ]
        mock_assistant.custom_template_manager.delete_template.return_value = True
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.delete('/api/templates/test_template?category=custom')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'deleted successfully' in data['message'].lower()
    
    def test_delete_template_not_found(self, client, mock_assistant):
        """Test template deletion when template not found"""
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.side_effect = Exception("Not found")
        mock_assistant.custom_template_manager.list_categories.return_value = []
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.delete('/api/templates/nonexistent')
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
    
    def test_generate_script_success(self, client, mock_assistant):
        """Test successful script generation from template"""
        mock_template = MagicMock()
        mock_template.name = "backup_template"
        mock_template.script_content = "Copy-Item -Path {{source}} -Destination {{destination}}"
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template
        
        generate_data = {
            'parameters': {
                'source': 'C:\\Data',
                'destination': 'D:\\Backup'
            }
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates/backup_template/generate', json=generate_data)
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'script' in data['data']
            assert 'C:\\Data' in data['data']['script']
            assert 'D:\\Backup' in data['data']['script']
    
    def test_generate_script_template_not_found(self, client, mock_assistant):
        """Test script generation when template not found"""
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.get_template_info.return_value = None
        
        generate_data = {
            'parameters': {
                'source': 'C:\\Data'
            }
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates/nonexistent/generate', json=generate_data)
            
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
    
    def test_generate_script_missing_parameters(self, client, mock_assistant):
        """Test script generation with missing parameters"""
        mock_assistant.custom_template_manager = MagicMock()
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates/test_template/generate', json={})
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
    
    def test_create_template_with_all_fields(self, client, mock_assistant):
        """Test template creation with all optional fields"""
        mock_template = MagicMock()
        mock_template.id = "full_template"
        mock_template.name = "Full Template"
        mock_template.description = "Complete template"
        mock_template.category = "automation"
        
        mock_assistant.custom_template_manager = MagicMock()
        mock_assistant.custom_template_manager.create_template.return_value = mock_template
        
        template_data = {
            'name': 'Full Template',
            'description': 'Complete template',
            'category': 'automation',
            'script_content': 'Get-Process | Where-Object {$_.CPU -gt 10}',
            'keywords': ['process', 'cpu', 'monitoring'],
            'author': 'test_user',
            'tags': ['system', 'monitoring']
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            
            # Verify all fields were passed to create_template
            mock_assistant.custom_template_manager.create_template.assert_called_once()
            call_kwargs = mock_assistant.custom_template_manager.create_template.call_args[1]
            assert call_kwargs['name'] == 'Full Template'
            assert call_kwargs['author'] == 'test_user'
            assert call_kwargs['tags'] == ['system', 'monitoring']
