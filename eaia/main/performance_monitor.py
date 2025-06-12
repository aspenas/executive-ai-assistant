"""Performance monitoring and metrics collection for the executive assistant."""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_reset: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """Monitor and track performance metrics for the executive assistant."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics = {
            'triage': PerformanceMetrics(),
            'draft': PerformanceMetrics(),
            'gmail_api': PerformanceMetrics(),
            'calendar_api': PerformanceMetrics(),
            'llm_api': PerformanceMetrics(),
            'overall': PerformanceMetrics()
        }
        self.rate_limiters = {}
    
    def start_operation(self, operation_type: str) -> str:
        """Start timing an operation. Returns operation ID."""
        operation_id = f"{operation_type}_{int(time.time() * 1000000)}"
        self._operation_start_times = getattr(self, '_operation_start_times', {})
        self._operation_start_times[operation_id] = time.time()
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error_type: Optional[str] = None):
        """End timing an operation and record metrics."""
        start_times = getattr(self, '_operation_start_times', {})
        if operation_id not in start_times:
            logger.warning(f"Operation ID {operation_id} not found in start times")
            return
        
        duration = time.time() - start_times[operation_id]
        operation_type = operation_id.split('_')[0]
        
        if operation_type in self.metrics:
            metrics = self.metrics[operation_type]
            self._update_metrics(metrics, duration, success, error_type)
        
        self._update_metrics(self.metrics['overall'], duration, success, error_type)
        
        del start_times[operation_id]
        
        logger.debug(f"Operation {operation_type} completed in {duration:.3f}s (success: {success})")
    
    def _update_metrics(self, metrics: PerformanceMetrics, duration: float, success: bool, error_type: Optional[str]):
        """Update metrics object with new data point."""
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            if error_type:
                metrics.error_counts[error_type] += 1
        
        metrics.response_times.append(duration)
        metrics.min_response_time = min(metrics.min_response_time, duration)
        metrics.max_response_time = max(metrics.max_response_time, duration)
        
        if metrics.response_times:
            metrics.average_response_time = sum(metrics.response_times) / len(metrics.response_times)
    
    def get_metrics_summary(self, operation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of performance metrics."""
        if operation_type and operation_type in self.metrics:
            metrics = self.metrics[operation_type]
            return self._format_metrics(operation_type, metrics)
        else:
            summary = {}
            for op_type, metrics in self.metrics.items():
                summary[op_type] = self._format_metrics(op_type, metrics)
            return summary
    
    def _format_metrics(self, operation_type: str, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Format metrics for display."""
        success_rate = (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0
        
        return {
            "operation_type": operation_type,
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "average_response_time_ms": round(metrics.average_response_time * 1000, 2),
            "min_response_time_ms": round(metrics.min_response_time * 1000, 2) if metrics.min_response_time != float('inf') else 0,
            "max_response_time_ms": round(metrics.max_response_time * 1000, 2),
            "error_breakdown": dict(metrics.error_counts),
            "last_reset": metrics.last_reset.isoformat()
        }
    
    def reset_metrics(self, operation_type: Optional[str] = None):
        """Reset metrics for specified operation type or all operations."""
        if operation_type and operation_type in self.metrics:
            self.metrics[operation_type] = PerformanceMetrics()
        else:
            for op_type in self.metrics:
                self.metrics[op_type] = PerformanceMetrics()
        
        logger.info(f"Reset metrics for {operation_type or 'all operations'}")
    
    def check_rate_limit(self, service: str, limit_per_minute: int) -> bool:
        """Check if operation is within rate limit."""
        now = time.time()
        
        if service not in self.rate_limiters:
            self.rate_limiters[service] = deque()
        
        while self.rate_limiters[service] and now - self.rate_limiters[service][0] > 60:
            self.rate_limiters[service].popleft()
        
        if len(self.rate_limiters[service]) >= limit_per_minute:
            return False
        
        self.rate_limiters[service].append(now)
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of the system."""
        overall_metrics = self.metrics['overall']
        
        success_rate = (overall_metrics.successful_requests / overall_metrics.total_requests * 100) if overall_metrics.total_requests > 0 else 100
        avg_response_time = overall_metrics.average_response_time
        
        health_score = 100
        if success_rate < 95:
            health_score -= (95 - success_rate) * 2
        if avg_response_time > 5.0:  # 5 seconds
            health_score -= min(50, (avg_response_time - 5.0) * 10)
        
        health_score = max(0, health_score)
        
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "health_score": round(health_score, 1),
            "total_requests": overall_metrics.total_requests,
            "success_rate_percent": round(success_rate, 2),
            "average_response_time_seconds": round(avg_response_time, 3),
            "active_errors": sum(overall_metrics.error_counts.values()),
            "uptime_since_reset": str(datetime.now() - overall_metrics.last_reset)
        }


performance_monitor = PerformanceMonitor()


def monitor_performance(operation_type: str):
    """Decorator to automatically monitor function performance."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            operation_id = performance_monitor.start_operation(operation_type)
            try:
                result = await func(*args, **kwargs)
                performance_monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                error_type = type(e).__name__
                performance_monitor.end_operation(operation_id, success=False, error_type=error_type)
                raise
        
        def sync_wrapper(*args, **kwargs):
            operation_id = performance_monitor.start_operation(operation_type)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_operation(operation_id, success=True)
                return result
            except Exception as e:
                error_type = type(e).__name__
                performance_monitor.end_operation(operation_id, success=False, error_type=error_type)
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
