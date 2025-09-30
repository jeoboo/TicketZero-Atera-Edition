#!/usr/bin/env python3
"""
Opera PMS Integration for TicketZero AI
Hotel property management system connector
"""

import asyncio
import aiohttp
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class OperaProperty:
    """Opera property configuration"""
    property_id: str
    property_name: str
    opera_server_url: str
    username: str
    password: str
    interface_id: str
    resort_code: str
    environment: str = "production"  # production, test, development

@dataclass
class HotelTicket:
    """Hotel-specific ticket structure"""
    ticket_id: str
    guest_name: str
    room_number: str
    reservation_id: Optional[str]
    folio_number: Optional[str]
    issue_category: str  # technical, housekeeping, maintenance, guest_services
    priority: str  # urgent, high, normal, low
    description: str
    reported_by: str  # guest, staff, system
    department: str  # front_desk, housekeeping, maintenance, it, management
    property_id: str
    created_at: datetime
    guest_language: str = "en"
    guest_vip_status: bool = False

class OperaPMSConnector:
    """Oracle Opera PMS integration connector"""

    def __init__(self, property_config: OperaProperty):
        self.property = property_config
        self.session = None
        self.auth_token = None
        self.base_url = property_config.opera_server_url

        # Opera API endpoints
        self.endpoints = {
            'auth': '/api/v1/authentication/login',
            'reservations': '/api/v1/reservations',
            'guests': '/api/v1/guests',
            'rooms': '/api/v1/rooms',
            'folios': '/api/v1/folios',
            'housekeeping': '/api/v1/housekeeping/rooms',
            'maintenance': '/api/v1/maintenance/workorders',
            'guest_requests': '/api/v1/guests/requests'
        }

    async def initialize(self):
        """Initialize Opera PMS connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )

            await self.authenticate()
            logger.info(f"Opera PMS connected for property: {self.property.property_name}")
            return True

        except Exception as e:
            logger.error(f"Opera PMS initialization failed: {e}")
            return False

    async def authenticate(self):
        """Authenticate with Opera PMS"""
        auth_payload = {
            "username": self.property.username,
            "password": self.property.password,
            "resortCode": self.property.resort_code,
            "interfaceId": self.property.interface_id
        }

        try:
            url = urljoin(self.base_url, self.endpoints['auth'])
            async with self.session.post(url, json=auth_payload) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.auth_token = auth_data.get('token')

                    # Update session headers with auth token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })

                    logger.info("Opera PMS authentication successful")
                else:
                    raise Exception(f"Authentication failed: {response.status}")

        except Exception as e:
            logger.error(f"Opera authentication error: {e}")
            raise

    async def get_guest_information(self, room_number: str = None, reservation_id: str = None) -> Optional[Dict]:
        """Retrieve guest information from Opera PMS"""
        try:
            if room_number:
                # Get current guest in room
                url = urljoin(self.base_url, f"{self.endpoints['rooms']}/{room_number}/guest")
            elif reservation_id:
                # Get guest by reservation
                url = urljoin(self.base_url, f"{self.endpoints['reservations']}/{reservation_id}/guest")
            else:
                return None

            async with self.session.get(url) as response:
                if response.status == 200:
                    guest_data = await response.json()
                    return {
                        'guest_name': f"{guest_data.get('firstName', '')} {guest_data.get('lastName', '')}".strip(),
                        'room_number': guest_data.get('roomNumber'),
                        'reservation_id': guest_data.get('reservationId'),
                        'folio_number': guest_data.get('folioNumber'),
                        'vip_status': guest_data.get('vipStatus', False),
                        'language': guest_data.get('language', 'en'),
                        'arrival_date': guest_data.get('arrivalDate'),
                        'departure_date': guest_data.get('departureDate'),
                        'guest_type': guest_data.get('guestType'),
                        'membership_level': guest_data.get('membershipLevel')
                    }
                else:
                    logger.warning(f"Guest not found for room {room_number}")
                    return None

        except Exception as e:
            logger.error(f"Error retrieving guest information: {e}")
            return None

    async def get_room_status(self, room_number: str) -> Optional[Dict]:
        """Get room status from Opera PMS"""
        try:
            url = urljoin(self.base_url, f"{self.endpoints['rooms']}/{room_number}/status")

            async with self.session.get(url) as response:
                if response.status == 200:
                    room_data = await response.json()
                    return {
                        'room_number': room_data.get('roomNumber'),
                        'room_type': room_data.get('roomType'),
                        'room_status': room_data.get('roomStatus'),  # occupied, vacant_dirty, vacant_clean, out_of_order
                        'housekeeping_status': room_data.get('housekeepingStatus'),
                        'maintenance_status': room_data.get('maintenanceStatus'),
                        'guest_count': room_data.get('guestCount', 0),
                        'last_checkout': room_data.get('lastCheckout'),
                        'next_arrival': room_data.get('nextArrival')
                    }
                else:
                    return None

        except Exception as e:
            logger.error(f"Error retrieving room status: {e}")
            return None

    async def create_maintenance_request(self, ticket: HotelTicket) -> bool:
        """Create maintenance work order in Opera PMS"""
        try:
            maintenance_data = {
                'roomNumber': ticket.room_number,
                'requestType': self._map_issue_to_maintenance_type(ticket.issue_category),
                'priority': self._map_priority_to_opera(ticket.priority),
                'description': ticket.description,
                'reportedBy': ticket.reported_by,
                'department': ticket.department,
                'requestDate': ticket.created_at.isoformat(),
                'guestName': ticket.guest_name,
                'reservationId': ticket.reservation_id
            }

            url = urljoin(self.base_url, self.endpoints['maintenance'])

            async with self.session.post(url, json=maintenance_data) as response:
                if response.status in [200, 201]:
                    work_order = await response.json()
                    logger.info(f"Maintenance work order created: {work_order.get('workOrderId')}")
                    return True
                else:
                    logger.error(f"Failed to create maintenance request: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error creating maintenance request: {e}")
            return False

    async def update_housekeeping_status(self, room_number: str, status: str, notes: str = "") -> bool:
        """Update housekeeping status in Opera PMS"""
        try:
            hk_data = {
                'roomNumber': room_number,
                'housekeepingStatus': status,  # clean, dirty, inspected, out_of_order
                'notes': notes,
                'updateTime': datetime.now().isoformat()
            }

            url = urljoin(self.base_url, f"{self.endpoints['housekeeping']}/{room_number}")

            async with self.session.put(url, json=hk_data) as response:
                if response.status == 200:
                    logger.info(f"Housekeeping status updated for room {room_number}: {status}")
                    return True
                else:
                    logger.error(f"Failed to update housekeeping status: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error updating housekeeping status: {e}")
            return False

    async def post_charges_to_folio(self, folio_number: str, charge_data: Dict) -> bool:
        """Post charges to guest folio"""
        try:
            url = urljoin(self.base_url, f"{self.endpoints['folios']}/{folio_number}/charges")

            async with self.session.post(url, json=charge_data) as response:
                if response.status in [200, 201]:
                    logger.info(f"Charge posted to folio {folio_number}")
                    return True
                else:
                    logger.error(f"Failed to post charge: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error posting charge to folio: {e}")
            return False

    def _map_issue_to_maintenance_type(self, issue_category: str) -> str:
        """Map ticket issue to Opera maintenance type"""
        mapping = {
            'technical': 'TECH',
            'maintenance': 'MAINT',
            'hvac': 'HVAC',
            'plumbing': 'PLUMB',
            'electrical': 'ELEC',
            'housekeeping': 'HK',
            'guest_services': 'GUEST'
        }
        return mapping.get(issue_category, 'GENERAL')

    def _map_priority_to_opera(self, priority: str) -> str:
        """Map ticket priority to Opera priority codes"""
        mapping = {
            'urgent': 'HIGH',
            'high': 'HIGH',
            'normal': 'MEDIUM',
            'low': 'LOW'
        }
        return mapping.get(priority, 'MEDIUM')

    async def close(self):
        """Close Opera PMS connection"""
        if self.session:
            await self.session.close()

class HotelWorkflowEngine:
    """Hotel-specific workflow engine for ticket processing"""

    def __init__(self, opera_connector: OperaPMSConnector):
        self.opera = opera_connector
        self.workflow_templates = self._load_hotel_workflows()

    def _load_hotel_workflows(self) -> Dict[str, Dict]:
        """Load hotel-specific workflow templates"""
        return {
            'guest_wifi_issue': {
                'category': 'technical',
                'priority': 'high',
                'department': 'it',
                'auto_actions': [
                    'check_network_status',
                    'reset_access_point',
                    'verify_guest_credentials',
                    'escalate_if_unresolved'
                ],
                'sla_minutes': 15,
                'guest_communication': True
            },
            'room_maintenance': {
                'category': 'maintenance',
                'priority': 'normal',
                'department': 'maintenance',
                'auto_actions': [
                    'create_work_order',
                    'notify_housekeeping',
                    'update_room_status',
                    'schedule_repair'
                ],
                'sla_minutes': 60,
                'guest_communication': True
            },
            'housekeeping_request': {
                'category': 'housekeeping',
                'priority': 'normal',
                'department': 'housekeeping',
                'auto_actions': [
                    'assign_housekeeper',
                    'update_room_status',
                    'notify_front_desk'
                ],
                'sla_minutes': 30,
                'guest_communication': False
            },
            'guest_complaint': {
                'category': 'guest_services',
                'priority': 'high',
                'department': 'front_desk',
                'auto_actions': [
                    'escalate_to_manager',
                    'document_complaint',
                    'offer_compensation',
                    'follow_up_required'
                ],
                'sla_minutes': 10,
                'guest_communication': True
            },
            'checkout_issue': {
                'category': 'guest_services',
                'priority': 'urgent',
                'department': 'front_desk',
                'auto_actions': [
                    'verify_folio_charges',
                    'process_payment',
                    'resolve_disputes',
                    'expedite_checkout'
                ],
                'sla_minutes': 5,
                'guest_communication': True
            }
        }

    async def process_hotel_ticket(self, ticket: HotelTicket) -> Dict[str, Any]:
        """Process hotel ticket with Opera PMS integration"""
        try:
            # Enrich ticket with Opera PMS data
            enriched_ticket = await self._enrich_ticket_with_pms_data(ticket)

            # Determine workflow based on issue category
            workflow = self._determine_workflow(enriched_ticket)

            # Execute automated actions
            results = await self._execute_workflow_actions(enriched_ticket, workflow)

            return {
                'success': True,
                'ticket_id': ticket.ticket_id,
                'workflow_applied': workflow['category'],
                'actions_completed': results['completed_actions'],
                'pms_integration': results['pms_updates'],
                'guest_notified': results['guest_communication'],
                'estimated_resolution_time': workflow['sla_minutes']
            }

        except Exception as e:
            logger.error(f"Hotel ticket processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'ticket_id': ticket.ticket_id
            }

    async def _enrich_ticket_with_pms_data(self, ticket: HotelTicket) -> HotelTicket:
        """Enrich ticket with Opera PMS data"""
        try:
            # Get guest information
            guest_info = await self.opera.get_guest_information(room_number=ticket.room_number)
            if guest_info:
                ticket.guest_name = guest_info['guest_name']
                ticket.reservation_id = guest_info['reservation_id']
                ticket.folio_number = guest_info['folio_number']
                ticket.guest_vip_status = guest_info['vip_status']
                ticket.guest_language = guest_info['language']

            # Get room status
            room_info = await self.opera.get_room_status(ticket.room_number)
            if room_info:
                # Add room context to ticket description
                ticket.description += f" [Room Status: {room_info['room_status']}, Type: {room_info['room_type']}]"

            return ticket

        except Exception as e:
            logger.error(f"Error enriching ticket with PMS data: {e}")
            return ticket

    def _determine_workflow(self, ticket: HotelTicket) -> Dict:
        """Determine appropriate workflow based on ticket characteristics"""
        # Simple keyword-based workflow determination
        description_lower = ticket.description.lower()

        if any(word in description_lower for word in ['wifi', 'internet', 'network', 'connection']):
            return self.workflow_templates['guest_wifi_issue']
        elif any(word in description_lower for word in ['maintenance', 'repair', 'broken', 'not working']):
            return self.workflow_templates['room_maintenance']
        elif any(word in description_lower for word in ['clean', 'towels', 'housekeeping', 'amenities']):
            return self.workflow_templates['housekeeping_request']
        elif any(word in description_lower for word in ['complaint', 'unhappy', 'problem', 'issue']):
            return self.workflow_templates['guest_complaint']
        elif any(word in description_lower for word in ['checkout', 'billing', 'charge', 'folio']):
            return self.workflow_templates['checkout_issue']
        else:
            # Default workflow
            return self.workflow_templates['guest_services']

    async def _execute_workflow_actions(self, ticket: HotelTicket, workflow: Dict) -> Dict:
        """Execute workflow-specific automated actions"""
        completed_actions = []
        pms_updates = []

        try:
            for action in workflow['auto_actions']:
                if action == 'create_work_order':
                    success = await self.opera.create_maintenance_request(ticket)
                    if success:
                        completed_actions.append('maintenance_work_order_created')
                        pms_updates.append('work_order')

                elif action == 'update_room_status':
                    # Update room status based on issue type
                    if ticket.issue_category == 'maintenance':
                        success = await self.opera.update_housekeeping_status(
                            ticket.room_number, 'out_of_order',
                            f"Maintenance issue: {ticket.description[:100]}"
                        )
                        if success:
                            completed_actions.append('room_status_updated')
                            pms_updates.append('housekeeping_status')

                elif action == 'escalate_to_manager':
                    # Log escalation (in real implementation, would notify manager)
                    completed_actions.append('escalated_to_manager')

                elif action == 'offer_compensation':
                    # In real implementation, could automatically post credits
                    completed_actions.append('compensation_offered')

                # Add more action implementations as needed

        except Exception as e:
            logger.error(f"Error executing workflow actions: {e}")

        return {
            'completed_actions': completed_actions,
            'pms_updates': pms_updates,
            'guest_communication': workflow.get('guest_communication', False)
        }

# Example usage and testing
async def demo_opera_integration():
    """Demo Opera PMS integration"""

    # Sample property configuration
    property_config = OperaProperty(
        property_id="HOTEL001",
        property_name="Demo Resort & Spa",
        opera_server_url="https://opera-api.demo-hotel.com",
        username=os.environ.get('OPERA_USERNAME', 'YOUR_OPERA_USERNAME_HERE'),
        password=os.environ.get('OPERA_PASSWORD', 'YOUR_OPERA_PASSWORD_HERE'),
        interface_id="TICKETZERO_AI",
        resort_code="DEMO"
    )

    # Initialize Opera connector
    opera_connector = OperaPMSConnector(property_config)

    try:
        # Initialize connection (would fail with demo credentials)
        print("Initializing Opera PMS connection...")
        # await opera_connector.initialize()

        # Sample hotel ticket
        hotel_ticket = HotelTicket(
            ticket_id="HTL-2024-001",
            guest_name="John Smith",
            room_number="1205",
            reservation_id="RSV123456",
            folio_number="FOL789012",
            issue_category="technical",
            priority="high",
            description="Guest reports WiFi not working in room, urgent business meeting in 30 minutes",
            reported_by="guest",
            department="it",
            property_id="HOTEL001",
            created_at=datetime.now(),
            guest_language="en",
            guest_vip_status=True
        )

        # Process ticket with workflow engine
        workflow_engine = HotelWorkflowEngine(opera_connector)
        result = await workflow_engine.process_hotel_ticket(hotel_ticket)

        print(f"Ticket processing result: {result}")

    except Exception as e:
        print(f"Demo error (expected with demo credentials): {e}")

    finally:
        await opera_connector.close()

if __name__ == "__main__":
    asyncio.run(demo_opera_integration())