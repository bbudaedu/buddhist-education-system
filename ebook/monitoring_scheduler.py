#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Monitoring Scheduler Integration
網站監控排程整合

This module provides scheduling integration for the website monitoring system,
including Windows Task Scheduler integration and notification system coordination.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Import monitoring components
from monitoring_controller import MonitoringController
from config_manager import ConfigManager
from notification_processor import NotificationProcessor


class MonitoringScheduler:
    """
    Scheduler integration for website monitoring system
    
    Provides:
    - Windows Task Scheduler integration
    - Scheduled monitoring execution
    - Notification system coordination
    - Schedule management and monitoring
    """
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize monitoring scheduler
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for scheduling operations
        """
        self.config_path = config_path
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.config_manager = ConfigManager(config_path, self.logger)
        self.controller = MonitoringController(config_path, self.logger)
        
        # Scheduler configuration
        self.task_name = "WebsiteMonitoring"
        self.script_path = os.path.abspath(__file__)
        self.cli_path = os.path.join(os.path.dirname(self.script_path), "website_monitoring_cli.py")
        
        self.logger.info("Monitoring Scheduler initialized")
    
    def create_scheduled_task(self, interval_minutes: int = 60, 
                            start_time: str = "09:00", 
                            enabled: bool = True) -> Tuple[bool, str]:
        """
        Create Windows scheduled task for monitoring
        
        Args:
            interval_minutes: Monitoring interval in minutes
            start_time: Start time in HH:MM format
            enabled: Whether task should be enabled
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info(f"Creating scheduled task: {self.task_name}")
            
            # Prepare task XML configuration
            task_xml = self._generate_task_xml(interval_minutes, start_time, enabled)
            
            # Create temporary XML file
            xml_file = f"{self.task_name}_task.xml"
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(task_xml)
            
            try:
                # Create scheduled task using schtasks command
                cmd = [
                    'schtasks',
                    '/create',
                    '/tn', self.task_name,
                    '/xml', xml_file,
                    '/f'  # Force overwrite if exists
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                # Clean up XML file
                os.remove(xml_file)
                
                # Update configuration
                self.config_manager.update_website_monitoring_config({
                    'scheduled_task': {
                        'enabled': enabled,
                        'interval_minutes': interval_minutes,
                        'start_time': start_time,
                        'task_name': self.task_name,
                        'created_date': datetime.now().isoformat()
                    }
                })
                
                message = f"Scheduled task '{self.task_name}' created successfully"
                self.logger.info(message)
                return True, message
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to create scheduled task: {e.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
            
            finally:
                # Clean up XML file if it still exists
                if os.path.exists(xml_file):
                    os.remove(xml_file)
                    
        except Exception as e:
            error_msg = f"Error creating scheduled task: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _generate_task_xml(self, interval_minutes: int, start_time: str, enabled: bool) -> str:
        """
        Generate Windows Task Scheduler XML configuration
        
        Args:
            interval_minutes: Monitoring interval in minutes
            start_time: Start time in HH:MM format
            enabled: Whether task should be enabled
            
        Returns:
            str: Task XML configuration
        """
        # Get current user and working directory
        username = os.environ.get('USERNAME', 'SYSTEM')
        working_dir = os.path.dirname(self.script_path)
        
        # Calculate repetition interval
        repetition_interval = f"PT{interval_minutes}M"
        
        xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>{username}</Author>
    <Description>Website Monitoring System - Automated monitoring of Buddhist Education website content</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>{repetition_interval}</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{start_time}:00</StartBoundary>
      <Enabled>{str(enabled).lower()}</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>{str(enabled).lower()}</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"{self.cli_path}" run</Arguments>
      <WorkingDirectory>{working_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
        
        return xml_template
    
    def delete_scheduled_task(self) -> Tuple[bool, str]:
        """
        Delete Windows scheduled task
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info(f"Deleting scheduled task: {self.task_name}")
            
            cmd = [
                'schtasks',
                '/delete',
                '/tn', self.task_name,
                '/f'  # Force delete without confirmation
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Update configuration
            monitoring_config = self.config_manager.get_website_monitoring_config()
            if 'scheduled_task' in monitoring_config:
                monitoring_config['scheduled_task']['enabled'] = False
                monitoring_config['scheduled_task']['deleted_date'] = datetime.now().isoformat()
                self.config_manager.update_website_monitoring_config(monitoring_config)
            
            message = f"Scheduled task '{self.task_name}' deleted successfully"
            self.logger.info(message)
            return True, message
            
        except subprocess.CalledProcessError as e:
            if "The system cannot find the file specified" in e.stderr:
                message = f"Scheduled task '{self.task_name}' does not exist"
                self.logger.info(message)
                return True, message
            else:
                error_msg = f"Failed to delete scheduled task: {e.stderr}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error deleting scheduled task: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_task_status(self) -> Dict[str, Any]:
        """
        Get scheduled task status
        
        Returns:
            Dict: Task status information
        """
        try:
            cmd = [
                'schtasks',
                '/query',
                '/tn', self.task_name,
                '/fo', 'csv',
                '/v'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse CSV output (simplified)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Extract basic status information
                status_line = lines[1].split(',')
                
                return {
                    'exists': True,
                    'task_name': self.task_name,
                    'status': status_line[3].strip('"') if len(status_line) > 3 else 'Unknown',
                    'next_run_time': status_line[4].strip('"') if len(status_line) > 4 else 'Unknown',
                    'last_run_time': status_line[5].strip('"') if len(status_line) > 5 else 'Unknown',
                    'last_result': status_line[6].strip('"') if len(status_line) > 6 else 'Unknown'
                }
            else:
                return {'exists': False, 'error': 'Task not found'}
                
        except subprocess.CalledProcessError as e:
            if "The system cannot find the file specified" in e.stderr:
                return {'exists': False, 'message': 'Task does not exist'}
            else:
                return {'exists': False, 'error': e.stderr}
                
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def enable_task(self) -> Tuple[bool, str]:
        """
        Enable scheduled task
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            cmd = [
                'schtasks',
                '/change',
                '/tn', self.task_name,
                '/enable'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            message = f"Scheduled task '{self.task_name}' enabled"
            self.logger.info(message)
            return True, message
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to enable scheduled task: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error enabling scheduled task: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def disable_task(self) -> Tuple[bool, str]:
        """
        Disable scheduled task
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            cmd = [
                'schtasks',
                '/change',
                '/tn', self.task_name,
                '/disable'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            message = f"Scheduled task '{self.task_name}' disabled"
            self.logger.info(message)
            return True, message
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to disable scheduled task: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error disabling scheduled task: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def run_task_now(self) -> Tuple[bool, str]:
        """
        Run scheduled task immediately
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            cmd = [
                'schtasks',
                '/run',
                '/tn', self.task_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            message = f"Scheduled task '{self.task_name}' started"
            self.logger.info(message)
            return True, message
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to run scheduled task: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error running scheduled task: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def setup_notification_scheduling(self) -> Tuple[bool, str]:
        """
        Setup notification scheduling integration
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.logger.info("Setting up notification scheduling integration...")
            
            # Get monitoring configuration
            monitoring_config = self.config_manager.get_website_monitoring_config()
            notification_config = monitoring_config.get('notifications', {})
            
            # Configure notification processor for scheduled execution
            notification_updates = {
                'scheduled_execution': True,
                'batch_notifications': True,
                'notification_queue_enabled': True,
                'retry_failed_notifications': True,
                'notification_log_enabled': True
            }
            
            # Update notification configuration
            notification_config.update(notification_updates)
            
            success = self.config_manager.update_notification_config(notification_config)
            
            if success:
                message = "Notification scheduling integration configured successfully"
                self.logger.info(message)
                return True, message
            else:
                message = "Failed to configure notification scheduling integration"
                self.logger.error(message)
                return False, message
                
        except Exception as e:
            error_msg = f"Error setting up notification scheduling: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_scheduling_status(self) -> Dict[str, Any]:
        """
        Get comprehensive scheduling status
        
        Returns:
            Dict: Scheduling status information
        """
        try:
            status = {
                'timestamp': datetime.now().isoformat(),
                'task_status': self.get_task_status(),
                'configuration': {},
                'system_status': {}
            }
            
            # Get configuration status
            monitoring_config = self.config_manager.get_website_monitoring_config()
            scheduled_task_config = monitoring_config.get('scheduled_task', {})
            
            status['configuration'] = {
                'task_configured': bool(scheduled_task_config),
                'task_enabled': scheduled_task_config.get('enabled', False),
                'interval_minutes': scheduled_task_config.get('interval_minutes', 0),
                'start_time': scheduled_task_config.get('start_time', ''),
                'created_date': scheduled_task_config.get('created_date', ''),
                'notification_scheduling': monitoring_config.get('notifications', {}).get('scheduled_execution', False)
            }
            
            # Get system status
            system_status = self.controller.get_system_status()
            status['system_status'] = {
                'monitoring_initialized': system_status.get('system_initialized', False),
                'monitoring_active': system_status.get('monitoring_status', {}).get('monitoring_active', False),
                'last_cycle_time': system_status.get('performance_metrics', {}).get('last_cycle_time'),
                'total_cycles': system_status.get('performance_metrics', {}).get('total_cycles', 0)
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting scheduling status: {e}")
            return {'error': str(e)}


def main():
    """
    Main scheduler script entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Website Monitoring Scheduler')
    parser.add_argument(
        'action',
        choices=['create', 'delete', 'enable', 'disable', 'run', 'status', 'setup-notifications'],
        help='Scheduler action to perform'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Monitoring interval in minutes (default: 60)'
    )
    parser.add_argument(
        '--start-time', '-s',
        default='09:00',
        help='Start time in HH:MM format (default: 09:00)'
    )
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
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'scheduler_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize scheduler
        scheduler = MonitoringScheduler(args.config, logger)
        
        # Execute action
        if args.action == 'create':
            success, message = scheduler.create_scheduled_task(args.interval, args.start_time)
            print(f"Create task: {'✓' if success else '✗'} {message}")
            
        elif args.action == 'delete':
            success, message = scheduler.delete_scheduled_task()
            print(f"Delete task: {'✓' if success else '✗'} {message}")
            
        elif args.action == 'enable':
            success, message = scheduler.enable_task()
            print(f"Enable task: {'✓' if success else '✗'} {message}")
            
        elif args.action == 'disable':
            success, message = scheduler.disable_task()
            print(f"Disable task: {'✓' if success else '✗'} {message}")
            
        elif args.action == 'run':
            success, message = scheduler.run_task_now()
            print(f"Run task: {'✓' if success else '✗'} {message}")
            
        elif args.action == 'status':
            status = scheduler.get_scheduling_status()
            print("Scheduling Status:")
            print("=" * 30)
            
            task_status = status.get('task_status', {})
            print(f"Task Exists: {'✓' if task_status.get('exists', False) else '✗'}")
            
            if task_status.get('exists'):
                print(f"Task Status: {task_status.get('status', 'Unknown')}")
                print(f"Next Run: {task_status.get('next_run_time', 'Unknown')}")
                print(f"Last Run: {task_status.get('last_run_time', 'Unknown')}")
                print(f"Last Result: {task_status.get('last_result', 'Unknown')}")
            
            config = status.get('configuration', {})
            print(f"Configuration: {'✓' if config.get('task_configured', False) else '✗'}")
            print(f"Interval: {config.get('interval_minutes', 0)} minutes")
            
        elif args.action == 'setup-notifications':
            success, message = scheduler.setup_notification_scheduling()
            print(f"Setup notifications: {'✓' if success else '✗'} {message}")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"✗ Scheduler error: {e}")
        logger.error(f"Scheduler error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())