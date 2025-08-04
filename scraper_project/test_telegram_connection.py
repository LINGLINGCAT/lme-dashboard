# -*- coding: utf-8 -*-
"""
測試Telegram連線
"""

import requests
import time

def test_telegram_connection():
    """測試Telegram連線"""
    print("🔍 測試Telegram連線...")
    print("=" * 40)
    
    # 測試不同的Telegram端點
    test_urls = [
        ("Telegram Web", "https://web.telegram.org"),
        ("Telegram API", "https://api.telegram.org"),
        ("BotFather", "https://t.me/botfather"),
        ("Telegram Main", "https://telegram.org")
    ]
    
    success_count = 0
    
    for name, url in test_urls:
        try:
            print(f"測試 {name}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: 連線成功")
                success_count += 1
            else:
                print(f"⚠️  {name}: 狀態碼 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: 連線失敗 - {e}")
    
    print("\n" + "=" * 40)
    print(f"測試結果: {success_count}/{len(test_urls)} 成功")
    
    if success_count >= 2:
        print("✅ Telegram連線正常，可以設定Telegram Bot")
        return True
    else:
        print("❌ Telegram連線有問題，建議先設定Email通知")
        return False

def suggest_next_steps(telegram_works):
    """建議下一步"""
    print("\n💡 建議下一步：")
    print("=" * 30)
    
    if telegram_works:
        print("1. 設定Telegram Bot：")
        print("   - 前往 https://t.me/botfather")
        print("   - 發送 /newbot 指令")
        print("   - 設定Bot名稱和用戶名")
        print("   - 取得Bot Token")
        print()
        print("2. 設定Chat ID：")
        print("   - 與您的Bot對話")
        print("   - 發送 /start 指令")
        print("   - 取得Chat ID")
        print()
        print("3. 測試Telegram通知：")
        print("   python test_telegram.py")
    else:
        print("1. 立即設定Email通知：")
        print("   python setup_email_only.py")
        print()
        print("2. 設定Gmail兩步驟驗證")
        print("3. 編輯.env檔案")
        print("4. 測試Email通知：")
        print("   python test_email_only.py")
        print()
        print("5. 啟動標案監控：")
        print("   python tender_notification.py --manual")

def main():
    """主函數"""
    print("Telegram連線測試工具")
    print("=" * 30)
    print()
    
    # 測試Telegram連線
    telegram_works = test_telegram_connection()
    
    # 建議下一步
    suggest_next_steps(telegram_works)
    
    print("\n" + "=" * 40)
    print("測試完成！")

if __name__ == "__main__":
    main() 