#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notification Processor Module
通知處理器模組

This module extends the main processor to output JSON data for the LINE bot notification system.
It wraps the existing main processor and generates JSON output files for integration.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import the existing main processor
from main_processor import MainProcessor


class NotificationProcessor(MainProcessor):
    """
    Extended MainProcessor that outputs JSON data for notification system integration
    
    This class extends the existing MainProcessor to generate JSON output files
    that can be consumed by the TypeScript LINE bot notification system.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize NotificationProcessor with configuration
        
        Args:
            config: Configuration dictionary containing all necessary settings
            logger: Logger instance for logging operations
        """
        super().__init__(config, logger)
        
        # Output configuration
        self.output_dir = config.get('notification_output_dir', 'generated_documents')
        self.json_output_enabled = config.get('enable_json_output', True)
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            self.logger.info(f"Created output directory: {self.output_dir}")
    
    def run(self) -> bool:
        """
        Execute the main processing workflow with JSON output generation
        
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            # Run the original processing workflow
            success = super().run()
            
            # Generate JSON output if processing was successful and JSON output is enabled
            if success and self.json_output_enabled:
                self._generate_json_output()
            
            return success
            
        except Exception as e:
            self.logger.error(f"NotificationProcessor run failed: {e}", exc_info=True)
            return False
    
    def start_processing_sync(self) -> bool:
        """
        Start processing synchronously (blocking call) with JSON output
        
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            # Call the parent's start_processing_sync method
            success = super().start_processing_sync()
            
            # Generate JSON output if processing was successful and JSON output is enabled
            if success and self.json_output_enabled:
                self._generate_json_output()
            
            return success
            
        except Exception as e:
            self.logger.error(f"NotificationProcessor start_processing_sync failed: {e}", exc_info=True)
            return False
    
    def _generate_json_output(self):
        """
        Generate JSON output file for notification system consumption
        
        Note: The MainProcessor already generates notification JSON files in _generate_notification_data(),
        so this method is mainly for logging and verification purposes.
        """
        try:
            self.logger.info("JSON output generation handled by MainProcessor._generate_notification_data()")
            
            # Verify that the output files were created
            latest_path = os.path.join(self.output_dir, "notification_data_latest.json")
            if os.path.exists(latest_path):
                self.logger.info(f"✅ Notification data file verified: {latest_path}")
                
                # Log summary information
                try:
                    with open(latest_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    books_count = len(data.get('successfullyProcessed', []))
                    self.logger.info(f"📚 Books in notification data: {books_count}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to read notification data for verification: {e}")
            else:
                self.logger.warning(f"⚠️ Notification data file not found: {latest_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to verify JSON output: {e}", exc_info=True)
    
    def get_latest_json_output_path(self) -> Optional[str]:
        """
        Get the path to the latest JSON output file
        
        Returns:
            Path to the latest JSON output file, or None if not found
        """
        try:
            # Check for the latest file created by MainProcessor
            latest_path = os.path.join(self.output_dir, "notification_data_latest.json")
            if os.path.exists(latest_path):
                return latest_path
            
            # Fallback: find the most recent timestamped file
            files = [f for f in os.listdir(self.output_dir) if f.startswith('notification_data_') and f.endswith('.json') and 'latest' not in f]
            if files:
                files.sort(reverse=True)  # Sort by name (timestamp) descending
                return os.path.join(self.output_dir, files[0])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get latest JSON output path: {e}")
            return None


def create_notification_config() -> Dict[str, Any]:
    """
    Create configuration for NotificationProcessor
    
    Returns:
        Dict: Configuration with all required settings including JSON output
    """
    # Load base configuration from existing config.json if available
    base_config = {}
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config.json: {e}")
    
    # Set default values for missing configuration
    default_config = {
        'gemini_api_key': 'your-api-key-here',
        'chromedriver_path': 'chromedriver-win64\\chromedriver.exe',
        'target_url': 'https://www.budaedu.org/#/books/applicable/chinese',
        'baseline_book_title': 'CH754-02',
        'download_dir': 'downloads',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_username': 'your-email@example.com',
        'smtp_password': 'your-password',
        'email_recipients': 'recipient@example.com',
        # Notification-specific configuration
        'notification_output_dir': 'generated_documents',
        'enable_json_output': True
    }
    
    # Merge configurations (base_config takes precedence)
    config = {**default_config, **base_config}
    
    return config


if __name__ == "__main__":
    """
    Main entry point for notification processor
    
    This script can be called directly by the TypeScript scheduler service
    to run the ebook processing with JSON output generation.
    """
    import sys
    
    # Set up logging
    log_filename = f"notification_processor_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 設置控制台輸出編碼為 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("Starting Notification Processor")
        logger.info("=" * 60)
        
        # Create configuration
        config = create_notification_config()
        
        # Validate critical configuration
        if not config.get('gemini_api_key') or config['gemini_api_key'] == 'your-api-key-here':
            logger.error("Gemini API key is not configured. Please set it in config.json")
            sys.exit(1)
        
        # Initialize and run processor
        processor = NotificationProcessor(config, logger)
        
        # Set up status callback for logging
        def status_callback(message):
            logger.info(f"[STATUS] {message}")
        
        processor.set_status_callback(status_callback)
        
        # Run processing
        logger.info("Starting ebook processing with JSON output...")
        success = processor.start_processing_sync()
        
        if success:
            logger.info("✅ Notification processor completed successfully")
            
            # Log the output file path for the TypeScript service
            output_path = processor.get_latest_json_output_path()
            if output_path:
                logger.info(f"📄 JSON output available at: {output_path}")
            
            sys.exit(0)
        else:
            logger.error("❌ Notification processor failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("⚠️ Processing interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C
        
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}", exc_info=True)
        sys.exit(1)