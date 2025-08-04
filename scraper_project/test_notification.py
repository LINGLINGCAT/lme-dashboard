# -*- coding: utf-8 -*-
"""
測試通知功能
"""

import sys
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.notification import NotificationManager, format_tender_notification
from utils.logger import main_logger

def test_notification():
    """測試通知功能"""
    print("開始測試通知功能...")
    
    # 建立通知管理器
    notification_manager = NotificationManager()
    
    # 測試資料
    test_tenders = [
        {
            'title': '廢銅回收標案測試',
            'agency': '台北市政府',
            'deadline': '2024-01-15',
            'budget': '100萬元',
            'source': '政府電子採購網',
            'keyword': '廢銅'
        },
        {
            'title': '金屬下腳料處理標案',
            'agency': '新北市政府',
            'deadline': '2024-01-20',
            'budget': '50萬元',
            'source': '新北市政府採購網',
            'keyword': '下腳'
        }
    ]
    
    # 格式化通知內容
    message = format_tender_notification(test_tenders)
    print("通知內容:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    
    # 測試發送通知
    subject = "標案通知測試"
    
    print("\n嘗試發送測試通知...")
    results = notification_manager.send_notification(subject, message)
    
    print(f"Email通知結果: {'成功' if results['email'] else '失敗'}")
    print(f"Line通知結果: {'成功' if results['line'] else '失敗'}")
    
    print("\n測試完成！")

if __name__ == "__main__":
    test_notification() 