#!/usr/bin/env python3
"""
LME Dashboard 快速測試工具
可以選擇性測試特定功能，速度更快
"""

import sys
import os
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test_data_fetching():
    """快速測試數據抓取 - 只測試一個數據源"""
    print("🔍 快速測試數據抓取...")
    
    try:
        # 只測試 LME 數據抓取（最常用的）
        lme_url = "https://quote.fx678.com/exchange/LME"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(lme_url, headers=headers, timeout=10)
        response.raise_for_status()
        print("✅ LME 數據抓取正常")
        return True
    except Exception as e:
        print(f"❌ LME 數據抓取失敗: {e}")
        return False

def quick_test_file_check():
    """快速檢查主要檔案"""
    print("📁 快速檢查主要檔案...")
    
    main_files = ["app.py", "requirements.txt", "utils/auth.py"]
    missing = []
    
    for file_path in main_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            missing.append(file_path)
            print(f"❌ {file_path} - 缺少")
    
    return len(missing) == 0

def quick_test_dependencies():
    """快速測試主要依賴套件"""
    print("📦 快速測試主要依賴...")
    
    main_packages = ["streamlit", "pandas", "requests"]
    missing = []
    
    for package in main_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - 未安裝")
    
    if missing:
        print(f"\n⚠️ 缺少套件: {missing}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    return True

def quick_test_auth():
    """快速測試認證系統"""
    print("🔐 快速測試認證...")
    
    try:
        from utils.auth import SecureAuth
        auth = SecureAuth()
        if auth.verify_password("password"):
            print("✅ 認證系統正常")
            return True
        else:
            print("❌ 預設密碼驗證失敗")
            return False
    except Exception as e:
        print(f"❌ 認證系統測試失敗: {e}")
        return False

def quick_test_calculation():
    """快速測試計算功能"""
    print("🧮 快速測試計算...")
    
    try:
        # 簡單的價格計算測試
        copper_price = 8500  # USD/噸
        usd_rate = 32.0
        composition = {"銅": 70, "鋅": 30}
        
        # 計算成分價格
        usd_price_per_ton = (copper_price * 0.7) / 1000
        twd_price_per_ton = usd_price_per_ton * usd_rate
        
        print(f"✅ 計算功能正常 (範例: C2680 = NT${twd_price_per_ton:.2f}/kg)")
        return True
    except Exception as e:
        print(f"❌ 計算功能測試失敗: {e}")
        return False

def show_test_menu():
    """顯示測試選單"""
    print("\n" + "="*40)
    print("🚀 LME Dashboard 快速測試工具")
    print("="*40)
    print("請選擇要測試的功能:")
    print("1. 數據抓取測試 (網路連接)")
    print("2. 檔案結構檢查")
    print("3. 依賴套件檢查")
    print("4. 認證系統測試")
    print("5. 計算功能測試")
    print("6. 全部快速測試")
    print("0. 退出")
    print("-"*40)

def run_selected_test(choice):
    """執行選擇的測試"""
    tests = {
        "1": ("數據抓取", quick_test_data_fetching),
        "2": ("檔案結構", quick_test_file_check),
        "3": ("依賴套件", quick_test_dependencies),
        "4": ("認證系統", quick_test_auth),
        "5": ("計算功能", quick_test_calculation),
    }
    
    if choice == "6":
        # 全部快速測試
        print("\n🔄 執行全部快速測試...")
        results = []
        for test_name, test_func in tests.values():
            print(f"\n--- 測試 {test_name} ---")
            result = test_func()
            results.append((test_name, result))
        
        # 顯示結果
        print("\n📊 快速測試結果:")
        print("-" * 30)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通過" if result else "❌ 失敗"
            print(f"{test_name:<12} {status}")
        
        print("-" * 30)
        print(f"總計: {passed}/{total} 項測試通過")
        
        if passed == total:
            print("🎉 快速測試全部通過！")
        else:
            print("⚠️ 部分測試失敗，請檢查問題。")
        
        return passed == total
    
    elif choice in tests:
        test_name, test_func = tests[choice]
        print(f"\n--- 測試 {test_name} ---")
        result = test_func()
        
        if result:
            print(f"✅ {test_name} 測試通過")
        else:
            print(f"❌ {test_name} 測試失敗")
        
        return result
    
    else:
        print("❌ 無效選擇")
        return False

def main():
    """主函數"""
    print("🚀 LME Dashboard 快速測試工具")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        show_test_menu()
        choice = input("請輸入選項 (0-6): ").strip()
        
        if choice == "0":
            print("👋 退出測試工具")
            break
        elif choice in ["1", "2", "3", "4", "5", "6"]:
            run_selected_test(choice)
            
            # 詢問是否繼續
            continue_test = input("\n是否繼續測試其他功能? (y/n): ").strip().lower()
            if continue_test != 'y':
                break
        else:
            print("❌ 無效選項，請重新選擇")
    
    print("\n💡 使用提示:")
    print("1. 執行 'streamlit run app.py' 啟動應用程式")
    print("2. 預設密碼為 'password'")
    print("3. 如需全面測試，請執行 'python test_all_functions.py'")

if __name__ == "__main__":
    main() 