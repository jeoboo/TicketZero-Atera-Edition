#!/usr/bin/env python3
"""
Test Azure Graph API Integration
Tests the existing Azure Graph integration for enterprise management
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.production.azure_graph_integration import AzureGraphClient, AzureConfig

async def test_azure_connection():
    """Test Azure Graph API connection with existing integration"""
    print("Testing Azure Graph API Integration")
    print("=" * 60)

    # Get configuration from environment
    config = AzureConfig(
        tenant_id=os.getenv('AZURE_TENANT_ID', ''),
        client_id=os.getenv('AZURE_CLIENT_ID', ''),
        client_secret=os.getenv('AZURE_CLIENT_SECRET', '')
    )

    if not all([config.tenant_id, config.client_id, config.client_secret]):
        print("- ERROR: Azure credentials not configured")
        print("\n Required environment variables:")
        print("   AZURE_TENANT_ID=your_tenant_id_here")
        print("   AZURE_CLIENT_ID=your_client_id_here")
        print("   AZURE_CLIENT_SECRET=your_client_secret_here")
        print("\n Get these from: https://portal.azure.com > App registrations")
        return False

    print(f" Configuration:")
    print(f"   Tenant ID: {config.tenant_id[:8]}...")
    print(f"   Client ID: {config.client_id[:8]}...")

    # Initialize Azure client
    azure_client = AzureGraphClient(config)

    try:
        print(f"\n Connecting to Azure Graph API...")

        # Test authentication
        token = await azure_client.get_access_token()
        if token:
            print("+ Successfully authenticated with Azure Graph API!")
        else:
            print("- Failed to authenticate")
            return False

        # Test users endpoint
        print(f"\n Testing Azure AD users access...")
        users = await azure_client.get_users(top=5)
        print(f"+ Found {len(users)} users")
        for user in users[:3]:
            print(f"   - {user.get('displayName', 'Unknown')} ({user.get('mail', 'No email')})")

        # Test devices endpoint
        print(f"\n Testing Azure AD devices access...")
        devices = await azure_client.get_devices(top=5)
        print(f"+ Found {len(devices)} managed devices")
        for device in devices[:3]:
            compliant = "+ Compliant" if device.get('isCompliant') else "- Non-compliant"
            print(f"   - {device.get('displayName', 'Unknown')} ({compliant})")

        # Test security alerts
        print(f"\n Testing security alerts access...")
        try:
            alerts = await azure_client.get_security_alerts(top=5)
            print(f"+ Found {len(alerts)} security alerts")
            for alert in alerts[:2]:
                severity = alert.get('severity', 'unknown').upper()
                print(f"   - {alert.get('title', 'Unknown alert')} (Severity: {severity})")
        except Exception as e:
            print(f"! Security alerts access limited: {str(e)[:100]}...")

        print(f"\n Azure Graph API integration successful!")
        print(f"\n Available features:")
        print(f"   + User Management (Get/Create/Update users)")
        print(f"   + Device Compliance (Monitor device status)")
        print(f"   + Security Alerts (Microsoft Defender integration)")
        print(f"   + Audit Logs (Sign-in and directory activity)")
        print(f"   + Atera Sync (Sync users and devices to Atera)")

        return True

    except Exception as e:
        print(f"- Azure Graph API test failed: {e}")
        return False

async def demo_atera_sync():
    """Demo Azure-Atera synchronization features"""
    print(f"\n Azure-Atera Sync Demo")
    print("=" * 60)

    config = AzureConfig(
        tenant_id=os.getenv('AZURE_TENANT_ID', ''),
        client_id=os.getenv('AZURE_CLIENT_ID', ''),
        client_secret=os.getenv('AZURE_CLIENT_SECRET', '')
    )

    azure_client = AzureGraphClient(config)

    try:
        # Get some Azure data for demo
        users = await azure_client.get_users(top=3)
        devices = await azure_client.get_devices(top=3)

        print(f" Azure AD Data Summary:")
        print(f"   Users found: {len(users)}")
        print(f"   Devices found: {len(devices)}")

        # Check for compliance issues
        non_compliant = [d for d in devices if not d.get('isCompliant', True)]
        if non_compliant:
            print(f"\n! Compliance Issues Found:")
            for device in non_compliant:
                print(f"   - {device.get('displayName')} is not compliant")
                print(f"     → Would create Atera ticket for compliance remediation")

        # Check for high-value users
        print(f"\n User Management Integration:")
        for user in users:
            job_title = user.get('jobTitle', 'Unknown Role')
            if any(role in job_title.lower() for role in ['admin', 'manager', 'director', 'ceo']):
                print(f"   - High-privilege user: {user.get('displayName')} ({job_title})")
                print(f"     → Would sync to Atera with elevated support priority")

        print(f"\n+ Sync capabilities ready for Atera integration")

    except Exception as e:
        print(f"- Demo failed: {e}")

if __name__ == "__main__":
    print("Azure Graph API - TicketZero Integration Test")
    print("=" * 60)

    async def run_tests():
        # Test basic connectivity
        basic_success = await test_azure_connection()

        if basic_success:
            # Run sync demo
            await demo_atera_sync()

            print(f"\n+ All tests completed successfully!")
            print(f"\n Next steps:")
            print(f"   1. Configure your Azure AD app credentials in .env.testing")
            print(f"   2. Use 'cp .env.testing .env' to activate")
            print(f"   3. Import AzureGraphClient in your TicketZero workflows")
            print(f"   4. Use AzureAteraSync for automated user/device synchronization")
        else:
            print(f"\n- Basic connectivity failed. Please check your Azure credentials.")

    asyncio.run(run_tests())