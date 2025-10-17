"""
Template API endpoints for managing PowerShell script templates
"""
import os
import sys
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError

from models.template import GenerateScriptRequest, Template as TemplateModel, TemplateParameter
from api.csrf import csrf_protect

# Add parent directory to path to import PowerShellAssistant
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

template_bp = Blueprint('template', __name__)


def get_assistant():
    """Get PowerShellAssistant instance from command API"""
    from api.command import get_assistant as get_cmd_assistant
    return get_cmd_assistant()


def get_sample_templates():
    """
    Get sample templates for demonstration
    
    Returns:
        List of sample template objects
    """
    from types import SimpleNamespace
    
    samples = [
        SimpleNamespace(
            name="backup_files",
            description="自动备份指定文件夹到目标位置，支持增量备份和压缩",
            category="automation",
            script_content='Copy-Item -Path {{sourcePath}} -Destination {{targetPath}} -Recurse',
            parameters=[
                SimpleNamespace(name="sourcePath", type="string", required=True, default="", description="源文件夹路径"),
                SimpleNamespace(name="targetPath", type="string", required=True, default="", description="目标文件夹路径"),
            ],
            keywords=["backup", "copy", "files"]
        ),
        SimpleNamespace(
            name="disk_cleanup",
            description="清理磁盘空间，删除临时文件和缓存",
            category="automation",
            script_content='Remove-Item -Path {{path}} -Recurse -Force',
            parameters=[
                SimpleNamespace(name="path", type="string", required=True, default="C:\\Temp", description="要清理的路径"),
            ],
            keywords=["cleanup", "disk", "temp"]
        ),
        SimpleNamespace(
            name="batch_rename",
            description="批量重命名文件，支持正则表达式替换",
            category="file_management",
            script_content='Get-ChildItem -Path {{path}} | Rename-Item -NewName {$_.Name -replace "{{pattern}}", "{{replacement}}"}',
            parameters=[
                SimpleNamespace(name="path", type="string", required=True, default="", description="文件路径"),
                SimpleNamespace(name="pattern", type="string", required=True, default="", description="匹配模式"),
                SimpleNamespace(name="replacement", type="string", required=True, default="", description="替换文本"),
            ],
            keywords=["rename", "batch", "files"]
        ),
        SimpleNamespace(
            name="resource_monitor",
            description="监控系统资源使用情况（CPU、内存、磁盘）",
            category="system_monitoring",
            script_content='Get-Process | Sort-Object CPU -Descending | Select-Object -First {{count}}',
            parameters=[
                SimpleNamespace(name="count", type="number", required=False, default=10, description="显示进程数量"),
            ],
            keywords=["monitor", "cpu", "memory", "performance"]
        ),
    ]
    
    return samples


