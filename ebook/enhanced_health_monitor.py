#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Health Monitoring System
增強型健康監控系統

This module provides comprehensive health monitoring with automated checks,
trend analysis, and predictive alerting for the website monitoring system.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import psutil

# Import existing monitoring infrastructure
from monitoring_dashboard import SystemHealthChecker, MonitoringDashboard
from monitoring_logger import get_monitoring_logger
from monitoring_controller import MonitoringController


class EnhancedHealthMonitor:
    """
    Enhanced health monitoring with predictive capabilities
    
    Provides:
    - Continuous health monitoring
    - Trend analysis and prediction
    - Automated health checks
    - Component-level health tracking
    - Integration with existing infrastructure
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize enhanced health monitor
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.logger = get_monitoring_logger()
        
        # Initialize components
        self.health_checker = SystemHealthChecker(self.logger)
        self.dashboard = MonitoringDashboard(config_path)
        self.controller = MonitoringController(config_path, self.logger.main_logger)
        
        # Health monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.health_history = []
        self.max_history_size = 1000
        self.health_lock = threading.Lock()
        
        # Component health tracking
        self.component_health = {
            'website_monitor': {'status': 'unknown', 'last_check': None},
            'carousel_scraper': {'status': 'unknown', 'last_check': None},
            'bulletin_scraper': {'status': 'unknown', 'last_check': None},
            'news_processor': {'status': 'unknown', 'last_check': None},
            'media_processor': {'status': 'unknown', 'last_check': None},
            'data_synchronizer': {'status': 'unknown', 'last_check': None},
            'notification_sender': {'status': 'unknown', 'last_check': None}
        }
        
        # Health check configuration
        self.check_interval_seconds = 300  # 5 minutes
        self.alert_cooldown_seconds = 1800  # 30 minutes
        self.last_alert_time = {}
        
        self.logger.log_info("Enhanced Health Monitor initialized")
    
    def start_continuous_monitoring(self, interval_seconds: int = None):
        """
        Start continuous health monitoring
        
        Args:
            interval_seconds: Check interval in seconds (uses default if None)
        """
        try:
            if self.monitoring_active:
                self.logger.log_warning("Health monitoring already active")
                return
            
            if interval_seconds:
                self.check_interval_seconds = interval_seconds
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.log_info("Continuous health monitoring started",
                               interval_seconds=self.check_interval_seconds)
            self.logger.log_audit("health_monitoring_started",
                                interval=self.check_interval_seconds)
            
        except Exception as e:
            self.logger.log_error(f"Error starting continuous health monitoring: {e}")
    
    def stop_continuous_monitoring(self):
        """Stop continuous health monitoring"""
        try:
            if not self.monitoring_active:
                return
            
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=10)
            
            self.logger.log_info("Continuous health monitoring stopped")
            self.logger.log_audit("health_monitoring_stopped")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping continuous health monitoring: {e}")
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform comprehensive health check
                health_report = self.perform_health_check()
                
                # Analyze trends
                trends = self.analyze_health_trends()
                
                # Check for alerts
                self._check_and_send_alerts(health_report, trends)
                
                # Sleep for interval
                time.sleep(self.check_interval_seconds)
                
            except Exception as e:
                self.logger.log_error(f"Error in health monitoring loop: {e}")
                time.sleep(self.check_interval_seconds)
    
    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Dict: Health check results
        """
        try:
            check_start = time.time()
            
            # Perform system health check
            health_report = self.health_checker.perform_comprehensive_health_check(self.controller)
            
            # Add component-specific checks
            component_checks = self._check_component_health()
            health_report['component_health'] = component_checks
            
            # Add performance metrics
            performance_metrics = self._collect_performance_metrics()
            health_report['performance_metrics'] = performance_metrics
            
            # Calculate health score
            health_score = self._calculate_health_score(health_report)
            health_report['health_score'] = health_score
            
            # Add check duration
            health_report['check_duration'] = time.time() - check_start
            
            # Store in history
            with self.health_lock:
                self.health_history.append(health_report)
                if len(self.health_history) > self.max_history_size:
                    self.health_history.pop(0)
            
            # Log health check
            self.logger.log_system_health({
                'overall_status': health_report.get('overall_status', 'unknown'),
                'health_score': health_score,
                'check_duration': health_report['check_duration']
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
    
    def _check_component_health(self) -> Dict[str, Any]:
        """Check health of individual components"""
        component_health = {}
        
        try:
            # Get system status
            system_status = self.controller.get_system_status()
            
            # Check website monitor
            monitoring_status = system_status.get('monitoring_status', {})
            component_health['website_monitor'] = {
                'status': 'healthy' if monitoring_status.get('monitoring_active', False) else 'warning',
                'last_check': datetime.now().isoformat(),
                'details': monitoring_status
            }
            
            # Check component status from system
            component_status = system_status.get('component_status', {})
            
            for component, is_healthy in component_status.items():
                component_health[component] = {
                    'status': 'healthy' if is_healthy else 'critical',
                    'last_check': datetime.now().isoformat()
                }
            
            # Update internal component health tracking
            with self.health_lock:
                self.component_health.update(component_health)
            
        except Exception as e:
            self.logger.log_error(f"Error checking component health: {e}")
        
        return component_health
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics"""
        try:
            # Get performance report from controller
            performance_report = self.controller.get_performance_report()
            
            # Get performance summary from logger
            perf_summary = self.logger.get_performance_summary()
            
            return {
                'controller_metrics': performance_report,
                'logger_metrics': perf_summary,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(f"Error collecting performance metrics: {e}")
            return {'error': str(e)}
    
    def _calculate_health_score(self, health_report: Dict[str, Any]) -> float:
        """
        Calculate overall health score (0-100)
        
        Args:
            health_report: Health check report
            
        Returns:
            float: Health score
        """
        try:
            score = 100.0
            
            # Deduct points based on overall status
            overall_status = health_report.get('overall_status', 'unknown')
            if overall_status == 'critical':
                score -= 50
            elif overall_status == 'warning':
                score -= 25
            elif overall_status == 'unknown':
                score -= 40
            
            # Deduct points for system resource issues
            system_resources = health_report.get('system_resources', {})
            if 'error' not in system_resources:
                for component in ['cpu', 'memory', 'disk']:
                    if component in system_resources:
                        status = system_resources[component].get('status', 'healthy')
                        if status == 'critical':
                            score -= 10
                        elif status == 'warning':
                            score -= 5
            
            # Deduct points for application health issues
            app_health = health_report.get('application_health', {})
            if 'error' not in app_health:
                error_status = app_health.get('errors', {}).get('status', 'healthy')
                if error_status == 'critical':
                    score -= 15
                elif error_status == 'warning':
                    score -= 7
                
                response_status = app_health.get('response_time', {}).get('status', 'healthy')
                if response_status == 'critical':
                    score -= 10
                elif response_status == 'warning':
                    score -= 5
            
            # Deduct points for connectivity issues
            connectivity = health_report.get('connectivity', {})
            if 'error' not in connectivity:
                critical_components = sum(
                    1 for status_info in connectivity.values()
                    if isinstance(status_info, dict) and status_info.get('status') == 'critical'
                )
                score -= critical_components * 5
            
            # Ensure score is within bounds
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating health score: {e}")
            return 50.0  # Default to middle score on error
    
    def analyze_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze health trends over time
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dict: Trend analysis results
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with self.health_lock:
                # Filter history by time
                recent_history = [
                    check for check in self.health_history
                    if datetime.fromisoformat(check['timestamp']) >= cutoff_time
                ]
            
            if not recent_history:
                return {'status': 'no_data', 'message': 'Insufficient health check history'}
            
            # Analyze trends
            trends = {
                'time_period_hours': hours,
                'total_checks': len(recent_history),
                'status_distribution': {'healthy': 0, 'warning': 0, 'critical': 0, 'unknown': 0},
                'health_score_trend': [],
                'average_health_score': 0,
                'degradation_detected': False,
                'improvement_detected': False,
                'recommendations': []
            }
            
            # Collect data
            health_scores = []
            for check in recent_history:
                status = check.get('overall_status', 'unknown')
                trends['status_distribution'][status] = trends['status_distribution'].get(status, 0) + 1
                
                health_score = check.get('health_score', 50.0)
                health_scores.append(health_score)
                trends['health_score_trend'].append({
                    'timestamp': check['timestamp'],
                    'score': health_score
                })
            
            # Calculate average health score
            if health_scores:
                trends['average_health_score'] = sum(health_scores) / len(health_scores)
            
            # Detect trends
            if len(health_scores) >= 5:
                # Compare first half vs second half
                mid_point = len(health_scores) // 2
                first_half_avg = sum(health_scores[:mid_point]) / mid_point
                second_half_avg = sum(health_scores[mid_point:]) / (len(health_scores) - mid_point)
                
                if second_half_avg < first_half_avg - 10:
                    trends['degradation_detected'] = True
                    trends['recommendations'].append(
                        "Health degradation detected - investigate recent changes and errors"
                    )
                elif second_half_avg > first_half_avg + 10:
                    trends['improvement_detected'] = True
                    trends['recommendations'].append(
                        "Health improvement detected - recent optimizations are effective"
                    )
            
            # Add recommendations based on status distribution
            critical_percentage = (trends['status_distribution']['critical'] / trends['total_checks']) * 100
            if critical_percentage > 20:
                trends['recommendations'].append(
                    f"High critical status rate ({critical_percentage:.1f}%) - immediate attention required"
                )
            
            warning_percentage = (trends['status_distribution']['warning'] / trends['total_checks']) * 100
            if warning_percentage > 40:
                trends['recommendations'].append(
                    f"High warning status rate ({warning_percentage:.1f}%) - proactive maintenance recommended"
                )
            
            return trends
            
        except Exception as e:
            self.logger.log_error(f"Error analyzing health trends: {e}")
            return {'error': str(e)}
    
    def _check_and_send_alerts(self, health_report: Dict[str, Any], trends: Dict[str, Any]):
        """Check for alert conditions and send alerts"""
        try:
            current_time = datetime.now()
            
            # Check overall status
            overall_status = health_report.get('overall_status', 'unknown')
            health_score = health_report.get('health_score', 50.0)
            
            # Critical status alert
            if overall_status == 'critical':
                alert_key = 'critical_status'
                if self._should_send_alert(alert_key):
                    self.logger.log_critical(
                        f"ALERT: System health is CRITICAL (score: {health_score:.1f})",
                        alert_type='critical_health',
                        health_score=health_score,
                        recommendations=health_report.get('recommendations', [])
                    )
                    self.last_alert_time[alert_key] = current_time
            
            # Health degradation alert
            if trends.get('degradation_detected', False):
                alert_key = 'health_degradation'
                if self._should_send_alert(alert_key):
                    self.logger.log_warning(
                        "ALERT: Health degradation detected",
                        alert_type='health_degradation',
                        average_score=trends.get('average_health_score', 0),
                        recommendations=trends.get('recommendations', [])
                    )
                    self.last_alert_time[alert_key] = current_time
            
            # Low health score alert
            if health_score < 60:
                alert_key = 'low_health_score'
                if self._should_send_alert(alert_key):
                    self.logger.log_warning(
                        f"ALERT: Low health score ({health_score:.1f})",
                        alert_type='low_health_score',
                        health_score=health_score,
                        overall_status=overall_status
                    )
                    self.last_alert_time[alert_key] = current_time
            
        except Exception as e:
            self.logger.log_error(f"Error checking and sending alerts: {e}")
    
    def _should_send_alert(self, alert_key: str) -> bool:
        """Check if alert should be sent based on cooldown"""
        if alert_key not in self.last_alert_time:
            return True
        
        time_since_last = (datetime.now() - self.last_alert_time[alert_key]).total_seconds()
        return time_since_last >= self.alert_cooldown_seconds
    
    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get health summary for quick status check
        
        Returns:
            Dict: Health summary
        """
        try:
            # Get latest health check
            with self.health_lock:
                if not self.health_history:
                    return {
                        'status': 'no_data',
                        'message': 'No health check data available'
                    }
                
                latest_check = self.health_history[-1]
            
            # Get recent trends
            trends = self.analyze_health_trends(1)  # Last hour
            
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': latest_check.get('overall_status', 'unknown'),
                'health_score': latest_check.get('health_score', 0),
                'monitoring_active': self.monitoring_active,
                'total_checks': len(self.health_history),
                'recent_trend': {
                    'average_score': trends.get('average_health_score', 0),
                    'degradation_detected': trends.get('degradation_detected', False),
                    'improvement_detected': trends.get('improvement_detected', False)
                },
                'component_health': self.component_health.copy(),
                'last_check_time': latest_check.get('timestamp')
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting health summary: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def export_health_report(self, output_file: str = None) -> str:
        """
        Export comprehensive health report
        
        Args:
            output_file: Output file path (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"health_report_{timestamp}.json"
            
            # Generate comprehensive report
            report = {
                'generation_time': datetime.now().isoformat(),
                'health_summary': self.get_health_summary(),
                'latest_health_check': self.health_history[-1] if self.health_history else None,
                'health_trends_24h': self.analyze_health_trends(24),
                'health_trends_7d': self.analyze_health_trends(168),
                'component_health': self.component_health.copy(),
                'monitoring_configuration': {
                    'check_interval_seconds': self.check_interval_seconds,
                    'alert_cooldown_seconds': self.alert_cooldown_seconds,
                    'monitoring_active': self.monitoring_active
                }
            }
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.log_audit("health_report_exported", output_file=output_file)
            
            return output_file
            
        except Exception as e:
            error_msg = f"Error exporting health report: {e}"
            self.logger.log_error(error_msg)
            return ""
    
    def cleanup(self):
        """Clean up health monitor resources"""
        try:
            # Stop monitoring
            self.stop_continuous_monitoring()
            
            # Clean up controller
            if self.controller:
                self.controller.cleanup_system()
            
            self.logger.log_info("Enhanced health monitor cleanup completed")
            
        except Exception as e:
            self.logger.log_error(f"Error during health monitor cleanup: {e}")


# Example usage and testing
def main():
    """
    Example usage of enhanced health monitor
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Health Monitor')
    parser.add_argument(
        'action',
        choices=['start', 'check', 'summary', 'trends', 'export'],
        help='Health monitor action to perform'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=300,
        help='Monitoring interval in seconds (default: 300)'
    )
    parser.add_argument(
        '--hours', '-H',
        type=int,
        default=24,
        help='Hours for trend analysis (default: 24)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for export action'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize health monitor
        monitor = EnhancedHealthMonitor(args.config)
        
        if args.action == 'start':
            print(f"Starting continuous health monitoring (interval: {args.interval}s)...")
            monitor.start_continuous_monitoring(args.interval)
            print("✓ Health monitoring started")
            print("Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping health monitoring...")
                monitor.stop_continuous_monitoring()
                print("✓ Health monitoring stopped")
        
        elif args.action == 'check':
            print("Performing health check...")
            health_report = monitor.perform_health_check()
            
            print("\nHealth Check Results:")
            print("=" * 50)
            print(f"Overall Status: {health_report.get('overall_status', 'unknown').upper()}")
            print(f"Health Score: {health_report.get('health_score', 0):.1f}/100")
            print(f"Check Duration: {health_report.get('check_duration', 0):.2f}s")
            
            recommendations = health_report.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")
        
        elif args.action == 'summary':
            summary = monitor.get_health_summary()
            print("Health Summary:")
            print("=" * 50)
            print(json.dumps(summary, indent=2, default=str))
        
        elif args.action == 'trends':
            trends = monitor.analyze_health_trends(args.hours)
            print(f"Health Trends (last {args.hours} hours):")
            print("=" * 50)
            print(json.dumps(trends, indent=2, default=str))
        
        elif args.action == 'export':
            output_file = monitor.export_health_report(args.output)
            if output_file:
                print(f"✓ Health report exported to: {output_file}")
            else:
                print("✗ Failed to export health report")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"✗ Health monitor error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
