#!/usr/bin/env python3
"""
測試身份驗證系統
"""

import os
import sys
from utils.auth import SecureAuth, create_password_hash

def test_password_hashing():
    """測試密碼哈希功能"""
    print("🔍 測試密碼哈希功能...")
    
    # 測試密碼
    test_password = "test123"
    hash1 = create_password_hash(test_password)
    hash2 = create_password_hash(test_password)
    
    # 驗證相同密碼產生相同哈希
    assert hash1 == hash2, "相同密碼應該產生相同哈希"
    print("✅ 密碼哈希功能正常")
    
    # 驗證不同密碼產生不同哈希
    different_password = "test456"
    hash3 = create_password_hash(different_password)
    assert hash1 != hash3, "不同密碼應該產生不同哈希"
    print("✅ 密碼哈希唯一性正常")

def test_auth_class():
    """測試 SecureAuth 類"""
    print("\n🔍 測試 SecureAuth 類...")
    
    # 設置測試環境變數
    test_hash = create_password_hash("test123")
    os.environ['DASHBOARD_PASSWORD_HASH'] = test_hash
    os.environ['MAX_LOGIN_ATTEMPTS'] = '3'
    os.environ['LOCKOUT_DURATION_MINUTES'] = '1'
    
    auth = SecureAuth()
    
    # 測試正確密碼
    assert auth.verify_password("test123"), "正確密碼應該驗證成功"
    print("✅ 正確密碼驗證正常")
    
    # 測試錯誤密碼
    assert not auth.verify_password("wrong"), "錯誤密碼應該驗證失敗"
    print("✅ 錯誤密碼驗證正常")
    
    # 測試環境變數讀取
    assert auth.max_attempts == 3, "應該正確讀取最大嘗試次數"
    assert auth.lockout_duration == 1, "應該正確讀取鎖定時間"
    print("✅ 環境變數讀取正常")

def test_default_values():
    """測試預設值"""
    print("\n🔍 測試預設值...")
    
    # 清除環境變數
    if 'DASHBOARD_PASSWORD_HASH' in os.environ:
        del os.environ['DASHBOARD_PASSWORD_HASH']
    if 'MAX_LOGIN_ATTEMPTS' in os.environ:
        del os.environ['MAX_LOGIN_ATTEMPTS']
    if 'LOCKOUT_DURATION_MINUTES' in os.environ:
        del os.environ['LOCKOUT_DURATION_MINUTES']
    
    auth = SecureAuth()
    
    # 測試預設密碼 "password"
    assert auth.verify_password("password"), "預設密碼 'password' 應該驗證成功"
    print("✅ 預設密碼驗證正常")
    
    # 測試預設配置
    assert auth.max_attempts == 5, "預設最大嘗試次數應該是 5"
    assert auth.lockout_duration == 15, "預設鎖定時間應該是 15 分鐘"
    print("✅ 預設配置正常")

def main():
    """主測試函數"""
    print("🧪 開始測試身份驗證系統...")
    print("=" * 50)
    
    try:
        test_password_hashing()
        test_auth_class()
        test_default_values()
        
        print("\n" + "=" * 50)
        print("🎉 所有測試通過！身份驗證系統正常工作")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 