def validate_template_data(data):
    """
    Validate template data
    
    Args:
        data: Template data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['name', 'description', 'script_content']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate name length
    if len(data['name']) > 100:
        return False, "Template name too long (max 100 characters)"
    
    # Validate category
    if 'category' in data:
        category = data['category']
        if not category or not isinstance(category, str):
            return False, "Invalid category"
        
        # Check category name format
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', category):
            return False, "Category name can only contain letters, numbers, underscores and hyphens"
    
    # Validate script content
    if len(data['script_content']) < 10:
        return False, "Script content too short (minimum 10 characters)"
    
    return True, None


@template_bp.route('', methods=['GET'])
def get_templates():
    """
    Get list of templates with optional filtering
    
    GET /api/templates?category=automation&search=backup
    Response: List of templates
    """
    try:
        # Get query parameters
        category = request.args.get('category', '').lower()
        search = request.args.get('search', '').lower()
        
        # Get assistant instance
        assistant = get_assistant()
        
        # Try to get templates from custom template manager
        templates = []
        if hasattr(assistant, 'custom_template_manager') and assistant.custom_template_manager:
            try:
                templates = assistant.custom_template_manager.list_custom_templates()
            except Exception as e:
                current_app.logger.warning(f"Failed to list custom templates: {str(e)}")
        
        # If no templates found, return sample templates for demonstration
        if not templates:
            current_app.logger.info("No custom templates found, returning sample templates")
            templates = get_sample_templates()
        
        # Filter by category if provided
        if category:
            templates = [t for t in templates if t.category.lower() == category]
        
        # Filter by search query if provided
        if search:
            templates = [
                t for t in templates
                if search in t.name.lower() or
                   search in t.description.lower() or
                   any(search in kw.lower() for kw in getattr(t, 'keywords', []))
            ]
        
        # Format templates for response
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.name,  # Use name as ID for now
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'script_content': template.script_content,
                'parameters': [
                    {
                        'name': p.name,
                        'type': p.type,
                        'required': p.required,
                        'default': p.default,
                        'description': p.description
                    }
                    for p in template.parameters
                ],
                'keywords': getattr(template, 'keywords', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
        
        response = {
            'success': True,
            'data': {
                'items': template_list,
                'total': len(template_list)
            }
        }
        
        current_app.logger.info(f"Retrieved {len(template_list)} templates")
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving templates: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve templates: {str(e)}',
                'code': 500
            }
        }), 500


@template_bp.route('/<template_id>', methods=['GET'])
def get_template_detail(template_id):
    """
    Get detailed information for a specific template
    
    GET /api/templates/:id
    Response: Template
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        if not assistant.custom_template_manager:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Template manager not initialized',
                    'code': 503
                }
            }), 503
        
        # Get template info
        template = assistant.custom_template_manager.get_template_info(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Template not found: {template_id}',
                    'code': 404
                }
            }), 404
        
        response = {
            'success': True,
            'data': {
                'id': template.name,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'script_content': template.script_content,
                'parameters': [
                    {
                        'name': p.name,
                        'type': p.type,
                        'required': p.required,
                        'default': p.default,
                        'description': p.description
                    }
                    for p in template.parameters
                ],
                'keywords': getattr(template, 'keywords', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving template detail: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to retrieve template: {str(e)}',
                'code': 500
            }
        }), 500


