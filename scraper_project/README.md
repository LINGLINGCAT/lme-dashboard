# 自動爬蟲系統

這是一個專門用於廢銅回收業的自動爬蟲系統，能夠自動搜尋潛在客戶和監控政府標案。

## 功能特色

### 1. 廢銅潛在客戶搜尋
- 自動搜尋沖壓工廠、電線電纜廠等潛在客戶
- 支援Google搜尋和商業目錄網站搜尋
- 自動提取公司基本資訊（名稱、地址、電話、Email）
- 智能過濾相關性，避免無關結果

### 2. 政府標案監控
- 監控政府電子採購網（https://web.pcc.gov.tw/opas/aspam/public/indexAspam）
- 監控各縣市政府採購網（台北、新北、桃園等）
- 根據關鍵字自動篩選相關標案
- 只搜尋最近30天的標案資料，避免重複查詢歷史資料
- 即時通知新標案資訊

### 3. 自動化通知
- 支援Email通知（Gmail、Outlook等）
- 支援Line通知（Line Notify）
- 自動發送搜尋結果和標案資訊
- 錯誤通知和異常處理

### 4. 資料管理
- 自動儲存結果到Excel檔案
- 完整的日誌記錄
- 資料去重和整理

## 安裝設定

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
複製 `env_example.txt` 為 `.env` 並填入您的設定：

```bash
cp env_example.txt .env
```

編輯 `.env` 檔案：
```env
# Email通知設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Line通知設定 (可選)
LINE_TOKEN=your_line_notify_token
```

### 3. 安裝Chrome瀏覽器
系統使用Selenium進行網頁爬取，需要安裝Chrome瀏覽器。

## 使用方法

### 1. 執行一次完整任務
```bash
python main.py --once
```

### 2. 只執行客戶搜尋
```bash
python main.py --customer
```

### 3. 只執行標案監控
```bash
python main.py --tender
```

### 4. 啟動排程模式
```bash
python main.py --schedule
```

## 排程設定

系統預設的排程時間：
- 每天早上9:00 - 客戶搜尋
- 每天早上10:00 - 標案監控
- 每天下午14:00 - 完整任務
- 每週一早上8:00 - 完整任務

您可以在 `main.py` 中修改排程時間。

## 關鍵字設定

### 客戶搜尋關鍵字
在 `config.py` 中的 `COPPER_CUSTOMER_KEYWORDS` 可以修改：
```python
COPPER_CUSTOMER_KEYWORDS = [
    "沖壓工廠", "沖壓廠", "金屬沖壓", "精密沖壓",
    "電線電纜廠", "電纜廠", "電線廠", "電纜製造",
    "銅加工", "銅製品", "銅材加工", "銅管製造",
    "廢銅回收", "廢金屬回收", "金屬回收",
    "五金加工", "金屬加工", "機械加工"
]
```

### 標案監控關鍵字
在 `config.py` 中的 `GOVERNMENT_TENDER_KEYWORDS` 可以修改：
```python
GOVERNMENT_TENDER_KEYWORDS = [
    "計量器", "下腳", "廢五金", "廢銅", "廢金屬",
    "金屬回收", "廢料回收", "資源回收", "環保回收",
    "銅製品", "銅材", "金屬加工", "沖壓件",
    "電線電纜", "電纜", "電線", "導體"
]
```

## 檔案結構

```
scraper_project/
├── main.py                 # 主程式
├── config.py              # 設定檔
├── requirements.txt       # 依賴套件
├── env_example.txt       # 環境變數範例
├── README.md             # 說明文件
├── scrapers/             # 爬蟲模組
│   ├── customer_scraper.py  # 客戶搜尋爬蟲
│   └── tender_scraper.py    # 標案監控爬蟲
├── utils/                # 工具模組
│   ├── logger.py         # 日誌工具
│   └── notification.py   # 通知工具
├── data/                 # 資料目錄
├── logs/                 # 日誌目錄
└── exports/              # 匯出目錄
```

## 輸出檔案

### 客戶資料
- 檔案位置：`data/potential_customers.xlsx`
- 包含欄位：公司名稱、地址、電話、Email、網站、來源URL、搜尋關鍵字、識別關鍵字、搜尋日期

### 標案資料
- 檔案位置：`data/government_tenders.xlsx`
- 包含欄位：標案名稱、招標機關、截止日期、預算金額、標案狀態、來源網站、標案網址、搜尋關鍵字、搜尋日期
- 搜尋範圍：最近30天的標案資料

## 注意事項

1. **遵守網站使用條款**：請確保您的爬蟲行為符合各網站的使用條款
2. **設定適當的延遲**：避免過於頻繁的請求，建議設定2-5秒的延遲
3. **定期檢查日誌**：監控系統運行狀況和錯誤訊息
4. **備份重要資料**：定期備份客戶和標案資料
5. **更新關鍵字**：根據業務需求定期更新搜尋關鍵字

## 故障排除

### 常見問題

1. **Chrome WebDriver錯誤**
   - 確保已安裝Chrome瀏覽器
   - 檢查Chrome版本與WebDriver版本相容性

2. **Email發送失敗**
   - 檢查SMTP設定是否正確
   - 確認Gmail應用程式密碼設定

3. **爬取結果為空**
   - 檢查網路連線
   - 確認網站結構是否變更
   - 調整關鍵字設定

4. **記憶體使用過高**
   - 減少同時處理的結果數量
   - 定期清理瀏覽器實例

## 技術支援

如有問題或建議，請檢查日誌檔案或聯繫開發者。

## 授權

本專案僅供學習和研究使用，請遵守相關法律法規。 