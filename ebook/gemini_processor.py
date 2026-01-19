#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI Processor Module for New Book Summary System
新書摘要系統的 Gemini AI 處理模組

This module handles AI-powered book summary generation using Google Gemini Pro 2.5 API.
Supports both PDF text extraction and Google Search-based summary generation.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, Tuple
import google.generativeai as genai
import pypdf

# OCR Processor for image-based PDFs
try:
    from ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class GeminiProcessor:
    """
    AI processor for generating book summaries using Google Gemini Pro 2.5 API
    
    Supports two processing methods:
    1. PDF text extraction for files <= 30MB
    2. Google Search-based summary for files > 30MB
    """
    
    def __init__(self, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize GeminiProcessor with API key and logger
        
        Args:
            api_key: Google Gemini API key
            logger: Logger instance for logging operations
        """
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.ocr_processor = None  # Lazy initialization
        
        # Initialize Gemini client
        self._initialize_client()
    
    def _get_ocr_processor(self):
        """
        Get or initialize OCR processor (lazy initialization).
        
        Returns:
            OCRProcessor instance or None if not available
        """
        if not OCR_AVAILABLE:
            self.logger.warning("OCR processor not available (ocr_processor module not found)")
            return None
        
        if self.ocr_processor is None:
            try:
                self.ocr_processor = OCRProcessor(self.api_key, self.logger)
                self.logger.info("OCR processor initialized for image-based PDF handling")
            except Exception as e:
                self.logger.error(f"Failed to initialize OCR processor: {e}")
                return None
        
        return self.ocr_processor
    
    def _is_content_quality_good(self, text: str, book_title: str = "") -> bool:
        """
        Check if extracted text is actual book content vs. metadata pages
        (donation acknowledgments, copyright notices, etc.)
        
        Args:
            text: Extracted text to evaluate
            book_title: Book title for context
            
        Returns:
            bool: True if text appears to be actual book content
        """
        if not text:
            return False
        
        # Minimum content threshold (characters)
        MIN_CONTENT_LENGTH = 500
        
        # Keywords that indicate metadata/non-content pages
        METADATA_KEYWORDS = [
            # Donation-related
            "捐贈", "捐款", "助印", "印贈", "結緣", "功德", "回向", 
            "恭印", "隨喜", "福田", "法施", "廣植", "善根",
            # Copyright/publishing-related
            "版權所有", "翻印必究", "財團法人", "基金會", 
            "發行", "印刷", "出版社", "出版日期",
            # Contact info
            "電話", "傳真", "地址", "郵政劃撥", "郵撥帳號",
            "電子郵件", "網址", "索取", "免費結緣",
            # Other metadata
            "目錄", "序言", "前言", "編輯說明"
        ]
        
        # Keywords that indicate actual Buddhist content
        CONTENT_KEYWORDS = [
            # Buddhist concepts
            "佛陀", "菩薩", "般若", "涅槃", "輪迴", "解脫", "成佛",
            "法門", "禪定", "智慧", "慈悲", "佛法", "修行", "覺悟",
            "眾生", "煩惱", "業障", "因果", "三寶", "五戒", "十善",
            "八正道", "四聖諦", "六度", "唯識", "淨土", "念佛",
            # Common Buddhist text markers
            "經云", "論云", "佛說", "如是我聞", "爾時", "世尊",
            # Chapter/section markers
            "第一章", "第二章", "第一節", "第二節"
        ]
        
        text_lower = text.lower()
        text_length = len(text)
        
        # Count metadata vs content keywords
        metadata_count = sum(1 for kw in METADATA_KEYWORDS if kw in text)
        content_count = sum(1 for kw in CONTENT_KEYWORDS if kw in text)
        
        self.logger.debug(f"Text quality check: length={text_length}, metadata_kw={metadata_count}, content_kw={content_count}")
        
        # If text is too short, likely just metadata pages
        if text_length < MIN_CONTENT_LENGTH:
            self.logger.info(f"Text too short ({text_length} chars < {MIN_CONTENT_LENGTH}), considered low quality")
            return False
        
        # If metadata keywords dominate, likely not real content
        if metadata_count > 5 and content_count < 3:
            self.logger.info(f"Too many metadata keywords ({metadata_count}) vs content keywords ({content_count})")
            return False
        
        # If text is mostly about donations/publishing
        donation_related = sum(1 for kw in ["捐贈", "捐款", "助印", "功德", "回向", "恭印"] if kw in text)
        if donation_related >= 3 and text_length < 2000:
            self.logger.info(f"Text appears to be donation/acknowledgment page ({donation_related} donation keywords)")
            return False
        
        return True
    
    def _initialize_client(self):
        """
        Initialize Gemini client using google-generativeai SDK
        
        Raises:
            Exception: If API key is invalid or client initialization fails
        """
        try:
            if not self.api_key or self.api_key.strip() == '':
                raise ValueError("Gemini API key is required")
            
            # Configure the API key
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.client = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
            self.logger.info(f"Gemini client initialized with model: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise 
   
    def check_pdf_size(self, pdf_path: str) -> int:
        """
        Check PDF file size in bytes and compare against 30MB threshold
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            int: File size in bytes
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            OSError: If file cannot be accessed
        """
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not os.path.isfile(pdf_path):
                raise OSError(f"Path is not a file: {pdf_path}")
            
            file_size = os.path.getsize(pdf_path)
            file_size_mb = file_size / (1024 * 1024)
            
            self.logger.info(f"PDF file size: {file_size_mb:.2f} MB ({file_size} bytes)")
            
            # 30MB threshold
            threshold_bytes = 30 * 1024 * 1024
            if file_size > threshold_bytes:
                self.logger.info(f"PDF size ({file_size_mb:.2f} MB) exceeds 30MB threshold")
            else:
                self.logger.info(f"PDF size ({file_size_mb:.2f} MB) is within 30MB threshold")
            
            return file_size
            
        except Exception as e:
            self.logger.error(f"Error checking PDF size for {pdf_path}: {e}")
            raise  
  
    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text content from PDF using pypdf library with enhanced file system error handling
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Extracted text content from the PDF
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PermissionError: If PDF file cannot be accessed
            Exception: If PDF extraction fails
        """
        try:
            # Comprehensive file system checks
            if not pdf_path:
                raise ValueError("PDF path is empty or None")
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            if not os.path.isfile(pdf_path):
                raise OSError(f"Path is not a file: {pdf_path}")
            
            if not os.access(pdf_path, os.R_OK):
                raise PermissionError(f"No read permission for PDF file: {pdf_path}")
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                raise OSError(f"PDF file is empty: {pdf_path}")
            
            self.logger.info(f"Extracting text from PDF: {pdf_path} ({file_size} bytes)")
            
            extracted_text = []
            
            try:
                with open(pdf_path, 'rb') as file:
                    try:
                        reader = pypdf.PdfReader(file)
                        total_pages = len(reader.pages)
                        
                        if total_pages == 0:
                            self.logger.warning(f"PDF has no pages: {pdf_path}")
                            return ""
                        
                        self.logger.info(f"PDF has {total_pages} pages")
                        
                        # Track extraction success
                        successful_pages = 0
                        
                        for page_num, page in enumerate(reader.pages, 1):
                            try:
                                page_text = page.extract_text()
                                if page_text and page_text.strip():
                                    extracted_text.append(page_text.strip())
                                    successful_pages += 1
                                    self.logger.debug(f"Extracted text from page {page_num}")
                                else:
                                    pass # Skip logging per page to avoid spam
                            except Exception as page_error:
                                self.logger.warning(f"Failed to extract text from page {page_num}: {page_error}")
                                continue
                        
                        self.logger.info(f"Successfully extracted text from {successful_pages}/{total_pages} pages")
                        
                    except pypdf.errors.PdfReadError as pdf_error:
                        raise Exception(f"PDF file is corrupted or invalid: {pdf_error}")
                    except Exception as reader_error:
                        raise Exception(f"Failed to read PDF file: {reader_error}")
                        
            except IOError as io_error:
                raise IOError(f"Failed to open PDF file: {io_error}")
            except OSError as os_error:
                raise OSError(f"File system error accessing PDF: {os_error}")
            
            full_text = "\n\n".join(extracted_text)
            text_length = len(full_text)
            
            if text_length == 0:
                self.logger.warning("No text could be extracted from the PDF - file may be image-based or encrypted")
                return ""
            
            self.logger.info(f"Successfully extracted {text_length} characters from PDF")
            return full_text
            
        except (FileNotFoundError, PermissionError, OSError, ValueError) as fs_error:
            self.logger.error(f"File system error extracting text from PDF {pdf_path}: {fs_error}")
            raise fs_error
        except Exception as e:
            self.logger.error(f"Unexpected error extracting text from PDF {pdf_path}: {e}")
            raise Exception(f"PDF text extraction failed: {e}")   
 
    def clean_summary_text(self, summary: str) -> str:
        """
        Clean summary text by removing common AI response prefixes using regex patterns
        
        Args:
            summary: Raw summary text from AI
            
        Returns:
            str: Cleaned summary text
        """
        if not summary:
            return summary
        
        import re
        
        cleaned_summary = summary.strip()
        
        # Define regex patterns to match and remove common prefixes
        patterns_to_remove = [
            # Match "好的，這是一份為書籍「...」生成的...摘要："
            r'^好的，這是一份為書籍[^：]*：\s*',
            r'^好的，這是[^：]*：\s*',
            # Match "以下是這本書的摘要："
            r'^以下是[^：]*：\s*',
            # Match "這是一份書籍摘要，內容如下："
            r'^這是一份[^：]*：\s*',
            # Match "摘要："
            r'^摘要：\s*',
            # Match "書籍摘要："
            r'^書籍摘要：\s*',
            # Match "內容摘要："
            r'^內容摘要：\s*',
            # Match "本書摘要："
            r'^本書摘要：\s*',
            # Match "生成的摘要："
            r'^生成的摘要：\s*',
            # Match any pattern ending with "摘要："
            r'^[^：]*摘要：\s*',
            # Match "這本書的摘要："
            r'^這本書的摘要：\s*',
            # Match "書籍摘要，內容如下："
            r'^書籍摘要，[^：]*：\s*',
        ]
        
        # Apply each pattern
        for pattern in patterns_to_remove:
            match = re.match(pattern, cleaned_summary, re.IGNORECASE)
            if match:
                # Remove the matched prefix
                cleaned_summary = cleaned_summary[match.end():].strip()
                self.logger.debug(f"Removed prefix using pattern: {pattern}")
                break
        
        # Additional cleanup: remove any remaining leading punctuation
        while cleaned_summary and cleaned_summary[0] in '：:。，,「」':
            cleaned_summary = cleaned_summary[1:].strip()
        
        return cleaned_summary

    def generate_summary_from_pdf(self, pdf_path: str, book_title: str, author: str = "") -> str:
        """
        Generate book summary from PDF content using Gemini API with enhanced error handling
        
        Args:
            pdf_path: Path to the PDF file
            book_title: Title of the book for context
            author: Author of the book (optional, used for fallback search)
            
        Returns:
            str: Generated 300-character Traditional Chinese summary
            
        Raises:
            Exception: If PDF processing or API call fails
        """
        try:
            self.logger.info(f"Generating summary from PDF: {book_title}")
            
            # For files <= 30MB, extract text and send as text prompt
            # (PDF upload feature may not be available in older SDK versions)
            # Try to extract text from PDF first
            extracted_text = self.extract_pdf_text(pdf_path)
            
            # Check if extracted text is low quality (e.g., only donation/copyright pages)
            use_ocr = False
            if not extracted_text:
                self.logger.info(f"No text extracted from PDF (likely image-based), attempting OCR for: {book_title}")
                use_ocr = True
            elif not self._is_content_quality_good(extracted_text, book_title):
                self.logger.info(f"Extracted text appears to be metadata only (donation/copyright pages), attempting OCR for: {book_title}")
                use_ocr = True
            
            if use_ocr:
                # Try OCR for image-based PDFs
                ocr_processor = self._get_ocr_processor()
                if ocr_processor:
                    try:
                        ocr_text = ocr_processor.process_pdf(pdf_path, book_title)
                        if ocr_text and len(ocr_text) > len(extracted_text or ""):
                            extracted_text = ocr_text
                            self.logger.info(f"OCR successful, extracted {len(extracted_text)} characters")
                        else:
                            self.logger.warning("OCR returned less text than pypdf, keeping original")
                    except Exception as ocr_error:
                        self.logger.error(f"OCR processing failed: {ocr_error}")
                
                # Final fallback to search if OCR also failed
                if not extracted_text:
                    self.logger.warning(f"Both pypdf and OCR failed, falling back to search method for: {book_title}")
                    return self.generate_summary_from_search(book_title, author)

            
            # Create prompt for summary generation with extracted text
            prompt = f"""請直接用繁體中文為這本書「{book_title}」生成 300 字的摘要，包含主要內容和重點。

重要指示：
- 直接輸出摘要內容，不要加上「好的」、「這是」、「以下是」等開頭語句
- 不要說明這是摘要或介紹文字
- 直接從書籍內容開始描述

書籍內容：
{extracted_text[:8000]}  # Limit text to avoid token limits
"""
            
            self.logger.info("Sending extracted text to Gemini API for summary generation...")
            
            # Define the API call function for retry mechanism
            def make_api_call():
                try:
                    response = self.client.generate_content(prompt)
                    
                    if not response:
                        raise Exception("No response received from Gemini API")
                    
                    if not hasattr(response, 'text') or not response.text:
                        raise Exception("Empty or invalid response from Gemini API")
                    
                    return response.text.strip()
                    
                except Exception as api_error:
                    # Log the specific API error for debugging
                    self.logger.debug(f"Gemini API call error: {api_error}")
                    raise api_error
            
            # Use retry mechanism for API call
            summary = self.retry_on_failure(make_api_call, max_retries=3, delay=10)
            
            if not summary:
                raise Exception("Generated summary is empty")
            
            # Clean the summary text
            cleaned_summary = self.clean_summary_text(summary)
            
            self.logger.info(f"Successfully generated summary ({len(cleaned_summary)} characters)")
            self.logger.debug(f"Summary preview: {cleaned_summary[:100]}...")
            
            return cleaned_summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary from PDF for {book_title}: {e}")
            raise   
 
    def generate_summary_from_search(self, book_title: str, author: str = "") -> str:
        """
        Generate book summary using Google Search via Gemini API with enhanced error handling
        
        Args:
            book_title: Title of the book to search for
            
        Returns:
            str: Generated 300-character Traditional Chinese summary
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Build book info string with author if available
            book_info = f"書名：{book_title}"
            if author and author.strip():
                book_info += f"\n作者：{author}"
                self.logger.info(f"Generating summary using Google Search for: {book_title} (作者: {author})")
            else:
                self.logger.info(f"Generating summary using Google Search for: {book_title}")
            
            # Create search-based prompt with author information
            # Note: This uses the model's training knowledge
            prompt = f"""請根據你的知識為以下書籍直接用繁體中文生成 300 字的摘要，包含主要內容和重點。

{book_info}

重要指示：
- 直接輸出摘要內容，不要加上「好的」、「這是」、「以下是」等開頭語句
- 不要說明這是摘要或介紹文字
- 直接從書籍內容開始描述
- 如果你不熟悉這本書，請說明無法提供摘要"""
            
            self.logger.info("Sending search query to Gemini API...")
            
            # Define the API call function for retry mechanism
            def make_search_api_call():
                try:
                    response = self.client.generate_content(prompt)
                    
                    if not response:
                        raise Exception("No response received from Gemini API")
                    
                    if not hasattr(response, 'text') or not response.text:
                        raise Exception("Empty or invalid response from Gemini API")
                    
                    return response.text.strip()
                    
                except Exception as api_error:
                    # Log the specific API error for debugging
                    self.logger.debug(f"Gemini API search call error: {api_error}")
                    raise api_error
            
            # Use retry mechanism for API call with slightly longer delay for search queries
            summary = self.retry_on_failure(make_search_api_call, max_retries=3, delay=15)
            
            if not summary:
                raise Exception("Generated summary is empty")
            
            # Check if the API indicated it couldn't provide a summary
            if "無法提供摘要" in summary or "不熟悉" in summary:
                self.logger.warning(f"Gemini API indicated it's not familiar with the book: {book_title}")
                # Still return the response as it might contain useful information
            
            # Clean the summary text
            cleaned_summary = self.clean_summary_text(summary)
            
            self.logger.info(f"Successfully generated summary from search ({len(cleaned_summary)} characters)")
            self.logger.debug(f"Summary preview: {cleaned_summary[:100]}...")
            
            return cleaned_summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary from search for {book_title}: {e}")
            raise 
   
    def process_book(self, book_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main book processing logic - selects processing method based on PDF size
        Supports both single PDF (download_path) and multiple PDFs (downloaded_files)
        
        Args:
            book_info: Dictionary containing book information with keys:
                - title: Book title
                - download_path: Path to downloaded PDF (legacy, single PDF)
                - downloaded_files: List of paths to downloaded PDFs (multi-PDF support)
                - pdf_url/pdf_urls: Original PDF URL(s)
                - filename/filenames: PDF filename(s)
                
        Returns:
            Dict containing processed book information with summary and metadata:
                - title: Book title
                - summary: Generated summary
                - processing_method: 'pdf_extract' or 'google_search'
                - file_size_bytes: Total PDF file size in bytes
                - timestamp: Processing timestamp
                - pdf_url: Original PDF URL
                - filename: PDF filename
                
        Raises:
            Exception: If processing fails
        """
        try:
            book_title = book_info['title']
            self.logger.info(f"Processing book: {book_title}")
            
            # Handle both single PDF and multiple PDFs
            pdf_paths = []
            if 'downloaded_files' in book_info and book_info['downloaded_files']:
                # Multi-PDF support (new format)
                pdf_paths = book_info['downloaded_files']
            elif 'download_path' in book_info and book_info['download_path']:
                # Single PDF support (legacy format)
                pdf_paths = [book_info['download_path']]
            else:
                raise Exception("No PDF files found in book_info (missing 'downloaded_files' or 'download_path')")
            
            if not pdf_paths:
                raise Exception("PDF paths list is empty")
            
            # Calculate total file size
            total_file_size = 0
            for pdf_path in pdf_paths:
                total_file_size += self.check_pdf_size(pdf_path)
            
            threshold_bytes = 30 * 1024 * 1024  # 30MB
            
            processing_method = None
            summary = None
            author = book_info.get('author', '')
            
            if total_file_size > threshold_bytes:
                # Large file: Try OCR first (OCR samples pages, so file size doesn't matter)
                # Only fall back to Google Search if OCR fails
                self.logger.info(f"Total PDF size ({total_file_size / (1024*1024):.2f} MB) > 30MB, attempting OCR (samples pages)")
                
                try:
                    # Try OCR for large files (pypdf text extraction may be slow for large files)
                    summary = self.generate_summary_from_pdf(pdf_paths[0], book_title, author)
                    if summary:
                        processing_method = 'pdf_extract'  # Actually used PDF/OCR
                    else:
                        raise Exception("PDF/OCR returned empty summary")
                except Exception as pdf_error:
                    self.logger.warning(f"PDF/OCR failed for large file, falling back to Google Search: {pdf_error}")
                    processing_method = 'google_search'
                    summary = self.generate_summary_from_search(book_title, author)
            else:
                # Use PDF extraction method for small files
                # For multiple PDFs, process the first one (usually contains main content)
                processing_method = 'pdf_extract'
                self.logger.info(f"Total PDF size ({total_file_size / (1024*1024):.2f} MB) <= 30MB, using PDF extraction method")
                self.logger.info(f"Processing first PDF of {len(pdf_paths)} files: {pdf_paths[0]}")
                summary = self.generate_summary_from_pdf(pdf_paths[0], book_title, author)
            
            # Create result with metadata
            result = {
                'title': book_title,
                'summary': summary,
                'processing_method': processing_method,
                'file_size_bytes': total_file_size,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'pdf_url': book_info.get('pdf_url', book_info.get('pdf_urls', [''])[0] if book_info.get('pdf_urls') else ''),
                'filename': book_info.get('filename', book_info.get('filenames', [''])[0] if book_info.get('filenames') else '')
            }
            
            self.logger.info(f"Successfully processed book: {book_title} using {processing_method}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing book {book_info.get('title', 'Unknown')}: {e}")
            raise 
   
    def retry_on_failure(self, func, *args, max_retries: int = 3, delay: int = 10, **kwargs) -> Any:
        """
        Enhanced retry mechanism for API calls with exponential backoff and rate limit handling
        
        Args:
            func: Function to retry
            *args: Positional arguments for the function
            max_retries: Maximum number of retry attempts (default: 3)
            delay: Initial delay between retries in seconds (default: 10)
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the successful function call
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                if attempt > 0:
                    # Calculate exponential backoff delay
                    wait_time = delay * (2 ** (attempt - 1))
                    self.logger.info(f"Retrying API call in {wait_time} seconds... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(wait_time)
                
                self.logger.info(f"Attempting Gemini API call (attempt {attempt + 1}/{max_retries + 1})")
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    self.logger.info(f"API call succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check for specific API error types
                if 'rate limit' in error_msg or 'quota' in error_msg or '429' in error_msg:
                    # Rate limit error - use a fixed longer delay
                    wait_time = 30  # Increase to 30s for quota limits
                    self.logger.warning(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    self.logger.info(f"Rate limit backoff: waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                elif 'authentication' in error_msg or 'api key' in error_msg or '401' in error_msg:
                    # Authentication error - don't retry
                    self.logger.error(f"Authentication error - not retrying: {e}")
                    raise e
                elif 'invalid' in error_msg and 'request' in error_msg or '400' in error_msg:
                    # Invalid request - don't retry
                    self.logger.error(f"Invalid request error - not retrying: {e}")
                    raise e
                elif 'service unavailable' in error_msg or '503' in error_msg:
                    # Service unavailable - retry with longer delay
                    service_delay = delay * (2 ** attempt) + 30  # Add extra 30 seconds for service issues
                    self.logger.warning(f"Service unavailable (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if attempt < max_retries:
                        self.logger.info(f"Service unavailable backoff: waiting {service_delay} seconds")
                        time.sleep(service_delay)
                    continue
                elif 'timeout' in error_msg or 'timed out' in error_msg:
                    # Timeout error - retry with standard backoff
                    self.logger.warning(f"Timeout error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    continue
                else:
                    # Generic error - retry with standard backoff
                    self.logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    continue
        
        # All attempts failed
        self.logger.error(f"All {max_retries + 1} Gemini API attempts failed. Last error: {last_exception}")
        
        # Provide more specific error message based on the last exception
        if last_exception:
            error_msg = str(last_exception).lower()
            if 'rate limit' in error_msg or 'quota' in error_msg:
                raise Exception(f"Gemini API rate limit exceeded after {max_retries + 1} attempts. Please try again later.")
            elif 'authentication' in error_msg or 'api key' in error_msg:
                raise Exception(f"Gemini API authentication failed. Please check your API key.")
            elif 'service unavailable' in error_msg:
                raise Exception(f"Gemini API service is currently unavailable. Please try again later.")
            else:
                raise Exception(f"Gemini API failed after {max_retries + 1} attempts: {last_exception}")
        else:
            raise Exception(f"Gemini API failed after {max_retries + 1} attempts with unknown error")
    
    def generate_summary_with_retry(self, book_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate book summary with retry mechanism
        
        Args:
            book_info: Dictionary containing book information
            
        Returns:
            Dict containing processed book information with summary
            
        Raises:
            Exception: If all retry attempts fail
        """
        return self.retry_on_failure(self.process_book, book_info)


# Example usage and testing functions
def create_test_book_info(title: str, pdf_path: str) -> Dict[str, Any]:
    """
    Create test book info dictionary
    
    Args:
        title: Book title
        pdf_path: Path to PDF file
        
    Returns:
        Dict with book information
    """
    return {
        'title': title,
        'download_path': pdf_path,
        'pdf_url': f'https://example.com/{os.path.basename(pdf_path)}',
        'filename': os.path.basename(pdf_path)
    }


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Example API key (replace with actual key)
    api_key = "your-gemini-api-key-here"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if os.path.exists(pdf_path):
            try:
                processor = GeminiProcessor(api_key)
                book_info = create_test_book_info("Test Book", pdf_path)
                result = processor.generate_summary_with_retry(book_info)
                print(f"Summary: {result['summary']}")
                print(f"Method: {result['processing_method']}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"File not found: {pdf_path}")
    else:
        print("Usage: python gemini_processor.py <pdf_path>")