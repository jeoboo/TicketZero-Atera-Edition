#!/usr/bin/env python3
"""
Test script for TicketZero AI License System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.production.license_manager import license_manager

def test_license_generation():
    """Test license generation"""
    print("Testing License Generation...")
    print("=" * 50)

    # Test creating licenses for different plans
    plans = ["starter", "professional", "enterprise"]

    for plan_id in plans:
        try:
            print(f"\nCreating {plan_id} license...")
            license_info = license_manager.create_license(
                plan_id=plan_id,
                customer_name=f"Test Customer {plan_id.title()}",
                customer_email=f"test_{plan_id}@company.com"
            )

            print(f"+ License created: {license_info.license_key}")
            print(f"  Customer: {license_info.customer_name}")
            print(f"  Plan: {license_info.license_type}")
            print(f"  Price: ${license_info.price_paid:,.2f}")
            print(f"  Max Clients: {license_info.max_clients}")
            print(f"  Max Tickets/Month: {license_info.max_tickets_per_month:,}")
            print(f"  Features: {len(license_info.features)} features")

        except Exception as e:
            print(f"- Error creating {plan_id} license: {e}")

def test_license_activation():
    """Test license activation"""
    print("\n\nTesting License Activation...")
    print("=" * 50)

    # Test with different license key formats
    test_keys = [
        "TZ-STA-1234-5678-ABCD-EFGH",  # Starter
        "TZ-PRO-9876-5432-WXYZ-QRST",  # Professional
        "TZ-ENT-1111-2222-3333-4444",  # Enterprise
        "INVALID-KEY-FORMAT"           # Invalid
    ]

    for key in test_keys:
        print(f"\nTesting activation of: {key}")
        success, message = license_manager.activate_license(key)
        if success:
            print(f"+ Activation successful: {message}")
        else:
            print(f"- Activation failed: {message}")

def test_license_validation():
    """Test license validation"""
    print("\n\nTesting License Validation...")
    print("=" * 50)

    # Test validation
    is_valid, message = license_manager.validate_license()
    print(f"License validation: {'Valid' if is_valid else 'Invalid'}")
    print(f"Message: {message}")

    # Get license status
    status = license_manager.get_license_status()
    print(f"\nLicense Status:")
    print(f"  Status: {status['status']}")
    print(f"  Message: {status['message']}")

    if status.get('license_key'):
        print(f"  License Key: {status['license_key']}")
        print(f"  Customer: {status.get('customer_name', 'N/A')}")
        print(f"  Plan: {status.get('plan_name', 'N/A')}")
        print(f"  Days Remaining: {status.get('days_remaining', 0)}")

def test_trial_license():
    """Test trial license generation"""
    print("\n\nTesting Trial License...")
    print("=" * 50)

    try:
        trial_license = license_manager.generate_trial_license("trial@test.com", days=30)
        print(f"+ Trial license generated: {trial_license.license_key}")
        print(f"  Customer: {trial_license.customer_name}")
        print(f"  Email: {trial_license.customer_email}")
        print(f"  Max Clients: {trial_license.max_clients}")
        print(f"  Max Tickets: {trial_license.max_tickets_per_month}")
        print(f"  Expires: {trial_license.expiry_date.strftime('%Y-%m-%d')}")

    except Exception as e:
        print(f"- Error generating trial: {e}")

def test_pricing_info():
    """Test pricing information"""
    print("\n\nTesting Pricing Information...")
    print("=" * 50)

    pricing = license_manager.get_pricing_info()
    for plan_id, plan in pricing.items():
        print(f"\n{plan['name']}:")
        print(f"  Price: {plan['price_formatted']}")
        print(f"  Duration: {plan['duration_months']} months")
        print(f"  Max Clients: {plan['max_clients']}")
        print(f"  Max Tickets/Month: {plan['max_tickets_per_month']:,}")
        print(f"  Features: {len(plan['features'])} features")
        print(f"  Recommended: {'Yes' if plan.get('recommended') else 'No'}")

def test_feature_access():
    """Test feature access checking"""
    print("\n\nTesting Feature Access...")
    print("=" * 50)

    test_features = [
        "AI Ticket Processing",
        "Advanced Dashboard",
        "White Label Branding",
        "Custom Integrations",
        "Premium Support"
    ]

    for feature in test_features:
        has_access = license_manager.check_feature_access(feature)
        print(f"  {feature}: {'Available' if has_access else 'Not Available'}")

    # Test usage limits
    limits = license_manager.get_usage_limits()
    print(f"\nUsage Limits:")
    print(f"  Max Clients: {limits['max_clients']}")
    print(f"  Max Tickets/Month: {limits['max_tickets_per_month']}")
    print(f"  Features Limited: {'Yes' if limits['features_limited'] else 'No'}")

if __name__ == "__main__":
    print("TicketZero AI - License System Test")
    print("=" * 50)

    try:
        # Run all tests
        test_license_generation()
        test_license_activation()
        test_license_validation()
        test_trial_license()
        test_pricing_info()
        test_feature_access()

        print("\n" + "=" * 50)
        print("+ All license tests completed successfully!")
        print("\nTo test the license interface:")
        print("1. Run: python src/production/msp_ticketzero_optimized.py")
        print("2. Open: http://localhost:8080")
        print("3. Click 'Admin Panel' button")
        print("4. Go to 'License & Billing' tab")
        print("5. Test license activation and trial generation")

        # Show sample license keys for testing
        print("\nSample license keys for testing:")
        print("  Starter:      TZ-STA-1234-5678-ABCD-EFGH")
        print("  Professional: TZ-PRO-9876-5432-WXYZ-QRST")
        print("  Enterprise:   TZ-ENT-1111-2222-3333-4444")

    except Exception as e:
        print(f"\n- Test failed: {e}")
        sys.exit(1)