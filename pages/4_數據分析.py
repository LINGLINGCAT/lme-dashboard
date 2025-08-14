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

def load_historical_data():
    """載入歷史數據"""
    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE, parse_dates=["日期"])
        return df
    return pd.DataFrame()

def create_price_trend_chart(df, price_columns):
    """創建價格趨勢圖"""
    if df.empty:
        return None
    
    fig = go.Figure()
    
    for col in price_columns:
        if col in df.columns:
            # 清理價格數據（移除 NT$ 和 US$ 符號）
            clean_values = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace(',', '')
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
            # 清理價格數據
            clean_values = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace(',', '')
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
            clean_values = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace(',', '')
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
    
    if df.empty:
        st.warning("⚠️ 沒有找到歷史數據。請先在前日收盤頁面生成一些數據。")
        st.info("💡 提示：您可以在前日收盤頁面查看歷史數據，或等待系統自動收集數據。")
        return
    
    # 數據概覽
    st.subheader("📈 數據概覽")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("數據點數", len(df))
    
    with col2:
        date_range = f"{df['日期'].min().strftime('%Y-%m-%d')} 至 {df['日期'].max().strftime('%Y-%m-%d')}"
        st.metric("時間範圍", date_range)
    
    with col3:
        price_columns = [col for col in df.columns if col.startswith('CSP')]
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
                clean_values = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace(',', '')
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

if __name__ == "__main__":
    main() 