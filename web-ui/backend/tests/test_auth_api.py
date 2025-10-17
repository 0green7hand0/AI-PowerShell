"""
Tests for authentication API endpoints
"""
import pytest
import jwt
from datetime import datetime, timedelta


def test_login_success(client):
    """Test successful login"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']
    assert data['data']['token_type'] == 'Bearer'
    assert data['data']['expires_in'] == 1800


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid username or password' in data['error']['message']


def test_login_missing_fields(client):
    """Test login with missing fields"""
    response = client.post('/api/auth/login', json={
        'username': 'admin'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False


def test_refresh_token_success(client, app):
    """Test successful token refresh"""
    # First login to get tokens
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    refresh_token = login_response.get_json()['data']['refresh_token']
    
    # Refresh the token
    response = client.post('/api/auth/refresh', json={
        'refresh_token': refresh_token
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert data['data']['token_type'] == 'Bearer'


def test_refresh_token_invalid(client):
    """Test token refresh with invalid token"""
    response = client.post('/api/auth/refresh', json={
        'refresh_token': 'invalid_token'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_refresh_token_expired(client, app):
    """Test token refresh with expired token"""
    # Create an expired refresh token
    with app.app_context():
        expire = datetime.utcnow() - timedelta(days=1)
        payload = {
            'sub': 'admin',
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        expired_token = jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    response = client.post('/api/auth/refresh', json={
        'refresh_token': expired_token
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'expired' in data['error']['message'].lower()


def test_verify_token_success(client):
    """Test token verification"""
    # First login to get token
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    access_token = login_response.get_json()['data']['access_token']
    
    # Verify the token
    response = client.get('/api/auth/verify', headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['username'] == 'admin'
    assert data['data']['role'] == 'admin'


def test_verify_token_missing(client):
    """Test token verification without token"""
    response = client.get('/api/auth/verify')
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
    assert 'missing' in data['error']['message'].lower()


def test_verify_token_invalid(client):
    """Test token verification with invalid token"""
    response = client.get('/api/auth/verify', headers={
        'Authorization': 'Bearer invalid_token'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_logout_success(client):
    """Test successful logout"""
    # First login to get token
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    access_token = login_response.get_json()['data']['access_token']
    
    # Logout
    response = client.post('/api/auth/logout', headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Logged out successfully' in data['message']


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.post('/api/auth/logout')
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False


def test_token_type_mismatch(client, app):
    """Test using access token as refresh token"""
    # First login to get tokens
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    access_token = login_response.get_json()['data']['access_token']
    
    # Try to use access token as refresh token
    response = client.post('/api/auth/refresh', json={
        'refresh_token': access_token
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['success'] is False
