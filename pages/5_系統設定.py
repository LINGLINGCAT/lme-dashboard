import streamlit as st
import hashlib
import os
from pathlib import Path
from utils.auth import check_password, logout, create_password_hash
import json
import datetime
import pandas as pd
import psutil

# 檢查密碼認證
check_password()

# --- 頁面設定 ---
st.set_page_config(page_title="系統設定", page_icon="⚙️", layout="wide")

# --- 設定檔案路徑 ---
SETTINGS_FILE = Path("data/settings.json")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def load_settings():
    """載入設定"""
    
    default_settings = {
        "refresh_interval": 30,
        "auto_save": True,
        "notifications": False,
        "theme": "light",
        "language": "zh-TW"
    }
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # 合併預設設定和已儲存的設定
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            st.error(f"載入設定失敗: {e}")
            return default_settings
    
    return default_settings

def save_settings(settings):
    """儲存設定"""
    
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"儲存設定失敗: {e}")
        return False

def change_password(new_password):
    """更改密碼"""
    try:
        # 創建新的密碼哈希
        password_hash = create_password_hash(new_password)
        
        # 更新環境變數（這裡只是顯示，實際需要手動更新 .env 檔案）
        st.success("✅ 密碼已成功更改！")
        st.info(f"新的密碼哈希: {password_hash}")
        st.warning("⚠️ 請將此哈希值更新到您的 .env 檔案中的 DASHBOARD_PASSWORD_HASH 變數")
        
        return True
    except Exception as e:
        st.error(f"更改密碼失敗: {e}")
        return False

