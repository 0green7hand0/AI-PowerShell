"""
Logs API endpoints for viewing system logs and real-time streaming
"""
import os
import sys
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

# Add parent directory to path to import PowerShellAssistant
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

logs_bp = Blueprint('logs', __name__)


def get_assistant():
    """Get PowerShellAssistant instance from command API"""
    from api.command import get_assistant as get_cmd_assistant
    return get_cmd_assistant()


@logs_bp.route('', methods=['GET'])
def get_logs():
    """
    Get system logs with optional filtering
    
    GET /api/logs?level=ERROR&limit=100&since=2025-10-07T00:00:00Z
    Response: List of log entries
    """
    try:
        # Get query parameters
        level = request.args.get('level', '').upper()
        limit = int(request.args.get('limit', 1000))
        since = request.args.get('since', '')
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Read log file
        try:
            log_file = assistant.config.logging.file
            # Convert to absolute path if relative
            if not os.path.isabs(log_file):
                # Get project root directory (3 levels up from this file)
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                log_file = os.path.join(project_root, log_file)
        except AttributeError:
            # If logging config not available, try default location
            current_app.logger.warning("Logging configuration not available, using default path")
            log_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs', 'assistant.log')
            log_file = os.path.abspath(log_file)
        
        current_app.logger.info(f"Reading log file from: {log_file}")
        current_app.logger.info(f"Log file exists: {os.path.exists(log_file)}")
        
        if not os.path.exists(log_file):
            current_app.logger.warning(f"Log file not found: {log_file}")
            return jsonify({
                'success': True,
                'data': {
                    'logs': [],
                    'total': 0
                }
            }), 200
        
        # Parse log file
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            current_app.logger.info(f"Total lines in log file: {len(lines)}")
            
            # Read last N lines (reverse order for recent logs)
            for line in reversed(lines[-limit*2:]):  # Read more than limit to account for filtering
                line = line.strip()
                if not line:
                    continue
                
                # Parse log line (format: timestamp - name - level - message)
                try:
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        timestamp_str, source, log_level, message = parts
                        
                        # Debug: log parsed values
                        current_app.logger.debug(f"Parsed line: level={log_level}, source={source}")
                        
                        # Filter by level if specified
                        if level and log_level != level:
                            continue
                        
                        # Filter by timestamp if specified
                        if since:
                            try:
                                log_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                                since_time = datetime.fromisoformat(since.replace('Z', '+00:00'))
                                if log_time < since_time:
                                    continue
                            except:
                                pass
                        
                        logs.append({
                            'timestamp': timestamp_str,
                            'level': log_level,
                            'message': message,
                            'source': source
                        })
                        
                        if len(logs) >= limit:
                            break
                    else:
                        current_app.logger.debug(f"Failed to parse line (not enough parts): {line[:100]}")
                except Exception as e:
                    # Skip malformed lines
                    current_app.logger.debug(f"Failed to parse line: {line[:100]}, error: {e}")
                    continue
        
        current_app.logger.info(f"Parsed {len(logs)} log entries")
        current_app.logger.info(f"ERROR/CRITICAL count: {len([log for log in logs if log['level'] in ['ERROR', 'CRITICAL']])}")
        
        # Reverse to show newest first
        logs.reverse()
        
        response = {
            'success': True,
            'data': {
                'logs': logs,
                'total': len(logs)
            }
        }
        
        current_app.logger.info(f"Retrieved {len(logs)} log entries")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving logs: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve logs: {str(e)}',
                'code': 500
            }
        }), 500


# WebSocket handlers for real-time logs
class SocketIOLogHandler(logging.Handler):
    """
    Custom log handler that emits logs to SocketIO
    """
    def __init__(self, socketio):
        super().__init__()
        self.socketio = socketio
        self.subscribers = set()
    
    def emit(self, record):
        """
        Emit log record to SocketIO
        """
        try:
            # Format log record
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'message': self.format(record),
                'source': record.name
            }
            
            # Emit to all subscribers
            self.socketio.emit('log', log_entry, namespace='/logs')
        except Exception as e:
            print(f"Error emitting log to SocketIO: {e}")
    
    def add_subscriber(self, client_id):
        """
        Add a subscriber
        """
        self.subscribers.add(client_id)
    
    def remove_subscriber(self, client_id):
        """
        Remove a subscriber
        """
        if client_id in self.subscribers:
            self.subscribers.remove(client_id)
    
    def has_subscribers(self):
        """
        Check if there are any subscribers
        """
        return len(self.subscribers) > 0

# Global log handler instance
log_handler = None

def setup_websocket_handlers(socketio):
    """
    Setup WebSocket handlers for real-time log streaming
    
    Args:
        socketio: Flask-SocketIO instance
    """
    global log_handler
    
    # Create and configure log handler
    log_handler = SocketIOLogHandler(socketio)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Add handler to root logger
    logging.getLogger().addHandler(log_handler)
    
    @socketio.on('connect', namespace='/logs')
    def handle_connect():
        """Handle client connection to logs namespace"""
        client_id = request.sid
        current_app.logger.info(f'Client connected to logs stream: {client_id}')
        
        if log_handler:
            log_handler.add_subscriber(client_id)
        
        socketio.emit('connected', {'message': 'Connected to log stream'}, namespace='/logs')
    
    @socketio.on('disconnect', namespace='/logs')
    def handle_disconnect():
        """Handle client disconnection from logs namespace"""
        client_id = request.sid
        current_app.logger.info(f'Client disconnected from logs stream: {client_id}')
        
        if log_handler:
            log_handler.remove_subscriber(client_id)
    
    @socketio.on('subscribe', namespace='/logs')
    def handle_subscribe(data):
        """Handle log subscription with filters"""
        level = data.get('level', 'ALL')
        client_id = request.sid
        current_app.logger.info(f'Client subscribed to logs with level: {level}, client_id: {client_id}')
        
        # Send test log to verify connection
        test_log = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': 'INFO',
            'message': f'Connected to real-time log stream with level filter: {level}',
            'source': 'websocket'
        }
        socketio.emit('log', test_log, namespace='/logs', to=client_id)
        
        socketio.emit('subscribed', {'level': level}, namespace='/logs', to=client_id)
