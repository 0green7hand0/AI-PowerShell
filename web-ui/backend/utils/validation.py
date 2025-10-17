"""
Input validation utilities for backend
"""
import re
import html
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    return html.escape(text)


def is_valid_command_input(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate command input for dangerous patterns
    
    Args:
        text: Command input text
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for null bytes
    if '\0' in text:
        return False, "Input contains null bytes"
    
    # Check for excessive length
    if len(text) > 10000:
        return False, "Input is too long (max 10000 characters)"
    
    # Check for script injection attempts
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',
        r'expression\s*\(',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Input contains potentially dangerous pattern: {pattern}"
    
    return True, None


def is_valid_file_path(path: str) -> tuple[bool, Optional[str]]:
    """
    Validate file path
    
    Args:
        path: File path
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for null bytes
    if '\0' in path:
        return False, "Path contains null bytes"
    
    # Check for path traversal
    if '../' in path or '..\\'  in path:
        return False, "Path contains traversal attempts"
    
    # Check for invalid characters (Windows)
    invalid_chars = r'[<>:"|?*]'
    if re.search(invalid_chars, path):
        return False, "Path contains invalid characters"
    
    return True, None


def is_valid_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format
    
    Args:
        username: Username
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        return False, "Username must be 3-20 characters and contain only letters, numbers, underscore, and hyphen"
    
    return True, None


def is_valid_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, None


def is_strong_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: Password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, None


def sanitize_input(text: str) -> str:
    """
    Remove dangerous characters from input
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace('\0', '')
    
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    return text


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, Optional[str]]:
    """
    Validate JSON structure has required fields
    
    Args:
        data: JSON data
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def is_valid_port(port: int) -> tuple[bool, Optional[str]]:
    """
    Validate port number
    
    Args:
        port: Port number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(port, int):
        return False, "Port must be an integer"
    
    if port < 1 or port > 65535:
        return False, "Port must be between 1 and 65535"
    
    return True, None


def is_valid_ipv4(ip: str) -> tuple[bool, Optional[str]]:
    """
    Validate IPv4 address
    
    Args:
        ip: IP address
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ipv4_pattern, ip):
        return False, "Invalid IPv4 format"
    
    parts = ip.split('.')
    for part in parts:
        num = int(part)
        if num < 0 or num > 255:
            return False, "IPv4 octets must be between 0 and 255"
    
    return True, None


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_and_sanitize_command_input(text: str) -> str:
    """
    Validate and sanitize command input
    
    Args:
        text: Command input
        
    Returns:
        Sanitized text
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate
    is_valid, error_msg = is_valid_command_input(text)
    if not is_valid:
        raise ValidationError(error_msg)
    
    # Sanitize
    return sanitize_input(text)


def validate_and_sanitize_file_path(path: str) -> str:
    """
    Validate and sanitize file path
    
    Args:
        path: File path
        
    Returns:
        Sanitized path
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate
    is_valid, error_msg = is_valid_file_path(path)
    if not is_valid:
        raise ValidationError(error_msg)
    
    # Sanitize
    return sanitize_input(path)
