# -*- coding: utf-8 -*-
"""
標案通知腳本 - 使用現有通知系統發送標案結果
"""

import os
import sys
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scrapers.tender_scraper import TenderScraper
from utils.advanced_notification import AdvancedNotificationManager, format_tender_notification_advanced
from utils.logger import tender_logger
from config import PATHS

class TenderNotificationService:
    """標案通知服務"""
    
    def __init__(self):
        self.notification_manager = AdvancedNotificationManager()
        self.scraper = TenderScraper()
    
    def run_daily_tender_search(self):
        """
        執行每日標案搜尋並發送通知
        """
        try:
            tender_logger.info("開始執行每日標案搜尋")
            
            # 執行標案搜尋
            tenders_data = self.scraper.run_search()
            
            # 儲存到Excel
            if tenders_data:
                self.scraper.save_to_excel(tenders_data)
            
            # 格式化通知內容
            notification_message = format_tender_notification_advanced(tenders_data)
            
            # 準備附件
            attachments = []
            if tenders_data and os.path.exists(PATHS['tender_file']):
                attachments.append(PATHS['tender_file'])
            
            # 發送通知
            subject = f"每日標案監控報告 - {datetime.now().strftime('%Y-%m-%d')}"
            
            results = self.notification_manager.send_notification(
                subject=subject,
                message=notification_message,
                attachments=attachments
            )
            
            # 記錄通知結果
            if results['email']:
                tender_logger.info("Email通知發送成功")
            if results['telegram']:
                tender_logger.info("Telegram通知發送成功")
            if results['discord']:
                tender_logger.info("Discord通知發送成功")
            if results['slack']:
                tender_logger.info("Slack通知發送成功")
            
            tender_logger.info(f"每日標案搜尋完成，找到 {len(tenders_data)} 個標案")
            
        except Exception as e:
            tender_logger.error(f"每日標案搜尋失敗: {e}")
            
            # 發送錯誤通知
            error_message = f"標案搜尋發生錯誤: {str(e)}"
            self.notification_manager.send_notification(
                subject="標案監控錯誤通知",
                message=error_message
            )
        
        finally:
            # 清理資源
            self.scraper.cleanup()
    
    def run_manual_search(self):
        """
        手動執行標案搜尋（用於測試）
        """
        print("開始手動執行標案搜尋...")
        self.run_daily_tender_search()
        print("手動執行完成")
    
    def schedule_daily_notification(self, time_str="09:00"):
        """
        設定每日定時通知
        
        Args:
            time_str (str): 執行時間，格式為 "HH:MM"
        """
        schedule.every().day.at(time_str).do(self.run_daily_tender_search)
        tender_logger.info(f"已設定每日 {time_str} 執行標案搜尋")
        
        print(f"標案通知服務已啟動，將於每日 {time_str} 執行")
        print("按 Ctrl+C 停止服務")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
        except KeyboardInterrupt:
            print("\n服務已停止")
            self.scraper.cleanup()

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="標案通知服務")
    parser.add_argument(
        "--manual", 
        action="store_true", 
        help="手動執行一次標案搜尋"
    )
    parser.add_argument(
        "--schedule", 
        type=str, 
        default="09:00",
        help="設定每日執行時間 (格式: HH:MM，預設: 09:00)"
    )
    
    args = parser.parse_args()
    
    service = TenderNotificationService()
    
    if args.manual:
        service.run_manual_search()
    else:
        service.schedule_daily_notification(args.schedule)

if __name__ == "__main__":
    main() 