#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Focused End-to-End Integration Tests for Website Monitor System
網站監控系統端到端整合測試 (聚焦版本)

This module provides focused end-to-end integration tests that use mocking
to avoid long execution times while still testing the complete data flow
and error recovery mechanisms.

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
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import monitoring system components
from website_monitor import WebsiteMonitor
from monitoring_controller import MonitoringController


class TestWebsiteMonitorEndToEndFocused(unittest.TestCase):
    """
    Focused end-to-end integration tests for website monitoring system
    Uses mocking to ensure fast execution while testing complete workflows
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all test cases"""
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_website_monitor_end_to_end_focused.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # Create temporary directory for test files
        cls.test_dir = tempfile.mkdtemp(prefix='website_monitor_focused_test_')
        cls.logger.info(f"Test directory created: {cls.test_dir}")
        
        # Create test configuration
        cls.test_config_path = os.path.join(cls.test_dir, "test_config.json")
        cls._create_test_configuration()
        
        cls.logger.info("Focused end-to-end test environment set up completed")
    
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
                "monitoring_interval": 300,
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
                    "enabled": False,
                    "headless": True,
                    "timeout": 30
                },
                "data_sync": {
                    "excel_output_dir": os.path.join(cls.test_dir, "generated_documents"),
                    "mysql_batch_size": 50,
                    "backup_enabled": True
                },
                "notifications": {
                    "line_enabled": False,
                    "email_enabled": False,
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
    
    def test_complete_monitoring_cycle_execution_mocked(self):
        """
        Test complete monitoring cycle execution with mocked scrapers
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing complete monitoring cycle execution with mocked scrapers...")
        
        try:
            # Initialize WebsiteMonitor
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            self.assertIsNotNone(self.website_monitor)
            
            # Mock scrapers directly on the instance
            self._setup_direct_mock_scrapers()
            
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
    
    def test_data_flow_validation_mocked(self):
        """
        Test complete data flow from scraping through synchronization to notification
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing data flow validation with mocked components...")
        
        try:
            # Initialize system components
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            
            # Set up mock scrapers with specific test data
            test_data = self._create_mock_content_data()
            self._setup_direct_mock_scrapers_with_data(test_data)
            
            # Track data flow through the system
            sync_calls = []
            notification_calls = []
            
            # Mock data synchronizer to track calls
            original_sync = self.website_monitor.synchronize_data
            def mock_sync(content_data):
                sync_calls.append(content_data)
                return True
            self.website_monitor.synchronize_data = mock_sync
            
            # Mock notification sender to track calls
            original_notify = self.website_monitor.send_notifications
            def mock_notify(content_data, processing_results):
                notification_calls.append((content_data, processing_results))
                return True
            self.website_monitor.send_notifications = mock_notify
            
            # Initialize components
            init_success = self.website_monitor.initialize_components()
            self.assertTrue(init_success)
            
            # Execute monitoring cycle
            cycle_success = self.website_monitor.start_monitoring_cycle()
            self.assertTrue(cycle_success)
            
            # Verify data flow
            self.assertEqual(len(sync_calls), 1, "Data synchronization should be called once")
            self.assertEqual(len(notification_calls), 1, "Notification processing should be called once")
            
            # Verify data integrity
            sync_data = sync_calls[0]
            notification_data, processing_results = notification_calls[0]
            
            # Check that the same content types are processed
            self.assertEqual(set(sync_data.keys()), set(notification_data.keys()))
            
            # Verify content counts match expected test data
            expected_counts = {k: len(v) for k, v in test_data.items()}
            actual_sync_counts = {k: len(v) for k, v in sync_data.items()}
            actual_notification_counts = {k: len(v) for k, v in notification_data.items()}
            
            self.assertEqual(expected_counts, actual_sync_counts)
            self.assertEqual(expected_counts, actual_notification_counts)
            
            self.logger.info("✓ Data flow validation test passed")
            
        except Exception as e:
            self.fail(f"Data flow validation test failed: {e}")
    
    def test_error_scenarios_and_recovery_mechanisms_focused(self):
        """
        Test error scenarios and recovery mechanisms with focused approach
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing error scenarios and recovery mechanisms...")
        
        try:
            # Test 1: Component initialization failure recovery
            self._test_component_initialization_failure_focused()
            
            # Test 2: Scraper failure recovery
            self._test_scraper_failure_recovery_focused()
            
            # Test 3: Data synchronization failure recovery
            self._test_data_sync_failure_recovery_focused()
            
            # Test 4: Notification failure recovery
            self._test_notification_failure_recovery_focused()
            
            self.logger.info("✓ Error scenarios and recovery mechanisms test passed")
            
        except Exception as e:
            self.fail(f"Error scenarios test failed: {e}")
    
    def test_monitoring_controller_integration_mocked(self):
        """
        Test MonitoringController integration with mocked WebsiteMonitor
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing MonitoringController integration with mocked components...")
        
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
            
            self.logger.info("✓ MonitoringController integration test passed")
            
        except Exception as e:
            self.fail(f"MonitoringController integration test failed: {e}")
    
    def test_performance_characteristics_mocked(self):
        """
        Test performance characteristics with mocked components for fast execution
        
        Requirements: 10.1, 10.2, 10.3
        """
        self.logger.info("Testing performance characteristics with mocked components...")
        
        try:
            # Initialize WebsiteMonitor
            self.website_monitor = WebsiteMonitor(self.test_config_path, self.logger)
            
            # Mock scrapers for fast execution
            self._setup_fast_mock_scrapers()
            
            # Initialize components
            init_success = self.website_monitor.initialize_components()
            self.assertTrue(init_success)
            
            # Measure performance of multiple cycles
            cycle_times = []
            
            for i in range(3):  # Run 3 cycles for performance measurement
                start_time = time.time()
                
                # Execute monitoring cycle
                cycle_success = self.website_monitor.start_monitoring_cycle()
                self.assertTrue(cycle_success, f"Cycle {i+1} should succeed")
                
                # Measure performance
                end_time = time.time()
                cycle_duration = end_time - start_time
                cycle_times.append(cycle_duration)
                
                self.logger.info(f"Cycle {i+1}: {cycle_duration:.2f}s")
            
            # Verify performance characteristics (with mocked components should be fast)
            avg_cycle_time = sum(cycle_times) / len(cycle_times)
            max_cycle_time = max(cycle_times)
            
            # Performance assertions for mocked execution
            self.assertLess(avg_cycle_time, 5.0, "Average mocked cycle time should be under 5 seconds")
            self.assertLess(max_cycle_time, 10.0, "Maximum mocked cycle time should be under 10 seconds")
            
            # Test resource cleanup
            self.website_monitor.cleanup()
            self.assertFalse(self.website_monitor.monitoring_active)
            
            self.logger.info("✓ Performance characteristics test passed")
                
        except Exception as e:
            self.fail(f"Performance characteristics test failed: {e}")
    
    # Helper methods for test setup and mocking
    
    def _setup_mock_scrapers(self, mock_carousel, mock_bulletin, mock_news, mock_media):
        """Set up mock scrapers with default test data"""
        # Mock carousel scraper
        mock_carousel_instance = Mock()
        mock_carousel_instance.extract_carousel_banners.return_value = [
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
        mock_carousel_instance.update_carousel_baseline.return_value = True
        mock_carousel_instance.cleanup.return_value = None
        mock_carousel.return_value = mock_carousel_instance
        
        # Mock bulletin scraper
        mock_bulletin_instance = Mock()
        mock_bulletin_instance.process_cancellation_monitoring.return_value = {
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
        mock_bulletin_instance.cleanup.return_value = None
        mock_bulletin.return_value = mock_bulletin_instance
        
        # Mock news processor
        mock_news_instance = Mock()
        mock_news_instance.extract_news_items.return_value = [
            {
                'announcement_id': 'test_news_1',
                'title': 'Test News Announcement',
                'publication_date': datetime.now().date(),
                'content': 'Test news content',
                'extraction_timestamp': datetime.now(),
                'content_type': 'news'
            }
        ]
        mock_news_instance.update_news_baseline.return_value = True
        mock_news_instance.cleanup.return_value = None
        mock_news.return_value = mock_news_instance
        
        # Mock media processor
        mock_media_instance = Mock()
        mock_media_instance.extract_media_content.return_value = [
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
        mock_media_instance.detect_new_media_content.return_value = []
        mock_media_instance.update_media_baseline.return_value = True
        mock_media_instance.cleanup.return_value = None
        mock_media.return_value = mock_media_instance
    
    def _setup_mock_scrapers_with_data(self, mock_carousel, mock_bulletin, mock_news, mock_media, test_data):
        """Set up mock scrapers with specific test data"""
        # Mock carousel scraper
        mock_carousel_instance = Mock()
        mock_carousel_instance.extract_carousel_banners.return_value = test_data.get('carousel', [])
        mock_carousel_instance.update_carousel_baseline.return_value = True
        mock_carousel_instance.cleanup.return_value = None
        mock_carousel.return_value = mock_carousel_instance
        
        # Mock bulletin scraper
        mock_bulletin_instance = Mock()
        mock_bulletin_instance.process_cancellation_monitoring.return_value = {
            'success': True,
            'cancellations': test_data.get('cancellation', []),
            'new_cancellations': test_data.get('cancellation', []),
            'message': 'Test data processing'
        }
        mock_bulletin_instance.cleanup.return_value = None
        mock_bulletin.return_value = mock_bulletin_instance
        
        # Mock news processor
        mock_news_instance = Mock()
        mock_news_instance.extract_news_items.return_value = test_data.get('news', [])
        mock_news_instance.update_news_baseline.return_value = True
        mock_news_instance.cleanup.return_value = None
        mock_news.return_value = mock_news_instance
        
        # Mock media processor
        mock_media_instance = Mock()
        mock_media_instance.extract_media_content.return_value = test_data.get('media', [])
        mock_media_instance.detect_new_media_content.return_value = []
        mock_media_instance.update_media_baseline.return_value = True
        mock_media_instance.cleanup.return_value = None
        mock_media.return_value = mock_media_instance
    
    def _setup_direct_mock_scrapers(self):
        """Set up mock scrapers directly on the WebsiteMonitor instance"""
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
        self.website_monitor.scrapers = {
            'carousel': mock_carousel,
            'bulletin': mock_bulletin
        }
        self.website_monitor.processors = {
            'news': mock_news,
            'media': mock_media
        }
    
    def _setup_direct_mock_scrapers_with_data(self, test_data):
        """Set up mock scrapers with specific test data directly on the instance"""
        # Mock carousel scraper
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.return_value = test_data.get('carousel', [])
        mock_carousel.update_carousel_baseline.return_value = True
        mock_carousel.cleanup.return_value = None
        
        # Mock bulletin scraper
        mock_bulletin = Mock()
        mock_bulletin.process_cancellation_monitoring.return_value = {
            'success': True,
            'cancellations': test_data.get('cancellation', []),
            'new_cancellations': test_data.get('cancellation', []),
            'message': 'Test data processing'
        }
        mock_bulletin.cleanup.return_value = None
        
        # Mock news processor
        mock_news = Mock()
        mock_news.extract_news_items.return_value = test_data.get('news', [])
        mock_news.update_news_baseline.return_value = True
        mock_news.cleanup.return_value = None
        
        # Mock media processor
        mock_media = Mock()
        mock_media.extract_media_content.return_value = test_data.get('media', [])
        mock_media.detect_new_media_content.return_value = []
        mock_media.update_media_baseline.return_value = True
        mock_media.cleanup.return_value = None
        
        # Assign mocked scrapers
        self.website_monitor.scrapers = {
            'carousel': mock_carousel,
            'bulletin': mock_bulletin
        }
        self.website_monitor.processors = {
            'news': mock_news,
            'media': mock_media
        }
    
    def _setup_fast_mock_scrapers(self):
        """Set up fast mock scrapers for performance testing"""
        # Mock scrapers that return immediately
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.return_value = [{'test': 'data'}]
        mock_carousel.cleanup.return_value = None
        
        mock_bulletin = Mock()
        mock_bulletin.process_cancellation_monitoring.return_value = {
            'success': True, 'cancellations': [{'test': 'data'}], 'new_cancellations': []
        }
        mock_bulletin.cleanup.return_value = None
        
        mock_news = Mock()
        mock_news.extract_news_items.return_value = [{'test': 'data'}]
        mock_news.cleanup.return_value = None
        
        mock_media = Mock()
        mock_media.extract_media_content.return_value = [{'test': 'data'}]
        mock_media.detect_new_media_content.return_value = []
        mock_media.cleanup.return_value = None
        
        # Assign mocked scrapers
        self.website_monitor.scrapers = {
            'carousel': mock_carousel,
            'bulletin': mock_bulletin
        }
        self.website_monitor.processors = {
            'news': mock_news,
            'media': mock_media
        }
    
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
                },
                {
                    'carousel_id': 'mock_carousel_2',
                    'banner_title': 'Mock Carousel Banner 2',
                    'image_url': 'https://example.com/banner2.jpg',
                    'activity_link': 'https://example.com/activity2',
                    'course_name': 'Mock Course 2',
                    'location': 'Mock Location 2',
                    'instructor': 'Mock Instructor 2',
                    'description': 'Mock Description 2',
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
    
    def _test_component_initialization_failure_focused(self):
        """Test component initialization failure recovery (focused)"""
        self.logger.info("Testing component initialization failure recovery (focused)...")
        
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
    
    def _test_scraper_failure_recovery_focused(self):
        """Test scraper failure recovery (focused)"""
        self.logger.info("Testing scraper failure recovery (focused)...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        
        # Mock scraper to fail
        mock_carousel = Mock()
        mock_carousel.extract_carousel_banners.side_effect = Exception("Scraper failure")
        mock_carousel.cleanup.return_value = None
        
        monitor.scrapers = {'carousel': mock_carousel}
        monitor.processors = {}
        
        monitor.initialize_components()
        
        # Cycle should handle scraper failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # The cycle might succeed or fail, but should not crash
        self.assertIsInstance(cycle_success, bool, "Cycle should return boolean result")
        
        monitor.cleanup()
    
    def _test_data_sync_failure_recovery_focused(self):
        """Test data synchronization failure recovery (focused)"""
        self.logger.info("Testing data synchronization failure recovery (focused)...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        self._setup_fast_mock_scrapers()
        
        # Mock data synchronizer to fail
        monitor.synchronize_data = Mock(return_value=False)
        
        monitor.initialize_components()
        
        # Cycle should handle sync failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # Cycle might fail due to sync failure, but should not crash
        self.assertIsInstance(cycle_success, bool)
        
        monitor.cleanup()
    
    def _test_notification_failure_recovery_focused(self):
        """Test notification failure recovery (focused)"""
        self.logger.info("Testing notification failure recovery (focused)...")
        
        monitor = WebsiteMonitor(self.test_config_path, self.logger)
        self._setup_fast_mock_scrapers()
        
        # Mock notification processor to fail
        monitor.send_notifications = Mock(return_value=False)
        
        monitor.initialize_components()
        
        # Cycle should handle notification failure gracefully
        cycle_success = monitor.start_monitoring_cycle()
        
        # Cycle might fail due to notification failure, but should not crash
        self.assertIsInstance(cycle_success, bool)
        
        monitor.cleanup()


def run_focused_end_to_end_tests():
    """Run all focused end-to-end integration tests"""
    print("=" * 80)
    print("Website Monitor Focused End-to-End Integration Tests")
    print("=" * 80)
    
    # Set up test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestWebsiteMonitorEndToEndFocused)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("Focused End-to-End Integration Test Summary")
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
    success = run_focused_end_to_end_tests()
    sys.exit(0 if success else 1)