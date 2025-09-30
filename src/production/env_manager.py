#!/usr/bin/env python3
"""
Environment Manager for TicketZero AI
Handles reading and writing environment variables to .env files
"""

import os
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EnvManager:
    """Manages environment variables and .env file operations"""

    def __init__(self, env_file_path: str = ".env"):
        self.env_file_path = env_file_path
        self.env_vars = {}
        self.load_env_vars()

    def load_env_vars(self):
        """Load environment variables from .env file"""
        self.env_vars = {}

        if not os.path.exists(self.env_file_path):
            logger.warning(f"Environment file {self.env_file_path} not found")
            return

        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]

                        self.env_vars[key] = value

            logger.info(f"Loaded {len(self.env_vars)} environment variables from {self.env_file_path}")

        except Exception as e:
            logger.error(f"Error loading environment file: {e}")

    def get_env_var(self, key: str, default: str = "") -> str:
        """Get environment variable value"""
        return self.env_vars.get(key, default)

    def set_env_var(self, key: str, value: str):
        """Set environment variable value"""
        self.env_vars[key] = value

    def update_env_vars(self, updates: Dict[str, str]):
        """Update multiple environment variables"""
        for key, value in updates.items():
            self.env_vars[key] = value

    def save_env_file(self):
        """Save environment variables back to .env file"""
        try:
            # Read existing file to preserve comments and structure
            existing_lines = []
            if os.path.exists(self.env_file_path):
                with open(self.env_file_path, 'r', encoding='utf-8') as f:
                    existing_lines = f.readlines()

            # Process existing lines and update values
            updated_lines = []
            updated_keys = set()

            for line in existing_lines:
                stripped = line.strip()

                # Keep comments and empty lines
                if not stripped or stripped.startswith('#'):
                    updated_lines.append(line)
                    continue

                # Update existing key=value pairs
                if '=' in stripped:
                    key = stripped.split('=', 1)[0].strip()
                    if key in self.env_vars:
                        value = self.env_vars[key]
                        # Quote value if it contains spaces or special characters
                        if ' ' in value or any(c in value for c in ['$', '"', "'", '\\', '`']):
                            value = f'"{value}"'
                        updated_lines.append(f"{key}={value}\n")
                        updated_keys.add(key)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            # Add new environment variables that weren't in the original file
            for key, value in self.env_vars.items():
                if key not in updated_keys:
                    # Quote value if it contains spaces or special characters
                    if ' ' in value or any(c in value for c in ['$', '"', "'", '\\', '`']):
                        value = f'"{value}"'
                    updated_lines.append(f"{key}={value}\n")

            # Write back to file
            with open(self.env_file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            logger.info(f"Successfully saved environment variables to {self.env_file_path}")

        except Exception as e:
            logger.error(f"Error saving environment file: {e}")
            raise

    def get_api_config(self) -> Dict[str, Dict[str, str]]:
        """Get API configuration from environment variables"""
        api_config = {
            "atera": {
                "api_key": self.get_env_var("ATERA_API_KEY"),
                "api_url": self.get_env_var("ATERA_API_URL", "https://app.atera.com/api/v3")
            },
            "openai": {
                "api_key": self.get_env_var("OPENAI_API_KEY"),
                "model": self.get_env_var("OPENAI_MODEL", "gpt-3.5-turbo")
            },
            "azure_openai": {
                "api_key": self.get_env_var("AZURE_OPENAI_API_KEY"),
                "endpoint": self.get_env_var("AZURE_OPENAI_ENDPOINT"),
                "deployment": self.get_env_var("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")
            },
            "lmstudio": {
                "endpoint": self.get_env_var("LMSTUDIO_URL", "http://127.0.0.1:1234/v1"),
                "model": self.get_env_var("LMSTUDIO_MODEL", "phi-3-mini-4k-instruct")
            },
            "email": {
                "smtp_host": self.get_env_var("SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": self.get_env_var("SMTP_PORT", "587"),
                "smtp_user": self.get_env_var("SMTP_USER"),
                "smtp_pass": self.get_env_var("SMTP_PASS")
            }
        }

        return api_config

    def update_api_config(self, api_config: Dict[str, Dict[str, str]]):
        """Update API configuration in environment variables"""
        updates = {}

        # Flatten API config to environment variables
        for provider, config in api_config.items():
            if provider == "atera":
                if config.get("api_key"):
                    updates["ATERA_API_KEY"] = config["api_key"]
                if config.get("api_url"):
                    updates["ATERA_API_URL"] = config["api_url"]

            elif provider == "openai":
                if config.get("api_key"):
                    updates["OPENAI_API_KEY"] = config["api_key"]
                if config.get("model"):
                    updates["OPENAI_MODEL"] = config["model"]

            elif provider == "azure_openai":
                if config.get("api_key"):
                    updates["AZURE_OPENAI_API_KEY"] = config["api_key"]
                if config.get("endpoint"):
                    updates["AZURE_OPENAI_ENDPOINT"] = config["endpoint"]
                if config.get("deployment"):
                    updates["AZURE_OPENAI_DEPLOYMENT"] = config["deployment"]

            elif provider == "lmstudio":
                if config.get("endpoint"):
                    updates["LMSTUDIO_URL"] = config["endpoint"]
                if config.get("model"):
                    updates["LMSTUDIO_MODEL"] = config["model"]

            elif provider == "email":
                if config.get("smtp_host"):
                    updates["SMTP_HOST"] = config["smtp_host"]
                if config.get("smtp_port"):
                    updates["SMTP_PORT"] = config["smtp_port"]
                if config.get("smtp_user"):
                    updates["SMTP_USER"] = config["smtp_user"]
                if config.get("smtp_pass"):
                    updates["SMTP_PASS"] = config["smtp_pass"]

        # Update environment variables
        self.update_env_vars(updates)

    def validate_api_config(self) -> Dict[str, List[str]]:
        """Validate API configuration and return any issues"""
        issues = {
            "missing": [],
            "invalid": [],
            "warnings": []
        }

        # Check required API keys
        required_keys = [
            ("ATERA_API_KEY", "Atera API key is required for ticket processing"),
        ]

        optional_keys = [
            ("OPENAI_API_KEY", "OpenAI API key for AI processing"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI API key for AI processing"),
            ("AZURE_OPENAI_ENDPOINT", "Azure OpenAI endpoint URL"),
        ]

        # Check required keys
        for key, description in required_keys:
            value = self.get_env_var(key)
            if not value or value == f"your-{key.lower().replace('_', '-')}-here":
                issues["missing"].append(f"{key}: {description}")

        # Check optional keys for warnings
        for key, description in optional_keys:
            value = self.get_env_var(key)
            if not value or value == f"your-{key.lower().replace('_', '-')}-here":
                issues["warnings"].append(f"{key}: {description}")

        # Validate URL formats
        url_keys = ["ATERA_API_URL", "AZURE_OPENAI_ENDPOINT", "LMSTUDIO_URL"]
        for key in url_keys:
            value = self.get_env_var(key)
            if value and not (value.startswith("http://") or value.startswith("https://")):
                issues["invalid"].append(f"{key}: Invalid URL format")

        return issues

# Global instance
env_manager = EnvManager()