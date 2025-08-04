#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def input_customer_data():
    """手動輸入客戶資料"""
    
    print("請輸入您的客戶資料來生成更準確的搜尋關鍵字")
    print("=" * 50)
    
    # 收集客戶公司名稱
    company_names = []
    print("\n請輸入您的客戶公司名稱（每行一個，輸入空行結束）：")
    while True:
        company = input("公司名稱: ").strip()
        if not company:
            break
        company_names.append(company)
    
    # 收集常見關鍵字
    keywords = []
    print("\n請輸入在客戶資料中常見的關鍵字（每行一個，輸入空行結束）：")
    while True:
        keyword = input("關鍵字: ").strip()
        if not keyword:
            break
        keywords.append(keyword)
    
    # 分析並生成建議
    print("\n" + "=" * 50)
    print("分析結果：")
    print("=" * 50)
    
    # 分析公司名稱
    if company_names:
        print(f"\n輸入的公司名稱（{len(company_names)}個）：")
        for i, company in enumerate(company_names, 1):
            print(f"  {i}. {company}")
    
    # 分析關鍵字
    if keywords:
        print(f"\n輸入的關鍵字（{len(keywords)}個）：")
        for i, keyword in enumerate(keywords, 1):
            print(f"  {i}. {keyword}")
    
    # 生成建議的搜尋關鍵字
    suggested_keywords = generate_suggested_keywords(company_names, keywords)
    
    print(f"\n建議的搜尋關鍵字（{len(suggested_keywords)}個）：")
    for i, keyword in enumerate(suggested_keywords, 1):
        print(f"  {i}. {keyword}")
    
    # 更新config.py
    update_config_keywords(suggested_keywords)
    
    print("\n關鍵字已更新到config.py檔案中！")

def generate_suggested_keywords(company_names, keywords):
    """生成建議的搜尋關鍵字"""
    suggested = []
    
    # 從公司名稱中提取關鍵字
    for company in company_names:
        # 移除常見的公司後綴
        import re
        company_clean = re.sub(r'(有限公司|股份有限公司|公司|企業|工業|製造|工廠)$', '', company)
        if len(company_clean) >= 2:
            suggested.append(company_clean)
    
    # 添加輸入的關鍵字
    suggested.extend(keywords)
    
    # 添加一些通用的關鍵字
    general_keywords = [
        "沖壓工廠", "沖壓廠", "金屬沖壓", "精密沖壓",
        "電線電纜廠", "電纜廠", "電線廠", "電纜製造",
        "銅加工", "銅製品", "銅材加工", "銅管製造",
        "廢銅回收", "廢金屬回收", "金屬回收",
        "五金加工", "金屬加工", "機械加工"
    ]
    suggested.extend(general_keywords)
    
    return list(set(suggested))  # 去重

def update_config_keywords(keywords):
    """更新config.py中的關鍵字"""
    config_path = "config.py"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到關鍵字列表的位置
        start_marker = "COPPER_CUSTOMER_KEYWORDS = ["
        end_marker = "]"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            start_pos += len(start_marker)
            end_pos = content.find(end_marker, start_pos)
            
            # 生成新的關鍵字列表
            new_keywords_str = '\n    "' + '",\n    "'.join(keywords) + '"\n'
            
            # 替換關鍵字列表
            new_content = content[:start_pos] + new_keywords_str + content[end_pos:]
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"\n已更新 {config_path} 檔案！")
        else:
            print("無法找到關鍵字列表位置")
    
    except Exception as e:
        print(f"更新config.py失敗: {e}")

if __name__ == "__main__":
    input_customer_data() 