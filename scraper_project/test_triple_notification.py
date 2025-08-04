# -*- coding: utf-8 -*-
"""
三層通知系統測試腳本
Telegram Bot + Discord + Email備份
"""

import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.advanced_notification import AdvancedNotificationManager

def test_triple_notification():
    """測試三層通知系統"""
    print("三層通知系統測試")
    print("=" * 40)
    print("Telegram Bot + Discord + Email備份")
    print()
    
    # 建立通知管理器
    manager = AdvancedNotificationManager()
    
    # 測試訊息
    test_message = """🔔 三層通知系統測試

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

✅ 三層通知系統測試完成！"""
    
    # 測試各層通知
    print("開始測試各層通知...")
    print()
    
    # 第一層：Telegram Bot
    print("1️⃣ 測試第一層 - Telegram Bot (主要通知)")
    telegram_result = manager.send_telegram_notification(test_message)
    if telegram_result:
        print("   ✅ Telegram通知發送成功")
    else:
        print("   ❌ Telegram通知發送失敗")
    print()
    
    # 第二層：Discord
    print("2️⃣ 測試第二層 - Discord (備用通知)")
    discord_result = manager.send_discord_notification(test_message)
    if discord_result:
        print("   ✅ Discord通知發送成功")
    else:
        print("   ❌ Discord通知發送失敗")
    print()
    
    # 第三層：Email
    print("3️⃣ 測試第三層 - Email (重要備份)")
    email_result = manager.send_email("三層通知系統測試", test_message)
    if email_result:
        print("   ✅ Email通知發送成功")
    else:
        print("   ❌ Email通知發送失敗")
    print()
    
    # 測試全部通知
    print("🔄 測試全部通知同時發送...")
    all_results = manager.send_notification("三層通知系統測試", test_message)
    
    print("\n📊 測試結果總結：")
    print("=" * 30)
    print(f"Telegram Bot: {'✅ 成功' if all_results['telegram'] else '❌ 失敗'}")
    print(f"Discord:      {'✅ 成功' if all_results['discord'] else '❌ 失敗'}")
    print(f"Email:        {'✅ 成功' if all_results['email'] else '❌ 失敗'}")
    print(f"Slack:        {'✅ 成功' if all_results['slack'] else '❌ 失敗'}")
    
    # 計算成功率
    success_count = sum(all_results.values())
    total_count = len(all_results)
    success_rate = (success_count / total_count) * 100
    
    print(f"\n📈 成功率: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 三層通知系統運作良好！")
    elif success_rate >= 50:
        print("⚠️  部分通知成功，請檢查失敗的設定")
    else:
        print("❌ 大部分通知失敗，請檢查設定")

def check_configuration():
    """檢查設定狀態"""
    print("🔍 檢查三層通知系統設定...")
    print("=" * 40)
    
    from config import NOTIFICATION_CONFIG
    
    # 檢查各層設定
    layers = [
        ("第一層 - Telegram Bot", NOTIFICATION_CONFIG.get('telegram', {})),
        ("第二層 - Discord", NOTIFICATION_CONFIG.get('discord', {})),
        ("第三層 - Email", NOTIFICATION_CONFIG.get('email', {})),
    ]
    
    for layer_name, config in layers:
        enabled = config.get('enabled', False)
        status = "✅ 已啟用" if enabled else "❌ 未啟用"
        print(f"{layer_name}: {status}")
        
        if not enabled:
            print(f"   請在config.py中啟用 {layer_name}")
    
    print("\n📝 設定建議：")
    print("- 確保至少啟用兩層通知")
    print("- Telegram Bot建議作為主要通知")
    print("- Email建議作為重要備份")
    print("- Discord建議作為備用通知")

def main():
    """主函數"""
    print("三層通知系統測試工具")
    print("=" * 40)
    
    # 檢查設定
    check_configuration()
    
    print("\n" + "="*40)
    
    # 詢問是否要測試
    test = input("是否要執行三層通知測試？(y/N): ").lower()
    if test == 'y':
        test_triple_notification()
    else:
        print("跳過測試")
    
    print("\n💡 提示：")
    print("- 如果某層通知失敗，請檢查對應的設定")
    print("- 建議先測試單一通知，再測試全部")
    print("- 詳細設定指南請參考各平台的設定文件")

if __name__ == "__main__":
    main() 