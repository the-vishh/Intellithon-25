"""
🔄 PHISHGUARD AI - RETRY HANDLER WITH EXPONENTIAL BACKOFF
=========================================================

Intelligent retry logic for API calls with exponential backoff and jitter

Features:
- Exponential backoff algorithm
- Jitter to prevent thundering herd
- Configurable max retries and delays
- Circuit breaker pattern
- Detailed logging
- Support for custom retry conditions

Author: PhishGuard AI Team
Version: 2.0.0
Date: October 10, 2025
"""

import time
import random
import logging
from typing import Callable, Optional, Any, Type, Tuple
from functools import wraps
from enum import Enum


# ============================================================================
# CONFIGURATION
# ============================================================================


class RetryConfig:
    """Configuration for retry behavior"""

    # Default retry parameters
    MAX_RETRIES = 3  # Maximum number of retry attempts
    INITIAL_DELAY = 1.0  # Initial delay in seconds (1s)
    MAX_DELAY = 32.0  # Maximum delay in seconds (32s)
    BACKOFF_FACTOR = 2.0  # Exponential backoff factor (2^n)
    JITTER_FACTOR = 0.3  # Random jitter (±30%)

    # Circuit breaker parameters
    CIRCUIT_BREAKER_THRESHOLD = 5  # Failures before opening circuit
    CIRCUIT_BREAKER_TIMEOUT = 60.0  # Seconds before trying again

    # Retryable HTTP status codes
    RETRYABLE_STATUS_CODES = {
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }

    # Retryable exceptions
    RETRYABLE_EXCEPTIONS = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


# ============================================================================
# CIRCUIT BREAKER STATES
# ============================================================================


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    Tracks failure rate and opens circuit after threshold exceeded
    """

    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        """
        Initialize circuit breaker

        Args:
            threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again
        """
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                logging.info("[CircuitBreaker] Entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpen(
                    f"Circuit breaker OPEN. Retry after "
                    f"{self.timeout - (time.time() - self.last_failure_time):.1f}s"
                )

        try:
            result = func(*args, **kwargs)

            # Success - reset circuit
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logging.info("[CircuitBreaker] Circuit CLOSED (recovered)")

            return result

        except Exception as e:
            self._record_failure()
            raise e

    def _record_failure(self):
        """Record a failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.threshold:
            self.state = CircuitState.OPEN
            logging.warning(
                f"[CircuitBreaker] Circuit OPEN after {self.failure_count} failures"
            )

    def reset(self):
        """Reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None


# ============================================================================
# RETRY HANDLER
# ============================================================================


class RetryHandler:
    """
    Intelligent retry handler with exponential backoff
    """

    def __init__(
        self,
        max_retries: int = RetryConfig.MAX_RETRIES,
        initial_delay: float = RetryConfig.INITIAL_DELAY,
        max_delay: float = RetryConfig.MAX_DELAY,
        backoff_factor: float = RetryConfig.BACKOFF_FACTOR,
        jitter_factor: float = RetryConfig.JITTER_FACTOR,
        retryable_exceptions: Tuple[
            Type[Exception], ...
        ] = RetryConfig.RETRYABLE_EXCEPTIONS,
        retryable_status_codes: set = RetryConfig.RETRYABLE_STATUS_CODES,
        use_circuit_breaker: bool = True,
    ):
        """
        Initialize retry handler

        Args:
            max_retries: Maximum retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Exponential backoff factor
            jitter_factor: Random jitter factor (0-1)
            retryable_exceptions: Exceptions that should trigger retry
            retryable_status_codes: HTTP status codes that should trigger retry
            use_circuit_breaker: Enable circuit breaker
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter_factor = jitter_factor
        self.retryable_exceptions = retryable_exceptions
        self.retryable_status_codes = retryable_status_codes

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker() if use_circuit_breaker else None

        # Statistics
        self.total_attempts = 0
        self.total_retries = 0
        self.total_failures = 0

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt with exponential backoff and jitter

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: delay = initial_delay * (backoff_factor ^ attempt)
        delay = self.initial_delay * (self.backoff_factor**attempt)

        # Cap at max_delay
        delay = min(delay, self.max_delay)

        # Add jitter to prevent thundering herd
        # Jitter range: ±(delay * jitter_factor)
        jitter_range = delay * self.jitter_factor
        jitter = random.uniform(-jitter_range, jitter_range)
        delay += jitter

        # Ensure non-negative
        delay = max(0, delay)

        return delay

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if should retry based on exception and attempt count

        Args:
            exception: Exception that occurred
            attempt: Current retry attempt

        Returns:
            True if should retry, False otherwise
        """
        # Check max retries
        if attempt >= self.max_retries:
            return False

        # Check if exception is retryable
        if isinstance(exception, self.retryable_exceptions):
            return True

        # Check HTTP status codes (if exception has status_code)
        if hasattr(exception, "status_code"):
            if exception.status_code in self.retryable_status_codes:
                return True

        # Check response attribute (for requests library)
        if hasattr(exception, "response") and exception.response is not None:
            if exception.response.status_code in self.retryable_status_codes:
                return True

        return False

    def execute(
        self,
        func: Callable,
        *args,
        on_retry: Optional[Callable[[Exception, int], None]] = None,
        **kwargs,
    ) -> Any:
        """
        Execute function with retry logic

        Args:
            func: Function to execute
            *args: Function arguments
            on_retry: Optional callback on retry (exception, attempt)
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries failed
        """
        self.total_attempts += 1
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Use circuit breaker if enabled
                if self.circuit_breaker:
                    result = self.circuit_breaker.call(func, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success
                if attempt > 0:
                    logging.info(f"[RetryHandler] ✅ Success after {attempt} retries")

                return result

            except Exception as e:
                last_exception = e

                # Check if should retry
                if not self.should_retry(e, attempt):
                    logging.error(
                        f"[RetryHandler] ❌ Failed (not retryable): {type(e).__name__}: {e}"
                    )
                    self.total_failures += 1
                    raise e

                # Calculate delay
                delay = self.calculate_delay(attempt)

                # Log retry
                logging.warning(
                    f"[RetryHandler] 🔄 Retry {attempt + 1}/{self.max_retries} "
                    f"after {delay:.2f}s: {type(e).__name__}: {e}"
                )

                # Call retry callback if provided
                if on_retry:
                    on_retry(e, attempt)

                # Wait before retry
                time.sleep(delay)

                self.total_retries += 1

        # All retries failed
        self.total_failures += 1
        logging.error(
            f"[RetryHandler] ❌ Failed after {self.max_retries} retries: "
            f"{type(last_exception).__name__}: {last_exception}"
        )
        raise last_exception

    def get_stats(self) -> dict:
        """
        Get retry statistics

        Returns:
            Dictionary with statistics
        """
        return {
            "total_attempts": self.total_attempts,
            "total_retries": self.total_retries,
            "total_failures": self.total_failures,
            "success_rate": (
                (self.total_attempts - self.total_failures) / self.total_attempts * 100
                if self.total_attempts > 0
                else 0
            ),
            "circuit_breaker_state": (
                self.circuit_breaker.state.value if self.circuit_breaker else None
            ),
        }


# ============================================================================
# DECORATOR
# ============================================================================


def retry(
    max_retries: int = RetryConfig.MAX_RETRIES,
    initial_delay: float = RetryConfig.INITIAL_DELAY,
    max_delay: float = RetryConfig.MAX_DELAY,
    backoff_factor: float = RetryConfig.BACKOFF_FACTOR,
    retryable_exceptions: Tuple[
        Type[Exception], ...
    ] = RetryConfig.RETRYABLE_EXCEPTIONS,
    use_circuit_breaker: bool = True,
):
    """
    Decorator to add retry logic to a function

    Args:
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Exponential backoff factor
        retryable_exceptions: Exceptions that should trigger retry
        use_circuit_breaker: Enable circuit breaker

    Example:
        @retry(max_retries=3, initial_delay=1.0)
        def fetch_url(url):
            response = requests.get(url)
            return response.json()
    """
    handler = RetryHandler(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        retryable_exceptions=retryable_exceptions,
        use_circuit_breaker=use_circuit_breaker,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute(func, *args, **kwargs)

        # Attach handler for stats
        wrapper.retry_handler = handler

        return wrapper

    return decorator


# ============================================================================
# EXCEPTIONS
# ============================================================================


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open"""

    pass


