#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integrated Scraper Manager
Integrates enhanced web scraping capabilities with existing BookScraper error handling and retry logic
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

# Import existing infrastructure
from book_scraper import BookScraper
from enhanced_web_scraper import EnhancedWebScraper
from config_manager import ConfigManager


class IntegratedScraperManager:
    """
    Integrated scraper manager that combines BookScraper error handling
    with enhanced web scraping capabilities using Chrome DevTools
    """
    
    def __init__(self, config_manager: ConfigManager, logger: Optional[logging.Logger] = None):
        """
        Initialize Integrated Scraper Manager
        
        Args:
            config_manager: ConfigManager instance
            logger: Logger instance
        """
        self.config_manager = config_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Get configuration
        self.config = config_manager.get_config()
        self.devtools_config = config_manager.get_chrome_devtools_config()
        
        # Initialize scrapers
        self.chromedriver_path = self.config.get('chromedriver_path')
        self.download_dir = self.config.get('download_dir', 'downloads')
        
        # Scraper instances
        self.enhanced_scraper = None
        self.fallback_scraper = None
        self.current_scraper = None
        
        # Error handling configuration
        self.error_config = {
            "max_retries": 3,
            "retry_delay": 5,
            "fallback_enabled": True,
            "devtools_timeout": 30
        }
        
        # Performance tracking
        self.performance_stats = {
            "devtools_success": 0,
            "devtools_failures": 0,
            "selenium_fallbacks": 0,
            "total_operations": 0
        }
    
    def initialize_scrapers(self) -> bool:
        """
        Initialize both enhanced and fallback scrapers
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize enhanced scraper with DevTools
            if self.devtools_config.get('enabled', False):
                try:
                    self.enhanced_scraper = EnhancedWebScraper(
                        self.chromedriver_path, 
                        self.download_dir, 
                        self.logger
                    )
                    
                    # Test enhanced scraper setup
                    driver = self.enhanced_scraper.setup_enhanced_driver(
                        enable_devtools=True,
                        headless=self.devtools_config.get('headless', True)
                    )
                    
                    if driver and self.enhanced_scraper.devtools_enabled:
                        self.current_scraper = self.enhanced_scraper
                        self.logger.info("Enhanced scraper with DevTools initialized successfully")
                    else:
                        raise Exception("DevTools not properly enabled")
                        
                except Exception as enhanced_error:
                    self.logger.warning(f"Enhanced scraper initialization failed: {enhanced_error}")
                    if self.enhanced_scraper:
                        self.enhanced_scraper.cleanup_enhanced()
                    self.enhanced_scraper = None
            
            # Initialize fallback scraper (standard BookScraper)
            if self.devtools_config.get('fallback_to_selenium', True):
                try:
                    self.fallback_scraper = BookScraper(
                        self.chromedriver_path,
                        self.download_dir,
                        self.logger
                    )
                    
                    # If no enhanced scraper, use fallback as current
                    if not self.current_scraper:
                        self.current_scraper = self.fallback_scraper
                        self.logger.info("Fallback scraper initialized as primary")
                    else:
                        self.logger.info("Fallback scraper initialized for error recovery")
                        
                except Exception as fallback_error:
                    self.logger.error(f"Fallback scraper initialization failed: {fallback_error}")
                    return False
            
            if not self.current_scraper:
                self.logger.error("No scraper could be initialized")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Scraper initialization failed: {e}")
            return False
    
    def navigate_with_integrated_error_handling(self, url: str) -> bool:
        """
        Navigate to URL with integrated error handling and automatic fallback
        
        Args:
            url: Target URL
            
        Returns:
            bool: True if navigation successful
        """
        self.performance_stats["total_operations"] += 1
        
        # Try enhanced scraper first if available
        if self.enhanced_scraper and self.current_scraper == self.enhanced_scraper:
            try:
                success = self.enhanced_scraper.navigate_with_enhanced_error_handling(
                    url, max_retries=self.error_config["max_retries"]
                )
                
                if success:
                    self.performance_stats["devtools_success"] += 1
                    self.logger.info(f"Enhanced navigation successful: {url}")
                    return True
                else:
                    self.performance_stats["devtools_failures"] += 1
                    self.logger.warning(f"Enhanced navigation failed: {url}")
                    
            except Exception as enhanced_error:
                self.performance_stats["devtools_failures"] += 1
                self.logger.warning(f"Enhanced navigation error: {enhanced_error}")
        
        # Fallback to standard scraper
        if self.fallback_scraper and self.error_config["fallback_enabled"]:
            try:
                self.performance_stats["selenium_fallbacks"] += 1
                self.logger.info(f"Attempting fallback navigation: {url}")
                
                # Setup fallback scraper if needed
                if not self.fallback_scraper.driver:
                    self.fallback_scraper.setup_driver()
                
                success = self.fallback_scraper.navigate_to_website(
                    url, 
                    max_retries=self.error_config["max_retries"],
                    retry_delay=self.error_config["retry_delay"]
                )
                
                if success:
                    # Switch to fallback scraper for subsequent operations
                    self.current_scraper = self.fallback_scraper
                    self.logger.info(f"Fallback navigation successful: {url}")
                    return True
                else:
                    self.logger.error(f"Fallback navigation also failed: {url}")
                    
            except Exception as fallback_error:
                self.logger.error(f"Fallback navigation error: {fallback_error}")
        
        return False
    
    def wait_for_content_with_fallback(self, timeout: int = None) -> bool:
        """
        Wait for content to load with integrated fallback handling
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            bool: True if content loaded
        """
        timeout = timeout or self.devtools_config.get('timeout', 30)
        
        # Try enhanced content waiting first
        if isinstance(self.current_scraper, EnhancedWebScraper):
            try:
                success = self.current_scraper.wait_for_dynamic_content(timeout)
                if success:
                    return True
                else:
                    self.logger.warning("Enhanced content waiting failed, trying fallback")
            except Exception as enhanced_error:
                self.logger.warning(f"Enhanced content waiting error: {enhanced_error}")
        
        # Fallback to standard content waiting
        if hasattr(self.current_scraper, 'wait_for_page_load'):
            try:
                return self.current_scraper.wait_for_page_load(timeout)
            except Exception as fallback_error:
                self.logger.error(f"Fallback content waiting error: {fallback_error}")
        
        return False
    
    def find_elements_with_fallback(self, selectors: List[str]) -> List[Dict[str, Any]]:
        """
        Find elements with integrated fallback handling
        
        Args:
            selectors: List of CSS selectors
            
        Returns:
            List of element information
        """
        elements = []
        
        # Try enhanced element finding first
        if isinstance(self.current_scraper, EnhancedWebScraper):
            try:
                elements = self.current_scraper.find_elements_advanced(selectors, method="hybrid")
                if elements:
                    self.logger.debug(f"Enhanced element finding found {len(elements)} elements")
                    return elements
                else:
                    self.logger.warning("Enhanced element finding returned no results")
            except Exception as enhanced_error:
                self.logger.warning(f"Enhanced element finding error: {enhanced_error}")
        
        # Fallback to standard element finding
        try:
            from selenium.webdriver.common.by import By
            
            for selector in selectors:
                try:
                    selenium_elements = self.current_scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, elem in enumerate(selenium_elements):
                        try:
                            elements.append({
                                "source": "selenium_fallback",
                                "element": elem,
                                "selector": selector,
                                "index": i,
                                "visible": elem.is_displayed(),
                                "enabled": elem.is_enabled(),
                                "tag_name": elem.tag_name,
                                "text": elem.text[:100] if elem.text else ""
                            })
                        except Exception as elem_error:
                            self.logger.debug(f"Error processing element: {elem_error}")
                            continue
                            
                    if selenium_elements:
                        self.logger.debug(f"Fallback found {len(selenium_elements)} elements with {selector}")
                        
                except Exception as selector_error:
                    self.logger.debug(f"Selector {selector} failed in fallback: {selector_error}")
                    continue
            
            return elements
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback element finding error: {fallback_error}")
            return []
    
    def extract_text_with_fallback(self, selectors: List[str]) -> Dict[str, str]:
        """
        Extract text with integrated fallback handling
        
        Args:
            selectors: List of CSS selectors
            
        Returns:
            Dictionary mapping selectors to extracted text
        """
        extracted_text = {}
        
        # Try enhanced text extraction first
        if isinstance(self.current_scraper, EnhancedWebScraper):
            try:
                extracted_text = self.current_scraper.extract_text_enhanced(selectors, method="hybrid")
                if extracted_text:
                    non_empty = {k: v for k, v in extracted_text.items() if v.strip()}
                    if non_empty:
                        self.logger.debug(f"Enhanced text extraction successful: {len(non_empty)} selectors")
                        return extracted_text
            except Exception as enhanced_error:
                self.logger.warning(f"Enhanced text extraction error: {enhanced_error}")
        
        # Fallback to standard text extraction
        try:
            from selenium.webdriver.common.by import By
            
            for selector in selectors:
                try:
                    elements = self.current_scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            text_content = elem.text or elem.get_attribute("textContent") or ""
                            if text_content.strip():
                                extracted_text[selector] = text_content.strip()
                                break
                except Exception as selector_error:
                    self.logger.debug(f"Fallback text extraction failed for {selector}: {selector_error}")
                    extracted_text[selector] = ""
            
            return extracted_text
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback text extraction error: {fallback_error}")
            return {}
    
    def handle_popup_with_fallback(self, timeout: int = 10) -> Dict[str, Any]:
        """
        Handle popups with integrated fallback handling
        
        Args:
            timeout: Maximum wait time for popup
            
        Returns:
            Dictionary with popup information
        """
        # Try enhanced popup handling first
        if isinstance(self.current_scraper, EnhancedWebScraper):
            try:
                popup_info = self.current_scraper.handle_popup_enhanced(timeout)
                if popup_info.get("found"):
                    self.logger.info("Enhanced popup handling successful")
                    return popup_info
            except Exception as enhanced_error:
                self.logger.warning(f"Enhanced popup handling error: {enhanced_error}")
        
        # Fallback to basic popup detection
        try:
            from selenium.webdriver.common.by import By
            
            modal_selectors = [
                ".modal", ".modal-dialog", ".popup", ".dialog",
                "[role='dialog']", "[role='alertdialog']"
            ]
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                for selector in modal_selectors:
                    try:
                        modals = self.current_scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                        for modal in modals:
                            if modal.is_displayed():
                                return {
                                    "found": True,
                                    "method": "selenium_fallback",
                                    "selector": selector,
                                    "content": modal.text,
                                    "element": modal
                                }
                    except Exception as selector_error:
                        continue
                
                time.sleep(0.5)
            
            return {"found": False, "method": "fallback_timeout"}
            
        except Exception as fallback_error:
            self.logger.error(f"Fallback popup handling error: {fallback_error}")
            return {"found": False, "error": str(fallback_error)}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the integrated scraper
        
        Returns:
            Dictionary with performance metrics
        """
        total_ops = self.performance_stats["total_operations"]
        if total_ops == 0:
            return self.performance_stats
        
        stats = self.performance_stats.copy()
        stats["devtools_success_rate"] = (stats["devtools_success"] / total_ops) * 100
        stats["fallback_usage_rate"] = (stats["selenium_fallbacks"] / total_ops) * 100
        
        return stats
    
    def cleanup_all(self):
        """
        Clean up all scraper resources
        """
        try:
            if self.enhanced_scraper:
                self.enhanced_scraper.cleanup_enhanced()
                self.enhanced_scraper = None
            
            if self.fallback_scraper:
                self.fallback_scraper.cleanup()
                self.fallback_scraper = None
            
            self.current_scraper = None
            self.logger.info("Integrated scraper manager cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")


