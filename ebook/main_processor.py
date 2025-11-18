#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Processor Module for New Book Summary System
新書摘要系統的主要處理器模組

This module orchestrates the complete workflow of the new book summary system,
coordinating all modules (scraper, AI processor, document generator, email sender)
and managing the overall processing flow with interruption handling.
"""

import os
import time
import logging
import threading
import json
import smtplib
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

# Import all required modules
from book_scraper import BookScraper
from gemini_processor import GeminiProcessor
from document_generator import DocumentGenerator
from email_sender import EmailSender
from progress_manager import ProgressManager
from config_manager import ConfigManager


class MainProcessor:
    """
    Main orchestrator class that coordinates all modules and manages the complete processing workflow.
    
    Handles:
    - Module initialization and coordination
    - Main processing workflow execution
    - Progress tracking and interruption handling
    - Threading for background execution
    - Error handling and recovery
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize MainProcessor with configuration and all required modules
        
        Args:
            config: Configuration dictionary containing all necessary settings
            logger: Logger instance for logging operations
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Processing state
        self.stop_flag = False
        self.is_running = False
        self.processing_thread = None
        
        # Initialize all modules
        self.scraper = None
        self.ai_processor = None
        self.document_generator = None
        self.email_sender = None
        self.progress_manager = None
        
        # Processing results
        self.processed_books = []
        self.processing_stats = {
            'total_books_found': 0,
            'books_processed': 0,
            'books_failed': 0,
            'pdf_extractions': 0,
            'google_searches': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Status update callback (for UI updates)
        self.status_callback = None
        
        self.logger.info("MainProcessor initialized")
        self._log_configuration()
    
    def _log_configuration(self):
        """Log configuration details (without sensitive information)"""
        self.logger.info("Configuration loaded:")
        self.logger.info(f"  Target URL: {self.config.get('target_url', 'Not set')}")
        self.logger.info(f"  Baseline book: {self.config.get('baseline_book_title', 'Not set')}")
        self.logger.info(f"  Download directory: {self.config.get('download_dir', 'Not set')}")
        self.logger.info(f"  ChromeDriver path: {self.config.get('chromedriver_path', 'Not set')}")
        self.logger.info(f"  Email recipients: {len(self.config.get('email_recipients', '').split(','))} recipients")
        # Don't log sensitive information like API keys or passwords
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """
        Set callback function for status updates (for UI integration)
        
        Args:
            callback: Function to call with status updates
        """
        self.status_callback = callback
        self.logger.debug("Status callback set")
    
    def _update_status(self, message: str):
        """
        Update status and call callback if set
        
        Args:
            message: Status message to log and send to callback
        """
        self.logger.info(message)
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as e:
                self.logger.warning(f"Status callback error: {e}")
    
    def _initialize_modules(self):
        """
        Initialize all modules (scraper, AI processor, document generator, email sender)
        
        Raises:
            Exception: If any module initialization fails
        """
        try:
            self.logger.info("Initializing modules...")
            
            # Initialize BookScraper
            self.scraper = BookScraper(
                chromedriver_path=self.config['chromedriver_path'],
                download_dir=self.config['download_dir'],
                logger=self.logger
            )
            self.logger.info("✓ BookScraper initialized")
            
            # Initialize GeminiProcessor
            self.ai_processor = GeminiProcessor(
                api_key=self.config['gemini_api_key'],
                logger=self.logger
            )
            self.logger.info("✓ GeminiProcessor initialized")
            
            # Initialize DocumentGenerator
            self.document_generator = DocumentGenerator(
                logger=self.logger
            )
            self.logger.info("✓ DocumentGenerator initialized")
            
            # Initialize EmailSender
            self.email_sender = EmailSender(
                config=self.config,
                logger=self.logger
            )
            self.logger.info("✓ EmailSender initialized")
            
            # Initialize ProgressManager
            self.progress_manager = ProgressManager(
                project_name="newbook_summary_email",
                cache_dir=self.config.get('download_dir', '.'),
                logger=self.logger
            )
            self.logger.info("✓ ProgressManager initialized")
            
            # Initialize ConfigManager
            self.config_manager = ConfigManager(logger=self.logger)
            self.logger.info("✓ ConfigManager initialized")
            
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            self.logger.debug("Module initialization error details:", exc_info=True)
            raise
    
    def _cleanup_modules(self):
        """Clean up all module resources"""
        try:
            self.logger.info("Cleaning up modules...")
            
            if self.scraper:
                self.scraper.cleanup()
                self.logger.debug("BookScraper cleaned up")
            
            # Other modules don't require explicit cleanup
            self.logger.info("Module cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Error during module cleanup: {e}")
    
    def should_stop(self) -> bool:
        """
        Check if processing should be stopped
        
        Returns:
            bool: True if stop flag is set, False otherwise
        """
        return self.stop_flag
    
    def set_stop_flag(self):
        """Set the stop flag for interruption"""
        self.stop_flag = True
        self.logger.warning("Stop flag set - processing will be interrupted")
        self._update_status("正在停止處理...")
    
    def clear_stop_flag(self):
        """Clear the stop flag"""
        self.stop_flag = False
        self.logger.info("Stop flag cleared")
    
    def run(self) -> bool:
        """
        Execute the main processing workflow
        
        Main workflow steps:
        1. Load progress cache
        2. Initialize web scraper and find new books
        3. Process each book (download, generate summary)
        4. Save progress after each book
        5. Generate Word and Excel documents
        6. Send email with attachments
        7. Clean up resources
        
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            self.is_running = True
            self.stop_flag = False
            self.processing_stats['start_time'] = datetime.now()
            
            self.logger.info("=" * 60)
            self.logger.info("開始新書摘要處理流程")
            self.logger.info("=" * 60)
            
            # Step 1: Initialize modules first
            self._update_status("初始化系統模組...")
            self._initialize_modules()
            
            if self.should_stop():
                return self._handle_interruption()
            
            # Step 2: Load progress cache (after modules are initialized)
            self._update_status("載入進度快取...")
            if not self._load_progress_cache():
                return False
            
            if self.should_stop():
                return self._handle_interruption()
            
            # Step 3: Find new books
            self._update_status("搜尋新書...")
            new_books = self._find_new_books()
            if not new_books:
                self.logger.info("沒有找到新書，處理完成")
                self._update_status("沒有找到新書")
                return True
            
            if self.should_stop():
                return self._handle_interruption()
            
            # Step 4: Process each book
            self._update_status(f"開始處理 {len(new_books)} 本新書...")
            if not self._process_all_books(new_books):
                return False
            
            if self.should_stop():
                return self._handle_interruption()
            
            # Step 5: Generate documents - don't fail entire process if this fails
            self._update_status("生成文件...")
            document_paths = None
            try:
                document_paths = self._generate_documents()
                if not document_paths:
                    self.logger.error("文件生成失敗，但處理流程繼續")
                    # Don't return False - continue without sending email
            except Exception as doc_error:
                self.logger.error(f"文件生成發生錯誤: {doc_error}")
                self.logger.debug("文件生成詳細錯誤:", exc_info=True)
                # Continue processing - don't let document generation failure stop everything
            
            if self.should_stop():
                return self._handle_interruption()
            
            # Step 6: Generate notification data (always generate, regardless of document/email status)
            self._update_status("生成通知資料...")
            try:
                notification_success = self._generate_notification_data()
                if notification_success:
                    self.logger.info("通知資料生成成功")
                else:
                    self.logger.error("通知資料生成失敗")
            except Exception as notification_error:
                self.logger.error(f"通知資料生成發生錯誤: {notification_error}")
                self.logger.debug("通知資料生成詳細錯誤:", exc_info=True)
            
            # Step 7: Send email - only if documents were generated successfully
            if document_paths:
                self._update_status("發送郵件...")
                try:
                    email_success = self._send_email(document_paths)
                    if not email_success:
                        self.logger.error("郵件發送失敗，但處理流程已完成")
                        # Don't return False - the main processing was successful
                except Exception as email_error:
                    self.logger.error(f"郵件發送發生錯誤: {email_error}")
                    self.logger.debug("郵件發送詳細錯誤:", exc_info=True)
                    # Continue - don't let email failure invalidate the entire process
            else:
                self.logger.warning("跳過郵件發送 (文件生成失敗)")
                self._update_status("跳過郵件發送 (文件生成失敗)")
            
            # Step 8: Mark completion and cleanup
            self._update_status("處理完成，清理資源...")
            self._mark_completion()
            
            self.processing_stats['end_time'] = datetime.now()
            self._log_final_statistics()
            
            self.logger.info("=" * 60)
            self.logger.info("新書摘要處理流程完成")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"處理流程發生錯誤: {e}", exc_info=True)
            self._update_status(f"處理失敗: {e}")
            return False
        finally:
            self._cleanup_modules()
            self.is_running = False
    
    def _load_progress_cache(self) -> bool:
        """
        Load progress cache and initialize session
        
        Returns:
            bool: True if cache loaded successfully or new session started
        """
        try:
            # Try to load existing progress
            existing_progress = self.progress_manager.load_progress()
            
            if existing_progress:
                # Resume from existing session
                self.logger.info("恢復先前的處理進度")
                processed_titles = self.progress_manager.get_processed_book_titles()
                self.logger.info(f"已處理 {len(processed_titles)} 本書籍")
                
                # Update processing stats from cache
                stats = existing_progress.get('processing_stats', {})
                self.processing_stats.update({
                    'books_processed': stats.get('books_processed', 0),
                    'books_failed': stats.get('books_failed', 0),
                    'pdf_extractions': stats.get('pdf_extractions', 0),
                    'google_searches': stats.get('google_searches', 0)
                })
            else:
                # Start new session
                self.logger.info("開始新的處理會話")
                session_config = {
                    'baseline_book_title': self.config.get('baseline_book_title', ''),
                    'target_url': self.config.get('target_url', ''),
                    'download_dir': self.config.get('download_dir', '')
                }
                self.progress_manager.start_new_session(session_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"載入進度快取失敗: {e}")
            return False
    
    def _find_new_books(self) -> List[Any]:
        """
        Initialize web scraper and find new books
        
        Returns:
            List: List of new book card elements
        """
        try:
            # Set up web driver
            self.scraper.setup_driver()
            
            # Navigate to website
            if not self.scraper.navigate_to_website(self.config['target_url']):
                raise Exception("無法訪問目標網站")
            
            # Wait for page to load
            if not self.scraper.wait_for_page_load():
                raise Exception("頁面載入失敗")
            
            # Find new books
            baseline_title = self.config['baseline_book_title']
            new_books = self.scraper.find_new_books(baseline_title)
            
            self.processing_stats['total_books_found'] = len(new_books)
            self.logger.info(f"找到 {len(new_books)} 本新書")
            
            # Update progress manager with total count
            self.progress_manager.save_progress(total_books=len(new_books))
            
            return new_books
            
        except Exception as e:
            self.logger.error(f"搜尋新書失敗: {e}")
            raise
    
    def _process_all_books(self, new_books: List[Any]) -> bool:
        """
        Process each book (download, generate summary) and save progress after each book
        Enhanced with network error handling - continues processing remaining books on network failures
        
        Args:
            new_books: List of book card elements to process
            
        Returns:
            bool: True if all books processed (some may have failed), False if critical error
        """
        try:
            total_books = len(new_books)
            network_failures = 0
            max_consecutive_network_failures = 5  # Stop if too many consecutive network failures
            consecutive_network_failures = 0
            
            for i, book_card in enumerate(new_books):
                if self.should_stop():
                    self.logger.warning("處理被中斷")
                    return self._handle_interruption()
                
                # Wrap individual book processing in comprehensive try-except to ensure continuation
                book_title = "未知書籍"
                try:
                    # Update status
                    self._update_status(f"處理書籍 {i+1}/{total_books}...")
                    
                    # Extract book information and download PDF with error isolation
                    book_info = None
                    try:
                        book_info = self.scraper.process_book_download(book_card, i, total_books)
                        book_title = book_info.get('title', f'書籍 {i+1}')
                    except Exception as scraper_error:
                        self.logger.error(f"書籍資訊提取失敗 (書籍 {i+1}): {scraper_error}")
                        # Create minimal book info to continue processing
                        book_info = {
                            'title': f'書籍 {i+1} (提取失敗)',
                            'pdf_url': '',
                            'filename': '',
                            'download_path': '',
                            'download_success': False,
                            'error_message': f'書籍資訊提取失敗: {scraper_error}'
                        }
                        book_title = book_info['title']
                        self.processing_stats['books_failed'] += 1
                    
                    # Check if book should be skipped (already processed)
                    if book_info and self.progress_manager.should_skip_book(book_info['title']):
                        self.logger.info(f"跳過已處理的書籍: {book_info['title']}")
                        continue
                    
                    # Process download results with error handling
                    processing_result = None
                    if book_info and not book_info.get('download_success', False):
                        error_msg = book_info.get('error_message', '')
                        
                        # Check for network-related download failures
                        if any(keyword in error_msg.lower() for keyword in ['網路', '連線', 'connection', 'timeout', 'network']):
                            network_failures += 1
                            consecutive_network_failures += 1
                            self.logger.warning(f"網路錯誤導致下載失敗: {book_title} - {error_msg}")
                            
                            # Check if we should pause due to too many consecutive network failures
                            if consecutive_network_failures >= max_consecutive_network_failures:
                                self.logger.error(f"連續 {consecutive_network_failures} 次網路失敗，可能網路連線有問題")
                                self._update_status(f"網路連線問題，暫停 30 秒後繼續...")
                                time.sleep(30)  # Wait 30 seconds before continuing
                                consecutive_network_failures = 0  # Reset counter
                        else:
                            consecutive_network_failures = 0  # Reset counter for non-network errors
                        
                        self.logger.error(f"下載失敗，跳過 AI 處理: {book_title} - {error_msg}")
                        if book_info.get('error_message') != f'書籍資訊提取失敗: {scraper_error}':  # Don't double count
                            self.processing_stats['books_failed'] += 1
                            
                    elif book_info and book_info.get('download_success', False):
                        # Download successful, reset consecutive network failure counter
                        consecutive_network_failures = 0
                        
                        # Process with AI if download was successful - with error isolation
                        try:
                            self.logger.info(f"開始 AI 處理: {book_title}")
                            processing_result = self.ai_processor.generate_summary_with_retry(book_info)
                            self.processing_stats['books_processed'] += 1
                            
                            # Update method statistics
                            method = processing_result.get('processing_method', '')
                            if method == 'pdf_extract':
                                self.processing_stats['pdf_extractions'] += 1
                            elif method == 'google_search':
                                self.processing_stats['google_searches'] += 1
                            
                            self.logger.info(f"✓ 成功處理: {book_title}")
                            
                        except Exception as ai_error:
                            self.logger.error(f"AI 處理失敗: {book_title} - {ai_error}")
                            # Don't let AI failures stop the entire process
                            if book_info:
                                book_info['error_message'] = f"AI 處理失敗: {ai_error}"
                            self.processing_stats['books_failed'] += 1
                            
                            # Log the specific AI error for debugging
                            self.logger.debug(f"AI 處理詳細錯誤: {ai_error}", exc_info=True)
                    
                    # Add to processed books list (even if failed, for progress tracking)
                    if book_info:
                        # Determine if processing was successful
                        processing_success = (
                            processing_result is not None and 
                            processing_result.get('summary') and 
                            len(processing_result.get('summary', '').strip()) > 0
                        )
                        
                        book_entry = {
                            **book_info,
                            **(processing_result or {}),
                            'processing_success': processing_success
                        }
                        
                        self.processed_books.append(book_entry)
                        
                        # Save progress after each book - with error isolation
                        try:
                            self.progress_manager.add_processed_book(book_info, processing_result)
                        except Exception as progress_error:
                            self.logger.warning(f"進度儲存失敗 (不影響處理): {progress_error}")
                    
                    # Log progress
                    processed_count = self.processing_stats['books_processed']
                    failed_count = self.processing_stats['books_failed']
                    self.logger.info(f"進度: {processed_count} 成功, {failed_count} 失敗, {i+1}/{total_books} 完成")
                    
                    if network_failures > 0:
                        self.logger.info(f"網路錯誤統計: {network_failures} 次網路相關失敗")
                    
                except Exception as e:
                    # Catch-all exception handler to ensure processing continues
                    self.logger.error(f"處理書籍時發生未預期錯誤 ({book_title}): {e}")
                    self.logger.debug(f"書籍處理詳細錯誤: {e}", exc_info=True)
                    self.processing_stats['books_failed'] += 1
                    
                    # Check if this is a network-related error
                    if any(keyword in str(e).lower() for keyword in ['網路', '連線', 'connection', 'timeout', 'network']):
                        network_failures += 1
                        consecutive_network_failures += 1
                        self.logger.warning(f"網路相關錯誤: {e}")
                    else:
                        consecutive_network_failures = 0
                    
                    # Create a minimal failed book entry for tracking
                    failed_book_info = {
                        'title': book_title,
                        'pdf_url': '',
                        'filename': '',
                        'download_path': '',
                        'download_success': False,
                        'processing_success': False,
                        'error_message': f'處理失敗: {e}'
                    }
                    self.processed_books.append(failed_book_info)
                    
                    # Try to save progress even for failed books
                    try:
                        self.progress_manager.add_processed_book(failed_book_info, None)
                    except Exception as progress_error:
                        self.logger.warning(f"失敗書籍進度儲存失敗: {progress_error}")
                    
                    # Continue with next book - this is critical for requirement 13.5
                    self.logger.info(f"繼續處理下一本書籍 (當前失敗不影響整體流程)")
                    continue
            
            # Log final network error statistics
            if network_failures > 0:
                self.logger.warning(f"處理完成，共發生 {network_failures} 次網路相關錯誤")
                self.processing_stats['network_failures'] = network_failures
            
            return True
            
        except Exception as e:
            self.logger.error(f"批次處理書籍失敗: {e}")
            return False
    
    def _generate_documents(self) -> Optional[Dict[str, str]]:
        """
        Generate Word and Excel documents with book summaries
        
        Returns:
            Dict with 'word_path' and 'excel_path' keys, or None if generation failed
        """
        try:
            # Filter successfully processed books for document generation
            successful_books = [
                book for book in self.processed_books 
                if book.get('summary') and book.get('processing_success', False)
            ]
            
            if not successful_books:
                self.logger.warning("沒有成功處理的書籍可生成文件")
                return None
            
            self.logger.info(f"生成文件，包含 {len(successful_books)} 本書籍")
            
            # Generate both documents to dedicated folder
            output_dir = 'generated_documents'
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            word_path, excel_path = self.document_generator.generate_both_documents(
                successful_books, output_dir
            )
            
            self.logger.info(f"文件生成完成:")
            self.logger.info(f"  Word 文件: {word_path}")
            self.logger.info(f"  Excel 文件: {excel_path}")
            
            return {
                'word_path': word_path,
                'excel_path': excel_path
            }
            
        except Exception as e:
            self.logger.error(f"文件生成失敗: {e}")
            return None
    
    def _send_email(self, document_paths: Dict[str, str]) -> bool:
        """
        Send email with Word and Excel attachments with enhanced error handling
        
        Args:
            document_paths: Dictionary with 'word_path' and 'excel_path'
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare email details
            recipients = [r.strip() for r in self.config['email_recipients'].split(',') if r.strip()]
            if not recipients:
                self.logger.error("沒有設定收件人")
                return False
            
            current_date = datetime.now().strftime('%Y年%m月%d日')
            subject = f"新書簡介 - {current_date}"
            
            # Create email body
            processed_count = self.processing_stats['books_processed']
            failed_count = self.processing_stats['books_failed']
            network_failures = self.processing_stats.get('network_failures', 0)
            
            body = f"""親愛的同仁，

附件為本日新書簡介文件，包含最新出版的佛教教育書籍摘要。

處理統計：
- 成功處理: {processed_count} 本書籍
- 處理失敗: {failed_count} 本書籍
- PDF 提取: {self.processing_stats['pdf_extractions']} 本
- Google 搜尋: {self.processing_stats['google_searches']} 本"""

            if network_failures > 0:
                body += f"\n- 網路錯誤: {network_failures} 次"

            body += f"""

文件包含：
- Word 文件：新書簡介摘要
- Excel 文件：新書詳細資料

請查收。

此郵件由新書摘要系統自動發送。
處理時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Verify attachment files exist before sending
            attachment_paths = []
            for doc_type, path in document_paths.items():
                if not os.path.exists(path):
                    self.logger.error(f"附件檔案不存在: {path}")
                    return False
                elif not os.access(path, os.R_OK):
                    self.logger.error(f"附件檔案無讀取權限: {path}")
                    return False
                else:
                    file_size = os.path.getsize(path)
                    if file_size == 0:
                        self.logger.error(f"附件檔案為空: {path}")
                        return False
                    attachment_paths.append(path)
                    self.logger.info(f"附件檔案驗證通過: {os.path.basename(path)} ({file_size} bytes)")
            
            # Send email with retry mechanism
            try:
                success = self.email_sender.send_notification_email(
                    subject=subject,
                    body=body,
                    is_html=False,
                    attachments=attachment_paths,
                    recipients=recipients
                )
                
                if success:
                    self.logger.info(f"郵件發送成功，收件人: {', '.join(recipients)}")
                    return True
                else:
                    self.logger.error("郵件發送失敗")
                    return False
                    
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP 認證失敗，請檢查郵件伺服器設定和密碼: {e}"
                self.logger.error(error_msg)
                self._update_status(f"郵件發送失敗: 認證錯誤")
                return False
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = f"收件人地址被拒絕，請檢查收件人設定: {e}"
                self.logger.error(error_msg)
                self._update_status(f"郵件發送失敗: 收件人錯誤")
                return False
                
            except smtplib.SMTPConnectError as e:
                error_msg = f"無法連接到郵件伺服器，請檢查網路連線和伺服器設定: {e}"
                self.logger.error(error_msg)
                self._update_status(f"郵件發送失敗: 連線錯誤")
                return False
                
            except smtplib.SMTPException as e:
                error_msg = f"SMTP 錯誤: {e}"
                self.logger.error(error_msg)
                self._update_status(f"郵件發送失敗: SMTP 錯誤")
                return False
                
        except Exception as e:
            error_msg = f"發送郵件時發生未預期錯誤: {e}"
            self.logger.error(error_msg, exc_info=True)
            self._update_status(f"郵件發送失敗: {e}")
            return False
    
    def _generate_notification_data(self) -> bool:
        """
        Generate JSON output file with processed book summaries for notification system
        
        Returns:
            bool: True if notification data generated successfully, False otherwise
        """
        try:
            # Filter successfully processed books for notifications
            successful_books = [
                book for book in self.processed_books 
                if book.get('summary') and book.get('processing_success', False)
            ]
            
            # Create notification data structure
            notification_data = {
                'processingDate': datetime.now().isoformat(),
                'totalBooksFound': self.processing_stats['total_books_found'],
                'successfullyProcessed': [],
                'processingStats': {
                    'booksProcessed': self.processing_stats['books_processed'],
                    'booksFailed': self.processing_stats['books_failed'],
                    'pdfExtractions': self.processing_stats['pdf_extractions'],
                    'googleSearches': self.processing_stats['google_searches'],
                    'processingTimeSeconds': self.processing_stats.get('processing_time_seconds', 0),
                    'networkFailures': self.processing_stats.get('network_failures', 0)
                }
            }
            
            # Process each successful book for notification format
            for book in successful_books:
                book_summary = {
                    'title': book.get('title', ''),
                    'author': book.get('author', ''),
                    'summary': book.get('summary', ''),
                    'downloadUrl': book.get('pdf_url', ''),
                    'processingMethod': book.get('processing_method', 'unknown'),
                    'processingSuccess': book.get('processing_success', False),
                    'filename': book.get('filename', ''),
                    'downloadPath': book.get('download_path', '')
                }
                notification_data['successfullyProcessed'].append(book_summary)
            
            # Ensure output directory exists
            output_dir = 'generated_documents'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Generate output file with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(output_dir, f'notification_data_{timestamp}.json')
            
            # Also create a latest file for easy access by the LINE bot
            latest_file = os.path.join(output_dir, 'notification_data_latest.json')
            
            # Write notification data to files
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
            
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(notification_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"通知資料已生成:")
            self.logger.info(f"  時間戳記檔案: {output_file}")
            self.logger.info(f"  最新檔案: {latest_file}")
            self.logger.info(f"  成功處理書籍數: {len(successful_books)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"生成通知資料失敗: {e}")
            return False

    def _mark_completion(self):
        """Mark processing as completed and clean up cache"""
        try:
            # Update baseline book title if we processed any books successfully
            self._update_baseline_book_title()
            
            # Mark session as completed
            self.progress_manager.mark_session_completed()
            
            # Clean up cache file (processing is complete)
            self.progress_manager.cleanup_cache()
            
            self.logger.info("處理標記為完成，快取已清理")
            
        except Exception as e:
            self.logger.warning(f"標記完成時發生錯誤: {e}")
    
    def _update_baseline_book_title(self):
        """
        Update baseline book title to the first successfully processed book
        This prevents reprocessing the same books in future runs
        """
        try:
            # Find successfully processed books
            successful_books = [
                book for book in self.processed_books 
                if book.get('processing_success', False) and book.get('title')
            ]
            
            if not successful_books:
                self.logger.info("沒有成功處理的書籍，不更新基準書籍標題")
                return
            
            # Use the first successfully processed book as the new baseline
            # This ensures we won't reprocess it in future runs
            new_baseline_title = successful_books[0]['title']
            
            # Update configuration
            success = self.config_manager.update_baseline_book_title(new_baseline_title)
            
            if success:
                self.logger.info(f"基準書籍標題已自動更新為: {new_baseline_title}")
                self.logger.info("下次執行時將從此書籍之後開始檢查新書")
                
                # Update our internal config as well
                self.config['baseline_book_title'] = new_baseline_title
            else:
                self.logger.error("自動更新基準書籍標題失敗")
                
        except Exception as e:
            self.logger.error(f"更新基準書籍標題時發生錯誤: {e}")
    
    def _log_final_statistics(self):
        """Log final processing statistics with error analysis"""
        stats = self.processing_stats
        
        # Calculate processing time
        if stats['start_time'] and stats['end_time']:
            processing_time = (stats['end_time'] - stats['start_time']).total_seconds()
            stats['processing_time_seconds'] = processing_time
        else:
            processing_time = 0
        
        self.logger.info("=" * 50)
        self.logger.info("最終處理統計")
        self.logger.info("=" * 50)
        self.logger.info(f"總書籍數: {stats['total_books_found']}")
        self.logger.info(f"成功處理: {stats['books_processed']}")
        self.logger.info(f"處理失敗: {stats['books_failed']}")
        self.logger.info(f"PDF 提取: {stats['pdf_extractions']}")
        self.logger.info(f"Google 搜尋: {stats['google_searches']}")
        
        # Network error statistics
        network_failures = stats.get('network_failures', 0)
        if network_failures > 0:
            self.logger.info(f"網路錯誤: {network_failures} 次")
        
        if processing_time > 0:
            self.logger.info(f"總處理時間: {processing_time:.1f} 秒")
            if stats['books_processed'] > 0:
                avg_time = processing_time / stats['books_processed']
                self.logger.info(f"平均每本書處理時間: {avg_time:.1f} 秒")
        
        success_rate = (stats['books_processed'] / stats['total_books_found'] * 100) if stats['total_books_found'] > 0 else 0
        self.logger.info(f"成功率: {success_rate:.1f}%")
        
        # Error analysis
        if stats['books_failed'] > 0:
            self.logger.info("錯誤分析:")
            
            # Analyze error types from processed books
            error_types = {}
            for book in self.processed_books:
                if not book.get('download_success', True) or not book.get('summary'):
                    error_msg = book.get('error_message', '未知錯誤')
                    # Categorize errors
                    if '網路' in error_msg or 'connection' in error_msg.lower() or 'timeout' in error_msg.lower():
                        error_types['網路錯誤'] = error_types.get('網路錯誤', 0) + 1
                    elif 'AI' in error_msg or 'API' in error_msg or 'Gemini' in error_msg:
                        error_types['AI 處理錯誤'] = error_types.get('AI 處理錯誤', 0) + 1
                    elif '檔案' in error_msg or 'file' in error_msg.lower() or 'PDF' in error_msg:
                        error_types['檔案錯誤'] = error_types.get('檔案錯誤', 0) + 1
                    elif '提取' in error_msg or 'extract' in error_msg.lower():
                        error_types['資訊提取錯誤'] = error_types.get('資訊提取錯誤', 0) + 1
                    else:
                        error_types['其他錯誤'] = error_types.get('其他錯誤', 0) + 1
            
            for error_type, count in error_types.items():
                self.logger.info(f"  {error_type}: {count} 次")
        
        # Processing resilience summary
        if stats['books_failed'] > 0 and stats['books_processed'] > 0:
            self.logger.info(f"處理韌性: 即使有 {stats['books_failed']} 本書籍失敗，系統仍成功處理了 {stats['books_processed']} 本書籍")
        
        self.logger.info("=" * 50)
    
    def _handle_interruption(self) -> bool:
        """
        Handle processing interruption - save progress before stopping and log interruption event
        
        Returns:
            bool: False to indicate processing was interrupted
        """
        try:
            self.logger.warning("處理被使用者中斷")
            self._update_status("正在儲存進度並停止...")
            
            # Save current progress before stopping
            if self.progress_manager:
                # Mark session as interrupted
                self.progress_manager.mark_session_interrupted()
                self.logger.info("進度已儲存，會話標記為中斷")
            
            # Log interruption event with current processing state
            processed_count = self.processing_stats['books_processed']
            failed_count = self.processing_stats['books_failed']
            total_found = self.processing_stats['total_books_found']
            
            self.logger.warning("=" * 50)
            self.logger.warning("處理中斷摘要")
            self.logger.warning("=" * 50)
            self.logger.warning(f"總書籍數: {total_found}")
            self.logger.warning(f"已處理: {processed_count}")
            self.logger.warning(f"處理失敗: {failed_count}")
            self.logger.warning(f"剩餘未處理: {total_found - processed_count - failed_count}")
            self.logger.warning(f"中斷時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.warning("可重新啟動程式以繼續處理剩餘書籍")
            self.logger.warning("=" * 50)
            
            self._update_status("處理已中斷，進度已儲存")
            
            return False
            
        except Exception as e:
            self.logger.error(f"處理中斷時發生錯誤: {e}")
            return False
    
    def request_stop(self):
        """
        Request processing to stop gracefully (public method for external calls)
        
        This method can be called from UI or other external components to request
        that processing stops at the next safe checkpoint.
        """
        if not self.is_running:
            self.logger.info("處理未在執行中，無需停止")
            return
        
        self.logger.info("收到停止請求")
        self.set_stop_flag()
        
        # If running in a separate thread, we can't force stop immediately
        # The processing loop will check the stop flag and handle interruption gracefully
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.info("等待處理執行緒安全停止...")
            # Don't join here as it might block the UI thread
            # Let the thread finish naturally when it checks the stop flag
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for processing thread to complete
        
        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            bool: True if thread completed, False if timeout occurred
        """
        if not self.processing_thread or not self.processing_thread.is_alive():
            return True
        
        try:
            self.processing_thread.join(timeout)
            return not self.processing_thread.is_alive()
        except Exception as e:
            self.logger.error(f"等待處理完成時發生錯誤: {e}")
            return False
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get current processing status for monitoring
        
        Returns:
            Dict: Current processing status and statistics
        """
        status = {
            'is_running': self.is_running,
            'stop_requested': self.stop_flag,
            'stats': self.processing_stats.copy()
        }
        
        # Add progress manager status if available
        if self.progress_manager:
            session_summary = self.progress_manager.get_session_summary()
            status['session'] = session_summary
        
        # Add thread status
        if self.processing_thread:
            status['thread_alive'] = self.processing_thread.is_alive()
        else:
            status['thread_alive'] = False
        
        return status
    
    def force_stop(self):
        """
        Force stop processing (emergency stop - may lose progress)
        
        Warning: This method should only be used in emergency situations
        as it may not save progress properly.
        """
        self.logger.warning("強制停止處理 (緊急停止)")
        self.stop_flag = True
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.warning("強制終止處理執行緒")
            # Note: Python doesn't have a clean way to force-kill threads
            # The thread will need to check stop_flag and exit naturally
            # This is just a more aggressive flag setting
        
        # Clean up modules immediately
        self._cleanup_modules()
        self.is_running = False
        
        self._update_status("處理已強制停止")
    
    def is_interruptible(self) -> bool:
        """
        Check if processing is currently in an interruptible state
        
        Returns:
            bool: True if processing can be safely interrupted
        """
        # Processing is interruptible if it's running and not in a critical section
        # For this implementation, we consider it always interruptible when running
        # as we check the stop flag between major operations
        return self.is_running and not self.stop_flag
    
    def start_processing_async(self) -> bool:
        """
        Start main processing in a separate thread for background execution
        
        This method allows the UI to remain responsive while processing runs in the background.
        The processing thread will update status through the callback mechanism.
        
        Returns:
            bool: True if thread started successfully, False if already running or error
        """
        try:
            if self.is_running:
                self.logger.warning("處理已在執行中，無法啟動新的處理")
                return False
            
            if self.processing_thread and self.processing_thread.is_alive():
                self.logger.warning("處理執行緒仍在運行中")
                return False
            
            # Clear any previous stop flag
            self.clear_stop_flag()
            
            # Create and start processing thread
            self.processing_thread = threading.Thread(
                target=self._run_with_exception_handling,
                name="MainProcessor-Thread",
                daemon=False  # Don't make it daemon so it can complete properly
            )
            
            self.logger.info("啟動背景處理執行緒...")
            self.processing_thread.start()
            
            # Give thread a moment to start
            time.sleep(0.1)
            
            if self.processing_thread.is_alive():
                self.logger.info(f"處理執行緒已啟動 (Thread ID: {self.processing_thread.ident})")
                return True
            else:
                self.logger.error("處理執行緒啟動失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"啟動背景處理時發生錯誤: {e}")
            return False
    
    def _run_with_exception_handling(self):
        """
        Wrapper for run() method with comprehensive exception handling for thread execution
        
        This method ensures that any exceptions in the processing thread are properly
        logged and don't crash the application.
        """
        try:
            self.logger.info(f"處理執行緒開始執行 (Thread: {threading.current_thread().name})")
            
            # Update UI from worker thread safely
            self._update_status("背景處理已開始...")
            
            # Run the main processing workflow
            success = self.run()
            
            if success:
                self.logger.info("背景處理成功完成")
                self._update_status("處理成功完成")
            else:
                self.logger.warning("背景處理未成功完成")
                self._update_status("處理未成功完成")
            
        except Exception as e:
            self.logger.error(f"背景處理執行緒發生未處理的錯誤: {e}", exc_info=True)
            self._update_status(f"處理發生錯誤: {e}")
            
            # Try to save progress even if there was an error
            try:
                if self.progress_manager:
                    self.progress_manager.mark_session_interrupted()
                    self.logger.info("錯誤發生時已儲存進度")
            except Exception as save_error:
                self.logger.error(f"儲存錯誤狀態進度失敗: {save_error}")
        
        finally:
            # Ensure cleanup happens regardless of success or failure
            try:
                self._cleanup_modules()
            except Exception as cleanup_error:
                self.logger.error(f"清理模組時發生錯誤: {cleanup_error}")
            
            # Mark as not running
            self.is_running = False
            self.logger.info("處理執行緒結束")
            self._update_status("處理執行緒已結束")
    
    def start_processing_sync(self) -> bool:
        """
        Start processing synchronously (blocking call)
        
        This method runs processing in the current thread and blocks until completion.
        Useful for testing or when background execution is not needed.
        
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            if self.is_running:
                self.logger.warning("處理已在執行中")
                return False
            
            self.logger.info("開始同步處理...")
            self.clear_stop_flag()
            
            # Run processing directly in current thread
            return self.run()
            
        except Exception as e:
            self.logger.error(f"同步處理發生錯誤: {e}")
            return False
    
    def update_ui_from_worker_thread(self, message: str):
        """
        Safely update UI from worker thread using the status callback
        
        This method provides a thread-safe way for the worker thread to update
        the UI without directly manipulating UI elements.
        
        Args:
            message: Status message to send to UI
        """
        try:
            if self.status_callback:
                # The callback should handle thread-safe UI updates
                # (e.g., using tkinter's after() method to schedule UI updates)
                self.status_callback(message)
            
            # Also log the message
            self.logger.info(f"[Worker Thread] {message}")
            
        except Exception as e:
            self.logger.error(f"UI 更新失敗: {e}")
    
    def get_thread_info(self) -> Dict[str, Any]:
        """
        Get information about the processing thread for debugging
        
        Returns:
            Dict: Thread information including status, ID, etc.
        """
        info = {
            'has_thread': self.processing_thread is not None,
            'thread_alive': False,
            'thread_name': None,
            'thread_id': None,
            'is_daemon': None,
            'current_thread_id': threading.current_thread().ident,
            'current_thread_name': threading.current_thread().name
        }
        
        if self.processing_thread:
            info.update({
                'thread_alive': self.processing_thread.is_alive(),
                'thread_name': self.processing_thread.name,
                'thread_id': self.processing_thread.ident,
                'is_daemon': self.processing_thread.daemon
            })
        
        return info
    
    def join_processing_thread(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for the processing thread to complete (join)
        
        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            bool: True if thread completed, False if timeout or no thread
        """
        if not self.processing_thread:
            self.logger.debug("沒有處理執行緒可等待")
            return True
        
        if not self.processing_thread.is_alive():
            self.logger.debug("處理執行緒已結束")
            return True
        
        try:
            self.logger.info(f"等待處理執行緒完成 (timeout: {timeout})")
            self.processing_thread.join(timeout)
            
            is_alive = self.processing_thread.is_alive()
            if not is_alive:
                self.logger.info("處理執行緒已完成")
                return True
            else:
                self.logger.warning(f"處理執行緒等待超時 ({timeout} 秒)")
                return False
                
        except Exception as e:
            self.logger.error(f"等待處理執行緒時發生錯誤: {e}")
            return False


# Example usage and testing functions
def create_test_config() -> Dict[str, Any]:
    """
    Create a test configuration for MainProcessor
    
    Returns:
        Dict: Test configuration with all required settings
    """
    return {
        'gemini_api_key': 'test-api-key',
        'chromedriver_path': 'chromedriver-win64\\chromedriver.exe',
        'target_url': 'https://www.budaedu.org/#/books/applicable/chinese',
        'baseline_book_title': 'CH754-02',
        'download_dir': 'downloads',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'test@example.com',
        'smtp_password': 'test-password',
        'email_recipients': 'recipient1@example.com,recipient2@example.com'
    }


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('main_processor_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # Create test configuration
    config = create_test_config()
    
    try:
        # Initialize MainProcessor
        processor = MainProcessor(config, logger)
        
        # Set up status callback for testing
        def status_callback(message):
            print(f"[STATUS] {message}")
        
        processor.set_status_callback(status_callback)
        
        # Test synchronous processing (for testing)
        if len(sys.argv) > 1 and sys.argv[1] == '--sync':
            logger.info("Testing synchronous processing...")
            success = processor.start_processing_sync()
            logger.info(f"Synchronous processing result: {success}")
        else:
            # Test asynchronous processing
            logger.info("Testing asynchronous processing...")
            success = processor.start_processing_async()
            
            if success:
                logger.info("Background processing started successfully")
                
                # Wait for completion or simulate interruption
                import time
                time.sleep(5)  # Let it run for 5 seconds
                
                if processor.is_running:
                    logger.info("Requesting stop...")
                    processor.request_stop()
                
                # Wait for completion
                processor.join_processing_thread(timeout=30)
                
            else:
                logger.error("Failed to start background processing")
        
        # Get final status
        final_status = processor.get_processing_status()
        logger.info(f"Final status: {final_status}")
        
    except Exception as e:
        logger.error(f"Test execution error: {e}", exc_info=True)