# AWS App Runner Deployment Script
# Load .env and configure AWS

Write-Host "========================================" -ForegroundColor Green
Write-Host "AWS App Runner Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Load .env file
Write-Host "Loading configuration from .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Error: .env file not found!" -ForegroundColor Red
    exit 1
}

$envContent = Get-Content ".env"
$env_vars = @{}

foreach ($line in $envContent) {
    if ($line -match "^\s*#" -or [string]::IsNullOrWhiteSpace($line)) {
        continue
    }
    $parts = $line -split "=", 2
    if ($parts.Count -eq 2) {
        $env_vars[$parts[0].Trim()] = $parts[1].Trim()
    }
}

$AWS_ACCESS_KEY_ID = $env_vars["AWS_ACCESS_KEY_ID"]
$AWS_SECRET_ACCESS_KEY = $env_vars["AWS_SECRET_ACCESS_KEY"]
$AWS_REGION = $env_vars["AWS_REGION"]
$ADMIN_PHONE = $env_vars["ADMIN_PHONE"]
$GOOGLE_API_KEY = $env_vars["GOOGLE_API_KEY"]
$ULTRAMSG_INSTANCE_ID = $env_vars["ULTRAMSG_INSTANCE_ID"]
$ULTRAMSG_TOKEN = $env_vars["ULTRAMSG_TOKEN"]

Write-Host "✓ Loaded credentials" -ForegroundColor Green
Write-Host ""

# Check AWS CLI
Write-Host "Checking AWS CLI..." -ForegroundColor Yellow
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "AWS CLI not found! Please install it first:" -ForegroundColor Red
    Write-Host "https://aws.amazon.com/cli/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or run this PowerShell command:" -ForegroundColor Yellow
    Write-Host "choco install awscli -y" -ForegroundColor Cyan
    exit 1
}

Write-Host "✓ AWS CLI found" -ForegroundColor Green
Write-Host ""

# Configure AWS credentials
Write-Host "Configuring AWS credentials..." -ForegroundColor Yellow
$awsCredsDir = "$env:USERPROFILE\.aws"
if (-not (Test-Path $awsCredsDir)) {
    New-Item -ItemType Directory -Path $awsCredsDir | Out-Null
}

$awsCredsContent = @"
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
region = $AWS_REGION
"@

Set-Content -Path "$awsCredsDir\credentials" -Value $awsCredsContent
Write-Host "✓ AWS credentials configured" -ForegroundColor Green
Write-Host ""

# Verify AWS access
Write-Host "Verifying AWS access..." -ForegroundColor Yellow
$accountId = aws sts get-caller-identity --query Account --output text 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to access AWS account!" -ForegroundColor Red
    Write-Host "Please check your credentials" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ AWS Account ID: $accountId" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOYMENT INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your GitHub repository is ready:" -ForegroundColor Yellow
Write-Host "https://github.com/harshaldxbweb-svg/harshal-dxb-agi" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to AWS Console:" -ForegroundColor White
Write-Host "   https://console.aws.amazon.com/apprunner" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Click 'Create Service'" -ForegroundColor White
Write-Host ""
Write-Host "3. Configure source:" -ForegroundColor White
Write-Host "   - Source code repository" -ForegroundColor Cyan
Write-Host "   - Connect GitHub" -ForegroundColor Cyan
Write-Host "   - Select: harshaldxbweb-svg/harshal-dxb-agi" -ForegroundColor Cyan
Write-Host "   - Branch: main" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Configure build & deploy:" -ForegroundColor White
Write-Host "   - Runtime: Python 11" -ForegroundColor Cyan
Write-Host "   - Build cmd: pip install --no-cache-dir -r requirements.txt" -ForegroundColor Cyan
Write-Host "   - Start cmd: gunicorn --bind 0.0.0.0:8080 --workers 4 --timeout 60 main:app" -ForegroundColor Cyan
Write-Host "   - Port: 8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Add environment variables:" -ForegroundColor White
Write-Host "   ADMIN_PHONE: $ADMIN_PHONE" -ForegroundColor Cyan
Write-Host "   GOOGLE_API_KEY: $GOOGLE_API_KEY" -ForegroundColor Cyan
Write-Host "   ULTRAMSG_INSTANCE_ID: $ULTRAMSG_INSTANCE_ID" -ForegroundColor Cyan
Write-Host "   ULTRAMSG_TOKEN: $ULTRAMSG_TOKEN" -ForegroundColor Cyan
Write-Host "   AWS_REGION: $AWS_REGION" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Create & Deploy (takes 5-10 minutes)" -ForegroundColor White
Write-Host ""
Write-Host "7. Copy the Service URL from App Runner dashboard" -ForegroundColor White
Write-Host ""
Write-Host "8. Add Webhook to ULTRAMSG:" -ForegroundColor White
Write-Host "   https://your-service-url.awsapprunner.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Ready to deploy! 🚀" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
