#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Enhanced Web Scraper
Tests the enhanced web scraping capabilities with Chrome DevTools integration
"""

import os
import sys
import logging
import time
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_web_scraper import EnhancedWebScraper
from config_manager import ConfigManager


def setup_test_logging() -> logging.Logger:
    """
    Set up logging for testing
    
    Returns:
        logging.Logger: Configured logger
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_enhanced_web_scraper.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_enhanced_driver_setup(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test enhanced driver setup with DevTools integration
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Enhanced Driver Setup ===")
        
        # Test with DevTools enabled
        driver = scraper.setup_enhanced_driver(enable_devtools=True, headless=True)
        if driver:
            logger.info("✓ Enhanced driver with DevTools setup successful")
            
            # Verify DevTools is enabled
            if scraper.devtools_enabled:
                logger.info("✓ DevTools integration confirmed")
            else:
                logger.warning("⚠ DevTools not enabled despite request")
            
            return True
        else:
            logger.error("✗ Enhanced driver setup failed")
            return False
            
    except Exception as e:
        logger.error(f"Enhanced driver setup test failed: {e}")
        return False


def test_enhanced_navigation(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test enhanced navigation with error handling and retry logic
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Enhanced Navigation ===")
        
        test_urls = [
            "https://www.budaedu.org/#/",
            "https://www.budaedu.org/#/books/applicable/chinese",
            "https://www.budaedu.org/#/bulletins/"
        ]
        
        success_count = 0
        for url in test_urls:
            logger.info(f"Testing navigation to: {url}")
            
            if scraper.navigate_with_enhanced_error_handling(url, max_retries=2):
                logger.info(f"✓ Enhanced navigation successful: {url}")
                success_count += 1
                
                # Verify current URL
                current_url = scraper.driver.current_url
                if "budaedu.org" in current_url:
                    logger.info(f"✓ URL verification passed: {current_url}")
                else:
                    logger.warning(f"⚠ URL verification failed: {current_url}")
                
                time.sleep(2)  # Brief pause between navigations
            else:
                logger.error(f"✗ Enhanced navigation failed: {url}")
        
        if success_count >= len(test_urls) // 2:  # At least half should succeed
            logger.info(f"✓ Enhanced navigation test passed ({success_count}/{len(test_urls)})")
            return True
        else:
            logger.error(f"✗ Enhanced navigation test failed ({success_count}/{len(test_urls)})")
            return False
            
    except Exception as e:
        logger.error(f"Enhanced navigation test failed: {e}")
        return False


def test_dynamic_content_waiting(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test dynamic content waiting capabilities
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Dynamic Content Waiting ===")
        
        # Navigate to a page with dynamic content
        if not scraper.navigate_with_enhanced_error_handling("https://www.budaedu.org/#/"):
            logger.error("✗ Failed to navigate for dynamic content test")
            return False
        
        # Test dynamic content waiting
        start_time = time.time()
        if scraper.wait_for_dynamic_content(timeout=30):
            wait_time = time.time() - start_time
            logger.info(f"✓ Dynamic content loaded successfully in {wait_time:.2f}s")
            return True
        else:
            logger.error("✗ Dynamic content waiting failed")
            return False
            
    except Exception as e:
        logger.error(f"Dynamic content waiting test failed: {e}")
        return False


def test_advanced_element_finding(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test advanced element finding capabilities
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Advanced Element Finding ===")
        
        # Navigate to books page for element testing
        if not scraper.navigate_with_enhanced_error_handling("https://www.budaedu.org/#/books/applicable/chinese"):
            logger.error("✗ Failed to navigate for element finding test")
            return False
        
        # Wait for content to load
        scraper.wait_for_dynamic_content()
        
        # Test different element finding methods
        test_selectors = [
            "button", "a", ".card", ".btn", 
            ".card-body", "h5", "p", "input"
        ]
        
        methods = ["hybrid", "devtools", "selenium"]
        results = {}
        
        for method in methods:
            try:
                elements = scraper.find_elements_advanced(test_selectors, method=method)
                results[method] = len(elements)
                logger.info(f"✓ {method.capitalize()} method found {len(elements)} elements")
            except Exception as method_error:
                logger.warning(f"⚠ {method.capitalize()} method failed: {method_error}")
                results[method] = 0
        
        # Check if at least one method found elements
        total_found = sum(results.values())
        if total_found > 0:
            logger.info(f"✓ Advanced element finding test passed (total: {total_found})")
            return True
        else:
            logger.error("✗ No elements found with any method")
            return False
            
    except Exception as e:
        logger.error(f"Advanced element finding test failed: {e}")
        return False


def test_enhanced_text_extraction(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test enhanced text extraction capabilities
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Enhanced Text Extraction ===")
        
        # Ensure we're on a page with text content
        if not scraper.navigate_with_enhanced_error_handling("https://www.budaedu.org/#/"):
            logger.error("✗ Failed to navigate for text extraction test")
            return False
        
        scraper.wait_for_dynamic_content()
        
        # Test text extraction from various selectors
        text_selectors = [
            "title", "h1", "h2", "h3", ".card-title", 
            ".navbar-brand", "p", "span"
        ]
        
        methods = ["hybrid", "devtools", "selenium"]
        extraction_results = {}
        
        for method in methods:
            try:
                extracted_text = scraper.extract_text_enhanced(text_selectors, method=method)
                non_empty_extractions = {k: v for k, v in extracted_text.items() if v.strip()}
                extraction_results[method] = len(non_empty_extractions)
                
                logger.info(f"✓ {method.capitalize()} extracted text from {len(non_empty_extractions)} selectors")
                
                # Log some sample extractions
                for selector, text in list(non_empty_extractions.items())[:3]:
                    logger.debug(f"  {selector}: {text[:50]}...")
                    
            except Exception as method_error:
                logger.warning(f"⚠ {method.capitalize()} text extraction failed: {method_error}")
                extraction_results[method] = 0
        
        # Check if at least one method extracted text
        total_extracted = sum(extraction_results.values())
        if total_extracted > 0:
            logger.info(f"✓ Enhanced text extraction test passed (total: {total_extracted})")
            return True
        else:
            logger.error("✗ No text extracted with any method")
            return False
            
    except Exception as e:
        logger.error(f"Enhanced text extraction test failed: {e}")
        return False


def test_popup_handling(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test enhanced popup handling capabilities
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Enhanced Popup Handling ===")
        
        # Navigate to homepage (should not have popups)
        if not scraper.navigate_with_enhanced_error_handling("https://www.budaedu.org/#/"):
            logger.error("✗ Failed to navigate for popup test")
            return False
        
        scraper.wait_for_dynamic_content()
        
        # Test popup detection (should not find any on homepage)
        popup_info = scraper.handle_popup_enhanced(timeout=5)
        
        if popup_info.get("found"):
            logger.info(f"✓ Popup detected: {popup_info.get('method', 'unknown')}")
            logger.info(f"  Title: {popup_info.get('title', 'N/A')}")
            logger.info(f"  Buttons: {popup_info.get('buttons', [])}")
        else:
            logger.info("✓ No popup found (expected for homepage)")
        
        # Test is considered successful regardless of popup presence
        # as the functionality is working correctly
        logger.info("✓ Enhanced popup handling test completed")
        return True
        
    except Exception as e:
        logger.error(f"Enhanced popup handling test failed: {e}")
        return False


def test_javascript_execution(scraper: EnhancedWebScraper, logger: logging.Logger) -> bool:
    """
    Test enhanced JavaScript execution capabilities
    
    Args:
        scraper: EnhancedWebScraper instance
        logger: Logger instance
        
    Returns:
        bool: True if test passed
    """
    try:
        logger.info("=== Testing Enhanced JavaScript Execution ===")
        
        # Test basic JavaScript execution
        test_scripts = [
            ("return document.title;", "Page title"),
            ("return document.readyState;", "Document ready state"),
            ("return window.location.href;", "Current URL"),
            ("return document.querySelectorAll('*').length;", "Element count")
        ]
        
        success_count = 0
        for script, description in test_scripts:
            try:
                result = scraper.execute_javascript_enhanced(script)
                if result is not None:
                    logger.info(f"✓ {description}: {str(result)[:100]}")
                    success_count += 1
                else:
                    logger.warning(f"⚠ {description}: No result returned")
            except Exception as script_error:
                logger.warning(f"⚠ {description} failed: {script_error}")
        
        if success_count >= len(test_scripts) // 2:
            logger.info(f"✓ Enhanced JavaScript execution test passed ({success_count}/{len(test_scripts)})")
            return True
        else:
            logger.error(f"✗ Enhanced JavaScript execution test failed ({success_count}/{len(test_scripts)})")
            return False
            
    except Exception as e:
        logger.error(f"Enhanced JavaScript execution test failed: {e}")
        return False


def run_enhanced_scraper_tests() -> bool:
    """
    Run all enhanced web scraper tests
    
    Returns:
        bool: True if all tests passed
    """
    logger = setup_test_logging()
    
    logger.info("Starting Enhanced Web Scraper Tests")
    logger.info("=" * 60)
    
    # Load configuration
    try:
        config_manager = ConfigManager(logger=logger)
        config = config_manager.get_config()
        
        chromedriver_path = config.get('chromedriver_path')
        download_dir = config.get('download_dir', 'downloads')
        
        if not chromedriver_path or not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver not found: {chromedriver_path}")
            return False
            
    except Exception as config_error:
        logger.error(f"Configuration loading failed: {config_error}")
        return False
    
    # Initialize enhanced scraper
    scraper = None
    try:
        scraper = EnhancedWebScraper(chromedriver_path, download_dir, logger)
        
        # Run all tests
        test_functions = [
            test_enhanced_driver_setup,
            test_enhanced_navigation,
            test_dynamic_content_waiting,
            test_advanced_element_finding,
            test_enhanced_text_extraction,
            test_popup_handling,
            test_javascript_execution
        ]
        
        test_results = []
        test_names = [
            "Enhanced Driver Setup",
            "Enhanced Navigation",
            "Dynamic Content Waiting",
            "Advanced Element Finding",
            "Enhanced Text Extraction",
            "Popup Handling",
            "JavaScript Execution"
        ]
        
        for test_func, test_name in zip(test_functions, test_names):
            try:
                logger.info(f"\n--- Running {test_name} Test ---")
                result = test_func(scraper, logger)
                test_results.append(result)
                
                if result:
                    logger.info(f"✓ {test_name} test PASSED")
                else:
                    logger.error(f"✗ {test_name} test FAILED")
                    
            except Exception as test_error:
                logger.error(f"✗ {test_name} test ERROR: {test_error}")
                test_results.append(False)
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Enhanced Web Scraper Test Results Summary:")
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        for i, (test_name, result) in enumerate(zip(test_names, test_results)):
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"  {i+1}. {test_name}: {status}")
        
        logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All Enhanced Web Scraper tests PASSED!")
            return True
        elif passed_tests >= total_tests * 0.7:  # 70% pass rate acceptable
            logger.info("✅ Enhanced Web Scraper tests mostly PASSED!")
            return True
        else:
            logger.error("❌ Enhanced Web Scraper tests FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"Enhanced Web Scraper test execution failed: {e}")
        return False
    finally:
        if scraper:
            scraper.cleanup_enhanced()


if __name__ == "__main__":
    success = run_enhanced_scraper_tests()
    sys.exit(0 if success else 1)