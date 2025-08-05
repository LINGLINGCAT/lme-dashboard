#!/usr/bin/env python3
"""
密碼哈希生成工具
用於生成新的密碼哈希值
"""

import hashlib

def generate_password_hash(password):
    """生成密碼的 SHA256 哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("🔐 密碼哈希生成工具")
    print("=" * 40)
    
    while True:
        password = input("請輸入要生成哈希的密碼 (或輸入 'quit' 退出): ")
        
        if password.lower() == 'quit':
            break
            
        if password:
            hash_value = generate_password_hash(password)
            print(f"密碼: {password}")
            print(f"SHA256 哈希: {hash_value}")
            print("-" * 40)
            
            # 顯示 .env 格式
            print("在 .env 文件中的設定:")
            if password == "password":
                print(f"DASHBOARD_PASSWORD_HASH={hash_value}")
            elif password == "admin":
                print(f"ADMIN_PASSWORD_HASH={hash_value}")
            else:
                print(f"# 自定義密碼哈希")
                print(f"CUSTOM_PASSWORD_HASH={hash_value}")
            print()
        else:
            print("❌ 密碼不能為空")
    
    print("👋 退出工具")

if __name__ == "__main__":
    main() 