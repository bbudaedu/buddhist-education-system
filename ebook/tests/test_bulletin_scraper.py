#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for BulletinScraper Course Cancellation Monitoring
測試公告爬蟲課程取消監控功能

This script tests the BulletinScraper implementation for extracting
course cancellation information from the Buddhist Education website.
"""

import os
import sys
import logging
import unittest
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bulletin_scraper import BulletinScraper
from enhanced_baseline_manager import EnhancedBaselineManager


class TestBulletinScraper(unittest.TestCase):
    """Test cases for BulletinScraper functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.chromedriver_path = "chromedriver-win64\\chromedriver.exe"
        self.download_dir = "test_downloads"
        
        # Create test logger
        self.logger = logging.getLogger("test_bulletin_scraper")
        self.logger.setLevel(logging.INFO)
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up test files
        test_files = [
            ".website_monitoring_baseline_cache.json",
            ".website_monitoring_baseline_cache.json.tmp"
        ]
        
        for filename in test_files:
            filepath = os.path.join(self.download_dir, filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
    
    def test_bulletin_scraper_initialization(self):
        """Test BulletinScraper initialization"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
            # Check basic properties
            self.assertEqual(scraper.content_type, "cancellation")
            self.assertEqual(scraper.bulletin_url, "https://www.budaedu.org/#/bulletins/course-cancel")
            self.assertIsNotNone(scraper.baseline_manager)
            
            print("✓ BulletinScraper initialization test passed")
            
        except Exception as e:
            self.fail(f"BulletinScraper initialization failed: {e}")
    
    def test_date_parsing(self):
        """Test date parsing functionality"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
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
            
            print("✓ Date parsing test passed")
            
        except Exception as e:
            self.fail(f"Date parsing test failed: {e}")
    
    def test_cancellation_id_generation(self):
        """Test cancellation ID generation"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
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
            
            print("✓ Cancellation ID generation test passed")
            
        except Exception as e:
            self.fail(f"Cancellation ID generation test failed: {e}")
    
    def test_baseline_management(self):
        """Test baseline management functionality"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
            # Test initial baseline (should be None)
            initial_baseline = scraper.get_cancellation_baseline()
            self.assertIsNone(initial_baseline)
            
            # Set a baseline
            test_date = date(2024, 1, 15)
            success = scraper.update_cancellation_baseline(test_date)
            self.assertTrue(success)
            
            # Retrieve the baseline
            retrieved_baseline = scraper.get_cancellation_baseline()
            self.assertEqual(retrieved_baseline, test_date)
            
            # Update with a newer date
            newer_date = date(2024, 1, 20)
            success = scraper.update_cancellation_baseline(newer_date)
            self.assertTrue(success)
            
            # Verify the update
            updated_baseline = scraper.get_cancellation_baseline()
            self.assertEqual(updated_baseline, newer_date)
            
            print("✓ Baseline management test passed")
            
        except Exception as e:
            self.fail(f"Baseline management test failed: {e}")
    
    def test_cancellation_filtering(self):
        """Test new cancellation filtering logic"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
            # Set up test data
            baseline_date = date(2024, 1, 15)
            scraper.update_cancellation_baseline(baseline_date)
            
            # Create test cancellations
            all_cancellations = [
                {
                    'cancellation_id': 'cancel_1',
                    'cancellation_date': date(2024, 1, 10),  # Before baseline
                    'course_name': '舊課程',
                    'instructor_name': '講師A'
                },
                {
                    'cancellation_id': 'cancel_2',
                    'cancellation_date': date(2024, 1, 15),  # Same as baseline
                    'course_name': '基準課程',
                    'instructor_name': '講師B'
                },
                {
                    'cancellation_id': 'cancel_3',
                    'cancellation_date': date(2024, 1, 20),  # After baseline
                    'course_name': '新課程',
                    'instructor_name': '講師C'
                }
            ]
            
            # Filter new cancellations
            new_cancellations = scraper.filter_new_cancellations(all_cancellations)
            
            # Should only return the one after baseline
            self.assertEqual(len(new_cancellations), 1)
            self.assertEqual(new_cancellations[0]['course_name'], '新課程')
            
            print("✓ Cancellation filtering test passed")
            
        except Exception as e:
            self.fail(f"Cancellation filtering test failed: {e}")
    
    def test_table_data_extraction_accuracy(self):
        """Test table data extraction accuracy with various row formats"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
            # Mock table row element
            mock_row = Mock()
            
            # Test case 1: Standard 3-column format
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
            
            # Test case 2: Missing instructor (2 columns)
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
            
            print("✓ Table data extraction accuracy test passed")
            
        except Exception as e:
            self.fail(f"Table data extraction accuracy test failed: {e}")
    
    def test_baseline_comparison_logic(self):
        """Test baseline comparison logic for detecting new cancellations"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
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
            scraper.update_cancellation_baseline(baseline_date)
            
            new_cancellations = scraper.filter_new_cancellations(all_cancellations)
            self.assertEqual(len(new_cancellations), 1)
            self.assertEqual(new_cancellations[0]['cancellation_date'], date(2024, 1, 15))
            
            # Test case 3: Baseline after all cancellations (no new ones)
            baseline_date = date(2024, 1, 20)
            scraper.update_cancellation_baseline(baseline_date)
            
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
            
        except Exception as e:
            self.fail(f"Baseline comparison logic test failed: {e}")
    
    def test_structured_data_format_for_cancellations(self):
        """Test structured data format compliance for cancellation records"""
        try:
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            
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
            
        except Exception as e:
            self.fail(f"Structured data format test failed: {e}")
    
    @patch('bulletin_scraper.BulletinScraper.setup_driver')
    @patch('bulletin_scraper.BulletinScraper.navigate_to_bulletin_page')
    @patch('bulletin_scraper.BulletinScraper.extract_cancellation_table')
    def test_process_cancellation_monitoring_mock(self, mock_extract, mock_navigate, mock_setup):
        """Test complete cancellation monitoring process with mocked web operations"""
        try:
            # Set up mocks
            mock_setup.return_value = True
            mock_navigate.return_value = True
            
            # Mock extracted cancellation data
            mock_cancellations = [
                {
                    'cancellation_id': 'cancel_test_1',
                    'cancellation_date': date(2024, 1, 20),
                    'course_name': '測試課程1',
                    'instructor_name': '測試講師1',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'cancellation'
                },
                {
                    'cancellation_id': 'cancel_test_2',
                    'cancellation_date': date(2024, 1, 25),
                    'course_name': '測試課程2',
                    'instructor_name': '測試講師2',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'cancellation'
                }
            ]
            mock_extract.return_value = mock_cancellations
            
            # Create scraper and set baseline
            scraper = BulletinScraper(self.chromedriver_path, self.download_dir, self.logger)
            scraper.update_cancellation_baseline(date(2024, 1, 15))
            
            # Mock driver to avoid actual browser operations
            scraper.driver = Mock()
            
            # Process monitoring
            result = scraper.process_cancellation_monitoring()
            
            # Verify results
            self.assertTrue(result['success'])
            self.assertEqual(len(result['cancellations']), 2)
            self.assertEqual(len(result['new_cancellations']), 2)  # Both are after baseline
            
            print("✓ Process cancellation monitoring test passed")
            
        except Exception as e:
            self.fail(f"Process cancellation monitoring test failed: {e}")


class TestEnhancedBaselineManager(unittest.TestCase):
    """Test cases for EnhancedBaselineManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = "test_baseline"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir, exist_ok=True)
        
        self.logger = logging.getLogger("test_baseline_manager")
        self.logger.setLevel(logging.INFO)
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up test files
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_baseline_manager_initialization(self):
        """Test EnhancedBaselineManager initialization"""
        try:
            manager = EnhancedBaselineManager("test_project", self.test_dir, self.logger)
            
            self.assertEqual(manager.project_name, "test_project")
            self.assertEqual(manager.cache_dir, self.test_dir)
            
            print("✓ EnhancedBaselineManager initialization test passed")
            
        except Exception as e:
            self.fail(f"EnhancedBaselineManager initialization failed: {e}")
    
    def test_cancellation_baseline_operations(self):
        """Test cancellation baseline operations"""
        try:
            manager = EnhancedBaselineManager("test_project", self.test_dir, self.logger)
            
            # Test initial state
            baseline = manager.get_cancellation_baseline()
            self.assertIsNone(baseline)
            
            # Set baseline
            test_date = date(2024, 1, 15)
            success = manager.update_cancellation_baseline(test_date)
            self.assertTrue(success)
            
            # Retrieve baseline
            retrieved = manager.get_cancellation_baseline()
            self.assertEqual(retrieved, test_date)
            
            # Update baseline
            new_date = date(2024, 1, 20)
            success = manager.update_cancellation_baseline(new_date)
            self.assertTrue(success)
            
            # Verify update
            updated = manager.get_cancellation_baseline()
            self.assertEqual(updated, new_date)
            
            print("✓ Cancellation baseline operations test passed")
            
        except Exception as e:
            self.fail(f"Cancellation baseline operations test failed: {e}")
    
    def test_multiple_content_type_baselines(self):
        """Test baseline management for multiple content types"""
        try:
            manager = EnhancedBaselineManager("test_project", self.test_dir, self.logger)
            
            # Set baselines for different content types
            manager.update_cancellation_baseline(date(2024, 1, 15))
            manager.update_carousel_baseline("carousel_123")
            manager.update_news_baseline(date(2024, 1, 20))
            manager.update_media_baseline("media_456")
            
            # Retrieve all baselines
            all_baselines = manager.get_all_baselines()
            
            self.assertEqual(all_baselines['cancellations'], date(2024, 1, 15))
            self.assertEqual(all_baselines['carousel'], "carousel_123")
            self.assertEqual(all_baselines['news'], date(2024, 1, 20))
            self.assertEqual(all_baselines['media'], "media_456")
            
            print("✓ Multiple content type baselines test passed")
            
        except Exception as e:
            self.fail(f"Multiple content type baselines test failed: {e}")


