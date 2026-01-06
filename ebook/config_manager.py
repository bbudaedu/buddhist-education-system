#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager Module for New Book Summary System
新書摘要系統的配置管理模組

This module handles configuration file operations including:
- Loading and saving configuration
- Updating baseline book title after processing
- Maintaining configuration integrity
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigManager:
    """
    Configuration manager for handling config.json operations
    
    Handles:
    - Loading configuration from file
    - Updating baseline book title after successful processing
    - Saving configuration with backup
    - Configuration validation
    """
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for logging operations
        """
        self.config_path = config_path
        self.logger = logger or logging.getLogger(__name__)
        self.config = {}
        
        # Load configuration on initialization
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Returns:
            Dict: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"配置檔案不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.logger.info(f"配置已載入: {self.config_path}")
            self.logger.debug(f"當前 baseline_book_title: {self.config.get('baseline_book_title', 'Not set')}")
            
            # Allow environment variables to override config
            if os.environ.get('CHROMEDRIVER_PATH'):
                self.config['chromedriver_path'] = os.environ.get('CHROMEDRIVER_PATH')
                self.logger.info(f"使用環境變數覆寫 chromedriver_path: {self.config['chromedriver_path']}")
                
            if os.environ.get('DOWNLOAD_DIR'):
                self.config['download_dir'] = os.environ.get('DOWNLOAD_DIR')
                self.logger.info(f"使用環境變數覆寫 download_dir: {self.config['download_dir']}")
            
            return self.config
            
        except FileNotFoundError:
            self.logger.error(f"配置檔案不存在: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"配置檔案格式錯誤: {e}")
            raise
        except Exception as e:
            self.logger.error(f"載入配置時發生錯誤: {e}")
            raise
    
    def save_config(self, backup: bool = True) -> bool:
        """
        Save current configuration to file with optional backup
        
        Args:
            backup: Whether to create backup before saving
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create backup if requested
            if backup and os.path.exists(self.config_path):
                backup_path = f"{self.config_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    import shutil
                    shutil.copy2(self.config_path, backup_path)
                    self.logger.info(f"配置備份已建立: {backup_path}")
                except Exception as backup_error:
                    self.logger.warning(f"建立配置備份失敗: {backup_error}")
                    # Continue saving even if backup fails
            
            # Save configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"配置已儲存: {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"儲存配置時發生錯誤: {e}")
            return False
    
    def update_baseline_book_title(self, new_baseline_title: str) -> bool:
        """
        Update baseline book title in configuration
        
        Args:
            new_baseline_title: New baseline book title to set
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            if not new_baseline_title or not new_baseline_title.strip():
                self.logger.warning("新的基準書籍標題為空，跳過更新")
                return False
            
            old_baseline = self.config.get('baseline_book_title', '')
            self.config['baseline_book_title'] = new_baseline_title.strip()
            
            # Update last run date
            self.config['last_run_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save configuration
            if self.save_config():
                self.logger.info(f"基準書籍標題已更新:")
                self.logger.info(f"  舊標題: {old_baseline}")
                self.logger.info(f"  新標題: {new_baseline_title}")
                self.logger.info(f"  更新時間: {self.config['last_run_date']}")
                return True
            else:
                self.logger.error("儲存配置失敗，基準書籍標題更新失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新基準書籍標題時發生錯誤: {e}")
            return False
    
    def get_baseline_book_title(self) -> str:
        """
        Get current baseline book title
        
        Returns:
            str: Current baseline book title
        """
        return self.config.get('baseline_book_title', '')
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration dictionary
        
        Returns:
            Dict: Current configuration
        """
        return self.config.copy()
    
    def update_config_value(self, key: str, value: Any) -> bool:
        """
        Update a specific configuration value
        
        Args:
            key: Configuration key to update
            value: New value to set
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            old_value = self.config.get(key, None)
            self.config[key] = value
            
            if self.save_config():
                self.logger.info(f"配置項目已更新: {key}")
                self.logger.debug(f"  舊值: {old_value}")
                self.logger.debug(f"  新值: {value}")
                return True
            else:
                self.logger.error(f"更新配置項目失敗: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"更新配置項目時發生錯誤 ({key}): {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate current configuration for required fields
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = [
            'gemini_api_key',
            'chromedriver_path',
            'target_url',
            'download_dir',
            'smtp_server',
            'smtp_port',
            'smtp_username',
            'smtp_password',
            'email_recipients'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in self.config or not self.config[field]:
                missing_fields.append(field)
        
        if missing_fields:
            self.logger.error(f"配置驗證失敗，缺少必要欄位: {missing_fields}")
            return False
        
        self.logger.info("配置驗證通過")
        return True
    
    def get_chrome_devtools_config(self) -> Dict[str, Any]:
        """
        Get Chrome DevTools configuration settings
        
        Returns:
            Dict: Chrome DevTools configuration
        """
        default_devtools_config = {
            "enabled": False,
            "headless": True,
            "timeout": 30,
            "debug_port": 9222,
            "fallback_to_selenium": True
        }
        
        website_monitoring = self.config.get('website_monitoring', {})
        devtools_config = website_monitoring.get('chrome_devtools', {})
        
        # Merge with defaults
        result = default_devtools_config.copy()
        result.update(devtools_config)
        
        return result
    
    def update_chrome_devtools_config(self, devtools_config: Dict[str, Any]) -> bool:
        """
        Update Chrome DevTools configuration
        
        Args:
            devtools_config: New DevTools configuration
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            # Update chrome_devtools section
            self.config['website_monitoring']['chrome_devtools'] = devtools_config
            
            if self.save_config():
                self.logger.info("Chrome DevTools 配置已更新")
                self.logger.debug(f"新配置: {devtools_config}")
                return True
            else:
                self.logger.error("更新 Chrome DevTools 配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新 Chrome DevTools 配置時發生錯誤: {e}")
            return False
    
    def enable_chrome_devtools(self, headless: bool = True, timeout: int = 30) -> bool:
        """
        Enable Chrome DevTools with specified settings
        
        Args:
            headless: Run in headless mode
            timeout: DevTools timeout in seconds
            
        Returns:
            bool: True if enabled successfully, False otherwise
        """
        devtools_config = {
            "enabled": True,
            "headless": headless,
            "timeout": timeout,
            "debug_port": 9222,
            "fallback_to_selenium": True
        }
        
        return self.update_chrome_devtools_config(devtools_config)
    
    def disable_chrome_devtools(self) -> bool:
        """
        Disable Chrome DevTools
        
        Returns:
            bool: True if disabled successfully, False otherwise
        """
        current_config = self.get_chrome_devtools_config()
        current_config["enabled"] = False
        
        return self.update_chrome_devtools_config(current_config)
    
    def update_website_monitoring_config(self, monitoring_config: Dict[str, Any]) -> bool:
        """
        Update website monitoring configuration
        
        Args:
            monitoring_config: New monitoring configuration
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            # Update monitoring configuration
            self.config['website_monitoring'].update(monitoring_config)
            
            if self.save_config():
                self.logger.info("網站監控配置已更新")
                self.logger.debug(f"新配置: {monitoring_config}")
                return True
            else:
                self.logger.error("更新網站監控配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新網站監控配置時發生錯誤: {e}")
            return False
    
    def enable_website_monitoring(self, interval_minutes: int = 60) -> bool:
        """
        Enable website monitoring with specified interval
        
        Args:
            interval_minutes: Monitoring interval in minutes
            
        Returns:
            bool: True if enabled successfully, False otherwise
        """
        monitoring_config = {
            "enabled": True,
            "monitoring_interval": interval_minutes * 60  # Convert to seconds
        }
        
        return self.update_website_monitoring_config(monitoring_config)
    
    def disable_website_monitoring(self) -> bool:
        """
        Disable website monitoring
        
        Returns:
            bool: True if disabled successfully, False otherwise
        """
        monitoring_config = {
            "enabled": False
        }
        
        return self.update_website_monitoring_config(monitoring_config)
    
    def update_content_type_config(self, content_type: str, enabled: bool, url: str = None) -> bool:
        """
        Update configuration for specific content type
        
        Args:
            content_type: Type of content ('carousel', 'cancellation', 'news', 'media')
            enabled: Whether this content type should be monitored
            url: URL for this content type (optional)
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            if 'content_types' not in self.config['website_monitoring']:
                self.config['website_monitoring']['content_types'] = {}
            
            # Update content type configuration
            content_config = {'enabled': enabled}
            if url:
                content_config['url'] = url
            
            self.config['website_monitoring']['content_types'][content_type] = content_config
            
            if self.save_config():
                self.logger.info(f"內容類型 {content_type} 配置已更新: enabled={enabled}")
                return True
            else:
                self.logger.error(f"更新內容類型 {content_type} 配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新內容類型配置時發生錯誤: {e}")
            return False
    
    def update_notification_config(self, notification_config: Dict[str, Any]) -> bool:
        """
        Update notification configuration
        
        Args:
            notification_config: New notification configuration
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            # Update notifications section
            self.config['website_monitoring']['notifications'] = notification_config
            
            if self.save_config():
                self.logger.info("通知配置已更新")
                self.logger.debug(f"新配置: {notification_config}")
                return True
            else:
                self.logger.error("更新通知配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新通知配置時發生錯誤: {e}")
            return False
    
    def get_monitoring_performance_config(self) -> Dict[str, Any]:
        """
        Get monitoring performance configuration
        
        Returns:
            Dict: Performance configuration settings
        """
        default_performance_config = {
            "max_concurrent_scrapers": 2,
            "request_delay_seconds": 2,
            "retry_attempts": 3,
            "timeout_seconds": 30,
            "memory_limit_mb": 512,
            "log_level": "INFO"
        }
        
        website_monitoring = self.config.get('website_monitoring', {})
        performance_config = website_monitoring.get('performance', {})
        
        # Merge with defaults
        result = default_performance_config.copy()
        result.update(performance_config)
        
        return result
    
    def update_monitoring_performance_config(self, performance_config: Dict[str, Any]) -> bool:
        """
        Update monitoring performance configuration
        
        Args:
            performance_config: New performance configuration
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            # Update performance section
            self.config['website_monitoring']['performance'] = performance_config
            
            if self.save_config():
                self.logger.info("監控效能配置已更新")
                self.logger.debug(f"新配置: {performance_config}")
                return True
            else:
                self.logger.error("更新監控效能配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新監控效能配置時發生錯誤: {e}")
            return False
    
    def get_data_sync_config(self) -> Dict[str, Any]:
        """
        Get data synchronization configuration
        
        Returns:
            Dict: Data sync configuration settings
        """
        default_sync_config = {
            "excel_output_dir": "generated_documents/website_monitoring",
            "mysql_batch_size": 100,
            "backup_enabled": True,
            "cleanup_old_files_days": 30,
            "excel_enabled": True,
            "mysql_enabled": False
        }
        
        website_monitoring = self.config.get('website_monitoring', {})
        sync_config = website_monitoring.get('data_sync', {})
        
        # Merge with defaults
        result = default_sync_config.copy()
        result.update(sync_config)
        
        return result
    
    def update_data_sync_config(self, sync_config: Dict[str, Any]) -> bool:
        """
        Update data synchronization configuration
        
        Args:
            sync_config: New data sync configuration
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Ensure website_monitoring section exists
            if 'website_monitoring' not in self.config:
                self.config['website_monitoring'] = {}
            
            # Update data_sync section
            self.config['website_monitoring']['data_sync'] = sync_config
            
            if self.save_config():
                self.logger.info("資料同步配置已更新")
                self.logger.debug(f"新配置: {sync_config}")
                return True
            else:
                self.logger.error("更新資料同步配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新資料同步配置時發生錯誤: {e}")
            return False
    
    def create_default_monitoring_config(self) -> bool:
        """
        Create default website monitoring configuration if it doesn't exist
        
        Returns:
            bool: True if default config created successfully, False otherwise
        """
        try:
            # Check if monitoring config already exists
            if 'website_monitoring' in self.config and self.config['website_monitoring']:
                self.logger.info("網站監控配置已存在，跳過建立預設配置")
                return True
            
            # Create default monitoring configuration
            default_config = {
                "enabled": False,
                "monitoring_interval": 3600,  # 1 hour in seconds
                "content_types": {
                    "carousel": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/"
                    },
                    "cancellation": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/course-cancel"
                    },
                    "news": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/bulletins/"
                    },
                    "media": {
                        "enabled": True,
                        "url": "https://www.budaedu.org/#/series/live-streaming"
                    }
                },
                "chrome_devtools": {
                    "enabled": False,
                    "headless": True,
                    "timeout": 30,
                    "debug_port": 9222,
                    "fallback_to_selenium": True
                },
                "data_sync": {
                    "excel_output_dir": "generated_documents/website_monitoring",
                    "mysql_batch_size": 100,
                    "backup_enabled": True,
                    "cleanup_old_files_days": 30,
                    "excel_enabled": True,
                    "mysql_enabled": False
                },
                "notifications": {
                    "line_enabled": False,
                    "email_enabled": True,
                    "immediate_alerts": ["cancellation"],
                    "daily_summary": ["carousel", "news", "media"],
                    "cycle_notifications": False
                },
                "performance": {
                    "max_concurrent_scrapers": 2,
                    "request_delay_seconds": 2,
                    "retry_attempts": 3,
                    "timeout_seconds": 30,
                    "memory_limit_mb": 512,
                    "log_level": "INFO"
                }
            }
            
            # Set the default configuration
            self.config['website_monitoring'] = default_config
            
            if self.save_config():
                self.logger.info("預設網站監控配置已建立")
                return True
            else:
                self.logger.error("建立預設網站監控配置失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"建立預設監控配置時發生錯誤: {e}")
            return False
    
    def validate_monitoring_config(self) -> bool:
        """
        Validate website monitoring configuration
        
        Returns:
            bool: True if monitoring configuration is valid, False otherwise
        """
        try:
            monitoring_config = self.get_website_monitoring_config()
            
            # Check required sections
            required_sections = ['content_types', 'chrome_devtools', 'data_sync', 'notifications']
            for section in required_sections:
                if section not in monitoring_config:
                    self.logger.error(f"監控配置缺少必要區段: {section}")
                    return False
            
            # Validate content types
            content_types = monitoring_config.get('content_types', {})
            required_content_types = ['carousel', 'cancellation', 'news', 'media']
            
            for content_type in required_content_types:
                if content_type not in content_types:
                    self.logger.warning(f"監控配置缺少內容類型: {content_type}")
                else:
                    type_config = content_types[content_type]
                    if 'enabled' not in type_config or 'url' not in type_config:
                        self.logger.error(f"內容類型 {content_type} 配置不完整")
                        return False
            
            # Validate Chrome DevTools config
            devtools_config = monitoring_config.get('chrome_devtools', {})
            if 'enabled' not in devtools_config:
                self.logger.error("Chrome DevTools 配置缺少 enabled 設定")
                return False
            
            # Validate notification config
            notification_config = monitoring_config.get('notifications', {})
            required_notification_fields = ['line_enabled', 'email_enabled']
            for field in required_notification_fields:
                if field not in notification_config:
                    self.logger.error(f"通知配置缺少必要欄位: {field}")
                    return False
            
            self.logger.info("網站監控配置驗證通過")
            return True
            
        except Exception as e:
            self.logger.error(f"驗證監控配置時發生錯誤: {e}")
            return False
    
    def get_monitoring_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current monitoring configuration
        
        Returns:
            Dict: Configuration summary
        """
        try:
            monitoring_config = self.get_website_monitoring_config()
            
            summary = {
                'monitoring_enabled': monitoring_config.get('enabled', False),
                'monitoring_interval_minutes': monitoring_config.get('monitoring_interval', 3600) // 60,
                'chrome_devtools_enabled': monitoring_config.get('chrome_devtools', {}).get('enabled', False),
                'content_types_enabled': {},
                'notifications_enabled': {
                    'line': monitoring_config.get('notifications', {}).get('line_enabled', False),
                    'email': monitoring_config.get('notifications', {}).get('email_enabled', False)
                },
                'data_sync_enabled': {
                    'excel': monitoring_config.get('data_sync', {}).get('excel_enabled', True),
                    'mysql': monitoring_config.get('data_sync', {}).get('mysql_enabled', False)
                }
            }
            
            # Get content type status
            content_types = monitoring_config.get('content_types', {})
            for content_type, config in content_types.items():
                summary['content_types_enabled'][content_type] = config.get('enabled', False)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"獲取監控配置摘要時發生錯誤: {e}")
            return {'error': str(e)}
    
    def get_website_monitoring_config(self) -> Dict[str, Any]:
        """
        Get website monitoring configuration
        
        Returns:
            Dict: Website monitoring configuration
        """
        default_monitoring_config = {
            "enabled": False,
            "monitoring_interval": 3600,
            "content_types": {
                "carousel": {"enabled": True, "url": "https://www.budaedu.org/#/"},
                "cancellation": {"enabled": True, "url": "https://www.budaedu.org/#/bulletins/course-cancel"},
                "news": {"enabled": True, "url": "https://www.budaedu.org/#/bulletins/"},
                "media": {"enabled": True, "url": "https://www.budaedu.org/#/series/live-streaming"}
            },
            "chrome_devtools": {
                "enabled": False,
                "headless": True,
                "timeout": 30
            },
            "data_sync": {
                "excel_output_dir": "generated_documents/website_monitoring",
                "mysql_batch_size": 100,
                "backup_enabled": True
            },
            "notifications": {
                "line_enabled": True,
                "email_enabled": True,
                "immediate_alerts": ["cancellation"],
                "daily_summary": ["carousel", "news", "media"]
            }
        }
        
        monitoring_config = self.config.get('website_monitoring', {})
        
        # Merge with defaults
        result = default_monitoring_config.copy()
        result.update(monitoring_config)
        
        return result
    
    def get_last_run_date(self) -> Optional[str]:
        """
        Get last run date from configuration
        
        Returns:
            str: Last run date string or None if not set
        """
        return self.config.get('last_run_date')
    
    def reset_baseline_to_empty(self) -> bool:
        """
        Reset baseline book title to empty (for testing or manual reset)
        
        Returns:
            bool: True if reset successfully, False otherwise
        """
        return self.update_baseline_book_title("")
    
    def create_config_from_template(self, template_path: str = "config_template.json") -> bool:
        """
        Create config.json from template if it doesn't exist
        
        Args:
            template_path: Path to configuration template file
            
        Returns:
            bool: True if created successfully, False otherwise
        """
        try:
            if os.path.exists(self.config_path):
                self.logger.info(f"配置檔案已存在: {self.config_path}")
                return True
            
            if not os.path.exists(template_path):
                self.logger.error(f"配置模板不存在: {template_path}")
                return False
            
            # Load template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_config = json.load(f)
            
            # Save as config.json
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"配置檔案已從模板建立: {self.config_path}")
            
            # Reload configuration
            self.load_config()
            return True
            
        except Exception as e:
            self.logger.error(f"從模板建立配置檔案時發生錯誤: {e}")
            return False


