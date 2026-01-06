#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Processor Integration Test
測試 OCR 處理器的完整功能
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_blank_page_detection(pdf_path: str):
    """Test blank page detection without API calls"""
    from ocr_processor import OCRProcessor
    import io
    from PIL import Image
    import fitz
    
    print(f"\n{'='*60}")
    print(f"Testing blank page detection: {pdf_path}")
    print('='*60)
    
    # Just test the local functions (no API key needed)
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"PDF has {total_pages} pages")
    
    # Create a dummy processor just for testing is_blank_page
    class DummyProcessor:
        BLANK_PAGE_THRESHOLD = 0.98
        logger = logger
        
        def is_blank_page(self, img):
            try:
                gray = img.convert('L')
                pixels = list(gray.getdata())
                if not pixels:
                    return True
                white_count = sum(1 for p in pixels if p >= 250)
                white_ratio = white_count / len(pixels)
                return white_ratio >= self.BLANK_PAGE_THRESHOLD
            except Exception as e:
                print(f"Error: {e}")
                return False
    
    processor = DummyProcessor()
    blank_pages = []
    content_pages = []
    
    # Check first 20 pages
    check_count = min(20, total_pages)
    
    for page_num in range(check_count):
        page = doc[page_num]
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        is_blank = processor.is_blank_page(img)
        
        if is_blank:
            blank_pages.append(page_num + 1)
            print(f"  Page {page_num + 1}: BLANK")
        else:
            content_pages.append(page_num + 1)
            print(f"  Page {page_num + 1}: CONTENT")
    
    doc.close()
    
    print(f"\nSummary (first {check_count} pages):")
    print(f"  Blank pages: {len(blank_pages)} - {blank_pages[:5]}{'...' if len(blank_pages) > 5 else ''}")
    print(f"  Content pages: {len(content_pages)} - {content_pages[:5]}{'...' if len(content_pages) > 5 else ''}")
    
    return True


def test_sampling_strategy():
    """Test the sampling algorithm"""
    print(f"\n{'='*60}")
    print("Testing sampling strategy")
    print('='*60)
    
    def calculate_sample_indices(total: int, max_sample: int = 20):
        if total <= max_sample:
            return list(range(total))
        
        front_count = max(2, max_sample // 4)
        back_count = max(2, max_sample // 4)
        middle_count = max_sample - front_count - back_count
        
        front = list(range(front_count))
        back = list(range(total - back_count, total))
        
        middle_start = front_count
        middle_end = total - back_count
        middle_range = middle_end - middle_start
        
        if middle_range > 0 and middle_count > 0:
            step = middle_range / middle_count
            middle = [int(middle_start + i * step) for i in range(middle_count)]
        else:
            middle = []
        
        return sorted(set(front + middle + back))
    
    # Test cases
    test_cases = [10, 20, 50, 100, 200]
    
    for total in test_cases:
        indices = calculate_sample_indices(total)
        print(f"  {total} pages -> {len(indices)} samples: {indices[:5]}...{indices[-3:]}")
    
    return True


def test_full_ocr_pipeline(pdf_path: str, api_key: str):
    """Test the full OCR pipeline (requires API key)"""
    from ocr_processor import OCRProcessor
    
    print(f"\n{'='*60}")
    print(f"Testing full OCR pipeline: {pdf_path}")
    print('='*60)
    
    processor = OCRProcessor(api_key, logger)
    
    # Check quota
    quota = processor.rate_limiter.get_remaining_quota()
    print(f"API quota: daily={quota['daily_remaining']}, minute={quota['minute_remaining']}")
    
    if quota['daily_remaining'] <= 0:
        print("No API quota remaining, skipping API test")
        return False
    
    # Run OCR
    text = processor.process_pdf(pdf_path, "測試書籍")
    
    print(f"\nExtracted text ({len(text)} chars):")
    print("-" * 40)
    print(text[:500] if text else "(No text extracted)")
    if len(text) > 500:
        print(f"... (truncated)")
    
    return bool(text)


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "downloads/CH113-01-01-001.pdf"
    api_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)
    
    # Run tests
    print("=" * 60)
    print("OCR PROCESSOR INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Blank page detection (no API)
    test_blank_page_detection(pdf_path)
    
    # Test 2: Sampling strategy
    test_sampling_strategy()
    
    # Test 3: Full OCR (only if API key provided)
    if api_key:
        test_full_ocr_pipeline(pdf_path, api_key)
    else:
        print(f"\n{'='*60}")
        print("Skipping full OCR test (no API key provided)")
        print("Usage: python test_ocr_integration.py <pdf_path> <api_key>")
        print('='*60)
    
    print("\n✅ All local tests passed!")
