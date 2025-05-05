#!/usr/bin/env python3
"""
Telegram Bot API Tester

A utility script to manually test various Telegram Bot API endpoints.
This can be used to verify the vulnerability or test other API endpoints.
"""

import os
import json
import argparse
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

def get_token():
    """Get the bot token from environment variables or command line."""
    return os.getenv("USER_A_BOT_TOKEN")

def make_request(method, endpoint, data=None, token=None):
    """Make a request to the Telegram Bot API."""
    if token is None:
        token = get_token()
    
    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    
    print(f"{Fore.BLUE}Making {method} request to {endpoint}...")
    print(f"{Fore.BLUE}URL: {url}")
    
    if data:
        print(f"{Fore.BLUE}Data: {json.dumps(data, indent=2)}")
    
    if method.upper() == "GET":
        response = requests.get(url, params=data)
    elif method.upper() == "POST":
        response = requests.post(url, json=data)
    else:
        print(f"{Fore.RED}Unsupported method: {method}")
        return None
    
    print(f"{Fore.GREEN}Status Code: {response.status_code}")
    
    try:
        json_response = response.json()
        print(f"{Fore.GREEN}Response: {json.dumps(json_response, indent=2)}")
        return json_response
    except json.JSONDecodeError:
        print(f"{Fore.RED}Failed to decode JSON response: {response.text}")
        return None

def get_me(token=None):
    """Get information about the bot."""
    return make_request("GET", "getMe", token=token)

def get_commands(token=None):
    """Get the current commands of the bot."""
    return make_request("GET", "getMyCommands", token=token)

def set_commands(commands, token=None):
    """Set commands for the bot."""
    data = {"commands": commands}
    return make_request("POST", "setMyCommands", data, token)

def remove_commands(token=None):
    """Remove all commands from the bot."""
    data = {"commands": []}
    return make_request("POST", "setMyCommands", data, token)

def get_updates(token=None):
    """Get updates from the bot."""
    return make_request("GET", "getUpdates", token=token)

def send_message(chat_id, text, token=None):
    """Send a message using the bot."""
    data = {
        "chat_id": chat_id,
        "text": text
    }
    return make_request("POST", "sendMessage", data, token)

def main():
    """Main function to run the API tester."""
    parser = argparse.ArgumentParser(description="Telegram Bot API Tester")
    parser.add_argument("--token", help="Bot token (overrides environment variable)")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET", help="HTTP method")
    parser.add_argument("--endpoint", required=True, help="API endpoint (e.g., getMe, getMyCommands)")
    parser.add_argument("--data", help="JSON data for the request")
    
    args = parser.parse_args()
    
    token = args.token if args.token else get_token()
    
    if not token:
        print(f"{Fore.RED}No bot token provided. Set USER_A_BOT_TOKEN environment variable or use --token.")
        return
    
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Invalid JSON data: {args.data}")
            return
    
    make_request(args.method, args.endpoint, data, token)

if __name__ == "__main__":
    main()
