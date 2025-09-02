@echo off
chcp 65001 >nul
echo 🚀 LME 數據自動記錄系統
echo ================================
echo.
echo 正在啟動自動記錄系統...
echo 系統將在每天 09:00 和 17:00 自動記錄 LME 數據
echo.
echo 按 Ctrl+C 可以停止程序
echo.

python auto_update_data.py

pause

