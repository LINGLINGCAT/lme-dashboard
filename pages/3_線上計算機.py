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
    "紅銅": {"銅": 100, "鋅": 0},
    "自定義": {}
}

def parse_lme_formula(formula, metal_prices):
    """解析LME係數公式並計算價格"""
    try:
        # 清理公式
        formula = formula.lower().replace(' ', '')
        
        # 處理銅價百分比公式 (如: lme銅價*72%)
        if 'lme銅價' in formula or 'lme铜' in formula:
            copper_price = metal_prices.get('銅')
            if copper_price is None:
                return None, "無法取得銅價"
            
            # 提取百分比
            percentage_match = re.search(r'\*(\d+(?:\.\d+)?)%?', formula)
            if percentage_match:
                percentage = float(percentage_match.group(1))
                usd_price = copper_price * percentage / 100
                return {
                    'usd_price': usd_price,
                    'formula_type': 'copper_percentage',
                    'percentage': percentage,
                    'copper_price': copper_price
                }, None
            else:
                return None, "無法解析銅價百分比公式"
        
        # 處理複合成分公式 (如: (cu*65+zn*35)*98%)
        elif '(' in formula and ')' in formula:
            # 提取括號內的部分
            inner_match = re.search(r'\((.*?)\)', formula)
            if not inner_match:
                return None, "無法解析括號內容"
            
            inner_formula = inner_match.group(1)
            
            # 提取最終百分比
            final_percentage_match = re.search(r'\*(\d+(?:\.\d+)?)%?', formula)
            final_percentage = 100
            if final_percentage_match:
                final_percentage = float(final_percentage_match.group(1))
            
            # 解析內部成分
            components = inner_formula.split('+')
            total_price = 0
            composition_parts = []
            
            for component in components:
                # 解析每個成分 (如: cu*65% 或 cu*65)
                metal_match = re.search(r'([a-z]+)\*(\d+(?:\.\d+)?)%?', component)
                if metal_match:
                    metal_code = metal_match.group(1)
                    percentage = float(metal_match.group(2))
                    
                    # 轉換金屬代碼
                    metal_map = {'cu': '銅', 'zn': '鋅', 'sn': '錫', 'ni': '鎳'}
                    metal_name = metal_map.get(metal_code, metal_code)
                    
                    if metal_name in metal_prices:
                        metal_price = metal_prices[metal_name]
                        contribution = (metal_price * percentage / 100) / 1000  # 轉換為每公斤
                        total_price += contribution
                        composition_parts.append(f"{metal_name}{percentage}%")
                    else:
                        return None, f"無法取得{metal_name}價格"
            
            # 應用最終百分比
            final_price = total_price * final_percentage / 100
            
            return {
                'usd_price': final_price,
                'formula_type': 'composition_percentage',
                'composition': composition_parts,
                'final_percentage': final_percentage,
                'base_price': total_price
            }, None
        
        else:
            return None, "不支援的公式格式"
    
    except Exception as e:
        return None, f"公式解析錯誤: {str(e)}"

