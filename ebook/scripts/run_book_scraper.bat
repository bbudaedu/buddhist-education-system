@echo off
chcp 65001 >nul
echo ========================================
echo 執行新書爬蟲與下載 (New Book Scraper)
echo ========================================
echo.

cd /d "%~dp0.."

echo 使用 config.json 中的設定執行新書爬蟲...
echo.

python run_new_book_scraper.py

echo.
pause
