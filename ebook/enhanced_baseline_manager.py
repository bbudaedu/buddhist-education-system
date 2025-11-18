#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Baseline Management Module for Website Monitoring System
網站監控系統的增強基線管理模組

This module extends the existing progress_manager functionality to handle
multiple content types including carousel, cancellation, news, and media content.
"""

import os
import json
import time
import uuid
import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from progress_manager import ProgressManager


class ContentType(Enum):
    """Enumeration of supported content types for baseline management"""
    CAROUSEL = 'carousel'
    CANCELLATION = 'cancellation'
    NEWS = 'news'
    MEDIA = 'media'
    BOOKS = 'books'  # Original book content type


@dataclass
class BaselineEntry:
    """
    Represents a baseline entry for content comparison
    """
    content_type: str
    baseline_key: str
    baseline_value: str
    last_updated: str
    extraction_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContentBaseline:
    """
    Represents baseline information for a specific content type
    """
    content_type: str
    last_baseline_key: str
    last_baseline_value: str
    last_updated: datetime
    total_items_processed: int = 0
    baseline_history: List[BaselineEntry] = None
    
    def __post_init__(self):
        if self.baseline_history is None:
            self.baseline_history = []


class EnhancedBaselineManager(ProgressManager):
    """
    Enhanced baseline manager that extends ProgressManager functionality
    to handle multiple content types with baseline tracking and comparison logic.
    
    Integrates with existing historical baseline functionality while adding
    support for carousel, cancellation, news, and media content types.
    """
    
    def __init__(self, project_name: str = "website_monitoring", 
                 cache_dir: str = ".", logger: Optional[logging.Logger] = None):
        """
        Initialize EnhancedBaselineManager
        
        Args:
            project_name: Name of the project for cache file naming
            cache_dir: Directory to store cache files
            logger: Logger instance for logging operations
        """
        super().__init__(project_name, cache_dir, logger)
        
        # Enhanced cache filename for baseline management
        self.baseline_cache_filename = f".{project_name}_baseline_cache.json"
        self.baseline_cache_path = os.path.join(cache_dir, self.baseline_cache_filename)
        
        # Content type baselines
        self.content_baselines: Dict[str, ContentBaseline] = {}
        
        # Load existing baselines
        self._load_baseline_cache()
        
        self.logger.info(f"EnhancedBaselineManager initialized for project: {project_name}")
        self.logger.info(f"Baseline cache path: {self.baseline_cache_path}")
    
    def _create_baseline_cache_structure(self) -> Dict[str, Any]:
        """
        Create the baseline cache structure for multiple content types
        
        Returns:
            Dict: Empty baseline cache structure
        """
        current_time = datetime.now().isoformat()
        
        return {
            "project_name": self.project_name,
            "created_time": current_time,
            "last_updated": current_time,
            "content_baselines": {},
            "baseline_history": [],
            "configuration": {
                "max_history_entries": 100,
                "baseline_comparison_enabled": True,
                "auto_backup_enabled": True
            }
        }
    
    def _load_baseline_cache(self) -> bool:
        """
        Load baseline cache from file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.baseline_cache_path):
                self.logger.info("No existing baseline cache found, creating new one")
                self.baseline_cache_data = self._create_baseline_cache_structure()
                return True
            
            self.logger.info(f"Loading baseline cache from: {self.baseline_cache_path}")
            
            with open(self.baseline_cache_path, 'r', encoding='utf-8') as f:
                self.baseline_cache_data = json.load(f)
            
            # Load content baselines into memory
            self._load_content_baselines_from_cache()
            
            self.logger.info(f"Loaded baseline cache with {len(self.content_baselines)} content types")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading baseline cache: {e}")
            self.baseline_cache_data = self._create_baseline_cache_structure()
            return False
    
    def _load_content_baselines_from_cache(self):
        """Load content baselines from cache data into memory objects"""
        try:
            content_baselines_data = self.baseline_cache_data.get("content_baselines", {})
            
            for content_type, baseline_data in content_baselines_data.items():
                # Convert string datetime back to datetime object
                last_updated_str = baseline_data.get("last_updated", datetime.now().isoformat())
                last_updated = datetime.fromisoformat(last_updated_str)
                
                # Load baseline history
                history_data = baseline_data.get("baseline_history", [])
                baseline_history = []
                for entry_data in history_data:
                    baseline_entry = BaselineEntry(
                        content_type=entry_data.get("content_type", content_type),
                        baseline_key=entry_data.get("baseline_key", ""),
                        baseline_value=entry_data.get("baseline_value", ""),
                        last_updated=entry_data.get("last_updated", ""),
                        extraction_count=entry_data.get("extraction_count", 0),
                        metadata=entry_data.get("metadata", {})
                    )
                    baseline_history.append(baseline_entry)
                
                # Create ContentBaseline object
                content_baseline = ContentBaseline(
                    content_type=content_type,
                    last_baseline_key=baseline_data.get("last_baseline_key", ""),
                    last_baseline_value=baseline_data.get("last_baseline_value", ""),
                    last_updated=last_updated,
                    total_items_processed=baseline_data.get("total_items_processed", 0),
                    baseline_history=baseline_history
                )
                
                self.content_baselines[content_type] = content_baseline
                
        except Exception as e:
            self.logger.error(f"Error loading content baselines from cache: {e}")
    
    def _save_baseline_cache(self) -> bool:
        """
        Save baseline cache to file using atomic write
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Update cache data with current baselines
            self.baseline_cache_data["last_updated"] = datetime.now().isoformat()
            self.baseline_cache_data["content_baselines"] = {}
            
            for content_type, baseline in self.content_baselines.items():
                # Convert ContentBaseline to dict for JSON serialization
                baseline_data = {
                    "content_type": baseline.content_type,
                    "last_baseline_key": baseline.last_baseline_key,
                    "last_baseline_value": baseline.last_baseline_value,
                    "last_updated": baseline.last_updated.isoformat(),
                    "total_items_processed": baseline.total_items_processed,
                    "baseline_history": []
                }
                
                # Convert baseline history to dict
                for entry in baseline.baseline_history:
                    entry_data = asdict(entry)
                    baseline_data["baseline_history"].append(entry_data)
                
                self.baseline_cache_data["content_baselines"][content_type] = baseline_data
            
            # Use atomic write with temporary file
            temp_file = self.baseline_cache_path + '.tmp'
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.baseline_cache_data, f, ensure_ascii=False, indent=2)
                
                # Replace original file atomically
                if os.path.exists(self.baseline_cache_path):
                    os.remove(self.baseline_cache_path)
                os.rename(temp_file, self.baseline_cache_path)
                
                self.logger.debug(f"Baseline cache saved to: {self.baseline_cache_path}")
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
                
        except Exception as e:
            self.logger.error(f"Error saving baseline cache: {e}")
            return False
    
    def get_content_baseline(self, content_type: str) -> Optional[ContentBaseline]:
        """
        Get baseline information for a specific content type
        
        Args:
            content_type: Type of content (carousel, cancellation, news, media, books)
            
        Returns:
            ContentBaseline: Baseline information or None if not found
        """
        return self.content_baselines.get(content_type)
    
    def set_content_baseline(self, content_type: str, baseline_key: str, 
                           baseline_value: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set or update baseline for a specific content type
        
        Args:
            content_type: Type of content
            baseline_key: Key identifier for the baseline (e.g., 'latest_title', 'latest_date')
            baseline_value: Value of the baseline
            metadata: Additional metadata for the baseline
            
        Returns:
            bool: True if baseline set successfully
        """
        try:
            current_time = datetime.now()
            
            # Get existing baseline or create new one
            if content_type in self.content_baselines:
                baseline = self.content_baselines[content_type]
                
                # Create history entry from current baseline
                if baseline.last_baseline_key and baseline.last_baseline_value:
                    history_entry = BaselineEntry(
                        content_type=content_type,
                        baseline_key=baseline.last_baseline_key,
                        baseline_value=baseline.last_baseline_value,
                        last_updated=baseline.last_updated.isoformat(),
                        extraction_count=baseline.total_items_processed,
                        metadata=metadata or {}
                    )
                    baseline.baseline_history.append(history_entry)
                    
                    # Limit history size
                    max_history = self.baseline_cache_data.get("configuration", {}).get("max_history_entries", 100)
                    if len(baseline.baseline_history) > max_history:
                        baseline.baseline_history = baseline.baseline_history[-max_history:]
                
                # Update baseline
                baseline.last_baseline_key = baseline_key
                baseline.last_baseline_value = baseline_value
                baseline.last_updated = current_time
                
            else:
                # Create new baseline
                baseline = ContentBaseline(
                    content_type=content_type,
                    last_baseline_key=baseline_key,
                    last_baseline_value=baseline_value,
                    last_updated=current_time,
                    total_items_processed=0,
                    baseline_history=[]
                )
                self.content_baselines[content_type] = baseline
            
            # Save to cache
            success = self._save_baseline_cache()
            
            if success:
                self.logger.info(f"Updated baseline for {content_type}: {baseline_key}={baseline_value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error setting baseline for {content_type}: {e}")
            return False
    
    def compare_with_baseline(self, content_type: str, current_key: str, 
                            current_value: str) -> Dict[str, Any]:
        """
        Compare current content with baseline to detect new items
        
        Args:
            content_type: Type of content to compare
            current_key: Current content key
            current_value: Current content value
            
        Returns:
            Dict: Comparison result with is_new, baseline_info, and comparison_details
        """
        try:
            baseline = self.get_content_baseline(content_type)
            
            if not baseline:
                # No baseline exists, consider as new
                return {
                    "is_new": True,
                    "reason": "no_baseline_exists",
                    "baseline_info": None,
                    "current_info": {
                        "key": current_key,
                        "value": current_value
                    },
                    "comparison_details": {
                        "baseline_key": None,
                        "baseline_value": None,
                        "matches_baseline": False
                    }
                }
            
            # Compare with current baseline
            matches_baseline = (
                baseline.last_baseline_key == current_key and 
                baseline.last_baseline_value == current_value
            )
            
            comparison_result = {
                "is_new": not matches_baseline,
                "reason": "content_changed" if not matches_baseline else "matches_baseline",
                "baseline_info": {
                    "key": baseline.last_baseline_key,
                    "value": baseline.last_baseline_value,
                    "last_updated": baseline.last_updated.isoformat(),
                    "total_processed": baseline.total_items_processed
                },
                "current_info": {
                    "key": current_key,
                    "value": current_value
                },
                "comparison_details": {
                    "baseline_key": baseline.last_baseline_key,
                    "baseline_value": baseline.last_baseline_value,
                    "matches_baseline": matches_baseline,
                    "key_changed": baseline.last_baseline_key != current_key,
                    "value_changed": baseline.last_baseline_value != current_value
                }
            }
            
            self.logger.debug(f"Baseline comparison for {content_type}: is_new={comparison_result['is_new']}")
            
            return comparison_result
            
        except Exception as e:
            self.logger.error(f"Error comparing with baseline for {content_type}: {e}")
            return {
                "is_new": True,
                "reason": "comparison_error",
                "error": str(e),
                "baseline_info": None,
                "current_info": {"key": current_key, "value": current_value}
            }
    
    def update_content_processed_count(self, content_type: str, increment: int = 1) -> bool:
        """
        Update the processed count for a content type
        
        Args:
            content_type: Type of content
            increment: Number to increment by (default: 1)
            
        Returns:
            bool: True if updated successfully
        """
        try:
            baseline = self.get_content_baseline(content_type)
            
            if baseline:
                baseline.total_items_processed += increment
                success = self._save_baseline_cache()
                
                if success:
                    self.logger.debug(f"Updated processed count for {content_type}: {baseline.total_items_processed}")
                
                return success
            else:
                self.logger.warning(f"No baseline found for content type: {content_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating processed count for {content_type}: {e}")
            return False
    
    def get_baseline_history(self, content_type: str, limit: Optional[int] = None) -> List[BaselineEntry]:
        """
        Get baseline history for a content type
        
        Args:
            content_type: Type of content
            limit: Maximum number of history entries to return
            
        Returns:
            List[BaselineEntry]: List of historical baseline entries
        """
        baseline = self.get_content_baseline(content_type)
        
        if not baseline:
            return []
        
        history = baseline.baseline_history
        
        if limit and len(history) > limit:
            return history[-limit:]
        
        return history
    
    def get_all_content_baselines(self) -> Dict[str, ContentBaseline]:
        """
        Get all content baselines
        
        Returns:
            Dict[str, ContentBaseline]: Dictionary of all content baselines
        """
        return self.content_baselines.copy()
    
    def detect_new_content_by_date(self, content_type: str, content_date: Union[str, date, datetime]) -> bool:
        """
        Detect new content based on date comparison with baseline
        
        Args:
            content_type: Type of content
            content_date: Date of the content to check
            
        Returns:
            bool: True if content is newer than baseline date
        """
        try:
            # Convert content_date to datetime if needed
            if isinstance(content_date, str):
                try:
                    content_datetime = datetime.fromisoformat(content_date)
                except ValueError:
                    # Try parsing as date only
                    content_datetime = datetime.strptime(content_date, '%Y-%m-%d')
            elif isinstance(content_date, date) and not isinstance(content_date, datetime):
                content_datetime = datetime.combine(content_date, datetime.min.time())
            else:
                content_datetime = content_date
            
            baseline = self.get_content_baseline(content_type)
            
            if not baseline:
                # No baseline, consider as new
                return True
            
            # Compare with baseline date
            baseline_datetime = baseline.last_updated
            
            is_newer = content_datetime > baseline_datetime
            
            self.logger.debug(f"Date comparison for {content_type}: content={content_datetime}, baseline={baseline_datetime}, is_newer={is_newer}")
            
            return is_newer
            
        except Exception as e:
            self.logger.error(f"Error detecting new content by date for {content_type}: {e}")
            return True  # Default to considering as new on error
    
    def detect_new_content_by_title(self, content_type: str, content_title: str) -> bool:
        """
        Detect new content based on title comparison with baseline
        
        Args:
            content_type: Type of content
            content_title: Title of the content to check
            
        Returns:
            bool: True if content title is different from baseline
        """
        try:
            baseline = self.get_content_baseline(content_type)
            
            if not baseline:
                # No baseline, consider as new
                return True
            
            # Compare with baseline title
            baseline_title = baseline.last_baseline_value
            
            is_different = content_title.strip() != baseline_title.strip()
            
            self.logger.debug(f"Title comparison for {content_type}: content='{content_title}', baseline='{baseline_title}', is_different={is_different}")
            
            return is_different
            
        except Exception as e:
            self.logger.error(f"Error detecting new content by title for {content_type}: {e}")
            return True  # Default to considering as new on error
    
    def get_content_type_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all content types
        
        Returns:
            Dict: Statistics for each content type
        """
        statistics = {}
        
        for content_type, baseline in self.content_baselines.items():
            statistics[content_type] = {
                "total_processed": baseline.total_items_processed,
                "last_updated": baseline.last_updated.isoformat(),
                "last_baseline_key": baseline.last_baseline_key,
                "last_baseline_value": baseline.last_baseline_value,
                "history_entries": len(baseline.baseline_history),
                "has_baseline": bool(baseline.last_baseline_key and baseline.last_baseline_value)
            }
        
        return statistics
    
    def cleanup_baseline_cache(self, force: bool = False) -> bool:
        """
        Clean up baseline cache file
        
        Args:
            force: If True, delete cache regardless of status
            
        Returns:
            bool: True if cleaned up successfully
        """
        try:
            if not os.path.exists(self.baseline_cache_path):
                self.logger.info("No baseline cache file to clean up")
                return True
            
            if not force:
                # Check if we should keep the cache
                total_baselines = len(self.content_baselines)
                if total_baselines > 0:
                    self.logger.info(f"Keeping baseline cache with {total_baselines} content types")
                    return False
            
            # Delete the cache file
            os.remove(self.baseline_cache_path)
            self.logger.info(f"Baseline cache file deleted: {self.baseline_cache_path}")
            
            # Clear baseline data
            self.content_baselines.clear()
            self.baseline_cache_data = self._create_baseline_cache_structure()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up baseline cache: {e}")
            return False
    
    def export_baselines_to_dict(self) -> Dict[str, Any]:
        """
        Export all baselines to a dictionary for backup or transfer
        
        Returns:
            Dict: Complete baseline data
        """
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "project_name": self.project_name,
                "content_baselines": {}
            }
            
            for content_type, baseline in self.content_baselines.items():
                baseline_data = {
                    "content_type": baseline.content_type,
                    "last_baseline_key": baseline.last_baseline_key,
                    "last_baseline_value": baseline.last_baseline_value,
                    "last_updated": baseline.last_updated.isoformat(),
                    "total_items_processed": baseline.total_items_processed,
                    "baseline_history": []
                }
                
                # Export history
                for entry in baseline.baseline_history:
                    entry_data = asdict(entry)
                    baseline_data["baseline_history"].append(entry_data)
                
                export_data["content_baselines"][content_type] = baseline_data
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting baselines: {e}")
            return {}
    
    def import_baselines_from_dict(self, import_data: Dict[str, Any]) -> bool:
        """
        Import baselines from a dictionary (for restore functionality)
        
        Args:
            import_data: Baseline data to import
            
        Returns:
            bool: True if imported successfully
        """
        try:
            if "content_baselines" not in import_data:
                self.logger.error("Invalid import data: missing content_baselines")
                return False
            
            # Clear existing baselines
            self.content_baselines.clear()
            
            # Import baselines
            for content_type, baseline_data in import_data["content_baselines"].items():
                # Convert datetime strings back to datetime objects
                last_updated_str = baseline_data.get("last_updated", datetime.now().isoformat())
                last_updated = datetime.fromisoformat(last_updated_str)
                
                # Import baseline history
                history_data = baseline_data.get("baseline_history", [])
                baseline_history = []
                for entry_data in history_data:
                    baseline_entry = BaselineEntry(
                        content_type=entry_data.get("content_type", content_type),
                        baseline_key=entry_data.get("baseline_key", ""),
                        baseline_value=entry_data.get("baseline_value", ""),
                        last_updated=entry_data.get("last_updated", ""),
                        extraction_count=entry_data.get("extraction_count", 0),
                        metadata=entry_data.get("metadata", {})
                    )
                    baseline_history.append(baseline_entry)
                
                # Create ContentBaseline object
                content_baseline = ContentBaseline(
                    content_type=content_type,
                    last_baseline_key=baseline_data.get("last_baseline_key", ""),
                    last_baseline_value=baseline_data.get("last_baseline_value", ""),
                    last_updated=last_updated,
                    total_items_processed=baseline_data.get("total_items_processed", 0),
                    baseline_history=baseline_history
                )
                
                self.content_baselines[content_type] = content_baseline
            
            # Save imported data
            success = self._save_baseline_cache()
            
            if success:
                imported_count = len(self.content_baselines)
                self.logger.info(f"Successfully imported {imported_count} content baselines")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error importing baselines: {e}")
            return False
    
    def get_cancellation_baseline(self) -> Optional[str]:
        """
        Get the latest cancellation baseline date
        
        Returns:
            str: Latest cancellation date or None if not found
        """
        try:
            baseline = self.get_content_baseline(ContentType.CANCELLATION.value)
            if baseline and baseline.last_baseline_value:
                return baseline.last_baseline_value
            return None
        except Exception as e:
            self.logger.error(f"Error getting cancellation baseline: {e}")
            return None
    
    def update_cancellation_baseline(self, latest_date: str) -> bool:
        """
        Update the cancellation baseline with the latest date
        
        Args:
            latest_date: Latest cancellation date found
            
        Returns:
            bool: True if updated successfully
        """
        try:
            baseline_key = create_cancellation_baseline_key(datetime.strptime(latest_date, '%Y-%m-%d').date())
            return self.set_content_baseline(
                ContentType.CANCELLATION.value,
                baseline_key,
                latest_date,
                {"update_timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            self.logger.error(f"Error updating cancellation baseline: {e}")
            return False


# Content-specific baseline management functions
def create_carousel_baseline_key(banner_title: str, extraction_timestamp: datetime) -> str:
    """
    Create a baseline key for carousel content
    
    Args:
        banner_title: Title of the carousel banner
        extraction_timestamp: When the content was extracted
        
    Returns:
        str: Baseline key for carousel content
    """
    return f"carousel_{extraction_timestamp.strftime('%Y%m%d_%H%M%S')}_{banner_title[:50]}"


def create_cancellation_baseline_key(latest_date: date) -> str:
    """
    Create a baseline key for cancellation content
    
    Args:
        latest_date: Latest cancellation date found
        
    Returns:
        str: Baseline key for cancellation content
    """
    return f"cancellation_{latest_date.strftime('%Y%m%d')}"


def create_news_baseline_key(latest_title: str, publication_date: date) -> str:
    """
    Create a baseline key for news content
    
    Args:
        latest_title: Title of the latest news item
        publication_date: Publication date of the news
        
    Returns:
        str: Baseline key for news content
    """
    return f"news_{publication_date.strftime('%Y%m%d')}_{latest_title[:50]}"


def create_media_baseline_key(latest_course_title: str, start_date: date) -> str:
    """
    Create a baseline key for media content
    
    Args:
        latest_course_title: Title of the latest course
        start_date: Start date of the course
        
    Returns:
        str: Baseline key for media content
    """
    return f"media_{start_date.strftime('%Y%m%d')}_{latest_course_title[:50]}"


# Example usage and testing functions
if __name__ == "__main__":
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create test enhanced baseline manager
    ebm = EnhancedBaselineManager("test_website_monitoring")
    
    print("Testing EnhancedBaselineManager...")
    
    # Test setting baselines for different content types
    test_data = [
        (ContentType.CAROUSEL.value, "latest_banner", "Test Banner Title", {"image_url": "test.jpg"}),
        (ContentType.CANCELLATION.value, "latest_date", "2024-01-15", {"course_count": 3}),
        (ContentType.NEWS.value, "latest_title", "Important Announcement", {"priority": "high"}),
        (ContentType.MEDIA.value, "latest_course", "Meditation Course", {"speaker": "Teacher A"})
    ]
    
    for content_type, key, value, metadata in test_data:
        success = ebm.set_content_baseline(content_type, key, value, metadata)
        print(f"Set baseline for {content_type}: {success}")
    
    # Test baseline comparison
    for content_type, key, value, _ in test_data:
        # Test with same value (should not be new)
        result = ebm.compare_with_baseline(content_type, key, value)
        print(f"Comparison for {content_type} (same): is_new={result['is_new']}")
        
        # Test with different value (should be new)
        result = ebm.compare_with_baseline(content_type, key, value + "_changed")
        print(f"Comparison for {content_type} (changed): is_new={result['is_new']}")
    
    # Test statistics
    stats = ebm.get_content_type_statistics()
    print(f"Content type statistics: {stats}")
    
    # Test export/import
    export_data = ebm.export_baselines_to_dict()
    print(f"Exported {len(export_data.get('content_baselines', {}))} baselines")
    
    # Clean up test cache
    ebm.cleanup_baseline_cache(force=True)
    print("Test completed")


class BaselineBackupManager:
    """
    Manages baseline backup and restoration functionality
    Integrates with existing configuration backup system
    """
    
    def __init__(self, baseline_manager: EnhancedBaselineManager, 
                 backup_dir: str = ".", logger: Optional[logging.Logger] = None):
        """
        Initialize BaselineBackupManager
        
        Args:
            baseline_manager: EnhancedBaselineManager instance
            backup_dir: Directory to store backup files
            logger: Logger instance
        """
        self.baseline_manager = baseline_manager
        self.backup_dir = backup_dir
        self.logger = logger or logging.getLogger(__name__)
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        self.logger.info(f"BaselineBackupManager initialized with backup dir: {backup_dir}")
    
    def create_baseline_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of current baselines using existing configuration backup system pattern
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            str: Path to the created backup file
        """
        try:
            # Generate backup filename using existing pattern
            if backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.baseline_manager.project_name}_baseline_backup_{backup_name}_{timestamp}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.baseline_manager.project_name}_baseline_backup_{timestamp}.json"
            
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Export current baselines
            baseline_data = self.baseline_manager.export_baselines_to_dict()
            
            # Add backup metadata
            backup_data = {
                "backup_metadata": {
                    "backup_name": backup_name or "auto_backup",
                    "backup_timestamp": datetime.now().isoformat(),
                    "project_name": self.baseline_manager.project_name,
                    "baseline_cache_path": self.baseline_manager.baseline_cache_path,
                    "content_types_count": len(baseline_data.get("content_baselines", {})),
                    "backup_version": "1.0"
                },
                "baseline_data": baseline_data
            }
            
            # Save backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Baseline backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error creating baseline backup: {e}")
            raise
    
    def restore_baseline_from_backup(self, backup_path: str, 
                                   create_restore_backup: bool = True) -> bool:
        """
        Restore baselines from a backup file with rollback capabilities
        
        Args:
            backup_path: Path to the backup file
            create_restore_backup: Whether to create a backup before restoring
            
        Returns:
            bool: True if restored successfully
        """
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create a backup of current state before restoring (if requested)
            restore_backup_path = None
            if create_restore_backup:
                try:
                    restore_backup_path = self.create_baseline_backup("pre_restore")
                    self.logger.info(f"Created pre-restore backup: {restore_backup_path}")
                except Exception as e:
                    self.logger.warning(f"Could not create pre-restore backup: {e}")
            
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup structure
            if not self._validate_backup_structure(backup_data):
                self.logger.error("Invalid backup file structure")
                return False
            
            # Extract baseline data
            baseline_data = backup_data.get("baseline_data", {})
            
            # Import baselines
            success = self.baseline_manager.import_baselines_from_dict(baseline_data)
            
            if success:
                backup_metadata = backup_data.get("backup_metadata", {})
                backup_timestamp = backup_metadata.get("backup_timestamp", "unknown")
                content_count = backup_metadata.get("content_types_count", 0)
                
                self.logger.info(f"Successfully restored baselines from backup: {backup_path}")
                self.logger.info(f"Backup timestamp: {backup_timestamp}, Content types: {content_count}")
                
                if restore_backup_path:
                    self.logger.info(f"Pre-restore backup available at: {restore_backup_path}")
            else:
                self.logger.error("Failed to import baselines from backup")
                
                # If we created a pre-restore backup and restore failed, we could restore from it
                if restore_backup_path:
                    self.logger.info(f"Restore failed. Pre-restore backup available at: {restore_backup_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error restoring baseline from backup: {e}")
            return False
    
    def _validate_backup_structure(self, backup_data: Dict[str, Any]) -> bool:
        """
        Validate backup file structure
        
        Args:
            backup_data: Loaded backup data
            
        Returns:
            bool: True if structure is valid
        """
        try:
            # Check required top-level keys
            if "backup_metadata" not in backup_data or "baseline_data" not in backup_data:
                return False
            
            # Check metadata structure
            metadata = backup_data["backup_metadata"]
            required_metadata_keys = ["backup_timestamp", "project_name", "backup_version"]
            for key in required_metadata_keys:
                if key not in metadata:
                    return False
            
            # Check baseline data structure
            baseline_data = backup_data["baseline_data"]
            if "content_baselines" not in baseline_data:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating backup structure: {e}")
            return False
    
    def list_available_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backup files in the backup directory
        
        Returns:
            List[Dict]: List of backup file information
        """
        try:
            backups = []
            
            # Look for backup files matching the pattern
            pattern = f"{self.baseline_manager.project_name}_baseline_backup_*.json"
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith(f"{self.baseline_manager.project_name}_baseline_backup_") and filename.endswith(".json"):
                    backup_path = os.path.join(self.backup_dir, filename)
                    
                    try:
                        # Get file info
                        file_stat = os.stat(backup_path)
                        file_size = file_stat.st_size
                        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                        
                        # Try to read backup metadata
                        backup_metadata = None
                        try:
                            with open(backup_path, 'r', encoding='utf-8') as f:
                                backup_data = json.load(f)
                                backup_metadata = backup_data.get("backup_metadata", {})
                        except:
                            pass  # If we can't read metadata, just use file info
                        
                        backup_info = {
                            "filename": filename,
                            "path": backup_path,
                            "file_size_bytes": file_size,
                            "file_modified": file_mtime.isoformat(),
                            "backup_name": backup_metadata.get("backup_name", "unknown") if backup_metadata else "unknown",
                            "backup_timestamp": backup_metadata.get("backup_timestamp", file_mtime.isoformat()) if backup_metadata else file_mtime.isoformat(),
                            "content_types_count": backup_metadata.get("content_types_count", 0) if backup_metadata else 0,
                            "backup_version": backup_metadata.get("backup_version", "unknown") if backup_metadata else "unknown"
                        }
                        
                        backups.append(backup_info)
                        
                    except Exception as e:
                        self.logger.warning(f"Error reading backup file {filename}: {e}")
                        continue
            
            # Sort by backup timestamp (newest first)
            backups.sort(key=lambda x: x["backup_timestamp"], reverse=True)
            
            self.logger.info(f"Found {len(backups)} backup files")
            return backups
            
        except Exception as e:
            self.logger.error(f"Error listing available backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_count: int = 10, keep_days: int = 30) -> int:
        """
        Clean up old backup files based on count and age
        
        Args:
            keep_count: Maximum number of backups to keep
            keep_days: Maximum age in days for backups to keep
            
        Returns:
            int: Number of backups deleted
        """
        try:
            backups = self.list_available_backups()
            
            if len(backups) <= keep_count:
                self.logger.info(f"Only {len(backups)} backups found, no cleanup needed")
                return 0
            
            deleted_count = 0
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # Keep the newest keep_count backups, delete older ones
            backups_to_delete = backups[keep_count:]
            
            for backup in backups_to_delete:
                try:
                    backup_date = datetime.fromisoformat(backup["backup_timestamp"])
                    
                    # Delete if older than cutoff date
                    if backup_date < cutoff_date:
                        os.remove(backup["path"])
                        deleted_count += 1
                        self.logger.info(f"Deleted old backup: {backup['filename']}")
                    
                except Exception as e:
                    self.logger.warning(f"Error deleting backup {backup['filename']}: {e}")
                    continue
            
            self.logger.info(f"Cleanup completed: {deleted_count} backups deleted")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    def create_automatic_backup(self) -> Optional[str]:
        """
        Create an automatic backup with timestamp-based naming
        Integrates with existing progress management infrastructure
        
        Returns:
            str: Path to created backup file or None if failed
        """
        try:
            # Check if baselines exist and are worth backing up
            stats = self.baseline_manager.get_content_type_statistics()
            
            if not stats:
                self.logger.info("No baselines to backup")
                return None
            
            # Create backup with automatic naming
            backup_path = self.create_baseline_backup("auto")
            
            # Cleanup old automatic backups
            self.cleanup_old_backups(keep_count=10, keep_days=30)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error creating automatic backup: {e}")
            return None


# Integration with existing configuration backup system
def integrate_with_config_backup_system(baseline_manager: EnhancedBaselineManager,
                                       config_backup_dir: str = ".") -> BaselineBackupManager:
    """
    Create a BaselineBackupManager that integrates with existing configuration backup system
    
    Args:
        baseline_manager: EnhancedBaselineManager instance
        config_backup_dir: Directory where config backups are stored
        
    Returns:
        BaselineBackupManager: Configured backup manager
    """
    # Use the same directory as config backups for consistency
    backup_manager = BaselineBackupManager(baseline_manager, config_backup_dir)
    
    return backup_manager


# Enhanced baseline manager with integrated backup functionality
class EnhancedBaselineManagerWithBackup(EnhancedBaselineManager):
    """
    Enhanced baseline manager with integrated backup and restoration capabilities
    """
    
    def __init__(self, project_name: str = "website_monitoring", 
                 cache_dir: str = ".", backup_dir: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize enhanced baseline manager with backup capabilities
        
        Args:
            project_name: Name of the project
            cache_dir: Directory for cache files
            backup_dir: Directory for backup files (defaults to cache_dir)
            logger: Logger instance
        """
        super().__init__(project_name, cache_dir, logger)
        
        # Initialize backup manager
        backup_directory = backup_dir or cache_dir
        self.backup_manager = BaselineBackupManager(self, backup_directory, logger)
        
        # Auto-backup configuration
        self.auto_backup_enabled = True
        self.auto_backup_interval_hours = 24  # Create backup every 24 hours
        self.last_auto_backup_time = None
        
        self.logger.info("EnhancedBaselineManagerWithBackup initialized with backup capabilities")
    
    def set_content_baseline(self, content_type: str, baseline_key: str, 
                           baseline_value: str, metadata: Optional[Dict[str, Any]] = None,
                           create_backup: bool = False) -> bool:
        """
        Set baseline with optional automatic backup creation
        
        Args:
            content_type: Type of content
            baseline_key: Baseline key
            baseline_value: Baseline value
            metadata: Additional metadata
            create_backup: Whether to create a backup before updating
            
        Returns:
            bool: True if successful
        """
        try:
            # Create backup if requested
            if create_backup:
                backup_path = self.backup_manager.create_baseline_backup("pre_update")
                self.logger.info(f"Created pre-update backup: {backup_path}")
            
            # Set the baseline using parent method
            success = super().set_content_baseline(content_type, baseline_key, baseline_value, metadata)
            
            # Check if auto-backup is needed
            if success and self.auto_backup_enabled:
                self._check_and_create_auto_backup()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error setting baseline with backup: {e}")
            return False
    
    def _check_and_create_auto_backup(self):
        """Check if auto-backup is needed and create one if necessary"""
        try:
            current_time = datetime.now()
            
            # Check if enough time has passed since last auto-backup
            if self.last_auto_backup_time:
                time_diff = current_time - self.last_auto_backup_time
                if time_diff.total_seconds() < (self.auto_backup_interval_hours * 3600):
                    return  # Not enough time has passed
            
            # Create auto-backup
            backup_path = self.backup_manager.create_automatic_backup()
            if backup_path:
                self.last_auto_backup_time = current_time
                self.logger.info(f"Auto-backup created: {backup_path}")
            
        except Exception as e:
            self.logger.warning(f"Error creating auto-backup: {e}")
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore baselines from backup with rollback capability
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            bool: True if successful
        """
        return self.backup_manager.restore_baseline_from_backup(backup_path, create_restore_backup=True)
    
    def create_manual_backup(self, backup_name: str) -> str:
        """
        Create a manual backup with custom name
        
        Args:
            backup_name: Custom name for the backup
            
        Returns:
            str: Path to created backup file
        """
        return self.backup_manager.create_baseline_backup(backup_name)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List[Dict]: List of backup information
        """
        return self.backup_manager.list_available_backups()
    
    def cleanup_old_backups(self, keep_count: int = 10, keep_days: int = 30) -> int:
        """
        Clean up old backup files
        
        Args:
            keep_count: Number of backups to keep
            keep_days: Maximum age in days
            
        Returns:
            int: Number of backups deleted
        """
        return self.backup_manager.cleanup_old_backups(keep_count, keep_days)


