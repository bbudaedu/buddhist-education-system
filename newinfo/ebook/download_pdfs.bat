@echo off
chcp 65001 >nul
echo 開始下載 PDF 檔案...
echo.
powershell -ExecutionPolicy Bypass -File download_pdfs.ps1
echo.
pause