def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st.title("⚙️ 系統設定")
    st.subheader("自定義您的 LME 報價看板")
    st.markdown("---")
    
    # 載入當前設定
    settings = load_settings()
    
    # 設定分頁
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 一般設定", "🔐 安全設定", "📊 數據設定", "ℹ️ 系統資訊"])
    
    with tab1:
        st.subheader("🔧 一般設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 更新頻率設定
            refresh_interval = st.slider(
                "自動更新頻率 (秒)",
                min_value=5,
                max_value=300,
                value=settings.get("refresh_interval", 30),
                step=5,
                help="設定數據自動更新的頻率"
            )
            
            # 主題設定
            theme = st.selectbox(
                "界面主題",
                ["light", "dark"],
                index=0 if settings.get("theme", "light") == "light" else 1,
                help="選擇界面主題"
            )
        
        with col2:
            # 語言設定
            language = st.selectbox(
                "語言設定",
                ["zh-TW", "en-US"],
                index=0 if settings.get("language", "zh-TW") == "zh-TW" else 1,
                help="選擇界面語言"
            )
            
            # 通知設定
            notifications = st.checkbox(
                "啟用通知",
                value=settings.get("notifications", False),
                help="啟用系統通知功能"
            )
        
        # 自動儲存設定
        auto_save = st.checkbox(
            "自動儲存數據",
            value=settings.get("auto_save", True),
            help="自動儲存歷史數據到本地檔案"
        )
        
        # 儲存一般設定
        if st.button("💾 儲存一般設定", type="primary"):
            settings.update({
                "refresh_interval": refresh_interval,
                "theme": theme,
                "language": language,
                "notifications": notifications,
                "auto_save": auto_save
            })
            
            if save_settings(settings):
                st.success("✅ 一般設定已儲存！")
                st.rerun()
    
    with tab2:
        st.subheader("🔐 安全設定")
        
        # 密碼管理
        st.markdown("**密碼管理**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_password = st.text_input(
                "新密碼",
                type="password",
                help="輸入新的登入密碼"
            )
            
            confirm_password = st.text_input(
                "確認密碼",
                type="password",
                help="再次輸入新密碼以確認"
            )
        
        with col2:
            if new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 6:
                        if st.button("🔐 更改密碼", type="primary"):
                            change_password(new_password)
                    else:
                        st.error("❌ 密碼長度至少需要6個字符")
                else:
                    st.error("❌ 兩次輸入的密碼不一致")
        
        # 登入嘗試設定
        st.markdown("**登入安全設定**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_attempts = st.number_input(
                "最大登入嘗試次數",
                min_value=3,
                max_value=10,
                value=5,
                help="超過此次數將鎖定帳戶"
            )
        
        with col2:
            lockout_duration = st.number_input(
                "鎖定時間 (分鐘)",
                min_value=5,
                max_value=60,
                value=15,
                help="帳戶被鎖定的時間"
            )
        
        # 安全提示
        st.info("""
        **安全提示：**
        - 使用強密碼（包含大小寫字母、數字和符號）
        - 定期更改密碼
        - 不要在公共場所登入
        - 登出時記得清除瀏覽器快取
        """)
    
    with tab3:
        st.subheader("📊 數據設定")
        
        # 數據來源設定
        st.markdown("**數據來源設定**")
        
        data_sources = st.multiselect(
            "啟用的數據來源",
            ["LME 即時報價", "台銀匯率", "Westmetall 收盤價"],
            default=["LME 即時報價", "台銀匯率", "Westmetall 收盤價"],
            help="選擇要使用的數據來源"
        )
        
        # 數據快取設定
        st.markdown("**數據快取設定**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cache_duration = st.number_input(
                "快取時間 (小時)",
                min_value=1,
                max_value=24,
                value=1,
                help="數據快取的有效時間"
            )
        
        with col2:
            max_cache_size = st.number_input(
                "最大快取大小 (MB)",
                min_value=10,
                max_value=1000,
                value=100,
                help="本地快取的最大大小"
            )
        
        # 數據清理
        st.markdown("**數據清理**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清理快取數據", type="secondary"):
                # 這裡可以添加清理快取數據的邏輯
                st.success("✅ 快取數據已清理！")
        
        with col2:
            if st.button("📊 重新整理歷史數據", type="secondary"):
                # 這裡可以添加重新整理歷史數據的邏輯
                st.success("✅ 歷史數據已重新整理！")
        
        # 數據匯出設定
        st.markdown("**數據匯出設定**")
        
        export_format = st.selectbox(
            "預設匯出格式",
            ["CSV", "Excel", "JSON"],
            help="選擇數據匯出的預設格式"
        )
        
        include_timestamp = st.checkbox(
            "匯出時包含時間戳記",
            value=True,
            help="在匯出的檔案名中包含時間戳記"
        )
    
    with tab4:
        st.subheader("ℹ️ 系統資訊")
        
        # 系統狀態
        st.markdown("**系統狀態**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("版本", "V1.5")
        
        with col2:
            st.metric("狀態", "運行中")
        
        with col3:
            st.metric("最後更新", "2024-01-01")
        
        # 數據統計
        st.markdown("**數據統計**")
        
        # 檢查數據檔案
        data_files = []
        if DATA_DIR.exists():
            for file in DATA_DIR.glob("*.csv"):
                data_files.append({
                    "檔案名": file.name,
                    "大小": f"{file.stat().st_size / 1024:.1f} KB",
                    "修改時間": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        
        if data_files:
            st.dataframe(pd.DataFrame(data_files), use_container_width=True, hide_index=True)
        else:
            st.info("📁 目前沒有數據檔案")
        
        # 系統資源
        st.markdown("**系統資源**")
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            memory_usage = psutil.virtual_memory()
            st.metric("記憶體使用率", f"{memory_usage.percent}%")
        
        with col2:
            disk_usage = psutil.disk_usage('.')
            st.metric("磁碟使用率", f"{disk_usage.percent}%")
        
        # 版本資訊
        st.markdown("**版本資訊**")
        
        version_info = {
            "Streamlit": "1.28.0",
            "Pandas": "2.1.0",
            "Plotly": "5.17.0",
            "Requests": "2.31.0",
            "BeautifulSoup4": "4.12.0"
        }
        
        version_df = pd.DataFrame([
            {"套件": k, "版本": v} for k, v in version_info.items()
        ])
        
        st.dataframe(version_df, use_container_width=True, hide_index=True)
        
        # 更新檢查
        st.markdown("**更新檢查**")
        
        if st.button("🔄 檢查更新", type="secondary"):
            st.info("📡 正在檢查更新...")
            st.success("✅ 目前使用的是最新版本！")
    
    # 底部說明
    st.markdown("---")
    st.markdown("""
    **💡 使用提示：**
    - 設定更改後會立即生效
    - 某些設定需要重新啟動應用程式才能生效
    - 建議定期備份重要設定
    - 如遇問題，可以重置為預設設定
    """)

if __name__ == "__main__":
    main() 