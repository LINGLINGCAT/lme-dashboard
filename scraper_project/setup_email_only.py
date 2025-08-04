# -*- coding: utf-8 -*-
"""
Email通知設定腳本
由於Telegram網路問題，先設定Email通知
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def create_email_env():
    """建立Email通知的.env檔案"""
    env_content = """# Email通知設定
# 由於Telegram網路問題，先使用Email通知

# Email通知設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Telegram Bot設定 (暫時停用)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Discord Webhook設定 (可選)
DISCORD_WEBHOOK_URL=
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
        print(f"已建立Email通知的.env檔案: {env_file}")
        print("請編輯此檔案並填入您的Gmail設定")
    except Exception as e:
        print(f"建立.env檔案失敗: {e}")

def update_config_for_email_only():
    """更新config.py以只啟用Email通知"""
    config_file = project_root / "config.py"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新通知設定
        new_notification_config = '''# 通知設定 - Email通知
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": True,  # 啟用Email通知
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "sender_email": os.getenv("SENDER_EMAIL", ""),
        "sender_password": os.getenv("SENDER_PASSWORD", ""),
        "recipient_emails": os.getenv("RECIPIENT_EMAILS", "").split(",")
    },
    "telegram": {
        "enabled": False,  # 暫時停用Telegram
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    },
    "discord": {
        "enabled": False,  # 可選
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
        
        print("已更新config.py以啟用Email通知")
        
    except Exception as e:
        print(f"更新config.py失敗: {e}")

def show_email_setup_guide():
    """顯示Email設定指南"""
    print("\n" + "="*60)
    print("Email通知設定指南")
    print("="*60)
    
    print("\n📧 Gmail設定步驟：")
    print("1. 開啟Gmail")
    print("2. 前往設定 > 安全性")
    print("3. 開啟兩步驟驗證")
    print("4. 產生應用程式密碼")
    print("5. 複製應用程式密碼")
    print("6. 設定到.env檔案")
    
    print("\n🔧 .env檔案設定：")
    print("SENDER_EMAIL=your_email@gmail.com")
    print("SENDER_PASSWORD=your_app_password")
    print("RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com")
    
    print("\n✅ Email通知優點：")
    print("- 完全免費")
    print("- 支援附件")
    print("- 設定簡單")
    print("- 手機推播（設定Email推播）")
    print("- 可靠備份")
    
    print("\n📱 手機推播設定：")
    print("1. 在手機上安裝Gmail應用程式")
    print("2. 開啟Email推播通知")
    print("3. 設定重要郵件通知")
    
    print("\n" + "="*60)

def create_email_test():
    """創建Email測試腳本"""
    email_test = '''# -*- coding: utf-8 -*-
"""
Email通知測試腳本
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.advanced_notification import AdvancedNotificationManager

def test_email():
    """測試Email通知"""
    print("Email通知測試")
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
    
    try:
        with open(project_root / "test_email_only.py", 'w', encoding='utf-8') as f:
            f.write(email_test)
        print("已創建Email測試腳本：test_email_only.py")
    except Exception as e:
        print(f"創建測試腳本失敗: {e}")

def main():
    """主函數"""
    print("Email通知設定")
    print("=" * 30)
    print("由於Telegram網路問題，先設定Email通知")
    
    # 建立.env檔案
    print("\n1. 建立環境變數檔案...")
    create_email_env()
    
    # 更新config.py
    print("\n2. 更新設定檔案...")
    update_config_for_email_only()
    
    # 創建測試腳本
    print("\n3. 創建測試腳本...")
    create_email_test()
    
    # 顯示設定指南
    show_email_setup_guide()
    
    print("\n✅ Email通知設定完成！")
    print("請按照上述指南設定Gmail，然後執行測試。")

if __name__ == "__main__":
    main() 