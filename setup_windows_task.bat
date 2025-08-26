@echo off
chcp 65001 >nul
echo 🚀 LME Dashboard Windows任務計劃設置
echo ======================================

cd /d "D:\ANACONDA\lme-dashboard"

echo 📋 正在創建Windows任務計劃...

REM 創建每小時執行的任務
schtasks /create /tn "LME Dashboard 數據更新" /tr "D:\ANACONDA\lme-dashboard\update_data.bat" /sc hourly /f

REM 創建每天上午9點執行的任務
schtasks /create /tn "LME Dashboard 每日更新 09:00" /tr "D:\ANACONDA\lme-dashboard\update_data.bat" /sc daily /st 09:00 /f

REM 創建每天下午3點執行的任務
schtasks /create /tn "LME Dashboard 每日更新 15:00" /tr "D:\ANACONDA\lme-dashboard\update_data.bat" /sc daily /st 15:00 /f

echo.
echo ✅ Windows任務計劃設置完成！
echo.
echo 📋 已創建的任務：
echo    • LME Dashboard 數據更新（每小時執行）
echo    • LME Dashboard 每日更新 09:00
echo    • LME Dashboard 每日更新 15:00
echo.
echo 💡 您可以在「工作排程器」中查看和管理這些任務
echo 💡 任務將在背景自動運行，無需手動啟動
echo.
pause