def calculate_reverse_percentage(target_price, base_price, formula_type, metal_prices, original_formula=None):
    """計算回推百分比"""
    try:
        if formula_type == 'copper_percentage':
            # 銅價百分比公式回推
            copper_price = metal_prices.get('銅')
            if copper_price is None:
                return None, "無法取得銅價"
            
            # 計算目標價格對應的銅價百分比
            target_percentage = (target_price / copper_price) * 100
            
            # 計算對應的複合成分百分比 - 支援多種標準成分
            reverse_results = {}
            
            # 常見的銅合金成分組合
            common_compositions = [
                {"name": "C2680", "formula": "(cu*65%+zn*35%)", "cu": 65, "zn": 35},
                {"name": "C2600", "formula": "(cu*70%+zn*30%)", "cu": 70, "zn": 30},
                {"name": "C2200", "formula": "(cu*90%+zn*10%)", "cu": 90, "zn": 10},
                {"name": "C2100", "formula": "(cu*95%+zn*5%)", "cu": 95, "zn": 5},
                {"name": "磷青銅", "formula": "(cu*94%+sn*6%)", "cu": 94, "sn": 6},
                {"name": "青銅", "formula": "(cu*88%+sn*12%)", "cu": 88, "sn": 12},
                {"name": "紅銅", "formula": "(cu*100%)", "cu": 100, "zn": 0}
            ]
            
            for comp in common_compositions:
                composition_price = (
                    (copper_price * comp["cu"] / 100) / 1000 +  # 銅的貢獻
                    (metal_prices.get('鋅', 0) * comp.get("zn", 0) / 100) / 1000 +  # 鋅的貢獻
                    (metal_prices.get('錫', 0) * comp.get("sn", 0) / 100) / 1000  # 錫的貢獻
                )
                
                if composition_price > 0:
                    comp_percentage = (target_price / composition_price) * 100
                    reverse_results[comp["name"]] = {
                        "formula": comp["formula"],
                        "percentage": comp_percentage
                    }
            
            return {
                'copper_percentage': target_percentage,
                'composition_results': reverse_results,
                'target_price': target_price
            }, None
        
        elif formula_type == 'composition_percentage':
            # 複合成分公式回推
            copper_price = metal_prices.get('銅')
            if copper_price is None:
                return None, "無法取得銅價"
            
            # 計算對應的銅價百分比
            copper_percentage = (target_price / copper_price) * 100
            
            # 如果有原始公式，嘗試解析成分
            composition_info = None
            if original_formula:
                try:
                    # 從原始公式中提取成分資訊
                    inner_match = re.search(r'\((.*?)\)', original_formula.lower())
                    if inner_match:
                        inner_formula = inner_match.group(1)
                        components = inner_formula.split('+')
                        composition_parts = []
                        
                        for component in components:
                            metal_match = re.search(r'([a-z]+)\*(\d+(?:\.\d+)?)', component)
                            if metal_match:
                                metal_code = metal_match.group(1)
                                percentage = float(metal_match.group(2))
                                metal_map = {'cu': '銅', 'zn': '鋅', 'sn': '錫'}
                                metal_name = metal_map.get(metal_code, metal_code)
                                composition_parts.append(f"{metal_name}{percentage}%")
                        
                        composition_info = " + ".join(composition_parts)
                except:
                    composition_info = "無法解析原始成分"
            
            return {
                'copper_percentage': copper_percentage,
                'original_composition': composition_info,
                'original_formula': original_formula
            }, None
        
        else:
            return None, "不支援的公式類型"
    
    except Exception as e:
        return None, f"回推計算錯誤: {str(e)}"

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
    prices['鎳'] = find_lme_name(df_calc, ['LME镍', 'LME鎳'])
    
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
            contribution = (metal_price * percentage / 100)  # 直接計算每噸價格
            usd_price_per_ton += contribution
            composition_text.append(f"{percentage}%{metal}")
    
    if usd_price_per_ton == 0:
        return None, "無法計算價格"
    
    # 計算台幣價格 (每公斤)
    twd_price_per_kg = (usd_price_per_ton * usd_rate) / 1000
    
    # 初始化變數
    percentage = 100
    usd_equivalent = usd_price_per_ton
    twd_equivalent = twd_price_per_kg
    
    # 如果用戶輸入了價格，計算百分比
    if input_price is not None:
        if input_currency == "TWD":
            # 輸入台幣，計算百分比
            percentage = (input_price / twd_price_per_kg) * 100
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
        "台幣價格/公斤": twd_price_per_kg,
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
            # 使用與預設成分相同的顯示方式
            st.markdown("**請輸入各金屬成分百分比：**")
            
            # 使用更緊湊的排版，避免右邊空白
            cu_percent = st.number_input("銅 (%)", min_value=0.0, max_value=100.0, value=70.0, step=0.1, key="cu_input")
            zn_percent = st.number_input("鋅 (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1, key="zn_input")
            sn_percent = st.number_input("錫 (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="sn_input")
            ni_percent = st.number_input("鎳 (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="ni_input")
            other_percent = st.number_input("其他 (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="other_input")
            
            # 組合成分字典
            metals = [
                ("銅", cu_percent),
                ("錫", sn_percent),
                ("鋅", zn_percent),
                ("鎳", ni_percent),
                ("其他", other_percent)
            ]
            
            for metal, percent in metals:
                if percent > 0:
                    composition[metal] = percent
                
            # 顯示當前成分（與預設成分相同的格式）
            if composition:
                # 使用與預設成分完全相同的顯示格式
                st.markdown(f"""
                <div style="
                    background-color: #e8f4fd;
                    border: 1px solid #bee5eb;
                    border-radius: 0.375rem;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    color: #0c5460;
                    font-weight: 500;
                ">
                    <strong>已選擇 自定義:</strong> {composition}
                </div>
                """, unsafe_allow_html=True)
        else:
            composition = DEFAULT_COMPOSITIONS[selected_composition].copy()
            st.markdown(f"""
            <div style="
                background-color: #e8f4fd;
                border: 1px solid #bee5eb;
                border-radius: 0.375rem;
                padding: 1rem;
                margin: 0.5rem 0;
                color: #0c5460;
                font-weight: 500;
            ">
                <strong>已選擇 {selected_composition}:</strong> {composition}
            </div>
            """, unsafe_allow_html=True)
        
        # 檢查成分總和
        total_percentage = sum(composition.values())
        if total_percentage != 100:
            st.warning(f"⚠️ 成分總和為 {total_percentage}%，應為 100%")
        
        # 在左側欄位底部顯示標準價格
        if composition and total_percentage == 100 and not df_lme.empty:
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
                
                # 計算標準價格
                result, calc_error = calculate_composition_price(composition, metal_prices, usd_mid_rate)
                if not calc_error:
                    st.markdown("---")
                    st.markdown("**📊 標準價格**")
                    
                    # 顯示標準價格 - 調整排版
                    col_price1, col_price2, col_price3 = st.columns(3)
                    
                    with col_price1:
                        st.metric(
                            "標準價格 (USD/噸)",
                            f"${result['美元價格/噸']:,.0f}"
                        )
                    
                    with col_price2:
                        st.metric(
                            "標準價格 (TWD/公斤)",
                            f"NT${result['台幣價格/公斤']:,.2f}"
                        )
                    
                    # 計算LME係數或百分比
                    copper_price = metal_prices.get('銅', 0)
                    if copper_price > 0:
                        # 檢查是否在LME係數計算模式下
                        if 'calc_mode' in locals() and calc_mode == "LME係數計算" and 'lme_calc_type' in locals():
                            if lme_calc_type == "複合成分係數":
                                # 複合成分係數模式：顯示LME係數
                                lme_coefficient = (result['美元價格/噸']) / copper_price
                                with col_price3:
                                    st.metric(
                                        "LME百分比",
                                        f"{lme_coefficient:.2f}%"
                                    )
                            else:
                                # 銅價百分比模式：顯示LME係數
                                lme_coefficient = (result['美元價格/噸']) / copper_price
                                with col_price3:
                                    st.metric(
                                        "LME百分比",
                                        f"{lme_coefficient:.2f}%"
                                    )
                        else:
                            # 標準模式：顯示LME百分比
                            lme_percentage = (result['美元價格/噸'] / copper_price) * 100
                            with col_price3:
                                st.metric(
                                    "LME百分比",
                                    f"{lme_percentage:.2f}%"
                                )
    
    with col2:
        # 計算模式選擇
        calc_mode = st.radio(
            "計算模式",
            ["現價計算", "係數計算"],
            horizontal=True,
            key="calc_mode_radio"
        )
        
        if calc_mode == "現價計算":
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
        else:  # LME係數計算
            # LME係數設定
            st.markdown("**LME係數設定**")
            lme_calc_type = st.radio(
                "計算類型",
                ["複合成分係數", "銅價百分比"],
                horizontal=True,
                key="lme_calc_type"
            )
            
            if lme_calc_type == "複合成分係數":
                # 成分係數百分比輸入
                final_percentage = st.number_input(
                    "成分係數百分比 (%)",
                    min_value=0.0,
                    max_value=200.0,
                    value=98.0,
                    step=0.1,
                    help="例如：98% 表示 (成分)*98%",
                    key="final_percentage_input"
                )
                input_price = None
                input_currency = "TWD"
            else:  # 銅價百分比
                copper_percentage = st.number_input(
                    "銅價百分比 (%)",
                    min_value=0.0,
                    max_value=200.0,
                    value=72.0,
                    step=0.1,
                    help="例如：72% 表示 lme銅價*72%",
                    key="copper_percentage_input"
                )
                input_price = None
                input_currency = "TWD"
        
        # 即時匯率顯示
        if not df_fx.empty:
            usd_row = df_fx[df_fx['幣別代碼'] == 'USD']
            if not usd_row.empty:
                usd_buy = pd.to_numeric(usd_row['即期買入'].iloc[0], errors='coerce')
                usd_sell = pd.to_numeric(usd_row['即期賣出'].iloc[0], errors='coerce')
                usd_mid_rate = (usd_buy + usd_sell) / 2
                st.metric("即時匯率", f"1 USD = {usd_mid_rate:.3f} TWD")
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
                
                # 只在有輸入價格或LME係數計算時顯示結果
                if (calc_mode == "現價計算" and input_price is not None) or calc_mode == "係數計算":
                    # 現價計算
                    result, calc_error = calculate_composition_price(composition, metal_prices, usd_mid_rate, input_price, input_currency)
                    if not calc_error:
                        st.markdown("---")
                        st.subheader("📊 成分百分比")
                        
                        # 顯示計算結果
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if input_price is not None:
                                if input_currency == "TWD":
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${result['美元等值']*1000:,.0f}"
                                    )
                                else:
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${input_price:,.0f}"
                                    )
                            else:
                                # 在LME係數計算模式下，顯示計算後的價格
                                if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                                    final_price = result['美元價格/噸'] * final_percentage / 100
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${final_price:,.2f}"
                                    )
                                elif calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                    # 銅價百分比模式：LME銅價 × 百分比
                                    copper_price = metal_prices.get('銅', 0)
                                    if copper_price > 0:
                                        calculated_price = copper_price * copper_percentage / 100
                                        st.metric(
                                            "成分價格 (USD/噸)",
                                            f"${calculated_price:,.0f}"
                                        )
                                    else:
                                        st.metric(
                                            "成分價格 (USD/噸)",
                                            f"${result['美元價格/噸']:,.0f}"
                                        )
                                else:
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${result['美元價格/噸']:,.0f}"
                                    )
                        
                        with col2:
                            if input_price is not None:
                                if input_currency == "TWD":
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${input_price:,.2f}"
                                    )
                                else:
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${result['台幣等值']/1000:,.2f}"
                                    )
                            else:
                                # 在LME係數計算模式下，顯示計算後的價格
                                if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                                    final_price = result['美元價格/噸'] * final_percentage / 100
                                    twd_price = (final_price * usd_mid_rate) / 1000
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${twd_price:,.2f}"
                                    )
                                elif calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                    # 銅價百分比模式：LME銅價 × 百分比
                                    copper_price = metal_prices.get('銅', 0)
                                    if copper_price > 0:
                                        calculated_price = copper_price * copper_percentage / 100
                                        twd_price = (calculated_price * usd_mid_rate) / 1000
                                        st.metric(
                                            "成分價格 (TWD/公斤)",
                                            f"NT${twd_price:,.2f}"
                                        )
                                    else:
                                        st.metric(
                                            "成分價格 (TWD/公斤)",
                                            f"NT${result['台幣價格/公斤']:,.2f}"
                                        )
                                else:
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${result['台幣價格/公斤']:,.2f}"
                                    )
                        
                        with col3:
                            if input_price is not None:
                                # 計算LME百分比
                                copper_price = metal_prices.get('銅', 0)
                                if copper_price > 0:
                                    if input_currency == "TWD":
                                        usd_price_for_lme = result['美元等值'] * 1000  # 轉換為每噸
                                        lme_percentage = (usd_price_for_lme / copper_price) * 100
                                    else:
                                        usd_price_for_lme = input_price
                                        lme_percentage = (usd_price_for_lme / copper_price) * 100
                                    st.metric(
                                        "LME百分比",
                                        f"{lme_percentage:.2f}%"
                                    )
                                else:
                                    st.metric(
                                        "成分百分比",
                                        f"{result['百分比']:.2f}%"
                                    )
                            else:
                                # 計算LME係數
                                copper_price = metal_prices.get('銅', 0)
                                if copper_price > 0:
                                                                        # 在LME係數計算模式下，應該顯示最終計算價格的LME係數
                                    if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                                        # 使用最終計算價格
                                        final_price = result['美元價格/噸'] * final_percentage / 100
                                        lme_coefficient = (final_price / copper_price) * 100
                                    elif calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                        # 銅價百分比模式
                                        user_percentage = copper_percentage
                                        calculated_price = copper_price * user_percentage / 100
                                        # 計算成分百分比：成分價格 / 標準價格
                                        composition_result, _ = calculate_composition_price(composition, metal_prices, usd_mid_rate)
                                        if composition_result:
                                            standard_price = composition_result['美元價格/噸']
                                            lme_coefficient = (calculated_price / standard_price) * 100
                                        else:
                                            lme_coefficient = 0
                                    else:
                                        # 使用標準價格
                                        usd_price_for_lme = result['美元價格/噸']
                                        lme_coefficient = (usd_price_for_lme) / copper_price
                                    
                                    # 根據模式顯示不同的標籤
                                    if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                        st.metric(
                                            "成分百分比",
                                            f"{lme_coefficient:.2f}%"
                                        )
                                    else:
                                        st.metric(
                                            "LME百分比",
                                            f"{lme_coefficient:.2f}%"
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
                        }])
                        
                        # 根據是否有輸入價格來決定顯示的價格
                        if input_price is not None:
                            if input_currency == "TWD":
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${result['美元等值']*1000:,.0f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)", 
                                    "數值": f"NT${input_price:,.2f}"
                                }])], ignore_index=True)
                            else:
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${input_price:,.0f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)", 
                                    "數值": f"NT${result['台幣等值']/1000:,.2f}"
                                }])], ignore_index=True)
                        else:
                            # 在係數計算模式下，顯示計算後的價格
                            if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                                final_price = result['美元價格/噸'] * final_percentage / 100
                                twd_price = (final_price * usd_mid_rate) / 1000
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${final_price:,.2f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)", 
                                    "數值": f"NT${twd_price:,.2f}"
                                }])], ignore_index=True)
                            elif calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                # 銅價百分比模式：LME銅價 × 百分比
                                copper_price = metal_prices.get('銅', 0)
                                if copper_price > 0:
                                    calculated_price = copper_price * copper_percentage / 100
                                    twd_price = (calculated_price * usd_mid_rate) / 1000
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "成分價格 (USD/噸)",
                                        "數值": f"${calculated_price:,.2f}"
                                    }, {
                                        "項目": "成分價格 (TWD/公斤)", 
                                        "數值": f"NT${twd_price:,.2f}"
                                    }])], ignore_index=True)
                                else:
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "成分價格 (USD/噸)",
                                        "數值": f"${result['美元價格/噸']:,.0f}"
                                    }, {
                                        "項目": "成分價格 (TWD/公斤)", 
                                        "數值": f"NT${result['台幣價格/公斤']:,.2f}"
                                    }])], ignore_index=True)
                            else:
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${result['美元價格/噸']:,.0f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)", 
                                    "數值": f"NT${result['台幣價格/公斤']:,.2f}"
                                }])], ignore_index=True)
                        
                        # 添加LME係數（當沒有輸入價格時）
                        if input_price is None:
                            copper_price = metal_prices.get('銅', 0)
                            if copper_price > 0:
                                # 在係數計算模式下，顯示LME係數
                                if calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                                    final_price = result['美元價格/噸'] * final_percentage / 100
                                    lme_coefficient = (final_price / copper_price) * 100
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "LME百分比",
                                        "數值": f"{lme_coefficient:.2f}%"
                                    }, {
                                        "項目": "LME銅價",
                                        "數值": f"${copper_price:,.2f}"
                                    }])], ignore_index=True)
                                elif calc_mode == "係數計算" and 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":
                                    user_percentage = copper_percentage
                                    calculated_price = copper_price * user_percentage / 100
                                    # 計算成分百分比：成分價格 / 標準價格
                                    composition_result, _ = calculate_composition_price(composition, metal_prices, usd_mid_rate)
                                    if composition_result:
                                        standard_price = composition_result['美元價格/噸']
                                        composition_percentage = (calculated_price / standard_price) * 100
                                    else:
                                        composition_percentage = 0
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "成分百分比",
                                        "數值": f"{composition_percentage:.2f}%"
                                    }, {
                                        "項目": "標準價格",
                                        "數值": f"${standard_price:,.2f}"
                                    }])], ignore_index=True)
                                else:
                                    # 標準模式顯示LME百分比
                                    lme_percentage = (result['美元價格/噸'] / copper_price) * 100
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "LME百分比",
                                        "數值": f"{lme_percentage:.2f}%"
                                    }, {
                                        "項目": "LME銅價",
                                        "數值": f"${copper_price:,.2f}"
                                    }])], ignore_index=True)
                        
                        if input_price is not None:
                            if input_currency == "TWD":
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分百分比",
                                    "數值": f"{result['百分比']:.2f}%"
                                }])], ignore_index=True)
                            else:
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": "成分百分比",
                                    "數值": f"{result['百分比']:.2f}%"
                                }])], ignore_index=True)
                            
                            # 添加LME百分比（當有輸入價格時）
                            if input_price is not None:
                                copper_price = metal_prices.get('銅', 0)
                                if copper_price > 0:
                                    if input_currency == "TWD":
                                        usd_price_for_lme = result['美元等值'] * 1000  # 轉換為每噸
                                    else:
                                        usd_price_for_lme = input_price
                                    
                                    lme_percentage = (usd_price_for_lme / copper_price) * 100
                                    result_df = pd.concat([result_df, pd.DataFrame([{
                                        "項目": "LME百分比",
                                        "數值": f"{lme_percentage:.2f}%"
                                    }, {
                                        "項目": "LME銅價",
                                        "數值": f"${copper_price:,.2f}"
                                    }])], ignore_index=True)
                            else:
                                result_df = pd.concat([result_df, pd.DataFrame([{
                                    "項目": f"輸入價格 ({input_currency})",
                                    "數值": f"${input_price:,.2f}"
                                }, {
                                    "項目": "台幣等值",
                                    "數值": f"NT${result['台幣等值']/1000:,.2f}"
                                }, {
                                    "項目": "成分百分比",
                                    "數值": f"{result['百分比']:.2f}%"
                                }])], ignore_index=True)
                        
                        st.dataframe(result_df, use_container_width=True, hide_index=True)
                        
                        # 百分比警告
                        if input_price is not None:
                            if result['百分比'] <= 0:
                                st.warning(f"⚠️ 警告：輸入價格過低，成分百分比為 {result['百分比']:.2f}%")
                            elif result['百分比'] >= 150:
                                st.warning(f"⚠️ 警告：輸入價格過高，成分百分比為 {result['百分比']:.2f}%")
                
                else:  # 係數計算
                    # 係數計算
                    # 檢查是否在係數計算模式下
                    if calc_mode == "係數計算":
                        # 確保 lme_calc_type 有定義
                        if 'lme_calc_type' in locals() and lme_calc_type == "複合成分係數":
                            # 複合成分係數計算邏輯
                            # 1. 計算標準成分價格
                            composition_result, _ = calculate_composition_price(composition, metal_prices, usd_mid_rate)
                            if composition_result:
                                standard_price = composition_result['美元價格/噸']
                                
                                # 2. 應用最終百分比計算成分價格
                                calculated_price = standard_price * final_percentage / 100
                                twd_price = (calculated_price * usd_mid_rate) / 1000
                                
                                # 3. 計算LME係數：(計算價格) / 銅價
                                copper_price = metal_prices.get('銅')
                                if copper_price:
                                    lme_coefficient = (calculated_price / copper_price) * 100
                                else:
                                    lme_coefficient = 0
                                
                                st.markdown("---")
                                st.subheader("📊 係數計算結果")
                                
                                # 顯示計算結果
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${calculated_price:,.2f}"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${twd_price:,.2f}"
                                    )
                                
                                with col3:
                                    st.metric(
                                        "LME百分比",
                                        f"{lme_coefficient:.2f}%"
                                    )
                                
                                # 詳細結果
                                st.markdown("**詳細計算結果**")
                                detail_df = pd.DataFrame([{
                                    "項目": "計算公式",
                                    "數值": f"標準價格 × {final_percentage}%"
                                }, {
                                    "項目": "標準價格 (USD/噸)",
                                    "數值": f"${standard_price:,.2f}"
                                }, {
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${calculated_price:,.2f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)",
                                    "數值": f"NT${twd_price:,.2f}"
                                }, {
                                    "項目": "LME百分比",
                                    "數值": f"{lme_coefficient:.2f}%"
                                }, {
                                    "項目": "當前銅價",
                                    "數值": f"${copper_price:,.2f}"
                                }])
                                
                                st.dataframe(detail_df, use_container_width=True, hide_index=True)
                                
                                # 顯示計算說明
                                st.markdown("**計算說明**")
                                st.info(f"""
                                - **計算公式**: 標準價格 × {final_percentage}% = ${calculated_price:,.2f}/kg
                                - **標準價格**: {composition} 的標準價格 = ${standard_price:,.2f}/kg
                                - **LME百分比**: (成分價格) ÷ 銅價 = {lme_coefficient:.2f}%
                                """)
                            else:
                                st.error("無法計算標準成分價格")
                                return
                        
                        elif 'lme_calc_type' in locals() and lme_calc_type == "銅價百分比":  # 銅價百分比
                            # 銅價百分比計算邏輯
                            copper_price = metal_prices.get('銅')
                            if copper_price is None:
                                st.error("無法取得銅價")
                            else:
                                # 使用用戶輸入的銅價百分比
                                user_percentage = copper_percentage  # 用戶輸入的百分比
                                calculated_price = copper_price * user_percentage / 100  # 直接計算每噸價格
                                
                                # 計算台幣價格 (每公斤)
                                twd_price = (calculated_price * usd_mid_rate) / 1000
                                
                                # 計算標準價格 (使用當前成分的標準價格)
                                composition_result, _ = calculate_composition_price(composition, metal_prices, usd_mid_rate)
                                if composition_result:
                                    standard_price = composition_result['美元價格/噸']
                                    # 計算對標準價格的百分比
                                    price_percentage = (calculated_price / standard_price) * 100
                                    
                                    # 回推計算：計算對應的複合成分百分比
                                    reverse_percentage = (calculated_price / standard_price) * 100
                                else:
                                    standard_price = 0
                                    price_percentage = 0
                                    reverse_percentage = 0
                                
                                st.markdown("---")
                                st.subheader("📊 係數計算結果")
                                
                                # 顯示計算結果
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric(
                                        "成分價格 (USD/噸)",
                                        f"${calculated_price:,.2f}"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "成分價格 (TWD/公斤)",
                                        f"NT${twd_price:,.2f}"
                                    )
                                
                                with col3:
                                    # 計算成分百分比
                                    composition_percentage = (calculated_price / standard_price) * 100
                                    st.metric(
                                        "成分百分比",
                                        f"{composition_percentage:.2f}%"
                                    )
                                
                                # 詳細結果
                                st.markdown("**詳細計算結果**")
                                composition_percentage = (calculated_price / standard_price) * 100
                                detail_df = pd.DataFrame([{
                                    "項目": "計算公式",
                                    "數值": f"LME銅價 × {user_percentage}%"
                                }, {
                                    "項目": "成分價格 (USD/噸)",
                                    "數值": f"${calculated_price:,.2f}"
                                }, {
                                    "項目": "成分價格 (TWD/公斤)",
                                    "數值": f"NT${twd_price:,.2f}"
                                }, {
                                    "項目": "成分百分比",
                                    "數值": f"{composition_percentage:.2f}%"
                                }, {
                                    "項目": "標準價格",
                                    "數值": f"${standard_price:,.2f}"
                                }, {
                                    "項目": "當前銅價",
                                    "數值": f"${copper_price:,.2f}"
                                }])
                                
                                st.dataframe(detail_df, use_container_width=True, hide_index=True)
                                
                                # 顯示計算說明
                                st.markdown("**計算說明**")
                                st.info(f"""
                                - **計算公式**: LME銅價 × {user_percentage}% = ${calculated_price:,.2f}/kg
                                - **標準價格**: 當前成分的標準價格 = ${standard_price:,.2f}/kg  
                                - **標準價格百分比**: 計算結果對標準價格的百分比 = {price_percentage:.2f}%
                                - **回推複合成分**: {composition} × {reverse_percentage:.2f}%
                                """)
    
    # 批量計算功能
    if composition and total_percentage == 100 and not df_lme.empty:
        metal_prices, price_error = get_metal_prices(df_lme)
        if not price_error:
            st.markdown("---")
            st.subheader("📊 批量計算")
            
            # 預設的批量計算組合
            batch_compositions = [
                {"銅": 65, "鋅": 35},  # C2680
                {"銅": 70, "鋅": 30},  # C2600
                {"銅": 94, "錫": 6},   # 磷青銅
                {"銅": 100, "鋅": 0}   # 紅銅
            ]
            
            if st.button("計算常見成分組合"):
                batch_results = []
                composition_names = ["C2680", "C2600", "磷青銅", "紅銅"]
                for i, comp in enumerate(batch_compositions):
                    batch_result, _ = calculate_composition_price(comp, metal_prices, usd_mid_rate)
                    if batch_result:
                        batch_results.append({
                            "成分": composition_names[i],
                            "銅含量": f"{comp.get('銅', 0)}%",
                            "鋅含量": f"{comp.get('鋅', 0)}%",
                            "錫含量": f"{comp.get('錫', 0)}%",
                            "美元價格/噸": f"${batch_result['美元價格/噸']:,.0f}",
                            "台幣價格/公斤": f"NT${batch_result['台幣價格/公斤']:,.2f}"
                        })
                
                if batch_results:
                    batch_df = pd.DataFrame(batch_results)
                    st.dataframe(batch_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
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