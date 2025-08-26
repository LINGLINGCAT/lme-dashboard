import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from pathlib import Path
from utils.auth import check_password, logout, is_admin
import numpy as np

# 檢查密碼認證
check_password()

# 檢查是否為管理員
if not is_admin():
    st.error("🔒 此頁面僅限管理員訪問")
    st.stop()

# 頁面配置
st.set_page_config(
    page_title="數據分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    """載入歷史數據 - 優先使用本地data目錄"""
    
    # 優先檢查本地data目錄（適用於雲端部署）
    local_data_paths = [
        Path("data/lme_updated_data.csv"),  # 優先載入包含完整資料的文件
        Path("data/lme_updated_data.xlsx"),
        Path("data/csp_history.csv"),
        Path("data/csp_history.xlsx"),
        Path("data/lme_historical_data.csv"),
        Path("data/lme_historical_data.xlsx"),
        Path("data/lme_prices.csv"),
        Path("data/historical_data.csv")
    ]
    
    for path in local_data_paths:
        if path.exists():
            try:
                if path.suffix == '.csv':
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)
                
                if not df.empty:
                    st.success(f"✅ 已載入本地數據：{path}")
                    st.info(f"📊 數據統計：{len(df)} 行，{len(df.columns)} 欄位")
                    return df
            except Exception as e:
                st.warning(f"⚠️ 載入 {path} 失敗：{e}")
    
    # 如果本地沒有數據，提供上傳功能
    st.warning("⚠️ 本地沒有歷史數據文件")
    
    # 數據上傳功能
    st.subheader("📤 上傳歷史數據")
    st.info("💡 提示：您可以運行 `python import_historical_data.py` 來導入 LME.xlsm 文件中的歷史數據")
    
    uploaded_file = st.file_uploader(
        "選擇CSV或Excel文件",
        type=['csv', 'xlsx', 'xls'],
        help="請上傳包含LME價格數據的文件"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if not df.empty:
                st.success(f"✅ 成功上傳數據：{uploaded_file.name}")
                st.write(f"📊 數據行數：{len(df)}")
                st.write(f"📋 欄位：{list(df.columns)}")
                
                # 保存到本地
                save_path = Path("data") / f"uploaded_{uploaded_file.name}"
                Path("data").mkdir(exist_ok=True)
                
                if uploaded_file.name.endswith('.csv'):
                    df.to_csv(save_path, index=False)
                else:
                    df.to_excel(save_path, index=False)
                
                st.success(f"💾 數據已保存到：{save_path}")
                return df
                
        except Exception as e:
            st.error(f"❌ 上傳失敗：{e}")
    
    # 如果都沒有數據，使用示例數據
    st.info("📋 使用示例數據進行演示")
    return create_sample_data()

def create_sample_data():
    """創建示例數據"""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # 模擬LME價格數據
    np.random.seed(42)
    base_prices = {
        'CSP磷': 2500,
        'CSP青': 2800,
        'CSP紅': 3200,
        '銅': 8500,
        '鋁': 2200
    }
    
    data = []
    for date in dates:
        for product, base_price in base_prices.items():
            # 添加隨機波動
            price = base_price + np.random.normal(0, base_price * 0.02)
            price = max(price, base_price * 0.8)  # 確保價格不會太低
            
            data.append({
                '日期': date,
                '品項': product,
                '價格': round(price, 2),
                '幣值': 'USD'
            })
    
    df = pd.DataFrame(data)
    return df

def create_price_trend_chart(df, price_columns):
    """創建價格趨勢圖"""
    if df.empty:
        return None
    
    fig = go.Figure()
    
    # 檢查是否為長格式數據
    if '品項' in df.columns and '價格' in df.columns:
        # 長格式數據處理
        for product in price_columns:
            product_data = df[df['品項'] == product].copy()
            if not product_data.empty:
                # 清理價格數據
                price_data = product_data['價格'].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                
                fig.add_trace(go.Scatter(
                    x=product_data['日期'],
                    y=numeric_values,
                    mode='lines+markers',
                    name=product,
                    line=dict(width=2)
                ))
    else:
        # 寬格式數據處理（原有邏輯）
        for col in price_columns:
            if col in df.columns:
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
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
    
    # 檢查是否為長格式數據
    if '品項' in df.columns and '價格' in df.columns:
        # 長格式數據處理
        for product in price_columns:
            product_data = df[df['品項'] == product].copy()
            if not product_data.empty:
                # 清理價格數據
                price_data = product_data['價格'].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                
                # 計算波動性指標
                if len(numeric_values.dropna()) > 1:
                    volatility = numeric_values.pct_change().std() * 100
                    max_price = numeric_values.max()
                    min_price = numeric_values.min()
                    avg_price = numeric_values.mean()
                    
                    volatility_data.append({
                        '產品': product,
                        '平均價格': avg_price,
                        '最高價格': max_price,
                        '最低價格': min_price,
                        '波動率 (%)': volatility
                    })
    else:
        # 寬格式數據處理（原有邏輯）
        for col in price_columns:
            if col in df.columns:
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
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
    
    # 檢查是否為長格式數據
    if '品項' in df.columns and '價格' in df.columns:
        # 長格式數據處理：轉換為寬格式
        correlation_data = {}
        
        for product in price_columns:
            product_data = df[df['品項'] == product].copy()
            if not product_data.empty:
                # 清理價格數據
                price_data = product_data['價格'].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                
                # 按日期排序並設置索引
                product_data_sorted = product_data.sort_values('日期')
                product_data_sorted['clean_price'] = numeric_values
                correlation_data[product] = product_data_sorted.set_index('日期')['clean_price']
        
        if len(correlation_data) < 2:
            return None
        
        # 創建寬格式DataFrame並計算相關性
        correlation_df = pd.DataFrame(correlation_data)
        correlation_matrix = correlation_df.corr()
        
        return correlation_matrix
    else:
        # 寬格式數據處理（原有邏輯）
        correlation_data = {}
        
        for col in price_columns:
            if col in df.columns:
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
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
    
    # 處理數據格式
    if not df.empty and '日期' in df.columns:
        # 確保日期欄位被正確解析 - 支援多種日期格式
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        
        # 清理價格數據中的貨幣符號（僅對寬格式數據）
        if '品項' not in df.columns:  # 寬格式數據
            price_columns = [col for col in df.columns if col != '日期']
            for col in price_columns:
                if col in df.columns:
                    # 轉換為字符串
                    df[col] = df[col].astype(str)
                    # 清理貨幣符號和格式
                    df[col] = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                    # 轉換為數值
                    df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 如果數據為空，提供手動輸入路徑的選項
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
            if pd.notna(min_date) and pd.notna(max_date) and hasattr(min_date, 'strftime'):
                date_range = f"{min_date.strftime('%Y-%m-%d')} 至 {max_date.strftime('%Y-%m-%d')}"
            else:
                date_range = "日期格式錯誤"
        except Exception as e:
            date_range = f"日期格式錯誤: {str(e)[:20]}"
        st.metric("時間範圍", date_range)
    
    with col3:
        # 檢測數據格式並識別價格欄位
        if '品項' in df.columns and '價格' in df.columns:
            # 長格式數據：每個產品一行
            unique_products = df['品項'].unique()
            # 確保所有產品名稱都是字符串
            price_columns = [str(product) for product in unique_products if pd.notna(product)]
            st.metric("價格指標", len(price_columns))
            st.info(f"📊 檢測到長格式數據，產品：{', '.join(price_columns)}")
        else:
            # 寬格式數據：每個產品一欄
            price_columns = []
            for col in df.columns:
                if col != '日期' and any(keyword in col.upper() for keyword in ['CSP', 'PRICE', '價格', '銅', '錫', '鋅', '磷', '青', '紅', 'FX_', 'USD', 'TWD', '匯率', '中間匯率']):
                    price_columns.append(col)
            st.metric("價格指標", len(price_columns))
            if price_columns:
                st.info(f"📊 檢測到寬格式數據，產品：{', '.join(price_columns)}")
    
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
            
            # 檢查是否為長格式數據
            if '品項' in df.columns and '價格' in df.columns:
                # 長格式數據處理
                for product in selected_prices:
                    product_data = df[df['品項'] == product].copy()
                    if not product_data.empty:
                        # 清理價格數據
                        price_data = product_data['價格'].astype(str)
                        clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                        numeric_values = pd.to_numeric(clean_values, errors='coerce')
                        
                        if len(numeric_values.dropna()) > 0:
                            summary_data.append({
                                '指標': product,
                                '最新價格': numeric_values.iloc[-1],
                                '平均價格': numeric_values.mean(),
                                '最高價格': numeric_values.max(),
                                '最低價格': numeric_values.min(),
                                '標準差': numeric_values.std()
                            })
            else:
                # 寬格式數據處理（原有邏輯）
                for col in selected_prices:
                    if col in df.columns:
                        price_data = df[col].astype(str)
                        clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
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
            # 相關性熱力圖 - 修正顏色映射以正確顯示負相關
            fig_corr = px.imshow(
                correlation_matrix,
                title="價格相關性矩陣",
                color_continuous_scale='RdBu_r',  # 使用紅藍色階，正確顯示負相關
                aspect='auto',
                zmin=-1,  # 確保負值正確顯示
                zmax=1    # 確保正值正確顯示
            )
            
            # 更新顏色條和懸停信息
            fig_corr.update_traces(
                hovertemplate="%{x} vs %{y}<br>相關性: %{z:.3f}<extra></extra>"
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # 相關性表格
            st.markdown("**相關性係數表**")
            st.dataframe(correlation_matrix.round(3), use_container_width=True)
            
            # 相關性解釋
            st.markdown("**相關性解釋**")
            st.markdown("""
            - **1.0**: 完全正相關（兩個指標同步上升）
            - **0.7-1.0**: 強正相關
            - **0.3-0.7**: 中等正相關
            - **0.0-0.3**: 弱相關
            - **0.0**: 無相關
            - **-0.3-0.0**: 弱負相關
            - **-0.7--0.3**: 中等負相關
            - **-1.0--0.7**: 強負相關
            - **-1.0**: 完全負相關（一個上升時另一個下降）
            """)
            
            # 特別說明負相關的意義
            st.info("💡 **負相關說明**：當相關性為負值時，表示兩個指標呈反向關係。例如，磷價格與中間匯率的相關性為 -0.211，表示當磷價格上升時，中間匯率傾向於下降。")
    
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