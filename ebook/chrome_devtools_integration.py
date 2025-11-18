#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome DevTools MCP Integration Module
Integrates Chrome DevTools Protocol with existing Selenium infrastructure for enhanced web scraping
"""

import os
import time
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


class ChromeDevToolsIntegration:
    """
    Chrome DevTools MCP integration class that extends existing Selenium infrastructure
    with advanced web interaction capabilities using Chrome DevTools Protocol
    """
    
    def __init__(self, chromedriver_path: str, logger: Optional[logging.Logger] = None):
        """
        Initialize Chrome DevTools integration
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            logger (logging.Logger): Logger instance for logging operations
        """
        self.chromedriver_path = chromedriver_path
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        self.devtools_enabled = False
        
        # Validate ChromeDriver path
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver not found at: {chromedriver_path}")
    
    def setup_enhanced_driver(self, headless: bool = True, enable_devtools: bool = True) -> webdriver.Chrome:
        """
        Set up Chrome WebDriver with DevTools Protocol support
        
        Args:
            headless (bool): Run browser in headless mode
            enable_devtools (bool): Enable Chrome DevTools Protocol
            
        Returns:
            webdriver.Chrome: Enhanced Chrome WebDriver instance
        """
        try:
            # Create Chrome options with DevTools support
            options = webdriver.ChromeOptions()
            
            # Basic Chrome options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Enable DevTools Protocol if requested
            if enable_devtools:
                options.add_argument("--remote-debugging-port=9222")
                options.add_argument("--enable-automation")
                options.add_experimental_option("useAutomationExtension", False)
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                self.devtools_enabled = True
                self.logger.info("Chrome DevTools Protocol enabled on port 9222")
            
            # Headless mode configuration
            if headless:
                options.add_argument("--headless")
                self.logger.info("Running Chrome in headless mode")
            
            # Performance optimizations
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2,  # Block images for faster loading
                "profile.default_content_setting_values.plugins": 1,
                "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
                "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            # Create Chrome service
            service = Service(self.chromedriver_path)
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Configure timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("Enhanced ChromeDriver initialized successfully")
            return self.driver
            
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize enhanced ChromeDriver: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error setting up enhanced WebDriver: {e}")
            raise
    
    def execute_devtools_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute Chrome DevTools Protocol command
        
        Args:
            command (str): DevTools command to execute
            params (Dict[str, Any]): Command parameters
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        if not self.driver or not self.devtools_enabled:
            raise RuntimeError("Chrome DevTools not available or not enabled")
        
        try:
            params = params or {}
            result = self.driver.execute_cdp_cmd(command, params)
            self.logger.debug(f"DevTools command executed: {command}")
            return result
        except Exception as e:
            self.logger.error(f"DevTools command failed: {command} - {e}")
            raise
    
    def get_page_elements_advanced(self, selector_type: str = "css") -> List[Dict[str, Any]]:
        """
        Get page elements using advanced DevTools element identification
        
        Args:
            selector_type (str): Type of selector to use ("css", "xpath", "text")
            
        Returns:
            List[Dict[str, Any]]: List of element information
        """
        try:
            # Get DOM document
            dom_result = self.execute_devtools_command("DOM.getDocument")
            
            # Query all elements based on selector type
            if selector_type == "css":
                # Get all interactive elements
                selectors = [
                    "button", "a", "input", "select", "textarea",
                    "[onclick]", "[role='button']", ".btn", ".button"
                ]
                elements = []
                
                for selector in selectors:
                    try:
                        query_result = self.execute_devtools_command(
                            "DOM.querySelectorAll",
                            {"nodeId": dom_result["root"]["nodeId"], "selector": selector}
                        )
                        
                        for node_id in query_result.get("nodeIds", []):
                            # Get element attributes
                            attrs_result = self.execute_devtools_command(
                                "DOM.getAttributes",
                                {"nodeId": node_id}
                            )
                            
                            # Get element box model for positioning
                            try:
                                box_result = self.execute_devtools_command(
                                    "DOM.getBoxModel",
                                    {"nodeId": node_id}
                                )
                                
                                elements.append({
                                    "nodeId": node_id,
                                    "selector": selector,
                                    "attributes": attrs_result.get("attributes", []),
                                    "boxModel": box_result.get("model", {}),
                                    "visible": True
                                })
                            except:
                                # Element might not be visible
                                elements.append({
                                    "nodeId": node_id,
                                    "selector": selector,
                                    "attributes": attrs_result.get("attributes", []),
                                    "boxModel": {},
                                    "visible": False
                                })
                                
                    except Exception as e:
                        self.logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                return elements
                
        except Exception as e:
            self.logger.error(f"Advanced element identification failed: {e}")
            return []
    
    def click_element_advanced(self, element_info: Dict[str, Any]) -> bool:
        """
        Click element using advanced DevTools interaction
        
        Args:
            element_info (Dict[str, Any]): Element information from get_page_elements_advanced
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            node_id = element_info.get("nodeId")
            if not node_id:
                return False
            
            # Get element center point for clicking
            box_model = element_info.get("boxModel", {})
            if box_model and "content" in box_model:
                content = box_model["content"]
                # Calculate center point
                x = (content[0] + content[4]) / 2
                y = (content[1] + content[5]) / 2
                
                # Dispatch click event using DevTools
                self.execute_devtools_command(
                    "Runtime.evaluate",
                    {
                        "expression": f"""
                        (function() {{
                            const element = document.querySelector('[data-node-id="{node_id}"]') || 
                                          document.elementFromPoint({x}, {y});
                            if (element) {{
                                element.click();
                                return true;
                            }}
                            return false;
                        }})()
                        """
                    }
                )
                
                self.logger.info(f"Advanced click executed at ({x}, {y})")
                return True
            else:
                # Fallback to JavaScript click
                self.execute_devtools_command(
                    "DOM.focus",
                    {"nodeId": node_id}
                )
                
                self.execute_devtools_command(
                    "Runtime.evaluate",
                    {
                        "expression": f"""
                        (function() {{
                            const walker = document.createTreeWalker(
                                document.body,
                                NodeFilter.SHOW_ELEMENT,
                                null,
                                false
                            );
                            let node;
                            while (node = walker.nextNode()) {{
                                if (node.nodeType === 1) {{
                                    node.click();
                                    return true;
                                }}
                            }}
                            return false;
                        }})()
                        """
                    }
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Advanced click failed: {e}")
            return False
    
    def wait_for_element_advanced(self, selector: str, timeout: int = 30) -> bool:
        """
        Wait for element using DevTools with advanced detection
        
        Args:
            selector (str): CSS selector for the element
            timeout (int): Maximum wait time in seconds
            
        Returns:
            bool: True if element found, False if timeout
        """
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Get DOM document
                    dom_result = self.execute_devtools_command("DOM.getDocument")
                    
                    # Query for the element
                    query_result = self.execute_devtools_command(
                        "DOM.querySelector",
                        {
                            "nodeId": dom_result["root"]["nodeId"],
                            "selector": selector
                        }
                    )
                    
                    if query_result.get("nodeId", 0) > 0:
                        self.logger.info(f"Element found with DevTools: {selector}")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"DevTools element search failed: {e}")
                
                time.sleep(0.5)
            
            self.logger.warning(f"Element not found within {timeout}s: {selector}")
            return False
            
        except Exception as e:
            self.logger.error(f"Advanced element wait failed: {e}")
            return False
    
    def extract_text_content_advanced(self, selector: str) -> str:
        """
        Extract text content using DevTools JavaScript execution
        
        Args:
            selector (str): CSS selector for the element
            
        Returns:
            str: Extracted text content
        """
        try:
            result = self.execute_devtools_command(
                "Runtime.evaluate",
                {
                    "expression": f"""
                    (function() {{
                        const element = document.querySelector('{selector}');
                        if (element) {{
                            return element.textContent || element.innerText || '';
                        }}
                        return '';
                    }})()
                    """,
                    "returnByValue": True
                }
            )
            
            text_content = result.get("result", {}).get("value", "")
            self.logger.debug(f"Extracted text from {selector}: {text_content[:100]}...")
            return text_content
            
        except Exception as e:
            self.logger.error(f"Advanced text extraction failed: {e}")
            return ""
    
    def handle_popup_dialog_advanced(self, timeout: int = 10) -> Dict[str, Any]:
        """
        Handle popup dialogs using DevTools with advanced detection
        
        Args:
            timeout (int): Maximum wait time for popup
            
        Returns:
            Dict[str, Any]: Popup content and metadata
        """
        try:
            start_time = time.time()
            popup_info = {
                "found": False,
                "title": "",
                "content": "",
                "buttons": [],
                "form_fields": []
            }
            
            while time.time() - start_time < timeout:
                # Check for modal dialogs
                modal_selectors = [
                    ".modal", ".modal-dialog", ".modal-content",
                    ".popup", ".dialog", ".overlay",
                    "[role='dialog']", "[role='alertdialog']"
                ]
                
                for selector in modal_selectors:
                    try:
                        # Check if modal exists and is visible
                        result = self.execute_devtools_command(
                            "Runtime.evaluate",
                            {
                                "expression": f"""
                                (function() {{
                                    const modal = document.querySelector('{selector}');
                                    if (modal && modal.offsetParent !== null) {{
                                        return {{
                                            found: true,
                                            title: modal.querySelector('h1, h2, h3, h4, h5, .modal-title, .title')?.textContent || '',
                                            content: modal.textContent || '',
                                            buttons: Array.from(modal.querySelectorAll('button, .btn')).map(btn => btn.textContent),
                                            formFields: Array.from(modal.querySelectorAll('input, select, textarea')).map(field => ({{
                                                type: field.type || field.tagName.toLowerCase(),
                                                name: field.name || field.id || '',
                                                value: field.value || ''
                                            }}))
                                        }};
                                    }}
                                    return {{ found: false }};
                                }})()
                                """,
                                "returnByValue": True
                            }
                        )
                        
                        modal_data = result.get("result", {}).get("value", {})
                        if modal_data.get("found"):
                            popup_info.update(modal_data)
                            self.logger.info(f"Popup dialog detected: {selector}")
                            return popup_info
                            
                    except Exception as e:
                        self.logger.debug(f"Modal check failed for {selector}: {e}")
                        continue
                
                time.sleep(0.5)
            
            self.logger.debug(f"No popup dialog found within {timeout}s")
            return popup_info
            
        except Exception as e:
            self.logger.error(f"Advanced popup handling failed: {e}")
            return {"found": False, "error": str(e)}
    
    def cleanup(self):
        """
        Clean up WebDriver and DevTools resources
        """
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Enhanced WebDriver closed")
            except Exception as e:
                self.logger.warning(f"Error closing enhanced WebDriver: {e}")
            finally:
                self.driver = None
                self.devtools_enabled = False