# Utility functions for backward compatibility
def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file (standalone function)
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict: Configuration dictionary
    """
    manager = ConfigManager(config_path)
    return manager.get_config()


def update_baseline_book_title(new_title: str, config_path: str = "config.json") -> bool:
    """
    Update baseline book title in configuration file (standalone function)
    
    Args:
        new_title: New baseline book title
        config_path: Path to configuration file
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    manager = ConfigManager(config_path)
    return manager.update_baseline_book_title(new_title)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Test ConfigManager
        config_manager = ConfigManager(logger=logger)
        
        # Test loading configuration
        config = config_manager.get_config()
        logger.info(f"Current baseline: {config_manager.get_baseline_book_title()}")
        
        # Test updating baseline (if command line argument provided)
        if len(sys.argv) > 1:
            new_baseline = sys.argv[1]
            logger.info(f"Testing baseline update to: {new_baseline}")
            
            success = config_manager.update_baseline_book_title(new_baseline)
            if success:
                logger.info("Baseline update test successful")
            else:
                logger.error("Baseline update test failed")
        
        # Test configuration validation
        is_valid = config_manager.validate_config()
        logger.info(f"Configuration validation: {'PASS' if is_valid else 'FAIL'}")
        
    except Exception as e:
        logger.error(f"Test execution error: {e}", exc_info=True)