#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Notification Integration
通知整合單元測試

Tests notification generation, formatting, and delivery for all content types
including carousel, cancellation, news, and media content.
"""

import os
import sys
import unittest
import logging
from datetime import datetime, date
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification_processor import NotificationProcessor
from website_notification_sender import WebsiteNotificationSender
from email_sender import EmailSender


class TestNotificationGeneration(unittest.TestCase):
    """Test notification generation for all content types"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test_notification')
        self.logger.setLevel(logging.INFO)
        
        # Mock configuration
        self.config = {
            'line_bot': {'enabled': False},
            'email': {'enabled': True},
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'smtp_username': 'test@test.com',
            'smtp_password': 'test_password',
            'email_recipients': ['recipient@test.com']
        }
        
        # Create mock email sender
        self.mock_email_sender = Mock(spec=EmailSender)
        self.mock_email_sender.send_notification_email = Mock(return_value=True)
        
        # Initialize notification processor
        self.processor = NotificationProcessor(
            config=self.config,
            email_sender=self.mock_email_sender,
            logger=self.logger
        )
    
    def test_carousel_notification_generation(self):
        """Test notification generation for carousel content"""
        # Arrange
        carousel_items = [
            {
                'content_type': 'carousel',
                'carousel_id': 'carousel_001',
                'banner_title': '佛學講座',
                'course_name': '心經導讀',
                'instructor': '釋慧空法師',
                'location': '台北講堂',
                'description': '深入淺出講解心經要義',
                'extraction_timestamp': datetime.now()
            }
        ]
        
        # Act
        result = self.processor.send_immediate_alerts(carousel_items)
        
        # Assert
        self.assertTrue(result, "Carousel notification should be generated successfully")
        self.mock_email_sender.send_notification_email.assert_called_once()
    
    def test_cancellation_notification_generation(self):
        """Test notification generation for course cancellation content"""
        # Arrange
        cancellation_items = [
            {
                'content_type': 'cancellation',
                'cancellation_id': 'cancel_001',
                'course_name': '禪修課程',
                'cancellation_date': date.today(),
                'instructor_name': '釋慧空法師',
                'extraction_timestamp': datetime.now()
            }
        ]
        
        # Act
        result = self.processor.send_immediate_alerts(cancellation_items)
        
        # Assert
        self.assertTrue(result, "Cancellation notification should be generated successfully")
        self.mock_email_sender.send_notification_email.assert_called_once()
    
    def test_news_notification_generation(self):
        """Test notification generation for news announcement content"""
        # Arrange
        news_items = [
            {
                'content_type': 'news',
                'announcement_id': 'news_001',
                'title': '重要公告：課程調整通知',
                'publication_date': date.today(),
                'content': '因應疫情調整，部分課程改為線上進行。詳情請參閱官網。',
                'extraction_timestamp': datetime.now()
            }
        ]
        
        # Act
        result = self.processor.send_immediate_alerts(news_items)
        
        # Assert
        self.assertTrue(result, "News notification should be generated successfully")
        self.mock_email_sender.send_notification_email.assert_called_once()
    
    def test_media_notification_generation(self):
        """Test notification generation for multimedia content"""
        # Arrange
        media_items = [
            {
                'content_type': 'media',
                'media_id': 'media_001',
                'course_title': '佛法概論',
                'speaker_name': '釋慧空法師',
                'start_date': date.today(),
                'redirect_url': 'https://example.com/video/001',
                'media_type': 'video',
                'extraction_timestamp': datetime.now()
            }
        ]
        
        # Act
        result = self.processor.process_daily_summary(media_items)
        
        # Assert
        self.assertTrue(result, "Media notification should be generated successfully")
        self.mock_email_sender.send_notification_email.assert_called_once()
    
    def test_mixed_content_notification_generation(self):
        """Test notification generation for mixed content types"""
        # Arrange
        mixed_items = [
            {
                'content_type': 'carousel',
                'banner_title': '新課程',
                'course_name': '金剛經',
                'instructor': '法師A',
                'extraction_timestamp': datetime.now()
            },
            {
                'content_type': 'news',
                'title': '公告',
                'publication_date': date.today(),
                'content': '測試內容',
                'extraction_timestamp': datetime.now()
            }
        ]
        
        # Act
        result = self.processor.process_daily_summary(mixed_items)
        
        # Assert
        self.assertTrue(result, "Mixed content notification should be generated successfully")
        self.mock_email_sender.send_notification_email.assert_called_once()


