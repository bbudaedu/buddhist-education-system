#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test News Integration
測試新聞爬蟲整合
"""

import os
import sys
import logging
from datetime import datetime


def setup_logging():
    """設定日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_news_integration():
    """測試新聞爬蟲整合"""
    logger = setup_logging()
    
    print("=" * 80)
    print("Testing News Integration with WebsiteMonitor")
    print("=" * 80)
    print()
    
    try:
        # Import WebsiteMonitor
        from website_monitor import WebsiteMonitor
        from config_manager import ConfigManager
        
        logger.info("Initializing WebsiteMonitor...")
        
        # Initialize config manager
        config_manager = ConfigManager("config.json", logger)
        
        # Initialize website monitor
        monitor = WebsiteMonitor("config.json", logger)
        
        # Initialize components
        logger.info("Initializing monitoring components...")
        if not monitor.initialize_components():
            logger.error("Failed to initialize components")
            return False
        
        # Test news processing
        logger.info("")
        logger.info("=" * 80)
        logger.info("Testing News Processing")
        logger.info("=" * 80)
        logger.info("")
        
        result = monitor.process_news_content()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("News Processing Result")
        logger.info("=" * 80)
        logger.info(f"Success: {result.get('success', False)}")
        logger.info(f"Message: {result.get('message', 'N/A')}")
        logger.info(f"Content Type: {result.get('content_type', 'N/A')}")
        logger.info(f"Items Found: {len(result.get('content', []))}")
        
        if result.get('output_file'):
            logger.info(f"Output File: {result['output_file']}")
        
        if result.get('error'):
            logger.error(f"Error: {result['error']}")
        
        # Display news items
        news_items = result.get('content', [])
        if news_items:
            logger.info("")
            logger.info("News Items:")
            for i, item in enumerate(news_items[:5], 1):  # Show first 5
                logger.info(f"  {i}. {item.get('title', 'N/A')} ({item.get('date', 'N/A')})")
            
            if len(news_items) > 5:
                logger.info(f"  ... and {len(news_items) - 5} more")
        
        logger.info("")
        logger.info("=" * 80)
        
        if result.get('success'):
            logger.info("✅ News integration test PASSED")
            return True
        else:
            logger.error("❌ News integration test FAILED")
            return False
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_news_integration()
    sys.exit(0 if success else 1)
