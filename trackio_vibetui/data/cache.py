"""Caching layer for data access."""

import time
from typing import Any, Dict, Optional, Tuple


class Cache:
    """Simple TTL-based cache."""

    def __init__(self, ttl_seconds: float = 30):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                # Expired, remove it
                del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set value in cache with current timestamp."""
        self._cache[key] = (value, time.time())

    def invalidate(self, key: str):
        """Remove a specific key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """Clear all cached values."""
        self._cache.clear()

    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys containing the pattern."""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]
