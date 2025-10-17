"""
Logs API endpoints for viewing system logs and real-time streaming
"""
import os
import sys
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
        limit = int(request.args.get('limit', 100))
        since = request.args.get('since', '')
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Read log file
        try:
            log_file = assistant.config.logging.file_path
        except AttributeError:
            # If logging config not available, try default location
            current_app.logger.warning("Logging configuration not available, using default path")
            log_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs', 'assistant.log')
            log_file = os.path.abspath(log_file)
        
        current_app.logger.info(f"Reading log file from: {log_file}")
        
        if not os.path.exists(log_file):
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
                except:
                    # Skip malformed lines
                    continue
        
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
def setup_websocket_handlers(socketio):
    """
    Setup WebSocket handlers for real-time log streaming
    
    Args:
        socketio: Flask-SocketIO instance
    """
    
    @socketio.on('connect', namespace='/logs')
    def handle_connect():
        """Handle client connection to logs namespace"""
        current_app.logger.info('Client connected to logs stream')
        socketio.emit('connected', {'message': 'Connected to log stream'}, namespace='/logs')
    
    @socketio.on('disconnect', namespace='/logs')
    def handle_disconnect():
        """Handle client disconnection from logs namespace"""
        current_app.logger.info('Client disconnected from logs stream')
    
    @socketio.on('subscribe', namespace='/logs')
    def handle_subscribe(data):
        """Handle log subscription with filters"""
        level = data.get('level', 'ALL')
        current_app.logger.info(f'Client subscribed to logs with level: {level}')
        socketio.emit('subscribed', {'level': level}, namespace='/logs')
    
    # Note: Real-time log streaming would require a log handler that emits to WebSocket
    # This is a simplified implementation. For production, consider using a proper
    # logging handler that integrates with SocketIO
