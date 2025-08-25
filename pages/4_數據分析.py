import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from pathlib import Path
from utils.auth import check_password, logout, is_admin

# 檢查密碼認證
check_password()

# 檢查是否為管理員
if not is_admin():
    st.error("🔒 此頁面僅限管理員訪問")
    st.stop()

# --- 頁面設定 ---
st.set_page_config(page_title="數據分析", page_icon="📊", layout="wide")

# --- 數據目錄 ---
DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "csp_history.csv"
# 使用真實LME數據 - 嘗試多種可能的路徑
REAL_DATA_PATHS = [
    Path("Z:/LME.xlsm"),  # 主要數據源 - 直接在Z:根目錄
    Path("Z:/LME/LME.xlsm"),  # 備用路徑
    Path("Z:/LME/LME.xlsx"),  # 備用路徑
    Path("Z:/LME/LME.xls"),   # 備用路徑
    Path("Z:/LME/LME_prices.csv"),  # 備用數據
    Path("Z:/LME/Westmetall_LME_prices.csv"),  # 備用數據
    Path("Z:/LME/FX_rates.csv"),  # 備用數據
    Path("Z:/LME/USD_Spot_Rates.csv"),  # 備用數據
    Path("Z:/LME/分頁3M RECORD.csv"),
    Path("Z:/LME/3M RECORD.csv"),
    Path("Z:/LME/3M.csv"),
    Path("Z:/LME/價格.csv")
]

def load_historical_data():
    """載入歷史數據"""
    # 優先嘗試載入主要數據源 Z:/LME.xlsm
    main_data_path = Path("Z:/LME.xlsm")
    
    if main_data_path.exists():
        try:
            # 載入Excel文件，指定工作表名稱
            df = pd.read_excel(main_data_path, sheet_name="3M RECORD")
            st.success(f"✅ 已載入主要數據源：{main_data_path} (工作表: 3M RECORD)")
            
            # 確保日期欄位被正確解析為datetime
            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
            
            return df
            
        except Exception as e:
            st.warning(f"⚠️ 載入主要數據源失敗：{e}")
            st.info("💡 嘗試載入備用數據源...")
    
    # 如果主要數據源失敗，嘗試其他路徑
    for data_path in REAL_DATA_PATHS[1:]:  # 跳過第一個（主要數據源）
        if data_path.exists():
            try:
                # 根據文件擴展名選擇載入方法
                if data_path.suffix.lower() in ['.xls', '.xlsx', '.xlsm']:
                    # 載入Excel文件，指定工作表名稱
                    df = pd.read_excel(data_path, sheet_name="3M RECORD")
                    st.success(f"✅ 已載入備用Excel數據：{data_path} (工作表: 3M RECORD)")
                else:
                    # 載入CSV文件
                    df = pd.read_csv(data_path)
                    st.success(f"✅ 已載入備用CSV數據：{data_path}")
                
                # 確保日期欄位被正確解析為datetime
                if '日期' in df.columns:
                    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                
                return df
                    
            except Exception as e:
                st.warning(f"⚠️ 載入 {data_path} 失敗：{e}")
                continue
    
    # 如果所有真實數據路徑都失敗，顯示路徑檢查
    st.error("❌ 無法找到真實LME數據文件")
    st.info("🔍 正在檢查以下路徑：")
    for path in REAL_DATA_PATHS:
        if path.exists():
            st.success(f"✅ 找到文件：{path}")
        else:
            st.error(f"❌ 文件不存在：{path}")
    
    # 嘗試列出Z:/LME目錄下的所有文件
    try:
        lme_dir = Path("Z:/LME")
        if lme_dir.exists():
            st.info("📁 Z:/LME 目錄內容：")
            files = list(lme_dir.glob("*"))
            if files:
                # 分類顯示文件
                csv_files = [f for f in files if f.is_file() and f.suffix.lower() == '.csv']
                excel_files = [f for f in files if f.is_file() and f.suffix.lower() in ['.xls', '.xlsx', '.xlsm']]
                other_files = [f for f in files if f.is_file() and f.suffix.lower() not in ['.csv', '.xls', '.xlsx', '.xlsm']]
                dirs = [f for f in files if f.is_dir()]
                
                if csv_files:
                    st.write("📊 **CSV數據文件：**")
                    for file in csv_files:
                        st.write(f"  📄 {file.name}")
                
                if excel_files:
                    st.write("📈 **Excel文件：**")
                    for file in excel_files:
                        st.write(f"  📄 {file.name}")
                
                if other_files:
                    st.write("📄 **其他文件：**")
                    for file in other_files:
                        st.write(f"  📄 {file.name}")
                
                if dirs:
                    st.write("📁 **目錄：**")
                    for dir in dirs:
                        st.write(f"  📁 {dir.name}/")
            else:
                st.warning("Z:/LME 目錄為空")
        else:
            st.error("❌ Z:/LME 目錄不存在")
    except Exception as e:
        st.error(f"❌ 無法訪問 Z:/LME 目錄：{e}")
    
    # 使用示例數據作為備用
    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
        st.info("ℹ️ 使用示例數據進行演示")
        # 確保日期欄位被正確解析為datetime
        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        return df
    
    return pd.DataFrame()

