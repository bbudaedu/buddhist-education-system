# Buddhist Education System - GitHub Upload Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Buddhist Education System" -ForegroundColor Cyan
Write-Host "GitHub Upload Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Create a new repository on GitHub" -ForegroundColor Yellow
Write-Host "  - Go to https://github.com/new" -ForegroundColor White
Write-Host "  - Repository name: buddhist-education-system" -ForegroundColor White
Write-Host "  - Description: Buddhist Education System - Ebook Summary and LINE Bot" -ForegroundColor White
Write-Host "  - Visibility: Public or Private (your choice)" -ForegroundColor White
Write-Host "  - DO NOT initialize with README" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when you have created the repository"

Write-Host ""
$username = Read-Host "Step 2: Enter your GitHub username"

Write-Host ""
Write-Host "Step 3: Adding remote repository..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/buddhist-education-system.git"

Write-Host ""
Write-Host "Step 4: Renaming branch to main..." -ForegroundColor Yellow
git branch -M main

Write-Host ""
Write-Host "Step 5: Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Upload Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your repository is now available at:" -ForegroundColor Cyan
Write-Host "https://github.com/$username/buddhist-education-system" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
