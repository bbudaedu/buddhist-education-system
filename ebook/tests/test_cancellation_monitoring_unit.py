#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Cancellation Monitoring
課程取消監控單元測試

This test file focuses on testing cancellation monitoring logic
without requiring ChromeDriver or browser initialization.
Tests cover: table data extraction, baseline comparison, and data format validation.
"""

import os
import sys
import logging
import unittest
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestCancellationMonitoringLogic(unittest.TestCase):
    """Test cases for cancellation monitoring core logic"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "test_cancellation_unit"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir, exist_ok=True)
        
        self.logger = logging.getLogger("test_cancellation")
        self.logger.setLevel(logging.WARNING)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('bulletin_scraper.BookScraper.__init__')
    def test_table_data_extraction_accuracy(self, mock_parent_init):
        """Test table data extraction accuracy with various row formats (Requirement 8.1)"""
        mock_parent_init.return_value = None
        
        from bulletin_scraper import BulletinScraper
        
        scraper = BulletinScraper.__new__(BulletinScraper)
        scraper.logger = self.logger
        scraper.content_type = "cancellation"
        
        # Test case 1: Standard 3-column format
        mock_row = Mock()
        mock_cells = [Mock(), Mock(), Mock()]
        mock_cells[0].text = "2024-01-15"
        mock_cells[1].text = "佛學入門課程"
        mock_cells[2].text = "釋慧明法師"
        mock_row.find_elements.return_value = mock_cells
        
        result = scraper.parse_table_row(mock_row)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['cancellation_date'], date(2024, 1, 15))
        self.assertEqual(result['course_name'], "佛學入門課程")
        self.assertEqual(result['instructor_name'], "釋慧明法師")
        self.assertEqual(result['content_type'], "cancellation")
        self.assertTrue(result['cancellation_id'].startswith("cancel_"))
        
        # Test case 2: Missing instructor (insufficient columns)
        mock_cells_2 = [Mock(), Mock()]
        mock_cells_2[0].text = "2024/02/20"
        mock_cells_2[1].text = "禪修進階班"
        mock_row.find_elements.return_value = mock_cells_2
        
        result2 = scraper.parse_table_row(mock_row)
        self.assertIsNone(result2)  # Should fail with insufficient columns
        
        # Test case 3: Extra columns (should still work)
        mock_cells_3 = [Mock(), Mock(), Mock(), Mock()]
        mock_cells_3[0].text = "2024.03.10"
        mock_cells_3[1].text = "經典研讀班"
        mock_cells_3[2].text = "釋智慧法師"
        mock_cells_3[3].text = "備註資訊"
        mock_row.find_elements.return_value = mock_cells_3
        
        result3 = scraper.parse_table_row(mock_row)
        
        self.assertIsNotNone(result3)
        self.assertEqual(result3['cancellation_date'], date(2024, 3, 10))
        self.assertEqual(result3['course_name'], "經典研讀班")
        self.assertEqual(result3['instructor_name'], "釋智慧法師")
        
        # Test case 4: Empty instructor field (should use default)
        mock_cells_4 = [Mock(), Mock(), Mock()]
        mock_cells_4[0].text = "2024-04-05"
        mock_cells_4[1].text = "念佛共修"
        mock_cells_4[2].text = ""
        mock_row.find_elements.return_value = mock_cells_4
        
        result4 = scraper.parse_table_row(mock_row)
        
        self.assertIsNotNone(result4)
        self.assertEqual(result4['instructor_name'], "未指定講師")
        
        print("✓ Table data extraction accuracy test passed")
    
    @patch('bulletin_scraper.BookScraper.__init__')
    def test_baseline_comparison_logic(self, mock_parent_init):
        """Test baseline comparison logic for detecting new cancellations (Requirement 8.2)"""
        mock_parent_init.return_value = None
        
        from bulletin_scraper import BulletinScraper
        from enhanced_baseline_manager import EnhancedBaselineManager
        from datetime import datetime
        
        scraper = BulletinScraper.__new__(BulletinScraper)
        scraper.logger = self.logger
        scraper.content_type = "cancellation"
        scraper.baseline_manager = EnhancedBaselineManager("test_project", self.test_dir, self.logger)
        
        # Mock the get_cancellation_baseline to return date objects for comparison
        def mock_get_baseline():
            baseline_str = scraper.baseline_manager.get_cancellation_baseline()
            if baseline_str:
                return datetime.strptime(baseline_str, '%Y-%m-%d').date()
            return None
        
        scraper.get_cancellation_baseline = mock_get_baseline
        
        # Test case 1: No baseline (all cancellations are new)
        all_cancellations = [
            {
                'cancellation_id': 'cancel_1',
                'cancellation_date': date(2024, 1, 10),
                'course_name': '課程1',
                'instructor_name': '講師1'
            },
            {
                'cancellation_id': 'cancel_2',
                'cancellation_date': date(2024, 1, 15),
                'course_name': '課程2',
                'instructor_name': '講師2'
            }
        ]
        
        new_cancellations = scraper.filter_new_cancellations(all_cancellations)
        self.assertEqual(len(new_cancellations), 2)
        
        # Test case 2: Baseline set, some new cancellations
        baseline_date = date(2024, 1, 12)
        scraper.baseline_manager.update_cancellation_baseline(baseline_date.isoformat())
        
        new_cancellations = scraper.filter_new_cancellations(all_cancellations)
        self.assertEqual(len(new_cancellations), 1)
        self.assertEqual(new_cancellations[0]['cancellation_date'], date(2024, 1, 15))
        
        # Test case 3: Baseline after all cancellations (no new ones)
        baseline_date = date(2024, 1, 20)
        scraper.baseline_manager.update_cancellation_baseline(baseline_date.isoformat())
        
        new_cancellations = scraper.filter_new_cancellations(all_cancellations)
        self.assertEqual(len(new_cancellations), 0)
        
        # Test case 4: Multiple new cancellations after baseline
        more_cancellations = [
            {
                'cancellation_id': 'cancel_3',
                'cancellation_date': date(2024, 1, 25),
                'course_name': '課程3',
                'instructor_name': '講師3'
            },
            {
                'cancellation_id': 'cancel_4',
                'cancellation_date': date(2024, 1, 30),
                'course_name': '課程4',
                'instructor_name': '講師4'
            },
            {
                'cancellation_id': 'cancel_5',
                'cancellation_date': date(2024, 1, 18),
                'course_name': '課程5',
                'instructor_name': '講師5'
            }
        ]
        
        new_cancellations = scraper.filter_new_cancellations(more_cancellations)
        self.assertEqual(len(new_cancellations), 2)  # Only dates after 2024-01-20
        
        # Verify the correct ones are returned
        new_dates = [c['cancellation_date'] for c in new_cancellations]
        self.assertIn(date(2024, 1, 25), new_dates)
        self.assertIn(date(2024, 1, 30), new_dates)
        self.assertNotIn(date(2024, 1, 18), new_dates)
        
        print("✓ Baseline comparison logic test passed")
    
    @patch('bulletin_scraper.BookScraper.__init__')
    def test_structured_data_format_for_cancellations(self, mock_parent_init):
        """Test structured data format compliance for cancellation records (Requirement 8.3)"""
        mock_parent_init.return_value = None
        
        from bulletin_scraper import BulletinScraper
        
        scraper = BulletinScraper.__new__(BulletinScraper)
        scraper.logger = self.logger
        scraper.content_type = "cancellation"
        
        # Mock table row with complete data
        mock_row = Mock()
        mock_cells = [Mock(), Mock(), Mock()]
        mock_cells[0].text = "2024-01-15"
        mock_cells[1].text = "佛學入門課程"
        mock_cells[2].text = "釋慧明法師"
        mock_row.find_elements.return_value = mock_cells
        
        result = scraper.parse_table_row(mock_row)
        
        # Verify all required fields are present (Requirements 8.1, 8.2, 8.3)
        required_fields = [
            'cancellation_id',
            'cancellation_date',
            'course_name',
            'instructor_name',
            'extraction_timestamp',
            'content_type'
        ]
        
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")
        
        # Verify field types
        self.assertIsInstance(result['cancellation_id'], str)
        self.assertIsInstance(result['cancellation_date'], date)
        self.assertIsInstance(result['course_name'], str)
        self.assertIsInstance(result['instructor_name'], str)
        self.assertIsInstance(result['extraction_timestamp'], datetime)
        self.assertEqual(result['content_type'], 'cancellation')
        
        # Verify ID format
        self.assertTrue(result['cancellation_id'].startswith('cancel_'))
        self.assertTrue(len(result['cancellation_id']) > 10)
        
        # Verify date is valid
        self.assertIsInstance(result['cancellation_date'], date)
        self.assertGreater(result['cancellation_date'], date(2020, 1, 1))
        
        # Verify non-empty strings
        self.assertTrue(len(result['course_name']) > 0)
        self.assertTrue(len(result['instructor_name']) > 0)
        
        # Test with missing instructor (should use default)
        mock_cells_no_instructor = [Mock(), Mock(), Mock()]
        mock_cells_no_instructor[0].text = "2024-02-20"
        mock_cells_no_instructor[1].text = "禪修課程"
        mock_cells_no_instructor[2].text = ""  # Empty instructor
        mock_row.find_elements.return_value = mock_cells_no_instructor
        
        result_no_instructor = scraper.parse_table_row(mock_row)
        
        self.assertIsNotNone(result_no_instructor)
        self.assertEqual(result_no_instructor['instructor_name'], "未指定講師")
        
        # Test data format consistency across multiple records
        test_records = []
        for i in range(3):
            mock_cells_test = [Mock(), Mock(), Mock()]
            mock_cells_test[0].text = f"2024-0{i+1}-15"
            mock_cells_test[1].text = f"測試課程{i+1}"
            mock_cells_test[2].text = f"測試講師{i+1}"
            mock_row.find_elements.return_value = mock_cells_test
            
            record = scraper.parse_table_row(mock_row)
            if record:
                test_records.append(record)
        
        # Verify all records have consistent structure
        for record in test_records:
            for field in required_fields:
                self.assertIn(field, record)
        
        print("✓ Structured data format test passed")
    
    @patch('bulletin_scraper.BookScraper.__init__')
    def test_date_parsing_accuracy(self, mock_parent_init):
        """Test date parsing with various formats"""
        mock_parent_init.return_value = None
        
        from bulletin_scraper import BulletinScraper
        
        scraper = BulletinScraper.__new__(BulletinScraper)
        scraper.logger = self.logger
        
        # Test various date formats
        test_cases = [
            ("2024-01-15", date(2024, 1, 15)),
            ("2024/01/15", date(2024, 1, 15)),
            ("01/15/2024", date(2024, 1, 15)),
            ("2024.01.15", date(2024, 1, 15)),
            ("", None),
            ("invalid_date", None)
        ]
        
        for date_text, expected in test_cases:
            result = scraper.parse_date_field(date_text)
            self.assertEqual(result, expected, f"Failed for date: {date_text}")
        
        print("✓ Date parsing accuracy test passed")
    
    @patch('bulletin_scraper.BookScraper.__init__')
    def test_cancellation_id_generation(self, mock_parent_init):
        """Test cancellation ID generation consistency"""
        mock_parent_init.return_value = None
        
        from bulletin_scraper import BulletinScraper
        
        scraper = BulletinScraper.__new__(BulletinScraper)
        scraper.logger = self.logger
        
        test_date = date(2024, 1, 15)
        course_name = "測試課程"
        instructor_name = "測試講師"
        
        # Generate ID
        cancellation_id = scraper.generate_cancellation_id(test_date, course_name, instructor_name)
        
        # Check ID format
        self.assertTrue(cancellation_id.startswith("cancel_"))
        self.assertTrue(len(cancellation_id) > 10)
        
        # Test consistency - same inputs should generate same ID
        cancellation_id2 = scraper.generate_cancellation_id(test_date, course_name, instructor_name)
        self.assertEqual(cancellation_id, cancellation_id2)
        
        # Different inputs should generate different IDs
        cancellation_id3 = scraper.generate_cancellation_id(date(2024, 1, 16), course_name, instructor_name)
        self.assertNotEqual(cancellation_id, cancellation_id3)
        
        print("✓ Cancellation ID generation test passed")


def main():
    """Main test runner"""
    print("🧪 Running Cancellation Monitoring Unit Tests")
    print("="*60)
    print("Testing: Table extraction, baseline comparison, data format")
    print("="*60)
    
    # Set up basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run unit tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCancellationMonitoringLogic)
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
        print("   ✓ Table data extraction accuracy (Requirement 8.1)")
        print("   ✓ Baseline comparison logic (Requirement 8.2)")
        print("   ✓ Structured data format validation (Requirement 8.3)")
        print("   ✓ Date parsing with multiple formats")
        print("   ✓ Cancellation ID generation consistency")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n🎉 Testing completed!")
    
    return 0 if (len(result.failures) == 0 and len(result.errors) == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
