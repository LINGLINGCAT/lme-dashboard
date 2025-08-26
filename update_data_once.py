#!/usr/bin/env python3
"""
LME Dashboard 一次性數據更新腳本
功能：從Z:/LME.xlsm抓取數據並更新到data目錄
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

def update_data():
    """更新LME數據"""
    print("🚀 LME Dashboard 數據更新工具")
    print("=" * 40)
    
    try:
        # 檢查源數據文件
        source_path = Path("Z:/LME.xlsm")
        if not source_path.exists():
            print(f"❌ 源數據文件不存在：{source_path}")
            print("💡 請確保Z:/LME.xlsm文件存在")
            return False
        
        # 載入Excel數據
        print(f"📊 正在載入數據：{source_path}")
        df = pd.read_excel(source_path, sheet_name="3M RECORD")
        
        if df.empty:
            print("❌ 載入的數據為空")
            return False
        
        # 確保data目錄存在
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # 保存為多種格式
        outputs = []
        
        # 1. 更新csp_history.csv（主要格式）
        csp_path = data_dir / "csp_history.csv"
        df.to_csv(csp_path, index=False, encoding='utf-8-sig')
        outputs.append(f"📁 CSP歷史數據：{csp_path}")
        
        # 2. 保存為lme_updated_data.csv（備用格式）
        lme_path = data_dir / "lme_updated_data.csv"
        df.to_csv(lme_path, index=False, encoding='utf-8-sig')
        outputs.append(f"📁 LME更新數據：{lme_path}")
        
        # 3. 保存為Excel格式（備用）
        excel_path = data_dir / "lme_updated_data.xlsx"
        df.to_excel(excel_path, index=False)
        outputs.append(f"📁 Excel格式：{excel_path}")
        
        print("✅ 數據更新成功！")
        print(f"📊 數據行數：{len(df)}")
        print(f"📋 欄位：{list(df.columns)}")
        print(f"🕒 更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("📁 已保存的文件：")
        for output in outputs:
            print(f"   {output}")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據更新失敗：{e}")
        return False

if __name__ == "__main__":
    success = update_data()
    if not success:
        sys.exit(1)

