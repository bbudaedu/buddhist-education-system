import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class DatabaseSyncManager:
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
        return self.config.get('enabled', True)
    
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

    def sync_website_monitoring_content(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync website monitoring content to database via API.
        
        Args:
            structured_data: Dictionary containing structured data for sync
            
        Returns:
            Dict: Sync result
        """
        try:
            if not self.is_sync_enabled():
                return {'success': True, 'message': 'Sync disabled'}
                
            self.logger.info("Syncing website monitoring content to database...")
            
            # Call the API endpoint
            response = self._make_sync_request('/api/sync/website-monitoring', structured_data)
            
            if response.get('success', False):
                self.logger.info("Website monitoring content synced successfully")
            else:
                self.logger.warning(f"Website monitoring content sync failed: {response.get('error', 'Unknown error')}")
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error syncing website monitoring content: {e}")
            return {'success': False, 'error': str(e)}


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