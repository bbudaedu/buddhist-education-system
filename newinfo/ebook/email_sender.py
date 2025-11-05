"""
Email Sender Module for New Book Summary System

This module provides email functionality for sending book summaries
with Word and Excel attachments to specified recipients.
"""

import smtplib
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional
import logging


class EmailSender:
    """
    Email sender class for sending book summaries with attachments.
    
    Handles SMTP connection, message creation, file attachments,
    and email delivery with proper error handling and logging.
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, logger: Optional[logging.Logger] = None):
        """
        Initialize EmailSender with SMTP settings.
        
        Args:
            smtp_server (str): SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port (int): SMTP server port (e.g., 587 for TLS)
            username (str): SMTP username/email address
            password (str): SMTP password or app-specific password
            logger (Optional[logging.Logger]): Logger instance for logging operations
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate SMTP settings
        if not all([smtp_server, smtp_port, username, password]):
            raise ValueError("All SMTP settings (server, port, username, password) must be provided")
        
        self.logger.info(f"EmailSender initialized with server: {smtp_server}:{smtp_port}")
    
    def create_message(self, recipients: List[str], subject: str, body: str, attachment_paths: Optional[List[str]] = None) -> MIMEMultipart:
        """
        Create MIME multipart email message with optional attachments.
        
        Args:
            recipients (List[str]): List of recipient email addresses
            subject (str): Email subject line
            body (str): Email body text content
            attachment_paths (Optional[List[str]]): List of file paths to attach
            
        Returns:
            MIMEMultipart: Configured email message ready to send
            
        Raises:
            ValueError: If recipients list is empty or invalid
            FileNotFoundError: If attachment file doesn't exist
        """
        if not recipients:
            raise ValueError("Recipients list cannot be empty")
        
        # Create multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        self.logger.info(f"Creating email message - Subject: {subject}, Recipients: {len(recipients)}")
        
        # Add email body text
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        self.logger.debug("Email body text attached")
        
        # Add attachments if provided
        if attachment_paths:
            for attachment_path in attachment_paths:
                if not os.path.exists(attachment_path):
                    raise FileNotFoundError(f"Attachment file not found: {attachment_path}")
                
                self._attach_file(msg, attachment_path)
                self.logger.info(f"Attached file: {os.path.basename(attachment_path)}")
        
        return msg
    
    def _attach_file(self, message: MIMEMultipart, file_path: str) -> None:
        """
        Attach a single file to the email message with appropriate MIME type.
        
        Args:
            message (MIMEMultipart): Email message to attach file to
            file_path (str): Path to the file to attach
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file cannot be read
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Determine MIME subtype based on file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            filename = os.path.basename(file_path)
            
            if file_ext == '.docx':
                # Microsoft Word document
                subtype = 'vnd.openxmlformats-officedocument.wordprocessingml.document'
                self.logger.debug(f"Attaching Word document: {filename}")
            elif file_ext == '.xlsx':
                # Microsoft Excel spreadsheet
                subtype = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                self.logger.debug(f"Attaching Excel spreadsheet: {filename}")
            elif file_ext == '.pdf':
                # PDF document
                subtype = 'pdf'
                self.logger.debug(f"Attaching PDF document: {filename}")
            else:
                # Generic binary file
                subtype = 'octet-stream'
                self.logger.debug(f"Attaching generic file: {filename}")
            
            # Create attachment
            attachment = MIMEApplication(file_data, _subtype=subtype)
            attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=filename
            )
            
            # Attach to message
            message.attach(attachment)
            self.logger.info(f"Successfully attached file: {filename} ({len(file_data)} bytes)")
            
        except IOError as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            raise IOError(f"Cannot read file {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error attaching file {file_path}: {e}")
            raise
    
    def send_email(self, recipients: List[str], subject: str, body: str, attachment_paths: Optional[List[str]] = None, max_retries: int = 3, retry_delay: int = 30) -> bool:
        """
        Send email with optional attachments to specified recipients with enhanced error handling.
        
        Args:
            recipients (List[str]): List of recipient email addresses
            subject (str): Email subject line
            body (str): Email body text content
            attachment_paths (Optional[List[str]]): List of file paths to attach
            max_retries (int): Maximum number of retry attempts for transient errors
            retry_delay (int): Delay between retries in seconds
            
        Returns:
            bool: True if email sent successfully, False otherwise
            
        Raises:
            smtplib.SMTPException: For SMTP-related errors with detailed messages
            Exception: For other unexpected errors
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retrying email send (attempt {attempt + 1}/{max_retries + 1}) after {retry_delay} seconds...")
                    time.sleep(retry_delay)
                
                # Create email message
                message = self.create_message(recipients, subject, body, attachment_paths)
                
                # Connect to SMTP server and send email
                self.logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
                
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=60) as server:
                    # Set debug level for detailed SMTP logging if needed
                    if self.logger.isEnabledFor(logging.DEBUG):
                        server.set_debuglevel(1)
                    
                    # Enable TLS encryption
                    try:
                        server.starttls()
                        self.logger.debug("TLS encryption enabled")
                    except smtplib.SMTPNotSupportedError as e:
                        self.logger.error(f"TLS not supported by server: {e}")
                        raise smtplib.SMTPException(f"TLS encryption required but not supported: {e}")
                    
                    # Authenticate with credentials
                    try:
                        server.login(self.username, self.password)
                        self.logger.debug("SMTP authentication successful")
                    except smtplib.SMTPAuthenticationError as e:
                        error_msg = f"SMTP authentication failed. Please check your username and password. Error: {e}"
                        self.logger.error(error_msg)
                        raise smtplib.SMTPAuthenticationError(error_msg)
                    
                    # Send email message
                    try:
                        refused_recipients = server.send_message(message)
                        
                        # Check if any recipients were refused
                        if refused_recipients:
                            refused_list = ', '.join(refused_recipients.keys())
                            self.logger.warning(f"Some recipients were refused: {refused_list}")
                            for recipient, (code, msg) in refused_recipients.items():
                                self.logger.warning(f"  {recipient}: {code} - {msg}")
                        
                        # Log success with recipient information
                        successful_recipients = [r for r in recipients if r not in refused_recipients]
                        if successful_recipients:
                            recipient_list = ', '.join(successful_recipients)
                            attachment_count = len(attachment_paths) if attachment_paths else 0
                            self.logger.info(f"Email sent successfully to: {recipient_list}")
                            self.logger.info(f"Subject: {subject}")
                            self.logger.info(f"Attachments: {attachment_count} files")
                            
                            if attachment_paths:
                                for path in attachment_paths:
                                    self.logger.info(f"  - {os.path.basename(path)}")
                            
                            return True
                        else:
                            raise smtplib.SMTPRecipientsRefused("All recipients were refused by the server")
                            
                    except smtplib.SMTPRecipientsRefused as e:
                        error_msg = f"All recipients refused by server. Check email addresses. Error: {e}"
                        self.logger.error(error_msg)
                        raise smtplib.SMTPRecipientsRefused(error_msg)
                    except smtplib.SMTPDataError as e:
                        error_msg = f"SMTP data error. Message may be too large or contain invalid content. Error: {e}"
                        self.logger.error(error_msg)
                        raise smtplib.SMTPDataError(error_msg)
                
            except smtplib.SMTPAuthenticationError as e:
                # Authentication errors are not transient - don't retry
                self.logger.error(f"SMTP authentication failed (not retrying): {e}")
                raise e
                
            except smtplib.SMTPRecipientsRefused as e:
                # Recipient errors are not transient - don't retry
                self.logger.error(f"Recipients refused (not retrying): {e}")
                raise e
                
            except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, 
                    ConnectionRefusedError, OSError) as e:
                # Connection errors - retry
                last_error = e
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    error_msg = f"Failed to connect to SMTP server after {max_retries + 1} attempts. Check server settings and network connection. Last error: {e}"
                    self.logger.error(error_msg)
                    raise smtplib.SMTPConnectError(error_msg)
                continue
                
            except smtplib.SMTPException as e:
                # Other SMTP errors - retry for some, not for others
                error_str = str(e).lower()
                if any(keyword in error_str for keyword in ['timeout', 'temporary', 'busy', '4']):
                    # Transient errors - retry
                    last_error = e
                    self.logger.warning(f"Transient SMTP error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt == max_retries:
                        error_msg = f"SMTP error persisted after {max_retries + 1} attempts: {e}"
                        self.logger.error(error_msg)
                        raise smtplib.SMTPException(error_msg)
                    continue
                else:
                    # Permanent errors - don't retry
                    error_msg = f"Permanent SMTP error: {e}"
                    self.logger.error(error_msg)
                    raise smtplib.SMTPException(error_msg)
                    
            except Exception as e:
                # Unexpected errors
                last_error = e
                self.logger.error(f"Unexpected error sending email (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    error_msg = f"Failed to send email after {max_retries + 1} attempts due to unexpected error: {e}"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)
                continue
        
        # Should not reach here, but just in case
        error_msg = f"Email sending failed after {max_retries + 1} attempts. Last error: {last_error}"
        self.logger.error(error_msg)
        raise Exception(error_msg)
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication without sending email.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info("Testing SMTP connection...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
            self.logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration (replace with actual values)
    smtp_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your_email@gmail.com',
        'password': 'your_app_password'  # Use app-specific password for Gmail
    }
    
    try:
        # Initialize email sender
        email_sender = EmailSender(**smtp_config)
        
        # Test connection
        if email_sender.test_connection():
            print("SMTP connection test passed!")
            
            # Example email sending
            recipients = ['jackyfang@budaedu.org', 'tyguo@budaedu.org']
            subject = '新書簡介 - 2024年10月30日'
            body = """親愛的同仁，

附件為本日新書簡介文件，包含最新出版的佛教教育書籍摘要。

文件包含：
- Word 文件：新書簡介摘要
- Excel 文件：新書詳細資料

請查收。

此郵件由系統自動發送。
"""
            
            # Example with attachments (files must exist)
            attachment_paths = [
                '新書簡介_2024-10-30.docx',
                '新書詳細資料_2024-10-30.xlsx'
            ]
            
            # Send email (uncomment to actually send)
            # success = email_sender.send_email(recipients, subject, body, attachment_paths)
            # print(f"Email sent: {success}")
            
        else:
            print("SMTP connection test failed!")
            
    except Exception as e:
        print(f"Error: {e}")