#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINE Notification Service for Website Monitoring
LINE 通知服務模組

This module provides integration with the TypeScript LINE bot service
to send website monitoring notifications via LINE messaging.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class LineNotificationService:
    """
    LINE notification service for website monitoring
    
    Integrates with TypeScript LINE bot backend to send notifications
    about website content updates via LINE messaging API.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize LINE notification service
        
        Args:
            config: Configuration dictionary
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        
        # Get LINE bot configuration
        line_config = config.get('line_bot', {})
        self.enabled = line_config.get('enabled', False)
        self.api_url = line_config.get('api_url', 'http://localhost:3000/api/notifications')
        self.api_key = line_config.get('api_key', '')
        
        # Notification settings
        monitoring_config = config.get('website_monitoring', {})
        notification_config = monitoring_config.get('notifications', {})
        self.line_enabled = notification_config.get('line_enabled', False)
        
        if self.line_enabled and self.enabled:
            self.logger.info(f"LINE notification service initialized (API: {self.api_url})")
        else:
            self.logger.info("LINE notification service disabled")
    
    def is_enabled(self) -> bool:
        """
        Check if LINE notifications are enabled
        
        Returns:
            bool: True if LINE notifications are enabled
        """
        return self.enabled and self.line_enabled
    
    def send_broadcast_message(self, message: str, content_type: str = 'news') -> bool:
        """
        Send broadcast message to all LINE bot users
        
        Args:
            message: Message text to broadcast
            content_type: Type of content ('news', 'cancellation', 'new_books')
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            if not self.is_enabled():
                self.logger.debug("LINE notifications disabled, skipping broadcast")
                return True
            
            self.logger.info(f"Sending LINE broadcast message (type: {content_type})...")
            
            # Prepare API request
            payload = {
                'type': 'broadcast',
                'message': message,
                'contentType': content_type,
                'timestamp': datetime.now().isoformat()
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Send request to LINE bot backend
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("LINE broadcast message sent successfully")
                return True
            else:
                self.logger.error(f"LINE broadcast failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LINE broadcast request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending LINE broadcast: {e}")
            return False
    
    def send_immediate_alert(self, alert_items: List[Dict[str, Any]]) -> bool:
        """
        Send immediate alert notification via LINE
        
        Args:
            alert_items: List of items requiring immediate notification
            
        Returns:
            bool: True if alert sent successfully
        """
        try:
            if not self.is_enabled():
                self.logger.debug("LINE notifications disabled, skipping alert")
                return True
            
            if not alert_items:
                self.logger.debug("No alert items to send")
                return True
            
            self.logger.info(f"Sending LINE immediate alert for {len(alert_items)} items...")
            
            # Format alert message
            message = self._format_immediate_alert(alert_items)
            
            # Send via broadcast
            return self.send_broadcast_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending LINE immediate alert: {e}")
            return False
    
    def send_daily_summary(self, summary_items: List[Dict[str, Any]]) -> bool:
        """
        Send daily summary notification via LINE
        
        Args:
            summary_items: List of items for daily summary
            
        Returns:
            bool: True if summary sent successfully
        """
        try:
            if not self.is_enabled():
                self.logger.debug("LINE notifications disabled, skipping summary")
                return True
            
            if not summary_items:
                self.logger.debug("No summary items to send")
                return True
            
            self.logger.info(f"Sending LINE daily summary for {len(summary_items)} items...")
            
            # Format summary message
            message = self._format_daily_summary(summary_items)
            
            # Send via broadcast
            return self.send_broadcast_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending LINE daily summary: {e}")
            return False
    
    def send_integrated_notification(self, structured_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Send integrated notification with structured data for Flex Message
        
        Args:
            structured_data: Structured data containing newBooks, news, cancellations
            
        Returns:
            bool: True if notification sent successfully
        """
        try:
            if not self.is_enabled():
                self.logger.debug("LINE notifications disabled, skipping integrated notification")
                return True
            
            self.logger.info("Sending LINE integrated notification (Flex Carousel)...")
            
            # Helper function to ensure all datetime objects are JSON serializable
            from datetime import date, datetime as dt
            def make_serializable(obj):
                """Convert datetime/date objects to ISO format strings"""
                if isinstance(obj, (date, dt)):
                    return obj.isoformat()
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [make_serializable(i) for i in obj]
                return obj
            
            # Serialize structured_data to ensure JSON compatibility
            serialized_data = make_serializable(structured_data)
            
            # Prepare API request with structured data
            payload = {
                'type': 'broadcast',
                'message': '佛教教育網站最新訊息',  # Fallback text
                'timestamp': datetime.now().isoformat(),
                'structuredData': serialized_data
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Send request to LINE bot backend
            response = requests.post(
                f"{self.api_url}/website-monitoring",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                messages_sent = result.get('messagesSent', 0)
                self.logger.info(f"LINE integrated notification sent successfully ({messages_sent} users)")
                return True
            else:
                self.logger.error(f"LINE integrated notification failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LINE integrated notification request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending LINE integrated notification: {e}")
            return False
    
    def _format_immediate_alert(self, alert_items: List[Dict[str, Any]]) -> str:
        """
        Format immediate alert items into LINE message
        
        Args:
            alert_items: List of alert items
            
        Returns:
            str: Formatted LINE message
        """
        try:
            message_parts = ["🚨 緊急通知\n"]
            
            for item in alert_items[:5]:  # Limit to 5 items
                content_type = item.get('content_type', 'unknown')
                
                if content_type == 'cancellation':
                    message_parts.append(
                        f"\n📅 課程取消\n"
                        f"課程：{item.get('course_name', '未知')}\n"
                        f"日期：{item.get('cancellation_date', '未知')}\n"
                        f"講師：{item.get('instructor_name', '未知')}"
                    )
                elif content_type == 'carousel':
                    message_parts.append(
                        f"\n🎯 新活動橫幅\n"
                        f"標題：{item.get('banner_title', '未知')}\n"
                        f"課程：{item.get('course_name', '未知')}"
                    )
                elif content_type == 'news':
                    title = item.get('title', '未知')
                    date = item.get('publication_date', '未知')
                    message_parts.append(
                        f"\n📰 重要公告\n"
                        f"標題：{title}\n"
                        f"日期：{date}"
                    )
            
            if len(alert_items) > 5:
                message_parts.append(f"\n... 還有 {len(alert_items) - 5} 項更新")
            
            message_parts.append(f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            return "\n".join(message_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting immediate alert: {e}")
            return f"🚨 緊急通知\n發生 {len(alert_items)} 項更新"
    
    def _format_daily_summary(self, summary_items: List[Dict[str, Any]]) -> str:
        """
        Format daily summary items into LINE message
        
        Args:
            summary_items: List of summary items
            
        Returns:
            str: Formatted LINE message
        """
        try:
            # Group items by content type
            grouped = {}
            for item in summary_items:
                content_type = item.get('content_type', 'unknown')
                if content_type not in grouped:
                    grouped[content_type] = []
                grouped[content_type].append(item)
            
            message_parts = ["📊 每日監控摘要\n"]
            
            type_names = {
                'carousel': '輪播橫幅',
                'news': '新聞公告',
                'media': '多媒體內容',
                'cancellation': '課程取消'
            }
            
            type_emojis = {
                'carousel': '🎯',
                'news': '📰',
                'media': '🎬',
                'cancellation': '📅'
            }
            
            for content_type, items in grouped.items():
                type_name = type_names.get(content_type, content_type)
                emoji = type_emojis.get(content_type, '📋')
                
                message_parts.append(f"\n{emoji} {type_name}：{len(items)} 項")
                
                # Show first 3 items
                for item in items[:3]:
                    if content_type == 'news':
                        title = item.get('title', '未知')
                        if len(title) > 30:
                            title = title[:30] + "..."
                        message_parts.append(f"  • {title}")
                    elif content_type == 'carousel':
                        title = item.get('banner_title', item.get('course_name', '未知'))
                        if len(title) > 30:
                            title = title[:30] + "..."
                        message_parts.append(f"  • {title}")
                    elif content_type == 'cancellation':
                        course = item.get('course_name', '未知')
                        message_parts.append(f"  • {course}")
                
                if len(items) > 3:
                    message_parts.append(f"  ... 還有 {len(items) - 3} 項")
            
            message_parts.append(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            return "\n".join(message_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting daily summary: {e}")
            return f"📊 每日監控摘要\n共 {len(summary_items)} 項更新"


# Example usage and testing
def main():
    """
    Example usage of LineNotificationService
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Mock configuration
        config = {
            'line_bot': {
                'enabled': True,
                'api_url': 'http://localhost:3000/api/notifications',
                'api_key': ''
            },
            'website_monitoring': {
                'notifications': {
                    'line_enabled': True
                }
            }
        }
        
        # Initialize service
        service = LineNotificationService(config, logger)
        
        # Test immediate alert
        test_alerts = [
            {
                'content_type': 'news',
                'title': '測試新聞標題',
                'publication_date': '2025-11-13'
            }
        ]
        
        success = service.send_immediate_alert(test_alerts)
        logger.info(f"Immediate alert test result: {success}")
        
        # Test daily summary
        test_summary = [
            {
                'content_type': 'news',
                'title': '測試新聞 1'
            },
            {
                'content_type': 'carousel',
                'banner_title': '測試橫幅'
            }
        ]
        
        success = service.send_daily_summary(test_summary)
        logger.info(f"Daily summary test result: {success}")
        
        logger.info("LINE notification service tests completed")
        
    except Exception as e:
        logger.error(f"Error in LINE notification service test: {e}")


if __name__ == "__main__":
    main()
