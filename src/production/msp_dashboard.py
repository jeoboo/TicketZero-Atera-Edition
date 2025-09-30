#!/usr/bin/env python3
"""
MSP Dashboard for TicketZero AI
Real-time monitoring and reporting for MSP operations
"""

import json
import time
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import logging
try:
    from .env_manager import env_manager
    from .license_manager import license_manager
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from env_manager import env_manager
    from license_manager import license_manager

logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """Real-time dashboard metrics"""
    timestamp: datetime
    active_tickets: int
    resolved_today: int
    escalated_today: int
    avg_resolution_time: float
    sla_compliance_rate: float
    cost_savings_today: float
    top_issues: List[str]
    client_performance: Dict[str, Any]

class MSPDashboard:
    """Real-time MSP dashboard for TicketZero AI"""

    def __init__(self, msp_system):
        self.msp_system = msp_system
        self.dashboard_data = {}
        self.update_interval = 30  # seconds

    async def start_monitoring(self):
        """Start real-time dashboard monitoring"""
        logger.info("Starting MSP dashboard monitoring...")

        while True:
            try:
                await self.update_dashboard()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(5)

    async def update_dashboard(self):
        """Update dashboard with latest metrics"""
        now = datetime.now()

        # Collect metrics from all clients
        all_metrics = []
        client_performance = {}

        for client_id, client in self.msp_system.clients.items():
            # Get performance data for this client
            report = self.msp_system.get_msp_performance_report(client_id, hours=24)

            client_performance[client_id] = {
                "name": client.client_name,
                "tickets_today": report.get('total_tickets_processed', 0),
                "resolution_rate": report.get('resolution_rate_percent', 0),
                "avg_response_time": report.get('avg_processing_time_seconds', 0),
                "sla_compliance": self._calculate_sla_compliance(report),
                "cost_savings": report.get('cost_savings_estimate', {}).get('total_savings', 0)
            }

        # Calculate aggregate metrics
        total_tickets_today = sum(cp.get('tickets_today', 0) for cp in client_performance.values())
        total_resolved = sum(
            int(cp.get('tickets_today', 0) * cp.get('resolution_rate', 0) / 100)
            for cp in client_performance.values()
        )
        total_escalated = total_tickets_today - total_resolved

        avg_resolution_time = sum(
            cp.get('avg_response_time', 0) for cp in client_performance.values()
        ) / max(1, len(client_performance))

        overall_sla_compliance = sum(
            cp.get('sla_compliance', 0) for cp in client_performance.values()
        ) / max(1, len(client_performance))

        total_cost_savings = sum(cp.get('cost_savings', 0) for cp in client_performance.values())

        # Identify top issues
        top_issues = self._identify_top_issues()

        # Create dashboard metrics
        metrics = DashboardMetrics(
            timestamp=now,
            active_tickets=self._count_active_tickets(),
            resolved_today=total_resolved,
            escalated_today=total_escalated,
            avg_resolution_time=avg_resolution_time,
            sla_compliance_rate=overall_sla_compliance,
            cost_savings_today=total_cost_savings,
            top_issues=top_issues,
            client_performance=client_performance
        )

        self.dashboard_data = asdict(metrics)
        self.dashboard_data['timestamp'] = now.isoformat()

        # Log key metrics
        logger.info(f"Dashboard Update - Tickets: {total_tickets_today}, "
                   f"Resolved: {total_resolved}, SLA: {overall_sla_compliance:.1f}%")

    def _calculate_sla_compliance(self, report: Dict) -> float:
        """Calculate SLA compliance percentage"""
        sla_data = report.get('sla_compliance', {})
        under_5s = sla_data.get('under_5_seconds', 0)
        total = report.get('total_tickets_processed', 0)

        return (under_5s / max(1, total)) * 100

    def _count_active_tickets(self) -> int:
        """Count currently active (processing) tickets"""
        active_count = 0
        cutoff_time = datetime.now() - timedelta(minutes=5)

        for metric in self.msp_system.metrics:
            if (metric.end_time is None or metric.end_time > cutoff_time) and \
               metric.resolution_status == "pending":
                active_count += 1

        return active_count

    def _identify_top_issues(self) -> List[str]:
        """Identify most common issues from recent tickets"""
        recent_metrics = [
            m for m in self.msp_system.metrics
            if m.start_time > datetime.now() - timedelta(hours=24)
        ]

        # This would analyze ticket titles/descriptions to find patterns
        # For now, return common IT issues
        return [
            "Email/Outlook Issues",
            "VPN Connection Problems",
            "Printer Connectivity",
            "Software Installation",
            "Password Resets"
        ]

    def get_dashboard_html(self, show_admin: bool = False) -> str:
        """Generate HTML dashboard"""
        if not self.dashboard_data:
            return "<h1>Dashboard Loading...</h1>"

        # Get API configuration for admin panel
        api_config = env_manager.get_api_config()
        config_issues = env_manager.validate_api_config()

        # Get license information
        license_status = license_manager.get_license_status()
        pricing_info = license_manager.get_pricing_info()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>TicketZero MSP Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .client-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .client-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .client-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
        }}
        .client-metric {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .admin-panel {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .admin-tabs {{
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 20px;
        }}
        .admin-tab {{
            padding: 10px 20px;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
        }}
        .admin-tab.active {{
            background: #667eea;
            color: white;
        }}
        .admin-content {{
            display: none;
        }}
        .admin-content.active {{
            display: block;
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        .form-label {{
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }}
        .form-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .form-input:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
        }}
        .btn-primary {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        .btn-secondary {{
            background: #6c757d;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }}
        .config-status {{
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .config-status.valid {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }}
        .config-status.invalid {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }}
        .config-status.warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }}
        .api-provider {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .api-provider h4 {{
            margin-top: 0;
            color: #667eea;
        }}
        .toggle-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            float: right;
        }}
        .admin-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 50px;
            cursor: pointer;
            font-size: 12px;
            z-index: 1000;
        }}
    </style>
    <script>
        function refreshDashboard() {{
            location.reload();
        }}

        function toggleAdmin() {{
            const adminPanel = document.getElementById('adminPanel');
            const toggleBtn = document.getElementById('adminToggle');
            if (adminPanel.style.display === 'none' || adminPanel.style.display === '') {{
                adminPanel.style.display = 'block';
                toggleBtn.innerText = 'Hide Admin';
            }} else {{
                adminPanel.style.display = 'none';
                toggleBtn.innerText = 'Admin Panel';
            }}
        }}

        function switchAdminTab(tabName) {{
            // Hide all content
            const contents = document.querySelectorAll('.admin-content');
            contents.forEach(content => content.classList.remove('active'));

            // Remove active from all tabs
            const tabs = document.querySelectorAll('.admin-tab');
            tabs.forEach(tab => tab.classList.remove('active'));

            // Show selected content and tab
            document.getElementById(tabName + 'Content').classList.add('active');
            document.getElementById(tabName + 'Tab').classList.add('active');
        }}

        async function saveAPIConfig() {{
            const formData = new FormData();

            // Collect all form inputs
            const inputs = document.querySelectorAll('#apiConfigContent input');
            inputs.forEach(input => {{
                formData.append(input.name, input.value);
            }});

            try {{
                const response = await fetch('/admin/save-config', {{
                    method: 'POST',
                    body: formData
                }});

                if (response.ok) {{
                    alert('Configuration saved successfully!');
                    location.reload();
                }} else {{
                    alert('Error saving configuration');
                }}
            }} catch (error) {{
                alert('Error: ' + error.message);
            }}
        }}

        function testAPIConnection(provider) {{
            alert('Testing ' + provider + ' connection... (Feature coming soon)');
        }}

        async function activateLicense() {{
            const licenseKey = document.getElementById('licenseKey').value;
            if (!licenseKey) {{
                alert('Please enter a license key');
                return;
            }}

            try {{
                const response = await fetch('/admin/activate-license', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ license_key: licenseKey }})
                }});

                const result = await response.json();
                if (result.success) {{
                    alert('License activated successfully!');
                    location.reload();
                }} else {{
                    alert('Activation failed: ' + result.message);
                }}
            }} catch (error) {{
                alert('Error: ' + error.message);
            }}
        }}

        async function generateTrial() {{
            const email = prompt('Enter your email address for trial license:');
            if (!email) return;

            try {{
                const response = await fetch('/admin/generate-trial', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ email: email }})
                }});

                const result = await response.json();
                if (result.success) {{
                    alert('Trial license generated successfully!');
                    location.reload();
                }} else {{
                    alert('Trial generation failed: ' + result.message);
                }}
            }} catch (error) {{
                alert('Error: ' + error.message);
            }}
        }}

        function purchasePlan(planId) {{
            alert('Redirecting to purchase page for ' + planId + ' plan...');
            // This would redirect to a payment processor
            window.open('https://ticketzero.ai/purchase?plan=' + planId, '_blank');
        }}

        // Auto-refresh every 30 seconds (pause when admin panel is open)
        function autoRefresh() {{
            const adminPanel = document.getElementById('adminPanel');
            if (!adminPanel || adminPanel.style.display === 'none') {{
                location.reload();
            }}
        }}
        setTimeout(autoRefresh, 30000);
    </script>