def run_integration_test():
    """Run integration test with actual website (if available)"""
    print("\n" + "="*60)
    print("INTEGRATION TEST - Course Cancellation Monitoring")
    print("="*60)
    
    # Set up logging for integration test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('integration_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("integration_test")
    
    chromedriver_path = "chromedriver-win64\\chromedriver.exe"
    download_dir = "test_downloads"
    
    # Check if ChromeDriver exists
    if not os.path.exists(chromedriver_path):
        print(f"⚠️  ChromeDriver not found at: {chromedriver_path}")
        print("   Skipping integration test")
        return
    
    scraper = None
    try:
        print("🚀 Starting integration test...")
        
        # Initialize scraper
        scraper = BulletinScraper(chromedriver_path, download_dir, logger)
        
        # Test baseline operations
        print("📊 Testing baseline operations...")
        initial_baseline = scraper.get_cancellation_baseline()
        print(f"   Initial baseline: {initial_baseline}")
        
        # Set a test baseline
        test_baseline = date(2024, 1, 1)
        success = scraper.update_cancellation_baseline(test_baseline)
        print(f"   Set test baseline: {success}")
        
        # Process cancellation monitoring
        print("🔍 Processing cancellation monitoring...")
        result = scraper.process_cancellation_monitoring()
        
        if result['success']:
            print(f"✅ Integration test completed successfully!")
            print(f"   Total cancellations found: {len(result['cancellations'])}")
            print(f"   New cancellations: {len(result['new_cancellations'])}")
            
            # Display some sample data
            if result['cancellations']:
                print("\n📋 Sample cancellation data:")
                for i, cancellation in enumerate(result['cancellations'][:3]):
                    print(f"   {i+1}. {cancellation['course_name']} - {cancellation['cancellation_date']}")
                    
        else:
            print(f"❌ Integration test failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        logger.error(f"Integration test error: {e}", exc_info=True)
    finally:
        if scraper:
            scraper.cleanup()
        print("🧹 Integration test cleanup completed")


def main():
    """Main test runner"""
    print("🧪 Running BulletinScraper Tests")
    print("="*50)
    
    # Set up basic logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add BulletinScraper tests
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestBulletinScraper))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestEnhancedBaselineManager))
    
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
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    # Ask user if they want to run integration test
    if result.testsRun > 0 and len(result.failures) == 0 and len(result.errors) == 0:
        print("\n✅ All unit tests passed!")
        
        try:
            user_input = input("\n🤔 Run integration test with actual website? (y/N): ").strip().lower()
            if user_input in ['y', 'yes']:
                run_integration_test()
            else:
                print("⏭️  Skipping integration test")
        except KeyboardInterrupt:
            print("\n⏭️  Skipping integration test")
    else:
        print("\n⚠️  Some tests failed. Fix issues before running integration test.")
    
    print("\n🎉 Testing completed!")


if __name__ == "__main__":
    main()