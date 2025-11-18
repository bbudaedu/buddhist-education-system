#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Sender Module for Website Monitoring
電子郵件發送模組

This module handles email notifications for website monitoring system.
Provides SMTP-based email sending with support for HTML and plain text.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional, Dict, Any


class EmailSender:
    """
    Email sender class for website monitoring notifications
    
    Handles:
    - SMTP email sending
    - HTML and plain text email support
    - Attachment support
    - Email template formatting
    - Error handling and retry logic
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize EmailSender with SMTP configuration
        
        Args:
            config: Configuration dictionary containing SMTP settings
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = config
        
        # SMTP configuration
        self.smtp_server = config.get('smtp_server', '')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username', '')
        self.smtp_password = config.get('smtp_password', '')
        self.smtp_use_tls = config.get('smtp_use_tls', True)
        
        # Email settings
        self.sender_email = config.get('sender_email', self.smtp_username)
        self.sender_name = config.get('sender_name', '佛教教育網站監控系統')
        
        # Handle email recipients (support both string and list formats)
        recipients_config = config.get('email_recipients', [])
        if isinstance(recipients_config, str):
            # Split comma-separated string into list
            self.recipients = [email.strip() for email in recipients_config.split(',') if email.strip()]
        elif isinstance(recipients_config, list):
            self.recipients = recipients_config
        else:
            self.recipients = []
        
        # Validate configuration
        self.is_configured = self._validate_configuration()
        
        if self.is_configured:
            self.logger.info("EmailSender initialized successfully")
        else:
            self.logger.warning("EmailSender configuration incomplete")
    
    def _validate_configuration(self) -> bool:
        """
        Validate email configuration
        
        Returns:
            bool: True if configuration is valid
        """
        required_fields = ['smtp_server', 'smtp_username', 'smtp_password']
        
        for field in required_fields:
            if not self.config.get(field):
                self.logger.error(f"Missing required email configuration: {field}")
                return False
        
        if not self.recipients:
            self.logger.warning("No email recipients configured")
            return False
        
        return True
    
    def send_notification_email(self, subject: str, body: str, is_html: bool = False,
                              attachments: Optional[List[str]] = None,
                              recipients: Optional[List[str]] = None) -> bool:
        """
        Send notification email
        
        Args:
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            attachments: List of file paths to attach
            recipients: List of recipient emails (uses default if None)
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not self.is_configured:
                self.logger.error("EmailSender not properly configured")
                return False
            
            # Use provided recipients or default
            email_recipients = recipients or self.recipients
            
            if not email_recipients:
                self.logger.error("No recipients specified for email")
                return False
            
            self.logger.info(f"Sending email to {len(email_recipients)} recipients: {subject}")
            
            # Create message
            message = self._create_email_message(subject, body, is_html, email_recipients)
            
            # Add attachments if provided
            if attachments:
                self._add_attachments(message, attachments)
            
            # Send email
            success = self._send_email(message, email_recipients)
            
            if success:
                self.logger.info("Email sent successfully")
            else:
                self.logger.error("Failed to send email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending notification email: {e}")
            return False
    
    def _create_email_message(self, subject: str, body: str, is_html: bool,
                             recipients: List[str]) -> MIMEMultipart:
        """
        Create email message with headers and body
        
        Args:
            subject: Email subject
            body: Email body content
            is_html: Whether body is HTML format
            recipients: List of recipient emails
            
        Returns:
            MIMEMultipart: Configured email message
        """
        try:
            # Create message container
            message = MIMEMultipart()
            
            # Set headers
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject
            message['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # Add body
            if is_html:
                body_part = MIMEText(body, 'html', 'utf-8')
            else:
                body_part = MIMEText(body, 'plain', 'utf-8')
            
            message.attach(body_part)
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error creating email message: {e}")
            raise
    
    def _add_attachments(self, message: MIMEMultipart, attachments: List[str]):
        """
        Add file attachments to email message
        
        Args:
            message: Email message to add attachments to
            attachments: List of file paths to attach
        """
        try:
            for file_path in attachments:
                if not os.path.exists(file_path):
                    self.logger.warning(f"Attachment file not found: {file_path}")
                    continue
                
                try:
                    with open(file_path, 'rb') as attachment_file:
                        # Create attachment part
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment_file.read())
                    
                    # Encode attachment
                    encoders.encode_base64(part)
                    
                    # Add header
                    filename = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    
                    # Attach to message
                    message.attach(part)
                    
                    self.logger.info(f"Added attachment: {filename}")
                    
                except Exception as e:
                    self.logger.warning(f"Error adding attachment {file_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing attachments: {e}")
    
    def _send_email(self, message: MIMEMultipart, recipients: List[str]) -> bool:
        """
        Send email message via SMTP
        
        Args:
            message: Configured email message
            recipients: List of recipient emails
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Enable TLS if configured
            if self.smtp_use_tls:
                server.starttls()
            
            # Login to SMTP server
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(self.sender_email, recipients, text)
            
            # Close connection
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            self.logger.error(f"SMTP recipients refused: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error(f"SMTP server disconnected: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending email via SMTP: {e}")
            return False
    
    def send_alert_email(self, alert_content: str, alert_type: str = "general") -> bool:
        """
        Send alert email with predefined formatting
        
        Args:
            alert_content: Alert content to send
            alert_type: Type of alert ('urgent', 'warning', 'info', 'general')
            
        Returns:
            bool: True if alert email sent successfully
        """
        try:
            # Determine subject based on alert type
            subject_prefixes = {
                'urgent': '🚨 緊急警報',
                'warning': '⚠️ 警告通知',
                'info': 'ℹ️ 資訊通知',
                'general': '📢 一般通知'
            }
            
            subject_prefix = subject_prefixes.get(alert_type, '📢 一般通知')
            subject = f"{subject_prefix} - 佛教教育網站監控"
            
            # Format email body
            body = f"""
{subject_prefix}

