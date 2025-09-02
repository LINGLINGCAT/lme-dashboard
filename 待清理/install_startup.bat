@echo off
chcp 65001 >nul
echo 🚀 LME Dashboard 開機自啟動設置
echo =================================

cd /d "D:\ANACONDA\lme-dashboard"

echo 📋 正在設置開機自啟動...

REM 創建開機自啟動任務
schtasks /create /tn "LME Dashboard 開機數據更新" /tr "D:\ANACONDA\lme-dashboard\simple_auto_update.py" /sc onstart /f

echo.
echo ✅ 開機自啟動設置完成！
echo.
echo 💡 系統開機時會自動執行數據更新
echo 💡 您可以在「工作排程器」中查看和管理此任務
echo.
pause

