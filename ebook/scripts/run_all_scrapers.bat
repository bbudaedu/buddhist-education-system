@echo off
chcp 65001 >nul
echo ========================================
echo 執行所有爬蟲 (All Scrapers)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 執行新書爬蟲...
call run_book_scraper.bat

echo.
echo [2/3] 執行輪播爬蟲...
call run_carousel_scraper.bat

echo.
echo [3/3] 執行公告爬蟲...
call run_bulletin_scraper.bat

echo.
echo ========================================
echo 所有爬蟲執行完成！
echo 結果已存到 downloads 目錄
echo ========================================
pause
