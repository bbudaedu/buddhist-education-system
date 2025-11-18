#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for NewsProcessor class
Tests news announcement monitoring with Chrome DevTools integration
"""

import os
import sys
import logging
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_processor import NewsProcessor


def setup_logging():
    """Set up logging configuration for testing"""
    log_filename = f"test_news_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def test_news_processor_basic():
    """Test basic NewsProcessor functionality"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("開始測試 NewsProcessor 基本功能")
    logger.info("=" * 60)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "test_downloads"
    
    # Create test download directory
    if not os.path.exists(download_dir):
        os.makedirs(download_dir, exist_ok=True)
    
    processor = None
    try:
        # Test 1: Initialize NewsProcessor
        logger.info("測試 1: 初始化 NewsProcessor...")
        processor = NewsProcessor(chromedriver_path, download_dir, logger, use_devtools=False)
        logger.info("✓ NewsProcessor 初始化成功")
        
        # Test 2: Setup WebDriver
        logger.info("測試 2: 設定 WebDriver...")
        processor.setup_driver()
        logger.info("✓ WebDriver 設定成功")
        
        # Test 3: Navigate to news page
        logger.info("測試 3: 導航到新聞頁面...")
        if processor.navigate_to_website(processor.news_url):
            logger.info("✓ 成功導航到新聞頁面")
        else:
            logger.error("✗ 導航到新聞頁面失敗")
            return False
        
        # Test 4: Wait for page load
        logger.info("測試 4: 等待頁面載入...")
        if processor.wait_for_page_load():
            logger.info("✓ 頁面載入成功")
        else:
            logger.warning("⚠ 頁面載入可能未完全成功")
        
        # Test 5: Find news elements
        logger.info("測試 5: 尋找新聞元素...")
        news_elements = processor._find_news_elements()
        if news_elements:
            logger.info(f"✓ 找到 {len(news_elements)} 個新聞元素")
        else:
            logger.warning("⚠ 未找到新聞元素")
        
        # Test 6: Extract news items (limited to first 2 for testing)
        logger.info("測試 6: 提取新聞項目 (限制前 2 個)...")
        if news_elements:
            test_elements = news_elements[:2]  # Limit for testing
            processed_news = []
            
            for i, element in enumerate(test_elements):
                try:
                    logger.info(f"處理新聞元素 {i + 1}/{len(test_elements)}")
                    news_data = processor.process_news_popup(element)
                    if news_data:
                        processed_news.append(news_data)
                        logger.info(f"✓ 成功處理: {news_data.get('title', '未知標題')}")
                    else:
                        logger.warning(f"⚠ 無法處理新聞元素 {i + 1}")
                except Exception as e:
                    logger.error(f"✗ 處理新聞元素 {i + 1} 時發生錯誤: {e}")
            
            logger.info(f"成功處理 {len(processed_news)} 個新聞項目")
            
            # Display results
            for i, news in enumerate(processed_news, 1):
                logger.info(f"新聞 {i}:")
                logger.info(f"  標題: {news.get('title', '未知')}")
                logger.info(f"  日期: {news.get('publication_date', '未知')}")
                logger.info(f"  內容長度: {len(news.get('content', ''))}")
                logger.info(f"  公告 ID: {news.get('announcement_id', '未知')}")
        
        logger.info("✓ NewsProcessor 基本功能測試完成")
        return True
        
    except Exception as e:
        logger.error(f"✗ 測試過程中發生錯誤: {e}")
        return False
    finally:
        if processor:
            processor.cleanup()


def test_news_processor_devtools():
    """Test NewsProcessor with Chrome DevTools integration"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("開始測試 NewsProcessor Chrome DevTools 整合")
    logger.info("=" * 60)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "test_downloads"
    
    processor = None
    try:
        # Test DevTools integration
        logger.info("測試: Chrome DevTools 整合...")
        processor = NewsProcessor(chromedriver_path, download_dir, logger, use_devtools=True)
        
        if processor.devtools_available:
            logger.info("✓ Chrome DevTools MCP 整合已啟用")
        else:
            logger.info("⚠ Chrome DevTools MCP 整合未啟用，將使用標準 Selenium")
        
        # Setup and test basic functionality with DevTools
        processor.setup_driver()
        
        # Test DevTools methods
        logger.info("測試 DevTools 方法...")
        
        # Test availability check
        available = processor._check_devtools_availability()
        logger.info(f"DevTools 可用性: {available}")
        
        # Test snapshot (should handle gracefully if not available)
        snapshot = processor._devtools_take_snapshot()
        if snapshot:
            logger.info("✓ DevTools 快照功能正常")
        else:
            logger.info("⚠ DevTools 快照功能未啟用或失敗")
        
        logger.info("✓ Chrome DevTools 整合測試完成")
        return True
        
    except Exception as e:
        logger.error(f"✗ DevTools 測試過程中發生錯誤: {e}")
        return False
    finally:
        if processor:
            processor.cleanup()


def test_error_handling():
    """Test error handling and recovery"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("開始測試 NewsProcessor 錯誤處理")
    logger.info("=" * 60)
    
    try:
        # Test with invalid ChromeDriver path
        logger.info("測試: 無效的 ChromeDriver 路徑...")
        try:
            processor = NewsProcessor("invalid_path", "downloads", logger)
            logger.error("✗ 應該拋出 FileNotFoundError")
            return False
        except FileNotFoundError:
            logger.info("✓ 正確處理無效 ChromeDriver 路徑")
        
        # Test with valid configuration but invalid URL
        logger.info("測試: 無效的 URL...")
        chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        if os.path.exists(chromedriver_path):
            processor = NewsProcessor(chromedriver_path, "downloads", logger)
            processor.setup_driver()
            
            # Try to navigate to invalid URL
            result = processor.navigate_to_website("https://invalid-url-that-does-not-exist.com")
            if not result:
                logger.info("✓ 正確處理無效 URL")
            else:
                logger.warning("⚠ 無效 URL 處理可能需要改進")
            
            processor.cleanup()
        else:
            logger.warning("⚠ ChromeDriver 不存在，跳過 URL 測試")
        
        logger.info("✓ 錯誤處理測試完成")
        return True
        
    except Exception as e:
        logger.error(f"✗ 錯誤處理測試失敗: {e}")
        return False


def main():
    """Run all tests"""
    logger = setup_logging()
    logger.info("開始 NewsProcessor 完整測試套件")
    
    test_results = []
    
    # Run tests
    test_results.append(("基本功能測試", test_news_processor_basic()))
    test_results.append(("DevTools 整合測試", test_news_processor_devtools()))
    test_results.append(("錯誤處理測試", test_error_handling()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("測試結果摘要")
    logger.info("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通過" if result else "✗ 失敗"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"總計: {passed}/{total} 測試通過")
    
    if passed == total:
        logger.info("🎉 所有測試通過！")
        return True
    else:
        logger.warning(f"⚠ {total - passed} 個測試失敗")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)