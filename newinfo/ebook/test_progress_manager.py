#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ProgressManager module
"""

import os
import logging
import tempfile
from progress_manager import ProgressManager, create_test_book_info, create_test_processing_result


def test_progress_manager():
    """Test all ProgressManager functionality"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Testing in temporary directory: {temp_dir}")
        
        # Test 1: Create new session
        logger.info("=== Test 1: Create new session ===")
        pm = ProgressManager("test_newbook", temp_dir, logger)
        
        config = {
            'baseline_book_title': 'CH754-02',
            'target_url': 'https://www.budaedu.org',
            'download_dir': 'downloads'
        }
        
        session_id = pm.start_new_session(config)
        assert session_id is not None, "Session ID should not be None"
        logger.info(f"✓ Created session: {session_id}")
        
        # Test 2: Add processed books
        logger.info("=== Test 2: Add processed books ===")
        test_books = [
            ("佛教入門", "CH001.pdf", True),
            ("禪修指南", "CH002.pdf", True),
            ("心經解釋", "CH003.pdf", False)  # This one fails
        ]
        
        for title, filename, success in test_books:
            book_info = create_test_book_info(title, filename, success)
            if success:
                processing_result = create_test_processing_result('pdf_extract')
                pm.add_processed_book(book_info, processing_result)
            else:
                book_info['error_message'] = 'PDF extraction failed'
                pm.add_processed_book(book_info, None)
        
        logger.info("✓ Added test books")
        
        # Test 3: Check session summary
        logger.info("=== Test 3: Check session summary ===")
        summary = pm.get_session_summary()
        assert summary['books_processed'] == 2, f"Expected 2 processed books, got {summary['books_processed']}"
        assert summary['books_failed'] == 1, f"Expected 1 failed book, got {summary['books_failed']}"
        logger.info("✓ Session summary correct")
        
        # Test 4: Save and load progress
        logger.info("=== Test 4: Save and load progress ===")
        pm.save_progress(total_books=5, status="in_progress")
        
        # Create new manager and load progress
        pm2 = ProgressManager("test_newbook", temp_dir, logger)
        loaded_data = pm2.load_progress()
        
        assert loaded_data is not None, "Should load existing progress"
        assert pm2.session_id == session_id, "Session ID should match"
        
        processed_titles = pm2.get_processed_book_titles()
        assert len(processed_titles) == 2, f"Expected 2 processed titles, got {len(processed_titles)}"
        assert "佛教入門" in processed_titles, "Should contain first book title"
        assert "禪修指南" in processed_titles, "Should contain second book title"
        
        logger.info("✓ Save and load working correctly")
        
        # Test 5: Skip already processed books
        logger.info("=== Test 5: Skip already processed books ===")
        should_skip = pm2.should_skip_book("佛教入門")
        assert should_skip == True, "Should skip already processed book"
        
        should_not_skip = pm2.should_skip_book("新書標題")
        assert should_not_skip == False, "Should not skip new book"
        
        logger.info("✓ Skip logic working correctly")
        
        # Test 6: Mark session completed and cleanup
        logger.info("=== Test 6: Mark completed and cleanup ===")
        pm2.mark_session_completed()
        
        # Check cache file exists
        cache_path = pm2.cache_path
        assert os.path.exists(cache_path), "Cache file should exist after completion"
        
        # Test cleanup
        pm2.cleanup_cache()
        assert not os.path.exists(cache_path), "Cache file should be deleted after cleanup"
        
        logger.info("✓ Completion and cleanup working correctly")
        
        logger.info("=== All tests passed! ===")


if __name__ == "__main__":
    test_progress_manager()