# 標案通知設定指南 - 多種通知方式

## 概述
由於Line Notify已停止服務，我們提供多種免費的通知替代方案。

## 可用的通知方式

### 1. **Email通知** (推薦)
- ✅ 完全免費
- ✅ 支援附件
- ✅ 設定簡單
- ✅ 手機推播（設定Email推播）

### 2. **Telegram Bot** (最推薦)
- ✅ 完全免費
- ✅ 支援文字、圖片、檔案
- ✅ 手機推播通知
- ✅ 可以建立群組
- ✅ 不需要Play商店

### 3. **Discord Webhook**
- ✅ 免費
- ✅ 支援豐富格式
- ✅ 可以建立專用頻道

### 4. **Slack Webhook**
- ✅ 免費版本可用
- ✅ 支援檔案上傳

## 快速設定

### 1. 執行快速設定
```bash
python setup_tender_notification.py
```

### 2. 編輯環境變數
編輯 `.env` 檔案：

```env
# Email通知設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Telegram Bot設定 (推薦)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord Webhook設定 (可選)
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Slack Webhook設定 (可選)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

## 各平台設定指南

### Email設定 (Gmail)
1. 開啟Gmail的兩步驟驗證
2. 產生應用程式密碼
3. 使用應用程式密碼作為 `SENDER_PASSWORD`

### Telegram Bot設定
1. 在Telegram中搜尋 `@BotFather`
2. 發送 `/newbot` 指令
3. 輸入Bot名稱和用戶名
4. 取得Bot Token
5. 開始與Bot對話
6. 取得Chat ID
7. 設定環境變數

詳細指南請參考：`telegram_setup_guide.md`

### Discord Webhook設定
1. 建立Discord伺服器
2. 建立專用頻道
3. 設定Webhook
4. 複製Webhook URL

### Slack Webhook設定
1. 建立Slack工作區
2. 建立專用頻道
3. 設定Incoming Webhook
4. 複製Webhook URL

## 測試通知

### 測試所有通知方式
```bash
python test_notification.py
```

### 測試Telegram Bot
```bash
python test_telegram.py
```

### 手動測試標案搜尋
```bash
python tender_notification.py --manual
```

## 啟用通知方式

在 `config.py` 中修改對應的設定：

```python
# 啟用Email
"email": {
    "enabled": True,
    # ... 其他設定
}

# 啟用Telegram
"telegram": {
    "enabled": True,
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
}

# 啟用Discord
"discord": {
    "enabled": True,
    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
}

# 啟用Slack
"slack": {
    "enabled": True,
    "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "")
}
```

## 通知內容範例

### Telegram通知
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

... 還有 1 個標案，詳見附件
```

### Discord通知
```
**每日標案監控報告 - 2024-01-15**

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

## 比較表

| 功能 | Email | Telegram | Discord | Slack |
|------|-------|----------|---------|-------|
| 免費 | ✅ | ✅ | ✅ | ✅ |
| 手機推播 | ✅ | ✅ | ✅ | ✅ |
| 附件支援 | ✅ | ✅ | ✅ | ✅ |
| 群組功能 | ❌ | ✅ | ✅ | ✅ |
| 設定難度 | 簡單 | 中等 | 簡單 | 簡單 |
| 不需要Play商店 | ✅ | ✅ | ✅ | ✅ |

## 推薦設定

### 初學者
1. **Email通知** - 最簡單，支援附件
2. **Telegram Bot** - 功能最完整

### 進階使用者
1. **Telegram Bot** - 主要通知
2. **Discord Webhook** - 備用通知
3. **Email通知** - 重要通知備份

## 故障排除

### 常見問題
1. **Telegram Bot沒有回應**
   - 確認Bot Token是否正確
   - 確認Chat ID是否正確
   - 確認是否已開始對話

2. **Email發送失敗**
   - 檢查Gmail應用程式密碼
   - 確認兩步驟驗證已開啟

3. **Discord/Slack通知失敗**
   - 確認Webhook URL是否正確
   - 確認頻道權限設定

### 測試步驟
1. 先測試單一通知方式
2. 確認網路連線正常
3. 檢查日誌檔案
4. 逐步啟用多種通知

## 安全建議
1. 不要將Token分享在公開場合
2. 定期更換Bot Token
3. 使用群組時設定適當權限
4. 備份重要的設定檔案 