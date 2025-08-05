import streamlit as st
from utils.auth import check_password, logout, is_admin
from version import get_version_display

# 檢查密碼認證
check_password()

st.set_page_config(
    page_title="LME 即時報價看板",
    page_icon="📈",
    layout="wide"
)

# --- CSS to hide the main page from the sidebar and admin pages for non-admin users ---
admin_pages_css = ""
if not is_admin():
    admin_pages_css = """
    [data-testid="stSidebarNav"] > ul > li:nth-child(4),
    [data-testid="stSidebarNav"] > ul > li:nth-child(5),
    [data-testid="stSidebarNav"] > ul > li:nth-child(6),
    [data-testid="stSidebarNav"] > ul > li:nth-child(7),
    [data-testid="stSidebarNav"] > ul > li:nth-child(8) {
        display: none !important;
    }
    """

st.markdown(f"""
<style>
    [data-testid="stSidebarNav"] > ul > li:first-child {{
        display: none;
    }}
    {admin_pages_css}
</style>
""", unsafe_allow_html=True)

# 側邊欄登出按鈕
with st.sidebar:
    if st.button("🚪 登出", type="secondary"):
        logout()

st.title("歡迎使用 LME 報價看板")
st.sidebar.success("請從上方選擇一個頁面")

# 顯示版本號
st.sidebar.markdown(f"**版本**: {get_version_display()}")

st.markdown(
    """
    這是一個使用 Streamlit 建立的 LME 報價與匯率儀表板。
    
    **👈 請從左側的側邊欄選擇您想要查看的頁面：**
    
    ### 📊 核心功能
    - **LME 即時報價看板**: 查看 LME 市場與台銀的即時匯率
    - **前日收盤**: 查看 Westmetall 的 LME 收盤價與台銀的每日匯率
    - **線上計算機**: 自定義成分計算與價格轉換工具
    
    ### 🚀 管理員功能 (僅管理員可見)
    - **數據分析**: 歷史數據視覺化與趨勢分析
    - **系統設定**: 自定義密碼、更新頻率等設定
    - **使用說明**: 完整操作指南與故障排除
    
    ### 💡 特色功能
    - 🔄 自動數據更新（每5秒）
    - 📈 即時價格試算
    - 📊 互動式圖表分析
    - 🔐 安全密碼認證
    - 📱 響應式設計（支援手機/電腦）
    """
)