#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Enhanced Baseline Management
Tests baseline tracking, comparison, and backup/restoration functionality
"""

import os
import json
import logging
import tempfile
import shutil
from datetime import datetime, date, timedelta
from enhanced_baseline_manager import (
    EnhancedBaselineManager,
    EnhancedBaselineManagerWithBackup,
    BaselineBackupManager,
    ContentType,
    BaselineEntry,
    ContentBaseline,
    create_carousel_baseline_key,
    create_cancellation_baseline_key,
    create_news_baseline_key,
    create_media_baseline_key
)


class TestBaselineTracking:
    """Test baseline tracking for all content types"""
    
    def __init__(self, test_dir):
        self.test_dir = test_dir
        self.logger = logging.getLogger(__name__)
        self.ebm = None
    
    def setup(self):
        """Set up test environment"""
        self.ebm = EnhancedBaselineManager("test_baseline_tracking", self.test_dir)
    
    def teardown(self):
        """Clean up test environment"""
        if self.ebm:
            self.ebm.cleanup_baseline_cache(force=True)
    
    def test_set_baseline_for_carousel(self):
        """Test setting baseline for carousel content"""
        print("  Testing carousel baseline tracking...")
        
        content_type = ContentType.CAROUSEL.value
        baseline_key = "latest_banner"
        baseline_value = "Test Banner Title"
        metadata = {"image_url": "test.jpg", "activity_link": "https://test.com"}
        
        # Set baseline
        success = self.ebm.set_content_baseline(content_type, baseline_key, baseline_value, metadata)
        assert success, "Failed to set carousel baseline"
        
        # Verify baseline was set
        baseline = self.ebm.get_content_baseline(content_type)
        assert baseline is not None, "Baseline not found"
        assert baseline.last_baseline_key == baseline_key, "Baseline key mismatch"
        assert baseline.last_baseline_value == baseline_value, "Baseline value mismatch"
        
        print("    ✓ Carousel baseline set and retrieved successfully")
        return True
    
    def test_set_baseline_for_cancellation(self):
        """Test setting baseline for cancellation content"""
        print("  Testing cancellation baseline tracking...")
        
        content_type = ContentType.CANCELLATION.value
        baseline_key = "latest_date"
        baseline_value = "2024-11-06"
        metadata = {"course_count": 3}
        
        # Set baseline
        success = self.ebm.set_content_baseline(content_type, baseline_key, baseline_value, metadata)
        assert success, "Failed to set cancellation baseline"
        
        # Verify baseline
        baseline = self.ebm.get_content_baseline(content_type)
        assert baseline is not None, "Baseline not found"
        assert baseline.last_baseline_value == baseline_value, "Baseline value mismatch"
        
        print("    ✓ Cancellation baseline set and retrieved successfully")
        return True
    
    def test_set_baseline_for_news(self):
        """Test setting baseline for news content"""
        print("  Testing news baseline tracking...")
        
        content_type = ContentType.NEWS.value
        baseline_key = "latest_title"
        baseline_value = "Important Announcement"
        metadata = {"priority": "high", "publication_date": "2024-11-06"}
        
        # Set baseline
        success = self.ebm.set_content_baseline(content_type, baseline_key, baseline_value, metadata)
        assert success, "Failed to set news baseline"
        
        # Verify baseline
        baseline = self.ebm.get_content_baseline(content_type)
        assert baseline is not None, "Baseline not found"
        assert baseline.last_baseline_value == baseline_value, "Baseline value mismatch"
        
        print("    ✓ News baseline set and retrieved successfully")
        return True
    
    def test_set_baseline_for_media(self):
        """Test setting baseline for media content"""
        print("  Testing media baseline tracking...")
        
        content_type = ContentType.MEDIA.value
        baseline_key = "latest_course"
        baseline_value = "Meditation Course"
        metadata = {"speaker": "Master Chen", "start_date": "2024-11-10"}
        
        # Set baseline
        success = self.ebm.set_content_baseline(content_type, baseline_key, baseline_value, metadata)
        assert success, "Failed to set media baseline"
        
        # Verify baseline
        baseline = self.ebm.get_content_baseline(content_type)
        assert baseline is not None, "Baseline not found"
        assert baseline.last_baseline_value == baseline_value, "Baseline value mismatch"
        
        print("    ✓ Media baseline set and retrieved successfully")
        return True
    
    def test_baseline_history_tracking(self):
        """Test that baseline history is tracked correctly"""
        print("  Testing baseline history tracking...")
        
        content_type = ContentType.CAROUSEL.value
        
        # Set initial baseline
        self.ebm.set_content_baseline(content_type, "key1", "value1", {"version": 1})
        
        # Update baseline multiple times
        self.ebm.set_content_baseline(content_type, "key2", "value2", {"version": 2})
        self.ebm.set_content_baseline(content_type, "key3", "value3", {"version": 3})
        
        # Get baseline history
        history = self.ebm.get_baseline_history(content_type)
        
        assert len(history) >= 2, f"Expected at least 2 history entries, got {len(history)}"
        
        # Verify history entries exist (order may vary based on implementation)
        history_values = [entry.baseline_value for entry in history]
        assert "value1" in history_values, "First value not in history"
        assert "value2" in history_values, "Second value not in history"
        
        # Verify current baseline is the latest
        current_baseline = self.ebm.get_content_baseline(content_type)
        assert current_baseline.last_baseline_value == "value3", "Current baseline should be latest"
        
        print(f"    ✓ Baseline history tracked correctly ({len(history)} entries)")
        return True
    
    def test_get_all_content_baselines(self):
        """Test retrieving all content baselines"""
        print("  Testing get all content baselines...")
        
        # Set baselines for multiple content types
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "value1")
        self.ebm.set_content_baseline(ContentType.NEWS.value, "key2", "value2")
        self.ebm.set_content_baseline(ContentType.MEDIA.value, "key3", "value3")
        
        # Get all baselines
        all_baselines = self.ebm.get_all_content_baselines()
        
        assert len(all_baselines) >= 3, f"Expected at least 3 baselines, got {len(all_baselines)}"
        assert ContentType.CAROUSEL.value in all_baselines, "Carousel baseline not found"
        assert ContentType.NEWS.value in all_baselines, "News baseline not found"
        assert ContentType.MEDIA.value in all_baselines, "Media baseline not found"
        
        print(f"    ✓ Retrieved all baselines ({len(all_baselines)} types)")
        return True
    
    def run_all_tests(self):
        """Run all baseline tracking tests"""
        print("\n=== Testing Baseline Tracking ===")
        
        self.setup()
        
        try:
            self.test_set_baseline_for_carousel()
            self.test_set_baseline_for_cancellation()
            self.test_set_baseline_for_news()
            self.test_set_baseline_for_media()
            self.test_baseline_history_tracking()
            self.test_get_all_content_baselines()
            
            print("✓ All baseline tracking tests passed")
            return True
        finally:
            self.teardown()


class TestBaselineComparison:
    """Test baseline comparison and update logic"""
    
    def __init__(self, test_dir):
        self.test_dir = test_dir
        self.logger = logging.getLogger(__name__)
        self.ebm = None
    
    def setup(self):
        """Set up test environment"""
        self.ebm = EnhancedBaselineManager("test_baseline_comparison", self.test_dir)
    
    def teardown(self):
        """Clean up test environment"""
        if self.ebm:
            self.ebm.cleanup_baseline_cache(force=True)
    
    def test_compare_with_no_baseline(self):
        """Test comparison when no baseline exists"""
        print("  Testing comparison with no baseline...")
        
        content_type = ContentType.CAROUSEL.value
        
        # Compare without setting baseline first
        result = self.ebm.compare_with_baseline(content_type, "test_key", "test_value")
        
        assert result["is_new"] == True, "Should be new when no baseline exists"
        assert result["reason"] == "no_baseline_exists", "Reason should be no_baseline_exists"
        assert result["baseline_info"] is None, "Baseline info should be None"
        
        print("    ✓ Correctly identified new content when no baseline exists")
        return True
    
    def test_compare_with_matching_baseline(self):
        """Test comparison with matching baseline"""
        print("  Testing comparison with matching baseline...")
        
        content_type = ContentType.NEWS.value
        baseline_key = "latest_title"
        baseline_value = "Test News"
        
        # Set baseline
        self.ebm.set_content_baseline(content_type, baseline_key, baseline_value)
        
        # Compare with same value
        result = self.ebm.compare_with_baseline(content_type, baseline_key, baseline_value)
        
        assert result["is_new"] == False, "Should not be new when baseline matches"
        assert result["reason"] == "matches_baseline", "Reason should be matches_baseline"
        assert result["comparison_details"]["matches_baseline"] == True, "Should match baseline"
        
        print("    ✓ Correctly identified matching baseline")
        return True
    
    def test_compare_with_different_value(self):
        """Test comparison with different value"""
        print("  Testing comparison with different value...")
        
        content_type = ContentType.MEDIA.value
        baseline_key = "latest_course"
        baseline_value = "Original Course"
        
        # Set baseline
        self.ebm.set_content_baseline(content_type, baseline_key, baseline_value)
        
        # Compare with different value
        new_value = "New Course"
        result = self.ebm.compare_with_baseline(content_type, baseline_key, new_value)
        
        assert result["is_new"] == True, "Should be new when value differs"
        assert result["reason"] == "content_changed", "Reason should be content_changed"
        assert result["comparison_details"]["value_changed"] == True, "Value should be marked as changed"
        
        print("    ✓ Correctly identified changed content")
        return True
    
    def test_compare_with_different_key(self):
        """Test comparison with different key"""
        print("  Testing comparison with different key...")
        
        content_type = ContentType.CANCELLATION.value
        baseline_key = "latest_date"
        baseline_value = "2024-11-06"
        
        # Set baseline
        self.ebm.set_content_baseline(content_type, baseline_key, baseline_value)
        
        # Compare with different key
        new_key = "different_key"
        result = self.ebm.compare_with_baseline(content_type, new_key, baseline_value)
        
        assert result["is_new"] == True, "Should be new when key differs"
        assert result["comparison_details"]["key_changed"] == True, "Key should be marked as changed"
        
        print("    ✓ Correctly identified changed key")
        return True
    
    def test_detect_new_content_by_date(self):
        """Test date-based content detection"""
        print("  Testing date-based content detection...")
        
        content_type = ContentType.NEWS.value
        
        # Set baseline with current time
        self.ebm.set_content_baseline(content_type, "test_key", "test_value")
        
        # Test with future date (should be new)
        future_date = datetime.now() + timedelta(days=1)
        is_new_future = self.ebm.detect_new_content_by_date(content_type, future_date)
        assert is_new_future == True, "Future date should be detected as new"
        
        # Test with past date (should not be new)
        past_date = datetime.now() - timedelta(days=1)
        is_new_past = self.ebm.detect_new_content_by_date(content_type, past_date)
        assert is_new_past == False, "Past date should not be detected as new"
        
        print("    ✓ Date-based detection working correctly")
        return True
    
    def test_detect_new_content_by_title(self):
        """Test title-based content detection"""
        print("  Testing title-based content detection...")
        
        content_type = ContentType.CAROUSEL.value
        baseline_title = "Original Banner Title"
        
        # Set baseline
        self.ebm.set_content_baseline(content_type, "latest_banner", baseline_title)
        
        # Test with same title (should not be new)
        is_new_same = self.ebm.detect_new_content_by_title(content_type, baseline_title)
        assert is_new_same == False, "Same title should not be detected as new"
        
        # Test with different title (should be new)
        different_title = "New Banner Title"
        is_new_different = self.ebm.detect_new_content_by_title(content_type, different_title)
        assert is_new_different == True, "Different title should be detected as new"
        
        print("    ✓ Title-based detection working correctly")
        return True
    
    def test_update_processed_count(self):
        """Test updating processed count"""
        print("  Testing processed count updates...")
        
        content_type = ContentType.MEDIA.value
        
        # Set initial baseline
        self.ebm.set_content_baseline(content_type, "test_key", "test_value")
        
        # Update processed count
        self.ebm.update_content_processed_count(content_type, 5)
        self.ebm.update_content_processed_count(content_type, 3)
        
        # Verify count
        baseline = self.ebm.get_content_baseline(content_type)
        assert baseline.total_items_processed == 8, f"Expected 8 processed items, got {baseline.total_items_processed}"
        
        print("    ✓ Processed count updated correctly")
        return True
    
    def run_all_tests(self):
        """Run all baseline comparison tests"""
        print("\n=== Testing Baseline Comparison and Update Logic ===")
        
        self.setup()
        
        try:
            self.test_compare_with_no_baseline()
            self.test_compare_with_matching_baseline()
            self.test_compare_with_different_value()
            self.test_compare_with_different_key()
            self.test_detect_new_content_by_date()
            self.test_detect_new_content_by_title()
            self.test_update_processed_count()
            
            print("✓ All baseline comparison tests passed")
            return True
        finally:
            self.teardown()


class TestBackupAndRestoration:
    """Test backup and restoration functionality"""
    
    def __init__(self, test_dir):
        self.test_dir = test_dir
        self.logger = logging.getLogger(__name__)
        self.ebm = None
    
    def setup(self):
        """Set up test environment"""
        self.ebm = EnhancedBaselineManagerWithBackup("test_backup", self.test_dir, self.test_dir)
    
    def teardown(self):
        """Clean up test environment"""
        if self.ebm:
            self.ebm.cleanup_baseline_cache(force=True)
            self.ebm.cleanup_old_backups(keep_count=0, keep_days=0)
    
    def test_create_manual_backup(self):
        """Test creating manual backup"""
        print("  Testing manual backup creation...")
        
        # Set some baselines
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "value1")
        self.ebm.set_content_baseline(ContentType.NEWS.value, "key2", "value2")
        
        # Create backup
        backup_path = self.ebm.create_manual_backup("test_manual")
        
        assert os.path.exists(backup_path), "Backup file not created"
        
        # Verify backup content
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        assert "backup_metadata" in backup_data, "Backup metadata missing"
        assert "baseline_data" in backup_data, "Baseline data missing"
        assert len(backup_data["baseline_data"]["content_baselines"]) >= 2, "Not all baselines backed up"
        
        print(f"    ✓ Manual backup created successfully: {os.path.basename(backup_path)}")
        return True
    
    def test_restore_from_backup(self):
        """Test restoring from backup"""
        print("  Testing backup restoration...")
        
        # Set initial baselines
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "original_value")
        self.ebm.set_content_baseline(ContentType.NEWS.value, "key2", "original_news")
        
        # Create backup
        backup_path = self.ebm.create_manual_backup("test_restore")
        
        # Modify baselines
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "modified_value")
        self.ebm.set_content_baseline(ContentType.NEWS.value, "key2", "modified_news")
        
        # Verify modification
        carousel_baseline = self.ebm.get_content_baseline(ContentType.CAROUSEL.value)
        assert carousel_baseline.last_baseline_value == "modified_value", "Baseline not modified"
        
        # Restore from backup
        restore_success = self.ebm.restore_from_backup(backup_path)
        assert restore_success, "Restore failed"
        
        # Verify restoration
        restored_carousel = self.ebm.get_content_baseline(ContentType.CAROUSEL.value)
        assert restored_carousel.last_baseline_value == "original_value", "Baseline not restored correctly"
        
        restored_news = self.ebm.get_content_baseline(ContentType.NEWS.value)
        assert restored_news.last_baseline_value == "original_news", "News baseline not restored correctly"
        
        print("    ✓ Backup restored successfully")
        return True
    
    def test_list_backups(self):
        """Test listing available backups"""
        print("  Testing backup listing...")
        
        # Create multiple backups
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "value1")
        
        backup1 = self.ebm.create_manual_backup("test_list_1")
        backup2 = self.ebm.create_manual_backup("test_list_2")
        
        # List backups
        backups = self.ebm.list_backups()
        
        assert len(backups) >= 2, f"Expected at least 2 backups, got {len(backups)}"
        
        # Verify backup info
        for backup in backups:
            assert "filename" in backup, "Backup filename missing"
            assert "path" in backup, "Backup path missing"
            assert "backup_name" in backup, "Backup name missing"
            assert os.path.exists(backup["path"]), f"Backup file not found: {backup['path']}"
        
        print(f"    ✓ Listed {len(backups)} backups successfully")
        return True
    
    def test_backup_with_history(self):
        """Test that backup includes baseline history"""
        print("  Testing backup with history...")
        
        content_type = ContentType.MEDIA.value
        
        # Create baseline with history
        self.ebm.set_content_baseline(content_type, "key1", "value1")
        self.ebm.set_content_baseline(content_type, "key2", "value2")
        self.ebm.set_content_baseline(content_type, "key3", "value3")
        
        # Create backup
        backup_path = self.ebm.create_manual_backup("test_history")
        
        # Load and verify backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        media_baseline = backup_data["baseline_data"]["content_baselines"].get(content_type)
        assert media_baseline is not None, "Media baseline not in backup"
        assert "baseline_history" in media_baseline, "Baseline history not in backup"
        assert len(media_baseline["baseline_history"]) >= 2, "Baseline history not complete"
        
        print("    ✓ Backup includes baseline history")
        return True
    
    def test_cleanup_old_backups(self):
        """Test cleaning up old backups"""
        print("  Testing backup cleanup...")
        
        # Create multiple backups
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "value1")
        
        for i in range(5):
            self.ebm.create_manual_backup(f"test_cleanup_{i}")
        
        # Verify backups created
        backups_before = self.ebm.list_backups()
        assert len(backups_before) >= 5, "Not all backups created"
        
        # Cleanup keeping only 2
        deleted_count = self.ebm.cleanup_old_backups(keep_count=2, keep_days=0)
        
        # Verify cleanup
        backups_after = self.ebm.list_backups()
        assert len(backups_after) <= 2, f"Expected at most 2 backups after cleanup, got {len(backups_after)}"
        assert deleted_count >= 3, f"Expected at least 3 deletions, got {deleted_count}"
        
        print(f"    ✓ Cleaned up {deleted_count} old backups")
        return True
    
    def test_export_import_baselines(self):
        """Test exporting and importing baselines"""
        print("  Testing baseline export/import...")
        
        # Set baselines
        self.ebm.set_content_baseline(ContentType.CAROUSEL.value, "key1", "value1", {"meta": "data1"})
        self.ebm.set_content_baseline(ContentType.NEWS.value, "key2", "value2", {"meta": "data2"})
        
        # Export baselines
        export_data = self.ebm.export_baselines_to_dict()
        
        assert "content_baselines" in export_data, "Export missing content_baselines"
        assert len(export_data["content_baselines"]) >= 2, "Not all baselines exported"
        
        # Clear baselines
        self.ebm.cleanup_baseline_cache(force=True)
        self.ebm = EnhancedBaselineManagerWithBackup("test_backup", self.test_dir, self.test_dir)
        
        # Import baselines
        import_success = self.ebm.import_baselines_from_dict(export_data)
        assert import_success, "Import failed"
        
        # Verify import
        carousel_baseline = self.ebm.get_content_baseline(ContentType.CAROUSEL.value)
        assert carousel_baseline is not None, "Carousel baseline not imported"
        assert carousel_baseline.last_baseline_value == "value1", "Carousel value not imported correctly"
        
        news_baseline = self.ebm.get_content_baseline(ContentType.NEWS.value)
        assert news_baseline is not None, "News baseline not imported"
        assert news_baseline.last_baseline_value == "value2", "News value not imported correctly"
        
        print("    ✓ Export/import working correctly")
        return True
    
    def run_all_tests(self):
        """Run all backup and restoration tests"""
        print("\n=== Testing Backup and Restoration Functionality ===")
        
        self.setup()
        
        try:
            self.test_create_manual_backup()
            self.test_restore_from_backup()
            self.test_list_backups()
            self.test_backup_with_history()
            self.test_cleanup_old_backups()
            self.test_export_import_baselines()
            
            print("✓ All backup and restoration tests passed")
            return True
        finally:
            self.teardown()


def run_all_unit_tests():
    """Run all unit tests for baseline management"""
    print("\n" + "="*60)
    print("BASELINE MANAGEMENT UNIT TESTS")
    print("="*60)
    
    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="baseline_test_")
    print(f"\nTest directory: {test_dir}")
    
    try:
        # Run test suites
        tracking_tests = TestBaselineTracking(test_dir)
        tracking_success = tracking_tests.run_all_tests()
        
        comparison_tests = TestBaselineComparison(test_dir)
        comparison_success = comparison_tests.run_all_tests()
        
        backup_tests = TestBackupAndRestoration(test_dir)
        backup_success = backup_tests.run_all_tests()
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Baseline Tracking Tests: {'✓ PASSED' if tracking_success else '✗ FAILED'}")
        print(f"Baseline Comparison Tests: {'✓ PASSED' if comparison_success else '✗ FAILED'}")
        print(f"Backup/Restoration Tests: {'✓ PASSED' if backup_success else '✗ FAILED'}")
        
        all_passed = tracking_success and comparison_success and backup_success
        
        if all_passed:
            print("\n✓ ALL UNIT TESTS PASSED")
        else:
            print("\n✗ SOME TESTS FAILED")
        
        return all_passed
        
    finally:
        # Cleanup test directory
        try:
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"\nWarning: Could not clean up test directory: {e}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,  # Set to WARNING to reduce noise during tests
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        success = run_all_unit_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
