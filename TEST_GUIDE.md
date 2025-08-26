# 🧪 數據自動化系統測試指南

## 📋 測試概述

本指南將幫助您測試數據自動化系統的所有功能，確保系統正常運行。

## 🚀 快速測試

### 1. 運行完整測試

#### Python 版本
```bash
python test_data_automation.py
```

#### BASH 版本 (Linux/Mac)
```bash
chmod +x test_system.sh
./test_system.sh
```

#### Windows 批處理版本
```cmd
test_system.bat
```

這些腳本會自動測試：
- ✅ 環境設定和套件安裝
- ✅ 數據目錄結構
- ✅ 歷史數據導入工具
- ✅ 自動更新工具
- ✅ 數據分析頁面
- ✅ Streamlit 應用
- ✅ 創建示例數據

## 📤 測試歷史數據導入

### 方法一：使用導入工具
```bash
# 1. 將 LME.xlsm 文件放在專案目錄下
# 2. 運行導入工具
python import_historical_data.py
```

### 方法二：手動上傳
1. 啟動數據分析頁面：`streamlit run pages/4_數據分析.py`
2. 在頁面上傳 CSV 或 Excel 文件
3. 系統會自動保存到 data 目錄

## ⏰ 測試自動記錄功能

### 1. 啟動自動記錄系統
```bash
# 方法一：直接運行
python auto_update_data.py

# 方法二：使用批處理文件
run_auto_update.bat
```

### 2. 測試定時記錄
- 系統會在每天 09:00 和 17:00 自動記錄
- 可以修改時間進行測試
- 檢查 `data/csp_history.csv` 文件是否有新記錄

### 3. 檢查日誌
```bash
# 查看自動記錄日誌
cat auto_record.log
```

## 📊 測試數據分析功能

### 1. 啟動數據分析頁面
```bash
streamlit run pages/4_數據分析.py
```

### 2. 測試功能
- ✅ 查看歷史數據圖表
- ✅ 測試價格趨勢分析
- ✅ 測試波動性分析
- ✅ 測試相關性分析
- ✅ 測試數據下載功能

## 🔧 測試各個頁面

### 1. 主應用程式
```bash
streamlit run app.py
```
測試：
- ✅ 登入功能
- ✅ 頁面導航
- ✅ 權限控制

### 2. LME 即時報價看板
```bash
streamlit run pages/1_LME_即時報價看板.py
```
測試：
- ✅ 即時數據顯示
- ✅ 自動更新功能
- ✅ 數據格式正確

### 3. 前日收盤
```bash
streamlit run pages/2_前日收盤.py
```
測試：
- ✅ 歷史數據顯示
- ✅ 數據保存功能
- ✅ 圖表顯示

### 4. 線上計算機
```bash
streamlit run pages/3_線上計算機.py
```
測試：
- ✅ 成分計算
- ✅ LME 係數計算
- ✅ 現價計算

### 5. 智能報價系統
```bash
streamlit run pages/8_智能報價系統.py
```
測試：
- ✅ 客戶管理
- ✅ 報價管理
- ✅ PDF 生成

## 📁 檢查數據文件

### 1. 檢查 data 目錄
```bash
ls -la data/
```

應該看到：
- `csp_history.csv` - 主歷史數據
- `csp_history.xlsx` - Excel 格式備份
- `lme_historical_data_*.csv` - 導入的歷史數據
- `auto_record.log` - 自動記錄日誌

### 2. 檢查數據品質
```bash
# 查看數據行數
wc -l data/csp_history.csv

# 查看數據內容
head -10 data/csp_history.csv
```

## 🐛 常見問題排除

### 1. 套件缺失
```bash
pip install pandas openpyxl schedule requests plotly streamlit numpy
```

### 2. 權限問題
```bash
# Windows
icacls data /grant Everyone:F

# Linux/Mac
chmod 755 data/
```

### 3. 數據文件損壞
```bash
# 刪除損壞文件，重新導入
rm data/csp_history.csv
python import_historical_data.py
```

### 4. 自動記錄不工作
```bash
# 檢查日誌
tail -f auto_record.log

# 手動測試記錄
python -c "from auto_update_data import record_lme_data; record_lme_data()"
```

## 📊 測試檢查清單

### 環境測試
- [ ] Python 環境正常
- [ ] 所有套件已安裝
- [ ] 數據目錄可寫入

### 數據導入測試
- [ ] LME.xlsm 文件可讀取
- [ ] 數據格式正確
- [ ] 數據已保存到 data 目錄

### 自動記錄測試
- [ ] 自動記錄腳本可運行
- [ ] 定時記錄功能正常
- [ ] 日誌文件正常生成

### 數據分析測試
- [ ] 數據分析頁面可訪問
- [ ] 圖表正常顯示
- [ ] 數據下載功能正常

### 應用程式測試
- [ ] 主應用程式正常啟動
- [ ] 所有頁面可訪問
- [ ] 權限控制正常

## 🎯 測試目標

完成所有測試後，您應該能夠：
1. ✅ 成功導入 LME.xlsm 中的歷史數據
2. ✅ 自動記錄系統正常運行
3. ✅ 數據分析功能完整可用
4. ✅ 所有頁面功能正常
5. ✅ 系統完全獨立於本地伺服器

## 📞 技術支援

如果遇到問題：
1. 檢查錯誤日誌
2. 運行測試腳本
3. 查看 README.md 文件
4. 檢查數據文件格式
