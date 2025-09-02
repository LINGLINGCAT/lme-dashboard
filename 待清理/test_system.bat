@echo off
chcp 65001 >nul
title 數據自動化系統測試

echo 🧪 數據自動化系統完整測試 (Windows)
echo ============================================================
echo.

set passed=0
set total=0

:: 1. 測試 Python 環境
echo 🔧 測試: Python 環境
echo --------------------------------------------------
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python 環境通過
    set /a passed+=1
) else (
    echo ❌ Python 環境失敗
)
set /a total+=1

:: 2. 測試必要套件
echo.
echo 🔧 測試: pandas 套件
echo --------------------------------------------------
python -c "import pandas; print('pandas 版本:', pandas.__version__)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pandas 套件通過
    set /a passed+=1
) else (
    echo ❌ pandas 套件失敗
)
set /a total+=1

echo.
echo 🔧 測試: openpyxl 套件
echo --------------------------------------------------
python -c "import openpyxl; print('openpyxl 可用')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ openpyxl 套件通過
    set /a passed+=1
) else (
    echo ❌ openpyxl 套件失敗
)
set /a total+=1

echo.
echo 🔧 測試: schedule 套件
echo --------------------------------------------------
python -c "import schedule; print('schedule 可用')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ schedule 套件通過
    set /a passed+=1
) else (
    echo ❌ schedule 套件失敗
)
set /a total+=1

echo.
echo 🔧 測試: streamlit 套件
echo --------------------------------------------------
python -c "import streamlit; print('streamlit 版本:', streamlit.__version__)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ streamlit 套件通過
    set /a passed+=1
) else (
    echo ❌ streamlit 套件失敗
)
set /a total+=1

:: 3. 測試數據目錄
echo.
echo 🔧 測試: 創建數據目錄
echo --------------------------------------------------
if not exist "data" mkdir data
echo ✅ 數據目錄已創建
set /a passed+=1
set /a total+=1

:: 4. 測試文件存在性
echo.
echo 🔧 測試: 導入腳本存在
echo --------------------------------------------------
if exist "import_historical_data.py" (
    echo ✅ 導入腳本存在
    set /a passed+=1
) else (
    echo ❌ 導入腳本不存在
)
set /a total+=1

echo.
echo 🔧 測試: 自動更新腳本存在
echo --------------------------------------------------
if exist "auto_update_data.py" (
    echo ✅ 自動更新腳本存在
    set /a passed+=1
) else (
    echo ❌ 自動更新腳本不存在
)
set /a total+=1

echo.
echo 🔧 測試: 批處理文件存在
echo --------------------------------------------------
if exist "run_auto_update.bat" (
    echo ✅ 批處理文件存在
    set /a passed+=1
) else (
    echo ❌ 批處理文件不存在
)
set /a total+=1

echo.
echo 🔧 測試: 主應用程式存在
echo --------------------------------------------------
if exist "app.py" (
    echo ✅ 主應用程式存在
    set /a passed+=1
) else (
    echo ❌ 主應用程式不存在
)
set /a total+=1

echo.
echo 🔧 測試: 數據分析頁面存在
echo --------------------------------------------------
if exist "pages\4_數據分析.py" (
    echo ✅ 數據分析頁面存在
    set /a passed+=1
) else (
    echo ❌ 數據分析頁面不存在
)
set /a total+=1

:: 5. 檢查 LME 文件
echo.
echo 🔍 檢查 LME 文件
echo --------------------------------------------------
set lme_found=false
for %%f in ("Z:\LME.xlsm" "D:\LME.xlsm" "C:\LME.xlsm" "LME.xlsm" "data\LME.xlsm") do (
    if exist "%%f" (
        echo ✅ 找到 LME 文件: %%f
        set lme_found=true
        goto :lme_check_done
    )
)
:lme_check_done
if "%lme_found%"=="false" (
    echo ⚠️  沒有找到 LME.xlsm 文件
    echo 💡 您可以：
    echo    1. 將 LME.xlsm 文件放在專案目錄下
    echo    2. 或使用數據上傳功能
)

:: 6. 檢查現有數據文件
echo.
echo 📁 檢查數據文件
echo --------------------------------------------------
if exist "data" (
    dir /b data\*.* >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ 數據目錄中有文件
        dir data\
    ) else (
        echo 📊 數據目錄為空
    )
) else (
    echo ❌ 數據目錄不存在
)

:: 7. 測試 Python 腳本語法
echo.
echo 🔧 測試: 導入腳本語法檢查
echo --------------------------------------------------
python -m py_compile import_historical_data.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 導入腳本語法檢查通過
    set /a passed+=1
) else (
    echo ❌ 導入腳本語法檢查失敗
)
set /a total+=1

