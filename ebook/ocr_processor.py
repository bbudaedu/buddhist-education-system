#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Processor Module for Image-based PDF Processing
圖片型 PDF 的 OCR 處理模組

This module handles OCR processing for image-based PDFs using Google Gemini Vision API.
Supports:
- PDF to image conversion using PyMuPDF
- Blank page detection to skip unnecessary processing
- Smart page sampling to optimize API usage
- Rate limiting to comply with free tier limits
"""

import os
import io
import time
import base64
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from PIL import Image

# PyMuPDF for PDF processing
import fitz  # pymupdf

# Google Generative AI
import google.generativeai as genai


class RateLimiter:
    """
    Rate limiter for Gemini API calls to comply with free tier limits.
    
    Free tier limits (Gemini 2.5 Flash):
    - RPM: 10 requests per minute
    - RPD: 250 requests per day
    - TPM: 250,000 tokens per minute
    """
    
    def __init__(self, rpm: int = 10, rpd: int = 20, logger: Optional[logging.Logger] = None):
        """
        Initialize RateLimiter.
        
        Args:
            rpm: Requests per minute limit
            rpd: Requests per day limit (FREE TIER = 20!)
            logger: Logger instance
        """
        self.rpm = rpm
        self.rpd = rpd
        self.logger = logger or logging.getLogger(__name__)
        
        # Track request timestamps
        self.minute_calls: List[datetime] = []
        self.daily_calls = 0
        self.daily_reset_date = datetime.now().date()
    
    def _reset_daily_if_needed(self):
        """Reset daily counter if it's a new day."""
        today = datetime.now().date()
        if today > self.daily_reset_date:
            self.daily_calls = 0
            self.daily_reset_date = today
            self.logger.info("Daily rate limit counter reset")
    
    def _clean_minute_calls(self):
        """Remove calls older than 1 minute."""
        now = datetime.now()
        self.minute_calls = [t for t in self.minute_calls if now - t < timedelta(minutes=1)]
    
    def can_make_request(self) -> Tuple[bool, str]:
        """
        Check if a request can be made without exceeding limits.
        
        Returns:
            Tuple of (can_proceed, reason_if_not)
        """
        self._reset_daily_if_needed()
        self._clean_minute_calls()
        
        if self.daily_calls >= self.rpd:
            return False, f"Daily limit reached ({self.rpd} requests/day)"
        
        if len(self.minute_calls) >= self.rpm:
            return False, f"Minute limit reached ({self.rpm} requests/minute)"
        
        return True, ""
    
    def wait_if_needed(self) -> bool:
        """
        Wait until a request can be safely made.
        
        Returns:
            bool: True if request can proceed, False if daily limit reached
        """
        self._reset_daily_if_needed()
        
        # Check daily limit first
        if self.daily_calls >= self.rpd:
            self.logger.error(f"Daily rate limit reached ({self.rpd} requests/day). Cannot proceed.")
            return False
        
        # Clean and check minute calls
        self._clean_minute_calls()
        
        # Wait if minute limit would be exceeded
        if len(self.minute_calls) >= self.rpm:
            oldest_call = min(self.minute_calls)
            wait_time = 60 - (datetime.now() - oldest_call).seconds + 1
            self.logger.info(f"Rate limit: waiting {wait_time} seconds before next request...")
            time.sleep(wait_time)
            self._clean_minute_calls()
        
        return True
    
    def record_request(self):
        """Record that a request was made."""
        self.minute_calls.append(datetime.now())
        self.daily_calls += 1
        self.logger.debug(f"Request recorded. Daily: {self.daily_calls}/{self.rpd}, Minute: {len(self.minute_calls)}/{self.rpm}")
    
    def get_remaining_quota(self) -> Dict[str, int]:
        """Get remaining quota information."""
        self._reset_daily_if_needed()
        self._clean_minute_calls()
        
        return {
            'daily_remaining': self.rpd - self.daily_calls,
            'minute_remaining': self.rpm - len(self.minute_calls)
        }


