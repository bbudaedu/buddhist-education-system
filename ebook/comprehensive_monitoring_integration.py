#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Monitoring Integration
綜合監控整合

This module integrates all monitoring components into a unified system with
comprehensive logging, performance metrics, health checks, and status reporting.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import existing monitoring infrastructure
from monitoring_logger import get_monitoring_logger
from monitoring_controller import MonitoringController
from monitoring_dashboard import MonitoringDashboard, SystemHealthChecker
from system_status_reporter import StatusReportGenerator, AutomatedReporter
from website_monitor import WebsiteMonitor

# Import enhanced monitoring components
from enhanced_monitoring_logger import get_enhanced_monitoring_logger, EnhancedMonitoringLogger
from enhanced_health_monitor import EnhancedHealthMonitor


class ComprehensiveMonitoringSystem:
    """
    Comprehensive monitoring system integrating all monitoring capabilities
    
    Provides:
    - Unified logging infrastructure
    - Real-time performance monitoring
    - Automated health checks
    - Status reporting and dashboards
    - Alert management
    - Integration with existing components
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize comprehensive monitoring system
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        
        # Initialize enhanced logger
        self.logger = get_enhanced_monitoring_logger()
        
        # Initialize monitoring components
        self.controller = MonitoringController(config_path, self.logger.main_logger)
        self.dashboard = MonitoringDashboard(config_path)
        self.health_monitor = EnhancedHealthMonitor(config_path)
        self.status_reporter = StatusReportGenerator(config_path)
        self.automated_reporter = AutomatedReporter(config_path)
        
        # System state
        self.system_initialized = False
        self.monitoring_active = False
        self.start_time = None
        
        # Monitoring threads
        self.monitoring_threads = []
        
        self.logger.log_info("Comprehensive Monitoring System initialized",
                           component="comprehensive_monitoring",
                           version="1.0.0")
        self.logger.log_audit("system_initialized", config_path=config_path)
    
    def initialize_system(self) -> Tuple[bool, str]:
        """
        Initialize the comprehensive monitoring system
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if self.system_initialized:
                return True, "System already initialized"
            
            self.logger.log_info("Initializing comprehensive monitoring system...")
            
            # Initialize controller
            success, message = self.controller.initialize_system()
            if not success:
                return False, f"Controller initialization failed: {message}"
            
            # Start enhanced logging features
            self.logger.start_real_time_monitoring(60)  # 1 minute intervals
            
            # Start health monitoring
            self.health_monitor.start_continuous_monitoring(300)  # 5 minute intervals
            
            self.system_initialized = True
            self.start_time = datetime.now()
            
            self.logger.log_info("Comprehensive monitoring system initialized successfully")
            self.logger.log_audit("system_initialization_completed")
            
            return True, "System initialized successfully"
            
        except Exception as e:
            error_msg = f"Error initializing comprehensive monitoring system: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg
    
    def start_monitoring(self, interval_minutes: int = 60) -> Tuple[bool, str]:
        """
        Start comprehensive monitoring
        
        Args:
            interval_minutes: Monitoring interval in minutes
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.system_initialized:
                init_success, init_msg = self.initialize_system()
                if not init_success:
                    return False, f"Initialization failed: {init_msg}"
            
            if self.monitoring_active:
                return True, "Monitoring already active"
            
            # Start website monitoring
            success, message = self.controller.start_monitoring(interval_minutes)
            if not success:
                return False, f"Failed to start monitoring: {message}"
            
            self.monitoring_active = True
            
            self.logger.log_info(f"Comprehensive monitoring started with {interval_minutes} minute interval")
            self.logger.log_audit("monitoring_started", interval_minutes=interval_minutes)
            
            return True, f"Monitoring started successfully with {interval_minutes} minute interval"
            
        except Exception as e:
            error_msg = f"Error starting comprehensive monitoring: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg
    
    def stop_monitoring(self) -> Tuple[bool, str]:
        """
        Stop comprehensive monitoring
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.monitoring_active:
                return True, "Monitoring not active"
            
            # Stop website monitoring
            success, message = self.controller.stop_monitoring()
            if not success:
                self.logger.log_warning(f"Controller stop warning: {message}")
            
            self.monitoring_active = False
            
            self.logger.log_info("Comprehensive monitoring stopped")
            self.logger.log_audit("monitoring_stopped")
            
            return True, "Monitoring stopped successfully"
            
        except Exception as e:
            error_msg = f"Error stopping comprehensive monitoring: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Returns:
            Dict: Comprehensive status information
        """
        try:
            status_start = time.time()
            
            # Get controller status
            controller_status = self.controller.get_system_status(force_refresh=True)
            
            # Get health summary
            health_summary = self.health_monitor.get_health_summary()
            
            # Get dashboard summary
            dashboard_summary = self.dashboard.get_dashboard_summary()
            
            # Get real-time metrics
            real_time_metrics = self.logger.get_real_time_metrics()
            
            # Get performance summary
            performance_summary = self.logger.get_performance_summary()
            
            # Calculate uptime
            uptime_hours = 0
            if self.start_time:
                uptime_delta = datetime.now() - self.start_time
                uptime_hours = uptime_delta.total_seconds() / 3600
            
            # Compile comprehensive status
            comprehensive_status = {
                'timestamp': datetime.now().isoformat(),
                'generation_time': time.time() - status_start,
                'system_initialized': self.system_initialized,
                'monitoring_active': self.monitoring_active,
                'uptime_hours': uptime_hours,
                'controller_status': controller_status,
                'health_summary': health_summary,
                'dashboard_summary': dashboard_summary,
                'real_time_metrics': real_time_metrics,
                'performance_summary': performance_summary,
                'component_status': {
                    'controller': controller_status.get('system_initialized', False),
                    'health_monitor': health_summary.get('monitoring_active', False),
                    'enhanced_logger': real_time_metrics.get('monitoring_active', False),
                    'dashboard': dashboard_summary.get('overall_status') != 'unknown'
                }
            }
            
            self.logger.log_performance("comprehensive_status_generation", 
                                      comprehensive_status['generation_time'])
            
            return comprehensive_status
            
        except Exception as e:
            error_msg = f"Error getting comprehensive status: {e}"
            self.logger.log_error(error_msg)
            return {
                'timestamp': datetime.now().isoformat(),
                'error': error_msg,
                'system_initialized': False
            }
    
    def generate_comprehensive_report(self, report_type: str = 'daily') -> Dict[str, Any]:
        """
        Generate comprehensive monitoring report
        
        Args:
            report_type: Type of report ('daily', 'weekly')
            
        Returns:
            Dict: Comprehensive report
        """
        try:
            report_start = time.time()
            
            self.logger.log_info(f"Generating {report_type} comprehensive report...")
            
            # Generate status report
            if report_type == 'daily':
                status_report = self.status_reporter.generate_daily_report()
            elif report_type == 'weekly':
                status_report = self.status_reporter.generate_weekly_report()
            else:
                return {'error': f'Unsupported report type: {report_type}'}
            
            # Get health trends
            hours = 24 if report_type == 'daily' else 168
            health_trends = self.health_monitor.analyze_health_trends(hours)
            
            # Get comprehensive status
            current_status = self.get_comprehensive_status()
            
            # Compile comprehensive report
            comprehensive_report = {
                'report_type': report_type,
                'generation_time': datetime.now().isoformat(),
                'generation_duration': time.time() - report_start,
                'status_report': status_report,
                'health_trends': health_trends,
                'current_status': current_status,
                'recommendations': self._generate_comprehensive_recommendations(
                    status_report, health_trends, current_status
                )
            }
            
            self.logger.log_performance(f"{report_type}_report_generation",
                                      comprehensive_report['generation_duration'])
            self.logger.log_audit(f"{report_type}_report_generated")
            
            return comprehensive_report
            
        except Exception as e:
            error_msg = f"Error generating comprehensive report: {e}"
            self.logger.log_error(error_msg)
            return {
                'report_type': report_type,
                'error': error_msg,
                'generation_time': datetime.now().isoformat()
            }
    
    def _generate_comprehensive_recommendations(self, status_report: Dict, 
                                              health_trends: Dict, 
                                              current_status: Dict) -> List[str]:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        try:
            # Add status report recommendations
            if 'recommendations' in status_report:
                recommendations.extend(status_report['recommendations'])
            
            # Add health trend recommendations
            if 'recommendations' in health_trends:
                recommendations.extend(health_trends['recommendations'])
            
            # Add current status recommendations
            health_summary = current_status.get('health_summary', {})
            health_score = health_summary.get('health_score', 100)
            
            if health_score < 70:
                recommendations.append(
                    f"Current health score is low ({health_score:.1f}) - investigate and resolve issues"
                )
            
            # Check component status
            component_status = current_status.get('component_status', {})
            unhealthy_components = [
                comp for comp, status in component_status.items() 
                if not status
            ]
            
            if unhealthy_components:
                recommendations.append(
                    f"Components need attention: {', '.join(unhealthy_components)}"
                )
            
            # Remove duplicates while preserving order
            seen = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec not in seen:
                    seen.add(rec)
                    unique_recommendations.append(rec)
            
            return unique_recommendations
            
        except Exception as e:
            self.logger.log_error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]
    
    def export_comprehensive_report(self, report_type: str = 'daily', 
                                   output_file: str = None) -> str:
        """
        Export comprehensive report to file
        
        Args:
            report_type: Type of report
            output_file: Output file path (optional)
            
        Returns:
            str: Path to exported file
        """
        try:
            # Generate report
            report = self.generate_comprehensive_report(report_type)
            
            if 'error' in report:
                self.logger.log_error(f"Report generation failed: {report['error']}")
                return ""
            
            # Determine output file
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"comprehensive_{report_type}_report_{timestamp}.json"
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.log_audit("comprehensive_report_exported",
                                report_type=report_type,
                                output_file=output_file)
            
            return output_file
            
        except Exception as e:
            error_msg = f"Error exporting comprehensive report: {e}"
            self.logger.log_error(error_msg)
            return ""
    
    def send_status_email(self, report_type: str = 'daily', 
                         recipients: List[str] = None) -> Tuple[bool, str]:
        """
        Send status report via email
        
        Args:
            report_type: Type of report
            recipients: Email recipients
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not recipients:
                return False, "No recipients specified"
            
            if report_type == 'daily':
                success, message = self.automated_reporter.send_daily_report(recipients)
            elif report_type == 'weekly':
                success, message = self.automated_reporter.send_weekly_report(recipients)
            else:
                return False, f"Unsupported report type: {report_type}"
            
            if success:
                self.logger.log_audit("status_email_sent",
                                    report_type=report_type,
                                    recipients=recipients)
            
            return success, message
            
        except Exception as e:
            error_msg = f"Error sending status email: {e}"
            self.logger.log_error(error_msg)
            return False, error_msg
    
    def cleanup(self):
        """Clean up comprehensive monitoring system"""
        try:
            self.logger.log_info("Cleaning up comprehensive monitoring system...")
            
            # Stop monitoring
            if self.monitoring_active:
                self.stop_monitoring()
            
            # Stop health monitoring
            self.health_monitor.stop_continuous_monitoring()
            
            # Stop enhanced logger monitoring
            self.logger.stop_real_time_monitoring()
            
            # Clean up controller
            self.controller.cleanup_system()
            
            # Clean up health monitor
            self.health_monitor.cleanup()
            
            # Clean up logger
            self.logger.cleanup()
            
            self.system_initialized = False
            
            self.logger.log_info("Comprehensive monitoring system cleanup completed")
            self.logger.log_audit("system_cleanup_completed")
            
        except Exception as e:
            self.logger.log_error(f"Error during system cleanup: {e}")


