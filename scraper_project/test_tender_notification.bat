@echo off
chcp 65001 >nul
echo 標案通知測試
echo =============

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

REM 執行手動測試
echo.
echo 開始手動測試標案通知...
echo 這將立即執行一次標案搜尋並發送通知
echo.

python tender_notification.py --manual

echo.
echo 測試完成！
pause 