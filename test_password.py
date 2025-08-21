#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def hash_password(password: str) -> str:
    """將密碼轉換為SHA256哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("🔐 密碼測試工具")
    print("=" * 50)
    
    # 從環境變數讀取哈希值
    dashboard_hash = os.getenv('DASHBOARD_PASSWORD_HASH')
    admin_hash = os.getenv('ADMIN_PASSWORD_HASH')
    
    print(f"環境變數中的 DASHBOARD_PASSWORD_HASH: {dashboard_hash}")
    print(f"環境變數中的 ADMIN_PASSWORD_HASH: {admin_hash}")
    print()
    
    # 測試密碼
    test_passwords = ['password', 'admin', 'AA716key']
    
    for password in test_passwords:
        hash_value = hash_password(password)
        print(f"密碼 '{password}' 的哈希值: {hash_value}")
        
        if hash_value == dashboard_hash:
            print(f"  ✅ 匹配 DASHBOARD_PASSWORD_HASH")
        if hash_value == admin_hash:
            print(f"  ✅ 匹配 ADMIN_PASSWORD_HASH")
        print()

if __name__ == "__main__":
    main()
