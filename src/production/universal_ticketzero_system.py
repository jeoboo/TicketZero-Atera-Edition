#!/usr/bin/env python3
"""
Universal TicketZero AI System
Multi-industry support: MSP, Hospitality, Enterprise, and more
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Import industry-specific connectors
from msp_ticketzero_optimized import MSPTicketZeroAI, MSPClient
from opera_pms_connector import OperaPMSConnector, OperaProperty, HotelTicket, HotelWorkflowEngine
from goto_admin_connector import GoToAdminConnector, GoToAdminConfig, GoToTicket, RemoteSupportWorkflow

logger = logging.getLogger(__name__)

class IndustryType(Enum):
    """Supported industry types"""
    MSP = "msp"
    HOSPITALITY = "hospitality"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERPRISE = "enterprise"
    RETAIL = "retail"

@dataclass
class UniversalClient:
    """Universal client configuration"""
    client_id: str
    client_name: str
    industry_type: IndustryType
    configuration: Dict[str, Any]
    active: bool = True

class UniversalTicketZeroSystem:
    """Universal TicketZero system supporting multiple industries"""

    def __init__(self):
        self.clients: Dict[str, UniversalClient] = {}
        self.industry_processors = {}
        self.active_sessions = {}

    async def initialize(self):
        """Initialize universal system"""
        try:
            # Initialize industry-specific processors
            await self._initialize_industry_processors()

            # Load client configurations
            await self._load_client_configurations()

            logger.info(f"Universal TicketZero initialized with {len(self.clients)} clients")
            return True

        except Exception as e:
            logger.error(f"Universal system initialization failed: {e}")
            return False

    async def _initialize_industry_processors(self):
        """Initialize processors for each industry"""

        # MSP Processor
        self.industry_processors[IndustryType.MSP] = {
            'name': 'MSP TicketZero AI',
            'processor': MSPTicketZeroAI(),
            'capabilities': [
                'automated_ticket_resolution',
                'multi_tenant_support',
                'atera_integration',
                'cost_tracking',
                'sla_monitoring'
            ]
        }

        # Initialize MSP processor
        await self.industry_processors[IndustryType.MSP]['processor'].initialize_clients()

        # Hospitality Processor (will be initialized per property)
        self.industry_processors[IndustryType.HOSPITALITY] = {
            'name': 'Hotel Operations AI',
            'processor': None,  # Initialized per property
            'capabilities': [
                'opera_pms_integration',
                'guest_service_automation',
                'housekeeping_coordination',
                'maintenance_management',
                'multilingual_support'
            ]
        }

        # Enterprise Processor
        self.industry_processors[IndustryType.ENTERPRISE] = {
            'name': 'Enterprise Support AI',
            'processor': None,  # Will use GoTo + custom workflows
            'capabilities': [
                'goto_remote_support',
                'advanced_escalation',
                'department_routing',
                'compliance_tracking',
                'audit_trails'
            ]
        }

    async def _load_client_configurations(self):
        """Load client configurations from various sources"""

        # Sample client configurations - in production, load from database
        sample_clients = [
            {
                'client_id': 'msp_001',
                'client_name': 'TechFlow MSP',
                'industry_type': IndustryType.MSP,
                'configuration': {
                    'atera_api_key': 'msp_atera_key_001',
                    'ai_provider': 'azure',
                    'response_timeout': 5,
                    'escalation_threshold': 2
                }
            },
            {
                'client_id': 'hotel_001',
                'client_name': 'Grand Resort & Spa',
                'industry_type': IndustryType.HOSPITALITY,
                'configuration': {
                    'property_id': 'GRAND001',
                    'opera_server_url': 'https://opera-api.grandresort.com',
                    'opera_username': os.getenv('OPERA_USERNAME', 'REPLACE_ME'),
                    'opera_password': os.getenv('OPERA_PASSWORD', 'REPLACE_ME'),
                    'resort_code': 'GRAND',
                    'interface_id': 'TICKETZERO_AI'
                }
            },
            {
                'client_id': 'enterprise_001',
                'client_name': 'MegaCorp Industries',
                'industry_type': IndustryType.ENTERPRISE,
                'configuration': {
                    'goto_client_id': 'goto_client_001',
                    'goto_client_secret': 'goto_secret_001',
                    'goto_api_key': 'goto_api_001',
                    'departments': ['IT', 'HR', 'Finance', 'Operations'],
                    'escalation_matrix': {
                        'IT': 'it_manager@megacorp.com',
                        'HR': 'hr_director@megacorp.com'
                    }
                }
            }
        ]

        for client_config in sample_clients:
            client = UniversalClient(**client_config)
            self.clients[client.client_id] = client

            # Initialize industry-specific components
            await self._initialize_client_processor(client)

    async def _initialize_client_processor(self, client: UniversalClient):
        """Initialize industry-specific processor for client"""

        if client.industry_type == IndustryType.HOSPITALITY:
            # Initialize Opera PMS connector for this property
            opera_config = OperaProperty(
                property_id=client.configuration['property_id'],
                property_name=client.client_name,
                opera_server_url=client.configuration['opera_server_url'],
                username=client.configuration['opera_username'],
                password=client.configuration['opera_password'],
                interface_id=client.configuration['interface_id'],
                resort_code=client.configuration['resort_code']
            )

            opera_connector = OperaPMSConnector(opera_config)
            # await opera_connector.initialize()  # Would need real credentials

            workflow_engine = HotelWorkflowEngine(opera_connector)

            # Store in active sessions
            self.active_sessions[client.client_id] = {
                'opera_connector': opera_connector,
                'workflow_engine': workflow_engine
            }

        elif client.industry_type == IndustryType.ENTERPRISE:
            # Initialize GoTo Admin connector
            goto_config = GoToAdminConfig(
                client_id=client.configuration['goto_client_id'],
                client_secret=client.configuration['goto_client_secret'],
                api_key=client.configuration['goto_api_key']
            )

            goto_connector = GoToAdminConnector(goto_config)
            # await goto_connector.initialize()  # Would need real credentials

            remote_workflow = RemoteSupportWorkflow(goto_connector)

            # Store in active sessions
            self.active_sessions[client.client_id] = {
                'goto_connector': goto_connector,
                'remote_workflow': remote_workflow
            }

    async def process_universal_ticket(self, client_id: str, ticket_data: Dict) -> Dict[str, Any]:
        """Process ticket using appropriate industry processor"""

        try:
            client = self.clients.get(client_id)
            if not client:
                return {
                    'success': False,
                    'error': f'Client {client_id} not found'
                }

            if not client.active:
                return {
                    'success': False,
                    'error': f'Client {client_id} is inactive'
                }

            # Route to appropriate industry processor
            if client.industry_type == IndustryType.MSP:
                return await self._process_msp_ticket(client, ticket_data)

            elif client.industry_type == IndustryType.HOSPITALITY:
                return await self._process_hotel_ticket(client, ticket_data)

            elif client.industry_type == IndustryType.ENTERPRISE:
                return await self._process_enterprise_ticket(client, ticket_data)

            else:
                return {
                    'success': False,
                    'error': f'Industry type {client.industry_type.value} not yet supported'
                }

        except Exception as e:
            logger.error(f"Universal ticket processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _process_msp_ticket(self, client: UniversalClient, ticket_data: Dict) -> Dict[str, Any]:
        """Process MSP ticket"""

        msp_processor = self.industry_processors[IndustryType.MSP]['processor']

        # Convert universal ticket to MSP ticket format
        result = await msp_processor.process_ticket_fast(ticket_data, client.client_id)

        return {
            'success': result.get('success', False),
            'industry': 'MSP',
            'processing_time': result.get('processing_time', 0),
            'resolution_status': result.get('status', 'unknown'),
            'solution': result.get('solution'),
            'escalated': result.get('escalated', False),
            'cost_savings': self._calculate_msp_savings(result)
        }

    async def _process_hotel_ticket(self, client: UniversalClient, ticket_data: Dict) -> Dict[str, Any]:
        """Process hotel ticket"""

        session = self.active_sessions.get(client.client_id)
        if not session:
            return {
                'success': False,
                'error': 'Hotel systems not initialized'
            }

        # Convert universal ticket to hotel ticket format
        hotel_ticket = HotelTicket(
            ticket_id=ticket_data.get('ticket_id', f"HTL-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            guest_name=ticket_data.get('guest_name', ''),
            room_number=ticket_data.get('room_number', ''),
            reservation_id=ticket_data.get('reservation_id'),
            folio_number=ticket_data.get('folio_number'),
            issue_category=ticket_data.get('category', 'guest_services'),
            priority=ticket_data.get('priority', 'normal'),
            description=ticket_data.get('description', ''),
            reported_by=ticket_data.get('reported_by', 'guest'),
            department=ticket_data.get('department', 'front_desk'),
            property_id=client.configuration['property_id'],
            created_at=datetime.now()
        )

        workflow_engine = session['workflow_engine']
        result = await workflow_engine.process_hotel_ticket(hotel_ticket)

        return {
            'success': result.get('success', False),
            'industry': 'Hospitality',
            'workflow_applied': result.get('workflow_applied'),
            'actions_completed': result.get('actions_completed', []),
            'pms_integration': result.get('pms_integration', []),
            'guest_notified': result.get('guest_notified', False),
            'estimated_resolution_time': result.get('estimated_resolution_time', 0)
        }

    async def _process_enterprise_ticket(self, client: UniversalClient, ticket_data: Dict) -> Dict[str, Any]:
        """Process enterprise ticket"""

        session = self.active_sessions.get(client.client_id)
        if not session:
            return {
                'success': False,
                'error': 'Enterprise systems not initialized'
            }

        # Convert universal ticket to GoTo ticket format
        goto_ticket = GoToTicket(
            ticket_id=ticket_data.get('ticket_id', f"ENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            title=ticket_data.get('title', ''),
            description=ticket_data.get('description', ''),
            category=ticket_data.get('category', 'support'),
            priority=ticket_data.get('priority', 'normal'),
            user_name=ticket_data.get('user_name', ''),
            user_email=ticket_data.get('user_email', ''),
            department=ticket_data.get('department', 'IT'),
            created_at=datetime.now(),
            requires_remote_session=ticket_data.get('requires_remote', False)
        )

        remote_workflow = session['remote_workflow']
        result = await remote_workflow.process_support_ticket(goto_ticket)

        return {
            'success': result.get('success', False),
            'industry': 'Enterprise',
            'workflow_type': result.get('workflow_type'),
            'remote_session_created': result.get('remote_session_created', False),
            'session_details': result.get('session_details'),
            'estimated_resolution_time': result.get('estimated_resolution_time', 0),
            'follow_up_required': result.get('follow_up_required', False)
        }

    def _calculate_msp_savings(self, result: Dict) -> Dict:
        """Calculate cost savings for MSP tickets"""
        if result.get('success'):
            processing_time = result.get('processing_time', 0)
            traditional_time = 30 * 60  # 30 minutes in seconds
            hourly_rate = 25  # $25/hour

            traditional_cost = (traditional_time / 3600) * hourly_rate
            ai_cost = (processing_time / 3600) * hourly_rate
            savings = traditional_cost - ai_cost

            return {
                'traditional_cost': round(traditional_cost, 2),
                'ai_cost': round(ai_cost, 2),
                'savings': round(savings, 2),
                'savings_percentage': round((savings / traditional_cost) * 100, 1) if traditional_cost > 0 else 0
            }
        return {}

    async def get_universal_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data across all industries"""

        dashboard_data = {
            'total_clients': len(self.clients),
            'active_clients': len([c for c in self.clients.values() if c.active]),
            'industries': {},
            'overall_metrics': {
                'total_tickets_24h': 0,
                'avg_resolution_time': 0,
                'cost_savings_24h': 0
            }
        }

        # Collect industry-specific metrics
        for industry in IndustryType:
            industry_clients = [c for c in self.clients.values() if c.industry_type == industry]

            if industry_clients:
                dashboard_data['industries'][industry.value] = {
                    'client_count': len(industry_clients),
                    'active_clients': len([c for c in industry_clients if c.active]),
                    'capabilities': self.industry_processors.get(industry, {}).get('capabilities', [])
                }

        # Get MSP metrics if available
        if IndustryType.MSP in self.industry_processors:
            msp_processor = self.industry_processors[IndustryType.MSP]['processor']
            if hasattr(msp_processor, 'get_msp_performance_report'):
                msp_report = msp_processor.get_msp_performance_report(hours=24)
                dashboard_data['overall_metrics']['total_tickets_24h'] += msp_report.get('total_tickets_processed', 0)
                dashboard_data['overall_metrics']['cost_savings_24h'] += msp_report.get('cost_savings_estimate', {}).get('total_savings', 0)

        return dashboard_data

    async def get_client_status(self, client_id: str) -> Dict[str, Any]:
        """Get detailed status for specific client"""

        client = self.clients.get(client_id)
        if not client:
            return {'error': f'Client {client_id} not found'}

        status = {
            'client_id': client.client_id,
            'client_name': client.client_name,
            'industry_type': client.industry_type.value,
            'active': client.active,
            'configuration_status': 'configured',
            'last_activity': datetime.now().isoformat(),
            'capabilities': self.industry_processors.get(client.industry_type, {}).get('capabilities', [])
        }

        # Add industry-specific status
        if client.industry_type == IndustryType.MSP:
            msp_processor = self.industry_processors[IndustryType.MSP]['processor']
            if hasattr(msp_processor, 'get_msp_performance_report'):
                msp_report = msp_processor.get_msp_performance_report(client_id, hours=24)
                status['performance'] = {
                    'tickets_24h': msp_report.get('total_tickets_processed', 0),
                    'resolution_rate': msp_report.get('resolution_rate_percent', 0),
                    'avg_response_time': msp_report.get('avg_processing_time_seconds', 0)
                }

        return status

    async def close(self):
        """Close all connections and cleanup"""
        try:
            # Close industry processors
            for industry_type, processor_info in self.industry_processors.items():
                processor = processor_info.get('processor')
                if processor and hasattr(processor, 'close'):
                    await processor.close()

            # Close active sessions
            for client_id, session in self.active_sessions.items():
                for connector_name, connector in session.items():
                    if hasattr(connector, 'close'):
                        await connector.close()

            logger.info("Universal TicketZero system closed")

        except Exception as e:
            logger.error(f"Error closing universal system: {e}")

