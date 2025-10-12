"""
 PHISHGUARD AI - RATE LIMITING SYSTEM
=======================================

Token Bucket Algorithm for API rate limiting

Features:
- Token bucket algorithm implementation
- Per-API rate limit configuration
- Thread-safe operation
- Auto-refill tokens
- Graceful degradation on limit exceeded

Author: PhishGuard AI Team
Version: 2.0.0
Date: October 10, 2025
"""

import time
import threading
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class APIService(Enum):
    """Supported API services with their rate limits"""

    PHISHTANK = "phishtank"
    VIRUSTOTAL = "virustotal"
    GOOGLE_SAFE_BROWSING = "google_safe_browsing"
    WHOIS = "whois"
    DNS = "dns"
    CUSTOM = "custom"


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an API"""

    max_requests: int  # Maximum requests allowed
    time_window: int  # Time window in seconds
    burst_size: int  # Maximum burst size (optional)

    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.max_requests


# ============================================================================
# RATE LIMIT CONFIGURATIONS
# ============================================================================

RATE_LIMIT_CONFIGS: Dict[APIService, RateLimitConfig] = {
    # PhishTank: 20 requests per minute
    APIService.PHISHTANK: RateLimitConfig(
        max_requests=20, time_window=60, burst_size=5
    ),
    # VirusTotal: 4 requests per minute (free tier)
    APIService.VIRUSTOTAL: RateLimitConfig(
        max_requests=4, time_window=60, burst_size=2
    ),
    # Google Safe Browsing: 10,000 requests per day
    APIService.GOOGLE_SAFE_BROWSING: RateLimitConfig(
        max_requests=10000, time_window=86400, burst_size=100  # 24 hours
    ),
    # WHOIS: 100 requests per hour
    APIService.WHOIS: RateLimitConfig(
        max_requests=100, time_window=3600, burst_size=10
    ),
    # DNS: 1000 requests per hour
    APIService.DNS: RateLimitConfig(max_requests=1000, time_window=3600, burst_size=50),
}


# ============================================================================
# TOKEN BUCKET IMPLEMENTATION
# ============================================================================


class TokenBucket:
    """
    Token Bucket algorithm for rate limiting

    Thread-safe implementation with automatic token refill
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize token bucket

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.tokens = float(config.max_requests)  # Start with full bucket
        self.last_refill = time.time()
        self.lock = threading.Lock()

        # Calculate refill rate (tokens per second)
        self.refill_rate = config.max_requests / config.time_window

    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate

        # Refill bucket (capped at max_requests)
        self.tokens = min(self.config.max_requests, self.tokens + tokens_to_add)

        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if rate limit exceeded
        """
        with self.lock:
            # Refill tokens first
            self._refill()

            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False

    def wait_time(self) -> float:
        """
        Calculate time to wait for next token

        Returns:
            Seconds to wait for next token
        """
        with self.lock:
            self._refill()

            if self.tokens >= 1:
                return 0.0

            # Calculate time needed to refill 1 token
            tokens_needed = 1 - self.tokens
            wait_time = tokens_needed / self.refill_rate

            return wait_time

    def available_tokens(self) -> int:
        """Get number of available tokens"""
        with self.lock:
            self._refill()
            return int(self.tokens)

    def reset(self):
        """Reset bucket to full capacity"""
        with self.lock:
            self.tokens = float(self.config.max_requests)
            self.last_refill = time.time()


# ============================================================================
# RATE LIMITER
# ============================================================================


class RateLimiter:
    """
    Central rate limiter for all API services

    Manages multiple token buckets for different APIs
    """

    def __init__(self):
        """Initialize rate limiter with all API configurations"""
        self.buckets: Dict[APIService, TokenBucket] = {}

        # Create token bucket for each API
        for service, config in RATE_LIMIT_CONFIGS.items():
            self.buckets[service] = TokenBucket(config)

    def acquire(self, service: APIService, tokens: int = 1, wait: bool = False) -> bool:
        """
        Acquire tokens for an API call

        Args:
            service: API service to rate limit
            tokens: Number of tokens to acquire
            wait: If True, wait for tokens to become available

        Returns:
            True if tokens acquired, False if rate limit exceeded

        Raises:
            ValueError: If service not configured
        """
        if service not in self.buckets:
            raise ValueError(f"Rate limiter not configured for service: {service}")

        bucket = self.buckets[service]

        if wait:
            # Wait for tokens to become available
            while not bucket.consume(tokens):
                wait_time = bucket.wait_time()
                print(
                    f"[RateLimiter] Rate limit reached for {service.value}. Waiting {wait_time:.2f}s..."
                )
                time.sleep(wait_time)
            return True
        else:
            # Try to consume without waiting
            return bucket.consume(tokens)

    def wait_time(self, service: APIService) -> float:
        """
        Get wait time for next token

        Args:
            service: API service

        Returns:
            Seconds to wait for next token
        """
        if service not in self.buckets:
            return 0.0

        return self.buckets[service].wait_time()

    def available(self, service: APIService) -> int:
        """
        Get available tokens for a service

        Args:
            service: API service

        Returns:
            Number of available tokens
        """
        if service not in self.buckets:
            return 0

        return self.buckets[service].available_tokens()

    def reset(self, service: Optional[APIService] = None):
        """
        Reset rate limiter

        Args:
            service: If provided, reset only this service. Otherwise reset all.
        """
        if service:
            if service in self.buckets:
                self.buckets[service].reset()
        else:
            for bucket in self.buckets.values():
                bucket.reset()

    def add_custom_service(self, name: str, config: RateLimitConfig):
        """
        Add a custom API service with rate limiting

        Args:
            name: Service name
            config: Rate limit configuration
        """
        # Create custom service enum
        custom_service = APIService.CUSTOM
        self.buckets[name] = TokenBucket(config)
        print(f"[RateLimiter] Added custom service: {name}")

    def get_stats(self) -> Dict[str, Dict[str, any]]:
        """
        Get statistics for all services

        Returns:
            Dictionary with stats for each service
        """
        stats = {}

        for service, bucket in self.buckets.items():
            stats[service.value] = {
                "available_tokens": bucket.available_tokens(),
                "max_requests": bucket.config.max_requests,
                "time_window": bucket.config.time_window,
                "refill_rate": bucket.refill_rate,
                "wait_time": bucket.wait_time(),
            }

        return stats


# ============================================================================
# GLOBAL RATE LIMITER INSTANCE
# ============================================================================

# Singleton instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance (singleton)

    Returns:
        Global RateLimiter instance
    """
    global _rate_limiter

    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
        print("[RateLimiter]  Initialized global rate limiter")

    return _rate_limiter


