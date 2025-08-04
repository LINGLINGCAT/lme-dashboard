@echo off
chcp 65001 >nul
echo 快速開始 - Email通知設定
echo =========================
echo 由於Telegram網路問題，先設定Email通知
echo.

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python
    pause
    exit /b 1
)

REM 檢查是否在正確的目錄
if not exist "setup_email_only.py" (
    echo 錯誤: 請在scraper_project目錄下執行此批次檔
    pause
    exit /b 1
)

echo 開始設定Email通知系統...
echo.

REM 執行Email設定
python setup_email_only.py

echo.
echo =========================
echo Email設定完成！
echo =========================
echo.
echo 接下來請：
echo.
echo 1. 設定Gmail兩步驟驗證：
echo    - 開啟Gmail
echo    - 前往設定 > 安全性
echo    - 開啟兩步驟驗證
echo    - 產生應用程式密碼
echo.
echo 2. 編輯 .env 檔案：
echo    - 填入您的Gmail帳號
echo    - 填入應用程式密碼
echo    - 填入收件人Email
echo.
echo 3. 測試Email通知：
echo    python test_email_only.py
echo.
echo 4. 啟動標案監控服務：
echo    python tender_notification.py --manual
echo.
echo 5. 設定每日自動執行：
echo    python tender_notification.py
echo.

pause 