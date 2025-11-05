@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo 📅 新書自動檢查系統管理工具
echo ================================
echo.

if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="status" goto status
if "%1"=="trigger" goto trigger
if "%1"=="audit" goto audit
if "%1"=="help" goto help
if "%1"=="" goto help

:help
echo 使用方式: automation.bat [命令]
echo.
echo 可用命令:
echo   start     - 啟動自動化系統
echo   stop      - 停止自動化系統
echo   restart   - 重新啟動系統
echo   status    - 檢查系統狀態
echo   trigger   - 手動觸發新書檢查
echo   audit     - 查看操作日誌
echo   help      - 顯示此幫助
echo.
echo 範例:
echo   automation.bat start
echo   automation.bat status
echo   automation.bat trigger
goto end

:start
echo 🚀 啟動自動化系統...
echo.
echo 正在編譯 TypeScript...
call npm run build
if errorlevel 1 (
    echo ❌ 編譯失敗
    goto end
)
echo.
echo 正在啟動服務...
start "LINE Bot Service" cmd /k "npm start"
echo ✅ 服務已在背景啟動
echo 💡 使用 "automation.bat status" 檢查狀態
goto end

:stop
echo 🛑 停止自動化系統...
taskkill /f /im node.exe /fi "WINDOWTITLE eq LINE Bot Service*" 2>nul
echo ✅ 系統已停止
goto end

:restart
echo 🔄 重新啟動自動化系統...
call :stop
timeout /t 3 /nobreak >nul
call :start
goto end

:status
echo 📊 檢查系統狀態...
node manage-automation.js status
goto end

:trigger
echo 🚀 手動觸發新書檢查...
node manage-automation.js trigger
goto end

:audit
echo 📋 查看操作日誌...
node manage-automation.js audit
goto end

:end
echo.
pause