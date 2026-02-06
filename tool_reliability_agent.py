"""
Tool Reliability & Drift Agent
Mandatory before real-world operations.
Monitors API failures, data drift, and scraper decay.
Without this, systems rot silently.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import statistics


class ToolType(Enum):
    API = "api"
    SCRAPER = "scraper"
    DATABASE = "database"
    MODEL = "model"
    EXTERNAL_SERVICE = "external_service"


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CRITICAL = "critical"


class DriftType(Enum):
    DATA_SCHEMA = "data_schema"
    DATA_DISTRIBUTION = "data_distribution"
    RESPONSE_FORMAT = "response_format"
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"


@dataclass
class ToolMetric:
    """Represents a single metric measurement"""
    timestamp: datetime
    success: bool
    response_time: float
    error_message: Optional[str] = None
    data_sample: Optional[Any] = None


@dataclass
class DriftDetection:
    """Represents detected drift in a tool"""
    drift_type: DriftType
    severity: float  # 0.0 to 1.0
    description: str
    detected_at: datetime
    baseline_value: Any
    current_value: Any
    recommendation: str


@dataclass
class Tool:
    """Represents a monitored tool"""
    name: str
    tool_type: ToolType
    endpoint: str
    expected_response_time: float = 1.0  # seconds
    max_error_rate: float = 0.05  # 5%
    check_interval: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    metrics: List[ToolMetric] = field(default_factory=list)
    drift_detections: List[DriftDetection] = field(default_factory=list)
    last_check: Optional[datetime] = None
    health_status: HealthStatus = HealthStatus.HEALTHY


class ToolReliabilityAgent:
    """
    Monitors tool reliability and drift to prevent silent system degradation.
    """
    
    def __init__(
        self,
        metric_retention: timedelta = timedelta(days=30),
        drift_threshold: float = 0.3
    ):
        self.tools: Dict[str, Tool] = {}
        self.metric_retention = metric_retention
        self.drift_threshold = drift_threshold
        self.alert_callbacks: List[Callable] = []
        
    def register_tool(self, tool: Tool):
        """Register a tool for monitoring"""
        self.tools[tool.name] = tool
        
    def unregister_tool(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def record_metric(
        self,
        tool_name: str,
        success: bool,
        response_time: float,
        error_message: Optional[str] = None,
        data_sample: Optional[Any] = None
    ):
        """Record a metric for a tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        
        tool = self.tools[tool_name]
        
        metric = ToolMetric(
            timestamp=datetime.now(),
            success=success,
            response_time=response_time,
            error_message=error_message,
            data_sample=data_sample
        )
        
        tool.metrics.append(metric)
        tool.last_check = datetime.now()
        
        # Clean old metrics
        self._clean_old_metrics(tool)
        
        # Update health status
        self._update_health_status(tool)
        
        # Check for drift
        drift = self._check_for_drift(tool)
        if drift:
            tool.drift_detections.append(drift)
            self._trigger_alert(tool, drift)
    
    def _clean_old_metrics(self, tool: Tool):
        """Remove metrics older than retention period"""
        cutoff = datetime.now() - self.metric_retention
        tool.metrics = [m for m in tool.metrics if m.timestamp >= cutoff]
    
    def _update_health_status(self, tool: Tool):
        """Update tool health status based on recent metrics"""
        if not tool.metrics:
            tool.health_status = HealthStatus.HEALTHY
            return
        
        # Analyze recent metrics (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in tool.metrics if m.timestamp >= recent_cutoff]
        
        if not recent_metrics:
            return
        
        # Calculate error rate
        error_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
        
        # Calculate average response time
        response_times = [m.response_time for m in recent_metrics]
        avg_response_time = statistics.mean(response_times)
        
        # Determine health status
        if error_rate > tool.max_error_rate * 3:
            tool.health_status = HealthStatus.CRITICAL
        elif error_rate > tool.max_error_rate * 2:
            tool.health_status = HealthStatus.FAILING
        elif error_rate > tool.max_error_rate or avg_response_time > tool.expected_response_time * 2:
            tool.health_status = HealthStatus.DEGRADED
        else:
            tool.health_status = HealthStatus.HEALTHY
    
    def _check_for_drift(self, tool: Tool) -> Optional[DriftDetection]:
        """Check if tool is experiencing drift"""
        if len(tool.metrics) < 100:
            # Need enough data to detect drift
            return None
        
        # Get baseline (first 20% of metrics) and current (last 20% of metrics)
        baseline_size = len(tool.metrics) // 5
        baseline_metrics = tool.metrics[:baseline_size]
        current_metrics = tool.metrics[-baseline_size:]
        
        # Check performance drift
        baseline_response_time = statistics.mean([m.response_time for m in baseline_metrics])
        current_response_time = statistics.mean([m.response_time for m in current_metrics])
        
        if current_response_time > baseline_response_time * (1 + self.drift_threshold):
            severity = min((current_response_time - baseline_response_time) / baseline_response_time, 1.0)
            return DriftDetection(
                drift_type=DriftType.PERFORMANCE,
                severity=severity,
                description=f"Response time degraded by {(severity*100):.1f}%",
                detected_at=datetime.now(),
                baseline_value=baseline_response_time,
                current_value=current_response_time,
                recommendation="Investigate performance issues, check server load, optimize queries"
            )
        
        # Check error rate drift
        baseline_error_rate = sum(1 for m in baseline_metrics if not m.success) / len(baseline_metrics)
        current_error_rate = sum(1 for m in current_metrics if not m.success) / len(current_metrics)
        
        if current_error_rate > baseline_error_rate * (1 + self.drift_threshold):
            severity = min((current_error_rate - baseline_error_rate) / max(baseline_error_rate, 0.01), 1.0)
            return DriftDetection(
                drift_type=DriftType.ERROR_RATE,
                severity=severity,
                description=f"Error rate increased by {(severity*100):.1f}%",
                detected_at=datetime.now(),
                baseline_value=baseline_error_rate,
                current_value=current_error_rate,
                recommendation="Review recent errors, check API changes, verify credentials"
            )
        
        return None
    
    def _trigger_alert(self, tool: Tool, drift: DriftDetection):
        """Trigger alert callbacks for drift detection"""
        for callback in self.alert_callbacks:
            try:
                callback(tool, drift)
            except Exception as e:
                print(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback to be called when drift is detected"""
        self.alert_callbacks.append(callback)
    
    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed status for a tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not registered")
        
        tool = self.tools[tool_name]
        
        # Calculate metrics
        if not tool.metrics:
            return {
                "name": tool.name,
                "type": tool.tool_type.value,
                "health": tool.health_status.value,
                "metrics_available": False
            }
        
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in tool.metrics if m.timestamp >= recent_cutoff]
        
        if not recent_metrics:
            recent_metrics = tool.metrics[-100:] if len(tool.metrics) >= 100 else tool.metrics
        
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics)
        avg_response_time = statistics.mean([m.response_time for m in recent_metrics])
        
        return {
            "name": tool.name,
            "type": tool.tool_type.value,
            "health": tool.health_status.value,
            "metrics_available": True,
            "total_checks": len(tool.metrics),
            "recent_checks": len(recent_metrics),
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "last_check": tool.last_check,
            "drift_detections": len(tool.drift_detections),
            "recent_drifts": [
                {
                    "type": d.drift_type.value,
                    "severity": d.severity,
                    "description": d.description,
                    "detected_at": d.detected_at
                }
                for d in tool.drift_detections[-5:]
            ]
        }
    
    def get_system_health_report(self) -> str:
        """Generate a system-wide health report"""
        report = "\nTool Reliability & Drift Report\n"
        report += "="*60 + "\n\n"
        
        if not self.tools:
            report += "No tools registered.\n"
            return report
        
        # Overall statistics
        total_tools = len(self.tools)
        healthy_tools = sum(1 for t in self.tools.values() if t.health_status == HealthStatus.HEALTHY)
        degraded_tools = sum(1 for t in self.tools.values() if t.health_status == HealthStatus.DEGRADED)
        failing_tools = sum(1 for t in self.tools.values() if t.health_status == HealthStatus.FAILING)
        critical_tools = sum(1 for t in self.tools.values() if t.health_status == HealthStatus.CRITICAL)
        
        report += f"System Overview:\n"
        report += f"  Total Tools: {total_tools}\n"
        report += f"  ✓ Healthy: {healthy_tools}\n"
        report += f"  ⚠ Degraded: {degraded_tools}\n"
        report += f"  ✗ Failing: {failing_tools}\n"
        report += f"  🚨 Critical: {critical_tools}\n\n"
        
        # Tool details
        report += "Tool Details:\n"
        report += "-" * 60 + "\n"
        
        for tool_name in sorted(self.tools.keys()):
            status = self.get_tool_status(tool_name)
            
            health_icon = {
                "healthy": "✓",
                "degraded": "⚠",
                "failing": "✗",
                "critical": "🚨"
            }.get(status["health"], "?")
            
            report += f"\n{health_icon} {status['name']} ({status['type']})\n"
            report += f"  Health: {status['health'].upper()}\n"
            
            if status["metrics_available"]:
                report += f"  Success Rate: {status['success_rate']*100:.1f}%\n"
                report += f"  Avg Response Time: {status['avg_response_time']:.3f}s\n"
                report += f"  Total Checks: {status['total_checks']}\n"
                report += f"  Recent Checks: {status['recent_checks']}\n"
                
                if status['last_check']:
                    report += f"  Last Check: {status['last_check']}\n"
                
                if status['drift_detections'] > 0:
                    report += f"  Drift Detections: {status['drift_detections']}\n"
                    
                    if status['recent_drifts']:
                        report += f"  Recent Drifts:\n"
                        for drift in status['recent_drifts']:
                            report += f"    - [{drift['type']}] {drift['description']} "
                            report += f"(severity: {drift['severity']:.2f})\n"
            else:
                report += f"  No metrics available\n"
        
        return report
    
    def get_recommendations(self) -> List[str]:
        """Get actionable recommendations based on current tool health"""
        recommendations = []
        
        for tool_name, tool in self.tools.items():
            if tool.health_status == HealthStatus.CRITICAL:
                recommendations.append(
                    f"URGENT: {tool_name} is in critical state. Immediate investigation required."
                )
            elif tool.health_status == HealthStatus.FAILING:
                recommendations.append(
                    f"HIGH PRIORITY: {tool_name} is failing. Review and fix issues soon."
                )
            elif tool.health_status == HealthStatus.DEGRADED:
                recommendations.append(
                    f"MONITOR: {tool_name} is degraded. Consider investigation if it persists."
                )
            
            # Recent drift recommendations
            recent_drifts = tool.drift_detections[-3:] if tool.drift_detections else []
            for drift in recent_drifts:
                recommendations.append(
                    f"{tool_name}: {drift.recommendation}"
                )
        
        return recommendations


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = ToolReliabilityAgent(
        metric_retention=timedelta(days=7),
        drift_threshold=0.2
    )
    
    # Add alert callback
    def alert_handler(tool: Tool, drift: DriftDetection):
        print(f"\n🚨 DRIFT ALERT: {tool.name}")
        print(f"   Type: {drift.drift_type.value}")
        print(f"   Severity: {drift.severity:.2f}")
        print(f"   {drift.description}")
        print(f"   Recommendation: {drift.recommendation}\n")
    
    agent.add_alert_callback(alert_handler)
    
    # Register tools
    api_tool = Tool(
        name="payment_api",
        tool_type=ToolType.API,
        endpoint="https://api.payment.com/v1",
        expected_response_time=0.5,
        max_error_rate=0.02
    )
    agent.register_tool(api_tool)
    
    scraper_tool = Tool(
        name="news_scraper",
        tool_type=ToolType.SCRAPER,
        endpoint="https://news.example.com",
        expected_response_time=2.0,
        max_error_rate=0.10
    )
    agent.register_tool(scraper_tool)
    
    db_tool = Tool(
        name="user_database",
        tool_type=ToolType.DATABASE,
        endpoint="postgresql://localhost:5432/users",
        expected_response_time=0.1,
        max_error_rate=0.01
    )
    agent.register_tool(db_tool)
    
    # Simulate some metrics
    import random
    
    # Healthy API
    for i in range(150):
        agent.record_metric(
            "payment_api",
            success=random.random() < 0.98,
            response_time=random.gauss(0.5, 0.1)
        )
    
    # Degrading scraper
    for i in range(150):
        # Gradually increase errors and response time
        error_prob = 0.05 + (i / 150) * 0.15
        base_time = 2.0 + (i / 150) * 2.0
        
        agent.record_metric(
            "news_scraper",
            success=random.random() > error_prob,
            response_time=random.gauss(base_time, 0.5)
        )
    
    # Stable database
    for i in range(150):
        agent.record_metric(
            "user_database",
            success=random.random() < 0.995,
            response_time=random.gauss(0.1, 0.02)
        )
    
    # Generate report
    print(agent.get_system_health_report())
    
    print("\nRecommendations:")
    print("-" * 60)
    for rec in agent.get_recommendations():
        print(f"  • {rec}")
