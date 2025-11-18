#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速新聞測試 - 只提取預覽資訊到 downloads
"""

import os
import json
from datetime import datetime
from book_scraper import BookScraper
from selenium.webdriver.common.by import By
import logging


# 簡單的日誌設定
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

print("=" * 60)
print("快速新聞測試")
print("=" * 60)

# 配置
chromedriver_path = "chromedriver-win64\\chromedriver.exe"
download_dir = "downloads"
news_url = "https://www.budaedu.org/#/bulletins/"

# 初始化
scraper = BookScraper(chromedriver_path, download_dir, logger)
scraper.setup_driver()
scraper.navigate_to_website(news_url)
scraper.wait_for_page_load()

# 找新聞連結
news_links = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href='javascript:void(0)']")
print(f"\n找到 {len(news_links)} 則新聞\n")

# 提取資訊
news_items = []
for i, link in enumerate(news_links, 1):
    try:
        # 獲取連結文字
        text = link.text.strip()
        lines = text.split('\n')
        
        title = lines[0] if len(lines) > 0 else "未知標題"
        date = lines[1] if len(lines) > 1 else "未知日期"
        
        news_items.append({
            "id": i,
            "title": title,
            "date": date,
            "full_text": text
        })
        
        print(f"{i}. {title} ({date})")
        
    except Exception as e:
        print(f"處理新聞 {i} 時發生錯誤: {e}")

# 儲存結果
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# JSON
json_file = os.path.join(download_dir, f"news_quick_{timestamp}.json")
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(news_items, f, ensure_ascii=False, indent=2)

# 文字檔
txt_file = os.path.join(download_dir, f"news_quick_{timestamp}.txt")
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write("佛陀教育基金會 - 最新消息\n")
    f.write(f"擷取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 60 + "\n\n")
    
    for news in news_items:
        f.write(f"【{news['id']}】 {news['title']}\n")
        f.write(f"日期: {news['date']}\n")
        f.write("-" * 60 + "\n\n")

print(f"\n檔案已儲存:")
print(f"  JSON: {json_file}")
print(f"  文字: {txt_file}")

# 清理
scraper.cleanup()
print("\n完成！")
