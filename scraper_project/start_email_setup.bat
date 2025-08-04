@echo off
chcp 65001 >nul
echo ========================================
echo 標案監控系統 - Email通知設定
echo ========================================
echo.

echo 由於Telegram網路問題，先設定Email通知
echo Email通知功能完整且可靠！
echo.

echo 步驟1: 設定Gmail兩步驟驗證
echo ----------------------------------------
echo 1. 開啟Gmail
echo 2. 前往設定 > 安全性
echo 3. 開啟兩步驟驗證
echo 4. 產生應用程式密碼
echo.

echo 步驟2: 設定Email通知
echo ----------------------------------------
echo 執行Email設定腳本...
python setup_email_only.py

echo.
echo 步驟3: 編輯.env檔案
echo ----------------------------------------
echo 請編輯 .env 檔案，填入以下資訊：
echo.
echo SENDER_EMAIL=您的Gmail帳號
echo SENDER_PASSWORD=您的應用程式密碼
echo RECIPIENT_EMAILS=收件人Email1,收件人Email2
echo.

echo 步驟4: 測試Email通知
echo ----------------------------------------
echo 執行測試...
python test_email_only.py

echo.
echo 步驟5: 啟動標案監控
echo ----------------------------------------
echo 手動測試: python tender_notification.py --manual
echo 自動執行: python tender_notification.py
echo.

echo ========================================
echo Email設定完成！
echo ========================================
echo.
echo 💡 提示：
echo - Email通知會發送到您的手機
echo - 支援附件和詳細資訊
echo - 稍後網路問題解決後可再設定Telegram
echo.

pause 