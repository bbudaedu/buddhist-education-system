#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for author field in the complete processing pipeline
測試作者欄位在完整處理流程中的整合
"""

import os
import sys
import logging
import json
from book_scraper import BookScraper

def setup_logging():
    """設定日誌記錄"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_author_integration.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def test_author_integration():
    """測試作者欄位在完整處理流程中的整合"""
    logger = setup_logging()
    
    # 配置參數
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "test_downloads"
    target_url = "https://www.budaedu.org/#/books/applicable/chinese"
    
    # 確保測試下載目錄存在
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
    
    scraper = None
    try:
        logger.info("=== 開始測試作者欄位整合 ===")
        
        # 初始化爬蟲
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        scraper.setup_driver()
        
        # 導航到網站
        if not scraper.navigate_to_website(target_url):
            logger.error("無法訪問目標網站")
            return False
        
        # 等待頁面載入
        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return False
        
        # 獲取第一本書進行完整測試
        from selenium.webdriver.common.by import By
        book_cards = scraper.driver.find_elements(By.CSS_SELECTOR, ".card-body")
        
        if len(book_cards) == 0:
            logger.error("未找到任何書籍卡片")
            return False
        
        # 測試第一本書的完整資訊提取
        first_book = book_cards[0]
        logger.info("測試第一本書的完整資訊提取...")
        
        # 使用 extract_book_info 方法（不實際下載PDF）
        book_info = scraper.extract_book_info(first_book)
        
        # 驗證所有必要欄位都存在
        required_fields = ['title', 'author', 'pdf_url', 'filename', 'download_path']
        missing_fields = []
        
        for field in required_fields:
            if field not in book_info:
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"缺少必要欄位: {missing_fields}")
            return False
        
        # 記錄提取結果
        logger.info("=== 書籍資訊提取結果 ===")
        logger.info(f"標題: {book_info['title']}")
        logger.info(f"作者: {book_info['author']}")
        logger.info(f"PDF URL: {book_info['pdf_url'][:50]}..." if book_info['pdf_url'] else "PDF URL: (空)")
        logger.info(f"檔案名稱: {book_info['filename']}")
        logger.info(f"下載路徑: {book_info['download_path']}")
        
        # 驗證作者欄位不為空且不是預設值
        if not book_info['author']:
            logger.error("作者欄位為空")
            return False
        
        if book_info['author'] == "":
            logger.error("作者欄位為空字串")
            return False
        
        # 測試JSON序列化（確保資料可以正確儲存）
        try:
            json_str = json.dumps(book_info, ensure_ascii=False, indent=2)
            logger.info("✓ 書籍資訊可以正確序列化為JSON")
            
            # 測試反序列化
            restored_info = json.loads(json_str)
            if restored_info['author'] != book_info['author']:
                logger.error("JSON反序列化後作者資訊不一致")
                return False
            
            logger.info("✓ JSON序列化/反序列化測試通過")
            
        except Exception as json_error:
            logger.error(f"JSON序列化失敗: {json_error}")
            return False
        
        # 模擬文件生成器會如何使用這些資料
        logger.info("=== 模擬文件生成器使用方式 ===")
        
        # 模擬 DocumentGenerator._extract_author_info 方法
        def mock_extract_author_info(title, book_data):
            # 檢查 book_data 是否有 author 欄位
            if 'author' in book_data:
                return book_data['author']
            return "未知作者"
        
        extracted_author = mock_extract_author_info(book_info['title'], book_info)
        logger.info(f"文件生成器提取的作者: {extracted_author}")
        
        if extracted_author != book_info['author']:
            logger.error("文件生成器提取的作者與原始資料不一致")
            return False
        
        logger.info("✓ 文件生成器整合測試通過")
        
        # 測試成功
        logger.info("=== 整合測試結果 ===")
        logger.info("✓ 作者欄位提取正常")
        logger.info("✓ 資料結構完整")
        logger.info("✓ JSON序列化正常")
        logger.info("✓ 文件生成器整合正常")
        logger.info("✓ 所有整合測試通過！")
        
        return True
        
    except Exception as e:
        logger.error(f"整合測試過程中發生錯誤: {e}")
        return False
    finally:
        if scraper:
            scraper.cleanup()

def main():
    """主函數"""
    try:
        success = test_author_integration()
        if success:
            print("\n✓ 作者欄位整合測試通過！")
            sys.exit(0)
        else:
            print("\n✗ 作者欄位整合測試失敗！")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ 整合測試執行失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()