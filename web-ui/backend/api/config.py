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


def camel_to_snake(name):
    """
    Convert camelCase string to snake_case
    
    @param name: camelCase string
    @return: snake_case string
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


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
                    'whitelistMode': config.security.whitelist_mode == 'strict',  # Convert to camelCase
                    'requireConfirmation': config.security.require_confirmation,  # Convert to camelCase
                    'dangerousPatterns': []  # Convert to camelCase
                },
                'execution': {
                    'timeout': config.execution.timeout,
                    'shellType': config.execution.platform,  # Rename to shellType for frontend
                    'encoding': config.execution.encoding,
                    'workingDirectory': config.execution.powershell_path,  # Rename to workingDirectory for frontend
                    'autoDetectPowershell': config.execution.auto_detect_powershell  # Convert to camelCase
                },
                'general': {
                    'language': 'zh-CN',  # Default
                    'theme': 'light',  # Default
                    'logLevel': config.logging.level,  # Convert to camelCase
                    'autoSave': True  # Default
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
            # Support both camelCase and snake_case for model name
            if 'model_name' in ai_config:
                updates['ai.model_name'] = ai_config['model_name']
            elif 'modelName' in ai_config:
                updates['ai.model_name'] = ai_config['modelName']
            if 'temperature' in ai_config:
                updates['ai.temperature'] = ai_config['temperature']
            # Support both camelCase and snake_case for max tokens
            if 'max_tokens' in ai_config:
                updates['ai.max_tokens'] = ai_config['max_tokens']
            elif 'maxTokens' in ai_config:
                updates['ai.max_tokens'] = ai_config['maxTokens']
        
        if 'security' in data:
            sec_config = data['security']
            # Support both camelCase and snake_case for whitelist mode
            if 'whitelist_mode' in sec_config:
                updates['security.whitelist_mode'] = 'strict' if sec_config['whitelist_mode'] else 'permissive'
            elif 'whitelistMode' in sec_config:
                updates['security.whitelist_mode'] = 'strict' if sec_config['whitelistMode'] else 'permissive'
            # Support both camelCase and snake_case for require confirmation
            if 'require_confirmation' in sec_config:
                updates['security.require_confirmation'] = sec_config['require_confirmation']
            elif 'requireConfirmation' in sec_config:
                updates['security.require_confirmation'] = sec_config['requireConfirmation']
        
        if 'execution' in data:
            exec_config = data['execution']
            if 'timeout' in exec_config:
                updates['execution.timeout'] = exec_config['timeout']
            # Support both camelCase and snake_case for platform (shellType in frontend)
            if 'platform' in exec_config:
                updates['execution.platform'] = exec_config['platform']
            elif 'shellType' in exec_config:
                updates['execution.platform'] = exec_config['shellType']
            if 'encoding' in exec_config:
                updates['execution.encoding'] = exec_config['encoding']
            # Support both camelCase and snake_case for powershell path
            if 'powershell_path' in exec_config:
                updates['execution.powershell_path'] = exec_config['powershell_path']
            elif 'powershellPath' in exec_config:
                updates['execution.powershell_path'] = exec_config['powershellPath']
            # Support both camelCase and snake_case for auto detect powershell
            if 'auto_detect_powershell' in exec_config:
                updates['execution.auto_detect_powershell'] = exec_config['auto_detect_powershell']
            elif 'autoDetectPowershell' in exec_config:
                updates['execution.auto_detect_powershell'] = exec_config['autoDetectPowershell']
        
        if 'general' in data:
            gen_config = data['general']
            # Support both camelCase and snake_case for language
            if 'language' in gen_config:
                # Language is not directly in config, but we can handle it if needed
                pass
            # Support both camelCase and snake_case for theme
            if 'theme' in gen_config:
                # Theme is not directly in config, but we can handle it if needed
                pass
            # Support both camelCase and snake_case for log level
            if 'log_level' in gen_config:
                updates['logging.level'] = gen_config['log_level']
            elif 'logLevel' in gen_config:
                updates['logging.level'] = gen_config['logLevel']
        
        # Convert dot-notation keys to nested dictionary
        nested_updates = {}
        for key, value in updates.items():
            parts = key.split('.')
            current = nested_updates
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        
        # Apply updates using config manager
        assistant.config_manager.update_config(nested_updates)
        
        # Save updated config
        assistant.config_manager.save_config(assistant.config_manager.get_config())
        
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


@config_bp.route('/reset', methods=['POST'])
@csrf_protect
def reset_config():
    """
    Reset configuration to default values
    
    POST /api/config/reset
    Response: Default AppConfig
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        # Reset config using config manager
        assistant.config_manager.reset_config()
        
        # Reload config
        assistant.config = assistant.config_manager.load_config()
        
        # Format response (convert snake_case to camelCase for frontend)
        response = {
            'success': True,
            'data': {
                'ai': {
                    'provider': assistant.config.ai.provider,
                    'modelName': assistant.config.ai.model_name,  # Convert to camelCase
                    'temperature': assistant.config.ai.temperature,
                    'maxTokens': assistant.config.ai.max_tokens  # Convert to camelCase
                },
                'security': {
                    'whitelistMode': assistant.config.security.whitelist_mode == 'strict',  # Convert to camelCase
                    'requireConfirmation': assistant.config.security.require_confirmation,  # Convert to camelCase
                    'dangerousPatterns': []  # Convert to camelCase
                },
                'execution': {
                    'timeout': assistant.config.execution.timeout,
                    'shellType': assistant.config.execution.platform,  # Rename to shellType for frontend
                    'encoding': assistant.config.execution.encoding,
                    'workingDirectory': assistant.config.execution.powershell_path,  # Rename to workingDirectory for frontend
                    'autoDetectPowershell': assistant.config.execution.auto_detect_powershell  # Convert to camelCase
                },
                'general': {
                    'language': 'zh-CN',  # Default
                    'theme': 'light',  # Default
                    'logLevel': assistant.config.logging.level,  # Convert to camelCase
                    'autoSave': True  # Default
                }
            },
            'message': 'Configuration reset to default values'
        }
        
        current_app.logger.info("Configuration reset to defaults")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error resetting config: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to reset configuration: {str(e)}',
                'code': 500
            }
        }), 500
