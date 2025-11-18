#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Media Processor Module for Website Monitoring
多媒體內容處理模組

This module extends BookScraper to handle multimedia content extraction
from the Buddhist Education website, including lecture introduction links,
course titles, speaker information, and start dates.
"""

import os
import time
import logging
import hashlib
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from book_scraper import BookScraper
from enhanced_baseline_manager import EnhancedBaselineManager


class MediaProcessor(BookScraper):
    """
    Media processor class for extracting multimedia content information
    from Buddhist education website
    
    Extends BookScraper to handle:
    - Lecture introduction links
    - Course titles and speaker information
    - Start dates and media types
    - Redirect URL processing
    """
    
    def __init__(self, chromedriver_path: str, download_dir: str, 
                 baseline_manager: Optional[EnhancedBaselineManager] = None,
                 logger: Optional[logging.Logger] = None,
                 media_url: Optional[str] = None):
        """
        Initialize MediaProcessor with enhanced functionality
        
        Args:
            chromedriver_path: Path to ChromeDriver executable
            download_dir: Directory for downloads (inherited from BookScraper)
            baseline_manager: Enhanced baseline manager for media content tracking
            logger: Logger instance for logging operations
            media_url: Single media URL to monitor (from config)
        """
        super().__init__(chromedriver_path, download_dir, logger)
        
        self.baseline_manager = baseline_manager or EnhancedBaselineManager(
            project_name="media_monitoring", 
            cache_dir=os.path.dirname(download_dir) or ".",
            logger=self.logger
        )
        
        # Media content URLs - use provided URL or default
        if media_url:
            self.media_urls = {
                "media": media_url
            }
        else:
            # Fallback to default URL
            self.media_urls = {
                "live_streaming": "https://www.budaedu.org/#/series/live-streaming"
            }
        
        # CSS selectors for media content elements
        self.media_selectors = {
            "lecture_links": [
                "a[href*='lecture']",
                "a[href*='series']", 
                "a[href*='streaming']",
                ".lecture-link",
                ".series-link",
                ".media-link"
            ],
            "course_title": [
                "h1", "h2", "h3", "h4", "h5",
                ".title", ".course-title", ".lecture-title",
                ".card-title", ".series-title"
            ],
            "speaker_info": [
                ".speaker", ".instructor", ".teacher",
                ".author", ".presenter", ".lecturer",
                "p:contains('講師')", "p:contains('主講')",
                "span:contains('講師')", "span:contains('主講')"
            ],
            "date_info": [
                ".date", ".start-date", ".course-date",
                "time", ".datetime", ".schedule",
                "p:contains('日期')", "span:contains('日期')"
            ]
        }
        
        self.logger.info("MediaProcessor initialized successfully")
    
    def extract_media_content(self, max_items: int = 50) -> List[Dict[str, Any]]:
        """
        Extract multimedia content from all media sections
        
        Args:
            max_items: Maximum number of media items to process
            
        Returns:
            List[Dict]: List of extracted media content information
        """
        all_media_content = []
        
        try:
            self.logger.info("Starting multimedia content extraction")
            
            # Process each media URL
            for section_name, url in self.media_urls.items():
                self.logger.info(f"Processing {section_name} section: {url}")
                
                section_content = self._extract_from_section(url, section_name, max_items)
                all_media_content.extend(section_content)
                
                # Respect rate limiting
                time.sleep(2)
            
            # Remove duplicates based on redirect URL or content hash
            unique_content = self._remove_duplicate_content(all_media_content)
            
            self.logger.info(f"Extracted {len(unique_content)} unique media items")
            return unique_content
            
        except Exception as e:
            self.logger.error(f"Error extracting media content: {e}")
            return []
    
    def _extract_from_section(self, url: str, section_name: str, max_items: int) -> List[Dict[str, Any]]:
        """
        Extract media content from a specific section
        
        Args:
            url: URL of the section to process
            section_name: Name of the section for logging
            max_items: Maximum items to extract from this section
            
        Returns:
            List[Dict]: Extracted media content from this section
        """
        section_content = []
        
        try:
            # Navigate to the section
            if not self.navigate_to_website(url):
                self.logger.error(f"Failed to navigate to {section_name}: {url}")
                return []
            
            # Wait for page to load
            if not self.wait_for_page_load():
                self.logger.warning(f"Page load timeout for {section_name}")
                # Continue anyway, might still find content
            
            # Find lecture introduction links
            lecture_links = self._find_lecture_links()
            
            if not lecture_links:
                self.logger.warning(f"No lecture links found in {section_name}")
                return []
            
            self.logger.info(f"Found {len(lecture_links)} lecture links in {section_name}")
            
            # Process each lecture link (up to max_items)
            for i, href_url in enumerate(lecture_links[:max_items]):
                try:
                    media_info = self._process_lecture_url(href_url, section_name, i + 1)
                    if media_info:
                        section_content.append(media_info)
                    
                    # Small delay between processing items
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing lecture link {i + 1} in {section_name}: {e}")
                    continue
            
            return section_content
            
        except Exception as e:
            self.logger.error(f"Error extracting from section {section_name}: {e}")
            return []
    
    def _find_lecture_links(self) -> List:
        """
        Find lecture introduction links on the current page
        
        Returns:
            List: List of WebElement objects representing lecture links
        """
        lecture_links = []
        
        try:
            # Try multiple selectors to find lecture links
            for selector in self.media_selectors["lecture_links"]:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        lecture_links.extend(links)
                        self.logger.debug(f"Found {len(links)} links with selector: {selector}")
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Extract href URLs immediately to avoid stale element issues
            unique_hrefs = []
            seen_hrefs = set()
            
            for link in lecture_links:
                try:
                    href = link.get_attribute('href')
                    if href and href not in seen_hrefs:
                        unique_hrefs.append(href)
                        seen_hrefs.add(href)
                except Exception as e:
                    self.logger.debug(f"Error getting href from link: {e}")
                    continue
            
            self.logger.info(f"Found {len(unique_hrefs)} unique lecture links")
            return unique_hrefs
            
        except Exception as e:
            self.logger.error(f"Error finding lecture links: {e}")
            return []
    
    def _process_lecture_url(self, redirect_url: str, section_name: str, item_index: int) -> Optional[Dict[str, Any]]:
        """
        Process a single lecture URL to extract media information
        
        Args:
            redirect_url: URL of the lecture link
            section_name: Name of the section for context
            item_index: Index of the item for logging
            
        Returns:
            Dict: Media information or None if extraction fails
        """
        try:
            if not redirect_url:
                self.logger.warning(f"No URL provided for lecture link {item_index}")
                return None
            
            self.logger.info(f"Processing lecture link {item_index}: {redirect_url}")
            
            # Extract basic information from the current page context
            media_info = {
                'media_id': self._generate_media_id(redirect_url),
                'course_title': '',
                'speaker_name': '',
                'start_date': None,
                'redirect_url': redirect_url,
                'media_type': self._determine_media_type(redirect_url, section_name),
                'extraction_timestamp': datetime.now(),
                'content_type': 'media',
                'section_name': section_name,
                'item_index': item_index
            }
            
            # Try to extract information from the redirect page
            enhanced_info = self._extract_from_redirect_page(redirect_url)
            if enhanced_info:
                # Update with enhanced information
                for key, value in enhanced_info.items():
                    if value and not media_info.get(key):
                        media_info[key] = value
            

            
            # Validate that we have minimum required information
            if not media_info['course_title'] and not media_info['speaker_name']:
                self.logger.warning(f"Insufficient information extracted for lecture link {item_index}")
                return None
            
            # Set default values for missing information
            if not media_info['course_title']:
                media_info['course_title'] = f"未知課程 ({section_name})"
            
            if not media_info['speaker_name']:
                media_info['speaker_name'] = "未知講師"
            
            if not media_info['start_date']:
                media_info['start_date'] = date.today()
            
            self.logger.info(f"Successfully extracted media info: {media_info['course_title']} by {media_info['speaker_name']}")
            return media_info
            
        except Exception as e:
            self.logger.error(f"Error processing lecture link {item_index}: {e}")
            return None
    
    def _generate_media_id(self, redirect_url: str) -> str:
        """
        Generate a unique media ID based on the redirect URL
        
        Args:
            redirect_url: The redirect URL for the media content
            
        Returns:
            str: Unique media ID
        """
        try:
            # Create hash from URL and timestamp
            url_hash = hashlib.md5(redirect_url.encode('utf-8')).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d")
            return f"media_{timestamp}_{url_hash}"
        except Exception as e:
            self.logger.warning(f"Error generating media ID: {e}")
            return f"media_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _determine_media_type(self, redirect_url: str, section_name: str) -> str:
        """
        Determine the media type based on URL and section
        
        Args:
            redirect_url: The redirect URL
            section_name: The section name where the link was found
            
        Returns:
            str: Media type classification
        """
        try:
            url_lower = redirect_url.lower()
            section_lower = section_name.lower()
            
            # Check URL patterns
            if 'streaming' in url_lower or 'live' in url_lower:
                return 'live_streaming'
            elif 'video' in url_lower or 'mp4' in url_lower:
                return 'video'
            elif 'audio' in url_lower or 'mp3' in url_lower:
                return 'audio'
            elif 'series' in url_lower:
                return 'lecture_series'
            
            # Check section patterns
            if 'streaming' in section_lower:
                return 'live_streaming'
            elif 'series' in section_lower:
                return 'lecture_series'
            elif 'multimedia' in section_lower:
                return 'multimedia'
            
            return 'unknown'
            
        except Exception as e:
            self.logger.warning(f"Error determining media type: {e}")
            return 'unknown'
    
    def _extract_course_title_from_context(self, link_element) -> str:
        """
        Extract course title from the link element's context
        
        Args:
            link_element: WebElement representing the lecture link
            
        Returns:
            str: Course title or empty string if not found
        """
        try:
            # Try to get title from link text first
            link_text = link_element.text.strip()
            if link_text and len(link_text) > 3:
                return link_text
            
            # Try to find title in parent elements
            parent = link_element.find_element(By.XPATH, "..")
            
            # Look for title elements in parent
            for selector in self.media_selectors["course_title"]:
                try:
                    title_elem = parent.find_element(By.CSS_SELECTOR, selector)
                    title = title_elem.text.strip()
                    if title and len(title) > 3:
                        return title
                except NoSuchElementException:
                    continue
            
            # Try grandparent if parent didn't work
            try:
                grandparent = parent.find_element(By.XPATH, "..")
                for selector in self.media_selectors["course_title"]:
                    try:
                        title_elem = grandparent.find_element(By.CSS_SELECTOR, selector)
                        title = title_elem.text.strip()
                        if title and len(title) > 3:
                            return title
                    except NoSuchElementException:
                        continue
            except NoSuchElementException:
                pass
            
            return ""
            
        except Exception as e:
            self.logger.debug(f"Error extracting course title from context: {e}")
            return ""
    
    def _extract_speaker_from_context(self, link_element) -> str:
        """
        Extract speaker information from the link element's context
        
        Args:
            link_element: WebElement representing the lecture link
            
        Returns:
            str: Speaker name or empty string if not found
        """
        try:
            # Try to find speaker info in parent elements
            parent = link_element.find_element(By.XPATH, "..")
            
            # Look for speaker elements in parent
            for selector in self.media_selectors["speaker_info"]:
                try:
                    speaker_elem = parent.find_element(By.CSS_SELECTOR, selector)
                    speaker = speaker_elem.text.strip()
                    if speaker and len(speaker) > 1:
                        # Clean up speaker text
                        speaker = speaker.replace('講師:', '').replace('主講:', '').replace('講師', '').strip()
                        if speaker:
                            return speaker
                except NoSuchElementException:
                    continue
            
            # Try to find speaker info in text content using patterns
            parent_text = parent.text
            if parent_text:
                # Look for patterns like "講師：XXX" or "主講：XXX"
                import re
                speaker_patterns = [
                    r'講師[：:]\s*([^\n\r]+)',
                    r'主講[：:]\s*([^\n\r]+)',
                    r'授課[：:]\s*([^\n\r]+)',
                    r'老師[：:]\s*([^\n\r]+)'
                ]
                
                for pattern in speaker_patterns:
                    match = re.search(pattern, parent_text)
                    if match:
                        speaker = match.group(1).strip()
                        if speaker and len(speaker) > 1:
                            return speaker
            
            return ""
            
        except Exception as e:
            self.logger.debug(f"Error extracting speaker from context: {e}")
            return ""
    
    def _extract_date_from_context(self, link_element) -> Optional[date]:
        """
        Extract date information from the link element's context
        
        Args:
            link_element: WebElement representing the lecture link
            
        Returns:
            date: Start date or None if not found
        """
        try:
            # Try to find date info in parent elements
            parent = link_element.find_element(By.XPATH, "..")
            
            # Look for date elements in parent
            for selector in self.media_selectors["date_info"]:
                try:
                    date_elem = parent.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_elem.text.strip()
                    if date_text:
                        parsed_date = self._parse_date_string(date_text)
                        if parsed_date:
                            return parsed_date
                except NoSuchElementException:
                    continue
            
            # Try to find date in text content using patterns
            parent_text = parent.text
            if parent_text:
                parsed_date = self._parse_date_from_text(parent_text)
                if parsed_date:
                    return parsed_date
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting date from context: {e}")
            return None
    
    def _parse_date_string(self, date_text: str) -> Optional[date]:
        """
        Parse date string into date object
        
        Args:
            date_text: Text containing date information
            
        Returns:
            date: Parsed date or None if parsing fails
        """
        try:
            import re
            
            # Clean up the date text
            date_text = date_text.strip()
            
            # Try various date patterns
            date_patterns = [
                r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
                r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM-DD-YYYY or MM/DD/YYYY
                r'(\d{4})年(\d{1,2})月(\d{1,2})日',      # Chinese format
                r'(\d{1,2})月(\d{1,2})日',              # MM月DD日 (assume current year)
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_text)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if '年' in pattern:  # Chinese format YYYY年MM月DD日
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        elif groups[0].isdigit() and len(groups[0]) == 4:  # YYYY-MM-DD
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        else:  # MM-DD-YYYY
                            month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # MM月DD日 format
                        month, day = int(groups[0]), int(groups[1])
                        year = datetime.now().year
                    
                    try:
                        return date(year, month, day)
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error parsing date string '{date_text}': {e}")
            return None
    
    def _parse_date_from_text(self, text: str) -> Optional[date]:
        """
        Parse date from general text content
        
        Args:
            text: Text content that might contain date information
            
        Returns:
            date: Parsed date or None if not found
        """
        try:
            # Split text into lines and check each line
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in ['日期', '時間', '開始', '上課']):
                    parsed_date = self._parse_date_string(line)
                    if parsed_date:
                        return parsed_date
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error parsing date from text: {e}")
            return None
    
    def _extract_from_redirect_page(self, redirect_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract enhanced information by following the redirect URL
        
        Args:
            redirect_url: URL to follow for more detailed information
            
        Returns:
            Dict: Enhanced media information or None if extraction fails
        """
        try:
            self.logger.debug(f"Following redirect URL for enhanced info: {redirect_url}")
            
            # Save current URL to return to later
            current_url = self.driver.current_url
            
            # Navigate to redirect URL
            self.driver.get(redirect_url)
            time.sleep(3)  # Wait for page to load
            
            enhanced_info = {}
            
            # Try to extract course title from the redirect page
            if not enhanced_info.get('course_title'):
                for selector in self.media_selectors["course_title"]:
                    try:
                        title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        title = title_elem.text.strip()
                        if title and len(title) > 3:
                            enhanced_info['course_title'] = title
                            break
                    except NoSuchElementException:
                        continue
            
            # Try to extract speaker information from the redirect page
            if not enhanced_info.get('speaker_name'):
                for selector in self.media_selectors["speaker_info"]:
                    try:
                        speaker_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        speaker = speaker_elem.text.strip()
                        if speaker and len(speaker) > 1:
                            speaker = speaker.replace('講師:', '').replace('主講:', '').strip()
                            if speaker:
                                enhanced_info['speaker_name'] = speaker
                                break
                    except NoSuchElementException:
                        continue
            
            # Try to extract date information from the redirect page
            if not enhanced_info.get('start_date'):
                for selector in self.media_selectors["date_info"]:
                    try:
                        date_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        date_text = date_elem.text.strip()
                        if date_text:
                            parsed_date = self._parse_date_string(date_text)
                            if parsed_date:
                                enhanced_info['start_date'] = parsed_date
                                break
                    except NoSuchElementException:
                        continue
            
            # Return to original page
            self.driver.get(current_url)
            time.sleep(2)
            
            return enhanced_info if enhanced_info else None
            
        except Exception as e:
            self.logger.debug(f"Error extracting from redirect page: {e}")
            # Try to return to original page
            try:
                self.driver.get(current_url)
            except:
                pass
            return None
    
    def _remove_duplicate_content(self, media_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate media content based on redirect URL and content similarity
        
        Args:
            media_content: List of media content dictionaries
            
        Returns:
            List[Dict]: Deduplicated media content
        """
        try:
            unique_content = []
            seen_urls = set()
            seen_hashes = set()
            
            for item in media_content:
                # Check for duplicate URLs
                redirect_url = item.get('redirect_url', '')
                if redirect_url in seen_urls:
                    continue
                
                # Create content hash for similarity detection
                content_string = f"{item.get('course_title', '')}{item.get('speaker_name', '')}{item.get('start_date', '')}"
                content_hash = hashlib.md5(content_string.encode('utf-8')).hexdigest()
                
                if content_hash in seen_hashes:
                    continue
                
                # Add to unique content
                unique_content.append(item)
                seen_urls.add(redirect_url)
                seen_hashes.add(content_hash)
            
            self.logger.info(f"Removed {len(media_content) - len(unique_content)} duplicate items")
            return unique_content
            
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {e}")
            return media_content
    
    def get_media_baseline(self) -> Optional[str]:
        """
        Get the current baseline for media content detection
        
        Returns:
            str: Latest media content ID from baseline or None if no baseline
        """
        try:
            return self.baseline_manager.get_media_baseline()
        except Exception as e:
            self.logger.error(f"Error getting media baseline: {e}")
            return None
    
    def update_media_baseline(self, latest_content_id: str) -> bool:
        """
        Update the baseline with the latest media content ID
        
        Args:
            latest_content_id: Latest media content ID to set as new baseline
            
        Returns:
            bool: True if baseline updated successfully, False otherwise
        """
        try:
            return self.baseline_manager.update_media_baseline(latest_content_id)
        except Exception as e:
            self.logger.error(f"Error updating media baseline: {e}")
            return False
    
    def detect_new_media_content(self, current_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect new media content based on baseline comparison
        
        Args:
            current_content: List of current media content
            
        Returns:
            List[Dict]: List of new media content items
        """
        try:
            if not current_content:
                return []
            
            baseline_content_id = self.get_media_baseline()
            
            if not baseline_content_id:
                self.logger.info("No baseline found, treating all content as new")
                return current_content
            
            # Find the baseline item in current content
            baseline_index = -1
            for i, item in enumerate(current_content):
                if item.get('media_id') == baseline_content_id:
                    baseline_index = i
                    break
            
            if baseline_index == -1:
                self.logger.warning(f"Baseline content ID not found in current content: {baseline_content_id}")
                return current_content
            
            # Return items before the baseline (new content)
            new_content = current_content[:baseline_index]
            self.logger.info(f"Detected {len(new_content)} new media items")
            
            return new_content
            
        except Exception as e:
            self.logger.error(f"Error detecting new media content: {e}")
            return []


# Example usage and testing functions
def main():
    """
    Example usage of MediaProcessor for testing
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('media_processor_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    # Configuration
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "downloads"
    
    processor = None
    try:
        # Initialize processor
        logger.info("Initializing MediaProcessor...")
        processor = MediaProcessor(chromedriver_path, download_dir, logger=logger)
        
        # Set up driver
        processor.setup_driver()
        
        # Extract media content
        logger.info("Extracting media content...")
        media_content = processor.extract_media_content(max_items=10)
        
        if media_content:
            logger.info(f"Successfully extracted {len(media_content)} media items")
            
            # Display results
            for i, item in enumerate(media_content, 1):
                logger.info(f"Media {i}:")
                logger.info(f"  Title: {item.get('course_title', 'N/A')}")
                logger.info(f"  Speaker: {item.get('speaker_name', 'N/A')}")
                logger.info(f"  Date: {item.get('start_date', 'N/A')}")
                logger.info(f"  Type: {item.get('media_type', 'N/A')}")
                logger.info(f"  URL: {item.get('redirect_url', 'N/A')}")
                logger.info("-" * 50)
            
            # Test baseline functionality
            if media_content:
                latest_id = media_content[0]['media_id']
                success = processor.update_media_baseline(latest_id)
                logger.info(f"Updated baseline: {success}")
                
                retrieved_baseline = processor.get_media_baseline()
                logger.info(f"Retrieved baseline: {retrieved_baseline}")
        else:
            logger.warning("No media content extracted")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
    finally:
        if processor:
            processor.cleanup()


if __name__ == "__main__":
    main()