@template_bp.route('', methods=['POST'])
@csrf_protect
def create_template():
    """
    Create a new template
    
    POST /api/templates
    Request body: Template
    Response: Created template
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Request body is required',
                    'code': 400
                }
            }), 400
        
        # Validate template data
        is_valid, error_msg = validate_template_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': {
                    'message': error_msg,
                    'code': 400
                }
            }), 400
        
        # Get assistant instance
        assistant = get_assistant()
        
        if not assistant.custom_template_manager:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Template manager not initialized',
                    'code': 503
                }
            }), 503
        
        # Extract template data
        name = data.get('name')
        description = data.get('description')
        category = data.get('category', 'custom')
        script_content = data.get('script_content')
        keywords = data.get('keywords', [])
        author = data.get('author', 'user')
        tags = data.get('tags', [])
        
        # Create template using custom template manager
        template = assistant.custom_template_manager.create_template(
            name=name,
            description=description,
            category=category,
            script_content=script_content,
            keywords=keywords,
            author=author,
            tags=tags
        )
        
        response = {
            'success': True,
            'data': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'message': 'Template created successfully'
            }
        }
        
        current_app.logger.info(f"Created template: {name} (ID: {template.id})")
        return jsonify(response), 201
        
    except ValueError as e:
        # Handle validation errors from template manager
        current_app.logger.warning(f"Template validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 400
            }
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error creating template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to create template: {str(e)}',
                'code': 500
            }
        }), 500


@template_bp.route('/<template_id>', methods=['PUT'])
@csrf_protect
def update_template(template_id):
    """
    Update an existing template
    
    PUT /api/templates/:id
    Request body: Partial template data
    Response: Updated template
    """
    try:
        data = request.get_json()
        
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
        
        if not assistant.custom_template_manager:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Template manager not initialized',
                    'code': 503
                }
            }), 503
        
        # Get template info to determine category
        try:
            template_info = assistant.custom_template_manager.get_template_info(template_id, data.get('category', 'custom'))
            category = template_info.get('category', 'custom')
        except Exception:
            # If template not found with provided category, try to find it
            categories = assistant.custom_template_manager.list_categories(include_system=False)
            found = False
            for cat in categories:
                try:
                    template_info = assistant.custom_template_manager.get_template_info(template_id, cat['name'])
                    category = cat['name']
                    found = True
                    break
                except Exception:
                    continue
            
            if not found:
                return jsonify({
                    'success': False,
                    'error': {
                        'message': f'Template not found: {template_id}',
                        'code': 404
                    }
                }), 404
        
        # Build updates dictionary
        updates = {}
        if 'name' in data:
            updates['name'] = data['name']
        if 'description' in data:
            updates['description'] = data['description']
        if 'keywords' in data:
            updates['keywords'] = data['keywords']
        if 'tags' in data:
            updates['tags'] = data['tags']
        if 'script_content' in data:
            updates['content'] = data['script_content']
        if 'parameters' in data:
            updates['parameters'] = data['parameters']
        
        # Update template
        template = assistant.custom_template_manager.edit_template(template_id, category, updates)
        
        response = {
            'success': True,
            'data': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'message': 'Template updated successfully'
            }
        }
        
        current_app.logger.info(f"Updated template: {template_id}")
        return jsonify(response), 200
        
    except ValueError as e:
        current_app.logger.warning(f"Template validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 400
            }
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error updating template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to update template: {str(e)}',
                'code': 500
            }
        }), 500


@template_bp.route('/<template_id>', methods=['DELETE'])
@csrf_protect
def delete_template(template_id):
    """
    Delete a template
    
    DELETE /api/templates/:id
    Query params: category (optional)
    Response: Success message
    """
    try:
        # Get assistant instance
        assistant = get_assistant()
        
        if not assistant.custom_template_manager:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Template manager not initialized',
                    'code': 503
                }
            }), 503
        
        # Get category from query params or try to find the template
        category = request.args.get('category', 'custom')
        
        # Try to find template if category not provided
        if not category or category == 'custom':
            categories = assistant.custom_template_manager.list_categories(include_system=False)
            found = False
            for cat in categories:
                try:
                    assistant.custom_template_manager.get_template_info(template_id, cat['name'])
                    category = cat['name']
                    found = True
                    break
                except Exception:
                    continue
            
            if not found:
                return jsonify({
                    'success': False,
                    'error': {
                        'message': f'Template not found: {template_id}',
                        'code': 404
                    }
                }), 404
        
        # Delete template
        success = assistant.custom_template_manager.delete_template(template_id, category)
        
        if not success:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Template not found: {template_id}',
                    'code': 404
                }
            }), 404
        
        response = {
            'success': True,
            'message': f'Template {template_id} deleted successfully'
        }
        
        current_app.logger.info(f"Deleted template: {template_id} from category: {category}")
        return jsonify(response), 200
        
    except ValueError as e:
        current_app.logger.warning(f"Template deletion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'message': str(e),
                'code': 400
            }
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error deleting template: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to delete template: {str(e)}',
                'code': 500
            }
        }), 500


@template_bp.route('/<template_id>/generate', methods=['POST'])
@csrf_protect
def generate_script(template_id):
    """
    Generate a script from a template with provided parameters
    
    POST /api/templates/:id/generate
    Request body: GenerateScriptRequest
    Response: Generated script
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Request body is required',
                    'code': 400
                }
            }), 400
        
        generate_req = GenerateScriptRequest(**data)
        
        # Get assistant instance
        assistant = get_assistant()
        
        if not assistant.custom_template_manager:
            return jsonify({
                'success': False,
                'error': {
                    'message': 'Template manager not initialized',
                    'code': 503
                }
            }), 503
        
        # Get template
        template = assistant.custom_template_manager.get_template_info(template_id)
        
        if not template:
            return jsonify({
                'success': False,
                'error': {
                    'message': f'Template not found: {template_id}',
                    'code': 404
                }
            }), 404
        
        # Generate script by replacing parameters
        script_content = template.script_content
        
        for param_name, param_value in generate_req.parameters.items():
            # Replace {{param_name}} with actual value
            placeholder = f"{{{{{param_name}}}}}"
            script_content = script_content.replace(placeholder, str(param_value))
        
        response = {
            'success': True,
            'data': {
                'script': script_content,
                'template_name': template.name,
                'parameters': generate_req.parameters,
                'message': 'Script generated successfully'
            }
        }
        
        current_app.logger.info(f"Generated script from template: {template_id}")
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
        current_app.logger.error(f"Error generating script: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'message': f'Failed to generate script: {str(e)}',
                'code': 500
            }
        }), 500
