#!/usr/bin/env python3
"""
Telegram Bot API Vulnerability - Endpoint Enumeration

This script automates the process of testing various Telegram Bot API endpoints
to identify which ones might be vulnerable to the permission issue after bot ownership transfer.
"""

import os
import json
import time
import logging
import requests
import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configure logging
logging_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TelegramEndpointEnumerator:
    """Class to handle the Telegram Bot API endpoint enumeration."""
    
    def __init__(self):
        """Initialize the enumerator with configuration from environment variables."""
        self.user_a_bot_token = os.getenv("USER_A_BOT_TOKEN")
        self.user_a_username = os.getenv("USER_A_TELEGRAM_USERNAME")
        self.user_b_username = os.getenv("USER_B_TELEGRAM_USERNAME")
        
        # Validate required environment variables
        self._validate_env_vars()
        
        # Base URL for Telegram Bot API
        self.api_base_url = f"https://api.telegram.org/bot{self.user_a_bot_token}"
        
        # Store API responses for reporting
        self.responses = {}
        
        # List of endpoints to test
        self.endpoints = [
            # Bot configuration endpoints
            {"method": "setMyCommands", "params": {"commands": []}, "http_method": "POST"},
            {"method": "deleteMyCommands", "params": {}, "http_method": "POST"},
            {"method": "setMyName", "params": {"name": "Test Bot"}, "http_method": "POST"},
            {"method": "setMyDescription", "params": {"description": "Test description"}, "http_method": "POST"},
            {"method": "setMyShortDescription", "params": {"short_description": "Test short description"}, "http_method": "POST"},
            {"method": "setChatMenuButton", "params": {"menu_button": {"type": "default"}}, "http_method": "POST"},
            {"method": "setMyDefaultAdministratorRights", "params": {"rights": {"can_manage_chat": True, "can_post_messages": True}}, "http_method": "POST"},
            
            # Webhook configuration endpoints
            {"method": "setWebhook", "params": {"url": ""}, "http_method": "POST"},
            {"method": "deleteWebhook", "params": {}, "http_method": "POST"},
            
            # Read-only endpoints (should always work)
            {"method": "getMe", "params": {}, "http_method": "GET"},
            {"method": "getMyCommands", "params": {}, "http_method": "GET"},
            {"method": "getMyName", "params": {}, "http_method": "GET"},
            {"method": "getMyDescription", "params": {}, "http_method": "GET"},
            {"method": "getMyShortDescription", "params": {}, "http_method": "GET"},
            {"method": "getChatMenuButton", "params": {}, "http_method": "GET"},
            {"method": "getMyDefaultAdministratorRights", "params": {}, "http_method": "GET"},
            {"method": "getWebhookInfo", "params": {}, "http_method": "GET"},
        ]
        
    def _validate_env_vars(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            ("USER_A_BOT_TOKEN", self.user_a_bot_token),
            ("USER_A_TELEGRAM_USERNAME", self.user_a_username),
            ("USER_B_TELEGRAM_USERNAME", self.user_b_username)
        ]
        
        missing_vars = [var_name for var_name, var_value in required_vars if not var_value]
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def test_endpoint(self, endpoint):
        """Test a specific API endpoint."""
        method = endpoint["method"]
        params = endpoint["params"]
        http_method = endpoint["http_method"]
        
        logger.info(f"{Fore.BLUE}Testing endpoint: {method}")
        
        url = f"{self.api_base_url}/{method}"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            if http_method == "GET":
                response = requests.get(url, params=params)
            else:  # POST
                response = requests.post(url, json=params)
            
            self.responses[method] = {
                "timestamp": timestamp,
                "status_code": response.status_code,
                "response": response.json() if response.text else {},
                "params": params,
                "http_method": http_method
            }
            
            status = "SUCCESS" if response.status_code == 200 and response.json().get("ok") else "FAILED"
            color = Fore.GREEN if status == "SUCCESS" else Fore.RED
            
            logger.info(f"{color}[{status}] {method} - Status Code: {response.status_code}")
            logger.debug(f"Response: {json.dumps(response.json() if response.text else {}, indent=2)}")
            
            return status == "SUCCESS"
            
        except Exception as e:
            logger.error(f"{Fore.RED}Error testing endpoint {method}: {str(e)}")
            self.responses[method] = {
                "timestamp": timestamp,
                "error": str(e),
                "params": params,
                "http_method": http_method
            }
            return False
    
    def run_tests(self):
        """Run tests for all endpoints."""
        logger.info(f"{Fore.CYAN}Starting Telegram Bot API endpoint enumeration...")
        
        results = {
            "success": [],
            "failed": []
        }
        
        for endpoint in self.endpoints:
            success = self.test_endpoint(endpoint)
            if success:
                results["success"].append(endpoint["method"])
            else:
                results["failed"].append(endpoint["method"])
            
            # Add a small delay between requests to avoid rate limiting
            time.sleep(0.5)
        
        logger.info(f"{Fore.CYAN}Endpoint enumeration completed.")
        logger.info(f"{Fore.GREEN}Successful endpoints: {', '.join(results['success'])}")
        logger.info(f"{Fore.RED}Failed endpoints: {', '.join(results['failed'])}")
        
        return results
    
    def generate_report(self):
        """Generate a report of the endpoint enumeration."""
        logger.info(f"{Fore.BLUE}Generating endpoint enumeration report...")
        
        report = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bot_token": f"{self.user_a_bot_token[:5]}...{self.user_a_bot_token[-5:]}",
            "user_a_username": self.user_a_username,
            "user_b_username": self.user_b_username,
            "endpoints": self.responses
        }
        
        # Save report to file
        with open("endpoint_enumeration_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"{Fore.GREEN}Report saved to endpoint_enumeration_report.json")
        
        # Generate a markdown report
        self._generate_markdown_report(report)
        
        return report
    
    def _generate_markdown_report(self, report):
        """Generate a markdown report of the endpoint enumeration."""
        logger.info(f"{Fore.BLUE}Generating markdown report...")
        
        with open("Endpoint_Enumeration_Report.md", "w") as f:
            f.write("# Telegram Bot API Vulnerability - Endpoint Enumeration Report\n\n")
            f.write(f"**Date:** {report['timestamp']}\n")
            f.write(f"**Bot Token (masked):** {report['bot_token']}\n")
            f.write(f"**User A Username:** {report['user_a_username']}\n")
            f.write(f"**User B Username:** {report['user_b_username']}\n\n")
            
            f.write("## Endpoint Test Results\n\n")
            f.write("| Endpoint | HTTP Method | Status Code | Result |\n")
            f.write("|----------|-------------|-------------|--------|\n")
            
            for method, data in report["endpoints"].items():
                status_code = data.get("status_code", "N/A")
                result = "SUCCESS" if status_code == 200 and data.get("response", {}).get("ok") else "FAILED"
                http_method = data.get("http_method", "N/A")
                
                f.write(f"| {method} | {http_method} | {status_code} | {result} |\n")
            
            f.write("\n## Detailed Results\n\n")
            
            for method, data in report["endpoints"].items():
                f.write(f"### {method}\n\n")
                f.write(f"**HTTP Method:** {data.get('http_method', 'N/A')}\n")
                f.write(f"**Timestamp:** {data.get('timestamp', 'N/A')}\n")
                f.write(f"**Parameters:** `{json.dumps(data.get('params', {}))}`\n")
                
                if "status_code" in data:
                    f.write(f"**Status Code:** {data['status_code']}\n")
                    f.write(f"**Response:** ```json\n{json.dumps(data.get('response', {}), indent=2)}\n```\n\n")
                else:
                    f.write(f"**Error:** {data.get('error', 'Unknown error')}\n\n")
            
            f.write("## Conclusion\n\n")
            f.write("This report shows which Telegram Bot API endpoints are accessible after bot ownership transfer. ")
            f.write("Endpoints that return a successful response (200 OK) are potentially vulnerable to the permission issue.\n\n")
            
            f.write("### Potentially Vulnerable Endpoints\n\n")
            vulnerable = [method for method, data in report["endpoints"].items() 
                         if data.get("status_code") == 200 and data.get("response", {}).get("ok")]
            
            if vulnerable:
                for method in vulnerable:
                    f.write(f"- `{method}`\n")
            else:
                f.write("No potentially vulnerable endpoints found.\n")
        
        logger.info(f"{Fore.GREEN}Markdown report saved to Endpoint_Enumeration_Report.md")

def simulate_ownership_transfer():
    """Simulate the ownership transfer process."""
    logger.info(f"{Fore.YELLOW}SIMULATION: Simulating bot ownership transfer...")
    logger.info(f"{Fore.YELLOW}In a real scenario, you would transfer the bot using BotFather.")
    
    # Simulate a delay for the transfer process
    time.sleep(2)
    
    logger.info(f"{Fore.GREEN}SIMULATION: Bot ownership transfer simulated.")
    return True

def main():
    """Main function to run the endpoint enumeration."""
    print(f"{Fore.CYAN}Telegram Bot API Vulnerability - Endpoint Enumeration")
    print(f"{Fore.CYAN}===================================================\n")
    
    try:
        # Initialize the enumerator
        enumerator = TelegramEndpointEnumerator()
        
        # Run tests before ownership transfer
        logger.info(f"{Fore.YELLOW}Running tests BEFORE ownership transfer...")
        before_results = enumerator.run_tests()
        
        # Simulate ownership transfer
        print(f"\n{Fore.YELLOW}SIMULATION: Bot ownership transfer")
        print(f"{Fore.YELLOW}In a real scenario, you would transfer the bot using BotFather.")
        
        input(f"\n{Fore.YELLOW}Press Enter to simulate the bot ownership transfer...")
        
        simulate_ownership_transfer()
        
        # Run tests after ownership transfer
        logger.info(f"{Fore.YELLOW}Running tests AFTER ownership transfer...")
        after_results = enumerator.run_tests()
        
        # Generate report
        enumerator.generate_report()
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
