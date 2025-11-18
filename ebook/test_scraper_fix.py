#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify book_scraper fixes for multiple PDF downloads
"""

import logging
import sys
from book_scraper import BookScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Test the book scraper with the fixed code"""
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    target_url = "https://www.budaedu.org/#/books/applicable/chinese"
    baseline_title = "淨心與淨土 CH861-36"
    
    scraper = None
    try:
        logger.info("=" * 60)
        logger.info("開始測試新書爬蟲 (支援多個 PDF 檔案)")
        logger.info("=" * 60)
        
        # Initialize scraper
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        
        # Set up driver and navigate
        scraper.setup_driver()
        if not scraper.navigate_to_website(target_url):
            logger.error("無法訪問目標網站")
            return
        
        # Wait for page to load
        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return
        
        # Find new books
        logger.info(f"尋找基準書籍之前的新書: {baseline_title}")
        new_books = scraper.find_new_books(baseline_title)
        
        if not new_books:
            logger.info("沒有找到新書")
            return
        
        logger.info(f"找到 {len(new_books)} 本新書")
        
        # Process only the first book as a test
        logger.info("=" * 60)
        logger.info("測試處理第一本新書...")
        logger.info("=" * 60)
        
        book_info = scraper.process_book_download(new_books[0], 0, 1)
        
        # Display results
        logger.info("=" * 60)
        logger.info("處理結果:")
        logger.info("=" * 60)
        logger.info(f"書名: {book_info.get('title', 'N/A')}")
        logger.info(f"作者: {book_info.get('author', 'N/A')}")
        logger.info(f"PDF 數量: {len(book_info.get('pdf_urls', []))}")
        logger.info(f"成功下載: {book_info.get('successful_downloads', 0)}")
        logger.info(f"下載失敗: {book_info.get('failed_downloads', 0)}")
        logger.info(f"下載成功: {book_info.get('download_success', False)}")
        
        if book_info.get('downloaded_files'):
            logger.info("已下載的檔案:")
            for file_path in book_info['downloaded_files']:
                logger.info(f"  - {file_path}")
        
        if book_info.get('error_message'):
            logger.warning(f"錯誤訊息: {book_info['error_message']}")
        
        logger.info("=" * 60)
        logger.info("測試完成")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
