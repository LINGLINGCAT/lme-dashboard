import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import io
from pathlib import Path
import time
import re

# --- 設定 ---
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
WESTMETALL_CACHE = DATA_DIR / "westmetall_cache.csv"
BOT_CACHE = DATA_DIR / "bot_cache.csv"
HISTORY_FILE = DATA_DIR / "csp_history.csv"

# --- 頁面設定 ---
st.set_page_config(page_title="前日收盤", page_icon="📅", layout="wide")

# --- 資料獲取函式 ---
@st.cache_data(ttl=3600)
def fetch_westmetall_lme_data():
    westmetall_url = "https://www.westmetall.com/en/markdaten.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(westmetall_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    
    # 1. 先從表格的 <th> 標籤中抓取來源日期（如 25. June 2025）
    date_str = ""
    ths = table.find_all("th")
    for th in ths:
        m = re.search(r"\d{1,2}\.\s*\w+\s*\d{4}", th.get_text())
        if m:
            date_str = m.group(0)
            break

    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            metal = cols[0].get_text(strip=True)
            settlement_kasse = cols[1].get_text(strip=True)
            three_months = cols[2].get_text(strip=True)
            # 2. 將來源日期加入每一筆資料
            data.append({
                "金屬": metal,
                "Settlement Kasse": settlement_kasse,
                "3 months": three_months,
                "來源日期": date_str,
                "抓取時間": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "資料來源": "Westmetall"
            })
    df = pd.DataFrame(data)
    return df, f"已從網路獲取最新數據 (BeautifulSoup, 日期: {date_str})"

@st.cache_data(ttl=3600)
def fetch_bot_daily_fx():
    """從台灣銀行抓取每日匯率，正確解析掛牌日期與時間"""
    url = "https://rate.bot.com.tw/xrt/all/day"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html = response.text

        # 1. 用正則表達式抓取掛牌日期（格式如：2025/06/26 16:02）
        date_match = re.search(r'掛牌日期[:：]\\s*(\\d{4}/\\d{2}/\\d{2} \\d{2}:\\d{2})', html)
        if date_match:
            fx_date = date_match.group(1)
            fx_date_only = fx_date.split(' ')[0]
            fx_time_only = fx_date.split(' ')[1]
        else:
            fx_date_only = datetime.now().strftime('%Y-%m-%d')
            fx_time_only = datetime.now().strftime('%H:%M:%S')

        # 2. 讀取表格
        tables = pd.read_html(io.StringIO(html), header=0)
        df = tables[0]
        df.columns = ['幣別', '現金買入', '現金賣出', '即期買入', '即期賣出'] + list(df.columns[5:])
        clean_df = df[['幣別', '即期買入', '即期賣出']].copy()
        clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')
        clean_df['掛牌日期'] = fx_date_only
        clean_df['掛牌時間'] = fx_time_only
        return clean_df, f"已從網路獲取最新數據（掛牌日期：{fx_date_only} {fx_time_only}）"
    except Exception as e:
        return pd.DataFrame(), f"台銀匯率數據獲取失敗: {e}"

# --- 主程式 ---
def main():
    st.title("📅 前日收盤價參考")
    st.subheader("版本: V8 - 最終穩定版")
    
    # --- 加載數據 ---
    df_westmetall, msg_westmetall = fetch_westmetall_lme_data()
    df_fx_daily_all, msg_fx = fetch_bot_daily_fx()
    st.caption(f"Westmetall: {msg_westmetall} | 台銀匯率: {msg_fx}")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Westmetall LME 前日收盤價")
        if not df_westmetall.empty:
            st.dataframe(df_westmetall, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("台銀每日匯率 (USD/CNY)")
        df_fx_filtered = df_fx_daily_all[df_fx_daily_all['幣別'].str.contains("美金|人民幣|USD|CNY")]
        if not df_fx_filtered.empty:
            st.dataframe(
                df_fx_filtered[['幣別', '即期買入', '即期賣出', '掛牌日期', '掛牌時間']].rename(
                    columns={'幣別': '幣別', '即期買入': '即期買入', '即期賣出': '即期賣出', '掛牌日期': '掛牌日期', '掛牌時間': '掛牌時間'}
                ),
                use_container_width=True,
                hide_index=True
            )

    # --- CSP 價格計算機 ---
    st.markdown("---")
    st.subheader("CSP 價格試算")

    if df_westmetall.empty or df_fx_daily_all.empty:
        st.warning("因上方資料載入失敗，無法進行價格試算。")
    else:
        try:
            # 1. 計算美金中間匯率
            usd_row = df_fx_daily_all[df_fx_daily_all['幣別'].str.contains("美金|USD")]
            spot_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
            spot_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
            usd_mid_rate = (spot_buy + spot_sell) / 2
            st.metric(label="當前美金中間匯率", value=f"{usd_mid_rate:.4f}")

            # 2. 準備 LME 價格資料
            df_calc = df_westmetall.copy()
            df_calc.set_index('金屬', inplace=True)
            for col in df_calc.columns:
                 df_calc[col] = pd.to_numeric(df_calc[col].astype(str).str.replace(',', ''), errors='coerce')
            
            # 3. 根據公式計算價格
            copper_settlement = df_calc.loc['Copper', 'Settlement Kasse']
            tin_settlement = df_calc.loc['Tin', 'Settlement Kasse']
            zinc_settlement = df_calc.loc['Zinc', 'Settlement Kasse']
            tin_3m = df_calc.loc['Tin', '3 months']
            zinc_3m = df_calc.loc['Zinc', '3 months']

            price_phosphor = (copper_settlement * 0.94 + tin_settlement * 0.06) / 1000 * usd_mid_rate
            price_bronze = (copper_settlement * 0.65 + zinc_settlement * 0.35) / 1000 * usd_mid_rate
            price_red_copper = copper_settlement / 1000 * usd_mid_rate
            price_tin = tin_3m
            price_zinc = zinc_3m

            # 4. 建立結果表格
            csp_data = { '磷': f"NT${price_phosphor:,.2f}", '青': f"NT${price_bronze:,.2f}", '紅': f"NT${price_red_copper:,.2f}", '錫': f"US${price_tin:,.2f}", '鋅': f"US${price_zinc:,.2f}" }
            st.dataframe(pd.DataFrame([csp_data]), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"計算過程中發生錯誤: {e}")

    # --- 顯示歷史數據 ---
    if HISTORY_FILE.exists():
        st.markdown("---")
        st.subheader("CSP 價格歷史趨勢")
        history_df = pd.read_csv(HISTORY_FILE, parse_dates=["日期"])
        history_df.set_index("日期", inplace=True)
        st.line_chart(history_df[['CSP磷', 'CSP青', 'CSP紅']])


def save_to_history(df, date_col="日期"):
    """保存到歷史記錄"""
    if df.empty:
        return
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if HISTORY_FILE.exists():
        history_df = pd.read_csv(HISTORY_FILE)
        # 如果今天的日期已經存在，就不再儲存
        if '日期' in history_df.columns and today_str in history_df['日期'].values:
            return
        updated_df = pd.concat([history_df, df], ignore_index=True)
    else:
        updated_df = df
        
    updated_df.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
    st.toast("已更新歷史數據！")

if __name__ == "__main__":
    main()