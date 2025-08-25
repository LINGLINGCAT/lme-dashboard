import sqlite3
from datetime import datetime, timedelta
import random

def init_sample_data():
    """初始化示例數據"""
    conn = sqlite3.connect('quotation_system.db')
    cursor = conn.cursor()
    
    # 清空現有數據
    cursor.execute("DELETE FROM partners")
    cursor.execute("DELETE FROM market_prices")
    cursor.execute("DELETE FROM quotations")
    cursor.execute("DELETE FROM quotation_items")
    cursor.execute("DELETE FROM quotation_history")
    
    # 插入示例客戶
    sample_customers = [
        ('C001', 'ABC金屬公司', 'SUPPLIER', '張經理', '02-1234-5678', 'zhang@abc.com', '台北市信義區信義路100號', '12345678', '月結30天', 1000000),
        ('C002', 'XYZ製造公司', 'CUSTOMER', '李經理', '02-2345-6789', 'li@xyz.com', '新北市板橋區文化路200號', '23456789', '現金交易', 500000),
        ('C003', 'DEF貿易公司', 'BOTH', '王經理', '02-3456-7890', 'wang@def.com', '台中市西區台灣大道300號', '34567890', '月結15天', 800000),
        ('C004', 'GHI工業公司', 'CUSTOMER', '陳經理', '02-4567-8901', 'chen@ghi.com', '高雄市前金區中正路400號', '45678901', '預付50%', 300000),
        ('C005', 'JKL材料公司', 'SUPPLIER', '劉經理', '02-5678-9012', 'liu@jkl.com', '桃園市中壢區環北路500號', '56789012', '月結45天', 1200000),
    ]
    
    cursor.executemany('''
        INSERT INTO partners (
            partner_code, partner_name, partner_type, contact_person, phone, email, 
            address, tax_id, payment_terms, credit_limit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_customers)
    
    # 插入示例市場價格
    products = ['磷青銅', '紅銅', '錫', '鋅', '青銅']
    currencies = ['TWD', 'USD']
    
    # 生成過去30天的市場價格
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        for product in products:
            for currency in currencies:
                if currency == 'TWD':
                    if product == '磷青銅':
                        base_price = 285000
                    elif product == '紅銅':
                        base_price = 320000
                    elif product == '錫':
                        base_price = 950000
                    elif product == '鋅':
                        base_price = 120000
                    else:  # 青銅
                        base_price = 280000
                else:  # USD
                    if product == '磷青銅':
                        base_price = 8500
                    elif product == '紅銅':
                        base_price = 9500
                    elif product == '錫':
                        base_price = 28000
                    elif product == '鋅':
                        base_price = 3500
                    else:  # 青銅
                        base_price = 8300
                
                # 添加隨機波動
                variation = random.uniform(-0.05, 0.05)  # ±5%波動
                price = base_price * (1 + variation)
                
                cursor.execute('''
                    INSERT INTO market_prices (product_name, price_date, price, currency, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (product, date.date(), round(price, 2), currency, 'LME'))
    
    # 插入示例報價單
    sample_quotations = [
        ('SQ-20241230-001', '2024-12-30', 'SELL', 2, 'TWD', 2850000, 0.05, 142500, 2992500, 1, 'SENT', '2024-12-31', '磷青銅報價'),
        ('BQ-20241230-001', '2024-12-30', 'BUY', 1, 'USD', 85000, 0.0, 0, 85000, 0, 'DRAFT', '2024-12-31', '紅銅採購'),
        ('SQ-20241229-001', '2024-12-29', 'SELL', 3, 'TWD', 1900000, 0.05, 95000, 1995000, 1, 'ACCEPTED', '2024-12-30', '錫銷售'),
        ('BQ-20241229-001', '2024-12-29', 'BUY', 5, 'USD', 70000, 0.0, 0, 70000, 0, 'REJECTED', '2024-12-30', '鋅採購'),
    ]
    
    cursor.executemany('''
        INSERT INTO quotations (
            quotation_no, quotation_date, quotation_type, customer_id, currency,
            total_amount, tax_rate, tax_amount, total_with_tax, invoice_required,
            status, valid_until, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_quotations)
    
    # 插入示例報價明細
    sample_items = [
        (1, '磷青銅', '銅合金', 10.0, '噸', 285000, 2850000, 283000, 2000, 'C5191規格'),
        (2, '紅銅', '純銅', 10.0, '噸', 8500, 85000, 8600, -100, 'C1100規格'),
        (3, '錫', '純錫', 2.0, '噸', 950000, 1900000, 945000, 5000, 'Sn99.9規格'),
        (4, '鋅', '純鋅', 20.0, '噸', 3500, 70000, 3600, -1000, 'Zn99.9規格'),
    ]
    
    cursor.executemany('''
        INSERT INTO quotation_items (
            quotation_id, product_name, product_category, quantity, unit,
            unit_price, total_price, market_price, price_difference, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_items)
    
    # 插入示例歷史記錄
    sample_history = [
        (1, 'CREATED', 'System', '報價單已創建'),
        (1, 'SENT', 'User', '報價單已發送'),
        (2, 'CREATED', 'System', '報價單已創建'),
        (3, 'CREATED', 'System', '報價單已創建'),
        (3, 'SENT', 'User', '報價單已發送'),
        (3, 'ACCEPTED', 'Customer', '客戶已接受報價'),
        (4, 'CREATED', 'System', '報價單已創建'),
        (4, 'SENT', 'User', '報價單已發送'),
        (4, 'REJECTED', 'Supplier', '供應商拒絕報價'),
    ]
    
    cursor.executemany('''
        INSERT INTO quotation_history (
            quotation_id, action_type, action_by, notes
        ) VALUES (?, ?, ?, ?)
    ''', sample_history)
    
    conn.commit()
    conn.close()
    
    print("✅ 示例數據初始化完成！")
    print("📊 已創建：")
    print("   - 5個客戶/供應商")
    print("   - 300條市場價格記錄")
    print("   - 4個示例報價單")
    print("   - 4個報價明細")
    print("   - 9條歷史記錄")

if __name__ == "__main__":
    init_sample_data()
