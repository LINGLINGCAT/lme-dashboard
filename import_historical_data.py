#!/usr/bin/env python3
"""
LME 歷史數據導入工具
將 LME.xlsm 文件中的 3M RECORD 分頁數據導入到 data 目錄
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

def find_lme_file():
    """尋找 LME.xlsm 文件"""
    print("🔍 尋找 LME.xlsm 文件...")
    
    possible_paths = [
        Path("Z:/LME.xlsm"),
        Path("Z:/LME/LME.xlsm"),
        Path("D:/LME.xlsm"),
        Path("D:/LME/LME.xlsm"),
        Path("C:/LME.xlsm"),
        Path("C:/LME/LME.xlsm"),
        Path("LME.xlsm"),
        Path("data/LME.xlsm")
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ 找到 LME 文件：{path}")
            return path
    
    print("❌ 找不到 LME.xlsm 文件")
    print("請將 LME.xlsm 文件放在以下位置之一：")
    for path in possible_paths:
        print(f"   - {path}")
    return None

def load_lme_data(file_path):
    """載入 LME.xlsm 文件中的 3M RECORD 分頁"""
    print(f"📊 載入 LME 數據：{file_path}")
    
    try:
        # 嘗試載入 3M RECORD 分頁
        df = pd.read_excel(file_path, sheet_name="3M RECORD")
        print(f"✅ 成功載入 3M RECORD 分頁，共 {len(df)} 行數據")
        print(f"📋 欄位：{list(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ 載入 3M RECORD 分頁失敗：{e}")
        
        # 嘗試其他可能的分頁名稱
        try:
            excel_file = pd.ExcelFile(file_path)
            print(f"📋 可用的分頁：{excel_file.sheet_names}")
            
            # 尋找包含 "3M" 或 "RECORD" 的分頁
            for sheet_name in excel_file.sheet_names:
                if "3M" in sheet_name.upper() or "RECORD" in sheet_name.upper():
                    print(f"🔄 嘗試載入分頁：{sheet_name}")
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    print(f"✅ 成功載入分頁 {sheet_name}，共 {len(df)} 行數據")
                    return df
            
            # 如果沒有找到，載入第一個分頁
            first_sheet = excel_file.sheet_names[0]
            print(f"🔄 載入第一個分頁：{first_sheet}")
            df = pd.read_excel(file_path, sheet_name=first_sheet)
            print(f"✅ 成功載入分頁 {first_sheet}，共 {len(df)} 行數據")
            return df
            
        except Exception as e2:
            print(f"❌ 載入 Excel 文件失敗：{e2}")
            return None

def clean_and_transform_data(df):
    """清理和轉換數據格式"""
    print("🧹 清理和轉換數據...")
    
    # 顯示原始數據的前幾行
    print("📋 原始數據前5行：")
    print(df.head())
    
    # 尋找日期欄位
    date_columns = []
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['date', '日期', '時間', 'time']):
            date_columns.append(col)
    
    if date_columns:
        print(f"📅 找到日期欄位：{date_columns}")
        date_col = date_columns[0]
    else:
        # 如果沒有找到日期欄位，假設第一欄是日期
        date_col = df.columns[0]
        print(f"📅 使用第一欄作為日期：{date_col}")
    
    # 尋找價格欄位
    price_columns = []
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['price', '價格', 'csp', '磷', '青', '紅', '銅', '鋁']):
            price_columns.append(col)
    
    print(f"💰 找到價格欄位：{price_columns}")
    
    # 創建標準化的數據結構
    cleaned_data = []
    
    for idx, row in df.iterrows():
        try:
            # 處理日期
            if pd.isna(row[date_col]):
                continue
                
            if isinstance(row[date_col], str):
                date = pd.to_datetime(row[date_col])
            else:
                date = pd.to_datetime(row[date_col])
            
            # 處理價格數據
            for price_col in price_columns:
                if pd.notna(row[price_col]) and row[price_col] != '':
                    price_value = row[price_col]
                    
                    # 清理價格數據
                    if isinstance(price_value, str):
                        # 移除貨幣符號和逗號
                        price_value = str(price_value).replace('NT$', '').replace('US$', '').replace('$', '').replace(',', '').strip()
                    
                    try:
                        price = float(price_value)
                        if price > 0:  # 確保價格有效
                            cleaned_data.append({
                                '日期': date,
                                '品項': price_col,
                                '價格': price,
                                '幣值': 'TWD' if 'NT$' in str(row[price_col]) else 'USD',
                                '來源': 'LME_歷史數據'
                            })
                    except (ValueError, TypeError):
                        continue
                        
        except Exception as e:
            print(f"⚠️ 處理第 {idx} 行時出錯：{e}")
            continue
    
    result_df = pd.DataFrame(cleaned_data)
    print(f"✅ 清理完成，共 {len(result_df)} 筆有效數據")
    
    if not result_df.empty:
        print("📊 數據統計：")
        print(result_df.groupby('品項')['價格'].agg(['count', 'mean', 'min', 'max']))
    
    return result_df

def save_to_data_directory(df, original_file_path):
    """保存數據到 data 目錄"""
    print("💾 保存數據到 data 目錄...")
    
    # 創建 data 目錄
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = Path(original_file_path).stem
    
    # 保存為 CSV
    csv_path = data_dir / f"lme_historical_data_{timestamp}.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 已保存到：{csv_path}")
    
    # 保存為 Excel
    excel_path = data_dir / f"lme_historical_data_{timestamp}.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"✅ 已保存到：{excel_path}")
    
    # 更新主歷史文件
    main_history_path = data_dir / "csp_history.csv"
    
    # 如果主歷史文件存在，合併數據
    if main_history_path.exists():
        try:
            existing_df = pd.read_csv(main_history_path)
            print(f"📊 現有歷史數據：{len(existing_df)} 筆")
            
            # 合併數據，避免重複
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['日期', '品項'], keep='last')
            combined_df = combined_df.sort_values('日期')
            
            combined_df.to_csv(main_history_path, index=False, encoding='utf-8-sig')
            print(f"✅ 已更新主歷史文件：{main_history_path}")
            print(f"📊 合併後總數據：{len(combined_df)} 筆")
            
        except Exception as e:
            print(f"⚠️ 合併現有數據失敗：{e}")
            # 如果合併失敗，直接覆蓋
            df.to_csv(main_history_path, index=False, encoding='utf-8-sig')
            print(f"✅ 已創建新的主歷史文件：{main_history_path}")
    else:
        # 如果主歷史文件不存在，創建新的
        df.to_csv(main_history_path, index=False, encoding='utf-8-sig')
        print(f"✅ 已創建主歷史文件：{main_history_path}")
    
    return main_history_path

def create_auto_record_schedule():
    """創建自動記錄時間表"""
    print("⏰ 設置自動記錄時間表...")
    
    schedule_content = """