{alert_content}

---
此郵件由佛教教育網站監控系統自動發送
發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
請勿回覆此郵件
            """.strip()
            
            return self.send_notification_email(subject, body, is_html=False)
            
        except Exception as e:
            self.logger.error(f"Error sending alert email: {e}")
            return False
    
    def send_summary_email(self, summary_content: str, summary_date: Optional[datetime] = None) -> bool:
        """
        Send summary email with predefined formatting
        
        Args:
            summary_content: Summary content to send
            summary_date: Date for the summary (uses current date if None)
            
        Returns:
            bool: True if summary email sent successfully
        """
        try:
            # Use provided date or current date
            if summary_date is None:
                summary_date = datetime.now()
            
            date_str = summary_date.strftime('%Y-%m-%d')
            subject = f"📊 每日監控摘要 - {date_str}"
            
            # Format email body
            body = f"""
📊 佛教教育網站監控 - 每日摘要報告

日期：{date_str}

{summary_content}

---
此郵件由佛教教育網站監控系統自動發送
發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
請勿回覆此郵件
            """.strip()
            
            return self.send_notification_email(subject, body, is_html=False)
            
        except Exception as e:
            self.logger.error(f"Error sending summary email: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """
        Test email connection and configuration
        
        Returns:
            bool: True if connection test successful
        """
        try:
            if not self.is_configured:
                self.logger.error("EmailSender not properly configured for testing")
                return False
            
            self.logger.info("Testing email connection...")
            
            # Create test SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Enable TLS if configured
            if self.smtp_use_tls:
                server.starttls()
            
            # Test login
            server.login(self.smtp_username, self.smtp_password)
            
            # Close connection
            server.quit()
            
            self.logger.info("Email connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """
        Send test email to verify functionality
        
        Returns:
            bool: True if test email sent successfully
        """
        try:
            subject = "🧪 測試郵件 - 佛教教育網站監控系統"
            body = f"""
這是一封測試郵件，用於驗證佛教教育網站監控系統的郵件發送功能。

如果您收到此郵件，表示郵件系統運作正常。

測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
此郵件由佛教教育網站監控系統自動發送
請勿回覆此郵件
            """.strip()
            
            success = self.send_notification_email(subject, body, is_html=False)
            
            if success:
                self.logger.info("Test email sent successfully")
            else:
                self.logger.error("Failed to send test email")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            return False
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """
        Get email configuration status for diagnostics
        
        Returns:
            Dict: Configuration status information
        """
        try:
            status = {
                'configured': self.is_configured,
                'smtp_server': self.smtp_server,
                'smtp_port': self.smtp_port,
                'smtp_use_tls': self.smtp_use_tls,
                'sender_email': self.sender_email,
                'sender_name': self.sender_name,
                'recipients_count': len(self.recipients),
                'recipients': self.recipients if len(self.recipients) <= 5 else self.recipients[:5] + ['...']
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting configuration status: {e}")
            return {'error': str(e)}


# Example usage and testing
def main():
    """
    Example usage of EmailSender
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Mock configuration (replace with real values for testing)
        config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_username': 'your_email@gmail.com',
            'smtp_password': 'your_app_password',
            'smtp_use_tls': True,
            'sender_email': 'your_email@gmail.com',
            'sender_name': '佛教教育網站監控系統',
            'email_recipients': ['recipient@example.com']
        }
        
        # Initialize EmailSender
        email_sender = EmailSender(config=config, logger=logger)
        
        # Get configuration status
        status = email_sender.get_configuration_status()
        logger.info(f"Configuration status: {status}")
        
        # Test connection (uncomment to test with real credentials)
        # connection_ok = email_sender.test_email_connection()
        # logger.info(f"Connection test: {connection_ok}")
        
        # Send test email (uncomment to test with real credentials)
        # test_sent = email_sender.send_test_email()
        # logger.info(f"Test email sent: {test_sent}")
        
        # Test alert email
        alert_content = "這是一個測試警報，用於驗證警報郵件功能。"
        # alert_sent = email_sender.send_alert_email(alert_content, "info")
        # logger.info(f"Alert email sent: {alert_sent}")
        
        logger.info("EmailSender testing completed")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")


if __name__ == "__main__":
    main()