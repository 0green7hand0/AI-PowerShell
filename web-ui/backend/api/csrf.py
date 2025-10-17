"""
CSRF protection for AI PowerShell Assistant Web UI
"""
import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, session
import logging

logger = logging.getLogger(__name__)

csrf_bp = Blueprint('csrf', __name__)

# In-memory token store (use Redis in production)
_csrf_tokens = {}


def generate_csrf_token():
    """
    Generate a new CSRF token
    
    Returns:
        str: CSRF token
    """
    token = secrets.token_urlsafe(32)
    timestamp = datetime.utcnow()
    
    # Store token with timestamp
    _csrf_tokens[token] = timestamp
    
    # Clean up old tokens (older than 1 hour)
    cleanup_expired_tokens()
    
    return token


def cleanup_expired_tokens():
    """Clean up expired CSRF tokens"""
    expiry_time = datetime.utcnow() - timedelta(hours=1)
    expired_tokens = [
        token for token, timestamp in _csrf_tokens.items()
        if timestamp < expiry_time
    ]
    for token in expired_tokens:
        del _csrf_tokens[token]


def verify_csrf_token(token: str) -> bool:
    """
    Verify CSRF token
    
    Args:
        token: CSRF token to verify
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token:
        return False
    
    # Check if token exists
    if token not in _csrf_tokens:
        return False
    
    # Check if token is expired (1 hour)
    timestamp = _csrf_tokens[token]
    if datetime.utcnow() - timestamp > timedelta(hours=1):
        del _csrf_tokens[token]
        return False
    
    return True


def csrf_protect(f):
    """
    Decorator to protect endpoints with CSRF token verification
    
    Usage:
        @app.route('/api/protected', methods=['POST'])
        @csrf_protect
        def protected_route():
            return jsonify({'message': 'Protected'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Skip CSRF check if disabled
        if not current_app.config.get('WTF_CSRF_ENABLED', True):
            return f(*args, **kwargs)
        
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)
        
        # Get CSRF token from header
        csrf_token = request.headers.get('X-CSRF-Token')
        
        if not csrf_token:
            logger.warning(f'CSRF token missing for {request.path}')
            return jsonify({
                'success': False,
                'error': {
                    'message': 'CSRF token is missing',
                    'code': 403
                }
            }), 403
        
        # Verify token
        if not verify_csrf_token(csrf_token):
            logger.warning(f'Invalid CSRF token for {request.path}')
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Invalid or expired CSRF token',
                    'code': 403
                }
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated


@csrf_bp.route('/token', methods=['GET'])
def get_csrf_token():
    """
    Get CSRF token endpoint
    
    Response:
        {
            "success": true,
            "data": {
                "csrf_token": "..."
            }
        }
    """
    try:
        token = generate_csrf_token()
        
        return jsonify({
            'success': True,
            'data': {
                'csrf_token': token
            }
        }), 200
    except Exception as e:
        logger.error(f'Error generating CSRF token: {str(e)}')
        return jsonify({
            'success': False,
            'error': {
                'message': 'Failed to generate CSRF token',
                'code': 500
            }
        }), 500


@csrf_bp.route('/verify', methods=['POST'])
def verify_csrf():
    """
    Verify CSRF token endpoint (for testing)
    
    Request body:
        {
            "csrf_token": "..."
        }
    
    Response:
        {
            "success": true,
            "data": {
                "valid": true
            }
        }
    """
    try:
        data = request.get_json()
        token = data.get('csrf_token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'CSRF token is required',
                    'code': 400
                }
            }), 400
        
        is_valid = verify_csrf_token(token)
        
        return jsonify({
            'success': True,
            'data': {
                'valid': is_valid
            }
        }), 200
    except Exception as e:
        logger.error(f'Error verifying CSRF token: {str(e)}')
        return jsonify({
            'success': False,
            'error': {
                'message': 'Failed to verify CSRF token',
                'code': 500
            }
        }), 500
