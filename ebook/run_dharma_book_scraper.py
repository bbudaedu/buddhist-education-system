#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dharma Book Scraper Runner
爬取最新法寶並同步到 Node.js 後端資料庫
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from book_scraper import BookScraper

# 設定
CONFIG = {
    "target_url": "https://www.budaedu.org/#/dharmas/applicable/book?language=chinese",
    "baseline_book_title": "淨心與淨土 CH861-36", # 暫時保留，雖然我們可能不需要它來做差異比對，而是全部抓取前幾頁
    "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
    "download_dir": "downloads",
    "api_url": "http://localhost:3000/api/sync/dharma-books"
}

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f"dharma_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def sync_to_api(books, logger):
    """同步書籍資料到 API"""
    try:
        logger.info(f"正在同步 {len(books)} 本書籍到 API: {CONFIG['api_url']}")
        response = requests.post(
            CONFIG['api_url'],
            json={"books": books},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"同步成功: {result.get('message')}")
            logger.info(f"詳細資訊: {result.get('details')}")
            return True
        else:
            logger.error(f"同步失敗 (HTTP {response.status_code}): {response.text}")
            return False
    except Exception as e:
        logger.error(f"同步過程發生錯誤: {e}")
        return False

def main():
    logger = setup_logging()
    logger.info("啟動 Dharma Book Scraper...")
    
    scraper = None
    try:
        scraper = BookScraper(CONFIG['chromedriver_path'], CONFIG['download_dir'], logger)
        scraper.setup_driver()
        
        if not scraper.navigate_to_website(CONFIG['target_url']):
            logger.error("無法訪問目標網站")
            return

        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return

        # 抓取書籍
        # 這裡我們可能需要修改 BookScraper 的 find_new_books 方法，或者直接在這裡調用 find_elements
        # 為了復用，我們假設 find_new_books 可以工作，或者我們使用它來獲取元素
        # 注意：find_new_books 依賴 baseline_title。如果我們想抓取所有顯示的書，可能需要調整。
        # 暫時使用 find_new_books，如果找不到 baseline，它會返回空。
        # 我們可以傳一個不存在的 baseline title 來強制它抓取所有（如果它有 fallback）
        # 或者我們直接操作 driver
        
        logger.info("抓取頁面上的書籍...")
        # 獲取所有書籍卡片
        from selenium.webdriver.common.by import By
        book_cards = scraper.driver.find_elements(By.CSS_SELECTOR, ".card.overflow-hidden")
        
        if not book_cards:
             book_cards = scraper.driver.find_elements(By.CSS_SELECTOR, ".card")
        
        logger.info(f"找到 {len(book_cards)} 個書籍卡片")
        
        books_data = []
        for i, card in enumerate(book_cards):
            try:
                # 提取資訊
                title = scraper.get_book_title(card)
                author = scraper.get_book_author(card)
                
                # 嘗試提取封面圖
                cover_url = ""
                try:
                    img = card.find_element(By.TAG_NAME, "img")
                    cover_url = img.get_attribute("src")
                except:
                    pass
                
                # 嘗試提取 PDF 連結 (這裡不下載，只抓連結)
                # 這裡比較麻煩，因為需要點擊按鈕。
                # 為了效率，我們暫時只抓取 metadata，PDF 連結可能需要點擊才能看到。
                # 如果 "電子檔下載" 是按鈕，我們可能需要點擊。
                # 但對於 "最新法寶" 列表，我們主要需要標題和封面來顯示 Carousel。
                # 點擊後會打開 PDF 或下載。
                # 我們可以構造一個假的 URL 或者如果頁面上有連結就抓。
                # 暫時將 url 設為書籍標題的 hash 或其他唯一標識，或者如果能抓到詳情頁連結
                
                # 假設沒有詳情頁，只有下載按鈕。
                # 我們可以使用 title 作為唯一標識的一部分
                book_url = f"book_{hash(title)}" 
                
                # 發布日期通常在卡片上嗎？
                # 假設沒有，使用當前日期或嘗試從文字提取
                publish_date = datetime.now().strftime('%Y-%m-%d')
                
                if title:
                    books_data.append({
                        "title": title,
                        "author": author,
                        "cover_image_url": cover_url,
                        "url": book_url, # 這裡應該是唯一標識
                        "publish_date": publish_date
                    })
                    logger.info(f"提取書籍: {title} / {author}")
            except Exception as e:
                logger.warning(f"處理卡片 {i} 時發生錯誤: {e}")

        if books_data:
            sync_to_api(books_data, logger)
        else:
            logger.warning("沒有提取到書籍資料")

    except Exception as e:
        logger.error(f"執行錯誤: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.cleanup()

if __name__ == "__main__":
    main()
