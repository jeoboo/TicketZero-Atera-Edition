#!/usr/bin/env python3
"""
Health Monitor for TicketZero AI MSP Edition
System health checks and monitoring
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class HealthMonitor:
    """System health monitoring and alerting"""

    def __init__(self, msp_system):
        self.msp_system = msp_system
        self.health_status = {
            "overall": "unknown",
            "components": {},
            "last_check": None,
            "alerts": []
        }
        self.check_interval = 60  # seconds

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("Starting health monitoring...")

        while True:
            try:
                await self.perform_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(30)  # Shorter retry interval on error

    async def perform_health_check(self):
        """Perform comprehensive system health check"""
        check_time = datetime.now()
        components = {}

        # Check AI Providers
        ai_status = await self._check_ai_providers()
        components["ai_providers"] = ai_status

        # Check MSP System Performance
        performance_status = self._check_system_performance()
        components["performance"] = performance_status

        # Check Client Configurations
        client_status = self._check_client_configs()
        components["clients"] = client_status

        # Check Recent Metrics
        metrics_status = self._check_metrics_health()
        components["metrics"] = metrics_status

        # Determine overall health
        overall_health = self._calculate_overall_health(components)

        # Update status
        self.health_status = {
            "overall": overall_health,
            "components": components,
            "last_check": check_time.isoformat(),
            "alerts": self._generate_alerts(components)
        }

        # Log health status
        logger.info(f"Health Check - Overall: {overall_health}, "
                   f"Alerts: {len(self.health_status['alerts'])}")

    async def _check_ai_providers(self) -> Dict[str, Any]:
        """Check AI provider availability and response times"""
        provider_status = {}

        for provider_name, provider in self.msp_system.ai_providers.items():
            start_time = time.time()

            try:
                # Quick test request
                test_ticket = {
                    'TicketTitle': 'Health Check Test',
                    'FirstComment': 'System health monitoring test'
                }

                response = await asyncio.wait_for(
                    provider.get_solution(test_ticket, timeout=3),
                    timeout=5
                )

                response_time = time.time() - start_time

                if response:
                    provider_status[provider_name] = {
                        "status": "healthy",
                        "response_time": round(response_time, 2),
                        "last_check": datetime.now().isoformat()
                    }
                else:
                    provider_status[provider_name] = {
                        "status": "unhealthy",
                        "error": "No response received",
                        "response_time": round(response_time, 2),
                        "last_check": datetime.now().isoformat()
                    }

            except asyncio.TimeoutError:
                provider_status[provider_name] = {
                    "status": "timeout",
                    "error": "Response timeout",
                    "response_time": time.time() - start_time,
                    "last_check": datetime.now().isoformat()
                }
            except Exception as e:
                provider_status[provider_name] = {
                    "status": "error",
                    "error": str(e),
                    "response_time": time.time() - start_time,
                    "last_check": datetime.now().isoformat()
                }

        return provider_status

    def _check_system_performance(self) -> Dict[str, Any]:
        """Check system performance metrics"""
        recent_metrics = [
            m for m in self.msp_system.metrics
            if m.start_time > datetime.now() - timedelta(hours=1)
        ]

        if not recent_metrics:
            return {
                "status": "no_data",
                "message": "No recent metrics available"
            }

        # Calculate performance indicators
        avg_processing_time = sum(m.total_processing_time for m in recent_metrics) / len(recent_metrics)
        resolved_count = len([m for m in recent_metrics if m.resolution_status == "resolved"])
        resolution_rate = (resolved_count / len(recent_metrics)) * 100

        # Determine status based on thresholds
        if avg_processing_time > 10:
            status = "degraded"
        elif resolution_rate < 50:
            status = "degraded"
        else:
            status = "healthy"

        return {
            "status": status,
            "metrics": {
                "avg_processing_time": round(avg_processing_time, 2),
                "resolution_rate": round(resolution_rate, 1),
                "total_tickets_hour": len(recent_metrics),
                "resolved_tickets_hour": resolved_count
            }
        }

    def _check_client_configs(self) -> Dict[str, Any]:
        """Check client configuration validity"""
        client_issues = []

        for client_id, client in self.msp_system.clients.items():
            # Check if client has required configuration
            if not client.atera_api_key or client.atera_api_key.startswith("${"):
                client_issues.append(f"Client {client_id}: Missing Atera API key")

            if client.response_timeout > 10:
                client_issues.append(f"Client {client_id}: Response timeout too high ({client.response_timeout}s)")

        return {
            "status": "healthy" if not client_issues else "issues",
            "total_clients": len(self.msp_system.clients),
            "issues": client_issues
        }

    def _check_metrics_health(self) -> Dict[str, Any]:
        """Check metrics collection health"""
        total_metrics = len(self.msp_system.metrics)
        recent_metrics = len([
            m for m in self.msp_system.metrics
            if m.start_time > datetime.now() - timedelta(hours=24)
        ])

        return {
            "status": "healthy" if recent_metrics > 0 else "no_activity",
            "total_metrics": total_metrics,
            "metrics_24h": recent_metrics
        }

    def _calculate_overall_health(self, components: Dict[str, Any]) -> str:
        """Calculate overall system health"""
        # Check for critical issues
        ai_providers = components.get("ai_providers", {})
        healthy_providers = len([p for p in ai_providers.values() if p.get("status") == "healthy"])

        if healthy_providers == 0:
            return "critical"

        performance = components.get("performance", {})
        if performance.get("status") == "degraded":
            return "degraded"

        clients = components.get("clients", {})
        if clients.get("status") == "issues":
            return "warning"

        return "healthy"

    def _generate_alerts(self, components: Dict[str, Any]) -> List[Dict]:
        """Generate alerts based on component status"""
        alerts = []
        now = datetime.now()

        # AI Provider alerts
        ai_providers = components.get("ai_providers", {})
        for provider_name, status in ai_providers.items():
            if status.get("status") not in ["healthy"]:
                alerts.append({
                    "type": "ai_provider_issue",
                    "severity": "high" if status.get("status") == "error" else "medium",
                    "message": f"AI Provider {provider_name}: {status.get('status')} - {status.get('error', 'Unknown issue')}",
                    "timestamp": now.isoformat(),
                    "component": f"ai_provider_{provider_name}"
                })

        # Performance alerts
        performance = components.get("performance", {})
        if performance.get("status") == "degraded":
            metrics = performance.get("metrics", {})
            alerts.append({
                "type": "performance_degraded",
                "severity": "medium",
                "message": f"Performance degraded - Avg time: {metrics.get('avg_processing_time', 0)}s, Resolution rate: {metrics.get('resolution_rate', 0)}%",
                "timestamp": now.isoformat(),
                "component": "performance"
            })

        # Client configuration alerts
        clients = components.get("clients", {})
        for issue in clients.get("issues", []):
            alerts.append({
                "type": "client_config_issue",
                "severity": "low",
                "message": issue,
                "timestamp": now.isoformat(),
                "component": "client_config"
            })

        return alerts

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status

    def get_health_summary(self) -> Dict[str, Any]:
        """Get simplified health summary"""
        return {
            "status": self.health_status.get("overall", "unknown"),
            "last_check": self.health_status.get("last_check"),
            "alert_count": len(self.health_status.get("alerts", [])),
            "components_healthy": len([
                c for c in self.health_status.get("components", {}).values()
                if c.get("status") == "healthy"
            ])
        }

    async def send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification (implement based on your notification system)"""
        # This would integrate with Slack, email, or other notification systems
        logger.warning(f"ALERT: {alert['message']}")

        # Example Slack integration (uncomment and configure)
        # slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        # if slack_webhook:
        #     payload = {
        #         "text": f"TicketZero Alert: {alert['message']}",
        #         "color": "danger" if alert['severity'] == "high" else "warning"
        #     }
        #     async with aiohttp.ClientSession() as session:
        #         await session.post(slack_webhook, json=payload)

def start_health_monitoring(msp_system):
    """Start health monitoring as a background task"""
    monitor = HealthMonitor(msp_system)
    return asyncio.create_task(monitor.start_monitoring())

if __name__ == "__main__":
    print("Health Monitor - Use with msp_ticketzero_optimized.py")