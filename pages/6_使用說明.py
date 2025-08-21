import streamlit as st
from utils.auth import check_password, logout, is_admin

# 檢查密碼認證
check_password()

# --- 頁面設定 ---
st.set_page_config(page_title="使用說明", page_icon="📖", layout="wide")

def main():
    # 側邊欄登出按鈕
    with st.sidebar:
        if st.button("🚪 登出", type="secondary"):
            logout()
    
    st.title("📖 使用說明")
    st.subheader("LME 報價看板完整操作指南")
    st.markdown("---")
    
    # 目錄
    st.markdown("## 📋 目錄")
    toc = """
    1. [快速開始](#快速開始)
    2. [功能頁面說明](#功能頁面說明)
    3. [數據來源](#數據來源)
    4. [計算工具使用](#計算工具使用)
    5. [常見問題](#常見問題)
    6. [故障排除](#故障排除)
    7. [進階功能](#進階功能)
    """
    st.markdown(toc)
    
    st.markdown("---")
    
    # 快速開始
    st.markdown("## 🚀 快速開始")
    
    with st.expander("首次使用指南", expanded=True):
        st.markdown("""
        ### 第一步：登入系統
        1. 在登入頁面輸入您的密碼
        2. 密碼預設為 "password"（建議首次登入後立即更改）
        3. 登入成功後會自動跳轉到主頁面
        
        ### 第二步：選擇功能頁面
        從左側側邊欄選擇您需要的功能：
        - **LME 即時報價看板**：查看即時金屬價格
        - **前日收盤**：查看歷史收盤價
        - **線上計算機**：進行價格計算
        - **數據分析**：查看趨勢分析
        - **系統設定**：自定義設定
        - **使用說明**：本頁面
        
        ### 第三步：開始使用
        根據您的需求選擇相應功能，系統會自動載入最新數據。
        """)
    
    st.markdown("---")
    
    # 功能頁面說明
    st.markdown("## 📊 功能頁面說明")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 LME 即時報價看板")
        st.markdown("""
        **功能：**
        - 即時顯示 LME 金屬價格
        - 台銀匯率資訊
        - 自動價格試算
        
        **使用方式：**
        1. 頁面會自動每5秒更新數據
        2. 查看即時價格和漲跌幅
        3. 系統自動計算 CSP 價格
        
        **數據來源：**
        - LME 價格：fx678.com
        - 台銀匯率：bot.com.tw
        """)
        
        st.markdown("### 📅 前日收盤")
        st.markdown("""
        **功能：**
        - 查看 Westmetall 收盤價
        - 台銀歷史匯率
        - CSP 價格試算
        - 歷史數據圖表
        
        **使用方式：**
        1. 查看前日收盤價格
        2. 進行價格計算
        3. 查看歷史趨勢圖
        """)
    
    with col2:
        st.markdown("### 🧮 線上計算機")
        st.markdown("""
        **功能：**
        - 自定義成分計算
        - LME 係數計算
        - 現價計算
        - 批量計算
        
        **使用方式：**
        1. 選擇預設成分或自定義
        2. 輸入價格進行計算
        3. 查看計算結果和百分比
        """)
        
        st.markdown("### 📊 數據分析")
        st.markdown("""
        **功能：**
        - 價格趨勢分析
        - 波動性分析
        - 相關性分析
        - 數據下載
        
        **使用方式：**
        1. 選擇要分析的價格指標
        2. 查看各種分析圖表
        3. 下載分析結果
        """)
    
    st.markdown("---")
    
    # 數據來源
    st.markdown("## 📡 數據來源")
    
    st.markdown("### 即時數據來源")
    
    data_sources = {
        "LME 金屬價格": {
            "來源": "fx678.com",
            "更新頻率": "每5秒",
            "包含數據": "銅、錫、鋅等金屬價格",
            "備註": "即時市場價格"
        },
        "台銀匯率": {
            "來源": "bot.com.tw",
            "更新頻率": "每5秒",
            "包含數據": "USD、CNY 等匯率",
            "備註": "台灣銀行官方匯率"
        },
        "Westmetall 收盤價": {
            "來源": "westmetall.com",
            "更新頻率": "每小時",
            "包含數據": "LME 收盤價",
            "備註": "德國 Westmetall 數據"
        }
    }
    
    for source, info in data_sources.items():
        with st.expander(f"📊 {source}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**來源網站：** {info['來源']}")
                st.markdown(f"**更新頻率：** {info['更新頻率']}")
            with col2:
                st.markdown(f"**包含數據：** {info['包含數據']}")
                st.markdown(f"**備註：** {info['備註']}")
    
    st.markdown("---")
    
    # 計算工具使用
    st.markdown("## 🧮 計算工具使用")
    
    st.markdown("### 成分計算")
    
    with st.expander("如何進行成分計算", expanded=True):
        st.markdown("""
        **步驟：**
        1. 進入「線上計算機」頁面
        2. 選擇預設成分或自定義成分
        3. 輸入各金屬的百分比（總和應為100%）
        4. 選擇計算模式：
           - **現價計算**：輸入價格計算百分比
           - **LME係數計算**：使用LME係數計算價格
        5. 查看計算結果
        
        **預設成分：**
        - C2680：銅70%，鋅30%
        - C2600：銅70%，鋅30%
        - 磷青銅：銅94%，錫6%
        - 青銅：銅65%，鋅35%
        - 紅銅：銅100%
        """)
    
    st.markdown("### LME 係數計算")
    
    with st.expander("LME 係數計算說明"):
        st.markdown("""
        **銅價百分比計算：**
        - 公式：LME銅價 × 百分比
        - 適用：簡單的銅價比例計算
        
        **複合成分係數計算：**
        - 公式：(cu×65% + zn×35%) × 98%
        - 適用：複雜的合金成分計算
        
        **使用步驟：**
        1. 選擇計算類型
        2. 輸入係數參數
        3. 系統自動計算結果
        4. 查看對應的銅價百分比
        """)
    
    st.markdown("---")
    
    # 常見問題
    st.markdown("## ❓ 常見問題")
    
    faq_data = {
        "Q: 為什麼數據載入失敗？": {
            "A": "可能是網路連線問題或數據來源網站暫時無法存取。請稍後再試或檢查網路連線。",
            "解決方法": "重新整理頁面或等待幾分鐘後再試"
        },
        "Q: 計算結果不正確怎麼辦？": {
            "A": "請檢查輸入的成分百分比是否總和為100%，以及價格輸入是否正確。",
            "解決方法": "重新檢查輸入數據，確保格式正確"
        },
        "Q: 如何更改密碼？": {
            "A": "進入「系統設定」頁面，在「安全設定」分頁中更改密碼。",
            "解決方法": "設定新密碼後，記得更新 .env 檔案"
        },
        "Q: 數據多久更新一次？": {
            "A": "即時數據每5秒更新，歷史數據每天更新。",
            "解決方法": "可在系統設定中調整更新頻率"
        },
        "Q: 如何下載數據？": {
            "A": "在「數據分析」頁面可以下載 CSV 格式的歷史數據。",
            "解決方法": "點擊下載按鈕即可獲得數據檔案"
        }
    }
    
    for question, answer in faq_data.items():
        with st.expander(question):
            st.markdown(f"**答案：** {answer['A']}")
            st.markdown(f"**解決方法：** {answer['解決方法']}")
    
    st.markdown("---")
    
    # 故障排除
    st.markdown("## 🔧 故障排除")
    
    st.markdown("### 常見錯誤及解決方法")
    
    error_solutions = {
        "ModuleNotFoundError": {
            "原因": "缺少必要的 Python 套件",
            "解決方法": "執行 `pip install -r requirements.txt`"
        },
        "ConnectionError": {
            "原因": "網路連線問題",
            "解決方法": "檢查網路連線，稍後再試"
        },
        "AuthenticationError": {
            "原因": "密碼錯誤或帳戶被鎖定",
            "解決方法": "檢查密碼，或等待鎖定時間結束"
        },
        "DataLoadError": {
            "原因": "數據來源網站暫時無法存取",
            "解決方法": "稍後再試，或使用快取數據"
        }
    }
    
    for error, solution in error_solutions.items():
        with st.expander(f"❌ {error}"):
            st.markdown(f"**原因：** {solution['原因']}")
            st.markdown(f"**解決方法：** {solution['解決方法']}")
    
    st.markdown("### 系統維護")
    
    st.markdown("""
    **定期維護項目：**
    1. **清理快取數據**：在系統設定中清理舊的快取檔案
    2. **更新密碼**：定期更改登入密碼
    3. **備份數據**：定期下載重要數據
    4. **檢查更新**：定期檢查系統更新
    """)
    
    st.markdown("---")
    
    # 進階功能
    st.markdown("## 🚀 進階功能")
    
    st.markdown("### 數據分析功能")
    
    with st.expander("如何使用數據分析功能"):
        st.markdown("""
        **價格趨勢分析：**
        - 選擇要分析的價格指標
        - 查看價格變化趨勢
        - 識別季節性和週期性模式
        
        **波動性分析：**
        - 計算各產品的波動率
        - 比較不同產品的風險
        - 評估投資風險
        
        **相關性分析：**
        - 查看產品間的相關性
        - 識別分散投資機會
        - 優化投資組合
        """)
    
    st.markdown("### 系統設定功能")
    
    with st.expander("系統設定說明"):
        st.markdown("""
        **一般設定：**
        - 調整更新頻率
        - 選擇界面主題
        - 設定語言偏好
        
        **安全設定：**
        - 更改登入密碼
        - 設定登入嘗試次數
        - 配置鎖定時間
        
        **數據設定：**
        - 選擇數據來源
        - 設定快取參數
        - 配置匯出格式
        """)
    
    st.markdown("### 快捷鍵")
    
    st.markdown("""
    **常用快捷鍵：**
    - `Ctrl + R`：重新整理頁面
    - `Ctrl + F`：搜尋功能
    - `F5`：重新載入數據
    - `Esc`：關閉彈出視窗
    """)
    
    st.markdown("---")
    
    # 聯絡支援
    st.markdown("## 📞 聯絡支援")
    
    st.markdown("""
    **如需進一步協助：**
    
    📧 **技術支援：** 請檢查系統設定中的錯誤日誌
    
    📖 **文件資源：** 查看 README.md 檔案
    
    🔧 **系統狀態：** 在系統設定頁面查看系統資訊
    
    ⚠️ **緊急問題：** 重新啟動應用程式或檢查網路連線
    """)
    
    # 底部資訊
    st.markdown("---")
    st.markdown("""
    **📝 版本資訊：**
    - 當前版本：V1.5
    - 最後更新：2024年1月
    - 支援平台：Windows, macOS, Linux
    
    **💡 使用提示：**
    - 建議使用 Chrome 或 Firefox 瀏覽器
    - 保持網路連線穩定
    - 定期備份重要數據
    """)

if __name__ == "__main__":
    main() 