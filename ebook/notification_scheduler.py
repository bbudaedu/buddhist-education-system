#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Scheduler Module
通知排程器模組

This module handles scheduling and batching of website monitoring notifications,
implementing immediate alerts for urgent content and daily summaries for regular content.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from queue import Queue, Empty
from dataclasses import dataclass, asdict

from website_notification_sender import WebsiteNotificationSender


@dataclass
class NotificationTask:
    """
    Represents a notification task with scheduling information
    """
    task_id: str
    content_data: Dict[str, List[Dict]]
    priority: str  # 'immediate', 'high', 'normal', 'low'
    scheduled_time: datetime
    retry_count: int = 0
    max_retries: int = 3
    attachment_paths: Optional[List[str]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class NotificationScheduler:
    """
    Handles scheduling and batching of website monitoring notifications
    
    Features:
    - Immediate alerts for urgent content (course cancellations)
    - Daily summary batching for regular content
    - Retry mechanism for failed notifications
    - Thread-safe operation
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize NotificationScheduler with configuration
        
        Args:
            config: Configuration dictionary containing scheduling settings
            logger: Logger instance for logging operations
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize notification sender
        self.notification_sender = WebsiteNotificationSender(config, logger)
        
        # Scheduling configuration
        self.immediate_alerts = config.get('website_monitoring', {}).get('notifications', {}).get('immediate_alerts', ['cancellation'])
        self.daily_summary = config.get('website_monitoring', {}).get('notifications', {}).get('daily_summary', ['carousel', 'news', 'media'])
        self.daily_summary_time = config.get('website_monitoring', {}).get('notifications', {}).get('daily_summary_time', '09:00')
        
        # Task queues
        self.immediate_queue = Queue()
        self.scheduled_queue = Queue()
        self.retry_queue = Queue()
        
        # Batching storage
        self.daily_batch = {}
        self.batch_lock = threading.Lock()
        
        # Scheduler control
        self.running = False
        self.scheduler_thread = None
        self.immediate_processor_thread = None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'immediate_sent': 0,
            'daily_summaries_sent': 0,
            'failed_notifications': 0,
            'retry_attempts': 0
        }
        
        self.logger.info("NotificationScheduler initialized")
    
    def start(self) -> None:
        """
        Start the notification scheduler
        """
        try:
            if self.running:
                self.logger.warning("Scheduler is already running")
                return
            
            self.running = True
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            # Start immediate processor thread
            self.immediate_processor_thread = threading.Thread(target=self._immediate_processor_loop, daemon=True)
            self.immediate_processor_thread.start()
            
            self.logger.info("NotificationScheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start NotificationScheduler: {e}")
            self.running = False
            raise
    
    def stop(self) -> None:
        """
        Stop the notification scheduler
        """
        try:
            self.running = False
            
            # Wait for threads to finish
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            if self.immediate_processor_thread and self.immediate_processor_thread.is_alive():
                self.immediate_processor_thread.join(timeout=5)
            
            self.logger.info("NotificationScheduler stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping NotificationScheduler: {e}")
    
    def schedule_notification(self, content_data: Dict[str, List[Dict]], attachment_paths: Optional[List[str]] = None) -> bool:
        """
        Schedule notification based on content priority
        
        Args:
            content_data: Dictionary containing content by type
            attachment_paths: Optional file attachments
            
        Returns:
            bool: True if scheduling successful
        """
        try:
            if not content_data or not any(content_data.values()):
                self.logger.info("No content data to schedule")
                return True
            
            # Separate immediate and regular content
            immediate_content = {}
            regular_content = {}
            
            for content_type, items in content_data.items():
                if not items:
                    continue
                
                if content_type in self.immediate_alerts:
                    immediate_content[content_type] = items
                else:
                    regular_content[content_type] = items
            
            # Schedule immediate notifications
            if immediate_content:
                task = NotificationTask(
                    task_id=f"immediate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    content_data=immediate_content,
                    priority='immediate',
                    scheduled_time=datetime.now(),
                    attachment_paths=attachment_paths
                )
                self.immediate_queue.put(task)
                self.logger.info(f"Scheduled immediate notification: {task.task_id}")
            
            # Add regular content to daily batch
            if regular_content:
                self._add_to_daily_batch(regular_content, attachment_paths)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notification: {e}")
            return False
    
    def _add_to_daily_batch(self, content_data: Dict[str, List[Dict]], attachment_paths: Optional[List[str]] = None) -> None:
        """
        Add content to daily batch for summary notification
        
        Args:
            content_data: Content data to batch
            attachment_paths: Optional file attachments
        """
        try:
            with self.batch_lock:
                today = datetime.now().date()
                
                if today not in self.daily_batch:
                    self.daily_batch[today] = {
                        'content_data': {},
                        'attachment_paths': set(),
                        'last_updated': datetime.now()
                    }
                
                # Merge content data
                for content_type, items in content_data.items():
                    if content_type not in self.daily_batch[today]['content_data']:
                        self.daily_batch[today]['content_data'][content_type] = []
                    
                    # Avoid duplicates by checking IDs
                    existing_ids = {item.get('id') for item in self.daily_batch[today]['content_data'][content_type]}
                    new_items = [item for item in items if item.get('id') not in existing_ids]
                    
                    self.daily_batch[today]['content_data'][content_type].extend(new_items)
                
                # Add attachment paths
                if attachment_paths:
                    self.daily_batch[today]['attachment_paths'].update(attachment_paths)
                
                self.daily_batch[today]['last_updated'] = datetime.now()
                
                self.logger.info(f"Added {sum(len(items) for items in content_data.values())} items to daily batch for {today}")
                
        except Exception as e:
            self.logger.error(f"Failed to add to daily batch: {e}")
    
    def _scheduler_loop(self) -> None:
        """
        Main scheduler loop for processing scheduled tasks and daily summaries
        """
        self.logger.info("Scheduler loop started")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Process scheduled tasks
                self._process_scheduled_tasks(current_time)
                
                # Process retry queue
                self._process_retry_queue(current_time)
                
                # Check for daily summary sending
                self._check_daily_summary_schedule(current_time)
                
                # Clean up old batches
                self._cleanup_old_batches(current_time)
                
                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _immediate_processor_loop(self) -> None:
        """
        Process immediate notifications as they arrive
        """
        self.logger.info("Immediate processor loop started")
        
        while self.running:
            try:
                # Get immediate task from queue (blocking with timeout)
                task = self.immediate_queue.get(timeout=1)
                
                self.logger.info(f"Processing immediate notification: {task.task_id}")
                
                # Send notification immediately
                success = self.notification_sender.send_notifications(
                    content_data=task.content_data,
                    attachment_paths=task.attachment_paths
                )
                
                if success:
                    self.stats['immediate_sent'] += 1
                    self.stats['total_processed'] += 1
                    self.logger.info(f"Immediate notification sent successfully: {task.task_id}")
                else:
                    self._handle_failed_task(task)
                
                self.immediate_queue.task_done()
                
            except Empty:
                # No immediate tasks, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing immediate notification: {e}")
    
    def _process_scheduled_tasks(self, current_time: datetime) -> None:
        """
        Process tasks from the scheduled queue
        
        Args:
            current_time: Current datetime for scheduling comparison
        """
        try:
            processed_tasks = []
            
            # Get all tasks from queue
            while not self.scheduled_queue.empty():
                try:
                    task = self.scheduled_queue.get_nowait()
                    
                    if task.scheduled_time <= current_time:
                        # Time to process this task
                        success = self.notification_sender.send_notifications(
                            content_data=task.content_data,
                            attachment_paths=task.attachment_paths
                        )
                        
                        if success:
                            self.stats['total_processed'] += 1
                            self.logger.info(f"Scheduled notification sent: {task.task_id}")
                        else:
                            self._handle_failed_task(task)
                    else:
                        # Not time yet, put back in queue
                        processed_tasks.append(task)
                    
                    self.scheduled_queue.task_done()
                    
                except Empty:
                    break
            
            # Put unprocessed tasks back in queue
            for task in processed_tasks:
                self.scheduled_queue.put(task)
                
        except Exception as e:
            self.logger.error(f"Error processing scheduled tasks: {e}")
    
    def _process_retry_queue(self, current_time: datetime) -> None:
        """
        Process tasks from the retry queue
        
        Args:
            current_time: Current datetime for retry timing
        """
        try:
            processed_tasks = []
            
            while not self.retry_queue.empty():
                try:
                    task = self.retry_queue.get_nowait()
                    
                    # Check if enough time has passed for retry (exponential backoff)
                    retry_delay = min(300 * (2 ** task.retry_count), 3600)  # Max 1 hour
                    retry_time = task.created_at + timedelta(seconds=retry_delay)
                    
                    if current_time >= retry_time:
                        # Attempt retry
                        success = self.notification_sender.send_notifications(
                            content_data=task.content_data,
                            attachment_paths=task.attachment_paths
                        )
                        
                        if success:
                            self.stats['total_processed'] += 1
                            self.stats['retry_attempts'] += 1
                            self.logger.info(f"Retry successful for task: {task.task_id}")
                        else:
                            task.retry_count += 1
                            if task.retry_count < task.max_retries:
                                processed_tasks.append(task)
                                self.logger.warning(f"Retry {task.retry_count} failed for task: {task.task_id}")
                            else:
                                self.stats['failed_notifications'] += 1
                                self.logger.error(f"Task failed after {task.max_retries} retries: {task.task_id}")
                    else:
                        # Not time for retry yet
                        processed_tasks.append(task)
                    
                    self.retry_queue.task_done()
                    
                except Empty:
                    break
            
            # Put tasks back in retry queue
            for task in processed_tasks:
                self.retry_queue.put(task)
                
        except Exception as e:
            self.logger.error(f"Error processing retry queue: {e}")
    
    def _check_daily_summary_schedule(self, current_time: datetime) -> None:
        """
        Check if it's time to send daily summary notifications
        
        Args:
            current_time: Current datetime
        """
        try:
            # Parse daily summary time
            summary_hour, summary_minute = map(int, self.daily_summary_time.split(':'))
            
            # Check if current time matches summary schedule
            if (current_time.hour == summary_hour and 
                current_time.minute == summary_minute and 
                current_time.second < 30):  # Within 30 seconds of scheduled time
                
                self._send_daily_summaries(current_time.date())
                
        except Exception as e:
            self.logger.error(f"Error checking daily summary schedule: {e}")
    
    def _send_daily_summaries(self, target_date: datetime.date) -> None:
        """
        Send daily summary notifications for the specified date
        
        Args:
            target_date: Date to send summaries for
        """
        try:
            with self.batch_lock:
                if target_date not in self.daily_batch:
                    self.logger.info(f"No daily batch data for {target_date}")
                    return
                
                batch_data = self.daily_batch[target_date]
                
                if not batch_data['content_data'] or not any(batch_data['content_data'].values()):
                    self.logger.info(f"No content in daily batch for {target_date}")
                    return
                
                # Send daily summary
                attachment_paths = list(batch_data['attachment_paths']) if batch_data['attachment_paths'] else None
                
                success = self.notification_sender.send_notifications(
                    content_data=batch_data['content_data'],
                    attachment_paths=attachment_paths
                )
                
                if success:
                    self.stats['daily_summaries_sent'] += 1
                    self.stats['total_processed'] += 1
                    self.logger.info(f"Daily summary sent for {target_date}")
                    
                    # Remove sent batch
                    del self.daily_batch[target_date]
                else:
                    self.logger.error(f"Failed to send daily summary for {target_date}")
                
        except Exception as e:
            self.logger.error(f"Error sending daily summaries: {e}")
    
    def _cleanup_old_batches(self, current_time: datetime) -> None:
        """
        Clean up old batch data
        
        Args:
            current_time: Current datetime
        """
        try:
            with self.batch_lock:
                cutoff_date = current_time.date() - timedelta(days=7)
                
                old_dates = [date for date in self.daily_batch.keys() if date < cutoff_date]
                
                for old_date in old_dates:
                    del self.daily_batch[old_date]
                    self.logger.info(f"Cleaned up old batch data for {old_date}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old batches: {e}")
    
    def _handle_failed_task(self, task: NotificationTask) -> None:
        """
        Handle a failed notification task
        
        Args:
            task: Failed notification task
        """
        try:
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self.retry_queue.put(task)
                self.logger.warning(f"Task queued for retry: {task.task_id} (attempt {task.retry_count})")
            else:
                self.stats['failed_notifications'] += 1
                self.logger.error(f"Task failed permanently: {task.task_id}")
                
        except Exception as e:
            self.logger.error(f"Error handling failed task: {e}")
    
    def force_daily_summary(self, target_date: Optional[datetime.date] = None) -> bool:
        """
        Force sending of daily summary for specified date
        
        Args:
            target_date: Date to send summary for (default: today)
            
        Returns:
            bool: True if summary sent successfully
        """
        try:
            if target_date is None:
                target_date = datetime.now().date()
            
            self._send_daily_summaries(target_date)
            return True
            
        except Exception as e:
            self.logger.error(f"Error forcing daily summary: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get scheduler statistics
        
        Returns:
            Dictionary containing scheduler statistics
        """
        try:
            with self.batch_lock:
                batch_info = {
                    date.isoformat(): {
                        'content_types': list(data['content_data'].keys()),
                        'total_items': sum(len(items) for items in data['content_data'].values()),
                        'last_updated': data['last_updated'].isoformat()
                    }
                    for date, data in self.daily_batch.items()
                }
            
            return {
                **self.stats,
                'queue_sizes': {
                    'immediate': self.immediate_queue.qsize(),
                    'scheduled': self.scheduled_queue.qsize(),
                    'retry': self.retry_queue.qsize()
                },
                'daily_batches': batch_info,
                'running': self.running
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}


# Example usage
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example configuration
    config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'your_email@gmail.com',
        'smtp_password': 'your_app_password',
        'email_recipients': 'recipient@example.com',
        'website_monitoring': {
            'notifications': {
                'email_enabled': True,
                'line_enabled': True,
                'immediate_alerts': ['cancellation'],
                'daily_summary': ['carousel', 'news', 'media'],
                'daily_summary_time': '09:00'
            }
        }
    }
    
    try:
        # Initialize scheduler
        scheduler = NotificationScheduler(config)
        
        # Start scheduler
        scheduler.start()
        
        # Example: Schedule some notifications
        test_content = {
            'cancellation': [{
                'id': 'cancel_001',
                'course_name': '測試課程',
                'instructor_name': '測試講師',
                'cancellation_date': '2024-11-07',
                'notification_text': '課程取消通知測試'
            }],
            'news': [{
                'id': 'news_001',
                'title': '測試公告',
                'publication_date': '2024-11-06',
                'content': '這是一個測試公告內容',
                'notification_text': '新公告測試'
            }]
        }
        
        scheduler.schedule_notification(test_content)
        
        # Keep running for demonstration
        print("Scheduler running... Press Ctrl+C to stop")
        try:
            while True:
                stats = scheduler.get_statistics()
                print(f"Stats: {stats}")
                time.sleep(60)
        except KeyboardInterrupt:
            print("Stopping scheduler...")
            scheduler.stop()
            
    except Exception as e:
        print(f"Error: {e}")