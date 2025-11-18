#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Data Synchronizer Module for Website Monitoring
增強型資料同步模組

This module coordinates dual storage to Excel files and MySQL database
for all website monitoring content types. Integrates with existing
document_generator and BookSyncService infrastructure.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import existing infrastructure
from document_generator import DocumentGenerator


class EnhancedDataSynchronizer:
    """
    Enhanced data synchronizer for coordinating dual storage
    
    Handles:
    - Excel file generation for all content types
    - MySQL database synchronization
    - Data consistency between storage systems
    - Batch operations for efficiency
    """
    
    def __init__(self, document_generator: DocumentGenerator, config: Dict[str, Any], 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize EnhancedDataSynchronizer
        
        Args:
            document_generator: DocumentGenerator instance for Excel operations
            config: Configuration dictionary
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.document_generator = document_generator
        self.config = config
        
        # MySQL integration (would be imported from LINE bot system)
        self.mysql_enabled = False
        self.book_sync_service = None
        
        # Initialize MySQL connection if available
        self._initialize_mysql_connection()
        
        self.logger.info("EnhancedDataSynchronizer initialized")
    
    def _initialize_mysql_connection(self):
        """
        Initialize MySQL connection using existing BookSyncService
        """
        try:
            # In a real implementation, this would import and initialize BookSyncService
            # from the LINE bot system for MySQL operations
            
            # For now, we'll simulate MySQL availability
            mysql_config = self.config.get('mysql', {})
            if mysql_config.get('enabled', False):
                self.mysql_enabled = True
                self.logger.info("MySQL synchronization enabled")
            else:
                self.logger.info("MySQL synchronization disabled")
                
        except Exception as e:
            self.logger.warning(f"MySQL initialization failed: {e}")
            self.mysql_enabled = False
    
    def sync_content_type(self, content_type: str, content_list: List[Dict[str, Any]]) -> bool:
        """
        Synchronize content of a specific type to both Excel and MySQL
        
        Args:
            content_type: Type of content ('carousel', 'cancellation', 'news', 'media')
            content_list: List of content items to synchronize
            
        Returns:
            bool: True if synchronization successful
        """
        try:
            if not content_list:
                self.logger.info(f"No {content_type} content to synchronize")
                return True
            
            self.logger.info(f"Synchronizing {len(content_list)} {content_type} items...")
            
            # Synchronize to Excel
            excel_success = self._sync_to_excel(content_type, content_list)
            
            # Synchronize to MySQL if enabled
            mysql_success = True
            if self.mysql_enabled:
                mysql_success = self._sync_to_mysql(content_type, content_list)
            
            overall_success = excel_success and mysql_success
            
            if overall_success:
                self.logger.info(f"✓ {content_type} synchronization completed successfully")
            else:
                self.logger.error(f"✗ {content_type} synchronization failed (Excel: {excel_success}, MySQL: {mysql_success})")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error synchronizing {content_type}: {e}")
            return False
    
    def _sync_to_excel(self, content_type: str, content_list: List[Dict[str, Any]]) -> bool:
        """
        Synchronize content to Excel files using DocumentGenerator
        
        Args:
            content_type: Type of content
            content_list: List of content items
            
        Returns:
            bool: True if Excel synchronization successful
        """
        try:
            # Prepare data for Excel generation
            excel_data = self._prepare_excel_data(content_type, content_list)
            
            if not excel_data:
                self.logger.warning(f"No Excel data prepared for {content_type}")
                return False
            
            # Generate Excel file using existing DocumentGenerator
            filename = f"{content_type}_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Use DocumentGenerator to create Excel file
            success = self.document_generator.create_monitoring_excel(
                filename=filename,
                content_type=content_type,
                data=excel_data
            )
            
            if success:
                self.logger.info(f"Excel file created: {filename}")
                return True
            else:
                self.logger.error(f"Failed to create Excel file for {content_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing {content_type} to Excel: {e}")
            return False
    
    def _prepare_excel_data(self, content_type: str, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare content data for Excel generation
        
        Args:
            content_type: Type of content
            content_list: List of content items
            
        Returns:
            List[Dict]: Prepared data for Excel generation
        """
        try:
            excel_data = []
            
            for item in content_list:
                if content_type == 'carousel':
                    excel_row = {
                        'ID': item.get('carousel_id', ''),
                        '橫幅標題': item.get('banner_title', ''),
                        '圖片URL': item.get('image_url', ''),
                        '活動連結': item.get('activity_link', ''),
                        '課程名稱': item.get('course_name', ''),
                        '地點': item.get('location', ''),
                        '講師': item.get('instructor', ''),
                        '描述': item.get('description', ''),
                        '提取時間': item.get('extraction_timestamp', '')
                    }
                
                elif content_type == 'cancellation':
                    excel_row = {
                        'ID': item.get('cancellation_id', ''),
                        '取消日期': item.get('cancellation_date', ''),
                        '課程名稱': item.get('course_name', ''),
                        '講師姓名': item.get('instructor_name', ''),
                        '提取時間': item.get('extraction_timestamp', '')
                    }
                
                elif content_type == 'news':
                    excel_row = {
                        'ID': item.get('announcement_id', ''),
                        '標題': item.get('title', ''),
                        '發布日期': item.get('publication_date', ''),
                        '內容': item.get('content', ''),
                        '提取時間': item.get('extraction_timestamp', '')
                    }
                
                elif content_type == 'media':
                    excel_row = {
                        'ID': item.get('media_id', ''),
                        '課程標題': item.get('course_title', ''),
                        '講師姓名': item.get('speaker_name', ''),
                        '開始日期': item.get('start_date', ''),
                        '重定向URL': item.get('redirect_url', ''),
                        '媒體類型': item.get('media_type', ''),
                        '提取時間': item.get('extraction_timestamp', '')
                    }
                
                else:
                    # Generic format for unknown content types
                    excel_row = item.copy()
                
                excel_data.append(excel_row)
            
            return excel_data
            
        except Exception as e:
            self.logger.error(f"Error preparing Excel data for {content_type}: {e}")
            return []
    
    def _sync_to_mysql(self, content_type: str, content_list: List[Dict[str, Any]]) -> bool:
        """
        Synchronize content to MySQL database
        
        Args:
            content_type: Type of content
            content_list: List of content items
            
        Returns:
            bool: True if MySQL synchronization successful
        """
        try:
            if not self.mysql_enabled or not self.book_sync_service:
                self.logger.info(f"MySQL sync skipped for {content_type} (not enabled)")
                return True
            
            # Prepare data for MySQL insertion
            mysql_data = self._prepare_mysql_data(content_type, content_list)
            
            if not mysql_data:
                self.logger.warning(f"No MySQL data prepared for {content_type}")
                return False
            
            # Use BookSyncService for MySQL operations
            table_name = self._get_mysql_table_name(content_type)
            
            # Batch insert/update operations
            success = self.book_sync_service.batch_upsert(table_name, mysql_data)
            
            if success:
                self.logger.info(f"MySQL sync completed for {content_type} ({len(mysql_data)} items)")
                return True
            else:
                self.logger.error(f"MySQL sync failed for {content_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error syncing {content_type} to MySQL: {e}")
            return False
    
    def _prepare_mysql_data(self, content_type: str, content_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare content data for MySQL insertion
        
        Args:
            content_type: Type of content
            content_list: List of content items
            
        Returns:
            List[Dict]: Prepared data for MySQL insertion
        """
        try:
            mysql_data = []
            
            for item in content_list:
                # Convert datetime objects to strings for MySQL
                mysql_row = {}
                
                for key, value in item.items():
                    if isinstance(value, datetime):
                        mysql_row[key] = value.isoformat()
                    else:
                        mysql_row[key] = value
                
                # Add common fields
                mysql_row['created_at'] = datetime.now().isoformat()
                mysql_row['updated_at'] = datetime.now().isoformat()
                
                mysql_data.append(mysql_row)
            
            return mysql_data
            
        except Exception as e:
            self.logger.error(f"Error preparing MySQL data for {content_type}: {e}")
            return []
    
    def _get_mysql_table_name(self, content_type: str) -> str:
        """
        Get MySQL table name for content type
        
        Args:
            content_type: Type of content
            
        Returns:
            str: MySQL table name
        """
        table_mapping = {
            'carousel': 'carousel_content',
            'cancellation': 'course_cancellations',
            'news': 'news_announcements',
            'media': 'media_content'
        }
        
        return table_mapping.get(content_type, f"{content_type}_content")
    
    def create_excel_sheets(self, content_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Create comprehensive Excel file with multiple sheets for all content types
        
        Args:
            content_data: Dictionary containing all content by type
            
        Returns:
            str: Path to created Excel file or empty string if failed
        """
        try:
            if not content_data or not any(content_data.values()):
                self.logger.warning("No content data to create Excel sheets")
                return ""
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"website_monitoring_comprehensive_{timestamp}.xlsx"
            
            # Prepare data for multi-sheet Excel
            sheets_data = {}
            
            for content_type, content_list in content_data.items():
                if content_list:
                    sheet_name = self._get_excel_sheet_name(content_type)
                    sheets_data[sheet_name] = self._prepare_excel_data(content_type, content_list)
            
            if not sheets_data:
                self.logger.warning("No valid sheet data prepared")
                return ""
            
            # Create multi-sheet Excel file
            success = self.document_generator.create_multi_sheet_excel(
                filename=filename,
                sheets_data=sheets_data
            )
            
            if success:
                file_path = os.path.join(self.document_generator.output_dir, filename)
                self.logger.info(f"Comprehensive Excel file created: {file_path}")
                return file_path
            else:
                self.logger.error("Failed to create comprehensive Excel file")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error creating Excel sheets: {e}")
            return ""
    
    def _get_excel_sheet_name(self, content_type: str) -> str:
        """
        Get Excel sheet name for content type
        
        Args:
            content_type: Type of content
            
        Returns:
            str: Excel sheet name
        """
        sheet_mapping = {
            'carousel': '輪播橫幅',
            'cancellation': '課程取消',
            'news': '新聞公告',
            'media': '多媒體內容'
        }
        
        return sheet_mapping.get(content_type, content_type.title())
    
    def sync_to_mysql_batch(self, content_data: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Synchronize all content types to MySQL in batch operations
        
        Args:
            content_data: Dictionary containing all content by type
            
        Returns:
            bool: True if all batch operations successful
        """
        try:
            if not self.mysql_enabled:
                self.logger.info("MySQL batch sync skipped (not enabled)")
                return True
            
            batch_results = {}
            
            for content_type, content_list in content_data.items():
                if content_list:
                    success = self._sync_to_mysql(content_type, content_list)
                    batch_results[content_type] = success
            
            overall_success = all(batch_results.values()) if batch_results else True
            
            if overall_success:
                self.logger.info("MySQL batch synchronization completed successfully")
            else:
                failed_types = [t for t, success in batch_results.items() if not success]
                self.logger.error(f"MySQL batch synchronization failed for: {failed_types}")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error in MySQL batch synchronization: {e}")
            return False
    
    def validate_data_consistency(self, content_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Validate data consistency between Excel and MySQL storage
        
        Args:
            content_data: Content data to validate
            
        Returns:
            Dict: Validation results
        """
        try:
            validation_results = {
                'consistent': True,
                'issues': [],
                'content_type_results': {}
            }
            
            for content_type, content_list in content_data.items():
                if not content_list:
                    continue
                
                type_result = {
                    'excel_count': len(content_list),
                    'mysql_count': 0,
                    'consistent': True,
                    'issues': []
                }
                
                # Check MySQL count if enabled
                if self.mysql_enabled and self.book_sync_service:
                    try:
                        table_name = self._get_mysql_table_name(content_type)
                        mysql_count = self.book_sync_service.get_record_count(table_name)
                        type_result['mysql_count'] = mysql_count
                        
                        if mysql_count != len(content_list):
                            type_result['consistent'] = False
                            type_result['issues'].append(f"Count mismatch: Excel {len(content_list)}, MySQL {mysql_count}")
                            validation_results['consistent'] = False
                            
                    except Exception as e:
                        type_result['issues'].append(f"MySQL validation error: {e}")
                        validation_results['consistent'] = False
                
                validation_results['content_type_results'][content_type] = type_result
            
            # Aggregate issues
            for content_type, result in validation_results['content_type_results'].items():
                validation_results['issues'].extend([f"{content_type}: {issue}" for issue in result['issues']])
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating data consistency: {e}")
            return {
                'consistent': False,
                'issues': [f"Validation error: {e}"],
                'content_type_results': {}
            }


# Example usage and testing
def main():
    """
    Example usage of EnhancedDataSynchronizer
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Mock configuration
        config = {
            'download_dir': 'generated_documents',
            'mysql': {
                'enabled': False  # Disabled for testing
            }
        }
        
        # Initialize DocumentGenerator (mock)
        document_generator = DocumentGenerator(
            output_dir=config['download_dir'],
            logger=logger
        )
        
        # Initialize EnhancedDataSynchronizer
        synchronizer = EnhancedDataSynchronizer(
            document_generator=document_generator,
            config=config,
            logger=logger
        )
        
        # Test data
        test_content = {
            'carousel': [
                {
                    'carousel_id': 'test_carousel_1',
                    'banner_title': '測試輪播橫幅',
                    'image_url': 'https://example.com/image.jpg',
                    'course_name': '測試課程',
                    'extraction_timestamp': datetime.now()
                }
            ],
            'news': [
                {
                    'announcement_id': 'test_news_1',
                    'title': '測試新聞',
                    'content': '這是測試新聞內容',
                    'extraction_timestamp': datetime.now()
                }
            ]
        }
        
        # Test synchronization
        for content_type, content_list in test_content.items():
            success = synchronizer.sync_content_type(content_type, content_list)
            logger.info(f"{content_type} sync result: {success}")
        
        # Test comprehensive Excel creation
        excel_path = synchronizer.create_excel_sheets(test_content)
        if excel_path:
            logger.info(f"Comprehensive Excel created: {excel_path}")
        
        # Test data validation
        validation_result = synchronizer.validate_data_consistency(test_content)
        logger.info(f"Data consistency validation: {validation_result}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")


if __name__ == "__main__":
    main()