# Example usage for backup and restoration
if __name__ == "__main__":
    # Additional testing for backup functionality
    print("\nTesting backup and restoration functionality...")
    
    # Create enhanced baseline manager with backup
    ebm_with_backup = EnhancedBaselineManagerWithBackup("test_backup_project")
    
    # Set some test baselines
    ebm_with_backup.set_content_baseline("carousel", "test_key", "test_value")
    ebm_with_backup.set_content_baseline("news", "latest_title", "Test News")
    
    # Create manual backup
    backup_path = ebm_with_backup.create_manual_backup("test_backup")
    print(f"Created manual backup: {backup_path}")
    
    # List backups
    backups = ebm_with_backup.list_backups()
    print(f"Available backups: {len(backups)}")
    
    # Modify baselines
    ebm_with_backup.set_content_baseline("carousel", "test_key", "modified_value")
    
    # Restore from backup
    if backups:
        restore_success = ebm_with_backup.restore_from_backup(backups[0]["path"])
        print(f"Restore successful: {restore_success}")
    
    # Cleanup
    ebm_with_backup.cleanup_baseline_cache(force=True)
    deleted_count = ebm_with_backup.cleanup_old_backups(keep_count=0, keep_days=0)
    print(f"Cleaned up {deleted_count} backup files")
    
    print("Backup testing completed")