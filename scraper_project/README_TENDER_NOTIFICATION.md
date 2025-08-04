# 標案通知服務 - 替代ntfy的解決方案

## 概述
由於無法下載ntfy，我們使用現有的通知系統（Email + Line）來實現每日標案監控通知功能。

## 解決方案特色
- ✅ 使用現有的Email和Line通知系統
- ✅ 自動監控政府標案網站
- ✅ 每日定時執行
- ✅ 支援附件（Excel檔案）
- ✅ 錯誤時自動發送錯誤通知
- ✅ 完整的日誌記錄

## 檔案說明

### 主要檔案
- `tender_notification.py` - 主要的標案通知服務
- `setup_tender_notification.py` - 快速設定腳本
- `test_notification.py` - 通知功能測試
- `test_tender_notification.bat` - Windows手動測試批次檔
- `start_tender_notification.bat` - Windows服務啟動批次檔

### 設定檔案
- `.env` - 環境變數設定（Email、Line Token等）
- `config.py` - 爬蟲和通知設定
- `tender_notification_setup.md` - 詳細設定指南

## 快速開始

### 1. 執行快速設定
```bash
python setup_tender_notification.py
```

### 2. 編輯環境變數
編輯 `.env` 檔案，填入您的Email和Line設定：
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
LINE_TOKEN=your_line_notify_token
```

### 3. 測試通知功能
```bash
python test_notification.py
```

### 4. 手動測試標案搜尋
```bash
python tender_notification.py --manual
```

### 5. 啟動每日服務
```bash
# 使用預設時間 (09:00)
python tender_notification.py

# 自訂執行時間
python tender_notification.py --schedule 14:30
```

## Windows批次檔案使用

### 手動測試
```bash
test_tender_notification.bat
```

### 啟動服務
```bash
start_tender_notification.bat
```

## 通知內容範例

### Email通知
```
主旨: 每日標案監控報告 - 2024-01-15

發現 3 個相關的政府標案：

1. 廢銅回收標案
   機關: 台北市政府
   截止日期: 2024-01-20
   預算: 100萬元
   來源: 政府電子採購網
   關鍵字: 廢銅

2. 金屬下腳料處理標案
   機關: 新北市政府
   截止日期: 2024-01-25
   預算: 50萬元
   來源: 新北市政府採購網
   關鍵字: 下腳

... 還有 1 個標案，詳見附件
```

### Line通知
```
每日標案監控報告 - 2024-01-15

發現 3 個相關的政府標案：

1. 廢銅回收標案
   機關: 台北市政府
   截止日期: 2024-01-20
   預算: 100萬元
   來源: 政府電子採購網
   關鍵字: 廢銅

2. 金屬下腳料處理標案
   機關: 新北市政府
   截止日期: 2024-01-25
   預算: 50萬元
   來源: 新北市政府採購網
   關鍵字: 下腳

... 還有 1 個標案，詳見附件
```

## 監控的網站
- 政府電子採購網
- 台北市政府採購網
- 新北市政府採購網
- 桃園市政府採購網

## 監控的關鍵字
- 下腳
- 金屬
- 銅
- 鋁
- 計量器
- 五金
- 廢料

## 系統需求
- Python 3.7+
- 網路連線
- Gmail帳號（Email通知）
- Line Notify Token（Line通知，可選）

## 故障排除

### 常見問題
1. **Email發送失敗**
   - 檢查Gmail應用程式密碼是否正確
   - 確認兩步驟驗證已開啟

2. **Line通知失敗**
   - 確認Line Token是否正確
   - 檢查網路連線

3. **爬蟲失敗**
   - 檢查網路連線
   - 查看logs目錄中的錯誤日誌

### 日誌檔案
- `logs/tender_scraper.log` - 標案爬蟲日誌
- `logs/main.log` - 通知系統日誌

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

## 與ntfy的比較

| 功能 | ntfy | 現有解決方案 |
|------|------|-------------|
| 安裝難度 | 需要下載安裝 | 使用現有系統 |
| 通知方式 | 推播通知 | Email + Line |
| 附件支援 | 有限 | 完整支援 |
| 設定複雜度 | 中等 | 簡單 |
| 可靠性 | 高 | 高 |
| 成本 | 免費 | 免費 |

## 優點
1. **無需額外安裝** - 使用現有的通知系統
2. **功能完整** - 支援Email和Line通知
3. **附件支援** - 可發送Excel檔案
4. **錯誤處理** - 自動發送錯誤通知
5. **日誌記錄** - 完整的執行記錄
6. **易於設定** - 提供快速設定腳本

## 注意事項
1. 請確保電腦在設定時間保持開機狀態
2. 建議使用穩定的網路連線
3. 定期檢查日誌檔案以確保服務正常運作
4. 如需修改通知內容格式，請編輯 `utils/notification.py`

## 未來改進
- 支援更多通知平台（Discord、Telegram等）
- 增加Webhook支援
- 優化爬蟲效能
- 增加更多政府網站監控 