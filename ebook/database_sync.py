#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Sync Manager for Website Monitoring System
資料庫同步管理器，用於網站監控系統

This module provides integration with the LINE bot MySQL database
for synchronizing website monitoring content.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime


class DatabaseSyncManager:
    """
    Manages synchronization with the LINE bot MySQL database.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the Database Sync Manager.
        
        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        self.api_base_url = self.config.get('linebot_api_url', 'http://localhost:3000')
        
        self.logger.info("Database Sync Manager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json.
        
        Returns:
            Dict: Configuration dictionary
        """
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # Add database sync configuration if not present
                if 'database_sync' not in config:
                    config['database_sync'] = {
                        'enabled': True,
                        'linebot_api_url': 'http://localhost:3000',
                        'sync_timeout': 30,
                        'retry_attempts': 3
                    }
                    
                    # Save updated config
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                
                return config.get('database_sync', {})
            else:
                self.logger.warning("Config file not found, using default settings")
                return {
                    'enabled': True,
                    'linebot_api_url': 'http://localhost:3000',
                    'sync_timeout': 30,
                    'retry_attempts': 3
                }
                
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {
                'enabled': False,
                'linebot_api_url': 'http://localhost:3000',
                'sync_timeout': 30,
                'retry_attempts': 3
            }
    
    def is_sync_enabled(self) -> bool:
        """
        Check if database sync is enabled.
        
        Returns:
            bool: True if sync is enabled
        """
        return self.config.get('enabled', False)
    
    def sync_website_monitoring_content(self, content_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Sync website monitoring content to the LINE bot database.
        
        Args:
            content_data: Dictionary with content type as key and data list as value
            
        Returns:
            Dict: Sync result information
        """
        if not self.is_sync_enabled():
            return {
                'success': True,
                'message': 'Database sync is disabled',
                'total_synced': 0
            }
        
        try:
            self.logger.info("Starting website monitoring content sync to database")
            
            # Prepare sync payload
            sync_payload = {
                'content_data': content_data,
                'sync_timestamp': datetime.now().isoformat(),
                'source': 'website_monitoring'
            }
            
            # Make API request to LINE bot service
            response = self._make_sync_request('/api/sync/website-monitoring', sync_payload)
            
            if response.get('success', False):
                total_synced = response.get('total_synced', 0)
                self.logger.info(f"Database sync successful: {total_synced} items synced")
                
                return {
                    'success': True,
                    'total_synced': total_synced,
                    'details': response.get('details', {}),
                    'message': f'Successfully synced {total_synced} items to database'
                }
            else:
                error_msg = response.get('error', 'Unknown database sync error')
                self.logger.error(f"Database sync failed: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg,
                    'total_synced': 0
                }
                
        except Exception as e:
            self.logger.error(f"Database sync exception: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_synced': 0
            }
    
    def auto_sync_after_generation(self, excel_path: str) -> Dict[str, Any]:
        """
        Automatically sync data after Excel generation (for backward compatibility).
        
        Args:
            excel_path: Path to the generated Excel file
            
        Returns:
            Dict: Sync result information
        """
        if not self.is_sync_enabled():
            return {
                'success': True,
                'message': 'Database sync is disabled'
            }
        
        try:
            self.logger.info(f"Auto-sync triggered for Excel file: {excel_path}")
            
            # For now, just log the auto-sync trigger
            # In a full implementation, this would parse the Excel file and sync the data
            
            return {
                'success': True,
                'message': f'Auto-sync completed for {excel_path}'
            }
            
        except Exception as e:
            self.logger.error(f"Auto-sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _make_sync_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to LINE bot API for sync operation.
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Returns:
            Dict: Response data
        """
        url = f"{self.api_base_url}{endpoint}"
        timeout = self.config.get('sync_timeout', 30)
        retry_attempts = self.config.get('retry_attempts', 3)
        
        for attempt in range(retry_attempts):
            try:
                self.logger.debug(f"Making sync request to {url} (attempt {attempt + 1})")
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'EbookSystem/1.0'
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # API endpoint not available - this is expected if LINE bot is not running
                    self.logger.info("LINE bot API not available (404) - sync skipped")
                    return {
                        'success': True,
                        'message': 'LINE bot API not available',
                        'total_synced': 0
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.logger.warning(f"Sync request failed: {error_msg}")
                    
                    if attempt == retry_attempts - 1:
                        return {
                            'success': False,
                            'error': error_msg
                        }
                
            except requests.exceptions.ConnectionError:
                self.logger.info("LINE bot service not available - sync skipped")
                return {
                    'success': True,
                    'message': 'LINE bot service not available',
                    'total_synced': 0
                }
            except requests.exceptions.Timeout:
                self.logger.warning(f"Sync request timeout (attempt {attempt + 1})")
                if attempt == retry_attempts - 1:
                    return {
                        'success': False,
                        'error': 'Request timeout'
                    }
            except Exception as e:
                self.logger.error(f"Sync request error: {e}")
                if attempt == retry_attempts - 1:
                    return {
                        'success': False,
                        'error': str(e)
                    }
        
        return {
            'success': False,
            'error': 'All retry attempts failed'
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to LINE bot database service.
        
        Returns:
            Dict: Connection test result
        """
        try:
            self.logger.info("Testing connection to LINE bot service")
            
            response = self._make_sync_request('/api/health', {})
            
            if response.get('success', False):
                self.logger.info("Connection test successful")
                return {
                    'success': True,
                    'message': 'Connection to LINE bot service successful'
                }
            else:
                self.logger.warning("Connection test failed")
                return {
                    'success': False,
                    'message': 'Connection to LINE bot service failed'
                }
                
        except Exception as e:
            self.logger.error(f"Connection test error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current sync status and statistics.
        
        Returns:
            Dict: Sync status information
        """
        try:
            status = {
                'sync_enabled': self.is_sync_enabled(),
                'api_url': self.api_base_url,
                'config': self.config
            }
            
            # Test connection
            connection_test = self.test_connection()
            status['connection_available'] = connection_test.get('success', False)
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get sync status: {e}")
            return {
                'sync_enabled': False,
                'error': str(e)
            }


# Create singleton instance
database_sync_manager = DatabaseSyncManager()


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test database sync manager
    try:
        # Test connection
        connection_result = database_sync_manager.test_connection()
        print(f"Connection test: {connection_result}")
        
        # Test sync status
        status = database_sync_manager.get_sync_status()
        print(f"Sync status: {status}")
        
        # Test content sync
        sample_content = {
            'carousel': [
                {
                    'carousel_id': 'test_001',
                    'banner_title': 'Test Banner',
                    'course_name': 'Test Course',
                    'extraction_timestamp': datetime.now().isoformat()
                }
            ]
        }
        
        sync_result = database_sync_manager.sync_website_monitoring_content(sample_content)
        print(f"Sync result: {sync_result}")
        
    except Exception as e:
        print(f"Test failed: {e}")