def create_price_trend_chart(df, price_columns):
    """創建價格趨勢圖"""
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for col in price_columns:
        if col in df.columns:
            # 確保價格數據是字符串格式，然後清理
            price_data = df[col].astype(str)
            # 清理各種貨幣符號和格式
            clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.replace(' ', '')
            numeric_values = pd.to_numeric(clean_values, errors='coerce')
            
            fig.add_trace(go.Scatter(
                x=df['日期'],
                y=numeric_values,
                mode='lines+markers',
                name=col,
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title="CSP 價格歷史趨勢",
        xaxis_title="日期",
        yaxis_title="價格",
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_volatility_analysis(df, price_columns):
    """創建波動性分析"""
    if df.empty:
        return None
    
    volatility_data = []
    
    for col in price_columns:
        if col in df.columns:
            # 確保價格數據是字符串格式，然後清理
            price_data = df[col].astype(str)
            # 清理各種貨幣符號和格式
            clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.replace(' ', '')
            numeric_values = pd.to_numeric(clean_values, errors='coerce')
            
            # 計算波動性指標
            if len(numeric_values.dropna()) > 1:
                volatility = numeric_values.pct_change().std() * 100
                max_price = numeric_values.max()
                min_price = numeric_values.min()
                avg_price = numeric_values.mean()
                
                volatility_data.append({
                    '產品': col,
                    '平均價格': avg_price,
                    '最高價格': max_price,
                    '最低價格': min_price,
                    '波動率 (%)': volatility
                })
    
    return pd.DataFrame(volatility_data)

def create_correlation_matrix(df, price_columns):
    """創建相關性矩陣"""
    if df.empty:
        return None
    
    # 準備數據
    correlation_data = {}
    
    for col in price_columns:
        if col in df.columns:
            # 確保價格數據是字符串格式，然後清理
            price_data = df[col].astype(str)
            # 清理各種貨幣符號和格式
            clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.replace(' ', '')
            numeric_values = pd.to_numeric(clean_values, errors='coerce')
            correlation_data[col] = numeric_values
    
    if len(correlation_data) < 2:
        return None
    
    correlation_df = pd.DataFrame(correlation_data)
    correlation_matrix = correlation_df.corr()
    
    return correlation_matrix

def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st.title("📊 數據分析")
    st.subheader("歷史數據視覺化與趨勢分析")
    st.markdown("---")
    
    # 載入歷史數據
    df = load_historical_data()
    
    # 如果自動載入失敗，提供手動輸入路徑的選項
    if df.empty:
        st.warning("⚠️ 沒有找到歷史數據。")
        
        # 手動輸入路徑
        with st.expander("🔧 手動指定數據文件路徑"):
            col1, col2 = st.columns(2)
            
            with col1:
                manual_path = st.text_input(
                    "請輸入您的LME數據文件完整路徑：",
                    value="Z:/LME.xlsm",
                    help="例如：Z:/LME.xlsm 或 Z:/LME/LME.xlsm"
                )
            
            with col2:
                # 提供常見路徑選項
                st.write("**常見路徑選項：**")
                common_paths = [
                    "Z:/LME.xlsm",
                    "Z:/LME/LME.xlsm",
                    "Z:/LME/LME.xlsx",
                    "Z:/LME/LME_prices.csv",
                    "Z:/LME/Westmetall_LME_prices.csv"
                ]
                for path in common_paths:
                    if st.button(f"📂 {path}", key=f"path_{path}"):
                        manual_path = path
            
            if st.button("📂 載入指定文件", type="primary"):
                if manual_path:
                    try:
                        # 根據文件擴展名選擇載入方法
                        if manual_path.lower().endswith(('.xls', '.xlsx', '.xlsm')):
                            # 載入Excel文件，指定工作表名稱
                            df = pd.read_excel(manual_path, sheet_name="3M RECORD")
                            st.success(f"✅ 成功載入Excel：{manual_path} (工作表: 3M RECORD)")
                        else:
                            # 載入CSV文件
                            df = pd.read_csv(manual_path)
                            st.success(f"✅ 成功載入CSV：{manual_path}")
                        
                        # 確保日期欄位被正確解析為datetime
                        if '日期' in df.columns:
                            df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                    except Exception as e:
                        st.error(f"❌ 載入失敗：{e}")
                        st.info("💡 請檢查文件路徑是否正確，或嘗試其他路徑")
                        return
                else:
                    st.error("請輸入文件路徑")
                    return
        return
    
    # 顯示數據預覽
    with st.expander("📋 數據預覽"):
        st.write("**數據形狀：**", df.shape)
        st.write("**欄位名稱：**", list(df.columns))
        
        # 顯示數據來源說明
        st.info("📊 **數據來源說明：**")
        if any('FX_' in col for col in df.columns):
            st.write("• **FX_開頭的欄位**：來自匯率數據文件（當天最新）")
        if any('CSP' in col for col in df.columns):
            st.write("• **CSP欄位**：來自LME價格數據")
        if any(col in ['USD', 'TWD'] for col in df.columns):
            st.write("• **USD/TWD欄位**：來自匯率數據")
        
        st.dataframe(df.head(10), use_container_width=True)
    
    # 數據概覽
    st.subheader("📈 數據概覽")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("數據點數", len(df))
    
    with col2:
        try:
            min_date = df['日期'].min()
            max_date = df['日期'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                date_range = f"{min_date.strftime('%Y-%m-%d')} 至 {max_date.strftime('%Y-%m-%d')}"
            else:
                date_range = "日期格式錯誤"
        except:
            date_range = "日期格式錯誤"
        st.metric("時間範圍", date_range)
    
    with col3:
        # 更靈活的價格欄位檢測
        price_columns = []
        for col in df.columns:
            if any(keyword in col.upper() for keyword in ['CSP', 'PRICE', '價格', '銅', '錫', '鋅', '磷', '青', '紅', 'FX_', 'USD', 'TWD', '匯率']):
                price_columns.append(col)
        st.metric("價格指標", len(price_columns))
    
    st.markdown("---")
    
    # 價格趨勢圖
    st.subheader("📈 價格趨勢分析")
    
    if not price_columns:
        st.warning("沒有找到價格數據列")
    else:
        # 選擇要顯示的價格指標
        selected_prices = st.multiselect(
            "選擇要分析的價格指標",
            price_columns,
            default=price_columns[:3] if len(price_columns) >= 3 else price_columns
        )
        
        if selected_prices:
            fig = create_price_trend_chart(df, selected_prices)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # 統計摘要
            st.markdown("**統計摘要**")
            summary_data = []
            
            for col in selected_prices:
                # 確保價格數據是字符串格式，然後清理
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace(',', '')
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                
                if len(numeric_values.dropna()) > 0:
                    summary_data.append({
                        '指標': col,
                        '最新價格': numeric_values.iloc[-1],
                        '平均價格': numeric_values.mean(),
                        '最高價格': numeric_values.max(),
                        '最低價格': numeric_values.min(),
                        '標準差': numeric_values.std()
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 波動性分析
    st.subheader("📊 波動性分析")
    
    volatility_df = pd.DataFrame()  # 初始化為空DataFrame
    
    if price_columns:
        volatility_df = create_volatility_analysis(df, price_columns)
        
        if not volatility_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # 波動率柱狀圖
                fig_vol = px.bar(
                    volatility_df,
                    x='產品',
                    y='波動率 (%)',
                    title="各產品波動率比較",
                    color='波動率 (%)',
                    color_continuous_scale='RdYlBu_r'
                )
                st.plotly_chart(fig_vol, use_container_width=True)
            
            with col2:
                # 價格範圍圖
                fig_range = px.scatter(
                    volatility_df,
                    x='平均價格',
                    y='波動率 (%)',
                    size='最高價格',
                    color='產品',
                    title="價格與波動率關係",
                    hover_data=['最高價格', '最低價格']
                )
                st.plotly_chart(fig_range, use_container_width=True)
            
            # 詳細波動性表格
            st.markdown("**詳細波動性數據**")
            st.dataframe(volatility_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # 相關性分析
    st.subheader("🔗 相關性分析")
    
    if len(price_columns) >= 2:
        correlation_matrix = create_correlation_matrix(df, price_columns)
        
        if correlation_matrix is not None:
            # 相關性熱力圖
            fig_corr = px.imshow(
                correlation_matrix,
                title="價格相關性矩陣",
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # 相關性表格
            st.markdown("**相關性係數表**")
            st.dataframe(correlation_matrix.round(3), use_container_width=True)
            
            # 相關性解釋
            st.markdown("**相關性解釋**")
            st.markdown("""
            - **1.0**: 完全正相關
            - **0.7-1.0**: 強正相關
            - **0.3-0.7**: 中等正相關
            - **0.0-0.3**: 弱相關
            - **0.0**: 無相關
            - **負值**: 負相關（一個上升時另一個下降）
            """)
    
    st.markdown("---")
    
    # 數據下載
    st.subheader("💾 數據下載")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not df.empty:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載完整歷史數據 (CSV)",
                data=csv,
                file_name=f"lme_dashboard_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if not volatility_df.empty:
            volatility_csv = volatility_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載波動性分析 (CSV)",
                data=volatility_csv,
                file_name=f"volatility_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # 使用說明
    st.markdown("---")
    st.subheader("📖 使用說明")
    
    with st.expander("如何解讀這些圖表？"):
        st.markdown("""
        **價格趨勢圖**：
        - 顯示各產品價格隨時間的變化
        - 可以觀察價格的季節性、週期性模式
        - 幫助識別價格的長期趨勢
        
        **波動性分析**：
        - 波動率越高，價格變化越劇烈
        - 高波動率產品風險較大，但也可能有更高收益機會
        - 平均價格與波動率的關係可以幫助風險評估
        
        **相關性分析**：
        - 正相關：兩個產品價格同向變動
        - 負相關：兩個產品價格反向變動
        - 無相關：兩個產品價格變動獨立
        - 高相關性產品可以考慮分散投資
        """)
    
    with st.expander("數據更新頻率"):
        st.markdown("""
        - **即時數據**：每5秒自動更新
        - **歷史數據**：每天自動收集並儲存
        - **分析圖表**：基於歷史數據即時生成
        - **數據來源**：LME市場、台銀匯率等公開數據
        """)
    
    with st.expander("支援的數據文件類型"):
        st.markdown("""
         **📈 主要數據源：**
         - `Z:/LME.xlsm`：主要LME數據文件（工作表：3M RECORD）
        
        **📊 備用數據文件：**
        - `Z:/LME/LME.xlsm`：備用Excel文件
        - `Z:/LME/LME_prices.csv`：LME市場價格歷史數據
        - `Z:/LME/Westmetall_LME_prices.csv`：Westmetall LME價格數據
        
        **💱 匯率數據文件（當天最新）：**
        - `Z:/LME/FX_rates.csv`：外匯匯率數據
        - `Z:/LME/USD_Spot_Rates.csv`：美元即期匯率
        
        **🔄 載入優先順序：**
        1. 優先載入 `Z:/LME.xlsm`（主要數據源）
        2. 如果失敗，嘗試其他備用路徑
        3. 最後使用示例數據進行演示
        """)

if __name__ == "__main__":
    main() 