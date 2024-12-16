"""
Core monitoring system implementation.
Contains base classes and main monitoring logic.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class CloudResource:
    """Base class for any cloud resource we want to monitor."""
    def __init__(self, resource_id: str, resource_type: str, region: str):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.region = region
        self.metadata: Dict = {}
        self.metrics: Dict = {}
        self.status = "unknown"
        
    def collect_metrics(self) -> Dict:
        """Abstract method that should be implemented by child classes."""
        raise NotImplementedError("Each resource type must implement collect_metrics()")

    def get_health_status(self) -> str:
        """Determine if the resource is healthy based on its metrics."""
        return self.status

class MetricData:
    """Represents a single metric measurement with its metadata."""
    def __init__(self, name: str, value: float, unit: str, timestamp: Optional[datetime] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat()
        }

class Alert:
    """Represents a monitoring alert."""
    def __init__(self, resource_id: str, metric_name: str, threshold: float,
                 current_value: float, severity: str):
        self.resource_id = resource_id
        self.metric_name = metric_name
        self.threshold = threshold
        self.current_value = current_value
        self.severity = severity
        self.timestamp = datetime.now()
        self.resolved = False

    def to_dict(self) -> Dict:
        return {
            "resource_id": self.resource_id,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved
        }

class MonitoringSystem:
    """Main monitoring system that orchestrates all monitoring activities."""
    def __init__(self):
        self.resources: Dict[str, CloudResource] = {}
        self.alerts: List[Alert] = []
        self.metric_history: Dict = {}
        
        # Define monitoring thresholds
        self.thresholds = {
            "CPUUtilization": 80.0,
            "MemoryUtilization": 80.0,
            "DiskUtilization": 85.0,
            "DatabaseConnections": 90.0
        }

    def add_resource(self, resource: CloudResource) -> None:
        """Add a resource to be monitored"""
        self.resources[resource.resource_id] = resource
        print(f"Added resource {resource.resource_id} for monitoring")

    def monitor_resources(self) -> None:
        """Main monitoring loop"""
        for resource in self.resources.values():
            metrics = resource.collect_metrics()
            self.check_thresholds(resource.resource_id, metrics)
            self.store_metrics(resource.resource_id, metrics)

    def check_thresholds(self, resource_id: str, metrics: Dict) -> None:
        """Check if any metrics exceed their thresholds and create alerts"""
        for metric_name, metric_data in metrics.items():
            if metric_name in self.thresholds:
                value = metric_data["value"]
                threshold = self.thresholds[metric_name]
                
                if value > threshold:
                    alert = Alert(
                        resource_id=resource_id,
                        metric_name=metric_name,
                        threshold=threshold,
                        current_value=value,
                        severity="HIGH"
                    )
                    self.alerts.append(alert)
