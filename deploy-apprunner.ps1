Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS App Runner Deployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Git Status" -ForegroundColor Yellow
git status
Write-Host ""

Write-Host "Step 2: Adding files..." -ForegroundColor Yellow
git add .
Write-Host "Files added" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: Committing..." -ForegroundColor Yellow
$msg = "Deploy to AWS App Runner"
git commit -m $msg
Write-Host "Committed" -ForegroundColor Green
Write-Host ""

Write-Host "Step 4: Pushing to repository..." -ForegroundColor Yellow
git push origin main
Write-Host "Pushed to repository" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "READY FOR AWS APP RUNNER DEPLOYMENT" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Go to AWS Console - App Runner" -ForegroundColor White
Write-Host "2. Create Service from GitHub" -ForegroundColor White
Write-Host "3. Connect repository and deploy" -ForegroundColor White
Write-Host "4. Add Secrets in AWS Secrets Manager" -ForegroundColor White
Write-Host ""
