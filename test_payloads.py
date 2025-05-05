#!/usr/bin/env python3
"""
Test script to verify the payload formats and API endpoints for the Telegram Bot API vulnerability.
"""

import json

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "="*80)
    print(f"{title}")
    print("="*80)

def main():
    """Main function to display test payloads and API endpoints."""
    print_section("TELEGRAM BOT API VULNERABILITY TEST PAYLOADS")
    
    # Bot token (masked for security)
    token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    masked_token = f"{token[:5]}...{token[-5:]}"
    
    print(f"\nBot Token (masked): {masked_token}")
    
    # API Endpoints
    print("\nAPI Endpoints:")
    endpoints = {
        "getMe": "GET",
        "getMyCommands": "GET",
        "setMyCommands": "POST",
        "deleteMyCommands": "POST",
        "getUpdates": "GET",
        "sendMessage": "POST"
    }
    
    for endpoint, method in endpoints.items():
        print(f"  - {method} https://api.telegram.org/bot<token>/{endpoint}")
    
    # Test Payloads
    print("\nTest Payloads:")
    
    # 1. Set Commands
    commands = [
        {"command": "start", "description": "Start the bot"},
        {"command": "help", "description": "Get help"},
        {"command": "settings", "description": "Change settings"},
        {"command": "info", "description": "Get information"}
    ]
    
    set_commands_payload = {"commands": commands}
    print("\n1. Set Commands:")
    print(f"curl -X POST \"https://api.telegram.org/bot<token>/setMyCommands\" \\")
    print(f"     -H \"Content-Type: application/json\" \\")
    print(f"     -d '{json.dumps(set_commands_payload)}'")
    
    # 2. Remove Commands
    remove_commands_payload = {"commands": []}
    print("\n2. Remove Commands:")
    print(f"curl -X POST \"https://api.telegram.org/bot<token>/setMyCommands\" \\")
    print(f"     -H \"Content-Type: application/json\" \\")
    print(f"     -d '{json.dumps(remove_commands_payload)}'")
    
    # Expected Responses
    print("\nExpected Responses:")
    
    # Success Response
    success_response = {"ok": True, "result": True}
    print("\n1. Success Response (HTTP 200 OK):")
    print(json.dumps(success_response, indent=2))
    
    # Error Response
    error_response = {
        "ok": False,
        "error_code": 400,
        "description": "Bad Request: permission denied"
    }
    print("\n2. Error Response (HTTP 400 Bad Request):")
    print(json.dumps(error_response, indent=2))
    
    # Exploitation Steps
    print_section("EXPLOITATION STEPS")
    
    steps = [
        "1. Create a bot using BotFather and note the token",
        "2. Set commands for the bot using setMyCommands",
        "3. Transfer the bot to another user using BotFather",
        "4. As the former owner, try to remove commands (should succeed)",
        "5. As the former owner, try to add commands back (should fail with permission error)",
        "6. Document the responses and timestamps for evidence"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print_section("END OF TEST PAYLOADS")

if __name__ == "__main__":
    main()
