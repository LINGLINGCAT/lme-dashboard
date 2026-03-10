#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LME Dashboard - Streamlit Cloud 部署版本
主要入口文件，用於 Streamlit Cloud 部署
"""

import streamlit as st
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ★ 必須是第一個 Streamlit 指令，否則 Cloud 可能出現 "Error running app"
st.set_page_config(
    page_title="LME 即時報價看板",
    page_icon="📈",
    layout="wide"
)

# 嘗試導入認證模組
try:
    from utils.auth import check_password, logout, is_admin
except ImportError as e:
    def check_password():
        return True
    def logout():
        st.rerun()
    def is_admin():
        return True

# 嘗試導入版本模組
try:
    from version import get_version_display
except ImportError:
    def get_version_display():
        return "V1.5"

# 檢查密碼認證
check_password()

# --- CSS to hide the main page from the sidebar and admin pages for non-admin users ---
admin_pages_css = ""
if not is_admin():
    admin_pages_css = """
    /* 隱藏管理員頁面：使用更精確的選擇器 */
    /* 隱藏包含"數據分析"、"系統設定"、"管理員功能"、"智能報價系統"的連結 */
    [data-testid="stSidebarNav"] a[href*="數據分析"],
    [data-testid="stSidebarNav"] a[href*="系統設定"],
    [data-testid="stSidebarNav"] a[href*="管理員功能"],
    [data-testid="stSidebarNav"] a[href*="智能報價系統"] {
        display: none !important;
    }
    /* 隱藏對應的 li 元素 */
    [data-testid="stSidebarNav"] li:has(a[href*="數據分析"]),
    [data-testid="stSidebarNav"] li:has(a[href*="系統設定"]),
    [data-testid="stSidebarNav"] li:has(a[href*="管理員功能"]),
    [data-testid="stSidebarNav"] li:has(a[href*="智能報價系統"]) {
        display: none !important;
    }
    """

st.markdown(f"""
<style>
    [data-testid="stSidebarNav"] > ul > li:first-child {{
        display: none;
    }}
    {admin_pages_css}
</style>
""", unsafe_allow_html=True)

# 側邊欄登出按鈕
with st.sidebar:
    if st.button("🚪 登出", type="secondary"):
        logout()

st.title("歡迎使用 LME 報價看板")
st.sidebar.success("請從上方選擇一個頁面")

# 顯示版本號
st.sidebar.markdown(f"**版本**: {get_version_display()}")

# 根據用戶權限顯示不同的內容
if is_admin():
    st.markdown(
        """
        這是一個使用 Streamlit 建立的 LME 報價與匯率儀表板。
        
        **👈 請從左側的側邊欄選擇您想要查看的頁面：**
        
        ### 📊 核心功能
        - **LME 即時報價看板**: 查看 LME 市場與台銀的即時匯率
        - **前日收盤**: 查看 Westmetall 的 LME 收盤價與台銀的每日匯率
        - **線上計算機**: 自定義成分計算與價格轉換工具
        
        ### 🚀 管理員功能
        - **數據分析**: 歷史數據視覺化與趨勢分析
        - **系統設定**: 自定義密碼、更新頻率等設定
        - **使用說明**: 完整操作指南與故障排除
        - **智能報價系統**: 完整的商業報價管理系統
        
        ### 💡 特色功能
        - 🔄 自動數據更新（每5秒）
        - 📈 即時價格試算
        - 📊 互動式圖表分析
        - 🔐 安全密碼認證
        - 📱 響應式設計（支援手機/電腦）
        """
    )
else:
    st.markdown(
        """
        這是一個使用 Streamlit 建立的 LME 報價與匯率儀表板。
        
        **👈 請從左側的側邊欄選擇您想要查看的頁面：**
        
        ### 📊 核心功能
        - **LME 即時報價看板**: 查看 LME 市場與台銀的即時匯率
        - **前日收盤**: 查看 Westmetall 的 LME 收盤價與台銀的每日匯率
        - **線上計算機**: 自定義成分計算與價格轉換工具
        
        ### 💡 特色功能
        - 🔄 自動數據更新（每5秒）
        - 📈 即時價格試算
        - 📊 互動式圖表分析
        - 🔐 安全密碼認證
        - 📱 響應式設計（支援手機/電腦）
        """
    )
