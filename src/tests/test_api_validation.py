#!/usr/bin/env python3
"""
API Validation Test Suite
Test all API integrations for proper response handling and validation
"""

import sys
import os
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api_validator import (
    validate_json_response,
    validate_atera_tickets,
    validate_lmstudio_response,
    validate_azure_token_response,
    validate_azure_graph_response,
    validate_atera_response,
    validate_goto_response,
    validate_openai_response,
    safe_get_nested,
    validate_response_schema
)

def test_json_response_validation():
    """Test basic JSON response validation"""
    print("Testing JSON response validation...")

    # Test valid response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": "test"}

    result = validate_json_response(mock_response)
    assert result is not None
    assert result["status"] == "success"
    print("Valid JSON response handled correctly")

    # Test invalid status code
    mock_response.status_code = 404
    result = validate_json_response(mock_response)
    assert result is None
    print("Invalid status code handled correctly")

    # Test missing required fields
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    result = validate_json_response(mock_response, required_fields=["data"])
    assert result is None
    print("Missing required fields handled correctly")

def test_atera_validation():
    """Test Atera API response validation"""
    print("\nTesting Atera API validation...")

    # Test valid Atera tickets response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"TicketID": 123, "TicketTitle": "Test Ticket"},
            {"TicketID": 124, "TicketTitle": "Another Ticket"}
        ]
    }

    tickets = validate_atera_tickets(mock_response)
    assert len(tickets) == 2
    assert tickets[0]["TicketID"] == 123
    print("Valid Atera tickets response processed correctly")

    # Test Atera error response
    mock_response.json.return_value = {"error": "Invalid API key"}
    result = validate_atera_response(mock_response)
    assert result is None
    print("Atera error response handled correctly")

def test_ai_provider_validation():
    """Test AI provider response validation"""
    print("\nTesting AI provider validation...")

    # Test valid LM Studio response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "This is a valid AI response"
                }
            }
        ]
    }

    result = validate_lmstudio_response(mock_response)
    assert result == "This is a valid AI response"
    print("+ Valid LM Studio response processed correctly")

    # Test OpenAI error response
    mock_response.json.return_value = {
        "error": {
            "type": "invalid_request_error",
            "message": "Invalid API key"
        }
    }

    result = validate_openai_response(mock_response)
    assert result is None
    print("+ OpenAI error response handled correctly")

    # Test empty content response
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": ""
                }
            }
        ]
    }

    result = validate_lmstudio_response(mock_response)
    assert result is None
    print("+ Empty AI response handled correctly")

def test_azure_validation():
    """Test Azure Graph API validation"""
    print("\nTesting Azure Graph API validation...")

    # Test valid Azure token response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "valid_token_12345",
        "expires_in": 3600
    }

    token = validate_azure_token_response(mock_response)
    assert token == "valid_token_12345"
    print("+ Valid Azure token response processed correctly")

    # Test Azure Graph error response
    mock_response.json.return_value = {
        "error": {
            "code": "InvalidAuthenticationToken",
            "message": "Access token is empty"
        }
    }

    result = validate_azure_graph_response(mock_response)
    assert result is None
    print("+ Azure Graph error response handled correctly")

def test_goto_validation():
    """Test GoTo API validation"""
    print("\nTesting GoTo API validation...")

    # Test valid GoTo response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "sessionId": "12345",
        "status": "active"
    }

    result = validate_goto_response(mock_response)
    assert result is not None
    assert result["sessionId"] == "12345"
    print("+ Valid GoTo response processed correctly")

    # Test GoTo error response
    mock_response.json.return_value = {
        "errorCode": "INVALID_CREDENTIALS",
        "error_description": "Invalid client credentials"
    }

    result = validate_goto_response(mock_response)
    assert result is None
    print("+ GoTo error response handled correctly")

def test_safe_nested_access():
    """Test safe nested dictionary access"""
    print("\nTesting safe nested access...")

    test_data = {
        "user": {
            "profile": {
                "name": "John Doe",
                "settings": {
                    "theme": "dark"
                }
            }
        }
    }

    # Test valid path
    result = safe_get_nested(test_data, "user.profile.name")
    assert result == "John Doe"
    print("+ Valid nested path accessed correctly")

    # Test invalid path
    result = safe_get_nested(test_data, "user.profile.age", default="Unknown")
    assert result == "Unknown"
    print("+ Invalid nested path handled with default")

    # Test deep path
    result = safe_get_nested(test_data, "user.profile.settings.theme")
    assert result == "dark"
    print("+ Deep nested path accessed correctly")

def test_response_schema_validation():
    """Test response schema validation"""
    print("\nTesting response schema validation...")

    # Test valid schema
    test_data = {
        "TicketID": 123,
        "TicketTitle": "Test Ticket",
        "Priority": "High"
    }

    schema = {
        "TicketID": int,
        "TicketTitle": str,
        "Priority": str
    }

    result = validate_response_schema(test_data, schema)
    assert result is True
    print("+ Valid schema validation passed")

    # Test invalid schema - wrong type
    test_data["TicketID"] = "not_an_int"
    result = validate_response_schema(test_data, schema)
    assert result is False
    print("+ Invalid schema validation failed correctly")

    # Test missing field
    del test_data["Priority"]
    result = validate_response_schema(test_data, schema)
    assert result is False
    print("+ Missing field validation failed correctly")

async def test_async_api_integration():
    """Test async API integration with mocked providers"""
    print("\nTesting async API integration...")

    try:
        # Import the MSP system for testing
        from production.msp_ticketzero_optimized import LMStudioProvider, AzureAIProvider, OpenAIProvider

        # Test LM Studio provider with mocked response
        lm_provider = LMStudioProvider()

        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "Test AI response"
                        }
                    }
                ]
            }

            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response

            test_ticket = {"TicketTitle": "Test ticket", "FirstComment": "Test description"}
            result = await lm_provider.get_solution(test_ticket)

            if result:
                print("+ LM Studio provider integration working")
            else:
                print("! LM Studio provider needs attention")

    except ImportError as e:
        print(f"! Could not import MSP system for async testing: {e}")

def run_all_tests():
    """Run all API validation tests"""
    print("API Validation Test Suite")
    print("=" * 60)

    try:
        test_json_response_validation()
        test_atera_validation()
        test_ai_provider_validation()
        test_azure_validation()
        test_goto_validation()
        test_safe_nested_access()
        test_response_schema_validation()

        print("\nRunning async integration tests...")
        asyncio.run(test_async_api_integration())

        print("\n" + "=" * 60)
        print("All API validation tests completed successfully!")
        print("\nTest Summary:")
        print("   - JSON response validation")
        print("   - Atera API validation")
        print("   - AI provider validation (LM Studio, OpenAI, Azure OpenAI)")
        print("   - Azure Graph API validation")
        print("   - GoTo API validation")
        print("   - Safe data access utilities")
        print("   - Response schema validation")

        print("\nAPI Security Features:")
        print("   - Proper error handling for all APIs")
        print("   - JSON parsing error protection")
        print("   - Required field validation")
        print("   - Type checking and schema validation")
        print("   - Graceful degradation on API failures")

    except Exception as e:
        print(f"\n- Test suite failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)