
# LME 數據自動記錄時間表
# 每天早上 9:00 和下午 17:00 自動記錄數據

import schedule
import time
from datetime import datetime
import pandas as pd
from pathlib import Path

def record_lme_data():
    """記錄 LME 數據"""
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