class TestNotificationFormatting(unittest.TestCase):
    """Test notification formatting for LINE and email"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test_formatting')
        self.logger.setLevel(logging.INFO)
        
        self.config = {
            'line_bot': {'enabled': False},
            'email': {'enabled': True}
        }
        
        self.mock_email_sender = Mock(spec=EmailSender)
        self.processor = NotificationProcessor(
            config=self.config,
            email_sender=self.mock_email_sender,
            logger=self.logger
        )
    
    def test_email_alert_formatting(self):
        """Test email alert formatting"""
        # Arrange
        alert_items = [
            {
                'content_type': 'cancellation',
                'course_name': '測試課程',
                'cancellation_date': date.today(),
                'instructor_name': '測試講師'
            }
        ]
        
        # Act
        formatted_content = self.processor._format_immediate_alerts(alert_items)
        
        # Assert
        self.assertIsNotNone(formatted_content, "Formatted content should not be None")
        self.assertIn('課程取消通知', formatted_content, "Should contain cancellation notice")
        self.assertIn('測試課程', formatted_content, "Should contain course name")
        self.assertIn('測試講師', formatted_content, "Should contain instructor name")
    
    def test_line_message_formatting(self):
        """Test LINE message formatting"""
        # Arrange
        summary_items = [
            {
                'content_type': 'carousel',
                'banner_title': '新活動',
                'course_name': '測試課程'
            }
        ]
        
        # Act
        summary_content = self.processor._generate_daily_summary(summary_items)
        
        # Assert
        self.assertIsNotNone(summary_content, "Summary content should not be None")
        self.assertIn('輪播橫幅', summary_content, "Should contain carousel label")
        self.assertIn('新活動', summary_content, "Should contain banner title")
    
    def test_carousel_content_formatting(self):
        """Test carousel content formatting"""
        # Arrange
        carousel_items = [
            {
                'content_type': 'carousel',
                'banner_title': '佛學講座',
                'course_name': '心經導讀',
                'instructor': '釋慧空法師'
            }
        ]
        
        # Act
        formatted = self.processor._format_immediate_alerts(carousel_items)
        
        # Assert
        self.assertIn('新活動橫幅', formatted, "Should contain carousel indicator")
        self.assertIn('佛學講座', formatted, "Should contain banner title")
        self.assertIn('心經導讀', formatted, "Should contain course name")
        self.assertIn('釋慧空法師', formatted, "Should contain instructor")
    
    def test_cancellation_content_formatting(self):
        """Test cancellation content formatting"""
        # Arrange
        cancellation_items = [
            {
                'content_type': 'cancellation',
                'course_name': '禪修課程',
                'cancellation_date': date.today(),
                'instructor_name': '釋慧空法師'
            }
        ]
        
        # Act
        formatted = self.processor._format_immediate_alerts(cancellation_items)
        
        # Assert
        self.assertIn('課程取消通知', formatted, "Should contain cancellation indicator")
        self.assertIn('禪修課程', formatted, "Should contain course name")
        self.assertIn('釋慧空法師', formatted, "Should contain instructor")
    
    def test_news_content_formatting(self):
        """Test news content formatting"""
        # Arrange
        news_items = [
            {
                'content_type': 'news',
                'title': '重要公告',
                'publication_date': date.today(),
                'content': '這是一則測試公告內容' * 10  # Long content
            }
        ]
        
        # Act
        formatted = self.processor._format_immediate_alerts(news_items)
        
        # Assert
        self.assertIn('重要公告', formatted, "Should contain news indicator")
        self.assertIn('重要公告', formatted, "Should contain title")
        # Content should be truncated to 100 chars
        self.assertIn('...', formatted, "Long content should be truncated")
    
    def test_media_content_formatting(self):
        """Test media content formatting"""
        # Arrange
        media_items = [
            {
                'content_type': 'media',
                'course_title': '佛法概論',
                'speaker_name': '釋慧空法師'
            }
        ]
        
        # Act
        summary = self.processor._generate_content_type_summary('media', media_items)
        
        # Assert
        self.assertIn('多媒體內容', summary, "Should contain media indicator")
        self.assertIn('佛法概論', summary, "Should contain course title")
        self.assertIn('釋慧空法師', summary, "Should contain speaker name")


class TestNotificationDeliveryErrorHandling(unittest.TestCase):
    """Test notification delivery error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test_error_handling')
        self.logger.setLevel(logging.INFO)
        
        self.config = {
            'line_bot': {'enabled': False},
            'email': {'enabled': True}
        }
    
    def test_email_delivery_failure_handling(self):
        """Test handling of email delivery failures"""
        # Arrange
        mock_email_sender = Mock(spec=EmailSender)
        mock_email_sender.send_notification_email = Mock(return_value=False)
        
        processor = NotificationProcessor(
            config=self.config,
            email_sender=mock_email_sender,
            logger=self.logger
        )
        
        alert_items = [
            {
                'content_type': 'cancellation',
                'course_name': '測試課程',
                'cancellation_date': date.today(),
                'instructor_name': '測試講師'
            }
        ]
        
        # Act
        result = processor.send_immediate_alerts(alert_items)
        
        # Assert
        self.assertFalse(result, "Should return False when email delivery fails")
        mock_email_sender.send_notification_email.assert_called_once()
    
    def test_line_delivery_failure_handling(self):
        """Test handling of LINE delivery failures"""
        # Arrange
        config_with_line = {
            'line_bot': {'enabled': True},
            'email': {'enabled': False}
        }
        
        processor = NotificationProcessor(
            config=config_with_line,
            email_sender=None,
            logger=self.logger
        )
        
        # Mock LINE service to fail
        processor.newbook_service = Mock()
        processor.newbook_service.send_broadcast_message = Mock(return_value=False)
        
        alert_items = [
            {
                'content_type': 'news',
                'title': '測試公告',
                'publication_date': date.today(),
                'content': '測試內容'
            }
        ]
        
        # Act
        result = processor.send_immediate_alerts(alert_items)
        
        # Assert
        self.assertFalse(result, "Should return False when LINE delivery fails")
    
    def test_partial_delivery_failure_handling(self):
        """Test handling when one channel fails but another succeeds"""
        # Arrange
        config_both = {
            'line_bot': {'enabled': True},
            'email': {'enabled': True}
        }
        
        mock_email_sender = Mock(spec=EmailSender)
        mock_email_sender.send_notification_email = Mock(return_value=True)
        
        processor = NotificationProcessor(
            config=config_both,
            email_sender=mock_email_sender,
            logger=self.logger
        )
        
        # Mock LINE service to fail
        processor.newbook_service = Mock()
        processor.newbook_service.send_broadcast_message = Mock(return_value=False)
        
        alert_items = [
            {
                'content_type': 'carousel',
                'banner_title': '測試橫幅',
                'course_name': '測試課程',
                'instructor': '測試講師'
            }
        ]
        
        # Act
        result = processor.send_immediate_alerts(alert_items)
        
        # Assert
        self.assertFalse(result, "Should return False when any channel fails")
        mock_email_sender.send_notification_email.assert_called_once()
    
    def test_empty_content_handling(self):
        """Test handling of empty content"""
        # Arrange
        mock_email_sender = Mock(spec=EmailSender)
        
        processor = NotificationProcessor(
            config=self.config,
            email_sender=mock_email_sender,
            logger=self.logger
        )
        
        # Act
        result = processor.send_immediate_alerts([])
        
        # Assert
        self.assertTrue(result, "Should return True for empty content (no-op)")
        mock_email_sender.send_notification_email.assert_not_called()
    
    def test_malformed_content_handling(self):
        """Test handling of malformed content data"""
        # Arrange
        mock_email_sender = Mock(spec=EmailSender)
        mock_email_sender.send_notification_email = Mock(return_value=True)
        
        processor = NotificationProcessor(
            config=self.config,
            email_sender=mock_email_sender,
            logger=self.logger
        )
        
        # Malformed items (missing required fields)
        malformed_items = [
            {
                'content_type': 'unknown',
                # Missing other required fields
            }
        ]
        
        # Act
        result = processor.send_immediate_alerts(malformed_items)
        
        # Assert
        # Should handle gracefully and still attempt to send
        self.assertTrue(result, "Should handle malformed content gracefully")


