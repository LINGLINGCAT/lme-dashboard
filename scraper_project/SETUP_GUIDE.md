# 自動爬蟲系統設定指南

## 快速開始

### 1. 環境準備

#### 安裝Python
- 下載並安裝Python 3.8或更新版本
- 確保Python已加入系統PATH

#### 安裝Chrome瀏覽器
- 下載並安裝Google Chrome瀏覽器
- 系統會自動下載對應的ChromeDriver

### 2. 專案設定

#### 複製專案檔案
```bash
# 進入專案目錄
cd scraper_project

# 安裝依賴套件
pip install -r requirements.txt
```

#### 設定環境變數
1. 複製環境變數範例檔案：
```bash
copy env_example.txt .env
```

2. 編輯 `.env` 檔案，填入您的設定：

**Email通知設定（必填）**
```env
# Gmail設定範例
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

**Line通知設定（可選）**
```env
LINE_TOKEN=your_line_notify_token
```

### 3. Gmail應用程式密碼設定

如果您使用Gmail，需要設定應用程式密碼：

1. 登入您的Google帳戶
2. 前往「安全性」設定
3. 開啟「兩步驟驗證」
4. 建立「應用程式密碼」
5. 將產生的密碼填入 `.env` 檔案的 `SENDER_PASSWORD`

### 4. Line Notify設定（可選）

1. 前往 [Line Notify](https://notify-bot.line.me/)
2. 登入您的Line帳戶
3. 建立新的通知權杖
4. 將權杖填入 `.env` 檔案的 `LINE_TOKEN`

## 使用方式

### 方法1：使用啟動腳本（推薦）
```bash
# Windows
start.bat

# 然後選擇執行模式
```

### 方法2：直接執行Python指令
```bash
# 執行一次完整任務
python main.py --once

# 只執行客戶搜尋
python main.py --customer

# 只執行標案監控
python main.py --tender

# 啟動排程模式
python main.py --schedule

# 執行測試
python run_example.py
```

## 搜尋範圍設定

### 標案搜尋日期範圍
系統預設只搜尋最近30天的標案資料，避免重複查詢歷史資料。您可以在 `config.py` 中修改：

```python
SCRAPER_CONFIG = {
    "delay_between_requests": 2,
    "max_retries": 3,
    "timeout": 30,
    "user_agent_rotation": True,
    "save_to_excel": True,
    "save_to_database": False,
    "search_days_back": 30  # 修改這個數值來調整搜尋範圍
}
```

- `search_days_back: 7` - 只搜尋最近7天
- `search_days_back: 30` - 只搜尋最近30天（預設）
- `search_days_back: 90` - 只搜尋最近90天

## 關鍵字自訂

### 客戶搜尋關鍵字
編輯 `config.py` 檔案中的 `COPPER_CUSTOMER_KEYWORDS`：

```python
COPPER_CUSTOMER_KEYWORDS = [
    "沖壓工廠", "沖壓廠", "金屬沖壓", "精密沖壓",
    "電線電纜廠", "電纜廠", "電線廠", "電纜製造",
    "銅加工", "銅製品", "銅材加工", "銅管製造",
    "廢銅回收", "廢金屬回收", "金屬回收",
    "五金加工", "金屬加工", "機械加工",
    # 您可以添加更多關鍵字
    "您的關鍵字1", "您的關鍵字2"
]
```

### 標案監控關鍵字
編輯 `config.py` 檔案中的 `GOVERNMENT_TENDER_KEYWORDS`：

```python
GOVERNMENT_TENDER_KEYWORDS = [
    "計量器", "下腳", "廢五金", "廢銅", "廢金屬",
    "金屬回收", "廢料回收", "資源回收", "環保回收",
    "銅製品", "銅材", "金屬加工", "沖壓件",
    "電線電纜", "電纜", "電線", "導體",
    # 您可以添加更多關鍵字
    "您的關鍵字1", "您的關鍵字2"
]
```

## 排程設定

### 修改排程時間
編輯 `main.py` 檔案中的 `setup_schedule` 方法：

```python
def setup_schedule(self):
    """設定排程任務"""
    # 修改這些時間以符合您的需求
    schedule.every().day.at("09:00").do(self.run_customer_search)
    schedule.every().day.at("10:00").do(self.run_tender_monitoring)
    schedule.every().day.at("14:00").do(self.run_daily_tasks)
    schedule.every().monday.at("08:00").do(self.run_daily_tasks)
```

### 排程格式
- `schedule.every().day.at("HH:MM")` - 每天特定時間
- `schedule.every().monday.at("HH:MM")` - 每週一特定時間
- `schedule.every().hour` - 每小時
- `schedule.every(30).minutes` - 每30分鐘

## 輸出檔案說明

### 客戶資料檔案
- **位置**: `data/potential_customers.xlsx`
- **內容**: 公司基本資訊、聯絡方式、搜尋來源等

### 標案資料檔案
- **位置**: `data/government_tenders.xlsx`
- **內容**: 標案資訊、招標機關、截止日期、預算等

### 日誌檔案
- **位置**: `logs/` 目錄
- **格式**: `scraper_main_YYYY-MM-DD.log`
- **內容**: 系統運行日誌、錯誤訊息等

## 故障排除

### 常見問題

#### 1. Chrome WebDriver錯誤
**問題**: `WebDriverException: Message: unknown error: cannot find Chrome binary`
**解決方案**:
- 確保已安裝Chrome瀏覽器
- 重新安裝Chrome瀏覽器
- 檢查Chrome版本與WebDriver相容性

#### 2. Email發送失敗
**問題**: `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`
**解決方案**:
- 確認Gmail應用程式密碼設定正確
- 檢查兩步驟驗證是否已開啟
- 確認Email地址和密碼無誤

#### 3. 爬取結果為空
**問題**: 搜尋結果為空或很少
**解決方案**:
- 檢查網路連線
- 調整關鍵字設定
- 增加搜尋結果數量限制
- 檢查網站結構是否變更

#### 4. 記憶體使用過高
**問題**: 程式執行時記憶體使用過高
**解決方案**:
- 減少同時處理的結果數量
- 增加請求間隔時間
- 定期重啟程式

### 效能優化

#### 1. 調整請求間隔
編輯 `config.py` 中的 `SCRAPER_CONFIG`：

```python
SCRAPER_CONFIG = {
    "delay_between_requests": 3,  # 增加延遲時間
    "max_retries": 3,
    "timeout": 30,
    "user_agent_rotation": True,
    "save_to_excel": True,
    "save_to_database": False
}
```

#### 2. 限制搜尋結果
在爬蟲程式中調整結果數量限制：

```python
# 在 customer_scraper.py 中
google_results = self.search_google(keyword, max_results=20)  # 減少結果數量

# 在 tender_scraper.py 中
for row in tender_rows[:10]:  # 減少處理數量
```

## 安全注意事項

1. **保護敏感資訊**: 不要將 `.env` 檔案上傳到公開的程式碼庫
2. **遵守網站條款**: 確保爬蟲行為符合各網站的使用條款
3. **合理使用**: 避免過於頻繁的請求，以免對目標網站造成負擔
4. **定期備份**: 定期備份重要的客戶和標案資料

## 技術支援

如果遇到問題：

1. 檢查日誌檔案 (`logs/` 目錄)
2. 執行測試程式 (`python run_example.py`)
3. 確認環境設定是否正確
4. 檢查網路連線和目標網站狀態

## 更新記錄

- v1.0.0: 初始版本，支援客戶搜尋和標案監控
- 支援Email和Line通知
- 支援自動排程執行
- 完整的日誌記錄和錯誤處理 