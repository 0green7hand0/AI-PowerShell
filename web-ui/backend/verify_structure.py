"""
Verification script to check Flask app structure without running it
"""
import os
import sys
import ast

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False

def check_function_in_file(filepath, function_name):
    """Check if a function exists in a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    print(f"  ✓ Function '{function_name}' found")
                    return True
        print(f"  ✗ Function '{function_name}' NOT FOUND")
        return False
    except Exception as e:
        print(f"  ✗ Error checking function: {e}")
        return False

def check_route_in_file(filepath, route_path):
    """Check if a route exists in a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if route_path in content:
                print(f"  ✓ Route '{route_path}' found")
                return True
            else:
                print(f"  ✗ Route '{route_path}' NOT FOUND")
                return False
    except Exception as e:
        print(f"  ✗ Error checking route: {e}")
        return False

def main():
    print("=" * 70)
    print("Flask Application Structure Verification")
    print("=" * 70)
    
    all_checks_passed = True
    
    # Check main app.py file
    print("\n1. Checking main application file...")
    app_file = "app.py"
    if check_file_exists(app_file, "Main app file"):
        check_function_in_file(app_file, "create_app")
        check_route_in_file(app_file, "/api/health")
    else:
        all_checks_passed = False
    
    # Check blueprints
    print("\n2. Checking API blueprints...")
    blueprints = [
        ("api/command.py", "Command API", "command_bp"),
        ("api/history.py", "History API", "history_bp"),
        ("api/template.py", "Template API", "template_bp"),
        ("api/config.py", "Config API", "config_bp"),
        ("api/logs.py", "Logs API", "logs_bp"),
    ]
    
    for filepath, description, blueprint_name in blueprints:
        if check_file_exists(filepath, description):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if blueprint_name in content:
                    print(f"  ✓ Blueprint '{blueprint_name}' found")
                else:
                    print(f"  ✗ Blueprint '{blueprint_name}' NOT FOUND")
                    all_checks_passed = False
        else:
            all_checks_passed = False
    
    # Check models
    print("\n3. Checking data models...")
    models = [
        ("models/command.py", "Command models"),
        ("models/history.py", "History models"),
        ("models/template.py", "Template models"),
        ("models/config.py", "Config models"),
    ]
    
    for filepath, description in models:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check app.py structure
    print("\n4. Checking app.py implementation details...")
    with open("app.py", 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    required_components = [
        ("CORS configuration", "CORS(app"),
        ("SocketIO initialization", "SocketIO(app"),
        ("Blueprint registration", "register_blueprint"),
        ("Health check endpoint", "@app.route('/api/health')"),
        ("Error handler for APIException", "@app.errorhandler(APIException)"),
        ("Error handler for ValidationError", "@app.errorhandler(ValidationError)"),
        ("Error handler for 404", "@app.errorhandler(404)"),
        ("Error handler for 500", "@app.errorhandler(500)"),
        ("Generic error handler", "@app.errorhandler(Exception)"),
    ]
    
    for component_name, search_string in required_components:
        if search_string in app_content:
            print(f"  ✓ {component_name}")
        else:
            print(f"  ✗ {component_name} NOT FOUND")
            all_checks_passed = False
    
    # Check exception classes
    print("\n5. Checking exception classes...")
    exception_classes = [
        "APIException",
        "ValidationException",
        "CommandExecutionException",
        "ResourceNotFoundException"
    ]
    
    for exc_class in exception_classes:
        if f"class {exc_class}" in app_content:
            print(f"  ✓ Exception class '{exc_class}'")
        else:
            print(f"  ✗ Exception class '{exc_class}' NOT FOUND")
            all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 70)
    if all_checks_passed:
        print("✓ ALL CHECKS PASSED - Flask application structure is complete!")
    else:
        print("⚠ SOME CHECKS FAILED - Review the output above")
    print("=" * 70)
    
    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    sys.exit(main())