class TestWebsiteNotificationSender(unittest.TestCase):
    """Test WebsiteNotificationSender integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.logger = logging.getLogger('test_website_sender')
        self.logger.setLevel(logging.INFO)
        
        self.config = {
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'smtp_username': 'test@test.com',
            'smtp_password': 'test_password',
            'email_recipients': 'recipient1@test.com,recipient2@test.com',
            'website_monitoring': {
                'notifications': {
                    'email_enabled': True,
                    'line_enabled': False,
                    'immediate_alerts': ['cancellation'],
                    'daily_summary': ['carousel', 'news', 'media']
                }
            }
        }
    
    @patch('website_notification_sender.EmailSender')
    def test_priority_based_notification_routing(self, mock_email_sender_class):
        """Test priority-based notification routing"""
        # Arrange
        mock_email_instance = Mock()
        mock_email_instance.send_website_monitoring_email = Mock(return_value=True)
        mock_email_sender_class.return_value = mock_email_instance
        
        sender = WebsiteNotificationSender(self.config, self.logger)
        
        content_data = {
            'cancellation': [
                {
                    'course_name': '緊急取消課程',
                    'cancellation_date': date.today(),
                    'instructor_name': '測試講師'
                }
            ],
            'carousel': [
                {
                    'banner_title': '一般橫幅',
                    'course_name': '一般課程'
                }
            ]
        }
        
        # Act
        result = sender.send_notifications(content_data)
        
        # Assert
        self.assertTrue(result, "Should send notifications successfully")
        # Should be called twice: once for immediate, once for regular
        self.assertEqual(mock_email_instance.send_website_monitoring_email.call_count, 2)
    
    @patch('website_notification_sender.EmailSender')
    def test_notification_with_attachments(self, mock_email_sender_class):
        """Test notification sending with file attachments"""
        # Arrange
        mock_email_instance = Mock()
        mock_email_instance.send_website_monitoring_email = Mock(return_value=True)
        mock_email_sender_class.return_value = mock_email_instance
        
        sender = WebsiteNotificationSender(self.config, self.logger)
        
        content_data = {
            'news': [
                {
                    'title': '測試新聞',
                    'publication_date': date.today(),
                    'content': '測試內容'
                }
            ]
        }
        
        attachment_paths = ['test_file1.xlsx', 'test_file2.pdf']
        
        # Act
        result = sender.send_notifications(content_data, attachment_paths)
        
        # Assert
        self.assertTrue(result, "Should send notifications with attachments")
        mock_email_instance.send_website_monitoring_email.assert_called()


def run_tests():
    """Run all notification integration tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationDeliveryErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestWebsiteNotificationSender))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("Running Notification Integration Unit Tests")
    print("=" * 70)
    
    success = run_tests()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ All notification integration tests passed!")
    else:
        print("✗ Some notification integration tests failed!")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
