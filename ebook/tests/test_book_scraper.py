#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for BookScraper class
"""

import logging
import os
from book_scraper import BookScraper

def test_book_scraper():
    """Test BookScraper initialization and basic functionality"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Configuration (using existing paths from the project)
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    target_url = "https://www.budaedu.org/#/books/applicable/chinese"
    baseline_title = "CH754-02"
    
    try:
        # Test BookScraper initialization
        logger.info("測試 BookScraper 初始化...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        logger.info("✓ BookScraper 初始化成功")
        
        # Test driver setup
        logger.info("測試 WebDriver 設定...")
        driver = scraper.setup_driver()
        if driver:
            logger.info("✓ WebDriver 設定成功")
        else:
            logger.error("✗ WebDriver 設定失敗")
            return False
        
        # Test navigation
        logger.info("測試網站導航...")
        if scraper.navigate_to_website(target_url):
            logger.info("✓ 網站導航成功")
        else:
            logger.error("✗ 網站導航失敗")
            scraper.cleanup()
            return False
        
        # Test page loading
        logger.info("測試頁面載入...")
        if scraper.wait_for_page_load(15):
            logger.info("✓ 頁面載入成功")
        else:
            logger.error("✗ 頁面載入失敗")
            scraper.cleanup()
            return False
        
        # Test new book identification
        logger.info("測試新書識別...")
        new_books = scraper.find_new_books(baseline_title)
        if new_books:
            logger.info(f"✓ 找到 {len(new_books)} 本新書")
            
            # Test book info extraction for first book only
            if len(new_books) > 0:
                logger.info("測試書籍資訊提取...")
                book_info = scraper.extract_book_info(new_books[0])
                if book_info['title']:
                    logger.info(f"✓ 成功提取書籍資訊: {book_info['title']}")
                    logger.info(f"  PDF URL: {book_info['pdf_url'][:50]}..." if book_info['pdf_url'] else "  無 PDF URL")
                else:
                    logger.warning("✗ 無法提取書籍資訊")
        else:
            logger.warning("未找到新書")
        
        # Cleanup
        scraper.cleanup()
        logger.info("✓ 測試完成")
        return True
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        try:
            scraper.cleanup()
        except:
            pass
        return False

if __name__ == "__main__":
    print("BookScraper 測試腳本")
    print("注意: 此測試需要有效的 ChromeDriver 和網路連線")
    print("=" * 50)
    
    success = test_book_scraper()
    
    print("=" * 50)
    if success:
        print("✓ 所有測試通過")
    else:
        print("✗ 測試失敗")