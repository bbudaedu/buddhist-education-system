@echo off
echo ========================================
echo Buddhist Education System
echo GitHub Upload Script
echo ========================================
echo.

echo Step 1: Please create a new repository on GitHub
echo   - Go to https://github.com/new
echo   - Repository name: buddhist-education-system
echo   - Description: Buddhist Education System - Ebook Summary and LINE Bot
echo   - Visibility: Public or Private (your choice)
echo   - DO NOT initialize with README
echo.
pause

echo.
echo Step 2: Enter your GitHub username
set /p USERNAME="GitHub Username: "

echo.
echo Step 3: Adding remote repository...
git remote add origin https://github.com/%USERNAME%/buddhist-education-system.git

echo.
echo Step 4: Renaming branch to main...
git branch -M main

echo.
echo Step 5: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Upload Complete!
echo ========================================
echo.
echo Your repository is now available at:
echo https://github.com/%USERNAME%/buddhist-education-system
echo.
pause
