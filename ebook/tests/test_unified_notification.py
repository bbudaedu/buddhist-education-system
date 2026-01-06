#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試統一通知服務
"""

import logging
import json
from unified_notification_service import UnifiedNotificationService
from line_notification_service import LineNotificationService
from email_sender import EmailSender

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """測試統一通知"""
    try:
        # 載入配置
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 初始化服務
        line_service = LineNotificationService(config, logger)
        email_sender = EmailSender(config, logger)
        unified_service = UnifiedNotificationService(line_service, email_sender, logger)
        
        # 準備測試資料
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
                    'id': 1,
                    'content_type': 'news',
                    'title': '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
                    'publication_date': '2025-11-13',
                    'url': 'https://publish.budaedu.org/laravel/public/front/lecturers/392',
                    'content': '本會地下室教室(1)，自 2025-12-07 起...'
                },
                {
                    'id': 2,
                    'content_type': 'news',
                    'title': '（學院第七屆）學佛基礎進階班－賢愚經課程公告',
                    'publication_date': '2025-11-11',
                    'url': 'https://publish.budaedu.org/laravel/public/front/lecturers/176',
                    'content': '本會七樓教室，自 2025-12-06 起...'
                },
                {
                    'id': 3,
                    'content_type': 'news',
                    'title': '緣起讚課程公告',
                    'publication_date': '2025-11-07',
                    'url': 'https://publish.budaedu.org/laravel/public/front/lecturers/366',
                    'content': '本會三學教室(3)，自 2025-11-13 起...'
                },
                {
                    'id': 4,
                    'content_type': 'news',
                    'title': '「略述華嚴經三聖圓融觀」及「心要法門」 課程公告',
                    'publication_date': '2025-11-07',
                    'url': 'https://publish.budaedu.org/laravel/public/front/lecturers/357',
                    'content': '本會三學教室(2)，自 2025-12-09 起...'
                },
                {
                    'id': 5,
                    'content_type': 'news',
                    'title': '阿彌陀佛四十八大願課程公告',
                    'publication_date': '2025-11-03',
                    'url': 'https://publish.budaedu.org/laravel/public/front/lecturers/378',
                    'content': '本會三樓講堂，自 2025-12-03 起...'
                }
            ]
        }
        
        logger.info("=" * 60)
        logger.info("測試統一通知服務")
        logger.info("=" * 60)
        
        # 發送統一通知
        success = unified_service.send_unified_notification(test_content)
        
        if success:
            logger.info("✅ 統一通知發送成功！")
        else:
            logger.error("❌ 統一通知發送失敗！")
        
        logger.info("=" * 60)
        
        return success
        
    except Exception as e:
        logger.error(f"測試失敗: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