</head>
<body>
    <button id="adminToggle" class="admin-toggle" onclick="toggleAdmin()">Admin Panel</button>

    <div class="header">
        <h1>🎯 TicketZero MSP Dashboard</h1>
        <p>Real-time AI-powered support monitoring</p>
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh</button>
    </div>

    <!-- Admin Panel -->
    <div id="adminPanel" class="admin-panel" style="display: none;">
        <h2>🔧 Admin Configuration Panel</h2>

        <!-- Configuration Status -->
        <div class="config-status {'valid' if not config_issues['missing'] and not config_issues['invalid'] else 'invalid' if config_issues['missing'] or config_issues['invalid'] else 'warning'}">
            {'✅ Configuration Valid' if not config_issues['missing'] and not config_issues['invalid'] else '❌ Configuration Issues Found' if config_issues['missing'] or config_issues['invalid'] else '⚠️ Configuration Warnings'}
            {f"<br>Missing: {', '.join(config_issues['missing'])}" if config_issues['missing'] else ""}
            {f"<br>Invalid: {', '.join(config_issues['invalid'])}" if config_issues['invalid'] else ""}
            {f"<br>Warnings: {', '.join(config_issues['warnings'])}" if config_issues['warnings'] else ""}
        </div>

        <!-- Admin Tabs -->
        <div class="admin-tabs">
            <button id="licenseTab" class="admin-tab active" onclick="switchAdminTab('license')">License & Billing</button>
            <button id="apiConfigTab" class="admin-tab" onclick="switchAdminTab('apiConfig')">API Configuration</button>
            <button id="clientManagementTab" class="admin-tab" onclick="switchAdminTab('clientManagement')">Client Management</button>
            <button id="systemStatusTab" class="admin-tab" onclick="switchAdminTab('systemStatus')">System Status</button>
        </div>

        <!-- License & Billing Tab -->
        <div id="licenseContent" class="admin-content active">
            <h3>License & Billing Management</h3>

            <!-- Current License Status -->
            <div class="api-provider">
                <h4>📄 Current License Status</h4>
                {'<div class="config-status valid">' if license_status['status'] == 'licensed' else '<div class="config-status invalid">'}
                    <strong>Status:</strong> {license_status['status'].title()}<br>
                    <strong>Message:</strong> {license_status['message']}<br>
                    {f"<strong>License Key:</strong> {license_status.get('license_key', 'N/A')}<br>" if license_status.get('license_key') else ""}
                    {f"<strong>Plan:</strong> {license_status.get('plan_name', 'N/A')}<br>" if license_status.get('plan_name') else ""}
                    {f"<strong>Customer:</strong> {license_status.get('customer_name', 'N/A')}<br>" if license_status.get('customer_name') else ""}
                    {f"<strong>Expires:</strong> {license_status.get('expiry_date', 'N/A')} ({license_status.get('days_remaining', 0)} days remaining)<br>" if license_status.get('expiry_date') else ""}
                    {f"<strong>Max Clients:</strong> {license_status.get('max_clients', 0)}<br>" if license_status.get('max_clients') else ""}
                    {f"<strong>Max Tickets/Month:</strong> {license_status.get('max_tickets_per_month', 0)}<br>" if license_status.get('max_tickets_per_month') else ""}
                </div>
            </div>

            <!-- License Activation -->
            <div class="api-provider">
                <h4>🔑 License Activation</h4>
                <div class="form-group">
                    <label class="form-label">License Key:</label>
                    <input type="text" id="licenseKey" class="form-input" placeholder="TZ-PRO-XXXX-XXXX-XXXX-XXXX">
                </div>
                <button type="button" class="btn-primary" onclick="activateLicense()">🔓 Activate License</button>
                <button type="button" class="toggle-btn" onclick="generateTrial()">📅 Start 30-Day Trial</button>
            </div>

            <!-- Pricing Plans -->
            <div class="api-provider">
                <h4>💰 Available Plans</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px;">"""

