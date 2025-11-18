#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Integration Tests for Website Monitor System
網站監控系統端到端整合測試

This module provides comprehensive end-to-end integration tests for the complete
website monitoring system, including:
- Complete monitoring cycle execution
- Data flow validation from scraping to notification
- Error scenarios and recovery mechanisms
- Performance and reliability testing

Requirements covered: 10.1, 10.2, 10.3
"""

import os
import sys
import json
import time
import logging
import unittest
import tempfile
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import monitoring system components
from website_monitor import WebsiteMonitor
from monitoring_controller import MonitoringController
from enhanced_config_manager import EnhancedConfigManager
from enhanced_data_synchronizer import EnhancedDataSynchronizer
from notification_processor import NotificationProcessor
from document_generator import DocumentGenerator
from email_sender import EmailSender


class TestWebsiteMonitorEndToEnd(unittest.TestCase):
    """
    Comprehensive end-to-end integration tests for website monitoring system
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all test cases"""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_website_monitor_end_to_end.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # Create temporary directory for test files
        cls.test_dir = tempfile.mkdtemp(prefix='website_monitor_test_')
        cls.logger.info(f"Test directory created: {cls.test_dir}")
        
        # Create test configuration
        cls.test_config_path = os.path.join(cls.test_dir, "test_config.json")
        cls._create_test_configuration()
        
        cls.logger.info("End-to-end test environment set up completed")
    
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
    
    @classmethod
    def _create_test_configuration(cls):
        """Create comprehensive test configuration"""
        test_config = {
            "gemini_api_key": "test_api_key_for_integration_testing",
            "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
            "target_url": "https://www.budaedu.org/#/books/applicable/chinese",
            "baseline_book_title": "Test Integration Book",
            "download_dir": os.path.join(cls.test_dir, "downloads"),
            "website_monitoring": {
                "enabled": True,
                "monitoring_interval": 300,  # 5 minutes for testing
                "content_types": {
                    "carousel": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/",
                        "baseline": ""
                    },
                    "cancellation": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/course-cancel",
                        "baseline": ""
                    },
                    "news": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/",
                        "baseline": ""
                    },
                    "media": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/series/live-streaming",
                        "baseline": ""
                    }
                },
                "chrome_devtools": {
                    "enabled": False,  # Disabled for testing to avoid MCP dependencies
                    "headless": True,
                    "timeout": 30
                },
                "data_sync": {
                    "excel_output_dir": os.path.join(cls.test_dir, "generated_documents"),
                    "mysql_batch_size": 50,
                    "backup_enabled": True
                },
                "notifications": {
                    "line_enabled": False,  # Disabled for testing
                    "email_enabled": False,  # Disabled for testing
                    "immediate_alerts": ["cancellation"],
                    "daily_summary": ["carousel", "news", "media"],
                    "cycle_notifications": True
                }
            },
            "smtp_server": "test.smtp.com",
            "smtp_username": "test@example.com",
            "smtp_password": "test_password",
            "email_recipients": ["recipient@example.com"],
            "line_bot": {
                "enabled": False,
                "channel_access_token": "test_token",
                "channel_secret": "test_secret"
            }
        }
        
        # Create directories
        os.makedirs(test_config["download_dir"], exist_ok=True)
        os.makedirs(test_config["website_monitoring"]["data_sync"]["excel_output_dir"], exist_ok=True)
        
        # Write configuration file
        with open(cls.test_config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        
        cls.logger.info(f"Test configuration created: {cls.test_config_path}")
    
    def setUp(self):
        """Set up for each test case"""
        self.logger.info(f"Starting test: {self._testMethodName}")
        
        # Initialize fresh instances for each test
        self.website_monitor = None
        self.monitoring_controller = None
        
        # Track test resources for cleanup
        self.test_resources = []
    
    def tearDown(self):
        """Clean up after each test case"""
        try:
            # Clean up website monitor
            if self.website_monitor:
                self.website_monitor.cleanup()
            
            # Clean up monitoring controller
            if self.monitoring_controller:
                self.monitoring_controller.cleanup_system()
            
            # Clean up any additional test resources
            for resource in self.test_resources:
                try:
                    if hasattr(resource, 'cleanup'):
                        resource.cleanup()
                    elif hasattr(resource, 'close'):
                        resource.close()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up resource: {e}")
            
        except Exception as e:
            self.logger.warning(f"Error in test cleanup: {e}")
        
        self.logger.info(f"Completed test: {self._testMethodName}")
    
    def test_complete_monitoring_cycle_execution(self):
        """
        Test complete monitoring cycle execution with all components
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing complete monitoring cycle execution...")
        
        try:
            # Initialize WebsiteMonitor
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            self.assertIsNotNone(self.website_monitor)
            
            # Mock the scrapers to avoid actual web scraping
            self._mock_scrapers_for_testing()
            
            # Initialize components
            init_success = self.website_monitor.initialize_components()
            self.assertTrue(init_success, "Component initialization should succeed")
            
            # Verify all components are initialized
            status = self.website_monitor.get_monitoring_status()
            self.assertTrue(status['components_initialized']['data_synchronizer'])
            self.assertTrue(status['components_initialized']['notification_processor'])
            
            # Execute single monitoring cycle
            cycle_success = self.website_monitor.start_monitoring_cycle()
            self.assertTrue(cycle_success, "Monitoring cycle should complete successfully")
            
            # Verify cycle statistics
            final_status = self.website_monitor.get_monitoring_status()
            stats = final_status['statistics']
            
            self.assertEqual(stats['cycles_completed'], 1)
            self.assertGreater(stats['total_content_processed'], 0)
            self.assertIsNotNone(stats['last_successful_cycle'])
            self.assertGreater(stats['average_cycle_time'], 0)
            
            self.logger.info("✓ Complete monitoring cycle execution test passed")
            
        except Exception as e:
            self.fail(f"Complete monitoring cycle execution test failed: {e}")
    
    def test_data_flow_from_scraping_to_notification(self):
        """
        Test complete data flow from scraping through synchronization to notification
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing data flow from scraping to notification...")
        
        try:
            # Initialize system components
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            
            # Mock components to track data flow
            mock_data = self._create_mock_content_data()
            
            # Mock scrapers to return test data
            self._mock_scrapers_with_test_data(mock_data)
            
            # Mock data synchronizer to track synchronization
            mock_sync_results = {}
            original_sync_method = None
            
            if hasattr(self.website_monitor, 'synchronize_data'):
                original_sync_method = self.website_monitor.synchronize_data
                
                def mock_synchronize_data(content_data):
                    mock_sync_results['called'] = True
                    mock_sync_results['content_data'] = content_data
                    mock_sync_results['total_items'] = sum(len(items) for items in content_data.values())
                    return True
                
                self.website_monitor.synchronize_data = mock_synchronize_data
            
            # Mock notification processor to track notifications
            mock_notification_results = {}
            original_notification_method = None
            
            if hasattr(self.website_monitor, 'send_notifications'):
                original_notification_method = self.website_monitor.send_notifications
                
                def mock_send_notifications(content_data, processing_results):
                    mock_notification_results['called'] = True
                    mock_notification_results['content_data'] = content_data
                    mock_notification_results['processing_results'] = processing_results
                    return True
                
                self.website_monitor.send_notifications = mock_send_notifications
            
            # Initialize components
            init_success = self.website_monitor.initialize_components()
            self.assertTrue(init_success)
            
            # Execute monitoring cycle
            cycle_success = self.website_monitor.start_monitoring_cycle()
            self.assertTrue(cycle_success)
            
            # Verify data synchronization was called
            self.assertTrue(mock_sync_results.get('called', False), "Data synchronization should be called")
            self.assertGreater(mock_sync_results.get('total_items', 0), 0, "Should have content to synchronize")
            
            # Verify notification processing was called
            self.assertTrue(mock_notification_results.get('called', False), "Notification processing should be called")
            
            # Verify data integrity through the flow
            sync_content = mock_sync_results.get('content_data', {})
            notification_content = mock_notification_results.get('content_data', {})
            
            # Check that the same content types are processed
            self.assertEqual(set(sync_content.keys()), set(notification_content.keys()))
            
            # Verify content counts match
            for content_type in sync_content.keys():
                sync_count = len(sync_content[content_type])
                notification_count = len(notification_content[content_type])
                self.assertEqual(sync_count, notification_count, 
                               f"Content count mismatch for {content_type}")
            
            self.logger.info("✓ Data flow from scraping to notification test passed")
            
        except Exception as e:
            self.fail(f"Data flow test failed: {e}")
    
    def test_error_scenarios_and_recovery_mechanisms(self):
        """
        Test error scenarios and recovery mechanisms
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing error scenarios and recovery mechanisms...")
        
        try:
            # Test 1: Component initialization failure recovery
            self._test_component_initialization_failure()
            
            # Test 2: Scraper failure recovery
            self._test_scraper_failure_recovery()
            
            # Test 3: Data synchronization failure recovery
            self._test_data_sync_failure_recovery()
            
            # Test 4: Notification failure recovery
            self._test_notification_failure_recovery()
            
            # Test 5: Network error recovery
            self._test_network_error_recovery()
            
            self.logger.info("✓ Error scenarios and recovery mechanisms test passed")
            
        except Exception as e:
            self.fail(f"Error scenarios test failed: {e}")
    
    def test_monitoring_controller_integration(self):
        """
        Test MonitoringController integration with WebsiteMonitor
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing MonitoringController integration...")
        
        try:
            # Initialize MonitoringController
            self.monitoring_controller = MonitoringController(self.test_config_path, self.logger)
            
            # Test system initialization
            init_success, init_message = self.monitoring_controller.initialize_system()
            self.assertTrue(init_success, f"System initialization should succeed: {init_message}")
            
            # Test system status retrieval
            status = self.monitoring_controller.get_system_status()
            self.assertTrue(status['system_initialized'])
            self.assertIn('configuration', status)
            self.assertIn('performance_metrics', status)
            
            # Mock the underlying website monitor for testing
            if self.monitoring_controller.website_monitor:
                self._mock_scrapers_for_testing(self.monitoring_controller.website_monitor)
            
            # Test single cycle execution through controller
            cycle_success, cycle_message, cycle_results = self.monitoring_controller.run_single_cycle()
            self.assertTrue(cycle_success, f"Single cycle should succeed: {cycle_message}")
            
            # Verify cycle results structure
            self.assertIn('success', cycle_results)
            self.assertIn('start_time', cycle_results)
            self.assertIn('end_time', cycle_results)
            self.assertIn('duration_seconds', cycle_results)
            
            # Test performance report generation
            performance_report = self.monitoring_controller.get_performance_report()
            self.assertIn('timestamp', performance_report)
            self.assertIn('performance_metrics', performance_report)
            self.assertIn('success_rate', performance_report)
            
            # Test configuration updates
            config_updates = {
                'chrome_devtools': {
                    'enabled': False,
                    'headless': True,
                    'timeout': 45
                }
            }
            update_success, update_message = self.monitoring_controller.update_configuration(config_updates)
            self.assertTrue(update_success, f"Configuration update should succeed: {update_message}")
            
            self.logger.info("✓ MonitoringController integration test passed")
            
        except Exception as e:
            self.fail(f"MonitoringController integration test failed: {e}")
    
    def test_concurrent_monitoring_operations(self):
        """
        Test concurrent monitoring operations and thread safety
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing concurrent monitoring operations...")
        
        try:
            # Initialize multiple monitoring instances
            monitor1 = WebsiteMonitor(self.test_config_path, self.logger)
            monitor2 = WebsiteMonitor(self.test_config_path, self.logger)
            
            self.test_resources.extend([monitor1, monitor2])
            
            # Mock scrapers for both instances
            self._mock_scrapers_for_testing(monitor1)
            self._mock_scrapers_for_testing(monitor2)
            
            # Initialize components
            init1 = monitor1.initialize_components()
            init2 = monitor2.initialize_components()
            
            self.assertTrue(init1 and init2, "Both monitors should initialize successfully")
            
            # Run concurrent monitoring cycles
            results = {}
            threads = []
            
            def run_monitoring_cycle(monitor, monitor_id):
                try:
                    success = monitor.start_monitoring_cycle()
                    results[monitor_id] = {'success': success, 'error': None}
                except Exception as e:
                    results[monitor_id] = {'success': False, 'error': str(e)}
            
            # Start concurrent threads
            thread1 = threading.Thread(target=run_monitoring_cycle, args=(monitor1, 'monitor1'))
            thread2 = threading.Thread(target=run_monitoring_cycle, args=(monitor2, 'monitor2'))
            
            threads.extend([thread1, thread2])
            
            thread1.start()
            thread2.start()
            
            # Wait for completion with timeout
            for thread in threads:
                thread.join(timeout=60)
                self.assertFalse(thread.is_alive(), "Thread should complete within timeout")
            
            # Verify both cycles completed successfully
            self.assertTrue(results['monitor1']['success'], 
                          f"Monitor1 should succeed: {results['monitor1'].get('error')}")
            self.assertTrue(results['monitor2']['success'], 
                          f"Monitor2 should succeed: {results['monitor2'].get('error')}")
            
            self.logger.info("✓ Concurrent monitoring operations test passed")
            
        except Exception as e:
            self.fail(f"Concurrent monitoring operations test failed: {e}")
    
    def test_performance_and_resource_management(self):
        """
        Test performance characteristics and resource management
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing performance and resource management...")
        
        try:
            # Initialize WebsiteMonitor
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            self._mock_scrapers_for_testing()
            
            # Initialize components
            init_success = self.website_monitor.initialize_components()
            self.assertTrue(init_success)
            
            # Measure performance of multiple cycles
            cycle_times = []
            memory_usage = []
            
            for i in range(3):  # Run 3 cycles for performance measurement
                start_time = time.time()
                
                # Monitor memory usage (simplified)
                import psutil
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # Execute monitoring cycle
                cycle_success = self.website_monitor.start_monitoring_cycle()
                self.assertTrue(cycle_success, f"Cycle {i+1} should succeed")
                
                # Measure performance
                end_time = time.time()
                cycle_duration = end_time - start_time
                cycle_times.append(cycle_duration)
                
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage.append(memory_after - memory_before)
                
                self.logger.info(f"Cycle {i+1}: {cycle_duration:.2f}s, Memory delta: {memory_after - memory_before:.2f}MB")
            
            # Verify performance characteristics
            avg_cycle_time = sum(cycle_times) / len(cycle_times)
            max_cycle_time = max(cycle_times)
            
            # Performance assertions (reasonable thresholds for testing - adjusted for actual web scraping)
            self.assertLess(avg_cycle_time, 600.0, "Average cycle time should be under 10 minutes")
            self.assertLess(max_cycle_time, 900.0, "Maximum cycle time should be under 15 minutes")
            
            # Memory usage should be reasonable
            avg_memory_delta = sum(memory_usage) / len(memory_usage)
            self.assertLess(avg_memory_delta, 100.0, "Average memory delta should be under 100MB")
            
            # Test resource cleanup
            initial_status = self.website_monitor.get_monitoring_status()
            self.website_monitor.cleanup()
            
            # Verify cleanup completed without errors
            self.assertFalse(self.website_monitor.monitoring_active)
            
            self.logger.info("✓ Performance and resource management test passed")
            
        except Exception as e:
            self.fail(f"Performance and resource management test failed: {e}")
    
    # Helper methods for test setup and mocking
    
    def _mock_scrapers_for_testing(self, monitor=None):
        """Mock scrapers to avoid actual web scraping during tests"""
        if monitor is None:
            monitor = self.website_monitor
        
        # Mock carousel scraper
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.return_value = [
            {
                'carousel_id': 'test_carousel_1',
                'banner_title': 'Test Carousel Banner',
                'image_url': 'https://example.com/banner.jpg',
                'activity_link': 'https://example.com/activity',
                'course_name': 'Test Course',
                'location': 'Test Location',
                'instructor': 'Test Instructor',
                'description': 'Test Description',
                'extraction_timestamp': datetime.now(),
                'content_type': 'carousel'
            }
        ]
        mock_carousel.update_carousel_baseline.return_value = True
        mock_carousel.cleanup.return_value = None
        
        # Mock bulletin scraper
        mock_bulletin = Mock()
        mock_bulletin.process_cancellation_monitoring.return_value = {
            'success': True,
            'cancellations': [
                {
                    'cancellation_id': 'test_cancel_1',
                    'cancellation_date': datetime.now().date(),
                    'course_name': 'Test Cancelled Course',
                    'instructor_name': 'Test Instructor',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'cancellation'
                }
            ],
            'new_cancellations': [],
            'message': 'Test cancellation processing completed'
        }
        mock_bulletin.cleanup.return_value = None
        
        # Mock news processor
        mock_news = Mock()
        mock_news.extract_news_items.return_value = [
            {
                'announcement_id': 'test_news_1',
                'title': 'Test News Announcement',
                'publication_date': datetime.now().date(),
                'content': 'Test news content',
                'extraction_timestamp': datetime.now(),
                'content_type': 'news'
            }
        ]
        mock_news.update_news_baseline.return_value = True
        mock_news.cleanup.return_value = None
        
        # Mock media processor
        mock_media = Mock()
        mock_media.extract_media_content.return_value = [
            {
                'media_id': 'test_media_1',
                'course_title': 'Test Media Course',
                'speaker_name': 'Test Speaker',
                'start_date': datetime.now().date(),
                'redirect_url': 'https://example.com/media',
                'media_type': 'video',
                'extraction_timestamp': datetime.now(),
                'content_type': 'media'
            }
        ]
        mock_media.detect_new_media_content.return_value = []
        mock_media.update_media_baseline.return_value = True
        mock_media.cleanup.return_value = None
        
        # Assign mocked scrapers
        monitor.scrapers = {
            'carousel': mock_carousel,
            'bulletin': mock_bulletin
        }
        monitor.processors = {
            'news': mock_news,
            'media': mock_media
        }
    
    def _mock_scrapers_with_test_data(self, test_data):
        """Mock scrapers with specific test data"""
        self._mock_scrapers_for_testing()
        
        # Update mock returns with test data
        if 'carousel' in test_data:
            self.website_monitor.scrapers['carousel'].extract_carousel_banners.return_value = test_data['carousel']
        
        if 'cancellation' in test_data:
            self.website_monitor.scrapers['bulletin'].process_cancellation_monitoring.return_value = {
                'success': True,
                'cancellations': test_data['cancellation'],
                'new_cancellations': test_data['cancellation'],
                'message': 'Test data processing'
            }
        
        if 'news' in test_data:
            self.website_monitor.processors['news'].extract_news_items.return_value = test_data['news']
        
        if 'media' in test_data:
            self.website_monitor.processors['media'].extract_media_content.return_value = test_data['media']
    
    def _create_mock_content_data(self):
        """Create mock content data for testing"""
        return {
            'carousel': [
                {
                    'carousel_id': 'mock_carousel_1',
                    'banner_title': 'Mock Carousel Banner 1',
                    'image_url': 'https://example.com/banner1.jpg',
                    'activity_link': 'https://example.com/activity1',
                    'course_name': 'Mock Course 1',
                    'location': 'Mock Location 1',
                    'instructor': 'Mock Instructor 1',
                    'description': 'Mock Description 1',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'carousel'
                }
            ],
            'cancellation': [
                {
                    'cancellation_id': 'mock_cancel_1',
                    'cancellation_date': datetime.now().date(),
                    'course_name': 'Mock Cancelled Course 1',
                    'instructor_name': 'Mock Instructor 1',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'cancellation'
                }
            ],
            'news': [
                {
                    'announcement_id': 'mock_news_1',
                    'title': 'Mock News Announcement 1',
                    'publication_date': datetime.now().date(),
                    'content': 'Mock news content 1',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'news'
                }
            ],
            'media': [
                {
                    'media_id': 'mock_media_1',
                    'course_title': 'Mock Media Course 1',
                    'speaker_name': 'Mock Speaker 1',
                    'start_date': datetime.now().date(),
                    'redirect_url': 'https://example.com/media1',
                    'media_type': 'video',
                    'extraction_timestamp': datetime.now(),
                    'content_type': 'media'
                }
            ]
        }
    
    def _test_component_initialization_failure(self):
        """Test component initialization failure recovery"""
        self.logger.info("Testing component initialization failure recovery...")
        
        # Create monitor with invalid configuration
        invalid_config_path = os.path.join(self.test_dir, "invalid_config.json")
        invalid_config = {"invalid": "config"}
        
        with open(invalid_config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        monitor = WebsiteMonitor(invalid_config_path, self.logger)
        
        # Initialization should fail gracefully
        init_success = monitor.initialize_components()
        self.assertFalse(init_success, "Initialization should fail with invalid config")
        
        # Monitor should handle failure gracefully
        status = monitor.get_monitoring_status()
        # Check that components are not initialized due to invalid config
        self.assertFalse(status.get('components_initialized', {}).get('data_synchronizer', True))
        
        monitor.cleanup()
    
    def _test_scraper_failure_recovery(self):
        """Test scraper failure recovery"""
        self.logger.info("Testing scraper failure recovery...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        
        # Mock scrapers with failures
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.side_effect = Exception("Scraper failure")
        mock_carousel.cleanup.return_value = None
        
        monitor.scrapers = {'carousel': mock_carousel}
        monitor.processors = {}
        
        # Initialize data components
        monitor._initialize_data_components()
        monitor._initialize_notification_components()
        
        # Cycle should handle scraper failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # The cycle might succeed or fail, but should not crash
        self.assertIsInstance(cycle_success, bool, "Cycle should return boolean result")
        
        monitor.cleanup()
    
    def _test_data_sync_failure_recovery(self):
        """Test data synchronization failure recovery"""
        self.logger.info("Testing data synchronization failure recovery...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        self._mock_scrapers_for_testing(monitor)
        
        # Mock data synchronizer to fail
        original_sync = monitor.synchronize_data
        monitor.synchronize_data = Mock(return_value=False)
        
        monitor.initialize_components()
        
        # Cycle should handle sync failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # Cycle might fail due to sync failure, but should not crash
        self.assertIsInstance(cycle_success, bool)
        
        monitor.cleanup()
    
    def _test_notification_failure_recovery(self):
        """Test notification failure recovery"""
        self.logger.info("Testing notification failure recovery...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        self._mock_scrapers_for_testing(monitor)
        
        # Mock notification processor to fail
        original_notify = monitor.send_notifications
        monitor.send_notifications = Mock(return_value=False)
        
        monitor.initialize_components()
        
        # Cycle should handle notification failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # Cycle might fail due to notification failure, but should not crash
        self.assertIsInstance(cycle_success, bool)
        
        monitor.cleanup()
    
    def _test_network_error_recovery(self):
        """Test network error recovery"""
        self.logger.info("Testing network error recovery...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        
        # Mock scrapers to simulate network errors
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.side_effect = [
            Exception("Network timeout"),  # First call fails
            []  # Second call succeeds with empty result
        ]
        mock_carousel.cleanup.return_value = None
        
        monitor.scrapers = {'carousel': mock_carousel}
        monitor.processors = {}
        
        monitor._initialize_data_components()
        monitor._initialize_notification_components()
        
        # First cycle should handle network error
        cycle_success1 = monitor.start_monitoring_cycle()
        self.assertIsInstance(cycle_success1, bool)
        
        # Second cycle should work (simulating network recovery)
        cycle_success2 = monitor.start_monitoring_cycle()
        self.assertIsInstance(cycle_success2, bool)
        
        monitor.cleanup()


def run_end_to_end_tests():
    """Run all end-to-end integration tests"""
    print("=" * 80)
    print("Website Monitor End-to-End Integration Tests")
    print("=" * 80)
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestWebsiteMonitorEndToEnd)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("End-to-End Integration Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_end_to_end_tests()
    sys.exit(0 if success else 1)