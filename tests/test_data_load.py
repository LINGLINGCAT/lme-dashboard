#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試數據載入功能
"""

import pandas as pd
from pathlib import Path

def test_data_loading():
    """測試數據載入功能"""
    print("🧪 測試數據載入功能")
    print("=" * 50)
    
    # 檢查本地數據文件
    local_data_paths = [
        Path("data/lme_updated_data.csv"),  # 優先載入包含完整資料的文件
        Path("data/lme_updated_data.xlsx"),
        Path("data/csp_history.csv"),
        Path("data/csp_history.xlsx"),
        Path("data/lme_historical_data.csv"),
        Path("data/lme_historical_data.xlsx"),
        Path("data/lme_prices.csv"),
        Path("data/historical_data.csv")
    ]
    
    print("📁 檢查本地數據文件：")
    for path in local_data_paths:
        if path.exists():
            print(f"✅ 文件存在：{path}")
            try:
                if path.suffix == '.csv':
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)
                
                if not df.empty:
                    print(f"   📊 數據統計：{len(df)} 行，{len(df.columns)} 欄位")
                    print(f"   📋 欄位：{list(df.columns)}")
                    
                    # 檢查是否包含我們需要的產品
                    if '品項' in df.columns:
                        products = df['品項'].unique()
                        print(f"   🏷️ 產品：{list(products)}")
                    else:
                        # 寬格式數據
                        price_cols = [col for col in df.columns if col != '日期']
                        print(f"   🏷️ 價格欄位：{price_cols}")
                    
                    return df
                else:
                    print(f"   ⚠️ 文件為空")
            except Exception as e:
                print(f"   ❌ 載入失敗：{e}")
        else:
            print(f"❌ 文件不存在：{path}")
    
    print("\n❌ 沒有找到可用的數據文件")
    return None

if __name__ == "__main__":
    df = test_data_loading()
    if df is not None:
        print(f"\n✅ 成功載入數據！")
    else:
        print(f"\n❌ 數據載入失敗")
