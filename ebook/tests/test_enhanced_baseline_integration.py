#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for Enhanced Baseline Manager
Tests integration with existing progress_manager functionality
"""

import os
import logging
from datetime import datetime, date
from enhanced_baseline_manager import (
    EnhancedBaselineManagerWithBackup, 
    ContentType,
    create_carousel_baseline_key,
    create_cancellation_baseline_key,
    create_news_baseline_key,
    create_media_baseline_key
)

def test_enhanced_baseline_integration():
    """Test enhanced baseline manager integration with existing functionality"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("Testing Enhanced Baseline Manager Integration...")
    
    # Create enhanced baseline manager with backup
    ebm = EnhancedBaselineManagerWithBackup("integration_test", ".")
    
    # Test 1: Basic baseline functionality
    print("\n1. Testing basic baseline functionality...")
    
    # Set baselines for different content types
    test_baselines = [
        (ContentType.CAROUSEL.value, "latest_banner", "New Course Banner", {"image_url": "banner.jpg"}),
        (ContentType.CANCELLATION.value, "latest_date", "2024-11-06", {"course_count": 2}),
        (ContentType.NEWS.value, "latest_title", "Important Update", {"priority": "high"}),
        (ContentType.MEDIA.value, "latest_course", "Meditation Series", {"speaker": "Master Chen"})
    ]
    
    for content_type, key, value, metadata in test_baselines:
        success = ebm.set_content_baseline(content_type, key, value, metadata)
        print(f"  Set {content_type} baseline: {success}")
        
        # Test baseline comparison
        comparison = ebm.compare_with_baseline(content_type, key, value)
        print(f"  {content_type} comparison (same): is_new={comparison['is_new']}")
        
        # Test with different value
        comparison_new = ebm.compare_with_baseline(content_type, key, value + "_new")
        print(f"  {content_type} comparison (different): is_new={comparison_new['is_new']}")
    
    # Test 2: Content-specific baseline key generation
    print("\n2. Testing content-specific baseline key generation...")
    
    carousel_key = create_carousel_baseline_key("Test Banner", datetime.now())
    cancellation_key = create_cancellation_baseline_key(date.today())
    news_key = create_news_baseline_key("Test News", date.today())
    media_key = create_media_baseline_key("Test Course", date.today())
    
    print(f"  Carousel key: {carousel_key}")
    print(f"  Cancellation key: {cancellation_key}")
    print(f"  News key: {news_key}")
    print(f"  Media key: {media_key}")
    
    # Test 3: Date-based and title-based detection
    print("\n3. Testing content detection methods...")
    
    # Test date-based detection
    is_new_date = ebm.detect_new_content_by_date(ContentType.NEWS.value, datetime.now())
    print(f"  New content by date (current): {is_new_date}")
    
    old_date = datetime(2020, 1, 1)
    is_old_date = ebm.detect_new_content_by_date(ContentType.NEWS.value, old_date)
    print(f"  New content by date (old): {is_old_date}")
    
    # Test title-based detection
    is_new_title = ebm.detect_new_content_by_title(ContentType.CAROUSEL.value, "Different Banner")
    print(f"  New content by title (different): {is_new_title}")
    
    is_same_title = ebm.detect_new_content_by_title(ContentType.CAROUSEL.value, "New Course Banner")
    print(f"  New content by title (same): {is_same_title}")
    
    # Test 4: Backup and restoration
    print("\n4. Testing backup and restoration...")
    
    # Create manual backup
    backup_path = ebm.create_manual_backup("integration_test")
    print(f"  Created backup: {backup_path}")
    
    # Modify baselines
    ebm.set_content_baseline(ContentType.CAROUSEL.value, "latest_banner", "Modified Banner")
    
    # Verify modification
    modified_comparison = ebm.compare_with_baseline(ContentType.CAROUSEL.value, "latest_banner", "New Course Banner")
    print(f"  After modification, original is new: {modified_comparison['is_new']}")
    
    # Restore from backup
    restore_success = ebm.restore_from_backup(backup_path)
    print(f"  Restore successful: {restore_success}")
    
    # Verify restoration
    restored_comparison = ebm.compare_with_baseline(ContentType.CAROUSEL.value, "latest_banner", "New Course Banner")
    print(f"  After restore, original is new: {restored_comparison['is_new']}")
    
    # Test 5: Statistics and history
    print("\n5. Testing statistics and history...")
    
    stats = ebm.get_content_type_statistics()
    print(f"  Content type statistics: {len(stats)} types")
    
    for content_type, stat in stats.items():
        print(f"    {content_type}: processed={stat['total_processed']}, has_baseline={stat['has_baseline']}")
    
    # Test processed count updates
    ebm.update_content_processed_count(ContentType.CAROUSEL.value, 5)
    ebm.update_content_processed_count(ContentType.NEWS.value, 3)
    
    updated_stats = ebm.get_content_type_statistics()
    print(f"  After count updates:")
    print(f"    Carousel processed: {updated_stats[ContentType.CAROUSEL.value]['total_processed']}")
    print(f"    News processed: {updated_stats[ContentType.NEWS.value]['total_processed']}")
    
    # Test 6: Backup management
    print("\n6. Testing backup management...")
    
    # List backups
    backups = ebm.list_backups()
    print(f"  Available backups: {len(backups)}")
    
    for backup in backups:
        print(f"    {backup['filename']}: {backup['backup_name']} ({backup['content_types_count']} types)")
    
    # Test 7: Integration with existing progress manager functionality
    print("\n7. Testing progress manager integration...")
    
    # Test session functionality (inherited from ProgressManager)
    session_id = ebm.start_new_session({
        'baseline_book_title': 'Integration Test',
        'target_url': 'https://test.com',
        'download_dir': 'test_downloads'
    })
    print(f"  Started session: {session_id}")
    
    # Get session summary
    summary = ebm.get_session_summary()
    print(f"  Session active: {summary['session_active']}")
    print(f"  Session status: {summary['status']}")
    
    # Mark session completed
    ebm.mark_session_completed()
    
    # Cleanup
    print("\n8. Cleanup...")
    
    # Cleanup caches
    ebm.cleanup_cache(force=True)
    ebm.cleanup_baseline_cache(force=True)
    
    # Cleanup backups
    deleted_count = ebm.cleanup_old_backups(keep_count=0, keep_days=0)
    print(f"  Deleted {deleted_count} backup files")
    
    print("\nIntegration test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_enhanced_baseline_integration()
    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()