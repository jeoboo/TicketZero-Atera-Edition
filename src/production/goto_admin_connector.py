#!/usr/bin/env python3
"""
GoTo Admin API Integration for TicketZero AI
VoIP system management and phone system administration
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
class GoToAdminConfig:
    """GoTo Admin configuration for VoIP management"""
    client_id: str
    client_secret: str
    api_key: str
    environment: str = "production"  # production, sandbox
    base_url: str = "https://api.goto.com/admin/rest/v1"
    phone_system_id: str = ""

@dataclass
class RemoteSession:
    """Remote support session data"""
    session_id: str
    session_key: str
    attendee_url: str
    organizer_url: str
    session_status: str
    created_at: datetime
    duration_minutes: int = 0
    attendee_name: str = ""
    attendee_email: str = ""

@dataclass
class GoToTicket:
    """GoTo-enhanced ticket structure"""
    ticket_id: str
    title: str
    description: str
    category: str  # remote_support, software_install, training, troubleshooting
    priority: str
    user_name: str
    user_email: str
    department: str
    created_at: datetime
    requires_remote_session: bool = False
    session_data: Optional[RemoteSession] = None

class GoToAdminConnector:
    """GoTo Admin API integration for remote support"""

    def __init__(self, config: GoToAdminConfig):
        self.config = config
        self.session = None
        self.access_token = None
        self.token_expires_at = None

    async def initialize(self):
        """Initialize GoTo Admin connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            await self.authenticate()
            logger.info("GoTo Admin API connected successfully")
            return True

        except Exception as e:
            logger.error(f"GoTo Admin initialization failed: {e}")
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

            auth_url = "https://api.getgo.com/oauth/v2/token"

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

                    logger.info("GoTo Admin authentication successful")
                else:
                    raise Exception(f"Authentication failed: {response.status}")

        except Exception as e:
            logger.error(f"GoTo authentication error: {e}")
            raise

    async def _ensure_valid_token(self):
        """Ensure access token is valid and refresh if needed"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            await self.authenticate()

    async def create_remote_support_session(self, ticket: GoToTicket) -> Optional[RemoteSession]:
        """Create a new remote support session"""
        try:
            await self._ensure_valid_token()

            session_data = {
                "sessionName": f"Support for {ticket.user_name} - {ticket.title}",
                "attendeeEmailInvitations": [ticket.user_email],
                "sessionType": "support",
                "startTime": datetime.now().isoformat(),
                "maxAttendees": 2,
                "sendInvitationEmails": True,
                "sessionDescription": f"Remote support session for ticket: {ticket.ticket_id}\n{ticket.description}",
                "organizerKey": self.config.api_key
            }

            url = urljoin(self.config.base_url, "/sessions")

            async with self.session.post(url, json=session_data) as response:
                if response.status in [200, 201]:
                    session_response = await response.json()

                    remote_session = RemoteSession(
                        session_id=session_response['sessionId'],
                        session_key=session_response['sessionKey'],
                        attendee_url=session_response['attendeeUrl'],
                        organizer_url=session_response['organizerUrl'],
                        session_status="scheduled",
                        created_at=datetime.now(),
                        attendee_name=ticket.user_name,
                        attendee_email=ticket.user_email
                    )

                    logger.info(f"Remote support session created: {remote_session.session_id}")
                    return remote_session

                else:
                    logger.error(f"Failed to create remote session: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return None

        except Exception as e:
            logger.error(f"Error creating remote support session: {e}")
            return None

    async def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current status of remote support session"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/sessions/{session_id}")

            async with self.session.get(url) as response:
                if response.status == 200:
                    session_data = await response.json()
                    return {
                        'session_id': session_data['sessionId'],
                        'status': session_data['status'],
                        'start_time': session_data.get('startTime'),
                        'end_time': session_data.get('endTime'),
                        'duration': session_data.get('duration', 0),
                        'attendee_count': session_data.get('attendeeCount', 0),
                        'recording_available': session_data.get('recordingAvailable', False)
                    }
                else:
                    return None

        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return None

    async def end_remote_session(self, session_id: str) -> bool:
        """End a remote support session"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/sessions/{session_id}/end")

            async with self.session.put(url) as response:
                if response.status == 200:
                    logger.info(f"Remote session ended: {session_id}")
                    return True
                else:
                    logger.error(f"Failed to end session: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error ending remote session: {e}")
            return False

    async def get_session_recording(self, session_id: str) -> Optional[Dict]:
        """Get recording information for completed session"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, f"/sessions/{session_id}/recordings")

            async with self.session.get(url) as response:
                if response.status == 200:
                    recording_data = await response.json()
                    if recording_data:
                        return {
                            'recording_id': recording_data.get('recordingId'),
                            'download_url': recording_data.get('downloadUrl'),
                            'duration': recording_data.get('duration'),
                            'file_size': recording_data.get('fileSize'),
                            'created_at': recording_data.get('createdTime')
                        }
                else:
                    return None

        except Exception as e:
            logger.error(f"Error getting session recording: {e}")
            return None

    async def create_unattended_access(self, computer_name: str, description: str) -> Optional[Dict]:
        """Create unattended access for remote computer management"""
        try:
            await self._ensure_valid_token()

            access_data = {
                "computerName": computer_name,
                "description": description,
                "accessType": "unattended",
                "permanentAccess": False,
                "accessDuration": 24  # hours
            }

            url = urljoin(self.config.base_url, "/computers/unattended")

            async with self.session.post(url, json=access_data) as response:
                if response.status in [200, 201]:
                    access_response = await response.json()
                    return {
                        'computer_id': access_response['computerId'],
                        'access_code': access_response['accessCode'],
                        'download_url': access_response['downloadUrl'],
                        'expires_at': access_response['expiresAt']
                    }
                else:
                    logger.error(f"Failed to create unattended access: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error creating unattended access: {e}")
            return None

    async def get_computer_list(self) -> List[Dict]:
        """Get list of computers with unattended access"""
        try:
            await self._ensure_valid_token()

            url = urljoin(self.config.base_url, "/computers")

            async with self.session.get(url) as response:
                if response.status == 200:
                    computers = await response.json()
                    return [
                        {
                            'computer_id': comp['computerId'],
                            'computer_name': comp['computerName'],
                            'status': comp['status'],
                            'last_seen': comp.get('lastSeen'),
                            'operating_system': comp.get('operatingSystem'),
                            'ip_address': comp.get('ipAddress')
                        }
                        for comp in computers
                    ]
                else:
                    return []

        except Exception as e:
            logger.error(f"Error getting computer list: {e}")
            return []

    async def send_session_invitation(self, session_id: str, attendee_email: str, custom_message: str = "") -> bool:
        """Send invitation to join remote support session"""
        try:
            await self._ensure_valid_token()

            invitation_data = {
                "attendeeEmail": attendee_email,
                "customMessage": custom_message or f"Please join the remote support session: {session_id}",
                "sendEmail": True
            }

            url = urljoin(self.config.base_url, f"/sessions/{session_id}/invitations")

            async with self.session.post(url, json=invitation_data) as response:
                if response.status in [200, 201]:
                    logger.info(f"Session invitation sent to {attendee_email}")
                    return True
                else:
                    logger.error(f"Failed to send invitation: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error sending session invitation: {e}")
            return False

    async def close(self):
        """Close GoTo Admin connection"""
        if self.session:
            await self.session.close()

class RemoteSupportWorkflow:
    """Workflow engine for remote support integration"""

    def __init__(self, goto_connector: GoToAdminConnector):
        self.goto = goto_connector
        self.support_workflows = self._load_support_workflows()

    def _load_support_workflows(self) -> Dict[str, Dict]:
        """Load remote support workflow templates"""
        return {
            'software_installation': {
                'requires_remote': True,
                'estimated_duration': 30,
                'auto_actions': [
                    'create_remote_session',
                    'send_invitation',
                    'prepare_installation_files',
                    'guide_installation_process'
                ],
                'follow_up_required': True
            },
            'troubleshooting': {
                'requires_remote': True,
                'estimated_duration': 45,
                'auto_actions': [
                    'create_remote_session',
                    'send_invitation',
                    'diagnose_issue',
                    'apply_fixes',
                    'verify_resolution'
                ],
                'follow_up_required': False
            },
            'training_session': {
                'requires_remote': True,
                'estimated_duration': 60,
                'auto_actions': [
                    'create_remote_session',
                    'send_invitation',
                    'screen_sharing_setup',
                    'conduct_training',
                    'provide_documentation'
                ],
                'follow_up_required': True
            },
            'quick_fix': {
                'requires_remote': False,
                'estimated_duration': 15,
                'auto_actions': [
                    'provide_instructions',
                    'monitor_progress',
                    'offer_remote_if_needed'
                ],
                'follow_up_required': False
            }
        }

    async def process_support_ticket(self, ticket: GoToTicket) -> Dict[str, Any]:
        """Process support ticket with GoTo integration"""
        try:
            # Determine workflow based on ticket analysis
            workflow = self._determine_support_workflow(ticket)

            # Execute workflow actions
            results = await self._execute_support_workflow(ticket, workflow)

            return {
                'success': True,
                'ticket_id': ticket.ticket_id,
                'workflow_type': workflow['type'],
                'remote_session_created': results.get('remote_session_created', False),
                'session_details': results.get('session_details'),
                'estimated_resolution_time': workflow['estimated_duration'],
                'follow_up_required': workflow['follow_up_required']
            }

        except Exception as e:
            logger.error(f"Support ticket processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket.ticket_id
            }

    def _determine_support_workflow(self, ticket: GoToTicket) -> Dict:
        """Determine appropriate support workflow"""
        description_lower = ticket.description.lower()
        title_lower = ticket.title.lower()

        # Check for software installation keywords
        if any(word in description_lower + title_lower for word in [
            'install', 'installation', 'setup', 'configure', 'software'
        ]):
            workflow_type = 'software_installation'

        # Check for training keywords
        elif any(word in description_lower + title_lower for word in [
            'training', 'learn', 'how to', 'tutorial', 'show me'
        ]):
            workflow_type = 'training_session'

        # Check for complex troubleshooting
        elif any(word in description_lower + title_lower for word in [
            'not working', 'error', 'problem', 'issue', 'troubleshoot'
        ]) and ticket.priority in ['high', 'urgent']:
            workflow_type = 'troubleshooting'

        # Default to quick fix for simple issues
        else:
            workflow_type = 'quick_fix'

        workflow_config = self.support_workflows[workflow_type].copy()
        workflow_config['type'] = workflow_type
        return workflow_config

    async def _execute_support_workflow(self, ticket: GoToTicket, workflow: Dict) -> Dict:
        """Execute support workflow actions"""
        results = {}

        try:
            if workflow['requires_remote']:
                # Create remote support session
                session = await self.goto.create_remote_support_session(ticket)
                if session:
                    results['remote_session_created'] = True
                    results['session_details'] = {
                        'session_id': session.session_id,
                        'attendee_url': session.attendee_url,
                        'organizer_url': session.organizer_url
                    }

                    # Send invitation with custom message
                    custom_message = self._generate_invitation_message(ticket, workflow)
                    await self.goto.send_session_invitation(
                        session.session_id,
                        ticket.user_email,
                        custom_message
                    )

                    results['invitation_sent'] = True
                    ticket.session_data = session
                else:
                    results['remote_session_created'] = False
                    results['fallback_action'] = 'manual_support_required'

            else:
                # Handle non-remote workflows
                results['remote_session_created'] = False
                results['action_type'] = 'instructions_provided'

            return results

        except Exception as e:
            logger.error(f"Error executing support workflow: {e}")
            return {'error': str(e)}

    def _generate_invitation_message(self, ticket: GoToTicket, workflow: Dict) -> str:
        """Generate custom invitation message for remote session"""
        workflow_type = workflow.get('type', 'support')
        duration = workflow.get('estimated_duration', 30)

        messages = {
            'software_installation': f"""
