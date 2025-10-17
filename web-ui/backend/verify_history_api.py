"""
Verification script for History API endpoints
Tests all history API functionality
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_response(response):
    """Print response details"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200


def test_get_empty_history():
    """Test getting history when empty"""
    print_section("2. Get Empty History")
    response = requests.get(f"{BASE_URL}/history")
    print_response(response)
    return response.status_code == 200


def test_create_history_via_command():
    """Create some history by executing commands"""
    print_section("3. Create History via Command Execution")
    
    # Translate and execute a few commands
    commands = [
        "显示当前时间",
        "列出当前目录文件",
        "显示系统信息"
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        
        # Translate
        translate_response = requests.post(
            f"{BASE_URL}/command/translate",
            json={"input": cmd}
        )
        
        if translate_response.status_code == 200:
            data = translate_response.json()
            if data.get('success'):
                command = data['data']['command']
                print(f"  Translated to: {command}")
                
                # Execute
                execute_response = requests.post(
                    f"{BASE_URL}/command/execute",
                    json={"command": command, "session_id": "test-session"}
                )
                
                if execute_response.status_code == 200:
                    print(f"  ✓ Executed successfully")
                else:
                    print(f"  ✗ Execution failed")
        
        time.sleep(0.5)
    
    print()
    return True


def test_get_history_list():
    """Test getting history list"""
    print_section("4. Get History List")
    response = requests.get(f"{BASE_URL}/history")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            items = data['data']['items']
            print(f"Found {len(items)} history items")
            return items
    return []


def test_pagination():
    """Test pagination"""
    print_section("5. Test Pagination")
    
    # Get first page
    print("Page 1 (limit=2):")
    response = requests.get(f"{BASE_URL}/history?page=1&limit=2")
    print_response(response)
    
    # Get second page
    print("Page 2 (limit=2):")
    response = requests.get(f"{BASE_URL}/history?page=2&limit=2")
    print_response(response)
    
    return response.status_code == 200


def test_search():
    """Test search functionality"""
    print_section("6. Test Search")
    
    # Search for "时间"
    print("Search for '时间':")
    response = requests.get(f"{BASE_URL}/history?search=时间")
    print_response(response)
    
    # Search for "Get-Date"
    print("Search for 'Get-Date':")
    response = requests.get(f"{BASE_URL}/history?search=Get-Date")
    print_response(response)
    
    return response.status_code == 200


def test_get_history_detail(history_id):
    """Test getting history detail"""
    print_section("7. Get History Detail")
    print(f"Getting detail for ID: {history_id}")
    response = requests.get(f"{BASE_URL}/history/{history_id}")
    print_response(response)
    return response.status_code == 200


def test_delete_history(history_id):
    """Test deleting a history item"""
    print_section("8. Delete History Item")
    print(f"Deleting history ID: {history_id}")
    response = requests.delete(f"{BASE_URL}/history/{history_id}")
    print_response(response)
    
    # Verify deletion
    if response.status_code == 200:
        print("Verifying deletion...")
        verify_response = requests.get(f"{BASE_URL}/history/{history_id}")
        print_response(verify_response)
        return verify_response.status_code == 404
    
    return False


def test_clear_all_history():
    """Test clearing all history"""
    print_section("9. Clear All History")
    response = requests.delete(f"{BASE_URL}/history")
    print_response(response)
    
    # Verify all cleared
    if response.status_code == 200:
        print("Verifying all history cleared...")
        verify_response = requests.get(f"{BASE_URL}/history")
        print_response(verify_response)
        data = verify_response.json()
        return data['data']['total'] == 0
    
    return False


def test_error_handling():
    """Test error handling"""
    print_section("10. Test Error Handling")
    
    # Test getting non-existent history
    print("Getting non-existent history:")
    response = requests.get(f"{BASE_URL}/history/nonexistent_id")
    print_response(response)
    
    # Test deleting non-existent history
    print("Deleting non-existent history:")
    response = requests.delete(f"{BASE_URL}/history/nonexistent_id")
    print_response(response)
    
    return True


def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("  History API Verification")
    print("="*60)
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("Press Enter to continue...")
    input()
    
    results = []
    
    # Run tests
    try:
        results.append(("Health Check", test_health_check()))
        results.append(("Get Empty History", test_get_empty_history()))
        results.append(("Create History", test_create_history_via_command()))
        
        # Get history items for further testing
        history_items = test_get_history_list()
        results.append(("Get History List", len(history_items) > 0))
        
        results.append(("Pagination", test_pagination()))
        results.append(("Search", test_search()))
        
        # Test detail and delete if we have items
        if history_items:
            history_id = history_items[0]['id']
            results.append(("Get History Detail", test_get_history_detail(history_id)))
            results.append(("Delete History", test_delete_history(history_id)))
        
        results.append(("Error Handling", test_error_handling()))
        
        # Don't clear all history by default - uncomment if needed
        # results.append(("Clear All History", test_clear_all_history()))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure the Flask server is running on http://localhost:5000")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
