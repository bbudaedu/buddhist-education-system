#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Monitoring Dashboard and Health Check System
網站監控儀表板和健康檢查系統

This module provides a comprehensive monitoring dashboard with health checks,
performance metrics, and system status reporting for the website monitoring system.
"""

import os
import sys
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import monitoring components
from monitoring_controller import MonitoringController
from config_manager import ConfigManager
from monitoring_logger import get_monitoring_logger, LogAnalyzer


class SystemHealthChecker:
    """
    System health monitoring and reporting
    
    Monitors:
    - System resources (CPU, memory, disk)
    - Application performance
    - Component status
    - Error rates
    - Network connectivity
    """
    
    def __init__(self, logger=None):
        """
        Initialize health checker
        
        Args:
            logger: Logger instance for health check operations
        """
        self.logger = logger or get_monitoring_logger()
        self.health_history = []
        self.max_history_size = 1000
        self.health_lock = threading.Lock()
        
        # Health thresholds
        self.thresholds = {
            'cpu_usage_warning': 80.0,
            'cpu_usage_critical': 95.0,
            'memory_usage_warning': 85.0,
            'memory_usage_critical': 95.0,
            'disk_usage_warning': 85.0,
            'disk_usage_critical': 95.0,
            'error_rate_warning': 5.0,
            'error_rate_critical': 15.0,
            'response_time_warning': 30.0,
            'response_time_critical': 60.0
        }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage
        
        Returns:
            Dict: System resource information
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # Network statistics
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'status': self._get_status_level(cpu_percent, 'cpu_usage')
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory_available_gb, 2),
                    'total_gb': round(memory.total / (1024**3), 2),
                    'status': self._get_status_level(memory_percent, 'memory_usage')
                },
                'disk': {
                    'usage_percent': round(disk_percent, 2),
                    'free_gb': round(disk_free_gb, 2),
                    'total_gb': round(disk.total / (1024**3), 2),
                    'status': self._get_status_level(disk_percent, 'disk_usage')
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            }
            
        except Exception as e:
            self.logger.log_error(f"Error checking system resources: {e}")
            return {'error': str(e)}
    
    def check_application_health(self, controller: MonitoringController) -> Dict[str, Any]:
        """
        Check application-specific health metrics
        
        Args:
            controller: MonitoringController instance
            
        Returns:
            Dict: Application health information
        """
        try:
            # Get system status
            system_status = controller.get_system_status()
            
            # Get performance report
            performance_report = controller.get_performance_report()
            
            # Analyze recent logs
            log_analyzer = LogAnalyzer()
            error_summary = log_analyzer.get_error_summary(1)  # Last hour
            perf_analysis = log_analyzer.analyze_performance_logs(1)  # Last hour
            
            # Calculate health metrics
            error_rate = error_summary.get('total_errors', 0)
            total_operations = perf_analysis.get('total_operations', 1)
            error_rate_percent = (error_rate / max(total_operations, 1)) * 100
            
            # Get average response time
            perf_summary = perf_analysis.get('performance_summary', {})
            avg_response_times = []
            for operation, metrics in perf_summary.items():
                avg_response_times.append(metrics.get('average_duration', 0))
            
            avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
            
            return {
                'system_initialized': system_status.get('system_initialized', False),
                'monitoring_active': system_status.get('monitoring_status', {}).get('monitoring_active', False),
                'components_status': system_status.get('component_status', {}),
                'performance': {
                    'success_rate': performance_report.get('success_rate', 0),
                    'average_cycle_time': performance_report.get('average_cycle_time', 0),
                    'uptime_hours': performance_report.get('uptime_hours', 0),
                    'total_cycles': system_status.get('performance_metrics', {}).get('total_cycles', 0)
                },
                'errors': {
                    'error_rate_percent': error_rate_percent,
                    'total_errors_last_hour': error_rate,
                    'status': self._get_status_level(error_rate_percent, 'error_rate')
                },
                'response_time': {
                    'average_seconds': avg_response_time,
                    'status': self._get_status_level(avg_response_time, 'response_time')
                }
            }
            
        except Exception as e:
            self.logger.log_error(f"Error checking application health: {e}")
            return {'error': str(e)}
    
    def check_component_connectivity(self) -> Dict[str, Any]:
        """
        Check connectivity to external components
        
        Returns:
            Dict: Connectivity status
        """
        try:
            connectivity = {}
            
            # Check website connectivity
            import requests
            
            websites_to_check = [
                'https://www.budaedu.org',
                'https://www.budaedu.org/#/',
                'https://www.budaedu.org/#/bulletins/'
            ]
            
            for url in websites_to_check:
                try:
                    response = requests.get(url, timeout=10)
                    connectivity[url] = {
                        'status': 'healthy' if response.status_code == 200 else 'warning',
                        'status_code': response.status_code,
                        'response_time': response.elapsed.total_seconds()
                    }
                except Exception as e:
                    connectivity[url] = {
                        'status': 'critical',
                        'error': str(e)
                    }
            
            # Check ChromeDriver availability
            chromedriver_path = "chromedriver-win64/chromedriver.exe"
            connectivity['chromedriver'] = {
                'status': 'healthy' if os.path.exists(chromedriver_path) else 'critical',
                'path': chromedriver_path,
                'exists': os.path.exists(chromedriver_path)
            }
            
            return connectivity
            
        except Exception as e:
            self.logger.log_error(f"Error checking component connectivity: {e}")
            return {'error': str(e)}
    
    def perform_comprehensive_health_check(self, controller: MonitoringController) -> Dict[str, Any]:
        """
        Perform comprehensive system health check
        
        Args:
            controller: MonitoringController instance
            
        Returns:
            Dict: Comprehensive health report
        """
        try:
            health_check_start = time.time()
            
            # Perform all health checks
            system_resources = self.check_system_resources()
            application_health = self.check_application_health(controller)
            connectivity = self.check_component_connectivity()
            
            # Calculate overall health status
            overall_status = self._calculate_overall_status(
                system_resources, application_health, connectivity
            )
            
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'check_duration': time.time() - health_check_start,
                'overall_status': overall_status,
                'system_resources': system_resources,
                'application_health': application_health,
                'connectivity': connectivity,
                'recommendations': self._generate_recommendations(
                    system_resources, application_health, connectivity
                )
            }
            
            # Store in history
            with self.health_lock:
                self.health_history.append(health_report)
                if len(self.health_history) > self.max_history_size:
                    self.health_history.pop(0)
            
            # Log health check
            self.logger.log_system_health({
                'overall_status': overall_status,
                'check_duration': health_report['check_duration'],
                'system_cpu': system_resources.get('cpu', {}).get('usage_percent', 0),
                'system_memory': system_resources.get('memory', {}).get('usage_percent', 0),
                'error_rate': application_health.get('errors', {}).get('error_rate_percent', 0)
            })
            
            return health_report
            
        except Exception as e:
            error_msg = f"Error performing health check: {e}"
            self.logger.log_error(error_msg)
            return {
                'timestamp': datetime.now().isoformat(),
                'error': error_msg,
                'overall_status': 'critical'
            }
    
    def _get_status_level(self, value: float, metric_type: str) -> str:
        """
        Get status level based on thresholds
        
        Args:
            value: Metric value
            metric_type: Type of metric
            
        Returns:
            str: Status level (healthy, warning, critical)
        """
        warning_threshold = self.thresholds.get(f"{metric_type}_warning", 80)
        critical_threshold = self.thresholds.get(f"{metric_type}_critical", 95)
        
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'healthy'
    
    def _calculate_overall_status(self, system_resources: Dict, 
                                 application_health: Dict, 
                                 connectivity: Dict) -> str:
        """
        Calculate overall system status
        
        Args:
            system_resources: System resource metrics
            application_health: Application health metrics
            connectivity: Connectivity status
            
        Returns:
            str: Overall status (healthy, warning, critical)
        """
        try:
            status_scores = []
            
            # System resources
            if 'error' not in system_resources:
                for component in ['cpu', 'memory', 'disk']:
                    if component in system_resources:
                        status = system_resources[component].get('status', 'healthy')
                        status_scores.append(self._status_to_score(status))
            
            # Application health
            if 'error' not in application_health:
                error_status = application_health.get('errors', {}).get('status', 'healthy')
                response_status = application_health.get('response_time', {}).get('status', 'healthy')
                status_scores.extend([
                    self._status_to_score(error_status),
                    self._status_to_score(response_status)
                ])
            
            # Connectivity
            if 'error' not in connectivity:
                for component, status_info in connectivity.items():
                    if isinstance(status_info, dict):
                        status = status_info.get('status', 'healthy')
                        status_scores.append(self._status_to_score(status))
            
            # Calculate overall score
            if not status_scores:
                return 'critical'
            
            avg_score = sum(status_scores) / len(status_scores)
            
            if avg_score >= 2.5:
                return 'critical'
            elif avg_score >= 1.5:
                return 'warning'
            else:
                return 'healthy'
                
        except Exception:
            return 'critical'
    
    def _status_to_score(self, status: str) -> int:
        """Convert status to numeric score"""
        return {'healthy': 0, 'warning': 2, 'critical': 3}.get(status, 3)
    
    def _generate_recommendations(self, system_resources: Dict, 
                                 application_health: Dict, 
                                 connectivity: Dict) -> List[str]:
        """
        Generate recommendations based on health check results
        
        Args:
            system_resources: System resource metrics
            application_health: Application health metrics
            connectivity: Connectivity status
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        try:
            # System resource recommendations
            if 'error' not in system_resources:
                cpu_usage = system_resources.get('cpu', {}).get('usage_percent', 0)
                memory_usage = system_resources.get('memory', {}).get('usage_percent', 0)
                disk_usage = system_resources.get('disk', {}).get('usage_percent', 0)
                
                if cpu_usage > self.thresholds['cpu_usage_warning']:
                    recommendations.append(f"High CPU usage ({cpu_usage:.1f}%) - Consider reducing monitoring frequency or optimizing scrapers")
                
                if memory_usage > self.thresholds['memory_usage_warning']:
                    recommendations.append(f"High memory usage ({memory_usage:.1f}%) - Check for memory leaks or reduce concurrent operations")
                
                if disk_usage > self.thresholds['disk_usage_warning']:
                    recommendations.append(f"High disk usage ({disk_usage:.1f}%) - Clean up old log files or increase disk space")
            
            # Application health recommendations
            if 'error' not in application_health:
                error_rate = application_health.get('errors', {}).get('error_rate_percent', 0)
                success_rate = application_health.get('performance', {}).get('success_rate', 100)
                
                if error_rate > self.thresholds['error_rate_warning']:
                    recommendations.append(f"High error rate ({error_rate:.1f}%) - Check error logs and fix recurring issues")
                
                if success_rate < 90:
                    recommendations.append(f"Low success rate ({success_rate:.1f}%) - Investigate monitoring failures")
            
            # Connectivity recommendations
            if 'error' not in connectivity:
                for component, status_info in connectivity.items():
                    if isinstance(status_info, dict) and status_info.get('status') == 'critical':
                        if 'chromedriver' in component:
                            recommendations.append("ChromeDriver not found - Install or update ChromeDriver")
                        else:
                            recommendations.append(f"Cannot connect to {component} - Check network connectivity")
            
            if not recommendations:
                recommendations.append("System is operating normally - no immediate actions required")
            
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get health check history for specified time period
        
        Args:
            hours: Number of hours of history to return
            
        Returns:
            List[Dict]: Health check history
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.health_lock:
                filtered_history = []
                for health_check in self.health_history:
                    check_time = datetime.fromisoformat(health_check['timestamp'])
                    if check_time >= cutoff_time:
                        filtered_history.append(health_check)
                
                return filtered_history
                
        except Exception as e:
            self.logger.log_error(f"Error getting health history: {e}")
            return []


