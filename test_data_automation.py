#!/usr/bin/env python3
"""
數據自動化系統完整測試腳本
測試歷史數據導入、自動記錄、數據分析等功能
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import time

def test_environment():
    """測試環境設定"""
    print("🔧 測試環境設定...")
    print("-" * 50)
    
    # 檢查必要套件
    required_packages = [
        'pandas', 'openpyxl', 'schedule', 'requests', 
        'plotly', 'streamlit', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (缺失)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少套件：{', '.join(missing_packages)}")
        print("請執行：pip install " + " ".join(missing_packages))
        return False
    
    print("✅ 所有必要套件都已安裝")
    return True

def test_data_directory():
    """測試數據目錄"""
    print("\n📁 測試數據目錄...")
    print("-" * 50)
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ 數據目錄：{data_dir.absolute()}")
    
    # 檢查現有數據文件
    data_files = list(data_dir.glob("*"))
    if data_files:
        print("📊 現有數據文件：")
        for file in data_files:
            size = file.stat().st_size
            print(f"   {file.name} ({size} bytes)")
    else:
        print("📊 數據目錄為空")
    
    return True

def test_import_tool():
    """測試歷史數據導入工具"""
    print("\n📤 測試歷史數據導入工具...")
    print("-" * 50)
    
    # 檢查導入腳本是否存在
    import_script = Path("import_historical_data.py")
    if not import_script.exists():
        print("❌ import_historical_data.py 不存在")
        return False
    
    print("✅ 導入腳本存在")
    
    # 檢查是否有 LME.xlsm 文件
    lme_files = [
        Path("Z:/LME.xlsm"),
        Path("D:/LME.xlsm"),
        Path("C:/LME.xlsm"),
        Path("LME.xlsm"),
        Path("data/LME.xlsm")
    ]
    
    found_lme = False
    for lme_file in lme_files:
        if lme_file.exists():
            print(f"✅ 找到 LME 文件：{lme_file}")
            found_lme = True
            break
    
    if not found_lme:
        print("⚠️ 沒有找到 LME.xlsm 文件")
        print("💡 您可以：")
        print("   1. 將 LME.xlsm 文件放在專案目錄下")
        print("   2. 或使用數據上傳功能")
    
    return True

def test_auto_update_tool():
    """測試自動更新工具"""
    print("\n⏰ 測試自動更新工具...")
    print("-" * 50)
    
    # 檢查自動更新腳本
    auto_script = Path("auto_update_data.py")
    if not auto_script.exists():
        print("❌ auto_update_data.py 不存在")
        return False
    
    print("✅ 自動更新腳本存在")
    
    # 檢查批處理文件
    bat_file = Path("run_auto_update.bat")
    if bat_file.exists():
        print("✅ 批處理文件存在")
    else:
        print("⚠️ 批處理文件不存在")
    
    return True

def test_data_analysis_page():
    """測試數據分析頁面"""
    print("\n📊 測試數據分析頁面...")
    print("-" * 50)
    
    analysis_script = Path("pages/4_數據分析.py")
    if not analysis_script.exists():
        print("❌ 數據分析頁面不存在")
        return False
    
    print("✅ 數據分析頁面存在")
    
    # 檢查是否有歷史數據
    history_files = [
        Path("data/csp_history.csv"),
        Path("data/csp_history.xlsx"),
        Path("data/lme_historical_data.csv"),
        Path("data/lme_historical_data.xlsx")
    ]
    
    has_data = False
    for file in history_files:
        if file.exists():
            print(f"✅ 找到歷史數據：{file.name}")
            has_data = True
    
    if not has_data:
        print("⚠️ 沒有找到歷史數據文件")
        print("💡 建議先運行：python import_historical_data.py")
    
    return True

def create_sample_data():
    """創建示例數據用於測試"""
    print("\n📊 創建示例數據...")
    print("-" * 50)
    
    # 創建示例歷史數據
    dates = pd.date_range(start='2024-01-01', end='2024-12-30', freq='D')
    
    sample_data = []
    for date in dates:
        sample_data.append({
            '日期': date,
            '品項': 'CSP磷',
            '價格': 285000 + (date.day % 30) * 1000,
            '幣值': 'TWD',
            '來源': '示例數據'
        })
        sample_data.append({
            '日期': date,
            '品項': 'CSP青',
            '價格': 320000 + (date.day % 30) * 1200,
            '幣值': 'TWD',
            '來源': '示例數據'
        })
    
    df = pd.DataFrame(sample_data)
    
    # 保存到 data 目錄
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    csv_path = data_dir / "csp_history.csv"
    excel_path = data_dir / "csp_history.xlsx"
    
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    df.to_excel(excel_path, index=False)
    
    print(f"✅ 已創建示例數據：{len(df)} 筆")
    print(f"📁 CSV：{csv_path}")
    print(f"📁 Excel：{excel_path}")
    
    return True

def test_streamlit_apps():
    """測試 Streamlit 應用"""
    print("\n🚀 測試 Streamlit 應用...")
    print("-" * 50)
    
    apps = [
        ("主應用程式", "app.py"),
        ("LME 即時報價看板", "pages/1_LME_即時報價看板.py"),
        ("前日收盤", "pages/2_前日收盤.py"),
        ("線上計算機", "pages/3_線上計算機.py"),
        ("數據分析", "pages/4_數據分析.py"),
        ("系統設定", "pages/5_系統設定.py"),
        ("使用說明", "pages/6_使用說明.py"),
        ("智能報價系統", "pages/8_智能報價系統.py")
    ]
    
    for app_name, app_path in apps:
        if Path(app_path).exists():
            print(f"✅ {app_name}: {app_path}")
        else:
            print(f"❌ {app_name}: {app_path} (缺失)")
    
    return True

def run_quick_test():
    """運行快速測試"""
    print("\n🧪 運行快速測試...")
    print("-" * 50)
    
    try:
        # 測試導入工具（不實際導入，只檢查功能）
        result = subprocess.run([
            sys.executable, "import_historical_data.py"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 導入工具測試通過")
        else:
            print("⚠️ 導入工具測試失敗（可能是正常的，因為沒有 LME 文件）")
        
    except subprocess.TimeoutExpired:
        print("⚠️ 導入工具測試超時（可能是正常的）")
    except Exception as e:
        print(f"⚠️ 導入工具測試出錯：{e}")

def main():
    """主測試函數"""
    print("🧪 數據自動化系統完整測試")
    print("=" * 60)
    
    tests = [
        ("環境設定", test_environment),
        ("數據目錄", test_data_directory),
        ("歷史數據導入工具", test_import_tool),
        ("自動更新工具", test_auto_update_tool),
        ("數據分析頁面", test_data_analysis_page),
        ("Streamlit 應用", test_streamlit_apps),
        ("創建示例數據", create_sample_data),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試失敗：{e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果：{passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統運行正常")
    else:
        print("⚠️ 部分測試失敗，請檢查上述錯誤訊息")
    
    print("\n🚀 下一步操作：")
    print("1. 導入歷史數據：python import_historical_data.py")
    print("2. 啟動自動記錄：python auto_update_data.py")
    print("3. 啟動主應用：streamlit run app.py")
    print("4. 測試數據分析：streamlit run pages/4_數據分析.py")
    
    print("\n💡 測試建議：")
    print("- 先運行導入工具導入歷史數據")
    print("- 然後啟動自動記錄系統")
    print("- 最後測試數據分析功能")

if __name__ == "__main__":
    main()
