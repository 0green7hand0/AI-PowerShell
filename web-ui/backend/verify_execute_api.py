"""
Verification script for Task 2.3: 实现命令执行 API
Tests the /api/command/execute endpoint
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_execute_simple_command():
    """Test 1: Execute a simple safe command"""
    print_section("Test 1: Execute Simple Command (Get-Date)")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": "Get-Date",
        "session_id": "test-session-001"
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'data' in data
            assert 'output' in data['data']
            assert 'execution_time' in data['data']
            assert 'return_code' in data['data']
            assert data['data']['return_code'] == 0
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_with_custom_timeout():
    """Test 2: Execute command with custom timeout"""
    print_section("Test 2: Execute with Custom Timeout")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": "Get-Process | Select-Object -First 5",
        "session_id": "test-session-002",
        "timeout": 60
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=65)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert data['data']['return_code'] == 0
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_command_with_output():
    """Test 3: Execute command that produces output"""
    print_section("Test 3: Execute Command with Output")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": "Write-Output 'Hello from PowerShell'",
        "session_id": "test-session-003"
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'Hello from PowerShell' in data['data']['output']
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_invalid_command():
    """Test 4: Execute invalid command (should return error)"""
    print_section("Test 4: Execute Invalid Command")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": "Invalid-CommandThatDoesNotExist",
        "session_id": "test-session-004"
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            # Command should execute but return error
            assert data['success'] is True
            assert data['data']['return_code'] != 0 or data['data']['error'] is not None
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_missing_fields():
    """Test 5: Execute with missing required fields"""
    print_section("Test 5: Execute with Missing Fields")
    
    url = f"{BASE_URL}/api/command/execute"
    
    # Test missing command
    payload = {
        "session_id": "test-session-005"
    }
    
    print(f"POST {url}")
    print(f"Request (missing command): {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            data = response.json()
            assert data['success'] is False
            print("✓ Test passed (correctly rejected missing command)!")
            return True
        else:
            print("✗ Test failed: Should return 400 for missing command")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_measures_time():
    """Test 6: Verify execution time is measured"""
    print_section("Test 6: Verify Execution Time Measurement")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": "Start-Sleep -Milliseconds 100",
        "session_id": "test-session-006"
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        start = time.time()
        response = requests.post(url, json=payload, timeout=10)
        elapsed = time.time() - start
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print(f"Client-side elapsed time: {elapsed:.3f}s")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'execution_time' in data['data']
            assert isinstance(data['data']['execution_time'], (int, float))
            assert data['data']['execution_time'] >= 0.1  # Should be at least 100ms
            print(f"Server-side execution time: {data['data']['execution_time']:.3f}s")
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def test_execute_multiline_command():
    """Test 7: Execute multiline command"""
    print_section("Test 7: Execute Multiline Command")
    
    url = f"{BASE_URL}/api/command/execute"
    payload = {
        "command": """$processes = Get-Process | Select-Object -First 3
Write-Output "Found $($processes.Count) processes"
$processes | Format-Table Name, Id""",
        "session_id": "test-session-007"
    }
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert data['data']['return_code'] == 0
            print("✓ Test passed!")
            return True
        else:
            print("✗ Test failed: Unexpected status code")
            return False
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        return False

def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("  Task 2.3 Verification: Command Execute API")
    print("="*60)
    print("\nTesting /api/command/execute endpoint...")
    print("Make sure the Flask server is running on http://localhost:5000")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server health check failed")
            return
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        print("\nPlease start the server with:")
        print("  cd web-ui/backend")
        print("  python app.py")
        return
    
    # Run tests
    results = []
    results.append(("Execute Simple Command", test_execute_simple_command()))
    results.append(("Execute with Custom Timeout", test_execute_with_custom_timeout()))
    results.append(("Execute Command with Output", test_execute_command_with_output()))
    results.append(("Execute Invalid Command", test_execute_invalid_command()))
    results.append(("Execute with Missing Fields", test_execute_missing_fields()))
    results.append(("Verify Execution Time", test_execute_measures_time()))
    results.append(("Execute Multiline Command", test_execute_multiline_command()))
    
    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Task 2.3 is complete.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")

if __name__ == "__main__":
    main()
