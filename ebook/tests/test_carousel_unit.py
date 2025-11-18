#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for CarouselScraper functionality
Tests carousel banner detection, popup extraction, and data format compliance
"""

import unittest
import os
import sys
import logging
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from carousel_scraper import CarouselScraper


class TestCarouselBannerDetection(unittest.TestCase):
    """Test carousel banner detection accuracy (Requirement 1.1, 1.2)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.ERROR)  # Suppress logs during tests
        
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
    def test_carousel_scraper_initialization(self):
        """Test CarouselScraper initializes correctly"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger,
            use_chrome_devtools=False
        )
        
        self.assertIsNotNone(scraper)
        self.assertEqual(scraper.carousel_url, "https://www.budaedu.org/#/")
        self.assertIsNone(scraper.carousel_baseline)
        self.assertFalse(scraper.use_chrome_devtools)
    
    def test_carousel_scraper_with_devtools(self):
        """Test CarouselScraper initializes with DevTools enabled"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger,
            use_chrome_devtools=True
        )
        
        self.assertTrue(scraper.use_chrome_devtools)
        self.assertIsNone(scraper.devtools_page_id)
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_convert_selenium_to_devtools_format(self, mock_setup):
        """Test conversion of Selenium elements to DevTools format"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock Selenium elements
        mock_element1 = Mock()
        mock_element1.get_attribute.side_effect = lambda attr: {
            'src': 'https://example.com/image1.jpg',
            'alt': 'Banner 1'
        }.get(attr, '')
        mock_element1.is_displayed.return_value = True
        
        mock_element2 = Mock()
        mock_element2.get_attribute.side_effect = lambda attr: {
            'src': 'https://example.com/image2.jpg',
            'alt': 'Banner 2'
        }.get(attr, '')
        mock_element2.is_displayed.return_value = False
        
        selenium_elements = [mock_element1, mock_element2]
        
        # Convert to DevTools format
        devtools_elements = scraper._convert_selenium_to_devtools_format(selenium_elements)
        
        # Verify conversion
        self.assertEqual(len(devtools_elements), 2)
        self.assertEqual(devtools_elements[0]['src'], 'https://example.com/image1.jpg')
        self.assertEqual(devtools_elements[0]['alt'], 'Banner 1')
        self.assertTrue(devtools_elements[0]['visible'])
        self.assertEqual(devtools_elements[1]['src'], 'https://example.com/image2.jpg')
        self.assertFalse(devtools_elements[1]['visible'])


class TestPopupContentExtraction(unittest.TestCase):
    """Test popup dialog content extraction (Requirement 1.3)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.ERROR)
        
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_parse_popup_fields_with_complete_data(self, mock_setup):
        """Test parsing popup fields with complete course information"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock popup container
        mock_container = Mock()
        mock_container.text = """
        佛學課程：心經導讀
        地點：台北講堂
        講師：釋慧明法師
        課程時間：每週三晚上7:00-9:00
        """
        
        # Parse fields
        fields = scraper._parse_popup_fields(mock_container)
        
        # Verify extracted fields
        self.assertIn('課程', fields['course_name'])
        self.assertIn('台北講堂', fields['location'])
        self.assertIn('釋慧明法師', fields['instructor'])
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_parse_popup_fields_with_partial_data(self, mock_setup):
        """Test parsing popup fields with partial information"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock popup container with partial data
        mock_container = Mock()
        mock_container.text = """
        禪修課程
        講師：釋慧明法師
        """
        
        # Parse fields
        fields = scraper._parse_popup_fields(mock_container)
        
        # Verify extracted fields
        self.assertIn('禪修', fields['course_name'])
        self.assertIn('釋慧明法師', fields['instructor'])
        self.assertEqual(fields['location'], '')  # No location provided
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_parse_popup_fields_with_minimal_data(self, mock_setup):
        """Test parsing popup fields with minimal information"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock popup container with minimal data
        mock_container = Mock()
        mock_container.text = "佛學講座"
        
        # Parse fields
        fields = scraper._parse_popup_fields(mock_container)
        
        # Verify at least course name is extracted
        self.assertEqual(fields['course_name'], '佛學講座')


class TestStructuredDataFormat(unittest.TestCase):
    """Test structured data format compliance (Requirement 1.4, 1.5)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.ERROR)
        
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_banner_data_structure_completeness(self, mock_setup):
        """Test that banner data contains all required fields"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock element info
        element_info = {
            'selector': 'img',
            'index': 0,
            'src': 'https://example.com/banner.jpg',
            'alt': 'Test Banner',
            'visible': True,
            'clickable': True
        }
        
        # Process banner (without actual clicking)
        with patch.object(scraper, 'process_banner_popup_enhanced', return_value={}):
            banner_data = scraper._process_single_banner_enhanced(element_info, 0)
        
        # Verify all required fields exist
        required_fields = [
            'carousel_id',
            'banner_title',
            'image_url',
            'activity_link',
            'course_name',
            'location',
            'instructor',
            'description',
            'extraction_timestamp',
            'content_type'
        ]
        
        for field in required_fields:
            self.assertIn(field, banner_data, f"Missing required field: {field}")
        
        # Verify field types
        self.assertIsInstance(banner_data['carousel_id'], str)
        self.assertIsInstance(banner_data['banner_title'], str)
        self.assertIsInstance(banner_data['image_url'], str)
        self.assertIsInstance(banner_data['extraction_timestamp'], datetime)
        self.assertEqual(banner_data['content_type'], 'carousel')
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_banner_data_id_uniqueness(self, mock_setup):
        """Test that carousel IDs are unique"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create multiple mock element infos
        element_infos = [
            {'selector': 'img', 'index': i, 'src': f'https://example.com/banner{i}.jpg',
             'alt': f'Banner {i}', 'visible': True, 'clickable': True}
            for i in range(3)
        ]
        
        # Process multiple banners
        banner_ids = []
        with patch.object(scraper, 'process_banner_popup_enhanced', return_value={}):
            for i, element_info in enumerate(element_infos):
                banner_data = scraper._process_single_banner_enhanced(element_info, i)
                banner_ids.append(banner_data['carousel_id'])
        
        # Verify all IDs are unique
        self.assertEqual(len(banner_ids), len(set(banner_ids)), "Carousel IDs are not unique")
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_banner_data_format_for_storage(self, mock_setup):
        """Test that banner data format is compatible with storage systems"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Create mock element info
        element_info = {
            'selector': 'img',
            'index': 0,
            'src': 'https://example.com/banner.jpg',
            'alt': 'Test Banner',
            'visible': True,
            'clickable': True
        }
        
        # Mock popup data
        popup_data = {
            'course_name': '心經導讀',
            'location': '台北講堂',
            'instructor': '釋慧明法師',
            'description': '深入淺出講解心經',
            'activity_link': 'https://example.com/activity'
        }
        
        with patch.object(scraper, 'process_banner_popup_enhanced', return_value=popup_data):
            banner_data = scraper._process_single_banner_enhanced(element_info, 0)
        
        # Verify data can be serialized (important for Excel/MySQL storage)
        import json
        try:
            # Convert datetime to string for JSON serialization
            banner_data_copy = banner_data.copy()
            banner_data_copy['extraction_timestamp'] = banner_data_copy['extraction_timestamp'].isoformat()
            json_str = json.dumps(banner_data_copy, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
        except (TypeError, ValueError) as e:
            self.fail(f"Banner data is not JSON serializable: {e}")


class TestBaselineManagement(unittest.TestCase):
    """Test baseline management functionality (Requirement 6.1)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.ERROR)
        
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_get_carousel_baseline_initial(self, mock_setup):
        """Test getting baseline when none exists"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Mock extract_carousel_banners to return empty list
        with patch.object(scraper, 'extract_carousel_banners', return_value=[]):
            baseline = scraper.get_carousel_baseline()
        
        # Verify baseline is created
        self.assertIsNotNone(baseline)
        self.assertIn('baseline_', baseline)
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_update_carousel_baseline(self, mock_setup):
        """Test updating carousel baseline"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Update baseline with valid ID
        new_baseline = "carousel_123_1234567890"
        result = scraper.update_carousel_baseline(new_baseline)
        
        # Verify update succeeded
        self.assertTrue(result)
        self.assertEqual(scraper.carousel_baseline, new_baseline)
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_update_carousel_baseline_invalid(self, mock_setup):
        """Test updating baseline with invalid data"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Try to update with empty string
        result = scraper.update_carousel_baseline("")
        
        # Verify update failed
        self.assertFalse(result)
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_update_carousel_baseline_none(self, mock_setup):
        """Test updating baseline with None"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger
        )
        
        # Try to update with None
        result = scraper.update_carousel_baseline(None)
        
        # Verify update failed
        self.assertFalse(result)


class TestChromeDevToolsIntegration(unittest.TestCase):
    """Test Chrome DevTools integration (Requirement 7.1, 7.2)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.ERROR)
        
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_devtools_disabled_by_default(self, mock_setup):
        """Test that DevTools can be disabled"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger,
            use_chrome_devtools=False
        )
        
        result = scraper.setup_chrome_devtools()
        
        # Verify DevTools setup returns False when disabled
        self.assertFalse(result)
    
    @patch('carousel_scraper.BookScraper.setup_driver')
    def test_devtools_fallback_on_error(self, mock_setup):
        """Test that system falls back to standard Selenium on DevTools error"""
        scraper = CarouselScraper(
            self.chromedriver_path,
            self.download_dir,
            self.logger,
            use_chrome_devtools=True
        )
        
        # Mock driver to raise exception on DevTools setup
        scraper.driver = Mock()
        scraper.driver.execute_cdp_cmd.side_effect = Exception("DevTools error")
        
        result = scraper.setup_chrome_devtools()
        
        # Verify fallback occurred
        self.assertFalse(result)
        self.assertFalse(scraper.use_chrome_devtools)


def run_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCarouselBannerDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestPopupContentExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredDataFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestBaselineManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestChromeDevToolsIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
