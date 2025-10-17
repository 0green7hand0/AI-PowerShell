"""
Simple test to verify all imports work correctly
"""
import sys

print("Testing imports...")

try:
    print("1. Testing Flask imports...")
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from flask_socketio import SocketIO
    print("   ✓ Flask imports successful")
except ImportError as e:
    print(f"   ✗ Flask import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing Pydantic imports...")
    from pydantic import BaseModel, Field, ValidationError
    print("   ✓ Pydantic imports successful")
except ImportError as e:
    print(f"   ✗ Pydantic import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing models...")
    from models.command import TranslateRequest, ExecuteRequest, SecurityInfo
    from models.history import HistoryItem, HistoryListResponse
    from models.template import Template, TemplateParameter, GenerateScriptRequest
    from models.config import AppConfig
    print("   ✓ Models import successful")
except ImportError as e:
    print(f"   ✗ Models import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing API blueprints...")
    from api.command import command_bp
    from api.history import history_bp
    from api.template import template_bp
    from api.config import config_bp
    from api.logs import logs_bp
    print("   ✓ API blueprints import successful")
except ImportError as e:
    print(f"   ✗ API blueprints import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing app creation...")
    from app import create_app
    app, socketio = create_app()
    print("   ✓ App creation successful")
    print(f"   ✓ Registered routes: {len(app.url_map._rules)} routes")
except Exception as e:
    print(f"   ✗ App creation failed: {e}")
    sys.exit(1)

print("\n✓ All tests passed! Backend is ready to run.")
print("\nTo start the server, run:")
print("  python app.py")
print("  or")
print("  run.bat (Windows)")
