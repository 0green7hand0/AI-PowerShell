"""
Caching utilities for Flask API
"""
import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional
from flask import request


class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self, default_timeout: int = 300):
        """
        Initialize cache
        
        Args:
            default_timeout: Default cache timeout in seconds
        """
        self._cache = {}
        self._default_timeout = default_timeout
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry is None or time.time() < expiry:
                return value
            else:
                # Remove expired entry
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds (None for no expiry)
        """
        if timeout is None:
            timeout = self._default_timeout
        
        expiry = time.time() + timeout if timeout > 0 else None
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items()
            if expiry is not None and current_time >= expiry
        ]
        for key in expired_keys:
            del self._cache[key]


# Global cache instance
cache = SimpleCache(default_timeout=300)  # 5 minutes default


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from arguments
    
    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create a string representation of arguments
    key_parts = [prefix]
    
    if args:
        key_parts.extend(str(arg) for arg in args)
    
    if kwargs:
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(json.dumps(sorted_kwargs, sort_keys=True))
    
    # Generate hash for long keys
    key_string = ':'.join(key_parts)
    if len(key_string) > 200:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    return key_string


def cached(timeout: int = 300, key_prefix: Optional[str] = None):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Optional key prefix (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    return decorator


def cache_response(timeout: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator to cache Flask route responses
    
    Args:
        timeout: Cache timeout in seconds
        key_func: Optional function to generate cache key from request
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from request
            if key_func:
                cache_key = key_func(request)
            else:
                # Default: use endpoint + query string
                cache_key = f"{request.endpoint}:{request.query_string.decode()}"
            
            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response
            
            # Call function and cache response
            response = func(*args, **kwargs)
            cache.set(cache_key, response, timeout)
            
            return response
        
        return wrapper
    return decorator


def invalidate_cache(pattern: Optional[str] = None) -> None:
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Optional pattern to match keys (None clears all)
    """
    if pattern is None:
        cache.clear()
    else:
        # Remove matching keys
        keys_to_delete = [
            key for key in cache._cache.keys()
            if pattern in key
        ]
        for key in keys_to_delete:
            cache.delete(key)
