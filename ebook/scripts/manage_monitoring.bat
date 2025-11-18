@echo off
chcp 65001 >nul
REM 監控系統管理工具

:menu
cls
echo ╔════════════════════════════════════════════════════════╗
echo ║     佛教教育網站監控系統 - 管理工具                    ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 請選擇操作：
echo.
echo [1] 檢查系統狀態
echo [2] 啟動監控（如果未運行）
echo [3] 停止所有監控進程
echo [4] 查看最新日誌
echo [5] 查看輸出檔案
echo [0] 離開
echo.
set /p choice="請輸入選項 (0-5): "

if "%choice%"=="1" goto check_status
if "%choice%"=="2" goto start_monitoring
if "%choice%"=="3" goto stop_monitoring
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto view_output
if "%choice%"=="0" goto end
goto menu

:check_status
cls
echo 檢查系統狀態...
echo.
python check_monitoring_status.py
pause
goto menu

:start_monitoring
cls
echo 啟動監控系統...
echo.
echo 檢查是否已有進程運行...
python check_monitoring_status.py | findstr "找到.*個監控進程" >nul
if %errorlevel%==0 (
    echo.
    echo ⚠ 監控系統已在運行中！
    echo 請先停止現有進程再啟動新的。
    pause
    goto menu
)

echo.
echo 啟動新的監控進程...
start "佛教教育監控系統" python comprehensive_monitoring_integration.py start
timeout /t 3 >nul
echo.
echo ✓ 監控系統已啟動
echo 視窗將在背景運行
pause
goto menu

:stop_monitoring
cls
echo 停止監控系統...
echo.
echo ⚠ 這將停止所有運行中的監控進程
set /p confirm="確定要停止嗎？(Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo.
echo 正在停止進程...
taskkill /F /FI "WINDOWTITLE eq 佛教教育監控系統*" 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *comprehensive_monitoring_integration.py*" 2>nul

timeout /t 2 >nul
echo.
echo ✓ 已發送停止信號
echo 請稍後使用「檢查系統狀態」確認
pause
goto menu

:view_logs
cls
echo 查看最新日誌...
echo.
echo 選擇要查看的日誌：
echo [1] 主日誌
echo [2] 錯誤日誌
echo [3] 效能日誌
echo [0] 返回
echo.
set /p log_choice="請選擇 (0-3): "

if "%log_choice%"=="1" (
    if exist logs\website_monitoring_enhanced_main.log (
        type logs\website_monitoring_enhanced_main.log | more
    ) else (
        echo 日誌檔案不存在
    )
)
if "%log_choice%"=="2" (
    if exist logs\errors\website_monitoring_enhanced_errors.log (
        type logs\errors\website_monitoring_enhanced_errors.log | more
    ) else (
        echo 錯誤日誌檔案不存在
    )
)
if "%log_choice%"=="3" (
    if exist logs\performance\website_monitoring_enhanced_performance.log (
        type logs\performance\website_monitoring_enhanced_performance.log | more
    ) else (
        echo 效能日誌檔案不存在
    )
)
pause
goto menu

:view_output
cls
echo 開啟輸出目錄...
if exist generated_documents (
    explorer generated_documents
    echo ✓ 已開啟 generated_documents 目錄
) else (
    echo ✗ 輸出目錄不存在
    echo 可能尚未產生任何文件
)
pause
goto menu

:end
echo 感謝使用！
timeout /t 2 >nul
exit
