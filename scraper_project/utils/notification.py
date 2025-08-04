# -*- coding: utf-8 -*-
"""
通知工具 - 支援Email和Line通知
"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from config import NOTIFICATION_CONFIG
from utils.logger import main_logger

class NotificationManager:
    """通知管理器"""
    
    def __init__(self):
        self.email_config = NOTIFICATION_CONFIG['email']
        self.line_config = NOTIFICATION_CONFIG['line']
    
    def send_email(self, subject, body, attachments=None):
        """
        發送Email通知
        
        Args:
            subject (str): 郵件主旨
            body (str): 郵件內容
            attachments (list): 附件檔案路徑列表
        
        Returns:
            bool: 發送是否成功
        """
        if not self.email_config['enabled']:
            main_logger.warning("Email通知已停用")
            return False
        
        try:
            # 建立郵件
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            # 添加郵件內容
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {file_path.split("/")[-1]}'
                        )
                        msg.attach(part)
                    except Exception as e:
                        main_logger.error(f"添加附件失敗: {file_path}, 錯誤: {e}")
            
            # 發送郵件
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(
                self.email_config['sender_email'],
                self.email_config['recipient_emails'],
                text
            )
            server.quit()
            
            main_logger.info(f"Email通知發送成功: {subject}")
            return True
            
        except Exception as e:
            main_logger.error(f"Email通知發送失敗: {e}")
            return False
    
    def send_line_notification(self, message):
        """
        發送Line通知
        
        Args:
            message (str): 通知訊息
        
        Returns:
            bool: 發送是否成功
        """
        if not self.line_config['enabled']:
            main_logger.warning("Line通知已停用")
            return False
        
        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {
                "Authorization": f"Bearer {self.line_config['line_token']}"
            }
            data = {
                "message": message
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                main_logger.info("Line通知發送成功")
                return True
            else:
                main_logger.error(f"Line通知發送失敗: {response.status_code}")
                return False
                
        except Exception as e:
            main_logger.error(f"Line通知發送失敗: {e}")
            return False
    
    def send_notification(self, subject, message, attachments=None):
        """
        發送通知（Email + Line）
        
        Args:
            subject (str): 通知主旨
            message (str): 通知內容
            attachments (list): 附件檔案路徑列表
        
        Returns:
            dict: 各通知方式的發送結果
        """
        results = {
            'email': False,
            'line': False
        }
        
        # 發送Email通知
        if self.email_config['enabled']:
            results['email'] = self.send_email(subject, message, attachments)
        
        # 發送Line通知
        if self.line_config['enabled']:
            results['line'] = self.send_line_notification(f"{subject}\n\n{message}")
        
        return results

def format_customer_notification(customers_data):
    """
    格式化客戶資料通知內容
    
    Args:
        customers_data (list): 客戶資料列表
    
    Returns:
        str: 格式化的通知內容
    """
    if not customers_data:
        return "今日未發現新的潛在客戶"
    
    message = f"發現 {len(customers_data)} 個新的潛在客戶：\n\n"
    
    for i, customer in enumerate(customers_data[:10], 1):  # 只顯示前10個
        message += f"{i}. {customer.get('company_name', 'N/A')}\n"
        message += f"   地址: {customer.get('address', 'N/A')}\n"
        message += f"   電話: {customer.get('phone', 'N/A')}\n"
        message += f"   網站: {customer.get('website', 'N/A')}\n"
        message += f"   關鍵字: {', '.join(customer.get('keywords', []))}\n\n"
    
    if len(customers_data) > 10:
        message += f"... 還有 {len(customers_data) - 10} 個客戶，詳見附件\n"
    
    return message

def format_tender_notification(tenders_data):
    """
    格式化標案資料通知內容
    
    Args:
        tenders_data (list): 標案資料列表
    
    Returns:
        str: 格式化的通知內容
    """
    if not tenders_data:
        return "今日未發現相關的政府標案"
    
    message = f"發現 {len(tenders_data)} 個相關的政府標案：\n\n"
    
    for i, tender in enumerate(tenders_data[:5], 1):  # 只顯示前5個
        message += f"{i}. {tender.get('title', 'N/A')}\n"
        message += f"   機關: {tender.get('agency', 'N/A')}\n"
        message += f"   截止日期: {tender.get('deadline', 'N/A')}\n"
        message += f"   預算: {tender.get('budget', 'N/A')}\n"
        message += f"   來源: {tender.get('source', 'N/A')}\n"
        message += f"   關鍵字: {tender.get('keyword', 'N/A')}\n\n"
    
    if len(tenders_data) > 5:
        message += f"... 還有 {len(tenders_data) - 5} 個標案，詳見附件\n"
    
    return message 