# ============================================================================
# GLOBAL RETRY HANDLER
# ============================================================================

# Singleton instance
_default_handler = None


def get_retry_handler() -> RetryHandler:
    """
    Get global retry handler instance (singleton)

    Returns:
        Global RetryHandler instance
    """
    global _default_handler

    if _default_handler is None:
        _default_handler = RetryHandler()
        logging.info("[RetryHandler] ✅ Initialized global retry handler")

    return _default_handler


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    print("🔄 PhishGuard Retry Handler - Example Usage\n")

    # Example 1: Using RetryHandler directly
    print("Example 1: Direct usage")
    print("-" * 50)

    handler = RetryHandler(max_retries=3, initial_delay=0.5)

    def flaky_function():
        """Simulates a function that fails randomly"""
        if random.random() < 0.7:
            raise ConnectionError("Connection failed")
        return "Success!"

    try:
        result = handler.execute(flaky_function)
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    print(f"\nStats: {handler.get_stats()}\n")

    # Example 2: Using @retry decorator
    print("Example 2: Using @retry decorator")
    print("-" * 50)

    @retry(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
    def fetch_data(url: str):
        """Simulates API call"""
        if random.random() < 0.5:
            raise TimeoutError(f"Timeout fetching {url}")
        return {"data": "example"}

    try:
        data = fetch_data("https://api.example.com")
        print(f"✅ Data: {data}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    print(f"\nStats: {fetch_data.retry_handler.get_stats()}\n")

    # Example 3: Exponential backoff visualization
    print("Example 3: Exponential Backoff Delays")
    print("-" * 50)

    handler = RetryHandler(
        max_retries=5, initial_delay=1.0, backoff_factor=2.0, jitter_factor=0.3
    )

    for attempt in range(6):
        delay = handler.calculate_delay(attempt)
        print(f"Attempt {attempt}: {delay:.3f}s delay")
