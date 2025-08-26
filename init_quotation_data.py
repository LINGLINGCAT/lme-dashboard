#!/usr/bin/env python3
"""
初始化智能報價系統數據
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import random

def init_quotation_database():
    """初始化智能報價系統數據庫"""
    print("🔧 初始化智能報價系統數據庫...")
    
    try:
        # 複製初始化腳本
        if os.path.exists('quotation_system/init_data.py'):
            print("✅ 找到初始化腳本")
            
            # 執行初始化
            import subprocess
            result = subprocess.run([sys.executable, 'quotation_system/init_data.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 數據庫初始化成功")
                return True
            else:
                print(f"❌ 數據庫初始化失敗: {result.stderr}")
                return False
        else:
            print("❌ 找不到初始化腳本: quotation_system/init_data.py")
            return False
            
    except Exception as e:
        print(f"❌ 初始化過程出錯: {e}")
        return False

def check_database_status():
    """檢查數據庫狀態"""
    print("\n📊 檢查數據庫狀態...")
    
    try:
        conn = sqlite3.connect('quotation_system.db')
        cursor = conn.cursor()
        
        # 檢查表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"✅ 數據庫表格: {len(tables)} 個")
        
        # 檢查數據量
        for table in ['partners', 'quotations', 'market_prices']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 筆數據")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 檢查數據庫狀態失敗: {e}")
        return False

def main():
    """主函數"""
    print("💰 智能報價系統初始化")
    print("=" * 50)
    
    # 初始化數據庫
    if init_quotation_database():
        # 檢查狀態
        check_database_status()
        
        print("\n🎉 初始化完成！")
        print("\n🚀 啟動智能報價系統:")
        print("   streamlit run pages/8_智能報價系統.py")
        print("   或")
        print("   cd quotation_system && streamlit run app.py")
        
        print("\n🧪 運行測試:")
        print("   python test_quotation_system.py")
    else:
        print("\n❌ 初始化失敗，請檢查錯誤訊息")

if __name__ == "__main__":
    main()
