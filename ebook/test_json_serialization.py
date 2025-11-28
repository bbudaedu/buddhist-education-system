#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LINE 通知 JSON 序列化修复
"""

import json
from datetime import date, datetime

# 模拟 make_serializable 函数
def make_serializable(obj):
    """Convert datetime/date objects to ISO format strings"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    return obj

# 测试数据 - 包含 date 对象
test_data = {
    'cancellations': [
        {
            'courseName': '華嚴經宗通',
            'date': date(2025, 11, 15),  # date 对象
            'instructor': '某某法師',
            'location': '七樓教室'
        }
    ],
    'news': [
        {
            'title': '小菩薩的慈悲畫室－佛法讀經與護生繪畫班 課程公告',
            'date': date(2025, 11, 13),  # date 对象 
            'url': 'https://www.budaedu.org/#/course/123'
        }
    ],
    'newBooks': [
        {
            'title': '淨土要義',
            'author': '某某法師'
        }
    ]
}

print("=== 测试 JSON 序列化 ===\n")

print("1. 原始数据（包含 date 对象）:")
print(f"   cancellations[0]['date'] = {test_data['cancellations'][0]['date']}")
print(f"   类型: {type(test_data['cancellations'][0]['date'])}\n")

print("2. 尝试直接 JSON 序列化（应该失败）:")
try:
    json_str = json.dumps(test_data)
    print("   ✗ 错误：应该失败但成功了！")
except TypeError as e:
    print(f"   ✓ 预期的错误: {e}\n")

print("3. 使用 make_serializable 处理后:")
serialized_data = make_serializable(test_data)
print(f"   cancellations[0]['date'] = {serialized_data['cancellations'][0]['date']}")
print(f"   类型: {type(serialized_data['cancellations'][0]['date'])}\n")

print("4. JSON 序列化测试:")
try:
    json_str = json.dumps(serialized_data, indent=2,ensure_ascii=False)
    print("   ✓ JSON 序列化成功！\n")
    print("   序列化结果预览（前200字符）:")
    print(f"   {json_str[:200]}...\n")
except TypeError as e:
    print(f"   ✗ JSON 序列化失败: {e}\n")

print("=== 测试完成 ===")