# Command-line interface
def main():
    """
    Main entry point for comprehensive monitoring system
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive Website Monitoring System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize and start monitoring
  python comprehensive_monitoring_integration.py start --interval 60
  
  # Get system status
  python comprehensive_monitoring_integration.py status
  
  # Generate daily report
  python comprehensive_monitoring_integration.py report --type daily
  
  # Send weekly report via email
  python comprehensive_monitoring_integration.py email --type weekly --recipients admin@example.com
        """
    )
    
    parser.add_argument(
        'action',
        choices=['start', 'stop', 'status', 'report', 'email', 'health'],
        help='Action to perform'
    )
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Monitoring interval in minutes (default: 60)'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['daily', 'weekly'],
        default='daily',
        help='Report type (default: daily)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for report export'
    )
    parser.add_argument(
        '--recipients', '-r',
        nargs='+',
        help='Email recipients for email action'
    )
    
    args = parser.parse_args()
    
    system = None
    try:
        # Initialize comprehensive monitoring system
        print("Initializing comprehensive monitoring system...")
        system = ComprehensiveMonitoringSystem(args.config)
        
        if args.action == 'start':
            print(f"Starting monitoring (interval: {args.interval} minutes)...")
            success, message = system.start_monitoring(args.interval)
            
            if success:
                print(f"✓ {message}")
                print("Press Ctrl+C to stop...")
                
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nStopping monitoring...")
                    success, message = system.stop_monitoring()
                    print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                return 1
        
        elif args.action == 'stop':
            success, message = system.stop_monitoring()
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                return 1
        
        elif args.action == 'status':
            print("Getting comprehensive status...")
            status = system.get_comprehensive_status()
            
            print("\nComprehensive System Status:")
            print("=" * 60)
            print(f"System Initialized: {'✓' if status.get('system_initialized', False) else '✗'}")
            print(f"Monitoring Active: {'✓' if status.get('monitoring_active', False) else '✗'}")
            print(f"Uptime: {status.get('uptime_hours', 0):.1f} hours")
            
            health_summary = status.get('health_summary', {})
            print(f"\nHealth Status: {health_summary.get('overall_status', 'unknown').upper()}")
            print(f"Health Score: {health_summary.get('health_score', 0):.1f}/100")
            
            component_status = status.get('component_status', {})
            print("\nComponent Status:")
            for component, is_healthy in component_status.items():
                status_icon = '✓' if is_healthy else '✗'
                print(f"  {status_icon} {component}")
        
        elif args.action == 'report':
            print(f"Generating {args.type} report...")
            output_file = system.export_comprehensive_report(args.type, args.output)
            
            if output_file:
                print(f"✓ Report exported to: {output_file}")
            else:
                print("✗ Failed to export report")
                return 1
        
        elif args.action == 'email':
            if not args.recipients:
                print("✗ Recipients required for email action")
                return 1
            
            print(f"Sending {args.type} report to {len(args.recipients)} recipients...")
            success, message = system.send_status_email(args.type, args.recipients)
            
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
                return 1
        
        elif args.action == 'health':
            print("Performing health check...")
            health_report = system.health_monitor.perform_health_check()
            
            print("\nHealth Check Results:")
            print("=" * 60)
            print(f"Overall Status: {health_report.get('overall_status', 'unknown').upper()}")
            print(f"Health Score: {health_report.get('health_score', 0):.1f}/100")
            print(f"Check Duration: {health_report.get('check_duration', 0):.2f}s")
            
            recommendations = health_report.get('recommendations', [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    finally:
        if system:
            system.cleanup()


if __name__ == "__main__":
    sys.exit(main())
