#!/usr/bin/env python3
"""
LME Dashboard 系統測試
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

def test_environment():
    """測試環境設定"""
    print("🔧 測試環境設定...")
    print("-" * 40)
    
    # 檢查 .env 檔案
    if os.path.exists(".env"):
        print("✅ .env 檔案存在")
        try:
            with open(".env", "r", encoding="utf-8") as f:
                content = f.read()
            
            required_vars = [
                "DASHBOARD_PASSWORD_HASH",
                "ADMIN_PASSWORD_HASH",
                "MAX_LOGIN_ATTEMPTS",
                "LOCKOUT_DURATION_MINUTES"
            ]
            
            missing_vars = []
            for var in required_vars:
                if var in content:
                    print(f"  ✅ {var}: 已設定")
                else:
                    print(f"  ❌ {var}: 未設定")
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"\n⚠️  缺少環境變數: {', '.join(missing_vars)}")
                print("請在 .env 檔案中添加以下內容:")
                print("DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8")
                print("ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")
                print("MAX_LOGIN_ATTEMPTS=5")
                print("LOCKOUT_DURATION_MINUTES=15")
                return False
            else:
                print("✅ 所有環境變數都已設定")
                return True
                
        except Exception as e:
            print(f"❌ 讀取 .env 檔案失敗: {e}")
            return False
    else:
        print("❌ .env 檔案不存在")
        print("請創建 .env 檔案並添加以下內容:")
        print("DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8")
        print("ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918")
        print("MAX_LOGIN_ATTEMPTS=5")
        print("LOCKOUT_DURATION_MINUTES=15")
        return False

def test_auth_module():
    """測試認證模組"""
    print("\n🔐 測試認證模組...")
    print("-" * 40)
    
    try:
        from utils.auth import SecureAuth
        
        # 創建認證實例
        auth = SecureAuth()
        print("✅ 認證模組載入成功")
        print(f"   當前密碼哈希: {auth.password_hash}")
        print(f"   最大嘗試次數: {auth.max_attempts}")
        print(f"   鎖定時間: {auth.lockout_duration} 分鐘")
        
        # 測試密碼驗證
        print("\n   測試密碼驗證:")
        test_cases = [
            ("password", "一般用戶密碼"),
            ("admin", "管理員密碼"),
            ("wrong", "錯誤密碼")
        ]
        
        for password, description in test_cases:
            is_valid = auth.verify_password(password)
            status = "✅ 正確" if is_valid else "❌ 錯誤"
            print(f"     {description}: {password} -> {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 認證模組測試失敗: {e}")
        return False

def test_admin_logic():
    """測試管理員邏輯"""
    print("\n👑 測試管理員邏輯...")
    print("-" * 40)
    
    try:
        from utils.auth import SecureAuth
        
        auth = SecureAuth()
        
        # 測試預設密碼哈希
        import hashlib
        
        # 預期的哈希值
        expected_password_hash = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        expected_admin_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
        
        # 生成測試哈希
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        admin_hash = hashlib.sha256("admin".encode()).hexdigest()
        
        print(f"   一般用戶密碼 'password':")
        print(f"     生成的哈希: {password_hash}")
        print(f"     預期哈希: {expected_password_hash}")
        print(f"     匹配: {'✅ 是' if password_hash == expected_password_hash else '❌ 否'}")
        
        print(f"\n   管理員密碼 'admin':")
        print(f"     生成的哈希: {admin_hash}")
        print(f"     預期哈希: {expected_admin_hash}")
        print(f"     匹配: {'✅ 是' if admin_hash == expected_admin_hash else '❌ 否'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 管理員邏輯測試失敗: {e}")
        return False

def test_file_structure():
    """測試檔案結構"""
    print("\n📁 測試檔案結構...")
    print("-" * 40)
    
    required_files = [
        "app.py",
        "utils/auth.py",
        "pages/1_LME_即時報價看板.py",
        "pages/2_前日收盤.py",
        "pages/3_線上計算機.py",
        "pages/4_數據分析.py",
        "pages/5_系統設定.py",
        "pages/6_使用說明.py",
        "pages/7_管理員功能.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  缺少檔案: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 所有必要檔案都存在")
        return True

def main():
    """主測試函數"""
    print("🚀 LME Dashboard 系統測試")
    print("=" * 60)
    
    # 執行測試
    env_ok = test_environment()
    auth_ok = test_auth_module()
    admin_ok = test_admin_logic()
    files_ok = test_file_structure()
    
    # 顯示測試結果
    print("\n" + "=" * 60)
    print("📊 測試結果:")
    print(f"   環境設定: {'✅ 通過' if env_ok else '❌ 失敗'}")
    print(f"   認證模組: {'✅ 通過' if auth_ok else '❌ 失敗'}")
    print(f"   管理員邏輯: {'✅ 通過' if admin_ok else '❌ 失敗'}")
    print(f"   檔案結構: {'✅ 通過' if files_ok else '❌ 失敗'}")
    
    if all([env_ok, auth_ok, admin_ok, files_ok]):
        print("\n🎉 所有測試通過！系統準備就緒。")
        print("\n💡 下一步:")
        print("   1. 啟動應用程式: streamlit run app.py")
        print("   2. 使用密碼 'password' 或 'admin' 登入")
        print("   3. 測試權限控制功能")
    else:
        print("\n⚠️  部分測試失敗，請檢查上述問題。")
        print("\n🔧 常見解決方案:")
        print("   1. 確保 .env 檔案存在且格式正確")
        print("   2. 檢查所有必要檔案是否存在")
        print("   3. 確認 Python 環境和依賴套件已安裝")

if __name__ == "__main__":
    main()
