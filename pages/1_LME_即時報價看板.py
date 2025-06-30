import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io
import traceback

# URL for data sources
lme_url = "https://quote.fx678.com/exchange/LME"
bot_url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"

def fetch_lme_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(lme_url, headers=headers, timeout=15)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        df['抓取時間'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['資料來源'] = 'LME'
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"LME 載入失敗: {e}"

def fetch_bot_fx_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(bot_url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text), header=[0, 1])
        df = tables[0]
        
        currency_col = [col for col in df.columns if '幣別' in col[0]][0]
        buy_cols = [col for col in df.columns if col[1] == '本行買入']
        sell_cols = [col for col in df.columns if col[1] == '本行賣出']
        
        def pick_spot_col(cols_to_check, df_to_check):
            for col in cols_to_check:
                vals = pd.to_numeric(df_to_check[col], errors='coerce')
                if vals.notna().sum() > 0 and vals.max() < 100 and vals.min() > 0.1:
                    return col
            return None
        
        spot_buy_col = pick_spot_col(buy_cols, df)
        spot_sell_col = pick_spot_col(sell_cols, df)
        
        if currency_col and spot_buy_col and spot_sell_col:
            df_fx = df[[currency_col, spot_sell_col, spot_buy_col]].copy()
            df_fx.columns = ['幣別', '即期買入', '即期賣出']
            df_fx['即期中間價'] = (
                pd.to_numeric(df_fx['即期買入'], errors='coerce') +
                pd.to_numeric(df_fx['即期賣出'], errors='coerce')
            ) / 2
            df_fx['抓取時間'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df_fx['資料來源'] = 'BOT'
            df_fx = df_fx[['幣別', '即期買入', '即期賣出', '即期中間價', '抓取時間', '資料來源']]
            return df_fx, None
        else:
            return pd.DataFrame(), "找不到正確的即期買入/賣出欄位"
    except Exception as e:
        return pd.DataFrame(), f"台銀匯率載入失敗: {e}"

def calculate_prices(df_lme, df_fx):
    """計算價格，參考前日收盤邏輯"""
    if df_lme.empty or df_fx.empty:
        return pd.DataFrame()
    
    # 取得 USD 和 CNY 的即期中間價
    usd_rate = df_fx[df_fx['幣別代碼'] == 'USD']['即期中間價'].iloc[0]
    cny_rate = df_fx[df_fx['幣別代碼'] == 'CNY']['即期中間價'].iloc[0]
    
    # 計算價格
    df_calc = df_lme.copy()
    df_calc['USD價格'] = df_calc['現貨價'] / usd_rate
    df_calc['CNY價格'] = df_calc['現貨價'] / cny_rate
    
    # 保留兩位小數
    df_calc['USD價格'] = df_calc['USD價格'].round(2)
    df_calc['CNY價格'] = df_calc['CNY價格'].round(2)
    
    return df_calc

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📈 LME 即時報價看板")
st.caption("版本: V1.2 - 即時價格試算")
st.markdown("---")

# 三欄布局
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("LME 市場即時報價")
    lme_placeholder = st.empty()

with col2:
    st.subheader("台銀即時匯率 (USD/CNY)")
    fx_placeholder = st.empty()

with col3:
    st.subheader("價格試算")
    calc_placeholder = st.empty()

while True:
    df_lme, lme_error = fetch_lme_data()
    df_fx_all, fx_error = fetch_bot_fx_data()
    
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

    with calc_placeholder.container():
        if lme_error or fx_error or df_lme.empty or df_fx_all.empty:
            st.error("無法計算價格: 請確認LME報價和匯率資料都已成功載入")
        else:
            df_calc = calculate_prices(df_lme, df_fx_all)
            if not df_calc.empty:
                st.dataframe(df_calc[['商品名稱', '現貨價', 'USD價格', 'CNY價格']], 
                           height=500, 
                           use_container_width=True, 
                           hide_index=True)

    time.sleep(5)  # 每5秒更新一次
{{ ... }}
