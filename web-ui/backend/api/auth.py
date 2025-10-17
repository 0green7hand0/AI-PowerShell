"""
Authentication API endpoints for AI PowerShell Assistant Web UI
"""
import os
import jwt
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


# Pydantic models
class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class RefreshRequest(BaseModel):
    """Token refresh request model"""
    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # subject (username)
    exp: int  # expiration time
    iat: int  # issued at
    type: str  # token type (access or refresh)


# Simple in-memory user store (replace with database in production)
USERS = {
    'admin': {
        'password': 'admin123',  # In production, use hashed passwords
        'role': 'admin'
    }
}


def create_access_token(username: str, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token
    
    Args:
        username: Username to encode in token
        expires_delta: Token expiration time delta
        
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        'sub': username,
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def create_refresh_token(username: str) -> str:
    """
    Create JWT refresh token
    
    Args:
        username: Username to encode in token
        
    Returns:
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        'sub': username,
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def verify_token(token: str, token_type: str = 'access') -> dict:
    """
    Verify JWT token
    
    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)
        
    Returns:
        Decoded token payload
        
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        if payload.get('type') != token_type:
            raise jwt.InvalidTokenError('Invalid token type')
        
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Token has expired')
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f'Invalid token: {str(e)}')


def token_required(f):
    """
    Decorator to require valid JWT token for endpoint access
    
    Usage:
        @auth_bp.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'user': current_user})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Authentication token is missing',
                    'code': 401
                }
            }), 401
        
        try:
            # Verify token
            payload = verify_token(token, 'access')
            current_user = payload['sub']
            
            # Check if user exists
            if current_user not in USERS:
                return jsonify({
                    'success': False,
                    'error': {
                        'message': 'User not found',
                        'code': 401
                    }
                }), 401
            
            # Pass current user to the route
            return f(current_user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Token has expired',
                    'code': 401
                }
            }), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Invalid token: {str(e)}',
                    'code': 401
                }
            }), 401
        except Exception as e:
            logger.error(f'Token verification error: {str(e)}')
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Authentication failed',
                    'code': 401
                }
            }), 401
    
    return decorated


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint
    
    Request body:
        {
            "username": "admin",
            "password": "admin123"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "access_token": "...",
                "refresh_token": "...",
                "expires_in": 1800,
                "token_type": "Bearer"
            }
        }
    """
    try:
        # Validate request
        data = LoginRequest(**request.get_json())
        
        # Check credentials
        user = USERS.get(data.username)
        if not user or user['password'] != data.password:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Invalid username or password',
                    'code': 401
                }
            }), 401
        
        # Create tokens
        access_token = create_access_token(data.username)
        refresh_token = create_refresh_token(data.username)
        
        logger.info(f'User {data.username} logged in successfully')
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': 1800,  # 30 minutes
                'token_type': 'Bearer'
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'message': 'Validation error',
                'details': e.errors(),
                'code': 400
            }
        }), 400
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return jsonify({
            'success': False,
            'error': {
                'message': 'Login failed',
                'code': 500
            }
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using refresh token
    
    Request body:
        {
            "refresh_token": "..."
        }
    
    Response:
        {
            "success": true,
            "data": {
                "access_token": "...",
                "expires_in": 1800,
                "token_type": "Bearer"
            }
        }
    """
    try:
        # Validate request
        data = RefreshRequest(**request.get_json())
        
        # Verify refresh token
        payload = verify_token(data.refresh_token, 'refresh')
        username = payload['sub']
        
        # Check if user exists
        if username not in USERS:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'User not found',
                    'code': 401
                }
            }), 401
        
        # Create new access token
        access_token = create_access_token(username)
        
        logger.info(f'Access token refreshed for user {username}')
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'expires_in': 1800,
                'token_type': 'Bearer'
            }
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            'success': False,
            'error': {
                'message': 'Refresh token has expired',
                'code': 401
            }
        }), 401
    except jwt.InvalidTokenError as e:
        return jsonify({
            'success': False,
            'error': {
                'message': f'Invalid refresh token: {str(e)}',
                'code': 401
            }
        }), 401
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': {
                'message': 'Validation error',
                'details': e.errors(),
                'code': 400
            }
        }), 400
    except Exception as e:
        logger.error(f'Token refresh error: {str(e)}')
        return jsonify({
            'success': False,
            'error': {
                'message': 'Token refresh failed',
                'code': 500
            }
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout endpoint (token invalidation would be handled by client)
    
    Response:
        {
            "success": true,
            "message": "Logged out successfully"
        }
    """
    logger.info(f'User {current_user} logged out')
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify(current_user):
    """
    Verify token endpoint
    
    Response:
        {
            "success": true,
            "data": {
                "username": "admin",
                "role": "admin"
            }
        }
    """
    user = USERS.get(current_user)
    
    return jsonify({
        'success': True,
        'data': {
            'username': current_user,
            'role': user.get('role', 'user')
        }
    }), 200