# Example usage and testing
def main():
    """
    Test Integrated Scraper Manager
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Testing Integrated Scraper Manager...")
        
        # Initialize configuration
        config_manager = ConfigManager(logger=logger)
        
        # Initialize integrated scraper manager
        scraper_manager = IntegratedScraperManager(config_manager, logger)
        
        # Test initialization
        if scraper_manager.initialize_scrapers():
            logger.info("✓ Scraper initialization successful")
        else:
            logger.error("✗ Scraper initialization failed")
            return
        
        # Test navigation with fallback
        test_url = "https://www.budaedu.org/#/"
        if scraper_manager.navigate_with_integrated_error_handling(test_url):
            logger.info("✓ Integrated navigation successful")
        else:
            logger.error("✗ Integrated navigation failed")
            return
        
        # Test content waiting
        if scraper_manager.wait_for_content_with_fallback():
            logger.info("✓ Integrated content waiting successful")
        else:
            logger.warning("⚠ Integrated content waiting issues")
        
        # Test element finding
        selectors = ["button", "a", ".card"]
        elements = scraper_manager.find_elements_with_fallback(selectors)
        logger.info(f"✓ Found {len(elements)} elements with integrated finding")
        
        # Test text extraction
        text_selectors = ["title", "h1", "h2"]
        extracted_text = scraper_manager.extract_text_with_fallback(text_selectors)
        logger.info(f"✓ Extracted text from {len(extracted_text)} selectors")
        
        # Test popup handling
        popup_info = scraper_manager.handle_popup_with_fallback(timeout=3)
        logger.info(f"✓ Popup handling completed: {popup_info.get('found', False)}")
        
        # Show performance stats
        stats = scraper_manager.get_performance_stats()
        logger.info(f"Performance stats: {stats}")
        
        logger.info("🎉 Integrated Scraper Manager test completed successfully!")
        
    except Exception as e:
        logger.error(f"Integrated Scraper Manager test failed: {e}")
    finally:
        if 'scraper_manager' in locals():
            scraper_manager.cleanup_all()


if __name__ == "__main__":
    main()