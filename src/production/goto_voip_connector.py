#!/usr/bin/env python3
"""
GoTo Admin VoIP Integration for TicketZero AI
VoIP phone system management and administration
"""

import asyncio
import aiohttp
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import base64
from urllib.parse import urljoin, urlencode

logger = logging.getLogger(__name__)

@dataclass
class GoToVoIPConfig:
    """GoTo Admin VoIP configuration"""
    client_id: str
    client_secret: str
    api_key: str
    phone_system_id: str
    environment: str = "production"  # production, sandbox
    base_url: str = "https://api.goto.com/admin/rest/v1"

@dataclass
class VoIPUser:
    """VoIP user data structure"""
    user_id: str
    extension: str
    first_name: str
    last_name: str
    email: str
    phone_number: str
    department: str
    status: str  # active, inactive, busy, dnd
    device_type: str  # desk_phone, softphone, mobile
    call_forwarding_enabled: bool = False
    voicemail_enabled: bool = True

@dataclass
class VoIPTicket:
    """VoIP-specific ticket structure"""
    ticket_id: str
    title: str
    description: str
    category: str  # phone_issues, voicemail, call_quality, system_outage, user_setup
    priority: str
    user_extension: str
    user_name: str
    user_email: str
    department: str
    created_at: datetime
    phone_system_affected: bool = False
    call_logs_needed: bool = False

