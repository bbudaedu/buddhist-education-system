#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Notification Service
統一通知服務 - 整合所有通知為一封訊息
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional


class UnifiedNotificationService:
    """
    統一通知服務
    將停課通知和新聞公告整合成一封訊息
    """
    
    def __init__(self, line_service, email_sender, logger: Optional[logging.Logger] = None):
        """
        Initialize UnifiedNotificationService
        
        Args:
            line_service: LINE notification service
            email_sender: Email sender service
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.line_service = line_service
        self.email_sender = email_sender
    
    def send_unified_notification(self, all_content: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        發送統一通知訊息
        
        Args:
            all_content: 所有內容 {'cancellation': [...], 'news': [...], ...}
            
        Returns:
            bool: True if successful
        """
        try:
            # 準備通知內容
            cancellations = all_content.get('cancellation', [])
            news_items = all_content.get('news', [])[:5]  # 只取最新 5 筆
            
            # 如果沒有任何內容，不發送通知
            if not cancellations and not news_items:
                self.logger.info("沒有新內容，跳過通知")
                return True
            
            # 格式化 LINE 訊息（分開發送）
            line_success = True
            if self.line_service and self.line_service.is_enabled():
                # 1. 發送停課通知
                if cancellations:
                    cancellation_msg = self._format_cancellation_message(cancellations)
                    success = self.line_service.send_broadcast_message(cancellation_msg, 'cancellation')
                    if success:
                        self.logger.info("LINE 停課通知發送成功")
                    else:
                        self.logger.error("LINE 停課通知發送失敗")
                        line_success = False
                
                # 2. 發送新聞公告
                if news_items:
                    news_msg = self._format_news_message(news_items)
                    success = self.line_service.send_broadcast_message(news_msg, 'news')
                    if success:
                        self.logger.info("LINE 新聞公告發送成功")
                    else:
                        self.logger.error("LINE 新聞公告發送失敗")
                        line_success = False
            
            # 格式化 Email 訊息（Email 仍然統一發送）
            email_subject, email_body = self._format_email_message(cancellations, news_items)
            
            # 發送 Email 通知
            email_success = True
            if self.email_sender:
                email_success = self.email_sender.send_notification_email(
                    subject=email_subject,
                    body=email_body,
                    is_html=False
                )
                if email_success:
                    self.logger.info("Email 統一通知發送成功")
                else:
                    self.logger.error("Email 統一通知發送失敗")
            
            return line_success and email_success
            
        except Exception as e:
            self.logger.error(f"發送統一通知時發生錯誤: {e}", exc_info=True)
            return False
    
    def _format_cancellation_message(self, cancellations: List[Dict]) -> str:
        """
        格式化停課通知訊息
        
        Args:
            cancellations: 停課通知列表
            
        Returns:
            str: 格式化的停課通知訊息
        """
        message_parts = ["🚫 停課通知\n"]
        
        for item in cancellations:
            course_name = item.get('course_name', '未知課程')
            date = item.get('cancellation_date', '未知日期')
            instructor = item.get('instructor_name', '未知講師')
            message_parts.append(f"• {course_name}")
            message_parts.append(f"  日期：{date}")
            message_parts.append(f"  講師：{instructor}\n")
        
        return "\n".join(message_parts).strip()
    
    def _format_news_message(self, news_items: List[Dict]) -> str:
        """
        格式化新聞公告訊息
        
        Args:
            news_items: 新聞公告列表（最多5筆）
            
        Returns:
            str: 格式化的新聞公告訊息
        """
        message_parts = ["📰 新聞公告\n"]
        
        for i, item in enumerate(news_items, 1):
            title = item.get('title', '未知標題')
            date = item.get('publication_date', item.get('date', '未知日期'))
            url = item.get('url', '')
            
            # 標題和日期
            message_parts.append(f"{i}. {title}")
            message_parts.append(f"   {date}")
            
            # 如果有連結，添加連結
            if url:
                message_parts.append(f"   {url}")
            
            message_parts.append("")  # 空行
        
        return "\n".join(message_parts).strip()
    
    def _format_email_message(self, cancellations: List[Dict], news_items: List[Dict]) -> tuple:
        """
        格式化 Email 訊息
        
        Args:
            cancellations: 停課通知列表
            news_items: 新聞公告列表
            
        Returns:
            tuple: (subject, body)
        """
        subject = f"【最新訊息】佛教教育網站更新通知 - {datetime.now().strftime('%Y-%m-%d')}"
        
        body_parts = [
            "佛教教育網站最新訊息",
            "=" * 60,
            ""
        ]
        
        # 1. 停課通知
        if cancellations:
            body_parts.append("【停課通知】")
            body_parts.append("")
            for item in cancellations:
                course_name = item.get('course_name', '未知課程')
                date = item.get('cancellation_date', '未知日期')
                instructor = item.get('instructor_name', '未知講師')
                location = item.get('location', '未知地點')
                
                body_parts.append(f"課程：{course_name}")
                body_parts.append(f"日期：{date}")
                body_parts.append(f"講師：{instructor}")
                body_parts.append(f"地點：{location}")
                body_parts.append("")
        
        # 2. 新聞公告
        if news_items:
            if cancellations:
                body_parts.append("-" * 60)
                body_parts.append("")
            body_parts.append("【新聞公告】（最新5筆）")
            body_parts.append("")
            for i, item in enumerate(news_items, 1):
                title = item.get('title', '未知標題')
                date = item.get('publication_date', item.get('date', '未知日期'))
                url = item.get('url', '')
                content = item.get('content', '')
                
                body_parts.append(f"{i}. {title}")
                body_parts.append(f"   日期：{date}")
                if url:
                    body_parts.append(f"   連結：{url}")
                if content:
                    # 只顯示前100字
                    preview = content[:100] + "..." if len(content) > 100 else content
                    body_parts.append(f"   內容：{preview}")
                body_parts.append("")
        
        body_parts.extend([
            "=" * 60,
            f"發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "此郵件由系統自動發送，請勿回覆。"
        ])
        
        return subject, "\n".join(body_parts)


# Example usage
def main():
    """測試統一通知服務"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Mock data
    test_content = {
        'cancellation': [
            {
                'course_name': '華嚴經宗通',
                'cancellation_date': '2025-11-15',
                'instructor_name': '某某法師',
                'location': '七樓教室'
            }
        ],
        'news': [
            {
                'title': '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
                'publication_date': '2025-11-13',
                'url': 'https://www.budaedu.org/#/course/123',
                'content': '本會地下室教室(1)，自 2025-12-07 起...'
            },
            {
                'title': '（學院第七屆）學佛基礎進階班－賢愚經課程公告',
                'publication_date': '2025-11-11',
                'url': 'https://www.budaedu.org/#/course/124',
                'content': '本會七樓教室，自 2025-12-06 起...'
            }
        ]
    }
    
    # Test formatting
    service = UnifiedNotificationService(None, None, logger)
    
    # Test cancellation message
    cancellation_msg = service._format_cancellation_message(test_content['cancellation'])
    print("=" * 60)
    print("停課通知訊息預覽：")
    print("=" * 60)
    print(cancellation_msg)
    print("=" * 60)
    print()
    
    # Test news message
    news_msg = service._format_news_message(test_content['news'])
    print("=" * 60)
    print("新聞公告訊息預覽：")
    print("=" * 60)
    print(news_msg)
    print("=" * 60)


if __name__ == "__main__":
    main()
