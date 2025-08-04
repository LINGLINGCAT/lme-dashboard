@echo off
chcp 65001 >nul
echo 標案通知服務啟動器
echo ====================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python
    pause
    exit /b 1
)

REM 檢查是否在正確的目錄
if not exist "tender_notification.py" (
    echo 錯誤: 請在scraper_project目錄下執行此批次檔
    pause
    exit /b 1
)

REM 安裝依賴套件
echo 檢查並安裝依賴套件...
pip install -r requirements.txt

REM 啟動標案通知服務
echo.
echo 啟動標案通知服務...
echo 預設執行時間: 每日 09:00
echo 按 Ctrl+C 停止服務
echo.

python tender_notification.py

pause 