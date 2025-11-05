#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration example showing how to use GeminiProcessor in the main application
"""

import logging
from gemini_processor import GeminiProcessor

def example_integration():
    """Example of how to integrate GeminiProcessor into the main application"""
    
    # Set up logging (this would be done in the main app)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('MainApp')
    
    # Configuration (this would come from ConfigManager)
    config = {
        'gemini_api_key': 'your-api-key-here',  # Replace with actual key
    }
    
    # Sample book information (this would come from BookScraper)
    book_info = {
        'title': '觀楞伽經記',
        'download_path': 'test/CH375-02-01-001.pdf',
        'pdf_url': 'https://www.budaedu.org/ebook/CH375-02-01-001.pdf',
        'filename': 'CH375-02-01-001.pdf'
    }
    
    try:
        # Initialize AI processor
        logger.info("Initializing Gemini AI processor...")
        ai_processor = GeminiProcessor(config['gemini_api_key'], logger)
        
        # Process the book (with retry mechanism)
        logger.info(f"Processing book: {book_info['title']}")
        result = ai_processor.generate_summary_with_retry(book_info)
        
        # Display results
        logger.info("Processing completed successfully!")
        print("\n=== Processing Results ===")
        print(f"Book Title: {result['title']}")
        print(f"Processing Method: {result['processing_method']}")
        print(f"File Size: {result['file_size_bytes'] / (1024*1024):.2f} MB")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Summary: {result['summary']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing book: {e}")
        return None

if __name__ == "__main__":
    print("=== GeminiProcessor Integration Example ===")
    print("Note: This example requires a valid Gemini API key")
    print("Replace 'your-api-key-here' with your actual API key to test")
    
    # Uncomment the line below to run the example with a real API key
    # example_integration()
    
    print("\nExample code structure shown above.")
    print("Integration points:")
    print("1. ConfigManager provides API key")
    print("2. BookScraper provides book_info dictionary")
    print("3. GeminiProcessor generates summaries with retry logic")
    print("4. Results are passed to DocumentGenerator and EmailSender")