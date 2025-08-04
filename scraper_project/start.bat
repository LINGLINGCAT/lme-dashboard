@echo off
echo 自動爬蟲系統啟動器
echo ====================

REM 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 未找到Python，請先安裝Python
    pause
    exit /b 1
)

REM 檢查是否在正確的目錄
if not exist "main.py" (
    echo 錯誤: 請在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 檢查環境變數檔案
if not exist ".env" (
    echo 警告: 未找到.env檔案
    echo 請複製env_example.txt為.env並設定您的環境變數
    echo.
    copy env_example.txt .env
    echo 已建立.env檔案，請編輯並設定您的環境變數
    pause
)

REM 安裝依賴套件
echo 檢查並安裝依賴套件...
pip install -r requirements.txt

echo.
echo 請選擇執行模式:
echo 1. 執行一次完整任務
echo 2. 只執行客戶搜尋
echo 3. 只執行標案監控
echo 4. 啟動排程模式
echo 5. 執行測試
echo 6. 退出
echo.

set /p choice="請輸入選項 (1-6): "

if "%choice%"=="1" (
    echo 執行一次完整任務...
    python main.py --once
) else if "%choice%"=="2" (
    echo 執行客戶搜尋...
    python main.py --customer
) else if "%choice%"=="3" (
    echo 執行標案監控...
    python main.py --tender
) else if "%choice%"=="4" (
    echo 啟動排程模式...
    python main.py --schedule
) else if "%choice%"=="5" (
    echo 執行測試...
    python run_example.py
) else if "%choice%"=="6" (
    echo 退出程式
    exit /b 0
) else (
    echo 無效選項，請重新執行
)

echo.
echo 程式執行完成
pause 