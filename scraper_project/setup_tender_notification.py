# -*- coding: utf-8 -*-
"""
標案通知快速設定腳本
"""

import os
import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def create_env_file():
    """建立.env檔案"""
    env_content = """# 標案通知服務環境變數設定

# Email通知設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com

# Line通知設定 (可選)
LINE_TOKEN=your_line_notify_token
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
        print(f"已建立.env檔案: {env_file}")
        print("請編輯此檔案並填入您的實際設定值")
    except Exception as e:
        print(f"建立.env檔案失敗: {e}")

def check_dependencies():
    """檢查依賴套件"""
    print("檢查依賴套件...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'selenium', 'pandas',
        'openpyxl', 'schedule', 'python-dotenv', 'lxml',
        'webdriver-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (未安裝)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n需要安裝以下套件: {', '.join(missing_packages)}")
        install = input("是否要自動安裝？(y/N): ").lower()
        if install == 'y':
            os.system(f"pip install {' '.join(missing_packages)}")
    else:
        print("\n所有依賴套件都已安裝")

def show_setup_guide():
    """顯示設定指南"""
    print("\n" + "="*60)
    print("標案通知服務設定指南")
    print("="*60)
    
    print("\n1. 環境變數設定")
    print("   編輯 .env 檔案並填入您的實際設定值")
    
    print("\n2. Gmail設定 (如果使用Gmail)")
    print("   - 開啟Gmail的兩步驟驗證")
    print("   - 產生應用程式密碼")
    print("   - 使用應用程式密碼作為 SENDER_PASSWORD")
    
    print("\n3. Line通知設定 (可選)")
    print("   - 前往 https://notify-bot.line.me/")
    print("   - 登入並建立新的通知群組")
    print("   - 複製Token並設定到 LINE_TOKEN")
    
    print("\n4. 測試通知")
    print("   執行: python test_notification.py")
    
    print("\n5. 手動測試標案搜尋")
    print("   執行: python tender_notification.py --manual")
    
    print("\n6. 啟動每日服務")
    print("   執行: python tender_notification.py")
    print("   或使用批次檔: start_tender_notification.bat")
    
    print("\n" + "="*60)

def main():
    """主函數"""
    print("標案通知服務快速設定")
    print("="*30)
    
    # 檢查依賴套件
    check_dependencies()
    
    # 建立.env檔案
    print("\n建立環境變數檔案...")
    create_env_file()
    
    # 顯示設定指南
    show_setup_guide()
    
    print("\n設定完成！請按照上述指南進行後續設定。")

if __name__ == "__main__":
    main() 