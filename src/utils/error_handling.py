"""
Error handling utilities for production-grade resilience
"""
import asyncio
import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar('T')


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
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
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                "Circuit breaker opened",
                failure_count=self.failure_count,
                threshold=self.failure_threshold
            )


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry decorator with exponential backoff"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        logger.error(
                            "Max retry attempts reached",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e)
                        )
                        raise e
                    
                    logger.warning(
                        "Retry attempt failed",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=current_delay,
                        error=str(e)
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def timeout(seconds: float):
    """Timeout decorator for async functions"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(
                    "Function timed out",
                    function=func.__name__,
                    timeout=seconds
                )
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
        
        return wrapper
    return decorator


class GracefulShutdown:
    """Graceful shutdown handler"""
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.tasks: set = set()
    
    def add_task(self, task: asyncio.Task):
        """Add a task to be cancelled on shutdown"""
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
    
    async def shutdown(self):
        """Initiate graceful shutdown"""
        logger.info("Initiating graceful shutdown")
        self.shutdown_event.set()
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("Graceful shutdown complete")


def safe_execute(
    default_return: Any = None,
    log_errors: bool = True,
    exceptions: tuple = (Exception,)
):
    """Safely execute function with error handling"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Union[T, Any]:
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    logger.error(
                        "Function execution failed",
                        function=func.__name__,
                        error=str(e),
                        args=args,
                        kwargs=kwargs
                    )
                return default_return
        
        return wrapper
    return decorator