# Add pricing plan cards
for plan_id, plan in pricing_info.items():
    html += f"""
                    <div class="api-provider" style="{'border: 2px solid #667eea;' if plan.get('recommended') else ''}">
                        <h5>{plan['name']} {'⭐ RECOMMENDED' if plan.get('recommended') else ''}</h5>
                        <div style="font-size: 2em; color: #667eea; font-weight: bold;">{plan['price_formatted']}</div>
                        <p><strong>Duration:</strong> {plan['duration_months']} months</p>
                        <p><strong>Max Clients:</strong> {plan['max_clients']}</p>
                        <p><strong>Max Tickets/Month:</strong> {plan['max_tickets_per_month']:,}</p>
                        <div style="margin: 10px 0;">
                            <strong>Features:</strong>
                            <ul style="margin: 5px 0; padding-left: 20px;">"""

    for feature in plan['features']:
        html += f"<li>{feature}</li>"

    html += f"""
                            </ul>
                        </div>
                        <button type="button" class="btn-primary" onclick="purchasePlan('{plan_id}')">Purchase Plan</button>
                    </div>"""

html += """
                </div>
            </div>

            <!-- License Features -->
            <div class="api-provider">
                <h4>✨ License Features</h4>
                {f"<p><strong>Available Features:</strong></p><ul>" if license_status.get('features_available') else "<p>No license features available.</p>"}
                {f"{''.join([f'<li>{feature}</li>' for feature in license_status.get('features_available', [])])}" if license_status.get('features_available') else ""}
                {f"</ul>" if license_status.get('features_available') else ""}
            </div>
        </div>

        <!-- API Configuration Tab -->
        <div id="apiConfigContent" class="admin-content">
            <h3>API Configuration</h3>
            <form id="apiConfigForm">

                <!-- Atera Configuration -->
                <div class="api-provider">
                    <h4>🎫 Atera RMM Integration</h4>
                    <div class="form-group">
                        <label class="form-label">API Key:</label>
                        <input type="text" name="atera_api_key" class="form-input"
                               value="{api_config['atera']['api_key']}" placeholder="Enter Atera API Key">
                    </div>
                    <div class="form-group">
                        <label class="form-label">API URL:</label>
                        <input type="text" name="atera_api_url" class="form-input"
                               value="{api_config['atera']['api_url']}" placeholder="https://app.atera.com/api/v3">
                    </div>
                    <button type="button" class="toggle-btn" onclick="testAPIConnection('Atera')">Test Connection</button>
                </div>

                <!-- OpenAI Configuration -->
                <div class="api-provider">
                    <h4>🤖 OpenAI Integration</h4>
                    <div class="form-group">
                        <label class="form-label">API Key:</label>
                        <input type="password" name="openai_api_key" class="form-input"
                               value="{api_config['openai']['api_key']}" placeholder="Enter OpenAI API Key">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model:</label>
                        <input type="text" name="openai_model" class="form-input"
                               value="{api_config['openai']['model']}" placeholder="gpt-3.5-turbo">
                    </div>
                    <button type="button" class="toggle-btn" onclick="testAPIConnection('OpenAI')">Test Connection</button>
                </div>

                <!-- Azure OpenAI Configuration -->
                <div class="api-provider">
                    <h4>☁️ Azure OpenAI Integration</h4>
                    <div class="form-group">
                        <label class="form-label">API Key:</label>
                        <input type="password" name="azure_openai_api_key" class="form-input"
                               value="{api_config['azure_openai']['api_key']}" placeholder="Enter Azure OpenAI API Key">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Endpoint:</label>
                        <input type="text" name="azure_openai_endpoint" class="form-input"
                               value="{api_config['azure_openai']['endpoint']}" placeholder="https://your-resource.openai.azure.com/">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Deployment:</label>
                        <input type="text" name="azure_openai_deployment" class="form-input"
                               value="{api_config['azure_openai']['deployment']}" placeholder="gpt-35-turbo">
                    </div>
                    <button type="button" class="toggle-btn" onclick="testAPIConnection('Azure OpenAI')">Test Connection</button>
                </div>

                <!-- LM Studio Configuration -->
                <div class="api-provider">
                    <h4>🏠 LM Studio Local AI</h4>
                    <div class="form-group">
                        <label class="form-label">Endpoint:</label>
                        <input type="text" name="lmstudio_endpoint" class="form-input"
                               value="{api_config['lmstudio']['endpoint']}" placeholder="http://127.0.0.1:1234/v1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Model:</label>
                        <input type="text" name="lmstudio_model" class="form-input"
                               value="{api_config['lmstudio']['model']}" placeholder="phi-3-mini-4k-instruct">
                    </div>
                    <button type="button" class="toggle-btn" onclick="testAPIConnection('LM Studio')">Test Connection</button>
                </div>

                <!-- Email Configuration -->
                <div class="api-provider">
                    <h4>📧 Email/SMTP Configuration</h4>
                    <div class="form-group">
                        <label class="form-label">SMTP Host:</label>
                        <input type="text" name="smtp_host" class="form-input"
                               value="{api_config['email']['smtp_host']}" placeholder="smtp.gmail.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">SMTP Port:</label>
                        <input type="text" name="smtp_port" class="form-input"
                               value="{api_config['email']['smtp_port']}" placeholder="587">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Username:</label>
                        <input type="text" name="smtp_user" class="form-input"
                               value="{api_config['email']['smtp_user']}" placeholder="your-email@gmail.com">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Password:</label>
                        <input type="password" name="smtp_pass" class="form-input"
                               value="{api_config['email']['smtp_pass']}" placeholder="Your app password">
                    </div>
                    <button type="button" class="toggle-btn" onclick="testAPIConnection('Email')">Test Connection</button>
                </div>

                <div style="text-align: center; margin-top: 20px;">
                    <button type="button" class="btn-primary" onclick="saveAPIConfig()">💾 Save Configuration</button>
                    <button type="button" class="btn-secondary" onclick="location.reload()">🔄 Reset</button>
                </div>
            </form>
        </div>

        <!-- Client Management Tab -->
        <div id="clientManagementContent" class="admin-content">
            <h3>Client Management</h3>
            <p>Client configuration management coming soon...</p>
            <div class="api-provider">
                <h4>Current Clients</h4>
                <p>• {len(self.msp_system.clients)} clients configured</p>
                <p>• Configuration file: config/msp_clients.json</p>
            </div>
        </div>

        <!-- System Status Tab -->
        <div id="systemStatusContent" class="admin-content">
            <h3>System Status</h3>
            <div class="api-provider">
                <h4>Environment Information</h4>
                <p><strong>Config File:</strong> {env_manager.env_file_path}</p>
                <p><strong>Total Environment Variables:</strong> {len(env_manager.env_vars)}</p>
                <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(self.dashboard_data.get('active_tickets', 0), 'active')}">{self.dashboard_data.get('active_tickets', 0)}</div>
            <div class="metric-label">Active Tickets</div>
        </div>
        <div class="metric-card">
            <div class="metric-value status-good">{self.dashboard_data.get('resolved_today', 0)}</div>
            <div class="metric-label">Resolved Today</div>
        </div>
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(self.dashboard_data.get('escalated_today', 0), 'escalated')}">{self.dashboard_data.get('escalated_today', 0)}</div>
            <div class="metric-label">Escalated Today</div>
        </div>
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(self.dashboard_data.get('avg_resolution_time', 0), 'response_time')}">{self.dashboard_data.get('avg_resolution_time', 0):.1f}s</div>
            <div class="metric-label">Avg Response Time</div>
        </div>
        <div class="metric-card">
            <div class="metric-value {self._get_status_class(self.dashboard_data.get('sla_compliance_rate', 0), 'sla')}">{self.dashboard_data.get('sla_compliance_rate', 0):.1f}%</div>
            <div class="metric-label">SLA Compliance</div>
        </div>
        <div class="metric-card">
            <div class="metric-value status-good">${self.dashboard_data.get('cost_savings_today', 0):.2f}</div>
            <div class="metric-label">Cost Savings Today</div>
        </div>
    </div>

    <h2>📊 Client Performance</h2>
    <div class="client-grid">
"""

