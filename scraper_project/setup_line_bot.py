#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE Bot通知設定腳本
"""

import os
import json
import requests

def setup_line_bot():
    """設定LINE Bot通知"""
    
    print("=" * 50)
    print("LINE Bot通知設定")
    print("=" * 50)
    
    print("\n步驟1：建立LINE Bot")
    print("1. 前往 https://developers.line.biz/")
    print("2. 使用LINE帳號登入")
    print("3. 點擊「Create a new provider」")
    print("4. 輸入Provider名稱（例如：台鐵招標監控）")
    print("5. 點擊「Create a new channel」→「Messaging API」")
    print("6. 輸入Channel名稱和描述")
    print("7. 複製Channel Access Token")
    print("8. 複製Channel Secret")
    
    print("\n步驟2：輸入您的LINE Bot設定")
    channel_token = input("請輸入Channel Access Token: ").strip()
    channel_secret = input("請輸入Channel Secret: ").strip()
    
    if not channel_token or not channel_secret:
        print("未輸入完整設定，跳過設定")
        return
    
    # 建立設定檔案
    config = {
        "line_channel_token": channel_token,
        "line_channel_secret": channel_secret,
        "email_enabled": False,
        "line_bot_enabled": True
    }
    
    try:
        with open("notification_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ LINE Bot通知設定完成！")
        print(f"設定已儲存到: notification_config.json")
        print("\n注意：您需要將LINE Bot加入聊天室才能接收通知")
        
    except Exception as e:
        print(f"❌ 設定失敗: {e}")

def test_line_bot_notification():
    """測試LINE Bot通知"""
    
    print("\n" + "=" * 50)
    print("測試LINE Bot通知")
    print("=" * 50)
    
    # 讀取設定
    try:
        with open("notification_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        channel_token = config.get("line_channel_token", "")
        if not channel_token:
            print("❌ 未找到LINE Bot Token，請先執行設定")
            return
        
        # 發送測試訊息
        message = {
            "type": "text",
            "text": "🔔 台鐵招標監控系統測試通知\n\n這是一則測試訊息，如果您收到這則通知，表示LINE Bot通知設定成功！\n\n監控時間: 測試時間\n監控網址: https://www.railway.gov.tw/tra-tip-web/adr/rent-tender"
        }
        
        headers = {
            'Authorization': f"Bearer {channel_token}",
            'Content-Type': 'application/json'
        }
        
        # 注意：這裡需要實際的用戶ID或群組ID
        # 在實際使用中，需要先獲取用戶ID
        print("⚠️  注意：LINE Bot需要知道要發送給誰")
        print("請將LINE Bot加入聊天室，並提供用戶ID或群組ID")
        user_id = input("請輸入用戶ID或群組ID（留空跳過測試）: ").strip()
        
        if user_id:
            data = {
                "to": user_id,
                "messages": [message]
            }
            
            response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
            
            if response.status_code == 200:
                print("✅ LINE Bot通知測試成功！")
                print("請檢查您的LINE聊天室是否收到測試訊息")
            else:
                print(f"❌ LINE Bot通知測試失敗: {response.status_code}")
                print(f"錯誤訊息: {response.text}")
        else:
            print("跳過測試")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

def main():
    """主函數"""
    print("台鐵招標監控 - LINE Bot通知設定")
    
    while True:
        print("\n請選擇操作：")
        print("1. 設定LINE Bot通知")
        print("2. 測試LINE Bot通知")
        print("3. 退出")
        
        choice = input("請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            setup_line_bot()
        elif choice == "2":
            test_line_bot_notification()
        elif choice == "3":
            print("再見！")
            break
        else:
            print("無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 