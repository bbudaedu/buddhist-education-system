#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Website Monitor Infrastructure
Tests the basic infrastructure setup for website monitoring

This script tests:
- WebsiteMonitor initialization
- Configuration management
- Chrome DevTools integration setup
- Basic monitoring cycle execution
"""

import os
import sys
import logging
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_monitor import WebsiteMonitor, ContentTypes
from enhanced_config_manager import EnhancedConfigManager


class TestWebsiteMonitorInfrastructure(unittest.TestCase):
    """Test cases for website monitor infrastructure"""
    
    def setUp(self):
        """Set up test environment"""
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Create test configuration
        self.test_config = {
            "gemini_api_key": "test_key",
            "chromedriver_path": "chromedriver-win64\\chromedriver.exe",
            "target_url": "https://www.budaedu.org/#/books/applicable/chinese",
            "baseline_book_title": "Test Book",
            "download_dir": "downloads",
            "website_monitoring": {
                "enabled": True,
                "monitoring_interval": 3600,
                "content_types": {
                    "carousel": {"enabled": True, "url": "https://www.budaedu.org/#/"},
                    "cancellation": {"enabled": True, "url": "https://www.budaedu.org/#/bulletins/course-cancel"},
                    "news": {"enabled": True, "url": "https://www.budaedu.org/#/bulletins/"},
                    "media": {"enabled": True, "url": "https://www.budaedu.org/#/series/live-streaming"}
                },
                "chrome_devtools": {
                    "enabled": False,
                    "headless": True,
                    "timeout": 30
                },
                "data_sync": {
                    "excel_output_dir": "generated_documents/website_monitoring",
                    "mysql_batch_size": 100,
                    "backup_enabled": True
                },
                "notifications": {
                    "line_enabled": True,
                    "email_enabled": True,
                    "immediate_alerts": ["cancellation"],
                    "daily_summary": ["carousel", "news", "media"]
                }
            }
        }
    
    def test_website_monitor_initialization(self):
        """Test WebsiteMonitor initialization"""
        try:
            monitor = WebsiteMonitor(self.test_config, self.logger)
            
            # Check basic attributes
            self.assertIsNotNone(monitor.config)
            self.assertIsNotNone(monitor.logger)
            self.assertIsNotNone(monitor.config_manager)
            self.assertIsInstance(monitor.scrapers, dict)
            
            # Check configuration parsing
            self.assertEqual(monitor.monitoring_config, self.test_config['website_monitoring'])
            self.assertEqual(monitor.content_types_config, self.test_config['website_monitoring']['content_types'])
            
            self.logger.info("✓ WebsiteMonitor 初始化測試通過")
            
        except Exception as e:
            self.fail(f"WebsiteMonitor 初始化失敗: {e}")
    
    def test_content_type_configuration(self):
        """Test content type configuration methods"""
        try:
            monitor = WebsiteMonitor(self.test_config, self.logger)
            
            # Test content type enablement
            self.assertTrue(monitor.is_content_type_enabled(ContentTypes.CAROUSEL))
            self.assertTrue(monitor.is_content_type_enabled(ContentTypes.CANCELLATION))
            self.assertTrue(monitor.is_content_type_enabled(ContentTypes.NEWS))
            self.assertTrue(monitor.is_content_type_enabled(ContentTypes.MEDIA))
            
            # Test URL retrieval
            self.assertEqual(monitor.get_content_type_url(ContentTypes.CAROUSEL), "https://www.budaedu.org/#/")
            self.assertEqual(monitor.get_content_type_url(ContentTypes.CANCELLATION), "https://www.budaedu.org/#/bulletins/course-cancel")
            self.assertEqual(monitor.get_content_type_url(ContentTypes.NEWS), "https://www.budaedu.org/#/bulletins/")
            self.assertEqual(monitor.get_content_type_url(ContentTypes.MEDIA), "https://www.budaedu.org/#/series/live-streaming")
            
            self.logger.info("✓ 內容類型配置測試通過")
            
        except Exception as e:
            self.fail(f"內容類型配置測試失敗: {e}")
    
    def test_chrome_devtools_setup(self):
        """Test Chrome DevTools setup"""
        try:
            monitor = WebsiteMonitor(self.test_config, self.logger)
            
            # Test Chrome DevTools setup (should succeed even if disabled)
            result = monitor.setup_chrome_devtools()
            self.assertTrue(result)
            
            # Test with Chrome DevTools enabled
            enabled_config = self.test_config.copy()
            enabled_config['website_monitoring']['chrome_devtools']['enabled'] = True
            
            monitor_enabled = WebsiteMonitor(enabled_config, self.logger)
            result_enabled = monitor_enabled.setup_chrome_devtools()
            self.assertTrue(result_enabled)
            
            self.logger.info("✓ Chrome DevTools 設定測試通過")
            
        except Exception as e:
            self.fail(f"Chrome DevTools 設定測試失敗: {e}")
    
    @patch('website_monitor.BookScraper')
    def test_base_scraper_initialization(self, mock_book_scraper):
        """Test base scraper initialization"""
        try:
            # Mock BookScraper
            mock_scraper_instance = Mock()
            mock_book_scraper.return_value = mock_scraper_instance
            
            monitor = WebsiteMonitor(self.test_config, self.logger)
            
            # Test base scraper initialization
            result = monitor.initialize_base_scraper()
            self.assertTrue(result)
            self.assertIsNotNone(monitor.base_scraper)
            
            # Verify BookScraper was called with correct parameters
            mock_book_scraper.assert_called_once_with(
                self.test_config['chromedriver_path'],
                self.test_config['download_dir'],
                monitor.logger
            )
            
            self.logger.info("✓ 基礎 BookScraper 初始化測試通過")
            
        except Exception as e:
            self.fail(f"基礎 BookScraper 初始化測試失敗: {e}")
    
    def test_enhanced_config_manager(self):
        """Test EnhancedConfigManager functionality"""
        try:
            # Create temporary config file for testing
            test_config_path = "test_config.json"
            
            # Clean up any existing test config
            if os.path.exists(test_config_path):
                os.remove(test_config_path)
            
            try:
                # Test with config template
                import json
                with open(test_config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.test_config, f, ensure_ascii=False, indent=2)
                
                config_manager = EnhancedConfigManager(test_config_path, self.logger)
                
                # Test website monitoring configuration
                self.assertTrue(config_manager.is_website_monitoring_enabled())
                self.assertFalse(config_manager.is_chrome_devtools_enabled())
                
                # Test content type configuration
                self.assertTrue(config_manager.is_content_type_enabled('carousel'))
                self.assertEqual(config_manager.get_content_type_url('carousel'), "https://www.budaedu.org/#/")
                
                # Test baseline management
                result = config_manager.update_content_type_baseline('carousel', 'test_baseline')
                self.assertTrue(result)
                self.assertEqual(config_manager.get_content_type_baseline('carousel'), 'test_baseline')
                
                # Test configuration validation
                self.assertTrue(config_manager.validate_website_monitoring_config())
                
                self.logger.info("✓ EnhancedConfigManager 測試通過")
                
            finally:
                # Clean up test config file
                if os.path.exists(test_config_path):
                    os.remove(test_config_path)
                    
        except Exception as e:
            self.fail(f"EnhancedConfigManager 測試失敗: {e}")
    
    @patch('website_monitor.BookScraper')
    def test_monitoring_cycle_structure(self, mock_book_scraper):
        """Test monitoring cycle structure without actual web scraping"""
        try:
            # Mock BookScraper and its methods
            mock_scraper_instance = Mock()
            mock_scraper_instance.setup_driver.return_value = True
            mock_scraper_instance.navigate_to_website.return_value = True
            mock_scraper_instance.wait_for_page_load.return_value = True
            mock_scraper_instance.cleanup.return_value = None
            mock_book_scraper.return_value = mock_scraper_instance
            
            monitor = WebsiteMonitor(self.test_config, self.logger)
            
            # Mock the content processing methods to return empty lists
            monitor.process_carousel_content = Mock(return_value=[])
            monitor.process_bulletin_content = Mock(return_value=[])
            monitor.process_news_content = Mock(return_value=[])
            monitor.process_media_content = Mock(return_value=[])
            monitor.synchronize_data = Mock(return_value=True)
            monitor.send_notifications = Mock(return_value=True)
            
            # Test monitoring cycle execution
            result = monitor.start_monitoring_cycle()
            self.assertTrue(result)
            
            # Verify that all content processing methods were called
            monitor.process_carousel_content.assert_called_once()
            monitor.process_bulletin_content.assert_called_once()
            monitor.process_news_content.assert_called_once()
            monitor.process_media_content.assert_called_once()
            
            # Verify scraper methods were called
            mock_scraper_instance.setup_driver.assert_called_once()
            mock_scraper_instance.cleanup.assert_called_once()
            
            self.logger.info("✓ 監控週期結構測試通過")
            
        except Exception as e:
            self.fail(f"監控週期結構測試失敗: {e}")


def run_infrastructure_tests():
    """Run all infrastructure tests"""
    print("=" * 60)
    print("Website Monitor Infrastructure Tests")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2, exit=False)


def run_manual_test():
    """Run manual test of WebsiteMonitor"""
    print("=" * 60)
    print("Manual Website Monitor Test")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Test with actual configuration
        config_manager = EnhancedConfigManager(logger=logger)
        config = config_manager.get_config()
        
        logger.info("測試 WebsiteMonitor 初始化...")
        monitor = WebsiteMonitor(config, logger)
        
        logger.info("測試配置驗證...")
        is_valid = config_manager.validate_website_monitoring_config()
        logger.info(f"配置驗證結果: {'通過' if is_valid else '失敗'}")
        
        logger.info("測試內容類型配置...")
        content_types = ['carousel', 'cancellation', 'news', 'media']
        for content_type in content_types:
            enabled = monitor.is_content_type_enabled(content_type)
            url = monitor.get_content_type_url(content_type)
            logger.info(f"{content_type}: 啟用={enabled}, URL={url}")
        
        logger.info("測試 Chrome DevTools 設定...")
        devtools_result = monitor.setup_chrome_devtools()
        logger.info(f"Chrome DevTools 設定結果: {'成功' if devtools_result else '失敗'}")
        
        logger.info("✓ 手動測試完成")
        
    except Exception as e:
        logger.error(f"手動測試失敗: {e}", exc_info=True)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        run_manual_test()
    else:
        run_infrastructure_tests()