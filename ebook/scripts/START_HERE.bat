@echo off
chcp 65001 >nul
REM 網站監控系統 - 快速啟動指南

:menu
cls
echo ╔════════════════════════════════════════════════════════╗
echo ║     佛教教育網站監控系統 - 啟動選單                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 請選擇操作：
echo.
echo [1] 啟動持續監控（每60分鐘檢查一次）
echo [2] 執行單次掃描
echo [3] 查看系統狀態
echo [4] 查看健康報告
echo [5] 產生每日報告
echo [6] 開啟設定檔
echo [0] 離開
echo.
set /p choice="請輸入選項 (0-6): "

if "%choice%"=="1" goto continuous
if "%choice%"=="2" goto single
if "%choice%"=="3" goto status
if "%choice%"=="4" goto health
if "%choice%"=="5" goto report
if "%choice%"=="6" goto config
if "%choice%"=="0" goto end
goto menu

:continuous
cls
echo 啟動持續監控模式...
echo 按 Ctrl+C 可停止監控
echo.
python comprehensive_monitoring_integration.py start
pause
goto menu

:single
cls
echo 執行單次掃描...
echo.
python comprehensive_monitoring_integration.py start --interval 0
pause
goto menu

:status
cls
echo 查詢系統狀態...
echo.
python comprehensive_monitoring_integration.py status
pause
goto menu

:health
cls
echo 產生健康檢查報告...
echo.
python comprehensive_monitoring_integration.py health
pause
goto menu

:report
cls
echo 產生每日報告...
echo.
python comprehensive_monitoring_integration.py report --type daily
pause
goto menu

:config
cls
echo 開啟設定檔...
notepad config.json
goto menu

:end
echo 感謝使用！
timeout /t 2 >nul
exit
