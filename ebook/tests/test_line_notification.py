#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LINE Notification Integration
測試 LINE 通知整合
"""

import logging
from datetime import datetime
from line_notification_service import LineNotificationService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_line_notification():
    """
    Test LINE notification service
    """
    try:
        # Configuration
        config = {
            'line_bot': {
                'enabled': True,
                'api_url': 'http://localhost:3000/api/notifications/website-monitoring',
                'api_key': ''
            },
            'website_monitoring': {
                'notifications': {
                    'line_enabled': True
                }
            }
        }
        
        # Initialize service
        logger.info("Initializing LINE notification service...")
        service = LineNotificationService(config, logger)
        
        if not service.is_enabled():
            logger.error("LINE notification service is not enabled")
            return False
        
        # Test 1: Immediate alert
        logger.info("\n=== Test 1: Immediate Alert ===")
        test_alerts = [
            {
                'content_type': 'news',
                'title': '【測試】重要公告',
                'publication_date': datetime.now().strftime('%Y-%m-%d'),
                'content': '這是一則測試新聞內容'
            },
            {
                'content_type': 'cancellation',
                'course_name': '測試課程',
                'cancellation_date': datetime.now().strftime('%Y-%m-%d'),
                'instructor_name': '測試講師'
            }
        ]
        
        success = service.send_immediate_alert(test_alerts)
        logger.info(f"Immediate alert result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test 2: Daily summary
        logger.info("\n=== Test 2: Daily Summary ===")
        test_summary = [
            {
                'content_type': 'news',
                'title': '測試新聞 1',
                'publication_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'content_type': 'news',
                'title': '測試新聞 2',
                'publication_date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'content_type': 'carousel',
                'banner_title': '測試橫幅',
                'course_name': '測試課程'
            },
            {
                'content_type': 'media',
                'course_title': '測試影片',
                'speaker_name': '測試講師'
            }
        ]
        
        success = service.send_daily_summary(test_summary)
        logger.info(f"Daily summary result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test 3: Simple broadcast
        logger.info("\n=== Test 3: Simple Broadcast ===")
        test_message = "🧪 測試訊息\n\n這是一則來自網站監控系統的測試通知。\n\n⏰ " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        success = service.send_broadcast_message(test_message)
        logger.info(f"Broadcast result: {'✅ Success' if success else '❌ Failed'}")
        
        logger.info("\n=== All Tests Completed ===")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Starting LINE notification integration test...")
    logger.info("Make sure the LINE bot server is running on http://localhost:3000")
    logger.info("")
    
    success = test_line_notification()
    
    if success:
        logger.info("\n✅ All tests completed successfully!")
    else:
        logger.error("\n❌ Tests failed!")
