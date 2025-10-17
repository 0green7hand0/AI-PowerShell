"""
Tests for CSRF protection
"""
import pytest


def test_get_csrf_token(client):
    """Test getting CSRF token"""
    response = client.get('/api/csrf/token')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'csrf_token' in data['data']
    assert len(data['data']['csrf_token']) > 0


def test_verify_csrf_token_valid(client):
    """Test verifying valid CSRF token"""
    # Get a token first
    token_response = client.get('/api/csrf/token')
    csrf_token = token_response.get_json()['data']['csrf_token']
    
    # Verify the token
    response = client.post('/api/csrf/verify', json={
        'csrf_token': csrf_token
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['valid'] is True


def test_verify_csrf_token_invalid(client):
    """Test verifying invalid CSRF token"""
    response = client.post('/api/csrf/verify', json={
        'csrf_token': 'invalid_token'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['valid'] is False


def test_verify_csrf_token_missing(client):
    """Test verifying without CSRF token"""
    response = client.post('/api/csrf/verify', json={})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_csrf_protect_decorator_get_request(client, app):
    """Test CSRF protection doesn't apply to GET requests"""
    from api.csrf import csrf_protect
    from flask import jsonify
    
    @app.route('/test/csrf/get', methods=['GET'])
    @csrf_protect
    def test_get():
        return jsonify({'success': True})
    
    response = client.get('/test/csrf/get')
    assert response.status_code == 200


def test_csrf_protect_decorator_post_without_token(client, app):
    """Test CSRF protection blocks POST without token"""
    from api.csrf import csrf_protect
    from flask import jsonify
    
    @app.route('/test/csrf/post', methods=['POST'])
    @csrf_protect
    def test_post():
        return jsonify({'success': True})
    
    response = client.post('/test/csrf/post', json={})
    assert response.status_code == 403
    data = response.get_json()
    assert data['success'] is False
    assert 'CSRF token is missing' in data['error']['message']


def test_csrf_protect_decorator_post_with_valid_token(client, app):
    """Test CSRF protection allows POST with valid token"""
    from api.csrf import csrf_protect
    from flask import jsonify
    
    @app.route('/test/csrf/post-valid', methods=['POST'])
    @csrf_protect
    def test_post_valid():
        return jsonify({'success': True})
    
    # Get a valid token
    token_response = client.get('/api/csrf/token')
    csrf_token = token_response.get_json()['data']['csrf_token']
    
    # Make POST request with token
    response = client.post('/test/csrf/post-valid', 
                          json={},
                          headers={'X-CSRF-Token': csrf_token})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_csrf_protect_decorator_post_with_invalid_token(client, app):
    """Test CSRF protection blocks POST with invalid token"""
    from api.csrf import csrf_protect
    from flask import jsonify
    
    @app.route('/test/csrf/post-invalid', methods=['POST'])
    @csrf_protect
    def test_post_invalid():
        return jsonify({'success': True})
    
    # Make POST request with invalid token
    response = client.post('/test/csrf/post-invalid',
                          json={},
                          headers={'X-CSRF-Token': 'invalid_token'})
    
    assert response.status_code == 403
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid or expired' in data['error']['message']


def test_csrf_disabled(client, app):
    """Test CSRF protection when disabled"""
    from api.csrf import csrf_protect
    from flask import jsonify
    
    # Disable CSRF
    app.config['WTF_CSRF_ENABLED'] = False
    
    @app.route('/test/csrf/disabled', methods=['POST'])
    @csrf_protect
    def test_disabled():
        return jsonify({'success': True})
    
    # Make POST request without token
    response = client.post('/test/csrf/disabled', json={})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    # Re-enable CSRF
    app.config['WTF_CSRF_ENABLED'] = True
