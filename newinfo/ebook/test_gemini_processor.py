#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for GeminiProcessor module
"""

import os
import logging
from gemini_processor import GeminiProcessor, create_test_book_info

def test_pdf_size_checking():
    """Test PDF size checking functionality"""
    print("Testing PDF size checking...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('test')
    
    # Test with a dummy API key (won't be used for size checking)
    processor = GeminiProcessor("dummy-key", logger)
    
    # Test with existing PDF files
    test_files = [
        "test/CH375-02-01-001.pdf",
        "test/CH380-37-01-001.pdf",
        "test/CH381-02-01-001.pdf"
    ]
    
    for pdf_path in test_files:
        if os.path.exists(pdf_path):
            try:
                file_size = processor.check_pdf_size(pdf_path)
                file_size_mb = file_size / (1024 * 1024)
                threshold_mb = 30
                
                print(f"✓ {pdf_path}: {file_size_mb:.2f} MB")
                
                if file_size_mb > threshold_mb:
                    print(f"  → Would use Google Search method")
                else:
                    print(f"  → Would use PDF extraction method")
                    
            except Exception as e:
                print(f"✗ Error checking {pdf_path}: {e}")
        else:
            print(f"✗ File not found: {pdf_path}")

def test_pdf_text_extraction():
    """Test PDF text extraction functionality"""
    print("\nTesting PDF text extraction...")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('test')
    
    # Test with a dummy API key (won't be used for text extraction)
    processor = GeminiProcessor("dummy-key", logger)
    
    # Test with one PDF file
    test_file = "test/CH375-02-01-001.pdf"
    
    if os.path.exists(test_file):
        try:
            text = processor.extract_pdf_text(test_file)
            if text:
                print(f"✓ Successfully extracted {len(text)} characters from {test_file}")
                print(f"  Preview: {text[:200]}...")
            else:
                print(f"✗ No text extracted from {test_file}")
        except Exception as e:
            print(f"✗ Error extracting text from {test_file}: {e}")
    else:
        print(f"✗ Test file not found: {test_file}")

def test_book_info_creation():
    """Test book info creation helper function"""
    print("\nTesting book info creation...")
    
    test_file = "test/CH375-02-01-001.pdf"
    book_info = create_test_book_info("測試書籍", test_file)
    
    expected_keys = ['title', 'download_path', 'pdf_url', 'filename']
    
    print(f"✓ Created book info with keys: {list(book_info.keys())}")
    
    for key in expected_keys:
        if key in book_info:
            print(f"  ✓ {key}: {book_info[key]}")
        else:
            print(f"  ✗ Missing key: {key}")

if __name__ == "__main__":
    print("=== GeminiProcessor Test Suite ===")
    
    try:
        test_pdf_size_checking()
        test_pdf_text_extraction()
        test_book_info_creation()
        
        print("\n=== Test Summary ===")
        print("✓ All basic functionality tests completed")
        print("Note: API-dependent tests require valid Gemini API key")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")