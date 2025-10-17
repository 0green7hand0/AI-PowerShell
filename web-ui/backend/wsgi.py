"""
WSGI entry point for production deployment
"""
import os
import sys

# Add parent directory to path to import PowerShellAssistant modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app
from config import get_config

# Get environment from environment variable
env = os.environ.get('FLASK_ENV', 'production')

# Create app with appropriate configuration
app, socketio = create_app()
app.config.from_object(get_config(env))

# For gunicorn
application = app

if __name__ == '__main__':
    # Run with SocketIO for development
    socketio.run(
        app,
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
