@echo off
REM 測試每日監控執行腳本
REM Test Daily Monitoring Execution Script

echo ================================================================================
echo Testing Daily Monitoring System
echo ================================================================================
echo.
echo This script will test the complete monitoring system including:
echo   - Carousel scraper (輪播橫幅)
echo   - Bulletin scraper (停課公告)
echo   - News processor (新聞處理)
echo   - Media processor (多媒體處理)
echo   - Book scraper (新書爬蟲)
echo.
echo Press Ctrl+C to cancel, or
pause

REM 執行監控腳本（手動模式）
call run_daily_monitoring_utf8.bat manual

echo.
echo ================================================================================
echo Test completed. Check the logs folder for detailed execution logs.
echo Check the generated_documents folder for output files.
echo ================================================================================
echo.
pause
