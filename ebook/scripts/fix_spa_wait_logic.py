#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正 SPA 等待邏輯
為 Vue.js 單頁應用增加適當的等待時間
"""

import re

def fix_carousel_scraper():
    """修正 carousel_scraper.py 的等待邏輯"""
    
    file_path = "carousel_scraper.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 navigate_to_page 方法並增加 SPA 等待時間
    # 搜尋 time.sleep 的部分並增加等待時間
    
    # 修正 1: 增加頁面載入後的等待時間
    pattern1 = r'(self\.driver\.get\(url\))\s*\n\s*(# Wait for page to load)'
    replacement1 = r'\1\n            \2\n            time.sleep(5)  # Wait for Vue.js SPA to render'
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        print("✓ 已增加 SPA 渲染等待時間")
    
    # 修正 2: 在 extract_carousel_banners 中增加等待
    pattern2 = r'(def extract_carousel_banners.*?:.*?\n.*?""".*?""")\s*\n\s*(try:)'
    replacement2 = r'\1\n        # Wait for Vue.js to render carousel\n        time.sleep(3)\n        \2'
    
    if re.search(pattern2, content, re.DOTALL):
        content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)
        print("✓ 已在 extract_carousel_banners 增加等待")
    
    # 寫回檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ {file_path} 修正完成")

def fix_news_processor():
    """修正 news_processor.py 的等待邏輯"""
    
    file_path = "news_processor.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在導航後增加等待
        pattern = r'(self\.driver\.get\(.*?\))\s*\n'
        replacement = r'\1\n            time.sleep(5)  # Wait for Vue.js SPA\n'
        
        if 'time.sleep(5)  # Wait for Vue.js SPA' not in content:
            content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ {file_path} 修正完成")
        else:
            print(f"○ {file_path} 已經有等待邏輯")
            
    except FileNotFoundError:
        print(f"✗ {file_path} 不存在")

def fix_media_processor():
    """修正 media_processor.py 的等待邏輯"""
    
    file_path = "media_processor.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在導航後增加等待
        if 'time.sleep(5)  # Wait for Vue.js SPA' not in content:
            pattern = r'(self\.driver\.get\(.*?\))\s*\n'
            replacement = r'\1\n            time.sleep(5)  # Wait for Vue.js SPA\n'
            content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ {file_path} 修正完成")
        else:
            print(f"○ {file_path} 已經有等待邏輯")
            
    except FileNotFoundError:
        print(f"✗ {file_path} 不存在")

def fix_bulletin_scraper():
    """修正 bulletin_scraper.py 的等待邏輯"""
    
    file_path = "bulletin_scraper.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在導航後增加等待
        if 'time.sleep(5)  # Wait for Vue.js SPA' not in content:
            pattern = r'(self\.driver\.get\(.*?\))\s*\n'
            replacement = r'\1\n            time.sleep(5)  # Wait for Vue.js SPA\n'
            content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ {file_path} 修正完成")
        else:
            print(f"○ {file_path} 已經有等待邏輯")
            
    except FileNotFoundError:
        print(f"✗ {file_path} 不存在")

def main():
    """主程式"""
    print("="*60)
    print("修正 SPA 等待邏輯")
    print("="*60)
    print()
    
    print("正在修正各個爬蟲模組...")
    print()
    
    fix_carousel_scraper()
    fix_news_processor()
    fix_media_processor()
    fix_bulletin_scraper()
    
    print()
    print("="*60)
    print("修正完成！")
    print("="*60)
    print()
    print("建議：")
    print("1. 重新執行監控系統測試")
    print("2. 如果還是找不到元素，可能需要增加更長的等待時間")
    print("3. 或使用 WebDriverWait 等待特定元素出現")

if __name__ == "__main__":
    main()
