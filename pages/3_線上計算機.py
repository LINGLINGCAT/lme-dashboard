import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io
import re
import sys
import os
from streamlit_autorefresh import st_autorefresh

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.auth import check_password, logout
except ImportError:
    # 如果無法導入認證模組，創建一個簡單的替代函數
    def check_password():
        return True
    
    def logout():
        st.rerun()

# 檢查密碼認證
check_password()

# --- 頁面設定 ---
st.set_page_config(page_title="線上計算機", page_icon="🧮", layout="wide")

# --- 資料來源 ---
lme_url = "https://quote.fx678.com/exchange/LME"
bot_url = "https://rate.bot.com.tw/xrt?Lang=zh-TW"

# --- 預設成分定義 ---
DEFAULT_COMPOSITIONS = {
    "C2680": {"銅": 65, "鋅": 35},
    "C2600": {"銅": 70, "鋅": 30},
    "磷青銅": {"銅": 94, "錫": 6},
    "青銅": {"銅": 65, "鋅": 35},
    "紅銅": {"銅": 100, "鋅": 0},
    "自定義": {}
}

def fetch_lme_data():
    """抓取 LME 即時價格"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(lme_url, headers=headers, timeout=15)
        response.raise_for_status()
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        df = df.rename(columns={df.columns[0]: "名稱", df.columns[1]: "最新價", df.columns[2]: "漲跌", df.columns[3]: "漲跌幅"})
        df = df[["名稱", "最新價", "漲跌", "漲跌幅"]]
        df['抓取時間'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['資料來源'] = 'LME'
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"LME 載入失敗: {e}"

def fetch_bot_fx_data():
    """抓取台銀即時匯率"""
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

def get_metal_prices(df_lme):
    """從 LME 數據中提取金屬價格"""
    if df_lme.empty:
        return {}, "LME 數據為空"
    
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
    
    prices = {}
    prices['銅'] = find_lme_name(df_calc, ['LME铜', 'LME銅'])
    prices['錫'] = find_lme_name(df_calc, ['LME锡', 'LME錫'])
    prices['鋅'] = find_lme_name(df_calc, ['LME锌', 'LME鋅'])
    
    # 檢查是否有缺失的價格
    missing_prices = [metal for metal, price in prices.items() if price is None]
    if missing_prices:
        return {}, f"缺少價格數據: {', '.join(missing_prices)}"
    
    return prices, None

def calculate_composition_price(composition, metal_prices, usd_rate, input_price=None, input_currency="TWD"):
    """計算成分價格"""
    if not composition:
        return None, "成分為空"
    
    # 計算成分的美元價格 (每噸)
    usd_price_per_ton = 0
    composition_text = []
    
    for metal, percentage in composition.items():
        if metal in metal_prices and metal_prices[metal] is not None:
            metal_price = metal_prices[metal]
            contribution = (metal_price * percentage / 100) / 1000  # 轉換為每公斤
            usd_price_per_ton += contribution
            composition_text.append(f"{percentage}%{metal}")
    
    if usd_price_per_ton == 0:
        return None, "無法計算價格"
    
    # 計算台幣價格
    twd_price_per_ton = usd_price_per_ton * usd_rate
    
    # 初始化變數
    percentage = 100
    usd_equivalent = usd_price_per_ton
    twd_equivalent = twd_price_per_ton
    
    # 如果用戶輸入了價格，計算百分比
    if input_price is not None:
        if input_currency == "TWD":
            # 輸入台幣，計算百分比
            percentage = (input_price / twd_price_per_ton) * 100
            usd_equivalent = input_price / usd_rate
            twd_equivalent = input_price
        else:  # USD
            # 輸入美金，計算百分比
            percentage = (input_price / usd_price_per_ton) * 100
            usd_equivalent = input_price
            twd_equivalent = input_price * usd_rate
    
    result = {
        "成分": " + ".join(composition_text),
        "美元價格/噸": usd_price_per_ton,
        "台幣價格/噸": twd_price_per_ton,
        "百分比": percentage,
        "美元等值": usd_equivalent,
        "台幣等值": twd_equivalent
    }
    
    return result, None

def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st_autorefresh(interval=30000, key="calculator_autorefresh")
    st.title("🧮 線上計算機")
    st.subheader("自定義成分計算與價格轉換")
    st.markdown("---")
    
    # --- 載入即時數據 ---
    with st.spinner("載入即時數據..."):
        df_lme, lme_error = fetch_lme_data()
        df_fx, fx_error = fetch_bot_fx_data()
    
    # 顯示數據狀態
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"LME 數據: {'✅ 成功' if lme_error is None else f'❌ {lme_error}'}")
    with col2:
        st.caption(f"台銀匯率: {'✅ 成功' if fx_error is None else f'❌ {fx_error}'}")
    
    st.markdown("---")
    
    # --- 成分設定與價格輸入 ---
    st.subheader("📋 成分設定與價格輸入")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 預設成分選擇
        selected_composition = st.selectbox(
            "選擇預設成分",
            list(DEFAULT_COMPOSITIONS.keys()),
            help="選擇預設成分或自定義"
        )
        
        # 自定義成分輸入
        st.markdown("**自定義成分 (百分比總和應為100%)**")
        
        # 創建成分輸入欄位
        composition = {}
        if selected_composition == "自定義":
            # 使用表格輸入方式
            st.markdown("**請輸入各金屬成分百分比：**")
            
            # 創建輸入表格
            col1, col2 = st.columns(2)
            
            with col1:
                cu_percent = st.number_input("銅 (%)", min_value=0.0, max_value=100.0, value=70.0, step=0.1, key="cu_input")
                sn_percent = st.number_input("錫 (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="sn_input")
            
            with col2:
                zn_percent = st.number_input("鋅 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1, key="zn_input")
                other_percent = st.number_input("其他 (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="other_input")
            
            # 組合成分字典
            if cu_percent > 0:
                composition["銅"] = cu_percent
            if sn_percent > 0:
                composition["錫"] = sn_percent
            if zn_percent > 0:
                composition["鋅"] = zn_percent
            if other_percent > 0:
                composition["其他"] = other_percent
                
            # 顯示當前成分
            if composition:
                st.info(f"**當前成分設定：** {composition}")
        else:
            composition = DEFAULT_COMPOSITIONS[selected_composition].copy()
            st.info(f"已選擇 {selected_composition}: {composition}")
        
        # 檢查成分總和
        total_percentage = sum(composition.values())
        if total_percentage != 100:
            st.warning(f"⚠️ 成分總和為 {total_percentage}%，應為 100%")
    
    with col2:
        # 價格輸入
        st.markdown("**輸入價格 (可選)**")
        input_currency = st.radio("幣別", ["TWD", "USD"], horizontal=True, key="price_currency_radio")
        input_price = st.number_input(
            f"價格 ({input_currency})",
            min_value=0.0,
            value=None,
            step=0.01,
            help="留空則顯示標準價格",
            key="price_input_field"
        )
        
        # 即時匯率顯示
        if not df_fx.empty:
            usd_row = df_fx[df_fx['幣別代碼'] == 'USD']
            if not usd_row.empty:
                usd_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
                usd_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
                usd_mid_rate = (usd_buy + usd_sell) / 2
                st.metric("即時匯率", f"1 USD = {usd_mid_rate:.2f} TWD")
            else:
                st.error("無法取得美金匯率")
                usd_mid_rate = 32.0  # 預設匯率
        else:
            st.error("無法取得匯率數據")
            usd_mid_rate = 32.0  # 預設匯率
    
    # 計算結果 (直接放在成分設定與價格輸入下方)
    if composition and total_percentage == 100:
        if not df_lme.empty:
            metal_prices, price_error = get_metal_prices(df_lme)
            if not price_error:
                # 取得匯率
                usd_mid_rate = 32.0  # 預設匯率
                if not df_fx.empty:
                    usd_row = df_fx[df_fx['幣別代碼'] == 'USD']
                    if not usd_row.empty:
                        usd_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
                        usd_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
                        usd_mid_rate = (usd_buy + usd_sell) / 2
                
                # 計算價格
                result, calc_error = calculate_composition_price(composition, metal_prices, usd_mid_rate, input_price, input_currency)
                if not calc_error:
                    st.markdown("---")
                    st.subheader("📊 計算結果")
                    
                    # 顯示計算結果
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "標準價格 (USD/噸)",
                            f"${result['美元價格/噸']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "標準價格 (TWD/噸)",
                            f"NT${result['台幣價格/噸']:,.2f}"
                        )
                    
                    with col3:
                        if input_price is not None:
                            st.metric(
                                "計算百分比",
                                f"{result['百分比']:.2f}%"
                            )
                        else:
                            st.metric(
                                "成分",
                                result["成分"]
                            )
                    
                    # 詳細結果表格
                    st.markdown("**詳細計算結果**")
                    result_df = pd.DataFrame([{
                        "項目": "成分",
                        "數值": result["成分"]
                    }, {
                        "項目": "標準美元價格/噸",
                        "數值": f"${result['美元價格/噸']:,.2f}"
                    }, {
                        "項目": "標準台幣價格/噸", 
                        "數值": f"NT${result['台幣價格/噸']:,.2f}"
                    }])
                    
                    if input_price is not None:
                        if input_currency == "TWD":
                            result_df = pd.concat([result_df, pd.DataFrame([{
                                "項目": f"輸入價格 ({input_currency})",
                                "數值": f"NT${input_price:,.2f}"
                            }, {
                                "項目": "美元等值",
                                "數值": f"${result['美元等值']:,.2f}"
                            }, {
                                "項目": "計算百分比",
                                "數值": f"{result['百分比']:.2f}%"
                            }])], ignore_index=True)
                        else:
                            result_df = pd.concat([result_df, pd.DataFrame([{
                                "項目": f"輸入價格 ({input_currency})",
                                "數值": f"${input_price:,.2f}"
                            }, {
                                "項目": "台幣等值",
                                "數值": f"NT${result['台幣等值']:,.2f}"
                            }, {
                                "項目": "計算百分比",
                                "數值": f"{result['百分比']:.2f}%"
                            }])], ignore_index=True)
                    
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    
                    # 百分比警告
                    if input_price is not None:
                        if result['百分比'] <= 0:
                            st.warning(f"⚠️ 警告：輸入價格過低，計算結果為 {result['百分比']:.2f}%")
                        elif result['百分比'] >= 150:
                            st.warning(f"⚠️ 警告：輸入價格過高，計算結果為 {result['百分比']:.2f}%")
    
    # 批量計算功能
    if composition and total_percentage == 100 and not df_lme.empty:
        metal_prices, price_error = get_metal_prices(df_lme)
        if not price_error:
            st.markdown("---")
            st.subheader("📊 批量計算")
            
            # 預設的批量計算組合
            batch_compositions = [
                {"銅": 70, "鋅": 30},
                {"銅": 80, "鋅": 20},
                {"銅": 90, "鋅": 10},
                {"銅": 95, "鋅": 5},
                {"銅": 98, "鋅": 2}
            ]
            
            if st.button("計算常見成分組合"):
                batch_results = []
                for comp in batch_compositions:
                    batch_result, _ = calculate_composition_price(comp, metal_prices, usd_mid_rate)
                    if batch_result:
                        batch_results.append({
                            "成分": batch_result["成分"],
                            "銅含量": f"{comp.get('銅', 0)}%",
                            "鋅含量": f"{comp.get('鋅', 0)}%",
                            "美元價格/噸": f"${batch_result['美元價格/噸']:,.2f}",
                            "台幣價格/噸": f"NT${batch_result['台幣價格/噸']:,.2f}"
                        })
                
                if batch_results:
                    batch_df = pd.DataFrame(batch_results)
                    st.dataframe(batch_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- 即時數據顯示 ---
    st.subheader("📈 即時參考數據")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**LME 金屬價格**")
        if not df_lme.empty:
            # 過濾主要金屬
            main_metals = df_lme[df_lme['名稱'].str.contains('銅|錫|鋅', na=False)]
            if not main_metals.empty:
                st.dataframe(main_metals[['名稱', '最新價', '漲跌', '漲跌幅']], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_lme[['名稱', '最新價', '漲跌', '漲跌幅']].head(5), use_container_width=True, hide_index=True)
        else:
            st.error("無法載入 LME 數據")
    
    with col2:
        st.markdown("**台銀匯率**")
        if not df_fx.empty:
            usd_cny_data = df_fx[df_fx['幣別代碼'].isin(['USD', 'CNY'])]
            if not usd_cny_data.empty:
                st.dataframe(usd_cny_data[['幣別', '即期買入', '即期賣出', '即期中間價']], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_fx[['幣別', '即期買入', '即期賣出', '即期中間價']].head(5), use_container_width=True, hide_index=True)
        else:
            st.error("無法載入匯率數據")

if __name__ == "__main__":
    main() 