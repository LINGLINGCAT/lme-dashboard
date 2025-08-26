import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import io
from pathlib import Path
import time
import re
from utils.auth import check_password, logout

# 檢查密碼認證
check_password()

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
    """從台灣銀行抓取每日匯率，正確解析掛牌時間（如 2025/06/26 16:02）"""
    url = "https://rate.bot.com.tw/xrt/all/day"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        html = response.text

        # 1. 用正則表達式抓取掛牌時間（格式如：2025/06/26 16:02）
        date_match = re.search(r'掛牌時間[：:]\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2})', html)
        if not date_match:
            # 有時候會寫成「掛牌日期」
            date_match = re.search(r'掛牌日期[：:]\s*(\d{4}/\d{2}/\d{2} \d{2}:\d{2})', html)
        if date_match:
            fx_datetime = date_match.group(1)
        else:
            fx_datetime = datetime.now().strftime('%Y/%m/%d %H:%M')

        # 2. 讀取表格
        tables = pd.read_html(io.StringIO(html), header=0)
        df = tables[0]
        df.columns = ['幣別', '現金買入', '現金賣出', '即期買入', '即期賣出'] + list(df.columns[5:])
        clean_df = df[['幣別', '即期買入', '即期賣出']].copy()
        clean_df['幣別代碼'] = clean_df['幣別'].str.extract(r'([A-Z]{3})')
        clean_df['掛牌時間'] = fx_datetime  # 直接合併日期與時間
        return clean_df, f"已從網路獲取最新數據（掛牌時間：{fx_datetime}）"
    except Exception as e:
        return pd.DataFrame(), f"台銀匯率數據獲取失敗: {e}"

def save_lme_data_to_csv(lme_data, fx_data):
    """保存LME和FX數據到CSV文件"""
    try:
        from pathlib import Path
        from datetime import datetime
        
        # 確保data目錄存在
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 準備數據
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 合併LME和FX數據
        combined_data = {}
        combined_data['日期'] = today
        
        # 添加LME數據
        if lme_data:
            for metal, price in lme_data.items():
                if price and price != 'N/A':
                    combined_data[f'LME_{metal}'] = price
        
        # 添加FX數據
        if fx_data:
            for currency, rate in fx_data.items():
                if rate and rate != 'N/A':
                    combined_data[f'FX_{currency}'] = rate
        
        # 檢查是否已有今天的數據
        csv_path = data_dir / "lme_daily_data.csv"
        
        if csv_path.exists():
            # 讀取現有數據
            existing_df = pd.read_csv(csv_path)
            
            # 檢查今天是否已有數據
            if today not in existing_df['日期'].values:
                # 添加新數據
                new_row = pd.DataFrame([combined_data])
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                updated_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                st.success(f"✅ 已保存今日數據到 {csv_path}")
            else:
                st.info(f"ℹ️ 今日數據已存在於 {csv_path}")
        else:
            # 創建新文件
            new_df = pd.DataFrame([combined_data])
            new_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            st.success(f"✅ 已創建並保存數據到 {csv_path}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ 保存數據失敗：{e}")
        return False

# --- 主程式 ---
def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st.title("📅 前日收盤價")
    st.subheader("版本: V9")
    
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
        st.subheader("台銀歷史匯率 (USD/CNY)")
        df_fx_filtered = df_fx_daily_all[df_fx_daily_all['幣別'].str.contains("美金|人民幣|USD|CNY")]
        if not df_fx_filtered.empty:
            st.dataframe(
                df_fx_filtered[['幣別', '即期買入', '即期賣出', '掛牌時間']],
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
            st.metric(label="歷史美金中間匯率", value=f"{usd_mid_rate:.4f}")

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

            # 5. 保存到歷史數據
            today = datetime.now().strftime('%Y-%m-%d')
            history_data = {
                '日期': [today],
                'CSP磷': [f"NT${price_phosphor:,.2f}"],
                'CSP青': [f"NT${price_bronze:,.2f}"],
                'CSP紅': [f"NT${price_red_copper:,.2f}"],
                'CSP錫': [f"US${price_tin:,.2f}"],
                'CSP鋅': [f"US${price_zinc:,.2f}"]
            }
            history_df = pd.DataFrame(history_data)
            save_to_history(history_df)

        except Exception as e:
            st.error(f"計算過程中發生錯誤: {e}")

    # --- 顯示歷史數據 ---
    if HISTORY_FILE.exists():
        st.markdown("---")
        st.subheader("CSP 價格歷史趨勢")
        history_df = pd.read_csv(HISTORY_FILE, parse_dates=["日期"])
        history_df.set_index("日期", inplace=True)
        st.line_chart(history_df[['CSP磷', 'CSP青', 'CSP紅']])

    # 在頁面底部添加保存按鈕
    st.markdown("---")
    st.subheader("💾 數據保存")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 保存今日數據", type="primary"):
            if 'lme_data' in st.session_state and 'fx_data' in st.session_state:
                save_lme_data_to_csv(st.session_state.lme_data, st.session_state.fx_data)
            else:
                st.warning("⚠️ 請先載入LME和FX數據")
    
    with col2:
        if st.button("📊 查看歷史數據"):
            csv_path = Path("data/lme_daily_data.csv")
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("📋 尚未有歷史數據")


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