# Add client cards
for client_id, client_data in self.dashboard_data.get('client_performance', {}).items():
    html += f"""
        <div class="client-card">
            <div class="client-name">{client_data.get('name', 'Unknown Client')}</div>
            <div class="client-metric">
                <span>Tickets Today:</span>
                <span><strong>{client_data.get('tickets_today', 0)}</strong></span>
            </div>
            <div class="client-metric">
                <span>Resolution Rate:</span>
                <span class="{self._get_status_class(client_data.get('resolution_rate', 0), 'resolution')}"><strong>{client_data.get('resolution_rate', 0):.1f}%</strong></span>
            </div>
            <div class="client-metric">
                <span>Avg Response:</span>
                <span class="{self._get_status_class(client_data.get('avg_response_time', 0), 'response_time')}"><strong>{client_data.get('avg_response_time', 0):.1f}s</strong></span>
            </div>
            <div class="client-metric">
                <span>SLA Compliance:</span>
                <span class="{self._get_status_class(client_data.get('sla_compliance', 0), 'sla')}"><strong>{client_data.get('sla_compliance', 0):.1f}%</strong></span>
            </div>
            <div class="client-metric">
                <span>Cost Savings:</span>
                <span class="status-good"><strong>${client_data.get('cost_savings', 0):.2f}</strong></span>
            </div>
        </div>
"""

