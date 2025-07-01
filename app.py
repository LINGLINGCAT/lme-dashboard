import streamlit as st
from utils.auth import check_password, logout

# 檢查密碼認證
check_password()

st.set_page_config(
    page_title="LME 即時報價看板",
    page_icon="📈",
    layout="wide"
)

# --- CSS to hide the main page from the sidebar ---
st.markdown("""
<style>
    [data-testid="stSidebarNav"] > ul > li:first-child {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# 側邊欄登出按鈕
with st.sidebar:
    if st.button("🚪 登出", type="secondary"):
        logout()

st.title("歡迎使用 LME 報價看板")
st.sidebar.success("請從上方選擇一個頁面")

st.markdown(
    """
    這是一個使用 Streamlit 建立的 LME 報價與匯率儀表板。
    
    **👈 請從左側的側邊欄選擇您想要查看的頁面：**
    - **LME 即時報價看板**: 查看 LME 市場與台銀的即時匯率。
    - **前日前日收盤參考**: 查看 Westmetall 的 LME 收盤價與台銀的每日匯率。
    """
)