#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoring Controller Module for Website Monitoring
監控控制器模組

This module provides a high-level interface for controlling and managing
the website monitoring system, including configuration, status monitoring,
and operational controls.
"""

import os
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Import monitoring components
from website_monitor import WebsiteMonitor
from config_manager import ConfigManager


class MonitoringController:
    """
    High-level controller for website monitoring system
    
    Provides:
    - Monitoring system lifecycle management
    - Configuration management interface
    - Status monitoring and reporting
    - Performance monitoring and optimization
    - Error handling and recovery
    """
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize MonitoringController
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path, self.logger)
        
        # Initialize website monitor
        self.website_monitor = None
        
        # Controller state
        self.is_initialized = False
        self.last_status_check = None
        self.status_cache = {}
        self.performance_metrics = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'failed_cycles': 0,
            'average_cycle_time': 0,
            'last_cycle_time': None,
            'uptime_start': datetime.now()
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        self.logger.info("MonitoringController initialized")
    
    def initialize_system(self) -> Tuple[bool, str]:
        """
        Initialize the monitoring system
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            with self._lock:
                if self.is_initialized:
                    return True, "System already initialized"
                
                self.logger.info("Initializing monitoring system...")
                
                # Create default monitoring configuration if needed
                if not self.config_manager.create_default_monitoring_config():
                    return False, "Failed to create default monitoring configuration"
                
                # Validate configuration
                if not self.config_manager.validate_monitoring_config():
                    return False, "Monitoring configuration validation failed"
                
                # Initialize WebsiteMonitor
                self.website_monitor = WebsiteMonitor(
                    config_path=self.config_manager.config_path,
                    logger=self.logger
                )
                
                # Initialize monitoring components
                if not self.website_monitor.initialize_components():
                    return False, "Failed to initialize monitoring components"
                
                self.is_initialized = True
                self.performance_metrics['uptime_start'] = datetime.now()
                
                self.logger.info("Monitoring system initialized successfully")
                return True, "System initialized successfully"
                
        except Exception as e:
            error_msg = f"Error initializing monitoring system: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def start_monitoring(self, interval_minutes: int = None) -> Tuple[bool, str]:
        """
        Start continuous monitoring
        
        Args:
            interval_minutes: Monitoring interval in minutes (uses config default if None)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.is_initialized:
                init_success, init_msg = self.initialize_system()
                if not init_success:
                    return False, f"Initialization failed: {init_msg}"
            
            # Get monitoring interval from config if not provided
            if interval_minutes is None:
                monitoring_config = self.config_manager.get_website_monitoring_config()
                interval_minutes = monitoring_config.get('monitoring_interval', 3600) // 60
            
            # Start continuous monitoring
            success = self.website_monitor.start_continuous_monitoring(interval_minutes)
            
            if success:
                # Update configuration to enabled
                self.config_manager.enable_website_monitoring(interval_minutes)
                
                message = f"Monitoring started with {interval_minutes} minute interval"
                self.logger.info(message)
                return True, message
            else:
                return False, "Failed to start monitoring"
                
        except Exception as e:
            error_msg = f"Error starting monitoring: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def stop_monitoring(self) -> Tuple[bool, str]:
        """
        Stop continuous monitoring
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.website_monitor:
                return True, "Monitoring not running"
            
            success = self.website_monitor.stop_continuous_monitoring()
            
            if success:
                # Update configuration to disabled
                self.config_manager.disable_website_monitoring()
                
                message = "Monitoring stopped successfully"
                self.logger.info(message)
                return True, message
            else:
                return False, "Failed to stop monitoring"
                
        except Exception as e:
            error_msg = f"Error stopping monitoring: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def run_single_cycle(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run a single monitoring cycle
        
        Returns:
            Tuple[bool, str, Dict]: (success, message, cycle_results)
        """
        try:
            if not self.is_initialized:
                init_success, init_msg = self.initialize_system()
                if not init_success:
                    return False, f"Initialization failed: {init_msg}", {}
            
            self.logger.info("Running single monitoring cycle...")
            
            cycle_start = datetime.now()
            success = self.website_monitor.start_monitoring_cycle()
            cycle_end = datetime.now()
            
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            # Update performance metrics
            self._update_performance_metrics(success, cycle_duration)
            
            # Get cycle results
            cycle_results = {
                'success': success,
                'start_time': cycle_start,
                'end_time': cycle_end,
                'duration_seconds': cycle_duration,
                'monitoring_status': self.website_monitor.get_monitoring_status()
            }
            
            if success:
                message = f"Single cycle completed successfully in {cycle_duration:.1f} seconds"
                self.logger.info(message)
                return True, message, cycle_results
            else:
                message = "Single cycle failed"
                self.logger.error(message)
                return False, message, cycle_results
                
        except Exception as e:
            error_msg = f"Error running single cycle: {e}"
            self.logger.error(error_msg)
            return False, error_msg, {}
    
    def get_system_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Args:
            force_refresh: Force refresh of status cache
            
        Returns:
            Dict: System status information
        """
        try:
            # Check cache freshness
            cache_valid = (
                not force_refresh and 
                self.last_status_check and 
                (datetime.now() - self.last_status_check).seconds < 30
            )
            
            if cache_valid and self.status_cache:
                return self.status_cache
            
            # Gather system status
            status = {
                'timestamp': datetime.now(),
                'system_initialized': self.is_initialized,
                'configuration': self.config_manager.get_monitoring_config_summary(),
                'performance_metrics': self.performance_metrics.copy(),
                'monitoring_status': {},
                'component_status': {
                    'config_manager': True,
                    'website_monitor': self.website_monitor is not None
                }
            }
            
            # Get monitoring status if available
            if self.website_monitor:
                try:
                    status['monitoring_status'] = self.website_monitor.get_monitoring_status()
                    status['component_status']['website_monitor'] = True
                except Exception as e:
                    self.logger.warning(f"Error getting monitoring status: {e}")
                    status['component_status']['website_monitor'] = False
            
            # Calculate uptime
            uptime_delta = datetime.now() - self.performance_metrics['uptime_start']
            status['uptime_hours'] = uptime_delta.total_seconds() / 3600
            
            # Cache the status
            self.status_cache = status
            self.last_status_check = datetime.now()
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                'timestamp': datetime.now(),
                'error': str(e),
                'system_initialized': False
            }
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update monitoring configuration
        
        Args:
            config_updates: Configuration updates to apply
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info(f"Updating configuration: {config_updates}")
            
            success_count = 0
            total_updates = 0
            errors = []
            
            # Update website monitoring config
            if 'website_monitoring' in config_updates:
                total_updates += 1
                if self.config_manager.update_website_monitoring_config(config_updates['website_monitoring']):
                    success_count += 1
                else:
                    errors.append("Failed to update website monitoring config")
            
            # Update Chrome DevTools config
            if 'chrome_devtools' in config_updates:
                total_updates += 1
                if self.config_manager.update_chrome_devtools_config(config_updates['chrome_devtools']):
                    success_count += 1
                else:
                    errors.append("Failed to update Chrome DevTools config")
            
            # Update notification config
            if 'notifications' in config_updates:
                total_updates += 1
                if self.config_manager.update_notification_config(config_updates['notifications']):
                    success_count += 1
                else:
                    errors.append("Failed to update notification config")
            
            # Update data sync config
            if 'data_sync' in config_updates:
                total_updates += 1
                if self.config_manager.update_data_sync_config(config_updates['data_sync']):
                    success_count += 1
                else:
                    errors.append("Failed to update data sync config")
            
            # Update performance config
            if 'performance' in config_updates:
                total_updates += 1
                if self.config_manager.update_monitoring_performance_config(config_updates['performance']):
                    success_count += 1
                else:
                    errors.append("Failed to update performance config")
            
            # Update content type configs
            if 'content_types' in config_updates:
                for content_type, type_config in config_updates['content_types'].items():
                    total_updates += 1
                    enabled = type_config.get('enabled', True)
                    url = type_config.get('url')
                    
                    if self.config_manager.update_content_type_config(content_type, enabled, url):
                        success_count += 1
                    else:
                        errors.append(f"Failed to update {content_type} config")
            
            # Clear status cache to force refresh
            self.status_cache = {}
            self.last_status_check = None
            
            if success_count == total_updates:
                message = f"All {total_updates} configuration updates applied successfully"
                self.logger.info(message)
                return True, message
            elif success_count > 0:
                message = f"{success_count}/{total_updates} configuration updates applied. Errors: {'; '.join(errors)}"
                self.logger.warning(message)
                return False, message
            else:
                message = f"All configuration updates failed. Errors: {'; '.join(errors)}"
                self.logger.error(message)
                return False, message
                
        except Exception as e:
            error_msg = f"Error updating configuration: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def enable_content_type(self, content_type: str) -> Tuple[bool, str]:
        """
        Enable monitoring for specific content type
        
        Args:
            content_type: Type of content to enable
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            success = self.config_manager.update_content_type_config(content_type, True)
            
            if success:
                message = f"Content type '{content_type}' enabled"
                self.logger.info(message)
                return True, message
            else:
                message = f"Failed to enable content type '{content_type}'"
                self.logger.error(message)
                return False, message
                
        except Exception as e:
            error_msg = f"Error enabling content type '{content_type}': {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def disable_content_type(self, content_type: str) -> Tuple[bool, str]:
        """
        Disable monitoring for specific content type
        
        Args:
            content_type: Type of content to disable
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            success = self.config_manager.update_content_type_config(content_type, False)
            
            if success:
                message = f"Content type '{content_type}' disabled"
                self.logger.info(message)
                return True, message
            else:
                message = f"Failed to disable content type '{content_type}'"
                self.logger.error(message)
                return False, message
                
        except Exception as e:
            error_msg = f"Error disabling content type '{content_type}': {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get detailed performance report
        
        Returns:
            Dict: Performance report
        """
        try:
            status = self.get_system_status()
            
            report = {
                'timestamp': datetime.now(),
                'uptime_hours': status.get('uptime_hours', 0),
                'performance_metrics': self.performance_metrics.copy(),
                'success_rate': 0,
                'average_cycle_time': self.performance_metrics.get('average_cycle_time', 0),
                'monitoring_active': status.get('monitoring_status', {}).get('monitoring_active', False),
                'component_health': status.get('component_status', {}),
                'configuration_summary': status.get('configuration', {})
            }
            
            # Calculate success rate
            total_cycles = self.performance_metrics.get('total_cycles', 0)
            successful_cycles = self.performance_metrics.get('successful_cycles', 0)
            
            if total_cycles > 0:
                report['success_rate'] = (successful_cycles / total_cycles) * 100
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def cleanup_system(self) -> Tuple[bool, str]:
        """
        Clean up system resources
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info("Cleaning up monitoring system...")
            
            # Stop monitoring if running
            if self.website_monitor and self.website_monitor.monitoring_active:
                self.website_monitor.stop_continuous_monitoring()
            
            # Clean up website monitor
            if self.website_monitor:
                self.website_monitor.cleanup()
            
            # Reset state
            self.is_initialized = False
            self.website_monitor = None
            self.status_cache = {}
            self.last_status_check = None
            
            message = "System cleanup completed"
            self.logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"Error during system cleanup: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _update_performance_metrics(self, cycle_success: bool, cycle_duration: float):
        """
        Update performance metrics after a monitoring cycle
        
        Args:
            cycle_success: Whether the cycle was successful
            cycle_duration: Duration of the cycle in seconds
        """
        try:
            with self._lock:
                self.performance_metrics['total_cycles'] += 1
                self.performance_metrics['last_cycle_time'] = datetime.now()
                
                if cycle_success:
                    self.performance_metrics['successful_cycles'] += 1
                else:
                    self.performance_metrics['failed_cycles'] += 1
                
                # Update average cycle time
                current_avg = self.performance_metrics['average_cycle_time']
                total_cycles = self.performance_metrics['total_cycles']
                
                if total_cycles == 1:
                    self.performance_metrics['average_cycle_time'] = cycle_duration
                else:
                    # Calculate running average
                    self.performance_metrics['average_cycle_time'] = (
                        (current_avg * (total_cycles - 1) + cycle_duration) / total_cycles
                    )
                    
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")


# Example usage and testing
def main():
    """
    Example usage of MonitoringController
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('monitoring_controller_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    controller = None
    try:
        # Initialize MonitoringController
        logger.info("Initializing MonitoringController...")
        controller = MonitoringController(logger=logger)
        
        # Initialize system
        success, message = controller.initialize_system()
        logger.info(f"System initialization: {success} - {message}")
        
        if success:
            # Get system status
            status = controller.get_system_status()
            logger.info(f"System status: {status}")
            
            # Run single cycle test
            success, message, results = controller.run_single_cycle()
            logger.info(f"Single cycle test: {success} - {message}")
            
            # Get performance report
            report = controller.get_performance_report()
            logger.info(f"Performance report: {report}")
            
            # Test configuration update
            config_updates = {
                'chrome_devtools': {
                    'enabled': True,
                    'headless': True
                }
            }
            success, message = controller.update_configuration(config_updates)
            logger.info(f"Configuration update: {success} - {message}")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
    finally:
        if controller:
            controller.cleanup_system()


if __name__ == "__main__":
    main()