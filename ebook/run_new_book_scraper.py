#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New Book Scraper Runner
使用 config.json 中的設定來執行新書爬蟲和下載
"""

import os
import sys
import json
import logging
from datetime import datetime
from book_scraper import BookScraper


def load_config():
    """載入配置檔案"""
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"錯誤: 找不到配置檔案 {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def setup_logging():
    """設定日誌"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"book_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """主程式"""
    print("=" * 70)
    print("新書爬蟲與下載系統")
    print("=" * 70)
    print()
    
    # 載入配置
    logger = setup_logging()
    logger.info("載入配置檔案...")
    config = load_config()
    
    # 顯示配置資訊
    target_url = config.get('target_url', 'https://www.budaedu.org/#/books/applicable/chinese')
    baseline_title = config.get('baseline_book_title', '淨心與淨土 CH861-36')
    chromedriver_path = config.get('chromedriver_path', 'chromedriver-win64\\chromedriver.exe')
    download_dir = config.get('download_dir', 'downloads')
    
    logger.info("配置資訊:")
    logger.info(f"  目標網址: {target_url}")
    logger.info(f"  基準書籍: {baseline_title}")
    logger.info(f"  ChromeDriver: {chromedriver_path}")
    logger.info(f"  下載目錄: {download_dir}")
    logger.info("")
    
    scraper = None
    try:
        # 初始化爬蟲
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        
        # 設定瀏覽器並導航
        scraper.setup_driver()
        if not scraper.navigate_to_website(target_url):
            logger.error("無法訪問目標網站")
            return
        
        # 等待頁面載入
        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return
        
        # 尋找新書
        logger.info(f"尋找基準書籍 '{baseline_title}' 之前的新書...")
        new_books = scraper.find_new_books(baseline_title)
        
        if not new_books or len(new_books) == 0:
            logger.info("沒有找到新書")
            logger.info("=" * 70)
            logger.info("執行完成 - 無新書")
            logger.info("=" * 70)
            return
        
        logger.info(f"找到 {len(new_books)} 本新書")
        logger.info("")
        
        # 處理每本新書
        processed_books = []
        for i, book_card in enumerate(new_books):
            logger.info("=" * 70)
            logger.info(f"處理新書 {i + 1}/{len(new_books)}")
            logger.info("=" * 70)
            
            book_info = scraper.process_book_download(book_card, i, len(new_books))
            processed_books.append(book_info)
            
            logger.info("")
        
        # 生成摘要
        logger.info("=" * 70)
        logger.info("下載摘要")
        logger.info("=" * 70)
        
        total_books = len(processed_books)
        successful_books = sum(1 for book in processed_books if book.get('download_success', False))
        failed_books = total_books - successful_books
        
        total_pdfs = sum(len(book.get('pdf_urls', [])) for book in processed_books)
        successful_pdfs = sum(book.get('successful_downloads', 0) for book in processed_books)
        failed_pdfs = sum(book.get('failed_downloads', 0) for book in processed_books)
        
        logger.info(f"總書籍數: {total_books}")
        logger.info(f"成功處理: {successful_books} 本")
        logger.info(f"處理失敗: {failed_books} 本")
        logger.info(f"")
        logger.info(f"總 PDF 數: {total_pdfs}")
        logger.info(f"成功下載: {successful_pdfs} 個")
        logger.info(f"下載失敗: {failed_pdfs} 個")
        logger.info(f"成功率: {(successful_pdfs / total_pdfs * 100) if total_pdfs > 0 else 0:.1f}%")
        logger.info("")
        
        # 顯示成功下載的書籍
        logger.info("成功下載的書籍:")
        for book in processed_books:
            if book.get('download_success'):
                title = book.get('title', 'N/A')
                pdf_count = book.get('successful_downloads', 0)
                logger.info(f"  ✓ {title} ({pdf_count} 個檔案)")
        
        # 顯示失敗的書籍
        if failed_books > 0:
            logger.info("")
            logger.info("處理失敗的書籍:")
            for book in processed_books:
                if not book.get('download_success'):
                    title = book.get('title', 'N/A')
                    error = book.get('error_message', 'Unknown error')
                    logger.info(f"  ✗ {title}")
                    logger.info(f"    原因: {error}")
        
        # 儲存結果到 JSON
        output_file = os.path.join(download_dir, f"new_books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_books, f, ensure_ascii=False, indent=2)
        
        logger.info("")
        logger.info(f"詳細結果已存到: {output_file}")
        logger.info("=" * 70)
        logger.info("執行完成！")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()