# Demo and testing
async def demo_universal_system():
    """Demo universal system with multiple industries"""

    universal_system = UniversalTicketZeroSystem()

    try:
        print("Initializing Universal TicketZero System...")
        await universal_system.initialize()

        # Test MSP ticket
        msp_ticket = {
            'ticket_id': 'MSP-001',
            'TicketTitle': 'Outlook not syncing emails',
            'FirstComment': 'User reports Outlook is not syncing emails properly since this morning',
            'Priority': 'High'
        }

        print("\nProcessing MSP ticket...")
        msp_result = await universal_system.process_universal_ticket('msp_001', msp_ticket)
        print(f"MSP Result: {msp_result}")

        # Test Hotel ticket
        hotel_ticket = {
            'ticket_id': 'HTL-001',
            'guest_name': 'John Smith',
            'room_number': '1205',
            'category': 'technical',
            'priority': 'high',
            'description': 'WiFi not working in room',
            'reported_by': 'guest',
            'department': 'it'
        }

        print("\nProcessing Hotel ticket...")
        hotel_result = await universal_system.process_universal_ticket('hotel_001', hotel_ticket)
        print(f"Hotel Result: {hotel_result}")

        # Test Enterprise ticket
        enterprise_ticket = {
            'ticket_id': 'ENT-001',
            'title': 'Need help with software installation',
            'description': 'User needs assistance installing new CRM software',
            'category': 'software_installation',
            'priority': 'normal',
            'user_name': 'Jane Doe',
            'user_email': 'jane.doe@megacorp.com',
            'department': 'Sales',
            'requires_remote': True
        }

        print("\nProcessing Enterprise ticket...")
        enterprise_result = await universal_system.process_universal_ticket('enterprise_001', enterprise_ticket)
        print(f"Enterprise Result: {enterprise_result}")

        # Get dashboard data
        print("\nUniversal Dashboard Data:")
        dashboard = await universal_system.get_universal_dashboard_data()
        print(f"Dashboard: {dashboard}")

    except Exception as e:
        print(f"Demo error: {e}")

    finally:
        await universal_system.close()

if __name__ == "__main__":
    asyncio.run(demo_universal_system())