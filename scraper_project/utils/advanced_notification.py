# -*- coding: utf-8 -*-
"""
進階通知工具 - 支援多種通知方式
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json
from config import NOTIFICATION_CONFIG
from utils.logger import main_logger

class AdvancedNotificationManager:
    """進階通知管理器"""
    
    def __init__(self):
        self.email_config = NOTIFICATION_CONFIG['email']
        self.telegram_config = NOTIFICATION_CONFIG.get('telegram', {})
        self.discord_config = NOTIFICATION_CONFIG.get('discord', {})
        self.slack_config = NOTIFICATION_CONFIG.get('slack', {})
    
    def send_email(self, subject, body, attachments=None):
        """發送Email通知"""
        if not self.email_config['enabled']:
            main_logger.warning("Email通知已停用")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
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
    
    def send_telegram_notification(self, message, chat_id=None):
        """發送Telegram通知"""
        if not self.telegram_config.get('enabled', False):
            main_logger.warning("Telegram通知已停用")
            return False
        
        try:
            bot_token = self.telegram_config.get('bot_token', '')
            chat_id = chat_id or self.telegram_config.get('chat_id', '')
            
            if not bot_token or not chat_id:
                main_logger.error("Telegram設定不完整")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                main_logger.info("Telegram通知發送成功")
                return True
            else:
                main_logger.error(f"Telegram通知發送失敗: {response.status_code}")
                return False
                
        except Exception as e:
            main_logger.error(f"Telegram通知發送失敗: {e}")
            return False
    
    def send_discord_notification(self, message, webhook_url=None):
        """發送Discord通知"""
        if not self.discord_config.get('enabled', False):
            main_logger.warning("Discord通知已停用")
            return False
        
        try:
            webhook_url = webhook_url or self.discord_config.get('webhook_url', '')
            
            if not webhook_url:
                main_logger.error("Discord Webhook URL未設定")
                return False
            
            data = {
                "content": message,
                "username": "標案監控機器人"
            }
            
            response = requests.post(webhook_url, json=data, timeout=30)
            
            if response.status_code == 204:
                main_logger.info("Discord通知發送成功")
                return True
            else:
                main_logger.error(f"Discord通知發送失敗: {response.status_code}")
                return False
                
        except Exception as e:
            main_logger.error(f"Discord通知發送失敗: {e}")
            return False
    
    def send_slack_notification(self, message, webhook_url=None):
        """發送Slack通知"""
        if not self.slack_config.get('enabled', False):
            main_logger.warning("Slack通知已停用")
            return False
        
        try:
            webhook_url = webhook_url or self.slack_config.get('webhook_url', '')
            
            if not webhook_url:
                main_logger.error("Slack Webhook URL未設定")
                return False
            
            data = {
                "text": message
            }
            
            response = requests.post(webhook_url, json=data, timeout=30)
            
            if response.status_code == 200:
                main_logger.info("Slack通知發送成功")
                return True
            else:
                main_logger.error(f"Slack通知發送失敗: {response.status_code}")
                return False
                
        except Exception as e:
            main_logger.error(f"Slack通知發送失敗: {e}")
            return False
    
    def send_notification(self, subject, message, attachments=None):
        """發送多種通知"""
        results = {
            'email': False,
            'telegram': False,
            'discord': False,
            'slack': False
        }
        
        # 發送Email通知
        if self.email_config['enabled']:
            results['email'] = self.send_email(subject, message, attachments)
        
        # 發送Telegram通知
        if self.telegram_config.get('enabled', False):
            results['telegram'] = self.send_telegram_notification(f"<b>{subject}</b>\n\n{message}")
        
        # 發送Discord通知
        if self.discord_config.get('enabled', False):
            results['discord'] = self.send_discord_notification(f"**{subject}**\n\n{message}")
        
        # 發送Slack通知
        if self.slack_config.get('enabled', False):
            results['slack'] = self.send_slack_notification(f"*{subject}*\n\n{message}")
        
        return results

def format_tender_notification_advanced(tenders_data):
    """格式化標案資料通知內容（支援HTML格式）"""
    if not tenders_data:
        return "今日未發現相關的政府標案"
    
    message = f"發現 {len(tenders_data)} 個相關的政府標案：\n\n"
    
    for i, tender in enumerate(tenders_data[:5], 1):
        message += f"{i}. {tender.get('title', 'N/A')}\n"
        message += f"   機關: {tender.get('agency', 'N/A')}\n"
        message += f"   截止日期: {tender.get('deadline', 'N/A')}\n"
        message += f"   預算: {tender.get('budget', 'N/A')}\n"
        message += f"   來源: {tender.get('source', 'N/A')}\n"
        message += f"   關鍵字: {tender.get('keyword', 'N/A')}\n\n"
    
    if len(tenders_data) > 5:
        message += f"... 還有 {len(tenders_data) - 5} 個標案，詳見附件\n"
    
    return message 