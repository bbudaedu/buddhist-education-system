#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Processor Module for Website Monitoring
通知處理模組

This module handles notification processing and distribution for website monitoring,
integrating with existing EmailSender and NewBookService infrastructure.
"""

import os
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional

# Import existing notification infrastructure
from email_sender import EmailSender
from line_notification_service import LineNotificationService


class NotificationProcessor:
    """
    Notification processor for website monitoring content
    
    Handles:
    - Immediate alerts for urgent content (e.g., course cancellations)
    - Daily summary notifications
    - Integration with existing EmailSender and LINE bot services
    - Notification formatting and content preparation
    """
    
    def __init__(self, config: Dict[str, Any], email_sender: Optional[EmailSender] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize NotificationProcessor
        
        Args:
            config: Configuration dictionary
            email_sender: EmailSender instance for email notifications
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        self.email_sender = email_sender
        
        # Initialize LINE notification service
        self.line_service = LineNotificationService(config, logger)
        self.line_enabled = self.line_service.is_enabled()
        
        # Notification templates and formatting
        self.notification_templates = self._load_notification_templates()
        
        self.logger.info("NotificationProcessor initialized")
    

    
    def _load_notification_templates(self) -> Dict[str, str]:
        """
        Load notification templates for different content types
        
        Returns:
            Dict: Notification templates
        """
        return {
            'immediate_alert_email': """
主旨：【緊急通知】佛教教育網站內容更新

親愛的用戶，

以下是需要立即關注的重要更新：

{content}

請及時查看相關資訊。

此郵件由系統自動發送，請勿回覆。
發送時間：{timestamp}
            """.strip(),
            
            'immediate_alert_line': """
🚨 緊急通知
{content}
⏰ {timestamp}
            """.strip(),
            
            'daily_summary_email': """
主旨：【每日摘要】佛教教育網站監控報告

親愛的用戶，

以下是今日的網站內容監控摘要：

{summary}

詳細資訊請查看附件或登入系統查看。

此郵件由系統自動發送，請勿回覆。
發送時間：{timestamp}
            """.strip(),
            
            'daily_summary_line': """
📊 每日監控摘要
{summary}
⏰ {timestamp}
            """.strip(),
            
            'cycle_summary_email': """
主旨：【監控週期】網站監控執行報告

監控週期執行完成：

{cycle_info}

系統狀態正常，持續監控中。

