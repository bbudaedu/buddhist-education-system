#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新書通知功能
Test New Book Notification Feature
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_notification_service import UnifiedNotificationService
from line_notification_service import LineNotificationService
from email_sender import EmailSender
from config_manager import ConfigManager

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_new_book_notification():
    """測試新書通知"""
    logger.info("=" * 60)
    logger.info("測試 1: 新書通知")
    logger.info("=" * 60)
    
    # 載入配置
    config_manager = ConfigManager("config.json", logger)
    config = config_manager.get_config()
    
    # 初始化服務
    line_service = LineNotificationService(config, logger)
    email_sender = EmailSender(config, logger)
    unified_service = UnifiedNotificationService(line_service, email_sender, logger)
    
    # 測試資料
    test_content = {
        'cancellation': [],
        'news': [],
        'new_books': [
            {
                'title': '金剛經講記',
                'author': '淨空法師'
            },
            {
                'title': '楞嚴經淺釋',
                'author': '宣化上人'
            }
        ]
    }
    
    # 發送通知
    logger.info("發送新書通知...")
    success = unified_service.send_unified_notification(test_content)
    
    if success:
        logger.info("✅ 新書通知發送成功")
    else:
        logger.error("❌ 新書通知發送失敗")
    
    return success

def test_mixed_notification():
    """測試混合通知（停課 + 新書 + 新聞）"""
    logger.info("\n" + "=" * 60)
    logger.info("測試 2: 混合通知（停課 + 新書 + 新聞）")
    logger.info("=" * 60)
    
    # 載入配置
    config_manager = ConfigManager("config.json", logger)
    config = config_manager.get_config()
    
    # 初始化服務
    line_service = LineNotificationService(config, logger)
    email_sender = EmailSender(config, logger)
    unified_service = UnifiedNotificationService(line_service, email_sender, logger)
    
    # 測試資料
    test_content = {
        'cancellation': [
            {
                'course_name': '華嚴經宗通',
                'cancellation_date': '2025-11-20',
                'instructor_name': '某某法師',
                'location': '七樓教室'
            }
        ],
        'news': [
            {
                'title': '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
                'publication_date': '2025-11-13',
                'url': 'https://www.budaedu.org/#/course/123'
            }
        ],
        'new_books': [
            {
                'title': '金剛經講記',
                'author': '淨空法師'
            },
            {
                'title': '楞嚴經淺釋',
                'author': '宣化上人'
            }
        ]
    }
    
    # 發送通知
    logger.info("發送混合通知...")
    success = unified_service.send_unified_notification(test_content)
    
    if success:
        logger.info("✅ 混合通知發送成功")
    else:
        logger.error("❌ 混合通知發送失敗")
    
    return success

def test_message_formatting():
    """測試訊息格式化"""
    logger.info("\n" + "=" * 60)
    logger.info("測試 3: 訊息格式化預覽")
    logger.info("=" * 60)
    
    # 載入配置
    config_manager = ConfigManager("config.json", logger)
    config = config_manager.get_config()
    
    # 初始化服務
    line_service = LineNotificationService(config, logger)
    unified_service = UnifiedNotificationService(line_service, None, logger)
    
    # 測試資料
    new_books = [
        {
            'title': '金剛經講記',
            'author': '淨空法師'
        },
        {
            'title': '楞嚴經淺釋',
            'author': '宣化上人'
        },
        {
            'title': '地藏菩薩本願經白話解釋',
            'author': '黃智海居士'
        }
    ]
    
    # 格式化訊息
    message = unified_service._format_new_books_message(new_books)
    
    logger.info("新書通知訊息預覽：")
    logger.info("-" * 60)
    print(message)
    logger.info("-" * 60)
    
    return True

def main():
    """主測試函數"""
    try:
        logger.info("開始測試新書通知功能\n")
        
        # 測試 1: 純新書通知
        result1 = test_new_book_notification()
        
        # 測試 2: 混合通知
        result2 = test_mixed_notification()
        
        # 測試 3: 訊息格式化
        result3 = test_message_formatting()
        
        # 總結
        logger.info("\n" + "=" * 60)
        logger.info("測試總結")
        logger.info("=" * 60)
        logger.info(f"測試 1 (新書通知): {'✅ 通過' if result1 else '❌ 失敗'}")
        logger.info(f"測試 2 (混合通知): {'✅ 通過' if result2 else '❌ 失敗'}")
        logger.info(f"測試 3 (訊息格式化): {'✅ 通過' if result3 else '❌ 失敗'}")
        
        if result1 and result2 and result3:
            logger.info("\n🎉 所有測試通過！")
            return 0
        else:
            logger.error("\n⚠️ 部分測試失敗")
            return 1
            
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
