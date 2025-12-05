"""
Test module for EmailSender class

Basic tests to verify email sender functionality without actually sending emails.
"""

import unittest
import logging
import tempfile
import os
from unittest.mock import patch, MagicMock
from email_sender import EmailSender


class TestEmailSender(unittest.TestCase):
    """Test cases for EmailSender class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.smtp_config = {
            'smtp_server': 'smtp.test.com',
            'smtp_port': 587,
            'username': 'test@test.com',
            'password': 'test_password'
        }
        self.logger = logging.getLogger('test')
        self.email_sender = EmailSender(**self.smtp_config, logger=self.logger)
    
    def test_init_valid_config(self):
        """Test EmailSender initialization with valid configuration"""
        sender = EmailSender(**self.smtp_config)
        self.assertEqual(sender.smtp_server, 'smtp.test.com')
        self.assertEqual(sender.smtp_port, 587)
        self.assertEqual(sender.username, 'test@test.com')
        self.assertEqual(sender.password, 'test_password')
    
    def test_init_invalid_config(self):
        """Test EmailSender initialization with invalid configuration"""
        with self.assertRaises(ValueError):
            EmailSender('', 587, 'test@test.com', 'password')
    
    def test_create_message_basic(self):
        """Test basic email message creation"""
        recipients = ['test1@test.com', 'test2@test.com']
        subject = 'Test Subject'
        body = 'Test body content'
        
        message = self.email_sender.create_message(recipients, subject, body)
        
        self.assertEqual(message['From'], 'test@test.com')
        self.assertEqual(message['To'], 'test1@test.com, test2@test.com')
        self.assertEqual(message['Subject'], 'Test Subject')
    
    def test_create_message_empty_recipients(self):
        """Test message creation with empty recipients list"""
        with self.assertRaises(ValueError):
            self.email_sender.create_message([], 'Subject', 'Body')
    
    def test_attach_file_word_document(self):
        """Test attaching Word document"""
        # Create temporary Word file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(b'Test Word content')
            temp_path = temp_file.name
        
        try:
            recipients = ['test@test.com']
            message = self.email_sender.create_message(recipients, 'Test', 'Body', [temp_path])
            
            # Check that attachment was added
            attachments = [part for part in message.walk() if part.get_content_disposition() == 'attachment']
            self.assertEqual(len(attachments), 1)
            
        finally:
            os.unlink(temp_path)
    
    def test_attach_file_excel_document(self):
        """Test attaching Excel document"""
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file.write(b'Test Excel content')
            temp_path = temp_file.name
        
        try:
            recipients = ['test@test.com']
            message = self.email_sender.create_message(recipients, 'Test', 'Body', [temp_path])
            
            # Check that attachment was added
            attachments = [part for part in message.walk() if part.get_content_disposition() == 'attachment']
            self.assertEqual(len(attachments), 1)
            
        finally:
            os.unlink(temp_path)
    
    def test_attach_nonexistent_file(self):
        """Test attaching non-existent file"""
        recipients = ['test@test.com']
        
        with self.assertRaises(FileNotFoundError):
            self.email_sender.create_message(recipients, 'Test', 'Body', ['nonexistent.docx'])
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        recipients = ['test@test.com']
        subject = 'Test Subject'
        body = 'Test body'
        
        result = self.email_sender.send_email(recipients, subject, body)
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_test_connection_success(self, mock_smtp):
        """Test successful connection test"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_sender.test_connection()
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'test_password')


if __name__ == '__main__':
    # Set up logging for tests
    logging.basicConfig(level=logging.DEBUG)
    
    # Run tests
    unittest.main()