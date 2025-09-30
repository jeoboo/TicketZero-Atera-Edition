"""
Azure Graph API Integration for Enterprise Authentication and Management
Integrates with Microsoft Graph for user management, device compliance, and security insights
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import aiohttp
from datetime import datetime, timedelta
import os
from dataclasses import dataclass

# Import validation utilities
try:
    from ..utils.api_validator import (
        validate_azure_graph_response,
        validate_azure_token_response,
        safe_async_api_call,
        safe_get_nested,
        validate_response_schema
    )
except ImportError:
    # Fallback if import fails
    def validate_azure_graph_response(response):
        try:
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def validate_azure_token_response(response):
        try:
            data = response.json() if response.status_code == 200 else None
            return data.get('access_token') if data else None
        except:
            return None

    async def safe_async_api_call(func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"API call failed: {e}")
            return None

    def safe_get_nested(data, path, default=None):
        try:
            keys = path.split('.')
            result = data
            for key in keys:
                result = result[key]
            return result
        except:
            return default

    def validate_response_schema(data, schema):
        return True  # Basic fallback

@dataclass
class AzureConfig:
    tenant_id: str
    client_id: str
    client_secret: str
    scope: str = "https://graph.microsoft.com/.default"

class AzureGraphClient:
    def __init__(self, config: AzureConfig):
        self.config = config
        self.access_token = None
        self.token_expires = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.logger = logging.getLogger(__name__)
        
    async def get_access_token(self) -> str:
        """Get OAuth2 access token for Microsoft Graph API"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
            
        token_url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'scope': self.config.scope,
            'grant_type': 'client_credentials'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                    self.logger.info("Azure Graph API token obtained successfully")
                    return self.access_token
                else:
                    error = await response.text()
                    self.logger.error(f"Failed to get Azure token: {error}")
                    raise Exception(f"Azure authentication failed: {response.status}")

    async def make_graph_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Microsoft Graph API with proper validation"""
        try:
            token = await self.get_access_token()
            if not token:
                self.logger.error("Failed to get access token")
                return None

            url = f"{self.base_url}{endpoint}"

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    if response.status == 204:
                        return {"status": "success"}

                    if response.status in [200, 201]:
                        try:
                            response_data = await response.json()

                            # Check for Graph API error structure
                            if 'error' in response_data:
                                error_info = response_data['error']
                                error_code = error_info.get('code', 'unknown')
                                error_message = error_info.get('message', 'Unknown error')
                                self.logger.error(f"Graph API error {error_code}: {error_message}")
                                return None

                            return response_data

                        except json.JSONDecodeError as e:
                            self.logger.error(f"Invalid JSON response: {e}")
                            return None
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Graph API error {response.status}: {error_text}")
                        return None

        except Exception as e:
            self.logger.error(f"Graph API request failed: {e}")
            return None

    async def get_users(self, filter_query: str = None, top: int = 100) -> List[Dict]:
        """Get Azure AD users with optional filtering"""
        endpoint = f"/users?$top={top}"
        if filter_query:
            endpoint += f"&$filter={filter_query}"
        
        response = await self.make_graph_request(endpoint)
        return response.get('value', [])

    async def get_devices(self, filter_query: str = None, top: int = 100) -> List[Dict]:
        """Get Azure AD devices with compliance status"""
        endpoint = f"/devices?$top={top}"
        if filter_query:
            endpoint += f"&$filter={filter_query}"
        
        response = await self.make_graph_request(endpoint)
        return response.get('value', [])

    async def get_device_compliance(self, device_id: str) -> Dict:
        """Get device compliance status and policies"""
        endpoint = f"/deviceManagement/managedDevices/{device_id}/deviceCompliancePolicyStates"
        return await self.make_graph_request(endpoint)

    async def get_security_alerts(self, top: int = 50) -> List[Dict]:
        """Get Microsoft Defender security alerts"""
        endpoint = f"/security/alerts?$top={top}&$orderby=createdDateTime desc"
        response = await self.make_graph_request(endpoint)
        return response.get('value', [])

    async def get_user_signin_logs(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get user sign-in logs for security analysis"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
        endpoint = f"/auditLogs/signIns?$filter=userId eq '{user_id}' and createdDateTime ge {start_date}"
        
        response = await self.make_graph_request(endpoint)
        return response.get('value', [])

    async def get_audit_logs(self, category: str = None, days: int = 7) -> List[Dict]:
        """Get Azure AD audit logs"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
        endpoint = f"/auditLogs/directoryAudits?$filter=activityDateTime ge {start_date}"
        
        if category:
            endpoint += f" and category eq '{category}'"
        
        response = await self.make_graph_request(endpoint)
        return response.get('value', [])

    async def create_security_incident(self, title: str, description: str, severity: str = "medium") -> Dict:
        """Create security incident in Microsoft Sentinel"""
        incident_data = {
            "title": title,
            "description": description,
            "severity": severity,
            "status": "New",
            "createdBy": "TicketZero AI Automation"
        }
        
        endpoint = "/security/incidents"
        return await self.make_graph_request(endpoint, "POST", incident_data)

