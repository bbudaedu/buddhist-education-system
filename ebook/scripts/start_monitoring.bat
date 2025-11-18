@echo off
REM Start Website Monitoring System
REM This will keep running until you close the window

cd /d "%~dp0"

echo ========================================
echo Website Monitoring System
echo ========================================
echo.
echo Starting monitoring service...
echo Press Ctrl+C to stop
echo.

python comprehensive_monitoring_integration.py start

pause
