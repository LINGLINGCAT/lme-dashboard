@echo off
chcp 65001 >nul
echo 安全DNS設定工具
echo ================
echo.

echo 請選擇DNS服務：
echo.
echo 1. Google DNS (8.8.8.8, 8.8.4.4) - 推薦
echo 2. Cloudflare DNS (1.1.1.1, 1.0.0.1) - 最快
echo 3. Quad9 DNS (9.9.9.9, 149.112.112.112) - 最安全
echo 4. 還原為自動DNS
echo.

set /p choice="請輸入選擇 (1-4): "

REM 需要管理員權限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 已取得管理員權限
) else (
    echo 請以管理員身份執行此批次檔
    echo 右鍵點擊此檔案 > 以系統管理員身份執行
    pause
    exit /b 1
)

echo 正在設定DNS伺服器...

REM 取得網路介面名稱
for /f "tokens=2 delims=:" %%i in ('netsh interface show interface ^| findstr "已啟用"') do (
    set "interface=%%i"
    goto :found
)

:found
echo 找到網路介面: %interface%

if "%choice%"=="1" (
    echo 設定Google DNS...
    netsh interface ip set dns name="%interface%" static 8.8.8.8
    netsh interface ip add dns name="%interface%" 8.8.4.4 index=2
    echo ✅ Google DNS設定完成
) else if "%choice%"=="2" (
    echo 設定Cloudflare DNS...
    netsh interface ip set dns name="%interface%" static 1.1.1.1
    netsh interface ip add dns name="%interface%" 1.0.0.1 index=2
    echo ✅ Cloudflare DNS設定完成
) else if "%choice%"=="3" (
    echo 設定Quad9 DNS...
    netsh interface ip set dns name="%interface%" static 9.9.9.9
    netsh interface ip add dns name="%interface%" 149.112.112.112 index=2
    echo ✅ Quad9 DNS設定完成
) else if "%choice%"=="4" (
    echo 還原為自動DNS...
    netsh interface ip set dns name="%interface%" dhcp
    echo ✅ 已還原為自動DNS
) else (
    echo 無效選擇，使用Google DNS...
    netsh interface ip set dns name="%interface%" static 8.8.8.8
    netsh interface ip add dns name="%interface%" 8.8.4.4 index=2
    echo ✅ Google DNS設定完成
)

echo.
echo 正在測試連線...
ping -n 1 google.com >nul
if %errorlevel% == 0 (
    echo ✅ 網路連線正常
) else (
    echo ❌ 網路連線仍有問題
)

echo.
echo 安全性說明：
echo ============
echo.
echo ✅ Google DNS (8.8.8.8):
echo    - 不會記錄個人資料
echo    - 使用加密通訊
echo    - 比ISP DNS更安全
echo.
echo ✅ Cloudflare DNS (1.1.1.1):
echo    - 最快的DNS服務
echo    - 承諾不會記錄查詢
echo    - 免費且可靠
echo.
echo ✅ Quad9 DNS (9.9.9.9):
echo    - 專注於安全性
echo    - 自動阻擋惡意網站
echo    - 保護隱私
echo.

echo 請重新啟動瀏覽器並測試Telegram連線
echo.

pause 