# ============================================================================
# DECORATOR FOR RATE-LIMITED FUNCTIONS
# ============================================================================


def rate_limited(service: APIService, tokens: int = 1, wait: bool = True):
    """
    Decorator to apply rate limiting to a function

    Args:
        service: API service to rate limit
        tokens: Number of tokens to consume per call
        wait: If True, wait for tokens. If False, raise exception.

    Example:
        @rate_limited(APIService.VIRUSTOTAL, tokens=1, wait=True)
        def check_virustotal(url):
            # API call here
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()

            if not limiter.acquire(service, tokens, wait):
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {service.value}. "
                    f"Wait {limiter.wait_time(service):.2f}s"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# EXCEPTIONS
# ============================================================================


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded"""

    pass


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print(" PhishGuard Rate Limiter - Example Usage\n")

    # Get rate limiter
    limiter = get_rate_limiter()

    # Example 1: VirusTotal rate limiting (4 requests/minute)
    print("Example 1: VirusTotal Rate Limiting")
    print("-" * 50)

    for i in range(6):
        if limiter.acquire(APIService.VIRUSTOTAL):
            print(f" Request {i+1} allowed")
        else:
            wait = limiter.wait_time(APIService.VIRUSTOTAL)
            print(f" Request {i+1} rate limited. Wait {wait:.2f}s")

    print(f"\nAvailable tokens: {limiter.available(APIService.VIRUSTOTAL)}\n")

    # Example 2: Using wait parameter
    print("Example 2: Waiting for tokens")
    print("-" * 50)

    limiter.acquire(APIService.PHISHTANK, wait=True)
    print(" Request completed (with wait)")

    # Example 3: Statistics
    print("\nExample 3: Rate Limiter Statistics")
    print("-" * 50)

    stats = limiter.get_stats()
    for service, data in stats.items():
        print(f"\n{service.upper()}:")
        print(f"  Available tokens: {data['available_tokens']}")
        print(f"  Max requests: {data['max_requests']}/{data['time_window']}s")
        print(f"  Refill rate: {data['refill_rate']:.4f} tokens/s")
        print(f"  Wait time: {data['wait_time']:.2f}s")

    # Example 4: Using decorator
    print("\n\nExample 4: Using @rate_limited decorator")
    print("-" * 50)

    @rate_limited(APIService.VIRUSTOTAL, tokens=1, wait=True)
    def check_virustotal_url(url: str):
        print(f"  Checking URL: {url}")
        return {"is_malicious": False}

    try:
        result = check_virustotal_url("https://example.com")
        print(f"  Result: {result}")
    except RateLimitExceeded as e:
        print(f"  Error: {e}")
