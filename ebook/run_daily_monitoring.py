#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Monitoring Execution Script
每日監控執行腳本 (API 版本)

This script is designed to be called by the Node.js scheduler to execute
a complete monitoring cycle using the API-based monitor.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Import new API-based monitoring components
from api_website_monitor import APIWebsiteMonitor
from config_manager import ConfigManager


def setup_logging():
    """Set up logging for daily monitoring execution"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"daily_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def main():
    """
    Main execution function for daily monitoring
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    logger = setup_logging()
    
    try:
        logger.info("=" * 80)
        logger.info("Starting Daily Monitoring Execution (API Version)")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # Initialize API-based website monitor
        logger.info("Initializing API website monitor...")
        monitor = APIWebsiteMonitor(logger=logger)
        
        # Execute monitoring cycle with notification
        logger.info("Executing monitoring cycle...")
        logger.info("-" * 80)
        
        result = monitor.run_monitoring_cycle(send_notification=True)
        
        logger.info("-" * 80)
        
        cycle_success = result.get('success', False)
        
        if cycle_success:
            logger.info("✅ Monitoring cycle completed successfully")
            
            # Get monitoring statistics
            stats = monitor.get_stats()
            logger.info(f"Monitoring Statistics:")
            logger.info(f"  - Cycles completed: {stats.get('cycles_completed', 0)}")
            logger.info(f"  - Remaining pushes today: {stats.get('remaining_pushes_today', '?')}")
            logger.info(f"  - Notification sent: {result.get('notification_sent', False)}")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            logger.info(f"  - Execution time: {execution_time:.2f} seconds")
            
            # Generate output summary for Node.js integration
            output_summary = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "statistics": {
                    "fetched": result.get('fetched', {}),
                    "new_items": result.get('new_items', {}),
                    "notification_sent": result.get('notification_sent', False)
                },
                "message": "Monitoring cycle completed successfully"
            }
            
            # Write summary to output file for Node.js to read
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Summary written to: {summary_file}")
            
            logger.info("=" * 80)
            logger.info("Daily Monitoring Execution Completed Successfully")
            logger.info("=" * 80)
            
            return 0
            
        else:
            logger.error("❌ Monitoring cycle failed")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            
            # Generate error output
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            output_summary = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": execution_time,
                "message": "Monitoring cycle failed",
                "error": result.get('error', 'Unknown error')
            }
            
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
            
            logger.error("=" * 80)
            logger.error("Daily Monitoring Execution Failed")
            logger.error("=" * 80)
            
            return 1
        
    except Exception as e:
        logger.error(f"💥 Unexpected error during daily monitoring: {e}", exc_info=True)
        
        # Generate error output
        try:
            output_summary = {
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "message": "Monitoring execution error",
                "error": str(e)
            }
            
            output_dir = Path("generated_documents")
            output_dir.mkdir(exist_ok=True)
            
            summary_file = output_dir / f"monitoring_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(output_summary, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        return 1
    
    finally:
        # API monitor doesn't need explicit cleanup
        logger.info("Monitoring execution finished")


if __name__ == "__main__":
    sys.exit(main())
