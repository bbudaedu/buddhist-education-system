@echo off
REM 設置 UTF-8 編碼的通知處理器啟動腳本
REM UTF-8 Encoded Notification Processor Startup Script

echo Setting up UTF-8 environment...

REM 設置控制台代碼頁為 UTF-8
chcp 65001 > nul

REM 設置 Python 環境變數
set PYTHONIOENCODING=utf-8
set LC_ALL=zh_TW.UTF-8
set LANG=zh_TW.UTF-8

REM 設置 Python 路徑（如果需要）
REM set PYTHONPATH=%PYTHONPATH%;.

echo Console encoding set to UTF-8 (CP65001)
echo Python IO encoding set to UTF-8
echo.

echo Starting notification processor...
echo =====================================

REM 執行通知處理器
python notification_processor.py

echo.
echo =====================================
echo Notification processor completed.

REM 如果有錯誤，暫停以查看錯誤訊息
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error occurred! Exit code: %ERRORLEVEL%
    echo Press any key to continue...
    pause > nul
)