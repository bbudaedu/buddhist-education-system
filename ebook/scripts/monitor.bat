@echo off
REM Website Monitoring CLI Wrapper
REM Usage: monitor.bat [command] [options]

cd /d "%~dp0"
python website_monitoring_cli.py %*

REM Keep window open to see results
pause
