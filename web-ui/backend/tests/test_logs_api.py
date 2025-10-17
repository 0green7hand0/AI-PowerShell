"""
Unit tests for logs API
Tests for task 2.7: 实现日志 API 和 WebSocket
"""
import pytest
from unittest.mock import patch, MagicMock
import json


class TestLogsEndpoint:
    """Tests for /api/logs endpoint"""
    
    def test_get_logs_success(self, client, mock_assistant):
        """Test successful logs retrieval"""
        # Setup mock logs
        mock_logs = [
            {
                'timestamp': '2025-10-08T14:30:00',
                'level': 'INFO',
                'message': 'Command executed successfully'
            },
            {
                'timestamp': '2025-10-08T14:29:00',
                'level': 'WARNING',
                'message': 'High CPU usage detected'
            }
        ]
        
        mock_assistant.log_engine.get_logs.return_value = mock_logs
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'data' in data
        assert len(data['data']) == 2
        assert data['data'][0]['level'] == 'INFO'
        assert data['data'][1]['level'] == 'WARNING'
    
    def test_get_logs_with_level_filter(self, client, mock_assistant):
        """Test logs retrieval with level filter"""
        mock_logs = [
            {
                'timestamp': '2025-10-08T14:30:00',
                'level': 'ERROR',
                'message': 'Command failed'
            }
        ]
        
        mock_assistant.log_engine.get_logs.return_value = mock_logs
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs?level=ERROR')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['level'] == 'ERROR'
        
        # Verify filter was passed to log engine
        mock_assistant.log_engine.get_logs.assert_called_once()
        call_args = mock_assistant.log_engine.get_logs.call_args
        assert call_args[1]['level'] == 'ERROR'
    
    def test_get_logs_with_limit(self, client, mock_assistant):
        """Test logs retrieval with limit"""
        mock_logs = [{'timestamp': '2025-10-08T14:30:00', 'level': 'INFO', 'message': 'Test'}]
        
        mock_assistant.log_engine.get_logs.return_value = mock_logs
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs?limit=50')
        
        assert response.status_code == 200
        
        # Verify limit was passed
        call_args = mock_assistant.log_engine.get_logs.call_args
        assert call_args[1]['limit'] == 50
    
    def test_get_logs_with_since_timestamp(self, client, mock_assistant):
        """Test logs retrieval with since timestamp"""
        mock_logs = []
        
        mock_assistant.log_engine.get_logs.return_value = mock_logs
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs?since=2025-10-08T14:00:00')
        
        assert response.status_code == 200
        
        # Verify since parameter was passed
        call_args = mock_assistant.log_engine.get_logs.call_args
        assert 'since' in call_args[1]
    
    def test_get_logs_empty_result(self, client, mock_assistant):
        """Test logs retrieval with no logs"""
        mock_assistant.log_engine.get_logs.return_value = []
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data'] == []
    
    def test_get_logs_engine_error(self, client, mock_assistant):
        """Test logs retrieval when log engine fails"""
        mock_assistant.log_engine.get_logs.side_effect = Exception('Log engine error')
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_logs_invalid_level(self, client, mock_assistant):
        """Test logs retrieval with invalid level"""
        mock_assistant.log_engine.get_logs.return_value = []
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs?level=INVALID')
        
        # Should either filter out or return error
        assert response.status_code in [200, 400]
    
    def test_get_logs_invalid_limit(self, client):
        """Test logs retrieval with invalid limit"""
        response = client.get('/api/logs?limit=invalid')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_get_logs_multiple_filters(self, client, mock_assistant):
        """Test logs retrieval with multiple filters"""
        mock_logs = []
        
        mock_assistant.log_engine.get_logs.return_value = mock_logs
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs?level=ERROR&limit=10&since=2025-10-08T14:00:00')
        
        assert response.status_code == 200
        
        # Verify all filters were passed
        call_args = mock_assistant.log_engine.get_logs.call_args
        assert call_args[1]['level'] == 'ERROR'
        assert call_args[1]['limit'] == 10


class TestSystemStatusEndpoint:
    """Tests for /api/logs/status endpoint"""
    
    def test_get_system_status_success(self, client, mock_assistant):
        """Test successful system status retrieval"""
        mock_status = {
            'ai_engine': 'online',
            'security_engine': 'online',
            'execution_engine': 'online',
            'log_engine': 'online'
        }
        
        mock_assistant.get_system_status.return_value = mock_status
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs/status')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert data['data']['ai_engine'] == 'online'
        assert data['data']['security_engine'] == 'online'
        assert data['data']['execution_engine'] == 'online'
    
    def test_get_system_status_partial_failure(self, client, mock_assistant):
        """Test system status with some engines offline"""
        mock_status = {
            'ai_engine': 'online',
            'security_engine': 'offline',
            'execution_engine': 'online',
            'log_engine': 'online'
        }
        
        mock_assistant.get_system_status.return_value = mock_status
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs/status')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['data']['security_engine'] == 'offline'
    
    def test_get_system_status_error(self, client, mock_assistant):
        """Test system status when check fails"""
        mock_assistant.get_system_status.side_effect = Exception('Status check failed')
        
        with patch('api.logs.get_assistant', return_value=mock_assistant):
            response = client.get('/api/logs/status')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False


class TestWebSocketLogs:
    """Tests for WebSocket log streaming"""
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection establishment"""
        # Note: WebSocket testing requires socketio test client
        # This is a placeholder for WebSocket tests
        pass
    
    def test_websocket_log_streaming(self, client):
        """Test real-time log streaming via WebSocket"""
        # Placeholder for WebSocket streaming tests
        pass
    
    def test_websocket_disconnect(self, client):
        """Test WebSocket disconnection"""
        # Placeholder for WebSocket disconnect tests
        pass
