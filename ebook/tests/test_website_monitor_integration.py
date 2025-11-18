#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test for Website Monitor Orchestrator
網站監控協調器整合測試

This script tests the integration of all WebsiteMonitor components
to ensure they work together correctly.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import monitoring components
from monitoring_controller import MonitoringController
from config_manager import ConfigManager


def setup_logging():
    """Set up logging for the integration test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('website_monitor_integration_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def test_config_manager(logger):
    """Test ConfigManager functionality"""
    logger.info("Testing ConfigManager...")
    
    try:
        # Create test config from template
        import shutil
        if os.path.exists("test_config_template.json"):
            shutil.copy("test_config_template.json", "test_config.json")
        
        # Initialize ConfigManager
        config_manager = ConfigManager("test_config.json", logger)
        
        # Test creating default monitoring config
        success = config_manager.create_default_monitoring_config()
        logger.info(f"Default config creation: {success}")
        
        # Test getting monitoring config
        monitoring_config = config_manager.get_website_monitoring_config()
        logger.info(f"Monitoring config loaded: {len(monitoring_config)} sections")
        
        # Test validation
        is_valid = config_manager.validate_monitoring_config()
        logger.info(f"Config validation: {is_valid}")
        
        # Test config summary
        summary = config_manager.get_monitoring_config_summary()
        logger.info(f"Config summary: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"ConfigManager test failed: {e}")
        return False


def test_monitoring_controller(logger):
    """Test MonitoringController functionality"""
    logger.info("Testing MonitoringController...")
    
    controller = None
    try:
        # Create test config from template
        import shutil
        if os.path.exists("test_config_template.json"):
            shutil.copy("test_config_template.json", "test_config.json")
        
        # Initialize MonitoringController
        controller = MonitoringController("test_config.json", logger)
        
        # Test system initialization
        success, message = controller.initialize_system()
        logger.info(f"System initialization: {success} - {message}")
        
        if not success:
            logger.error("System initialization failed, skipping further tests")
            return False
        
        # Test getting system status
        status = controller.get_system_status()
        logger.info(f"System status retrieved: {status.get('system_initialized', False)}")
        
        # Test configuration update
        config_updates = {
            'chrome_devtools': {
                'enabled': False,  # Keep disabled for testing
                'headless': True
            }
        }
        success, message = controller.update_configuration(config_updates)
        logger.info(f"Configuration update: {success} - {message}")
        
        # Test content type management
        success, message = controller.enable_content_type('carousel')
        logger.info(f"Enable carousel: {success} - {message}")
        
        success, message = controller.disable_content_type('media')
        logger.info(f"Disable media: {success} - {message}")
        
        # Test performance report
        report = controller.get_performance_report()
        logger.info(f"Performance report generated: {len(report)} metrics")
        
        return True
        
    except Exception as e:
        logger.error(f"MonitoringController test failed: {e}")
        return False
    finally:
        if controller:
            controller.cleanup_system()


def test_component_imports(logger):
    """Test that all components can be imported successfully"""
    logger.info("Testing component imports...")
    
    try:
        # Test importing all main components
        from website_monitor import WebsiteMonitor
        from enhanced_data_synchronizer import EnhancedDataSynchronizer
        from notification_processor import NotificationProcessor
        from document_generator import DocumentGenerator
        from email_sender import EmailSender
        
        logger.info("✓ All main components imported successfully")
        
        # Test importing specialized scrapers
        from carousel_scraper import CarouselScraper
        from bulletin_scraper import BulletinScraper
        from news_processor import NewsProcessor
        from media_processor import MediaProcessor
        
        logger.info("✓ All specialized scrapers imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"Import test failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import test: {e}")
        return False


def test_basic_functionality(logger):
    """Test basic functionality without actual web scraping"""
    logger.info("Testing basic functionality...")
    
    try:
        # Test DocumentGenerator
        from document_generator import DocumentGenerator
        
        doc_gen = DocumentGenerator("test_output", logger)
        logger.info("✓ DocumentGenerator initialized")
        
        # Test EmailSender (without actual sending)
        from email_sender import EmailSender
        
        email_config = {
            'smtp_server': 'test.smtp.com',
            'smtp_username': 'test@example.com',
            'smtp_password': 'test_password',
            'email_recipients': ['recipient@example.com']
        }
        
        email_sender = EmailSender(email_config, logger)
        status = email_sender.get_configuration_status()
        logger.info(f"✓ EmailSender initialized: {status['configured']}")
        
        # Test NotificationProcessor
        from notification_processor import NotificationProcessor
        
        notification_processor = NotificationProcessor(
            config={'line_bot': {'enabled': False}},
            email_sender=None,
            logger=logger
        )
        logger.info("✓ NotificationProcessor initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"Basic functionality test failed: {e}")
        return False


def cleanup_test_files(logger):
    """Clean up test files created during testing"""
    logger.info("Cleaning up test files...")
    
    try:
        test_files = [
            "test_config.json",
            "test_output"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed test file: {file_path}")
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    logger.info(f"Removed test directory: {file_path}")
        
    except Exception as e:
        logger.warning(f"Error cleaning up test files: {e}")


def main():
    """Run integration tests for WebsiteMonitor orchestrator"""
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("Starting WebsiteMonitor Integration Tests")
    logger.info("="*60)
    
    test_results = {}
    
    try:
        # Run all tests
        test_results['imports'] = test_component_imports(logger)
        test_results['config_manager'] = test_config_manager(logger)
        test_results['basic_functionality'] = test_basic_functionality(logger)
        test_results['monitoring_controller'] = test_monitoring_controller(logger)
        
        # Summary
        logger.info("="*60)
        logger.info("Integration Test Results:")
        logger.info("="*60)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"{test_name:20}: {status}")
        
        logger.info("-"*60)
        logger.info(f"Total: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All integration tests PASSED!")
            return True
        else:
            logger.error(f"❌ {total_tests - passed_tests} tests FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"Integration test execution failed: {e}")
        return False
    finally:
        cleanup_test_files(logger)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)