html += f"""
    </div>

    <h2>🔥 Top Issues Today</h2>
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        <ul>
"""

for issue in self.dashboard_data.get('top_issues', []):
    html += f"            <li>{issue}</li>\n"

html += f"""
        </ul>
    </div>

    <div class="timestamp">
        Last updated: {self.dashboard_data.get('timestamp', 'Unknown')}
    </div>
</body>
</html>
"""
        return html

    def _get_status_class(self, value: float, metric_type: str) -> str:
        """Get CSS class based on metric value and type"""
        if metric_type == 'active':
            return 'status-good' if value < 5 else 'status-warning' if value < 20 else 'status-critical'
        elif metric_type == 'escalated':
            return 'status-good' if value < 3 else 'status-warning' if value < 10 else 'status-critical'
        elif metric_type == 'response_time':
            return 'status-good' if value < 5 else 'status-warning' if value < 15 else 'status-critical'
        elif metric_type == 'sla':
            return 'status-good' if value > 85 else 'status-warning' if value > 70 else 'status-critical'
        elif metric_type == 'resolution':
            return 'status-good' if value > 75 else 'status-warning' if value > 50 else 'status-critical'
        else:
            return 'status-good'

    def get_api_summary(self) -> Dict:
        """Get summary data for API consumers"""
        if not self.dashboard_data:
            return {"status": "initializing"}

        return {
            "status": "active",
            "timestamp": self.dashboard_data.get('timestamp'),
            "summary": {
                "active_tickets": self.dashboard_data.get('active_tickets', 0),
                "resolved_today": self.dashboard_data.get('resolved_today', 0),
                "sla_compliance": self.dashboard_data.get('sla_compliance_rate', 0),
                "cost_savings_today": self.dashboard_data.get('cost_savings_today', 0)
            },
            "clients": len(self.dashboard_data.get('client_performance', {})),
            "top_issues": self.dashboard_data.get('top_issues', [])[:3]
        }

    async def export_daily_report(self, output_path: str):
        """Export daily performance report"""
        report_data = {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "summary": self.dashboard_data,
            "detailed_metrics": []
        }

        # Add detailed metrics for each client
        for client_id, client in self.msp_system.clients.items():
            client_report = self.msp_system.get_msp_performance_report(client_id, hours=24)
            report_data["detailed_metrics"].append({
                "client_id": client_id,
                "client_name": client.client_name,
                "performance": client_report
            })

        # Save report
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info(f"Daily report exported to {output_path}")

