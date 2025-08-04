# -*- coding: utf-8 -*-
"""
自動爬蟲主程式
整合客戶搜尋和標案監控功能
"""

import schedule
import time
from datetime import datetime
import sys
import os

# 添加專案路徑到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.customer_scraper import CustomerScraper
from scrapers.tender_scraper import TenderScraper
from utils.notification import NotificationManager, format_customer_notification, format_tender_notification
from utils.logger import main_logger
from config import PATHS

class AutoScraper:
    """自動爬蟲主類別"""
    
    def __init__(self):
        self.customer_scraper = None
        self.tender_scraper = None
        self.notification_manager = NotificationManager()
        
        main_logger.info("自動爬蟲系統初始化完成")
    
    def run_customer_search(self):
        """執行客戶搜尋任務"""
        try:
            main_logger.info("開始執行客戶搜尋任務")
            
            # 初始化客戶爬蟲
            self.customer_scraper = CustomerScraper()
            
            # 執行搜尋
            customers_data = self.customer_scraper.run_search()
            
            # 儲存結果
            self.customer_scraper.save_to_excel(customers_data)
            
            # 發送通知
            if customers_data:
                subject = f"廢銅潛在客戶搜尋結果 - {datetime.now().strftime('%Y-%m-%d')}"
                message = format_customer_notification(customers_data)
                attachments = [PATHS['customer_file']] if os.path.exists(PATHS['customer_file']) else None
                
                self.notification_manager.send_notification(subject, message, attachments)
            
            # 清理資源
            self.customer_scraper.cleanup()
            
            main_logger.info("客戶搜尋任務完成")
            
        except Exception as e:
            main_logger.error(f"客戶搜尋任務執行失敗: {e}")
            self._send_error_notification("客戶搜尋", str(e))
    
    def run_tender_monitoring(self):
        """執行標案監控任務"""
        try:
            main_logger.info("開始執行標案監控任務")
            
            # 初始化標案爬蟲
            self.tender_scraper = TenderScraper()
            
            # 執行搜尋
            tenders_data = self.tender_scraper.run_search()
            
            # 儲存結果
            self.tender_scraper.save_to_excel(tenders_data)
            
            # 發送通知
            if tenders_data:
                subject = f"政府標案監控結果 - {datetime.now().strftime('%Y-%m-%d')}"
                message = format_tender_notification(tenders_data)
                attachments = [PATHS['tender_file']] if os.path.exists(PATHS['tender_file']) else None
                
                self.notification_manager.send_notification(subject, message, attachments)
            
            # 清理資源
            self.tender_scraper.cleanup()
            
            main_logger.info("標案監控任務完成")
            
        except Exception as e:
            main_logger.error(f"標案監控任務執行失敗: {e}")
            self._send_error_notification("標案監控", str(e))
    
    def run_daily_tasks(self):
        """執行每日任務"""
        try:
            main_logger.info("開始執行每日自動化任務")
            
            # 執行客戶搜尋
            self.run_customer_search()
            
            # 等待一段時間後執行標案監控
            time.sleep(60)  # 等待1分鐘
            
            # 執行標案監控
            self.run_tender_monitoring()
            
            main_logger.info("每日自動化任務完成")
            
        except Exception as e:
            main_logger.error(f"每日任務執行失敗: {e}")
            self._send_error_notification("每日任務", str(e))
    
    def _send_error_notification(self, task_name, error_message):
        """發送錯誤通知"""
        try:
            subject = f"自動爬蟲錯誤通知 - {task_name}"
            message = f"任務: {task_name}\n時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n錯誤: {error_message}"
            
            self.notification_manager.send_notification(subject, message)
            
        except Exception as e:
            main_logger.error(f"發送錯誤通知失敗: {e}")
    
    def setup_schedule(self):
        """設定排程任務"""
        # 每天早上9點執行客戶搜尋
        schedule.every().day.at("09:00").do(self.run_customer_search)
        
        # 每天早上10點執行標案監控
        schedule.every().day.at("10:00").do(self.run_tender_monitoring)
        
        # 每天下午2點執行完整任務
        schedule.every().day.at("14:00").do(self.run_daily_tasks)
        
        # 每週一早上8點執行完整任務
        schedule.every().monday.at("08:00").do(self.run_daily_tasks)
        
        main_logger.info("排程任務設定完成")
    
    def run_scheduler(self):
        """執行排程器"""
        main_logger.info("開始執行排程器")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
                
            except KeyboardInterrupt:
                main_logger.info("收到中斷信號，正在關閉排程器...")
                break
            except Exception as e:
                main_logger.error(f"排程器執行錯誤: {e}")
                time.sleep(300)  # 發生錯誤時等待5分鐘
    
    def run_once(self):
        """執行一次完整任務"""
        main_logger.info("執行一次完整任務")
        self.run_daily_tasks()

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自動爬蟲系統')
    parser.add_argument('--once', action='store_true', help='執行一次完整任務')
    parser.add_argument('--customer', action='store_true', help='只執行客戶搜尋')
    parser.add_argument('--tender', action='store_true', help='只執行標案監控')
    parser.add_argument('--schedule', action='store_true', help='啟動排程模式')
    
    args = parser.parse_args()
    
    # 建立自動爬蟲實例
    auto_scraper = AutoScraper()
    
    try:
        if args.once:
            # 執行一次完整任務
            auto_scraper.run_once()
        elif args.customer:
            # 只執行客戶搜尋
            auto_scraper.run_customer_search()
        elif args.tender:
            # 只執行標案監控
            auto_scraper.run_tender_monitoring()
        elif args.schedule:
            # 啟動排程模式
            auto_scraper.setup_schedule()
            auto_scraper.run_scheduler()
        else:
            # 預設執行一次完整任務
            print("未指定參數，執行一次完整任務...")
            auto_scraper.run_once()
    
    except KeyboardInterrupt:
        main_logger.info("程式被使用者中斷")
    except Exception as e:
        main_logger.error(f"程式執行失敗: {e}")
        auto_scraper._send_error_notification("主程式", str(e))

if __name__ == "__main__":
    main() 