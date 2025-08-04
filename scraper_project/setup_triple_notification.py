# -*- coding: utf-8 -*-
"""
三層通知系統設定腳本
Telegram Bot + Discord + Email備份
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def create_triple_notification_env():
    """建立三層通知系統的.env檔案"""
    env_content = """# 三層通知系統環境變數設定
# Telegram Bot + Discord + Email備份

# Email通知設定 (第三層 - 重要備份)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Telegram Bot設定 (第一層 - 主要通知)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord Webhook設定 (第二層 - 備用通知)
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Slack Webhook設定 (可選)
SLACK_WEBHOOK_URL=your_slack_webhook_url
"""
    
    env_file = project_root / ".env"
    
    if env_file.exists():
        print("發現現有的.env檔案")
        overwrite = input("是否要覆蓋現有的.env檔案？(y/N): ").lower()
        if overwrite != 'y':
            print("跳過.env檔案建立")
            return
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"已建立三層通知系統的.env檔案: {env_file}")
        print("請編輯此檔案並填入您的實際設定值")
    except Exception as e:
        print(f"建立.env檔案失敗: {e}")

def update_config_for_triple_notification():
    """更新config.py以啟用三層通知"""
    config_file = project_root / "config.py"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新通知設定
        new_notification_config = '''# 通知設定 - 三層通知系統
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": True,  # 第三層 - 重要備份
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "sender_email": os.getenv("SENDER_EMAIL", ""),
        "sender_password": os.getenv("SENDER_PASSWORD", ""),
        "recipient_emails": os.getenv("RECIPIENT_EMAILS", "").split(",")
    },
    "telegram": {
        "enabled": True,  # 第一層 - 主要通知
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    },
    "discord": {
        "enabled": True,  # 第二層 - 備用通知
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
    },
    "slack": {
        "enabled": False,  # 可選
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "")
    }
}'''
        
        # 替換通知設定
        import re
        pattern = r'# 通知設定.*?}'
        content = re.sub(pattern, new_notification_config, content, flags=re.DOTALL)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("已更新config.py以啟用三層通知系統")
        
    except Exception as e:
        print(f"更新config.py失敗: {e}")

def show_triple_notification_guide():
    """顯示三層通知系統設定指南"""
    print("\n" + "="*70)
    print("三層通知系統設定指南")
    print("="*70)
    
    print("\n🎯 三層通知系統架構：")
    print("第一層 - Telegram Bot (主要通知)")
    print("第二層 - Discord (備用通知)")
    print("第三層 - Email (重要備份)")
    
    print("\n📋 設定步驟：")
    
    print("\n1. Telegram Bot設定 (第一層 - 主要通知)")
    print("   - 在Telegram中搜尋 @BotFather")
    print("   - 發送 /newbot 指令")
    print("   - 輸入Bot名稱和用戶名")
    print("   - 取得Bot Token")
    print("   - 開始與Bot對話")
    print("   - 取得Chat ID")
    print("   - 設定到 .env 檔案")
    
    print("\n2. Discord Webhook設定 (第二層 - 備用通知)")
    print("   - 建立Discord伺服器")
    print("   - 建立專用頻道")
    print("   - 設定Webhook")
    print("   - 複製Webhook URL")
    print("   - 設定到 .env 檔案")
    
    print("\n3. Email設定 (第三層 - 重要備份)")
    print("   - 開啟Gmail兩步驟驗證")
    print("   - 產生應用程式密碼")
    print("   - 設定到 .env 檔案")
    
    print("\n4. 測試各層通知")
    print("   - 測試Telegram: python test_telegram.py")
    print("   - 測試Discord: python test_discord.py")
    print("   - 測試Email: python test_email.py")
    print("   - 測試全部: python test_notification.py")
    
    print("\n5. 啟動服務")
    print("   - 手動測試: python tender_notification.py --manual")
    print("   - 啟動服務: python tender_notification.py")
    
    print("\n" + "="*70)

def create_test_scripts():
    """創建測試腳本"""
    
    # Discord測試腳本
    discord_test = '''# -*- coding: utf-8 -*-
"""
Discord Webhook 測試腳本
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.advanced_notification import AdvancedNotificationManager

def test_discord():
    """測試Discord Webhook"""
    print("Discord Webhook 測試")
    print("=" * 30)
    
    manager = AdvancedNotificationManager()
    
    test_message = """**🔔 標案監控測試通知**

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
    
    print("發送測試訊息到Discord...")
    result = manager.send_discord_notification(test_message)
    
    if result:
        print("✅ Discord通知發送成功！")
        print("請檢查您的Discord頻道是否收到訊息")
    else:
        print("❌ Discord通知發送失敗")
        print("請檢查Discord Webhook URL是否正確")

if __name__ == "__main__":
    test_discord()
'''
    
    # Email測試腳本
    email_test = '''# -*- coding: utf-8 -*-
"""
Email 測試腳本
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.advanced_notification import AdvancedNotificationManager

def test_email():
    """測試Email通知"""
    print("Email 通知測試")
    print("=" * 20)
    
    manager = AdvancedNotificationManager()
    
    test_message = """標案監控測試通知

發現 2 個相關的政府標案：

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

測試完成！"""
    
    print("發送測試Email...")
    result = manager.send_email("標案監控測試", test_message)
    
    if result:
        print("✅ Email通知發送成功！")
        print("請檢查您的Email信箱")
    else:
        print("❌ Email通知發送失敗")
        print("請檢查Email設定是否正確")

if __name__ == "__main__":
    test_email()
'''
    
    # 寫入測試腳本
    try:
        with open(project_root / "test_discord.py", 'w', encoding='utf-8') as f:
            f.write(discord_test)
        
        with open(project_root / "test_email.py", 'w', encoding='utf-8') as f:
            f.write(email_test)
        
        print("已創建測試腳本：")
        print("- test_discord.py")
        print("- test_email.py")
        
    except Exception as e:
        print(f"創建測試腳本失敗: {e}")

def main():
    """主函數"""
    print("三層通知系統設定")
    print("=" * 30)
    print("Telegram Bot + Discord + Email備份")
    
    # 建立.env檔案
    print("\n1. 建立環境變數檔案...")
    create_triple_notification_env()
    
    # 更新config.py
    print("\n2. 更新設定檔案...")
    update_config_for_triple_notification()
    
    # 創建測試腳本
    print("\n3. 創建測試腳本...")
    create_test_scripts()
    
    # 顯示設定指南
    show_triple_notification_guide()
    
    print("\n✅ 三層通知系統設定完成！")
    print("請按照上述指南進行後續設定。")

if __name__ == "__main__":
    main() 