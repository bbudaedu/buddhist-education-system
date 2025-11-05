#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for the complete new book summary system
"""

import logging
import sys
import tkinter as tk
from newbook_summary_app import NewBookSummaryApp

def test_application_startup():
    """Test that the main application can start up without errors"""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Testing application startup...")
        
        # Create Tkinter root window
        root = tk.Tk()
        root.withdraw()  # Hide the window for testing
        
        # Initialize the application
        app = NewBookSummaryApp(root)
        logger.info("Application initialized successfully")
        
        # Test configuration manager
        config_manager = app.config_manager
        if config_manager:
            logger.info("Configuration manager is available")
            
            # Test configuration validation (should fail with empty config)
            is_valid, errors = config_manager.validate_all()
            logger.info(f"Configuration validation result: {is_valid}, errors: {len(errors)}")
        
        # Test logger
        if app.logger:
            logger.info("Application logger is available")
            app.logger.info("Test log message from application")
        
        # Clean up
        root.destroy()
        
        logger.info("Application startup test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Application startup test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_application_startup()
    if success:
        print("✓ Integration test passed")
        sys.exit(0)
    else:
        print("✗ Integration test failed")
        sys.exit(1)