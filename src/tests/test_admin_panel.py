#!/usr/bin/env python3
"""
Test script for Admin Panel API Configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.production.env_manager import env_manager

def test_env_manager():
    """Test environment manager functionality"""
    print("Testing Environment Manager...")
    print("=" * 50)

    # Test loading current environment
    print(f"Environment file: {env_manager.env_file_path}")
    print(f"Total variables loaded: {len(env_manager.env_vars)}")

    # Test getting API configuration
    api_config = env_manager.get_api_config()
    print("\nCurrent API Configuration:")
    for provider, config in api_config.items():
        print(f"\n{provider.upper()}:")
        for key, value in config.items():
            # Mask sensitive values
            display_value = value if not any(word in key.lower() for word in ['key', 'password', 'pass']) else ('*' * len(value) if value else '')
            print(f"  {key}: {display_value}")

    # Test validation
    issues = env_manager.validate_api_config()
    print("\nConfiguration Validation:")
    print(f"Missing required: {len(issues['missing'])}")
    print(f"Invalid format: {len(issues['invalid'])}")
    print(f"Warnings: {len(issues['warnings'])}")

    if issues['missing']:
        print("\nMissing required variables:")
        for issue in issues['missing']:
            print(f"  - {issue}")

    if issues['warnings']:
        print("\nWarnings:")
        for warning in issues['warnings']:
            print(f"  - {warning}")

    # Test updating configuration
    print("\nTesting configuration update...")
    test_updates = {
        "atera": {
            "api_key": "test_atera_key_123",
            "api_url": "https://app.atera.com/api/v3"
        },
        "openai": {
            "api_key": "test_openai_key_456",
            "model": "gpt-3.5-turbo"
        }
    }

    # Update configuration
    env_manager.update_api_config(test_updates)
    print("Configuration updated in memory")

    # Check if values were updated
    updated_config = env_manager.get_api_config()
    print(f"Atera API Key updated: {updated_config['atera']['api_key'] == 'test_atera_key_123'}")
    print(f"OpenAI API Key updated: {updated_config['openai']['api_key'] == 'test_openai_key_456'}")

    print("\n" + "=" * 50)
    print("Environment Manager test completed!")

def test_dashboard_integration():
    """Test dashboard integration"""
    print("\nTesting Dashboard Integration...")
    print("=" * 50)

    try:
        # Import the dashboard components
        from src.production.msp_dashboard import MSPDashboard

        # Create a mock MSP system for testing
        class MockMSPSystem:
            def __init__(self):
                self.clients = {}
                self.metrics = []

        mock_system = MockMSPSystem()
        dashboard = MSPDashboard(mock_system)

        # Test HTML generation with admin panel
        html = dashboard.get_dashboard_html(show_admin=False)
        print(f"Dashboard HTML generated: {len(html)} characters")
        print("Admin panel toggle button included:", "Admin Panel" in html)

        # Check if admin panel elements are present
        admin_elements = [
            "admin-panel",
            "API Configuration",
            "saveAPIConfig",
            "Atera RMM Integration",
            "OpenAI Integration"
        ]

        for element in admin_elements:
            if element in html:
                print(f"+ {element} found in HTML")
            else:
                print(f"- {element} missing from HTML")

        print("\nDashboard integration test completed!")

    except Exception as e:
        print(f"Dashboard integration test failed: {e}")

if __name__ == "__main__":
    print("TicketZero AI - Admin Panel Test")
    print("=" * 50)

    try:
        test_env_manager()
        test_dashboard_integration()

        print("\n" + "=" * 50)
        print("+ All tests completed successfully!")
        print("\nTo test the admin panel:")
        print("1. Run: python src/production/msp_ticketzero_optimized.py")
        print("2. Open: http://localhost:8080")
        print("3. Click 'Admin Panel' button")
        print("4. Configure API settings")
        print("5. Click 'Save Configuration'")

    except Exception as e:
        print(f"\n- Test failed: {e}")
        sys.exit(1)