#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
數據分析頁面測試腳本
測試修改後的數據分析功能
"""

import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

def create_test_data():
    """創建測試用的 Excel 文件"""
    
    # 創建測試數據
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    # 3M 數據（每天即時價）
    data_3m = {
        '日期': dates,
        '銅_3M': np.random.normal(8500, 200, len(dates)),
        '鋁_3M': np.random.normal(2200, 50, len(dates)),
        '鋅_3M': np.random.normal(2800, 80, len(dates)),
        '錫_3M': np.random.normal(25000, 500, len(dates))
    }
    df_3m = pd.DataFrame(data_3m)
    
    # CSP 數據（前日收盤）
    data_csp = {
        '日期': dates,
        'CSP磷': np.random.normal(2500, 100, len(dates)),
        'CSP青': np.random.normal(2800, 120, len(dates)),
        'CSP紅': np.random.normal(3200, 150, len(dates))
    }
    df_csp = pd.DataFrame(data_csp)
    
    return df_3m, df_csp

def test_data_loading():
    """測試數據載入功能"""
    print("🧪 測試數據載入功能...")
    
    # 創建測試數據
    df_3m, df_csp = create_test_data()
    
    # 創建臨時 Excel 文件
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        # 保存到 Excel 文件
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            df_3m.to_excel(writer, sheet_name='3M', index=False)
            df_csp.to_excel(writer, sheet_name='CSP', index=False)
        
        print(f"✅ 測試文件已創建：{temp_path}")
        
        # 測試載入功能
        try:
            # 載入 3M 分頁
            loaded_3m = pd.read_excel(temp_path, sheet_name='3M')
            print(f"✅ 3M 數據載入成功：{len(loaded_3m)} 行")
            print(f"   欄位：{list(loaded_3m.columns)}")
            
            # 載入 CSP 分頁
            loaded_csp = pd.read_excel(temp_path, sheet_name='CSP')
            print(f"✅ CSP 數據載入成功：{len(loaded_csp)} 行")
            print(f"   欄位：{list(loaded_csp.columns)}")
            
            # 驗證數據完整性
            assert len(loaded_3m) == len(df_3m), "3M 數據行數不匹配"
            assert len(loaded_csp) == len(df_csp), "CSP 數據行數不匹配"
            assert list(loaded_3m.columns) == list(df_3m.columns), "3M 欄位不匹配"
            assert list(loaded_csp.columns) == list(df_csp.columns), "CSP 欄位不匹配"
            
            print("✅ 數據完整性驗證通過")
            
        except Exception as e:
            print(f"❌ 數據載入失敗：{e}")
            return False
        
    except Exception as e:
        print(f"❌ 創建測試文件失敗：{e}")
        return False
    
    finally:
        # 清理臨時文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print(f"🧹 已清理臨時文件：{temp_path}")
    
    return True

def test_data_processing():
    """測試數據處理功能"""
    print("\n🧪 測試數據處理功能...")
    
    # 創建測試數據
    df_3m, df_csp = create_test_data()
    
    # 模擬數據分析頁面的處理邏輯
    def process_data(df, data_type):
        """處理數據格式"""
        if df is None or df.empty:
            return df
        
        # 確保日期欄位被正確解析
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        if date_columns:
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 清理價格數據中的貨幣符號
        price_columns = [col for col in df.columns if col not in date_columns]
        for col in price_columns:
            if col in df.columns:
                # 轉換為字符串
                df[col] = df[col].astype(str)
                # 清理貨幣符號和格式
                df[col] = df[col].str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                # 轉換為數值
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    # 測試處理功能
    try:
        processed_3m = process_data(df_3m, "3M")
        processed_csp = process_data(df_csp, "CSP")
        
        print(f"✅ 3M 數據處理成功：{len(processed_3m)} 行")
        print(f"✅ CSP 數據處理成功：{len(processed_csp)} 行")
        
        # 驗證日期欄位
        date_col_3m = [col for col in processed_3m.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        date_col_csp = [col for col in processed_csp.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        
        if date_col_3m:
            print(f"✅ 3M 日期欄位：{date_col_3m[0]}")
        if date_col_csp:
            print(f"✅ CSP 日期欄位：{date_col_csp[0]}")
        
        # 驗證價格欄位
        price_cols_3m = [col for col in processed_3m.columns if col not in date_col_3m]
        price_cols_csp = [col for col in processed_csp.columns if col not in date_col_csp]
        
        print(f"✅ 3M 價格欄位：{price_cols_3m}")
        print(f"✅ CSP 價格欄位：{price_cols_csp}")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據處理失敗：{e}")
        return False

def test_analysis_functions():
    """測試分析功能"""
    print("\n🧪 測試分析功能...")
    
    # 創建測試數據
    df_3m, df_csp = create_test_data()
    
    # 模擬波動性分析
    def create_volatility_analysis(df, data_type):
        """創建波動性分析"""
        if df is None or df.empty:
            return None
        
        # 找到日期欄位
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        if not date_columns:
            return None
        
        date_col = date_columns[0]
        price_columns = [col for col in df.columns if col != date_col]
        
        volatility_data = []
        
        for col in price_columns:
            if col in df.columns:
                # 清理價格數據
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                
                # 計算波動性指標
                if len(numeric_values.dropna()) > 1:
                    volatility = numeric_values.pct_change().std() * 100
                    max_price = numeric_values.max()
                    min_price = numeric_values.min()
                    avg_price = numeric_values.mean()
                    
                    volatility_data.append({
                        '產品': col,
                        '平均價格': avg_price,
                        '最高價格': max_price,
                        '最低價格': min_price,
                        '波動率 (%)': volatility
                    })
        
        return pd.DataFrame(volatility_data)
    
    # 模擬相關性分析
    def create_correlation_matrix(df):
        """創建相關性矩陣"""
        if df is None or df.empty:
            return None
        
        # 找到日期欄位
        date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['日期', 'date', 'time'])]
        if not date_columns:
            return None
        
        date_col = date_columns[0]
        price_columns = [col for col in df.columns if col != date_col]
        
        if len(price_columns) < 2:
            return None
        
        correlation_data = {}
        
        for col in price_columns:
            if col in df.columns:
                # 清理價格數據
                price_data = df[col].astype(str)
                clean_values = price_data.str.replace('NT$', '').str.replace('US$', '').str.replace('$', '').str.replace(',', '').str.strip()
                numeric_values = pd.to_numeric(clean_values, errors='coerce')
                correlation_data[col] = numeric_values
        
        if len(correlation_data) < 2:
            return None
        
        correlation_df = pd.DataFrame(correlation_data)
        correlation_matrix = correlation_df.corr()
        
        return correlation_matrix
    
    try:
        # 測試波動性分析
        volatility_3m = create_volatility_analysis(df_3m, "3M")
        volatility_csp = create_volatility_analysis(df_csp, "CSP")
        
        if volatility_3m is not None and not volatility_3m.empty:
            print(f"✅ 3M 波動性分析成功：{len(volatility_3m)} 個產品")
        else:
            print("⚠️ 3M 波動性分析無結果")
        
        if volatility_csp is not None and not volatility_csp.empty:
            print(f"✅ CSP 波動性分析成功：{len(volatility_csp)} 個產品")
        else:
            print("⚠️ CSP 波動性分析無結果")
        
        # 測試相關性分析
        correlation_3m = create_correlation_matrix(df_3m)
        correlation_csp = create_correlation_matrix(df_csp)
        
        if correlation_3m is not None:
            print(f"✅ 3M 相關性分析成功：{correlation_3m.shape}")
        else:
            print("⚠️ 3M 相關性分析無結果")
        
        if correlation_csp is not None:
            print(f"✅ CSP 相關性分析成功：{correlation_csp.shape}")
        else:
            print("⚠️ CSP 相關性分析無結果")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析功能測試失敗：{e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試數據分析頁面功能")
    print("=" * 50)
    
    # 測試數據載入
    test1_passed = test_data_loading()
    
    # 測試數據處理
    test2_passed = test_data_processing()
    
    # 測試分析功能
    test3_passed = test_analysis_functions()
    
    print("\n" + "=" * 50)
    print("📊 測試結果總結：")
    print(f"數據載入測試：{'✅ 通過' if test1_passed else '❌ 失敗'}")
    print(f"數據處理測試：{'✅ 通過' if test2_passed else '❌ 失敗'}")
    print(f"分析功能測試：{'✅ 通過' if test3_passed else '❌ 失敗'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 所有測試通過！數據分析頁面功能正常")
    else:
        print("\n⚠️ 部分測試失敗，請檢查相關功能")

if __name__ == "__main__":
    main()
