#!/usr/bin/env python3
"""
API Response Validation Utilities
Secure validation for all API responses
"""

import json
import logging
from typing import Dict, Any, Optional, List

def validate_json_response(response, required_fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Safely validate and parse JSON API responses

    Args:
        response: requests.Response object
        required_fields: List of required fields in the JSON response

    Returns:
        Parsed JSON data or None if invalid
    """
    try:
        # Check status code first
        if not response.status_code in [200, 201]:
            logging.warning(f"API returned status {response.status_code}")
            return None

        # Parse JSON safely
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response: {e}")
            return None

        # Validate required fields
        if required_fields:
            for field in required_fields:
                if field not in data:
                    logging.error(f"Missing required field: {field}")
                    return None

        return data

    except Exception as e:
        logging.error(f"Response validation error: {e}")
        return None

def validate_atera_tickets(response) -> List[Dict[str, Any]]:
    """Validate Atera tickets API response"""
    data = validate_json_response(response, ['items'])
    if not data:
        return []

    tickets = data.get('items', [])
    if not isinstance(tickets, list):
        logging.error("Tickets data is not a list")
        return []

    # Validate each ticket has required fields
    validated_tickets = []
    for ticket in tickets:
        if isinstance(ticket, dict) and 'TicketID' in ticket:
            validated_tickets.append(ticket)
        else:
            logging.warning("Invalid ticket format detected")

    return validated_tickets

def validate_lmstudio_response(response) -> Optional[str]:
    """Validate LM Studio AI response"""
    data = validate_json_response(response, ['choices'])
    if not data:
        return None

    choices = data.get('choices', [])
    if not choices or not isinstance(choices, list):
        logging.error("No choices in LM Studio response")
        return None

    try:
        message = choices[0].get('message', {})
        content = message.get('content', '').strip()

        if not content:
            logging.error("Empty content in LM Studio response")
            return None

        return content

    except (IndexError, KeyError, AttributeError) as e:
        logging.error(f"Invalid LM Studio response structure: {e}")
        return None

def validate_azure_token_response(response) -> Optional[str]:
    """Validate Azure AD token response"""
    data = validate_json_response(response, ['access_token'])
    if not data:
        return None

    token = data.get('access_token')
    if not token or not isinstance(token, str):
        logging.error("Invalid access token in Azure response")
        return None

    return token

def validate_azure_graph_response(response) -> Optional[Dict[str, Any]]:
    """Validate Azure Graph API response"""
    data = validate_json_response(response)
    if not data:
        return None

    # Check for Azure error structure
    if 'error' in data:
        error_info = data['error']
        error_code = error_info.get('code', 'unknown')
        error_message = error_info.get('message', 'Unknown error')
        logging.error(f"Azure Graph API error {error_code}: {error_message}")
        return None

    return data

def validate_atera_response(response) -> Optional[Dict[str, Any]]:
    """Validate Atera API response"""
    data = validate_json_response(response)
    if not data:
        return None

    # Check for Atera error structure
    if 'error' in data or 'Error' in data:
        error_msg = data.get('error', data.get('Error', 'Unknown Atera error'))
        logging.error(f"Atera API error: {error_msg}")
        return None

    return data

def validate_goto_response(response) -> Optional[Dict[str, Any]]:
    """Validate GoTo API response"""
    data = validate_json_response(response)
    if not data:
        return None

    # Check for GoTo error structure
    if 'errorCode' in data or 'error_description' in data:
        error_code = data.get('errorCode', 'unknown')
        error_desc = data.get('error_description', data.get('description', 'Unknown GoTo error'))
        logging.error(f"GoTo API error {error_code}: {error_desc}")
        return None

    return data

def validate_openai_response(response) -> Optional[str]:
    """Validate OpenAI/Azure OpenAI response"""
    data = validate_json_response(response)
    if not data:
        return None

    # Check for OpenAI error structure
    if 'error' in data:
        error_info = data['error']
        error_type = error_info.get('type', 'unknown')
        error_message = error_info.get('message', 'Unknown OpenAI error')
        logging.error(f"OpenAI API error {error_type}: {error_message}")
        return None

    # Extract content from choices
    choices = data.get('choices', [])
    if not choices:
        logging.error("No choices in OpenAI response")
        return None

    try:
        message = choices[0].get('message', {})
        content = message.get('content', '').strip()

        if not content:
            logging.error("Empty content in OpenAI response")
            return None

        return content

    except (IndexError, KeyError, AttributeError) as e:
        logging.error(f"Invalid OpenAI response structure: {e}")
        return None

def safe_api_call(func, *args, max_retries: int = 3, **kwargs):
    """
    Safely execute API calls with retries and error handling

    Args:
        func: Function to call
        max_retries: Maximum number of retry attempts
        *args, **kwargs: Arguments for the function

    Returns:
        Function result or None if all retries failed
    """
    import time

    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logging.error(f"API call failed after {max_retries} attempts: {e}")
                return None

async def safe_async_api_call(func, *args, max_retries: int = 3, **kwargs):
    """
    Safely execute async API calls with retries and error handling
    """
    import asyncio

    for attempt in range(max_retries):
        try:
            result = await func(*args, **kwargs)
            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logging.warning(f"Async API call failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logging.error(f"Async API call failed after {max_retries} attempts: {e}")
                return None

def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values

    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., 'user.profile.name')
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    try:
        keys = path.split('.')
        result = data

        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return default

        return result

    except Exception:
        return default

def validate_response_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate response data against a simple schema

    Args:
        data: Data to validate
        schema: Schema with required fields and types

    Example schema:
        {
            'TicketID': int,
            'TicketTitle': str,
            'Priority': str
        }

    Returns:
        True if valid, False otherwise
    """
    try:
        for field, expected_type in schema.items():
            if field not in data:
                logging.error(f"Missing required field: {field}")
                return False

            if not isinstance(data[field], expected_type):
                logging.error(f"Field {field} should be {expected_type.__name__}, got {type(data[field]).__name__}")
                return False

        return True

    except Exception as e:
        logging.error(f"Schema validation error: {e}")
        return False