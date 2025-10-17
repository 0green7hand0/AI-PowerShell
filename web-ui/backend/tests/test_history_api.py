"""
Unit tests for History API endpoints
"""
import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture(autouse=True)
def patch_get_assistant(mock_assistant):
    """Automatically patch get_assistant for all tests"""
    with patch('api.history.get_assistant', return_value=mock_assistant):
        yield


class TestHistoryAPI:
    """Test suite for History API endpoints"""
    
    def test_get_history_empty(self, client, mock_assistant):
        """Test getting history when no records exist"""
        # Mock empty history
        mock_assistant.storage.load_history.return_value = []
        
        response = client.get('/api/history')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['items'] == []
        assert data['data']['total'] == 0
        assert data['data']['page'] == 1
        assert data['data']['limit'] == 20
    
    def test_get_history_with_records(self, client, mock_assistant):
        """Test getting history with existing records"""
        # Mock history data
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': '显示当前时间',
                'command': 'Get-Date',
                'success': True,
                'output': '2024-01-15 10:30:00',
                'error': None,
                'execution_time': 0.123,
                'timestamp': '2024-01-15T10:30:00'
            },
            {
                'id': 'hist_002',
                'user_input': '列出文件',
                'command': 'Get-ChildItem',
                'success': True,
                'output': 'file1.txt\nfile2.txt',
                'error': None,
                'execution_time': 0.234,
                'timestamp': '2024-01-15T10:29:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        response = client.get('/api/history')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['items']) == 2
        assert data['data']['total'] == 2
        assert data['data']['items'][0]['id'] == 'hist_001'
        assert data['data']['items'][0]['user_input'] == '显示当前时间'
    
    def test_get_history_pagination(self, client, mock_assistant):
        """Test history pagination"""
        # Create 25 mock history items
        mock_history = [
            {
                'id': f'hist_{i:03d}',
                'user_input': f'Command {i}',
                'command': f'Get-Command{i}',
                'success': True,
                'output': f'Output {i}',
                'error': None,
                'execution_time': 0.1,
                'timestamp': f'2024-01-15T10:{i:02d}:00'
            }
            for i in range(25)
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        # Test first page
        response = client.get('/api/history?page=1&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 10
        assert data['data']['total'] == 25
        assert data['data']['page'] == 1
        
        # Test second page
        response = client.get('/api/history?page=2&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 10
        assert data['data']['page'] == 2
        
        # Test third page (partial)
        response = client.get('/api/history?page=3&limit=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 5
        assert data['data']['page'] == 3
    
    def test_get_history_search(self, client, mock_assistant):
        """Test history search functionality"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': '显示CPU使用率',
                'command': 'Get-Process | Sort-Object CPU',
                'success': True,
                'output': 'process list',
                'error': None,
                'execution_time': 0.5,
                'timestamp': '2024-01-15T10:30:00'
            },
            {
                'id': 'hist_002',
                'user_input': '列出文件',
                'command': 'Get-ChildItem',
                'success': True,
                'output': 'file list',
                'error': None,
                'execution_time': 0.2,
                'timestamp': '2024-01-15T10:29:00'
            },
            {
                'id': 'hist_003',
                'user_input': '显示内存使用',
                'command': 'Get-Process | Select Memory',
                'success': True,
                'output': 'memory info',
                'error': None,
                'execution_time': 0.3,
                'timestamp': '2024-01-15T10:28:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        # Search for "CPU"
        response = client.get('/api/history?search=CPU')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 1
        assert 'CPU' in data['data']['items'][0]['user_input']
        
        # Search for "Get-Process"
        response = client.get('/api/history?search=Get-Process')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 2
        
        # Search for non-existent term
        response = client.get('/api/history?search=nonexistent')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 0
    
    def test_get_history_sorting(self, client, mock_assistant):
        """Test that history is sorted by timestamp (newest first)"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': 'Old command',
                'command': 'Get-Old',
                'success': True,
                'output': 'old',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:00:00'
            },
            {
                'id': 'hist_002',
                'user_input': 'New command',
                'command': 'Get-New',
                'success': True,
                'output': 'new',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:30:00'
            },
            {
                'id': 'hist_003',
                'user_input': 'Middle command',
                'command': 'Get-Middle',
                'success': True,
                'output': 'middle',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:15:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        response = client.get('/api/history')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should be sorted newest first
        assert data['data']['items'][0]['user_input'] == 'New command'
        assert data['data']['items'][1]['user_input'] == 'Middle command'
        assert data['data']['items'][2]['user_input'] == 'Old command'
    
    def test_get_history_detail_success(self, client, mock_assistant):
        """Test getting detail of a specific history item"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': '显示当前时间',
                'command': 'Get-Date',
                'success': True,
                'output': '2024-01-15 10:30:00',
                'error': None,
                'execution_time': 0.123,
                'timestamp': '2024-01-15T10:30:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        response = client.get('/api/history/hist_001')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == 'hist_001'
        assert data['data']['user_input'] == '显示当前时间'
        assert data['data']['command'] == 'Get-Date'
    
    def test_get_history_detail_not_found(self, client, mock_assistant):
        """Test getting detail of non-existent history item"""
        mock_assistant.storage.load_history.return_value = []
        
        response = client.get('/api/history/nonexistent_id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error']['message'].lower()
    
    def test_delete_history_success(self, client, mock_assistant):
        """Test deleting a history item"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': 'Command 1',
                'command': 'Get-Command1',
                'success': True,
                'output': 'output1',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:30:00'
            },
            {
                'id': 'hist_002',
                'user_input': 'Command 2',
                'command': 'Get-Command2',
                'success': True,
                'output': 'output2',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:29:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        mock_assistant.storage.save_history_batch.return_value = True
        
        response = client.delete('/api/history/hist_001')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()
        
        # Verify save_history_batch was called with correct data
        mock_assistant.storage.save_history_batch.assert_called_once()
        saved_history = mock_assistant.storage.save_history_batch.call_args[0][0]
        assert len(saved_history) == 1
        assert saved_history[0]['id'] == 'hist_002'
    
    def test_delete_history_not_found(self, client, mock_assistant):
        """Test deleting non-existent history item"""
        mock_assistant.storage.load_history.return_value = []
        
        response = client.delete('/api/history/nonexistent_id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error']['message'].lower()
    
    def test_delete_history_save_failure(self, client, mock_assistant):
        """Test handling of save failure during deletion"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': 'Command 1',
                'command': 'Get-Command1',
                'success': True,
                'output': 'output1',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:30:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        mock_assistant.storage.save_history_batch.return_value = False
        
        response = client.delete('/api/history/hist_001')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'failed to save' in data['error']['message'].lower()
    
    def test_clear_all_history_success(self, client, mock_assistant):
        """Test clearing all history"""
        mock_assistant.storage.clear_history.return_value = True
        
        response = client.delete('/api/history')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'cleared successfully' in data['message'].lower()
        mock_assistant.storage.clear_history.assert_called_once()
    
    def test_clear_all_history_failure(self, client, mock_assistant):
        """Test handling of failure when clearing all history"""
        mock_assistant.storage.clear_history.return_value = False
        
        response = client.delete('/api/history')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'failed to clear' in data['error']['message'].lower()
    
    def test_history_with_missing_ids(self, client, mock_assistant):
        """Test handling of history items without IDs"""
        mock_history = [
            {
                # No ID field
                'user_input': 'Command without ID',
                'command': 'Get-Command',
                'success': True,
                'output': 'output',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:30:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        response = client.get('/api/history')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['items']) == 1
        # Should have generated an ID
        assert data['data']['items'][0]['id'].startswith('hist_')
    
    def test_history_error_handling(self, client, mock_assistant):
        """Test error handling when storage fails"""
        mock_assistant.storage.load_history.side_effect = Exception("Storage error")
        
        response = client.get('/api/history')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_history_case_insensitive_search(self, client, mock_assistant):
        """Test that search is case-insensitive"""
        mock_history = [
            {
                'id': 'hist_001',
                'user_input': '显示CPU使用率',
                'command': 'Get-Process',
                'success': True,
                'output': 'output',
                'error': None,
                'execution_time': 0.1,
                'timestamp': '2024-01-15T10:30:00'
            }
        ]
        mock_assistant.storage.load_history.return_value = mock_history
        
        # Search with lowercase
        response = client.get('/api/history?search=cpu')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 1
        
        # Search with uppercase
        response = client.get('/api/history?search=CPU')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['items']) == 1
