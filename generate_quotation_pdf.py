import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def get_quotation_data(quotation_id):
    """從數據庫獲取報價單數據"""
    conn = sqlite3.connect('quotation_system.db')
    
    # 獲取報價單主表數據
    quotation_df = pd.read_sql_query('''
        SELECT q.*, p.partner_name, p.contact_person, p.phone, p.address
        FROM quotations q
        LEFT JOIN partners p ON q.customer_id = p.id
        WHERE q.id = ?
    ''', conn, params=[quotation_id])
    
    # 獲取報價明細
    items_df = pd.read_sql_query('''
        SELECT * FROM quotation_items WHERE quotation_id = ?
    ''', conn, params=[quotation_id])
    
    conn.close()
    
    return quotation_df.iloc[0] if not quotation_df.empty else None, items_df

def generate_quotation_pdf(quotation_id, output_path=None):
    """生成固定格式的PDF報價單"""
    
    # 獲取數據
    quotation, items = get_quotation_data(quotation_id)
    
    if quotation is None:
        print(f"❌ 找不到報價單 ID: {quotation_id}")
        return
    
    # 設置輸出文件路徑
    if output_path is None:
        output_path = f"報價單_{quotation['quotation_no']}.pdf"
    
    # 創建PDF文檔
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    # 樣式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # 居中
    )
    
    # 標題
    story.append(Paragraph("報價單", title_style))
    story.append(Spacer(1, 20))
    
    # 基本信息表格
    basic_info = [
        ['報價單號:', quotation['quotation_no'], '報價日期:', quotation['quotation_date']],
        ['客戶名稱:', quotation['partner_name'], '聯絡人:', quotation['contact_person']],
        ['電話:', quotation['phone'], '地址:', quotation['address']],
        ['報價類型:', quotation['quotation_type'], '幣值:', quotation['currency']],
        ['有效期至:', quotation['valid_until'], '稅率:', f"{quotation['tax_rate']*100}%"]
    ]
    
    basic_table = Table(basic_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    basic_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('BACKGROUND', (2, 0), (2, -1), colors.grey),
    ]))
    
    story.append(basic_table)
    story.append(Spacer(1, 20))
    
    # 品項明細表格
    if not items.empty:
        # 準備表格數據
        table_data = [['品項', '數量', '單位', '單價', '小計', '備註']]
        
        for _, item in items.iterrows():
            table_data.append([
                item['product_name'],
                str(item['quantity']),
                item['unit'],
                f"{item['unit_price']:,.2f}",
                f"{item['total_price']:,.2f}",
                item.get('notes', '')
            ])
        
        # 添加合計行
        total_amount = items['total_price'].sum()
        tax_amount = total_amount * quotation['tax_rate']
        total_with_tax = total_amount + tax_amount
        
        table_data.extend([
            ['', '', '', '小計:', f"{total_amount:,.2f}", ''],
            ['', '', '', '稅額:', f"{tax_amount:,.2f}", ''],
            ['', '', '', '總計:', f"{total_with_tax:,.2f}", '']
        ])
        
        items_table = Table(table_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # 品項左對齊
            ('ALIGN', (-1, 0), (-1, -1), 'LEFT'),  # 備註左對齊
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
        ]))
        
        story.append(Paragraph("品項明細", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(items_table)
        story.append(Spacer(1, 20))
    
    # 備註
    if quotation['notes']:
        story.append(Paragraph("備註:", styles['Heading3']))
        story.append(Paragraph(quotation['notes'], styles['Normal']))
        story.append(Spacer(1, 20))
    
    # 條款
    terms = [
        "1. 本報價單有效期至上述日期止",
        "2. 付款條件：貨到付款或依雙方約定",
        "3. 交貨地點：依雙方約定",
        "4. 品質保證：依國際標準或雙方約定",
        "5. 其他條款依雙方協議"
    ]
    
    story.append(Paragraph("條款與條件:", styles['Heading3']))
    for term in terms:
        story.append(Paragraph(term, styles['Normal']))
    
    # 生成PDF
    doc.build(story)
    print(f"✅ PDF報價單已生成: {output_path}")
    return output_path

def generate_contract_pdf(quotation_id, output_path=None):
    """生成合約PDF"""
    # 類似報價單的邏輯，但格式更正式
    # 這裡可以擴展為正式的合約格式
    pass

def main():
    print("=== 報價單PDF生成器 ===")
    
    # 顯示所有報價單
    conn = sqlite3.connect('quotation_system.db')
    quotations_df = pd.read_sql_query('''
        SELECT q.id, q.quotation_no, q.quotation_date, q.quotation_type, 
               q.total_amount, p.partner_name
        FROM quotations q
        LEFT JOIN partners p ON q.customer_id = p.id
        ORDER BY q.created_at DESC
    ''', conn)
    conn.close()
    
    if not quotations_df.empty:
        print("\n=== 可用的報價單 ===")
        for _, row in quotations_df.iterrows():
            print(f"ID: {row['id']} | {row['quotation_no']} | {row['partner_name']} | {row['total_amount']:,.0f}")
        
        print("\n請輸入要生成PDF的報價單ID:")
        # 這裡可以添加用戶輸入邏輯
        
        # 示例：生成第一個報價單的PDF
        if len(quotations_df) > 0:
            quotation_id = quotations_df.iloc[0]['id']
            generate_quotation_pdf(quotation_id)
    else:
        print("暫無報價單記錄")

if __name__ == "__main__":
    main()

