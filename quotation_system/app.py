import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

# 頁面配置
st.set_page_config(
    page_title="智能報價系統",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化數據庫
def init_database():
    """初始化數據庫和表格"""
    conn = sqlite3.connect('quotation_system.db')
    cursor = conn.cursor()
    
    # 創建客戶/供應商表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_code VARCHAR(20) UNIQUE,
            partner_name VARCHAR(100),
            partner_type TEXT CHECK(partner_type IN ('CUSTOMER', 'SUPPLIER', 'BOTH')),
            contact_person VARCHAR(50),
            phone VARCHAR(20),
            email VARCHAR(100),
            address TEXT,
            tax_id VARCHAR(20),
            payment_terms VARCHAR(100),
            credit_limit DECIMAL(15,2),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 創建報價單主表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_no VARCHAR(20) UNIQUE,
            quotation_date DATE,
            quotation_type TEXT CHECK(quotation_type IN ('BUY', 'SELL')),
            customer_id INTEGER,
            currency TEXT CHECK(currency IN ('TWD', 'USD')),
            total_amount DECIMAL(15,2),
            tax_rate DECIMAL(5,2) DEFAULT 0.05,
            tax_amount DECIMAL(15,2),
            total_with_tax DECIMAL(15,2),
            invoice_required BOOLEAN DEFAULT 0,
            invoice_no VARCHAR(20),
            status TEXT CHECK(status IN ('DRAFT', 'SENT', 'ACCEPTED', 'REJECTED', 'EXPIRED')) DEFAULT 'DRAFT',
            valid_until DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES partners(id)
        )
    ''')
    
    # 創建報價明細表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            product_name VARCHAR(50),
            product_category VARCHAR(30),
            quantity DECIMAL(10,2),
            unit VARCHAR(20),
            unit_price DECIMAL(15,2),
            total_price DECIMAL(15,2),
            market_price DECIMAL(15,2),
            price_difference DECIMAL(15,2),
            notes TEXT,
            FOREIGN KEY (quotation_id) REFERENCES quotations(id)
        )
    ''')
    
    # 創建市場價格表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name VARCHAR(50),
            price_date DATE,
            price DECIMAL(15,2),
            currency TEXT CHECK(currency IN ('TWD', 'USD')),
            source VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 創建報價歷史記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            action_type TEXT CHECK(action_type IN ('CREATED', 'SENT', 'VIEWED', 'ACCEPTED', 'REJECTED', 'EXPIRED')),
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action_by VARCHAR(50),
            notes TEXT,
            FOREIGN KEY (quotation_id) REFERENCES quotations(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# 生成報價單號
def generate_quotation_no(quotation_type):
    """生成報價單號"""
    conn = sqlite3.connect('quotation_system.db')
    cursor = conn.cursor()
    
    # 獲取今天的日期
    today = datetime.now().strftime('%Y%m%d')
    
    # 查詢今天的報價單數量
    cursor.execute('''
        SELECT COUNT(*) FROM quotations 
        WHERE quotation_no LIKE ? AND quotation_date = ?
    ''', (f'{quotation_type}Q-{today}-%', today))
    
    count = cursor.fetchone()[0] + 1
    
    conn.close()
    
    return f"{quotation_type}Q-{today}-{count:03d}"

# 獲取市場價格
def get_market_price(product_name, currency):
    """獲取最新市場價格"""
    conn = sqlite3.connect('quotation_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT price FROM market_prices 
        WHERE product_name = ? AND currency = ?
        ORDER BY price_date DESC, created_at DESC
        LIMIT 1
    ''', (product_name, currency))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0

# 計算價格建議
def suggest_price(product_name, currency, quotation_type, customer_id=None):
    """智能價格建議"""
    market_price = get_market_price(product_name, currency)
    
    if market_price == 0:
        return 0
    
    # 根據買賣類型調整價格
    if quotation_type == 'BUY':
        # 買入價格建議：市場價格的95-98%
        suggested_price = market_price * 0.96
    else:
        # 賣出價格建議：市場價格的102-105%
        suggested_price = market_price * 1.03
    
    return round(suggested_price, 2)

# 主應用
def main():
    # 初始化數據庫
    init_database()
    
    # 側邊欄
    st.sidebar.title("💰 智能報價系統")
    
    # 導航選單
    page = st.sidebar.selectbox(
        "選擇功能",
        ["📝 新增報價", "📋 報價管理", "👥 客戶管理", "📊 數據分析", "⚙️ 系統設定"]
    )
    
    # 頁面路由
    if page == "📝 新增報價":
        show_new_quotation()
    elif page == "📋 報價管理":
        show_quotation_management()
    elif page == "👥 客戶管理":
        show_customer_management()
    elif page == "📊 數據分析":
        show_data_analysis()
    elif page == "⚙️ 系統設定":
        show_system_settings()

# 新增報價頁面
def show_new_quotation():
    st.title("📝 新增報價單")
    st.markdown("---")
    
    # 基本信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quotation_type = st.selectbox("報價類型", ["SELL", "BUY"])
        currency = st.selectbox("幣值", ["TWD", "USD"])
    
    with col2:
        quotation_date = st.date_input("報價日期", datetime.now())
        valid_days = st.number_input("有效期(天)", min_value=1, max_value=90, value=7)
    
    with col3:
        invoice_required = st.checkbox("需要發票")
        tax_rate = st.number_input("稅率(%)", min_value=0.0, max_value=100.0, value=5.0) / 100
    
    # 客戶選擇
    st.subheader("客戶/供應商信息")
    col1, col2 = st.columns(2)
    
    with col1:
        # 獲取客戶列表
        conn = sqlite3.connect('quotation_system.db')
        customers = pd.read_sql_query('''
            SELECT id, partner_name, partner_type FROM partners 
            WHERE is_active = 1
        ''', conn)
        conn.close()
        
        if not customers.empty:
            customer_options = {f"{row['partner_name']} ({row['partner_type']})": row['id'] 
                              for _, row in customers.iterrows()}
            selected_customer = st.selectbox("選擇客戶/供應商", list(customer_options.keys()))
            customer_id = customer_options[selected_customer]
        else:
            st.warning("請先在客戶管理中新增客戶/供應商")
            return
    
    with col2:
        if st.button("➕ 新增客戶"):
            st.session_state.show_new_customer = True
    
    # 品項明細
    st.subheader("品項明細")
    
    # 初始化品項列表
    if 'items' not in st.session_state:
        st.session_state.items = []
    
    # 新增品項
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        product_name = st.selectbox("品項", ["磷青銅", "紅銅", "錫", "鋅", "青銅"])
    
    with col2:
        quantity = st.number_input("數量", min_value=0.01, value=1.0, step=0.01)
    
    with col3:
        unit = st.selectbox("單位", ["噸", "KG", "個"])
    
    with col4:
        unit_price = st.number_input("單價", min_value=0.0, value=0.0, step=0.01)
    
    with col5:
        if st.button("➕ 新增品項"):
            # 獲取市場價格
            market_price = get_market_price(product_name, currency)
            
            # 計算小計
            total_price = quantity * unit_price
            
            # 計算與市場價差
            price_diff = unit_price - market_price if market_price > 0 else 0
            
            # 添加到品項列表
            item = {
                'product_name': product_name,
                'quantity': quantity,
                'unit': unit,
                'unit_price': unit_price,
                'total_price': total_price,
                'market_price': market_price,
                'price_difference': price_diff
            }
            st.session_state.items.append(item)
            st.success(f"已新增 {product_name}")
    
    # 顯示品項列表
    if st.session_state.items:
        st.subheader("已新增品項")
        
        # 創建DataFrame
        items_df = pd.DataFrame(st.session_state.items)
        
        # 顯示表格
        st.dataframe(items_df, use_container_width=True)
        
        # 計算總計
        total_amount = items_df['total_price'].sum()
        tax_amount = total_amount * tax_rate
        total_with_tax = total_amount + tax_amount
        
        # 顯示總計
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("總計", f"{currency} {total_amount:,.2f}")
        with col2:
            st.metric("稅額", f"{currency} {tax_amount:,.2f}")
        with col3:
            st.metric("含稅總額", f"{currency} {total_with_tax:,.2f}")
        with col4:
            st.metric("品項數量", len(st.session_state.items))
        
        # 備註
        notes = st.text_area("備註")
        
        # 保存按鈕
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("💾 保存報價單", type="primary"):
                save_quotation(quotation_type, currency, quotation_date, valid_days, 
                             customer_id, invoice_required, tax_rate, notes)

# 保存報價單
def save_quotation(quotation_type, currency, quotation_date, valid_days, 
                  customer_id, invoice_required, tax_rate, notes):
    """保存報價單到數據庫"""
    try:
        conn = sqlite3.connect('quotation_system.db')
        cursor = conn.cursor()
        
        # 生成報價單號
        quotation_no = generate_quotation_no(quotation_type)
        
        # 計算總計
        total_amount = sum(item['total_price'] for item in st.session_state.items)
        tax_amount = total_amount * tax_rate
        total_with_tax = total_amount + tax_amount
        
        # 有效期
        valid_until = quotation_date + timedelta(days=valid_days)
        
        # 插入報價單主表
        cursor.execute('''
            INSERT INTO quotations (
                quotation_no, quotation_date, quotation_type, customer_id,
                currency, total_amount, tax_rate, tax_amount, total_with_tax,
                invoice_required, status, valid_until, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quotation_no, quotation_date, quotation_type, customer_id,
              currency, total_amount, tax_rate, tax_amount, total_with_tax,
              invoice_required, 'DRAFT', valid_until, notes))
        
        quotation_id = cursor.lastrowid
        
        # 插入品項明細
        for item in st.session_state.items:
            cursor.execute('''
                INSERT INTO quotation_items (
                    quotation_id, product_name, quantity, unit, unit_price,
                    total_price, market_price, price_difference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (quotation_id, item['product_name'], item['quantity'], 
                  item['unit'], item['unit_price'], item['total_price'],
                  item['market_price'], item['price_difference']))
        
        # 插入歷史記錄
        cursor.execute('''
            INSERT INTO quotation_history (quotation_id, action_type, action_by, notes)
            VALUES (?, 'CREATED', 'System', '報價單已創建')
        ''', (quotation_id,))
        
        conn.commit()
        conn.close()
        
        # 清空品項列表
        st.session_state.items = []
        
        st.success(f"✅ 報價單已保存！報價單號：{quotation_no}")
        
    except Exception as e:
        st.error(f"❌ 保存失敗：{str(e)}")

# 報價管理頁面
def show_quotation_management():
    st.title("📋 報價管理")
    st.markdown("---")
    
    # 篩選條件
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("狀態篩選", ["全部", "DRAFT", "SENT", "ACCEPTED", "REJECTED", "EXPIRED"])
    
    with col2:
        type_filter = st.selectbox("類型篩選", ["全部", "BUY", "SELL"])
    
    with col3:
        currency_filter = st.selectbox("幣值篩選", ["全部", "TWD", "USD"])
    
    with col4:
        date_filter = st.date_input("日期篩選", datetime.now())
    
    # 查詢報價單
    conn = sqlite3.connect('quotation_system.db')
    
    query = '''
        SELECT q.*, p.partner_name, p.partner_type
        FROM quotations q
        LEFT JOIN partners p ON q.customer_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if status_filter != "全部":
        query += " AND q.status = ?"
        params.append(status_filter)
    
    if type_filter != "全部":
        query += " AND q.quotation_type = ?"
        params.append(type_filter)
    
    if currency_filter != "全部":
        query += " AND q.currency = ?"
        params.append(currency_filter)
    
    query += " ORDER BY q.created_at DESC"
    
    quotations_df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # 顯示報價單列表
    if not quotations_df.empty:
        st.dataframe(quotations_df, use_container_width=True)
        
        # 統計信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("總報價單數", len(quotations_df))
        with col2:
            accepted_count = len(quotations_df[quotations_df['status'] == 'ACCEPTED'])
            st.metric("成功報價", accepted_count)
        with col3:
            success_rate = (accepted_count / len(quotations_df)) * 100 if len(quotations_df) > 0 else 0
            st.metric("成功率", f"{success_rate:.1f}%")
        with col4:
            total_amount = quotations_df['total_amount'].sum()
            st.metric("總金額", f"{total_amount:,.0f}")
    else:
        st.info("暫無報價單記錄")

# 客戶管理頁面
def show_customer_management():
    st.title("👥 客戶管理")
    st.markdown("---")
    
    # 新增客戶
    with st.expander("➕ 新增客戶/供應商"):
        col1, col2 = st.columns(2)
        
        with col1:
            partner_code = st.text_input("客戶代碼")
            partner_name = st.text_input("客戶名稱")
            partner_type = st.selectbox("類型", ["CUSTOMER", "SUPPLIER", "BOTH"])
            contact_person = st.text_input("聯絡人")
            phone = st.text_input("電話")
        
        with col2:
            email = st.text_input("電子郵件")
            address = st.text_area("地址")
            tax_id = st.text_input("統一編號")
            payment_terms = st.text_input("付款條件")
            credit_limit = st.number_input("信用額度", min_value=0.0, value=0.0)
        
        if st.button("💾 保存客戶"):
            save_customer(partner_code, partner_name, partner_type, contact_person,
                         phone, email, address, tax_id, payment_terms, credit_limit)
    
    # 客戶列表
    conn = sqlite3.connect('quotation_system.db')
    customers_df = pd.read_sql_query('''
        SELECT * FROM partners WHERE is_active = 1 ORDER BY created_at DESC
    ''', conn)
    conn.close()
    
    if not customers_df.empty:
        st.dataframe(customers_df, use_container_width=True)
    else:
        st.info("暫無客戶記錄")

# 保存客戶
def save_customer(partner_code, partner_name, partner_type, contact_person,
                 phone, email, address, tax_id, payment_terms, credit_limit):
    """保存客戶到數據庫"""
    try:
        conn = sqlite3.connect('quotation_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO partners (
                partner_code, partner_name, partner_type, contact_person,
                phone, email, address, tax_id, payment_terms, credit_limit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (partner_code, partner_name, partner_type, contact_person,
              phone, email, address, tax_id, payment_terms, credit_limit))
        
        conn.commit()
        conn.close()
        
        st.success("✅ 客戶已保存！")
        
    except Exception as e:
        st.error(f"❌ 保存失敗：{str(e)}")

# 數據分析頁面
def show_data_analysis():
    st.title("📊 數據分析")
    st.markdown("---")
    
    conn = sqlite3.connect('quotation_system.db')
    
    # 報價成功率分析
    st.subheader("📈 報價成功率分析")
    
    success_df = pd.read_sql_query('''
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM quotations), 2) as percentage
        FROM quotations 
        GROUP BY status
    ''', conn)
    
    if not success_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(success_df, values='count', names='status', title='報價狀態分布')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(success_df, x='status', y='percentage', title='各狀態佔比')
            st.plotly_chart(fig, use_container_width=True)
    
    # 金額趨勢分析
    st.subheader("💰 金額趨勢分析")
    
    trend_df = pd.read_sql_query('''
        SELECT 
            DATE(quotation_date) as date,
            SUM(total_amount) as total_amount,
            COUNT(*) as quotation_count
        FROM quotations 
        GROUP BY DATE(quotation_date)
        ORDER BY date DESC
        LIMIT 30
    ''', conn)
    
    if not trend_df.empty:
        fig = px.line(trend_df, x='date', y='total_amount', title='每日報價金額趨勢')
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# 系統設定頁面
def show_system_settings():
    st.title("⚙️ 系統設定")
    st.markdown("---")
    
    # 市場價格管理
    st.subheader("📊 市場價格管理")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        product_name = st.selectbox("品項", ["磷青銅", "紅銅", "錫", "鋅", "青銅"])
    
    with col2:
        price = st.number_input("價格", min_value=0.0, value=0.0, step=0.01)
    
    with col3:
        currency = st.selectbox("幣值", ["TWD", "USD"])
    
    with col4:
        source = st.text_input("價格來源", "LME")
    
    if st.button("💾 保存市場價格"):
        save_market_price(product_name, price, currency, source)
    
    # 顯示市場價格歷史
    conn = sqlite3.connect('quotation_system.db')
    prices_df = pd.read_sql_query('''
        SELECT * FROM market_prices 
        ORDER BY price_date DESC, created_at DESC
        LIMIT 50
    ''', conn)
    conn.close()
    
    if not prices_df.empty:
        st.dataframe(prices_df, use_container_width=True)

# 保存市場價格
def save_market_price(product_name, price, currency, source):
    """保存市場價格到數據庫"""
    try:
        conn = sqlite3.connect('quotation_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_prices (product_name, price_date, price, currency, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_name, datetime.now().date(), price, currency, source))
        
        conn.commit()
        conn.close()
        
        st.success("✅ 市場價格已保存！")
        
    except Exception as e:
        st.error(f"❌ 保存失敗：{str(e)}")

if __name__ == "__main__":
    main()
