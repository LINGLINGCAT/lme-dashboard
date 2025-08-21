from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import hashlib
import os
import secrets
from typing import Optional
import time

class SecureAuth:
    def __init__(self):
        # 從環境變數獲取密碼，如果沒有則使用預設值
        self.password_hash = os.getenv('DASHBOARD_PASSWORD_HASH', 
                                     '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')  # "password"的SHA256
        self.max_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION_MINUTES', '15'))
        
    def hash_password(self, password: str) -> str:
        """將密碼轉換為SHA256哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """驗證密碼是否正確"""
        return self.hash_password(password) == self.password_hash
    
    def is_locked_out(self) -> bool:
        """檢查是否被鎖定"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'lockout_time' not in st.session_state:
            st.session_state.lockout_time = 0
            
        # 檢查是否在鎖定期間
        if st.session_state.lockout_time > 0:
            if time.time() - st.session_state.lockout_time < self.lockout_duration * 60:
                return True
            else:
                # 鎖定期間已過，重置
                st.session_state.lockout_time = 0
                st.session_state.login_attempts = 0
        return False
    
    def record_failed_attempt(self):
        """記錄失敗的登入嘗試"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'lockout_time' not in st.session_state:
            st.session_state.lockout_time = 0
            
        st.session_state.login_attempts += 1
        
        # 如果超過最大嘗試次數，開始鎖定
        if st.session_state.login_attempts >= self.max_attempts:
            st.session_state.lockout_time = time.time()
    
    def get_remaining_attempts(self) -> int:
        """獲取剩餘嘗試次數"""
        if 'login_attempts' not in st.session_state:
            return self.max_attempts
        return max(0, self.max_attempts - st.session_state.login_attempts)
    
    def get_lockout_remaining_time(self) -> int:
        """獲取鎖定剩餘時間（分鐘）"""
        if st.session_state.lockout_time == 0:
            return 0
        remaining = self.lockout_duration * 60 - (time.time() - st.session_state.lockout_time)
        return max(0, int(remaining // 60))
    
    def reset_attempts(self):
        """重置嘗試次數（登入成功時調用）"""
        st.session_state.login_attempts = 0
        st.session_state.lockout_time = 0

def check_password() -> bool:
    """安全的密碼檢查函數"""
    auth = SecureAuth()
    
    # 檢查是否已經登入
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    
    if st.session_state.authenticated:
        return True
    
    # 檢查是否被鎖定
    if auth.is_locked_out():
        remaining_time = auth.get_lockout_remaining_time()
        st.error(f"🔒 帳戶已被鎖定，請等待 {remaining_time} 分鐘後再試")
        st.stop()
        return False
    
    # 顯示登入界面
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🔐 LME 報價看板</h1>
        <p>請輸入密碼以繼續</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("密碼", type="password", key="password_input")
            
            if st.button("登入", type="primary", use_container_width=True):
                # 檢查是否為管理員密碼
                admin_password = os.getenv('ADMIN_PASSWORD_HASH')
                is_admin_login = admin_password and auth.hash_password(password) == admin_password
                
                # 檢查是否為一般用戶密碼或管理員密碼
                if auth.verify_password(password) or is_admin_login:
                    st.session_state.authenticated = True
                    if is_admin_login:
                        st.session_state.is_admin = True
                    auth.reset_attempts()
                    st.success("登入成功！")
                    st.rerun()
                else:
                    auth.record_failed_attempt()
                    remaining = auth.get_remaining_attempts()
                    if remaining > 0:
                        st.error(f"❌ 密碼錯誤，還剩 {remaining} 次嘗試機會")
                    else:
                        st.error("❌ 密碼錯誤次數過多，帳戶已被鎖定")
            
            # 顯示剩餘嘗試次數
            remaining = auth.get_remaining_attempts()
            if remaining < auth.max_attempts:
                st.warning(f"⚠️ 剩餘嘗試次數: {remaining}")
    
    st.stop()
    return False

def logout():
    """登出函數"""
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    if "is_admin" in st.session_state:
        del st.session_state.is_admin
    if "password_input" in st.session_state:
        del st.session_state.password_input
    st.rerun()

def is_admin() -> bool:
    """檢查當前用戶是否為管理員"""
    return st.session_state.get("is_admin", False)

def create_password_hash(password: str) -> str:
    """創建密碼哈希（用於設置環境變數）"""
    return hashlib.sha256(password.encode()).hexdigest() 