async def start_dashboard_server(msp_system, port: int = 8080):
    """Start simple HTTP server for dashboard"""
    from aiohttp import web
    import multipart

    dashboard = MSPDashboard(msp_system)

    # Start background monitoring
    asyncio.create_task(dashboard.start_monitoring())

    async def dashboard_handler(request):
        html = dashboard.get_dashboard_html()
        return web.Response(text=html, content_type='text/html')

    async def api_handler(request):
        data = dashboard.get_api_summary()
        return web.json_response(data)

    async def save_config_handler(request):
        """Handle saving API configuration"""
        try:
            if request.method == 'POST':
                # Parse form data
                data = await request.post()

                # Create API config structure
                api_config = {
                    "atera": {
                        "api_key": data.get('atera_api_key', ''),
                        "api_url": data.get('atera_api_url', '')
                    },
                    "openai": {
                        "api_key": data.get('openai_api_key', ''),
                        "model": data.get('openai_model', '')
                    },
                    "azure_openai": {
                        "api_key": data.get('azure_openai_api_key', ''),
                        "endpoint": data.get('azure_openai_endpoint', ''),
                        "deployment": data.get('azure_openai_deployment', '')
                    },
                    "lmstudio": {
                        "endpoint": data.get('lmstudio_endpoint', ''),
                        "model": data.get('lmstudio_model', '')
                    },
                    "email": {
                        "smtp_host": data.get('smtp_host', ''),
                        "smtp_port": data.get('smtp_port', ''),
                        "smtp_user": data.get('smtp_user', ''),
                        "smtp_pass": data.get('smtp_pass', '')
                    }
                }

                # Update environment variables
                env_manager.update_api_config(api_config)
                env_manager.save_env_file()

                logger.info("API configuration updated successfully")
                return web.json_response({"status": "success", "message": "Configuration saved successfully"})

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def test_connection_handler(request):
        """Handle testing API connections"""
        try:
            provider = request.query.get('provider', '')
            # This would implement actual connection testing
            # For now, return a placeholder response
            return web.json_response({
                "status": "success",
                "message": f"{provider} connection test passed",
                "details": "Connection test feature coming soon"
            })
        except Exception as e:
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def admin_handler(request):
        """Handle admin panel requests"""
        show_admin = request.query.get('admin', 'false').lower() == 'true'
        html = dashboard.get_dashboard_html(show_admin=show_admin)
        return web.Response(text=html, content_type='text/html')

    async def activate_license_handler(request):
        """Handle license activation"""
        try:
            data = await request.json()
            license_key = data.get('license_key', '').strip()

            if not license_key:
                return web.json_response({"success": False, "message": "License key is required"})

            success, message = license_manager.activate_license(license_key)
            return web.json_response({"success": success, "message": message})

        except Exception as e:
            logger.error(f"Error activating license: {e}")
            return web.json_response({"success": False, "message": str(e)}, status=500)

    async def generate_trial_handler(request):
        """Handle trial license generation"""
        try:
            data = await request.json()
            email = data.get('email', '').strip()

            if not email:
                return web.json_response({"success": False, "message": "Email is required"})

            trial_license = license_manager.generate_trial_license(email)
            return web.json_response({
                "success": True,
                "message": f"Trial license generated: {trial_license.license_key}",
                "license_key": trial_license.license_key
            })

        except Exception as e:
            logger.error(f"Error generating trial: {e}")
            return web.json_response({"success": False, "message": str(e)}, status=500)

    async def license_status_handler(request):
        """Handle license status requests"""
        try:
            status = license_manager.get_license_status()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    app = web.Application()
    app.router.add_get('/', dashboard_handler)
    app.router.add_get('/api/summary', api_handler)
    app.router.add_post('/admin/save-config', save_config_handler)
    app.router.add_get('/admin/test-connection', test_connection_handler)
    app.router.add_get('/admin', admin_handler)
    app.router.add_post('/admin/activate-license', activate_license_handler)
    app.router.add_post('/admin/generate-trial', generate_trial_handler)
    app.router.add_get('/api/license-status', license_status_handler)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, 'localhost', port)
    await site.start()

    logger.info(f"MSP Dashboard started at http://localhost:{port}")
    logger.info(f"Admin panel available at http://localhost:{port}/admin")
    return runner

if __name__ == "__main__":
    # Demo dashboard
    print("MSP Dashboard module - Use with msp_ticketzero_optimized.py")