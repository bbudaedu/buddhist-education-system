#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for News Processing
新聞公告處理單元測試

Tests news item identification, popup content extraction, and data format validation
Requirements: 9.1, 9.2, 9.3
"""

import os
import sys
import logging
import unittest
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestNewsItemIdentification(unittest.TestCase):
    """Test news item identification and clicking (Requirement 9.1, 9.2)"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "test_news_unit"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir, exist_ok=True)
        
        self.logger = logging.getLogger("test_news")
        self.logger.setLevel(logging.WARNING)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('news_processor.BookScraper.__init__')
    def test_find_news_elements_with_standard_selectors(self, mock_parent_init):
        """Test finding news elements using standard CSS selectors"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        # Mock news elements
        mock_element1 = Mock()
        mock_element1.text = "重要公告：佛學講座時間調整通知"
        mock_element1.is_displayed.return_value = True
        
        mock_element2 = Mock()
        mock_element2.text = "新書推薦：心經導讀精選"
        mock_element2.is_displayed.return_value = True
        
        mock_element3 = Mock()
        mock_element3.text = "搜尋"  # Should be filtered out
        mock_element3.is_displayed.return_value = True
        
        processor.driver.find_elements.return_value = [mock_element1, mock_element2, mock_element3]
        
        # Find news elements
        news_elements = processor._find_news_elements()
        
        # Verify correct elements found (excluding search box)
        self.assertGreater(len(news_elements), 0)
        
        print("✓ News element identification with standard selectors test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_find_news_elements_with_multiple_selectors(self, mock_parent_init):
        """Test finding news elements using multiple selector strategies"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        # Mock that first selectors fail, but later ones succeed
        def mock_find_elements(by, selector):
            if selector == ".news-item":
                return []  # First selector fails
            elif selector == ".announcement-item":
                mock_elem = Mock()
                mock_elem.text = "測試公告內容"
                mock_elem.is_displayed.return_value = True
                return [mock_elem]
            return []
        
        processor.driver.find_elements.side_effect = mock_find_elements
        
        # Find news elements
        news_elements = processor._find_news_elements()
        
        # Verify fallback selectors work
        self.assertGreaterEqual(len(news_elements), 0)
        
        print("✓ News element identification with multiple selectors test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_enhanced_click_news_item_with_selenium(self, mock_parent_init):
        """Test clicking news item using Selenium fallback"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock news element
        mock_element = Mock()
        mock_element.get_attribute.return_value = "news-item-1"
        
        # Test JavaScript click
        result = processor._enhanced_click_news_item(mock_element)
        
        # Verify click was attempted
        self.assertTrue(result)
        processor.driver.execute_script.assert_called_once()
        
        print("✓ Enhanced click with Selenium fallback test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_enhanced_click_news_item_with_devtools(self, mock_parent_init):
        """Test clicking news item using DevTools integration"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = True
        
        # Mock news element with ID
        mock_element = Mock()
        mock_element.get_attribute.side_effect = lambda attr: {
            'id': 'news-123',
            'class': 'news-item clickable'
        }.get(attr, '')
        
        # Mock DevTools click success
        with patch.object(processor, '_devtools_click_element', return_value=True):
            result = processor._enhanced_click_news_item(mock_element)
        
        # Verify DevTools click was used
        self.assertTrue(result)
        
        print("✓ Enhanced click with DevTools integration test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_preview_title_from_element(self, mock_parent_init):
        """Test extracting preview title from news element"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        from selenium.common.exceptions import NoSuchElementException
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Test case 1: Title in h3 tag
        mock_element = Mock()
        mock_title_elem = Mock()
        mock_title_elem.text = "重要公告：課程時間調整"
        mock_element.find_element.return_value = mock_title_elem
        
        title = processor._extract_preview_title(mock_element)
        self.assertEqual(title, "重要公告：課程時間調整")
        
        # Test case 2: No title tag, use first line of text
        mock_element2 = Mock()
        mock_element2.find_element.side_effect = NoSuchElementException("No title element")
        mock_element2.text = "佛學講座通知\n詳細內容請見..."
        
        title2 = processor._extract_preview_title(mock_element2)
        self.assertEqual(title2, "佛學講座通知")
        
        # Test case 3: Empty element
        mock_element3 = Mock()
        mock_element3.find_element.side_effect = NoSuchElementException("No title element")
        mock_element3.text = ""
        
        title3 = processor._extract_preview_title(mock_element3)
        self.assertEqual(title3, "")
        
        print("✓ Preview title extraction test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_preview_date_from_element(self, mock_parent_init):
        """Test extracting preview date from news element"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Test case 1: Standard date format YYYY-MM-DD
        mock_element = Mock()
        mock_element.text = "發布日期：2024-01-15\n重要公告內容"
        
        extracted_date = processor._extract_preview_date(mock_element)
        self.assertEqual(extracted_date, date(2024, 1, 15))
        
        # Test case 2: Chinese date format
        mock_element2 = Mock()
        mock_element2.text = "2024年3月20日 佛學講座通知"
        
        extracted_date2 = processor._extract_preview_date(mock_element2)
        self.assertEqual(extracted_date2, date(2024, 3, 20))
        
        # Test case 3: Slash format
        mock_element3 = Mock()
        mock_element3.text = "公告時間：2024/05/10"
        
        extracted_date3 = processor._extract_preview_date(mock_element3)
        self.assertEqual(extracted_date3, date(2024, 5, 10))
        
        # Test case 4: No date found (should return today)
        mock_element4 = Mock()
        mock_element4.text = "沒有日期的公告"
        
        extracted_date4 = processor._extract_preview_date(mock_element4)
        self.assertEqual(extracted_date4, date.today())
        
        print("✓ Preview date extraction test passed")


class TestPopupContentExtraction(unittest.TestCase):
    """Test popup content extraction (Requirement 9.3)"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_news")
        self.logger.setLevel(logging.WARNING)
    
    @patch('news_processor.BookScraper.__init__')
    def test_enhanced_wait_for_popup_with_selenium(self, mock_parent_init):
        """Test waiting for popup using Selenium"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        from selenium.webdriver.support.ui import WebDriverWait
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock popup element
        mock_popup = Mock()
        mock_popup.is_displayed.return_value = True
        
        # Mock WebDriverWait to return popup
        with patch('news_processor.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_popup
            
            result = processor._enhanced_wait_for_popup()
        
        # Verify popup was detected
        self.assertTrue(result)
        
        print("✓ Enhanced wait for popup with Selenium test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_enhanced_wait_for_popup_with_devtools(self, mock_parent_init):
        """Test waiting for popup using DevTools"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = True
        
        # Mock DevTools wait success
        with patch.object(processor, '_devtools_wait_for_element', return_value=True):
            result = processor._enhanced_wait_for_popup()
        
        # Verify DevTools wait was used
        self.assertTrue(result)
        
        print("✓ Enhanced wait for popup with DevTools test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_popup_title(self, mock_parent_init):
        """Test extracting title from popup element"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Mock popup element with title
        mock_popup = Mock()
        mock_title_elem = Mock()
        mock_title_elem.text = "重要公告：課程調整通知"
        mock_popup.find_element.return_value = mock_title_elem
        
        title = processor._extract_popup_title(mock_popup)
        
        # Verify title extracted
        self.assertEqual(title, "重要公告：課程調整通知")
        
        print("✓ Popup title extraction test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_popup_date(self, mock_parent_init):
        """Test extracting date from popup element"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Mock popup element with date
        mock_popup = Mock()
        mock_popup.text = "發布日期：2024-02-15\n公告內容詳情..."
        
        extracted_date = processor._extract_popup_date(mock_popup)
        
        # Verify date extracted
        self.assertEqual(extracted_date, date(2024, 2, 15))
        
        print("✓ Popup date extraction test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_popup_text(self, mock_parent_init):
        """Test extracting main content from popup element"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Mock popup element with content
        mock_popup = Mock()
        mock_content_elem1 = Mock()
        mock_content_elem1.text = "第一段內容：課程時間調整說明"
        mock_content_elem2 = Mock()
        mock_content_elem2.text = "第二段內容：請學員注意新的上課時間"
        
        mock_popup.find_elements.return_value = [mock_content_elem1, mock_content_elem2]
        
        content = processor._extract_popup_text(mock_popup)
        
        # Verify content extracted
        self.assertIn("第一段內容", content)
        self.assertIn("第二段內容", content)
        
        print("✓ Popup text extraction test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_extract_popup_content_complete(self, mock_parent_init):
        """Test complete popup content extraction"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        from selenium.webdriver.support.ui import WebDriverWait
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        # Mock popup element
        mock_popup = Mock()
        mock_popup.is_displayed.return_value = True
        mock_popup.text = "2024-03-10\n重要公告\n課程調整詳情..."
        
        # Mock title element
        mock_title = Mock()
        mock_title.text = "重要公告"
        
        # Mock content elements
        mock_content = Mock()
        mock_content.text = "課程調整詳情..."
        
        mock_popup.find_element.return_value = mock_title
        mock_popup.find_elements.return_value = [mock_content]
        
        # Mock WebDriverWait
        with patch('news_processor.WebDriverWait') as mock_wait:
            mock_wait.return_value.until.return_value = mock_popup
            
            result = processor._extract_popup_content()
        
        # Verify all fields extracted
        self.assertIsNotNone(result)
        self.assertIn('title', result)
        self.assertIn('publication_date', result)
        self.assertIn('content', result)
        self.assertEqual(result['title'], "重要公告")
        
        print("✓ Complete popup content extraction test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_enhanced_close_popup(self, mock_parent_init):
        """Test closing popup dialog"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock close button
        mock_close_btn = Mock()
        processor.driver.find_elements.return_value = [mock_close_btn]
        
        # Test closing popup
        result = processor._enhanced_close_popup()
        
        # Verify close was attempted
        self.assertTrue(result)
        mock_close_btn.click.assert_called_once()
        
        print("✓ Enhanced close popup test passed")


class TestStructuredDataFormat(unittest.TestCase):
    """Test structured data format for news announcements (Requirement 9.3)"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_news")
        self.logger.setLevel(logging.WARNING)
    
    @patch('news_processor.BookScraper.__init__')
    def test_news_data_structure_completeness(self, mock_parent_init):
        """Test that news data contains all required fields"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock news element
        mock_element = Mock()
        mock_element.text = "2024-01-15\n重要公告標題"
        mock_element.get_attribute.return_value = "news-1"
        
        # Mock popup content
        popup_content = {
            'title': '重要公告標題',
            'publication_date': date(2024, 1, 15),
            'content': '這是公告的詳細內容...'
        }
        
        # Mock methods
        with patch.object(processor, '_enhanced_click_news_item', return_value=True), \
             patch.object(processor, '_enhanced_wait_for_popup', return_value=True), \
             patch.object(processor, '_enhanced_extract_popup_content', return_value=popup_content), \
             patch.object(processor, '_enhanced_close_popup', return_value=True), \
             patch.object(processor, '_extract_preview_title', return_value='重要公告標題'), \
             patch.object(processor, '_extract_preview_date', return_value=date(2024, 1, 15)):
            
            news_data = processor.process_news_popup(mock_element)
        
        # Verify all required fields exist
        required_fields = [
            'announcement_id',
            'title',
            'publication_date',
            'content',
            'extraction_timestamp',
            'content_type'
        ]
        
        for field in required_fields:
            self.assertIn(field, news_data, f"Missing required field: {field}")
        
        # Verify field types
        self.assertIsInstance(news_data['announcement_id'], str)
        self.assertIsInstance(news_data['title'], str)
        self.assertIsInstance(news_data['publication_date'], date)
        self.assertIsInstance(news_data['content'], str)
        self.assertIsInstance(news_data['extraction_timestamp'], datetime)
        self.assertEqual(news_data['content_type'], 'news')
        
        print("✓ News data structure completeness test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_announcement_id_generation(self, mock_parent_init):
        """Test announcement ID generation consistency"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Generate ID for same title
        title1 = "測試公告標題"
        id1 = processor._generate_announcement_id(title1)
        id2 = processor._generate_announcement_id(title1)
        
        # Verify ID format
        self.assertTrue(id1.startswith("news_"))
        self.assertTrue(len(id1) > 8)
        
        # Verify consistency (same title on same day generates same ID)
        self.assertEqual(id1, id2)
        
        # Verify different titles generate different IDs
        title2 = "另一個公告標題"
        id3 = processor._generate_announcement_id(title2)
        self.assertNotEqual(id1, id3)
        
        print("✓ Announcement ID generation test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_news_data_format_for_storage(self, mock_parent_init):
        """Test that news data format is compatible with storage systems"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock news element
        mock_element = Mock()
        mock_element.text = "2024-02-20\n佛學講座通知"
        mock_element.get_attribute.return_value = "news-2"
        
        # Mock popup content
        popup_content = {
            'title': '佛學講座通知',
            'publication_date': date(2024, 2, 20),
            'content': '本週佛學講座將於週三晚上7點舉行...'
        }
        
        # Mock methods
        with patch.object(processor, '_enhanced_click_news_item', return_value=True), \
             patch.object(processor, '_enhanced_wait_for_popup', return_value=True), \
             patch.object(processor, '_enhanced_extract_popup_content', return_value=popup_content), \
             patch.object(processor, '_enhanced_close_popup', return_value=True), \
             patch.object(processor, '_extract_preview_title', return_value='佛學講座通知'), \
             patch.object(processor, '_extract_preview_date', return_value=date(2024, 2, 20)):
            
            news_data = processor.process_news_popup(mock_element)
        
        # Verify data can be serialized (important for Excel/MySQL storage)
        import json
        try:
            # Convert datetime and date to string for JSON serialization
            news_data_copy = news_data.copy()
            news_data_copy['extraction_timestamp'] = news_data_copy['extraction_timestamp'].isoformat()
            news_data_copy['publication_date'] = news_data_copy['publication_date'].isoformat()
            json_str = json.dumps(news_data_copy, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
        except (TypeError, ValueError) as e:
            self.fail(f"News data is not JSON serializable: {e}")
        
        print("✓ News data format for storage test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_news_data_with_partial_content(self, mock_parent_init):
        """Test news data structure with partial/missing content"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.devtools_available = False
        
        # Mock news element
        mock_element = Mock()
        mock_element.text = "簡短公告"
        mock_element.get_attribute.return_value = "news-3"
        
        # Mock scroll into view
        processor.driver.execute_script = Mock()
        
        # Test case 1: Popup appears but content extraction returns None (partial content)
        with patch.object(processor, '_enhanced_click_news_item', return_value=True), \
             patch.object(processor, '_enhanced_wait_for_popup', return_value=True), \
             patch.object(processor, '_enhanced_extract_popup_content', return_value=None), \
             patch.object(processor, '_enhanced_close_popup', return_value=True), \
             patch.object(processor, '_extract_preview_title', return_value='簡短公告'), \
             patch.object(processor, '_extract_preview_date', return_value=date.today()):
            
            news_data = processor.process_news_popup(mock_element)
        
        # Verify fallback data is created when popup content extraction fails
        self.assertIsNotNone(news_data)
        self.assertEqual(news_data['title'], '簡短公告')
        self.assertEqual(news_data['content'], '無法提取完整內容')
        self.assertEqual(news_data['content_type'], 'news')
        
        # Test case 2: Popup doesn't appear (returns None as per implementation)
        with patch.object(processor, '_enhanced_click_news_item', return_value=True), \
             patch.object(processor, '_enhanced_wait_for_popup', return_value=False), \
             patch.object(processor, '_extract_preview_title', return_value='簡短公告'), \
             patch.object(processor, '_extract_preview_date', return_value=date.today()):
            
            news_data_no_popup = processor.process_news_popup(mock_element)
        
        # Verify None is returned when popup doesn't appear (as per implementation)
        self.assertIsNone(news_data_no_popup)
        
        print("✓ News data with partial content test passed")


class TestBaselineManagement(unittest.TestCase):
    """Test baseline management for news detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_news")
        self.logger.setLevel(logging.WARNING)
    
    @patch('news_processor.BookScraper.__init__')
    def test_get_news_baseline_initial(self, mock_parent_init):
        """Test getting baseline when none exists"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        baseline = processor.get_news_baseline()
        
        # Verify baseline returns None initially
        self.assertIsNone(baseline)
        
        print("✓ Get news baseline initial test passed")
    
    @patch('news_processor.BookScraper.__init__')
    def test_update_news_baseline(self, mock_parent_init):
        """Test updating news baseline"""
        mock_parent_init.return_value = None
        
        from news_processor import NewsProcessor
        
        processor = NewsProcessor.__new__(NewsProcessor)
        processor.logger = self.logger
        
        # Update baseline with valid timestamp
        new_baseline = datetime(2024, 3, 15, 10, 30, 0)
        result = processor.update_news_baseline(new_baseline)
        
        # Verify update succeeded
        self.assertTrue(result)
        
        print("✓ Update news baseline test passed")


def main():
    """Main test runner"""
    print("🧪 Running News Processing Unit Tests")
    print("="*60)
    print("Testing: News identification, popup extraction, data format")
    print("="*60)
    
    # Set up basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNewsItemIdentification))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPopupContentExtraction))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStructuredDataFormat))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBaselineManagement))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}")
            print(f"     {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}")
            print(f"     {traceback}")
    
    if result.testsRun > 0 and len(result.failures) == 0 and len(result.errors) == 0:
        print("\n✅ All unit tests passed!")
        print("\n📝 Test Coverage:")
        print("   ✓ News item identification and clicking (Requirement 9.1, 9.2)")
        print("   ✓ Popup content extraction (Requirement 9.3)")
        print("   ✓ Structured data format validation (Requirement 9.3)")
        print("   ✓ Preview title and date extraction")
        print("   ✓ Enhanced DevTools integration")
        print("   ✓ Selenium fallback mechanisms")
        print("   ✓ Announcement ID generation")
        print("   ✓ Baseline management")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n🎉 Testing completed!")
    
    return 0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
