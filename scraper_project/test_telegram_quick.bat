@echo off
chcp 65001 >nul
echo Telegram Bot 快速測試工具
echo =========================
echo.

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python
    pause
    exit /b 1
)

REM 檢查是否在正確的目錄
if not exist "quick_telegram_test.py" (
    echo 錯誤: 請在scraper_project目錄下執行此批次檔
    pause
    exit /b 1
)

REM 安裝requests套件（如果需要）
echo 檢查requests套件...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo 安裝requests套件...
    pip install requests
)

REM 執行Telegram測試
echo.
echo 開始Telegram Bot測試...
echo.

python quick_telegram_test.py

echo.
echo 測試完成！
pause 