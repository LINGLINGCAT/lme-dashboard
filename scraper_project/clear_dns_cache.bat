@echo off
chcp 65001 >nul
echo DNS快取清除工具
echo ================
echo.

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

echo 正在清除DNS快取...
ipconfig /flushdns
echo ✅ DNS快取已清除

echo.
echo 正在重新設定DNS伺服器...

REM 取得網路介面名稱
for /f "tokens=2 delims=:" %%i in ('netsh interface show interface ^| findstr "已啟用"') do (
    set "interface=%%i"
    goto :found
)

:found
echo 找到網路介面: %interface%

REM 設定Google DNS
netsh interface ip set dns name="%interface%" static 8.8.8.8
netsh interface ip add dns name="%interface%" 8.8.4.4 index=2

echo ✅ DNS伺服器已重新設定
echo 主要DNS: 8.8.8.8
echo 次要DNS: 8.8.4.4

echo.
echo 正在測試連線...
ping -n 1 google.com >nul
if %errorlevel% == 0 (
    echo ✅ 基本網路連線正常
) else (
    echo ❌ 基本網路連線有問題
)

echo.
echo 請重新啟動瀏覽器並測試
echo 如果問題持續，建議使用VPN
echo.

pause 