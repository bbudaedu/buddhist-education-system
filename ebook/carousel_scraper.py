#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carousel Scraper Module for Buddhist Education Website Monitoring
Extends BookScraper to monitor carousel banners and extract course information
Integrates Chrome DevTools MCP for advanced web element interaction
"""

import time
import logging
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from book_scraper import BookScraper


class CarouselScraper(BookScraper):
    """
    Carousel scraper class for extracting carousel banner information from Buddhist education website
    Extends BookScraper functionality to handle carousel content monitoring
    Integrates Chrome DevTools MCP for advanced web element interaction
    """
    
    def __init__(self, chromedriver_path, download_dir, logger=None, use_chrome_devtools=True):
        """
        Initialize CarouselScraper with Chrome WebDriver configuration
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            download_dir (str): Directory for downloads (inherited from BookScraper)
            logger (logging.Logger): Logger instance for logging operations
            use_chrome_devtools (bool): Whether to use Chrome DevTools MCP integration
        """
        super().__init__(chromedriver_path, download_dir, logger)
        self.carousel_url = "https://www.budaedu.org/#/"
        self.carousel_baseline = None
        self.use_chrome_devtools = use_chrome_devtools
        self.devtools_page_id = None
    
    def setup_chrome_devtools(self):
        """
        Set up Chrome DevTools MCP integration
        
        Returns:
            bool: True if DevTools setup successful, False otherwise
        """
        if not self.use_chrome_devtools:
            self.logger.info("Chrome DevTools 整合已停用")
            return False
        
        try:
            # Note: Chrome DevTools MCP integration would be handled by the MCP server
            # This method prepares the scraper for DevTools usage
            self.logger.info("準備 Chrome DevTools 整合...")
            
            # Enable Chrome DevTools Protocol in existing driver
            if self.driver:
                # Add DevTools-specific capabilities
                self.driver.execute_cdp_cmd('Runtime.enable', {})
                self.driver.execute_cdp_cmd('DOM.enable', {})
                self.driver.execute_cdp_cmd('Page.enable', {})
                self.logger.info("Chrome DevTools Protocol 已啟用")
                return True
            else:
                self.logger.warning("WebDriver 未初始化，無法設定 DevTools")
                return False
                
        except Exception as e:
            self.logger.warning(f"設定 Chrome DevTools 時發生錯誤: {e}")
            self.logger.info("將使用標準 Selenium 功能")
            self.use_chrome_devtools = False
            return False
    
    def _devtools_find_carousel_elements(self):
        """
        Use Chrome DevTools to find carousel elements with advanced selectors
        
        Returns:
            list: List of carousel element information
        """
        try:
            if not self.use_chrome_devtools:
                return []
            
            # Use DevTools to execute advanced JavaScript for element detection
            carousel_detection_script = """
            // Advanced carousel detection using DevTools
            function findCarouselElements() {
                const selectors = [
                    '.carousel-item img',      // 實際使用的選擇器（4個輪播）
                    '.carousel-item',          // 輪播項目容器
                    '.carousel img',           // 備用選擇器
                    '[class*="carousel"] img', // 通用輪播圖片
                    '.banner img',
                    '.swiper-slide img',
                    '.slide img',
                    '[class*="banner"] img',
                    '[class*="slide"] img'
                ];
                
                let elements = [];
                for (const selector of selectors) {
                    const found = document.querySelectorAll(selector);
                    if (found.length > 0) {
                        elements = Array.from(found).map((el, index) => ({
                            selector: selector,
                            index: index,
                            src: el.src,
                            alt: el.alt,
                            visible: el.offsetParent !== null,
                            rect: el.getBoundingClientRect(),
                            clickable: el.closest('a, button, [onclick]') !== null
                        }));
                        break;
                    }
                }
                
                return elements;
            }
            
            return findCarouselElements();
            """
            
            # Execute script using DevTools
            result = self.driver.execute_script(carousel_detection_script)
            
            if result and len(result) > 0:
                self.logger.info(f"DevTools 找到 {len(result)} 個輪播元素")
                return result
            else:
                self.logger.warning("DevTools 未找到輪播元素")
                return []
                
        except Exception as e:
            self.logger.error(f"使用 DevTools 尋找輪播元素時發生錯誤: {e}")
            return []
    
    def _devtools_click_element(self, element_info):
        """
        Use Chrome DevTools to click an element with advanced interaction
        
        Args:
            element_info (dict): Element information from DevTools detection
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            if not self.use_chrome_devtools:
                return False
            
            # Use DevTools to perform precise clicking
            click_script = f"""
            // Advanced clicking using DevTools
            function clickElementByIndex(selector, index) {{
                const elements = document.querySelectorAll(selector);
                if (elements.length > index) {{
                    const element = elements[index];
                    
                    // Scroll element into view
                    element.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                    
                    // Wait a moment for scroll
                    setTimeout(() => {{
                        // Try multiple click methods
                        try {{
                            // Method 1: Direct click
                            element.click();
                        }} catch (e1) {{
                            try {{
                                // Method 2: Dispatch click event
                                const event = new MouseEvent('click', {{
                                    view: window,
                                    bubbles: true,
                                    cancelable: true
                                }});
                                element.dispatchEvent(event);
                            }} catch (e2) {{
                                // Method 3: Click parent if element is not directly clickable
                                const clickableParent = element.closest('a, button, [onclick]');
                                if (clickableParent) {{
                                    clickableParent.click();
                                }}
                            }}
                        }}
                    }}, 500);
                    
                    return true;
                }}
                return false;
            }}
            
            return clickElementByIndex('{element_info["selector"]}', {element_info["index"]});
            """
            
            result = self.driver.execute_script(click_script)
            
            if result:
                self.logger.info("DevTools 成功點擊元素")
                time.sleep(3)  # Wait for popup to appear
                return True
            else:
                self.logger.warning("DevTools 點擊元素失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"使用 DevTools 點擊元素時發生錯誤: {e}")
            return False
    
    def _devtools_extract_popup_content(self):
        """
        Use Chrome DevTools to extract popup content with advanced DOM manipulation
        
        Returns:
            dict: Popup content information
        """
        try:
            if not self.use_chrome_devtools:
                return {}
            
            # Advanced popup content extraction script
            popup_extraction_script = """
            // Advanced popup content extraction using DevTools
            function extractPopupContent() {
                const popupSelectors = [
                    '.modal-content',
                    '.modal-body', 
                    '.popup-content',
                    '.dialog-content',
                    '[role="dialog"]',
                    '.modal'
                ];
                
                let popup = null;
                for (const selector of popupSelectors) {
                    popup = document.querySelector(selector);
                    if (popup && popup.offsetParent !== null) {
                        break;
                    }
                }
                
                if (!popup) {
                    return null;
                }
                
                // Extract structured information
                const result = {
                    fullText: popup.innerText,
                    courseName: '',
                    location: '',
                    instructor: '',
                    description: '',
                    activityLink: ''
                };
                
                // Try to find specific fields
                const text = popup.innerText;
                const lines = text.split('\\n').map(line => line.trim()).filter(line => line);
                
                // Parse lines for specific information
                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i];
                    
                    // Course name (usually first significant line or contains '課程')
                    if (!result.courseName && (line.includes('課程') || (i === 0 && line.length > 5))) {
                        result.courseName = line;
                    }
                    
                    // Location
                    if (line.includes('地點') || line.includes('位置') || line.includes('教室')) {
                        result.location = line.replace(/地點[:：]?/g, '').replace(/位置[:：]?/g, '').replace(/教室[:：]?/g, '').trim();
                    }
                    
                    // Instructor
                    if (line.includes('講師') || line.includes('老師') || line.includes('主講')) {
                        result.instructor = line.replace(/講師[:：]?/g, '').replace(/老師[:：]?/g, '').replace(/主講[:：]?/g, '').trim();
                    }
                }
                
                // If course name still empty, use first non-empty line
                if (!result.courseName && lines.length > 0) {
                    result.courseName = lines[0];
                }
                
                // Always set description to full text for comprehensive information
                result.description = text;
                
                // Look for links
                const links = popup.querySelectorAll('a');
                if (links.length > 0) {
                    result.activityLink = links[0].href;
                }
                
                return result;
            }
            
            return extractPopupContent();
            """
            
            result = self.driver.execute_script(popup_extraction_script)
            
            if result:
                self.logger.info("DevTools 成功提取彈窗內容")
                return {
                    'course_name': result.get('courseName', ''),
                    'location': result.get('location', ''),
                    'instructor': result.get('instructor', ''),
                    'description': result.get('description', ''),
                    'activity_link': result.get('activityLink', '')
                }
            else:
                self.logger.warning("DevTools 未找到彈窗內容")
                return {}
                
        except Exception as e:
            self.logger.error(f"使用 DevTools 提取彈窗內容時發生錯誤: {e}")
            return {}
        
    def extract_carousel_banners(self):
        """
        Extract carousel banner information from the homepage
        Integrates Chrome DevTools for enhanced element detection and interaction
        
        Returns:
            list: List of carousel banner data dictionaries
        """
        try:
            self.logger.info("開始提取輪播橫幅資訊...")
            
            # Navigate to homepage
            if not self.navigate_to_website(self.carousel_url):
                self.logger.error("無法訪問首頁")
                return []
            
            # Wait for page to load
            if not self.wait_for_page_load():
                self.logger.error("首頁載入失敗")
                return []
            
            # Set up Chrome DevTools if enabled
            self.setup_chrome_devtools()
            
            # Try DevTools method first, fallback to standard Selenium
            carousel_elements = []
            if self.use_chrome_devtools:
                devtools_elements = self._devtools_find_carousel_elements()
                if devtools_elements:
                    self.logger.info("使用 Chrome DevTools 找到輪播元素")
                    carousel_elements = devtools_elements
            
            # Fallback to standard Selenium method
            if not carousel_elements:
                self.logger.info("使用標準 Selenium 方法尋找輪播元素")
                selenium_elements = self._find_carousel_elements()
                # Convert Selenium elements to DevTools-compatible format
                carousel_elements = self._convert_selenium_to_devtools_format(selenium_elements)
            
            if not carousel_elements:
                self.logger.warning("未找到輪播橫幅元素")
                return []
            
            extracted_banners = []
            for i, element_info in enumerate(carousel_elements):
                try:
                    self.logger.info(f"處理輪播橫幅 {i + 1}/{len(carousel_elements)}")
                    banner_data = self._process_single_banner_enhanced(element_info, i)
                    if banner_data:
                        extracted_banners.append(banner_data)
                        
                except Exception as e:
                    self.logger.error(f"處理輪播橫幅 {i + 1} 時發生錯誤: {e}")
                    continue
            
            self.logger.info(f"成功提取 {len(extracted_banners)} 個輪播橫幅")
            return extracted_banners
            
        except Exception as e:
            self.logger.error(f"提取輪播橫幅時發生錯誤: {e}")
            return []
    
    def _convert_selenium_to_devtools_format(self, selenium_elements):
        """
        Convert Selenium WebElements to DevTools-compatible format
        
        Args:
            selenium_elements (list): List of Selenium WebElements
            
        Returns:
            list: List of element information dictionaries
        """
        try:
            devtools_elements = []
            for i, element in enumerate(selenium_elements):
                try:
                    element_info = {
                        'selector': 'img',  # Generic selector
                        'index': i,
                        'src': element.get_attribute('src') or '',
                        'alt': element.get_attribute('alt') or '',
                        'visible': element.is_displayed(),
                        'selenium_element': element,  # Keep reference for fallback
                        'clickable': True
                    }
                    devtools_elements.append(element_info)
                except Exception as e:
                    self.logger.warning(f"轉換元素 {i} 時發生錯誤: {e}")
                    continue
            
            return devtools_elements
            
        except Exception as e:
            self.logger.error(f"轉換 Selenium 元素格式時發生錯誤: {e}")
            return []
    
    def _process_single_banner_enhanced(self, element_info, banner_index):
        """
        Process a single carousel banner using enhanced DevTools integration
        
        Args:
            element_info (dict): Element information from DevTools or converted Selenium
            banner_index (int): Index of the banner
            
        Returns:
            dict: Banner information or None if processing fails
        """
        try:
            # Extract basic banner information
            banner_data = {
                'carousel_id': f"carousel_{banner_index}_{int(time.time())}",
                'banner_title': element_info.get('alt', f"輪播橫幅 {banner_index + 1}"),
                'image_url': element_info.get('src', ''),
                'activity_link': '',
                'course_name': '',
                'location': '',
                'instructor': '',
                'description': '',
                'extraction_timestamp': datetime.now(),
                'content_type': 'carousel'
            }
            
            self.logger.info(f"橫幅基本資訊: {banner_data['banner_title']}")
            
            # Try to click banner and extract popup information using enhanced methods
            popup_data = self.process_banner_popup_enhanced(element_info)
            if popup_data:
                banner_data.update(popup_data)
            
            return banner_data
            
        except Exception as e:
            self.logger.error(f"處理單個橫幅時發生錯誤: {e}")
            return None
    
    def process_banner_popup_enhanced(self, element_info):
        """
        Click banner and extract popup dialog information using enhanced DevTools methods
        
        Args:
            element_info (dict): Element information from DevTools detection
            
        Returns:
            dict: Popup information or empty dict if extraction fails
        """
        popup_data = {
            'activity_link': '',
            'course_name': '',
            'location': '',
            'instructor': '',
            'description': ''
        }
        
        try:
            # Try DevTools clicking first
            click_success = False
            if self.use_chrome_devtools and 'selenium_element' not in element_info:
                click_success = self._devtools_click_element(element_info)
            
            # Fallback to Selenium clicking
            if not click_success and 'selenium_element' in element_info:
                self.logger.info("使用 Selenium 備用點擊方法...")
                selenium_element = element_info['selenium_element']
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selenium_element)
                time.sleep(2)
                
                # Find clickable parent and click
                clickable_element = self._find_clickable_parent(selenium_element)
                if clickable_element:
                    self.driver.execute_script("arguments[0].click();", clickable_element)
                    click_success = True
                    time.sleep(3)
            
            if not click_success:
                self.logger.warning("無法點擊輪播橫幅")
                return popup_data
            
            # Wait for popup to fully load and stabilize
            time.sleep(2)
            
            # Try DevTools popup extraction first
            if self.use_chrome_devtools:
                devtools_popup_data = self._devtools_extract_popup_content()
                if devtools_popup_data and any(devtools_popup_data.values()):
                    popup_data.update(devtools_popup_data)
                    self.logger.info("使用 DevTools 成功提取彈窗資訊")
                else:
                    # Fallback to standard extraction
                    self.logger.info("DevTools 提取失敗，使用標準方法...")
                    standard_popup_data = self._extract_popup_content()
                    if standard_popup_data:
                        popup_data.update(standard_popup_data)
            else:
                # Use standard extraction method
                standard_popup_data = self._extract_popup_content()
                if standard_popup_data:
                    popup_data.update(standard_popup_data)
            
            # Close popup
            self._close_popup()
            
            return popup_data
            
        except Exception as e:
            self.logger.error(f"處理橫幅彈窗時發生錯誤: {e}")
            # Try to close any open popup
            self._close_popup()
            return popup_data
    
    def _find_carousel_elements(self):
        """
        Find carousel banner elements on the homepage
        
        Returns:
            list: List of carousel banner WebElements
        """
        try:
            # Wait for carousel to load (Vue.js SPA needs more time)
            time.sleep(10)
            
            # Try multiple selectors for carousel elements
            carousel_selectors = [
                ".carousel-item img",
                ".carousel img", 
                ".banner img",
                ".swiper-slide img",
                ".slide img",
                "[class*='carousel'] img",
                "[class*='banner'] img",
                "[class*='slide'] img"
            ]
            
            carousel_elements = []
            for selector in carousel_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"使用選擇器 '{selector}' 找到 {len(elements)} 個輪播元素")
                        carousel_elements = elements
                        break
                except Exception as e:
                    self.logger.debug(f"選擇器 '{selector}' 失敗: {e}")
                    continue
            
            if not carousel_elements:
                # Fallback: look for any clickable images in the main content area
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, "main, .main, #main, .content")
                    carousel_elements = main_content.find_elements(By.TAG_NAME, "img")
                    self.logger.info(f"備用方法找到 {len(carousel_elements)} 個圖片元素")
                except Exception as e:
                    self.logger.warning(f"備用方法也失敗: {e}")
            
            return carousel_elements
            
        except Exception as e:
            self.logger.error(f"尋找輪播元素時發生錯誤: {e}")
            return []
    
    def _process_single_banner(self, banner_element, banner_index):
        """
        Process a single carousel banner to extract information
        
        Args:
            banner_element: Selenium WebElement representing a banner
            banner_index (int): Index of the banner
            
        Returns:
            dict: Banner information or None if processing fails
        """
        try:
            # Extract basic banner information
            banner_data = {
                'carousel_id': f"carousel_{banner_index}_{int(time.time())}",
                'banner_title': '',
                'image_url': '',
                'activity_link': '',
                'course_name': '',
                'location': '',
                'instructor': '',
                'description': '',
                'extraction_timestamp': datetime.now(),
                'content_type': 'carousel'
            }
            
            # Get image URL
            banner_data['image_url'] = banner_element.get_attribute('src') or ''
            
            # Get alt text as potential title
            banner_data['banner_title'] = banner_element.get_attribute('alt') or f"輪播橫幅 {banner_index + 1}"
            
            self.logger.info(f"橫幅基本資訊: {banner_data['banner_title']}")
            
            # Try to click banner and extract popup information
            popup_data = self.process_banner_popup(banner_element)
            if popup_data:
                banner_data.update(popup_data)
            
            return banner_data
            
        except Exception as e:
            self.logger.error(f"處理單個橫幅時發生錯誤: {e}")
            return None
    
    def process_banner_popup(self, banner_element):
        """
        Click banner and extract popup dialog information
        
        Args:
            banner_element: Selenium WebElement representing a banner
            
        Returns:
            dict: Popup information or empty dict if extraction fails
        """
        popup_data = {
            'activity_link': '',
            'course_name': '',
            'location': '',
            'instructor': '',
            'description': ''
        }
        
        try:
            # Scroll to banner to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", banner_element)
            time.sleep(2)
            
            # Try to find clickable parent element
            clickable_element = self._find_clickable_parent(banner_element)
            if not clickable_element:
                self.logger.warning("找不到可點擊的父元素")
                return popup_data
            
            # Click the banner using JavaScript to avoid interception
            self.logger.info("點擊輪播橫幅...")
            self.driver.execute_script("arguments[0].click();", clickable_element)
            time.sleep(3)
            
            # Extract popup information
            popup_info = self._extract_popup_content()
            if popup_info:
                popup_data.update(popup_info)
                self.logger.info("成功提取彈窗資訊")
            else:
                self.logger.warning("未能提取彈窗資訊")
            
            # Close popup
            self._close_popup()
            
            return popup_data
            
        except Exception as e:
            self.logger.error(f"處理橫幅彈窗時發生錯誤: {e}")
            # Try to close any open popup
            self._close_popup()
            return popup_data
    
    def _find_clickable_parent(self, banner_element):
        """
        Find the clickable parent element of a banner image
        
        Args:
            banner_element: Selenium WebElement representing a banner image
            
        Returns:
            WebElement: Clickable parent element or the banner itself
        """
        try:
            # Try to find parent link or button
            parent_selectors = [
                "..",  # Direct parent
                "../..",  # Grandparent
                "../../..",  # Great-grandparent
            ]
            
            for selector in parent_selectors:
                try:
                    parent = banner_element.find_element(By.XPATH, selector)
                    tag_name = parent.tag_name.lower()
                    
                    # Check if parent is clickable
                    if tag_name in ['a', 'button'] or parent.get_attribute('onclick'):
                        return parent
                    
                    # Check if parent has click event listeners
                    if parent.get_attribute('data-toggle') or parent.get_attribute('data-target'):
                        return parent
                        
                except Exception:
                    continue
            
            # If no clickable parent found, return the banner itself
            return banner_element
            
        except Exception as e:
            self.logger.warning(f"尋找可點擊父元素時發生錯誤: {e}")
            return banner_element
    
    def _extract_popup_content(self):
        """
        Extract content from opened popup dialog
        
        Returns:
            dict: Popup content information
        """
        popup_info = {}
        
        try:
            # Wait for popup to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal, .popup, .dialog, [role='dialog']"))
            )
            
            # Find popup container
            popup_selectors = [
                ".modal-content",
                ".modal-body", 
                ".popup-content",
                ".dialog-content",
                "[role='dialog']",
                ".modal"
            ]
            
            popup_container = None
            for selector in popup_selectors:
                try:
                    popup_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup_container:
                        break
                except Exception:
                    continue
            
            if not popup_container:
                self.logger.warning("找不到彈窗容器")
                return popup_info
            
            # Extract course information from popup
            popup_text = popup_container.text
            self.logger.debug(f"彈窗內容: {popup_text[:200]}...")
            
            # Try to extract structured information
            popup_info['description'] = popup_text.strip()
            
            # Look for specific fields
            popup_info.update(self._parse_popup_fields(popup_container))
            
            # Try to find activity link
            links = popup_container.find_elements(By.TAG_NAME, "a")
            if links:
                popup_info['activity_link'] = links[0].get_attribute('href') or ''
            
            return popup_info
            
        except TimeoutException:
            self.logger.warning("等待彈窗出現超時")
            return popup_info
        except Exception as e:
            self.logger.error(f"提取彈窗內容時發生錯誤: {e}")
            return popup_info
    
    def _parse_popup_fields(self, popup_container):
        """
        Parse specific fields from popup content
        
        Args:
            popup_container: WebElement containing popup content
            
        Returns:
            dict: Parsed field information
        """
        fields = {
            'course_name': '',
            'location': '',
            'instructor': ''
        }
        
        try:
            # Look for common field patterns
            text_content = popup_container.text
            lines = text_content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to identify course name (usually the first significant line or title)
                if not fields['course_name'] and len(line) > 5 and '課程' in line:
                    fields['course_name'] = line
                
                # Look for location information
                if '地點' in line or '位置' in line or '教室' in line:
                    fields['location'] = line.replace('地點:', '').replace('位置:', '').replace('教室:', '').strip()
                
                # Look for instructor information
                if '講師' in line or '老師' in line or '主講' in line:
                    fields['instructor'] = line.replace('講師:', '').replace('老師:', '').replace('主講:', '').strip()
            
            # If course name still empty, use first non-empty line
            if not fields['course_name'] and lines:
                for line in lines:
                    if line.strip() and len(line.strip()) > 3:
                        fields['course_name'] = line.strip()
                        break
            
            return fields
            
        except Exception as e:
            self.logger.error(f"解析彈窗欄位時發生錯誤: {e}")
            return fields
    
    def _close_popup(self):
        """
        Close any open popup dialog
        
        Returns:
            bool: True if popup closed successfully, False otherwise
        """
        try:
            time.sleep(2)  # Wait for popup to fully appear
            
            # Try multiple strategies to close popup
            close_strategies = [
                # Strategy 1: Find and click close button
                lambda: self._click_close_button(),
                # Strategy 2: Press ESC key
                lambda: self._press_escape_key(),
                # Strategy 3: Click outside popup (backdrop)
                lambda: self._click_backdrop()
            ]
            
            for strategy in close_strategies:
                try:
                    if strategy():
                        self.logger.info("成功關閉彈窗")
                        # Wait longer to ensure popup is completely closed
                        time.sleep(3)
                        # Verify popup is actually closed
                        if self._verify_popup_closed():
                            self.logger.info("確認彈窗已完全關閉")
                            return True
                        else:
                            self.logger.warning("彈窗可能未完全關閉，繼續嘗試...")
                            continue
                except Exception as e:
                    self.logger.debug(f"關閉彈窗策略失敗: {e}")
                    continue
            
            self.logger.warning("所有關閉彈窗策略都失敗")
            return False
            
        except Exception as e:
            self.logger.error(f"關閉彈窗時發生錯誤: {e}")
            return False
    
    def _click_close_button(self):
        """Click close button to close popup"""
        close_selectors = [
            "button.close",
            ".close",
            ".modal-close",
            "[data-dismiss='modal']",
            "[aria-label='Close']",
            ".btn-close",
            "button[type='button']:contains('×')",
            "button[type='button']:contains('關閉')"
        ]
        
        for selector in close_selectors:
            try:
                close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if close_button.is_displayed():
                    close_button.click()
                    return True
            except Exception:
                continue
        
        return False
    
    def _press_escape_key(self):
        """Press ESC key to close popup"""
        from selenium.webdriver.common.keys import Keys
        try:
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            return True
        except Exception:
            return False
    
    def _click_backdrop(self):
        """Click backdrop to close popup"""
        try:
            backdrop = self.driver.find_element(By.CSS_SELECTOR, ".modal-backdrop, .backdrop")
            if backdrop.is_displayed():
                backdrop.click()
                return True
        except Exception:
            pass
        return False
    
    def _verify_popup_closed(self):
        """
        Verify that popup is completely closed
        
        Returns:
            bool: True if popup is closed, False if still visible
        """
        try:
            popup_selectors = [
                ".modal-content",
                ".modal-body", 
                ".popup-content",
                ".dialog-content",
                "[role='dialog']",
                ".modal"
            ]
            
            for selector in popup_selectors:
                try:
                    popup = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if popup.is_displayed():
                        self.logger.debug(f"彈窗仍然可見: {selector}")
                        return False
                except Exception:
                    continue
            
            # No visible popup found
            return True
            
        except Exception as e:
            self.logger.debug(f"驗證彈窗關閉時發生錯誤: {e}")
            return True  # Assume closed if verification fails
    
    def get_carousel_baseline(self):
        """
        Get current carousel baseline for comparison
        
        Returns:
            str: Baseline identifier for carousel content
        """
        try:
            if not self.carousel_baseline:
                # Generate baseline from current carousel state
                banners = self.extract_carousel_banners()
                if banners:
                    # Use first banner's carousel_id as baseline
                    self.carousel_baseline = banners[0]['carousel_id']
                    self.logger.info(f"設定輪播基準線: {self.carousel_baseline}")
                else:
                    # Use timestamp as fallback baseline
                    self.carousel_baseline = f"baseline_{int(time.time())}"
                    self.logger.warning(f"使用時間戳作為基準線: {self.carousel_baseline}")
            
            return self.carousel_baseline
            
        except Exception as e:
            self.logger.error(f"獲取輪播基準線時發生錯誤: {e}")
            return f"error_baseline_{int(time.time())}"
    
    def update_carousel_baseline(self, latest_banner_id):
        """
        Update carousel baseline with latest banner information
        
        Args:
            latest_banner_id (str): ID of the latest banner
            
        Returns:
            bool: True if baseline updated successfully, False otherwise
        """
        try:
            if latest_banner_id:
                self.carousel_baseline = latest_banner_id
                self.logger.info(f"更新輪播基準線: {latest_banner_id}")
                return True
            else:
                self.logger.warning("無效的橫幅 ID，無法更新基準線")
                return False
                
        except Exception as e:
            self.logger.error(f"更新輪播基準線時發生錯誤: {e}")
            return False


