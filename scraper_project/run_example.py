# -*- coding: utf-8 -*-
"""
範例執行腳本
用於測試和示範自動爬蟲系統
"""

import os
import sys
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_customer_scraper():
    """測試客戶搜尋功能"""
    print("=" * 50)
    print("測試客戶搜尋功能")
    print("=" * 50)
    
    try:
        from scrapers.customer_scraper import CustomerScraper
        
        # 建立客戶爬蟲實例
        scraper = CustomerScraper()
        
        # 執行搜尋（只搜尋前3個關鍵字以節省時間）
        from config import COPPER_CUSTOMER_KEYWORDS
        test_keywords = COPPER_CUSTOMER_KEYWORDS[:3]
        
        print(f"測試關鍵字: {test_keywords}")
        
        # 修改關鍵字列表進行測試
        import config
        original_keywords = config.COPPER_CUSTOMER_KEYWORDS
        config.COPPER_CUSTOMER_KEYWORDS = test_keywords
        
        # 執行搜尋
        customers_data = scraper.run_search()
        
        # 恢復原始關鍵字
        config.COPPER_CUSTOMER_KEYWORDS = original_keywords
        
        # 儲存結果
        scraper.save_to_excel(customers_data)
        
        print(f"找到 {len(customers_data)} 個潛在客戶")
        
        # 顯示前3個結果
        for i, customer in enumerate(customers_data[:3], 1):
            print(f"\n{i}. {customer.get('company_name', 'N/A')}")
            print(f"   地址: {customer.get('address', 'N/A')}")
            print(f"   電話: {customer.get('phone', 'N/A')}")
            print(f"   網站: {customer.get('website', 'N/A')}")
        
        # 清理資源
        scraper.cleanup()
        
        print("\n客戶搜尋測試完成！")
        
    except Exception as e:
        print(f"客戶搜尋測試失敗: {e}")

def test_tender_scraper():
    """測試標案監控功能"""
    print("\n" + "=" * 50)
    print("測試標案監控功能")
    print("=" * 50)
    print("注意：系統只會搜尋最近30天的標案資料")
    
    try:
        from scrapers.tender_scraper import TenderScraper
        
        # 建立標案爬蟲實例
        scraper = TenderScraper()
        
        # 執行搜尋（只搜尋前3個關鍵字以節省時間）
        from config import GOVERNMENT_TENDER_KEYWORDS
        test_keywords = GOVERNMENT_TENDER_KEYWORDS[:3]
        
        print(f"測試關鍵字: {test_keywords}")
        
        # 修改關鍵字列表進行測試
        import config
        original_keywords = config.GOVERNMENT_TENDER_KEYWORDS
        config.GOVERNMENT_TENDER_KEYWORDS = test_keywords
        
        # 執行搜尋
        tenders_data = scraper.run_search()
        
        # 恢復原始關鍵字
        config.GOVERNMENT_TENDER_KEYWORDS = original_keywords
        
        # 儲存結果
        scraper.save_to_excel(tenders_data)
        
        print(f"找到 {len(tenders_data)} 個相關標案")
        
        # 顯示前3個結果
        for i, tender in enumerate(tenders_data[:3], 1):
            print(f"\n{i}. {tender.get('title', 'N/A')}")
            print(f"   機關: {tender.get('agency', 'N/A')}")
            print(f"   截止日期: {tender.get('deadline', 'N/A')}")
            print(f"   預算: {tender.get('budget', 'N/A')}")
            print(f"   來源: {tender.get('source', 'N/A')}")
        
        # 清理資源
        scraper.cleanup()
        
        print("\n標案監控測試完成！")
        
    except Exception as e:
        print(f"標案監控測試失敗: {e}")

def test_notification():
    """測試通知功能"""
    print("\n" + "=" * 50)
    print("測試通知功能")
    print("=" * 50)
    
    try:
        from utils.notification import NotificationManager
        
        # 建立通知管理器
        notification_manager = NotificationManager()
        
        # 測試通知
        subject = "自動爬蟲系統測試通知"
        message = f"""
這是一封測試通知

時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系統: 自動爬蟲系統
狀態: 測試中

如果您收到這封通知，表示通知系統運作正常。
        """
        
        # 發送通知
        results = notification_manager.send_notification(subject, message)
        
        print("通知發送結果:")
        print(f"Email: {'成功' if results['email'] else '失敗'}")
        print(f"Line: {'成功' if results['line'] else '失敗'}")
        
        print("\n通知測試完成！")
        
    except Exception as e:
        print(f"通知測試失敗: {e}")

def main():
    """主測試函數"""
    print("自動爬蟲系統測試")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查環境變數
    print("\n檢查環境設定...")
    if os.path.exists('.env'):
        print("✓ 找到 .env 檔案")
    else:
        print("⚠ 未找到 .env 檔案，請複製 env_example.txt 為 .env 並設定")
    
    # 檢查必要目錄
    for dir_name in ['data', 'logs', 'exports']:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name} 目錄存在")
        else:
            print(f"⚠ {dir_name} 目錄不存在，將自動建立")
    
    # 執行測試
    try:
        # 測試客戶搜尋
        test_customer_scraper()
        
        # 測試標案監控
        test_tender_scraper()
        
        # 測試通知
        test_notification()
        
        print("\n" + "=" * 50)
        print("所有測試完成！")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n測試被使用者中斷")
    except Exception as e:
        print(f"\n測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 