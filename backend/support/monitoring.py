"""
System Monitoring

Provides system health monitoring and lifecycle management.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime


class SystemMonitor:
    """
    Monitors system health and state.
    """
    
    def __init__(self):
        """Initialize system monitor."""
        self.running = False
        self.start_time = None
        self.metrics = {}
    
    def start(self):
        """Start the system monitor."""
        self.running = True
        self.start_time = datetime.now()
        self.metrics['started_at'] = self.start_time.isoformat()
    
    def stop(self):
        """Stop the system monitor."""
        self.running = False
        self.metrics['stopped_at'] = datetime.now().isoformat()
    
    def is_running(self) -> bool:
        """Check if system is running."""
        return self.running
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return {
            'running': self.running,
            'uptime_seconds': self._get_uptime(),
            'metrics': self.metrics
        }
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
    
    def record_metric(self, key: str, value: Any):
        """Record a metric."""
        self.metrics[key] = value
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            'healthy': self.running,
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': self._get_uptime()
        }
