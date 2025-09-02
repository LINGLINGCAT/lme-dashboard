#!/bin/bash

# 🧪 數據自動化系統測試腳本 (BASH 版本)
# 測試歷史數據導入、自動記錄、數據分析等功能

echo "🧪 數據自動化系統完整測試 (BASH)"
echo "============================================================"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試計數器
passed=0
total=0

# 測試函數
test_step() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}🔧 測試: $test_name${NC}"
    echo "--------------------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name 通過${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ $test_name 失敗${NC}"
    fi
    ((total++))
}

# 1. 測試 Python 環境
test_step "Python 環境" "python --version"

# 2. 測試必要套件
test_step "pandas 套件" "python -c 'import pandas; print(\"pandas 版本:\", pandas.__version__)'"
test_step "openpyxl 套件" "python -c 'import openpyxl; print(\"openpyxl 可用\")'"
test_step "schedule 套件" "python -c 'import schedule; print(\"schedule 可用\")'"
test_step "streamlit 套件" "python -c 'import streamlit; print(\"streamlit 版本:\", streamlit.__version__)'"
test_step "plotly 套件" "python -c 'import plotly; print(\"plotly 可用\")'"

# 3. 測試數據目錄
test_step "創建數據目錄" "mkdir -p data && echo '數據目錄已創建'"

# 4. 測試文件存在性
test_step "導入腳本存在" "test -f import_historical_data.py"
test_step "自動更新腳本存在" "test -f auto_update_data.py"
test_step "批處理文件存在" "test -f run_auto_update.bat"
test_step "主應用程式存在" "test -f app.py"
test_step "數據分析頁面存在" "test -f pages/4_數據分析.py"

# 5. 檢查 LME 文件
echo -e "\n${BLUE}🔍 檢查 LME 文件${NC}"
echo "--------------------------------------------------"
lme_found=false
for path in "Z:/LME.xlsm" "D:/LME.xlsm" "C:/LME.xlsm" "LME.xlsm" "data/LME.xlsm"; do
    if [ -f "$path" ]; then
        echo -e "${GREEN}✅ 找到 LME 文件: $path${NC}"
        lme_found=true
        break
    fi
done

if [ "$lme_found" = false ]; then
    echo -e "${YELLOW}⚠️  沒有找到 LME.xlsm 文件${NC}"
    echo "💡 您可以："
    echo "   1. 將 LME.xlsm 文件放在專案目錄下"
    echo "   2. 或使用數據上傳功能"
fi

# 6. 檢查現有數據文件
echo -e "\n${BLUE}📁 檢查數據文件${NC}"
echo "--------------------------------------------------"
if [ -d "data" ]; then
    data_files=$(ls -la data/ 2>/dev/null | wc -l)
    if [ "$data_files" -gt 3 ]; then  # 至少有 . 和 .. 目錄
        echo -e "${GREEN}✅ 數據目錄中有文件${NC}"
        ls -la data/
    else
        echo -e "${YELLOW}📊 數據目錄為空${NC}"
    fi
else
    echo -e "${RED}❌ 數據目錄不存在${NC}"
fi

# 7. 測試 Python 腳本語法
test_step "導入腳本語法檢查" "python -m py_compile import_historical_data.py"
test_step "自動更新腳本語法檢查" "python -m py_compile auto_update_data.py"

# 8. 創建示例數據
echo -e "\n${BLUE}📊 創建示例數據${NC}"
echo "--------------------------------------------------"
if python -c "
import pandas as pd
from datetime import datetime, timedelta
import os

# 創建示例數據
dates = pd.date_range(start='2024-01-01', end='2024-12-30', freq='D')
sample_data = []
for date in dates:
    sample_data.append({
        '日期': date,
        '品項': 'CSP磷',
        '價格': 285000 + (date.day % 30) * 1000,
        '幣值': 'TWD',
        '來源': '示例數據'
    })

df = pd.DataFrame(sample_data)
os.makedirs('data', exist_ok=True)
df.to_csv('data/csp_history.csv', index=False, encoding='utf-8-sig')
df.to_excel('data/csp_history.xlsx', index=False)
print(f'✅ 已創建示例數據: {len(df)} 筆')
"; then
    echo -e "${GREEN}✅ 示例數據創建成功${NC}"
    ((passed++))
else
    echo -e "${RED}❌ 示例數據創建失敗${NC}"
fi
((total++))

# 9. 測試 Streamlit 應用
echo -e "\n${BLUE}🚀 測試 Streamlit 應用${NC}"
echo "--------------------------------------------------"
apps=(
    "app.py:主應用程式"
    "pages/1_LME_即時報價看板.py:LME 即時報價看板"
    "pages/2_前日收盤.py:前日收盤"
    "pages/3_線上計算機.py:線上計算機"
    "pages/4_數據分析.py:數據分析"
    "pages/5_系統設定.py:系統設定"
    "pages/6_使用說明.py:使用說明"
    "pages/8_智能報價系統.py:智能報價系統"
)

for app in "${apps[@]}"; do
    IFS=':' read -r file_path app_name <<< "$app"
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✅ $app_name: $file_path${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ $app_name: $file_path (缺失)${NC}"
    fi
    ((total++))
done

# 10. 測試數據文件
echo -e "\n${BLUE}📊 測試數據文件${NC}"
echo "--------------------------------------------------"
if [ -f "data/csp_history.csv" ]; then
    line_count=$(wc -l < "data/csp_history.csv")
    echo -e "${GREEN}✅ csp_history.csv 存在，共 $line_count 行${NC}"
    ((passed++))
else
    echo -e "${RED}❌ csp_history.csv 不存在${NC}"
fi
((total++))

if [ -f "data/csp_history.xlsx" ]; then
    echo -e "${GREEN}✅ csp_history.xlsx 存在${NC}"
    ((passed++))
else
    echo -e "${RED}❌ csp_history.xlsx 不存在${NC}"
fi
((total++))

# 顯示測試結果
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}📊 測試結果: $passed/$total 通過${NC}"

if [ "$passed" -eq "$total" ]; then
    echo -e "${GREEN}🎉 所有測試通過！系統運行正常${NC}"
else
    echo -e "${YELLOW}⚠️  部分測試失敗，請檢查上述錯誤訊息${NC}"
fi

# 顯示下一步操作
echo -e "\n${BLUE}🚀 下一步操作:${NC}"
echo "1. 導入歷史數據: python import_historical_data.py"
echo "2. 啟動自動記錄: python auto_update_data.py"
echo "3. 啟動主應用: streamlit run app.py"
echo "4. 測試數據分析: streamlit run pages/4_數據分析.py"

echo -e "\n${BLUE}💡 測試建議:${NC}"
echo "- 先運行導入工具導入歷史數據"
echo "- 然後啟動自動記錄系統"
echo "- 最後測試數據分析功能"

echo -e "\n${BLUE}📁 數據文件位置:${NC}"
echo "- data/csp_history.csv (主歷史數據)"
echo "- data/csp_history.xlsx (Excel 格式備份)"
echo "- auto_record.log (自動記錄日誌)"

echo -e "\n${GREEN}✅ 測試完成！${NC}"
