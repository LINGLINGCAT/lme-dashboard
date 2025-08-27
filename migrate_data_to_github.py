#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據遷移腳本
將現有的歷史數據整合到新的 DATA.xlsx 文件中，準備上傳到 GitHub
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import glob
import os

def find_existing_data_files():
    """查找現有的數據文件"""
    data_dir = Path("data")
    existing_files = []
    
    # 查找所有可能的數據文件
    patterns = [
        "*.csv",
        "*.xlsx", 
        "*.xls",
        "lme_*.csv",
        "lme_*.xlsx",
        "csp_*.csv",
        "csp_*.xlsx",
        "historical_*.csv",
        "historical_*.xlsx"
    ]
    
    for pattern in patterns:
        files = list(data_dir.glob(pattern))
        existing_files.extend(files)
    
    # 去重
    existing_files = list(set(existing_files))
    
    return existing_files

def load_existing_data():
    """載入現有的歷史數據"""
    print("🔍 查找現有數據文件...")
    
    existing_files = find_existing_data_files()
    
    if not existing_files:
        print("⚠️ 沒有找到現有數據文件")
        return None, None
    
    print(f"📁 找到 {len(existing_files)} 個數據文件：")
    for file in existing_files:
        print(f"   - {file}")
    
    # 嘗試載入數據
    all_3m_data = []
    all_csp_data = []
    
    for file_path in existing_files:
        try:
            print(f"\n📊 處理文件：{file_path}")
            
            # 根據文件類型載入
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            print(f"   ✅ 載入成功：{len(df)} 行，{len(df.columns)} 欄位")
            print(f"   📋 欄位：{list(df.columns)}")
            
            # 分析數據類型並分類
            if is_3m_data(df):
                all_3m_data.append(df)
                print(f"   🏷️ 分類為：3M 數據")
            elif is_csp_data(df):
                all_csp_data.append(df)
                print(f"   🏷️ 分類為：CSP 數據")
            else:
                print(f"   ⚠️ 無法分類，跳過")
                
        except Exception as e:
            print(f"   ❌ 載入失敗：{e}")
    
    return all_3m_data, all_csp_data

def is_3m_data(df):
    """判斷是否為 3M 數據"""
    if df is None or df.empty:
        return False
    
    # 檢查欄位名稱
    columns = [col.lower() for col in df.columns]
    
    # 3M 數據的特徵
    three_m_indicators = ['3m', '銅', '鋁', '鋅', '錫', '鎳', '鉛', 'copper', 'aluminum', 'zinc', 'tin', 'nickel', 'lead']
    
    for indicator in three_m_indicators:
        if any(indicator in col for col in columns):
            return True
    
    return False

def is_csp_data(df):
    """判斷是否為 CSP 數據"""
    if df is None or df.empty:
        return False
    
    # 檢查欄位名稱
    columns = [col.lower() for col in df.columns]
    
    # CSP 數據的特徵
    csp_indicators = ['csp', '磷', '青', '紅', '黃', '白', 'phosphorus']
    
    for indicator in csp_indicators:
        if any(indicator in col for col in columns):
            return True
    
    return False

