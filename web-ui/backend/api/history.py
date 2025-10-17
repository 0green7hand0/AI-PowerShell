"""
History API endpoints for managing command history
"""
import os
import sys
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from api.csrf import csrf_protect

# Add parent directory to path to import PowerShellAssistant
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

history_bp = Blueprint('history', __name__)


def get_assistant():
    """Get PowerShellAssistant instance from command API"""
    from api.command import get_assistant as get_cmd_assistant
    return get_cmd_assistant()


@history_bp.route('', methods=['GET'])
def get_history():
    """
    Get command history list with pagination and search
    
    GET /api/history?page=1&limit=20&search=keyword
    Response: HistoryListResponse
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '').lower()
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Load history from storage
        history_data = assistant.storage.load_history()
        
        # Filter by search query if provided
        if search:
            history_data = [
                item for item in history_data
                if search in item.get('user_input', '').lower() or
                   search in item.get('command', '').lower()
            ]
        
        # Sort by timestamp (newest first)
        history_data.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        
        # Calculate pagination
        total = len(history_data)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_items = history_data[start_idx:end_idx]
        
        # Format items and ensure IDs are present
        items = []
        for idx, item in enumerate(paginated_items):
            # Generate ID if not present (use timestamp-based ID for consistency)
            if 'id' not in item or not item['id']:
                timestamp = item.get('timestamp', datetime.now().isoformat())
                item_id = f"hist_{timestamp.replace(':', '').replace('-', '').replace('.', '')[:20]}"
            else:
                item_id = item['id']
            
            items.append({
                'id': item_id,
                'user_input': item.get('user_input', ''),
                'command': item.get('command', ''),
                'success': item.get('success', False),
                'output': item.get('output', ''),
                'error': item.get('error', ''),
                'execution_time': item.get('execution_time', 0.0),
                'timestamp': item.get('timestamp', datetime.now().isoformat())
            })
        
        response = {
            'success': True,
            'data': {
                'items': items,
                'total': total,
                'page': page,
                'limit': limit
            }
        }
        
        current_app.logger.info(f"Retrieved {len(items)} history items (page {page})")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve history: {str(e)}',
                'code': 500
            }
        }), 500


@history_bp.route('/<history_id>', methods=['GET'])
def get_history_detail(history_id):
    """
    Get detailed information for a specific history item
    
    GET /api/history/:id
    Response: HistoryItem
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        # Load history from storage
        history_data = assistant.storage.load_history()
        
        # Find the specific item
        item = None
        for idx, hist_item in enumerate(history_data):
            # Generate consistent ID if not present
            if 'id' not in hist_item or not hist_item['id']:
                timestamp = hist_item.get('timestamp', datetime.now().isoformat())
                item_id = f"hist_{timestamp.replace(':', '').replace('-', '').replace('.', '')[:20]}"
            else:
                item_id = hist_item['id']
            
            if item_id == history_id:
                item = hist_item
                item['id'] = item_id  # Ensure ID is in the item
                break
        
        if not item:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'History item not found: {history_id}',
                    'code': 404
                }
            }), 404
        
        response = {
            'success': True,
            'data': {
                'id': history_id,
                'user_input': item.get('user_input', ''),
                'command': item.get('command', ''),
                'success': item.get('success', False),
                'output': item.get('output', ''),
                'error': item.get('error', ''),
                'execution_time': item.get('execution_time', 0.0),
                'timestamp': item.get('timestamp', datetime.now().isoformat())
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving history detail: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve history detail: {str(e)}',
                'code': 500
            }
        }), 500


@history_bp.route('/<history_id>', methods=['DELETE'])
@csrf_protect
def delete_history(history_id):
    """
    Delete a history item
    
    DELETE /api/history/:id
    Response: Success message
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        # Load history from storage
        history_data = assistant.storage.load_history()
        
        # Find and remove the item
        found = False
        new_history = []
        for idx, item in enumerate(history_data):
            # Generate consistent ID if not present
            if 'id' not in item or not item['id']:
                timestamp = item.get('timestamp', datetime.now().isoformat())
                item_id = f"hist_{timestamp.replace(':', '').replace('-', '').replace('.', '')[:20]}"
                item['id'] = item_id  # Add ID to item for future consistency
            else:
                item_id = item['id']
            
            if item_id != history_id:
                new_history.append(item)
            else:
                found = True
        
        if not found:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'History item not found: {history_id}',
                    'code': 404
                }
            }), 404
        
        # Save updated history using batch save
        success = assistant.storage.save_history_batch(new_history)
        
        if not success:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Failed to save updated history',
                    'code': 500
                }
            }), 500
        
        response = {
            'success': True,
            'message': f'History item {history_id} deleted successfully'
        }
        
        current_app.logger.info(f"Deleted history item: {history_id}")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to delete history: {str(e)}',
                'code': 500
            }
        }), 500


@history_bp.route('', methods=['DELETE'])
@csrf_protect
def clear_all_history():
    """
    Clear all history records
    
    DELETE /api/history
    Response: Success message
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        # Clear all history
        success = assistant.storage.clear_history()
        
        if not success:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Failed to clear history',
                    'code': 500
                }
            }), 500
        
        response = {
            'success': True,
            'message': 'All history cleared successfully'
        }
        
        current_app.logger.info("Cleared all history")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error clearing history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to clear history: {str(e)}',
                'code': 500
            }
        }), 500
