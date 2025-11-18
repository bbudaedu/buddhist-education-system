#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulletin Scraper Module for Buddhist Education Website Monitoring
佛教教育網站公告監控的爬蟲模組

This module extends BookScraper to handle course cancellation monitoring
from the Buddhist Education website bulletin pages.
"""

import os
import time
import logging
import hashlib
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from book_scraper import BookScraper
from enhanced_baseline_manager import EnhancedBaselineManager


class BulletinScraper(BookScraper):
    """
    Bulletin scraper class for extracting course cancellation information
    from Buddhist education website bulletin pages
    
    Extends BookScraper to reuse existing web automation infrastructure
    """
    
    def __init__(self, chromedriver_path, download_dir, logger=None):
        """
        Initialize BulletinScraper with Chrome WebDriver configuration
        
        Args:
            chromedriver_path (str): Path to ChromeDriver executable
            download_dir (str): Directory for temporary files (inherited from BookScraper)
            logger (logging.Logger): Logger instance for logging operations
        """
        super().__init__(chromedriver_path, download_dir, logger)
        
        # Bulletin-specific configuration
        self.bulletin_url = "https://www.budaedu.org/#/bulletins/course-cancel"
        self.content_type = "cancellation"
        
        # Initialize enhanced baseline manager
        self.baseline_manager = EnhancedBaselineManager("website_monitoring", download_dir, logger)
        
        self.logger.info("BulletinScraper initialized for course cancellation monitoring")
    
    def navigate_to_bulletin_page(self, max_retries=3, retry_delay=5):
        """
        Navigate to course cancellation bulletin page
        
        Args:
            max_retries (int): Maximum number of retry attempts (default: 3)
            retry_delay (int): Delay between retries in seconds (default: 5)
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.logger.info(f"Navigating to bulletin page: {self.bulletin_url}")
            
            # Use inherited navigation method from BookScraper
            success = self.navigate_to_website(self.bulletin_url, max_retries, retry_delay)
            
            if success:
                # Wait for bulletin-specific content to load
                success = self.wait_for_bulletin_content()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error navigating to bulletin page: {e}")
            return False
    
    def wait_for_bulletin_content(self, timeout=15):
        """
        Wait for bulletin page content to load completely
        
        Args:
            timeout (int): Maximum wait time in seconds (default: 15)
            
        Returns:
            bool: True if content loaded successfully, False if timeout
        """
        try:
            self.logger.info(f"Waiting for bulletin content to load (max {timeout} seconds)...")
            
            # Wait for document ready state first
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Look for table elements that contain cancellation data
            table_selectors = [
                "table",
                ".table",
                "[class*='table']",
                "tbody",
                ".bulletin-table",
                ".cancellation-table"
            ]
            
            table_found = False
            for selector in table_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Found bulletin table with selector: {selector}")
                    table_found = True
                    break
                except TimeoutException:
                    continue
            
            if not table_found:
                self.logger.warning("No table elements found, but page loaded")
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            self.logger.info("Bulletin content loading completed")
            return True
            
        except TimeoutException:
            self.logger.error(f"Bulletin content loading timeout ({timeout} seconds)")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for bulletin content: {e}")
            return False
    
    def extract_cancellation_table(self):
        """
        Extract course cancellation information from bulletin table
        
        Returns:
            List[Dict]: List of cancellation records with structured data
        """
        try:
            if not self.driver:
                self.logger.error("WebDriver not initialized")
                return []
            
            self.logger.info("Extracting cancellation table data...")
            
            # Find table elements
            table_rows = self.find_table_rows()
            if not table_rows:
                self.logger.warning("No table rows found")
                return []
            
            cancellations = []
            for i, row in enumerate(table_rows):
                try:
                    cancellation_data = self.parse_table_row(row)
                    if cancellation_data:
                        cancellations.append(cancellation_data)
                        self.logger.info(f"Extracted cancellation {i+1}: {cancellation_data['course_name']}")
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing table row {i+1}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(cancellations)} cancellation records")
            return cancellations
            
        except Exception as e:
            self.logger.error(f"Error extracting cancellation table: {e}")
            return []
    
    def find_table_rows(self):
        """
        Find table rows containing cancellation data
        
        Returns:
            List: List of WebElement objects representing table rows
        """
        try:
            # Try multiple strategies to find table rows
            row_selectors = [
                "tbody tr",
                "table tr",
                ".table tr",
                "tr",
                "[class*='table'] tr",
                ".bulletin-row",
                ".cancellation-row"
            ]
            
            table_rows = []
            for selector in row_selectors:
                try:
                    rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if rows:
                        # Filter out header rows (usually first row)
                        filtered_rows = []
                        for row in rows:
                            row_text = row.text.strip()
                            # Skip empty rows and header rows
                            if (row_text and 
                                not any(header in row_text.lower() for header in 
                                       ['日期', 'date', '課程', 'course', '講師', 'instructor', '標題', 'title'])):
                                filtered_rows.append(row)
                        
                        if filtered_rows:
                            self.logger.info(f"Found {len(filtered_rows)} data rows using selector: {selector}")
                            return filtered_rows
                            
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            self.logger.warning("No table rows found with any selector")
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding table rows: {e}")
            return []
    
    def parse_table_row(self, row_element):
        """
        Parse a single table row to extract cancellation information
        
        Args:
            row_element: Selenium WebElement representing a table row
            
        Returns:
            Dict: Cancellation information with required fields or None if parsing fails
        """
        try:
            # Get all cells in the row
            cells = row_element.find_elements(By.TAG_NAME, "td")
            if not cells:
                # Try alternative cell selectors
                cells = row_element.find_elements(By.CSS_SELECTOR, "th, td, .cell, [class*='cell']")
            
            if len(cells) < 3:
                self.logger.debug(f"Row has insufficient cells ({len(cells)}), skipping")
                return None
            
            # Extract text from cells
            cell_texts = [cell.text.strip() for cell in cells]
            
            # Parse based on expected table structure
            # Typical structure: [Date, Course Name, Instructor, ...]
            cancellation_date = self.parse_date_field(cell_texts[0])
            course_name = cell_texts[1] if len(cell_texts) > 1 else ""
            instructor_name = cell_texts[2] if len(cell_texts) > 2 else ""
            
            # Validate required fields
            if not cancellation_date or not course_name:
                self.logger.debug(f"Missing required fields in row: date={cancellation_date}, course={course_name}")
                return None
            
            # Generate unique ID for this cancellation
            cancellation_id = self.generate_cancellation_id(cancellation_date, course_name, instructor_name)
            
            cancellation_data = {
                'cancellation_id': cancellation_id,
                'cancellation_date': cancellation_date,
                'course_name': course_name,
                'instructor_name': instructor_name or "未指定講師",
                'extraction_timestamp': datetime.now(),
                'content_type': self.content_type,
                'raw_row_data': cell_texts  # Keep original data for debugging
            }
            
            return cancellation_data
            
        except Exception as e:
            self.logger.error(f"Error parsing table row: {e}")
            return None
    
    def parse_date_field(self, date_text):
        """
        Parse date field from table cell text
        
        Args:
            date_text (str): Raw date text from table cell
            
        Returns:
            date: Parsed date object or None if parsing fails
        """
        try:
            if not date_text:
                return None
            
            # Clean up date text
            date_text = date_text.strip()
            
            # Try multiple date formats commonly used
            date_formats = [
                "%Y-%m-%d",      # 2024-01-15
                "%Y/%m/%d",      # 2024/01/15
                "%m/%d/%Y",      # 01/15/2024
                "%d/%m/%Y",      # 15/01/2024
                "%Y.%m.%d",      # 2024.01.15
                "%m-%d-%Y",      # 01-15-2024
                "%d-%m-%Y",      # 15-01-2024
            ]
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(date_text, date_format).date()
                    self.logger.debug(f"Successfully parsed date: {date_text} -> {parsed_date}")
                    return parsed_date
                except ValueError:
                    continue
            
            # Try to extract date from text containing other characters
            import re
            
            # Look for patterns like "2024-01-15" within the text
            date_patterns = [
                r'(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})',  # YYYY-MM-DD variants
                r'(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4})',  # MM-DD-YYYY variants
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    extracted_date = match.group(1)
                    # Try parsing the extracted date
                    for date_format in date_formats:
                        try:
                            parsed_date = datetime.strptime(extracted_date, date_format).date()
                            self.logger.debug(f"Extracted and parsed date: {extracted_date} -> {parsed_date}")
                            return parsed_date
                        except ValueError:
                            continue
            
            self.logger.warning(f"Could not parse date: {date_text}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing date field: {e}")
            return None
    
    def generate_cancellation_id(self, cancellation_date, course_name, instructor_name):
        """
        Generate unique ID for cancellation record
        
        Args:
            cancellation_date (date): Date of cancellation
            course_name (str): Name of cancelled course
            instructor_name (str): Name of instructor
            
        Returns:
            str: Unique cancellation ID
        """
        try:
            # Create unique string from key fields
            id_string = f"{cancellation_date}_{course_name}_{instructor_name}"
            
            # Generate hash for consistent ID
            hash_object = hashlib.md5(id_string.encode('utf-8'))
            cancellation_id = f"cancel_{hash_object.hexdigest()[:12]}"
            
            return cancellation_id
            
        except Exception as e:
            self.logger.error(f"Error generating cancellation ID: {e}")
            # Fallback to timestamp-based ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"cancel_{timestamp}"
    
    def get_cancellation_baseline(self):
        """
        Get the current baseline for cancellation detection
        This will be used to identify new cancellations
        
        Returns:
            date: Latest cancellation date from baseline or None if no baseline
        """
        try:
            return self.baseline_manager.get_cancellation_baseline()
            
        except Exception as e:
            self.logger.error(f"Error getting cancellation baseline: {e}")
            return None
    
    def update_cancellation_baseline(self, latest_date):
        """
        Update the baseline with the latest cancellation date
        
        Args:
            latest_date (date): Latest cancellation date to set as new baseline
            
        Returns:
            bool: True if baseline updated successfully, False otherwise
        """
        try:
            return self.baseline_manager.update_cancellation_baseline(latest_date)
            
        except Exception as e:
            self.logger.error(f"Error updating cancellation baseline: {e}")
            return False
    
    def filter_new_cancellations(self, all_cancellations):
        """
        Filter cancellations to identify only new ones based on baseline
        
        Args:
            all_cancellations (List[Dict]): All extracted cancellation records
            
        Returns:
            List[Dict]: New cancellation records only
        """
        try:
            baseline_date = self.get_cancellation_baseline()
            
            if not baseline_date:
                self.logger.info("No baseline date found, treating all cancellations as new")
                return all_cancellations
            
            new_cancellations = []
            for cancellation in all_cancellations:
                cancellation_date = cancellation.get('cancellation_date')
                if cancellation_date and cancellation_date > baseline_date:
                    new_cancellations.append(cancellation)
            
            self.logger.info(f"Filtered {len(new_cancellations)} new cancellations from {len(all_cancellations)} total")
            return new_cancellations
            
        except Exception as e:
            self.logger.error(f"Error filtering new cancellations: {e}")
            return all_cancellations  # Return all if filtering fails
    
    def process_cancellation_monitoring(self):
        """
        Complete cancellation monitoring process
        
        Returns:
            Dict: Processing results with cancellation data and status
        """
        try:
            self.logger.info("Starting course cancellation monitoring process")
            
            # Set up driver if not already done
            if not self.driver:
                self.setup_driver()
            
            # Navigate to bulletin page
            if not self.navigate_to_bulletin_page():
                return {
                    'success': False,
                    'error': 'Failed to navigate to bulletin page',
                    'cancellations': []
                }
            
            # Extract all cancellation data
            all_cancellations = self.extract_cancellation_table()
            
            if not all_cancellations:
                self.logger.info("No cancellation data found")
                return {
                    'success': True,
                    'message': 'No cancellation data found',
                    'cancellations': [],
                    'new_cancellations': []
                }
            
            # Filter for new cancellations
            new_cancellations = self.filter_new_cancellations(all_cancellations)
            
            # Update baseline if we have new cancellations
            if new_cancellations:
                latest_date = max(c['cancellation_date'] for c in new_cancellations)
                self.update_cancellation_baseline(latest_date)
            
            result = {
                'success': True,
                'message': f'Successfully processed {len(all_cancellations)} cancellations, {len(new_cancellations)} new',
                'cancellations': all_cancellations,
                'new_cancellations': new_cancellations,
                'extraction_timestamp': datetime.now(),
                'content_type': self.content_type
            }
            
            self.logger.info(f"Cancellation monitoring completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Error in cancellation monitoring process: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'cancellations': []
            }
        finally:
            # Clean up resources
            if self.driver:
                try:
                    self.cleanup()
                except Exception as cleanup_error:
                    self.logger.warning(f"Error during cleanup: {cleanup_error}")


# Example usage and testing functions
def main():
    """
    Example usage of BulletinScraper class for testing
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bulletin_scraper_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"  # Not used for bulletin scraping but required by parent class
    
    scraper = None
    try:
        # Initialize scraper
        logger.info("Initializing BulletinScraper...")
        scraper = BulletinScraper(chromedriver_path, download_dir, logger)
        
        # Process cancellation monitoring
        result = scraper.process_cancellation_monitoring()
        
        if result['success']:
            logger.info("Cancellation monitoring completed successfully")
            logger.info(f"Total cancellations: {len(result['cancellations'])}")
            logger.info(f"New cancellations: {len(result['new_cancellations'])}")
            
            # Log details of new cancellations
            for cancellation in result['new_cancellations']:
                logger.info(f"New cancellation: {cancellation['course_name']} on {cancellation['cancellation_date']}")
        else:
            logger.error(f"Cancellation monitoring failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()