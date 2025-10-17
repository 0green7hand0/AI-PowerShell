"""
Tests for validation utilities
"""
import pytest
from utils.validation import (
    sanitize_html,
    is_valid_command_input,
    is_valid_file_path,
    is_valid_username,
    is_valid_email,
    is_strong_password,
    sanitize_input,
    is_valid_port,
    is_valid_ipv4,
    ValidationError,
    validate_and_sanitize_command_input,
    validate_and_sanitize_file_path
)


def test_sanitize_html():
    """Test HTML sanitization"""
    assert sanitize_html('<script>alert("xss")</script>') == '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
    assert sanitize_html('Hello <b>World</b>') == 'Hello &lt;b&gt;World&lt;/b&gt;'
    assert sanitize_html('Normal text') == 'Normal text'


def test_is_valid_command_input():
    """Test command input validation"""
    # Valid inputs
    assert is_valid_command_input('Get-Process')[0] is True
    assert is_valid_command_input('ls -la')[0] is True
    
    # Invalid inputs
    assert is_valid_command_input('test\0null')[0] is False
    assert is_valid_command_input('<script>alert("xss")</script>')[0] is False
    assert is_valid_command_input('javascript:alert(1)')[0] is False
    assert is_valid_command_input('onclick=alert(1)')[0] is False
    assert is_valid_command_input('a' * 10001)[0] is False


def test_is_valid_file_path():
    """Test file path validation"""
    # Valid paths
    assert is_valid_file_path('C:\\Users\\test\\file.txt')[0] is True
    assert is_valid_file_path('/home/user/file.txt')[0] is True
    
    # Invalid paths
    assert is_valid_file_path('test\0null')[0] is False
    assert is_valid_file_path('../../../etc/passwd')[0] is False
    assert is_valid_file_path('..\\..\\windows\\system32')[0] is False
    assert is_valid_file_path('file<test>.txt')[0] is False


def test_is_valid_username():
    """Test username validation"""
    # Valid usernames
    assert is_valid_username('admin')[0] is True
    assert is_valid_username('user_123')[0] is True
    assert is_valid_username('test-user')[0] is True
    
    # Invalid usernames
    assert is_valid_username('ab')[0] is False  # Too short
    assert is_valid_username('a' * 21)[0] is False  # Too long
    assert is_valid_username('user@test')[0] is False  # Invalid char
    assert is_valid_username('user name')[0] is False  # Space


def test_is_valid_email():
    """Test email validation"""
    # Valid emails
    assert is_valid_email('test@example.com')[0] is True
    assert is_valid_email('user.name@domain.co.uk')[0] is True
    
    # Invalid emails
    assert is_valid_email('invalid')[0] is False
    assert is_valid_email('@example.com')[0] is False
    assert is_valid_email('test@')[0] is False
    assert is_valid_email('test @example.com')[0] is False


def test_is_strong_password():
    """Test password strength validation"""
    # Strong passwords
    assert is_strong_password('Password123')[0] is True
    assert is_strong_password('MyP@ssw0rd')[0] is True
    
    # Weak passwords
    assert is_strong_password('short')[0] is False  # Too short
    assert is_strong_password('alllowercase123')[0] is False  # No uppercase
    assert is_strong_password('ALLUPPERCASE123')[0] is False  # No lowercase
    assert is_strong_password('NoNumbers')[0] is False  # No numbers


def test_sanitize_input():
    """Test input sanitization"""
    assert sanitize_input('normal text') == 'normal text'
    assert sanitize_input('test\0null') == 'testnull'
    assert sanitize_input('test\x01control') == 'testcontrol'
    assert sanitize_input('test\nline\tbreak') == 'test\nline\tbreak'  # Keep newline and tab


def test_is_valid_port():
    """Test port validation"""
    # Valid ports
    assert is_valid_port(80)[0] is True
    assert is_valid_port(443)[0] is True
    assert is_valid_port(8080)[0] is True
    assert is_valid_port(65535)[0] is True
    
    # Invalid ports
    assert is_valid_port(0)[0] is False
    assert is_valid_port(-1)[0] is False
    assert is_valid_port(65536)[0] is False
    assert is_valid_port('not a number')[0] is False


def test_is_valid_ipv4():
    """Test IPv4 validation"""
    # Valid IPs
    assert is_valid_ipv4('192.168.1.1')[0] is True
    assert is_valid_ipv4('10.0.0.1')[0] is True
    assert is_valid_ipv4('255.255.255.255')[0] is True
    
    # Invalid IPs
    assert is_valid_ipv4('256.1.1.1')[0] is False
    assert is_valid_ipv4('192.168.1')[0] is False
    assert is_valid_ipv4('192.168.1.1.1')[0] is False
    assert is_valid_ipv4('not.an.ip.address')[0] is False


def test_validate_and_sanitize_command_input():
    """Test command input validation and sanitization"""
    # Valid input
    result = validate_and_sanitize_command_input('Get-Process')
    assert result == 'Get-Process'
    
    # Invalid input
    with pytest.raises(ValidationError):
        validate_and_sanitize_command_input('<script>alert("xss")</script>')
    
    with pytest.raises(ValidationError):
        validate_and_sanitize_command_input('test\0null')


def test_validate_and_sanitize_file_path():
    """Test file path validation and sanitization"""
    # Valid path
    result = validate_and_sanitize_file_path('C:\\Users\\test\\file.txt')
    assert result == 'C:\\Users\\test\\file.txt'
    
    # Invalid path
    with pytest.raises(ValidationError):
        validate_and_sanitize_file_path('../../../etc/passwd')
    
    with pytest.raises(ValidationError):
        validate_and_sanitize_file_path('test\0null')
