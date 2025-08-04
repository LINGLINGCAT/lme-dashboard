#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LINE通知設定腳本
"""

import os
import json

def setup_line_notify():
    """設定LINE通知"""
    
    print("=" * 50)
    print("LINE通知設定")
    print("=" * 50)
    
    print("\n步驟1：取得LINE Notify Token")
    print("1. 前往 https://notify-bot.line.me/")
    print("2. 使用LINE帳號登入")
    print("3. 點擊「發行存取權杖」")
    print("4. 輸入服務名稱（例如：台鐵招標監控）")
    print("5. 選擇要接收通知的聊天室")
    print("6. 複製產生的Token")
    
    print("\n步驟2：輸入您的LINE Token")
    token = input("請輸入您的LINE Token: ").strip()
    
    if not token:
        print("未輸入Token，跳過設定")
        return
    
    # 建立設定檔案
    config = {
        "line_token": token,
        "email_enabled": False,
        "line_enabled": True
    }
    
    try:
        with open("notification_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ LINE通知設定完成！")
        print(f"Token已儲存到: notification_config.json")
        
        # 設定環境變數
        os.environ["LINE_TOKEN"] = token
        print("環境變數已設定")
        
    except Exception as e:
        print(f"❌ 設定失敗: {e}")

def test_line_notification():
    """測試LINE通知"""
    
    import requests
    
    print("\n" + "=" * 50)
    print("測試LINE通知")
    print("=" * 50)
    
    # 讀取設定
    try:
        with open("notification_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        token = config.get("line_token", "")
        if not token:
            print("❌ 未找到LINE Token，請先執行設定")
            return
        
        # 發送測試訊息
        message = "🔔 台鐵招標監控系統測試通知\n\n這是一則測試訊息，如果您收到這則通知，表示LINE通知設定成功！\n\n監控時間: 測試時間\n監控網址: https://www.railway.gov.tw/tra-tip-web/adr/rent-tender"
        
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'message': message
        }
        
        response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
        
        if response.status_code == 200:
            print("✅ LINE通知測試成功！")
            print("請檢查您的LINE聊天室是否收到測試訊息")
        else:
            print(f"❌ LINE通知測試失敗: {response.status_code}")
            print(f"錯誤訊息: {response.text}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

def main():
    """主函數"""
    print("台鐵招標監控 - LINE通知設定")
    
    while True:
        print("\n請選擇操作：")
        print("1. 設定LINE通知")
        print("2. 測試LINE通知")
        print("3. 退出")
        
        choice = input("請輸入選項 (1-3): ").strip()
        
        if choice == "1":
            setup_line_notify()
        elif choice == "2":
            test_line_notification()
        elif choice == "3":
            print("再見！")
            break
        else:
            print("無效的選項，請重新選擇")

if __name__ == "__main__":
    main() 