"""
Configuration API endpoints for managing application settings
"""
import os
import sys
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from models.config import AppConfig
from api.csrf import csrf_protect

# Add parent directory to path to import PowerShellAssistant
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

config_bp = Blueprint('config', __name__)


def get_assistant():
    """Get PowerShellAssistant instance from command API"""
    from api.command import get_assistant as get_cmd_assistant
    return get_cmd_assistant()


@config_bp.route('', methods=['GET'])
def get_config():
    """
    Get current application configuration
    
    GET /api/config
    Response: AppConfig
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        # Get current config
        config = assistant.config
        
        # Format response (convert snake_case to camelCase for frontend)
        response = {
            'success': True,
            'data': {
                'ai': {
                    'provider': config.ai.provider,
                    'modelName': config.ai.model_name,  # Convert to camelCase
                    'temperature': config.ai.temperature,
                    'maxTokens': config.ai.max_tokens  # Convert to camelCase
                },
                'security': {
                    'whitelist_mode': config.security.whitelist_mode == 'strict',
                    'require_confirmation': config.security.require_confirmation,
                    'dangerous_patterns': []  # Not directly exposed in config
                },
                'execution': {
                    'timeout': config.execution.timeout,
                    'platform': config.execution.platform,
                    'encoding': config.execution.encoding,
                    'powershell_path': config.execution.powershell_path,
                    'auto_detect_powershell': config.execution.auto_detect_powershell
                },
                'general': {
                    'language': 'zh-CN',  # Default
                    'theme': 'light',  # Default
                    'log_level': config.logging.level
                }
            }
        }
        
        current_app.logger.info("Retrieved configuration")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving config: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve configuration: {str(e)}',
                'code': 500
            }
        }), 500


@config_bp.route('', methods=['PUT'])
@csrf_protect
def update_config():
    """
    Update application configuration
    
    PUT /api/config
    Request body: Partial AppConfig
    Response: Updated configuration
    """
    try:
        # Handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception as e:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Invalid JSON in request body',
                    'code': 400
                }
            }), 400
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Request body is required',
                    'code': 400
                }
            }), 400
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Update configuration sections
        updates = {}
        
        if 'ai' in data:
            ai_config = data['ai']
            if 'provider' in ai_config:
                updates['ai.provider'] = ai_config['provider']
            if 'model_name' in ai_config:
                updates['ai.model_name'] = ai_config['model_name']
            if 'temperature' in ai_config:
                updates['ai.temperature'] = ai_config['temperature']
            if 'max_tokens' in ai_config:
                updates['ai.max_tokens'] = ai_config['max_tokens']
        
        if 'security' in data:
            sec_config = data['security']
            if 'whitelist_mode' in sec_config:
                updates['security.whitelist_mode'] = 'strict' if sec_config['whitelist_mode'] else 'permissive'
            if 'require_confirmation' in sec_config:
                updates['security.require_confirmation'] = sec_config['require_confirmation']
        
        if 'execution' in data:
            exec_config = data['execution']
            if 'timeout' in exec_config:
                updates['execution.timeout'] = exec_config['timeout']
            if 'platform' in exec_config:
                updates['execution.platform'] = exec_config['platform']
            if 'encoding' in exec_config:
                updates['execution.encoding'] = exec_config['encoding']
            if 'powershell_path' in exec_config:
                updates['execution.powershell_path'] = exec_config['powershell_path']
            if 'auto_detect_powershell' in exec_config:
                updates['execution.auto_detect_powershell'] = exec_config['auto_detect_powershell']
        
        if 'general' in data:
            gen_config = data['general']
            if 'log_level' in gen_config:
                updates['logging.level'] = gen_config['log_level']
        
        # Apply updates using config manager
        for key, value in updates.items():
            assistant.config_manager.update_config(key, value)
        
        # Reload config
        assistant.config = assistant.config_manager.load_config()
        
        response = {
            'success': True,
            'data': data,
            'message': 'Configuration updated successfully. Some changes may require restart.'
        }
        
        current_app.logger.info(f"Updated configuration: {list(updates.keys())}")
        return jsonify(response), 200
        
    except ValidationError as e:
        current_app.logger.warning(f"Validation error: {e.errors()}")
        return jsonify({
            'success': False,
            'error': {
                'message': 'Validation error',
                'details': e.errors(),
                'code': 400
            }
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error updating config: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to update configuration: {str(e)}',
                'code': 500
            }
        }), 500
