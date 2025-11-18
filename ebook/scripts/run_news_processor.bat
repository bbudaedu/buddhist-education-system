@echo off
chcp 65001 >nul
echo ========================================
echo 執行新聞公告爬蟲 (News Processor)
echo ========================================
echo.

cd /d "%~dp0.."

echo 開始爬取新聞公告...
echo 目標網址: https://www.budaedu.org/#/bulletins/
echo 輸出目錄: downloads
echo.

python run_news_processor.py

echo.
pause
