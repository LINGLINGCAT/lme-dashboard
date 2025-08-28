import streamlit as st是要
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

# --- 數據來源配置 ---
# 支援多種數據來源路徑
DATA_PATHS = [
    Path("Z:/DATA.xlsx"),           # 雲端/網路磁碟機
    Path("data/DATA.xlsx"),         # 本地備份
    Path("DATA.xlsx"),              # 當前目錄
    Path("Z:/LME/DATA.xlsx"),       # 備用雲端路徑
]

def load_cloud_data():
    """從多個來源載入數據"""
    
    # 嘗試多個數據來源路徑
    for data_path in DATA_PATHS:
        try:
            if data_path.exists():
                st.success(f"✅ 找到數據文件：{data_path}")
                
                # 載入兩個分頁的數據
                try:
                    # 載入 3M 分頁（每天即時價）
                    df_3m = pd.read_excel(data_path, sheet_name="3M")
                    st.success(f"✅ 成功載入 3M 數據：{len(df_3m)} 行")
                except Exception as e:
                    st.warning(f"⚠️ 載入 3M 分頁失敗：{e}")
                    df_3m = None
                
                try:
                    # 載入 CSP 分頁（前日收盤）
                    df_csp = pd.read_excel(data_path, sheet_name="CSP")
                    st.success(f"✅ 成功載入 CSP 數據：{len(df_csp)} 行")
                except Exception as e:
                    st.warning(f"⚠️ 載入 CSP 分頁失敗：{e}")
                    df_csp = None
                
                if df_3m is None and df_csp is None:
                    st.error("❌ 無法載入任何數據分頁")
                    continue
                
                return df_3m, df_csp
                
        except Exception as e:
            st.warning(f"⚠️ 嘗試路徑 {data_path} 失敗：{e}")
            continue
    
    # 如果所有路徑都失敗
    st.error("❌ 無法找到或載入任何數據文件")
    st.info("💡 請確認以下路徑之一存在且可訪問：")
    for path in DATA_PATHS:
        st.write(f"   - {path}")
    return None, None

def process_data(df, data_type):
    """處理數據格式"""
    if df is None or df.empty:
        return df
    
    # 確保日期欄位被正確解析
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if date_columns:
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 清理價格數據中的貨幣符號
    price_columns = [col for col in df.columns if col not in date_columns]
    for col in price_columns:
        if col in df.columns:
            # 轉換為字符串
            df[col] = df[col].astype(str)
            # 清理貨幣符號和格式
            df[col] = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
            # 轉換為數值
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def create_price_trend_chart(df, title="價格趨勢"):
    """創建價格趨勢圖"""
    if df is None or df.empty:
        return None
    
    # 找到日期欄位
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if not date_columns:
        st.warning("⚠️ 找不到日期欄位")
        return None
    
    date_col = date_columns[0]
    price_columns = [col for col in df.columns if col != date_col]
    
    fig = go.Figure()
    
    for col in price_columns:
        if col in df.columns:
            # 清理價格數據
            price_data = df[col].astype(str)
            clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
            numeric_values = pd.to_numeric(clean_values, errors='coerce')
            
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=numeric_values,
                mode='lines+markers',
                name=col,
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="價格",
        hovermode='x unified',
        height=500
    )
    
    return fig

def create_volatility_analysis(df, data_type):
    """創建波動性分析"""
    if df is None or df.empty:
        return None
    
    # 找到日期欄位
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if not date_columns:
        return None
    
    date_col = date_columns[0]
    price_columns = [col for col in df.columns if col != date_col]
    
    volatility_data = []
    
    for col in price_columns:
        if col in df.columns:
            # 清理價格數據
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

