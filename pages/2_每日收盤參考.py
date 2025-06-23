import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import io

# ----------------------------
# 頁面設定
# ----------------------------
st.set_page_config(
    page_title="每日收盤價參考",
    page_icon="📅",
    layout="wide"
)

# -------------------------------------------------------------------
# 爬蟲函式
# -------------------------------------------------------------------
@st.cache_data(ttl=3600) # 快取 1 小時 (3600秒)
def fetch_westmetall_daily():
    """從 westmetall.com 抓取每日收盤價"""
    url = "https://www.westmetall.com/en/markdaten.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        return pd.read_html(io.StringIO(str(table)))[0]
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600) # 快取 1 小時
def fetch_bot_daily_fx():
    """從台灣銀行抓取每日匯率數據"""
    url = "https://rate.bot.com.tw/xrt/all/day"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_html(io.StringIO(response.text), header=0)[0]
        df = df.iloc[:, [0, 3, 4]]
        df.columns = ['幣別', '即期買入', '即期賣出']
        df['幣別代碼'] = df['幣別'].str.extract(r'([A-Z]{3})')
        return df
    except Exception:
        return pd.DataFrame()

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📅 每日收盤價參考")
st.markdown(f"數據緩存於伺服器一小時，上次更新時間約為：**{datetime.now().strftime('%Y-%m-%d %H:%M')}**")
st.markdown("---")

# 建立兩個欄位
col1, col2 = st.columns(2)

# 抓取數據
df_westmetall = fetch_westmetall_daily()
df_fx_daily_all = fetch_bot_daily_fx()

with col1:
    st.subheader("Westmetall LME 收盤價")
    if not df_westmetall.empty:
        st.dataframe(df_westmetall, use_container_width=True, hide_index=True)
    else:
        st.error("Westmetall 數據載入失敗。")

with col2:
    st.subheader("台銀每日匯率 (USD/CNY)")
    if not df_fx_daily_all.empty:
        df_fx_daily_filtered = df_fx_daily_all[df_fx_daily_all['幣別代碼'].isin(['USD', 'CNY'])]
        st.dataframe(df_fx_daily_filtered[['幣別', '即期買入', '即期賣出']], use_container_width=True, hide_index=True)
    else:
        st.error("每日匯率載入失敗。")

if st.button("清除快取並強制刷新"):
    st.cache_data.clear()
    st.rerun()
