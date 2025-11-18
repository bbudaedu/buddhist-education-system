#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試停課通知發送流程
"""

import sys
import json
import logging
from datetime import datetime
from unified_notification_service import UnifiedNotificationService
from line_notification_service import LINENotificationService

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """載入配置"""
    try:
        with open('ebook/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"載入配置失敗: {e}")
        return None

def test_cancellation_notification():
    """測試停課通知"""
    logger.info("=" * 60)
    logger.info("開始測試停課通知發送")
    logger.info("=" * 60)
    
    # 載入配置
    config = load_config()
    if not config:
        logger.error("無法載入配置，測試終止")
        return False
    
    # 初始化 LINE 服務
    line_service = LINENotificationService(config, logger)
    
    if not line_service.is_enabled():
        logger.error("LINE 通知服務未啟用")
        return False
    
    # 準備測試資料
    test_content = {
        'cancellation': [
            {
                'course_name': '【測試】華嚴經宗通',
                'cancellation_date': '2025-11-20',
                'instructor_name': '測試法師',
                'location': '七樓教室'
            }
        ],
        'news': []  # 不發送新聞
    }
    
    # 初始化統一通知服務
    unified_service = UnifiedNotificationService(line_service, None, logger)
    
    # 發送通知
    logger.info("發送停課通知...")
    success = unified_service.send_unified_notification(test_content)
    
    if success:
        logger.info("✅ 停課通知發送成功")
    else:
        logger.error("❌ 停課通知發送失敗")
    
    logger.info("=" * 60)
    return success

def test_news_notification():
    """測試新聞通知"""
    logger.info("=" * 60)
    logger.info("開始測試新聞通知發送")
    logger.info("=" * 60)
    
    # 載入配置
    config = load_config()
    if not config:
        logger.error("無法載入配置，測試終止")
        return False
    
    # 初始化 LINE 服務
    line_service = LINENotificationService(config, logger)
    
    if not line_service.is_enabled():
        logger.error("LINE 通知服務未啟用")
        return False
    
    # 準備測試資料
    test_content = {
        'cancellation': [],  # 不發送停課
        'news': [
            {
                'title': '【測試】小菩薩的慈悲畫室課程公告',
                'publication_date': '2025-11-14',
                'url': 'https://www.budaedu.org/#/course/test123',
                'content': '這是測試新聞內容...'
            }
        ]
    }
    
    # 初始化統一通知服務
    unified_service = UnifiedNotificationService(line_service, None, logger)
    
    # 發送通知
    logger.info("發送新聞通知...")
    success = unified_service.send_unified_notification(test_content)
    
    if success:
        logger.info("✅ 新聞通知發送成功")
    else:
        logger.error("❌ 新聞通知發送失敗")
    
    logger.info("=" * 60)
    return success

def test_mixed_notification():
    """測試混合通知（停課 + 新聞）"""
    logger.info("=" * 60)
    logger.info("開始測試混合通知發送")
    logger.info("=" * 60)
    
    # 載入配置
    config = load_config()
    if not config:
        logger.error("無法載入配置，測試終止")
        return False
    
    # 初始化 LINE 服務
    line_service = LINENotificationService(config, logger)
    
    if not line_service.is_enabled():
        logger.error("LINE 通知服務未啟用")
        return False
    
    # 準備測試資料
    test_content = {
        'cancellation': [
            {
                'course_name': '【測試】華嚴經宗通',
                'cancellation_date': '2025-11-20',
                'instructor_name': '測試法師',
                'location': '七樓教室'
            }
        ],
        'news': [
            {
                'title': '【測試】小菩薩的慈悲畫室課程公告',
                'publication_date': '2025-11-14',
                'url': 'https://www.budaedu.org/#/course/test123',
                'content': '這是測試新聞內容...'
            }
        ]
    }
    
    # 初始化統一通知服務
    unified_service = UnifiedNotificationService(line_service, None, logger)
    
    # 發送通知
    logger.info("發送混合通知...")
    success = unified_service.send_unified_notification(test_content)
    
    if success:
        logger.info("✅ 混合通知發送成功")
    else:
        logger.error("❌ 混合通知發送失敗")
    
    logger.info("=" * 60)
    return success

if __name__ == "__main__":
    print("\n選擇測試項目：")
    print("1. 測試停課通知")
    print("2. 測試新聞通知")
    print("3. 測試混合通知（停課 + 新聞）")
    print("4. 全部測試")
    
    choice = input("\n請輸入選項 (1-4): ").strip()
    
    if choice == '1':
        test_cancellation_notification()
    elif choice == '2':
        test_news_notification()
    elif choice == '3':
        test_mixed_notification()
    elif choice == '4':
        print("\n執行全部測試...\n")
        test_cancellation_notification()
        print("\n")
        test_news_notification()
        print("\n")
        test_mixed_notification()
    else:
        print("無效的選項")
        sys.exit(1)
