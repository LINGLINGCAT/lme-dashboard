# -*- coding: utf-8 -*-
"""
Telegram Bot 快速測試腳本
"""

import requests
import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_telegram_bot():
    """測試Telegram Bot"""
    print("Telegram Bot 快速測試")
    print("=" * 30)
    
    # 取得Bot Token和Chat ID
    bot_token = input("請輸入您的Bot Token: ").strip()
    chat_id = input("請輸入您的Chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("❌ Bot Token或Chat ID不能為空")
        return
    
    # 測試訊息
    test_message = """🔔 標案監控機器人測試

📋 這是一個測試訊息，如果您看到這則訊息，表示Telegram Bot設定成功！

✅ 測試完成！"""
    
    # 發送測試訊息
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": test_message,
        "parse_mode": "HTML"
    }
    
    try:
        print("發送測試訊息...")
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Telegram Bot測試成功！")
            print("請檢查您的Telegram是否收到測試訊息")
            
            # 詢問是否要設定到.env檔案
            save_to_env = input("\n是否要將設定儲存到.env檔案？(y/N): ").lower()
            if save_to_env == 'y':
                save_telegram_config(bot_token, chat_id)
        else:
            print(f"❌ Telegram Bot測試失敗: {response.status_code}")
            print("請檢查Bot Token和Chat ID是否正確")
            
    except Exception as e:
        print(f"❌ 發送失敗: {e}")
        print("請檢查網路連線和設定")

def save_telegram_config(bot_token, chat_id):
    """儲存Telegram設定到.env檔案"""
    env_file = project_root / ".env"
    
    try:
        # 讀取現有的.env檔案
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 更新或添加Telegram設定
        lines = content.split('\n')
        new_lines = []
        telegram_token_found = False
        telegram_chat_found = False
        
        for line in lines:
            if line.startswith('TELEGRAM_BOT_TOKEN='):
                new_lines.append(f'TELEGRAM_BOT_TOKEN={bot_token}')
                telegram_token_found = True
            elif line.startswith('TELEGRAM_CHAT_ID='):
                new_lines.append(f'TELEGRAM_CHAT_ID={chat_id}')
                telegram_chat_found = True
            else:
                new_lines.append(line)
        
        # 如果沒有找到，添加新的設定
        if not telegram_token_found:
            new_lines.append(f'TELEGRAM_BOT_TOKEN={bot_token}')
        if not telegram_chat_found:
            new_lines.append(f'TELEGRAM_CHAT_ID={chat_id}')
        
        # 寫入.env檔案
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Telegram設定已儲存到.env檔案")
        
    except Exception as e:
        print(f"❌ 儲存設定失敗: {e}")

def show_telegram_setup_guide():
    """顯示Telegram設定指南"""
    print("\n" + "="*50)
    print("Telegram Bot 設定指南")
    print("="*50)
    
    print("\n📱 設定步驟：")
    print("1. 在Telegram中搜尋 @BotFather")
    print("2. 發送 /newbot 指令")
    print("3. 輸入Bot名稱：標案監控機器人")
    print("4. 輸入Bot用戶名：tender_monitor_bot")
    print("5. 複製Bot Token")
    print("6. 搜尋您的Bot並開始對話")
    print("7. 發送任意訊息")
    print("8. 取得Chat ID")
    print("9. 執行此測試腳本")
    
    print("\n🔗 取得Chat ID：")
    print("在瀏覽器中開啟：")
    print("https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("將 <YOUR_BOT_TOKEN> 替換為您的實際Bot Token")

def main():
    """主函數"""
    print("Telegram Bot 快速測試工具")
    print("=" * 40)
    
    # 顯示設定指南
    show_telegram_setup_guide()
    
    print("\n" + "="*50)
    
    # 詢問是否要測試
    test = input("是否要測試Telegram Bot？(y/N): ").lower()
    if test == 'y':
        test_telegram_bot()
    else:
        print("跳過測試")

if __name__ == "__main__":
    main() 