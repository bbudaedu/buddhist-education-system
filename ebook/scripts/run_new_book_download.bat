@echo off
chcp 65001 >nul
echo ========================================
echo 執行新書下載 (New Book Download)
echo ========================================
echo.

cd /d "%~dp0.."

echo 開始爬取並下載新書...
echo.
echo 配置資訊:
echo - 目標網址: https://www.budaedu.org/#/books/applicable/chinese
echo - 基準書籍: 淨心與淨土 CH861-36
echo - 下載目錄: downloads
echo.

python test_scraper_fix.py

echo.
echo ========================================
echo 執行完成！
echo ========================================
pause
