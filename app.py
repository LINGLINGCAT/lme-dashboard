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
# 從你的 lme_to_csv.py 移植過來的爬蟲函式
# -------------------------------------------------------------------

def fetch_lme_data():
    """從 fx678.com 抓取 LME 數據"""
    url = "https://quote.fx678.com/exchange/LME"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        df['抓取時間'] = datetime.now().strftime('%H:%M:%S')
        return df
    except Exception as e:
        # st.error(f"抓取 LME 數據失敗: {e}")
        return pd.DataFrame() # 返回空的DataFrame以避免中斷

def fetch_bot_fx_data():
    """從台灣銀行抓取外匯數據，並只保留 USD 和 CNY"""
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        df = df.iloc[:, [0, 1, 2, 3, 4]]
        df.columns = ['幣別', '現金買入', '現金賣出', '即期買入', '即期賣出']
        
        # 提取貨幣代碼
        df['幣別代碼'] = df['幣別'].str.extract(r'([A-Z]{3})')
        
        # 篩選出 USD 和 CNY
        target_currencies = ['USD', 'CNY']
        df_filtered = df[df['幣別代碼'].isin(target_currencies)].copy()
        
        # 返回整理後的 DataFrame
        return df_filtered[['幣別', '現金買入', '現金賣出', '即期買入', '即期賣出']]

    except Exception as e:
        # st.error(f"抓取外匯數據失敗: {e}")
        return pd.DataFrame()

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📈 LME 即時報價看板")

# 建立兩個欄位來並排顯示
col1, col2 = st.columns(2)

with col1:
    st.subheader("LME 市場報價")
    lme_placeholder = st.empty()

with col2:
    st.subheader("台灣銀行即期匯率 (USD/CNY)")
    fx_placeholder = st.empty()

# ----------------------------
# 計算功能區 (待辦)
# ----------------------------
st.markdown("---")
st.header("⚙️ 即時計算工具")
st.warning("計算功能將在下一步加入。請您提供 Excel 中的計算公式。")
# 在這裡，我們會根據你提供的 Excel 公式，加入輸入框和計算邏輯

# ----------------------------
# 5秒自動更新迴圈
# ----------------------------
while True:
    # 抓取最新數據
    df_lme = fetch_lme_data()
    df_fx = fetch_bot_fx_data()

    # 在 LME placeholder 中顯示數據
    with lme_placeholder.container():
        if not df_lme.empty:
            st.dataframe(df_lme, height=500, use_container_width=True, hide_index=True)
        else:
            st.error("LME 數據載入失敗，請稍後...")

    # 在外匯 placeholder 中顯示數據
    with fx_placeholder.container():
        if not df_fx.empty:
            st.dataframe(df_fx, height=500, use_container_width=True, hide_index=True)
        else:
            st.error("外匯數據載入失敗，請稍後...")
            
    # 等待 5 秒
    time.sleep(5)