import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import io
from pathlib import Path
import time

# --- 設定 ---
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
WESTMETALL_CACHE = DATA_DIR / "westmetall_cache.csv"
BOT_CACHE = DATA_DIR / "bot_cache.csv"
HISTORY_FILE = DATA_DIR / "csp_history.csv" # 重新命名，因為它現在包含計算結果

# --- 頁面設定 ---
st.set_page_config(page_title="每日收盤價參考", page_icon="📅", layout="wide")

# --- 資料獲取函式 (帶有檔案快取) ---
@st.cache_data(ttl=3600)
def fetch_data_with_cache(url, cache_file, fetch_function, *args):
    """通用快取邏輯"""
    try:
        if cache_file.exists():
            cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if (datetime.now() - cache_time).total_seconds() < 3600:
                return pd.read_csv(cache_file, encoding='utf-8-sig'), f"使用快取數據 (上次更新: {cache_time.strftime('%Y-%m-%d %H:%M:%S')})"
        
        df = fetch_function(url, *args)
        df.to_csv(cache_file, index=False, encoding='utf-8-sig')
        return df, "已從網路獲取最新數據"
    except Exception as e:
        if cache_file.exists():
            cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            return pd.read_csv(cache_file, encoding='utf-8-sig'), f"網路請求失敗，使用快取數據 ({e}) (上次更新: {cache_time.strftime('%Y-%m-%d %H:%M:%S')})"
        return pd.DataFrame(), f"數據獲取失敗，且無可用快取: {e}"

def parse_westmetall(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'data'})
    df = pd.read_html(str(table))[0]
    # 清理欄位名稱
    df.columns = ['金屬', '日期', 'Settlement', '3 months', 'Chart Table Average']
    df = df[['金屬', 'Settlement', '3 months']]
    return df

def parse_bot_fx(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    tables = pd.read_html(io.StringIO(response.text))
    df = tables[0]
    df.columns = ['幣別', '現金買入', '現金賣出', '即期買入', '即期賣出'] + list(df.columns[5:])
    clean_df = df[['幣別', '即期買入', '即期賣出']].copy()
    clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')
    return clean_df

# --- 主程式 ---
def main():
    st.title("📅 每日收盤價參考")
    
    # --- 加載數據 ---
    with st.spinner("正在獲取最新數據..."):
        df_westmetall, msg_westmetall = fetch_data_with_cache("https://www.westmetall.com/en/markdaten.php", WESTMETALL_CACHE, parse_westmetall)
        df_fx_daily_all, msg_fx = fetch_data_with_cache("https://rate.bot.com.tw/xrt/all/day", BOT_CACHE, parse_bot_fx)

    st.caption(f"Westmetall: {msg_westmetall} | 台銀匯率: {msg_fx}")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Westmetall LME 收盤價")
        if df_westmetall.empty:
            st.warning("Westmetall 數據無法載入。")
        else:
            st.dataframe(df_westmetall, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("台銀每日匯率 (USD/CNY)")
        if df_fx_daily_all.empty:
            st.warning("台銀匯率數據無法載入。")
        else:
            df_fx_daily_filtered = df_fx_daily_all[df_fx_daily_all['幣別代碼'].isin(['USD', 'CNY'])]
            st.dataframe(df_fx_daily_filtered[['幣別代碼', '即期買入', '即期賣出']].rename(columns={'幣別代碼': '幣別'}), use_container_width=True, hide_index=True)

    # --- CSP 價格計算機 ---
    st.markdown("---")
    st.subheader("CSP 價格試算")

    if df_westmetall.empty or df_fx_daily_all.empty:
        st.warning("因上方資料載入失敗，無法進行價格試算。")
    else:
        try:
            # 1. 計算美金中間匯率
            usd_row = df_fx_daily_all[df_fx_daily_all['幣別代碼'] == 'USD']
            if usd_row.empty:
                st.error("無法在台銀匯率中找到美金(USD)資料。")
            else:
                spot_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
                spot_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
                usd_mid_rate = (spot_buy + spot_sell) / 2
                st.metric(label="當前美金中間匯率", value=f"{usd_mid_rate:.4f}")

                # 2. 準備 LME 價格資料
                df_calc = df_westmetall.copy()
                df_calc.set_index('金屬', inplace=True)
                for col in df_calc.columns:
                    df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce')

                # 3. 根據公式計算價格
                copper_settlement = df_calc.loc['Copper', 'Settlement']
                tin_settlement = df_calc.loc['Tin', 'Settlement']
                zinc_settlement = df_calc.loc['Zinc', 'Settlement']
                tin_3m = df_calc.loc['Tin', '3 months']
                zinc_3m = df_calc.loc['Zinc', '3 months']

                price_phosphor = (copper_settlement * 0.94 + tin_settlement * 0.06) / 1000 * usd_mid_rate
                price_bronze = (copper_settlement * 0.65 + zinc_settlement * 0.35) / 1000 * usd_mid_rate
                price_red_copper = copper_settlement / 1000 * usd_mid_rate
                price_tin = tin_3m
                price_zinc = zinc_3m

                # 4. 建立結果表格
                csp_data = {
                    '磷': f"NT${price_phosphor:,.2f}",
                    '青': f"NT${price_bronze:,.2f}",
                    '紅': f"NT${price_red_copper:,.2f}",
                    '錫': f"US${price_tin:,.2f}",
                    '鋅': f"US${price_zinc:,.2f}"
                }
                st.dataframe(pd.DataFrame([csp_data]), use_container_width=True, hide_index=True)
                
                # 5. 保存歷史數據
                history_data = {
                    '日期': datetime.now().strftime('%Y-%m-%d'),
                    '美金中間價': usd_mid_rate,
                    'LME銅價': copper_settlement,
                    'CSP磷': price_phosphor,
                    'CSP青': price_bronze,
                    'CSP紅': price_red_copper
                }
                save_to_history(pd.DataFrame([history_data]))

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