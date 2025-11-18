#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復網站選擇器
根據實際的網站結構更新所有爬蟲的選擇器
"""

import re
import os
from pathlib import Path

# 新的選擇器配置
NEW_SELECTORS = {
    # 書籍頁面選擇器
    'book_card': '.card.overflow-hidden',
    'book_title': 'h5',
    'book_author': 'p',
    'book_image': 'img.card-img-left',
    
    # 新聞/公告選擇器（需要實際測試後確認）
    'news_item': '.card',
    'news_title': 'h5',
    
    # 輪播選擇器
    'carousel_item': '.carousel-item',
    
    # 通用等待選擇器
    'wait_for_content': '.card, .container',
}

def update_file_selectors(file_path, updates):
    """更新檔案中的選擇器"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        for old_pattern, new_value in updates:
            if old_pattern in content:
                content = content.replace(old_pattern, new_value)
                modified = True
                print(f"  ✓ 更新: {old_pattern} → {new_value}")
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"  ✗ 錯誤: {e}")
        return False

def main():
    """主要修復流程"""
    print("=" * 60)
    print("修復網站選擇器")
    print("=" * 60)
    
    # 需要更新的檔案和對應的修改
    files_to_update = {
        'book_scraper.py': [
            # 這些是常見的錯誤選擇器模式
            ("'.book-card'", "'.card.overflow-hidden'"),
            ('".book-card"', '".card.overflow-hidden"'),
            ("'div.book-card'", "'div.card.overflow-hidden'"),
            ('"div.book-card"', '"div.card.overflow-hidden"'),
        ],
        'enhanced_web_scraper.py': [
            ("'.book-card'", "'.card.overflow-hidden'"),
            ('".book-card"', '".card.overflow-hidden"'),
            ("'div.book-card'", "'div.card.overflow-hidden'"),
            ('"div.book-card"', '"div.card.overflow-hidden"'),
        ],
        'carousel_scraper.py': [
            # 輪播相關的選擇器可能也需要更新
        ],
        'news_processor.py': [
            ("'.news-item'", "'.card'"),
            ('".news-item"', '".card"'),
        ],
    }
    
    updated_files = []
    
    for filename, updates in files_to_update.items():
        file_path = Path(filename)
        if file_path.exists():
            print(f"\n處理檔案: {filename}")
            if update_file_selectors(file_path, updates):
                updated_files.append(filename)
                print(f"  ✓ {filename} 已更新")
            else:
                print(f"  - {filename} 無需更新")
        else:
            print(f"  ⊘ {filename} 不存在")
    
    print("\n" + "=" * 60)
    if updated_files:
        print(f"✓ 完成！已更新 {len(updated_files)} 個檔案")
        print("更新的檔案:")
        for f in updated_files:
            print(f"  - {f}")
    else:
        print("沒有檔案需要更新")
    print("=" * 60)
    
    # 建議下一步
    print("\n建議下一步:")
    print("1. 執行診斷工具確認: python diagnose_website.py")
    print("2. 測試單一爬蟲: python test_carousel_scraper.py")
    print("3. 執行完整測試: python start_monitoring.bat")

if __name__ == "__main__":
    main()
