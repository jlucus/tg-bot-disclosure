#!/usr/bin/env python3
"""
Telegram Bot API Vulnerability - Permission Pattern Testing

This script tests the specific vulnerability pattern where a former bot owner
can remove settings but not add them back after ownership transfer.
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

class TelegramPermissionTester:
    """Class to test the permission pattern in Telegram Bot API."""
    
    def __init__(self):
        """Initialize the tester with configuration from environment variables."""
        self.user_a_bot_token = os.getenv("USER_A_BOT_TOKEN")
        self.user_a_username = os.getenv("USER_A_TELEGRAM_USERNAME")
        self.user_b_username = os.getenv("USER_B_TELEGRAM_USERNAME")
        
        # Validate required environment variables
        self._validate_env_vars()
        
        # Base URL for Telegram Bot API
        self.api_base_url = f"https://api.telegram.org/bot{self.user_a_bot_token}"
        
        # Store API responses for reporting
        self.responses = {}
        
        # Test cases for the permission pattern
        self.test_cases = [
            {
                "name": "Bot Commands",
                "add_endpoint": "setMyCommands",
                "add_params": {"commands": [{"command": "test", "description": "Test command"}]},
                "remove_endpoint": "setMyCommands",
                "remove_params": {"commands": []},
                "get_endpoint": "getMyCommands",
                "get_params": {}
            },
            {
                "name": "Bot Name",
                "add_endpoint": "setMyName",
                "add_params": {"name": "Test Bot Name"},
                "remove_endpoint": "setMyName",
                "remove_params": {"name": ""},
                "get_endpoint": "getMyName",
                "get_params": {}
            },
            {
                "name": "Bot Description",
                "add_endpoint": "setMyDescription",
                "add_params": {"description": "Test bot description with detailed information"},
                "remove_endpoint": "setMyDescription",
                "remove_params": {"description": ""},
                "get_endpoint": "getMyDescription",
                "get_params": {}
            },
            {
                "name": "Bot Short Description",
                "add_endpoint": "setMyShortDescription",
                "add_params": {"short_description": "Test short description"},
                "remove_endpoint": "setMyShortDescription",
                "remove_params": {"short_description": ""},
                "get_endpoint": "getMyShortDescription",
                "get_params": {}
            }
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
    
    def make_request(self, endpoint, params=None, http_method="POST"):
        """Make a request to the Telegram Bot API."""
        url = f"{self.api_base_url}/{endpoint}"
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            if http_method == "GET":
                response = requests.get(url, params=params)
            else:  # POST
                response = requests.post(url, json=params)
            
            result = {
                "timestamp": timestamp,
                "status_code": response.status_code,
                "response": response.json() if response.text else {},
                "params": params,
                "http_method": http_method
            }
            
            success = response.status_code == 200 and response.json().get("ok")
            
            return success, result
            
        except Exception as e:
            logger.error(f"Error making request to {endpoint}: {str(e)}")
            return False, {
                "timestamp": timestamp,
                "error": str(e),
                "params": params,
                "http_method": http_method
            }
    
    def test_permission_pattern(self, test_case, after_transfer=False):
        """Test the permission pattern for a specific test case."""
        name = test_case["name"]
        add_endpoint = test_case["add_endpoint"]
        add_params = test_case["add_params"]
        remove_endpoint = test_case["remove_endpoint"]
        remove_params = test_case["remove_params"]
        get_endpoint = test_case["get_endpoint"]
        get_params = test_case["get_params"]
        
        phase = "AFTER TRANSFER" if after_transfer else "BEFORE TRANSFER"
        logger.info(f"{Fore.CYAN}Testing {name} {phase}")
        
        # Step 1: Add setting
        logger.info(f"{Fore.BLUE}Step 1: Adding {name}")
        add_success, add_result = self.make_request(add_endpoint, add_params)
        
        status = "SUCCESS" if add_success else "FAILED"
        color = Fore.GREEN if add_success else Fore.RED
        logger.info(f"{color}[{status}] Add {name}")
        
        # Step 2: Verify setting was added
        logger.info(f"{Fore.BLUE}Step 2: Verifying {name} was added")
        get_success, get_result = self.make_request(get_endpoint, get_params, "GET")
        
        if get_success:
            logger.info(f"{Fore.GREEN}[SUCCESS] Get {name}")
            logger.info(f"{Fore.GREEN}Current value: {json.dumps(get_result['response'].get('result', {}))}")
        else:
            logger.info(f"{Fore.RED}[FAILED] Get {name}")
        
        # Step 3: Remove setting
        logger.info(f"{Fore.BLUE}Step 3: Removing {name}")
        remove_success, remove_result = self.make_request(remove_endpoint, remove_params)
        
        status = "SUCCESS" if remove_success else "FAILED"
        color = Fore.GREEN if remove_success else Fore.RED
        logger.info(f"{color}[{status}] Remove {name}")
        
        # Step 4: Verify setting was removed
        logger.info(f"{Fore.BLUE}Step 4: Verifying {name} was removed")
        get_success, get_result = self.make_request(get_endpoint, get_params, "GET")
        
        if get_success:
            logger.info(f"{Fore.GREEN}[SUCCESS] Get {name}")
            logger.info(f"{Fore.GREEN}Current value: {json.dumps(get_result['response'].get('result', {}))}")
        else:
            logger.info(f"{Fore.RED}[FAILED] Get {name}")
        
        # Store results
        key = f"{name.lower().replace(' ', '_')}_{phase.lower().replace(' ', '_')}"
        self.responses[key] = {
            "add": add_result,
            "get_after_add": get_result,
            "remove": remove_result,
            "get_after_remove": get_result
        }
        
        return {
            "add_success": add_success,
            "remove_success": remove_success,
            "get_success": get_success
        }
    
    def run_tests(self):
        """Run all permission pattern tests."""
        logger.info(f"{Fore.CYAN}Starting Telegram Bot API permission pattern tests...")
        
        # Run tests before ownership transfer
        logger.info(f"{Fore.YELLOW}Running tests BEFORE ownership transfer...")
        before_results = {}
        for test_case in self.test_cases:
            before_results[test_case["name"]] = self.test_permission_pattern(test_case)
            time.sleep(1)  # Add a small delay between tests
        
        # Simulate ownership transfer
        print(f"\n{Fore.YELLOW}SIMULATION: Bot ownership transfer")
        print(f"{Fore.YELLOW}In a real scenario, you would transfer the bot using BotFather.")
        
        input(f"\n{Fore.YELLOW}Press Enter to simulate the bot ownership transfer...")
        
        logger.info(f"{Fore.YELLOW}SIMULATION: Simulating bot ownership transfer...")
        logger.info(f"{Fore.YELLOW}In a real scenario, you would transfer the bot from {self.user_a_username} to {self.user_b_username} using BotFather.")
        
        # Simulate a delay for the transfer process
        time.sleep(2)
        
        logger.info(f"{Fore.GREEN}SIMULATION: Bot ownership transfer simulated.")
        
        # Run tests after ownership transfer
        logger.info(f"{Fore.YELLOW}Running tests AFTER ownership transfer...")
        after_results = {}
        for test_case in self.test_cases:
            after_results[test_case["name"]] = self.test_permission_pattern(test_case, True)
            time.sleep(1)  # Add a small delay between tests
        
        # Generate report
        self.generate_report(before_results, after_results)
        
        logger.info(f"{Fore.CYAN}Permission pattern tests completed.")
        
        return before_results, after_results
    
    def generate_report(self, before_results, after_results):
        """Generate a report of the permission pattern tests."""
        logger.info(f"{Fore.BLUE}Generating permission pattern test report...")
        
        report = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bot_token": f"{self.user_a_bot_token[:5]}...{self.user_a_bot_token[-5:]}",
            "user_a_username": self.user_a_username,
            "user_b_username": self.user_b_username,
            "before_transfer": before_results,
            "after_transfer": after_results,
            "detailed_responses": self.responses
        }
        
        # Save report to file
        with open("permission_pattern_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"{Fore.GREEN}Report saved to permission_pattern_report.json")
        
        # Generate a markdown report
        self._generate_markdown_report(report)
        
        return report
    
    def _generate_markdown_report(self, report):
        """Generate a markdown report of the permission pattern tests."""
        logger.info(f"{Fore.BLUE}Generating markdown report...")
        
        with open("Permission_Pattern_Report.md", "w") as f:
            f.write("# Telegram Bot API Vulnerability - Permission Pattern Report\n\n")
            f.write(f"**Date:** {report['timestamp']}\n")
            f.write(f"**Bot Token (masked):** {report['bot_token']}\n")
            f.write(f"**User A Username:** {report['user_a_username']}\n")
            f.write(f"**User B Username:** {report['user_b_username']}\n\n")
            
            f.write("## Permission Pattern Test Results\n\n")
            f.write("This report tests the specific vulnerability pattern where a former bot owner can remove settings but not add them back after ownership transfer.\n\n")
            
            f.write("### Before Transfer\n\n")
            f.write("| Test Case | Add | Remove |\n")
            f.write("|-----------|-----|--------|\n")
            
            for name, results in report["before_transfer"].items():
                add_status = "✅ Success" if results["add_success"] else "❌ Failed"
                remove_status = "✅ Success" if results["remove_success"] else "❌ Failed"
                f.write(f"| {name} | {add_status} | {remove_status} |\n")
            
            f.write("\n### After Transfer\n\n")
            f.write("| Test Case | Add | Remove |\n")
            f.write("|-----------|-----|--------|\n")
            
            for name, results in report["after_transfer"].items():
                add_status = "✅ Success" if results["add_success"] else "❌ Failed"
                remove_status = "✅ Success" if results["remove_success"] else "❌ Failed"
                f.write(f"| {name} | {add_status} | {remove_status} |\n")
            
            f.write("\n## Conclusion\n\n")
            
            # Check if the vulnerability pattern is confirmed
            pattern_confirmed = False
            for name, results in report["after_transfer"].items():
                if not results["add_success"] and results["remove_success"]:
                    pattern_confirmed = True
                    break
            
            if pattern_confirmed:
                f.write("**Vulnerability Pattern Confirmed:** The tests confirm that after ownership transfer, the former owner can still remove settings but cannot add them back. This represents a security vulnerability in the Telegram Bot API's permission model.\n\n")
            else:
                f.write("**Vulnerability Pattern Not Confirmed:** The tests did not confirm the expected vulnerability pattern. Further investigation may be needed.\n\n")
            
            f.write("### Detailed Findings\n\n")
            
            for name, results in report["after_transfer"].items():
                f.write(f"#### {name}\n\n")
                if not results["add_success"] and results["remove_success"]:
                    f.write(f"- ✅ **Vulnerability Confirmed:** Former owner can remove {name.lower()} but cannot add them back.\n")
                elif results["add_success"] and results["remove_success"]:
                    f.write(f"- ⚠️ **Full Access Retained:** Former owner can both add and remove {name.lower()}.\n")
                elif not results["add_success"] and not results["remove_success"]:
                    f.write(f"- ❌ **No Access:** Former owner cannot add or remove {name.lower()}.\n")
                else:
                    f.write(f"- ❓ **Unexpected Pattern:** Former owner can add but not remove {name.lower()}.\n")
                f.write("\n")
        
        logger.info(f"{Fore.GREEN}Markdown report saved to Permission_Pattern_Report.md")

def main():
    """Main function to run the permission pattern tests."""
    print(f"{Fore.CYAN}Telegram Bot API Vulnerability - Permission Pattern Testing")
    print(f"{Fore.CYAN}===================================================\n")
    
    try:
        # Initialize the tester
        tester = TelegramPermissionTester()
        
        # Run tests
        tester.run_tests()
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    main()
