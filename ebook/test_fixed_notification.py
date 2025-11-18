#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的通知系統
"""

import json
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 載入配置
with open('ebook/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化服務
from line_notification_service import LineNotificationService
from unified_notification_service import UnifiedNotificationService

line_service = LineNotificationService(config, logger)
unified_service = UnifiedNotificationService(line_service, None, logger)

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

print("=" * 60)
print("測試修復後的通知系統")
print("=" * 60)
print()

# 發送通知
success = unified_service.send_unified_notification(test_content)

if success:
    print("\n✅ 通知發送成功！")
    print("\n請檢查：")
    print("1. LINE bot 是否收到兩則訊息（停課通知 + 新聞公告）")
    print("2. Node.js 伺服器日誌是否顯示正確的 contentType")
else:
    print("\n❌ 通知發送失敗")

print("=" * 60)
