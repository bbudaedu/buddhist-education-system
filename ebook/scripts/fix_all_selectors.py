#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整修復所有選擇器
基於 Chrome DevTools MCP 的實際檢測結果
"""

import re
from pathlib import Path

# 基於實際網站結構的正確選擇器
CORRECT_SELECTORS = {
    # 書籍頁面 (https://www.budaedu.org/#/books/applicable/chinese)
    'book_card': '.card.overflow-hidden',  # 10 個書籍卡片
    'book_title': 'h5',                     # 書籍標題
    'book_author': 'p',                     # 作者資訊
    'book_image': 'img.card-img-left',      # 書籍封面
    
    # 首頁輪播 (https://www.budaedu.org/#/)
    'carousel_item': '.carousel-item',      # 4 個輪播項目
    'carousel_image': '.carousel-item img', # 輪播圖片
    
    # 首頁最新法寶
    'home_book_card': '.card',              # 13 個卡片（包含書籍）
    'home_book_title': 'h4',                # 首頁書籍標題用 h4
    
    # 等待頁面載入的選擇器
    'wait_selector': '.card.overflow-hidden, .card, .carousel-item',
}

def fix_book_scraper():
    """修復 book_scraper.py"""
    file_path = Path('book_scraper.py')
    if not file_path.exists():
        print(f"✗ {file_path} 不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 修復等待選擇器
    content = re.sub(
        r'EC\.presence_of_element_located\(\(By\.CSS_SELECTOR, "[^"]+"\)\)',
        f'EC.presence_of_element_located((By.CSS_SELECTOR, "{CORRECT_SELECTORS["wait_selector"]}"))',
        content,
        count=1
    )
    
    # 修復選擇器列表（已經在之前修復過，這裡確保正確）
    old_selectors = '''            selectors_to_try = [
                ".card-body",
                ".book-card", 
                ".card",
                "[class*='card']",
                ".book-item",
                ".item"
            ]'''
    
    new_selectors = '''            selectors_to_try = [
                ".card.overflow-hidden",  # 實際的書籍卡片選擇器
                ".card",                   # 通用卡片選擇器
                "[class*='card']",         # 包含 card 的任何元素
                ".book-card",              # 舊版選擇器（備用）
                ".book-item",
                ".item"
            ]'''
    
    if old_selectors in content:
        content = content.replace(old_selectors, new_selectors)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {file_path} 已更新")
        return True
    else:
        print(f"- {file_path} 無需更新")
        return False

def fix_carousel_scraper():
    """修復 carousel_scraper.py"""
    file_path = Path('carousel_scraper.py')
    if not file_path.exists():
        print(f"✗ {file_path} 不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 更新輪播選擇器腳本中的選擇器優先順序
    old_script = '''                const selectors = [
                    '.carousel-item img',
                    '.carousel img', 
                    '.banner img',
                    '.swiper-slide img',
                    '.slide img',
                    '[class*="carousel"] img',
                    '[class*="banner"] img',
                    '[class*="slide"] img'
                ];'''
    
    new_script = '''                const selectors = [
                    '.carousel-item img',      // 實際使用的選擇器（4個輪播）
                    '.carousel-item',          // 輪播項目容器
                    '.carousel img',           // 備用選擇器
                    '[class*="carousel"] img', // 通用輪播圖片
                    '.banner img',
                    '.swiper-slide img',
                    '.slide img',
                    '[class*="banner"] img',
                    '[class*="slide"] img'
                ];'''
    
    if old_script in content:
        content = content.replace(old_script, new_script)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ {file_path} 已更新")
        return True
    else:
        print(f"- {file_path} 無需更新")
        return False

def create_selector_config():
    """建立選擇器配置檔案供參考"""
    config_content = f"""# 網站選擇器配置
# 基於 Chrome DevTools MCP 實際檢測結果
# 檢測日期: 2025-11-10

## 書籍頁面 (https://www.budaedu.org/#/books/applicable/chinese)
- 書籍卡片: `{CORRECT_SELECTORS['book_card']}` (10 個)
- 書籍標題: `{CORRECT_SELECTORS['book_title']}`
- 作者資訊: `{CORRECT_SELECTORS['book_author']}`
- 書籍封面: `{CORRECT_SELECTORS['book_image']}`

## 首頁輪播 (https://www.budaedu.org/#/)
- 輪播項目: `{CORRECT_SELECTORS['carousel_item']}` (4 個)
- 輪播圖片: `{CORRECT_SELECTORS['carousel_image']}`

## 首頁最新法寶
- 卡片容器: `{CORRECT_SELECTORS['home_book_card']}` (13 個)
- 書籍標題: `{CORRECT_SELECTORS['home_book_title']}`

## 等待頁面載入
- 等待選擇器: `{CORRECT_SELECTORS['wait_selector']}`

## 重要提示
1. 這是一個 Vue.js SPA 應用，使用 Hash-based routing (#/)
2. 頁面需要額外的等待時間讓 JavaScript 渲染內容（建議 5-8 秒）
3. 書籍頁面和首頁使用不同的標題標籤（h5 vs h4）
4. 所有 URL 都需要包含 # 符號，例如: `/#/books/applicable/chinese`

## 測試結果
- ✓ 書籍卡片選擇器已驗證
- ✓ 輪播選擇器已驗證
- ✓ 頁面載入等待已驗證
"""
    
    with open('SELECTOR_CONFIG.md', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✓ 已建立 SELECTOR_CONFIG.md 配置文件")

def main():
    """主要修復流程"""
    print("=" * 60)
    print("完整修復所有選擇器")
    print("基於 Chrome DevTools MCP 實際檢測結果")
    print("=" * 60)
    print()
    
    updated = []
    
    # 修復各個檔案
    if fix_book_scraper():
        updated.append('book_scraper.py')
    
    if fix_carousel_scraper():
        updated.append('carousel_scraper.py')
    
    # 建立配置文件
    create_selector_config()
    
    print()
    print("=" * 60)
    if updated:
        print(f"✓ 完成！已更新 {len(updated)} 個檔案")
        for f in updated:
            print(f"  - {f}")
    else:
        print("✓ 所有檔案已是最新狀態")
    print("=" * 60)
    
    print("\n建議測試步驟:")
    print("1. 執行單次監控測試:")
    print("   python comprehensive_monitoring_integration.py start --interval 0")
    print()
    print("2. 檢查日誌輸出，確認能找到元素")
    print()
    print("3. 如果成功，啟動持續監控:")
    print("   start_monitoring.bat")

if __name__ == "__main__":
    main()
