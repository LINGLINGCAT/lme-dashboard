# Telegram Bot 設定指南

## 概述
Telegram Bot是一個免費且功能強大的通知工具，可以發送文字訊息、圖片和檔案。

## 設定步驟

### 1. 建立Telegram Bot

1. **開啟Telegram**
   - 在手機或電腦上開啟Telegram應用程式

2. **搜尋BotFather**
   - 在Telegram中搜尋 `@BotFather`
   - 點擊開始對話

3. **建立新Bot**
   - 發送 `/newbot` 指令
   - 輸入Bot名稱（例如：標案監控機器人）
   - 輸入Bot用戶名（例如：tender_monitor_bot）
   - 系統會回傳Bot Token，請保存下來

### 2. 取得Chat ID

#### 方法一：個人聊天
1. 搜尋您剛才建立的Bot
2. 點擊開始對話
3. 發送任意訊息
4. 在瀏覽器開啟：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. 找到 `"chat":{"id":` 後面的數字就是您的Chat ID

#### 方法二：群組聊天
1. 建立一個Telegram群組
2. 將Bot加入群組
3. 在群組中發送訊息
4. 使用相同方法取得群組的Chat ID

### 3. 設定環境變數

在 `.env` 檔案中添加：

```env
# Telegram Bot設定
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. 啟用Telegram通知

在 `config.py` 中修改：

```python
"telegram": {
    "enabled": True,  # 改為True
    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
}
```

## 測試Bot

### 手動測試
```bash
python test_telegram.py
```

### 測試腳本
```python
from utils.advanced_notification import AdvancedNotificationManager

manager = AdvancedNotificationManager()
result = manager.send_telegram_notification("測試訊息")
print(f"發送結果: {'成功' if result else '失敗'}")
```

## 優點
- ✅ 完全免費
- ✅ 支援文字、圖片、檔案
- ✅ 可以建立群組通知
- ✅ 支援HTML格式
- ✅ 手機推播通知
- ✅ 不需要Play商店

## 注意事項
1. Bot Token要保密，不要分享給他人
2. Chat ID可能是負數（群組）或正數（個人）
3. 首次使用時需要先發送訊息給Bot

## 故障排除

### 常見問題
1. **Bot沒有回應**
   - 確認Bot Token是否正確
   - 確認Chat ID是否正確

2. **無法發送訊息**
   - 確認Bot是否已開始對話
   - 確認群組中Bot是否有權限

3. **找不到Chat ID**
   - 先發送訊息給Bot
   - 再使用getUpdates API

## 進階功能

### 群組通知
- 建立專門的Telegram群組
- 將Bot加入群組
- 設定群組的Chat ID

### 多個通知目標
- 可以設定多個Chat ID
- 支援個人和群組同時通知

### 檔案上傳
- 支援Excel檔案附件
- 支援圖片和文件

## 安全建議
1. 定期更換Bot Token
2. 不要將Token分享在公開場合
3. 使用群組時設定適當的權限 