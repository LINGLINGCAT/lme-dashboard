# -*- coding: utf-8 -*-
"""
爬蟲專案設定檔
"""

import os
from dotenv import load_dotenv

load_dotenv()

# 廢銅潛在客戶搜尋關鍵字 - 簡化版本
COPPER_CUSTOMER_KEYWORDS = [
    "名家利",
    "宏于電機",
    "金屬回收",
    "回收商",
    "規格",
    "廠房拆解",
    "環保回收",
    "沖壓加工",
    "廢銅回收",
    "銅製品",
    "銅材加工",
    "中盤商",
    "廢車回收",
    "政府採購",
    "以他們的磅",
    "機械公司",
    "廢金屬回收",
    "標案",
    "公家機關",
    "精密機械",
    "沖壓工廠",
    "汽車拆解廠",
    "貿易商",
    "金屬沖壓",
    "資源回收",
    "德輝",
    "機械加工",
    "電線製造",
    "廢料回收",
    "機電公司",
    "古物商",
    "裁切廠",
    "電纜廠",
    "汽車回收",
    "電線回收",
    "精密加工",
    "大正科技機械",
    "家電拆解",
    "鈦貿",
    "電線電纜廠",
    "電線廠",
    "五金加工",
    "政府機關",
    "工程行",
    "金屬加工",
    "宏于袋子只扣",
    "華貿",
    "沖壓",
    "銅管製造",
    "沖壓廠",
    "汽車零件",
    "電纜製造",
    "廢電線回收",
    "精密沖壓",
    "銅加工"
]

# 政府標案監控關鍵字
GOVERNMENT_TENDER_KEYWORDS = [
    "下腳", "金屬", "銅", "鋁", "計量器", "五金", "廢料"
]

# 搜尋引擎設定
SEARCH_ENGINES = {
    "google": "https://www.google.com/search",
    "bing": "https://www.bing.com/search",
    "yahoo": "https://search.yahoo.com/search"
}

# 政府標案網站
GOVERNMENT_SITES = {
    "政府電子採購網": "https://web.pcc.gov.tw/opas/aspam/public/indexAspam",
    "台北市政府採購網": "https://gpis.taipei.gov.tw/",
    "新北市政府採購網": "https://www.cop.ntpc.gov.tw/",
    "桃園市政府採購網": "https://gpis.tycg.gov.tw/"
}

# 通知設定
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": True,
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "sender_email": os.getenv("SENDER_EMAIL", ""),
        "sender_password": os.getenv("SENDER_PASSWORD", ""),
        "recipient_emails": os.getenv("RECIPIENT_EMAILS", "").split(",")
    },
    "telegram": {
        "enabled": False,
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    },
    "discord": {
        "enabled": False,
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
    },
    "slack": {
        "enabled": False,
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL", "")
    }
}

# 爬蟲設定
SCRAPER_CONFIG = {
    "delay_between_requests": 2,  # 請求間隔秒數
    "max_retries": 3,  # 最大重試次數
    "timeout": 30,  # 請求超時時間
    "user_agent_rotation": True,  # 是否輪換User-Agent
    "save_to_excel": True,  # 是否儲存到Excel
    "save_to_database": False,  # 是否儲存到資料庫
    "search_days_back": 30  # 搜尋最近30天的資料
}

# 檔案路徑設定
PATHS = {
    "data_dir": "data",
    "logs_dir": "logs",
    "exports_dir": "exports",
    "customer_file": "data/potential_customers.xlsx",
    "tender_file": "data/government_tenders.xlsx"
}

# 建立必要的目錄
for path in PATHS.values():
    if path.endswith(('.xlsx', '.csv')):
        continue
    os.makedirs(path, exist_ok=True) 