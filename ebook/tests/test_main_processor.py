#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for MainProcessor functionality
"""

import logging
import sys
from main_processor import MainProcessor, create_test_config

def test_main_processor():
    """Test MainProcessor initialization and basic functionality"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create test configuration
        config = create_test_config()
        logger.info("Test configuration created")
        
        # Initialize MainProcessor
        processor = MainProcessor(config, logger)
        logger.info("MainProcessor initialized successfully")
        
        # Test status callback
        def status_callback(message):
            logger.info(f"[STATUS CALLBACK] {message}")
        
        processor.set_status_callback(status_callback)
        logger.info("Status callback set")
        
        # Test stop flag functionality
        processor.clear_stop_flag()
        assert not processor.should_stop(), "Stop flag should be cleared"
        
        processor.set_stop_flag()
        assert processor.should_stop(), "Stop flag should be set"
        
        processor.clear_stop_flag()
        assert not processor.should_stop(), "Stop flag should be cleared again"
        
        logger.info("Stop flag functionality test passed")
        
        # Test processing status
        status = processor.get_processing_status()
        logger.info(f"Processing status: {status}")
        
        # Test thread info
        thread_info = processor.get_thread_info()
        logger.info(f"Thread info: {thread_info}")
        
        logger.info("All basic tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_main_processor()
    if success:
        print("✓ MainProcessor test passed")
        sys.exit(0)
    else:
        print("✗ MainProcessor test failed")
        sys.exit(1)