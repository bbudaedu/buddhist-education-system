#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for notification data output functionality
測試通知資料輸出功能的腳本
"""

import os
import json
import logging
from datetime import datetime
from main_processor import MainProcessor

def test_notification_data_generation():
    """Test the notification data generation functionality"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create test configuration
    config = {
        'gemini_api_key': 'test-key',
        'chromedriver_path': 'chromedriver-win64\\chromedriver.exe',
        'target_url': 'https://www.budaedu.org/#/books/applicable/chinese',
        'baseline_book_title': 'CH754-02',
        'download_dir': 'downloads',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'test@example.com',
        'smtp_password': 'test-password',
        'email_recipients': 'test@example.com'
    }
    
    # Create processor instance
    processor = MainProcessor(config, logger)
    
    # Create mock processed books data
    processor.processed_books = [
        {
            'title': '測試書籍1',
            'author': '測試作者1',
            'summary': '這是第一本測試書籍的摘要內容。',
            'pdf_url': 'https://example.com/book1.pdf',
            'processing_method': 'pdf_extract',
            'processing_success': True,
            'filename': 'book1.pdf',
            'download_path': 'downloads/book1.pdf'
        },
        {
            'title': '測試書籍2',
            'author': '測試作者2',
            'summary': '這是第二本測試書籍的摘要內容。',
            'pdf_url': 'https://example.com/book2.pdf',
            'processing_method': 'google_search',
            'processing_success': True,
            'filename': 'book2.pdf',
            'download_path': 'downloads/book2.pdf'
        },
        {
            'title': '失敗書籍',
            'author': '',
            'summary': '',
            'pdf_url': '',
            'processing_method': 'pdf_extract',
            'processing_success': False,
            'filename': '',
            'download_path': '',
            'error_message': '處理失敗'
        }
    ]
    
    # Set mock processing stats
    processor.processing_stats = {
        'total_books_found': 3,
        'books_processed': 2,
        'books_failed': 1,
        'pdf_extractions': 1,
        'google_searches': 1,
        'processing_time_seconds': 120.5,
        'network_failures': 0
    }
    
    # Test notification data generation
    logger.info("測試通知資料生成...")
    success = processor._generate_notification_data()
    
    if success:
        logger.info("✓ 通知資料生成成功")
        
        # Verify the output files
        output_dir = 'generated_documents'
        latest_file = os.path.join(output_dir, 'notification_data_latest.json')
        
        if os.path.exists(latest_file):
            logger.info("✓ 最新通知資料檔案存在")
            
            # Read and verify the content
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info("通知資料內容:")
            logger.info(f"  處理日期: {data['processingDate']}")
            logger.info(f"  總書籍數: {data['totalBooksFound']}")
            logger.info(f"  成功處理數: {len(data['successfullyProcessed'])}")
            logger.info(f"  處理統計: {data['processingStats']}")
            
            # Verify successful books
            for i, book in enumerate(data['successfullyProcessed']):
                logger.info(f"  書籍 {i+1}: {book['title']} - {book['processingMethod']}")
            
            logger.info("✓ 通知資料格式正確")
            return True
        else:
            logger.error("✗ 最新通知資料檔案不存在")
            return False
    else:
        logger.error("✗ 通知資料生成失敗")
        return False

if __name__ == "__main__":
    success = test_notification_data_generation()
    if success:
        print("測試成功！")
    else:
        print("測試失敗！")