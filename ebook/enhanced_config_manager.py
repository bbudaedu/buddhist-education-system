#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Configuration Manager for Website Monitoring
Extends existing ConfigManager with website monitoring capabilities

This module provides enhanced configuration management for:
- Website monitoring settings
- Chrome DevTools integration
- Content type configuration
- Baseline management for multiple content types
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from config_manager import ConfigManager


class EnhancedConfigManager(ConfigManager):
    """
    Enhanced configuration manager extending base ConfigManager
    
    Adds support for:
    - Website monitoring configuration
    - Chrome DevTools settings
    - Content type baselines
    - Monitoring schedules
    """
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize EnhancedConfigManager
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for logging operations
        """
        super().__init__(config_path, logger)
        
        # Initialize website monitoring configuration if not present
        self._ensure_website_monitoring_config()
    
    def _ensure_website_monitoring_config(self) -> bool:
        """
        Ensure website monitoring configuration exists in config
        
        Returns:
            bool: True if configuration exists or was created, False otherwise
        """
        try:
            if 'website_monitoring' not in self.config:
                self.logger.info("初始化網站監控配置...")
                
                default_monitoring_config = {
                    "enabled": True,
                    "monitoring_interval": 3600,
                    "content_types": {
                        "carousel": {
                            "enabled": True,
                            "url": "https://www.budaedu.org/#/",
                            "baseline": ""
                        },
                        "cancellation": {
                            "enabled": True,
                            "url": "https://www.budaedu.org/#/bulletins/course-cancel",
                            "baseline": ""
                        },
                        "news": {
                            "enabled": True,
                            "url": "https://www.budaedu.org/#/bulletins/",
                            "baseline": ""
                        },
                        "media": {
                            "enabled": True,
                            "url": "https://www.budaedu.org/#/series/live-streaming",
                            "baseline": ""
                        }
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
                
                self.config['website_monitoring'] = default_monitoring_config
                
                if self.save_config():
                    self.logger.info("網站監控配置已初始化")
                    return True
                else:
                    self.logger.error("儲存網站監控配置失敗")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"確保網站監控配置時發生錯誤: {e}")
            return False
    
    def get_website_monitoring_config(self) -> Dict[str, Any]:
        """
        Get website monitoring configuration
        
        Returns:
            Dict: Website monitoring configuration
        """
        return self.config.get('website_monitoring', {})
    
    def is_website_monitoring_enabled(self) -> bool:
        """
        Check if website monitoring is enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_website_monitoring_config().get('enabled', False)
    
    def get_content_type_config(self, content_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific content type
        
        Args:
            content_type: Content type to get configuration for
            
        Returns:
            Dict: Content type configuration
        """
        content_types = self.get_website_monitoring_config().get('content_types', {})
        return content_types.get(content_type, {})
    
    def is_content_type_enabled(self, content_type: str) -> bool:
        """
        Check if a content type is enabled
        
        Args:
            content_type: Content type to check
            
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_content_type_config(content_type).get('enabled', False)
    
    def get_content_type_url(self, content_type: str) -> str:
        """
        Get URL for a specific content type
        
        Args:
            content_type: Content type to get URL for
            
        Returns:
            str: URL for the content type
        """
        return self.get_content_type_config(content_type).get('url', '')
    
    def get_content_type_baseline(self, content_type: str) -> str:
        """
        Get baseline for a specific content type
        
        Args:
            content_type: Content type to get baseline for
            
        Returns:
            str: Baseline value for the content type
        """
        return self.get_content_type_config(content_type).get('baseline', '')
    
    def update_content_type_baseline(self, content_type: str, baseline: str) -> bool:
        """
        Update baseline for a specific content type
        
        Args:
            content_type: Content type to update baseline for
            baseline: New baseline value
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            if 'website_monitoring' not in self.config:
                self._ensure_website_monitoring_config()
            
            content_types = self.config['website_monitoring'].get('content_types', {})
            if content_type not in content_types:
                self.logger.warning(f"內容類型不存在: {content_type}")
                return False
            
            old_baseline = content_types[content_type].get('baseline', '')
            content_types[content_type]['baseline'] = baseline
            
            # Update last run date
            self.config['website_monitoring']['last_run_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if self.save_config():
                self.logger.info(f"{content_type} 基準已更新:")
                self.logger.info(f"  舊基準: {old_baseline}")
                self.logger.info(f"  新基準: {baseline}")
                return True
            else:
                self.logger.error(f"儲存 {content_type} 基準失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新 {content_type} 基準時發生錯誤: {e}")
            return False
    
    def get_chrome_devtools_config(self) -> Dict[str, Any]:
        """
        Get Chrome DevTools configuration
        
        Returns:
            Dict: Chrome DevTools configuration
        """
        return self.get_website_monitoring_config().get('chrome_devtools', {})
    
    def is_chrome_devtools_enabled(self) -> bool:
        """
        Check if Chrome DevTools is enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_chrome_devtools_config().get('enabled', False)
    
    def enable_chrome_devtools(self, enabled: bool = True) -> bool:
        """
        Enable or disable Chrome DevTools
        
        Args:
            enabled: Whether to enable Chrome DevTools
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            if 'website_monitoring' not in self.config:
                self._ensure_website_monitoring_config()
            
            self.config['website_monitoring']['chrome_devtools']['enabled'] = enabled
            
            if self.save_config():
                status = "啟用" if enabled else "停用"
                self.logger.info(f"Chrome DevTools 已{status}")
                return True
            else:
                self.logger.error("更新 Chrome DevTools 設定失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新 Chrome DevTools 設定時發生錯誤: {e}")
            return False
    
    def get_data_sync_config(self) -> Dict[str, Any]:
        """
        Get data synchronization configuration
        
        Returns:
            Dict: Data sync configuration
        """
        return self.get_website_monitoring_config().get('data_sync', {})
    
    def get_excel_output_dir(self) -> str:
        """
        Get Excel output directory for website monitoring
        
        Returns:
            str: Excel output directory path
        """
        return self.get_data_sync_config().get('excel_output_dir', 'generated_documents/website_monitoring')
    
    def get_notification_config(self) -> Dict[str, Any]:
        """
        Get notification configuration
        
        Returns:
            Dict: Notification configuration
        """
        return self.get_website_monitoring_config().get('notifications', {})
    
    def is_line_notifications_enabled(self) -> bool:
        """
        Check if LINE notifications are enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_notification_config().get('line_enabled', False)
    
    def is_email_notifications_enabled(self) -> bool:
        """
        Check if email notifications are enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.get_notification_config().get('email_enabled', False)
    
    def get_immediate_alert_types(self) -> List[str]:
        """
        Get content types that should trigger immediate alerts
        
        Returns:
            List[str]: List of content types for immediate alerts
        """
        return self.get_notification_config().get('immediate_alerts', [])
    
    def get_daily_summary_types(self) -> List[str]:
        """
        Get content types that should be included in daily summaries
        
        Returns:
            List[str]: List of content types for daily summaries
        """
        return self.get_notification_config().get('daily_summary', [])
    
    def get_monitoring_interval(self) -> int:
        """
        Get monitoring interval in seconds
        
        Returns:
            int: Monitoring interval in seconds
        """
        return self.get_website_monitoring_config().get('monitoring_interval', 3600)
    
    def update_monitoring_interval(self, interval: int) -> bool:
        """
        Update monitoring interval
        
        Args:
            interval: New monitoring interval in seconds
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            if interval <= 0:
                self.logger.error("監控間隔必須大於 0")
                return False
            
            if 'website_monitoring' not in self.config:
                self._ensure_website_monitoring_config()
            
            old_interval = self.config['website_monitoring'].get('monitoring_interval', 3600)
            self.config['website_monitoring']['monitoring_interval'] = interval
            
            if self.save_config():
                self.logger.info(f"監控間隔已更新: {old_interval} -> {interval} 秒")
                return True
            else:
                self.logger.error("更新監控間隔失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"更新監控間隔時發生錯誤: {e}")
            return False
    
    def validate_website_monitoring_config(self) -> bool:
        """
        Validate website monitoring configuration
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            monitoring_config = self.get_website_monitoring_config()
            
            if not monitoring_config:
                self.logger.error("網站監控配置不存在")
                return False
            
            # Check required fields
            required_fields = ['enabled', 'content_types', 'chrome_devtools', 'data_sync', 'notifications']
            missing_fields = []
            
            for field in required_fields:
                if field not in monitoring_config:
                    missing_fields.append(field)
            
            if missing_fields:
                self.logger.error(f"網站監控配置缺少必要欄位: {missing_fields}")
                return False
            
            # Validate content types
            content_types = monitoring_config.get('content_types', {})
            expected_content_types = ['carousel', 'cancellation', 'news', 'media']
            
            for content_type in expected_content_types:
                if content_type not in content_types:
                    self.logger.warning(f"內容類型配置缺少: {content_type}")
                else:
                    type_config = content_types[content_type]
                    if 'enabled' not in type_config or 'url' not in type_config:
                        self.logger.error(f"{content_type} 配置不完整")
                        return False
            
            self.logger.info("網站監控配置驗證通過")
            return True
            
        except Exception as e:
            self.logger.error(f"驗證網站監控配置時發生錯誤: {e}")
            return False


def main():
    """
    Example usage and testing of EnhancedConfigManager
    """
    import sys
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Test EnhancedConfigManager
        config_manager = EnhancedConfigManager(logger=logger)
        
        # Test website monitoring configuration
        logger.info(f"網站監控啟用: {config_manager.is_website_monitoring_enabled()}")
        logger.info(f"Chrome DevTools 啟用: {config_manager.is_chrome_devtools_enabled()}")
        
        # Test content type configuration
        content_types = ['carousel', 'cancellation', 'news', 'media']
        for content_type in content_types:
            enabled = config_manager.is_content_type_enabled(content_type)
            url = config_manager.get_content_type_url(content_type)
            baseline = config_manager.get_content_type_baseline(content_type)
            logger.info(f"{content_type}: 啟用={enabled}, URL={url}, 基準={baseline}")
        
        # Test configuration validation
        is_valid = config_manager.validate_website_monitoring_config()
        logger.info(f"配置驗證: {'通過' if is_valid else '失敗'}")
        
        # Test baseline update (if command line argument provided)
        if len(sys.argv) > 2:
            content_type = sys.argv[1]
            new_baseline = sys.argv[2]
            logger.info(f"測試更新 {content_type} 基準為: {new_baseline}")
            
            success = config_manager.update_content_type_baseline(content_type, new_baseline)
            if success:
                logger.info("基準更新測試成功")
            else:
                logger.error("基準更新測試失敗")
        
    except Exception as e:
        logger.error(f"測試執行錯誤: {e}", exc_info=True)


if __name__ == "__main__":
    main()