class OCRProcessor:
    """
    OCR Processor for image-based PDFs using Gemini Vision API.
    
    Features:
    - PDF to image conversion
    - Blank page detection (local, no API cost)
    - Smart page sampling for large PDFs
    - Rate-limited API calls
    """
    
    # Configuration constants - OPTIMIZED FOR FREE TIER (20 RPD)
    MAX_PAGES_PER_REQUEST = 10  # Increased to reduce batch count
    MIN_SAMPLE_PAGES = 3  # Reduced for free tier
    MAX_SAMPLE_PAGES = 8  # Reduced: 8 pages = 1 API call
    IMAGE_DPI = 150  # DPI for PDF rendering
    MAX_IMAGE_DIMENSION = 1024  # Max width/height
    BLANK_PAGE_THRESHOLD = 0.98  # White pixel ratio
    
    def __init__(self, api_key: str, logger: Optional[logging.Logger] = None):
        """
        Initialize OCRProcessor.
        
        Args:
            api_key: Google Gemini API key
            logger: Logger instance
        """
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__)
        self.rate_limiter = RateLimiter(rpm=10, rpd=20, logger=self.logger)  # FREE TIER LIMIT
        
        # Initialize Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.logger.info("OCRProcessor initialized (FREE TIER: 20 requests/day)")
    
    def convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Image objects using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL Image objects for each page
        """
        images = []
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            self.logger.info(f"Converting PDF to images: {total_pages} pages")
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Render page to pixmap
                # Use zoom to control DPI (72 is default, 150/72 ≈ 2.08x zoom)
                zoom = self.IMAGE_DPI / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Resize if too large
                img = self._resize_image(img)
                
                images.append(img)
                
            doc.close()
            self.logger.info(f"Successfully converted {len(images)} pages to images")
            
        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {e}")
            raise
        
        return images
    
    def _resize_image(self, img: Image.Image) -> Image.Image:
        """
        Resize image if it exceeds maximum dimensions.
        
        Args:
            img: PIL Image
            
        Returns:
            Resized image (or original if within limits)
        """
        width, height = img.size
        
        if width <= self.MAX_IMAGE_DIMENSION and height <= self.MAX_IMAGE_DIMENSION:
            return img
        
        # Calculate scaling factor
        scale = min(self.MAX_IMAGE_DIMENSION / width, self.MAX_IMAGE_DIMENSION / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def is_blank_page(self, img: Image.Image) -> bool:
        """
        Detect if a page is blank using pixel analysis.
        This is a local operation - no API cost.
        
        Args:
            img: PIL Image
            
        Returns:
            bool: True if page appears to be blank
        """
        try:
            # Convert to grayscale
            gray = img.convert('L')
            pixels = list(gray.getdata())
            
            if not pixels:
                return True
            
            # Count near-white pixels (>=250 out of 255)
            white_threshold = 250
            white_count = sum(1 for p in pixels if p >= white_threshold)
            white_ratio = white_count / len(pixels)
            
            is_blank = white_ratio >= self.BLANK_PAGE_THRESHOLD
            
            if is_blank:
                self.logger.debug(f"Blank page detected (white ratio: {white_ratio:.2%})")
            
            return is_blank
            
        except Exception as e:
            self.logger.warning(f"Error detecting blank page: {e}")
            return False
    
    def filter_blank_pages(self, images: List[Image.Image]) -> Tuple[List[Image.Image], List[int]]:
        """
        Filter out blank pages from the image list.
        
        Args:
            images: List of PIL Images
            
        Returns:
            Tuple of (filtered images, original page indices)
        """
        filtered_images = []
        page_indices = []
        
        for idx, img in enumerate(images):
            if not self.is_blank_page(img):
                filtered_images.append(img)
                page_indices.append(idx)
        
        blank_count = len(images) - len(filtered_images)
        self.logger.info(f"Filtered out {blank_count} blank pages, {len(filtered_images)} pages remaining")
        
        return filtered_images, page_indices
    
    def sample_pages(self, images: List[Image.Image], page_indices: List[int]) -> Tuple[List[Image.Image], List[int]]:
        """
        Sample representative pages from a large PDF.
        Strategy: Front + Middle + Back sampling.
        
        Args:
            images: List of content (non-blank) images
            page_indices: Original page indices
            
        Returns:
            Tuple of (sampled images, sampled page indices)
        """
        total = len(images)
        
        if total <= self.MAX_SAMPLE_PAGES:
            self.logger.info(f"PDF has {total} content pages, no sampling needed")
            return images, page_indices
        
        # Calculate sample distribution
        # Front 25%, Middle 50%, Back 25% of sample budget
        sample_budget = self.MAX_SAMPLE_PAGES
        front_count = max(2, sample_budget // 4)
        back_count = max(2, sample_budget // 4)
        middle_count = sample_budget - front_count - back_count
        
        # Select indices
        front_indices = list(range(front_count))
        back_indices = list(range(total - back_count, total))
        
        # Middle: evenly distributed
        middle_start = front_count
        middle_end = total - back_count
        middle_range = middle_end - middle_start
        
        if middle_range > 0 and middle_count > 0:
            step = middle_range / middle_count
            middle_indices = [int(middle_start + i * step) for i in range(middle_count)]
        else:
            middle_indices = []
        
        # Combine and deduplicate
        all_indices = sorted(set(front_indices + middle_indices + back_indices))
        
        sampled_images = [images[i] for i in all_indices]
        sampled_page_indices = [page_indices[i] for i in all_indices]
        
        self.logger.info(f"Sampled {len(sampled_images)} pages from {total} content pages")
        self.logger.debug(f"Sampled page indices: {sampled_page_indices}")
        
        return sampled_images, sampled_page_indices
    
    def _image_to_base64(self, img: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def extract_text_from_images(self, images: List[Image.Image], book_title: str = "") -> str:
        """
        Extract text from images using Gemini Vision API.
        Processes in batches to comply with rate limits.
        
        Args:
            images: List of PIL Images
            book_title: Book title for context
            
        Returns:
            Extracted text content
        """
        if not images:
            return ""
        
        all_text = []
        
        # Process in batches
        for batch_start in range(0, len(images), self.MAX_PAGES_PER_REQUEST):
            batch_end = min(batch_start + self.MAX_PAGES_PER_REQUEST, len(images))
            batch = images[batch_start:batch_end]
            
            self.logger.info(f"Processing batch: pages {batch_start + 1} to {batch_end} of {len(images)}")
            
            # Wait for rate limit
            if not self.rate_limiter.wait_if_needed():
                self.logger.error("Rate limit exceeded, stopping OCR")
                break
            
            try:
                batch_text = self._ocr_batch(batch, book_title)
                if batch_text:
                    all_text.append(batch_text)
                
                self.rate_limiter.record_request()
                
            except Exception as e:
                self.logger.error(f"Error processing batch: {e}")
                # Continue with next batch
                continue
        
        # Combine all extracted text
        combined_text = "\n\n".join(all_text)
        self.logger.info(f"OCR complete: extracted {len(combined_text)} characters")
        
        return combined_text
    
    def _ocr_batch(self, images: List[Image.Image], book_title: str = "") -> str:
        """
        Perform OCR on a batch of images.
        
        Args:
            images: Batch of PIL Images
            book_title: Book title for context
            
        Returns:
            Extracted text from the batch
        """
        try:
            # Build prompt
            context = f"這是書籍「{book_title}」的掃描頁面。" if book_title else "這是書籍的掃描頁面。"
            
            prompt = f"""{context}

