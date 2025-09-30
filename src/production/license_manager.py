#!/usr/bin/env python3
"""
TicketZero AI - Enterprise License Manager
Professional licensing system with $2.5K base pricing
"""

import os
import json
import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import base64
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

@dataclass
class LicenseInfo:
    """License information structure"""
    license_key: str
    customer_name: str
    customer_email: str
    license_type: str  # starter, professional, enterprise
    max_clients: int
    max_tickets_per_month: int
    issue_date: datetime
    expiry_date: datetime
    features: List[str]
    price_paid: float
    is_active: bool = True
    activation_count: int = 0
    max_activations: int = 3

@dataclass
class LicensePlan:
    """License plan definition"""
    plan_id: str
    name: str
    price: float
    max_clients: int
    max_tickets_per_month: int
    features: List[str]
    duration_months: int

class LicenseManager:
    """Professional license management system"""

    def __init__(self, license_file: str = "license.json"):
        self.license_file = license_file
        self.secret_key = self._get_or_create_secret_key()
        self.current_license = None
        self.license_plans = self._init_license_plans()

        # Load existing license
        self.load_license()

    def _get_or_create_secret_key(self) -> bytes:
        """Get or create encryption key for license security"""
        key_file = "license.key"

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def _init_license_plans(self) -> Dict[str, LicensePlan]:
        """Initialize available license plans"""
        return {
            "starter": LicensePlan(
                plan_id="starter",
                name="TicketZero AI Starter",
                price=2500.00,  # $2.5K base price
                max_clients=5,
                max_tickets_per_month=1000,
                features=[
                    "AI Ticket Processing",
                    "Atera Integration",
                    "Basic Dashboard",
                    "Email Support",
                    "Standard SLA"
                ],
                duration_months=12
            ),
            "professional": LicensePlan(
                plan_id="professional",
                name="TicketZero AI Professional",
                price=4500.00,  # $4.5K for professional
                max_clients=15,
                max_tickets_per_month=5000,
                features=[
                    "AI Ticket Processing",
                    "Atera Integration",
                    "Advanced Dashboard",
                    "Multi-LLM Support",
                    "Real-time Monitoring",
                    "Custom Workflows",
                    "Priority Support",
                    "SLA Monitoring"
                ],
                duration_months=12
            ),
            "enterprise": LicensePlan(
                plan_id="enterprise",
                name="TicketZero AI Enterprise",
                price=7500.00,  # $7.5K for enterprise
                max_clients=50,
                max_tickets_per_month=25000,
                features=[
                    "AI Ticket Processing",
                    "Atera Integration",
                    "Enterprise Dashboard",
                    "Multi-LLM Support",
                    "Real-time Monitoring",
                    "Custom Workflows",
                    "Advanced Analytics",
                    "White Label Branding",
                    "24/7 Premium Support",
                    "SLA Guarantees",
                    "API Access",
                    "Custom Integrations"
                ],
                duration_months=12
            )
        }

    def generate_license_key(self, plan_id: str, customer_name: str, customer_email: str) -> str:
        """Generate secure license key"""
        plan = self.license_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan ID: {plan_id}")

        # Create unique identifier
        unique_data = f"{customer_email}:{plan_id}:{time.time()}:{uuid.uuid4()}"

        # Create license key hash
        license_hash = hashlib.sha256(unique_data.encode()).hexdigest()[:16].upper()

        # Format as professional license key
        license_key = f"TZ-{plan_id.upper()[:3]}-{license_hash[:4]}-{license_hash[4:8]}-{license_hash[8:12]}-{license_hash[12:16]}"

        return license_key

    def create_license(self, plan_id: str, customer_name: str, customer_email: str,
                      custom_duration_months: Optional[int] = None) -> LicenseInfo:
        """Create new license"""
        plan = self.license_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan ID: {plan_id}")

        license_key = self.generate_license_key(plan_id, customer_name, customer_email)

        duration = custom_duration_months or plan.duration_months
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=duration * 30)

        license_info = LicenseInfo(
            license_key=license_key,
            customer_name=customer_name,
            customer_email=customer_email,
            license_type=plan_id,
            max_clients=plan.max_clients,
            max_tickets_per_month=plan.max_tickets_per_month,
            issue_date=issue_date,
            expiry_date=expiry_date,
            features=plan.features.copy(),
            price_paid=plan.price,
            is_active=True,
            activation_count=0,
            max_activations=3
        )

        logger.info(f"Created license {license_key} for {customer_name} ({customer_email})")
        return license_info

    def save_license(self, license_info: LicenseInfo):
        """Save license to encrypted file"""
        try:
            # Convert to dictionary
            license_data = asdict(license_info)

            # Convert datetime objects to ISO format
            license_data['issue_date'] = license_info.issue_date.isoformat()
            license_data['expiry_date'] = license_info.expiry_date.isoformat()

            # Encrypt license data
            fernet = Fernet(self.secret_key)
            license_json = json.dumps(license_data, indent=2)
            encrypted_data = fernet.encrypt(license_json.encode())

            # Save to file
            with open(self.license_file, 'wb') as f:
                f.write(encrypted_data)

            self.current_license = license_info
            logger.info(f"License saved: {license_info.license_key}")

        except Exception as e:
            logger.error(f"Error saving license: {e}")
            raise

    def load_license(self) -> Optional[LicenseInfo]:
        """Load license from encrypted file"""
        if not os.path.exists(self.license_file):
            return None

        try:
            # Read encrypted file
            with open(self.license_file, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt license data
            fernet = Fernet(self.secret_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())

            # Convert datetime strings back to datetime objects
            license_data['issue_date'] = datetime.fromisoformat(license_data['issue_date'])
            license_data['expiry_date'] = datetime.fromisoformat(license_data['expiry_date'])

            # Create LicenseInfo object
            self.current_license = LicenseInfo(**license_data)
            logger.info(f"License loaded: {self.current_license.license_key}")
            return self.current_license

        except Exception as e:
            logger.error(f"Error loading license: {e}")
            return None

    def validate_license(self) -> Tuple[bool, str]:
        """Validate current license"""
        if not self.current_license:
            return False, "No license found"

        # Check if license is active
        if not self.current_license.is_active:
            return False, "License is deactivated"

        # Check expiry date
        if datetime.now() > self.current_license.expiry_date:
            return False, f"License expired on {self.current_license.expiry_date.strftime('%Y-%m-%d')}"

        # Check activation count
        if self.current_license.activation_count >= self.current_license.max_activations:
            return False, f"Maximum activations ({self.current_license.max_activations}) exceeded"

        return True, "License valid"

    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """Activate license with key"""
        # For demo purposes, we'll create a license for the provided key
        # In production, this would validate against a license server

        # Parse license key to determine plan
        if license_key.startswith("TZ-STA"):
            plan_id = "starter"
        elif license_key.startswith("TZ-PRO"):
            plan_id = "professional"
        elif license_key.startswith("TZ-ENT"):
            plan_id = "enterprise"
        else:
            return False, "Invalid license key format"

        try:
            # Create license for the key
            license_info = self.create_license(
                plan_id=plan_id,
                customer_name="Licensed User",
                customer_email="user@company.com"
            )
            license_info.license_key = license_key
            license_info.activation_count = 1

            # Save the activated license
            self.save_license(license_info)

            return True, f"License activated successfully: {plan_id.title()} Plan"

        except Exception as e:
            return False, f"Activation failed: {str(e)}"

    def get_license_status(self) -> Dict:
        """Get comprehensive license status"""
        if not self.current_license:
            return {
                "status": "unlicensed",
                "message": "No valid license found",
                "trial_available": True,
                "days_remaining": 0,
                "features_available": [],
                "upgrade_required": True
            }

        is_valid, message = self.validate_license()
        days_remaining = (self.current_license.expiry_date - datetime.now()).days

        return {
            "status": "licensed" if is_valid else "invalid",
            "message": message,
            "license_key": self.current_license.license_key,
            "customer_name": self.current_license.customer_name,
            "license_type": self.current_license.license_type,
            "plan_name": "Trial License" if self.current_license.license_type == "trial" else self.license_plans[self.current_license.license_type].name,
            "days_remaining": max(0, days_remaining),
            "expiry_date": self.current_license.expiry_date.strftime('%Y-%m-%d'),
            "max_clients": self.current_license.max_clients,
            "max_tickets_per_month": self.current_license.max_tickets_per_month,
            "features_available": self.current_license.features,
            "price_paid": self.current_license.price_paid,
            "activation_count": self.current_license.activation_count,
            "max_activations": self.current_license.max_activations,
            "upgrade_available": self.current_license.license_type != "enterprise"
        }

    def check_feature_access(self, feature: str) -> bool:
        """Check if current license includes specific feature"""
        if not self.current_license:
            return False

        is_valid, _ = self.validate_license()
        if not is_valid:
            return False

        return feature in self.current_license.features

    def get_usage_limits(self) -> Dict:
        """Get current usage limits"""
        if not self.current_license:
            return {
                "max_clients": 1,
                "max_tickets_per_month": 50,
                "features_limited": True
            }

        return {
            "max_clients": self.current_license.max_clients,
            "max_tickets_per_month": self.current_license.max_tickets_per_month,
            "features_limited": False
        }

    def generate_trial_license(self, customer_email: str, days: int = 30) -> LicenseInfo:
        """Generate trial license"""
        trial_license = LicenseInfo(
            license_key="TZ-TRIAL-" + str(uuid.uuid4())[:8].upper(),
            customer_name="Trial User",
            customer_email=customer_email,
            license_type="trial",
            max_clients=2,
            max_tickets_per_month=100,
            issue_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=days),
            features=[
                "AI Ticket Processing",
                "Atera Integration",
                "Basic Dashboard"
            ],
            price_paid=0.0,
            is_active=True,
            activation_count=1,
            max_activations=1
        )

        self.save_license(trial_license)
        return trial_license

    def get_pricing_info(self) -> Dict:
        """Get pricing information for all plans"""
        pricing = {}
        for plan_id, plan in self.license_plans.items():
            pricing[plan_id] = {
                "name": plan.name,
                "price": plan.price,
                "price_formatted": f"${plan.price:,.2f}",
                "duration_months": plan.duration_months,
                "max_clients": plan.max_clients,
                "max_tickets_per_month": plan.max_tickets_per_month,
                "features": plan.features,
                "recommended": plan_id == "professional"
            }
        return pricing

# Global license manager instance
license_manager = LicenseManager()