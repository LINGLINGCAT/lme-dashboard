#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版數據分析頁面測試
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 頁面配置
st.set_page_config(
    page_title="數據分析測試",
    page_icon="📊",
    layout="wide"
)

st.title("📊 數據分析測試")
st.subheader("簡化版測試")

# 載入數據
def load_data():
    """載入數據"""
    data_paths = [
        Path("data/lme_updated_data.csv"),
        Path("data/csp_history.csv"),
    ]
    
    for path in data_paths:
        if path.exists():
            try:
                df = pd.read_csv(path)
                if not df.empty:
                    st.success(f"✅ 成功載入：{path}")
                    st.write(f"📊 數據：{len(df)} 行，{len(df.columns)} 欄位")
                    st.write(f"📋 欄位：{list(df.columns)}")
                    return df
            except Exception as e:
                st.error(f"❌ 載入失敗：{e}")
    
    st.error("❌ 沒有找到數據文件")
    return None

# 載入數據
df = load_data()

if df is not None:
    st.subheader("📈 數據預覽")
    st.dataframe(df.head(10))
    
    # 檢查數據格式
    if '品項' in df.columns:
        st.write("📊 長格式數據")
        products = df['品項'].unique()
        st.write(f"🏷️ 產品：{list(products)}")
    else:
        st.write("📊 寬格式數據")
        price_cols = [col for col in df.columns if col != '日期']
        st.write(f"🏷️ 價格欄位：{price_cols}")

st.info("✅ 測試完成！")