class DevToolsBookScraper:
    """
    Enhanced BookScraper that integrates Chrome DevTools capabilities
    with existing Selenium infrastructure
    """
    
    def __init__(self, chromedriver_path: str, download_dir: str, logger: Optional[logging.Logger] = None):
        """
        Initialize DevTools-enhanced BookScraper
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            download_dir (str): Directory for downloads
            logger (logging.Logger): Logger instance
        """
        self.chromedriver_path = chromedriver_path
        self.download_dir = download_dir
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize DevTools integration
        self.devtools = ChromeDevToolsIntegration(chromedriver_path, logger)
        self.driver = None
        
        # Create download directory if needed
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
            self.logger.info(f"Created download directory: {download_dir}")
    
    def setup_enhanced_scraper(self, headless: bool = True) -> bool:
        """
        Set up enhanced scraper with DevTools support
        
        Args:
            headless (bool): Run in headless mode
            
        Returns:
            bool: True if setup successful
        """
        try:
            self.driver = self.devtools.setup_enhanced_driver(headless=headless, enable_devtools=True)
            self.logger.info("Enhanced scraper setup completed")
            return True
        except Exception as e:
            self.logger.error(f"Enhanced scraper setup failed: {e}")
            return False
    
    def navigate_with_devtools_fallback(self, url: str, max_retries: int = 3) -> bool:
        """
        Navigate to URL with DevTools error handling and Selenium fallback
        
        Args:
            url (str): Target URL
            max_retries (int): Maximum retry attempts
            
        Returns:
            bool: True if navigation successful
        """
        for attempt in range(max_retries):
            try:
                if not self.driver:
                    if not self.setup_enhanced_scraper():
                        return False
                
                self.logger.info(f"Navigating to: {url} (attempt {attempt + 1})")
                self.driver.get(url)
                
                # Wait for page load using DevTools
                if self.devtools.devtools_enabled:
                    try:
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
                            self.logger.info("Page loaded successfully with DevTools")
                            return True
                            
                    except Exception as devtools_error:
                        self.logger.warning(f"DevTools page check failed, using Selenium fallback: {devtools_error}")
                
                # Fallback to standard Selenium wait
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                self.logger.info("Page loaded successfully with Selenium fallback")
                return True
                
            except Exception as e:
                self.logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"All navigation attempts failed for: {url}")
                    return False
                time.sleep(5)
        
        return False
    
    def cleanup(self):
        """
        Clean up all resources
        """
        if self.devtools:
            self.devtools.cleanup()
        self.driver = None
        self.logger.info("DevTools BookScraper cleanup completed")


# Example usage and testing
def main():
    """
    Test Chrome DevTools integration
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    test_url = "https://www.budaedu.org/#/"
    
    scraper = None
    try:
        # Test DevTools integration
        logger.info("Testing Chrome DevTools integration...")
        scraper = DevToolsBookScraper(chromedriver_path, download_dir, logger)
        
        if scraper.setup_enhanced_scraper(headless=False):
            logger.info("✓ DevTools setup successful")
            
            if scraper.navigate_with_devtools_fallback(test_url):
                logger.info("✓ Navigation with DevTools successful")
                
                # Test advanced element detection
                if scraper.devtools.devtools_enabled:
                    elements = scraper.devtools.get_page_elements_advanced()
                    logger.info(f"✓ Found {len(elements)} interactive elements")
                    
                    # Test popup detection
                    popup_info = scraper.devtools.handle_popup_dialog_advanced(timeout=5)
                    logger.info(f"✓ Popup detection completed: {popup_info.get('found', False)}")
                
            else:
                logger.error("✗ Navigation failed")
        else:
            logger.error("✗ DevTools setup failed")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()