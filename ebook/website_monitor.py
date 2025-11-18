#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website Monitor Orchestrator Module for Buddhist Education Website Monitoring
網站監控協調器模組

This module provides the main WebsiteMonitor orchestrator class that coordinates
all specialized scrapers and processors for comprehensive website monitoring.
Integrates with existing infrastructure and Chrome DevTools MCP functionality.
"""

import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import existing infrastructure components
from config_manager import ConfigManager
from progress_manager import ProgressManager

# Import specialized scrapers and processors
from carousel_scraper import CarouselScraper
from bulletin_scraper import BulletinScraper
# NewsProcessor replaced by run_news_scraper_correct.py
from media_processor import MediaProcessor

# Import data synchronization components
from enhanced_data_synchronizer import EnhancedDataSynchronizer
from document_generator import DocumentGenerator

# Import notification components
from email_sender import EmailSender
from unified_notification_service import UnifiedNotificationService
from line_notification_service import LineNotificationService


class WebsiteMonitor:
    """
    Main orchestrator class for comprehensive website monitoring
    
    Coordinates all monitoring activities including:
    - Carousel banner monitoring
    - Course cancellation monitoring  
    - News announcement monitoring
    - Multimedia content monitoring
    - Data synchronization to Excel and MySQL
    - Notification processing and distribution
    """
    
    def __init__(self, config_path: str = "config.json", logger: Optional[logging.Logger] = None):
        """
        Initialize WebsiteMonitor with configuration and logging
        
        Args:
            config_path: Path to configuration file
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path, self.logger)
        self.config = self.config_manager.get_config()
        
        # Initialize progress manager for session tracking
        self.progress_manager = ProgressManager("website_monitoring", ".", self.logger)
        
        # Initialize specialized scrapers and processors
        self.scrapers = {}
        self.processors = {}
        
        # Initialize data synchronization components
        self.data_synchronizer = None
        self.document_generator = None
        
        # Initialize notification components
        self.notification_processor = None
        self.email_sender = None
        
        # Monitoring state
        self.monitoring_active = False
        self.current_session_id = None
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Performance tracking
        self.monitoring_stats = {
            'cycles_completed': 0,
            'total_content_processed': 0,
            'errors_encountered': 0,
            'last_successful_cycle': None,
            'average_cycle_time': 0
        }
        
        self.logger.info("WebsiteMonitor orchestrator initialized")
    
    def initialize_components(self) -> bool:
        """
        Initialize all monitoring components and validate configuration
        
        Returns:
            bool: True if all components initialized successfully
        """
        try:
            self.logger.info("Initializing website monitoring components...")
            
            # Validate configuration
            if not self._validate_configuration():
                return False
            
            # Get monitoring configuration
            monitoring_config = self.config_manager.get_website_monitoring_config()
            
            # Initialize scrapers and processors
            success = self._initialize_scrapers_and_processors(monitoring_config)
            if not success:
                return False
            
            # Initialize data synchronization components
            success = self._initialize_data_components()
            if not success:
                return False
            
            # Initialize notification components
            success = self._initialize_notification_components()
            if not success:
                return False
            
            self.logger.info("All website monitoring components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            return False
    
    def _validate_configuration(self) -> bool:
        """
        Validate that required configuration is present
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            required_fields = [
                'chromedriver_path',
                'download_dir'
            ]
            
            for field in required_fields:
                if field not in self.config or not self.config[field]:
                    self.logger.error(f"Missing required configuration field: {field}")
                    return False
            
            # Validate ChromeDriver path
            if not os.path.exists(self.config['chromedriver_path']):
                self.logger.error(f"ChromeDriver not found: {self.config['chromedriver_path']}")
                return False
            
            # Ensure download directory exists
            download_dir = self.config['download_dir']
            if not os.path.exists(download_dir):
                os.makedirs(download_dir, exist_ok=True)
                self.logger.info(f"Created download directory: {download_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False
    
    def _initialize_scrapers_and_processors(self, monitoring_config: Dict[str, Any]) -> bool:
        """
        Initialize specialized scrapers and processors
        
        Args:
            monitoring_config: Website monitoring configuration
            
        Returns:
            bool: True if initialization successful
        """
        try:
            chromedriver_path = self.config['chromedriver_path']
            download_dir = self.config['download_dir']
            
            # Initialize CarouselScraper if enabled
            if monitoring_config['content_types']['carousel']['enabled']:
                self.scrapers['carousel'] = CarouselScraper(
                    chromedriver_path=chromedriver_path,
                    download_dir=download_dir,
                    logger=self.logger,
                    use_chrome_devtools=monitoring_config['chrome_devtools']['enabled']
                )
                self.logger.info("CarouselScraper initialized")
            
            # Initialize BulletinScraper if enabled
            if monitoring_config['content_types']['cancellation']['enabled']:
                self.scrapers['bulletin'] = BulletinScraper(
                    chromedriver_path=chromedriver_path,
                    download_dir=download_dir,
                    logger=self.logger
                )
                self.logger.info("BulletinScraper initialized")
            
            # News processing uses run_news_scraper_correct.py (no initialization needed)
            if monitoring_config['content_types']['news']['enabled']:
                # Add a placeholder to indicate news processing is enabled
                self.processors['news'] = True  # Placeholder - actual processing via subprocess
                self.logger.info("News processing enabled (using run_news_scraper_correct.py)")
            
            # Initialize MediaProcessor if enabled
            if monitoring_config['content_types']['media']['enabled']:
                media_url = monitoring_config['content_types']['media'].get('url')
                self.processors['media'] = MediaProcessor(
                    chromedriver_path=chromedriver_path,
                    download_dir=download_dir,
                    logger=self.logger,
                    media_url=media_url
                )
                self.logger.info("MediaProcessor initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing scrapers and processors: {e}")
            return False
    
    def _initialize_data_components(self) -> bool:
        """
        Initialize data synchronization components
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize DocumentGenerator for Excel operations
            self.document_generator = DocumentGenerator(
                output_dir=self.config.get('download_dir', 'generated_documents'),
                logger=self.logger
            )
            
            # Initialize EnhancedDataSynchronizer for dual storage coordination
            self.data_synchronizer = EnhancedDataSynchronizer(
                document_generator=self.document_generator,
                config=self.config,
                logger=self.logger
            )
            
            self.logger.info("Data synchronization components initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing data components: {e}")
            return False
    
    def _initialize_notification_components(self) -> bool:
        """
        Initialize notification processing components
        
        Returns:
            bool: True if initialization successful
        """
        try:
            monitoring_config = self.config_manager.get_website_monitoring_config()
            
            # Initialize EmailSender if email notifications enabled
            if monitoring_config['notifications']['email_enabled']:
                self.email_sender = EmailSender(
                    config=self.config,
                    logger=self.logger
                )
                self.logger.info("EmailSender initialized")
            
            # Initialize LINE notification service
            line_service = LineNotificationService(
                config=self.config,
                logger=self.logger
            )
            
            # Initialize UnifiedNotificationService for integrated notifications
            self.notification_processor = UnifiedNotificationService(
                line_service=line_service,
                email_sender=self.email_sender,
                logger=self.logger
            )
            
            self.logger.info("Unified notification service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing notification components: {e}")
            return False
    
    def start_monitoring_cycle(self) -> bool:
        """
        Start a single monitoring cycle to process all content types
        
        Returns:
            bool: True if cycle completed successfully
        """
        try:
            cycle_start_time = datetime.now()
            self.logger.info("Starting website monitoring cycle")
            
            # Start new progress session
            self.current_session_id = self.progress_manager.start_new_session({
                'monitoring_type': 'website_monitoring',
                'cycle_start_time': cycle_start_time.isoformat()
            })
            
            # Process all content types
            all_content = {}
            processing_results = {}
            
            # Process carousel content
            if 'carousel' in self.scrapers:
                carousel_result = self.process_carousel_content()
                all_content['carousel'] = carousel_result.get('content', [])
                processing_results['carousel'] = carousel_result
            
            # Process course cancellation content
            if 'bulletin' in self.scrapers:
                bulletin_result = self.process_bulletin_content()
                all_content['cancellation'] = bulletin_result.get('content', [])
                processing_results['cancellation'] = bulletin_result
            
            # Process news content
            if 'news' in self.processors:
                news_result = self.process_news_content()
                all_content['news'] = news_result.get('content', [])
                processing_results['news'] = news_result
            
            # Process media content
            if 'media' in self.processors:
                media_result = self.process_media_content()
                all_content['media'] = media_result.get('content', [])
                processing_results['media'] = media_result
            
            # Synchronize all data to Excel and MySQL
            sync_success = self.synchronize_data(all_content)
            
            # Send notifications for new content
            notification_success = self.send_notifications(all_content, processing_results)
            
            # Update monitoring statistics
            cycle_end_time = datetime.now()
            cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
            
            self._update_monitoring_stats(cycle_duration, all_content, sync_success and notification_success)
            
            # Mark session as completed
            self.progress_manager.mark_session_completed()
            
            self.logger.info(f"Monitoring cycle completed in {cycle_duration:.1f} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
            if self.progress_manager:
                self.progress_manager.mark_session_interrupted()
            return False
    
    def process_carousel_content(self) -> Dict[str, Any]:
        """
        Process carousel banner content monitoring
        
        Returns:
            Dict: Processing results with content and status
        """
        try:
            self.logger.info("Processing carousel content...")
            
            carousel_scraper = self.scrapers['carousel']
            
            # Extract carousel banners
            banners = carousel_scraper.extract_carousel_banners()
            
            if banners:
                self.logger.info(f"Extracted {len(banners)} carousel banners")
                
                # Update baseline with latest banner
                if banners:
                    latest_banner_id = banners[0]['carousel_id']
                    carousel_scraper.update_carousel_baseline(latest_banner_id)
                
                return {
                    'success': True,
                    'content': banners,
                    'message': f'Successfully processed {len(banners)} carousel banners',
                    'content_type': 'carousel'
                }
            else:
                return {
                    'success': True,
                    'content': [],
                    'message': 'No carousel banners found',
                    'content_type': 'carousel'
                }
                
        except Exception as e:
            error_msg = f"Error processing carousel content: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'content': [],
                'error': error_msg,
                'content_type': 'carousel'
            }
        finally:
            # Clean up carousel scraper resources
            if 'carousel' in self.scrapers:
                try:
                    self.scrapers['carousel'].cleanup()
                except Exception as cleanup_error:
                    self.logger.warning(f"Carousel scraper cleanup error: {cleanup_error}")
    
    def process_bulletin_content(self) -> Dict[str, Any]:
        """
        Process course cancellation bulletin content
        
        Returns:
            Dict: Processing results with content and status
        """
        try:
            self.logger.info("Processing bulletin content...")
            
            bulletin_scraper = self.scrapers['bulletin']
            
            # Process cancellation monitoring
            result = bulletin_scraper.process_cancellation_monitoring()
            
            if result['success']:
                cancellations = result.get('cancellations', [])
                new_cancellations = result.get('new_cancellations', [])
                
                self.logger.info(f"Processed {len(cancellations)} cancellations, {len(new_cancellations)} new")
                
                return {
                    'success': True,
                    'content': cancellations,
                    'new_content': new_cancellations,
                    'message': result['message'],
                    'content_type': 'cancellation'
                }
            else:
                return {
                    'success': False,
                    'content': [],
                    'error': result.get('error', 'Unknown error'),
                    'content_type': 'cancellation'
                }
                
        except Exception as e:
            error_msg = f"Error processing bulletin content: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'content': [],
                'error': error_msg,
                'content_type': 'cancellation'
            }
    
    def process_news_content(self) -> Dict[str, Any]:
        """
        Process news announcement content using run_news_scraper_correct.py
        
        Returns:
            Dict: Processing results with content and status
        """
        try:
            self.logger.info("Processing news content using run_news_scraper_correct.py...")
            
            import subprocess
            import json
            from pathlib import Path
            
            # 執行新聞爬蟲腳本
            script_path = os.path.join(os.path.dirname(__file__), 'run_news_scraper_correct.py')
            
            if not os.path.exists(script_path):
                error_msg = f"News scraper script not found: {script_path}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'content': [],
                    'error': error_msg,
                    'content_type': 'news'
                }
            
            # 執行腳本
            self.logger.info(f"Executing: python {script_path}")
            result = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__),
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                error_msg = f"News scraper failed with exit code {result.returncode}"
                self.logger.error(error_msg)
                self.logger.error(f"stderr: {result.stderr}")
                return {
                    'success': False,
                    'content': [],
                    'error': error_msg,
                    'content_type': 'news'
                }
            
            # 讀取最新的 JSON 輸出檔案
            download_dir = self.config.get('download_dir', 'downloads')
            news_files = sorted(Path(download_dir).glob('news_*.json'), key=os.path.getmtime, reverse=True)
            
            if not news_files:
                self.logger.warning("No news JSON files found")
                return {
                    'success': True,
                    'content': [],
                    'message': 'No news items found',
                    'content_type': 'news'
                }
            
            # 讀取最新的新聞檔案
            latest_news_file = news_files[0]
            self.logger.info(f"Reading news from: {latest_news_file}")
            
            with open(latest_news_file, 'r', encoding='utf-8') as f:
                news_items = json.load(f)
            
            if news_items:
                self.logger.info(f"Successfully extracted {len(news_items)} news items")
                
                return {
                    'success': True,
                    'content': news_items,
                    'message': f'Successfully processed {len(news_items)} news items',
                    'content_type': 'news',
                    'output_file': str(latest_news_file)
                }
            else:
                return {
                    'success': True,
                    'content': [],
                    'message': 'No news items found',
                    'content_type': 'news'
                }
                
        except Exception as e:
            error_msg = f"Error processing news content: {e}"
            self.logger.error(error_msg, exc_info=True)
            return {
                'success': False,
                'content': [],
                'error': error_msg,
                'content_type': 'news'
            }
    
    def process_media_content(self) -> Dict[str, Any]:
        """
        Process multimedia content monitoring
        
        Returns:
            Dict: Processing results with content and status
        """
        try:
            self.logger.info("Processing media content...")
            
            media_processor = self.processors['media']
            
            # Extract media content
            media_items = media_processor.extract_media_content(max_items=20)
            
            if media_items:
                self.logger.info(f"Extracted {len(media_items)} media items")
                
                # Detect new media content
                new_media_items = media_processor.detect_new_media_content(media_items)
                
                # Update baseline with latest media
                if media_items:
                    latest_media_id = media_items[0]['media_id']
                    media_processor.update_media_baseline(latest_media_id)
                
                return {
                    'success': True,
                    'content': media_items,
                    'new_content': new_media_items,
                    'message': f'Successfully processed {len(media_items)} media items, {len(new_media_items)} new',
                    'content_type': 'media'
                }
            else:
                return {
                    'success': True,
                    'content': [],
                    'message': 'No media items found',
                    'content_type': 'media'
                }
                
        except Exception as e:
            error_msg = f"Error processing media content: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'content': [],
                'error': error_msg,
                'content_type': 'media'
            }
        finally:
            # Clean up media processor resources
            if 'media' in self.processors:
                try:
                    self.processors['media'].cleanup()
                except Exception as cleanup_error:
                    self.logger.warning(f"Media processor cleanup error: {cleanup_error}")   
 
    def synchronize_data(self, all_content: Dict[str, List[Dict[str, Any]]]) -> bool:
        """
        Synchronize all extracted content to Excel files and MySQL database
        
        Args:
            all_content: Dictionary containing all extracted content by type
            
        Returns:
            bool: True if synchronization successful
        """
        try:
            if not self.data_synchronizer:
                self.logger.error("Data synchronizer not initialized")
                return False
            
            self.logger.info("Starting data synchronization...")
            
            # Calculate total items for logging
            total_items = sum(len(content) for content in all_content.values())
            
            if total_items == 0:
                self.logger.info("No content to synchronize")
                return True
            
            # Synchronize each content type
            sync_results = {}
            
            for content_type, content_list in all_content.items():
                if content_list:
                    self.logger.info(f"Synchronizing {len(content_list)} {content_type} items...")
                    
                    try:
                        success = self.data_synchronizer.sync_content_type(content_type, content_list)
                        sync_results[content_type] = success
                        
                        if success:
                            self.logger.info(f"✓ {content_type} synchronization successful")
                        else:
                            self.logger.error(f"✗ {content_type} synchronization failed")
                            
                    except Exception as e:
                        self.logger.error(f"Error synchronizing {content_type}: {e}")
                        sync_results[content_type] = False
            
            # Check overall synchronization success
            overall_success = all(sync_results.values()) if sync_results else True
            
            if overall_success:
                self.logger.info(f"Data synchronization completed successfully ({total_items} items)")
            else:
                failed_types = [t for t, success in sync_results.items() if not success]
                self.logger.error(f"Data synchronization partially failed for: {failed_types}")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error in data synchronization: {e}")
            return False
    
    def send_notifications(self, all_content: Dict[str, List[Dict[str, Any]]], 
                          processing_results: Dict[str, Dict[str, Any]]) -> bool:
        """
        Send unified notification for new content
        
        Args:
            all_content: Dictionary containing all extracted content by type
            processing_results: Processing results for each content type
            
        Returns:
            bool: True if notifications sent successfully
        """
        try:
            if not self.notification_processor:
                self.logger.warning("Notification processor not initialized, skipping notifications")
                return True
            
            self.logger.info("Sending unified notification...")
            
            # 使用統一通知服務發送整合訊息
            success = self.notification_processor.send_unified_notification(all_content)
            
            if success:
                self.logger.info("Unified notification sent successfully")
            else:
                self.logger.error("Failed to send unified notification")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending notifications: {e}")
            return False
    
    def _generate_cycle_summary(self, all_content: Dict[str, List[Dict[str, Any]]], 
                               processing_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of the monitoring cycle
        
        Args:
            all_content: All extracted content
            processing_results: Processing results for each content type
            
        Returns:
            Dict: Cycle summary information
        """
        try:
            summary = {
                'cycle_timestamp': datetime.now(),
                'total_items_processed': sum(len(content) for content in all_content.values()),
                'content_type_counts': {content_type: len(content) for content_type, content in all_content.items()},
                'processing_success': {},
                'new_content_counts': {},
                'errors': []
            }
            
            # Analyze processing results
            for content_type, result in processing_results.items():
                summary['processing_success'][content_type] = result.get('success', False)
                
                if not result.get('success', False):
                    error_msg = result.get('error', 'Unknown error')
                    summary['errors'].append(f"{content_type}: {error_msg}")
                
                # Count new content
                new_content = result.get('new_content', [])
                summary['new_content_counts'][content_type] = len(new_content)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating cycle summary: {e}")
            return {'error': str(e)}
    
    def _update_monitoring_stats(self, cycle_duration: float, all_content: Dict[str, List], success: bool):
        """
        Update monitoring statistics
        
        Args:
            cycle_duration: Duration of the monitoring cycle in seconds
            all_content: All processed content
            success: Whether the cycle was successful
        """
        try:
            self.monitoring_stats['cycles_completed'] += 1
            
            total_items = sum(len(content) for content in all_content.values())
            self.monitoring_stats['total_content_processed'] += total_items
            
            if not success:
                self.monitoring_stats['errors_encountered'] += 1
            else:
                self.monitoring_stats['last_successful_cycle'] = datetime.now()
            
            # Update average cycle time
            current_avg = self.monitoring_stats['average_cycle_time']
            cycles_count = self.monitoring_stats['cycles_completed']
            
            if cycles_count == 1:
                self.monitoring_stats['average_cycle_time'] = cycle_duration
            else:
                # Calculate running average
                self.monitoring_stats['average_cycle_time'] = (
                    (current_avg * (cycles_count - 1) + cycle_duration) / cycles_count
                )
            
            self.logger.info(f"Monitoring stats updated: {cycles_count} cycles, {total_items} items processed")
            
        except Exception as e:
            self.logger.error(f"Error updating monitoring stats: {e}")
    
    def start_continuous_monitoring(self, interval_minutes: int = 60) -> bool:
        """
        Start continuous monitoring with specified interval
        
        Args:
            interval_minutes: Monitoring interval in minutes
            
        Returns:
            bool: True if monitoring started successfully
        """
        try:
            if self.monitoring_active:
                self.logger.warning("Monitoring is already active")
                return False
            
            self.logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")
            
            # Initialize components if not already done
            if not self.scrapers and not self.processors:
                if not self.initialize_components():
                    return False
            
            # Reset stop event
            self.stop_monitoring.clear()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._continuous_monitoring_loop,
                args=(interval_minutes,),
                daemon=True
            )
            
            self.monitoring_active = True
            self.monitoring_thread.start()
            
            self.logger.info("Continuous monitoring started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting continuous monitoring: {e}")
            return False
    
    def stop_continuous_monitoring(self) -> bool:
        """
        Stop continuous monitoring
        
        Returns:
            bool: True if monitoring stopped successfully
        """
        try:
            if not self.monitoring_active:
                self.logger.warning("Monitoring is not active")
                return False
            
            self.logger.info("Stopping continuous monitoring...")
            
            # Signal monitoring thread to stop
            self.stop_monitoring.set()
            
            # Wait for monitoring thread to finish (with timeout)
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=30)
                
                if self.monitoring_thread.is_alive():
                    self.logger.warning("Monitoring thread did not stop within timeout")
                    return False
            
            self.monitoring_active = False
            self.monitoring_thread = None
            
            self.logger.info("Continuous monitoring stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping continuous monitoring: {e}")
            return False
    
    def _continuous_monitoring_loop(self, interval_minutes: int):
        """
        Main loop for continuous monitoring
        
        Args:
            interval_minutes: Monitoring interval in minutes
        """
        try:
            interval_seconds = interval_minutes * 60
            
            while not self.stop_monitoring.is_set():
                try:
                    # Run monitoring cycle
                    cycle_success = self.start_monitoring_cycle()
                    
                    if cycle_success:
                        self.logger.info("Monitoring cycle completed successfully")
                    else:
                        self.logger.error("Monitoring cycle failed")
                    
                    # Wait for next cycle (with ability to stop)
                    if self.stop_monitoring.wait(timeout=interval_seconds):
                        # Stop event was set
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    # Wait a bit before retrying
                    if self.stop_monitoring.wait(timeout=60):
                        break
            
            self.logger.info("Monitoring loop ended")
            
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring loop: {e}")
        finally:
            self.monitoring_active = False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status and statistics
        
        Returns:
            Dict: Monitoring status information
        """
        try:
            status = {
                'monitoring_active': self.monitoring_active,
                'current_session_id': self.current_session_id,
                'components_initialized': {
                    'scrapers': len(self.scrapers),
                    'processors': len(self.processors),
                    'data_synchronizer': self.data_synchronizer is not None,
                    'notification_processor': self.notification_processor is not None
                },
                'statistics': self.monitoring_stats.copy(),
                'configuration': {
                    'monitoring_enabled': self.config_manager.get_website_monitoring_config()['enabled'],
                    'chrome_devtools_enabled': self.config_manager.get_chrome_devtools_config()['enabled'],
                    'content_types_enabled': {}
                }
            }
            
            # Get enabled content types
            monitoring_config = self.config_manager.get_website_monitoring_config()
            for content_type, config in monitoring_config['content_types'].items():
                status['configuration']['content_types_enabled'][content_type] = config['enabled']
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting monitoring status: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """
        Clean up all monitoring resources
        """
        try:
            self.logger.info("Cleaning up website monitoring resources...")
            
            # Stop continuous monitoring if active
            if self.monitoring_active:
                self.stop_continuous_monitoring()
            
            # Clean up scrapers
            for scraper_name, scraper in self.scrapers.items():
                try:
                    scraper.cleanup()
                    self.logger.debug(f"Cleaned up {scraper_name} scraper")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {scraper_name} scraper: {e}")
            
            # Clean up processors
            for processor_name, processor in self.processors.items():
                try:
                    processor.cleanup()
                    self.logger.debug(f"Cleaned up {processor_name} processor")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up {processor_name} processor: {e}")
            
            # Clean up progress manager
            if self.progress_manager:
                try:
                    if self.current_session_id:
                        self.progress_manager.mark_session_completed()
                except Exception as e:
                    self.logger.warning(f"Error finalizing progress session: {e}")
            
            self.logger.info("Website monitoring cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Example usage and testing functions
def main():
    """
    Example usage of WebsiteMonitor orchestrator
    """
    import logging
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('website_monitor_test.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    monitor = None
    try:
        # Initialize WebsiteMonitor
        logger.info("Initializing WebsiteMonitor...")
        monitor = WebsiteMonitor(logger=logger)
        
        # Initialize all components
        if not monitor.initialize_components():
            logger.error("Failed to initialize components")
            return
        
        # Get monitoring status
        status = monitor.get_monitoring_status()
        logger.info(f"Monitoring status: {status}")
        
        # Run a single monitoring cycle
        logger.info("Running single monitoring cycle...")
        success = monitor.start_monitoring_cycle()
        
        if success:
            logger.info("Monitoring cycle completed successfully")
            
            # Display final statistics
            final_status = monitor.get_monitoring_status()
            stats = final_status['statistics']
            logger.info(f"Final statistics:")
            logger.info(f"  Cycles completed: {stats['cycles_completed']}")
            logger.info(f"  Total content processed: {stats['total_content_processed']}")
            logger.info(f"  Errors encountered: {stats['errors_encountered']}")
            logger.info(f"  Average cycle time: {stats['average_cycle_time']:.1f} seconds")
        else:
            logger.error("Monitoring cycle failed")
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    finally:
        if monitor:
            monitor.cleanup()


if __name__ == "__main__":
    main()