@echo off
chcp 65001 >nul
echo 🚀 LME Dashboard 數據更新工具
echo ================================

cd /d "D:\ANACONDA\lme-dashboard"

echo 📊 正在更新LME數據...
python update_data_once.py

echo.
echo ✅ 數據更新完成！
echo 📁 更新時間：%date% %time%
echo.
pause

