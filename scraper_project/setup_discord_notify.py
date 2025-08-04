#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord通知設定腳本
"""

import os
import json
import requests

def setup_discord_notify():
    """設定Discord通知"""
    
    print("=" * 50)
    print("Discord通知設定")
    print("=" * 50)
    
    print("\n步驟1：建立Discord Webhook")
    print("1. 開啟Discord，進入您要接收通知的伺服器")
    print("2. 選擇一個頻道，點擊齒輪圖示（編輯頻道）")
    print("3. 點擊「整合」→「Webhook」")
    print("4. 點擊「新增Webhook」")
    print("5. 輸入Webhook名稱（例如：台鐵招標監控）")
    print("6. 複製Webhook URL")
    
    print("\n步驟2：輸入您的Discord Webhook URL")
    webhook_url = input("請輸入您的Discord Webhook URL: ").strip()
    
    if not webhook_url:
        print("未輸入Webhook URL，跳過設定")
        return
    
    # 建立設定檔案
    config = {
        "discord_webhook_url": webhook_url,
        "email_enabled": False,
        "discord_enabled": True
    }
    
    try:
        with open("notification_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Discord通知設定完成！")
        print(f"Webhook URL已儲存到: notification_config.json")
        
    except Exception as e:
        print(f"❌ 設定失敗: {e}")

def test_discord_notification():
    """測試Discord通知"""
    
    print("\n" + "=" * 50)
    print("測試Discord通知")
    print("=" * 50)
    
    # 讀取設定
    try:
        with open("notification_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        webhook_url = config.get("discord_webhook_url", "")
        if not webhook_url:
            print("❌ 未找到Discord Webhook URL，請先執行設定")
            return
        
        # 發送測試訊息
        message = {
            "content": "🔔 台鐵招標監控系統測試通知",
            "embeds": [
                {
                    "title": "測試通知",
                    "description": "這是一則測試訊息，如果您收到這則通知，表示Discord通知設定成功！",
                    "color": 0x00ff00,
                    "fields": [
                        {
                            "name": "監控時間",
                            "value": "測試時間",
                            "inline": True
                        },
                        {
                            "name": "監控網址",
                            "value": "https://www.railway.gov.tw/tra-tip-web/adr/rent-tender",
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "台鐵招標監控系統"
                    }
                }
            ]
        }
        
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 204:
            print("✅ Discord通知測試成功！")
            print("請檢查您的Discord頻道是否收到測試訊息")
        else:
            print(f"❌ Discord通知測試失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

def main():
    """主函數"""
    print("台鐵招標監控 - Discord通知設定")
    
    while True:
        print("\n請選擇操作：")
        print("1. 設定Discord通知")
        print("2. 測試Discord通知")
        print("3. 退出")
        
        choice = input("請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            setup_discord_notify()
        elif choice == "2":
            test_discord_notification()
        elif choice == "3":
            print("再見！")
            break
        else:
            print("無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 