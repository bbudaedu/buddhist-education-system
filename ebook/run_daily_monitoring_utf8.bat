@echo off
REM 每日監控執行腳本 (UTF-8)
REM Daily Monitoring Execution Script (UTF-8)

echo ================================================================================
echo Daily Website Monitoring Execution
echo ================================================================================
echo.

REM 設置控制台代碼頁為 UTF-8
chcp 65001 > nul

REM 設置 Python 環境變數
set PYTHONIOENCODING=utf-8
set LC_ALL=zh_TW.UTF-8
set LANG=zh_TW.UTF-8

echo [%date% %time%] Starting daily monitoring execution...
echo.

REM 執行每日監控腳本
python run_daily_monitoring.py

REM 儲存退出碼
set EXIT_CODE=%ERRORLEVEL%

echo.
echo [%date% %time%] Daily monitoring execution completed.
echo Exit code: %EXIT_CODE%
echo ================================================================================

REM 如果有錯誤，暫停以查看錯誤訊息（僅在手動執行時）
if %EXIT_CODE% NEQ 0 (
    if "%1"=="manual" (
        echo.
        echo Error occurred! Press any key to continue...
        pause > nul
    )
)

exit /b %EXIT_CODE%
