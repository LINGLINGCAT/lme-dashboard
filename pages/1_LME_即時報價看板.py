import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io
import re
from streamlit_autorefresh import st_autorefresh
from utils.auth import check_password, logout

# 檢查密碼認證
check_password()

# --- 頁面設定 ---
st.set_page_config(page_title="LME 即時報價看板", page_icon="📈", layout="wide")

# --- 資料來源 ---
lme_url = "https://quote.fx678.com/exchange/LME"
bot_url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"

def fetch_lme_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(lme_url, headers=headers, timeout=15)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        # 只保留主要欄位並重新命名
        df = df.rename(columns={df.columns[0]: "名稱", df.columns[1]: "最新價", df.columns[2]: "漲跌", df.columns[3]: "漲跌幅"})
        df = df[["名稱", "最新價", "漲跌", "漲跌幅"]]
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
        tables = pd.read_html(io.StringIO(response.text), header=[0,1])
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
            df_fx['幣別代碼'] = df_fx['幣別'].str.extract(r'([A-Z]{3})')
            df_fx = df_fx[['幣別', '即期買入', '即期賣出', '即期中間價', '抓取時間', '資料來源', '幣別代碼']]
            return df_fx, None
        else:
            return pd.DataFrame(), "找不到正確的即期買入/賣出欄位"
    except Exception as e:
        return pd.DataFrame(), f"台銀匯率載入失敗: {e}"

def calculate_prices(df_lme, df_fx):
    if df_lme.empty or df_fx.empty:
        return pd.DataFrame(), None
    usd_row = df_fx[df_fx['幣別代碼'] == 'USD']
    if usd_row.empty:
        return pd.DataFrame(), "找不到美金匯率"
    spot_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
    spot_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
    usd_mid_rate = (spot_buy + spot_sell) / 2
    try:
        df_calc = df_lme.copy()
        df_calc.set_index('名稱', inplace=True)
        for col in ['最新價']:
            df_calc[col] = pd.to_numeric(df_calc[col].astype(str).str.replace(',', ''), errors='coerce')
        def find_lme_name(df, names):
            for idx in df.index:
                for name in names:
                    if name in idx.replace(' ', ''):
                        return df.loc[idx, '最新價']
            return None
        copper = find_lme_name(df_calc, ['LME铜', 'LME銅'])
        tin = find_lme_name(df_calc, ['LME锡', 'LME錫'])
        zinc = find_lme_name(df_calc, ['LME锌', 'LME鋅'])
        if copper is None or tin is None or zinc is None:
            return pd.DataFrame(), "價格計算失敗: 缺少 LME銅、LME錫或LME鋅資料"
        price_phosphor = (copper * 0.94 + tin * 0.06) / 1000 * usd_mid_rate
        price_bronze = (copper * 0.65 + zinc * 0.35) / 1000 * usd_mid_rate
        price_red_copper = copper / 1000 * usd_mid_rate
        price_tin = tin
        price_zinc = zinc
        csp_data = {
            '磷': f"NT${price_phosphor:,.2f}",
            '青': f"NT${price_bronze:,.2f}",
            '紅': f"NT${price_red_copper:,.2f}",
            '錫': f"US${price_tin:,.2f}",
            '鋅': f"US${price_zinc:,.2f}"
        }
        return pd.DataFrame([csp_data]), None
    except Exception as e:
        return pd.DataFrame(), f"價格計算失敗: {e}"

def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st_autorefresh(interval=5000, key="lme_autorefresh")
    st.title("📈 LME 即時報價看板")
    st.subheader("版本: V1.5 - 即時價格試算")
    st.markdown("---")
    # --- 載入資料 ---
    df_lme, lme_error = fetch_lme_data()
    df_fx, fx_error = fetch_bot_fx_data()
    st.caption(f"LME: {'成功' if lme_error is None else lme_error} | 台銀匯率: {'成功' if fx_error is None else fx_error}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("LME 市場即時報價")
        if lme_error:
            st.error(lme_error)
        elif not df_lme.empty:
            st.dataframe(df_lme[["名稱", "最新價", "漲跌", "漲跌幅"]], use_container_width=True, hide_index=True)
    with col2:
        st.subheader("台銀即時匯率 (USD/CNY)")
        if fx_error:
            st.error(fx_error)
        elif not df_fx.empty:
            if '幣別代碼' in df_fx.columns:
                df_fx_filtered = df_fx[df_fx['幣別代碼'].isin(['USD', 'CNY'])]
            else:
                df_fx_filtered = df_fx[df_fx['幣別'].str.contains('美金|USD|人民幣|CNY')]
            st.dataframe(df_fx_filtered[['幣別', '即期買入', '即期賣出', '即期中間價']], use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("即時價格試算")
    if df_lme.empty or df_fx.empty:
        st.warning("因上方資料載入失敗，無法進行價格試算。")
    else:
        df_csp, calc_error = calculate_prices(df_lme, df_fx)
        if calc_error:
            st.error(calc_error)
        else:
            st.dataframe(df_csp, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
