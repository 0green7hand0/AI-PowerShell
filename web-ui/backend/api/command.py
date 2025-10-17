"""
Command API endpoints for translation and execution
"""
import os
import sys
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from models.command import TranslateRequest, ExecuteRequest
from utils.validation import validate_and_sanitize_command_input, ValidationError as CustomValidationError
from api.csrf import csrf_protect

# Add parent directory to path to import PowerShellAssistant
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

command_bp = Blueprint('command', __name__)

# Global assistant instance (lazy loaded)
_assistant = None
_assistant_config_path = None


def get_assistant():
    """Get or create PowerShellAssistant instance"""
    global _assistant, _assistant_config_path
    
    # Config path
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'default.yaml'))
    
    # Recreate assistant if config path changed or not initialized
    if _assistant is None or _assistant_config_path != config_path:
        try:
            from src.main import PowerShellAssistant
            current_app.logger.info(f"Loading config from: {config_path}")
            _assistant = PowerShellAssistant(config_path=config_path)
            _assistant_config_path = config_path
            current_app.logger.info("PowerShellAssistant initialized successfully")
            current_app.logger.info(f"AI Provider: {_assistant.config.ai.provider}, Model: {_assistant.config.ai.model_name}")
            current_app.logger.info(f"Encoding: {_assistant.executor.encoding}")
        except Exception as e:
            current_app.logger.error(f"Failed to initialize PowerShellAssistant: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to initialize PowerShellAssistant: {str(e)}")
    return _assistant


@command_bp.route('/translate', methods=['POST'])
@csrf_protect
def translate_command():
    """
    Translate natural language to PowerShell command
    
    POST /api/command/translate
    Request body: TranslateRequest
    Response: TranslateResponse
    """
    try:
        # Validate request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Request body is required or invalid JSON',
                    'code': 400
                }
            }), 400
        
        translate_req = TranslateRequest(**data)
        
        # Validate and sanitize input
        try:
            sanitized_input = validate_and_sanitize_command_input(translate_req.input)
            translate_req.input = sanitized_input
        except CustomValidationError as e:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Input validation failed: {str(e)}',
                    'code': 400
                }
            }), 400
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Build context
        from src.interfaces.base import Context
        context = Context(
            session_id=translate_req.context.get('sessionId', 'web-session') if translate_req.context else 'web-session',
            working_directory=os.getcwd(),
            command_history=translate_req.context.get('history', []) if translate_req.context else []
        )
        
        # Translate using AI engine
        current_app.logger.info(f"📝 用户输入: {translate_req.input}")
        current_app.logger.info(f"🤖 开始 AI 翻译...")
        
        suggestion = assistant.ai_engine.translate_natural_language(translate_req.input, context)
        
        current_app.logger.info(f"✅ AI 生成命令: {suggestion.generated_command}")
        current_app.logger.info(f"📊 置信度: {suggestion.confidence_score * 100:.1f}%")
        
        # Perform security check
        current_app.logger.info(f"🔒 执行安全检查...")
        validation = assistant.security_engine.validate_command(suggestion.generated_command, context)
        
        # Map risk level to security level string
        risk_level_map = {
            'safe': 'safe',
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical'
        }
        
        security_level = risk_level_map.get(validation.risk_level.value, 'safe')
        
        # Log security result
        security_emoji = {
            'safe': '✅',
            'low': '⚠️',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '🛑'
        }
        current_app.logger.info(f"{security_emoji.get(security_level, '❓')} 安全级别: {security_level}")
        
        if validation.warnings:
            for warning in validation.warnings:
                current_app.logger.warning(f"⚠️ 安全警告: {warning}")
        
        response = {
            'success': True,
            'data': {
                'command': suggestion.generated_command,
                'confidence': suggestion.confidence_score,
                'explanation': suggestion.explanation,
                'security': {
                    'level': security_level,
                    'warnings': validation.warnings,
                    'requires_confirmation': validation.requires_confirmation,
                    'requires_elevation': validation.requires_elevation
                }
            }
        }
        
        current_app.logger.info(f"🎉 命令翻译完成")
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
    except RuntimeError as e:
        current_app.logger.error(f"Runtime error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 503
            }
        }), 503
    except Exception as e:
        current_app.logger.error(f"Translation error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Translation failed: {str(e)}',
                'code': 500
            }
        }), 500


@command_bp.route('/execute', methods=['POST'])
@csrf_protect
def execute_command():
    """
    Execute PowerShell command
    
    POST /api/command/execute
    Request body: ExecuteRequest
    Response: ExecuteResponse
    """
    try:
        # Validate request
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Request body is required or invalid JSON',
                    'code': 400
                }
            }), 400
        
        execute_req = ExecuteRequest(**data)
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Execute command with timeout
        current_app.logger.info(f"⚡ 开始执行命令: {execute_req.command}")
        start_time = time.time()
        
        result = assistant.executor.execute(
            execute_req.command,
            timeout=execute_req.timeout
        )
        
        execution_time = time.time() - start_time
        
        # Log execution result
        if result.success:
            current_app.logger.info(f"✅ 命令执行成功 (耗时: {execution_time:.2f}秒)")
            if result.output:
                output_preview = result.output[:100] + '...' if len(result.output) > 100 else result.output
                current_app.logger.info(f"📤 输出: {output_preview}")
        else:
            current_app.logger.error(f"❌ 命令执行失败: {result.error}")
        
        assistant.log_engine.log_execution(execute_req.command, result)
        
        # Save to history
        history_entry = {
            'id': f"hist_{int(time.time() * 1000)}",
            'user_input': '',  # Not available in execute endpoint
            'command': execute_req.command,
            'success': result.return_code == 0 and not result.error,
            'output': result.output or '',
            'error': result.error or '',
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Save single entry to history
            assistant.storage.save_history(history_entry)
            current_app.logger.info(f"Saved to history: {history_entry['id']}")
        except Exception as e:
            current_app.logger.warning(f"Failed to save history: {str(e)}")
        
        response = {
            'success': True,
            'data': {
                'output': result.output,
                'error': result.error,
                'executionTime': execution_time,
                'returnCode': result.return_code
            }
        }
        
        current_app.logger.info(f"Execution completed: return_code={result.return_code}")
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
    except RuntimeError as e:
        current_app.logger.error(f"Runtime error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 503
            }
        }), 503
    except Exception as e:
        current_app.logger.error(f"Execution error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Execution failed: {str(e)}',
                'code': 500
            }
        }), 500
