@echo off
chcp 65001 >nul
echo ========================================
echo 緊急Email設定 - 立即開始標案監控
echo ========================================
echo.

echo 由於Telegram網路問題持續，建議立即設定Email通知
echo Email通知功能完整且不受網路限制影響！
echo.

echo 步驟1: 設定Gmail兩步驟驗證
echo ----------------------------------------
echo 請按照以下步驟設定：
echo.
echo 1. 開啟Gmail (https://gmail.com)
echo 2. 點擊右上角設定圖示
echo 3. 選擇「查看所有設定」
echo 4. 點擊「安全性」標籤
echo 5. 在「登入Google」區段，點擊「2步驟驗證」
echo 6. 按照指示開啟2步驟驗證
echo 7. 在「應用程式密碼」區段，點擊「應用程式密碼」
echo 8. 選擇「其他」，輸入名稱「標案監控」
echo 9. 複製產生的16位密碼
echo.

pause

echo 步驟2: 執行Email設定
echo ----------------------------------------
echo 正在執行Email設定腳本...
python setup_email_only.py

echo.
echo 步驟3: 編輯.env檔案
echo ----------------------------------------
echo 請編輯 .env 檔案，填入以下資訊：
echo.
echo SENDER_EMAIL=您的Gmail帳號@gmail.com
echo SENDER_PASSWORD=您的16位應用程式密碼
echo RECIPIENT_EMAILS=收件人Email1@example.com,收件人Email2@example.com
echo.

echo 範例：
echo SENDER_EMAIL=yourname@gmail.com
echo SENDER_PASSWORD=abcd efgh ijkl mnop
echo RECIPIENT_EMAILS=yourname@gmail.com,backup@example.com
echo.

pause

echo 步驟4: 測試Email通知
echo ----------------------------------------
echo 正在測試Email通知...
python test_email_only.py

echo.
echo 步驟5: 啟動標案監控
echo ----------------------------------------
echo 手動測試標案監控：
python tender_notification.py --manual

echo.
echo 設定每日自動執行：
echo python tender_notification.py
echo.

echo ========================================
echo Email設定完成！
echo ========================================
echo.
echo ✅ Email通知優點：
echo - 功能完整且可靠
echo - 支援附件和詳細資訊
echo - 會發送到您的手機
echo - 不受網路限制影響
echo - 可以立即開始使用
echo.
echo 💡 稍後當網路問題解決後，可以再設定Telegram Bot
echo.

pause 