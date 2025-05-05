# tg-bot-disclosure

# Attack surface: Telegram Bot API:



Telegram Bot API setMyCommands
https://api.telegram.org/bot<token>/setMyCommands

# Severity: 9.0 (Critical) \ [Estimated CVSS v3.1 score]

CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:A/MAV:N/MAC:H/MAT:N/MPR:L/MUI:N/MVC:H/MVI:H/MVA:H/AU:Y/V:C/RE:L/U:Red

## Description

When a Telegram bot is transferred from User A to User B via BotFather, the original bot token remains unchanged. We observed that the *former* owner (User A) who still holds the bot token can continue calling certain Bot API methods that modify bot configuration. In particular, User A was able to call setMyCommands with an empty command list to remove all commands (the API returned success). However, when User A tried to restore or add commands via setMyCommands with a non-empty list, the Bot API responded with HTTP 400 (“Bad Request: permission denied”), indicating insufficient rights. In other words, some command-modifying operations succeed for the old token while others fail. This partial access persistence is a security flaw: after ownership transfer, the previous owner should no longer have any access, but here they can still interfere with the bot’s settings and commands. This violates intended access control for transferred bots and could allow disruption of the bot’s normal operation.

## Steps to reproduce:

1. Set up bot: Using User A’s Telegram account, create a new bot via BotFather and note its <token>. Configure one or more commands via the Bot API (e.g. call setMyCommands to add a sample command).
2. Transfer ownership: Use BotFather’s Transfer Bot command to transfer the bot from User A to User B. After transfer, User B is the new owner, but the bot token remains the same.
3. Old-owner API call (remove): Still acting as User A (using the old <token>), call the Bot API to remove commands. For example:

   * POST https://api.telegram.org/bot<token>/setMyCommands with JSON payload {"commands":[]}.
   * Expected result: HTTP 200 OK, e.g. response {"ok":true,"result":true}, indicating commands were cleared.
4. Old-owner API call (restore): Again as User A, call the Bot API to set commands. For example:

   * POST https://api.telegram.org/bot<token>/setMyCommands with payload {"commands":[{"command":"test","description":"desc"}]}.
   * Observed result: HTTP 400 Bad Request, with an error like “permission denied” (e.g. {"ok":false,"error_code":400,"description":"Bad Request: ... permission"}). The API explicitly rejects the command addition despite using a valid token.
5. Verification (optional): Confirm that User B (new owner) can successfully call both API methods with the same token. Also verify that User A can still call other reading or message-sending methods (e.g. getMyCommands, getUpdates, sendMessage) using the old token, indicating continued partial access.

## Impact

* Unauthorized configuration control: The former owner can delete or alter the bot’s commands and settings despite no longer owning the bot. This can break the bot’s functionality or confuse users.
* Potential message/data exposure: Since the old token remains valid, User A could also receive updates (getUpdates) or send messages on behalf of the bot, leading to information leakage or impersonation.
* Access control violation: The issue shows that ownership transfer does not fully revoke privileges, violating the security expectation that only the new owner should control the bot. An attacker in the old-owner position could exploit this to sabotage or hijack bot behavior.
* Trust and continuity risk: Bots often serve many users; if an old owner can interfere at will, the integrity and availability of the service are undermined. Users may be misled by missing or altered commands, and the new owner’s trust in the bot platform could be compromised.


## Additional details
* Example API requests and payloads (replace `<token>` and `<commands>`):

  * Remove all commands:

    
    curl -X POST "https://api.telegram.org/bot<token>/setMyCommands" \
         -d '{"commands":[]}'
    
  * Add a command (e.g. “test”):

    
    curl -X POST "https://api.telegram.org/bot<token>/setMyCommands" \
         -d '{"commands":[{"command":"test","description":"desc"}]}'
    
* Expected vs. actual responses:

  * Removing commands: HTTP 200 OK, e.g. {"ok":true,"result":true}.
  * Restoring/adding commands: HTTP 400 Bad Request, e.g. {"ok":false,"error_code":400,"description":"Bad Request: ... permission denied"}.
* Timestamps: Record the exact date/time (UTC) of each API request and response. For example, use 2025-05-04T19:00:00Z format.
* Environment: Tested on Telegram Bot API version 9.0 (as of April 2025) using curl. Bot created and transferred using @BotFather.
* Additional observations: The issue is reproducible consistently; attempts to call other bot-setting methods (like setMyName, setMyShortDescription, etc.) with the old token may exhibit similar partial access.

## Possible follow-up vulnerabilities

* Other Bot API methods: Similar permission inconsistencies might exist in other endpoints. For example, the old owner may still be able to invoke methods like setMyName, setMyShortDescription, deleteMyCommands, setWebhook, etc., leading to unintended changes. If the old token is accepted for any action, the same flaw could allow misuse.
* Message handling: The previous owner could potentially keep calling getUpdates or sendMessage with the old token, allowing continued access to user messages and broadcasting unauthorized messages, which is a serious privacy and abuse risk.
* Token validity: Since the token is not regenerated, any leaked or backed-up token remains valid after transfer. Attackers could exploit this persistent credential to regain control or create confusion even if the old owner’s account is compromised.
* Other ownership transfers: Telegram group or channel ownership transfer features (or bot-admin privileges in groups) might have analogous issues if tokens or permissions aren’t updated correctly when roles change.

## Example Payloads and Evidence (to be filled by reporter)

* Bot Token (masked): Indicate the bot’s token (e.g. show first/last characters) to identify which bot was tested.
* Commands used: Show the exact JSON commands list you attempted (empty list vs. specific commands).
* cURL/API requests: Provide the actual requests made. For example:

  
  curl -X POST https://api.telegram.org/bot<token>/setMyCommands \
       -d '{"commands":[]}'   # Removing commands
  curl -X POST https://api.telegram.org/bot<token>/setMyCommands \
       -d '{"commands":[{"command":"test","description":"desc"}]}'   # Restoring commands
  
* HTTP Responses: For each request, include the status code and full JSON response. For example:

  
  HTTP/1.1 200 OK
  {"ok":true,"result":true}
  

  
  HTTP/1.1 400 Bad Request
  {"ok":false,"error_code":400,"description":"Bad Request: ... permission denied"}
  
* Timestamps: List the exact UTC timestamps when you made each request (e.g. 2025-05-04T19:05:00Z).
* Screenshots/Logs: Attach any screenshots or log excerpts showing the requests and responses (e.g. output from curl or API testing tools).

All sections above follow Telegram’s disclosure template. Please replace placeholders (like <token>) with actual data when submitting.

Sources: Telegram Bot API documentation, Telegram BotFather transfer announcement, and Telegram Bug Bounty report guidelines.