# Example usage and testing
def main():
    """
    Example usage of CarouselScraper class with Chrome DevTools integration
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('carousel_scraper_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    
    scraper = None
    try:
        # Initialize scraper with DevTools enabled
        logger.info("初始化 CarouselScraper (Chrome DevTools 已啟用)...")
        scraper = CarouselScraper(chromedriver_path, download_dir, logger, use_chrome_devtools=True)
        
        # Set up driver
        scraper.setup_driver()
        
        # Extract carousel banners using enhanced methods
        banners = scraper.extract_carousel_banners()
        
        if banners:
            logger.info(f"成功提取 {len(banners)} 個輪播橫幅:")
            for i, banner in enumerate(banners):
                logger.info(f"橫幅 {i + 1}: {banner['banner_title']}")
                logger.info(f"  圖片 URL: {banner['image_url']}")
                logger.info(f"  課程名稱: {banner['course_name']}")
                logger.info(f"  地點: {banner['location']}")
                logger.info(f"  講師: {banner['instructor']}")
                logger.info(f"  活動連結: {banner['activity_link']}")
                if banner['description']:
                    logger.info(f"  描述: {banner['description'][:100]}...")
                logger.info("-" * 50)
        else:
            logger.info("未找到輪播橫幅")
        
        # Test baseline functionality
        baseline = scraper.get_carousel_baseline()
        logger.info(f"當前基準線: {baseline}")
        
        # Test without DevTools for comparison
        logger.info("\n測試標準 Selenium 模式...")
        scraper.use_chrome_devtools = False
        banners_standard = scraper.extract_carousel_banners()
        logger.info(f"標準模式提取到 {len(banners_standard)} 個橫幅")
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()