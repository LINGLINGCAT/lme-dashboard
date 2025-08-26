import sqlite3
import pandas as pd

def view_database():
    """查看數據庫內容"""
    conn = sqlite3.connect('quotation_system.db')
    
    print("=== 數據庫表格 ===")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n=== 客戶資料 (前3筆) ===")
    try:
        df = pd.read_sql('SELECT id, partner_name, partner_type, contact_person FROM partners LIMIT 3', conn)
        print(df)
    except Exception as e:
        print(f"讀取客戶資料失敗: {e}")
    
    print("\n=== 報價單 (前3筆) ===")
    try:
        df2 = pd.read_sql('SELECT quotation_no, quotation_date, quotation_type, total_amount FROM quotations LIMIT 3', conn)
        print(df2)
    except Exception as e:
        print(f"讀取報價單失敗: {e}")
    
    print("\n=== 市場價格 (前3筆) ===")
    try:
        df3 = pd.read_sql('SELECT product_name, price_date, price, currency FROM market_prices LIMIT 3', conn)
        print(df3)
    except Exception as e:
        print(f"讀取市場價格失敗: {e}")
    
    conn.close()

if __name__ == "__main__":
    view_database()

