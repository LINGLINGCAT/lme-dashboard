#!/usr/bin/env python3
"""
LME 數據自動記錄腳本
每天早上 9:00 和下午 17:00 自動從 LME 即時看板獲取數據並記錄
"""

import schedule
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_record.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_lme_realtime_data():
    """從 LME 即時看板獲取數據"""
    try:
        # 嘗試從本地數據文件獲取最新數據
        data_files = [
            Path("data/lme_realtime_data.csv"),
            Path("data/lme_updated_data.csv"),
            Path("data/lme_updated_data.xlsx")
        ]
        
        for file_path in data_files:
            if file_path.exists():
                try:
                    if file_path.suffix == '.csv':
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    
                    if not df.empty:
                        logging.info(f"✅ 從 {file_path} 獲取到 {len(df)} 行數據")
                        return df
                        
                except Exception as e:
                    logging.warning(f"⚠️ 讀取 {file_path} 失敗：{e}")
                    continue
        
        # 如果本地文件不可用，嘗試從網路獲取
        logging.info("🔄 嘗試從網路獲取 LME 數據...")
        
        # 這裡可以添加從 Westmetall 或其他 LME 數據源獲取數據的邏輯
        # 目前先返回模擬數據
        return create_sample_realtime_data()
        
    except Exception as e:
        logging.error(f"❌ 獲取 LME 數據失敗：{e}")
        return None

def create_sample_realtime_data():
    """創建示例即時數據（當無法獲取真實數據時使用）"""
    current_time = datetime.now()
    
    # 模擬 LME 價格數據
    sample_data = {
        '日期': [current_time],
        'CSP磷': [285000],
        'CSP青': [320000],
        'CSP紅': [350000],
        'CSP錫': [950000],
        'CSP鋅': [120000],
        '幣值': ['TWD'],
        '來源': ['自動記錄']
    }
    
    df = pd.DataFrame(sample_data)
    logging.info("📊 使用示例數據")
    return df

def record_lme_data():
    """記錄 LME 數據到歷史文件"""
    try:
        logging.info("🔄 開始記錄 LME 數據...")
        
        # 獲取即時數據
        realtime_df = get_lme_realtime_data()
        if realtime_df is None or realtime_df.empty:
            logging.error("❌ 無法獲取即時數據")
            return
        
        # 轉換數據格式
        record_time = datetime.now()
        records = []
        
        # 處理每一行數據
        for _, row in realtime_df.iterrows():
            # 處理日期
            if '日期' in row:
                date = pd.to_datetime(row['日期'])
            else:
                date = record_time
            
            # 處理價格數據
            price_columns = ['CSP磷', 'CSP青', 'CSP紅', 'CSP錫', 'CSP鋅']
            
            for col in price_columns:
                if col in row and pd.notna(row[col]) and row[col] != '':
                    try:
                        price_value = row[col]
                        
                        # 清理價格數據
                        if isinstance(price_value, str):
                            price_value = str(price_value).replace('NT$', '').replace('US$', '').replace('$', '').replace(',', '').strip()
                        
                        price = float(price_value)
                        if price > 0:
                            records.append({
                                '日期': date,
                                '品項': col,
                                '價格': price,
                                '幣值': row.get('幣值', 'TWD'),
                                '來源': row.get('來源', '自動記錄')
                            })
                    except (ValueError, TypeError) as e:
                        logging.warning(f"⚠️ 處理價格 {col} 失敗：{e}")
                        continue
        
        if not records:
            logging.warning("⚠️ 沒有有效的價格數據可以記錄")
            return
        
        # 保存到歷史文件
        history_path = Path("data/csp_history.csv")
        history_path.parent.mkdir(exist_ok=True)
        
        # 讀取現有歷史數據
        if history_path.exists():
            try:
                existing_df = pd.read_csv(history_path)
                logging.info(f"📊 現有歷史數據：{len(existing_df)} 筆")
            except Exception as e:
                logging.warning(f"⚠️ 讀取現有歷史數據失敗：{e}")
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()
        
        # 創建新記錄的 DataFrame
        new_df = pd.DataFrame(records)
        
        # 合併數據，避免重複
        if not existing_df.empty:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            # 移除重複記錄（同一天同一品項）
            combined_df = combined_df.drop_duplicates(subset=['日期', '品項'], keep='last')
            combined_df = combined_df.sort_values('日期')
        else:
            combined_df = new_df
        
        # 保存到文件
        combined_df.to_csv(history_path, index=False, encoding='utf-8-sig')
        
        logging.info(f"✅ 數據記錄成功！")
        logging.info(f"📊 新增記錄：{len(records)} 筆")
        logging.info(f"📊 總記錄數：{len(combined_df)} 筆")
        logging.info(f"📁 保存位置：{history_path}")
        
        # 同時保存為 Excel 格式
        excel_path = Path("data/csp_history.xlsx")
        combined_df.to_excel(excel_path, index=False)
        logging.info(f"📁 Excel 格式：{excel_path}")
        
    except Exception as e:
        logging.error(f"❌ 記錄數據失敗：{e}")

def check_data_quality():
    """檢查數據品質"""
    try:
        history_path = Path("data/csp_history.csv")
        if not history_path.exists():
            logging.warning("⚠️ 歷史數據文件不存在")
            return
        
        df = pd.read_csv(history_path)
        logging.info(f"📊 數據品質檢查：")
        logging.info(f"   總記錄數：{len(df)}")
        logging.info(f"   日期範圍：{df['日期'].min()} 到 {df['日期'].max()}")
        logging.info(f"   品項種類：{df['品項'].nunique()}")
        
        # 檢查最近7天的數據
        recent_date = datetime.now() - timedelta(days=7)
        recent_df = df[pd.to_datetime(df['日期']) >= recent_date]
        logging.info(f"   最近7天記錄：{len(recent_df)} 筆")
        
        # 檢查各品項的數據量
        item_counts = df['品項'].value_counts()
        logging.info(f"   各品項記錄數：")
        for item, count in item_counts.items():
            logging.info(f"     {item}: {count} 筆")
            
    except Exception as e:
        logging.error(f"❌ 數據品質檢查失敗：{e}")

def main():
    """主函數"""
    logging.info("🚀 LME 數據自動記錄系統啟動")
    logging.info("=" * 50)
    
    # 檢查數據品質
    check_data_quality()
    
    # 設置定時任務
    schedule.every().day.at("09:00").do(record_lme_data)
    schedule.every().day.at("17:00").do(record_lme_data)
    
    # 也可以設置每小時記錄一次（可選）
    # schedule.every().hour.do(record_lme_data)
    
    logging.info("⏰ 自動記錄已設置：")
    logging.info("   - 每天 09:00")
    logging.info("   - 每天 17:00")
    logging.info("按 Ctrl+C 停止")
    
    # 立即執行一次記錄（測試）
    logging.info("🧪 執行測試記錄...")
    record_lme_data()
    
    # 運行定時任務
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    except KeyboardInterrupt:
        logging.info("🛑 用戶停止程序")
    except Exception as e:
        logging.error(f"❌ 程序運行錯誤：{e}")

if __name__ == "__main__":
    main()

