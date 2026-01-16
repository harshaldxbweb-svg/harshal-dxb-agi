# AWS App Runner Deployment Script
# Run this script to deploy to AWS App Runner

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS App Runner Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git not found. Please install Git." -ForegroundColor Red
    exit 1
}

# Check if AWS CLI is available
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  AWS CLI not found. You'll need to deploy manually from AWS Console." -ForegroundColor Yellow
}

Write-Host "Step 1: Git Configuration" -ForegroundColor Yellow
Write-Host "Checking Git status..."
git status
Write-Host ""

Write-Host "Step 2: Adding all files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Committing changes..." -ForegroundColor Yellow
$commitMessage = "Deploy to AWS App Runner - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m $commitMessage
Write-Host "✓ Committed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Pushing to repository..." -ForegroundColor Yellow
git push origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pushed to repository" -ForegroundColor Green
} else {
    Write-Host "❌ Git push failed. Check your credentials." -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Ready for AWS App Runner Deployment!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to AWS Console: https://console.aws.amazon.com/apprunner" -ForegroundColor White
Write-Host "2. Click 'Create Service'" -ForegroundColor White
Write-Host "3. Select 'Source Code Repository' > GitHub" -ForegroundColor White
Write-Host "4. Connect and select your repository" -ForegroundColor White
Write-Host "5. Configure Secrets in AWS Secrets Manager:" -ForegroundColor White
Write-Host "   - admin_phone" -ForegroundColor Cyan
Write-Host "   - google_api_key" -ForegroundColor Cyan
Write-Host "   - ultramsg_instance_id" -ForegroundColor Cyan
Write-Host "   - ultramsg_token" -ForegroundColor Cyan
Write-Host "   - aws_region" -ForegroundColor Cyan
Write-Host "6. Deploy and get the webhook URL" -ForegroundColor White
Write-Host "7. Add webhook URL to ULTRAMSG" -ForegroundColor White
Write-Host ""
Write-Host "Webhook URL format: https://your-app-runner-url.awsapprunner.com" -ForegroundColor Magenta
Write-Host ""
