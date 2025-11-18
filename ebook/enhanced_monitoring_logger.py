#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Monitoring Logger for Website Monitoring System
增強型網站監控日誌系統

This module extends the existing monitoring logger with additional capabilities
for comprehensive logging, performance metrics, and system health monitoring.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import psutil

# Import existing monitoring infrastructure
from monitoring_logger import MonitoringLogger, get_monitoring_logger, OperationTimer
from system_status_reporter import StatusReportGenerator
from monitoring_dashboard import SystemHealthChecker


class EnhancedMonitoringLogger(MonitoringLogger):
    """
    Enhanced monitoring logger with additional capabilities
    
    Extends MonitoringLogger with:
    - Real-time performance tracking
    - Advanced health monitoring
    - Automated alerting
    - Comprehensive metrics collection
    - Integration with existing infrastructure
    """
    
    def __init__(self, name: str = "website_monitoring_enhanced", log_dir: str = "logs"):
        """
        Initialize enhanced monitoring logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        super().__init__(name, log_dir)
        
        # Enhanced metrics tracking
        self.real_time_metrics = {
            'operations_per_minute': [],
            'error_rates': [],
            'response_times': [],
            'system_resources': [],
            'component_health': {}
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'error_rate_warning': 5.0,
            'error_rate_critical': 15.0,
            'response_time_warning': 30.0,
            'response_time_critical': 60.0,
            'cpu_usage_warning': 80.0,
            'cpu_usage_critical': 95.0,
            'memory_usage_warning': 85.0,
            'memory_usage_critical': 95.0
        }
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_lock = threading.Lock()
        
        # Integration components
        self.health_checker = SystemHealthChecker(self)
        self.status_reporter = None
        
        self.log_info("Enhanced Monitoring Logger initialized", 
                     component="enhanced_logger", 
                     version="1.0.0")
    
    def start_real_time_monitoring(self, interval_seconds: int = 60):
        """
        Start real-time monitoring thread
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        try:
            if self.monitoring_active:
                self.log_warning("Real-time monitoring already active")
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._real_time_monitoring_loop,
                args=(interval_seconds,),
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.log_info("Real-time monitoring started", 
                         interval_seconds=interval_seconds,
                         component="real_time_monitor")
            
        except Exception as e:
            self.log_error(f"Error starting real-time monitoring: {e}")
    
    def stop_real_time_monitoring(self):
        """Stop real-time monitoring thread"""
        try:
            if not self.monitoring_active:
                return
            
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            self.log_info("Real-time monitoring stopped", component="real_time_monitor")
            
        except Exception as e:
            self.log_error(f"Error stopping real-time monitoring: {e}")
    
    def _real_time_monitoring_loop(self, interval_seconds: int):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect performance metrics
                self._collect_performance_metrics()
                
                # Check for alerts
                self._check_alert_conditions()
                
                # Sleep for interval
                time.sleep(interval_seconds)
                
            except Exception as e:
                self.log_error(f"Error in real-time monitoring loop: {e}")
                time.sleep(interval_seconds)
    
    def _collect_system_metrics(self):
        """Collect system resource metrics"""
        try:
            # Get system resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            system_metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': (disk.used / disk.total) * 100,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
            
            with self.metrics_lock:
                self.real_time_metrics['system_resources'].append(system_metrics)
                
                # Keep only last 100 entries
                if len(self.real_time_metrics['system_resources']) > 100:
                    self.real_time_metrics['system_resources'].pop(0)
            
            # Log system health
            self.log_system_health(system_metrics)
            
        except Exception as e:
            self.log_error(f"Error collecting system metrics: {e}")
    
    def _collect_performance_metrics(self):
        """Collect performance metrics from existing data"""
        try:
            # Get performance summary
            perf_summary = self.get_performance_summary()
            
            if perf_summary:
                current_time = datetime.now()
                
                # Calculate operations per minute
                total_operations = sum(
                    metrics.get('count', 0) 
                    for metrics in perf_summary.values()
                )
                
                # Calculate average response time
                response_times = [
                    metrics.get('average_duration', 0)
                    for metrics in perf_summary.values()
                ]
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                
                with self.metrics_lock:
                    # Store operations per minute
                    self.real_time_metrics['operations_per_minute'].append({
                        'timestamp': current_time.isoformat(),
                        'operations': total_operations
                    })
                    
                    # Store response times
                    self.real_time_metrics['response_times'].append({
                        'timestamp': current_time.isoformat(),
                        'average_response_time': avg_response_time
                    })
                    
                    # Keep only last 100 entries
                    for metric_list in ['operations_per_minute', 'response_times']:
                        if len(self.real_time_metrics[metric_list]) > 100:
                            self.real_time_metrics[metric_list].pop(0)
            
        except Exception as e:
            self.log_error(f"Error collecting performance metrics: {e}")
    
    def _check_alert_conditions(self):
        """Check for alert conditions and generate alerts"""
        try:
            alerts = []
            
            # Check system resource alerts
            if self.real_time_metrics['system_resources']:
                latest_system = self.real_time_metrics['system_resources'][-1]
                
                cpu_usage = latest_system.get('cpu_usage', 0)
                memory_usage = latest_system.get('memory_usage', 0)
                
                if cpu_usage >= self.alert_thresholds['cpu_usage_critical']:
                    alerts.append({
                        'level': 'critical',
                        'type': 'system_resources',
                        'message': f'Critical CPU usage: {cpu_usage:.1f}%',
                        'value': cpu_usage,
                        'threshold': self.alert_thresholds['cpu_usage_critical']
                    })
                elif cpu_usage >= self.alert_thresholds['cpu_usage_warning']:
                    alerts.append({
                        'level': 'warning',
                        'type': 'system_resources',
                        'message': f'High CPU usage: {cpu_usage:.1f}%',
                        'value': cpu_usage,
                        'threshold': self.alert_thresholds['cpu_usage_warning']
                    })
                
                if memory_usage >= self.alert_thresholds['memory_usage_critical']:
                    alerts.append({
                        'level': 'critical',
                        'type': 'system_resources',
                        'message': f'Critical memory usage: {memory_usage:.1f}%',
                        'value': memory_usage,
                        'threshold': self.alert_thresholds['memory_usage_critical']
                    })
                elif memory_usage >= self.alert_thresholds['memory_usage_warning']:
                    alerts.append({
                        'level': 'warning',
                        'type': 'system_resources',
                        'message': f'High memory usage: {memory_usage:.1f}%',
                        'value': memory_usage,
                        'threshold': self.alert_thresholds['memory_usage_warning']
                    })
            
            # Check response time alerts
            if self.real_time_metrics['response_times']:
                latest_response = self.real_time_metrics['response_times'][-1]
                response_time = latest_response.get('average_response_time', 0)
                
                if response_time >= self.alert_thresholds['response_time_critical']:
                    alerts.append({
                        'level': 'critical',
                        'type': 'performance',
                        'message': f'Critical response time: {response_time:.2f}s',
                        'value': response_time,
                        'threshold': self.alert_thresholds['response_time_critical']
                    })
                elif response_time >= self.alert_thresholds['response_time_warning']:
                    alerts.append({
                        'level': 'warning',
                        'type': 'performance',
                        'message': f'High response time: {response_time:.2f}s',
                        'value': response_time,
                        'threshold': self.alert_thresholds['response_time_warning']
                    })
            
            # Log alerts
            for alert in alerts:
                if alert['level'] == 'critical':
                    self.log_critical(alert['message'], alert_data=alert)
                else:
                    self.log_warning(alert['message'], alert_data=alert)
            
        except Exception as e:
            self.log_error(f"Error checking alert conditions: {e}")
    
    def log_component_health(self, component: str, status: str, **kwargs):
        """
        Log component health status
        
        Args:
            component: Component name
            status: Health status (healthy, warning, critical)
            **kwargs: Additional health data
        """
        health_data = {
            'component': component,
            'health_status': status,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        with self.metrics_lock:
            self.real_time_metrics['component_health'][component] = health_data
        
        if status == 'critical':
            self.log_critical(f"Component {component} is in critical state", **health_data)
        elif status == 'warning':
            self.log_warning(f"Component {component} has warnings", **health_data)
        else:
            self.log_info(f"Component {component} is healthy", **health_data)
    
    def log_monitoring_cycle(self, cycle_type: str, success: bool, duration: float, **kwargs):
        """
        Log monitoring cycle execution
        
        Args:
            cycle_type: Type of monitoring cycle
            success: Whether cycle was successful
            duration: Cycle duration in seconds
            **kwargs: Additional cycle data
        """
        cycle_data = {
            'cycle_type': cycle_type,
            'success': success,
            'duration_seconds': duration,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        # Log performance
        self.log_performance(f"monitoring_cycle_{cycle_type}", duration, **cycle_data)
        
        # Log audit
        self.log_audit(f"monitoring_cycle_executed", 
                      cycle_type=cycle_type, 
                      success=success, 
                      duration=duration)
        
        if success:
            self.log_info(f"Monitoring cycle '{cycle_type}' completed successfully", **cycle_data)
        else:
            self.log_error(f"Monitoring cycle '{cycle_type}' failed", **cycle_data)
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """
        Get current real-time metrics
        
        Returns:
            Dict: Real-time metrics data
        """
        try:
            with self.metrics_lock:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'monitoring_active': self.monitoring_active,
                    'metrics': {
                        'operations_per_minute': self.real_time_metrics['operations_per_minute'][-10:],
                        'response_times': self.real_time_metrics['response_times'][-10:],
                        'system_resources': self.real_time_metrics['system_resources'][-10:],
                        'component_health': self.real_time_metrics['component_health'].copy()
                    },
                    'alert_thresholds': self.alert_thresholds.copy()
                }
        except Exception as e:
            self.log_error(f"Error getting real-time metrics: {e}")
            return {'error': str(e)}
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report
        
        Returns:
            Dict: Health report
        """
        try:
            # Get system health from health checker
            from monitoring_controller import MonitoringController
            
            # Create temporary controller for health check
            controller = MonitoringController()
            health_report = self.health_checker.perform_comprehensive_health_check(controller)
            
            # Add real-time metrics
            real_time_data = self.get_real_time_metrics()
            
            # Combine reports
            comprehensive_report = {
                'timestamp': datetime.now().isoformat(),
                'health_check': health_report,
                'real_time_metrics': real_time_data,
                'performance_summary': self.get_performance_summary(),
                'log_statistics': self._get_log_statistics()
            }
            
            return comprehensive_report
            
        except Exception as e:
            self.log_error(f"Error generating health report: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        try:
            stats = {
                'log_files': {},
                'total_size_mb': 0,
                'oldest_log': None,
                'newest_log': None
            }
            
            # Scan log directories
            for log_dir in [self.log_dir, self.performance_log_dir, self.error_log_dir, self.audit_log_dir]:
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log*"):
                        file_stat = log_file.stat()
                        file_size_mb = file_stat.st_size / (1024 * 1024)
                        file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                        
                        stats['log_files'][str(log_file)] = {
                            'size_mb': round(file_size_mb, 2),
                            'modified': file_mtime.isoformat()
                        }
                        
                        stats['total_size_mb'] += file_size_mb
                        
                        if stats['oldest_log'] is None or file_mtime < datetime.fromisoformat(stats['oldest_log']):
                            stats['oldest_log'] = file_mtime.isoformat()
                        
                        if stats['newest_log'] is None or file_mtime > datetime.fromisoformat(stats['newest_log']):
                            stats['newest_log'] = file_mtime.isoformat()
            
            stats['total_size_mb'] = round(stats['total_size_mb'], 2)
            stats['total_files'] = len(stats['log_files'])
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def update_alert_thresholds(self, thresholds: Dict[str, float]):
        """
        Update alert thresholds
        
        Args:
            thresholds: New threshold values
        """
        try:
            self.alert_thresholds.update(thresholds)
            self.log_audit("alert_thresholds_updated", thresholds=thresholds)
            self.log_info("Alert thresholds updated", new_thresholds=thresholds)
            
        except Exception as e:
            self.log_error(f"Error updating alert thresholds: {e}")
    
    def cleanup(self):
        """Clean up enhanced logger resources"""
        try:
            # Stop real-time monitoring
            self.stop_real_time_monitoring()
            
            # Clean up old logs
            self.cleanup_old_logs()
            
            self.log_info("Enhanced monitoring logger cleanup completed")
            
        except Exception as e:
            self.log_error(f"Error during enhanced logger cleanup: {e}")


# Global enhanced logger instance
_enhanced_monitoring_logger = None


def get_enhanced_monitoring_logger(name: str = "website_monitoring_enhanced", 
                                 log_dir: str = "logs") -> EnhancedMonitoringLogger:
    """
    Get global enhanced monitoring logger instance
    
    Args:
        name: Logger name
        log_dir: Log directory
        
    Returns:
        EnhancedMonitoringLogger: Enhanced logger instance
    """
    global _enhanced_monitoring_logger
    
    if _enhanced_monitoring_logger is None:
        _enhanced_monitoring_logger = EnhancedMonitoringLogger(name, log_dir)
    
    return _enhanced_monitoring_logger


# Example usage and testing
def main():
    """
    Example usage of enhanced monitoring logger
    """
    # Initialize enhanced logger
    logger = get_enhanced_monitoring_logger()
    
    try:
        # Start real-time monitoring
        logger.start_real_time_monitoring(30)  # 30 second intervals
        
        # Test logging with enhanced features
        logger.log_info("Enhanced monitoring system started", 
                       component="main", 
                       version="1.0.0")
        
        # Test component health logging
        logger.log_component_health("website_monitor", "healthy", 
                                   last_check=datetime.now().isoformat(),
                                   cycles_completed=10)
        
        # Test monitoring cycle logging
        with logger.start_operation("test_monitoring_cycle") as timer:
            time.sleep(0.5)  # Simulate work
            timer.add_data(items_processed=50, success_rate=98.5)
        
        logger.log_monitoring_cycle("carousel_scraping", True, 0.5, 
                                   items_found=5, 
                                   new_items=2)
        
        # Wait a bit for real-time monitoring
        time.sleep(35)
        
        # Get real-time metrics
        metrics = logger.get_real_time_metrics()
        print("Real-time Metrics:")
        print(json.dumps(metrics, indent=2, default=str))
        
        # Generate health report
        health_report = logger.generate_health_report()
        print("\nHealth Report:")
        print(json.dumps(health_report, indent=2, default=str))
        
    except Exception as e:
        logger.log_error(f"Error in enhanced logger test: {e}")
    
    finally:
        # Cleanup
        logger.cleanup()


if __name__ == "__main__":
    main()