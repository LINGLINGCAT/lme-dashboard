# -*- coding: utf-8 -*-
"""
Telegram Bot 測試腳本
"""

import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.advanced_notification import AdvancedNotificationManager

def test_telegram():
    """測試Telegram Bot"""
    print("Telegram Bot 測試")
    print("=" * 30)
    
    # 建立通知管理器
    manager = AdvancedNotificationManager()
    
    # 測試訊息
    test_message = """🔔 標案監控測試通知

📋 發現 2 個相關的政府標案：

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

✅ 測試完成！"""
    
    print("發送測試訊息...")
    result = manager.send_telegram_notification(test_message)
    
    if result:
        print("✅ Telegram通知發送成功！")
        print("請檢查您的Telegram是否收到訊息")
    else:
        print("❌ Telegram通知發送失敗")
        print("請檢查以下設定：")
        print("1. Bot Token是否正確")
        print("2. Chat ID是否正確")
        print("3. 是否已開始與Bot對話")
        print("4. 網路連線是否正常")

def check_telegram_config():
    """檢查Telegram設定"""
    print("\n檢查Telegram設定...")
    
    from config import NOTIFICATION_CONFIG
    
    telegram_config = NOTIFICATION_CONFIG.get('telegram', {})
    
    print(f"Telegram啟用狀態: {'✅ 已啟用' if telegram_config.get('enabled', False) else '❌ 未啟用'}")
    print(f"Bot Token: {'✅ 已設定' if telegram_config.get('bot_token') else '❌ 未設定'}")
    print(f"Chat ID: {'✅ 已設定' if telegram_config.get('chat_id') else '❌ 未設定'}")
    
    if not telegram_config.get('enabled', False):
        print("\n要啟用Telegram通知，請在config.py中設定：")
        print('"telegram": {')
        print('    "enabled": True,')
        print('    "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),')
        print('    "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")')
        print('}')

def main():
    """主函數"""
    print("Telegram Bot 設定檢查")
    print("=" * 40)
    
    # 檢查設定
    check_telegram_config()
    
    # 詢問是否要測試
    test = input("\n是否要發送測試訊息？(y/N): ").lower()
    if test == 'y':
        test_telegram()
    else:
        print("跳過測試")

if __name__ == "__main__":
    main() 