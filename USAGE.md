# Telegram Bot API Vulnerability Exploitation

This project demonstrates a vulnerability in the Telegram Bot API where a former bot owner can still have partial access to the bot after transferring ownership.

## Vulnerability Description

When a Telegram bot is transferred from one owner (User A) to another (User B), the bot token remains the same. This creates a security issue where the former owner (User A) can still use the token to perform certain actions, specifically:

1. User A can still remove bot commands using the `setMyCommands` endpoint with an empty commands list
2. User A cannot add commands back (receives a permission error)
3. User A may still have access to other API endpoints like `getUpdates` and `sendMessage`

This vulnerability allows a malicious former owner to disrupt the bot's functionality even after transferring ownership.

## Prerequisites

- Python 3.7+
- Two Telegram accounts (one for User A, one for User B)
- Access to BotFather to create and transfer a bot

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/jlucus/tg-bot-disclosure.git
   cd tg-bot-disclosure
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a bot using BotFather:
   - Open Telegram and search for @BotFather
   - Send the command `/newbot`
   - Follow the instructions to create a new bot
   - Copy the bot token provided by BotFather

4. Configure the `.env` file:
   - Copy the example `.env` file or use the existing one
   - Fill in the following values:
     - `USER_A_BOT_TOKEN`: The token of the bot created in step 3
     - `USER_A_TELEGRAM_USERNAME`: Your Telegram username (User A)
     - `USER_B_TELEGRAM_USERNAME`: The Telegram username of User B
     - `BOT_NAME`: The name of your bot
     - `BOT_USERNAME`: The username of your bot (without @)

## Usage

### Automated Exploitation

Run the main exploitation script:

```
python exploit_automation.py
```

This script will:
1. Verify the bot token and get bot information
2. Set initial commands for the bot
3. Prompt you to transfer the bot to User B using BotFather
4. After transfer, attempt to remove commands as User A (should succeed)
5. Attempt to restore commands as User A (should fail with permission error)
6. Generate a report of the exploitation

### Manual Testing

You can also use the `telegram_api_tester.py` script to manually test different API endpoints:

```
python telegram_api_tester.py --endpoint getMe
python telegram_api_tester.py --method POST --endpoint setMyCommands --data '{"commands":[]}'
```

## Exploitation Steps in Detail

1. **Bot Creation and Setup**:
   - User A creates a bot via BotFather
   - User A sets commands for the bot using `setMyCommands`

2. **Ownership Transfer**:
   - User A transfers the bot to User B using BotFather's "Transfer Bot Ownership" feature
   - After transfer, User B is the new owner, but the bot token remains the same

3. **Exploitation**:
   - User A (former owner) can still use the old token to call `setMyCommands` with an empty commands list
   - This removes all commands from the bot, disrupting its functionality
   - User A cannot add commands back (receives a permission error)
   - User A may still have access to other API endpoints

4. **Verification**:
   - User B (new owner) can successfully call all API methods with the same token
   - This confirms that the token is still valid and the bot is functional

## Report Generation

The exploitation script generates a detailed report in `exploit_report.json` containing:
- Bot information
- Original commands
- Exploitation attempts and responses
- Timestamps of each request

This report can be used as evidence when reporting the vulnerability.

## Security Implications

This vulnerability has several security implications:
- Unauthorized configuration control by former owners
- Potential message/data exposure if the former owner can still access `getUpdates`
- Access control violation (ownership transfer doesn't fully revoke privileges)
- Trust and continuity risk for bot users and new owners

## Responsible Disclosure

This tool is intended for educational purposes and responsible disclosure. If you discover this vulnerability in a production system, please report it to the appropriate security team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
