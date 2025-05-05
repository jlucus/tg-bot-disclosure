# Telegram Bot API Vulnerability Exploitation Setup Script
# This script sets up the environment for the exploitation

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed. Please install Python 3.7 or higher." -ForegroundColor Red
    exit 1
}

# Check if pip is installed
try {
    $pipVersion = pip --version
    Write-Host "Pip is installed: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "Pip is not installed. Please install pip." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv .venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Check if .env file exists
if (Test-Path .env) {
    Write-Host ".env file already exists." -ForegroundColor Yellow
    
    # Check if required variables are set
    $envContent = Get-Content .env -Raw
    $missingVars = @()
    
    if ($envContent -notmatch "USER_A_BOT_TOKEN=.+") {
        $missingVars += "USER_A_BOT_TOKEN"
    }
    if ($envContent -notmatch "USER_A_TELEGRAM_USERNAME=.+") {
        $missingVars += "USER_A_TELEGRAM_USERNAME"
    }
    if ($envContent -notmatch "USER_B_TELEGRAM_USERNAME=.+") {
        $missingVars += "USER_B_TELEGRAM_USERNAME"
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "The following required variables are not set in .env file:" -ForegroundColor Red
        foreach ($var in $missingVars) {
            Write-Host "  - $var" -ForegroundColor Red
        }
        Write-Host "Please edit the .env file and set these variables." -ForegroundColor Yellow
    } else {
        Write-Host "All required variables are set in .env file." -ForegroundColor Green
    }
} else {
    Write-Host ".env file does not exist. Creating template..." -ForegroundColor Yellow
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    if (-not (Test-Path .env)) {
        # If .env.example doesn't exist, create a new .env file
        @"
# Telegram Bot Configuration
# User A (Original Owner)
USER_A_BOT_TOKEN=
USER_A_TELEGRAM_USERNAME=

# User B (New Owner)
USER_B_TELEGRAM_USERNAME=

# Bot Configuration
BOT_NAME=
BOT_USERNAME=
BOT_DESCRIPTION="A test bot for demonstrating Telegram Bot API vulnerability"

# Logging
LOG_LEVEL=INFO
"@ | Out-File -FilePath .env -Encoding utf8
    }
    Write-Host "Please edit the .env file and set the required variables." -ForegroundColor Yellow
}

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To run the exploitation script, use: python exploit_automation.py" -ForegroundColor Cyan
Write-Host "To run the API tester, use: python telegram_api_tester.py --endpoint <endpoint>" -ForegroundColor Cyan
Write-Host "`nFor more information, see USAGE.md" -ForegroundColor Cyan
