# 三層通知系統完整指南
## Telegram Bot + Discord + Email備份

### 🎯 系統架構
```
第一層 - Telegram Bot (主要通知)
    ↓
第二層 - Discord (備用通知)
    ↓
第三層 - Email (重要備份)
```

### 🚀 快速開始

#### 1. 執行設定腳本
```bash
# Windows
setup_triple_notification.bat

# 或手動執行
python setup_triple_notification.py
```

#### 2. 設定各平台

##### Telegram Bot (第一層 - 主要通知)
1. 在Telegram中搜尋 `@BotFather`
2. 發送 `/newbot` 指令
3. 輸入Bot名稱和用戶名
4. 取得Bot Token
5. 開始與Bot對話
6. 取得Chat ID
7. 設定到 `.env` 檔案

##### Discord Webhook (第二層 - 備用通知)
1. 前往 https://discord.com/
2. 建立新伺服器
3. 建立專用頻道
4. 設定Webhook
5. 複製Webhook URL
6. 設定到 `.env` 檔案

##### Email (第三層 - 重要備份)
1. 開啟Gmail兩步驟驗證
2. 產生應用程式密碼
3. 設定到 `.env` 檔案

#### 3. 編輯環境變數
編輯 `.env` 檔案：
```env
# Email通知設定 (第三層 - 重要備份)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Telegram Bot設定 (第一層 - 主要通知)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord Webhook設定 (第二層 - 備用通知)
DISCORD_WEBHOOK_URL=your_discord_webhook_url
```

#### 4. 測試通知系統
```bash
# 測試全部三層通知
python test_triple_notification.py

# 測試單一平台
python test_telegram.py
python test_discord.py
python test_email.py
```

#### 5. 啟動服務
```bash
# 手動測試標案搜尋
python tender_notification.py --manual

# 啟動每日服務
python tender_notification.py

# 自訂執行時間
python tender_notification.py --schedule 14:30
```

### 📋 詳細設定指南

#### Telegram Bot設定
- 參考：`telegram_setup_guide.md`
- 優點：手機推播、群組功能、檔案支援
- 建議：作為主要通知方式

#### Discord Webhook設定
- 參考：`discord_setup_guide.md`
- 優點：豐富格式、權限管理、多頻道
- 建議：作為備用通知方式

#### Email設定
- 優點：可靠、支援附件、備份功能
- 建議：作為重要通知備份

### 🔧 故障排除

#### 常見問題

1. **Telegram Bot沒有回應**
   - 確認Bot Token是否正確
   - 確認Chat ID是否正確
   - 確認是否已開始對話

2. **Discord Webhook失敗**
   - 確認Webhook URL是否正確
   - 確認頻道權限設定
   - 確認伺服器是否正常

3. **Email發送失敗**
   - 檢查Gmail應用程式密碼
   - 確認兩步驟驗證已開啟
   - 檢查SMTP設定

#### 測試步驟
1. 先測試單一通知方式
2. 確認網路連線正常
3. 檢查日誌檔案
4. 逐步啟用多種通知

### 📊 通知內容範例

#### Telegram通知
```
🔔 每日標案監控報告 - 2024-01-15

📋 發現 3 個相關的政府標案：

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

✅ 通知發送完成
```

#### Discord通知
```
**🔔 每日標案監控報告 - 2024-01-15**

📋 發現 3 個相關的政府標案：

1. 廢銅回收標案
   - 機關: 台北市政府
   - 截止日期: 2024-01-20
   - 預算: 100萬元
   - 來源: 政府電子採購網
   - 關鍵字: 廢銅

2. 金屬下腳料處理標案
   - 機關: 新北市政府
   - 截止日期: 2024-01-25
   - 預算: 50萬元
   - 來源: 新北市政府採購網
   - 關鍵字: 下腳

✅ 通知發送完成
```

#### Email通知
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

### 🎯 最佳實踐

#### 通知策略
- **主要通知**：Telegram Bot（手機推播）
- **備用通知**：Discord（桌面通知）
- **重要備份**：Email（可靠備份）

#### 頻率設定
- **每日通知**：標案搜尋結果
- **即時通知**：錯誤訊息
- **定期通知**：系統狀態

#### 安全建議
1. 不要將Token分享在公開場合
2. 定期更換Bot Token
3. 設定適當的權限
4. 監控通知使用情況

### 📁 檔案結構
```
scraper_project/
├── setup_triple_notification.py      # 三層通知設定腳本
├── setup_triple_notification.bat     # Windows設定批次檔
├── test_triple_notification.py       # 三層通知測試
├── test_telegram.py                  # Telegram測試
├── test_discord.py                   # Discord測試
├── test_email.py                     # Email測試
├── tender_notification.py            # 主要通知服務
├── utils/
│   └── advanced_notification.py      # 進階通知模組
├── telegram_setup_guide.md           # Telegram設定指南
├── discord_setup_guide.md            # Discord設定指南
├── notification_setup_guide.md       # 通知設定指南
└── TRIPLE_NOTIFICATION_GUIDE.md     # 本指南
```

### 🎉 完成檢查清單

- [ ] 執行設定腳本
- [ ] 設定Telegram Bot
- [ ] 設定Discord Webhook
- [ ] 設定Email
- [ ] 編輯.env檔案
- [ ] 測試單一通知
- [ ] 測試全部通知
- [ ] 手動測試標案搜尋
- [ ] 啟動每日服務

### 💡 進階功能

#### 自訂通知時間
```bash
# 設定每日下午2點執行
python tender_notification.py --schedule 14:00
```

#### 修改搜尋關鍵字
編輯 `config.py` 中的 `GOVERNMENT_TENDER_KEYWORDS` 列表。

#### 修改搜尋時間範圍
編輯 `config.py` 中的 `SCRAPER_CONFIG['search_days_back']` 參數。

### 🆘 支援

如果遇到問題，請：
1. 檢查日誌檔案
2. 執行測試腳本
3. 參考各平台設定指南
4. 確認網路連線正常

---

**🎯 三層通知系統確保您不會錯過任何重要標案！** 