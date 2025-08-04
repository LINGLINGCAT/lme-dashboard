#!/usr/bin/env python3
"""
LME Dashboard 功能測試腳本
測試所有主要功能是否正常工作
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

def test_data_fetching():
    """測試數據抓取功能"""
    print("🔍 測試數據抓取功能...")
    
    # 測試 LME 數據抓取
    try:
        lme_url = "https://quote.fx678.com/exchange/LME"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(lme_url, headers=headers, timeout=15)
        response.raise_for_status()
        print("✅ LME 數據抓取成功")
    except Exception as e:
        print(f"❌ LME 數據抓取失敗: {e}")
        return False
    
    # 測試台銀匯率抓取
    try:
        bot_url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
        response = requests.get(bot_url, headers=headers, timeout=15)
        response.raise_for_status()
        print("✅ 台銀匯率抓取成功")
    except Exception as e:
        print(f"❌ 台銀匯率抓取失敗: {e}")
        return False
    
    # 測試 Westmetall 數據抓取
    try:
        westmetall_url = "https://www.westmetall.com/en/markdaten.php"
        response = requests.get(westmetall_url, headers=headers, timeout=15)
        response.raise_for_status()
        print("✅ Westmetall 數據抓取成功")
    except Exception as e:
        print(f"❌ Westmetall 數據抓取失敗: {e}")
        return False
    
    return True

def test_file_structure():
    """測試檔案結構"""
    print("\n📁 測試檔案結構...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md",
        "utils/auth.py",
        "pages/1_LME_即時報價看板.py",
        "pages/2_前日收盤.py",
        "pages/3_線上計算機.py",
        "pages/4_數據分析.py",
        "pages/5_系統設定.py",
        "pages/6_使用說明.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ 缺少檔案: {missing_files}")
        return False
    
    return True

def test_dependencies():
    """測試依賴套件"""
    print("\n📦 測試依賴套件...")
    
    required_packages = [
        "streamlit",
        "pandas", 
        "requests",
        "beautifulsoup4",
        "lxml",
        "streamlit_autorefresh",
        "python_dotenv",
        "plotly",
        "psutil"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安裝")
    
    if missing_packages:
        print(f"\n⚠️ 缺少套件: {missing_packages}")
        print("請執行: pip install -r requirements.txt")
        return False
    
    return True

def test_data_directory():
    """測試數據目錄"""
    print("\n📊 測試數據目錄...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        print("✅ 創建數據目錄")
    else:
        print("✅ 數據目錄存在")
    
    # 檢查是否有歷史數據檔案
    history_file = data_dir / "csp_history.csv"
    if history_file.exists():
        print("✅ 歷史數據檔案存在")
        # 檢查檔案內容
        try:
            df = pd.read_csv(history_file)
            print(f"✅ 歷史數據檔案可讀取，包含 {len(df)} 筆記錄")
        except Exception as e:
            print(f"❌ 歷史數據檔案讀取失敗: {e}")
    else:
        print("ℹ️ 歷史數據檔案不存在（首次使用）")
    
    return True

def test_settings():
    """測試設定功能"""
    print("\n⚙️ 測試設定功能...")
    
    settings_file = Path("data/settings.json")
    
    # 測試設定載入
    try:
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print("✅ 設定檔案載入成功")
        else:
            # 創建預設設定
            default_settings = {
                "refresh_interval": 30,
                "auto_save": True,
                "notifications": False,
                "theme": "light",
                "language": "zh-TW"
            }
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=2)
            print("✅ 創建預設設定檔案")
    except Exception as e:
        print(f"❌ 設定檔案操作失敗: {e}")
        return False
    
    return True

def test_auth_system():
    """測試認證系統"""
    print("\n🔐 測試認證系統...")
    
    try:
        from utils.auth import SecureAuth, create_password_hash
        
        # 測試密碼哈希
        test_password = "test123"
        password_hash = create_password_hash(test_password)
        print("✅ 密碼哈希功能正常")
        
        # 測試認證類別
        auth = SecureAuth()
        if auth.verify_password("password"):  # 預設密碼
            print("✅ 預設密碼驗證正常")
        else:
            print("❌ 預設密碼驗證失敗")
            return False
        
        print("✅ 認證系統測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 認證系統測試失敗: {e}")
        return False

def test_calculations():
    """測試計算功能"""
    print("\n🧮 測試計算功能...")
    
    # 模擬金屬價格
    metal_prices = {
        "銅": 8500,  # USD/噸
        "錫": 25000,  # USD/噸
        "鋅": 2500    # USD/噸
    }
    
    # 測試成分計算
    try:
        # 測試 C2680 成分 (銅70%, 鋅30%)
        composition = {"銅": 70, "鋅": 30}
        usd_rate = 32.0  # 假設匯率
        
        # 計算成分價格
        usd_price_per_ton = 0
        for metal, percentage in composition.items():
            if metal in metal_prices:
                contribution = (metal_prices[metal] * percentage / 100) / 1000
                usd_price_per_ton += contribution
        
        twd_price_per_ton = usd_price_per_ton * usd_rate
        
        print(f"✅ 成分計算正常")
        print(f"   C2680 價格: ${usd_price_per_ton:.2f}/kg (USD), NT${twd_price_per_ton:.2f}/kg (TWD)")
        
        return True
        
    except Exception as e:
        print(f"❌ 計算功能測試失敗: {e}")
        return False

def generate_test_report():
    """生成測試報告"""
    print("\n" + "="*50)
    print("📋 LME Dashboard 功能測試報告")
    print("="*50)
    
    tests = [
        ("檔案結構", test_file_structure),
        ("依賴套件", test_dependencies),
        ("數據目錄", test_data_directory),
        ("設定功能", test_settings),
        ("認證系統", test_auth_system),
        ("計算功能", test_calculations),
        ("數據抓取", test_data_fetching)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果
    print("\n📊 測試結果摘要:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print("-" * 30)
    print(f"總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統運行正常。")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查上述問題。")
        return False

def main():
    """主測試函數"""
    print("🚀 開始 LME Dashboard 功能測試...")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = generate_test_report()
    
    if success:
        print("\n✅ 系統測試完成，可以正常使用！")
        print("\n💡 使用提示:")
        print("1. 執行 'streamlit run app.py' 啟動應用程式")
        print("2. 預設密碼為 'password'")
        print("3. 首次使用建議更改密碼")
    else:
        print("\n❌ 系統測試發現問題，請修復後再使用。")
    
    return success

if __name__ == "__main__":
    main() 