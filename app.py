import streamlit as st
import pandas as pd
import numpy as np
import time

# 頁面設定
st.set_page_config(
    page_title="LME 即時報價看板",
    page_icon="📈",
    layout="wide"
)

# 標題
st.title("📈 LME 即時報價看板")

# 假的數據抓取函式 (之後會換成真的)
def fetch_data():
    # 建立一個範例 DataFrame
    data = {
        '商品 (Product)': ['銅 (Copper)', '鋁 (Aluminium)', '鋅 (Zinc)', '鉛 (Lead)'],
        '3個月報價 (3M)': np.random.uniform(8000, 10000, 4),
        '現貨價 (Cash)': np.random.uniform(8000, 10000, 4),
        '漲跌幅 (%)': np.random.uniform(-1.5, 1.5, 4)
    }
    df = pd.DataFrame(data)
    
    # 格式化數字
    df['3個月報價 (3M)'] = df['3個月報價 (3M)'].map('{:,.2f}'.format)
    df['現貨價 (Cash)'] = df['現貨價 (Cash)'].map('{:,.2f}'.format)
    df['漲跌幅 (%)'] = df['漲跌幅 (%)'].map('{:+.2f}%'.format)
    return df

# 建立一個空的容器，用來存放我們的表格
placeholder = st.empty()

# 無窮迴圈，用來持續更新資料
while True:
    # 抓取新數據
    df = fetch_data()
    
    # 在 placeholder 容器中顯示 DataFrame
    with placeholder.container():
        st.header("LME 主要金屬報價")
        st.dataframe(df, use_container_width=True)
    
    # 等待 5 秒
    time.sleep(5)
