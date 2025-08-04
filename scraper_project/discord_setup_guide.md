# Discord Webhook 設定指南

## 概述
Discord Webhook是一個免費且功能強大的通知工具，可以發送文字訊息、圖片和檔案到Discord頻道。

## 設定步驟

### 1. 建立Discord伺服器

1. **開啟Discord**
   - 在瀏覽器中前往 https://discord.com/
   - 登入或註冊帳號

2. **建立新伺服器**
   - 點擊左側的 "+" 按鈕
   - 選擇 "建立伺服器"
   - 輸入伺服器名稱（例如：標案監控中心）
   - 選擇伺服器類型（建議選擇 "社群"）

### 2. 建立專用頻道

1. **建立通知頻道**
   - 在伺服器中右鍵點擊
   - 選擇 "建立頻道"
   - 輸入頻道名稱（例如：#標案通知）
   - 選擇頻道類型為 "文字頻道"

2. **設定頻道權限**
   - 右鍵點擊頻道
   - 選擇 "編輯頻道"
   - 在 "權限" 標籤中設定適當權限

### 3. 設定Webhook

1. **開啟頻道設定**
   - 右鍵點擊通知頻道
   - 選擇 "編輯頻道"

2. **建立Webhook**
   - 點擊 "整合" 標籤
   - 點擊 "Webhook"
   - 點擊 "新增Webhook"

3. **設定Webhook**
   - 輸入Webhook名稱（例如：標案監控機器人）
   - 選擇頭像（可選）
   - 點擊 "複製Webhook URL"
   - 保存這個URL

### 4. 設定環境變數

在 `.env` 檔案中添加：

```env
# Discord Webhook設定
DISCORD_WEBHOOK_URL=your_webhook_url_here
```

### 5. 啟用Discord通知

在 `config.py` 中確認設定：

```python
"discord": {
    "enabled": True,
    "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
}
```

## 測試Webhook

### 手動測試
```bash
python test_discord.py
```

### 測試腳本
```python
from utils.advanced_notification import AdvancedNotificationManager

manager = AdvancedNotificationManager()
result = manager.send_discord_notification("**測試訊息**")
print(f"發送結果: {'成功' if result else '失敗'}")
```

## 優點
- ✅ 完全免費
- ✅ 支援文字、圖片、檔案
- ✅ 可以建立多個頻道
- ✅ 支援豐富的訊息格式
- ✅ 可以設定權限
- ✅ 不需要Play商店

## 進階功能

### 多個通知頻道
- 可以建立多個Webhook
- 不同類型的通知發送到不同頻道

### 權限管理
- 可以設定誰能看到通知
- 可以設定機器人權限

### 訊息格式
- 支援Markdown格式
- 支援表情符號
- 支援嵌入訊息

## 故障排除

### 常見問題
1. **Webhook沒有回應**
   - 確認Webhook URL是否正確
   - 確認頻道權限設定
   - 確認伺服器是否正常

2. **無法發送訊息**
   - 確認Webhook是否已建立
   - 確認頻道是否存在
   - 確認網路連線

3. **訊息格式錯誤**
   - 檢查Markdown語法
   - 確認訊息長度限制

## 安全建議
1. 不要將Webhook URL分享在公開場合
2. 定期更換Webhook
3. 設定適當的頻道權限
4. 監控Webhook使用情況

## 最佳實踐

### 頻道組織
```
# 標案通知 - 主要通知
# 錯誤通知 - 錯誤訊息
# 系統狀態 - 系統狀態
# 測試頻道 - 測試用
```

### 訊息格式
```markdown
**🔔 標案監控通知**

📋 發現 3 個相關標案：

1. 廢銅回收標案
   - 機關: 台北市政府
   - 截止日期: 2024-01-20
   - 預算: 100萬元

2. 金屬下腳料處理標案
   - 機關: 新北市政府
   - 截止日期: 2024-01-25
   - 預算: 50萬元

✅ 通知發送完成
```

### 通知頻率
- 主要通知：每日一次
- 錯誤通知：即時發送
- 系統狀態：每小時一次 