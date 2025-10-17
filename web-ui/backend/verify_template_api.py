"""
Verification script for Template API endpoints

This script tests all template management API endpoints to ensure they work correctly.
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from unittest.mock import MagicMock, patch


def verify_template_api():
    """Verify all template API endpoints"""
    print("=" * 60)
    print("Template API Verification")
    print("=" * 60)
    
    # Create test app
    app, socketio = create_app({'TESTING': True})
    client = app.test_client()
    
    # Create mock assistant
    mock_assistant = MagicMock()
    mock_assistant.custom_template_manager = MagicMock()
    
    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }
    
    def test(name, func):
        """Run a test and record result"""
        try:
            func()
            results['passed'] += 1
            results['tests'].append({'name': name, 'status': 'PASSED'})
            print(f"✓ {name}")
        except AssertionError as e:
            results['failed'] += 1
            results['tests'].append({'name': name, 'status': 'FAILED', 'error': str(e)})
            print(f"✗ {name}: {str(e)}")
        except Exception as e:
            results['failed'] += 1
            results['tests'].append({'name': name, 'status': 'ERROR', 'error': str(e)})
            print(f"✗ {name}: ERROR - {str(e)}")
    
    # Test 1: GET /api/templates - List templates
    def test_get_templates():
        mock_template = MagicMock()
        mock_template.name = "test_template"
        mock_template.description = "Test template"
        mock_template.category = "custom"
        mock_template.script_content = "Get-Process"
        mock_template.parameters = []
        mock_template.keywords = ["test"]
        
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.get_json()
            assert data['success'] is True, "Response should be successful"
            assert 'templates' in data['data'], "Response should contain templates"
    
    test("GET /api/templates - List templates", test_get_templates)
    
    # Test 2: GET /api/templates with category filter
    def test_get_templates_with_category():
        mock_template = MagicMock()
        mock_template.name = "automation_template"
        mock_template.description = "Automation template"
        mock_template.category = "automation"
        mock_template.script_content = "Start-Process"
        mock_template.parameters = []
        mock_template.keywords = ["automation"]
        
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates?category=automation')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 1
    
    test("GET /api/templates?category=automation - Filter by category", test_get_templates_with_category)
    
    # Test 3: GET /api/templates with search
    def test_get_templates_with_search():
        mock_template = MagicMock()
        mock_template.name = "backup_script"
        mock_template.description = "Backup files"
        mock_template.category = "automation"
        mock_template.script_content = "Copy-Item"
        mock_template.parameters = []
        mock_template.keywords = ["backup"]
        
        mock_assistant.custom_template_manager.list_custom_templates.return_value = [mock_template]
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates?search=backup')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert len(data['data']['templates']) == 1
    
    test("GET /api/templates?search=backup - Search templates", test_get_templates_with_search)
    
    # Test 4: GET /api/templates/:id - Get template detail
    def test_get_template_detail():
        mock_template = MagicMock()
        mock_template.name = "test_template"
        mock_template.description = "Test template"
        mock_template.category = "custom"
        mock_template.script_content = "Get-Process"
        mock_template.parameters = []
        mock_template.keywords = ["test"]
        
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates/test_template')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['data']['name'] == "test_template"
    
    test("GET /api/templates/:id - Get template detail", test_get_template_detail)
    
    # Test 5: POST /api/templates - Create template
    def test_create_template():
        mock_template = MagicMock()
        mock_template.id = "new_template"
        mock_template.name = "New Template"
        mock_template.description = "A new template"
        mock_template.category = "custom"
        
        mock_assistant.custom_template_manager.create_template.return_value = mock_template
        
        template_data = {
            'name': 'New Template',
            'description': 'A new template',
            'category': 'custom',
            'script_content': 'Get-Process | Select-Object -First 5',
            'keywords': ['test']
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            assert response.status_code == 201
            data = response.get_json()
            assert data['success'] is True
            assert 'created successfully' in data['data']['message'].lower()
    
    test("POST /api/templates - Create template", test_create_template)
    
    # Test 6: POST /api/templates - Validation error
    def test_create_template_validation():
        template_data = {
            'name': 'Test'
            # Missing required fields
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.post('/api/templates', json=template_data)
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
    
    test("POST /api/templates - Validation error", test_create_template_validation)
    
    # Test 7: PUT /api/templates/:id - Update template
    def test_update_template():
        mock_template_info = {
            'id': 'test_template',
            'name': 'Test Template',
            'category': 'custom'
        }
        
        mock_updated_template = MagicMock()
        mock_updated_template.id = "test_template"
        mock_updated_template.name = "Updated Template"
        mock_updated_template.description = "Updated"
        mock_updated_template.category = "custom"
        
        mock_assistant.custom_template_manager.get_template_info.return_value = mock_template_info
        mock_assistant.custom_template_manager.edit_template.return_value = mock_updated_template
        
        update_data = {
            'name': 'Updated Template',
            'description': 'Updated'
        }
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.put('/api/templates/test_template', json=update_data)
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    test("PUT /api/templates/:id - Update template", test_update_template)
    
    # Test 8: DELETE /api/templates/:id - Delete template
    def test_delete_template():
        mock_template_info = {
            'id': 'test_template',
            'name': 'Test Template',
            'category': 'custom'
        }
        
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
    
    test("DELETE /api/templates/:id - Delete template", test_delete_template)
    
    # Test 9: POST /api/templates/:id/generate - Generate script
    def test_generate_script():
        mock_template = MagicMock()
        mock_template.name = "backup_template"
        mock_template.script_content = "Copy-Item -Path {{source}} -Destination {{destination}}"
        
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
    
    test("POST /api/templates/:id/generate - Generate script", test_generate_script)
    
    # Test 10: Template not found scenarios
    def test_template_not_found():
        mock_assistant.custom_template_manager.get_template_info.return_value = None
        
        with patch('api.template.get_assistant', return_value=mock_assistant):
            response = client.get('/api/templates/nonexistent')
            assert response.status_code == 404
            data = response.get_json()
            assert data['success'] is False
    
    test("GET /api/templates/:id - Template not found", test_template_not_found)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total tests: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    
    if results['failed'] > 0:
        print("\nFailed tests:")
        for test_result in results['tests']:
            if test_result['status'] != 'PASSED':
                print(f"  - {test_result['name']}: {test_result.get('error', 'Unknown error')}")
    
    print("=" * 60)
    
    return results['failed'] == 0


if __name__ == '__main__':
    success = verify_template_api()
    sys.exit(0 if success else 1)
