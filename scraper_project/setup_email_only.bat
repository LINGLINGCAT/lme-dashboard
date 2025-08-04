@echo off
chcp 65001 >nul
echo Email通知設定工具
echo ==================
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

REM 安裝依賴套件
echo 檢查並安裝依賴套件...
pip install -r requirements.txt

REM 執行Email設定
echo.
echo 開始設定Email通知...
echo.

python setup_email_only.py

echo.
echo 設定完成！
echo.
echo 接下來請：
echo 1. 編輯 .env 檔案，填入您的Gmail設定
echo 2. 設定Gmail兩步驟驗證和應用程式密碼
echo 3. 執行測試: python test_email_only.py
echo 4. 啟動服務: python tender_notification.py
echo.

pause 