此郵件由系統自動發送，請勿回覆。
發送時間：{timestamp}
            """.strip()
        }
    
    def send_immediate_alerts(self, alert_items: List[Dict[str, Any]]) -> bool:
        """
        Send immediate alerts for urgent content
        
        Args:
            alert_items: List of items requiring immediate notification
            
        Returns:
            bool: True if alerts sent successfully
        """
        try:
            if not alert_items:
                self.logger.info("No immediate alerts to send")
                return True
            
            self.logger.info(f"Sending immediate alerts for {len(alert_items)} items")
            
            # Format alert content
            alert_content = self._format_immediate_alerts(alert_items)
            
            # Send email alerts
            email_success = True
            if self.email_sender:
                email_success = self._send_email_alert(alert_content)
            
            # Send LINE alerts
            line_success = True
            if self.line_enabled:
                line_success = self._send_line_alert(alert_content)
            
            overall_success = email_success and line_success
            
            if overall_success:
                self.logger.info("Immediate alerts sent successfully")
            else:
                self.logger.error(f"Alert sending failed (Email: {email_success}, LINE: {line_success})")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error sending immediate alerts: {e}")
            return False
    
    def _format_immediate_alerts(self, alert_items: List[Dict[str, Any]]) -> str:
        """
        Format immediate alert items into readable content
        
        Args:
            alert_items: List of alert items
            
        Returns:
            str: Formatted alert content
        """
        try:
            formatted_content = []
            
            for item in alert_items:
                content_type = item.get('content_type', 'unknown')
                
                if content_type == 'cancellation':
                    alert_text = f"📅 課程取消通知\n"
                    alert_text += f"課程：{item.get('course_name', '未知課程')}\n"
                    alert_text += f"日期：{item.get('cancellation_date', '未知日期')}\n"
                    alert_text += f"講師：{item.get('instructor_name', '未知講師')}\n"
                    
                elif content_type == 'carousel':
                    alert_text = f"🎯 新活動橫幅\n"
                    alert_text += f"標題：{item.get('banner_title', '未知標題')}\n"
                    alert_text += f"課程：{item.get('course_name', '未知課程')}\n"
                    alert_text += f"講師：{item.get('instructor', '未知講師')}\n"
                    
                elif content_type == 'news':
                    alert_text = f"📰 重要公告\n"
                    alert_text += f"標題：{item.get('title', '未知標題')}\n"
                    alert_text += f"日期：{item.get('publication_date', '未知日期')}\n"
                    content_preview = item.get('content', '')[:100]
                    if len(content_preview) == 100:
                        content_preview += "..."
                    alert_text += f"內容：{content_preview}\n"
                    
                else:
                    alert_text = f"ℹ️ 新內容更新\n"
                    alert_text += f"類型：{content_type}\n"
                    alert_text += f"時間：{item.get('extraction_timestamp', '未知時間')}\n"
                
                formatted_content.append(alert_text)
            
            return "\n" + "="*50 + "\n".join(formatted_content) + "="*50 + "\n"
            
        except Exception as e:
            self.logger.error(f"Error formatting immediate alerts: {e}")
            return f"格式化警報內容時發生錯誤：{e}"
    
    def _send_email_alert(self, alert_content: str) -> bool:
        """
        Send email alert using EmailSender
        
        Args:
            alert_content: Formatted alert content
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not self.email_sender:
                self.logger.warning("EmailSender not available, skipping email alert")
                return True
            
            # Prepare email content
            email_body = self.notification_templates['immediate_alert_email'].format(
                content=alert_content,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Send email using existing EmailSender
            success = self.email_sender.send_notification_email(
                subject="【緊急通知】佛教教育網站內容更新",
                body=email_body,
                is_html=False
            )
            
            if success:
                self.logger.info("Email alert sent successfully")
            else:
                self.logger.error("Failed to send email alert")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
            return False
    
    def _send_line_alert(self, alert_content: str) -> bool:
        """
        Send LINE alert using LineNotificationService
        
        Args:
            alert_content: Formatted alert content
            
        Returns:
            bool: True if LINE message sent successfully
        """
        try:
            if not self.line_enabled:
                self.logger.info("LINE bot not available, skipping LINE alert")
                return True
            
            # Prepare LINE message
            line_message = self.notification_templates['immediate_alert_line'].format(
                content=alert_content,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Send LINE message using LineNotificationService
            success = self.line_service.send_broadcast_message(line_message)
            
            if success:
                self.logger.info("LINE alert sent successfully")
            else:
                self.logger.error("Failed to send LINE alert")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending LINE alert: {e}")
            return False
    
    def process_daily_summary(self, summary_items: List[Dict[str, Any]]) -> bool:
        """
        Process and send daily summary notifications
        
        Args:
            summary_items: List of items for daily summary
            
        Returns:
            bool: True if summary processed successfully
        """
        try:
            if not summary_items:
                self.logger.info("No items for daily summary")
                return True
            
            self.logger.info(f"Processing daily summary for {len(summary_items)} items")
            
            # Generate summary content
            summary_content = self._generate_daily_summary(summary_items)
            
            # Send email summary
            email_success = True
            if self.email_sender:
                email_success = self._send_email_summary(summary_content)
            
            # Send LINE summary
            line_success = True
            if self.line_enabled:
                line_success = self._send_line_summary(summary_content)
            
            overall_success = email_success and line_success
            
            if overall_success:
                self.logger.info("Daily summary processed successfully")
            else:
                self.logger.error(f"Summary processing failed (Email: {email_success}, LINE: {line_success})")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error processing daily summary: {e}")
            return False
    
    def _generate_daily_summary(self, summary_items: List[Dict[str, Any]]) -> str:
        """
        Generate daily summary content from items
        
        Args:
            summary_items: List of items to summarize
            
        Returns:
            str: Generated summary content
        """
        try:
            # Group items by content type
            grouped_items = {}
            for item in summary_items:
                content_type = item.get('content_type', 'unknown')
                if content_type not in grouped_items:
                    grouped_items[content_type] = []
                grouped_items[content_type].append(item)
            
            summary_parts = []
            
            # Generate summary for each content type
            for content_type, items in grouped_items.items():
                type_summary = self._generate_content_type_summary(content_type, items)
                if type_summary:
                    summary_parts.append(type_summary)
            
            # Combine all summaries
            if summary_parts:
                return "\n\n".join(summary_parts)
            else:
                return "今日無新內容更新。"
                
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {e}")
            return f"生成每日摘要時發生錯誤：{e}"
    
    def _generate_content_type_summary(self, content_type: str, items: List[Dict[str, Any]]) -> str:
        """
        Generate summary for specific content type
        
        Args:
            content_type: Type of content
            items: List of items of this type
            
        Returns:
            str: Summary for this content type
        """
        try:
            if not items:
                return ""
            
            type_names = {
                'carousel': '輪播橫幅',
                'cancellation': '課程取消',
                'news': '新聞公告',
                'media': '多媒體內容'
            }
            
            type_name = type_names.get(content_type, content_type)
            summary = f"📋 {type_name} ({len(items)} 項)\n"
            
            # Add details for each item (limit to first 5 items)
            for i, item in enumerate(items[:5]):
                if content_type == 'carousel':
                    summary += f"  • {item.get('banner_title', '未知標題')} - {item.get('course_name', '未知課程')}\n"
                elif content_type == 'cancellation':
                    summary += f"  • {item.get('course_name', '未知課程')} ({item.get('cancellation_date', '未知日期')})\n"
                elif content_type == 'news':
                    summary += f"  • {item.get('title', '未知標題')} ({item.get('publication_date', '未知日期')})\n"
                elif content_type == 'media':
                    summary += f"  • {item.get('course_title', '未知課程')} - {item.get('speaker_name', '未知講師')}\n"
                else:
                    summary += f"  • 項目 {i+1}\n"
            
            # Add "more items" note if there are more than 5
            if len(items) > 5:
                summary += f"  ... 還有 {len(items) - 5} 項\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary for {content_type}: {e}")
            return f"{content_type}: 摘要生成錯誤"
    
    def _send_email_summary(self, summary_content: str) -> bool:
        """
        Send email summary using EmailSender
        
        Args:
            summary_content: Generated summary content
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not self.email_sender:
                self.logger.warning("EmailSender not available, skipping email summary")
                return True
            
            # Prepare email content
            email_body = self.notification_templates['daily_summary_email'].format(
                summary=summary_content,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Send email
            success = self.email_sender.send_notification_email(
                subject="【每日摘要】佛教教育網站監控報告",
                body=email_body,
                is_html=False
            )
            
            if success:
                self.logger.info("Email summary sent successfully")
            else:
                self.logger.error("Failed to send email summary")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending email summary: {e}")
            return False
    
    def _send_line_summary(self, summary_content: str) -> bool:
        """
        Send LINE summary using LineNotificationService
        
        Args:
            summary_content: Generated summary content
            
        Returns:
            bool: True if LINE message sent successfully
        """
        try:
            if not self.line_enabled:
                self.logger.info("LINE bot not available, skipping LINE summary")
                return True
            
            # Prepare LINE message (truncate if too long)
            line_message = self.notification_templates['daily_summary_line'].format(
                summary=summary_content[:800],  # LINE message length limit
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Add truncation notice if content was truncated
            if len(summary_content) > 800:
                line_message += "\n... (內容過長，已截斷)"
            
            # Send LINE message
            success = self.line_service.send_broadcast_message(line_message)
            
            if success:
                self.logger.info("LINE summary sent successfully")
            else:
                self.logger.error("Failed to send LINE summary")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending LINE summary: {e}")
            return False
    
    def send_cycle_summary(self, cycle_summary: Dict[str, Any]) -> bool:
        """
        Send monitoring cycle completion summary
        
        Args:
            cycle_summary: Cycle summary information
            
        Returns:
            bool: True if cycle summary sent successfully
        """
        try:
            self.logger.info("Sending monitoring cycle summary")
            
            # Format cycle summary
            cycle_content = self._format_cycle_summary(cycle_summary)
            
            # Send email summary only (cycle summaries are typically less urgent)
            email_success = True
            if self.email_sender:
                email_success = self._send_cycle_email(cycle_content)
            
            if email_success:
                self.logger.info("Cycle summary sent successfully")
            else:
                self.logger.error("Failed to send cycle summary")
            
            return email_success
            
        except Exception as e:
            self.logger.error(f"Error sending cycle summary: {e}")
            return False
    
    def _format_cycle_summary(self, cycle_summary: Dict[str, Any]) -> str:
        """
        Format monitoring cycle summary
        
        Args:
            cycle_summary: Cycle summary data
            
        Returns:
            str: Formatted cycle summary
        """
        try:
            summary_lines = []
            
            # Basic cycle information
            timestamp = cycle_summary.get('cycle_timestamp', datetime.now())
            summary_lines.append(f"監控週期時間：{timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            total_items = cycle_summary.get('total_items_processed', 0)
            summary_lines.append(f"總處理項目數：{total_items}")
            
            # Content type breakdown
            content_counts = cycle_summary.get('content_type_counts', {})
            if content_counts:
                summary_lines.append("\n內容類型統計：")
                for content_type, count in content_counts.items():
                    type_name = {
                        'carousel': '輪播橫幅',
                        'cancellation': '課程取消',
                        'news': '新聞公告',
                        'media': '多媒體內容'
                    }.get(content_type, content_type)
                    summary_lines.append(f"  • {type_name}：{count} 項")
            
            # New content counts
            new_counts = cycle_summary.get('new_content_counts', {})
            if any(new_counts.values()):
                summary_lines.append("\n新內容統計：")
                for content_type, count in new_counts.items():
                    if count > 0:
                        type_name = {
                            'carousel': '輪播橫幅',
                            'cancellation': '課程取消',
                            'news': '新聞公告',
                            'media': '多媒體內容'
                        }.get(content_type, content_type)
                        summary_lines.append(f"  • {type_name}：{count} 項新內容")
            
            # Processing status
            processing_success = cycle_summary.get('processing_success', {})
            if processing_success:
                summary_lines.append("\n處理狀態：")
                for content_type, success in processing_success.items():
                    status = "成功" if success else "失敗"
                    type_name = {
                        'carousel': '輪播橫幅',
                        'cancellation': '課程取消',
                        'news': '新聞公告',
                        'media': '多媒體內容'
                    }.get(content_type, content_type)
                    summary_lines.append(f"  • {type_name}：{status}")
            
            # Errors
            errors = cycle_summary.get('errors', [])
            if errors:
                summary_lines.append("\n錯誤報告：")
                for error in errors:
                    summary_lines.append(f"  • {error}")
            
            return "\n".join(summary_lines)
            
        except Exception as e:
            self.logger.error(f"Error formatting cycle summary: {e}")
            return f"格式化週期摘要時發生錯誤：{e}"
    
    def _send_cycle_email(self, cycle_content: str) -> bool:
        """
        Send cycle summary email
        
        Args:
            cycle_content: Formatted cycle content
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not self.email_sender:
                self.logger.warning("EmailSender not available, skipping cycle email")
                return True
            
            # Prepare email content
            email_body = self.notification_templates['cycle_summary_email'].format(
                cycle_info=cycle_content,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Send email
            success = self.email_sender.send_notification_email(
                subject="【監控週期】網站監控執行報告",
                body=email_body,
                is_html=False
            )
            
            if success:
                self.logger.info("Cycle summary email sent successfully")
            else:
                self.logger.error("Failed to send cycle summary email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending cycle email: {e}")
            return False


# Example usage and testing
def main():
    """
    Example usage of NotificationProcessor
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
                'enabled': False  # Disabled for testing
            },
            'email': {
                'enabled': True
            }
        }
        
        # Initialize NotificationProcessor (without EmailSender for testing)
        processor = NotificationProcessor(
            config=config,
            email_sender=None,  # Mock EmailSender
            logger=logger
        )
        
        # Test immediate alerts
        test_alerts = [
            {
                'content_type': 'cancellation',
                'course_name': '測試課程',
                'cancellation_date': date.today(),
                'instructor_name': '測試講師'
            }
        ]
        
        success = processor.send_immediate_alerts(test_alerts)
        logger.info(f"Immediate alerts test result: {success}")
        
        # Test daily summary
        test_summary_items = [
            {
                'content_type': 'news',
                'title': '測試新聞',
                'publication_date': date.today()
            },
            {
                'content_type': 'carousel',
                'banner_title': '測試橫幅',
                'course_name': '測試課程'
            }
        ]
        
        success = processor.process_daily_summary(test_summary_items)
        logger.info(f"Daily summary test result: {success}")
        
        # Test cycle summary
        test_cycle_summary = {
            'cycle_timestamp': datetime.now(),
            'total_items_processed': 5,
            'content_type_counts': {'news': 2, 'carousel': 3},
            'processing_success': {'news': True, 'carousel': True},
            'errors': []
        }
        
        success = processor.send_cycle_summary(test_cycle_summary)
        logger.info(f"Cycle summary test result: {success}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")


if __name__ == "__main__":
    main()