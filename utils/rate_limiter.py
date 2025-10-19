# utils/rate_limiter.py
from __future__ import annotations

import time
import hashlib
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

# Rate limiting configuration
RATE_LIMITS = {
    "default": {"requests": 100, "window": 3600},  # 100 requests per hour
    "ask": {"requests": 20, "window": 3600},       # 20 asks per hour
    "admin": {"requests": 1000, "window": 3600},   # 1000 admin requests per hour
}

# In-memory storage (use Redis in production)
_rate_limit_storage: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))


@dataclass
class RateLimitInfo:
    limit: int
    remaining: int
    reset_time: int
    window: int


class RateLimiter:
    """Simple in-memory rate limiter with sliding window."""
    
    def __init__(self, storage: Optional[Dict] = None):
        self.storage = storage or _rate_limit_storage
    
    def _get_key(self, request: Request, user_id: Optional[str] = None) -> str:
        """Generate a unique key for rate limiting."""
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP-based limiting
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _cleanup_expired_entries(self, key: str, window: int):
        """Remove expired entries from the rate limit storage."""
        current_time = time.time()
        cutoff_time = current_time - window
        
        # Remove entries older than the window
        expired_keys = [
            timestamp_str for timestamp_str in self.storage[key].keys()
            if float(timestamp_str) < cutoff_time
        ]
        
        for expired_key in expired_keys:
            del self.storage[key][expired_key]
    
    def check_rate_limit(
        self, 
        request: Request, 
        limit_type: str = "default",
        user_id: Optional[str] = None
    ) -> RateLimitInfo:
        """Check if request is within rate limits."""
        limits = RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])
        limit = limits["requests"]
        window = limits["window"]
        
        key = self._get_key(request, user_id)
        current_time = time.time()
        
        # Cleanup expired entries
        self._cleanup_expired_entries(key, window)
        
        # Count current requests in the window
        current_requests = len(self.storage[key])
        
        # Check if limit exceeded
        if current_requests >= limit:
            # Calculate reset time (oldest request + window)
            oldest_timestamp = min(float(ts) for ts in self.storage[key].keys())
            reset_time = int(oldest_timestamp + window)
            
            return RateLimitInfo(
                limit=limit,
                remaining=0,
                reset_time=reset_time,
                window=window
            )
        
        # Add current request
        self.storage[key][str(current_time)] = current_time
        
        # Calculate remaining requests
        remaining = max(0, limit - current_requests - 1)
        
        # Calculate reset time (current time + window)
        reset_time = int(current_time + window)
        
        return RateLimitInfo(
            limit=limit,
            remaining=remaining,
            reset_time=reset_time,
            window=window
        )
    
    def is_allowed(
        self, 
        request: Request, 
        limit_type: str = "default",
        user_id: Optional[str] = None
    ) -> bool:
        """Check if request is allowed without throwing exception."""
        rate_limit_info = self.check_rate_limit(request, limit_type, user_id)
        return rate_limit_info.remaining > 0


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_middleware(limit_type: str = "default"):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Check rate limit
            rate_limit_info = rate_limiter.check_rate_limit(request, limit_type)
            
            if rate_limit_info.remaining <= 0:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": rate_limit_info.limit,
                        "window": rate_limit_info.window,
                        "reset_time": rate_limit_info.reset_time
                    }
                )
            
            # Add rate limit headers
            response = await func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(rate_limit_info.limit)
                response.headers["X-RateLimit-Remaining"] = str(rate_limit_info.remaining)
                response.headers["X-RateLimit-Reset"] = str(rate_limit_info.reset_time)
            
            return response
        
        return wrapper
    return decorator


def get_rate_limit_info(request: Request, limit_type: str = "default", user_id: Optional[str] = None) -> RateLimitInfo:
    """Get current rate limit information without incrementing the counter."""
    return rate_limiter.check_rate_limit(request, limit_type, user_id)
