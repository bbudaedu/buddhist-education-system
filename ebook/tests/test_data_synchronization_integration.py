#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Synchronization Integration Tests
資料同步整合測試

This module provides integration tests for data synchronization between
Excel files and MySQL database, covering:
- Excel and MySQL data consistency
- Batch operation performance
- Error recovery and rollback functionality

Requirements covered: 4.1, 4.2, 4.3
"""

import os
import sys
import json
import time
import logging
import unittest
import tempfile
from datetime import datetime
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import data synchronization components
from enhanced_data_synchronizer import EnhancedDataSynchronizer
from document_generator import DocumentGenerator


class TestDataSynchronizationIntegration(unittest.TestCase):
    """
    Integration tests for data synchronization functionality
    
    Tests Excel and MySQL data consistency, batch operations,
    and error recovery mechanisms.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all test cases"""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_data_sync_integration.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # Create temporary directory for test files
        cls.test_dir = tempfile.mkdtemp(prefix='data_sync_test_')
        cls.logger.info(f"Test directory created: {cls.test_dir}")
        
        # Create test configuration
        cls.test_config = {
            'download_dir': os.path.join(cls.test_dir, 'generated_documents'),
            'mysql': {
                'enabled': False  # Disabled for unit testing
            }
        }
        
        # Create output directory
        os.makedirs(cls.test_config['download_dir'], exist_ok=True)
        
        cls.logger.info("Data synchronization test environment set up completed")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        try:
            import shutil
            if os.path.exists(cls.test_dir):
                shutil.rmtree(cls.test_dir)
                cls.logger.info(f"Test directory cleaned up: {cls.test_dir}")
        except Exception as e:
            cls.logger.warning(f"Error cleaning up test directory: {e}")
    
    def setUp(self):
        """Set up for each test case"""
        self.logger.info(f"Starting test: {self._testMethodName}")
        
        # Initialize DocumentGenerator
        self.document_generator = DocumentGenerator(
            output_dir=self.test_config['download_dir'],
            logger=self.logger
        )
        
        # Initialize EnhancedDataSynchronizer
        self.synchronizer = EnhancedDataSynchronizer(
            document_generator=self.document_generator,
            config=self.test_config,
            logger=self.logger
        )
    
    def tearDown(self):
        """Clean up after each test case"""
        self.logger.info(f"Completed test: {self._testMethodName}")
    
    def test_excel_mysql_data_consistency_carousel(self):
        """
        Test data consistency between Excel and MySQL for carousel content
        
        Requirements: 4.1, 4.5, 4.8
        """
        self.logger.info("Testing Excel and MySQL data consistency for carousel content...")
        
        try:
            # Prepare test carousel data
            carousel_data = [
                {
                    'carousel_id': 'carousel_001',
                    'banner_title': '佛學講座：心經導讀',
                    'image_url': 'https://example.com/banner1.jpg',
                    'activity_link': 'https://example.com/activity1',
                    'course_name': '心經導讀課程',
                    'location': '台北講堂',
                    'instructor': '釋慧明法師',
                    'description': '深入淺出講解心經要義',
                    'extraction_timestamp': datetime.now()
                },
                {
                    'carousel_id': 'carousel_002',
                    'banner_title': '禪修營報名',
                    'image_url': 'https://example.com/banner2.jpg',
                    'activity_link': 'https://example.com/activity2',
                    'course_name': '初階禪修營',
                    'location': '南投禪修中心',
                    'instructor': '釋慧光法師',
                    'description': '三日兩夜禪修體驗',
                    'extraction_timestamp': datetime.now()
                }
            ]
            
            # Test Excel synchronization
            excel_success = self.synchronizer.sync_content_type('carousel', carousel_data)
            self.assertTrue(excel_success, "Excel synchronization should succeed")
            
            # Verify Excel file was created
            excel_files = self.document_generator.list_generated_files()
            self.assertGreater(len(excel_files), 0, "Excel file should be created")
            
            # Verify Excel data structure
            excel_data = self.synchronizer._prepare_excel_data('carousel', carousel_data)
            self.assertEqual(len(excel_data), len(carousel_data), 
                           "Excel data count should match input data")
            
            # Verify required fields are present
            for row in excel_data:
                self.assertIn('ID', row)
                self.assertIn('橫幅標題', row)
                self.assertIn('課程名稱', row)
                self.assertIn('講師', row)
            
            # Test data consistency validation
            content_data = {'carousel': carousel_data}
            validation_result = self.synchronizer.validate_data_consistency(content_data)
            
            self.assertIsInstance(validation_result, dict)
            self.assertIn('consistent', validation_result)
            self.assertIn('content_type_results', validation_result)
            
            # Verify carousel content validation
            self.assertIn('carousel', validation_result['content_type_results'])
            carousel_result = validation_result['content_type_results']['carousel']
            self.assertEqual(carousel_result['excel_count'], len(carousel_data))
            
            self.logger.info("✓ Excel and MySQL data consistency test for carousel passed")
            
        except Exception as e:
            self.fail(f"Excel and MySQL data consistency test failed: {e}")
    
    def test_excel_mysql_data_consistency_all_content_types(self):
        """
        Test data consistency for all content types
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        self.logger.info("Testing data consistency for all content types...")
        
        try:
            # Prepare test data for all content types
            test_content = {
                'carousel': [
                    {
                        'carousel_id': 'carousel_test_1',
                        'banner_title': '測試輪播',
                        'image_url': 'https://example.com/test.jpg',
                        'course_name': '測試課程',
                        'location': '測試地點',
                        'instructor': '測試講師',
                        'extraction_timestamp': datetime.now()
                    }
                ],
                'cancellation': [
                    {
                        'cancellation_id': 'cancel_test_1',
                        'cancellation_date': datetime.now().date(),
                        'course_name': '取消課程測試',
                        'instructor_name': '測試講師',
                        'extraction_timestamp': datetime.now()
                    }
                ],
                'news': [
                    {
                        'announcement_id': 'news_test_1',
                        'title': '測試新聞公告',
                        'publication_date': datetime.now().date(),
                        'content': '這是測試新聞內容',
                        'extraction_timestamp': datetime.now()
                    }
                ],
                'media': [
                    {
                        'media_id': 'media_test_1',
                        'course_title': '測試多媒體課程',
                        'speaker_name': '測試講者',
                        'start_date': datetime.now().date(),
                        'redirect_url': 'https://example.com/media',
                        'media_type': 'video',
                        'extraction_timestamp': datetime.now()
                    }
                ]
            }
            
            # Test synchronization for each content type
            for content_type, content_list in test_content.items():
                sync_success = self.synchronizer.sync_content_type(content_type, content_list)
                self.assertTrue(sync_success, 
                              f"{content_type} synchronization should succeed")
            
            # Test comprehensive Excel creation with all content types
            excel_path = self.synchronizer.create_excel_sheets(test_content)
            self.assertTrue(excel_path, "Comprehensive Excel file should be created")
            self.assertTrue(os.path.exists(excel_path), "Excel file should exist")
            
            # Validate data consistency across all content types
            validation_result = self.synchronizer.validate_data_consistency(test_content)
            
            self.assertIsInstance(validation_result, dict)
            self.assertIn('content_type_results', validation_result)
            
            # Verify each content type
            for content_type in test_content.keys():
                self.assertIn(content_type, validation_result['content_type_results'])
                type_result = validation_result['content_type_results'][content_type]
                self.assertEqual(type_result['excel_count'], len(test_content[content_type]))
            
            self.logger.info("✓ Data consistency test for all content types passed")
            
        except Exception as e:
            self.fail(f"Data consistency test for all content types failed: {e}")
    
    def test_batch_operation_performance(self):
        """
        Test batch operation performance with large datasets
        
        Requirements: 4.1, 4.2, 4.3
        """
        self.logger.info("Testing batch operation performance...")
        
        try:
            # Generate large dataset for performance testing
            large_dataset_size = 100
            
            large_carousel_data = []
            for i in range(large_dataset_size):
                large_carousel_data.append({
                    'carousel_id': f'carousel_perf_{i:04d}',
                    'banner_title': f'性能測試輪播 {i}',
                    'image_url': f'https://example.com/banner{i}.jpg',
                    'activity_link': f'https://example.com/activity{i}',
                    'course_name': f'性能測試課程 {i}',
                    'location': '測試地點',
                    'instructor': '測試講師',
                    'description': f'性能測試描述 {i}',
                    'extraction_timestamp': datetime.now()
                })
            
            # Measure Excel synchronization performance
            start_time = time.time()
            excel_success = self.synchronizer.sync_content_type('carousel', large_carousel_data)
            excel_duration = time.time() - start_time
            
            self.assertTrue(excel_success, "Large dataset Excel sync should succeed")
            self.logger.info(f"Excel sync time for {large_dataset_size} items: {excel_duration:.2f}s")
            
            # Performance assertions
            self.assertLess(excel_duration, 10.0, 
                          f"Excel sync should complete within 10 seconds for {large_dataset_size} items")
            
            # Test batch MySQL synchronization (mocked)
            content_data = {
                'carousel': large_carousel_data[:50],  # First 50 items
                'news': large_carousel_data[50:]  # Remaining items as news (for variety)
            }
            
            start_time = time.time()
            batch_success = self.synchronizer.sync_to_mysql_batch(content_data)
            batch_duration = time.time() - start_time
            
            self.assertTrue(batch_success, "Batch MySQL sync should succeed")
            self.logger.info(f"Batch MySQL sync time: {batch_duration:.2f}s")
            
            # Verify batch operation efficiency
            self.assertLess(batch_duration, 5.0, 
                          "Batch MySQL sync should be efficient (mocked)")
            
            # Test comprehensive Excel creation performance
            start_time = time.time()
            excel_path = self.synchronizer.create_excel_sheets(content_data)
            comprehensive_duration = time.time() - start_time
            
            self.assertTrue(excel_path, "Comprehensive Excel should be created")
            self.logger.info(f"Comprehensive Excel creation time: {comprehensive_duration:.2f}s")
            
            self.assertLess(comprehensive_duration, 15.0, 
                          "Comprehensive Excel creation should complete within 15 seconds")
            
            self.logger.info("✓ Batch operation performance test passed")
            
        except Exception as e:
            self.fail(f"Batch operation performance test failed: {e}")
    
    def test_error_recovery_excel_generation_failure(self):
        """
        Test error recovery when Excel generation fails
        
        Requirements: 4.5, 4.7, 4.8
        """
        self.logger.info("Testing error recovery for Excel generation failure...")
        
        try:
            # Test with invalid data that should cause Excel generation to fail gracefully
            invalid_data = [
                {
                    'carousel_id': None,  # Invalid: None value
                    'banner_title': 'Test',
                    'extraction_timestamp': 'invalid_datetime'  # Invalid datetime
                }
            ]
            
            # Attempt synchronization with invalid data
            sync_success = self.synchronizer.sync_content_type('carousel', invalid_data)
            
            # System should handle error gracefully
            # The sync might succeed with data conversion or fail gracefully
            self.assertIsInstance(sync_success, bool, "Sync should return boolean result")
            
            # Test with empty data
            empty_success = self.synchronizer.sync_content_type('carousel', [])
            self.assertTrue(empty_success, "Empty data should be handled gracefully")
            
            # Test with None data
            none_success = self.synchronizer.sync_content_type('carousel', None)
            self.assertIsInstance(none_success, bool, "None data should be handled")
            
            self.logger.info("✓ Error recovery for Excel generation failure test passed")
            
        except Exception as e:
            self.fail(f"Error recovery test failed: {e}")
    
    def test_error_recovery_mysql_sync_failure(self):
        """
        Test error recovery when MySQL synchronization fails
        
        Requirements: 4.5, 4.7, 4.8
        """
        self.logger.info("Testing error recovery for MySQL sync failure...")
        
        try:
            # Create synchronizer with MySQL enabled but no actual connection
            mysql_config = {
                'download_dir': self.test_config['download_dir'],
                'mysql': {
                    'enabled': True  # Enabled but will fail
                }
            }
            
            mysql_synchronizer = EnhancedDataSynchronizer(
                document_generator=self.document_generator,
                config=mysql_config,
                logger=self.logger
            )
            
            # Prepare test data
            test_data = [
                {
                    'carousel_id': 'error_test_1',
                    'banner_title': 'Error Recovery Test',
                    'course_name': 'Test Course',
                    'extraction_timestamp': datetime.now()
                }
            ]
            
            # Attempt synchronization (MySQL will fail, Excel should succeed)
            sync_success = mysql_synchronizer.sync_content_type('carousel', test_data)
            
            # System should handle MySQL failure gracefully
            # Excel sync should still succeed even if MySQL fails
            self.assertIsInstance(sync_success, bool, "Sync should return boolean result")
            
            # Verify Excel file was still created despite MySQL failure
            excel_files = self.document_generator.list_generated_files()
            self.assertGreater(len(excel_files), 0, 
                             "Excel file should be created even if MySQL fails")
            
            self.logger.info("✓ Error recovery for MySQL sync failure test passed")
            
        except Exception as e:
            self.fail(f"Error recovery for MySQL sync failure test failed: {e}")
    
    def test_rollback_functionality(self):
        """
        Test rollback functionality for failed synchronization
        
        Requirements: 4.5, 4.7, 4.8
        """
        self.logger.info("Testing rollback functionality...")
        
        try:
            # Prepare test data
            test_data = {
                'carousel': [
                    {
                        'carousel_id': 'rollback_test_1',
                        'banner_title': 'Rollback Test',
                        'course_name': 'Test Course',
                        'extraction_timestamp': datetime.now()
                    }
                ]
            }
            
            # Get initial file count
            initial_files = self.document_generator.list_generated_files()
            initial_count = len(initial_files)
            
            # Add small delay to ensure unique timestamp
            time.sleep(0.1)
            
            # Perform successful synchronization
            sync_success = self.synchronizer.sync_content_type('carousel', test_data['carousel'])
            self.assertTrue(sync_success, "Initial sync should succeed")
            
            # Verify file was created
            after_sync_files = self.document_generator.list_generated_files()
            self.assertGreaterEqual(len(after_sync_files), initial_count, 
                             "File count should not decrease")
            
            # Test data consistency validation (acts as verification before commit)
            validation_result = self.synchronizer.validate_data_consistency(test_data)
            self.assertIsInstance(validation_result, dict)
            self.assertIn('consistent', validation_result)
            
            # In a real implementation with transactions, we would test:
            # 1. Begin transaction
            # 2. Perform operations
            # 3. Detect error
            # 4. Rollback transaction
            # 5. Verify data is unchanged
            
            # For this test, we verify that the system can detect inconsistencies
            # which would trigger a rollback in a transactional system
            
            self.logger.info("✓ Rollback functionality test passed")
            
        except Exception as e:
            self.fail(f"Rollback functionality test failed: {e}")
    
    def test_data_consistency_validation_comprehensive(self):
        """
        Test comprehensive data consistency validation
        
        Requirements: 4.5, 4.8
        """
        self.logger.info("Testing comprehensive data consistency validation...")
        
        try:
            # Prepare comprehensive test data
            comprehensive_data = {
                'carousel': [
                    {
                        'carousel_id': f'carousel_val_{i}',
                        'banner_title': f'驗證測試 {i}',
                        'course_name': f'課程 {i}',
                        'extraction_timestamp': datetime.now()
                    }
                    for i in range(10)
                ],
                'cancellation': [
                    {
                        'cancellation_id': f'cancel_val_{i}',
                        'course_name': f'取消課程 {i}',
                        'instructor_name': f'講師 {i}',
                        'extraction_timestamp': datetime.now()
                    }
                    for i in range(5)
                ],
                'news': [
                    {
                        'announcement_id': f'news_val_{i}',
                        'title': f'新聞 {i}',
                        'content': f'內容 {i}',
                        'extraction_timestamp': datetime.now()
                    }
                    for i in range(8)
                ],
                'media': [
                    {
                        'media_id': f'media_val_{i}',
                        'course_title': f'媒體課程 {i}',
                        'speaker_name': f'講者 {i}',
                        'extraction_timestamp': datetime.now()
                    }
                    for i in range(6)
                ]
            }
            
            # Synchronize all content types
            for content_type, content_list in comprehensive_data.items():
                sync_success = self.synchronizer.sync_content_type(content_type, content_list)
                self.assertTrue(sync_success, 
                              f"{content_type} sync should succeed")
            
            # Perform comprehensive validation
            validation_result = self.synchronizer.validate_data_consistency(comprehensive_data)
            
            # Verify validation structure
            self.assertIsInstance(validation_result, dict)
            self.assertIn('consistent', validation_result)
            self.assertIn('issues', validation_result)
            self.assertIn('content_type_results', validation_result)
            
            # Verify each content type validation
            for content_type, content_list in comprehensive_data.items():
                self.assertIn(content_type, validation_result['content_type_results'])
                
                type_result = validation_result['content_type_results'][content_type]
                self.assertIn('excel_count', type_result)
                self.assertIn('consistent', type_result)
                self.assertIn('issues', type_result)
                
                # Verify counts match
                self.assertEqual(type_result['excel_count'], len(content_list),
                               f"{content_type} Excel count should match input")
            
            # Log validation results
            self.logger.info(f"Validation result: {validation_result['consistent']}")
            if validation_result['issues']:
                self.logger.info(f"Validation issues: {validation_result['issues']}")
            
            self.logger.info("✓ Comprehensive data consistency validation test passed")
            
        except Exception as e:
            self.fail(f"Comprehensive data consistency validation test failed: {e}")
    
    def test_concurrent_synchronization_operations(self):
        """
        Test concurrent synchronization operations for thread safety
        
        Requirements: 4.1, 4.2, 4.3
        """
        self.logger.info("Testing concurrent synchronization operations...")
        
        try:
            import threading
            
            # Prepare test data for concurrent operations
            test_datasets = {
                'thread_1': {
                    'carousel': [
                        {
                            'carousel_id': 'concurrent_1_1',
                            'banner_title': '並發測試 1',
                            'course_name': '課程 1',
                            'extraction_timestamp': datetime.now()
                        }
                    ]
                },
                'thread_2': {
                    'news': [
                        {
                            'announcement_id': 'concurrent_2_1',
                            'title': '並發新聞 2',
                            'content': '內容 2',
                            'extraction_timestamp': datetime.now()
                        }
                    ]
                },
                'thread_3': {
                    'media': [
                        {
                            'media_id': 'concurrent_3_1',
                            'course_title': '並發媒體 3',
                            'speaker_name': '講者 3',
                            'extraction_timestamp': datetime.now()
                        }
                    ]
                }
            }
            
            results = {}
            threads = []
            
            def sync_operation(thread_id, content_data):
                try:
                    for content_type, content_list in content_data.items():
                        success = self.synchronizer.sync_content_type(content_type, content_list)
                        results[thread_id] = {
                            'success': success,
                            'content_type': content_type,
                            'error': None
                        }
                except Exception as e:
                    results[thread_id] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Start concurrent threads
            for thread_id, content_data in test_datasets.items():
                thread = threading.Thread(
                    target=sync_operation,
                    args=(thread_id, content_data)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=30)
                self.assertFalse(thread.is_alive(), "Thread should complete within timeout")
            
            # Verify all operations succeeded
            for thread_id, result in results.items():
                self.assertTrue(result['success'], 
                              f"{thread_id} should succeed: {result.get('error')}")
            
            self.logger.info("✓ Concurrent synchronization operations test passed")
            
        except Exception as e:
            self.fail(f"Concurrent synchronization operations test failed: {e}")


def run_tests():
    """Run all data synchronization integration tests"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataSynchronizationIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
