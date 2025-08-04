#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from collections import Counter

def analyze_customer_folders():
    """分析客戶資料夾結構來生成關鍵字"""
    
    print("正在分析客戶資料夾結構...")
    print("=" * 50)
    
    # 基於您提供的資料夾結構分析
    folder_categories = {
        "沖壓相關": [
            "1沖壓 裁切廠",
            "宏于電機", "宏于袋子只扣0.4 0.7 1.2以他們的磅",
            "旭宏", "得意", "達德鴻德", "岱煒", "銘鈺", "坤勝科技",
            "基準", "續展", "大正科技機械股份有限公司", "信盛精密",
            "德輝科技", "華貿", "宣德", "台塑", "汎新", "鈦貿",
            "名家利", "金峰", "聯懿", "頤溱綠能", "洛瑪"
        ],
        "電線電纜相關": [
            "2家電拆解場 電線電纜",
            "宏于電機", "宏于袋子只扣0.4 0.7 1.2以他們的磅"
        ],
        "機電工程": [
            "3廠房拆解工程行 機電公司",
            "宏于電機", "大正科技機械股份有限公司", "德輝科技"
        ],
        "汽車相關": [
            "4汽車拆解廠"
        ],
        "貿易商": [
            "5古物商 貿易商 中盤商",
            "華貿", "鈦貿", "名家利"
        ],
        "公家機關": [
            "6公家機關"
        ],
        "其他公司": [
            "METALCOM", "Ready", "RMCE", "大吉", "大陸", "尤信",
            "台積電", "弘振", "立得", "宏定", "玖峰企業",
            "邢台雙涵", "亞特吉", "尚唯", "東鈺"
        ]
    }
    
    # 分析公司名稱中的關鍵字
    company_keywords = []
    for category, companies in folder_categories.items():
        for company in companies:
            # 提取公司名稱中的關鍵字
            keywords = extract_keywords_from_company(company)
            company_keywords.extend(keywords)
    
    # 統計關鍵字頻率
    keyword_counter = Counter(company_keywords)
    
    print("分析結果：")
    print("=" * 50)
    
    # 顯示各類別的公司
    for category, companies in folder_categories.items():
        print(f"\n{category}（{len(companies)}個）：")
        for company in companies:
            print(f"  - {company}")
    
    # 生成建議的搜尋關鍵字
    suggested_keywords = generate_keywords_from_analysis(keyword_counter, folder_categories)
    
    print(f"\n建議的搜尋關鍵字（{len(suggested_keywords)}個）：")
    for i, keyword in enumerate(suggested_keywords, 1):
        print(f"  {i}. {keyword}")
    
    # 更新config.py
    update_config_keywords(suggested_keywords)
    
    print("\n關鍵字已更新到config.py檔案中！")
    
    return suggested_keywords

def extract_keywords_from_company(company_name):
    """從公司名稱中提取關鍵字"""
    keywords = []
    
    # 移除常見的公司後綴
    clean_name = re.sub(r'(有限公司|股份有限公司|公司|企業|工業|製造|工廠|科技|精密|機械)$', '', company_name)
    
    # 提取中文關鍵字
    chinese_keywords = re.findall(r'[\u4e00-\u9fff]+', clean_name)
    keywords.extend(chinese_keywords)
    
    # 提取英文關鍵字
    english_keywords = re.findall(r'[A-Za-z]+', clean_name)
    keywords.extend(english_keywords)
    
    # 提取數字（可能代表規格）
    numbers = re.findall(r'\d+', clean_name)
    if numbers:
        keywords.append("規格")
    
    return keywords

def generate_keywords_from_analysis(keyword_counter, folder_categories):
    """基於分析結果生成搜尋關鍵字"""
    suggested = []
    
    # 基於資料夾分類生成關鍵字
    category_keywords = {
        "沖壓相關": [
            "沖壓工廠", "沖壓廠", "金屬沖壓", "精密沖壓", "裁切廠",
            "沖壓加工", "金屬加工", "精密加工", "機械加工"
        ],
        "電線電纜相關": [
            "電線電纜廠", "電纜廠", "電線廠", "電纜製造", "電線製造",
            "家電拆解", "廢電線回收", "電線回收"
        ],
        "機電工程": [
            "機電公司", "廠房拆解", "工程行", "機械公司", "精密機械"
        ],
        "汽車相關": [
            "汽車拆解廠", "汽車回收", "廢車回收", "汽車零件"
        ],
        "貿易商": [
            "貿易商", "中盤商", "古物商", "回收商", "廢料回收"
        ],
        "公家機關": [
            "政府機關", "公家機關", "政府採購", "標案"
        ]
    }
    
    # 添加分類關鍵字
    for category, companies in folder_categories.items():
        if category in category_keywords:
            suggested.extend(category_keywords[category])
    
    # 添加高頻公司名稱關鍵字
    for keyword, count in keyword_counter.most_common(10):
        if len(keyword) >= 2 and keyword not in suggested:
            suggested.append(keyword)
    
    # 添加一些通用的關鍵字
    general_keywords = [
        "銅加工", "銅製品", "銅材加工", "銅管製造",
        "廢銅回收", "廢金屬回收", "金屬回收",
        "五金加工", "金屬加工", "機械加工",
        "廢料回收", "資源回收", "環保回收"
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
    analyze_customer_folders() 