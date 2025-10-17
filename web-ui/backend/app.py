"""
Flask application factory for AI PowerShell Assistant Web UI
"""
import os
import sys
import logging
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_caching import Cache
from pydantic import ValidationError
import time

from api.command import command_bp
from api.history import history_bp
from api.template import template_bp
from api.config import config_bp
from api.logs import logs_bp
from api.auth import auth_bp
from api.csrf import csrf_bp


class APIException(Exception):
    """Base API exception"""
    status_code = 500
    message = "Internal server error"
    
    def __init__(self, message=None, status_code=None):
        super().__init__()
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code


class ValidationException(APIException):
    """Validation error exception"""
    status_code = 400
    message = "Validation error"


class CommandExecutionException(APIException):
    """Command execution error exception"""
    status_code = 500
    message = "Command execution failed"


class ResourceNotFoundException(APIException):
    """Resource not found exception"""
    status_code = 404
    message = "Resource not found"


def create_app(config=None):
    """
    Create and configure the Flask application
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Tuple of (Flask application instance, SocketIO instance)
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'DEBUG': os.environ.get('FLASK_DEBUG', 'True').lower() == 'true',
        'CORS_HEADERS': 'Content-Type',
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max request size
        'AUTH_ENABLED': os.environ.get('AUTH_ENABLED', 'False').lower() == 'true',
        'WTF_CSRF_ENABLED': os.environ.get('CSRF_ENABLED', 'False').lower() == 'true',
        'WTF_CSRF_TIME_LIMIT': None,  # No time limit for CSRF tokens
        # Caching configuration
        'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'SimpleCache'),
        'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', '300')),
        'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        # Performance configuration
        'JSON_SORT_KEYS': False,  # Disable JSON key sorting for performance
        'JSONIFY_PRETTYPRINT_REGULAR': False,  # Disable pretty print in production
    })
    
    if config:
        app.config.update(config)
    
    # Initialize caching
    cache = Cache(app)
    app.config['CACHE'] = cache
    
    # Configure logging - write to the same file as PowerShell Assistant
    log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'assistant.log'))
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.config['DEBUG'] else logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"]
        }
    })
    
    # Initialize SocketIO for real-time logs
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Store socketio instance in app config for access in blueprints
    app.config['SOCKETIO'] = socketio
    
    # Performance monitoring middleware
    @app.before_request
    def before_request():
        """Track request start time"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Add performance headers and logging"""
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            response.headers['X-Response-Time'] = f'{elapsed:.3f}s'
            
            # Log slow requests
            if elapsed > 1.0:
                app.logger.warning(
                    f'Slow request: {request.method} {request.path} took {elapsed:.3f}s'
                )
        
        # Add caching headers for static resources
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Compression hint
        if not app.config['DEBUG']:
            response.headers['Vary'] = 'Accept-Encoding'
        
        return response
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(csrf_bp, url_prefix='/api/csrf')
    app.register_blueprint(command_bp, url_prefix='/api/command')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(template_bp, url_prefix='/api/templates')
    app.register_blueprint(config_bp, url_prefix='/api/config')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    
    # Setup WebSocket handlers for logs
    from api.logs import setup_websocket_handlers
    setup_websocket_handlers(socketio)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint to verify API is running"""
        try:
            # Add path to import PowerShellAssistant modules
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            
            # Try to get assistant instance and check components
            components = {
                'api': 'operational',
                'config': 'operational',
                'ai': 'operational',
                'security': 'operational',
                'execution': 'operational'
            }
            
            try:
                from api.command import get_assistant
                assistant = get_assistant()
                
                # Check if assistant components are initialized
                if hasattr(assistant, 'ai_engine') and assistant.ai_engine:
                    components['ai'] = 'operational'
                else:
                    components['ai'] = 'degraded'
                    
                if hasattr(assistant, 'security_engine') and assistant.security_engine:
                    components['security'] = 'operational'
                else:
                    components['security'] = 'degraded'
                    
                if hasattr(assistant, 'execution_engine') and assistant.execution_engine:
                    components['execution'] = 'operational'
                else:
                    components['execution'] = 'degraded'
                    
            except Exception as e:
                app.logger.warning(f'Could not check assistant components: {str(e)}')
                # Keep default operational status
            
            return jsonify({
                'success': True,
                'status': 'healthy',
                'message': 'AI PowerShell Assistant API is running',
                'version': '1.0.0',
                'components': components
            }), 200
        except Exception as e:
            app.logger.warning(f'Health check warning: {str(e)}')
            return jsonify({
                'success': True,
                'status': 'degraded',
                'message': 'API is running but some components may not be fully initialized',
                'version': '1.0.0',
                'components': {
                    'api': 'operational',
                    'ai': 'offline',
                    'security': 'offline',
                    'execution': 'offline'
                }
            }), 200
    
    # Error handlers
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions"""
        response = {
            'success': False,
            'error': {
                'message': error.message,
                'code': error.status_code
            }
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Pydantic validation errors"""
        response = {
            'success': False,
            'error': {
                'message': 'Validation error',
                'details': error.errors(),
                'code': 400
            }
        }
        return jsonify(response), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({
            'success': False,
            'error': {
                'message': 'Resource not found',
                'code': 404
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Internal server error: {str(error)}')
        return jsonify({
            'success': False,
            'error': {
                'message': 'Internal server error',
                'code': 500
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        app.logger.error(f'Unexpected error: {str(error)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': 'An unexpected error occurred',
                'code': 500
            }
        }), 500
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