class GoToVoIPConnector:
    """GoTo Admin VoIP API integration"""

    def __init__(self, config: GoToVoIPConfig):
        self.config = config
        self.session = None
        self.access_token = None
        self.token_expires_at = None

    async def initialize(self):
        """Initialize GoTo VoIP connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            await self.authenticate()
            logger.info("GoTo VoIP API connected successfully")
            return True

        except Exception as e:
            logger.error(f"GoTo VoIP initialization failed: {e}")
            return False

    async def authenticate(self):
        """Authenticate with GoTo Admin using OAuth 2.0"""
        try:
            # Prepare OAuth credentials
            credentials = base64.b64encode(
                f"{self.config.client_id}:{self.config.client_secret}".encode()
            ).decode()

            auth_headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            auth_data = {
                'grant_type': 'client_credentials',
                'scope': 'admin'
            }

            auth_url = "https://api.goto.com/oauth/v2/token"

            async with self.session.post(
                auth_url,
                headers=auth_headers,
                data=urlencode(auth_data)
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                    # Update session headers
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })

                    logger.info("GoTo VoIP authentication successful")
                else:
                    raise Exception(f"Authentication failed: {response.status}")

        except Exception as e:
            logger.error(f"GoTo VoIP authentication error: {e}")
            raise

    async def _ensure_valid_token(self):
        """Ensure access token is valid and refresh if needed"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            await self.authenticate()

    async def get_voip_user(self, extension: str = None, email: str = None) -> Optional[VoIPUser]:
        """Get VoIP user information by extension or email"""
        try:
            await self._ensure_valid_token()

            if extension:
                url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/extension/{extension}")
            elif email:
                url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/email/{email}")
            else:
                return None

            async with self.session.get(url) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return VoIPUser(
                        user_id=user_data['userId'],
                        extension=user_data['extension'],
                        first_name=user_data['firstName'],
                        last_name=user_data['lastName'],
                        email=user_data['email'],
                        phone_number=user_data.get('phoneNumber', ''),
                        department=user_data.get('department', ''),
                        status=user_data.get('status', 'active'),
                        device_type=user_data.get('deviceType', 'desk_phone'),
                        call_forwarding_enabled=user_data.get('callForwardingEnabled', False),
                        voicemail_enabled=user_data.get('voicemailEnabled', True)
                    )
                else:
                    logger.warning(f"VoIP user not found: {extension or email}")
                    return None

        except Exception as e:
            logger.error(f"Error retrieving VoIP user: {e}")
            return None

    async def reset_voip_password(self, user_id: str) -> bool:
        """Reset VoIP user password"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/{user_id}/reset-password")

            async with self.session.post(url) as response:
                if response.status == 200:
                    logger.info(f"VoIP password reset for user: {user_id}")
                    return True
                else:
                    logger.error(f"Failed to reset VoIP password: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error resetting VoIP password: {e}")
            return False

    async def update_call_forwarding(self, user_id: str, enabled: bool, forward_to: str = "") -> bool:
        """Update call forwarding settings"""
        try:
            await self._ensure_valid_token()

            forwarding_data = {
                'enabled': enabled,
                'forwardTo': forward_to if enabled else ""
            }

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/{user_id}/call-forwarding")

            async with self.session.put(url, json=forwarding_data) as response:
                if response.status == 200:
                    action = "enabled" if enabled else "disabled"
                    logger.info(f"Call forwarding {action} for user: {user_id}")
                    return True
                else:
                    logger.error(f"Failed to update call forwarding: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error updating call forwarding: {e}")
            return False

    async def get_call_logs(self, extension: str, hours: int = 24) -> List[Dict]:
        """Get call logs for specific extension"""
        try:
            await self._ensure_valid_token()

            start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            end_time = datetime.now().isoformat()

            params = {
                'extension': extension,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 100
            }

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/call-logs")

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    call_data = await response.json()
                    return [
                        {
                            'call_id': call['callId'],
                            'direction': call['direction'],  # inbound, outbound
                            'caller_number': call['callerNumber'],
                            'called_number': call['calledNumber'],
                            'start_time': call['startTime'],
                            'duration': call['duration'],
                            'status': call['status'],  # answered, missed, busy
                            'recording_available': call.get('recordingAvailable', False)
                        }
                        for call in call_data.get('calls', [])
                    ]
                else:
                    return []

        except Exception as e:
            logger.error(f"Error retrieving call logs: {e}")
            return []

    async def restart_voip_device(self, user_id: str) -> bool:
        """Restart VoIP device for user"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/{user_id}/device/restart")

            async with self.session.post(url) as response:
                if response.status == 200:
                    logger.info(f"VoIP device restart initiated for user: {user_id}")
                    return True
                else:
                    logger.error(f"Failed to restart VoIP device: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error restarting VoIP device: {e}")
            return False

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall VoIP system status"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/status")

            async with self.session.get(url) as response:
                if response.status == 200:
                    status_data = await response.json()
                    return {
                        'system_status': status_data.get('status', 'unknown'),
                        'active_calls': status_data.get('activeCalls', 0),
                        'registered_devices': status_data.get('registeredDevices', 0),
                        'system_uptime': status_data.get('uptime', ''),
                        'last_maintenance': status_data.get('lastMaintenance', ''),
                        'service_alerts': status_data.get('alerts', [])
                    }
                else:
                    return {'system_status': 'unavailable'}

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'system_status': 'error', 'error': str(e)}

    async def create_voip_user(self, user_data: Dict) -> Optional[str]:
        """Create new VoIP user"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users")

            async with self.session.post(url, json=user_data) as response:
                if response.status in [200, 201]:
                    user_response = await response.json()
                    user_id = user_response.get('userId')
                    logger.info(f"VoIP user created: {user_id}")
                    return user_id
                else:
                    logger.error(f"Failed to create VoIP user: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error creating VoIP user: {e}")
            return None

    async def update_voicemail_greeting(self, user_id: str, greeting_text: str) -> bool:
        """Update voicemail greeting for user"""
        try:
            await self._ensure_valid_token()

            greeting_data = {
                'greetingText': greeting_text,
                'useDefault': False
            }

            url = urljoin(self.config.base_url, f"/phone-systems/{self.config.phone_system_id}/users/{user_id}/voicemail/greeting")

            async with self.session.put(url, json=greeting_data) as response:
                if response.status == 200:
                    logger.info(f"Voicemail greeting updated for user: {user_id}")
                    return True
                else:
                    logger.error(f"Failed to update voicemail greeting: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error updating voicemail greeting: {e}")
            return False

    async def close(self):
        """Close GoTo VoIP connection"""
        if self.session:
            await self.session.close()

class VoIPWorkflowEngine:
    """Workflow engine for VoIP-specific support"""

    def __init__(self, goto_voip: GoToVoIPConnector):
        self.goto_voip = goto_voip
        self.voip_workflows = self._load_voip_workflows()

    def _load_voip_workflows(self) -> Dict[str, Dict]:
        """Load VoIP-specific workflow templates"""
        return {
            'phone_not_working': {
                'category': 'device_issue',
                'priority': 'high',
                'auto_actions': [
                    'check_user_status',
                    'restart_device',
                    'verify_registration',
                    'check_call_logs'
                ],
                'escalation_threshold': 2
            },
            'voicemail_issues': {
                'category': 'voicemail',
                'priority': 'normal',
                'auto_actions': [
                    'check_voicemail_settings',
                    'reset_voicemail_password',
                    'update_greeting'
                ],
                'escalation_threshold': 1
            },
            'call_quality_problems': {
                'category': 'network_issue',
                'priority': 'high',
                'auto_actions': [
                    'check_system_status',
                    'analyze_call_logs',
                    'check_network_connectivity',
                    'escalate_to_network_team'
                ],
                'escalation_threshold': 1
            },
            'call_forwarding_setup': {
                'category': 'configuration',
                'priority': 'normal',
                'auto_actions': [
                    'get_user_preferences',
                    'configure_forwarding',
                    'test_forwarding',
                    'send_confirmation'
                ],
                'escalation_threshold': 2
            },
            'new_user_setup': {
                'category': 'provisioning',
                'priority': 'normal',
                'auto_actions': [
                    'create_user_account',
                    'assign_extension',
                    'configure_device',
                    'send_credentials'
                ],
                'escalation_threshold': 1
            }
        }

    async def process_voip_ticket(self, ticket: VoIPTicket) -> Dict[str, Any]:
        """Process VoIP ticket with automated actions"""
        try:
            # Determine workflow based on ticket analysis
            workflow = self._determine_voip_workflow(ticket)

            # Execute workflow actions
            results = await self._execute_voip_workflow(ticket, workflow)

            return {
                'success': True,
                'ticket_id': ticket.ticket_id,
                'workflow_type': workflow['category'],
                'actions_completed': results.get('completed_actions', []),
                'voip_changes_made': results.get('voip_changes', []),
                'escalation_needed': results.get('escalation_needed', False),
                'resolution_status': results.get('status', 'in_progress')
            }

        except Exception as e:
            logger.error(f"VoIP ticket processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket.ticket_id
            }

    def _determine_voip_workflow(self, ticket: VoIPTicket) -> Dict:
        """Determine appropriate VoIP workflow"""
        description_lower = ticket.description.lower()
        title_lower = ticket.title.lower()
        combined_text = description_lower + " " + title_lower

        # Check for specific VoIP issues
        if any(word in combined_text for word in ['phone not working', 'no dial tone', 'cant make calls', 'phone dead']):
            workflow_type = 'phone_not_working'
        elif any(word in combined_text for word in ['voicemail', 'voice mail', 'greeting', 'mailbox']):
            workflow_type = 'voicemail_issues'
        elif any(word in combined_text for word in ['call quality', 'static', 'echo', 'dropping calls']):
            workflow_type = 'call_quality_problems'
        elif any(word in combined_text for word in ['call forwarding', 'forward calls', 'redirect calls']):
            workflow_type = 'call_forwarding_setup'
        elif any(word in combined_text for word in ['new user', 'new employee', 'setup phone', 'provision']):
            workflow_type = 'new_user_setup'
        else:
            # Default to device issue
            workflow_type = 'phone_not_working'

        workflow_config = self.voip_workflows[workflow_type].copy()
        workflow_config['type'] = workflow_type
        return workflow_config

    async def _execute_voip_workflow(self, ticket: VoIPTicket, workflow: Dict) -> Dict:
        """Execute VoIP workflow actions"""
        completed_actions = []
        voip_changes = []

        try:
            # Get user information first
            user = await self.goto_voip.get_voip_user(extension=ticket.user_extension)
            if not user:
                return {
                    'status': 'failed',
                    'error': 'User not found in VoIP system'
                }

            workflow_type = workflow.get('type', '')

            if workflow_type == 'phone_not_working':
                # Restart device
                restart_success = await self.goto_voip.restart_voip_device(user.user_id)
                if restart_success:
                    completed_actions.append('device_restarted')
                    voip_changes.append('device_restart')

                # Check call logs for patterns
                call_logs = await self.goto_voip.get_call_logs(ticket.user_extension, hours=24)
                if call_logs:
                    completed_actions.append('call_logs_analyzed')

            elif workflow_type == 'voicemail_issues':
                # Reset voicemail password
                reset_success = await self.goto_voip.reset_voip_password(user.user_id)
                if reset_success:
                    completed_actions.append('voicemail_password_reset')
                    voip_changes.append('password_reset')

            elif workflow_type == 'call_forwarding_setup':
                # Configure call forwarding (would need target number from ticket)
                # This is a placeholder - real implementation would parse target from ticket
                forwarding_success = await self.goto_voip.update_call_forwarding(
                    user.user_id, True, "5551234567"  # Example number
                )
                if forwarding_success:
                    completed_actions.append('call_forwarding_configured')
                    voip_changes.append('call_forwarding_enabled')

            # Check system status for all workflows
            system_status = await self.goto_voip.get_system_status()
            if system_status.get('system_status') == 'healthy':
                completed_actions.append('system_status_verified')

            return {
                'status': 'completed' if completed_actions else 'failed',
                'completed_actions': completed_actions,
                'voip_changes': voip_changes,
                'escalation_needed': len(completed_actions) == 0,
                'user_info': {
                    'extension': user.extension,
                    'status': user.status,
                    'device_type': user.device_type
                }
            }

        except Exception as e:
            logger.error(f"Error executing VoIP workflow: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'escalation_needed': True
            }

# Example usage and testing
async def demo_voip_integration():
    """Demo GoTo VoIP integration"""

    # Sample configuration (would need real credentials)
    voip_config = GoToVoIPConfig(
        client_id=os.environ.get('GOTO_CLIENT_ID', 'YOUR_GOTO_CLIENT_ID_HERE'),
        client_secret=os.environ.get('GOTO_CLIENT_SECRET', 'YOUR_GOTO_CLIENT_SECRET_HERE'),
        api_key=os.environ.get('GOTO_API_KEY', 'YOUR_GOTO_API_KEY_HERE'),
        phone_system_id=os.environ.get('GOTO_PHONE_SYSTEM_ID', 'YOUR_PHONE_SYSTEM_ID_HERE'),
        environment="sandbox"
    )

    # Initialize GoTo VoIP connector
    voip_connector = GoToVoIPConnector(voip_config)

    try:
        # Initialize connection (would fail with demo credentials)
        print("Initializing GoTo VoIP connection...")
        # await voip_connector.initialize()

        # Sample VoIP ticket
        voip_ticket = VoIPTicket(
            ticket_id="VOIP-2024-001",
            title="Phone not working - no dial tone",
            description="User reports their desk phone has no dial tone and cannot make or receive calls since this morning",
            category="device_issue",
            priority="high",
            user_extension="1234",
            user_name="John Smith",
            user_email="john.smith@company.com",
            department="sales",
            created_at=datetime.now(),
            phone_system_affected=False,
            call_logs_needed=True
        )

        # Process ticket with workflow engine
        workflow_engine = VoIPWorkflowEngine(voip_connector)
        result = await workflow_engine.process_voip_ticket(voip_ticket)

        print(f"VoIP ticket processing result: {result}")

    except Exception as e:
        print(f"Demo error (expected with demo credentials): {e}")

    finally:
        await voip_connector.close()

if __name__ == "__main__":
    asyncio.run(demo_voip_integration())