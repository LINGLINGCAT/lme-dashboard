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
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        tables = pd.read_html(url, header=[0, 1])
        df = tables[0]

        # --- 更穩健的欄位尋找邏輯 (參考 lme_to_csv.py) ---
        currency_col = [col for col in df.columns if '幣別' in col[0]][0]
        
        # 尋找所有可能的買入/賣出欄位
        buy_cols = [col for col in df.columns if col[1] == '本行買入']
        sell_cols = [col for col in df.columns if col[1] == '本行賣出']

        # 定義一個輔助函式，用來從候選欄位中挑選出正確的"即期"欄位
        def pick_spot_col(cols_to_check, df_to_check):
            for col in cols_to_check:
                # 轉換為數字，同時處理非數字的 '-' 字元
                vals = pd.to_numeric(df_to_check[col], errors='coerce')
                # 判斷是否為有效的匯率欄位
                if vals.notna().sum() > 0 and vals.max() < 100 and vals.min() > 0.1:
                    return col
            return None 

        spot_buy_col = pick_spot_col(buy_cols, df)
        spot_sell_col = pick_spot_col(sell_cols, df)

        # 確保我們找到了所有需要的欄位
        if not (currency_col and spot_buy_col and spot_sell_col):
            raise ValueError("無法從台銀網站自動判斷正確的即期匯率欄位。")

        # 用找到的欄位建立乾淨的 DataFrame
        clean_df = df[[currency_col, spot_buy_col, spot_sell_col]].copy()
        clean_df.columns = ['幣別', '即期買入', '即期賣出']
        
        # 清理幣別，只留下英文代碼
        clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')
        
        return clean_df, None
    except Exception as e:
        error_details = f"錯誤類型: {type(e).__name__}\n"
        error_details += f"錯誤訊息: {e}\n"
        error_details += f"Traceback:\n{traceback.format_exc()}"
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