請執行 OCR，提取這些頁面中的所有繁體中文文字內容。

重要指示：
- 直接輸出識別到的文字，不要加任何說明
- 保持文字的段落結構
- 忽略頁碼、頁首頁尾等非正文內容
- 如果頁面是目錄、版權頁等，簡要標註即可"""
            
            # Build content parts
            content_parts = [prompt]
            
            for img in images:
                # Convert image to bytes for Gemini
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()
                
                content_parts.append({
                    'mime_type': 'image/png',
                    'data': base64.b64encode(image_bytes).decode('utf-8')
                })
            
            # Call Gemini Vision API
            response = self.model.generate_content(content_parts)
            
            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            
            return ""
            
        except Exception as e:
            self.logger.error(f"OCR batch error: {e}")
            raise
    
    def process_pdf(self, pdf_path: str, book_title: str = "") -> str:
        """
        Main entry point: Process an image-based PDF and extract text.
        
        Workflow:
        1. Convert PDF pages to images
        2. Filter out blank pages
        3. Sample pages if too many
        4. OCR selected pages
        5. Return combined text
        
        Args:
            pdf_path: Path to the PDF file
            book_title: Book title for context
            
        Returns:
            Extracted text content
        """
        self.logger.info(f"Starting OCR processing for: {pdf_path}")
        
        try:
            # Check remaining quota
            quota = self.rate_limiter.get_remaining_quota()
            self.logger.info(f"API quota: {quota['daily_remaining']} daily, {quota['minute_remaining']} per minute")
            
            if quota['daily_remaining'] <= 0:
                self.logger.error("No daily API quota remaining")
                return ""
            
            # Step 1: Convert PDF to images
            images = self.convert_pdf_to_images(pdf_path)
            if not images:
                self.logger.warning("No images extracted from PDF")
                return ""
            
            # Step 2: Filter blank pages
            content_images, page_indices = self.filter_blank_pages(images)
            if not content_images:
                self.logger.warning("All pages appear to be blank")
                return ""
            
            # Step 3: Sample if needed
            sampled_images, sampled_indices = self.sample_pages(content_images, page_indices)
            
            # Step 4: OCR
            extracted_text = self.extract_text_from_images(sampled_images, book_title)
            
            self.logger.info(f"OCR processing complete for: {book_title or pdf_path}")
            
            return extracted_text
            
        except Exception as e:
            self.logger.error(f"OCR processing failed: {e}")
            raise


# Testing function
def test_ocr_processor():
    """Test the OCR processor with a sample PDF."""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 3:
        print("Usage: python ocr_processor.py <api_key> <pdf_path> [book_title]")
        print("  or:  python ocr_processor.py --test <pdf_path>")
        return
    
    if sys.argv[1] == '--test':
        # Quick test mode - just verify PDF processing
        pdf_path = sys.argv[2]
        if not os.path.exists(pdf_path):
            print(f"File not found: {pdf_path}")
            return
        
        print(f"Testing PDF processing: {pdf_path}")
        
        # Just test PDF to image conversion and blank detection
        doc = fitz.open(pdf_path)
        print(f"PDF has {len(doc)} pages")
        
        for i in range(min(3, len(doc))):
            page = doc[i]
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            print(f"  Page {i+1}: {img.size}")
        
        doc.close()
        print("PDF processing test complete!")
        return
    
    api_key = sys.argv[1]
    pdf_path = sys.argv[2]
    book_title = sys.argv[3] if len(sys.argv) > 3 else ""
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    processor = OCRProcessor(api_key)
    text = processor.process_pdf(pdf_path, book_title)
    
    print("\n" + "="*60)
    print("EXTRACTED TEXT:")
    print("="*60)
    print(text[:2000] if len(text) > 2000 else text)
    if len(text) > 2000:
        print(f"\n... (truncated, total {len(text)} characters)")


if __name__ == "__main__":
    test_ocr_processor()