Hello {ticket.user_name},

I'm ready to help you with the software installation for: {ticket.title}

Please join our remote support session where I'll guide you through the installation process step by step. This session is estimated to take approximately {duration} minutes.

Click the link below to join:
""",
            'troubleshooting': f"""
Hello {ticket.user_name},

I'm here to help resolve the issue you're experiencing: {ticket.title}

Please join our remote support session so I can diagnose and fix the problem directly. This should take approximately {duration} minutes.

Click the link below to join:
""",
            'training_session': f"""
Hello {ticket.user_name},

I'm ready to provide the training session you requested for: {ticket.title}

Please join our remote session where I'll walk you through the features and answer any questions. This training session is scheduled for approximately {duration} minutes.

Click the link below to join:
"""
        }

        return messages.get(workflow_type, f"""
Hello {ticket.user_name},

I'm here to help you with: {ticket.title}

Please join our remote support session so we can resolve this together. This should take approximately {duration} minutes.

Click the link below to join:
""")

# Example usage and testing
async def demo_goto_integration():
    """Demo GoTo Admin integration"""

    # Sample configuration (would need real credentials)
    goto_config = GoToAdminConfig(
        client_id=os.environ.get('GOTO_CLIENT_ID', 'YOUR_GOTO_CLIENT_ID_HERE'),
        client_secret=os.environ.get('GOTO_CLIENT_SECRET', 'YOUR_GOTO_CLIENT_SECRET_HERE'),
        api_key=os.environ.get('GOTO_API_KEY', 'YOUR_GOTO_API_KEY_HERE'),
        environment="sandbox"
    )

    # Initialize GoTo connector
    goto_connector = GoToAdminConnector(goto_config)

    try:
        # Initialize connection (would fail with demo credentials)
        print("Initializing GoTo Admin connection...")
        # await goto_connector.initialize()

        # Sample support ticket
        support_ticket = GoToTicket(
            ticket_id="SUP-2024-001",
            title="Need help installing Microsoft Office 365",
            description="User needs assistance installing Office 365 on their new laptop. They've never done this before and need step-by-step guidance.",
            category="software_installation",
            priority="normal",
            user_name="Jane Doe",
            user_email="jane.doe@company.com",
            department="marketing",
            created_at=datetime.now(),
            requires_remote_session=True
        )

        # Process ticket with workflow engine
        workflow_engine = RemoteSupportWorkflow(goto_connector)
        result = await workflow_engine.process_support_ticket(support_ticket)

        print(f"Support ticket processing result: {result}")

    except Exception as e:
        print(f"Demo error (expected with demo credentials): {e}")

    finally:
        await goto_connector.close()

if __name__ == "__main__":
    asyncio.run(demo_goto_integration())