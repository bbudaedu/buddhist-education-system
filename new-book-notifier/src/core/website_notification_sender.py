#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Notification Sender Module
網站監控通知發送器模組

This module coordinates notifications for website monitoring content,
integrating with existing EmailSender and triggering LINE bot notifications.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.config import settings

from email_sender import EmailSender


class WebsiteNotificationSender:
    """
    Coordinates notifications for website monitoring content
    
    Handles both email notifications (direct) and LINE notifications (via TypeScript service)
    with priority-based delivery and error handling.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize WebsiteNotificationSender with configuration
        
        Args:
            config: Configuration dictionary containing notification settings
            logger: Logger instance for logging operations
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Email configuration
        self.email_enabled = config.get('website_monitoring', {}).get('notifications', {}).get('email_enabled', True)
        if self.email_enabled:
            try:
                self.email_sender = EmailSender(
                    smtp_server=config.get('smtp_server', ''),
                    smtp_port=config.get('smtp_port', 587),
                    username=config.get('smtp_username', ''),
                    password=config.get('smtp_password', ''),
                    logger=logger
                )
                self.email_recipients = config.get('email_recipients', '').split(',')
                self.email_recipients = [r.strip() for r in self.email_recipients if r.strip()]
            except Exception as e:
                self.logger.error(f"Failed to initialize EmailSender: {e}")
                self.email_enabled = False
        
        # LINE notification configuration
        self.line_enabled = config.get('website_monitoring', {}).get('notifications', {}).get('line_enabled', True)
        self.line_service_path = config.get('line_service_path', '../Line-bot-llm-mysql')
        
        # Priority configuration
        self.immediate_alerts = config.get('website_monitoring', {}).get('notifications', {}).get('immediate_alerts', ['cancellation'])
        self.daily_summary = config.get('website_monitoring', {}).get('notifications', {}).get('daily_summary', ['carousel', 'news', 'media'])
        
        self.logger.info(f"WebsiteNotificationSender initialized - Email: {self.email_enabled}, LINE: {self.line_enabled}")
    
    def send_notifications(self, content_data: Dict[str, List[Dict]], attachment_paths: Optional[List[str]] = None) -> bool:
        """
        Send notifications for website monitoring content
        
        Args:
            content_data: Dictionary containing content by type (carousel, cancellation, news, media)
            attachment_paths: Optional list of file paths to attach to email
            
        Returns:
            bool: True if all enabled notifications sent successfully, False otherwise
        """
        try:
            if not content_data or not any(content_data.values()):
                self.logger.info("No content data to notify")
                return True
            
            success = True
            
            # Send immediate alerts first (high priority content)
            immediate_content = self._filter_content_by_priority(content_data, 'immediate')
            if immediate_content:
                success &= self._send_immediate_notifications(immediate_content, attachment_paths)
            
            # Send regular notifications for other content
            regular_content = self._filter_content_by_priority(content_data, 'normal')
            if regular_content:
                success &= self._send_regular_notifications(regular_content, attachment_paths)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send notifications: {e}", exc_info=True)
            return False
    
    def _filter_content_by_priority(self, content_data: Dict[str, List[Dict]], priority: str) -> Dict[str, List[Dict]]:
        """
        Filter content data by priority level
        
        Args:
            content_data: Original content data
            priority: Priority level ('immediate', 'normal')
            
        Returns:
            Filtered content data
        """
        try:
            filtered_content = {}
            
            for content_type, items in content_data.items():
                if not items:
                    continue
                
                if priority == 'immediate' and content_type in self.immediate_alerts:
                    filtered_content[content_type] = items
                elif priority == 'normal' and content_type not in self.immediate_alerts:
                    filtered_content[content_type] = items
            
            return filtered_content
            
        except Exception as e:
            self.logger.error(f"Failed to filter content by priority: {e}")
            return {}
    
    def _send_immediate_notifications(self, content_data: Dict[str, List[Dict]], attachment_paths: Optional[List[str]] = None) -> bool:
        """
        Send immediate notifications for high-priority content
        
        Args:
            content_data: High-priority content data
            attachment_paths: Optional file attachments
            
        Returns:
            bool: True if notifications sent successfully
        """
        try:
            success = True
            
            # Send email notification
            if self.email_enabled and self.email_recipients:
                try:
                    email_success = self.email_sender.send_website_monitoring_email(
                        recipients=self.email_recipients,
                        content_data=content_data,
                        attachment_paths=attachment_paths
                    )
                    if email_success:
                        self.logger.info("Immediate email notification sent successfully")
                    else:
                        self.logger.error("Failed to send immediate email notification")
                        success = False
                except Exception as e:
                    self.logger.error(f"Error sending immediate email notification: {e}")
                    success = False
            
            # Send LINE notification
            if self.line_enabled:
                try:
                    line_success = self._send_line_notification(content_data, priority='immediate')
                    if line_success:
                        self.logger.info("Immediate LINE notification sent successfully")
                    else:
                        self.logger.error("Failed to send immediate LINE notification")
                        success = False
                except Exception as e:
                    self.logger.error(f"Error sending immediate LINE notification: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send immediate notifications: {e}")
            return False
    
    def _send_regular_notifications(self, content_data: Dict[str, List[Dict]], attachment_paths: Optional[List[str]] = None) -> bool:
        """
        Send regular notifications for normal-priority content
        
        Args:
            content_data: Normal-priority content data
            attachment_paths: Optional file attachments
            
        Returns:
            bool: True if notifications sent successfully
        """
        try:
            success = True
            
            # Send email notification
            if self.email_enabled and self.email_recipients:
                try:
                    email_success = self.email_sender.send_website_monitoring_email(
                        recipients=self.email_recipients,
                        content_data=content_data,
                        attachment_paths=attachment_paths
                    )
                    if email_success:
                        self.logger.info("Regular email notification sent successfully")
                    else:
                        self.logger.error("Failed to send regular email notification")
                        success = False
                except Exception as e:
                    self.logger.error(f"Error sending regular email notification: {e}")
                    success = False
            
            # Send LINE notification
            if self.line_enabled:
                try:
                    line_success = self._send_line_notification(content_data, priority='normal')
                    if line_success:
                        self.logger.info("Regular LINE notification sent successfully")
                    else:
                        self.logger.error("Failed to send regular LINE notification")
                        success = False
                except Exception as e:
                    self.logger.error(f"Error sending regular LINE notification: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send regular notifications: {e}")
            return False
    
    def _send_line_notification(self, content_data: Dict[str, List[Dict]], priority: str = 'normal') -> bool:
        """
        Send LINE notification by calling the configured webhook URL
        
        Args:
            content_data: Content data to notify
            priority: Notification priority
            
        Returns:
            bool: True if LINE notification sent successfully
        """
        if not content_data:
            return False
            
        try:
            # Format payload for LINE bot webhook
            # 準備傳送給 LINE Bot 的 Webhook Payload
            payload = {
                "type": "broadcast",
                "message": "New content from New Book Notifier",
                "timestamp": datetime.now().isoformat(),
                "priority": priority,
                "structuredData": {}
            }
            
            # Map Python types to TypeScript types expected by LINE bot
            if 'news' in content_data and content_data['news']:
                payload['structuredData']['news'] = content_data['news']
            
            if 'cancellation' in content_data and content_data['cancellation']:
                payload['structuredData']['cancellations'] = content_data['cancellation']
                
            if 'carousel' in content_data and content_data['carousel']:
                payload['structuredData']['newBooks'] = content_data['carousel']
                
            if 'media' in content_data and content_data['media']:
                payload['structuredData']['videos'] = content_data['media']
                
            if not payload['structuredData']:
                self.logger.info("No content to send via LINE after filtering")
                return True
                
            self.logger.info(f"Sending LINE notification payload via webhook to {settings.line_bot_webhook_url}")
            
            webhook_url = settings.line_bot_webhook_url
            if not webhook_url:
                self.logger.error("LINE_BOT_WEBHOOK_URL environment variable is not set")
                return False
                
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response.raise_for_status()
            
            resp_data = response.json()
            if resp_data.get("success"):
                self.logger.info(f"LINE notification sent successfully. Result: {resp_data}")
                return True
            else:
                self.logger.error(f"LINE notification failed. Result: {resp_data}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error sending LINE webhook notification: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending LINE webhook notification: {str(e)}")
            return False
    
    def test_email_connection(self) -> bool:
        """
        Test email connection
        
        Returns:
            bool: True if email connection successful
        """
        try:
            if not self.email_enabled:
                self.logger.info("Email notifications are disabled")
                return True
            
            return self.email_sender.test_connection()
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False
    
    def send_test_notification(self) -> bool:
        """
        Send test notification to verify configuration
        
        Returns:
            bool: True if test notification sent successfully
        """
        try:
            test_content = {
                'test': [{
                    'id': 'test_001',
                    'content_type': 'test',
                    'notification_text': '系統測試通知',
                    'timestamp': datetime.now().isoformat()
                }]
            }
            
            return self.send_notifications(test_content)
            
        except Exception as e:
            self.logger.error(f"Failed to send test notification: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'your_email@gmail.com',
        'smtp_password': 'your_app_password',
        'email_recipients': 'recipient1@example.com,recipient2@example.com',
        'website_monitoring': {
            'notifications': {
                'email_enabled': True,
                'line_enabled': True,
                'immediate_alerts': ['cancellation'],
                'daily_summary': ['carousel', 'news', 'media']
            }
        }
    }
    
    try:
        # Initialize notification sender
        notification_sender = WebsiteNotificationSender(config)
        
        # Test email connection
        if notification_sender.test_email_connection():
            print("Email connection test passed!")
            
            # Send test notification
            if notification_sender.send_test_notification():
                print("Test notification sent successfully!")
            else:
                print("Test notification failed!")
        else:
            print("Email connection test failed!")
            
    except Exception as e:
        print(f"Error: {e}")