"""
Connection pool utilities for backend services
"""
import queue
import threading
import time
from typing import Any, Callable, Optional, TypeVar, Generic
from contextlib import contextmanager


T = TypeVar('T')


class ConnectionPool(Generic[T]):
    """Generic connection pool implementation"""
    
    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 10,
        timeout: float = 30.0,
        max_idle_time: float = 300.0
    ):
        """
        Initialize connection pool
        
        Args:
            factory: Function to create new connections
            max_size: Maximum number of connections in pool
            timeout: Timeout for acquiring connection
            max_idle_time: Maximum idle time before connection is closed
        """
        self._factory = factory
        self._max_size = max_size
        self._timeout = timeout
        self._max_idle_time = max_idle_time
        
        self._pool: queue.Queue = queue.Queue(maxsize=max_size)
        self._size = 0
        self._lock = threading.Lock()
        self._last_used = {}
    
    def _create_connection(self) -> T:
        """Create a new connection"""
        return self._factory()
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager)
        
        Yields:
            Connection object
        """
        conn = self.acquire()
        try:
            yield conn
        finally:
            self.release(conn)
    
    def acquire(self) -> T:
        """
        Acquire a connection from the pool
        
        Returns:
            Connection object
            
        Raises:
            queue.Empty: If timeout is reached
        """
        try:
            # Try to get existing connection
            conn = self._pool.get(timeout=self._timeout)
            
            # Check if connection is still valid
            if self._is_connection_stale(conn):
                # Close stale connection and create new one
                self._close_connection(conn)
                conn = self._create_connection()
            
            self._last_used[id(conn)] = time.time()
            return conn
            
        except queue.Empty:
            # No available connections, try to create new one
            with self._lock:
                if self._size < self._max_size:
                    self._size += 1
                    conn = self._create_connection()
                    self._last_used[id(conn)] = time.time()
                    return conn
            
            # Pool is full, wait for available connection
            raise queue.Empty("Connection pool exhausted")
    
    def release(self, conn: T) -> None:
        """
        Release a connection back to the pool
        
        Args:
            conn: Connection to release
        """
        try:
            self._last_used[id(conn)] = time.time()
            self._pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            self._close_connection(conn)
            with self._lock:
                self._size -= 1
    
    def _is_connection_stale(self, conn: T) -> bool:
        """
        Check if connection is stale
        
        Args:
            conn: Connection to check
            
        Returns:
            True if connection is stale
        """
        conn_id = id(conn)
        if conn_id not in self._last_used:
            return False
        
        idle_time = time.time() - self._last_used[conn_id]
        return idle_time > self._max_idle_time
    
    def _close_connection(self, conn: T) -> None:
        """
        Close a connection
        
        Args:
            conn: Connection to close
        """
        # Try to close connection if it has a close method
        if hasattr(conn, 'close'):
            try:
                conn.close()
            except Exception:
                pass
        
        # Remove from tracking
        conn_id = id(conn)
        if conn_id in self._last_used:
            del self._last_used[conn_id]
    
    def cleanup(self) -> None:
        """Clean up stale connections"""
        stale_connections = []
        
        # Collect stale connections
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if self._is_connection_stale(conn):
                    stale_connections.append(conn)
                else:
                    self._pool.put_nowait(conn)
            except queue.Empty:
                break
        
        # Close stale connections
        for conn in stale_connections:
            self._close_connection(conn)
            with self._lock:
                self._size -= 1
    
    def close_all(self) -> None:
        """Close all connections in the pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                self._close_connection(conn)
            except queue.Empty:
                break
        
        with self._lock:
            self._size = 0
        
        self._last_used.clear()
    
    @property
    def size(self) -> int:
        """Get current pool size"""
        return self._size
    
    @property
    def available(self) -> int:
        """Get number of available connections"""
        return self._pool.qsize()


class SessionPool:
    """Session pool for reusing HTTP sessions"""
    
    def __init__(self, max_size: int = 10):
        """
        Initialize session pool
        
        Args:
            max_size: Maximum number of sessions
        """
        import requests
        self._pool = ConnectionPool(
            factory=lambda: requests.Session(),
            max_size=max_size
        )
    
    @contextmanager
    def get_session(self):
        """
        Get a session from the pool
        
        Yields:
            requests.Session object
        """
        with self._pool.get_connection() as session:
            yield session
    
    def cleanup(self) -> None:
        """Clean up stale sessions"""
        self._pool.cleanup()
    
    def close_all(self) -> None:
        """Close all sessions"""
        self._pool.close_all()


# Global session pool instance
session_pool = SessionPool(max_size=10)
