"""Enhanced error handling and retry logic for the executive assistant."""

import asyncio
import logging
from typing import Any, Callable, Dict, Optional, Tuple
from functools import wraps
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class CircuitBreaker:
    """Circuit breaker pattern for external service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


def with_retry(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    fallback_func: Optional[Callable] = None
):
    """Decorator for adding retry logic and circuit breaker to async functions."""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    if circuit_breaker and not circuit_breaker.can_execute():
                        logger.warning(f"Circuit breaker OPEN for {func.__name__}")
                        if fallback_func:
                            return await fallback_func(*args, **kwargs)
                        raise Exception("Circuit breaker is OPEN")
                    
                    result = await func(*args, **kwargs)
                    
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{retry_config.max_attempts} failed for {func.__name__}: {str(e)}"
                    )
                    
                    if attempt == retry_config.max_attempts - 1:
                        break
                    
                    delay = min(
                        retry_config.base_delay * (retry_config.exponential_base ** attempt),
                        retry_config.max_delay
                    )
                    
                    if retry_config.jitter:
                        import random
                        delay *= (0.5 + random.random() * 0.5)
                    
                    await asyncio.sleep(delay)
            
            logger.error(f"All {retry_config.max_attempts} attempts failed for {func.__name__}")
            
            if fallback_func:
                try:
                    return await fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback function also failed: {str(fallback_error)}")
            
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling for the executive assistant."""
    
    def __init__(self):
        self.circuit_breakers = {}
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def handle_llm_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM-related errors with appropriate fallbacks."""
        logger.error(f"LLM error in {context.get('function', 'unknown')}: {str(error)}")
        
        if context.get("function") == "triage":
            return {"response": "notify", "reason": "Error in triage, defaulting to notify"}
        elif context.get("function") == "draft":
            return {"action": "question", "content": "I encountered an error. Could you please clarify what you'd like me to do with this email?"}
        else:
            return {"error": True, "message": "An error occurred. Please try again."}
    
    async def handle_gmail_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Gmail API errors."""
        logger.error(f"Gmail API error in {context.get('function', 'unknown')}: {str(error)}")
        
        error_str = str(error).lower()
        
        if "quota" in error_str or "rate limit" in error_str:
            return {
                "error": True,
                "type": "rate_limit",
                "message": "Gmail API rate limit reached. Please try again later.",
                "retry_after": 300  # 5 minutes
            }
        elif "auth" in error_str or "permission" in error_str:
            return {
                "error": True,
                "type": "auth_error",
                "message": "Gmail authentication error. Please check credentials.",
                "requires_reauth": True
            }
        else:
            return {
                "error": True,
                "type": "gmail_error",
                "message": "Gmail API error occurred. Please try again."
            }
    
    async def handle_calendar_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar-related errors."""
        logger.error(f"Calendar error in {context.get('function', 'unknown')}: {str(error)}")
        
        return {
            "error": True,
            "type": "calendar_error",
            "message": "Calendar operation failed. Please check manually.",
            "fallback_action": "notify_user"
        }


error_handler = ErrorHandler()

gmail_retry = with_retry(
    RetryConfig(max_attempts=3, base_delay=2.0),
    error_handler.get_circuit_breaker("gmail")
)

llm_retry = with_retry(
    RetryConfig(max_attempts=2, base_delay=1.0),
    error_handler.get_circuit_breaker("llm")
)

calendar_retry = with_retry(
    RetryConfig(max_attempts=3, base_delay=1.5),
    error_handler.get_circuit_breaker("calendar")
)
