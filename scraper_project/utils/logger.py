# -*- coding: utf-8 -*-
"""
日誌記錄工具
"""

import logging
import os
from datetime import datetime
from config import PATHS

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    設定日誌記錄器
    
    Args:
        name (str): 日誌記錄器名稱
        log_file (str): 日誌檔案路徑
        level: 日誌等級
    
    Returns:
        logging.Logger: 設定好的日誌記錄器
    """
    # 建立日誌記錄器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重複添加handler
    if logger.handlers:
        return logger
    
    # 建立格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台輸出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 檔案輸出
    if log_file:
        # 確保日誌目錄存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_daily_logger(name):
    """
    取得每日日誌記錄器
    
    Args:
        name (str): 日誌記錄器名稱
    
    Returns:
        logging.Logger: 每日日誌記錄器
    """
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(PATHS['logs_dir'], f'{name}_{today}.log')
    return setup_logger(name, log_file)

# 建立主要日誌記錄器
main_logger = get_daily_logger('scraper_main')
customer_logger = get_daily_logger('customer_scraper')
tender_logger = get_daily_logger('tender_scraper') 