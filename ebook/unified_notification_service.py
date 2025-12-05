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
        支援兩種模式：
        1. 傳統模式：分開發送文字訊息（向後相容）
        2. Flex Message 模式：發送結構化資料，由 LINE Bot 創建 Flex Carousel
        
        Args:
            all_content: 所有內容 {'cancellation': [...], 'news': [...], 'new_books': [...], ...}
            
        Returns:
            bool: True if successful
        """
        try:
            # 準備通知內容
            cancellations = all_content.get('cancellation', [])
            news_items = all_content.get('news', [])[:5]  # 只取最新 5 筆
            new_books = all_content.get('new_books', [])  # 新書通知
            new_videos = all_content.get('new_videos', [])[:5]  # 最新影音
            
            # 如果沒有任何內容，不發送通知
            if not cancellations and not news_items and not new_books and not new_videos:
                self.logger.info("沒有新內容，跳過通知")
                return True
            
            # 發送 LINE 通知（使用 Flex Message 整合模式）
            line_success = True
            if self.line_service and self.line_service.is_enabled():
                line_success = self._send_integrated_line_notification(
                    cancellations, news_items, new_books, new_videos
                )
            
            # 格式化 Email 訊息（HTML 格式，包含影音）
            email_subject, email_body, is_html = self._format_email_message(
                cancellations, news_items, new_books, new_videos
            )
            
            # 發送 Email 通知
            email_success = True
            if self.email_sender:
                email_success = self.email_sender.send_notification_email(
                    subject=email_subject,
                    body=email_body,
                    is_html=is_html
                )
                if email_success:
                    self.logger.info("Email 統一通知發送成功")
                else:
                    self.logger.error("Email 統一通知發送失敗")
            
            return line_success and email_success
            
        except Exception as e:
            self.logger.error(f"發送統一通知時發生錯誤: {e}", exc_info=True)
            return False
    
    def _send_integrated_line_notification(self, cancellations: List[Dict], 
                                          news_items: List[Dict], 
                                          new_books: List[Dict],
                                          new_videos: List[Dict] = None) -> bool:
        """
        發送整合的 LINE 通知（使用 Flex Message）
        
        Args:
            cancellations: 停課通知列表
            news_items: 新聞公告列表
            new_books: 新書列表
            new_videos: 影音列表
            
        Returns:
            bool: True if successful
        """
        try:
            # 準備結構化資料
            structured_data = {}
            
            # 轉換新書資料（包含佛卡）
            if new_books:
                structured_data['newBooks'] = [
                    {
                        'title': book.get('title', '未知書名'),
                        'author': book.get('author', ''),
                        'url': book.get('url', ''),  # 加入官網連結
                        'coverUrl': book.get('coverUrl', book.get('imageUrl', '')),
                        'source': book.get('source', 'books')  # books 或 buddha_cards
                    }
                    for book in new_books
                ]
            
            # 轉換新聞資料
            if news_items:
                structured_data['news'] = [
                    {
                        'title': item.get('title', '未知標題'),
                        'date': item.get('publishDate', item.get('publication_date', item.get('date', ''))),
                        'url': item.get('url', ''),
                        'content': item.get('content', '')[:100] if item.get('content') else ''
                    }
                    for item in news_items
                ]
            
            # 轉換停課資料 - 使用正確的 API 欄位名稱
            if cancellations:
                structured_data['cancellations'] = [
                    {
                        'courseName': item.get('courseName', item.get('course_name', '未知課程')),
                        'cancelDate': item.get('cancelDate', item.get('cancellation_date', '未知日期')),
                        'instructor': item.get('instructor', item.get('instructor_name', '')),
                        'time': item.get('time', ''),
                        'url': item.get('url', 'https://www.budaedu.org/#/bulletins/course-cancel')
                    }
                    for item in cancellations
                ]
            
            # 轉換影音資料
            if new_videos:
                structured_data['videos'] = [
                    {
                        'id': item.get('id', ''),
                        'title': item.get('title', '未知標題'),
                        'instructor': item.get('instructor', ''),
                        'episodeCount': item.get('episodeCount', item.get('episode_count', 0)),
                        'url': item.get('url', '')
                    }
                    for item in new_videos
                ]
            
            # 發送整合通知
            success = self.line_service.send_integrated_notification(structured_data)
            
            if success:
                self.logger.info("LINE 整合通知發送成功（Flex Carousel）")
            else:
                self.logger.error("LINE 整合通知發送失敗")
            
            return success
            
        except Exception as e:
            self.logger.error(f"發送整合 LINE 通知時發生錯誤: {e}", exc_info=True)
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
    
    def _format_new_books_message(self, new_books: List[Dict]) -> str:
        """
        格式化新書通知訊息
        
        Args:
            new_books: 新書列表
            
        Returns:
            str: 格式化的新書通知訊息
        """
        message_parts = ["📚 新書上架通知\n"]
        
        for i, book in enumerate(new_books, 1):
            title = book.get('title', '未知書名')
            author = book.get('author', '未知作者')
            
            message_parts.append(f"{i}. {title}")
            message_parts.append(f"   作者：{author}")
            message_parts.append("")  # 空行
        
        return "\n".join(message_parts).strip()
    
    def _format_email_message(self, cancellations: List[Dict], news_items: List[Dict], 
                              new_books: List[Dict], new_videos: List[Dict] = None) -> tuple:
        """
        格式化 Email 訊息 (HTML 格式)
        
        Args:
            cancellations: 停課通知列表
            news_items: 新聞公告列表
            new_books: 新書列表
            new_videos: 影音列表
            
        Returns:
            tuple: (subject, body, is_html)
        """
        subject = f"【最新訊息】佛教教育網站更新通知 - {datetime.now().strftime('%Y-%m-%d')}"
        
        html_parts = [
            "<html><body>",
            "<h2 style='color:#2c3e50;'>佛教教育網站最新訊息</h2>",
            "<hr style='border:1px solid #bdc3c7;'>"
        ]
        
        # 1. 停課通知
        if cancellations:
            html_parts.append("<h3 style='color:#e74c3c;'>🚫 停課通知</h3>")
            html_parts.append("<ul>")
            for item in cancellations:
                course_name = item.get('courseName', item.get('course_name', '未知課程'))
                date = item.get('cancelDate', item.get('cancellation_date', '未知日期'))
                if date and len(date) > 10:
                    date = date[:10]
                instructor = item.get('instructor', item.get('instructor_name', '未知講師'))
                time_slot = item.get('time', '')
                url = item.get('url', 'https://www.budaedu.org/#/bulletins/course-cancel')
                
                html_parts.append(f"<li><strong>{course_name}</strong><br/>")
                html_parts.append(f"日期：{date} | 講師：{instructor}")
                if time_slot:
                    html_parts.append(f" | 時間：{time_slot}")
                html_parts.append(f" <a href='{url}'>更多資訊</a></li>")
            html_parts.append("</ul>")
        
        # 2. 新書上架
        if new_books:
            html_parts.append("<h3 style='color:#27ae60;'>📚 新書上架</h3>")
            html_parts.append("<ul>")
            for book in new_books:
                title = book.get('title', '未知書名')
                author = book.get('author', '')
                url = book.get('url', '')
                
                html_parts.append(f"<li><strong>{title}</strong>")
                if author and author != '-':
                    html_parts.append(f"<br/>作者：{author}")
                if url:
                    html_parts.append(f" <a href='{url}'>更多資訊</a>")
                html_parts.append("</li>")
            html_parts.append("</ul>")
        
        # 3. 新聞公告
        if news_items:
            html_parts.append("<h3 style='color:#3498db;'>📰 新聞公告</h3>")
            html_parts.append("<ul>")
            for item in news_items:
                title = item.get('title', '未知標題')
                date = item.get('publication_date', item.get('date', ''))
                url = item.get('url', '')
                
                html_parts.append(f"<li><strong>{title}</strong>")
                if date:
                    html_parts.append(f" ({date})")
                if url:
                    html_parts.append(f" <a href='{url}'>更多資訊</a>")
                html_parts.append("</li>")
            html_parts.append("</ul>")
        
        # 4. 最新影音
        if new_videos:
            html_parts.append("<h3 style='color:#9b59b6;'>🎥 最新影音</h3>")
            html_parts.append("<ul>")
            for video in new_videos:
                title = video.get('title', '未知標題')
                instructor = video.get('instructor', '')
                episode_count = video.get('episodeCount', video.get('episode_count', 0))
                url = video.get('url', '')
                
                html_parts.append(f"<li><strong>{title}</strong>")
                if instructor:
                    html_parts.append(f"<br/>講師：{instructor}")
                if episode_count:
                    html_parts.append(f" | 共 {episode_count} 集")
                if url:
                    html_parts.append(f" <a href='{url}'>更多資訊</a>")
                html_parts.append("</li>")
            html_parts.append("</ul>")
        
        html_parts.extend([
            "<hr style='border:1px solid #bdc3c7;'>",
            f"<p style='color:#7f8c8d;font-size:12px;'>發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>",
            "此郵件由系統自動發送，請勿回覆。</p>",
            "</body></html>"
        ])
        
        return subject, "".join(html_parts), True


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
