#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper Module for Buddhist Education New Book System
使用 Selenium 爬取佛教教育網站的新書資訊
"""

import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


class BookScraper:
    """Web scraper class for extracting new book information from Buddhist education website"""
    
    def __init__(self, chromedriver_path, download_dir, logger=None):
        """
        Initialize BookScraper with Chrome WebDriver configuration
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            download_dir (str): Directory for PDF downloads
            logger (logging.Logger): Logger instance for logging operations
        """
        self.chromedriver_path = chromedriver_path
        self.download_dir = download_dir
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        
        # Validate inputs
        if not os.path.exists(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver not found at: {chromedriver_path}")
        
        # Create download directory if it doesn't exist
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
            self.logger.info(f"已建立下載目錄: {download_dir}")
    
    def setup_driver(self):
        """
        Set up Chrome WebDriver with download preferences for PDF files
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        try:
            # Create Chrome options
            options = webdriver.ChromeOptions()
            
            # Configure download preferences for PDF files
            prefs = {
                "download.default_directory": os.path.abspath(self.download_dir),
                "download.prompt_for_download": False,  # Disable download prompt
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "profile.default_content_settings.popups": 0,
                "profile.default_content_setting_values.automatic_downloads": 1,  # Allow multiple downloads
                "plugins.always_open_pdf_externally": True,  # Download PDFs instead of opening in browser
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 2  # Block images for faster loading
            }
            options.add_experimental_option("prefs", prefs)
            
            # Additional Chrome options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Create Chrome service
            service = Service(self.chromedriver_path)
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            self.logger.info(f"ChromeDriver 已初始化，下載目錄: {self.download_dir}")
            return self.driver
            
        except WebDriverException as e:
            self.logger.error(f"初始化 ChromeDriver 失敗: {e}")
            raise
        except Exception as e:
            self.logger.error(f"設定 WebDriver 時發生錯誤: {e}")
            raise
    
    def cleanup(self):
        """
        Clean up WebDriver resources
        """
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver 已關閉")
            except Exception as e:
                self.logger.warning(f"關閉 WebDriver 時發生錯誤: {e}")
            finally:
                self.driver = None
    
    def navigate_to_website(self, url, max_retries=3, retry_delay=5):
        """
        Navigate to target website URL with network error handling and retry logic
        
        Args:
            url (str): Target website URL
            max_retries (int): Maximum number of retry attempts (default: 3)
            retry_delay (int): Delay between retries in seconds (default: 5)
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        for attempt in range(max_retries + 1):
            try:
                if not self.driver:
                    self.setup_driver()
                
                if attempt > 0:
                    self.logger.info(f"重試訪問網站 (第 {attempt + 1} 次嘗試): {url}")
                    time.sleep(retry_delay)
                else:
                    self.logger.info(f"正在訪問網站: {url}")
                
                self.driver.get(url)
                
                # Log current URL to verify navigation
                current_url = self.driver.current_url
                self.logger.info(f"當前頁面 URL: {current_url}")
                
                return True
                
            except (WebDriverException, ConnectionError, TimeoutError) as e:
                self.logger.warning(f"網路連線錯誤 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    self.logger.error(f"經過 {max_retries + 1} 次嘗試後仍無法訪問網站: {url}")
                    return False
                continue
            except Exception as e:
                self.logger.error(f"導航到網站時發生未預期錯誤: {e}")
                return False
        
        return False
    
    def wait_for_page_load(self, timeout=15):
        """
        Wait for dynamic content to load (up to specified timeout)
        
        Args:
            timeout (int): Maximum wait time in seconds (default: 15)
            
        Returns:
            bool: True if page loaded successfully, False if timeout
        """
        try:
            if not self.driver:
                self.logger.error("WebDriver 未初始化")
                return False
            
            self.logger.info(f"等待頁面載入完成 (最多 {timeout} 秒)...")
            
            # Wait for document ready state
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for SPA content to load
            # Look for book card elements as indicator of content loading
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".card-body"))
                )
                self.logger.info("頁面內容載入完成")
                
                # Additional sleep to ensure all dynamic content is loaded
                time.sleep(3)
                return True
                
            except TimeoutException:
                self.logger.warning("未找到書籍卡片元素，嘗試其他選擇器...")
                
                # Try alternative selectors for different page structures
                alternative_selectors = [
                    ".book-card",
                    ".card",
                    "[class*='card']",
                    ".book-item",
                    ".item"
                ]
                
                for selector in alternative_selectors:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        self.logger.info(f"找到內容元素: {selector}")
                        time.sleep(3)
                        return True
                    except TimeoutException:
                        continue
                
                self.logger.warning("未找到任何書籍元素，但頁面已載入")
                time.sleep(8)  # Give more time for content to appear
                return True
                
        except TimeoutException:
            self.logger.error(f"頁面載入超時 ({timeout} 秒)")
            return False
        except Exception as e:
            self.logger.error(f"等待頁面載入時發生錯誤: {e}")
            return False
    
    def find_new_books(self, baseline_title):
        """
        Identify new books by finding all book cards before the baseline book
        
        Args:
            baseline_title (str): Title or partial title of the baseline book
            
        Returns:
            list: List of book card elements representing new books
        """
        try:
            if not self.driver:
                self.logger.error("WebDriver 未初始化")
                return []
            
            # Try multiple selectors to locate book card elements
            book_cards = []
            selectors_to_try = [
                ".card-body",
                ".book-card", 
                ".card",
                "[class*='card']",
                ".book-item",
                ".item"
            ]
            
            for selector in selectors_to_try:
                book_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if book_cards:
                    self.logger.info(f"使用選擇器 '{selector}' 找到 {len(book_cards)} 個書籍卡片")
                    break
            
            if len(book_cards) == 0:
                self.logger.warning("未找到任何書籍卡片")
                # Debug: Log page source snippet
                try:
                    page_source = self.driver.page_source
                    self.logger.debug(f"頁面原始碼片段 (前500字符): {page_source[:500]}")
                except Exception as e:
                    self.logger.warning(f"無法獲取頁面原始碼: {e}")
                return []
            
            # Find baseline book by title matching
            baseline_index = -1
            for i, card in enumerate(book_cards):
                try:
                    card_text = card.text
                    if baseline_title in card_text:
                        baseline_index = i
                        self.logger.info(f"找到基準書籍 (索引 {i}): {baseline_title}")
                        self.logger.debug(f"基準書籍內容: {card_text[:100]}...")
                        break
                except Exception as e:
                    self.logger.warning(f"讀取卡片 {i} 內容時發生錯誤: {e}")
                    continue
            
            if baseline_index == -1:
                self.logger.error(f"未找到包含基準書名的書籍: {baseline_title}")
                
                # Debug: Log all book titles found on the page
                self.logger.info("=== 調試資訊：網站上找到的所有書籍 ===")
                for i, card in enumerate(book_cards):
                    try:
                        # Try to extract title from h5 tag
                        title_elem = card.find_element(By.TAG_NAME, "h5")
                        title = title_elem.text.strip()
                        self.logger.info(f"書籍 {i+1}: {title}")
                    except Exception as e:
                        # If h5 not found, try to get first few lines of card text
                        try:
                            card_text = card.text.strip()
                            first_line = card_text.split('\n')[0] if card_text else "無法讀取"
                            self.logger.info(f"書籍 {i+1}: {first_line} (從卡片文字提取)")
                        except Exception as e2:
                            self.logger.warning(f"書籍 {i+1}: 無法讀取標題 - {e2}")
                self.logger.info("=== 調試資訊結束 ===")
                
                return []
            
            # Extract books appearing before baseline
            new_books = book_cards[:baseline_index]
            self.logger.info(f"識別出 {len(new_books)} 本新書")
            
            # Log information about new books for debugging
            for i, book in enumerate(new_books):
                try:
                    # Extract title from h5 tag within card
                    title_elem = book.find_element(By.TAG_NAME, "h5")
                    title = title_elem.text
                    self.logger.info(f"新書 {i+1}: {title}")
                except Exception as e:
                    self.logger.warning(f"無法提取新書 {i+1} 的標題: {e}")
            
            return new_books
            
        except NoSuchElementException as e:
            self.logger.error(f"找不到書籍卡片元素: {e}")
            return []
        except Exception as e:
            self.logger.error(f"識別新書時發生錯誤: {e}")
            return []
    
    def get_book_title(self, book_card):
        """
        Extract book title from a book card element
        
        Args:
            book_card: Selenium WebElement representing a book card
            
        Returns:
            str: Book title or empty string if extraction fails
        """
        try:
            # Try to find title in h5 tag
            title_elem = book_card.find_element(By.TAG_NAME, "h5")
            title = title_elem.text.strip()
            return title
        except NoSuchElementException:
            try:
                # Fallback: try to find title in other common elements
                title_elem = book_card.find_element(By.CSS_SELECTOR, ".card-title, .title, h4, h6")
                title = title_elem.text.strip()
                return title
            except NoSuchElementException:
                self.logger.warning("無法找到書籍標題元素")
                return ""
        except Exception as e:
            self.logger.error(f"提取書籍標題時發生錯誤: {e}")
            return ""
    
    def extract_book_info(self, book_card):
        """
        Extract comprehensive book information from a book card element
        
        Args:
            book_card: Selenium WebElement representing a book card
            
        Returns:
            dict: Book information including title, PDF URL, and filename
        """
        book_info = {
            'title': '',
            'pdf_url': '',
            'filename': '',
            'download_path': ''
        }
        
        try:
            # Extract book title
            book_info['title'] = self.get_book_title(book_card)
            if not book_info['title']:
                self.logger.warning("無法提取書籍標題")
                return book_info
            
            self.logger.info(f"正在處理書籍: {book_info['title']}")
            
            # Scroll to book card to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", book_card)
            time.sleep(1)
            
            # Click "電子檔下載" button
            pdf_url = self.click_download_button(book_card)
            if pdf_url:
                book_info['pdf_url'] = pdf_url
                book_info['filename'] = pdf_url.split('/')[-1] if pdf_url else ''
                book_info['download_path'] = os.path.join(self.download_dir, book_info['filename'])
                self.logger.info(f"成功提取 PDF 連結: {book_info['filename']}")
            else:
                self.logger.warning(f"無法提取 PDF 連結: {book_info['title']}")
            
            return book_info
            
        except Exception as e:
            self.logger.error(f"提取書籍資訊時發生錯誤: {e}")
            return book_info
    
    def click_download_button(self, book_card):
        """
        Click "電子檔下載" button and extract PDF download link from modal
        
        Args:
            book_card: Selenium WebElement representing a book card
            
        Returns:
            str: PDF download URL or empty string if extraction fails
        """
        try:
            # Find "電子檔下載" button within the card
            buttons = book_card.find_elements(By.TAG_NAME, "button")
            download_btn = None
            
            for btn in buttons:
                if "電子檔下載" in btn.text:
                    download_btn = btn
                    break
            
            if not download_btn:
                self.logger.warning("找不到電子檔下載按鈕")
                return ""
            
            # Click the download button using JavaScript to avoid element interception
            self.driver.execute_script("arguments[0].click();", download_btn)
            self.logger.info("已點擊電子檔下載按鈕")
            time.sleep(3)  # Wait for modal to appear
            
            # Extract PDF download link from modal
            pdf_url = self.extract_pdf_link_from_modal()
            
            # Close the modal
            self.close_download_modal()
            
            return pdf_url
            
        except Exception as e:
            self.logger.error(f"點擊下載按鈕時發生錯誤: {e}")
            # Try to close modal in case it's still open
            self.close_download_modal()
            return ""
    
    def extract_pdf_link_from_modal(self):
        """
        Extract PDF download link from the opened modal
        
        Returns:
            str: PDF download URL or empty string if not found
        """
        try:
            # Try multiple strategies to find PDF links
            pdf_links = []
            
            # Strategy 1: Find links with .pdf or .PDF in href
            pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(@href,'.pdf') or contains(@href,'.PDF')]")
            
            if len(pdf_links) == 0:
                # Strategy 2: Find links containing PDF text
                pdf_links = self.driver.find_elements(By.XPATH, "//a[contains(text(),'PDF') or contains(text(),'pdf')]")
            
            if len(pdf_links) == 0:
                # Strategy 3: Find all links within modal
                modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal, .modal-dialog, .modal-content")
                if modals:
                    pdf_links = modals[0].find_elements(By.TAG_NAME, "a")
            
            self.logger.info(f"找到 {len(pdf_links)} 個潛在的 PDF 連結")
            
            if len(pdf_links) > 0:
                # Get the first PDF link
                href = pdf_links[0].get_attribute('href')
                if href:
                    self.logger.info(f"提取到 PDF 連結: {href}")
                    return href
                else:
                    self.logger.warning("PDF 連結為空")
                    return ""
            else:
                self.logger.warning("未找到 PDF 連結")
                return ""
                
        except Exception as e:
            self.logger.error(f"從彈窗提取 PDF 連結時發生錯誤: {e}")
            return ""
    
    def close_download_modal(self):
        """
        Close the download modal dialog
        
        Returns:
            bool: True if modal closed successfully, False otherwise
        """
        try:
            time.sleep(2)  # Wait for modal to fully appear
            
            # Strategy 1: Find and click close button
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.close, .close, .modal-close, [data-dismiss='modal']")
            if close_buttons:
                close_buttons[0].click()
                self.logger.info("已關閉彈窗 (關閉按鈕)")
                time.sleep(2)
                return True
            
            # Strategy 2: Press ESC key
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            self.logger.info("已關閉彈窗 (ESC 鍵)")
            time.sleep(2)
            return True
            
        except Exception as e:
            self.logger.warning(f"關閉彈窗時發生錯誤: {e}")
            # Try one more time with ESC key
            try:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(2)
                return True
            except:
                return False
    
    def download_pdf(self, pdf_url, filename, max_retries=3, retry_delay=10):
        """
        Download PDF using extracted URL and save with original filename
        Enhanced with network error handling and retry logic
        
        Args:
            pdf_url (str): PDF download URL
            filename (str): Original filename for the PDF
            max_retries (int): Maximum number of retry attempts (default: 3)
            retry_delay (int): Delay between retries in seconds (default: 10)
            
        Returns:
            tuple: (success: bool, file_path: str, error_message: str)
        """
        if not pdf_url or not filename:
            error_msg = "PDF URL 或檔案名稱為空"
            self.logger.error(error_msg)
            return False, "", error_msg
        
        file_path = os.path.join(self.download_dir, filename)
        
        for attempt in range(max_retries + 1):
            try:
                import requests
                import urllib3
                
                # Disable SSL warnings for this request
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                if attempt > 0:
                    self.logger.info(f"重試下載 PDF (第 {attempt + 1} 次嘗試): {filename}")
                    time.sleep(retry_delay)
                else:
                    self.logger.info(f"開始下載 PDF: {filename}")
                
                self.logger.debug(f"下載 URL: {pdf_url}")
                
                # Configure request headers to mimic browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/pdf,application/octet-stream,*/*',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # Make request with timeout
                response = requests.get(
                    pdf_url, 
                    headers=headers, 
                    timeout=120,  # 2 minutes timeout
                    verify=False,  # Skip SSL verification if needed
                    stream=True    # Stream download for large files
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'octet-stream' not in content_type:
                    self.logger.warning(f"內容類型可能不是 PDF: {content_type}")
                
                # Get file size
                content_length = response.headers.get('content-length')
                if content_length:
                    file_size_mb = int(content_length) / (1024 * 1024)
                    self.logger.info(f"檔案大小: {file_size_mb:.2f} MB")
                
                # Write file in chunks
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was created and has content
                if os.path.exists(file_path):
                    actual_size = os.path.getsize(file_path)
                    if actual_size > 0:
                        self.logger.info(f"✓ PDF 下載成功: {filename} ({actual_size} bytes)")
                        return True, file_path, ""
                    else:
                        error_msg = f"下載的檔案為空: {filename}"
                        self.logger.error(error_msg)
                        # Remove empty file
                        try:
                            os.remove(file_path)
                        except:
                            pass
                        return False, "", error_msg
                else:
                    error_msg = f"檔案未成功建立: {filename}"
                    self.logger.error(error_msg)
                    return False, "", error_msg
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, 
                    requests.exceptions.ChunkedEncodingError) as e:
                self.logger.warning(f"網路連線錯誤 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    error_msg = f"經過 {max_retries + 1} 次嘗試後仍無法下載: {filename} - {e}"
                    self.logger.error(error_msg)
                    return False, "", error_msg
                continue
            except requests.exceptions.HTTPError as e:
                # HTTP errors (4xx, 5xx) - don't retry for client errors (4xx)
                if hasattr(e.response, 'status_code') and 400 <= e.response.status_code < 500:
                    error_msg = f"HTTP 客戶端錯誤 ({e.response.status_code}): {filename} - {e}"
                    self.logger.error(error_msg)
                    return False, "", error_msg
                else:
                    # Server errors (5xx) - retry
                    self.logger.warning(f"HTTP 伺服器錯誤 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt == max_retries:
                        error_msg = f"經過 {max_retries + 1} 次嘗試後仍有 HTTP 錯誤: {filename} - {e}"
                        self.logger.error(error_msg)
                        return False, "", error_msg
                    continue
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"請求錯誤 (嘗試 {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    error_msg = f"經過 {max_retries + 1} 次嘗試後仍有請求錯誤: {filename} - {e}"
                    self.logger.error(error_msg)
                    return False, "", error_msg
                continue
            except Exception as e:
                error_msg = f"下載 PDF 時發生未預期錯誤: {e}"
                self.logger.error(error_msg)
                return False, "", error_msg
        
        return False, "", "未知錯誤"
    
    def process_book_download(self, book_card, book_index=None, total_books=None):
        """
        Process a single book: extract info and download PDF with enhanced file system error handling
        
        Args:
            book_card: Selenium WebElement representing a book card
            book_index (int): Index of current book (for logging)
            total_books (int): Total number of books (for logging)
            
        Returns:
            dict: Book information with download status
        """
        try:
            # Log progress if indices provided
            if book_index is not None and total_books is not None:
                self.logger.info(f"處理書籍 {book_index + 1}/{total_books}")
            
            # Extract book information
            book_info = self.extract_book_info(book_card)
            
            if not book_info['title']:
                self.logger.warning("跳過無標題的書籍")
                book_info['download_success'] = False
                book_info['error_message'] = "無法提取書籍標題"
                return book_info
            
            if not book_info['pdf_url']:
                self.logger.warning(f"跳過無 PDF 連結的書籍: {book_info['title']}")
                book_info['download_success'] = False
                book_info['error_message'] = "無法提取 PDF 連結"
                return book_info
            
            # Check download directory accessibility before attempting download
            try:
                if not os.path.exists(self.download_dir):
                    os.makedirs(self.download_dir, exist_ok=True)
                    self.logger.info(f"建立下載目錄: {self.download_dir}")
                
                # Test write permissions
                test_file = os.path.join(self.download_dir, '.write_test')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except (PermissionError, OSError) as e:
                    raise Exception(f"下載目錄無寫入權限: {self.download_dir} - {e}")
                    
            except Exception as dir_error:
                error_msg = f"下載目錄錯誤: {dir_error}"
                self.logger.error(error_msg)
                book_info['download_success'] = False
                book_info['error_message'] = error_msg
                return book_info
            
            # Download PDF with file system error handling
            success, file_path, error_msg = self.download_pdf(book_info['pdf_url'], book_info['filename'])
            
            book_info['download_success'] = success
            book_info['download_path'] = file_path if success else ""
            book_info['error_message'] = error_msg
            
            # Additional file system validation if download was successful
            if success and file_path:
                try:
                    # Verify file exists and is readable
                    if not os.path.exists(file_path):
                        error_msg = f"下載的檔案不存在: {file_path}"
                        self.logger.error(error_msg)
                        book_info['download_success'] = False
                        book_info['error_message'] = error_msg
                    elif not os.path.isfile(file_path):
                        error_msg = f"下載路徑不是檔案: {file_path}"
                        self.logger.error(error_msg)
                        book_info['download_success'] = False
                        book_info['error_message'] = error_msg
                    elif not os.access(file_path, os.R_OK):
                        error_msg = f"下載的檔案無讀取權限: {file_path}"
                        self.logger.error(error_msg)
                        book_info['download_success'] = False
                        book_info['error_message'] = error_msg
                    else:
                        # Check file size
                        file_size = os.path.getsize(file_path)
                        if file_size == 0:
                            error_msg = f"下載的檔案為空: {file_path}"
                            self.logger.error(error_msg)
                            book_info['download_success'] = False
                            book_info['error_message'] = error_msg
                            # Remove empty file
                            try:
                                os.remove(file_path)
                                self.logger.info(f"已刪除空檔案: {file_path}")
                            except Exception as remove_error:
                                self.logger.warning(f"無法刪除空檔案: {remove_error}")
                        else:
                            book_info['file_size_bytes'] = file_size
                            
                except Exception as validation_error:
                    error_msg = f"檔案驗證失敗: {validation_error}"
                    self.logger.error(error_msg)
                    book_info['download_success'] = False
                    book_info['error_message'] = error_msg
            
            # Log download status
            if book_info['download_success']:
                self.logger.info(f"✓ 成功處理: {book_info['title']}")
            else:
                self.logger.error(f"✗ 處理失敗: {book_info['title']} - {book_info['error_message']}")
            
            return book_info
            
        except Exception as e:
            error_msg = f"處理書籍時發生錯誤: {e}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'title': self.get_book_title(book_card) if book_card else "未知",
                'pdf_url': '',
                'filename': '',
                'download_path': '',
                'download_success': False,
                'error_message': error_msg
            }
    
    def get_download_summary(self, processed_books):
        """
        Generate a summary of download results
        
        Args:
            processed_books (list): List of processed book information dictionaries
            
        Returns:
            dict: Summary statistics
        """
        total_books = len(processed_books)
        successful_downloads = sum(1 for book in processed_books if book.get('download_success', False))
        failed_downloads = total_books - successful_downloads
        
        summary = {
            'total_books': total_books,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'success_rate': (successful_downloads / total_books * 100) if total_books > 0 else 0
        }
        
        self.logger.info("=" * 50)
        self.logger.info("下載摘要")
        self.logger.info("=" * 50)
        self.logger.info(f"總書籍數: {summary['total_books']}")
        self.logger.info(f"成功下載: {summary['successful_downloads']}")
        self.logger.info(f"下載失敗: {summary['failed_downloads']}")
        self.logger.info(f"成功率: {summary['success_rate']:.1f}%")
        self.logger.info("=" * 50)
        
        return summary
# Example usage and main function for testing
def main():
    """
    Example usage of BookScraper class
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('book_scraper_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    target_url = "https://www.budaedu.org/#/books/applicable/chinese"
    baseline_title = "CH754-02"
    
    scraper = None
    try:
        # Initialize scraper
        logger.info("初始化 BookScraper...")
        scraper = BookScraper(chromedriver_path, download_dir, logger)
        
        # Set up driver and navigate
        scraper.setup_driver()
        if not scraper.navigate_to_website(target_url):
            logger.error("無法訪問目標網站")
            return
        
        # Wait for page to load
        if not scraper.wait_for_page_load():
            logger.error("頁面載入失敗")
            return
        
        # Find new books
        new_books = scraper.find_new_books(baseline_title)
        if not new_books:
            logger.info("沒有找到新書")
            return
        
        # Process each new book
        processed_books = []
        for i, book_card in enumerate(new_books):
            book_info = scraper.process_book_download(book_card, i, len(new_books))
            processed_books.append(book_info)
        
        # Generate summary
        scraper.get_download_summary(processed_books)
        
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {e}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()