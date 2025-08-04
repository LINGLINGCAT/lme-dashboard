# 標案通知服務設定指南

## 概述
這個服務會自動監控政府標案網站，搜尋相關的標案資訊，並透過Email或Line發送通知。

## 功能特色
- 自動監控政府電子採購網、台北市、新北市、桃園市政府採購網
- 支援Email和Line通知
- 可設定每日定時執行
- 自動儲存結果到Excel檔案
- 錯誤時會發送錯誤通知

## 設定步驟

### 1. 環境變數設定
在專案根目錄建立 `.env` 檔案，設定以下參數：

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

### 2. Gmail設定 (如果使用Gmail)
1. 開啟Gmail的兩步驟驗證
2. 產生應用程式密碼
3. 使用應用程式密碼作為 `SENDER_PASSWORD`

### 3. Line通知設定 (可選)
1. 前往 https://notify-bot.line.me/
2. 登入並建立新的通知群組
3. 複製Token並設定到 `LINE_TOKEN`

## 使用方法

### 手動測試
```bash
# 執行一次標案搜尋並發送通知
python tender_notification.py --manual
```

### 啟動每日定時服務
```bash
# 使用預設時間 (09:00)
python tender_notification.py

# 自訂執行時間
python tender_notification.py --schedule 14:30
```

### 使用批次檔案 (Windows)
```bash
# 手動測試
test_tender_notification.bat

# 啟動服務
start_tender_notification.bat
```

## 通知內容格式

### Email通知
- 主旨：每日標案監控報告 - YYYY-MM-DD
- 內容：包含標案摘要和詳細Excel附件

### Line通知
- 訊息：標案摘要資訊

## 監控的關鍵字
- 下腳
- 金屬
- 銅
- 鋁
- 計量器
- 五金
- 廢料

## 檔案結構
```
scraper_project/
├── tender_notification.py          # 主要通知腳本
├── start_tender_notification.bat   # Windows服務啟動器
├── test_tender_notification.bat    # 手動測試啟動器
├── data/
│   └── government_tenders.xlsx     # 標案資料檔案
└── logs/                          # 日誌檔案
```

## 故障排除

### 常見問題
1. **Email發送失敗**
   - 檢查SMTP設定是否正確
   - 確認Gmail應用程式密碼是否正確
   - 檢查防火牆設定

2. **Line通知失敗**
   - 確認Line Token是否正確
   - 檢查網路連線

3. **爬蟲失敗**
   - 檢查網路連線
   - 確認網站結構是否有變更
   - 查看logs目錄中的錯誤日誌

### 日誌檔案
- 主要日誌：`logs/tender_scraper.log`
- 通知日誌：`logs/main.log`

## 進階設定

### 修改搜尋關鍵字
編輯 `config.py` 中的 `GOVERNMENT_TENDER_KEYWORDS` 列表。

### 修改搜尋時間範圍
編輯 `config.py` 中的 `SCRAPER_CONFIG['search_days_back']` 參數。

### 自訂通知時間
```bash
# 設定每日下午2點執行
python tender_notification.py --schedule 14:00
```

## 系統需求
- Python 3.7+
- Windows/Linux/macOS
- 網路連線
- 足夠的磁碟空間儲存Excel檔案

## 注意事項
1. 請確保電腦在設定時間保持開機狀態
2. 建議使用穩定的網路連線
3. 定期檢查日誌檔案以確保服務正常運作
4. 如需修改通知內容格式，請編輯 `utils/notification.py` 