import streamlit as st
from utils.auth import check_password, is_admin

# 檢查密碼認證
check_password()

st.set_page_config(
    page_title="權限測試",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 權限狀態測試")

# 檢查登入狀態
st.subheader("📊 當前登入狀態")

col1, col2 = st.columns(2)

with col1:
    st.metric("已登入", "✅ 是" if st.session_state.get("authenticated", False) else "❌ 否")
    st.metric("管理員權限", "✅ 是" if is_admin() else "❌ 否")

with col2:
    st.metric("用戶類型", "🔧 管理員" if is_admin() else "👤 一般用戶")
    st.metric("可見頁面", "全部" if is_admin() else "基本功能")

# 顯示詳細資訊
st.subheader("🔍 詳細資訊")

st.json({
    "authenticated": st.session_state.get("authenticated", False),
    "is_admin": st.session_state.get("is_admin", False),
    "session_state_keys": list(st.session_state.keys())
})

# 測試 CSS 隱藏邏輯
st.subheader("🎨 CSS 隱藏邏輯測試")

if not is_admin():
    st.success("✅ 一般用戶 - 管理員頁面應該被隱藏")
    st.code("""
    [data-testid="stSidebarNav"] > ul > li:nth-child(4),
    [data-testid="stSidebarNav"] > ul > li:nth-child(5),
    [data-testid="stSidebarNav"] > ul > li:nth-child(6),
    [data-testid="stSidebarNav"] > ul > li:nth-child(7),
    [data-testid="stSidebarNav"] > ul > li:nth-child(8) {
        display: none !important;
    }
    """)
else:
    st.info("🔧 管理員用戶 - 可以看到所有頁面")

# 登出按鈕
if st.button("🚪 登出並重新測試"):
    if "authenticated" in st.session_state:
        del st.session_state.authenticated
    if "is_admin" in st.session_state:
        del st.session_state.is_admin
    st.rerun()

st.markdown("---")
st.markdown("**測試說明：**")
st.markdown("""
- 如果您看到「管理員權限: ✅ 是」，表示您使用了管理員密碼登入
- 如果您看到「管理員權限: ❌ 否」，表示您使用了一般用戶密碼登入
- 一般用戶應該只能看到 3 個基本頁面
- 管理員可以看到所有頁面
""") 