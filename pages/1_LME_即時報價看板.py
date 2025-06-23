import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import io
import traceback

# ----------------------------
# 頁面設定
# ----------------------------
st.set_page_config(page_title="LME 即時報價看板", page_icon="📈", layout="wide")

# -------------------------------------------------------------------
# 爬蟲函式
# -------------------------------------------------------------------
def fetch_lme_realtime():
    url = "https://quote.fx678.com/exchange/LME"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        df = pd.read_html(io.StringIO(response.text))[0]
        df['抓取時間'] = datetime.now().strftime('%H:%M:%S')
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"LME 載入失敗: {e}"

def fetch_bot_realtime_fx():
    """從台灣銀行抓取即時匯率 (V7 - 採用經驗證的 header=[0,1] 解析)"""
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    try:
        # 使用 header=[0, 1] 直接讓 pandas 處理 MultiIndex，這是最穩定的作法
        tables = pd.read_html(requests.get(url).text, header=[0, 1])
        df = tables[0]

        # 搜尋我們需要的欄位
        currency_col = [col for col in df.columns if '幣別' in col[0]][0]
        
        # 尋找包含'即期'和'買入'/'賣出'的欄位
        spot_buy_col = [col for col in df.columns if '即期' in col[0] and '買入' in col[1]][0]
        spot_sell_col = [col for col in df.columns if '即期' in col[0] and '賣出' in col[1]][0]

        # 建立一個乾淨的 DataFrame
        clean_df = df[[currency_col, spot_buy_col, spot_sell_col]].copy()
        
        # 簡化欄位名稱
        clean_df.columns = ['幣別', '即期買入', '即期賣出']
        
        # 提取貨幣代碼 (例如, 從 "美金 (USD)" 中提取 "USD")
        clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')
        
        return clean_df, "已從網路獲取最新數據"
    except Exception as e:
        error_details = f"Traceback:\n{traceback.format_exc()}"
        return pd.DataFrame(), f"台銀即時匯率載入失敗:\n\n```\n{error_details}\n```"

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📈 LME 即時報價看板")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.subheader("LME 市場即時報價")
    lme_placeholder = st.empty()
with col2:
    st.subheader("台銀即時匯率 (USD/CNY)")
    fx_placeholder = st.empty()

while True:
    df_lme, lme_error = fetch_lme_realtime()
    df_fx_all, fx_error = fetch_bot_realtime_fx()

    with lme_placeholder.container():
        if lme_error:
            st.error(lme_error)
        elif not df_lme.empty:
            st.dataframe(df_lme, height=500, use_container_width=True, hide_index=True)

    with fx_placeholder.container():
        if fx_error:
            st.error(fx_error)
        elif not df_fx_all.empty:
            df_fx_filtered = df_fx_all[df_fx_all['幣別代碼'].isin(['USD', 'CNY'])]
            st.dataframe(df_fx_filtered[['幣別代碼', '即期買入', '即期賣出']].rename(columns={'幣別代碼': '幣別'}), height=500, use_container_width=True, hide_index=True)
        else:
            st.warning("無法載入台銀即時匯率。")

    time.sleep(5) 