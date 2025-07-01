#!/usr/bin/env python3
"""
LME Dashboard 密碼設置工具
用於生成安全的密碼哈希並設置環境變數
"""

import hashlib
import os
import getpass
from utils.auth import create_password_hash

def main():
    print("🔐 LME Dashboard 密碼設置工具")
    print("=" * 40)
    
    # 獲取密碼
    password = getpass.getpass("請輸入新密碼: ")
    if not password:
        print("❌ 密碼不能為空")
        return
    
    confirm_password = getpass.getpass("請再次輸入密碼確認: ")
    if password != confirm_password:
        print("❌ 兩次輸入的密碼不一致")
        return
    
    # 生成密碼哈希
    password_hash = create_password_hash(password)
    
    print("\n✅ 密碼哈希生成成功！")
    print(f"密碼哈希: {password_hash}")
    
    # 詢問是否要創建 .env 文件
    create_env = input("\n是否要創建 .env 文件？(y/n): ").lower().strip()
    
    if create_env == 'y':
        env_content = f"""# LME Dashboard 安全配置
# 自動生成的配置文件

# 密碼哈希
DASHBOARD_PASSWORD_HASH={password_hash}

# 最大登入嘗試次數
MAX_LOGIN_ATTEMPTS=5

# 鎖定時間（分鐘）
LOCKOUT_DURATION_MINUTES=15
"""
        
        try:
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ .env 文件已創建")
            print("⚠️  請確保 .env 文件已添加到 .gitignore 中")
        except Exception as e:
            print(f"❌ 創建 .env 文件失敗: {e}")
    
    print("\n📋 手動設置環境變數:")
    print(f"export DASHBOARD_PASSWORD_HASH={password_hash}")
    print(f"export MAX_LOGIN_ATTEMPTS=5")
    print(f"export LOCKOUT_DURATION_MINUTES=15")

if __name__ == "__main__":
    main() 