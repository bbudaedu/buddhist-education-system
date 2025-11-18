#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Web Scraper Module
Integrates Chrome DevTools with existing BookScraper for advanced web scraping capabilities
"""

import os
import time
import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Import existing infrastructure
from book_scraper import BookScraper
from chrome_devtools_integration import ChromeDevToolsIntegration, DevToolsBookScraper
from config_manager import ConfigManager


class EnhancedWebScraper(BookScraper):
    """
    Enhanced web scraper that combines existing BookScraper functionality
    with Chrome DevTools Protocol for advanced web interactions
    """
    
    def __init__(self, chromedriver_path: str, download_dir: str, logger: Optional[logging.Logger] = None):
        """
        Initialize Enhanced Web Scraper
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            download_dir (str): Directory for downloads
            logger (logging.Logger): Logger instance
        """
        # Initialize parent BookScraper
        super().__init__(chromedriver_path, download_dir, logger)
        
        # Initialize DevTools integration
        self.devtools = ChromeDevToolsIntegration(chromedriver_path, logger)
        self.devtools_enabled = False
        
        # Enhanced scraping configuration
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 5,
            "element_wait_timeout": 30,
            "page_load_timeout": 60
        }
        
        # JavaScript execution capabilities
        self.js_capabilities = {
            "scroll_to_element": True,
            "click_with_js": True,
            "extract_dynamic_content": True,
            "handle_spa_navigation": True
        }
    
    def setup_enhanced_driver(self, enable_devtools: bool = True, headless: bool = True) -> webdriver.Chrome:
        """
        Set up enhanced Chrome WebDriver with DevTools support
        
        Args:
            enable_devtools (bool): Enable Chrome DevTools Protocol
            headless (bool): Run in headless mode
            
        Returns:
            webdriver.Chrome: Enhanced Chrome WebDriver instance
        """
        try:
            if enable_devtools:
                # Use DevTools-enhanced driver
                self.driver = self.devtools.setup_enhanced_driver(headless=headless, enable_devtools=True)
                self.devtools_enabled = self.devtools.devtools_enabled
                self.logger.info("Enhanced driver with DevTools initialized")
            else:
                # Fallback to standard BookScraper driver
                self.driver = self.setup_driver()
                self.devtools_enabled = False
                self.logger.info("Standard driver initialized (DevTools disabled)")
            
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Enhanced driver setup failed: {e}")
            # Fallback to standard driver
            try:
                self.driver = self.setup_driver()
                self.devtools_enabled = False
                self.logger.warning("Fallback to standard driver successful")
                return self.driver
            except Exception as fallback_error:
                self.logger.error(f"Fallback driver setup also failed: {fallback_error}")
                raise
    
    def navigate_with_enhanced_error_handling(self, url: str, max_retries: int = None) -> bool:
        """
        Navigate to URL with enhanced error handling and retry logic
        
        Args:
            url (str): Target URL
            max_retries (int): Maximum retry attempts (uses config default if None)
            
        Returns:
            bool: True if navigation successful
        """
        max_retries = max_retries or self.retry_config["max_retries"]
        retry_delay = self.retry_config["retry_delay"]
        
        for attempt in range(max_retries):
            try:
                if not self.driver:
                    self.setup_enhanced_driver()
                
                self.logger.info(f"Enhanced navigation to: {url} (attempt {attempt + 1}/{max_retries})")
                
                # Use DevTools navigation if available
                if self.devtools_enabled:
                    try:
                        self.driver.get(url)
                        
                        # Use DevTools to check page load state
                        result = self.devtools.execute_devtools_command(
                            "Runtime.evaluate",
                            {
                                "expression": "document.readyState",
                                "returnByValue": True
                            }
                        )
                        
                        ready_state = result.get("result", {}).get("value", "")
                        if ready_state == "complete":
                            self.logger.info("Enhanced navigation successful with DevTools")
                            return True
                            
                    except Exception as devtools_error:
                        self.logger.warning(f"DevTools navigation failed, using Selenium fallback: {devtools_error}")
                
                # Fallback to standard navigation
                return self.navigate_to_website(url, max_retries=1, retry_delay=0)
                
            except Exception as e:
                self.logger.warning(f"Enhanced navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All enhanced navigation attempts failed for: {url}")
                    return False
        
        return False
    
    def wait_for_dynamic_content(self, timeout: int = None) -> bool:
        """
        Wait for dynamic content to load using enhanced detection methods
        
        Args:
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if content loaded successfully
        """
        timeout = timeout or self.retry_config["element_wait_timeout"]
        
        try:
            # Use DevTools for advanced content detection if available
            if self.devtools_enabled:
                try:
                    # Check for JavaScript framework completion
                    frameworks_check = self.devtools.execute_devtools_command(
                        "Runtime.evaluate",
                        {
                            "expression": """
                            (function() {
                                // Check for common SPA frameworks
                                const checks = {
                                    vue: typeof Vue !== 'undefined' && Vue.version,
                                    react: typeof React !== 'undefined',
                                    angular: typeof angular !== 'undefined' || typeof ng !== 'undefined',
                                    jquery: typeof jQuery !== 'undefined' || typeof $ !== 'undefined'
                                };
                                
                                // Check if page has finished loading
                                const readyState = document.readyState === 'complete';
                                const noActiveRequests = !window.fetch || window.fetch.toString().includes('[native code]');
                                
                                return {
                                    frameworks: checks,
                                    readyState: readyState,
                                    timestamp: Date.now()
                                };
                            })()
                            """,
                            "returnByValue": True
                        }
                    )
                    
                    framework_info = frameworks_check.get("result", {}).get("value", {})
                    self.logger.debug(f"Framework detection: {framework_info}")
                    
                    # Wait for specific content indicators
                    content_ready = self.devtools.wait_for_element_advanced("body", timeout=timeout)
                    if content_ready:
                        # Additional wait for dynamic content
                        time.sleep(3)
                        self.logger.info("Dynamic content loaded successfully with DevTools")
                        return True
                        
                except Exception as devtools_error:
                    self.logger.warning(f"DevTools content detection failed: {devtools_error}")
            
            # Fallback to standard content waiting
            return self.wait_for_page_load(timeout)
            
        except Exception as e:
            self.logger.error(f"Enhanced content waiting failed: {e}")
            return False
    
    def find_elements_advanced(self, selectors: List[str], method: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Find elements using advanced identification methods
        
        Args:
            selectors (List[str]): List of CSS selectors to try
            method (str): Detection method ("devtools", "selenium", "hybrid")
            
        Returns:
            List[Dict[str, Any]]: List of element information with metadata
        """
        elements = []
        
        try:
            if method in ["devtools", "hybrid"] and self.devtools_enabled:
                try:
                    # Use DevTools for advanced element detection
                    devtools_elements = self.devtools.get_page_elements_advanced()
                    
                    # Filter elements by selectors
                    for element in devtools_elements:
                        element_selector = element.get("selector", "")
                        if any(selector in element_selector for selector in selectors):
                            elements.append({
                                "source": "devtools",
                                "element_info": element,
                                "selector": element_selector,
                                "visible": element.get("visible", False),
                                "interactive": True
                            })
                    
                    if elements:
                        self.logger.info(f"Found {len(elements)} elements using DevTools")
                        return elements
                        
                except Exception as devtools_error:
                    self.logger.warning(f"DevTools element detection failed: {devtools_error}")
            
            if method in ["selenium", "hybrid"]:
                # Fallback to Selenium element detection
                for selector in selectors:
                    try:
                        selenium_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for i, elem in enumerate(selenium_elements):
                            try:
                                # Get element information
                                is_displayed = elem.is_displayed()
                                is_enabled = elem.is_enabled()
                                tag_name = elem.tag_name
                                text_content = elem.text[:100] if elem.text else ""
                                
                                elements.append({
                                    "source": "selenium",
                                    "element": elem,
                                    "selector": selector,
                                    "index": i,
                                    "visible": is_displayed,
                                    "enabled": is_enabled,
                                    "tag_name": tag_name,
                                    "text": text_content,
                                    "interactive": is_displayed and is_enabled
                                })
                                
                            except Exception as elem_error:
                                self.logger.debug(f"Error getting element info: {elem_error}")
                                continue
                        
                        if selenium_elements:
                            self.logger.info(f"Found {len(selenium_elements)} elements with selector: {selector}")
                            
                    except Exception as selector_error:
                        self.logger.debug(f"Selector {selector} failed: {selector_error}")
                        continue
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Advanced element finding failed: {e}")
            return []
    
    def click_element_enhanced(self, element_info: Dict[str, Any]) -> bool:
        """
        Click element using enhanced interaction methods
        
        Args:
            element_info (Dict[str, Any]): Element information from find_elements_advanced
            
        Returns:
            bool: True if click successful
        """
        try:
            source = element_info.get("source", "selenium")
            
            if source == "devtools" and self.devtools_enabled:
                # Use DevTools for clicking
                devtools_element = element_info.get("element_info", {})
                success = self.devtools.click_element_advanced(devtools_element)
                if success:
                    self.logger.info("Element clicked successfully with DevTools")
                    return True
            
            if source == "selenium" or not self.devtools_enabled:
                # Use Selenium for clicking
                element = element_info.get("element")
                if element:
                    try:
                        # Scroll to element first
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1)
                        
                        # Try regular click first
                        element.click()
                        self.logger.info("Element clicked successfully with Selenium")
                        return True
                        
                    except Exception as click_error:
                        # Fallback to JavaScript click
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                            self.logger.info("Element clicked successfully with JavaScript")
                            return True
                        except Exception as js_error:
                            self.logger.error(f"JavaScript click also failed: {js_error}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Enhanced element click failed: {e}")
            return False
    
    def extract_text_enhanced(self, selectors: List[str], method: str = "hybrid") -> Dict[str, str]:
        """
        Extract text content using enhanced methods
        
        Args:
            selectors (List[str]): List of CSS selectors for text extraction
            method (str): Extraction method ("devtools", "selenium", "hybrid")
            
        Returns:
            Dict[str, str]: Mapping of selector to extracted text
        """
        extracted_text = {}
        
        try:
            for selector in selectors:
                text_content = ""
                
                # Try DevTools extraction first if available
                if method in ["devtools", "hybrid"] and self.devtools_enabled:
                    try:
                        text_content = self.devtools.extract_text_content_advanced(selector)
                        if text_content:
                            extracted_text[selector] = text_content
                            self.logger.debug(f"Text extracted with DevTools for {selector}: {text_content[:50]}...")
                            continue
                    except Exception as devtools_error:
                        self.logger.debug(f"DevTools text extraction failed for {selector}: {devtools_error}")
                
                # Fallback to Selenium extraction
                if method in ["selenium", "hybrid"]:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            # Get text from first visible element
                            for elem in elements:
                                if elem.is_displayed():
                                    text_content = elem.text or elem.get_attribute("textContent") or ""
                                    if text_content.strip():
                                        extracted_text[selector] = text_content.strip()
                                        self.logger.debug(f"Text extracted with Selenium for {selector}: {text_content[:50]}...")
                                        break
                    except Exception as selenium_error:
                        self.logger.debug(f"Selenium text extraction failed for {selector}: {selenium_error}")
                
                # If no text found, record empty result
                if selector not in extracted_text:
                    extracted_text[selector] = ""
            
            return extracted_text
            
        except Exception as e:
            self.logger.error(f"Enhanced text extraction failed: {e}")
            return {}
    
    def handle_popup_enhanced(self, timeout: int = 10) -> Dict[str, Any]:
        """
        Handle popup dialogs using enhanced detection and interaction
        
        Args:
            timeout (int): Maximum wait time for popup
            
        Returns:
            Dict[str, Any]: Popup information and interaction results
        """
        try:
            popup_info = {"found": False, "method": None, "content": {}}
            
            # Try DevTools popup detection first
            if self.devtools_enabled:
                try:
                    devtools_popup = self.devtools.handle_popup_dialog_advanced(timeout=timeout)
                    if devtools_popup.get("found"):
                        popup_info.update(devtools_popup)
                        popup_info["method"] = "devtools"
                        self.logger.info("Popup detected and handled with DevTools")
                        return popup_info
                except Exception as devtools_error:
                    self.logger.debug(f"DevTools popup detection failed: {devtools_error}")
            
            # Fallback to Selenium popup detection
            start_time = time.time()
            modal_selectors = [
                ".modal", ".modal-dialog", ".modal-content",
                ".popup", ".dialog", ".overlay", ".lightbox",
                "[role='dialog']", "[role='alertdialog']"
            ]
            
            while time.time() - start_time < timeout:
                for selector in modal_selectors:
                    try:
                        modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for modal in modals:
                            if modal.is_displayed():
                                # Extract popup content
                                title = ""
                                content = ""
                                buttons = []
                                
                                try:
                                    title_elem = modal.find_element(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, .modal-title, .title")
                                    title = title_elem.text
                                except:
                                    pass
                                
                                content = modal.text
                                
                                try:
                                    button_elems = modal.find_elements(By.CSS_SELECTOR, "button, .btn")
                                    buttons = [btn.text for btn in button_elems if btn.text]
                                except:
                                    pass
                                
                                popup_info = {
                                    "found": True,
                                    "method": "selenium",
                                    "selector": selector,
                                    "title": title,
                                    "content": content,
                                    "buttons": buttons,
                                    "element": modal
                                }
                                
                                self.logger.info(f"Popup detected with Selenium: {selector}")
                                return popup_info
                                
                    except Exception as selector_error:
                        self.logger.debug(f"Popup check failed for {selector}: {selector_error}")
                        continue
                
                time.sleep(0.5)
            
            self.logger.debug(f"No popup found within {timeout}s")
            return popup_info
            
        except Exception as e:
            self.logger.error(f"Enhanced popup handling failed: {e}")
            return {"found": False, "error": str(e)}
    
    def execute_javascript_enhanced(self, script: str, *args) -> Any:
        """
        Execute JavaScript with enhanced error handling and DevTools integration
        
        Args:
            script (str): JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            Any: Script execution result
        """
        try:
            # Try DevTools JavaScript execution first if available
            if self.devtools_enabled:
                try:
                    result = self.devtools.execute_devtools_command(
                        "Runtime.evaluate",
                        {
                            "expression": script,
                            "returnByValue": True
                        }
                    )
                    
                    return result.get("result", {}).get("value")
                    
                except Exception as devtools_error:
                    self.logger.debug(f"DevTools JavaScript execution failed: {devtools_error}")
            
            # Fallback to Selenium JavaScript execution
            return self.driver.execute_script(script, *args)
            
        except Exception as e:
            self.logger.error(f"Enhanced JavaScript execution failed: {e}")
            return None
    
    def cleanup_enhanced(self):
        """
        Clean up enhanced scraper resources
        """
        try:
            # Clean up DevTools integration
            if self.devtools:
                self.devtools.cleanup()
            
            # Clean up parent BookScraper
            self.cleanup()
            
            self.logger.info("Enhanced web scraper cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Enhanced cleanup error: {e}")


# Example usage and testing
def main():
    """
    Test Enhanced Web Scraper functionality
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    config_manager = ConfigManager(logger=logger)
    config = config_manager.get_config()
    
    chromedriver_path = config.get('chromedriver_path')
    download_dir = config.get('download_dir', 'downloads')
    test_url = "https://www.budaedu.org/#/"
    
    scraper = None
    try:
        logger.info("Testing Enhanced Web Scraper...")
        
        # Initialize enhanced scraper
        scraper = EnhancedWebScraper(chromedriver_path, download_dir, logger)
        
        # Test enhanced driver setup
        driver = scraper.setup_enhanced_driver(enable_devtools=True, headless=True)
        if driver:
            logger.info("✓ Enhanced driver setup successful")
        else:
            logger.error("✗ Enhanced driver setup failed")
            return
        
        # Test enhanced navigation
        if scraper.navigate_with_enhanced_error_handling(test_url):
            logger.info("✓ Enhanced navigation successful")
        else:
            logger.error("✗ Enhanced navigation failed")
            return
        
        # Test dynamic content waiting
        if scraper.wait_for_dynamic_content():
            logger.info("✓ Dynamic content loading successful")
        else:
            logger.warning("⚠ Dynamic content loading may have issues")
        
        # Test advanced element finding
        selectors = ["button", "a", ".card", ".btn"]
        elements = scraper.find_elements_advanced(selectors, method="hybrid")
        logger.info(f"✓ Found {len(elements)} elements using advanced detection")
        
        # Test enhanced text extraction
        text_selectors = ["title", "h1", "h2", ".card-title"]
        extracted_text = scraper.extract_text_enhanced(text_selectors, method="hybrid")
        logger.info(f"✓ Extracted text from {len(extracted_text)} selectors")
        
        # Test popup detection (should not find any on homepage)
        popup_info = scraper.handle_popup_enhanced(timeout=3)
        logger.info(f"✓ Popup detection test completed: {popup_info.get('found', False)}")
        
        # Test JavaScript execution
        page_title = scraper.execute_javascript_enhanced("return document.title;")
        logger.info(f"✓ JavaScript execution successful - Title: {page_title}")
        
        logger.info("🎉 All Enhanced Web Scraper tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Enhanced Web Scraper test failed: {e}")
    finally:
        if scraper:
            scraper.cleanup_enhanced()


if __name__ == "__main__":
    main()