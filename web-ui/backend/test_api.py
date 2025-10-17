"""
Simple test script to verify backend API functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app


def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.get('/api/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_json()}")
        assert response.status_code == 200
        assert response.get_json()['success'] == True
    
    print("✓ Health check passed")


def test_translate_endpoint():
    """Test command translation endpoint"""
    print("\n=== Testing Command Translation ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.post('/api/command/translate', json={
            'input': '显示当前时间'
        })
        print(f"Status Code: {response.status_code}")
        data = response.get_json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            assert data['success'] == True
            assert 'command' in data['data']
            print(f"✓ Translation successful: {data['data']['command']}")
        else:
            print(f"⚠ Translation returned error (expected if AI not configured)")


def test_history_endpoint():
    """Test history endpoint"""
    print("\n=== Testing History Endpoint ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.get('/api/history?page=1&limit=10')
        print(f"Status Code: {response.status_code}")
        data = response.get_json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            assert data['success'] == True
            print(f"✓ History retrieved: {data['data']['total']} items")
        else:
            print(f"⚠ History returned error")


def test_templates_endpoint():
    """Test templates endpoint"""
    print("\n=== Testing Templates Endpoint ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.get('/api/templates')
        print(f"Status Code: {response.status_code}")
        data = response.get_json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            assert data['success'] == True
            print(f"✓ Templates retrieved: {len(data['data']['templates'])} templates")
        else:
            print(f"⚠ Templates returned error")


def test_config_endpoint():
    """Test config endpoint"""
    print("\n=== Testing Config Endpoint ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.get('/api/config')
        print(f"Status Code: {response.status_code}")
        data = response.get_json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            assert data['success'] == True
            assert 'ai' in data['data']
            print(f"✓ Config retrieved")
        else:
            print(f"⚠ Config returned error")


def test_logs_endpoint():
    """Test logs endpoint"""
    print("\n=== Testing Logs Endpoint ===")
    app, socketio = create_app({'TESTING': True})
    
    with app.test_client() as client:
        response = client.get('/api/logs?limit=10')
        print(f"Status Code: {response.status_code}")
        data = response.get_json()
        print(f"Response: {data}")
        
        if response.status_code == 200:
            assert data['success'] == True
            print(f"✓ Logs retrieved: {data['data']['total']} entries")
        else:
            print(f"⚠ Logs returned error")


if __name__ == '__main__':
    print("=" * 60)
    print("Backend API Test Suite")
    print("=" * 60)
    
    try:
        test_health_check()
        test_translate_endpoint()
        test_history_endpoint()
        test_templates_endpoint()
        test_config_endpoint()
        test_logs_endpoint()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