def create_correlation_matrix(df):
    """創建相關性矩陣"""
    if df is None or df.empty:
        return None
    
    # 找到日期欄位
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if not date_columns:
        return None
    
    date_col = date_columns[0]
    price_columns = [col for col in df.columns if col != date_col]
    
    if len(price_columns) < 2:
        return None
    
    correlation_data = {}
    
    for col in price_columns:
        if col in df.columns:
            # 清理價格數據
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
    st.subheader("多來源數據視覺化與趨勢分析")
    st.markdown("---")
    
    # 顯示數據來源
    st.info("📁 **數據來源：** 支援多個路徑，自動選擇可用的數據文件")
    st.info("📊 **數據分頁：** 3M（每天即時價）、CSP（前日收盤）")
    
    # 載入雲端數據
    df_3m, df_csp = load_cloud_data()
    
    if df_3m is None and df_csp is None:
        st.error("❌ 無法載入任何數據，請檢查雲端文件路徑")
        return
    
    # 處理數據格式
    df_3m = process_data(df_3m, "3M")
    df_csp = process_data(df_csp, "CSP")
    
    # 數據概覽
    st.subheader("📈 數據概覽")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_rows = (len(df_3m) if df_3m is not None else 0) + (len(df_csp) if df_csp is not None else 0)
        st.metric("總數據點數", total_rows)
    
    with col2:
        if df_3m is not None and not df_3m.empty:
            date_columns_3m = [col for col in df_3m.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
            if date_columns_3m:
                min_date_3m = df_3m[date_columns_3m[0]].min()
                max_date_3m = df_3m[date_columns_3m[0]].max()
                date_range_3m = f"{min_date_3m.strftime('%Y-%m-%d')} 至 {max_date_3m.strftime('%Y-%m-%d')}"
            else:
                date_range_3m = "無日期欄位"
        else:
            date_range_3m = "無數據"
        st.metric("3M 時間範圍", date_range_3m)
    
    with col3:
        if df_csp is not None and not df_csp.empty:
            date_columns_csp = [col for col in df_csp.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
            if date_columns_csp:
                min_date_csp = df_csp[date_columns_csp[0]].min()
                max_date_csp = df_csp[date_columns_csp[0]].max()
                date_range_csp = f"{min_date_csp.strftime('%Y-%m-%d')} 至 {max_date_csp.strftime('%Y-%m-%d')}"
            else:
                date_range_csp = "無日期欄位"
        else:
            date_range_csp = "無數據"
        st.metric("CSP 時間範圍", date_range_csp)
    
    st.markdown("---")
    
    # 數據預覽
    with st.expander("📋 數據預覽"):
        col1, col2 = st.columns(2)
        
        with col1:
            if df_3m is not None and not df_3m.empty:
                st.write("**3M 數據預覽：**")
                st.write(f"形狀：{df_3m.shape}")
                st.write(f"欄位：{list(df_3m.columns)}")
                st.dataframe(df_3m.head(5), use_container_width=True)
            else:
                st.write("**3M 數據：** 無數據")
        
        with col2:
            if df_csp is not None and not df_csp.empty:
                st.write("**CSP 數據預覽：**")
                st.write(f"形狀：{df_csp.shape}")
                st.write(f"欄位：{list(df_csp.columns)}")
                st.dataframe(df_csp.head(5), use_container_width=True)
            else:
                st.write("**CSP 數據：** 無數據")
    
    st.markdown("---")
    
    # 3M 數據分析
    if df_3m is not None and not df_3m.empty:
        st.subheader("📈 3M 數據分析（每天即時價）")
        
        # 價格趨勢圖
        fig_3m = create_price_trend_chart(df_3m, "3M 價格趨勢（每天即時價）")
        if fig_3m:
            st.plotly_chart(fig_3m, use_container_width=True)
        
        # 波動性分析
        volatility_3m = create_volatility_analysis(df_3m, "3M")
        if volatility_3m is not None and not volatility_3m.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vol_3m = px.bar(
                    volatility_3m,
                    x='產品',
                    y='波動率 (%)',
                    title="3M 各產品波動率比較",
                    color='波動率 (%)',
                    color_continuous_scale='RdYlBu_r'
                )
                st.plotly_chart(fig_vol_3m, use_container_width=True)
            
            with col2:
                fig_range_3m = px.scatter(
                    volatility_3m,
                    x='平均價格',
                    y='波動率 (%)',
                    size='最高價格',
                    color='產品',
                    title="3M 價格與波動率關係",
                    hover_data=['最高價格', '最低價格']
                )
                st.plotly_chart(fig_range_3m, use_container_width=True)
            
            st.markdown("**3M 詳細波動性數據**")
            st.dataframe(volatility_3m, use_container_width=True, hide_index=True)
        
        # 相關性分析
        correlation_3m = create_correlation_matrix(df_3m)
        if correlation_3m is not None:
            st.markdown("**3M 相關性分析**")
            fig_corr_3m = px.imshow(
                correlation_3m,
                title="3M 價格相關性矩陣",
                color_continuous_scale='RdBu_r',
                aspect='auto',
                zmin=-1,
                zmax=1
            )
            fig_corr_3m.update_traces(
                hovertemplate="%{x} vs %{y}<br>相關性: %{z:.3f}<extra></extra>"
            )
            st.plotly_chart(fig_corr_3m, use_container_width=True)
            st.dataframe(correlation_3m.round(3), use_container_width=True)
    
    st.markdown("---")
    
    # CSP 數據分析
    if df_csp is not None and not df_csp.empty:
        st.subheader("📊 CSP 數據分析（前日收盤）")
        
        # 價格趨勢圖
        fig_csp = create_price_trend_chart(df_csp, "CSP 價格趨勢（前日收盤）")
        if fig_csp:
            st.plotly_chart(fig_csp, use_container_width=True)
        
        # 波動性分析
        volatility_csp = create_volatility_analysis(df_csp, "CSP")
        if volatility_csp is not None and not volatility_csp.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vol_csp = px.bar(
                    volatility_csp,
                    x='產品',
                    y='波動率 (%)',
                    title="CSP 各產品波動率比較",
                    color='波動率 (%)',
                    color_continuous_scale='RdYlBu_r'
                )
                st.plotly_chart(fig_vol_csp, use_container_width=True)
            
            with col2:
                fig_range_csp = px.scatter(
                    volatility_csp,
                    x='平均價格',
                    y='波動率 (%)',
                    size='最高價格',
                    color='產品',
                    title="CSP 價格與波動率關係",
                    hover_data=['最高價格', '最低價格']
                )
                st.plotly_chart(fig_range_csp, use_container_width=True)
            
            st.markdown("**CSP 詳細波動性數據**")
            st.dataframe(volatility_csp, use_container_width=True, hide_index=True)
        
        # 相關性分析
        correlation_csp = create_correlation_matrix(df_csp)
        if correlation_csp is not None:
            st.markdown("**CSP 相關性分析**")
            fig_corr_csp = px.imshow(
                correlation_csp,
                title="CSP 價格相關性矩陣",
                color_continuous_scale='RdBu_r',
                aspect='auto',
                zmin=-1,
                zmax=1
            )
            fig_corr_csp.update_traces(
                hovertemplate="%{x} vs %{y}<br>相關性: %{z:.3f}<extra></extra>"
            )
            st.plotly_chart(fig_corr_csp, use_container_width=True)
            st.dataframe(correlation_csp.round(3), use_container_width=True)
    
    st.markdown("---")
    
    # 數據下載
    st.subheader("💾 數據下載")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if df_3m is not None and not df_3m.empty:
            csv_3m = df_3m.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載 3M 數據 (CSV)",
                data=csv_3m,
                file_name=f"3m_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if df_csp is not None and not df_csp.empty:
            csv_csp = df_csp.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載 CSP 數據 (CSV)",
                data=csv_csp,
                file_name=f"csp_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # 使用說明
    st.markdown("---")
    st.subheader("📖 使用說明")
    
    with st.expander("數據來源說明"):
        st.markdown("""
        **📁 雲端數據文件：** `Z:\DATA.xlsx`
        
        **📊 數據分頁：**
        - **3M 分頁**：包含每天的即時價格數據
        - **CSP 分頁**：包含前日收盤價格數據
        
        **🔄 數據更新：**
        - 數據由 Streamlit 應用程式自動從雲端抓取
        - 每次重新整理頁面時會重新載入最新數據
        - 確保數據的即時性和準確性
        """)
    
    with st.expander("如何解讀圖表？"):
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

if __name__ == "__main__":
    main() 