def merge_dataframes(dataframes, data_type):
    """合併多個 DataFrame"""
    if not dataframes:
        return None
    
    if len(dataframes) == 1:
        return dataframes[0]
    
    print(f"🔄 合併 {len(dataframes)} 個 {data_type} 數據文件...")
    
    # 嘗試合併
    try:
        merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
        
        # 去重（基於日期）
        date_columns = [col for col in merged_df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        if date_columns:
            merged_df = merged_df.drop_duplicates(subset=date_columns[0])
            print(f"   ✅ 去重後：{len(merged_df)} 行")
        
        return merged_df
        
    except Exception as e:
        print(f"   ❌ 合併失敗：{e}")
        return dataframes[0]  # 返回第一個文件

def create_standardized_data():
    """創建標準化的數據文件"""
    print("\n🚀 開始數據遷移...")
    
    # 載入現有數據
    all_3m_data, all_csp_data = load_existing_data()
    
    # 合併數據
    df_3m = merge_dataframes(all_3m_data, "3M") if all_3m_data else None
    df_csp = merge_dataframes(all_csp_data, "CSP") if all_csp_data else None
    
    # 如果沒有現有數據，創建示例數據
    if df_3m is None and df_csp is None:
        print("📝 沒有找到現有數據，創建示例數據...")
        df_3m, df_csp = create_sample_data()
    
    # 標準化數據格式
    df_3m = standardize_3m_data(df_3m)
    df_csp = standardize_csp_data(df_csp)
    
    return df_3m, df_csp

def standardize_3m_data(df):
    """標準化 3M 數據格式"""
    if df is None or df.empty:
        return create_sample_3m_data()
    
    print("🔧 標準化 3M 數據格式...")
    
    # 確保有日期欄位
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if not date_columns:
        print("   ⚠️ 沒有找到日期欄位，使用索引作為日期")
        df['日期'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
    else:
        # 確保日期格式正確
        df[date_columns[0]] = pd.to_datetime(df[date_columns[0]], errors='coerce')
        df = df.rename(columns={date_columns[0]: '日期'})
    
    # 標準化價格欄位名稱
    price_columns = [col for col in df.columns if col != '日期']
    new_columns = ['日期']
    
    for col in price_columns:
        if any(keyword in col.lower() for keyword in ['銅', 'copper']):
            new_columns.append('銅_3M')
        elif any(keyword in col.lower() for keyword in ['鋁', 'aluminum']):
            new_columns.append('鋁_3M')
        elif any(keyword in col.lower() for keyword in ['鋅', 'zinc']):
            new_columns.append('鋅_3M')
        elif any(keyword in col.lower() for keyword in ['錫', 'tin']):
            new_columns.append('錫_3M')
        elif any(keyword in col.lower() for keyword in ['鎳', 'nickel']):
            new_columns.append('鎳_3M')
        elif any(keyword in col.lower() for keyword in ['鉛', 'lead']):
            new_columns.append('鉛_3M')
        else:
            new_columns.append(col)
    
    df.columns = new_columns
    
    # 清理數據
    df = df.dropna(subset=['日期'])
    df = df.sort_values('日期')
    
    print(f"   ✅ 標準化完成：{len(df)} 行，{len(df.columns)} 欄位")
    return df

def standardize_csp_data(df):
    """標準化 CSP 數據格式"""
    if df is None or df.empty:
        return create_sample_csp_data()
    
    print("🔧 標準化 CSP 數據格式...")
    
    # 確保有日期欄位
    date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
    if not date_columns:
        print("   ⚠️ 沒有找到日期欄位，使用索引作為日期")
        df['日期'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
    else:
        # 確保日期格式正確
        df[date_columns[0]] = pd.to_datetime(df[date_columns[0]], errors='coerce')
        df = df.rename(columns={date_columns[0]: '日期'})
    
    # 標準化價格欄位名稱
    price_columns = [col for col in df.columns if col != '日期']
    new_columns = ['日期']
    
    for col in price_columns:
        if any(keyword in col.lower() for keyword in ['磷', 'phosphorus']):
            new_columns.append('CSP磷')
        elif any(keyword in col.lower() for keyword in ['青', 'blue']):
            new_columns.append('CSP青')
        elif any(keyword in col.lower() for keyword in ['紅', 'red']):
            new_columns.append('CSP紅')
        elif any(keyword in col.lower() for keyword in ['黃', 'yellow']):
            new_columns.append('CSP黃')
        elif any(keyword in col.lower() for keyword in ['白', 'white']):
            new_columns.append('CSP白')
        else:
            new_columns.append(col)
    
    df.columns = new_columns
    
    # 清理數據
    df = df.dropna(subset=['日期'])
    df = df.sort_values('日期')
    
    print(f"   ✅ 標準化完成：{len(df)} 行，{len(df.columns)} 欄位")
    return df

def create_sample_3m_data():
    """創建示例 3M 數據"""
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    
    data = {
        '日期': dates,
        '銅_3M': np.random.normal(8500, 200, len(dates)),
        '鋁_3M': np.random.normal(2200, 50, len(dates)),
        '鋅_3M': np.random.normal(2800, 80, len(dates)),
        '錫_3M': np.random.normal(25000, 500, len(dates)),
        '鎳_3M': np.random.normal(18000, 400, len(dates)),
        '鉛_3M': np.random.normal(2000, 60, len(dates))
    }
    
    return pd.DataFrame(data)

def create_sample_csp_data():
    """創建示例 CSP 數據"""
    dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
    
    data = {
        '日期': dates,
        'CSP磷': np.random.normal(2500, 100, len(dates)),
        'CSP青': np.random.normal(2800, 120, len(dates)),
        'CSP紅': np.random.normal(3200, 150, len(dates)),
        'CSP黃': np.random.normal(3000, 130, len(dates)),
        'CSP白': np.random.normal(2600, 110, len(dates))
    }
    
    return pd.DataFrame(data)

def create_sample_data():
    """創建示例數據"""
    return create_sample_3m_data(), create_sample_csp_data()

def save_to_github_format():
    """保存為 GitHub 格式的數據文件"""
    print("\n💾 保存數據文件...")
    
    # 創建標準化數據
    df_3m, df_csp = create_standardized_data()
    
    # 保存到 data/DATA.xlsx
    output_path = Path("data/DATA.xlsx")
    output_path.parent.mkdir(exist_ok=True)
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_3m.to_excel(writer, sheet_name='3M', index=False)
            df_csp.to_excel(writer, sheet_name='CSP', index=False)
        
        print(f"✅ 數據已保存到：{output_path}")
        print(f"📊 3M 數據：{len(df_3m)} 行，{len(df_3m.columns)} 欄位")
        print(f"📊 CSP 數據：{len(df_csp)} 行，{len(df_csp.columns)} 欄位")
        
        # 顯示數據統計
        print(f"\n📈 數據統計：")
        print(f"   3M 時間範圍：{df_3m['日期'].min().strftime('%Y-%m-%d')} 至 {df_3m['日期'].max().strftime('%Y-%m-%d')}")
        print(f"   CSP 時間範圍：{df_csp['日期'].min().strftime('%Y-%m-%d')} 至 {df_csp['日期'].max().strftime('%Y-%m-%d')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存失敗：{e}")
        return False

def main():
    """主函數"""
    print("🚀 LME Dashboard 數據遷移工具")
    print("=" * 50)
    print("📋 功能：將現有數據整合並準備上傳到 GitHub")
    print("=" * 50)
    
    # 執行數據遷移
    success = save_to_github_format()
    
    if success:
        print("\n🎉 數據遷移完成！")
        print("📝 下一步：")
        print("   1. 檢查 data/DATA.xlsx 文件")
        print("   2. 提交到 Git：git add data/DATA.xlsx")
        print("   3. 推送到 GitHub：git push origin main")
        print("   4. 部署到 Streamlit Cloud")
    else:
        print("\n❌ 數據遷移失敗，請檢查錯誤信息")

if __name__ == "__main__":
    main()
