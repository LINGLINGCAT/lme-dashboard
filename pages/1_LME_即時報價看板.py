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
    """從台灣銀行抓取即時匯率 (V8 - 採用 lme_to_csv.py 的穩健邏輯)"""
    url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"
    try:
        tables = pd.read_html(requests.get(url).text, header=[0, 1])
        df = tables[0]

        # --- 來自 lme_to_csv.py 的穩健欄位挑選邏輯 ---
        def pick_spot_col(cols_to_check, df_to_check):
            """從候選欄位中，根據數值範圍挑選出'即期'匯率欄。"""
            for col in cols_to_check:
                vals = pd.to_numeric(df_to_check[col], errors='coerce')
                # 檢查數值是否在一個合理的即期匯率範圍內 (e.g. >0.1, <100)
                if vals.notna().sum() > 0 and vals.max() < 100 and vals.min() > 0.1:
                    return col
            return None

        # 1. 找到所有名為'本行買入'和'本行賣出'的欄位 (這會包含現金和即期)
        buy_cols = [col for col in df.columns if '本行買入' in col[1]]
        sell_cols = [col for col in df.columns if '本行賣出' in col[1]]

        # 2. 使用輔助函式從候選者中挑出正確的即期匯率欄位
        spot_buy_col = pick_spot_col(buy_cols, df)
        spot_sell_col = pick_spot_col(sell_cols, df)

        # 3. 找到幣別欄位
        currency_col = [col for col in df.columns if '幣別' in col[0]][0]

        if not all([currency_col, spot_buy_col, spot_sell_col]):
             raise ValueError("無法從台銀網站上定位到必要的即期匯率欄位。")

        # 4. 建立乾淨的 DataFrame
        clean_df = df[[currency_col, spot_buy_col, spot_sell_col]].copy()
        clean_df.columns = ['幣別', '即期買入', '即期賣出']
        clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')

        return clean_df, "已從網路獲取最新數據 (V8)"
    except Exception as e:
        error_details = f"Traceback:\n{traceback.format_exc()}"
        return pd.DataFrame(), f"台銀即時匯率載入失敗:\n\n```\n{error_details}\n```"

# -------------------------------------------------------------------
# Streamlit 應用程式主體
# -------------------------------------------------------------------
st.title("📈 LME 即時報價看板")
st.caption("版本: V1.1 - 3M價格試算功能")
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

            # 取得美金那一列
            usd_row = df_fx_all[df_fx_all['幣別代碼'] == 'USD']
            spot_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
            spot_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
            usd_mid_rate = (spot_buy + spot_sell) / 2

            # --- 3M價格試算 ---
            try:
                # 1. LME金屬最新價
                df_lme_calc = df_lme.copy()
                df_lme_calc.set_index('名稱', inplace=True)
                for col in ['最新價']:
                    df_lme_calc[col] = pd.to_numeric(df_lme_calc[col], errors='coerce')

                copper_3m = df_lme_calc.loc['LME銅', '最新價']
                tin_3m = df_lme_calc.loc['LME錫', '最新價']
                zinc_3m = df_lme_calc.loc['LME鋅', '最新價']

                # 2. 計算CSP價格
                price_phosphor = (copper_3m * 0.94 + tin_3m * 0.06) / 1000 * usd_mid_rate
                price_bronze = (copper_3m * 0.65 + zinc_3m * 0.35) / 1000 * usd_mid_rate
                price_red_copper = copper_3m / 1000 * usd_mid_rate
                price_tin = tin_3m
                price_zinc = zinc_3m

                csp_data = {
                    '磷': f"NT${price_phosphor:,.2f}",
                    '青': f"NT${price_bronze:,.2f}",
                    '紅': f"NT${price_red_copper:,.2f}",
                    '錫': f"US${price_tin:,.2f}",
                    '鋅': f"US${price_zinc:,.2f}"
                }

                st.markdown("---")
                st.subheader("3M價格試算")
                st.metric(label="美金中間匯率", value=f"{usd_mid_rate:.4f}")
                st.dataframe(pd.DataFrame([csp_data]), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"3M價格試算失敗: {e}")
        else:
            st.warning("無法載入台銀即時匯率。")

    time.sleep(5) 