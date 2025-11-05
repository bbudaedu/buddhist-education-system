#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Management Module for New Book Summary System
新書摘要系統的進度管理模組

This module handles progress tracking, caching, and resumption functionality
for the new book processing workflow.
"""

import os
import json
import time
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProgressManager:
    """
    Manages processing progress with JSON-based caching for resumption capability
    
    Handles:
    - Session tracking with unique IDs
    - Processed books list persistence
    - Progress save/load functionality
    - Cache cleanup when processing completes
    """
    
    def __init__(self, project_name: str = "newbook_summary", 
                 cache_dir: str = ".", logger: Optional[logging.Logger] = None):
        """
        Initialize ProgressManager
        
        Args:
            project_name: Name of the project for cache file naming
            cache_dir: Directory to store cache files (default: current directory)
            logger: Logger instance for logging operations
        """
        self.project_name = project_name
        self.cache_dir = cache_dir
        self.logger = logger or logging.getLogger(__name__)
        
        # Generate cache filename with project name
        self.cache_filename = f".{project_name}_progress_cache.json"
        self.cache_path = os.path.join(cache_dir, self.cache_filename)
        
        # Current session data
        self.session_id = None
        self.session_data = None
        
        self.logger.info(f"ProgressManager initialized for project: {project_name}")
        self.logger.info(f"Cache file path: {self.cache_path}")
    
    def create_progress_cache_structure(self) -> Dict[str, Any]:
        """
        Define JSON format for progress data
        
        Returns:
            Dict: Empty progress cache structure with session ID and timestamps
        """
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        cache_structure = {
            "session_id": session_id,
            "project_name": self.project_name,
            "start_time": current_time,
            "last_updated": current_time,
            "status": "in_progress",  # in_progress, completed, interrupted
            "total_books_found": 0,
            "processed_books": [],
            "failed_books": [],
            "processing_stats": {
                "books_processed": 0,
                "books_failed": 0,
                "pdf_extractions": 0,
                "google_searches": 0,
                "total_processing_time": 0
            },
            "configuration": {
                "baseline_book_title": "",
                "target_url": "",
                "download_dir": ""
            }
        }
        
        self.logger.info(f"Created progress cache structure with session ID: {session_id}")
        return cache_structure   
 
    def create_processed_book_entry(self, book_info: Dict[str, Any], 
                                   processing_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a processed book entry for the cache
        
        Args:
            book_info: Basic book information (title, filename, etc.)
            processing_result: Result from AI processing (summary, method, etc.)
            
        Returns:
            Dict: Processed book entry with all relevant information
        """
        entry = {
            "title": book_info.get('title', ''),
            "filename": book_info.get('filename', ''),
            "pdf_url": book_info.get('pdf_url', ''),
            "download_path": book_info.get('download_path', ''),
            "file_size_bytes": book_info.get('file_size_bytes', 0),
            "download_success": book_info.get('download_success', False),
            "processing_timestamp": datetime.now().isoformat(),
            "processing_success": False,
            "processing_method": "",
            "summary": "",
            "error_message": ""
        }
        
        # Add processing results if available
        if processing_result:
            entry.update({
                "processing_success": True,
                "processing_method": processing_result.get('processing_method', ''),
                "summary": processing_result.get('summary', ''),
                "file_size_bytes": processing_result.get('file_size_bytes', entry["file_size_bytes"])
            })
        else:
            # Mark as failed if no processing result
            entry["error_message"] = book_info.get('error_message', 'Processing failed')
        
        return entry
    
    def start_new_session(self, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new processing session
        
        Args:
            config: Configuration dictionary with baseline_book_title, target_url, etc.
            
        Returns:
            str: Session ID for the new session
        """
        try:
            # Create new cache structure
            self.session_data = self.create_progress_cache_structure()
            self.session_id = self.session_data["session_id"]
            
            # Update configuration if provided
            if config:
                self.session_data["configuration"].update({
                    "baseline_book_title": config.get('baseline_book_title', ''),
                    "target_url": config.get('target_url', ''),
                    "download_dir": config.get('download_dir', '')
                })
            
            self.logger.info(f"Started new session: {self.session_id}")
            return self.session_id
            
        except Exception as e:
            self.logger.error(f"Error starting new session: {e}")
            raise 
   
    def save_progress(self, processed_books: Optional[List[Dict[str, Any]]] = None,
                     total_books: Optional[int] = None, status: str = "in_progress") -> bool:
        """
        Save processed books to JSON cache file using atomic write with temporary file
        
        Args:
            processed_books: List of processed book entries to save
            total_books: Total number of books found (for progress calculation)
            status: Current processing status ('in_progress', 'completed', 'interrupted')
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if not self.session_data:
                self.logger.error("No active session to save")
                return False
            
            # Update session data
            current_time = datetime.now().isoformat()
            self.session_data["last_updated"] = current_time
            self.session_data["status"] = status
            
            if total_books is not None:
                self.session_data["total_books_found"] = total_books
            
            if processed_books is not None:
                # Separate successful and failed books
                successful_books = []
                failed_books = []
                
                for book in processed_books:
                    if book.get('processing_success', False):
                        successful_books.append(book)
                    else:
                        failed_books.append(book)
                
                self.session_data["processed_books"] = successful_books
                self.session_data["failed_books"] = failed_books
                
                # Update processing stats
                stats = self.session_data["processing_stats"]
                stats["books_processed"] = len(successful_books)
                stats["books_failed"] = len(failed_books)
                
                # Count processing methods
                pdf_extractions = sum(1 for book in successful_books 
                                    if book.get('processing_method') == 'pdf_extract')
                google_searches = sum(1 for book in successful_books 
                                    if book.get('processing_method') == 'google_search')
                
                stats["pdf_extractions"] = pdf_extractions
                stats["google_searches"] = google_searches
            
            # Use atomic write with temporary file
            temp_file = self.cache_path + '.tmp'
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(self.session_data, f, ensure_ascii=False, indent=2)
                
                # Replace original file atomically
                if os.path.exists(self.cache_path):
                    os.remove(self.cache_path)
                os.rename(temp_file, self.cache_path)
                
                books_count = len(self.session_data.get("processed_books", []))
                failed_count = len(self.session_data.get("failed_books", []))
                
                self.logger.info(f"Progress saved: {books_count} processed, {failed_count} failed")
                self.logger.debug(f"Cache saved to: {self.cache_path}")
                
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
            self.logger.error(f"Error saving progress: {e}")
            return False
    
    def add_processed_book(self, book_info: Dict[str, Any], 
                          processing_result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a single processed book to the current session and save immediately
        
        Args:
            book_info: Basic book information
            processing_result: Result from AI processing
            
        Returns:
            bool: True if book added and saved successfully
        """
        try:
            if not self.session_data:
                self.logger.error("No active session to add book to")
                return False
            
            # Create processed book entry
            book_entry = self.create_processed_book_entry(book_info, processing_result)
            
            # Add to appropriate list based on success
            if book_entry["processing_success"]:
                self.session_data["processed_books"].append(book_entry)
                self.logger.info(f"Added successful book: {book_entry['title']}")
            else:
                self.session_data["failed_books"].append(book_entry)
                self.logger.warning(f"Added failed book: {book_entry['title']} - {book_entry['error_message']}")
            
            # Save progress immediately
            return self.save_progress()
            
        except Exception as e:
            self.logger.error(f"Error adding processed book: {e}")
            return False    

    def load_progress(self) -> Optional[Dict[str, Any]]:
        """
        Load cache file on startup and parse processed books list
        
        Returns:
            Dict: Loaded session data or None if no cache exists or loading fails
        """
        try:
            if not os.path.exists(self.cache_path):
                self.logger.info("No existing progress cache found")
                return None
            
            self.logger.info(f"Loading progress cache from: {self.cache_path}")
            
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                self.session_data = json.load(f)
            
            # Validate cache structure
            if not self._validate_cache_structure(self.session_data):
                self.logger.error("Invalid cache structure, ignoring cache file")
                return None
            
            self.session_id = self.session_data["session_id"]
            
            # Log cache information
            processed_count = len(self.session_data.get("processed_books", []))
            failed_count = len(self.session_data.get("failed_books", []))
            total_books = self.session_data.get("total_books_found", 0)
            status = self.session_data.get("status", "unknown")
            
            self.logger.info(f"Loaded session: {self.session_id}")
            self.logger.info(f"Session status: {status}")
            self.logger.info(f"Progress: {processed_count} processed, {failed_count} failed, {total_books} total")
            
            # Log start time and last updated
            start_time = self.session_data.get("start_time", "unknown")
            last_updated = self.session_data.get("last_updated", "unknown")
            self.logger.info(f"Started: {start_time}, Last updated: {last_updated}")
            
            return self.session_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in cache file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading progress cache: {e}")
            return None
    
    def _validate_cache_structure(self, cache_data: Dict[str, Any]) -> bool:
        """
        Validate that the loaded cache has the expected structure
        
        Args:
            cache_data: Loaded cache data to validate
            
        Returns:
            bool: True if structure is valid, False otherwise
        """
        required_keys = [
            "session_id", "project_name", "start_time", "last_updated",
            "status", "processed_books", "failed_books", "processing_stats"
        ]
        
        for key in required_keys:
            if key not in cache_data:
                self.logger.error(f"Missing required key in cache: {key}")
                return False
        
        # Validate that lists are actually lists
        if not isinstance(cache_data["processed_books"], list):
            self.logger.error("processed_books is not a list")
            return False
        
        if not isinstance(cache_data["failed_books"], list):
            self.logger.error("failed_books is not a list")
            return False
        
        # Validate project name matches
        if cache_data["project_name"] != self.project_name:
            self.logger.warning(f"Project name mismatch: cache={cache_data['project_name']}, current={self.project_name}")
        
        return True
    
    def get_processed_book_titles(self) -> List[str]:
        """
        Get list of titles of already processed books to skip during processing
        
        Returns:
            List[str]: List of book titles that have been successfully processed
        """
        if not self.session_data:
            return []
        
        processed_titles = []
        
        # Get titles from successfully processed books
        for book in self.session_data.get("processed_books", []):
            title = book.get("title", "")
            if title:
                processed_titles.append(title)
        
        self.logger.info(f"Found {len(processed_titles)} previously processed books")
        return processed_titles
    
    def should_skip_book(self, book_title: str) -> bool:
        """
        Check if a book should be skipped because it was already processed
        
        Args:
            book_title: Title of the book to check
            
        Returns:
            bool: True if book should be skipped, False if it should be processed
        """
        processed_titles = self.get_processed_book_titles()
        
        # Check for exact match
        if book_title in processed_titles:
            self.logger.info(f"Skipping already processed book: {book_title}")
            return True
        
        # Check for partial matches (in case titles have slight variations)
        for processed_title in processed_titles:
            if book_title.strip() == processed_title.strip():
                self.logger.info(f"Skipping already processed book (exact match): {book_title}")
                return True
        
        return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session for display purposes
        
        Returns:
            Dict: Session summary with key statistics
        """
        if not self.session_data:
            return {
                "session_active": False,
                "message": "No active session"
            }
        
        processed_books = self.session_data.get("processed_books", [])
        failed_books = self.session_data.get("failed_books", [])
        stats = self.session_data.get("processing_stats", {})
        
        summary = {
            "session_active": True,
            "session_id": self.session_id,
            "status": self.session_data.get("status", "unknown"),
            "start_time": self.session_data.get("start_time", ""),
            "last_updated": self.session_data.get("last_updated", ""),
            "total_books_found": self.session_data.get("total_books_found", 0),
            "books_processed": len(processed_books),
            "books_failed": len(failed_books),
            "pdf_extractions": stats.get("pdf_extractions", 0),
            "google_searches": stats.get("google_searches", 0),
            "completion_percentage": 0
        }
        
        # Calculate completion percentage
        total_books = summary["total_books_found"]
        if total_books > 0:
            completed = summary["books_processed"] + summary["books_failed"]
            summary["completion_percentage"] = (completed / total_books) * 100
        
        return summary
    
    def cleanup_cache(self, force: bool = False) -> bool:
        """
        Delete cache file when all books are processed or when forced
        
        Args:
            force: If True, delete cache regardless of completion status
            
        Returns:
            bool: True if cache was deleted successfully, False otherwise
        """
        try:
            if not os.path.exists(self.cache_path):
                self.logger.info("No cache file to clean up")
                return True
            
            # Check if processing is complete (unless forced)
            if not force and self.session_data:
                status = self.session_data.get("status", "")
                total_books = self.session_data.get("total_books_found", 0)
                processed_count = len(self.session_data.get("processed_books", []))
                failed_count = len(self.session_data.get("failed_books", []))
                completed_count = processed_count + failed_count
                
                if status != "completed" and completed_count < total_books:
                    self.logger.info(f"Processing not complete ({completed_count}/{total_books}), keeping cache")
                    return False
            
            # Delete the cache file
            os.remove(self.cache_path)
            self.logger.info(f"Cache file deleted: {self.cache_path}")
            
            # Clear session data
            self.session_data = None
            self.session_id = None
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up cache: {e}")
            return False
    
    def mark_session_completed(self) -> bool:
        """
        Mark the current session as completed and optionally clean up cache
        
        Returns:
            bool: True if session marked as completed successfully
        """
        try:
            if not self.session_data:
                self.logger.error("No active session to mark as completed")
                return False
            
            # Update session status
            self.session_data["status"] = "completed"
            self.session_data["last_updated"] = datetime.now().isoformat()
            
            # Calculate final processing time (if start_time is available)
            start_time_str = self.session_data.get("start_time", "")
            if start_time_str:
                try:
                    start_time = datetime.fromisoformat(start_time_str)
                    end_time = datetime.now()
                    processing_time = (end_time - start_time).total_seconds()
                    self.session_data["processing_stats"]["total_processing_time"] = processing_time
                    
                    self.logger.info(f"Total processing time: {processing_time:.1f} seconds")
                except Exception as e:
                    self.logger.warning(f"Could not calculate processing time: {e}")
            
            # Save final state
            success = self.save_progress(status="completed")
            
            if success:
                processed_count = len(self.session_data.get("processed_books", []))
                failed_count = len(self.session_data.get("failed_books", []))
                self.logger.info(f"Session completed: {processed_count} processed, {failed_count} failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error marking session as completed: {e}")
            return False
    
    def mark_session_interrupted(self) -> bool:
        """
        Mark the current session as interrupted (for user-initiated stops)
        
        Returns:
            bool: True if session marked as interrupted successfully
        """
        try:
            if not self.session_data:
                self.logger.error("No active session to mark as interrupted")
                return False
            
            # Update session status
            self.session_data["status"] = "interrupted"
            self.session_data["last_updated"] = datetime.now().isoformat()
            
            # Save interrupted state
            success = self.save_progress(status="interrupted")
            
            if success:
                processed_count = len(self.session_data.get("processed_books", []))
                failed_count = len(self.session_data.get("failed_books", []))
                self.logger.info(f"Session interrupted: {processed_count} processed, {failed_count} failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error marking session as interrupted: {e}")
            return False
    
    def get_cache_file_info(self) -> Dict[str, Any]:
        """
        Get information about the cache file for debugging purposes
        
        Returns:
            Dict: Cache file information including size, modification time, etc.
        """
        info = {
            "cache_path": self.cache_path,
            "exists": False,
            "size_bytes": 0,
            "modified_time": "",
            "readable": False
        }
        
        try:
            if os.path.exists(self.cache_path):
                info["exists"] = True
                info["size_bytes"] = os.path.getsize(self.cache_path)
                info["modified_time"] = datetime.fromtimestamp(
                    os.path.getmtime(self.cache_path)
                ).isoformat()
                info["readable"] = os.access(self.cache_path, os.R_OK)
            
        except Exception as e:
            self.logger.warning(f"Error getting cache file info: {e}")
        
        return info


# Example usage and testing functions
def create_test_book_info(title: str, filename: str, success: bool = True) -> Dict[str, Any]:
    """
    Create test book info for testing purposes
    
    Args:
        title: Book title
        filename: PDF filename
        success: Whether the book processing was successful
        
    Returns:
        Dict: Test book information
    """
    return {
        'title': title,
        'filename': filename,
        'pdf_url': f'https://example.com/{filename}',
        'download_path': f'downloads/{filename}',
        'file_size_bytes': 1024 * 1024,  # 1MB
        'download_success': success,
        'error_message': '' if success else 'Test error'
    }


def create_test_processing_result(method: str = 'pdf_extract') -> Dict[str, Any]:
    """
    Create test processing result for testing purposes
    
    Args:
        method: Processing method ('pdf_extract' or 'google_search')
        
    Returns:
        Dict: Test processing result
    """
    return {
        'processing_method': method,
        'summary': '這是一本測試書籍的摘要，包含了主要內容和重點。',
        'file_size_bytes': 1024 * 1024,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create test progress manager
    pm = ProgressManager("test_project")
    
    # Test basic functionality
    print("Testing ProgressManager...")
    
    # Start new session
    session_id = pm.start_new_session({
        'baseline_book_title': 'Test Baseline',
        'target_url': 'https://example.com',
        'download_dir': 'test_downloads'
    })
    print(f"Started session: {session_id}")
    
    # Add some test books
    for i in range(3):
        book_info = create_test_book_info(f"Test Book {i+1}", f"test{i+1}.pdf")
        processing_result = create_test_processing_result()
        pm.add_processed_book(book_info, processing_result)
    
    # Get session summary
    summary = pm.get_session_summary()
    print(f"Session summary: {summary}")
    
    # Test load functionality
    pm2 = ProgressManager("test_project")
    loaded_data = pm2.load_progress()
    if loaded_data:
        print("Successfully loaded progress from cache")
        print(f"Processed books: {pm2.get_processed_book_titles()}")
    
    # Clean up test cache
    pm.cleanup_cache(force=True)
    print("Test completed")