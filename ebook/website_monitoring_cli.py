#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Monitoring CLI Interface
網站監控命令列介面

This module provides a unified command-line interface for the website monitoring system,
including manual execution, scheduling integration, and deployment management.
"""

import os
import sys
import argparse
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Import monitoring components
from monitoring_controller import MonitoringController
from config_manager import ConfigManager


class WebsiteMonitoringCLI:
    """
    Command-line interface for website monitoring system
    
    Provides:
    - Manual monitoring execution
    - Configuration management
    - Status monitoring and reporting
    - Scheduling integration
    - Deployment utilities
    """
    
    def __init__(self, config_path: str = "config.json", verbose: bool = False):
        """
        Initialize CLI interface
        
        Args:
            config_path: Path to configuration file
            verbose: Enable verbose logging
        """
        self.config_path = config_path
        self.verbose = verbose
        
        # Set up logging
        self.setup_logging()
        
        # Initialize components
        self.controller = MonitoringController(config_path, self.logger)
        self.config_manager = ConfigManager(config_path, self.logger)
        
        self.logger.info("Website Monitoring CLI initialized")
    
    def setup_logging(self):
        """Set up logging configuration"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        handlers = [
            logging.FileHandler(
                os.path.join(log_dir, f'website_monitoring_cli_{datetime.now().strftime("%Y%m%d")}.log'),
                encoding='utf-8'
            )
        ]
        
        # Add console handler if verbose
        if self.verbose:
            handlers.append(logging.StreamHandler())
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers
        )
        
        self.logger = logging.getLogger(__name__)
    
    def run_single_cycle(self, content_types: Optional[List[str]] = None) -> int:
        """
        Run a single monitoring cycle
        
        Args:
            content_types: Specific content types to monitor (optional)
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Starting single monitoring cycle...")
            self.logger.info("CLI: Starting single monitoring cycle")
            
            # Filter content types if specified
            if content_types:
                self._configure_content_types(content_types)
            
            # Run single cycle
            success, message, results = self.controller.run_single_cycle()
            
            if success:
                print(f"✓ Monitoring cycle completed successfully")
                print(f"  Duration: {results.get('duration_seconds', 0):.1f} seconds")
                
                # Display content summary
                monitoring_status = results.get('monitoring_status', {})
                stats = monitoring_status.get('statistics', {})
                
                if stats:
                    print(f"  Content processed: {stats.get('total_content_processed', 0)} items")
                    print(f"  Cycles completed: {stats.get('cycles_completed', 0)}")
                
                self.logger.info(f"CLI: Single cycle completed - {message}")
                return 0
            else:
                print(f"✗ Monitoring cycle failed: {message}")
                self.logger.error(f"CLI: Single cycle failed - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error running single cycle: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def start_continuous_monitoring(self, interval_minutes: int = 60) -> int:
        """
        Start continuous monitoring
        
        Args:
            interval_minutes: Monitoring interval in minutes
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print(f"Starting continuous monitoring (interval: {interval_minutes} minutes)...")
            self.logger.info(f"CLI: Starting continuous monitoring - {interval_minutes} min interval")
            
            success, message = self.controller.start_monitoring(interval_minutes)
            
            if success:
                print(f"✓ Continuous monitoring started")
                print(f"  Interval: {interval_minutes} minutes")
                print(f"  Press Ctrl+C to stop monitoring")
                
                self.logger.info(f"CLI: Continuous monitoring started - {message}")
                
                # Keep running until interrupted
                try:
                    while True:
                        time.sleep(10)
                        # Check if monitoring is still active
                        status = self.controller.get_system_status()
                        if not status.get('monitoring_status', {}).get('monitoring_active', False):
                            print("Monitoring stopped unexpectedly")
                            break
                            
                except KeyboardInterrupt:
                    print("\nStopping monitoring...")
                    success, message = self.controller.stop_monitoring()
                    if success:
                        print("✓ Monitoring stopped successfully")
                    else:
                        print(f"✗ Error stopping monitoring: {message}")
                
                return 0
            else:
                print(f"✗ Failed to start monitoring: {message}")
                self.logger.error(f"CLI: Failed to start monitoring - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error starting continuous monitoring: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def stop_monitoring(self) -> int:
        """
        Stop continuous monitoring
        
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Stopping monitoring...")
            self.logger.info("CLI: Stopping monitoring")
            
            success, message = self.controller.stop_monitoring()
            
            if success:
                print(f"✓ Monitoring stopped successfully")
                self.logger.info(f"CLI: Monitoring stopped - {message}")
                return 0
            else:
                print(f"✗ Failed to stop monitoring: {message}")
                self.logger.error(f"CLI: Failed to stop monitoring - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error stopping monitoring: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def show_status(self, detailed: bool = False) -> int:
        """
        Show system status
        
        Args:
            detailed: Show detailed status information
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Website Monitoring System Status")
            print("=" * 40)
            
            status = self.controller.get_system_status(force_refresh=True)
            
            # Basic status
            print(f"System Initialized: {'✓' if status.get('system_initialized', False) else '✗'}")
            
            monitoring_status = status.get('monitoring_status', {})
            print(f"Monitoring Active: {'✓' if monitoring_status.get('monitoring_active', False) else '✗'}")
            
            # Configuration summary
            config_summary = status.get('configuration', {})
            print(f"Monitoring Enabled: {'✓' if config_summary.get('monitoring_enabled', False) else '✗'}")
            print(f"Chrome DevTools: {'✓' if config_summary.get('chrome_devtools_enabled', False) else '✗'}")
            
            # Content types
            content_types = config_summary.get('content_types_enabled', {})
            if content_types:
                print("\nContent Types:")
                for content_type, enabled in content_types.items():
                    status_icon = '✓' if enabled else '✗'
                    print(f"  {content_type}: {status_icon}")
            
            # Performance metrics
            performance = status.get('performance_metrics', {})
            if performance:
                print(f"\nPerformance:")
                print(f"  Total Cycles: {performance.get('total_cycles', 0)}")
                print(f"  Successful: {performance.get('successful_cycles', 0)}")
                print(f"  Failed: {performance.get('failed_cycles', 0)}")
                print(f"  Uptime: {status.get('uptime_hours', 0):.1f} hours")
                
                avg_time = performance.get('average_cycle_time', 0)
                if avg_time > 0:
                    print(f"  Avg Cycle Time: {avg_time:.1f} seconds")
            
            # Detailed information
            if detailed:
                print(f"\nDetailed Information:")
                print(f"  Configuration File: {self.config_path}")
                print(f"  Current Session: {monitoring_status.get('current_session_id', 'None')}")
                
                components = monitoring_status.get('components_initialized', {})
                print(f"  Components:")
                print(f"    Scrapers: {components.get('scrapers', 0)}")
                print(f"    Processors: {components.get('processors', 0)}")
                print(f"    Data Sync: {'✓' if components.get('data_synchronizer', False) else '✗'}")
                print(f"    Notifications: {'✓' if components.get('notification_processor', False) else '✗'}")
            
            return 0
            
        except Exception as e:
            error_msg = f"Error getting status: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def configure_system(self, config_updates: Dict[str, Any]) -> int:
        """
        Update system configuration
        
        Args:
            config_updates: Configuration updates to apply
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Updating system configuration...")
            self.logger.info(f"CLI: Updating configuration - {config_updates}")
            
            success, message = self.controller.update_configuration(config_updates)
            
            if success:
                print(f"✓ Configuration updated successfully")
                self.logger.info(f"CLI: Configuration updated - {message}")
                return 0
            else:
                print(f"✗ Configuration update failed: {message}")
                self.logger.error(f"CLI: Configuration update failed - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error updating configuration: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def enable_content_type(self, content_type: str) -> int:
        """
        Enable specific content type monitoring
        
        Args:
            content_type: Content type to enable
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print(f"Enabling {content_type} monitoring...")
            
            success, message = self.controller.enable_content_type(content_type)
            
            if success:
                print(f"✓ {content_type} monitoring enabled")
                return 0
            else:
                print(f"✗ Failed to enable {content_type}: {message}")
                return 1
                
        except Exception as e:
            print(f"✗ Error enabling {content_type}: {e}")
            return 1
    
    def disable_content_type(self, content_type: str) -> int:
        """
        Disable specific content type monitoring
        
        Args:
            content_type: Content type to disable
            
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print(f"Disabling {content_type} monitoring...")
            
            success, message = self.controller.disable_content_type(content_type)
            
            if success:
                print(f"✓ {content_type} monitoring disabled")
                return 0
            else:
                print(f"✗ Failed to disable {content_type}: {message}")
                return 1
                
        except Exception as e:
            print(f"✗ Error disabling {content_type}: {e}")
            return 1
    
    def show_performance_report(self) -> int:
        """
        Show detailed performance report
        
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Performance Report")
            print("=" * 30)
            
            report = self.controller.get_performance_report()
            
            if 'error' in report:
                print(f"✗ Error generating report: {report['error']}")
                return 1
            
            print(f"Uptime: {report.get('uptime_hours', 0):.1f} hours")
            print(f"Success Rate: {report.get('success_rate', 0):.1f}%")
            print(f"Average Cycle Time: {report.get('average_cycle_time', 0):.1f} seconds")
            print(f"Monitoring Active: {'✓' if report.get('monitoring_active', False) else '✗'}")
            
            # Component health
            health = report.get('component_health', {})
            if health:
                print("\nComponent Health:")
                for component, status in health.items():
                    status_icon = '✓' if status else '✗'
                    print(f"  {component}: {status_icon}")
            
            return 0
            
        except Exception as e:
            error_msg = f"Error generating performance report: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def initialize_system(self) -> int:
        """
        Initialize monitoring system
        
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Initializing monitoring system...")
            self.logger.info("CLI: Initializing system")
            
            success, message = self.controller.initialize_system()
            
            if success:
                print(f"✓ System initialized successfully")
                self.logger.info(f"CLI: System initialized - {message}")
                return 0
            else:
                print(f"✗ System initialization failed: {message}")
                self.logger.error(f"CLI: System initialization failed - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error initializing system: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def cleanup_system(self) -> int:
        """
        Clean up system resources
        
        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            print("Cleaning up system resources...")
            self.logger.info("CLI: Cleaning up system")
            
            success, message = self.controller.cleanup_system()
            
            if success:
                print(f"✓ System cleanup completed")
                self.logger.info(f"CLI: System cleanup completed - {message}")
                return 0
            else:
                print(f"✗ System cleanup failed: {message}")
                self.logger.error(f"CLI: System cleanup failed - {message}")
                return 1
                
        except Exception as e:
            error_msg = f"Error during cleanup: {e}"
            print(f"✗ {error_msg}")
            self.logger.error(f"CLI: {error_msg}")
            return 1
    
    def _configure_content_types(self, content_types: List[str]):
        """
        Configure specific content types for monitoring
        
        Args:
            content_types: List of content types to enable
        """
        try:
            # Disable all content types first
            all_types = ['carousel', 'cancellation', 'news', 'media']
            
            for content_type in all_types:
                enabled = content_type in content_types
                self.controller.update_configuration({
                    'content_types': {
                        content_type: {'enabled': enabled}
                    }
                })
            
            self.logger.info(f"CLI: Configured content types - {content_types}")
            
        except Exception as e:
            self.logger.error(f"CLI: Error configuring content types: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Website Monitoring System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                          # Run single monitoring cycle
  %(prog)s start --interval 30          # Start continuous monitoring (30 min)
  %(prog)s status --detailed            # Show detailed system status
  %(prog)s enable carousel news         # Enable specific content types
  %(prog)s disable media               # Disable media monitoring
  %(prog)s performance                 # Show performance report
        """
    )
    
    # Global options
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run single cycle
    run_parser = subparsers.add_parser('run', help='Run single monitoring cycle')
    run_parser.add_argument(
        '--content-types',
        nargs='+',
        choices=['carousel', 'cancellation', 'news', 'media'],
        help='Specific content types to monitor'
    )
    
    # Start continuous monitoring
    start_parser = subparsers.add_parser('start', help='Start continuous monitoring')
    start_parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Monitoring interval in minutes (default: 60)'
    )
    
    # Stop monitoring
    subparsers.add_parser('stop', help='Stop continuous monitoring')
    
    # Show status
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.add_argument(
        '--detailed', '-d',
        action='store_true',
        help='Show detailed status information'
    )
    
    # Enable content types
    enable_parser = subparsers.add_parser('enable', help='Enable content type monitoring')
    enable_parser.add_argument(
        'content_types',
        nargs='+',
        choices=['carousel', 'cancellation', 'news', 'media'],
        help='Content types to enable'
    )
    
    # Disable content types
    disable_parser = subparsers.add_parser('disable', help='Disable content type monitoring')
    disable_parser.add_argument(
        'content_types',
        nargs='+',
        choices=['carousel', 'cancellation', 'news', 'media'],
        help='Content types to disable'
    )
    
    # Performance report
    subparsers.add_parser('performance', help='Show performance report')
    
    # Initialize system
    subparsers.add_parser('init', help='Initialize monitoring system')
    
    # Cleanup system
    subparsers.add_parser('cleanup', help='Clean up system resources')
    
    return parser


def main():
    """
    Main CLI entry point
    """
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize CLI
    cli = WebsiteMonitoringCLI(args.config, args.verbose)
    
    try:
        # Execute command
        if args.command == 'run':
            return cli.run_single_cycle(args.content_types)
        
        elif args.command == 'start':
            return cli.start_continuous_monitoring(args.interval)
        
        elif args.command == 'stop':
            return cli.stop_monitoring()
        
        elif args.command == 'status':
            return cli.show_status(args.detailed)
        
        elif args.command == 'enable':
            exit_code = 0
            for content_type in args.content_types:
                result = cli.enable_content_type(content_type)
                if result != 0:
                    exit_code = result
            return exit_code
        
        elif args.command == 'disable':
            exit_code = 0
            for content_type in args.content_types:
                result = cli.disable_content_type(content_type)
                if result != 0:
                    exit_code = result
            return exit_code
        
        elif args.command == 'performance':
            return cli.show_performance_report()
        
        elif args.command == 'init':
            return cli.initialize_system()
        
        elif args.command == 'cleanup':
            return cli.cleanup_system()
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())