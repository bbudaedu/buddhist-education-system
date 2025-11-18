#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的選擇器
"""

import time
import logging
from book_scraper import BookScraper

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_book_page():
    """測試書籍頁面爬取"""
    logger.info("=" * 60)
    logger.info("測試書籍頁面爬取")
    logger.info("=" * 60)
    
    scraper = BookScraper(
        chromedriver_path='chromedriver-win64/chromedriver.exe',
        download_dir='test_downloads',
        logger=logger
    )
    
    try:
        # 初始化 WebDriver
        if not scraper.setup_driver():
            logger.error("✗ WebDriver 初始化失敗")
            return False
        
        # 導航到書籍頁面
        url = "https://www.budaedu.org/#/books/applicable/chinese"
        logger.info(f"導航到: {url}")
        
        if not scraper.navigate_to_website(url):
            logger.error("✗ 無法訪問網站")
            return False
        
        logger.info("✓ 成功訪問網站")
        
        # 等待頁面載入
        logger.info("等待頁面載入...")
        if not scraper.wait_for_page_load(timeout=30):
            logger.warning("⚠ 頁面載入超時，但繼續嘗試")
        
        # 嘗試找到書籍卡片（使用 baseline 方法）
        logger.info("嘗試找到書籍卡片...")
        baseline_title = "淨心與淨土 CH861-36"  # 使用第3本書作為 baseline
        books = scraper.find_new_books(baseline_title)
        
        if books:
            logger.info(f"✓ 成功找到 {len(books)} 本新書（在 baseline 之前）")
            for i, book in enumerate(books[:3], 1):  # 只顯示前3本
                title = scraper.get_book_title(book)
                author = scraper.get_book_author(book)
                logger.info(f"  書籍 {i}: {title}")
                logger.info(f"    作者: {author}")
            return True
        else:
            logger.info("⚠ 未找到新書（可能所有書都在 baseline 之後）")
            logger.info("嘗試直接查找所有書籍卡片...")
            
            # 除錯：顯示頁面資訊
            logger.info("除錯資訊:")
            logger.info(f"  當前 URL: {scraper.driver.current_url}")
            logger.info(f"  頁面標題: {scraper.driver.title}")
            
            # 嘗試手動查找元素
            from selenium.webdriver.common.by import By
            cards = scraper.driver.find_elements(By.CSS_SELECTOR, ".card")
            logger.info(f"  找到 .card 元素: {len(cards)} 個")
            
            overflow_cards = scraper.driver.find_elements(By.CSS_SELECTOR, ".card.overflow-hidden")
            logger.info(f"  找到 .card.overflow-hidden 元素: {len(overflow_cards)} 個")
            
            return False
        
    except Exception as e:
        logger.error(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if scraper.driver:
            scraper.driver.quit()
            logger.info("WebDriver 已關閉")

if __name__ == "__main__":
    success = test_book_page()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ 測試成功！選擇器修復有效")
    else:
        print("✗ 測試失敗，需要進一步調查")
    print("=" * 60)