class AzureAteraSync:
    """Synchronize Azure AD data with Atera for unified management"""
    
    def __init__(self, azure_client: AzureGraphClient, atera_client):
        self.azure = azure_client
        self.atera = atera_client
        self.logger = logging.getLogger(__name__)

    async def sync_users_to_atera(self) -> Dict:
        """Sync Azure AD users to Atera contacts"""
        try:
            azure_users = await self.azure.get_users()
            atera_contacts = await self.atera.get_contacts()
            
            sync_results = {
                "created": 0,
                "updated": 0,
                "errors": []
            }
            
            for user in azure_users:
                try:
                    # Check if user exists in Atera
                    existing_contact = next(
                        (c for c in atera_contacts if c.get('Email') == user.get('mail')), 
                        None
                    )
                    
                    contact_data = {
                        "FirstName": user.get('givenName', ''),
                        "LastName": user.get('surname', ''),
                        "Email": user.get('mail', ''),
                        "Title": user.get('jobTitle', ''),
                        "Phone": user.get('businessPhones', [''])[0] if user.get('businessPhones') else '',
                        "Notes": f"Synced from Azure AD - ID: {user.get('id')}"
                    }
                    
                    if existing_contact:
                        # Update existing contact
                        await self.atera.update_contact(existing_contact['ContactID'], contact_data)
                        sync_results["updated"] += 1
                    else:
                        # Create new contact
                        await self.atera.create_contact(contact_data)
                        sync_results["created"] += 1
                        
                except Exception as e:
                    sync_results["errors"].append(f"User {user.get('mail')}: {str(e)}")
                    
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Azure-Atera sync failed: {e}")
            return {"error": str(e)}

    async def sync_devices_to_atera(self) -> Dict:
        """Sync Azure AD devices to Atera agents/devices"""
        try:
            azure_devices = await self.azure.get_devices()
            
            sync_results = {
                "processed": 0,
                "compliance_issues": [],
                "security_alerts": []
            }
            
            for device in azure_devices:
                try:
                    # Check device compliance
                    if not device.get('isCompliant', True):
                        sync_results["compliance_issues"].append({
                            "device": device.get('displayName'),
                            "id": device.get('id'),
                            "issue": "Device not compliant with policies"
                        })
                    
                    # Check for security issues
                    if device.get('trustType') != 'Workplace':
                        sync_results["security_alerts"].append({
                            "device": device.get('displayName'),
                            "id": device.get('id'),
                            "alert": f"Untrusted device type: {device.get('trustType')}"
                        })
                    
                    sync_results["processed"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Device sync error for {device.get('displayName')}: {e}")
                    
            return sync_results
            
        except Exception as e:
            self.logger.error(f"Device sync failed: {e}")
            return {"error": str(e)}

    async def create_atera_tickets_from_azure_alerts(self) -> List[Dict]:
        """Create Atera tickets from Azure security alerts"""
        try:
            alerts = await self.azure.get_security_alerts()
            created_tickets = []
            
            for alert in alerts:
                # Only process high severity alerts
                if alert.get('severity', '').lower() in ['high', 'critical']:
                    ticket_data = {
                        "TicketTitle": f"Security Alert: {alert.get('title', 'Unknown')}",
                        "TicketDescription": f"""
Azure Security Alert Details:
- Alert ID: {alert.get('id')}
- Severity: {alert.get('severity')}
- Category: {alert.get('category')}
- Description: {alert.get('description', 'No description available')}
- Affected Resource: {alert.get('resourceIdentifiers', [{}])[0].get('resourceName', 'Unknown')}
- Detection Source: {alert.get('vendorInformation', {}).get('vendor', 'Microsoft Defender')}
- Created: {alert.get('createdDateTime')}

Automated Response Required: High priority security incident requiring immediate attention.
                        """.strip(),
                        "TicketPriority": "Critical" if alert.get('severity') == 'high' else "High",
                        "TicketType": "Security Incident",
                        "TicketStatus": "Open",
                        "Source": "Azure Security Center"
                    }
                    
                    ticket = await self.atera.create_ticket(ticket_data)
                    if ticket:
                        created_tickets.append(ticket)
            
            return created_tickets
            
        except Exception as e:
            self.logger.error(f"Failed to create tickets from Azure alerts: {e}")
            return []

# Usage example and configuration
async def main():
    """Example usage of Azure Graph integration"""
    
    # Configure Azure AD app
    config = AzureConfig(
        tenant_id=os.getenv('AZURE_TENANT_ID'),
        client_id=os.getenv('AZURE_CLIENT_ID'),
        client_secret=os.getenv('AZURE_CLIENT_SECRET')
    )
    
    # Initialize clients
    azure_client = AzureGraphClient(config)
    
    try:
        # Test connection
        users = await azure_client.get_users(top=5)
        print(f"Successfully connected to Azure. Found {len(users)} users.")
        
        # Get security alerts
        alerts = await azure_client.get_security_alerts(top=10)
        print(f"Found {len(alerts)} security alerts.")
        
        # Get device compliance
        devices = await azure_client.get_devices(top=5)
        print(f"Found {len(devices)} managed devices.")
        
    except Exception as e:
        print(f"Azure integration test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())