class MonitoringDashboard:
    """
    Comprehensive monitoring dashboard
    
    Provides:
    - Real-time system status
    - Performance metrics visualization
    - Health check reporting
    - Alert management
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize monitoring dashboard
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = get_monitoring_logger()
        
        # Initialize components
        self.controller = MonitoringController(config_path, self.logger.main_logger)
        self.config_manager = ConfigManager(config_path, self.logger.main_logger)
        self.health_checker = SystemHealthChecker(self.logger)
        self.log_analyzer = LogAnalyzer()
        
        # Dashboard state
        self.last_update = None
        self.dashboard_data = {}
        
        self.logger.log_info("Monitoring Dashboard initialized")
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data
        
        Returns:
            Dict: Dashboard data
        """
        try:
            dashboard_start = time.time()
            
            # Get system status
            system_status = self.controller.get_system_status(force_refresh=True)
            
            # Perform health check
            health_report = self.health_checker.perform_comprehensive_health_check(self.controller)
            
            # Get performance analysis
            performance_analysis = self.log_analyzer.analyze_performance_logs(24)
            error_summary = self.log_analyzer.get_error_summary(24)
            
            # Get configuration summary
            config_summary = self.config_manager.get_monitoring_config_summary()
            
            # Compile dashboard data
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'generation_time': time.time() - dashboard_start,
                'system_status': system_status,
                'health_report': health_report,
                'performance_analysis': performance_analysis,
                'error_summary': error_summary,
                'configuration': config_summary,
                'alerts': self._generate_alerts(health_report, performance_analysis, error_summary)
            }
            
            # Cache dashboard data
            self.dashboard_data = dashboard_data
            self.last_update = datetime.now()
            
            self.logger.log_performance("dashboard_generation", dashboard_data['generation_time'])
            
            return dashboard_data
            
        except Exception as e:
            error_msg = f"Error generating dashboard data: {e}"
            self.logger.log_error(error_msg)
            return {
                'timestamp': datetime.now().isoformat(),
                'error': error_msg
            }
    
    def _generate_alerts(self, health_report: Dict, 
                        performance_analysis: Dict, 
                        error_summary: Dict) -> List[Dict[str, Any]]:
        """
        Generate alerts based on system status
        
        Args:
            health_report: Health check report
            performance_analysis: Performance analysis data
            error_summary: Error summary data
            
        Returns:
            List[Dict]: List of alerts
        """
        alerts = []
        
        try:
            # Health-based alerts
            overall_status = health_report.get('overall_status', 'unknown')
            if overall_status == 'critical':
                alerts.append({
                    'level': 'critical',
                    'type': 'system_health',
                    'message': 'System health is critical - immediate attention required',
                    'timestamp': datetime.now().isoformat()
                })
            elif overall_status == 'warning':
                alerts.append({
                    'level': 'warning',
                    'type': 'system_health',
                    'message': 'System health warning - monitoring recommended',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Performance-based alerts
            error_rate = performance_analysis.get('error_rate', 0)
            if error_rate > 15:
                alerts.append({
                    'level': 'critical',
                    'type': 'performance',
                    'message': f'High error rate: {error_rate:.1f}%',
                    'timestamp': datetime.now().isoformat()
                })
            elif error_rate > 5:
                alerts.append({
                    'level': 'warning',
                    'type': 'performance',
                    'message': f'Elevated error rate: {error_rate:.1f}%',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Error-based alerts
            total_errors = error_summary.get('total_errors', 0)
            if total_errors > 50:
                alerts.append({
                    'level': 'warning',
                    'type': 'errors',
                    'message': f'High number of errors in last 24h: {total_errors}',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Resource-based alerts
            system_resources = health_report.get('system_resources', {})
            if 'error' not in system_resources:
                cpu_usage = system_resources.get('cpu', {}).get('usage_percent', 0)
                memory_usage = system_resources.get('memory', {}).get('usage_percent', 0)
                
                if cpu_usage > 90:
                    alerts.append({
                        'level': 'critical',
                        'type': 'resources',
                        'message': f'Critical CPU usage: {cpu_usage:.1f}%',
                        'timestamp': datetime.now().isoformat()
                    })
                
                if memory_usage > 90:
                    alerts.append({
                        'level': 'critical',
                        'type': 'resources',
                        'message': f'Critical memory usage: {memory_usage:.1f}%',
                        'timestamp': datetime.now().isoformat()
                    })
            
        except Exception as e:
            alerts.append({
                'level': 'warning',
                'type': 'system',
                'message': f'Error generating alerts: {e}',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get dashboard summary for quick status check
        
        Returns:
            Dict: Dashboard summary
        """
        try:
            if not self.dashboard_data or not self.last_update:
                # Generate fresh data if none exists
                self.generate_dashboard_data()
            
            # Check if data is stale (older than 5 minutes)
            if self.last_update and (datetime.now() - self.last_update).seconds > 300:
                self.generate_dashboard_data()
            
            health_report = self.dashboard_data.get('health_report', {})
            system_status = self.dashboard_data.get('system_status', {})
            alerts = self.dashboard_data.get('alerts', [])
            
            return {
                'timestamp': self.dashboard_data.get('timestamp'),
                'overall_status': health_report.get('overall_status', 'unknown'),
                'monitoring_active': system_status.get('monitoring_status', {}).get('monitoring_active', False),
                'system_initialized': system_status.get('system_initialized', False),
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a.get('level') == 'critical']),
                'uptime_hours': system_status.get('uptime_hours', 0),
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting dashboard summary: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'overall_status': 'unknown'
            }
    
    def export_dashboard_report(self, output_file: str = None) -> str:
        """
        Export dashboard data to JSON file
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"monitoring_dashboard_report_{timestamp}.json"
            
            # Generate fresh dashboard data
            dashboard_data = self.generate_dashboard_data()
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.log_audit("dashboard_report_exported", output_file=output_file)
            
            return output_file
            
        except Exception as e:
            error_msg = f"Error exporting dashboard report: {e}"
            self.logger.log_error(error_msg)
            return ""


def main():
    """
    Main dashboard script entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Website Monitoring Dashboard')
    parser.add_argument(
        'action',
        choices=['status', 'health', 'dashboard', 'export'],
        help='Dashboard action to perform'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for export action'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize dashboard
        dashboard = MonitoringDashboard(args.config)
        
        if args.action == 'status':
            summary = dashboard.get_dashboard_summary()
            print("System Status Summary:")
            print("=" * 30)
            print(f"Overall Status: {summary.get('overall_status', 'unknown').upper()}")
            print(f"Monitoring Active: {'✓' if summary.get('monitoring_active', False) else '✗'}")
            print(f"System Initialized: {'✓' if summary.get('system_initialized', False) else '✗'}")
            print(f"Total Alerts: {summary.get('total_alerts', 0)}")
            print(f"Critical Alerts: {summary.get('critical_alerts', 0)}")
            print(f"Uptime: {summary.get('uptime_hours', 0):.1f} hours")
            
        elif args.action == 'health':
            health_checker = SystemHealthChecker()
            controller = MonitoringController(args.config)
            health_report = health_checker.perform_comprehensive_health_check(controller)
            
            print("Health Check Report:")
            print("=" * 30)
            print(f"Overall Status: {health_report.get('overall_status', 'unknown').upper()}")
            print(f"Check Duration: {health_report.get('check_duration', 0):.2f} seconds")
            
            recommendations = health_report.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")
            
        elif args.action == 'dashboard':
            dashboard_data = dashboard.generate_dashboard_data()
            print("Dashboard Data Generated:")
            print("=" * 30)
            print(f"Generation Time: {dashboard_data.get('generation_time', 0):.2f} seconds")
            print(f"Timestamp: {dashboard_data.get('timestamp')}")
            
            if 'error' in dashboard_data:
                print(f"Error: {dashboard_data['error']}")
            else:
                print("✓ Dashboard data generated successfully")
            
        elif args.action == 'export':
            output_file = dashboard.export_dashboard_report(args.output)
            if output_file:
                print(f"✓ Dashboard report exported to: {output_file}")
            else:
                print("✗ Failed to export dashboard report")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"✗ Dashboard error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())