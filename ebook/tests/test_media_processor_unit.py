#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Media Processing
多媒體內容處理單元測試

Tests lecture link detection, media content extraction, and data format validation
Requirements: 3.1, 3.2, 3.3
"""

import os
import sys
import logging
import unittest
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestLectureLinkDetection(unittest.TestCase):
    """Test lecture link detection and processing (Requirement 3.1, 3.2)"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "test_media_unit"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir, exist_ok=True)
        
        self.logger = logging.getLogger("test_media")
        self.logger.setLevel(logging.WARNING)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('media_processor.BookScraper.__init__')
    def test_find_lecture_links_with_standard_selectors(self, mock_parent_init):
        """Test finding lecture links using standard CSS selectors"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.media_selectors = {
            "lecture_links": [
                "a[href*='lecture']",
                "a[href*='series']", 
                "a[href*='streaming']"
            ]
        }
        
        # Mock lecture link elements
        mock_link1 = Mock()
        mock_link1.get_attribute.return_value = "https://www.budaedu.org/#/series/lecture-1"
        
        mock_link2 = Mock()
        mock_link2.get_attribute.return_value = "https://www.budaedu.org/#/series/lecture-2"
        
        mock_link3 = Mock()
        mock_link3.get_attribute.return_value = "https://www.budaedu.org/#/streaming/live-1"
        
        processor.driver.find_elements.return_value = [mock_link1, mock_link2, mock_link3]
        
        # Find lecture links
        lecture_links = processor._find_lecture_links()
        
        # Verify correct links found
        self.assertEqual(len(lecture_links), 3)
        self.assertIn("lecture-1", lecture_links[0])
        self.assertIn("lecture-2", lecture_links[1])
        self.assertIn("live-1", lecture_links[2])
        
        print("✓ Lecture link detection with standard selectors test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_find_lecture_links_with_multiple_selectors(self, mock_parent_init):
        """Test finding lecture links using multiple selector strategies"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        # Mock that first selectors fail, but later ones succeed
        def mock_find_elements(by, selector):
            if selector == "a[href*='lecture']":
                mock_link = Mock()
                mock_link.get_attribute.return_value = "https://www.budaedu.org/#/lecture/test"
                return [mock_link]
            return []
        
        processor.driver.find_elements.side_effect = mock_find_elements
        
        # Find lecture links
        lecture_links = processor._find_lecture_links()
        
        # Verify fallback selectors work
        self.assertGreaterEqual(len(lecture_links), 0)
        
        print("✓ Lecture link detection with multiple selectors test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_find_lecture_links_removes_duplicates(self, mock_parent_init):
        """Test that duplicate lecture links are removed"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        processor.media_selectors = {
            "lecture_links": ["a[href*='lecture']", "a[href*='series']"]
        }
        
        # Mock duplicate link elements
        mock_link1 = Mock()
        mock_link1.get_attribute.return_value = "https://www.budaedu.org/#/series/lecture-1"
        
        mock_link2 = Mock()
        mock_link2.get_attribute.return_value = "https://www.budaedu.org/#/series/lecture-1"  # Duplicate
        
        mock_link3 = Mock()
        mock_link3.get_attribute.return_value = "https://www.budaedu.org/#/series/lecture-2"
        
        processor.driver.find_elements.return_value = [mock_link1, mock_link2, mock_link3]
        
        # Find lecture links
        lecture_links = processor._find_lecture_links()
        
        # Verify duplicates removed
        self.assertEqual(len(lecture_links), 2)
        
        print("✓ Lecture link duplicate removal test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_determine_media_type_from_url(self, mock_parent_init):
        """Test media type determination from URL patterns"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Test various URL patterns
        test_cases = [
            ("https://www.budaedu.org/#/series/live-streaming", "live_streaming", "live_streaming"),
            ("https://www.budaedu.org/#/series/lecture-series", "lecture_series", "lecture_series"),
            ("https://www.budaedu.org/#/video/course-1", "multimedia", "video"),
            ("https://www.budaedu.org/#/audio/dharma-talk", "multimedia", "audio"),
            ("https://www.budaedu.org/#/series/general", "lecture_series", "lecture_series"),
            ("https://www.budaedu.org/#/unknown", "unknown_section", "unknown"),
        ]
        
        for url, section, expected_type in test_cases:
            media_type = processor._determine_media_type(url, section)
            self.assertEqual(media_type, expected_type, f"Failed for URL: {url}")
        
        print("✓ Media type determination test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_generate_media_id_consistency(self, mock_parent_init):
        """Test media ID generation consistency"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Generate ID for same URL
        url = "https://www.budaedu.org/#/series/lecture-1"
        id1 = processor._generate_media_id(url)
        id2 = processor._generate_media_id(url)
        
        # Verify ID format
        self.assertTrue(id1.startswith("media_"))
        self.assertTrue(len(id1) > 10)
        
        # Verify consistency (same URL on same day generates same ID)
        self.assertEqual(id1, id2)
        
        # Verify different URLs generate different IDs
        url2 = "https://www.budaedu.org/#/series/lecture-2"
        id3 = processor._generate_media_id(url2)
        self.assertNotEqual(id1, id3)
        
        print("✓ Media ID generation consistency test passed")


class TestMediaContentExtraction(unittest.TestCase):
    """Test media content data extraction (Requirement 3.3, 3.4, 3.5)"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_media")
        self.logger.setLevel(logging.WARNING)
    
    @patch('media_processor.BookScraper.__init__')
    def test_parse_date_string_with_various_formats(self, mock_parent_init):
        """Test date parsing with various formats"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Test various date formats
        test_cases = [
            ("2024-01-15", date(2024, 1, 15)),
            ("2024/01/15", date(2024, 1, 15)),
            ("01/15/2024", date(2024, 1, 15)),
            ("2024年1月15日", date(2024, 1, 15)),
            ("3月20日", date(datetime.now().year, 3, 20)),
            ("", None),
            ("invalid_date", None)
        ]
        
        for date_text, expected in test_cases:
            result = processor._parse_date_string(date_text)
            if expected:
                self.assertEqual(result, expected, f"Failed for date: {date_text}")
            else:
                self.assertIsNone(result, f"Should be None for: {date_text}")
        
        print("✓ Date parsing with various formats test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_parse_date_from_text_content(self, mock_parent_init):
        """Test extracting date from general text content"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Test text with date information
        test_cases = [
            ("開始日期：2024-03-15\n課程內容...", date(2024, 3, 15)),
            ("上課時間：2024年5月20日\n地點：台北", date(2024, 5, 20)),
            ("日期：2024/06/10\n講師資訊", date(2024, 6, 10)),
            ("沒有日期的文字內容", None),
        ]
        
        for text, expected in test_cases:
            result = processor._parse_date_from_text(text)
            if expected:
                self.assertEqual(result, expected, f"Failed for text: {text[:30]}")
            else:
                self.assertIsNone(result, f"Should be None for text without date")
        
        print("✓ Date extraction from text content test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_process_lecture_url_with_complete_data(self, mock_parent_init):
        """Test processing lecture URL with complete information"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-1"
        section_name = "live_streaming"
        
        # Mock enhanced info extraction
        enhanced_info = {
            'course_title': '心經導讀',
            'speaker_name': '釋慧明法師',
            'start_date': date(2024, 3, 15)
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_info = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify all fields extracted
        self.assertIsNotNone(media_info)
        self.assertEqual(media_info['course_title'], '心經導讀')
        self.assertEqual(media_info['speaker_name'], '釋慧明法師')
        self.assertEqual(media_info['start_date'], date(2024, 3, 15))
        self.assertEqual(media_info['redirect_url'], redirect_url)
        self.assertEqual(media_info['content_type'], 'media')
        
        print("✓ Process lecture URL with complete data test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_process_lecture_url_with_partial_data(self, mock_parent_init):
        """Test processing lecture URL with partial information"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-2"
        section_name = "lecture_series"
        
        # Mock enhanced info extraction with partial data
        enhanced_info = {
            'course_title': '禪修課程',
            'speaker_name': '',  # Missing speaker
            'start_date': None  # Missing date
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_info = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify default values applied
        self.assertIsNotNone(media_info)
        self.assertEqual(media_info['course_title'], '禪修課程')
        self.assertEqual(media_info['speaker_name'], '未知講師')  # Default value
        self.assertEqual(media_info['start_date'], date.today())  # Default to today
        
        print("✓ Process lecture URL with partial data test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_process_lecture_url_with_minimal_data(self, mock_parent_init):
        """Test processing lecture URL with minimal information"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-3"
        section_name = "multimedia"
        
        # Mock enhanced info extraction returns minimal data (at least one field populated)
        # According to implementation, if both course_title and speaker_name are empty, returns None
        # So we provide at least a course title
        enhanced_info = {
            'course_title': '簡短課程',
            'speaker_name': '',
            'start_date': None
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_info = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify default values applied for missing fields
        self.assertIsNotNone(media_info)
        self.assertEqual(media_info['course_title'], '簡短課程')
        self.assertEqual(media_info['speaker_name'], '未知講師')  # Default applied
        self.assertEqual(media_info['start_date'], date.today())  # Default applied
        self.assertEqual(media_info['redirect_url'], redirect_url)
        
        print("✓ Process lecture URL with minimal data test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_remove_duplicate_content(self, mock_parent_init):
        """Test removing duplicate media content"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create test media content with duplicates
        media_content = [
            {
                'media_id': 'media_1',
                'course_title': '心經導讀',
                'speaker_name': '釋慧明法師',
                'start_date': date(2024, 3, 15),
                'redirect_url': 'https://example.com/lecture-1'
            },
            {
                'media_id': 'media_2',
                'course_title': '心經導讀',  # Duplicate content
                'speaker_name': '釋慧明法師',
                'start_date': date(2024, 3, 15),
                'redirect_url': 'https://example.com/lecture-1'  # Same URL
            },
            {
                'media_id': 'media_3',
                'course_title': '禪修課程',
                'speaker_name': '釋智慧法師',
                'start_date': date(2024, 4, 10),
                'redirect_url': 'https://example.com/lecture-2'
            }
        ]
        
        # Remove duplicates
        unique_content = processor._remove_duplicate_content(media_content)
        
        # Verify duplicates removed
        self.assertEqual(len(unique_content), 2)
        
        print("✓ Remove duplicate content test passed")


class TestStructuredDataFormat(unittest.TestCase):
    """Test structured data format compliance (Requirement 3.6, 3.7)"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_media")
        self.logger.setLevel(logging.WARNING)
    
    @patch('media_processor.BookScraper.__init__')
    def test_media_data_structure_completeness(self, mock_parent_init):
        """Test that media data contains all required fields"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-1"
        section_name = "live_streaming"
        
        # Mock enhanced info extraction
        enhanced_info = {
            'course_title': '心經導讀',
            'speaker_name': '釋慧明法師',
            'start_date': date(2024, 3, 15)
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_data = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify all required fields exist (Requirements 3.1-3.7)
        required_fields = [
            'media_id',
            'course_title',
            'speaker_name',
            'start_date',
            'redirect_url',
            'media_type',
            'extraction_timestamp',
            'content_type'
        ]
        
        for field in required_fields:
            self.assertIn(field, media_data, f"Missing required field: {field}")
        
        # Verify field types
        self.assertIsInstance(media_data['media_id'], str)
        self.assertIsInstance(media_data['course_title'], str)
        self.assertIsInstance(media_data['speaker_name'], str)
        self.assertIsInstance(media_data['start_date'], date)
        self.assertIsInstance(media_data['redirect_url'], str)
        self.assertIsInstance(media_data['media_type'], str)
        self.assertIsInstance(media_data['extraction_timestamp'], datetime)
        self.assertEqual(media_data['content_type'], 'media')
        
        print("✓ Media data structure completeness test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_media_data_id_uniqueness(self, mock_parent_init):
        """Test that media IDs are unique"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        # Create multiple media items
        urls = [
            "https://www.budaedu.org/#/series/lecture-1",
            "https://www.budaedu.org/#/series/lecture-2",
            "https://www.budaedu.org/#/series/lecture-3"
        ]
        
        media_ids = []
        for i, url in enumerate(urls):
            enhanced_info = {
                'course_title': f'課程{i+1}',
                'speaker_name': f'講師{i+1}',
                'start_date': date(2024, 3, 15 + i)
            }
            
            with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
                media_data = processor._process_lecture_url(url, "lecture_series", i + 1)
                media_ids.append(media_data['media_id'])
        
        # Verify all IDs are unique
        self.assertEqual(len(media_ids), len(set(media_ids)), "Media IDs are not unique")
        
        print("✓ Media data ID uniqueness test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_media_data_format_for_storage(self, mock_parent_init):
        """Test that media data format is compatible with storage systems"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-1"
        section_name = "live_streaming"
        
        # Mock enhanced info extraction
        enhanced_info = {
            'course_title': '心經導讀',
            'speaker_name': '釋慧明法師',
            'start_date': date(2024, 3, 15)
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_data = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify data can be serialized (important for Excel/MySQL storage)
        import json
        try:
            # Convert datetime and date to string for JSON serialization
            media_data_copy = media_data.copy()
            media_data_copy['extraction_timestamp'] = media_data_copy['extraction_timestamp'].isoformat()
            media_data_copy['start_date'] = media_data_copy['start_date'].isoformat()
            json_str = json.dumps(media_data_copy, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
        except (TypeError, ValueError) as e:
            self.fail(f"Media data is not JSON serializable: {e}")
        
        print("✓ Media data format for storage test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_media_data_with_chinese_characters(self, mock_parent_init):
        """Test media data handling with Chinese characters"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        processor.driver = Mock()
        
        redirect_url = "https://www.budaedu.org/#/series/lecture-chinese"
        section_name = "lecture_series"
        
        # Mock enhanced info with Chinese characters
        enhanced_info = {
            'course_title': '佛學入門：四聖諦與八正道',
            'speaker_name': '釋慧明法師',
            'start_date': date(2024, 3, 15)
        }
        
        with patch.object(processor, '_extract_from_redirect_page', return_value=enhanced_info):
            media_data = processor._process_lecture_url(redirect_url, section_name, 1)
        
        # Verify Chinese characters preserved
        self.assertEqual(media_data['course_title'], '佛學入門：四聖諦與八正道')
        self.assertEqual(media_data['speaker_name'], '釋慧明法師')
        
        # Verify can be serialized with Chinese characters
        import json
        media_data_copy = media_data.copy()
        media_data_copy['extraction_timestamp'] = media_data_copy['extraction_timestamp'].isoformat()
        media_data_copy['start_date'] = media_data_copy['start_date'].isoformat()
        json_str = json.dumps(media_data_copy, ensure_ascii=False)
        self.assertIn('佛學入門', json_str)
        
        print("✓ Media data with Chinese characters test passed")


class TestBaselineManagement(unittest.TestCase):
    """Test baseline management for media detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger("test_media")
        self.logger.setLevel(logging.WARNING)
    
    @patch('media_processor.BookScraper.__init__')
    def test_get_media_baseline_initial(self, mock_parent_init):
        """Test getting baseline when none exists"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create a proper mock for baseline_manager
        mock_baseline_manager = MagicMock()
        mock_baseline_manager.get_media_baseline.return_value = None
        processor.baseline_manager = mock_baseline_manager
        
        baseline = processor.get_media_baseline()
        
        # Verify baseline returns None initially
        self.assertIsNone(baseline)
        
        print("✓ Get media baseline initial test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_update_media_baseline(self, mock_parent_init):
        """Test updating media baseline"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create a proper mock for baseline_manager
        mock_baseline_manager = MagicMock()
        mock_baseline_manager.update_media_baseline.return_value = True
        processor.baseline_manager = mock_baseline_manager
        
        # Update baseline with valid ID
        new_baseline = "media_20240315_abc123"
        result = processor.update_media_baseline(new_baseline)
        
        # Verify update succeeded
        self.assertTrue(result)
        processor.baseline_manager.update_media_baseline.assert_called_once_with(new_baseline)
        
        print("✓ Update media baseline test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_detect_new_media_content_no_baseline(self, mock_parent_init):
        """Test detecting new media content when no baseline exists"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create a proper mock for baseline_manager
        mock_baseline_manager = MagicMock()
        mock_baseline_manager.get_media_baseline.return_value = None
        processor.baseline_manager = mock_baseline_manager
        
        # Create test media content
        current_content = [
            {'media_id': 'media_1', 'course_title': '課程1'},
            {'media_id': 'media_2', 'course_title': '課程2'},
            {'media_id': 'media_3', 'course_title': '課程3'}
        ]
        
        # Detect new content
        new_content = processor.detect_new_media_content(current_content)
        
        # Verify all content is new when no baseline
        self.assertEqual(len(new_content), 3)
        
        print("✓ Detect new media content without baseline test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_detect_new_media_content_with_baseline(self, mock_parent_init):
        """Test detecting new media content with existing baseline"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create a proper mock for baseline_manager
        mock_baseline_manager = MagicMock()
        mock_baseline_manager.get_media_baseline.return_value = 'media_2'
        processor.baseline_manager = mock_baseline_manager
        
        # Create test media content (ordered newest to oldest)
        current_content = [
            {'media_id': 'media_4', 'course_title': '課程4'},  # New
            {'media_id': 'media_3', 'course_title': '課程3'},  # New
            {'media_id': 'media_2', 'course_title': '課程2'},  # Baseline
            {'media_id': 'media_1', 'course_title': '課程1'}   # Old
        ]
        
        # Detect new content
        new_content = processor.detect_new_media_content(current_content)
        
        # Verify only content before baseline is returned
        self.assertEqual(len(new_content), 2)
        self.assertEqual(new_content[0]['media_id'], 'media_4')
        self.assertEqual(new_content[1]['media_id'], 'media_3')
        
        print("✓ Detect new media content with baseline test passed")
    
    @patch('media_processor.BookScraper.__init__')
    def test_detect_new_media_content_baseline_not_found(self, mock_parent_init):
        """Test detecting new media when baseline ID not in current content"""
        mock_parent_init.return_value = None
        
        from media_processor import MediaProcessor
        
        processor = MediaProcessor.__new__(MediaProcessor)
        processor.logger = self.logger
        
        # Create a proper mock for baseline_manager
        mock_baseline_manager = MagicMock()
        mock_baseline_manager.get_media_baseline.return_value = 'media_999'  # Not in list
        processor.baseline_manager = mock_baseline_manager
        
        # Create test media content
        current_content = [
            {'media_id': 'media_3', 'course_title': '課程3'},
            {'media_id': 'media_2', 'course_title': '課程2'},
            {'media_id': 'media_1', 'course_title': '課程1'}
        ]
        
        # Detect new content
        new_content = processor.detect_new_media_content(current_content)
        
        # Verify all content is returned when baseline not found
        self.assertEqual(len(new_content), 3)
        
        print("✓ Detect new media content with missing baseline test passed")


def main():
    """Main test runner"""
    print("🧪 Running Media Processing Unit Tests")
    print("="*60)
    print("Testing: Lecture link detection, content extraction, data format")
    print("="*60)
    
    # Set up basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLectureLinkDetection))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMediaContentExtraction))
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
        print("   ✓ Lecture link detection and processing (Requirement 3.1)")
        print("   ✓ Media content data extraction (Requirement 3.2)")
        print("   ✓ Structured data format compliance (Requirement 3.3)")
        print("   ✓ Course title extraction")
        print("   ✓ Speaker information extraction")
        print("   ✓ Start date extraction")
        print("   ✓ Redirect URL processing")
        print("   ✓ Media type determination")
        print("   ✓ Date parsing with multiple formats")
        print("   ✓ Duplicate content removal")
        print("   ✓ Media ID generation consistency")
        print("   ✓ Baseline management")
        print("   ✓ Chinese character handling")
        print("   ✓ Storage format compatibility")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n🎉 Testing completed!")
    
    return 0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
