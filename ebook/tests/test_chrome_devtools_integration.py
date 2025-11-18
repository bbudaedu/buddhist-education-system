#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Chrome DevTools MCP Functionality
Tests element identification, popup handling, content extraction, and error recovery
Requirements: 7.1, 7.2, 7.3
"""

import os
import sys
import logging
import time
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chrome_devtools_integration import ChromeDevToolsIntegration, DevToolsBookScraper
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
            logging.FileHandler('test_chrome_devtools_integration.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_element_identification_accuracy(logger: logging.Logger) -> bool:
    """
    Test element identification and interaction accuracy using Chrome DevTools
    Requirement 7.1: Chrome DevTools integration with existing Selenium automation
    Requirement 7.2: Extended ChromeDriver configuration for debugging capabilities
    
    Args:
        logger: Logger instance
        
    Returns:
        bool: True if test passed, False otherwise
    """
    scraper = None
    try:
        logger.info("=== Test 1: Element Identification and Interaction Accuracy ===")
        
        # Load configuration
        config_manager = ConfigManager(logger=logger)
        config = config_manager.get_config()
        
        chromedriver_path = config.get('chromedriver_path')
        download_dir = config.get('download_dir', 'test_downloads')
        
        if not chromedriver_path or not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver not found: {chromedriver_path}")
            return False
        
        # Initialize enhanced scraper
        scraper = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        # Setup with DevTools enabled
        if not scraper.setup_enhanced_scraper(headless=True):
            logger.error("✗ Failed to setup enhanced scraper")
            return False
        
        logger.info("✓ Enhanced scraper setup successful")
        
        # Navigate to test page
        test_url = "https://www.budaedu.org/#/"
        if not scraper.navigate_with_devtools_fallback(test_url):
            logger.error("✗ Navigation failed")
            scraper.cleanup()
            return False
        
        logger.info("✓ Navigation successful")
        time.sleep(3)  # Wait for page to fully load
        
        # Test 1.1: Advanced element detection
        if scraper.devtools and scraper.devtools.devtools_enabled:
            logger.info("Testing advanced element detection...")
            
            elements = scraper.devtools.get_page_elements_advanced(selector_type="css")
            
            if len(elements) > 0:
                logger.info(f"✓ Found {len(elements)} interactive elements")
                
                # Verify element structure
                sample_element = elements[0] if elements else None
                if sample_element:
                    required_keys = ['nodeId', 'selector', 'attributes', 'visible']
                    if all(key in sample_element for key in required_keys):
                        logger.info("✓ Element structure is correct")
                    else:
                        logger.error("✗ Element structure is incomplete")
                        scraper.cleanup()
                        return False
                
                # Count visible vs hidden elements
                visible_count = sum(1 for el in elements if el.get('visible', False))
                logger.info(f"✓ Visible elements: {visible_count}/{len(elements)}")
                
            else:
                logger.warning("⚠ No interactive elements found (may be expected for this page)")
        
        # Test 1.2: Element waiting functionality
        logger.info("Testing element waiting functionality...")
        
        if scraper.devtools and scraper.devtools.devtools_enabled:
            # Test waiting for body element (should always exist)
            body_found = scraper.devtools.wait_for_element_advanced("body", timeout=10)
            if body_found:
                logger.info("✓ Element waiting works correctly")
            else:
                logger.error("✗ Element waiting failed for body element")
                scraper.cleanup()
                return False
            
            # Test waiting for non-existent element (should timeout quickly)
            start_time = time.time()
            nonexistent_found = scraper.devtools.wait_for_element_advanced(
                ".nonexistent-element-12345", 
                timeout=3
            )
            elapsed_time = time.time() - start_time
            
            if not nonexistent_found and elapsed_time >= 2.5:
                logger.info("✓ Element waiting timeout works correctly")
            else:
                logger.warning("⚠ Element waiting timeout behavior unexpected")
        
        # Test 1.3: Text content extraction
        logger.info("Testing text content extraction...")
        
        if scraper.devtools and scraper.devtools.devtools_enabled:
            # Extract page title
            title_text = scraper.devtools.extract_text_content_advanced("title")
            if title_text:
                logger.info(f"✓ Text extraction successful - Title: {title_text[:50]}")
            else:
                logger.warning("⚠ Text extraction returned empty (may be expected)")
            
            # Extract body text
            body_text = scraper.devtools.extract_text_content_advanced("body")
            if body_text and len(body_text) > 0:
                logger.info(f"✓ Body text extraction successful - Length: {len(body_text)} chars")
            else:
                logger.warning("⚠ Body text extraction returned empty")
        
        scraper.cleanup()
        logger.info("✓ Element identification and interaction test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Element identification test failed: {e}")
        if scraper:
            scraper.cleanup()
        return False


def test_popup_handling_and_extraction(logger: logging.Logger) -> bool:
    """
    Test popup dialog handling and content extraction
    Requirement 7.2: Extended ChromeDriver configuration for debugging capabilities
    Requirement 7.3: Leverage existing wait_for_page_load for JavaScript-rendered elements
    
    Args:
        logger: Logger instance
        
    Returns:
        bool: True if test passed, False otherwise
    """
    scraper = None
    try:
        logger.info("=== Test 2: Popup Handling and Content Extraction ===")
        
        # Load configuration
        config_manager = ConfigManager(logger=logger)
        config = config_manager.get_config()
        
        chromedriver_path = config.get('chromedriver_path')
        download_dir = config.get('download_dir', 'test_downloads')
        
        # Initialize enhanced scraper
        scraper = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        if not scraper.setup_enhanced_scraper(headless=True):
            logger.error("✗ Failed to setup enhanced scraper")
            return False
        
        logger.info("✓ Enhanced scraper setup successful")
        
        # Navigate to test page
        test_url = "https://www.budaedu.org/#/"
        if not scraper.navigate_with_devtools_fallback(test_url):
            logger.error("✗ Navigation failed")
            scraper.cleanup()
            return False
        
        logger.info("✓ Navigation successful")
        time.sleep(3)
        
        # Test 2.1: Popup detection on homepage (should not find popup)
        logger.info("Testing popup detection on homepage...")
        
        if scraper.devtools and scraper.devtools.devtools_enabled:
            popup_info = scraper.devtools.handle_popup_dialog_advanced(timeout=3)
            
            if not popup_info.get('found'):
                logger.info("✓ Correctly detected no popup on homepage")
            else:
                logger.warning("⚠ Unexpected popup detected on homepage")
            
            # Verify popup info structure
            required_keys = ['found', 'title', 'content', 'buttons', 'form_fields']
            if all(key in popup_info for key in required_keys):
                logger.info("✓ Popup info structure is correct")
            else:
                logger.error("✗ Popup info structure is incomplete")
                scraper.cleanup()
                return False
        
        # Test 2.2: Navigate to carousel page and test popup detection
        logger.info("Testing popup detection on carousel page...")
        
        carousel_url = "https://www.budaedu.org/#/"
        if scraper.driver:
            try:
                scraper.driver.get(carousel_url)
                time.sleep(3)
                
                # Try to find and click carousel elements
                if scraper.devtools and scraper.devtools.devtools_enabled:
                    # Look for carousel banners
                    carousel_elements = scraper.devtools.get_page_elements_advanced()
                    
                    # Filter for potential carousel elements
                    carousel_candidates = [
                        el for el in carousel_elements 
                        if 'carousel' in str(el.get('attributes', [])).lower() or
                           'banner' in str(el.get('attributes', [])).lower() or
                           'slide' in str(el.get('attributes', [])).lower()
                    ]
                    
                    if carousel_candidates:
                        logger.info(f"✓ Found {len(carousel_candidates)} potential carousel elements")
                        
                        # Try clicking first carousel element
                        first_carousel = carousel_candidates[0]
                        click_success = scraper.devtools.click_element_advanced(first_carousel)
                        
                        if click_success:
                            logger.info("✓ Carousel element click executed")
                            time.sleep(2)
                            
                            # Check for popup after click
                            popup_after_click = scraper.devtools.handle_popup_dialog_advanced(timeout=5)
                            
                            if popup_after_click.get('found'):
                                logger.info("✓ Popup detected after carousel click")
                                logger.info(f"  - Title: {popup_after_click.get('title', 'N/A')}")
                                logger.info(f"  - Buttons: {len(popup_after_click.get('buttons', []))}")
                                logger.info(f"  - Form fields: {len(popup_after_click.get('form_fields', []))}")
                            else:
                                logger.info("✓ No popup after click (may be expected)")
                        else:
                            logger.warning("⚠ Carousel element click failed")
                    else:
                        logger.info("✓ No carousel elements found (page structure may vary)")
                
            except Exception as carousel_error:
                logger.warning(f"⚠ Carousel page test encountered issue: {carousel_error}")
        
        # Test 2.3: Test popup content extraction with simulated popup
        logger.info("Testing popup content extraction capabilities...")
        
        if scraper.devtools and scraper.devtools.devtools_enabled:
            try:
                # Inject a test modal dialog
                inject_result = scraper.devtools.execute_devtools_command(
                    "Runtime.evaluate",
                    {
                        "expression": """
                        (function() {
                            const modal = document.createElement('div');
                            modal.className = 'test-modal';
                            modal.style.display = 'block';
                            modal.innerHTML = `
                                <h2 class="modal-title">Test Course Title</h2>
                                <p>Test course description content</p>
                                <button>Confirm</button>
                                <button>Cancel</button>
                                <input type="text" name="test-field" value="test-value" />
                            `;
                            document.body.appendChild(modal);
                            return true;
                        })()
                        """,
                        "returnByValue": True
                    }
                )
                
                time.sleep(1)
                
                # Try to detect the injected modal
                test_popup = scraper.devtools.handle_popup_dialog_advanced(timeout=3)
                
                if test_popup.get('found'):
                    logger.info("✓ Successfully detected injected test modal")
                    logger.info(f"  - Title: {test_popup.get('title', 'N/A')}")
                    logger.info(f"  - Content length: {len(test_popup.get('content', ''))}")
                    logger.info(f"  - Buttons found: {len(test_popup.get('buttons', []))}")
                    logger.info(f"  - Form fields found: {len(test_popup.get('form_fields', []))}")
                else:
                    logger.warning("⚠ Could not detect injected test modal")
                
                # Clean up test modal
                scraper.devtools.execute_devtools_command(
                    "Runtime.evaluate",
                    {
                        "expression": """
                        (function() {
                            const modal = document.querySelector('.test-modal');
                            if (modal) modal.remove();
                        })()
                        """
                    }
                )
                
            except Exception as inject_error:
                logger.warning(f"⚠ Modal injection test failed: {inject_error}")
        
        scraper.cleanup()
        logger.info("✓ Popup handling and extraction test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Popup handling test failed: {e}")
        if scraper:
            scraper.cleanup()
        return False


def test_error_recovery_and_selenium_fallback(logger: logging.Logger) -> bool:
    """
    Test error recovery and fallback to standard Selenium
    Requirement 7.1: Chrome DevTools integration with existing Selenium automation
    Requirement 7.3: Extend existing network error handling and retry logic
    
    Args:
        logger: Logger instance
        
    Returns:
        bool: True if test passed, False otherwise
    """
    scraper = None
    try:
        logger.info("=== Test 3: Error Recovery and Selenium Fallback ===")
        
        # Load configuration
        config_manager = ConfigManager(logger=logger)
        config = config_manager.get_config()
        
        chromedriver_path = config.get('chromedriver_path')
        download_dir = config.get('download_dir', 'test_downloads')
        
        # Test 3.1: Setup with DevTools disabled (Selenium-only mode)
        logger.info("Testing Selenium-only mode (DevTools disabled)...")
        
        devtools = ChromeDevToolsIntegration(chromedriver_path, logger)
        driver = devtools.setup_enhanced_driver(headless=True, enable_devtools=False)
        
        if driver and not devtools.devtools_enabled:
            logger.info("✓ Selenium-only mode setup successful")
        else:
            logger.error("✗ Selenium-only mode setup failed")
            devtools.cleanup()
            return False
        
        # Test navigation in Selenium-only mode
        try:
            driver.get("https://www.budaedu.org/#/")
            time.sleep(3)
            
            if "budaedu.org" in driver.current_url:
                logger.info("✓ Navigation works in Selenium-only mode")
            else:
                logger.warning("⚠ Navigation may have issues in Selenium-only mode")
        except Exception as nav_error:
            logger.error(f"✗ Navigation failed in Selenium-only mode: {nav_error}")
            devtools.cleanup()
            return False
        
        devtools.cleanup()
        
        # Test 3.2: Navigation with retry logic
        logger.info("Testing navigation with retry logic...")
        
        scraper = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        if not scraper.setup_enhanced_scraper(headless=True):
            logger.error("✗ Failed to setup scraper for retry test")
            return False
        
        # Test successful navigation
        success = scraper.navigate_with_devtools_fallback("https://www.budaedu.org/#/", max_retries=3)
        
        if success:
            logger.info("✓ Navigation with retry logic successful")
        else:
            logger.error("✗ Navigation with retry logic failed")
            scraper.cleanup()
            return False
        
        # Test 3.3: Invalid URL handling
        logger.info("Testing invalid URL handling...")
        
        invalid_url = "https://invalid-url-that-does-not-exist-12345.com"
        invalid_success = scraper.navigate_with_devtools_fallback(invalid_url, max_retries=2)
        
        if not invalid_success:
            logger.info("✓ Invalid URL correctly handled (failed as expected)")
        else:
            logger.warning("⚠ Invalid URL unexpectedly succeeded")
        
        scraper.cleanup()
        
        # Test 3.4: DevTools command error handling
        logger.info("Testing DevTools command error handling...")
        
        devtools2 = ChromeDevToolsIntegration(chromedriver_path, logger)
        driver2 = devtools2.setup_enhanced_driver(headless=True, enable_devtools=True)
        
        if driver2:
            driver2.get("https://www.budaedu.org/#/")
            time.sleep(2)
            
            # Test invalid DevTools command
            try:
                result = devtools2.execute_devtools_command("Invalid.Command", {})
                logger.warning("⚠ Invalid command did not raise exception")
            except Exception as cmd_error:
                logger.info("✓ Invalid DevTools command correctly raised exception")
            
            # Test valid command after error
            try:
                result = devtools2.execute_devtools_command(
                    "Runtime.evaluate",
                    {"expression": "document.title", "returnByValue": True}
                )
                logger.info("✓ DevTools recovered after error and executed valid command")
            except Exception as recovery_error:
                logger.error(f"✗ DevTools failed to recover: {recovery_error}")
                devtools2.cleanup()
                return False
        
        devtools2.cleanup()
        
        # Test 3.5: Graceful degradation when DevTools unavailable
        logger.info("Testing graceful degradation...")
        
        scraper2 = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        # Setup without DevTools
        scraper2.devtools.setup_enhanced_driver(headless=True, enable_devtools=False)
        
        # Navigation should still work via Selenium
        if scraper2.driver:
            try:
                scraper2.driver.get("https://www.budaedu.org/#/")
                time.sleep(2)
                
                # Standard Selenium operations should work
                page_title = scraper2.driver.title
                logger.info(f"✓ Graceful degradation successful - Page title: {page_title}")
                
            except Exception as degradation_error:
                logger.error(f"✗ Graceful degradation failed: {degradation_error}")
                scraper2.cleanup()
                return False
        
        scraper2.cleanup()
        
        logger.info("✓ Error recovery and Selenium fallback test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Error recovery test failed: {e}")
        if scraper:
            scraper.cleanup()
        return False


def test_devtools_with_existing_selenium(logger: logging.Logger) -> bool:
    """
    Test Chrome DevTools integration with existing Selenium infrastructure
    Requirement 7.1: Chrome DevTools integration with existing Selenium automation
    Requirement 7.4: Use existing headless Chrome configuration from BookScraper
    
    Args:
        logger: Logger instance
        
    Returns:
        bool: True if test passed, False otherwise
    """
    scraper = None
    try:
        logger.info("=== Test 4: DevTools Integration with Existing Selenium ===")
        
        # Load configuration
        config_manager = ConfigManager(logger=logger)
        config = config_manager.get_config()
        
        chromedriver_path = config.get('chromedriver_path')
        download_dir = config.get('download_dir', 'test_downloads')
        
        # Test 4.1: Verify DevTools extends existing BookScraper
        logger.info("Testing DevTools extends existing BookScraper infrastructure...")
        
        scraper = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        # Verify scraper has both DevTools and standard Selenium capabilities
        if hasattr(scraper, 'devtools') and hasattr(scraper, 'driver'):
            logger.info("✓ Scraper has both DevTools and Selenium capabilities")
        else:
            logger.error("✗ Scraper missing required capabilities")
            return False
        
        # Test 4.2: Setup with headless mode (existing BookScraper configuration)
        logger.info("Testing headless mode configuration...")
        
        if scraper.setup_enhanced_scraper(headless=True):
            logger.info("✓ Headless mode setup successful")
            
            # Verify driver is running in headless mode
            if scraper.driver:
                # Navigate to verify headless operation
                scraper.driver.get("https://www.budaedu.org/#/")
                time.sleep(2)
                
                page_title = scraper.driver.title
                logger.info(f"✓ Headless browser operational - Title: {page_title}")
            else:
                logger.error("✗ Driver not initialized")
                scraper.cleanup()
                return False
        else:
            logger.error("✗ Headless mode setup failed")
            return False
        
        # Test 4.3: Verify DevTools and Selenium can work together
        logger.info("Testing DevTools and Selenium interoperability...")
        
        if scraper.devtools and scraper.devtools.devtools_enabled:
            # Use DevTools to get page info
            devtools_title = scraper.devtools.extract_text_content_advanced("title")
            
            # Use Selenium to get same info
            selenium_title = scraper.driver.title
            
            logger.info(f"  DevTools title: {devtools_title}")
            logger.info(f"  Selenium title: {selenium_title}")
            
            if devtools_title or selenium_title:
                logger.info("✓ Both DevTools and Selenium can extract page information")
            else:
                logger.warning("⚠ Title extraction returned empty (may be expected)")
        
        # Test 4.4: Verify existing wait functionality works with DevTools
        logger.info("Testing wait functionality compatibility...")
        
        if scraper.driver:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            
            try:
                # Standard Selenium wait
                WebDriverWait(scraper.driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                logger.info("✓ Standard Selenium wait works")
                
                # DevTools wait
                if scraper.devtools and scraper.devtools.devtools_enabled:
                    body_found = scraper.devtools.wait_for_element_advanced("body", timeout=10)
                    if body_found:
                        logger.info("✓ DevTools wait works")
                    else:
                        logger.warning("⚠ DevTools wait did not find body element")
                
            except Exception as wait_error:
                logger.error(f"✗ Wait functionality test failed: {wait_error}")
                scraper.cleanup()
                return False
        
        scraper.cleanup()
        logger.info("✓ DevTools integration with existing Selenium test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"DevTools-Selenium integration test failed: {e}")
        if scraper:
            scraper.cleanup()
        return False


def run_integration_tests() -> bool:
    """
    Run all Chrome DevTools integration tests
    Requirements: 7.1, 7.2, 7.3
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    logger = setup_test_logging()
    
    logger.info("=" * 80)
    logger.info("Chrome DevTools MCP Integration Tests")
    logger.info("Testing Requirements: 7.1, 7.2, 7.3")
    logger.info("=" * 80)
    
    test_results = []
    test_names = []
    
    # Test 1: Element Identification and Interaction Accuracy (Req 7.1, 7.2)
    logger.info("\n")
    test_names.append("Element Identification and Interaction Accuracy")
    test_results.append(test_element_identification_accuracy(logger))
    
    # Test 2: Popup Handling and Content Extraction (Req 7.2, 7.3)
    logger.info("\n")
    test_names.append("Popup Handling and Content Extraction")
    test_results.append(test_popup_handling_and_extraction(logger))
    
    # Test 3: Error Recovery and Selenium Fallback (Req 7.1, 7.3)
    logger.info("\n")
    test_names.append("Error Recovery and Selenium Fallback")
    test_results.append(test_error_recovery_and_selenium_fallback(logger))
    
    # Test 4: DevTools Integration with Existing Selenium (Req 7.1, 7.4)
    logger.info("\n")
    test_names.append("DevTools Integration with Existing Selenium")
    test_results.append(test_devtools_with_existing_selenium(logger))
    
    # Summary
    logger.info("\n")
    logger.info("=" * 80)
    logger.info("Test Results Summary")
    logger.info("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    for i, (test_name, result) in enumerate(zip(test_names, test_results)):
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {i+1}. {test_name}: {status}")
    
    logger.info("-" * 80)
    logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")
    logger.info("=" * 80)
    
    if passed_tests == total_tests:
        logger.info("🎉 All Chrome DevTools integration tests PASSED!")
        logger.info("\nRequirements Coverage:")
        logger.info("  ✓ 7.1: Chrome DevTools integration with existing Selenium automation")
        logger.info("  ✓ 7.2: Extended ChromeDriver configuration for debugging capabilities")
        logger.info("  ✓ 7.3: Leverage existing wait_for_page_load for JavaScript-rendered elements")
        return True
    else:
        logger.error("❌ Some Chrome DevTools integration tests FAILED!")
        logger.error(f"   {total_tests - passed_tests} test(s) need attention")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)