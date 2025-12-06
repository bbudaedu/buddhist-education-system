#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Notification Service
多通道通知服務 - Email 整合模組

整合現有 email_sender.py，提供：
- 驗證碼發送
- 訂閱通知發送
- 批量 Email 發送
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加父目錄到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_sender import EmailSender


class EmailNotificationService:
    """
    Email 通知服務
    擴展 email_sender 以支援訂閱通知系統
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None):
        """
        初始化 Email 通知服務
        
        Args:
            config: SMTP 配置，若無則從 config.json 或環境變數讀取
            logger: Logger 實例
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # 優先從 config.json 讀取配置
        if config is None:
            try:
                from config_manager import ConfigManager
                config_manager = ConfigManager()
                cfg = config_manager.config
                config = {
                    'smtp_server': cfg.get('smtp_server', 'smtp.gmail.com'),
                    'smtp_port': int(cfg.get('smtp_port', 587)),
                    'smtp_username': cfg.get('smtp_username', ''),
                    'smtp_password': cfg.get('smtp_password', ''),
                    'smtp_use_tls': cfg.get('smtp_use_tls', True),
                    'sender_email': cfg.get('sender_email', cfg.get('smtp_username', '')),
                    'sender_name': cfg.get('sender_name', '佛陀教育基金會'),
                    'email_recipients': cfg.get('email_recipients', [])
                }
                self.logger.info("已從 config.json 讀取 SMTP 設定")
            except Exception as e:
                self.logger.warning(f"無法從 config.json 讀取設定: {e}，改用環境變數")
                config = {
                    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                    'smtp_username': os.getenv('SMTP_USERNAME', ''),
                    'smtp_password': os.getenv('SMTP_PASSWORD', ''),
                    'smtp_use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
                    'sender_email': os.getenv('SENDER_EMAIL', ''),
                    'sender_name': os.getenv('SENDER_NAME', '佛陀教育基金會'),
                    'email_recipients': []
                }
        
        self.email_sender = EmailSender(config=config, logger=self.logger)
        
        if self.email_sender.is_configured:
            self.logger.info("EmailNotificationService 初始化成功")
        else:
            self.logger.warning("EmailNotificationService 配置不完整")
    
    def send_verification_code(self, email: str, code: str, display_name: str = "用戶") -> bool:
        """
        發送 Email 驗證碼
        
        Args:
            email: 目標 Email
            code: 6 位數驗證碼
            display_name: 用戶顯示名稱
            
        Returns:
            bool: 發送是否成功
        """
        try:
            subject = "📧 佛陀教育基金會 - Email 驗證碼"
            
            body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ width: 80px; height: auto; }}
        .code-box {{ background: #f5f5f5; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
        .code {{ font-size: 32px; font-weight: bold; color: #06c755; letter-spacing: 8px; }}
        .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://www.budaedu.org/img/logo.png" alt="佛陀教育基金會" class="logo">
            <h2>Email 驗證碼</h2>
        </div>
        
        <p>親愛的 {display_name}，</p>
        <p>您正在設定佛陀教育基金會通知服務的 Email，請使用以下驗證碼完成驗證：</p>
        
        <div class="code-box">
            <div class="code">{code}</div>
        </div>
        
        <p>此驗證碼將在 <strong>10 分鐘</strong>後失效。</p>
        <p>如果這不是您的操作，請忽略此郵件。</p>
        
        <div class="footer">
            <p>此郵件由系統自動發送，請勿回覆</p>
            <p>佛陀教育基金會 © {datetime.now().year}</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            success = self.email_sender.send_notification_email(
                subject=subject,
                body=body,
                is_html=True,
                recipients=[email]
            )
            
            if success:
                self.logger.info(f"驗證碼已發送至 {email}")
            else:
                self.logger.error(f"驗證碼發送失敗: {email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"發送驗證碼時發生錯誤: {e}")
            return False
    
    def send_notification_to_subscribers(
        self, 
        subscribers: List[Dict[str, str]], 
        notification_type: str,
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        發送通知給多個訂閱者
        
        Args:
            subscribers: 訂閱者列表，每個包含 email, display_name
            notification_type: 通知類型 (new_books, news, cancellation, video)
            content: 通知內容
            
        Returns:
            Dict: 發送結果 {success_count, failed_count, failed_emails}
        """
        result = {
            'success_count': 0,
            'failed_count': 0,
            'failed_emails': []
        }
        
        if not subscribers:
            self.logger.warning("沒有訂閱者")
            return result
        
        # 根據通知類型建立郵件內容
        subject, body = self._format_notification_email(notification_type, content)
        
        for subscriber in subscribers:
            email = subscriber.get('email')
            if not email:
                continue
            
            try:
                success = self.email_sender.send_notification_email(
                    subject=subject,
                    body=body,
                    is_html=True,
                    recipients=[email]
                )
                
                if success:
                    result['success_count'] += 1
                else:
                    result['failed_count'] += 1
                    result['failed_emails'].append(email)
                    
            except Exception as e:
                self.logger.error(f"發送通知至 {email} 失敗: {e}")
                result['failed_count'] += 1
                result['failed_emails'].append(email)
        
        self.logger.info(
            f"通知發送完成: 成功 {result['success_count']}, 失敗 {result['failed_count']}"
        )
        
        return result
    
    def _format_notification_email(
        self, 
        notification_type: str, 
        content: Dict[str, Any]
    ) -> tuple:
        """
        根據通知類型格式化郵件
        
        Returns:
            tuple: (subject, body)
        """
        type_config = {
            'new_books': {
                'emoji': '📚',
                'title': '新書上架通知'
            },
            'news': {
                'emoji': '📰',
                'title': '最新消息'
            },
            'cancellation': {
                'emoji': '📢',
                'title': '停課通知'
            },
            'video': {
                'emoji': '🎬',
                'title': '新影音通知'
            }
        }
        
        config = type_config.get(notification_type, {
            'emoji': '🔔',
            'title': '通知'
        })
        
        subject = f"{config['emoji']} 佛陀教育基金會 - {config['title']}"
        
        # 建立內容列表
        items_html = ""
        items = content.get('items', [])
        for item in items[:10]:  # 最多顯示 10 項
            title = item.get('title', '')
            url = item.get('url', '')
            items_html += f'<li><a href="{url}">{title}</a></li>'
        
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; background: linear-gradient(135deg, #06c755, #03a9f4); color: white; padding: 20px; border-radius: 8px; }}
        .content {{ padding: 20px 0; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 10px 0; }}
        a {{ color: #06c755; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }}
        .button {{ display: inline-block; background: #06c755; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{config['emoji']} {config['title']}</h1>
        </div>
        
        <div class="content">
            <p>{content.get('message', '以下是最新資訊：')}</p>
            <ul>
                {items_html}
            </ul>
            
            <p style="text-align: center;">
                <a href="https://www.budaedu.org" class="button">前往官網查看更多</a>
            </p>
        </div>
        
        <div class="footer">
            <p>您收到此郵件是因為您訂閱了佛陀教育基金會的通知服務</p>
            <p>如需取消訂閱，請透過 LINE Bot 操作</p>
            <p>佛陀教育基金會 © {datetime.now().year}</p>
        </div>
    </div>
</body>
</html>
        """.strip()
        
        return subject, body


# API 端點入口（供 Node.js 呼叫）
def send_verification_email(email: str, code: str, display_name: str = "用戶") -> bool:
    """
    API 進入點：發送驗證碼
    """
    service = EmailNotificationService()
    return service.send_verification_code(email, code, display_name)


def send_notification_emails(subscribers: List[Dict], notification_type: str, content: Dict) -> Dict:
    """
    API 進入點：發送訂閱通知
    """
    service = EmailNotificationService()
    return service.send_notification_to_subscribers(subscribers, notification_type, content)


if __name__ == "__main__":
    # 測試
    logging.basicConfig(level=logging.INFO)
    
    # 測試驗證碼發送
    # send_verification_email("test@example.com", "123456", "測試用戶")
    
    print("EmailNotificationService 模組載入成功")
