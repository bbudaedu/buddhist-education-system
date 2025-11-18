#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷通知發送問題
"""

import json
import logging
from datetime import datetime

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

print("=" * 60)
print("診斷通知發送")
print("=" * 60)
print()

# 測試 1: 只有停課通知
print("測試 1: 只發送停課通知")
print("-" * 60)
test1 = {
    'cancellation': [
        {
            'course_name': '【測試】華嚴經宗通',
            'cancellation_date': '2025-11-20',
            'instructor_name': '測試法師',
            'location': '七樓教室'
        }
    ],
    'news': []
}
success1 = unified_service.send_unified_notification(test1)
print(f"結果: {'✅ 成功' if success1 else '❌ 失敗'}")
print()

# 測試 2: 只有新聞通知
print("測試 2: 只發送新聞通知")
print("-" * 60)
test2 = {
    'cancellation': [],
    'news': [
        {
            'title': '【測試】小菩薩的慈悲畫室課程公告',
            'publication_date': '2025-11-14',
            'url': 'https://www.budaedu.org/#/course/test123'
        }
    ]
}
success2 = unified_service.send_unified_notification(test2)
print(f"結果: {'✅ 成功' if success2 else '❌ 失敗'}")
print()

# 測試 3: 兩者都有
print("測試 3: 發送停課 + 新聞")
print("-" * 60)
test3 = {
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
            'url': 'https://www.budaedu.org/#/course/test123'
        }
    ]
}
success3 = unified_service.send_unified_notification(test3)
print(f"結果: {'✅ 成功' if success3 else '❌ 失敗'}")
print()

# 測試 4: 兩者都空
print("測試 4: 沒有任何內容")
print("-" * 60)
test4 = {
    'cancellation': [],
    'news': []
}
success4 = unified_service.send_unified_notification(test4)
print(f"結果: {'✅ 成功' if success4 else '❌ 失敗'} (應該跳過)")
print()

print("=" * 60)
print("診斷完成")
print("=" * 60)
print()
print("📊 總結：")
print(f"  測試 1 (只有停課): {'✅' if success1 else '❌'}")
print(f"  測試 2 (只有新聞): {'✅' if success2 else '❌'}")
print(f"  測試 3 (停課+新聞): {'✅' if success3 else '❌'}")
print(f"  測試 4 (都沒有): {'✅' if success4 else '❌'}")
print()
print("💡 提示：")
print("  - 如果測試 1 成功，表示停課通知可以正常發送")
print("  - 如果測試 2 成功，表示新聞通知可以正常發送")
print("  - 檢查 Node.js 日誌確認用戶是否收到通知")
print("  - 用戶需要訂閱對應類型才能收到通知")
