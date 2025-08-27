#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建示例數據文件
生成符合數據分析頁面要求的 Z:/DATA.xlsx 文件
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def create_sample_data():
    """創建示例數據"""
    
    # 生成日期範圍（過去一年的數據）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # 3M 數據（每天即時價）
    np.random.seed(42)  # 確保可重現性
    data_3m = {
        '日期': dates,
        '銅_3M': np.random.normal(8500, 200, len(dates)),
        '鋁_3M': np.random.normal(2200, 50, len(dates)),
        '鋅_3M': np.random.normal(2800, 80, len(dates)),
        '錫_3M': np.random.normal(25000, 500, len(dates)),
        '鎳_3M': np.random.normal(18000, 400, len(dates)),
        '鉛_3M': np.random.normal(2000, 60, len(dates))
    }
    df_3m = pd.DataFrame(data_3m)
    
    # CSP 數據（前日收盤）
    data_csp = {
        '日期': dates,
        'CSP磷': np.random.normal(2500, 100, len(dates)),
        'CSP青': np.random.normal(2800, 120, len(dates)),
        'CSP紅': np.random.normal(3200, 150, len(dates)),
        'CSP黃': np.random.normal(3000, 130, len(dates)),
        'CSP白': np.random.normal(2600, 110, len(dates))
    }
    df_csp = pd.DataFrame(data_csp)
    
    return df_3m, df_csp

def save_sample_data():
    """保存示例數據到 Z:/DATA.xlsx"""
    
    # 創建數據
    df_3m, df_csp = create_sample_data()
    
    # 設定文件路徑
    file_path = Path("Z:/DATA.xlsx")
    
    try:
        # 確保目錄存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存到 Excel 文件
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_3m.to_excel(writer, sheet_name='3M', index=False)
            df_csp.to_excel(writer, sheet_name='CSP', index=False)
        
        print(f"✅ 示例數據已保存到：{file_path}")
        print(f"📊 3M 數據：{len(df_3m)} 行，{len(df_3m.columns)} 欄位")
        print(f"📊 CSP 數據：{len(df_csp)} 行，{len(df_csp.columns)} 欄位")
        print(f"📅 數據時間範圍：{df_3m['日期'].min().strftime('%Y-%m-%d')} 至 {df_3m['日期'].max().strftime('%Y-%m-%d')}")
        
        # 顯示欄位資訊
        print("\n📋 3M 欄位：")
        for col in df_3m.columns:
            print(f"  - {col}")
        
        print("\n📋 CSP 欄位：")
        for col in df_csp.columns:
            print(f"  - {col}")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存失敗：{e}")
        print("💡 請確認 Z: 磁碟機可訪問，或修改路徑")
        return False

def create_local_backup():
    """創建本地備份文件"""
    
    # 創建數據
    df_3m, df_csp = create_sample_data()
    
    # 設定本地備份路徑
    backup_path = Path("data/DATA.xlsx")
    
    try:
        # 確保目錄存在
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存到本地備份
        with pd.ExcelWriter(backup_path, engine='openpyxl') as writer:
            df_3m.to_excel(writer, sheet_name='3M', index=False)
            df_csp.to_excel(writer, sheet_name='CSP', index=False)
        
        print(f"✅ 本地備份已保存到：{backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ 本地備份失敗：{e}")
        return False

def main():
    """主函數"""
    print("🚀 創建示例數據文件")
    print("=" * 50)
    
    # 嘗試保存到 Z: 磁碟機
    success_cloud = save_sample_data()
    
    # 創建本地備份
    success_local = create_local_backup()
    
    print("\n" + "=" * 50)
    print("📊 創建結果：")
    print(f"雲端文件：{'✅ 成功' if success_cloud else '❌ 失敗'}")
    print(f"本地備份：{'✅ 成功' if success_local else '❌ 失敗'}")
    
    if success_cloud or success_local:
        print("\n🎉 示例數據創建完成！")
        print("💡 現在可以測試數據分析頁面功能")
        
        if not success_cloud:
            print("⚠️ 注意：雲端文件創建失敗，請檢查 Z: 磁碟機權限")
            print("💡 可以使用本地備份文件進行測試")
    else:
        print("\n❌ 數據創建失敗，請檢查權限和路徑")

if __name__ == "__main__":
    main()
