# -*- coding: utf-8 -*-
"""
網路問題診斷腳本
檢查網路連線和Telegram可達性
"""

import requests
import socket
import subprocess
import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_basic_connectivity():
    """檢查基本網路連線"""
    print("🔍 檢查基本網路連線...")
    
    # 測試基本連線
    test_sites = [
        ("Google", "https://www.google.com"),
        ("GitHub", "https://github.com"),
        ("Telegram Web", "https://web.telegram.org"),
        ("Telegram API", "https://api.telegram.org")
    ]
    
    for name, url in test_sites:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: 連線正常")
            else:
                print(f"⚠️  {name}: 狀態碼 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 連線失敗 - {e}")
    
    print()

def check_dns_resolution():
    """檢查DNS解析"""
    print("🔍 檢查DNS解析...")
    
    test_domains = [
        "google.com",
        "telegram.org",
        "api.telegram.org",
        "web.telegram.org"
    ]
    
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain}: {ip}")
        except Exception as e:
            print(f"❌ {domain}: DNS解析失敗 - {e}")
    
    print()

def check_telegram_specific():
    """檢查Telegram特定連線"""
    print("🔍 檢查Telegram特定連線...")
    
    telegram_endpoints = [
        ("BotFather", "https://t.me/botfather"),
        ("Telegram Web", "https://web.telegram.org"),
        ("Telegram API", "https://api.telegram.org/bot123456789:test/getMe")
    ]
    
    for name, url in telegram_endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 404]:  # 404是正常的，因為我們用了假的bot token
                print(f"✅ {name}: 可達")
            else:
                print(f"⚠️  {name}: 狀態碼 {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: 連線失敗 - {e}")
    
    print()

def suggest_solutions():
    """建議解決方案"""
    print("💡 解決方案建議：")
    print("=" * 50)
    
    print("\n1. 更換DNS伺服器：")
    print("   - Google DNS: 8.8.8.8, 8.8.4.4")
    print("   - Cloudflare DNS: 1.1.1.1, 1.0.0.1")
    
    print("\n2. 使用VPN：")
    print("   - ProtonVPN (免費)")
    print("   - Windscribe (免費)")
    print("   - ExpressVPN (付費)")
    
    print("\n3. 檢查防火牆設定：")
    print("   - 確認防火牆沒有阻擋Telegram")
    print("   - 檢查公司網路政策")
    
    print("\n4. 暫時解決方案：")
    print("   - 先設定Email通知")
    print("   - 稍後網路問題解決後再設定Telegram")
    
    print("\n5. 測試其他通知方式：")
    print("   - Discord Webhook")
    print("   - Slack Webhook")
    print("   - Email通知")

def run_network_tests():
    """執行網路測試"""
    print("🌐 網路問題診斷工具")
    print("=" * 40)
    print()
    
    # 執行各種測試
    check_basic_connectivity()
    check_dns_resolution()
    check_telegram_specific()
    
    # 建議解決方案
    suggest_solutions()
    
    print("\n" + "=" * 50)
    print("診斷完成！")

def quick_email_setup():
    """快速Email設定"""
    print("\n🚀 快速Email設定")
    print("=" * 30)
    
    setup = input("是否要立即設定Email通知？(y/N): ").lower()
    if setup == 'y':
        print("執行Email設定...")
        try:
            # 執行Email設定腳本
            subprocess.run([sys.executable, "setup_email_only.py"], check=True)
            print("✅ Email設定完成！")
        except subprocess.CalledProcessError as e:
            print(f"❌ Email設定失敗: {e}")
    else:
        print("跳過Email設定")

def main():
    """主函數"""
    print("網路問題診斷工具")
    print("=" * 30)
    
    # 執行網路診斷
    run_network_tests()
    
    # 詢問是否要設定Email
    quick_email_setup()
    
    print("\n💡 提示：")
    print("- 如果網路問題持續，建議先使用Email通知")
    print("- Email通知功能完整且可靠")
    print("- 稍後網路問題解決後可以再設定Telegram")

if __name__ == "__main__":
    main() 