# LME 數據自動記錄時間表
# 每天早上 9:00 和下午 17:00 自動記錄數據

import schedule
import time
from datetime import datetime
import pandas as pd
from pathlib import Path

def record_lme_data():
    \"\"\"記錄 LME 數據\"\"\"
    try:
        # 這裡可以添加從 LME 即時看板獲取數據的邏輯
        # 目前先記錄時間戳
        timestamp = datetime.now()
        data = {
            '日期': timestamp,
            '品項': '自動記錄',
            '價格': 0,
            '幣值': 'TWD',
            '來源': '自動記錄'
        }
        
        # 保存到歷史文件
        history_path = Path("data/csp_history.csv")
        if history_path.exists():
            df = pd.read_csv(history_path)
            new_df = pd.DataFrame([data])
            combined_df = pd.concat([df, new_df], ignore_index=True)
            combined_df.to_csv(history_path, index=False, encoding='utf-8-sig')
            print(f"✅ {timestamp} - 數據已記錄")
        else:
            print("⚠️ 歷史文件不存在")
            
    except Exception as e:
        print(f"❌ 記錄數據失敗：{e}")

# 設置定時任務
schedule.every().day.at("09:00").do(record_lme_data)
schedule.every().day.at("17:00").do(record_lme_data)

print("⏰ 自動記錄已設置：每天 09:00 和 17:00")
print("按 Ctrl+C 停止")

# 運行定時任務
while True:
    schedule.run_pending()
    time.sleep(60)
"""
    
    schedule_path = Path("auto_record_lme.py")
    with open(schedule_path, 'w', encoding='utf-8') as f:
        f.write(schedule_content)
    
    print(f"✅ 已創建自動記錄腳本：{schedule_path}")
    print("🚀 運行方式：python auto_record_lme.py")

def main():
    """主函數"""
    print("📊 LME 歷史數據導入工具")
    print("=" * 50)
    
    # 1. 尋找 LME 文件
    lme_file = find_lme_file()
    if not lme_file:
        return
    
    # 2. 載入數據
    df = load_lme_data(lme_file)
    if df is None:
        return
    
    # 3. 清理和轉換數據
    cleaned_df = clean_and_transform_data(df)
    if cleaned_df.empty:
        print("❌ 沒有有效的數據可以導入")
        return
    
    # 4. 保存到 data 目錄
    history_path = save_to_data_directory(cleaned_df, lme_file)
    
    # 5. 創建自動記錄時間表
    create_auto_record_schedule()
    
    print("\n🎉 數據導入完成！")
    print("\n📋 後續步驟：")
    print("1. 檢查 data 目錄中的文件")
    print("2. 運行自動記錄腳本：python auto_record_lme.py")
    print("3. 在數據分析頁面查看導入的數據")
    
    print(f"\n📁 數據文件位置：{history_path}")

if __name__ == "__main__":
    main()