echo.
echo 🔧 測試: 自動更新腳本語法檢查
echo --------------------------------------------------
python -m py_compile auto_update_data.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 自動更新腳本語法檢查通過
    set /a passed+=1
) else (
    echo ❌ 自動更新腳本語法檢查失敗
)
set /a total+=1

:: 8. 創建示例數據
echo.
echo 📊 創建示例數據
echo --------------------------------------------------
python -c "import pandas as pd; from datetime import datetime, timedelta; import os; dates = pd.date_range(start='2024-01-01', end='2024-12-30', freq='D'); sample_data = [{'日期': date, '品項': 'CSP磷', '價格': 285000 + (date.day %% 30) * 1000, '幣值': 'TWD', '來源': '示例數據'} for date in dates]; df = pd.DataFrame(sample_data); os.makedirs('data', exist_ok=True); df.to_csv('data/csp_history.csv', index=False, encoding='utf-8-sig'); df.to_excel('data/csp_history.xlsx', index=False); print(f'✅ 已創建示例數據: {len(df)} 筆')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 示例數據創建成功
    set /a passed+=1
) else (
    echo ❌ 示例數據創建失敗
)
set /a total+=1

:: 9. 測試 Streamlit 應用
echo.
echo 🚀 測試 Streamlit 應用
echo --------------------------------------------------
if exist "app.py" (
    echo ✅ 主應用程式: app.py
    set /a passed+=1
) else (
    echo ❌ 主應用程式: app.py (缺失)
)
set /a total+=1

if exist "pages\1_LME_即時報價看板.py" (
    echo ✅ LME 即時報價看板: pages\1_LME_即時報價看板.py
    set /a passed+=1
) else (
    echo ❌ LME 即時報價看板: pages\1_LME_即時報價看板.py (缺失)
)
set /a total+=1

if exist "pages\2_前日收盤.py" (
    echo ✅ 前日收盤: pages\2_前日收盤.py
    set /a passed+=1
) else (
    echo ❌ 前日收盤: pages\2_前日收盤.py (缺失)
)
set /a total+=1

if exist "pages\3_線上計算機.py" (
    echo ✅ 線上計算機: pages\3_線上計算機.py
    set /a passed+=1
) else (
    echo ❌ 線上計算機: pages\3_線上計算機.py (缺失)
)
set /a total+=1

if exist "pages\4_數據分析.py" (
    echo ✅ 數據分析: pages\4_數據分析.py
    set /a passed+=1
) else (
    echo ❌ 數據分析: pages\4_數據分析.py (缺失)
)
set /a total+=1

if exist "pages\5_系統設定.py" (
    echo ✅ 系統設定: pages\5_系統設定.py
    set /a passed+=1
) else (
    echo ❌ 系統設定: pages\5_系統設定.py (缺失)
)
set /a total+=1

if exist "pages\6_使用說明.py" (
    echo ✅ 使用說明: pages\6_使用說明.py
    set /a passed+=1
) else (
    echo ❌ 使用說明: pages\6_使用說明.py (缺失)
)
set /a total+=1

if exist "pages\8_智能報價系統.py" (
    echo ✅ 智能報價系統: pages\8_智能報價系統.py
    set /a passed+=1
) else (
    echo ❌ 智能報價系統: pages\8_智能報價系統.py (缺失)
)
set /a total+=1

:: 10. 測試數據文件
echo.
echo 📊 測試數據文件
echo --------------------------------------------------
if exist "data\csp_history.csv" (
    echo ✅ csp_history.csv 存在
    set /a passed+=1
) else (
    echo ❌ csp_history.csv 不存在
)
set /a total+=1

if exist "data\csp_history.xlsx" (
    echo ✅ csp_history.xlsx 存在
    set /a passed+=1
) else (
    echo ❌ csp_history.xlsx 不存在
)
set /a total+=1

:: 顯示測試結果
echo.
echo ============================================================
echo 📊 測試結果: %passed%/%total% 通過

if %passed% equ %total% (
    echo 🎉 所有測試通過！系統運行正常
) else (
    echo ⚠️  部分測試失敗，請檢查上述錯誤訊息
)

:: 顯示下一步操作
echo.
echo 🚀 下一步操作:
echo 1. 導入歷史數據: python import_historical_data.py
echo 2. 啟動自動記錄: python auto_update_data.py
echo 3. 啟動主應用: streamlit run app.py
echo 4. 測試數據分析: streamlit run pages/4_數據分析.py

echo.
echo 💡 測試建議:
echo - 先運行導入工具導入歷史數據
echo - 然後啟動自動記錄系統
echo - 最後測試數據分析功能

echo.
echo 📁 數據文件位置:
echo - data/csp_history.csv (主歷史數據)
echo - data/csp_history.xlsx (Excel 格式備份)
echo - auto_record.log (自動記錄日誌)

echo.
echo ✅ 測試完成！
pause
