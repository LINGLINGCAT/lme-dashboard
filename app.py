import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import io

# ----------------------------
# 頁面設定
# ----------------------------
st.set_page_config(
    page_title="LME 即時報價看板",
    page_icon="📈",
    layout="wide"
)

# -------------------------------------------------------------------
# 爬蟲函式
# -------------------------------------------------------------------
def fetch_lme_realtime():
    """從 fx678.com 抓取 LME 即時數據"""
    url = "https://quote.fx678.com/exchange/LME"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_html(io.StringIO(response.text))[0]
        df['抓取時間'] = datetime.now().strftime('%H:%M:%S')
        return df
    except Exception:
        return pd.DataFrame()

def fetch_bot_realtime_fx():
    """從台灣銀行抓取即時外匯數據"""
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_html(io.StringIO(response.text))[0]
        df = df.iloc[:, [0, 3, 4]]
        df.columns = ['幣別', '即期買入', '即期賣出']
        df['幣別代碼'] = df['幣別'].str.extract(r'([A-Z]{3})')
        return df
    except Exception:
        return pd.DataFrame()

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📈 LME 即時報價看板")
st.markdown("---")

# 建立兩個欄位來並排顯示
col1, col2 = st.columns(2)

with col1:
    st.subheader("LME 市場即時報價")
    lme_placeholder = st.empty()

with col2:
    st.subheader("台銀即時匯率 (USD/CNY)")
    fx_placeholder = st.empty()

# ----------------------------
# 5秒自動更新迴圈
# ----------------------------
while True:
    df_lme = fetch_lme_realtime()
    df_fx_all = fetch_bot_realtime_fx()

    # 顯示 LME 數據
    with lme_placeholder.container():
        if not df_lme.empty:
            st.dataframe(df_lme, height=500, use_container_width=True, hide_index=True)
        else:
            st.error("LME 即時數據載入失敗。")

    # 顯示篩選後的匯率數據
    with fx_placeholder.container():
        if not df_fx_all.empty:
            df_fx_filtered = df_fx_all[df_fx_all['幣別代碼'].isin(['USD', 'CNY'])]
            st.dataframe(df_fx_filtered[['幣別', '即期買入', '即期賣出']], height=500, use_container_width=True, hide_index=True)
        else:
            st.error("即時匯率載入失敗。")

    time.sleep(5)